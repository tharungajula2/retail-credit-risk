"""
stability.py
------------
Population Stability Index (PSI) and Characteristic Stability Index (CSI) Module.

Functions:
- psi: Calculates score PSI between expected (train) and actual (oot) score distributions.
- psi_table: Generates per-bin PSI contribution table.
- csi: Calculates CSI for a single variable across WoEBinner feature bins.
"""

from pathlib import Path
from typing import Any, Dict, Tuple, Union
import numpy as np
import pandas as pd
from creditrisk.features.binning import WoEBinner


def get_stability_band(val: float) -> str:
    """Categorizes PSI/CSI values into standard regulatory stability bands."""
    if val < 0.10:
        return "stable"
    elif val < 0.25:
        return "moderate shift"
    else:
        return "significant shift"


def psi(expected: pd.Series, actual: pd.Series, n_bins: int = 10) -> Tuple[float, pd.DataFrame]:
    """
    Computes Population Stability Index (PSI) using expected (train) fixed quantile bins.

    Parameters
    ----------
    expected : pd.Series
        Reference baseline distribution (e.g., train scores).
    actual : pd.Series
        Target validation distribution (e.g., oot scores).
    n_bins : int, optional
        Number of quantile bins.

    Returns
    -------
    Tuple[float, pd.DataFrame]
        (psi_total, psi_detail_table)
    """
    # 1. Obtain fixed bin edges from expected (train) scores
    _, bin_edges = pd.qcut(expected, q=n_bins, retbins=True, duplicates="drop")
    bin_edges[0] = -np.inf
    bin_edges[-1] = np.inf

    # 2. Bin expected and actual scores using the exact same fixed edges
    exp_binned = pd.cut(expected, bins=bin_edges, include_lowest=True)
    act_binned = pd.cut(actual, bins=bin_edges, include_lowest=True)

    exp_counts = exp_binned.value_counts(sort=False)
    act_counts = act_binned.value_counts(sort=False)

    n_exp = len(expected)
    n_act = len(actual)

    table_rows = []
    psi_total = 0.0
    eps = 1e-6  # Epsilon to prevent log(0) or zero division

    for interval in exp_counts.index:
        c_exp = exp_counts[interval]
        c_act = act_counts[interval]

        pct_exp = (c_exp / n_exp) if n_exp > 0 else eps
        pct_act = (c_act / n_act) if n_act > 0 else eps

        pct_exp_adj = max(pct_exp, eps)
        pct_act_adj = max(pct_act, eps)

        psi_bin = (pct_act_adj - pct_exp_adj) * np.log(pct_act_adj / pct_exp_adj)
        psi_total += psi_bin

        table_rows.append(
            {
                "bin_interval": str(interval),
                "expected_count": c_exp,
                "actual_count": c_act,
                "expected_pct": pct_exp,
                "actual_pct": pct_act,
                "psi_bin": psi_bin,
            }
        )

    detail_df = pd.DataFrame(table_rows)
    return float(psi_total), detail_df


def csi(
    train_df: pd.DataFrame,
    oot_df: pd.DataFrame,
    variable: str,
    woe_binner: WoEBinner,
) -> Tuple[float, pd.DataFrame]:
    """
    Computes Characteristic Stability Index (CSI) for a specific feature across its WoE bins.

    Parameters
    ----------
    train_df : pd.DataFrame
        Training dataset (expected).
    oot_df : pd.DataFrame
        Out-of-time dataset (actual).
    variable : str
        Feature name.
    woe_binner : WoEBinner
        Fitted binner object.

    Returns
    -------
    Tuple[float, pd.DataFrame]
        (csi_total, csi_detail_table)
    """
    rule = woe_binner.binner_rules_[variable]
    x_train = train_df[variable]
    x_oot = oot_df[variable]

    if rule["type"] == "numeric":
        bins = rule["bins"]
        missing_train = x_train.isna()
        missing_oot = x_oot.isna()

        labels = [f"[{bins[i]:.2f}, {bins[i+1]:.2f})" for i in range(len(bins) - 1)]
        binned_train = pd.cut(x_train, bins=bins, labels=labels, include_lowest=True).astype(str)
        binned_oot = pd.cut(x_oot, bins=bins, labels=labels, include_lowest=True).astype(str)

        binned_train[missing_train] = "MISSING"
        binned_oot[missing_oot] = "MISSING"
    else:
        freq_cats = rule["frequent_categories"]
        binned_train = x_train.astype(str).fillna("MISSING").apply(lambda val: val if val in freq_cats or val == "MISSING" else "OTHER")
        binned_oot = x_oot.astype(str).fillna("MISSING").apply(lambda val: val if val in freq_cats or val == "MISSING" else "OTHER")

    # Combine unique bins across both
    unique_bins = list(set(binned_train.unique()).union(set(binned_oot.unique())))
    
    n_train = len(x_train)
    n_oot = len(x_oot)

    csi_total = 0.0
    table_rows = []
    eps = 1e-6

    for b_label in sorted(unique_bins):
        c_train = (binned_train == b_label).sum()
        c_oot = (binned_oot == b_label).sum()

        pct_train = (c_train / n_train) if n_train > 0 else eps
        pct_oot = (c_oot / n_oot) if n_oot > 0 else eps

        pct_train_adj = max(pct_train, eps)
        pct_oot_adj = max(pct_oot, eps)

        csi_bin = (pct_oot_adj - pct_train_adj) * np.log(pct_oot_adj / pct_train_adj)
        csi_total += csi_bin

        table_rows.append(
            {
                "variable": variable,
                "bin": b_label,
                "train_count": c_train,
                "oot_count": c_oot,
                "train_pct": pct_train,
                "oot_pct": pct_oot,
                "csi_bin": csi_bin,
            }
        )

    detail_df = pd.DataFrame(table_rows)
    return float(csi_total), detail_df
