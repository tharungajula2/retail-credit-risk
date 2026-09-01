"""
run_sampling.py
---------------
Execution script that loads raw data, applies target building, partitions the dataset
into Train, In-Time Test, and OOT samples, exports summary metrics to CSV, and saves
Parquet files to data/processed/.
"""

from pathlib import Path
import pandas as pd
from creditrisk.data.sampling import build_samples, sample_summary
from creditrisk.data.target import build_target

PROJECT_ROOT = Path(__file__).resolve().parents[3]
RAW_DATA_PATH = PROJECT_ROOT / "datasets" / "loan_data_2007_2014.csv"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_TABLE_PATH = PROJECT_ROOT / "outputs" / "tables" / "sample_summary.csv"


def main():
    print(f"Loading raw dataset from: {RAW_DATA_PATH}...")
    df_raw = pd.read_csv(RAW_DATA_PATH, low_memory=False)

    print("Building target variables...")
    df_target = build_target(df_raw)

    print("Partitioning samples (Train, In-Time Test, OOT)...")
    samples = build_samples(df_target)

    print("Generating sample summary table...")
    summary_df = sample_summary(samples, output_path=OUTPUT_TABLE_PATH)

    print("\nSample Summary:")
    print(summary_df.to_string(index=False))

    # Ensure data/processed/ directory exists
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Save samples as parquet files
    for name, sample_df in samples.items():
        parquet_path = PROCESSED_DATA_DIR / f"{name}.parquet"
        print(f"Saving {name} sample ({len(sample_df):,} rows) to: {parquet_path}...")
        sample_df.to_parquet(parquet_path, index=False)

    print("\nSampling execution completed successfully.")


if __name__ == "__main__":
    main()
