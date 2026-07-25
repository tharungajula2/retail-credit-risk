"""
run_basel_capital.py
--------------------
Execution script to calculate Basel III IRB RWA vs Standardised RWA and Downturn LGD capital requirements
on the Out-Of-Time (OOT 2014) portfolio.
"""

from pathlib import Path
import pandas as pd

from creditrisk.features.binning import WoEBinner
from creditrisk.models.lgd_model import TwoStageLGD
from creditrisk.models.pd_model import PDModel
from creditrisk.regulatory.basel_capital import (
    compare_downturn_capital,
    portfolio_capital_summary
)
from creditrisk.regulatory.expected_loss import compute_expected_loss

PROJECT_ROOT = Path(__file__).resolve().parents[3]
OOT_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "oot.parquet"
PD_MODEL_B_PATH = PROJECT_ROOT / "outputs" / "models" / "pd_model_b.pkl"
WOE_BINNER_PD_PATH = PROJECT_ROOT / "outputs" / "models" / "woe_binner.pkl"
LGD_MODEL_PATH = PROJECT_ROOT / "outputs" / "models" / "lgd_model.pkl"
SUMMARY_OUTPUT_PATH = PROJECT_ROOT / "outputs" / "tables" / "basel_capital_summary.csv"
DOWNTURN_OUTPUT_PATH = PROJECT_ROOT / "outputs" / "tables" / "basel_downturn_comparison.csv"


def main():
    print(f"Loading OOT (2014) portfolio dataset from: {OOT_DATA_PATH}...")
    df_oot = pd.read_parquet(OOT_DATA_PATH)
    print(f"OOT portfolio loaded ({len(df_oot):,} loans).")

    print("Loading models and computing risk parameters (PD, LGD, EAD)...")
    pd_model_b = PDModel.load(PD_MODEL_B_PATH)
    woe_binner_pd = WoEBinner.load(WOE_BINNER_PD_PATH)
    lgd_model = TwoStageLGD.load(LGD_MODEL_PATH)

    df_el = compute_expected_loss(
        df_oot,
        pd_model=pd_model_b,
        lgd_model=lgd_model,
        woe_binner_pd=woe_binner_pd
    )

    print("\nComputing Basel III IRB & Standardised Capital Requirements...")
    summary_df, metrics = portfolio_capital_summary(df_el, output_path=SUMMARY_OUTPUT_PATH)

    print("\nRecomputing Portfolio IRB Capital using Downturn LGD (+8pp add-on)...")
    comp_df = compare_downturn_capital(df_el, output_path=DOWNTURN_OUTPUT_PATH)

    print("\nBasel Downturn LGD Capital Comparison Table:")
    print(comp_df.to_string(index=False))


if __name__ == "__main__":
    main()
