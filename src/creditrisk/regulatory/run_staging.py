"""
run_staging.py
--------------
Execution script to evaluate IFRS 9 staging and SICR classification on the Out-Of-Time (OOT 2014) portfolio.
"""

from pathlib import Path
import pandas as pd

from creditrisk.features.binning import WoEBinner
from creditrisk.models.pd_model import PDModel
from creditrisk.regulatory.staging import assign_ifrs9_stages, stage_summary

PROJECT_ROOT = Path(__file__).resolve().parents[3]
OOT_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "oot.parquet"
PD_MODEL_B_PATH = PROJECT_ROOT / "outputs" / "models" / "pd_model_b.pkl"
WOE_BINNER_PD_PATH = PROJECT_ROOT / "outputs" / "models" / "woe_binner.pkl"
SUMMARY_OUTPUT_PATH = PROJECT_ROOT / "outputs" / "tables" / "staging_summary.csv"


def main():
    print(f"Loading OOT (2014) portfolio dataset from: {OOT_DATA_PATH}...")
    df_oot = pd.read_parquet(OOT_DATA_PATH)
    print(f"OOT portfolio loaded ({len(df_oot):,} loans).")

    print(f"Loading deployment PD Model B from: {PD_MODEL_B_PATH}...")
    pd_model_b = PDModel.load(PD_MODEL_B_PATH)

    print(f"Loading PD WoEBinner from: {WOE_BINNER_PD_PATH}...")
    woe_binner_pd = WoEBinner.load(WOE_BINNER_PD_PATH)

    print("\nAssigning IFRS 9 Stages (Stage 1 Performing, Stage 2 SICR, Stage 3 Default)...")
    df_staged = assign_ifrs9_stages(
        df_oot,
        pd_model=pd_model_b,
        woe_binner_pd=woe_binner_pd
    )

    print("Generating IFRS 9 Staging Summary table...")
    summary_df, metrics = stage_summary(df_staged, output_path=SUMMARY_OUTPUT_PATH)

    print("\nIFRS 9 Staging Summary Table (OOT 2014 Portfolio):")
    print(summary_df.to_string(index=False))


if __name__ == "__main__":
    main()
