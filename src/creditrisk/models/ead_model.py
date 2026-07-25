"""
ead_model.py
------------
Exposure At Default (EAD) modeling module for term loans.

1. build_ead_term(df): Computes outstanding balance at default (`ead`) and fraction owed (`ead_ratio`)
   for defaulted loans. This definition is identical to `ead_approx` used in `lgd_data.py`.
2. ead_summary(df): Computes summary statistics and breakdowns by term and grade.
3. get_portfolio_ead(df): Computes EAD for all loans (actual EAD for defaulted loans, out_prncp for performing).
"""

from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SUMMARY_PATH = PROJECT_ROOT / "outputs" / "tables" / "ead_summary.csv"
DEFAULT_FIGURE_PATH = PROJECT_ROOT / "outputs" / "figures" / "ead_ratio_distribution.png"


def build_ead_term(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes Exposure At Default (EAD) for defaulted loans (ever_default == 1).

    Derived Columns:
    - funded           : funded_amnt
    - principal_repaid : total_rec_prncp
    - ead              : max(funded - principal_repaid, 0)
    - ead_ratio        : ead / funded, clipped to [0, 1]

    CONSISTENCY NOTE:
    `ead` is identical to `ead_approx` derived in `lgd_data.py` (LGD modeling) to ensure
    absolute consistency across PD, LGD, and EAD risk parameters.
    """
    if "ever_default" not in df.columns:
        raise KeyError("Input DataFrame must contain 'ever_default' column.")

    ead_df = df[df["ever_default"] == 1].copy()

    for col in ["funded_amnt", "total_rec_prncp"]:
        if col not in ead_df.columns:
            raise KeyError(f"Missing required column '{col}' for EAD calculation.")

    ead_df["funded"] = ead_df["funded_amnt"].astype(float)
    ead_df["principal_repaid"] = ead_df["total_rec_prncp"].fillna(0.0).astype(float)

    # EAD: outstanding principal at default (clamped at 0 minimum)
    ead_df["ead"] = np.maximum(ead_df["funded"] - ead_df["principal_repaid"], 0.0)

    # Safe division guard for funded <= 0
    valid_funded_mask = ead_df["funded"] > 0
    raw_ratio = np.where(
        valid_funded_mask,
        ead_df["ead"] / ead_df["funded"],
        0.0
    )
    ead_df["ead_ratio"] = np.clip(raw_ratio, 0.0, 1.0)

    return ead_df


def get_portfolio_ead(df: pd.DataFrame) -> pd.Series:
    """
    Calculates EAD for ANY loan across the entire portfolio (defaulted or performing).

    Logic:
    - Defaulted loans (ever_default == 1): actual EAD = max(funded_amnt - total_rec_prncp, 0)
    - Performing loans (ever_default == 0): current outstanding principal = max(out_prncp, 0)

    Returns
    -------
    pd.Series
        EAD values aligned with input DataFrame index.
    """
    if "ever_default" not in df.columns:
        raise KeyError("Input DataFrame must contain 'ever_default' column.")
    for col in ["funded_amnt", "total_rec_prncp", "out_prncp"]:
        if col not in df.columns:
            raise KeyError(f"Missing required column '{col}' for portfolio EAD.")

    funded = df["funded_amnt"].astype(float)
    prncp_repaid = df["total_rec_prncp"].fillna(0.0).astype(float)
    out_prncp = df["out_prncp"].fillna(0.0).astype(float)

    actual_ead = np.maximum(funded - prncp_repaid, 0.0)
    performing_ead = np.maximum(out_prncp, 0.0)

    ead_series = np.where(df["ever_default"] == 1, actual_ead, performing_ead)
    return pd.Series(ead_series, index=df.index, name="ead")


def ead_summary(
    df: pd.DataFrame,
    summary_path: Union[str, Path] = DEFAULT_SUMMARY_PATH,
    fig_path: Union[str, Path] = DEFAULT_FIGURE_PATH
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Generates EAD summary tables and plots distribution histogram of ead_ratio.

    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]
        Overall EAD summary, EAD breakdown by term, EAD breakdown by grade.
    """
    if "ead_ratio" not in df.columns:
        ead_df = build_ead_term(df)
    else:
        ead_df = df[df["ever_default"] == 1] if "ever_default" in df.columns else df

    count_defaulted = len(ead_df)
    if count_defaulted == 0:
        raise ValueError("No defaulted loans found to analyze EAD distribution.")

    # 1. Overall Metrics
    overall = pd.DataFrame([{
        "segment": "Overall",
        "category": "All",
        "count_defaulted": count_defaulted,
        "mean_ead": float(ead_df["ead"].mean()),
        "median_ead": float(ead_df["ead"].median()),
        "mean_ead_ratio": float(ead_df["ead_ratio"].mean()),
        "median_ead_ratio": float(ead_df["ead_ratio"].median())
    }])

    # 2. Breakdown by Term
    term_summary = (
        ead_df.groupby("term")
        .agg(
            count_defaulted=("ead", "count"),
            mean_ead=("ead", "mean"),
            median_ead=("ead", "median"),
            mean_ead_ratio=("ead_ratio", "mean"),
            median_ead_ratio=("ead_ratio", "median")
        )
        .reset_index()
    )
    term_summary.insert(0, "segment", "By Term")
    term_summary.rename(columns={"term": "category"}, inplace=True)

    # 3. Breakdown by Grade
    grade_summary = (
        ead_df.groupby("grade")
        .agg(
            count_defaulted=("ead", "count"),
            mean_ead=("ead", "mean"),
            median_ead=("ead", "median"),
            mean_ead_ratio=("ead_ratio", "mean"),
            median_ead_ratio=("ead_ratio", "median")
        )
        .reset_index()
    )
    grade_summary.insert(0, "segment", "By Grade")
    grade_summary.rename(columns={"grade": "category"}, inplace=True)

    # Combine into unified summary table
    summary_combined = pd.concat([overall, term_summary, grade_summary], ignore_index=True)

    # Ensure parent directories exist
    summary_path = Path(summary_path)
    fig_path = Path(fig_path)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    fig_path.parent.mkdir(parents=True, exist_ok=True)

    summary_combined.to_csv(summary_path, index=False)

    print("=" * 70)
    print(" EAD SUMMARY TABLE (DEFAULTED LOANS)")
    print("=" * 70)
    print(summary_combined.to_string(index=False))
    print("=" * 70)
    print(f"Saved summary CSV to: {summary_path}")

    # Plot 20-bin Histogram of ead_ratio
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.hist(ead_df["ead_ratio"], bins=20, range=(0.0, 1.0), color="#2ca02c", edgecolor="black", alpha=0.8)
    ax.set_title("EAD Ratio Distribution (Defaulted Loans)", fontsize=13, pad=12)
    ax.set_xlabel("EAD Ratio (outstanding balance at default / funded amount)", fontsize=11)
    ax.set_ylabel("Number of Defaulted Loans", fontsize=11)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()
    fig.savefig(fig_path, dpi=300)
    plt.close(fig)
    print(f"Saved EAD ratio histogram figure to: {fig_path}")

    return overall, term_summary, grade_summary
