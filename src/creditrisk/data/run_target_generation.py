"""
run_target_generation.py
-------------------------
Execution script that processes the raw LendingClub dataset to engineer
the 12-month default target variable and generate the vintage summary table.
"""

from pathlib import Path
import pandas as pd
from creditrisk.data.target import build_target, target_summary

PROJECT_ROOT = Path(__file__).resolve().parents[3]
RAW_DATA_PATH = PROJECT_ROOT / "datasets" / "loan_data_2007_2014.csv"
OUTPUT_TABLE_PATH = PROJECT_ROOT / "outputs" / "tables" / "target_summary_by_vintage.csv"


def main():
    print(f"Loading raw dataset from: {RAW_DATA_PATH}...")
    df_raw = pd.read_csv(RAW_DATA_PATH, low_memory=False)
    print(f"Dataset loaded successfully ({len(df_raw):,} rows).")

    print("Building 12-month default target variables...")
    df_target = build_target(df_raw)

    print("Generating vintage summary table...")
    summary_df = target_summary(df_target, output_path=OUTPUT_TABLE_PATH)

    print("\nTarget summary by vintage year:")
    print(summary_df.to_string(index=False))


if __name__ == "__main__":
    main()
