"""
binning.py
----------
Weight of Evidence (WoE) and Information Value (IV) Feature Binning Engine.

Provides the WoEBinner class which:
- Enforces anti-leakage protection via assert_no_leakage().
- Bins numeric features starting at 20 quantiles and merging adjacent bins to achieve
  >= 5% minimum bin size and strict WoE monotonicity.
- Bins categorical features, merging rare categories (< 5%) into 'OTHER'.
- Assigns dedicated bins to missing values (NaN/null).
- Uses Laplace (+0.5) smoothing for finite log-odds.
- Computes per-bin WoE, total variable IV, and predictive strength ratings.
"""

import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
from creditrisk.data.schema import assert_no_leakage

MIN_BIN_PCT = 0.05  # Minimum 5% of rows per bin


def _is_monotonic(values: List[float]) -> bool:
    """Checks if a list of floats is strictly non-decreasing or non-increasing."""
    if len(values) <= 1:
        return True
    diffs = np.diff(values)
    return bool(np.all(diffs >= 0) or np.all(diffs <= 0))


class WoEBinner:
    """
    Weight of Evidence (WoE) and Information Value (IV) Transformer.
    """

    def __init__(self, min_bin_pct: float = MIN_BIN_PCT):
        self.min_bin_pct = min_bin_pct
        self.binner_rules_: Dict[str, Dict[str, Any]] = {}
        self.iv_summary_: Optional[pd.DataFrame] = None
        self.is_fitted_: bool = False

    def _bin_numeric_variable(self, x: pd.Series, y: pd.Series) -> Dict[str, Any]:
        """
        Bins a numeric feature starting with up to 20 quantiles, merging adjacent bins
        until every bin holds >= min_bin_pct rows and WoE values across bins are monotonic.
        """
        total_rows = len(x)
        min_rows = int(np.ceil(self.min_bin_pct * total_rows))

        missing_mask = x.isna()
        x_valid = x[~missing_mask]
        y_valid = y[~missing_mask]

        if len(x_valid.unique()) <= 1:
            # Single value or all missing
            bins = [-np.inf, np.inf]
        else:
            # Start with up to 20 quantile cuts
            q_cnt = min(20, len(x_valid.unique()))
            _, bins = pd.qcut(x_valid, q=q_cnt, retbins=True, duplicates="drop")
            bins = list(bins)
            bins[0] = -np.inf
            bins[-1] = np.inf

        # Iteratively merge adjacent bins to satisfy minimum size and monotonicity
        while len(bins) > 2:
            # Categorize valid numeric data into current bin intervals
            binned = pd.cut(x_valid, bins=bins, include_lowest=True)
            cat_counts = binned.value_counts(sort=False)
            
            # Check minimum size condition on valid bins
            violates_size = (cat_counts < min_rows).any()

            # Compute current WoE values across non-missing bins to check monotonicity
            temp_woes = []
            for interval in cat_counts.index:
                mask = binned == interval
                g = (y_valid[mask] == 0).sum() + 0.5
                b = (y_valid[mask] == 1).sum() + 0.5
                temp_woes.append(np.log(g / b))

            violates_monotonicity = not _is_monotonic(temp_woes)

            if not violates_size and not violates_monotonicity:
                break  # Binning criteria satisfied!

            # Find best adjacent pair of bins to merge
            # Prioritize merging smallest bin or non-monotonic pair
            pair_to_merge = 0
            min_pair_sum = np.inf

            for i in range(len(bins) - 2):
                pair_sum = cat_counts.iloc[i] + cat_counts.iloc[i + 1]
                if pair_sum < min_pair_sum:
                    min_pair_sum = pair_sum
                    pair_to_merge = i

            # Remove the boundary between pair_to_merge and pair_to_merge + 1
            bins.pop(pair_to_merge + 1)

        return {"type": "numeric", "bins": bins}

    def _bin_categorical_variable(self, x: pd.Series, y: pd.Series) -> Dict[str, Any]:
        """
        Bins a categorical feature. Categories with < min_bin_pct rows are merged into 'OTHER'.
        """
        total_rows = len(x)
        min_rows = int(np.ceil(self.min_bin_pct * total_rows))

        x_str = x.astype(str).fillna("MISSING")
        val_counts = x_str.value_counts()

        frequent_cats = set(val_counts[val_counts >= min_rows].index) - {"MISSING", "nan", "None"}

        return {"type": "categorical", "frequent_categories": frequent_cats}

    def fit(self, X: pd.DataFrame, y: Union[pd.Series, np.ndarray]) -> "WoEBinner":
        """
        Fits the WoE binner on features X and binary target y.
        """
        assert_no_leakage(list(X.columns))

        y_series = pd.Series(y, index=X.index)
        total_goods = (y_series == 0).sum()
        total_bads = (y_series == 1).sum()
        total_rows = len(X)

        self.binner_rules_ = {}
        summary_list = []

        for col in X.columns:
            x_col = X[col]

            if pd.api.types.is_numeric_dtype(x_col) and not pd.api.types.is_bool_dtype(x_col):
                rule = self._bin_numeric_variable(x_col, y_series)
            else:
                rule = self._bin_categorical_variable(x_col, y_series)

            # Assign bins to all rows for computing bin statistics
            if rule["type"] == "numeric":
                bins = rule["bins"]
                missing_mask = x_col.isna()
                labels = [f"[{bins[i]:.2f}, {bins[i+1]:.2f})" for i in range(len(bins) - 1)]
                binned_series = pd.cut(x_col, bins=bins, labels=labels, include_lowest=True).astype(str)
                binned_series[missing_mask] = "MISSING"
            else:
                freq_cats = rule["frequent_categories"]
                binned_series = x_col.astype(str).fillna("MISSING")
                binned_series = binned_series.apply(
                    lambda val: val if val in freq_cats or val == "MISSING" else "OTHER"
                )

            # Build detailed bin statistics table
            bin_stats = []
            unique_bins = list(binned_series.unique())

            # Sort bins logically (MISSING at end, numeric intervals in order)
            if rule["type"] == "numeric":
                non_missing_bins = [b for b in unique_bins if b != "MISSING"]
                non_missing_bins.sort(key=lambda b_str: float(b_str.split(",")[0].replace("[", "")))
                if "MISSING" in unique_bins:
                    unique_bins = non_missing_bins + ["MISSING"]
                else:
                    unique_bins = non_missing_bins

            K = len(unique_bins)  # Total bins for Laplace smoothing parameter

            var_iv = 0.0
            bin_detail_list = []

            for b_label in unique_bins:
                mask = binned_series == b_label
                n = int(mask.sum())
                n_good = int((y_series[mask] == 0).sum())
                n_bad = int((y_series[mask] == 1).sum())

                # Laplace smoothing (+0.5)
                pct_good = (n_good + 0.5) / (total_goods + 0.5 * K)
                pct_bad = (n_bad + 0.5) / (total_bads + 0.5 * K)

                woe = float(np.log(pct_good / pct_bad))
                iv_bin = float((pct_good - pct_bad) * woe)
                var_iv += iv_bin

                bin_detail_list.append(
                    {
                        "bin": b_label,
                        "n": n,
                        "n_good": n_good,
                        "n_bad": n_bad,
                        "pct_good": pct_good,
                        "pct_bad": pct_bad,
                        "woe": woe,
                        "iv_bin": iv_bin,
                    }
                )

            rule["bin_table"] = pd.DataFrame(bin_detail_list)
            rule["total_iv"] = var_iv
            self.binner_rules_[col] = rule

            # Evaluate IV strength category
            if var_iv < 0.02:
                strength = "useless"
            elif var_iv < 0.1:
                strength = "weak"
            elif var_iv < 0.3:
                strength = "medium"
            elif var_iv < 0.5:
                strength = "strong"
            else:
                strength = "suspicious"

            summary_list.append(
                {
                    "variable": col,
                    "n_bins": K,
                    "IV": var_iv,
                    "iv_strength": strength,
                }
            )

        self.iv_summary_ = pd.DataFrame(summary_list).sort_values("IV", ascending=False).reset_index(drop=True)
        self.is_fitted_ = True
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Transforms input DataFrame features into WoE float values.
        """
        if not self.is_fitted_:
            raise ValueError("WoEBinner is not fitted yet. Call fit() before transform().")

        X_woe = pd.DataFrame(index=X.index)

        for col in X.columns:
            if col not in self.binner_rules_:
                raise ValueError(f"Column '{col}' was not fitted in WoEBinner.")

            rule = self.binner_rules_[col]
            x_col = X[col]
            bin_table = rule["bin_table"]
            woe_map = dict(zip(bin_table["bin"], bin_table["woe"]))

            if rule["type"] == "numeric":
                bins = rule["bins"]
                missing_mask = x_col.isna()
                labels = [f"[{bins[i]:.2f}, {bins[i+1]:.2f})" for i in range(len(bins) - 1)]
                binned = pd.cut(x_col, bins=bins, labels=labels, include_lowest=True).astype(str)
                binned[missing_mask] = "MISSING"
                X_woe[col] = binned.map(woe_map).astype(float)
            else:
                freq_cats = rule["frequent_categories"]
                x_str = x_col.astype(str).fillna("MISSING")
                binned = x_str.apply(lambda val: val if val in freq_cats or val == "MISSING" else "OTHER")
                X_woe[col] = binned.map(woe_map).astype(float)

        return X_woe

    def fit_transform(self, X: pd.DataFrame, y: Union[pd.Series, np.ndarray]) -> pd.DataFrame:
        """Fits binner and transforms X in one step."""
        return self.fit(X, y).transform(X)

    def get_iv_table(self) -> pd.DataFrame:
        """Returns IV summary table sorted by IV descending."""
        if not self.is_fitted_ or self.iv_summary_ is None:
            raise ValueError("WoEBinner is not fitted yet.")
        return self.iv_summary_.copy()

    def get_bin_table(self, variable: str) -> pd.DataFrame:
        """Returns the full bin detail table for a given variable."""
        if not self.is_fitted_ or variable not in self.binner_rules_:
            raise ValueError(f"Variable '{variable}' was not fitted or does not exist.")
        return self.binner_rules_[variable]["bin_table"].copy()

    def save(self, path: Union[str, Path]) -> None:
        """Saves fitted WoEBinner object to path using pickle."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, path: Union[str, Path]) -> "WoEBinner":
        """Loads fitted WoEBinner object from path."""
        path = Path(path)
        with open(path, "rb") as f:
            binner = pickle.load(f)
        return binner
