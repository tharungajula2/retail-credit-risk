"""
run_expected_loss.py
--------------------
Execution script to compute Expected Loss (EL = PD * LGD * EAD) on the Out-Of-Time (OOT 2014) portfolio.
"""

from pathlib import Path
import pandas as pd

from creditrisk.features.binning import WoEBinner
from creditrisk.models.lgd_model import TwoStageLGD
from creditrisk.models.pd_model import PDModel
from creditrisk.regulatory.expected_loss import (
    compute_expected_loss,
    portfolio_el_summary
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
OOT_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "oot.parquet"
PD_MODEL_B_PATH = PROJECT_ROOT / "outputs" / "models" / "pd_model_b.pkl"
WOE_BINNER_PD_PATH = PROJECT_ROOT / "outputs" / "models" / "woe_binner.pkl"
LGD_MODEL_PATH = PROJECT_ROOT / "outputs" / "models" / "lgd_model.pkl"
SUMMARY_OUTPUT_PATH = PROJECT_ROOT / "outputs" / "tables" / "expected_loss_summary.csv"


def main():
    print(f"Loading OOT (2014) portfolio dataset from: {OOT_DATA_PATH}...")
    df_oot = pd.read_parquet(OOT_DATA_PATH)
    print(f"OOT portfolio loaded ({len(df_oot):,} loans).")

    print(f"Loading deployment PD Model B from: {PD_MODEL_B_PATH}...")
    pd_model_b = PDModel.load(PD_MODEL_B_PATH)

    print(f"Loading PD WoEBinner from: {WOE_BINNER_PD_PATH}...")
    woe_binner_pd = WoEBinner.load(WOE_BINNER_PD_PATH)

    print(f"Loading Two-Stage LGD Model from: {LGD_MODEL_PATH}...")
    lgd_model = TwoStageLGD.load(LGD_MODEL_PATH)

    print("\nComputing Expected Loss (EL = PD * LGD * EAD) across OOT portfolio...")
    df_el = compute_expected_loss(
        df_oot,
        pd_model=pd_model_b,
        lgd_model=lgd_model,
        woe_binner_pd=woe_binner_pd
    )

    print("Generating portfolio Expected Loss summary tables...")
    summary_df, metrics = portfolio_el_summary(df_el, output_path=SUMMARY_OUTPUT_PATH)

    print("\nExpected Loss Summary Table (OOT 2014 Portfolio):")
    print(summary_df.to_string(index=False))


if __name__ == "__main__":
    main()
