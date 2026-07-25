"""
ecl.py
------
IFRS 9 and US CECL Expected Credit Loss (ECL) provisioning engine.

Stage 1: 12-month ECL = pd_12m * lgd * ead * discount_factor
Stage 2: Lifetime ECL = lifetime_pd * lgd * ead * discount_factor
Stage 3: Credit-Impaired ECL = 1.0 * lgd * ead (already defaulted, PD = 1)

EIR Discounting:
Discounts future credit losses using loan Effective Interest Rate (int_rate / 100.0)
over expected time-to-default t (years). Documented as simplified EIR discounting.

US CECL Contrast:
Under US CECL (ASC 326), ALL performing loans require lifetime ECL from day one without staging.
"""

from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union
import numpy as np
import pandas as pd

from creditrisk.features.binning import WoEBinner
from creditrisk.models.ead_model import get_portfolio_ead
from creditrisk.models.lgd_model import TwoStageLGD
from creditrisk.models.pd_model import PDModel
from creditrisk.regulatory.lifetime_pd import (
    build_hazard_curve,
    compute_remaining_term,
    scale_lifetime_to_account
)
from creditrisk.regulatory.staging import assign_ifrs9_stages

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_ECL_SUMMARY_PATH = PROJECT_ROOT / "outputs" / "tables" / "ecl_summary.csv"
DEFAULT_CECL_COMPARE_PATH = PROJECT_ROOT / "outputs" / "tables" / "ifrs9_vs_cecl.csv"


def compute_ecl(
    df: pd.DataFrame,
    pd_model: Optional[PDModel] = None,
    lgd_model: Optional[TwoStageLGD] = None,
    woe_binner_pd: Optional[WoEBinner] = None,
    term_structure: Optional[pd.DataFrame] = None,
    snapshot_date: str = "2016-01-31"
) -> pd.DataFrame:
    """
    Computes IFRS 9 Expected Credit Loss (ECL) for every loan in the portfolio.

    Parameters
    ----------
    df : pd.DataFrame
        Loan portfolio DataFrame.
    pd_model : Optional[PDModel]
        Fitted PD Model B.
    lgd_model : Optional[TwoStageLGD]
        Fitted TwoStageLGD model.
    woe_binner_pd : Optional[WoEBinner]
        Fitted PD WoEBinner.
    term_structure : Optional[pd.DataFrame]
        Lifetime PD term structure table.
    snapshot_date : str
        Reporting snapshot date.

    Returns
    -------
    pd.DataFrame
        DataFrame augmented with `stage`, `current_pd_12m`, `lifetime_pd`, `lgd_hat`, `ead`, `discount_factor`, `ecl`.
    """
    df_out = assign_ifrs9_stages(df, pd_model=pd_model, woe_binner_pd=woe_binner_pd)

    # LGD prediction
    if "lgd_hat" not in df_out.columns:
        if lgd_model is not None:
            df_out["lgd_hat"] = lgd_model.predict_lgd(df_out)
        else:
            df_out["lgd_hat"] = 0.93  # default fallback

    # EAD calculation
    if "ead" not in df_out.columns:
        df_out["ead"] = get_portfolio_ead(df_out)

    # Remaining term & Lifetime PD calculation
    if "remaining_term" not in df_out.columns:
        df_out["remaining_term"] = compute_remaining_term(df_out, snapshot_date=snapshot_date)

    if term_structure is None:
        # Build default term structure if not provided
        if "months_to_default" in df_out.columns:
            term_structure = build_hazard_curve(df_out, max_months=60)
        else:
            # Fallback simple linear scale
            term_structure = pd.DataFrame({
                "month": list(range(1, 61)),
                "cumulative_pd": np.linspace(0.003, 0.11, 60)
            })

    if "lifetime_pd" not in df_out.columns:
        df_out["lifetime_pd"] = scale_lifetime_to_account(
            df_out["current_pd_12m"],
            df_out["remaining_term"],
            term_structure
        )

    # EIR Discounting calculation
    # int_rate in percentage (e.g. 12.5 -> 0.125)
    eir = (df_out["int_rate"].fillna(12.0) / 100.0).astype(float) if "int_rate" in df_out.columns else 0.12
    t_years = (df_out["remaining_term"] / 24.0).astype(float)  # average expected time-to-default proxy
    df_out["discount_factor"] = 1.0 / np.power(1.0 + eir, t_years)

    # Staged ECL calculation
    stg1_mask = (df_out["stage"] == "Stage 1")
    stg2_mask = (df_out["stage"] == "Stage 2")
    stg3_mask = (df_out["stage"] == "Stage 3")

    ecl_stg1 = df_out["current_pd_12m"] * df_out["lgd_hat"] * df_out["ead"] * df_out["discount_factor"]
    ecl_stg2 = df_out["lifetime_pd"] * df_out["lgd_hat"] * df_out["ead"] * df_out["discount_factor"]
    ecl_stg3 = 1.0 * df_out["lgd_hat"] * df_out["ead"]  # Undiscounted Stage 3 default loss

    df_out["ecl"] = np.where(stg3_mask, ecl_stg3, np.where(stg2_mask, ecl_stg2, ecl_stg1))
    return df_out


