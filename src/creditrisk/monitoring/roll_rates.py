"""
roll_rates.py
-------------
Roll-rate and delinquency status transition proxy module.

DOCUMENTED DATA LIMITATION:
A true roll-rate transition matrix requires a longitudinal monthly panel dataset tracking individual
loan delinquency states from month t-1 to month t (computing exact roll-forward, cure, and roll-backward rates).
Because LendingClub data represents a cross-sectional snapshot rather than a monthly panel, this module
constructs a delinquency distribution and roll-rate proxy by vintage year.
"""

from pathlib import Path
from typing import Any, Dict, Tuple, Union
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_ROLL_RATE_PATH = PROJECT_ROOT / "outputs" / "tables" / "roll_rate_proxy.csv"


def roll_rate_proxy(
    df: pd.DataFrame,
    output_path: Union[str, Path] = DEFAULT_ROLL_RATE_PATH
) -> pd.DataFrame:
    """
    Constructs a delinquency status distribution and roll-rate proxy table by vintage year.

    Parameters
    ----------
    df : pd.DataFrame
        Loan DataFrame containing 'loan_status' and 'vintage_year' or 'issue_d'.

    Returns
    -------
    pd.DataFrame
        Roll-rate proxy summary table across status buckets.
    """
    df_calc = df.copy()

    if "vintage_year" not in df_calc.columns:
        if "issue_d" in df_calc.columns:
            df_calc["vintage_year"] = pd.to_datetime(df_calc["issue_d"], format="%b-%y", errors="coerce").dt.year
        else:
            df_calc["vintage_year"] = "All"

    # Map loan status into standardized delinquency buckets
    status_map = {
        "Fully Paid": "Fully Paid / Cured",
        "Current": "Current (Performing)",
        "In Grace Period": "In Grace Period (1-15 DPD)",
        "Late (16-30 days)": "Late 16-30 DPD",
        "Late (31-120 days)": "Late 31-120 DPD",
        "Charged Off": "Default / Charged Off",
        "Default": "Default / Charged Off"
    }

    df_calc["status_bucket"] = df_calc["loan_status"].map(status_map).fillna("Other")

    # Aggregate counts by vintage_year and status_bucket
    pivot_counts = (
        df_calc.groupby(["vintage_year", "status_bucket"])
        .size()
        .unstack(fill_value=0)
    )

    pivot_pcts = pivot_counts.div(pivot_counts.sum(axis=1), axis=0) * 100.0

    summary_rows = []
    for v_year in pivot_counts.index:
        row_dict = {
            "NOTICE": "[CROSS-SECTIONAL PROXY - NOT MONTHLY PANEL]",
            "vintage_year": v_year,
            "total_loans": int(pivot_counts.loc[v_year].sum()),
            "current_pct": float(pivot_pcts.loc[v_year].get("Current (Performing)", 0.0)),
            "grace_period_pct": float(pivot_pcts.loc[v_year].get("In Grace Period (1-15 DPD)", 0.0)),
            "late_16_30_pct": float(pivot_pcts.loc[v_year].get("Late 16-30 DPD", 0.0)),
            "late_31_120_pct": float(pivot_pcts.loc[v_year].get("Late 31-120 DPD", 0.0)),
            "default_charged_off_pct": float(pivot_pcts.loc[v_year].get("Default / Charged Off", 0.0)),
            "fully_paid_pct": float(pivot_pcts.loc[v_year].get("Fully Paid / Cured", 0.0))
        }
        summary_rows.append(row_dict)

    roll_rate_df = pd.DataFrame(summary_rows)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    roll_rate_df.to_csv(output_path, index=False)

    print("=" * 80)
    print(" DELINQUENCY ROLL-RATE PROXY TABLE BY VINTAGE")
    print("=" * 80)
    print(roll_rate_df.to_string(index=False))
    print("=" * 80)
    print(f"Saved Roll-Rate Proxy table to: {output_path}")

    return roll_rate_df
