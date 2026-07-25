"""
macro_scenarios.py
------------------
IFRS 9 Forward-Looking Macroeconomic Scenarios and Performing-Book Comparison Module.

Implements:
1. Forward-looking scenario ECL modeling (Baseline, Upside, Downside) using PD scalar multipliers.
   DOCUMENTED SIMPLIFICATION:
   In commercial banking practice, macro models link PD/LGD dynamically to GDP growth, unemployment,
   and house price indices (HPI). Here we utilize direct PD scenario multipliers as a documented proxy.
2. Probability-weighted ECL aggregation (IFRS 9 reported financial statement provision).
3. Performing-book ECL comparison (Stage 1 + Stage 2 loans only) vs Basel Regulatory EL.
"""

from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union
import numpy as np
import pandas as pd
import yaml

from creditrisk.features.binning import WoEBinner
from creditrisk.models.lgd_model import TwoStageLGD
from creditrisk.models.pd_model import PDModel
from creditrisk.regulatory.ecl import compute_ecl

PROJECT_ROOT = Path(__file__).resolve().parents[3]
CONFIG_PATH = PROJECT_ROOT / "config" / "macro_scenarios.yaml"
DEFAULT_WEIGHTED_PATH = PROJECT_ROOT / "outputs" / "tables" / "ecl_scenario_weighted.csv"
DEFAULT_PERFORMING_PATH = PROJECT_ROOT / "outputs" / "tables" / "ifrs9_vs_basel_performing.csv"


def load_macro_config(config_path: Union[str, Path] = CONFIG_PATH) -> Dict[str, Any]:
    """Loads forward-looking macroeconomic scenarios from YAML file."""
    path = Path(config_path)
    if not path.exists():
        return {
            "scenarios": {
                "baseline": {"pd_multiplier": 1.00, "weight": 0.50},
                "upside": {"pd_multiplier": 0.85, "weight": 0.20},
                "downside": {"pd_multiplier": 1.50, "weight": 0.30}
            }
        }
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def scenario_ecl(
    df: pd.DataFrame,
    pd_multiplier: float,
    pd_model: Optional[PDModel] = None,
    lgd_model: Optional[TwoStageLGD] = None,
    woe_binner_pd: Optional[WoEBinner] = None,
    term_structure: Optional[pd.DataFrame] = None
) -> pd.DataFrame:
    """
    Recomputes IFRS 9 ECL for a specific macroeconomic scenario with PD scaled by pd_multiplier.
    """
    # First compute baseline ECL variables
    df_out = compute_ecl(
        df,
        pd_model=pd_model,
        lgd_model=lgd_model,
        woe_binner_pd=woe_binner_pd,
        term_structure=term_structure
    )

    if pd_multiplier == 1.0:
        return df_out

    # Scale 12m PD and lifetime PD for non-defaulted loans (Stage 1 and Stage 2)
    stg3_mask = (df_out["stage"] == "Stage 3")
    
    scaled_pd_12m = np.where(stg3_mask, 1.0, np.clip(df_out["current_pd_12m"] * pd_multiplier, 0.0, 1.0))
    scaled_lifetime_pd = np.where(stg3_mask, 1.0, np.clip(df_out["lifetime_pd"] * pd_multiplier, 0.0, 1.0))

    df_out["current_pd_12m"] = scaled_pd_12m
    df_out["lifetime_pd"] = scaled_lifetime_pd

    # Recompute ECL with scaled PDs
    stg1_mask = (df_out["stage"] == "Stage 1")
    stg2_mask = (df_out["stage"] == "Stage 2")

    ecl_stg1 = df_out["current_pd_12m"] * df_out["lgd_hat"] * df_out["ead"] * df_out["discount_factor"]
    ecl_stg2 = df_out["lifetime_pd"] * df_out["lgd_hat"] * df_out["ead"] * df_out["discount_factor"]
    ecl_stg3 = 1.0 * df_out["lgd_hat"] * df_out["ead"]

    df_out["ecl"] = np.where(stg3_mask, ecl_stg3, np.where(stg2_mask, ecl_stg2, ecl_stg1))
    return df_out


