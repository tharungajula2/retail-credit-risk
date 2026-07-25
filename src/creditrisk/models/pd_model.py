"""
pd_model.py
-----------
Probability of Default (PD) Logistic Regression Modeling Class.

Fits statsmodels Logit on WoE-transformed features, provides statistical summary tables,
flags positive coefficient sign anomalies, predicts default probabilities, and supports
model serialization.
"""

import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import numpy as np
import pandas as pd
import statsmodels.api as sm
import yaml
from creditrisk.data.schema import assert_no_leakage, get_pd_eligible_columns
from creditrisk.features.binning import WoEBinner

CONFIG_PATH = Path(__file__).resolve().parents[3] / "config" / "pd_model.yaml"


def load_pd_config(config: Union[Dict[str, Any], Path, str] = CONFIG_PATH) -> Dict[str, Any]:
    """Loads PD model configuration parameters."""
    if isinstance(config, (str, Path)):
        path = Path(config)
        if not path.exists():
            raise FileNotFoundError(f"PD model configuration file not found at: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    elif isinstance(config, dict):
        return config
    else:
        raise TypeError("Config must be a dictionary or a valid file path.")


class PDModel:
    """
    Probability of Default (PD) Logistic Regression Wrapper using statsmodels.
    """

    def __init__(self, config: Union[Dict[str, Any], Path, str] = CONFIG_PATH):
        self.config = load_pd_config(config)
        self.model_fit_: Optional[sm.DiscreteResults] = None
        self.features_: List[str] = []
        self.is_fitted_: bool = False

    def fit(
        self,
        train_df: pd.DataFrame,
        woe_binner: WoEBinner,
        iv_table: pd.DataFrame,
        exclude_cols: Optional[List[str]] = None,
    ) -> "PDModel":
        """
        Selects features based on IV thresholds and exclusions, WoE-transforms inputs using
        the pre-fitted woe_binner (without refitting), and fits statsmodels Logit.
        """
        min_iv = self.config.get("min_iv_threshold", 0.02)
        target_col = self.config.get("target_column", "default_12m")
        drop_unstable = set(self.config.get("drop_unstable", ["tot_cur_bal", "total_rev_hi_lim"]))

        # Combine all excluded columns (model-specific exclusions + drop_unstable)
        all_exclusions = set(exclude_cols or []).union(drop_unstable)

        # 1. Candidate features above IV threshold (excluding all_exclusions)
        candidate_cols = [
            c for c in iv_table[iv_table["IV"] >= min_iv]["variable"]
            if c not in all_exclusions
        ]

        # 2. Assert zero target leakage on candidate features
        assert_no_leakage(candidate_cols)

        # 3. Filter candidates to PD-eligible columns
        pd_eligible = set(get_pd_eligible_columns())
        selected_cols = [c for c in candidate_cols if c in pd_eligible]

        if not selected_cols:
            raise ValueError("No features selected after IV threshold filtering and exclusions.")

        self.features_ = selected_cols

        # 3. WoE-transform features using the pre-fitted binner
        X_train_raw = train_df[self.features_]
        X_train_woe = woe_binner.transform(X_train_raw)

        # 4. Add intercept constant and fit statsmodels Logit
        X_train_woe_const = sm.add_constant(X_train_woe, has_constant="add")
        y_train = train_df[target_col]

        logit_model = sm.Logit(y_train, X_train_woe_const)
        self.model_fit_ = logit_model.fit(disp=False)
        self.is_fitted_ = True

        return self

    def summary(self) -> pd.DataFrame:
        """
        Returns a DataFrame summarizing model coefficients, std errors, p-values,
        significance flags, and positive sign anomaly flags.
        """
        if not self.is_fitted_ or self.model_fit_ is None:
            raise ValueError("PDModel is not fitted yet. Call fit() before summary().")

        res = self.model_fit_
        summary_df = pd.DataFrame(
            {
                "variable": res.params.index,
                "coefficient": res.params.values,
                "std_err": res.bse.values,
                "p_value": res.pvalues.values,
            }
        )

        summary_df["significant"] = summary_df["p_value"] < 0.05
        # In WoE encoding (where higher WoE = higher goods ratio / lower risk),
        # predicting default (y=1) should yield a NEGATIVE coefficient.
        # A positive coefficient indicates a potential misbehaving feature / sign anomaly.
        summary_df["positive_sign_flag"] = (summary_df["variable"] != "const") & (summary_df["coefficient"] > 0)

        return summary_df

    def predict_pd(self, df: pd.DataFrame, woe_binner: WoEBinner) -> np.ndarray:
        """
        Transforms input DataFrame features to WoE and predicts Probability of Default (PD).
        """
        if not self.is_fitted_ or self.model_fit_ is None:
            raise ValueError("PDModel is not fitted yet. Call fit() before predict_pd().")

        X_raw = df[self.features_]
        X_woe = woe_binner.transform(X_raw)
        X_woe_const = sm.add_constant(X_woe, has_constant="add")

        predicted_pds = self.model_fit_.predict(X_woe_const)
        return predicted_pds.values

    def save(self, path: Union[str, Path]) -> None:
        """Saves fitted PDModel instance to disk via pickle."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, path: Union[str, Path]) -> "PDModel":
        """Loads fitted PDModel instance from disk."""
        path = Path(path)
        with open(path, "rb") as f:
            model = pickle.load(f)
        return model
