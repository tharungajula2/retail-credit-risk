"""
lifetime_pd.py
--------------
Lifetime Probability of Default (PD) term structure engine for IFRS 9 / CECL Stage 2 modeling.

1. build_hazard_curve(df): Derives discrete-time monthly hazard rate, survival rate, and cumulative
   PD curve over months 1..60 from default timing data (months_to_default).
2. scale_lifetime_to_account(pd_12m, remaining_term, term_structure): Multiplicatively scales the
   portfolio term structure to an individual loan's 12-month PD, preserving account-level risk alignment.
3. compute_remaining_term(df, snapshot_date="2016-01-31"): Computes remaining loan term in months
   floored at 1 and capped at original term.
"""

from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from creditrisk.data.target import parse_lc_date

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SUMMARY_PATH = PROJECT_ROOT / "outputs" / "tables" / "lifetime_pd_term_structure.csv"
DEFAULT_FIGURE_PATH = PROJECT_ROOT / "outputs" / "figures" / "lifetime_pd_curve.png"
DEFAULT_SNAPSHOT_DATE = "2016-01-31"


def build_hazard_curve(
    df: pd.DataFrame,
    max_months: int = 60,
    output_path: Union[str, Path] = DEFAULT_SUMMARY_PATH,
    fig_path: Union[str, Path] = DEFAULT_FIGURE_PATH
) -> pd.DataFrame:
    """
    Computes discrete-time hazard, survival, and cumulative PD curve across months 1..max_months.

    Parameters
    ----------
    df : pd.DataFrame
        Loan DataFrame containing 'ever_default' and 'months_to_default'.
    max_months : int
        Maximum term duration in months (default 60).
    output_path : str or Path
        Destination CSV path.
    fig_path : str or Path
        Destination PNG plot path.

    Returns
    -------
    pd.DataFrame
        Table with columns [month, n_at_risk, n_defaults, hazard, survival, cumulative_pd].
    """
    if "ever_default" not in df.columns or "months_to_default" not in df.columns:
        raise KeyError("DataFrame must contain 'ever_default' and 'months_to_default' columns.")

    total_loans = len(df)
    def_df = df[df["ever_default"] == 1].copy()

    # Clean months_to_default: floor at 1
    m_def = np.maximum(def_df["months_to_default"].fillna(1).astype(int), 1)
    
    # Count defaults occurring in each month m=1..max_months
    default_counts_by_m = m_def.value_counts()

    records = []
    current_at_risk = total_loans
    cum_survival = 1.0

    for m in range(1, max_months + 1):
        n_def = int(default_counts_by_m.get(m, 0))
        n_risk = current_at_risk

        hazard = (n_def / n_risk) if n_risk > 0 else 0.0
        hazard = max(0.0, min(1.0, hazard))

        cum_survival = cum_survival * (1.0 - hazard)
        cum_pd = 1.0 - cum_survival

        records.append({
            "month": m,
            "n_at_risk": n_risk,
            "n_defaults": n_def,
            "hazard": hazard,
            "survival": cum_survival,
            "cumulative_pd": cum_pd
        })

        # Update at risk for start of next month (subtract defaults)
        current_at_risk = max(0, current_at_risk - n_def)

    term_table = pd.DataFrame(records)

    # Save summary table
    output_path = Path(output_path)
    fig_path = Path(fig_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig_path.parent.mkdir(parents=True, exist_ok=True)

    term_table.to_csv(output_path, index=False)

    # Plot Cumulative PD curve
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.plot(term_table["month"], term_table["cumulative_pd"] * 100.0, 'b-', linewidth=2.5, label="Cumulative PD (%)")
    ax.set_title("Portfolio Lifetime Cumulative PD Term Structure (1–60 Months)", fontsize=13, pad=12)
    ax.set_xlabel("Loan Seasoning Age (Months)", fontsize=11)
    ax.set_ylabel("Cumulative PD (%)", fontsize=11)
    ax.grid(True, linestyle="--", alpha=0.5)

    # Annotate key milestone months
    milestones = [6, 12, 18, 24, 36, 48, 60]
    for m in milestones:
        if m in term_table["month"].values:
            val = term_table.loc[term_table["month"] == m, "cumulative_pd"].values[0] * 100.0
            ax.scatter([m], [val], color="red", s=30, zorder=5)

    plt.tight_layout()
    fig.savefig(fig_path, dpi=300)
    plt.close(fig)

    print("=" * 65)
    print(f"Saved Lifetime PD Term Structure table to: {output_path}")
    print(f"Saved Lifetime PD Curve plot to: {fig_path}")

    return term_table


def scale_lifetime_to_account(
    pd_12m: Union[float, np.ndarray, pd.Series],
    remaining_term: Union[int, np.ndarray, pd.Series],
    term_structure: pd.DataFrame
) -> Union[float, np.ndarray, pd.Series]:
    """
    Scales the portfolio term structure multiplicatively to match an individual loan's 12-month PD.

    Parameters
    ----------
    pd_12m : float or array-like
        Loan's predicted 12-month PD.
    remaining_term : int or array-like
        Loan's remaining term in months.
    term_structure : pd.DataFrame
        Table generated by build_hazard_curve containing 'month' and 'cumulative_pd'.

    Returns
    -------
    float or array-like
        Scaled account-level lifetime PD.
    """
    ts_dict = dict(zip(term_structure["month"], term_structure["cumulative_pd"]))
    portfolio_pd_12m = ts_dict.get(12, 0.0)

    pd_12m_arr = np.maximum(np.asarray(pd_12m, dtype=float), 0.0)
    rem_term_arr = np.asarray(remaining_term, dtype=int)

    # Multiplicative scaling ratio (loan_pd_12m / portfolio_pd_12m)
    scale_factor = np.where(portfolio_pd_12m > 0, pd_12m_arr / portfolio_pd_12m, 1.0)

    # Look up portfolio cumulative PD at remaining_term (clamped between month 1 and max month)
    max_m = max(ts_dict.keys())
    clamped_term = np.clip(rem_term_arr, 1, max_m)
    if np.ndim(clamped_term) == 0:
        portfolio_cum_pd_at_rem = ts_dict.get(int(clamped_term), 0.0)
    else:
        portfolio_cum_pd_at_rem = np.array([ts_dict.get(int(m), 0.0) for m in clamped_term])

    scaled_lifetime_pd = np.clip(portfolio_cum_pd_at_rem * scale_factor, 0.0, 1.0)

    return float(scaled_lifetime_pd) if np.ndim(pd_12m) == 0 and np.ndim(remaining_term) == 0 else scaled_lifetime_pd


def compute_remaining_term(
    df: pd.DataFrame,
    snapshot_date: str = DEFAULT_SNAPSHOT_DATE
) -> pd.Series:
    """
    Computes remaining loan term in months as of snapshot_date.

    Remaining term = original_term_months - months_elapsed_since_issue.
    Floored at 1, capped at original_term_months.

    Parameters
    ----------
    df : pd.DataFrame
        Loan DataFrame containing 'issue_d' and 'term'.
    snapshot_date : str
        Reporting snapshot date string (default "2016-01-31").

    Returns
    -------
    pd.Series
        Remaining term in months aligned with df.index.
    """
    if "issue_d" not in df.columns or "term" not in df.columns:
        raise KeyError("DataFrame must contain 'issue_d' and 'term' columns.")

    parsed_issue = parse_lc_date(df["issue_d"])
    snap_dt = pd.to_datetime(snapshot_date)

    # Parse term months (e.g. ' 36 months' -> 36, ' 60 months' -> 60)
    term_months = (
        df["term"]
        .astype(str)
        .str.extract(r"(\d+)")
        .fillna(36)
        .astype(int)[0]
    )

    # Months elapsed from issue date to snapshot date
    elapsed_months = (snap_dt.year - parsed_issue.dt.year) * 12 + (snap_dt.month - parsed_issue.dt.month)
    elapsed_months = np.maximum(elapsed_months, 0)

    rem_term = term_months - elapsed_months
    rem_term_clamped = np.clip(rem_term, 1, term_months)

    return pd.Series(rem_term_clamped, index=df.index, name="remaining_term")
