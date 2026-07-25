"""
lgd_data.py
-----------
LGD dataset construction and recovery/loss distribution analysis under the Basel definition.

Under Basel guidelines, LGD is calculated as loss relative to Exposure At Default (EAD),
rather than the initial funded amount.

DOCUMENTED LIMITATION / COLUMN NOTE:
`ead_approx` is calculated as max(funded_amnt - total_rec_prncp, 0). This is an approximation
because LendingClub's `total_rec_prncp` tracks cumulative principal received over the life
of the loan and may include a small amount of post-default principal repayments.
"""

from pathlib import Path
from typing import Any, Dict, Tuple, Union
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for server/script rendering
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_FIGURE_PATH = PROJECT_ROOT / "outputs" / "figures" / "lgd_distribution_basel.png"
DEFAULT_SUMMARY_PATH = PROJECT_ROOT / "outputs" / "tables" / "lgd_distribution_summary.csv"


def build_lgd_base(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filters for defaulted loans (ever_default == 1) and calculates LGD target metrics
    under the Basel definition (Loss / Exposure At Default).

    Derived Columns:
    - funded             : funded_amnt
    - principal_repaid   : total_rec_prncp (principal repaid over loan life)
    - ead_approx         : max(funded - principal_repaid, 0) -- balance at default
    - post_default_recov : recoveries (post charge-off collections)
    - loss               : max(ead_approx - post_default_recov, 0)
    - lgd                : loss / ead_approx clipped to [0, 1]. If ead_approx == 0,
                           lgd = 0.0 and ead_zero_flag = 1.
    - ead_zero_flag      : 1 if ead_approx == 0 else 0
    - recovery_rate      : 1 - lgd
    - has_recovery       : 1 if post_default_recov > 0 else 0

    Note on EAD:
    ead_approx is an approximation because total_rec_prncp may include a small amount
    of post-default principal payments.
    """
    if "ever_default" not in df.columns:
        raise KeyError("Input DataFrame must contain 'ever_default' column.")

    # Filter strictly for defaulted loans across full dataset
    lgd_df = df[df["ever_default"] == 1].copy()

    for col in ["funded_amnt", "total_rec_prncp", "recoveries"]:
        if col not in lgd_df.columns:
            raise KeyError(f"Missing required monetary column '{col}' for Basel LGD calculation.")

    lgd_df["funded"] = lgd_df["funded_amnt"].astype(float)
    lgd_df["principal_repaid"] = lgd_df["total_rec_prncp"].fillna(0.0).astype(float)
    
    # EAD approximation: balance at default (clamped at 0 minimum)
    lgd_df["ead_approx"] = np.maximum(lgd_df["funded"] - lgd_df["principal_repaid"], 0.0)
    
    # Post-default recoveries (charge-off recoveries)
    lgd_df["post_default_recov"] = lgd_df["recoveries"].fillna(0.0).astype(float)
    
    # Loss on outstanding exposure
    lgd_df["loss"] = np.maximum(lgd_df["ead_approx"] - lgd_df["post_default_recov"], 0.0)

    # Edge case handling for ead_approx == 0
    ead_zero_mask = lgd_df["ead_approx"] <= 0
    lgd_df["ead_zero_flag"] = ead_zero_mask.astype(int)

    # Calculate LGD = loss / ead_approx, clipped to [0, 1]
    raw_lgd = np.where(
        ~ead_zero_mask,
        lgd_df["loss"] / lgd_df["ead_approx"],
        0.0
    )
    lgd_df["lgd"] = np.clip(raw_lgd, 0.0, 1.0)
    lgd_df["recovery_rate"] = 1.0 - lgd_df["lgd"]
    lgd_df["has_recovery"] = (lgd_df["post_default_recov"] > 0).astype(int)

    return lgd_df


def lgd_distribution_report(
    df: pd.DataFrame,
    fig_path: Union[str, Path] = DEFAULT_FIGURE_PATH,
    summary_path: Union[str, Path] = DEFAULT_SUMMARY_PATH
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Calculates Basel LGD distribution statistics, outputs summary table,
    and plots histogram of Basel LGD saved to fig_path.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame processed via build_lgd_base or containing derived Basel LGD columns.
    fig_path : str or Path
        Destination filepath for LGD histogram image.
    summary_path : str or Path
        Destination filepath for summary statistics CSV table.

    Returns
    -------
    Tuple[pd.DataFrame, Dict[str, Any]]
        Summary statistics DataFrame and metrics dictionary.
    """
    if "lgd" not in df.columns or "ead_approx" not in df.columns:
        lgd_df = build_lgd_base(df)
    else:
        lgd_df = df[df["ever_default"] == 1] if "ever_default" in df.columns else df

    count_defaulted = len(lgd_df)
    if count_defaulted == 0:
        raise ValueError("No defaulted loans found to analyze LGD distribution.")

    lgd_series = lgd_df["lgd"]
    rec_series = lgd_df["recovery_rate"]
    ead_zero_count = int(lgd_df["ead_zero_flag"].sum())

    metrics = {
        "count_defaulted_loans": count_defaulted,
        "count_ead_zero": ead_zero_count,
        "fraction_ead_zero": float(ead_zero_count / count_defaulted),
        "mean_lgd": float(lgd_series.mean()),
        "median_lgd": float(lgd_series.median()),
        "std_lgd": float(lgd_series.std()),
        "mean_recovery_rate": float(rec_series.mean()),
        "median_recovery_rate": float(rec_series.median()),
        "std_recovery_rate": float(rec_series.std()),
        "fraction_total_loss_lgd1": float((lgd_series == 1.0).mean()),
        "fraction_zero_loss_lgd0": float((lgd_series == 0.0).mean()),
        "fraction_has_post_default_recovery": float((lgd_df["has_recovery"] == 1).mean())
    }

    summary_table = pd.DataFrame([metrics])

    fig_path = Path(fig_path)
    summary_path = Path(summary_path)
    fig_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.parent.mkdir(parents=True, exist_ok=True)

    summary_table.to_csv(summary_path, index=False)

    print("=" * 65)
    print(" BASEL LGD DISTRIBUTION SUMMARY")
    print("=" * 65)
    print(f"Defaulted Loans Count            : {metrics['count_defaulted_loans']:,}")
    print(f"EAD Zero Count (Fraction)        : {metrics['count_ead_zero']:,} ({metrics['fraction_ead_zero']*100:.2f}%)")
    print(f"LGD Mean (Std)                   : {metrics['mean_lgd']:.4f} ({metrics['std_lgd']:.4f})")
    print(f"LGD Median                       : {metrics['median_lgd']:.4f}")
    print(f"Recovery Rate Mean (Std)         : {metrics['mean_recovery_rate']:.4f} ({metrics['std_recovery_rate']:.4f})")
    print(f"Recovery Rate Median             : {metrics['median_recovery_rate']:.4f}")
    print(f"Fraction Total Loss (LGD == 1.0) : {metrics['fraction_total_loss_lgd1']:.4f} ({metrics['fraction_total_loss_lgd1']*100:.2f}%)")
    print(f"Fraction Zero Loss (LGD == 0.0)  : {metrics['fraction_zero_loss_lgd0']:.4f} ({metrics['fraction_zero_loss_lgd0']*100:.2f}%)")
    print(f"Fraction Has Post-Default Recov  : {metrics['fraction_has_post_default_recovery']:.4f} ({metrics['fraction_has_post_default_recovery']*100:.2f}%)")
    print("=" * 65)
    print(f"Saved summary CSV to: {summary_path}")

    # Plot 20-bin Histogram of Basel LGD
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.hist(lgd_series, bins=20, range=(0.0, 1.0), color="#d62728", edgecolor="black", alpha=0.8)
    ax.set_title("Basel LGD Distribution (Loss / Exposure At Default)", fontsize=13, pad=12)
    ax.set_xlabel("Loss Given Default (LGD = loss / ead_approx)", fontsize=11)
    ax.set_ylabel("Number of Defaulted Loans", fontsize=11)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()
    fig.savefig(fig_path, dpi=300)
    plt.close(fig)
    print(f"Saved Basel LGD histogram figure to: {fig_path}")

    return summary_table, metrics
