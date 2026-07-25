"""
transitions.py
--------------
Rating-grade-to-outcome transition matrix and migration analytics module.

1. transition_matrix(df): Constructs row-normalized transition probabilities from origination grade
   (A, B, C, D, E, F, G) to final loan outcome (Fully Paid, Current, Late, Default / Charged Off).
   DOCUMENTED NOTE:
   A true periodic rating-migration matrix requires periodic re-rating of active exposures over time.
   This module constructs an origination-grade-to-resolution outcome transition matrix, a standard
   industry variant for un-rerated retail loan books.
2. default_by_grade_summary(df): Computes total loan counts and observed default rates per origination grade.
"""

from pathlib import Path
from typing import Any, Dict, Tuple, Union
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_TRANSITION_TABLE_PATH = PROJECT_ROOT / "outputs" / "tables" / "transition_matrix.csv"
DEFAULT_HEATMAP_PATH = PROJECT_ROOT / "outputs" / "figures" / "transition_matrix.png"


def transition_matrix(
    df: pd.DataFrame,
    output_path: Union[str, Path] = DEFAULT_TRANSITION_TABLE_PATH,
    fig_path: Union[str, Path] = DEFAULT_HEATMAP_PATH
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Constructs an origination grade-to-final outcome transition matrix with row-normalized probabilities.

    Parameters
    ----------
    df : pd.DataFrame
        Loan DataFrame containing 'grade' and 'loan_status'.

    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame]
        Row-normalized transition matrix DataFrame and raw count matrix DataFrame.
    """
    if "grade" not in df.columns or "loan_status" not in df.columns:
        raise KeyError("DataFrame must contain 'grade' and 'loan_status' columns.")

    df_calc = df.copy()

    # Map raw loan status into standardized outcome buckets
    outcome_map = {
        "Fully Paid": "Fully Paid",
        "Current": "Current",
        "In Grace Period": "Late",
        "Late (16-30 days)": "Late",
        "Late (31-120 days)": "Late",
        "Charged Off": "Default",
        "Default": "Default"
    }

    df_calc["outcome"] = df_calc["loan_status"].map(outcome_map).fillna("Other")

    # Order grades A->G and outcomes Fully Paid, Current, Late, Default
    grades_order = [g for g in ["A", "B", "C", "D", "E", "F", "G"] if g in df_calc["grade"].unique()]
    outcomes_order = ["Fully Paid", "Current", "Late", "Default"]

    # Compute raw counts
    counts_df = (
        df_calc.groupby(["grade", "outcome"])
        .size()
        .unstack(fill_value=0)
        .reindex(index=grades_order, columns=outcomes_order, fill_value=0)
    )

    # Row-normalize to get transition probabilities (row sum = 1.0)
    row_sums = counts_df.sum(axis=1)
    norm_matrix = counts_df.div(row_sums, axis=0)

    # Add total loans column for context
    matrix_export = norm_matrix.copy()
    matrix_export.insert(0, "total_loans", row_sums)

    output_path = Path(output_path)
    fig_path = Path(fig_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig_path.parent.mkdir(parents=True, exist_ok=True)

    matrix_export.reset_index().to_csv(output_path, index=False)

    # Plot Heatmap using matplotlib directly
    fig, ax = plt.subplots(figsize=(8, 6))
    cax = ax.imshow(norm_matrix.values * 100.0, cmap="YlOrRd", aspect="auto")
    fig.colorbar(cax, label="Transition Probability (%)")

    # Add text annotations
    for i in range(len(grades_order)):
        for j in range(len(outcomes_order)):
            val = norm_matrix.values[i, j] * 100.0
            ax.text(j, i, f"{val:.2f}%", ha="center", va="center", color="black" if val < 50 else "white", fontsize=10, weight="bold")

    ax.set_xticks(range(len(outcomes_order)))
    ax.set_xticklabels(outcomes_order)
    ax.set_yticks(range(len(grades_order)))
    ax.set_yticklabels(grades_order)

    ax.set_title("Origination Rating Grade to Outcome Transition Matrix (%)", fontsize=13, pad=12)
    ax.set_xlabel("Final Outcome Status", fontsize=11)
    ax.set_ylabel("Origination Rating Grade", fontsize=11)

    plt.tight_layout()
    fig.savefig(fig_path, dpi=300)
    plt.close(fig)

    print("=" * 75)
    print(" ORIGINATION RATING GRADE TO OUTCOME TRANSITION MATRIX (ROW-NORMALIZED)")
    print("=" * 75)
    print(matrix_export.to_string())
    print("=" * 75)
    print(f"Saved Transition Matrix to: {output_path}")
    print(f"Saved Transition Heatmap to: {fig_path}")

    return norm_matrix, counts_df


def default_by_grade_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes observed default counts, total loans, and default rate per origination grade.
    """
    norm_matrix, counts_df = transition_matrix(df)

    summary_df = pd.DataFrame({
        "grade": counts_df.index,
        "total_loans": counts_df.sum(axis=1).values,
        "default_count": counts_df["Default"].values,
        "default_rate_pct": norm_matrix["Default"].values * 100.0
    }).reset_index(drop=True)

    print("\nOBSERVED DEFAULT RATE BY ORIGINATION GRADE:")
    print(summary_df.to_string(index=False))

    return summary_df
