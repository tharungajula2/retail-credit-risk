"""
target.py
---------
Target engineering module for 12-month Probability of Default (PD) modeling.

Provides functions to parse LendingClub dates with century rollover fixes,
construct 12-month default target labels based on DPD lag windows, and compute
vintage summary statistics across loan origination cohorts.
"""

from pathlib import Path
from typing import Any, Dict, Union
import numpy as np
import pandas as pd
import yaml

CONFIG_PATH = Path(__file__).resolve().parents[3] / "config" / "target_definition.yaml"
OUTPUT_TABLE_PATH = Path(__file__).resolve().parents[3] / "outputs" / "tables" / "target_summary_by_vintage.csv"


def load_target_config(config: Union[Dict[str, Any], Path, str] = CONFIG_PATH) -> Dict[str, Any]:
    """
    Loads target configuration parameters from a YAML file path or returns the dict if provided.
    """
    if isinstance(config, (str, Path)):
        path = Path(config)
        if not path.exists():
            raise FileNotFoundError(f"Target configuration file not found at: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    elif isinstance(config, dict):
        return config
    else:
        raise TypeError("Config must be a dictionary or a valid file path.")


def parse_lc_date(series: pd.Series) -> pd.Series:
    """
    Parses LendingClub string dates (e.g., 'Dec-68', 'Jun-14') in '%b-%y' format.

    CRITICAL CENTURY CORRECTION:
    pandas interprets two-digit years like '68' as 2068. Any resulting year > 2015
    has 100 years subtracted so 'Dec-68' correctly evaluates to 1968-12-01.

    Parameters
    ----------
    series : pd.Series
        String date series in '%b-%y' format.

    Returns
    -------
    pd.Series
        Datetime pd.Series with corrected years.
    """
    parsed = pd.to_datetime(series, format="%b-%y", errors="coerce")

    # Correct century rollover where pandas parsed 20th century years into 21st century (e.g. 2068 -> 1968).
    # Threshold set to > 2049 so legitimate dates up to 2016/2025 (like 'Jan-16') are preserved as 2016.
    future_year_mask = parsed.dt.year > 2049
    parsed = parsed.mask(future_year_mask, parsed - pd.DateOffset(years=100))

    return parsed


def build_target(df: pd.DataFrame, config: Union[Dict[str, Any], Path, str] = CONFIG_PATH) -> pd.DataFrame:
    """
    Constructs default target flags, estimated default dates, and vintage tracking columns.

    New Columns Created:
    - ever_default        : 1 if loan_status is in default_statuses else 0
    - est_default_date    : last_pymnt_d + days_past_due_lag_months for default loans (or issue_d if last_pymnt_d missing)
    - months_to_default   : whole months from issue_d to est_default_date
    - default_12m         : 1 if ever_default == 1 AND months_to_default <= 12, else 0
    - vintage_year        : Year of origination (from issue_d)
    - vintage_quarter     : Year and Quarter of origination (e.g., '2014Q1')

    Parameters
    ----------
    df : pd.DataFrame
        Raw or processed loan DataFrame containing 'loan_status', 'issue_d', 'last_pymnt_d'.
    config : dict or Path
        Target configuration parameters.

    Returns
    -------
    pd.DataFrame
        Copy of input DataFrame augmented with target flags.
    """
    cfg = load_target_config(config)
    default_statuses = set(cfg.get("default_statuses", []))
    lag_months = cfg.get("days_past_due_lag_months", 3)
    perf_window = cfg.get("performance_window_months", 12)

    df_out = df.copy()

    # 1. Identify ever-default loans
    df_out["ever_default"] = df_out["loan_status"].isin(default_statuses).astype(int)

    # 2. Parse origination and payment dates with century fix
    parsed_issue = parse_lc_date(df_out["issue_d"])
    parsed_last_pymnt = parse_lc_date(df_out["last_pymnt_d"])

    # 3. Estimate default event date (last payment date + 3 months DPD lag)
    # If last_pymnt_d is missing for a default loan, assume default occurred relative to issue_d
    est_default = parsed_last_pymnt + pd.DateOffset(months=lag_months)
    est_default = est_default.fillna(parsed_issue)

    # Only assign estimated default date to defaulted loans
    df_out["est_default_date"] = np.where(df_out["ever_default"] == 1, est_default, pd.NaT)
    df_out["est_default_date"] = pd.to_datetime(df_out["est_default_date"])

    # 4. Compute whole months from origination to estimated default date
    est_def_dt = df_out["est_default_date"]
    months_diff = (est_def_dt.dt.year - parsed_issue.dt.year) * 12 + (est_def_dt.dt.month - parsed_issue.dt.month)

    df_out["months_to_default"] = np.where(df_out["ever_default"] == 1, months_diff, np.nan)

    # 5. Build binary 12-month default target flag
    is_def_12m = (df_out["ever_default"] == 1) & (df_out["months_to_default"] <= perf_window) & (df_out["months_to_default"] >= 0)
    df_out["default_12m"] = is_def_12m.astype(int)

    # 6. Extract vintage cohort indicators
    df_out["vintage_year"] = parsed_issue.dt.year
    df_out["vintage_quarter"] = parsed_issue.dt.year.astype(str) + "Q" + parsed_issue.dt.quarter.astype(str)

    return df_out


def target_summary(df: pd.DataFrame, output_path: Path = OUTPUT_TABLE_PATH) -> pd.DataFrame:
    """
    Computes vintage summary statistics (loan count, ever-default count/rate, 12m default count/rate)
    grouped by vintage_year and exports the results to a CSV file.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame produced by build_target.
    output_path : Path, optional
        Destination path for the summary CSV.

    Returns
    -------
    pd.DataFrame
        Summary table grouped by vintage year.
    """
    grouped = df.groupby("vintage_year", as_index=False).agg(
        n_loans=("loan_status", "count"),
        n_ever_default=("ever_default", "sum"),
        n_default_12m=("default_12m", "sum"),
    )

    grouped["ever_default_rate"] = grouped["n_ever_default"] / grouped["n_loans"]
    grouped["default_12m_rate"] = grouped["n_default_12m"] / grouped["n_loans"]

    # Reorder columns as requested
    summary_df = grouped[
        ["vintage_year", "n_loans", "n_ever_default", "ever_default_rate", "n_default_12m", "default_12m_rate"]
    ]

    # Save to CSV
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary_df.to_csv(output_path, index=False)
    print(f"Vintage summary saved to: {output_path}")

    return summary_df