def probability_weighted_ecl(
    df: pd.DataFrame,
    pd_model: Optional[PDModel] = None,
    lgd_model: Optional[TwoStageLGD] = None,
    woe_binner_pd: Optional[WoEBinner] = None,
    term_structure: Optional[pd.DataFrame] = None,
    config_path: Union[str, Path] = CONFIG_PATH,
    output_path: Union[str, Path] = DEFAULT_WEIGHTED_PATH
) -> Tuple[pd.DataFrame, float, Dict[str, pd.DataFrame]]:
    """
    Computes scenario ECLs and the final IFRS 9 probability-weighted ECL financial provision.

    Formula:
    Reported IFRS 9 ECL = sum(Scenario_ECL_i * Scenario_Weight_i)

    Returns
    -------
    Tuple[pd.DataFrame, float, Dict[str, pd.DataFrame]]
        Scenario summary table, final weighted ECL total, and dict of scenario DataFrames.
    """
    cfg = load_macro_config(config_path)
    scenarios_cfg = cfg.get("scenarios", {})

    # Validate weights sum to 1.0
    total_weight = sum(sc.get("weight", 0.0) for sc in scenarios_cfg.values())
    if not np.isclose(total_weight, 1.0, atol=1e-3):
        raise ValueError(f"Scenario weights must sum to 1.0 (got {total_weight:.4f}).")

    scenario_results = []
    scenario_dfs = {}
    weighted_ecl_total = 0.0
    total_ead = float(df["ead"].sum()) if "ead" in df.columns else 0.0

    for sc_name, sc_info in scenarios_cfg.items():
        mult = sc_info.get("pd_multiplier", 1.0)
        w = sc_info.get("weight", 0.0)

        df_sc = scenario_ecl(
            df,
            pd_multiplier=mult,
            pd_model=pd_model,
            lgd_model=lgd_model,
            woe_binner_pd=woe_binner_pd,
            term_structure=term_structure
        )
        scenario_dfs[sc_name] = df_sc

        if total_ead == 0.0:
            total_ead = float(df_sc["ead"].sum())

        sc_ecl_total = float(df_sc["ecl"].sum())
        weighted_contrib = sc_ecl_total * w
        weighted_ecl_total += weighted_contrib

        scenario_results.append({
            "scenario": sc_name.capitalize(),
            "pd_multiplier": mult,
            "weight": w,
            "scenario_ecl": sc_ecl_total,
            "weighted_ecl_contribution": weighted_contrib,
            "ecl_pct_ead": (sc_ecl_total / total_ead * 100.0) if total_ead > 0 else 0.0
        })

    summary_table = pd.DataFrame(scenario_results)

    # Final Probability-Weighted Total Row
    final_row = pd.DataFrame([{
        "scenario": "Probability-Weighted Total (Reported IFRS 9)",
        "pd_multiplier": 1.00,
        "weight": 1.00,
        "scenario_ecl": weighted_ecl_total,
        "weighted_ecl_contribution": weighted_ecl_total,
        "ecl_pct_ead": (weighted_ecl_total / total_ead * 100.0) if total_ead > 0 else 0.0
    }])

    summary_combined = pd.concat([summary_table, final_row], ignore_index=True)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary_combined.to_csv(output_path, index=False)

    print("=" * 80)
    print(" IFRS 9 FORWARD-LOOKING MACROECONOMIC SCENARIO ECL SUMMARY")
    print("=" * 80)
    print(summary_combined.to_string(index=False))
    print("=" * 80)
    print(f"Saved Probability-Weighted ECL summary to: {output_path}")

    return summary_combined, weighted_ecl_total, scenario_dfs


def ecl_performing_only(
    df_ecl: pd.DataFrame,
    df_basel_el: pd.DataFrame,
    output_path: Union[str, Path] = DEFAULT_PERFORMING_PATH
) -> pd.DataFrame:
    """
    Computes IFRS 9 ECL on Stage 1 + Stage 2 performing loans only for a like-for-like
    comparison against Basel Regulatory EL on performing exposures.

    Saves summary to output_path.
    """
    # Filter performing loans (Stage 1 + Stage 2)
    perf_mask_ecl = df_ecl["stage"].isin(["Stage 1", "Stage 2"])
    perf_ecl_df = df_ecl[perf_mask_ecl]

    perf_count = len(perf_ecl_df)
    perf_ead = float(perf_ecl_df["ead"].sum())
    perf_ifrs9_ecl = float(perf_ecl_df["ecl"].sum())

    # Basel EL on performing loans
    if "ever_default" in df_basel_el.columns:
        perf_mask_basel = (df_basel_el["ever_default"] == 0)
        perf_basel_df = df_basel_el[perf_mask_basel]
    else:
        perf_basel_df = df_basel_el.iloc[perf_mask_ecl.values]

    perf_basel_el = float(perf_basel_df["el"].sum())

    comp_df = pd.DataFrame([
        {
            "scope": "Performing Portfolio (Stage 1 + Stage 2)",
            "metric": "Basel III Regulatory EL",
            "count": perf_count,
            "total_ead": perf_ead,
            "provision_usd": perf_basel_el,
            "coverage_pct_ead": (perf_basel_el / perf_ead * 100.0) if perf_ead > 0 else 0.0,
            "description": "12-Month Expected Loss on performing loans"
        },
        {
            "scope": "Performing Portfolio (Stage 1 + Stage 2)",
            "metric": "IFRS 9 Performing ECL (Staged)",
            "count": perf_count,
            "total_ead": perf_ead,
            "provision_usd": perf_ifrs9_ecl,
            "coverage_pct_ead": (perf_ifrs9_ecl / perf_ead * 100.0) if perf_ead > 0 else 0.0,
            "description": "Staged ECL (Stage 1 12m + Stage 2 Lifetime) on performing loans"
        },
        {
            "scope": "Performing Portfolio (Stage 1 + Stage 2)",
            "metric": "IFRS 9 vs Basel Delta (Difference)",
            "count": perf_count,
            "total_ead": 0.0,
            "provision_usd": perf_ifrs9_ecl - perf_basel_el,
            "coverage_pct_ead": ((perf_ifrs9_ecl - perf_basel_el) / perf_ead * 100.0) if perf_ead > 0 else 0.0,
            "description": "Additional performing-book provision under IFRS 9 due to Stage 2 Lifetime ECL"
        }
    ])

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    comp_df.to_csv(output_path, index=False)

    print("=" * 80)
    print(" PERFORMING PORTFOLIO PROVISION COMPARISON: IFRS 9 vs BASEL REGULATORY EL")
    print("=" * 80)
    print(comp_df.to_string(index=False))
    print("=" * 80)
    print(f"Saved performing-book comparison summary to: {output_path}")

    return comp_df