def compute_cecl(
    df: pd.DataFrame,
    pd_model: Optional[PDModel] = None,
    lgd_model: Optional[TwoStageLGD] = None,
    woe_binner_pd: Optional[WoEBinner] = None,
    term_structure: Optional[pd.DataFrame] = None
) -> pd.DataFrame:
    """
    Computes US CECL (ASC 326) provision:
    Under US CECL, ALL performing loans require Lifetime ECL from day one (no staging).

    CECL Formula:
    - Performing loans (Stage 1 & Stage 2): CECL = lifetime_pd * lgd * ead * discount_factor
    - Impaired loans (Stage 3): CECL = 1.0 * lgd * ead
    """
    df_ecl = compute_ecl(
        df,
        pd_model=pd_model,
        lgd_model=lgd_model,
        woe_binner_pd=woe_binner_pd,
        term_structure=term_structure
    )

    df_cecl = df_ecl.copy()
    stg3_mask = (df_cecl["stage"] == "Stage 3")

    cecl_performing = df_cecl["lifetime_pd"] * df_cecl["lgd_hat"] * df_cecl["ead"] * df_cecl["discount_factor"]
    cecl_defaulted = 1.0 * df_cecl["lgd_hat"] * df_cecl["ead"]

    df_cecl["cecl"] = np.where(stg3_mask, cecl_defaulted, cecl_performing)
    return df_cecl


