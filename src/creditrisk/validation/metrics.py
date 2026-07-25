"""
metrics.py
----------
Statistical Validation Metrics for Credit Risk Probability of Default (PD) Models.

Functions:
- gini_auc: Computes ROC-AUC and Gini coefficient (Gini = 2 * AUC - 1).
- ks_statistic: Computes Kolmogorov-Smirnov statistic (max separation between cumulative good and bad distributions) and cutoff score.
- calibration_table: Computes decile mean predicted PD vs observed default rate.
- hosmer_lemeshow: Computes Hosmer-Lemeshow chi-square statistic and p-value.
- brier_score: Computes Brier score loss (mean squared prediction error).
"""

from typing import Tuple
import numpy as np
import pandas as pd
from scipy.stats import chi2
from sklearn.metrics import brier_score_loss, roc_auc_score


def gini_auc(y_true: np.ndarray, pd_pred: np.ndarray) -> Tuple[float, float]:
    """
    Computes ROC-AUC and Gini coefficient.

    Gini = 2 * AUC - 1
    """
    auc = float(roc_auc_score(y_true, pd_pred))
    gini = 2.0 * auc - 1.0
    return auc, gini


def ks_statistic(y_true: np.ndarray, pd_pred: np.ndarray) -> Tuple[float, float]:
    """
    Computes Kolmogorov-Smirnov (KS) statistic: maximum vertical separation
    between cumulative distribution functions of goods (y=0) and bads (y=1).

    Returns
    -------
    Tuple[float, float]
        (ks_statistic, cutoff_threshold)
    """
    df = pd.DataFrame({"y_true": y_true, "pd_pred": pd_pred})
    df = df.sort_values("pd_pred", ascending=False).reset_index(drop=True)

    n_bad = (df["y_true"] == 1).sum()
    n_good = (df["y_true"] == 0).sum()

    if n_bad == 0 or n_good == 0:
        return 0.0, 0.0

    df["cum_bad"] = (df["y_true"] == 1).cumsum() / n_bad
    df["cum_good"] = (df["y_true"] == 0).cumsum() / n_good

    df["ks_diff"] = np.abs(df["cum_bad"] - df["cum_good"])
    max_idx = df["ks_diff"].idxmax()

    ks_stat = float(df.loc[max_idx, "ks_diff"])
    cutoff = float(df.loc[max_idx, "pd_pred"])

    return ks_stat, cutoff


def calibration_table(y_true: np.ndarray, pd_pred: np.ndarray, n_bins: int = 10) -> pd.DataFrame:
    """
    Bins predicted PD into n_bins quantiles and computes mean predicted PD,
    observed default rate, loan count, and default count per bin.
    """
    df = pd.DataFrame({"y_true": y_true, "pd_pred": pd_pred})

    # Cut into n_bins quantiles
    df["decile"] = pd.qcut(df["pd_pred"], q=n_bins, duplicates="drop")

    calib = df.groupby("decile", observed=False, as_index=False).agg(
        n_loans=("y_true", "count"),
        n_defaults=("y_true", "sum"),
        mean_predicted_pd=("pd_pred", "mean"),
        observed_default_rate=("y_true", "mean"),
    )

    calib["decile_num"] = range(1, len(calib) + 1)
    return calib[["decile_num", "n_loans", "n_defaults", "mean_predicted_pd", "observed_default_rate"]]


def hosmer_lemeshow(y_true: np.ndarray, pd_pred: np.ndarray, n_bins: int = 10) -> Tuple[float, float]:
    """
    Performs Hosmer-Lemeshow goodness-of-fit chi-square calibration test.

    Returns
    -------
    Tuple[float, float]
        (hl_statistic, p_value)
    """
    calib = calibration_table(y_true, pd_pred, n_bins=n_bins)
    k = len(calib)

    if k <= 2:
        return 0.0, 1.0

    hl_stat = 0.0

    for _, row in calib.iterrows():
        n_g = row["n_loans"]
        obs_1 = row["n_defaults"]
        obs_0 = n_g - obs_1

        exp_1 = n_g * row["mean_predicted_pd"]
        exp_0 = n_g * (1.0 - row["mean_predicted_pd"])

        # Add small epsilon to prevent division by zero
        eps = 1e-9
        term_1 = ((obs_1 - exp_1) ** 2) / (exp_1 + eps)
        term_0 = ((obs_0 - exp_0) ** 2) / (exp_0 + eps)

        hl_stat += (term_1 + term_0)

    df_degrees = k - 2
    p_val = float(1.0 - chi2.cdf(hl_stat, df=df_degrees))

    return float(hl_stat), p_val


def brier_score(y_true: np.ndarray, pd_pred: np.ndarray) -> float:
    """
    Computes Brier score loss (mean squared error of probability predictions).
    """
    return float(brier_score_loss(y_true, pd_pred))
