"""
run_macro_scenarios.py
-----------------------
Execution script to evaluate forward-looking IFRS 9 macroeconomic scenarios (Baseline, Upside, Downside),
compute probability-weighted ECL provisions, and perform the performing-book IFRS 9 vs Basel EL comparison.
"""

from pathlib import Path
import pandas as pd

from creditrisk.features.binning import WoEBinner
from creditrisk.models.lgd_model import TwoStageLGD
from creditrisk.models.pd_model import PDModel
from creditrisk.regulatory.ecl import compute_ecl
from creditrisk.regulatory.expected_loss import compute_expected_loss
from creditrisk.regulatory.macro_scenarios import (
    ecl_performing_only,
    probability_weighted_ecl
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
OOT_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "oot.parquet"
PD_MODEL_B_PATH = PROJECT_ROOT / "outputs" / "models" / "pd_model_b.pkl"
WOE_BINNER_PD_PATH = PROJECT_ROOT / "outputs" / "models" / "woe_binner.pkl"
LGD_MODEL_PATH = PROJECT_ROOT / "outputs" / "models" / "lgd_model.pkl"
TERM_STRUCT_PATH = PROJECT_ROOT / "outputs" / "tables" / "lifetime_pd_term_structure.csv"
WEIGHTED_OUTPUT_PATH = PROJECT_ROOT / "outputs" / "tables" / "ecl_scenario_weighted.csv"
PERFORMING_OUTPUT_PATH = PROJECT_ROOT / "outputs" / "tables" / "ifrs9_vs_basel_performing.csv"


def main():
    print(f"Loading OOT (2014) portfolio dataset from: {OOT_DATA_PATH}...")
    df_oot = pd.read_parquet(OOT_DATA_PATH)
    print(f"OOT portfolio loaded ({len(df_oot):,} loans).")

    print("Loading model artifacts and term structure...")
    pd_model_b = PDModel.load(PD_MODEL_B_PATH)
    woe_binner_pd = WoEBinner.load(WOE_BINNER_PD_PATH)
    lgd_model = TwoStageLGD.load(LGD_MODEL_PATH)
    term_struct = pd.read_csv(TERM_STRUCT_PATH) if TERM_STRUCT_PATH.exists() else None

    # 1. Compute Probability-Weighted IFRS 9 ECL
    print("\nComputing IFRS 9 Forward-Looking Macroeconomic Scenario ECLs...")
    weighted_summary_df, weighted_total_ecl, scenario_dfs = probability_weighted_ecl(
        df_oot,
        pd_model=pd_model_b,
        lgd_model=lgd_model,
        woe_binner_pd=woe_binner_pd,
        term_structure=term_struct,
        output_path=WEIGHTED_OUTPUT_PATH
    )

    # 2. Compute Baseline ECL and Basel EL for Performing-Only Comparison
    df_baseline_ecl = scenario_dfs["baseline"]
    df_basel_el = compute_expected_loss(
        df_oot,
        pd_model=pd_model_b,
        lgd_model=lgd_model,
        woe_binner_pd=woe_binner_pd
    )

    print("\nEvaluating Performing-Only (Stage 1 + Stage 2) IFRS 9 ECL vs Basel EL Comparison...")
    perf_comp_df = ecl_performing_only(
        df_baseline_ecl,
        df_basel_el,
        output_path=PERFORMING_OUTPUT_PATH
    )

    # Calculate Downside vs Baseline addition
    ecl_baseline = float(summary_df_find(weighted_summary_df, "Baseline"))
    ecl_downside = float(summary_df_find(weighted_summary_df, "Downside"))
    downside_addition = ecl_downside - ecl_baseline
    downside_pct = (downside_addition / ecl_baseline * 100.0) if ecl_baseline > 0 else 0.0

    print("\n" + "=" * 80)
    print(" STAGE 8 FORWARD-LOOKING MACROECONOMIC & PERFORMING-BOOK RESULTS")
    print("=" * 80)
    print(f"Baseline Scenario ECL (pd_mult 1.00) : ${ecl_baseline:,.2f}")
    print(f"Downside Scenario ECL (pd_mult 1.50) : ${ecl_downside:,.2f}")
    print(f"Downside Addition over Baseline      : +${downside_addition:,.2f} (+{downside_pct:.2f}%)")
    print(f"Final Probability-Weighted ECL       : ${weighted_total_ecl:,.2f}")
    print("=" * 80)


def summary_df_find(df: pd.DataFrame, scenario_name: str) -> float:
    mask = df["scenario"].astype(str).str.lower() == scenario_name.lower()
    if mask.any():
        return float(df.loc[mask, "scenario_ecl"].values[0])
    return 0.0


if __name__ == "__main__":
    main()
