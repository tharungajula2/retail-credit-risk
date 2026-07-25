"""
run_ecl.py
----------
Execution script to compute IFRS 9 ECL, US CECL provisions, and compare side-by-side with Basel Regulatory EL
on the Out-Of-Time (OOT 2014) portfolio.
"""

from pathlib import Path
import pandas as pd

from creditrisk.features.binning import WoEBinner
from creditrisk.models.lgd_model import TwoStageLGD
from creditrisk.models.pd_model import PDModel
from creditrisk.regulatory.ecl import (
    compare_ifrs9_vs_cecl_vs_basel,
    compute_cecl,
    compute_ecl,
    ecl_summary
)
from creditrisk.regulatory.expected_loss import compute_expected_loss

PROJECT_ROOT = Path(__file__).resolve().parents[3]
OOT_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "oot.parquet"
PD_MODEL_B_PATH = PROJECT_ROOT / "outputs" / "models" / "pd_model_b.pkl"
WOE_BINNER_PD_PATH = PROJECT_ROOT / "outputs" / "models" / "woe_binner.pkl"
LGD_MODEL_PATH = PROJECT_ROOT / "outputs" / "models" / "lgd_model.pkl"
TERM_STRUCT_PATH = PROJECT_ROOT / "outputs" / "tables" / "lifetime_pd_term_structure.csv"
ECL_SUMMARY_PATH = PROJECT_ROOT / "outputs" / "tables" / "ecl_summary.csv"
CECL_COMPARE_PATH = PROJECT_ROOT / "outputs" / "tables" / "ifrs9_vs_cecl.csv"


def main():
    print(f"Loading OOT (2014) portfolio dataset from: {OOT_DATA_PATH}...")
    df_oot = pd.read_parquet(OOT_DATA_PATH)
    print(f"OOT portfolio loaded ({len(df_oot):,} loans).")

    print("Loading model artifacts and term structure...")
    pd_model_b = PDModel.load(PD_MODEL_B_PATH)
    woe_binner_pd = WoEBinner.load(WOE_BINNER_PD_PATH)
    lgd_model = TwoStageLGD.load(LGD_MODEL_PATH)
    term_struct = pd.read_csv(TERM_STRUCT_PATH) if TERM_STRUCT_PATH.exists() else None

    # 1. Compute IFRS 9 Staged ECL
    print("\nComputing IFRS 9 Staged Expected Credit Loss (ECL)...")
    df_ecl = compute_ecl(
        df_oot,
        pd_model=pd_model_b,
        lgd_model=lgd_model,
        woe_binner_pd=woe_binner_pd,
        term_structure=term_struct
    )

    print("Generating IFRS 9 ECL summary table...")
    ecl_sum_df, ecl_metrics = ecl_summary(df_ecl, output_path=ECL_SUMMARY_PATH)

    # 2. Compute US CECL Lifetime Provision
    print("\nComputing US CECL Provisions (Day-1 Lifetime ECL for ALL performing loans)...")
    df_cecl = compute_cecl(
        df_oot,
        pd_model=pd_model_b,
        lgd_model=lgd_model,
        woe_binner_pd=woe_binner_pd,
        term_structure=term_struct
    )

    # 3. Compute Basel Regulatory EL
    print("\nComputing Basel Regulatory Expected Loss (EL)...")
    df_basel_el = compute_expected_loss(
        df_oot,
        pd_model=pd_model_b,
        lgd_model=lgd_model,
        woe_binner_pd=woe_binner_pd
    )
    total_basel_el = float(df_basel_el["el"].sum())

    # 4. Compare Frameworks Side-by-Side
    print("\nGenerating Framework Comparison (IFRS 9 vs US CECL vs Basel EL)...")
    comp_df = compare_ifrs9_vs_cecl_vs_basel(
        df_ecl,
        df_cecl,
        total_basel_el=total_basel_el,
        output_path=CECL_COMPARE_PATH
    )

    print("\n" + "=" * 80)
    print(" SUMMARY RESULTS (OOT 2014 PORTFOLIO)")
    print("=" * 80)
    print(f"Total Portfolio Exposure (EAD)   : ${ecl_metrics['total_ead']:,.2f}")
    print(f"Total IFRS 9 ECL Provision       : ${ecl_metrics['total_ecl']:,.2f}  (Coverage: {ecl_metrics['portfolio_coverage_ratio']*100:.2f}%)")
    print(f"Total US CECL Provision          : ${df_cecl['cecl'].sum():,.2f}  (Coverage: {df_cecl['cecl'].sum()/ecl_metrics['total_ead']*100:.2f}%)")
    print(f"Total Basel Regulatory EL        : ${total_basel_el:,.2f}  (Coverage: {total_basel_el/ecl_metrics['total_ead']*100:.2f}%)")
    print("=" * 80)


if __name__ == "__main__":
    main()
