"""
run_binning.py
--------------
Execution script that fits WoEBinner on the training sample (data/processed/train.parquet)
using PD-eligible candidate features. Exports IV summary and detailed bin tables.
"""

from pathlib import Path
import pandas as pd
from creditrisk.data.schema import get_pd_eligible_columns
from creditrisk.features.binning import WoEBinner

PROJECT_ROOT = Path(__file__).resolve().parents[3]
TRAIN_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "train.parquet"
OUTPUT_TABLES_DIR = PROJECT_ROOT / "outputs" / "tables"
BIN_TABLES_DIR = OUTPUT_TABLES_DIR / "bin_tables"
MODEL_OUTPUT_PATH = PROJECT_ROOT / "outputs" / "models" / "woe_binner.pkl"


def main():
    print(f"Loading train sample from: {TRAIN_DATA_PATH}...")
    df_train = pd.read_parquet(TRAIN_DATA_PATH)
    print(f"Train sample loaded successfully ({len(df_train):,} rows).")

    # Get PD-eligible columns
    pd_cols = get_pd_eligible_columns()
    
    # Filter features that exist in df_train
    features_to_bin = [c for c in pd_cols if c in df_train.columns]
    print(f"Total PD-eligible features to bin: {len(features_to_bin)}")

    X_train = df_train[features_to_bin]
    y_train = df_train["default_12m"]

    print("Fitting WoEBinner on training dataset (enforcing monotonicity and Laplace smoothing)...")
    binner = WoEBinner(min_bin_pct=0.05)
    binner.fit(X_train, y_train)

    # 1. Save IV summary table
    iv_table = binner.get_iv_table()
    OUTPUT_TABLES_DIR.mkdir(parents=True, exist_ok=True)
    iv_summary_path = OUTPUT_TABLES_DIR / "iv_summary.csv"
    iv_table.to_csv(iv_summary_path, index=False)
    print(f"\nIV summary table saved to: {iv_summary_path}")

    # 2. Save individual bin tables
    BIN_TABLES_DIR.mkdir(parents=True, exist_ok=True)
    for col in features_to_bin:
        bin_df = binner.get_bin_table(col)
        # Clean filename for column names
        clean_name = col.replace(":", "_").replace("/", "_")
        bin_table_path = BIN_TABLES_DIR / f"{clean_name}_bins.csv"
        bin_df.to_csv(bin_table_path, index=False)

    print(f"Detailed bin tables saved for {len(features_to_bin)} features in: {BIN_TABLES_DIR}")

    # 3. Save fitted WoEBinner object
    MODEL_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    binner.save(MODEL_OUTPUT_PATH)
    print(f"Fitted WoEBinner saved to: {MODEL_OUTPUT_PATH}")

    print("\n" + "=" * 65)
    print("               TOP 15 PREDICTIVE FEATURES BY IV              ")
    print("=" * 65)
    print(iv_table.head(15).to_string(index=False))


if __name__ == "__main__":
    main()
