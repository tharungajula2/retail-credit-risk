"""
vintage.py
----------
Portfolio monitoring analytics module for vintage curve analysis and cohort seasoning.

1. vintage_curves(df): Computes cumulative default rate matrix across months-on-book (0..48)
   by origination vintage year, exports table and multi-vintage trend plot.
2. vintage_maturity_comparison(df): Compares cumulative default rates at fixed months-on-book
   (MOB 12, MOB 18) across vintage cohorts to evaluate underwriting quality changes over time.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from creditrisk.data.target import build_target

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_VINTAGE_CURVES_PATH = PROJECT_ROOT / "outputs" / "tables" / "vintage_curves.csv"
DEFAULT_MATURITY_PATH = PROJECT_ROOT / "outputs" / "tables" / "vintage_maturity_comparison.csv"
DEFAULT_VINTAGE_PLOT_PATH = PROJECT_ROOT / "outputs" / "figures" / "vintage_curves.png"


def vintage_curves(
    df: pd.DataFrame,
    max_mob: int = 48,
    output_path: Union[str, Path] = DEFAULT_VINTAGE_CURVES_PATH,
    fig_path: Union[str, Path] = DEFAULT_VINTAGE_PLOT_PATH
) -> pd.DataFrame:
    """
    Computes cumulative default rate matrix across months-on-book (MOB 0..max_mob) by vintage year.

    Parameters
    ----------
    df : pd.DataFrame
        Loan DataFrame containing 'vintage_year', 'ever_default', and 'months_to_default'.
    max_mob : int
        Maximum month-on-book (default 48).

    Returns
    -------
    pd.DataFrame
        Matrix with rows = vintage_year and columns = mob_0, mob_1, ..., mob_max_mob.
    """
    if "vintage_year" not in df.columns or "ever_default" not in df.columns:
        df_target = build_target(df)
    else:
        df_target = df.copy()

    vintage_years = sorted(df_target["vintage_year"].dropna().unique())
    mob_cols = [f"mob_{m}" for m in range(max_mob + 1)]

    matrix_rows = []

    for v_year in vintage_years:
        v_df = df_target[df_target["vintage_year"] == v_year]
        v_total = len(v_df)

        if v_total == 0:
            continue

        v_defaults = v_df[v_df["ever_default"] == 1]
        m_def = v_defaults["months_to_default"].fillna(1).astype(int)

        row_vals = [0.0]  # MOB 0 cumulative default rate is 0.0

        for m in range(1, max_mob + 1):
            # Defaults occurring on or before month m
            cum_defs = (m_def <= m).sum()
            cum_def_rate = cum_defs / v_total
            row_vals.append(cum_def_rate)

        row_dict = {"vintage_year": int(v_year), "total_loans": v_total}
        for mob_col, val in zip(mob_cols, row_vals):
            row_dict[mob_col] = val

        matrix_rows.append(row_dict)

    vintage_matrix = pd.DataFrame(matrix_rows)

    # Save summary table
    output_path = Path(output_path)
    fig_path = Path(fig_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig_path.parent.mkdir(parents=True, exist_ok=True)

    vintage_matrix.to_csv(output_path, index=False)

    # Plot Multi-Vintage Trend Chart
    fig, ax = plt.subplots(figsize=(10, 6))

    colors = plt.cm.tab10(np.linspace(0, 1, len(vintage_matrix)))
    mobs = list(range(max_mob + 1))

    for idx, row in vintage_matrix.iterrows():
        v_year = int(row["vintage_year"])
        y_vals = [row[f"mob_{m}"] * 100.0 for m in mobs]
        ax.plot(mobs, y_vals, marker='o', markersize=3, label=f"Vintage {v_year}", color=colors[idx], linewidth=2)

    ax.set_title("Vintage Cumulative Default Curves by Origination Cohort (MOB 0–48)", fontsize=13, pad=12)
    ax.set_xlabel("Months on Book (MOB / Seasoning Age)", fontsize=11)
    ax.set_ylabel("Cumulative Default Rate (%)", fontsize=11)
    ax.legend(title="Origination Vintage", loc="upper left")
    ax.grid(True, linestyle="--", alpha=0.5)

    plt.tight_layout()
    fig.savefig(fig_path, dpi=300)
    plt.close(fig)

    print("=" * 70)
    print(f"Saved Vintage Curves matrix to: {output_path}")
    print(f"Saved Vintage Curves plot to: {fig_path}")

    return vintage_matrix


def vintage_maturity_comparison(
    df: pd.DataFrame,
    milestone_mobs: List[int] = [12, 18, 24],
    output_path: Union[str, Path] = DEFAULT_MATURITY_PATH
) -> pd.DataFrame:
    """
    Compares cumulative default rates at fixed months-on-book (e.g., MOB 12, MOB 18, MOB 24)
    across origination vintage years.
    """
    matrix = vintage_curves(df, max_mob=max(milestone_mobs))

    cols = ["vintage_year", "total_loans"] + [f"mob_{m}" for m in milestone_mobs]
    maturity_df = matrix[cols].copy()

    # Rename columns for clarity
    rename_dict = {f"mob_{m}": f"default_rate_mob_{m}" for m in milestone_mobs}
    maturity_df.rename(columns=rename_dict, inplace=True)

    # Express default rates as percentage
    for m in milestone_mobs:
        col_name = f"default_rate_mob_{m}"
        maturity_df[f"{col_name}_pct"] = maturity_df[col_name] * 100.0

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    maturity_df.to_csv(output_path, index=False)

    print("=" * 75)
    print(" VINTAGE MATURITY COMPARISON (FIXED MONTHS-ON-BOOK)")
    print("=" * 75)
    print(maturity_df.to_string(index=False))
    print("=" * 75)
    print(f"Saved Vintage Maturity comparison table to: {output_path}")

    return maturity_df