def ecl_summary(
    df: pd.DataFrame,
    output_path: Union[str, Path] = DEFAULT_ECL_SUMMARY_PATH
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Generates IFRS 9 ECL summary table by stage: total ECL, ECL % of EAD, coverage ratio (ECL / EAD).

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame processed via compute_ecl.
    output_path : str or Path
        Destination CSV path.

    Returns
    -------
    Tuple[pd.DataFrame, Dict[str, Any]]
        Summary DataFrame and metrics dictionary.
    """
    for col in ["stage", "ead", "ecl"]:
        if col not in df.columns:
            raise KeyError(f"Missing required column '{col}' for ECL summary.")

    total_count = len(df)
    total_ead = float(df["ead"].sum())
    total_ecl = float(df["ecl"].sum())

    summary_df = (
        df.groupby("stage")
        .agg(
            count=("ecl", "count"),
            total_ead=("ead", "sum"),
            total_ecl=("ecl", "sum")
        )
        .reset_index()
    )

    summary_df["ecl_pct_ead"] = np.where(summary_df["total_ead"] > 0, summary_df["total_ecl"] / summary_df["total_ead"] * 100.0, 0.0)
    summary_df["coverage_ratio"] = np.where(summary_df["total_ead"] > 0, summary_df["total_ecl"] / summary_df["total_ead"], 0.0)

    # Stage order
    order_map = {"Stage 1": 1, "Stage 2": 2, "Stage 3": 3}
    summary_df["order"] = summary_df["stage"].map(order_map).fillna(4)
    summary_df = summary_df.sort_values("order").drop(columns=["order"]).reset_index(drop=True)

    total_row = pd.DataFrame([{
        "stage": "Total Portfolio",
        "count": total_count,
        "total_ead": total_ead,
        "total_ecl": total_ecl,
        "ecl_pct_ead": (total_ecl / total_ead * 100.0) if total_ead > 0 else 0.0,
        "coverage_ratio": (total_ecl / total_ead) if total_ead > 0 else 0.0
    }])

    summary_combined = pd.concat([summary_df, total_row], ignore_index=True)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary_combined.to_csv(output_path, index=False)

    print("=" * 75)
    print(" IFRS 9 EXPECTED CREDIT LOSS (ECL) SUMMARY TABLE BY STAGE")
    print("=" * 75)
    print(summary_combined.to_string(index=False))
    print("=" * 75)
    print(f"Saved ECL summary to: {output_path}")

    metrics = {
        "total_count": total_count,
        "total_ead": total_ead,
        "total_ecl": total_ecl,
        "portfolio_coverage_ratio": float(total_ecl / total_ead) if total_ead > 0 else 0.0
    }

    return summary_combined, metrics


def compare_ifrs9_vs_cecl_vs_basel(
    df_ecl: pd.DataFrame,
    df_cecl: pd.DataFrame,
    total_basel_el: float,
    output_path: Union[str, Path] = DEFAULT_CECL_COMPARE_PATH
) -> pd.DataFrame:
    """
    Compares IFRS 9 ECL vs US CECL Provision vs Basel Regulatory EL side-by-side.
    Saves comparison table to output_path.
    """
    total_ead = float(df_ecl["ead"].sum())
    total_ifrs9_ecl = float(df_ecl["ecl"].sum())
    total_cecl_provision = float(df_cecl["cecl"].sum())

    comp_df = pd.DataFrame([
        {
            "accounting_framework": "Basel III Regulatory EL",
            "horizon_scope": "12-Month EL (PD_12m * LGD * EAD)",
            "total_provision_usd": total_basel_el,
            "coverage_pct_ead": (total_basel_el / total_ead * 100.0) if total_ead > 0 else 0.0,
            "notes": "Regulatory capital baseline (undiscounted 12m expected loss)"
        },
        {
            "accounting_framework": "IFRS 9 Financial Instruments",
            "horizon_scope": "Staged (Stage 1: 12m, Stage 2: Lifetime, Stage 3: Default)",
            "total_provision_usd": total_ifrs9_ecl,
            "coverage_pct_ead": (total_ifrs9_ecl / total_ead * 100.0) if total_ead > 0 else 0.0,
            "notes": "International accounting standard (discounted EIR, staged SICR)"
        },
        {
            "accounting_framework": "US CECL (ASC 326)",
            "horizon_scope": "Lifetime for ALL performing loans (Day-1 Lifetime)",
            "total_provision_usd": total_cecl_provision,
            "coverage_pct_ead": (total_cecl_provision / total_ead * 100.0) if total_ead > 0 else 0.0,
            "notes": "US GAAP accounting standard (no staging, lifetime from origination)"
        },
        {
            "accounting_framework": "CECL vs IFRS 9 Difference (Delta)",
            "horizon_scope": "Lifetime Day-1 Impact on Stage 1 Loans",
            "total_provision_usd": total_cecl_provision - total_ifrs9_ecl,
            "coverage_pct_ead": ((total_cecl_provision - total_ifrs9_ecl) / total_ead * 100.0) if total_ead > 0 else 0.0,
            "notes": "Additional provision required by US GAAP over IFRS 9"
        }
    ])

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    comp_df.to_csv(output_path, index=False)

    print("=" * 80)
    print(" ACCOUNTING & REGULATORY PROVISIONING COMPARISON: IFRS 9 vs US CECL vs BASEL EL")
    print("=" * 80)
    print(comp_df.to_string(index=False))
    print("=" * 80)
    print(f"Saved IFRS 9 vs CECL comparison table to: {output_path}")

    return comp_df
