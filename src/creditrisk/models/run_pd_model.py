"""
run_pd_model.py
---------------
Execution script that fits Model A (borrower fundamentals) and Model B (full model)
on the training dataset, exports coefficient tables, and saves fitted model artifacts.
"""

from pathlib import Path
import pandas as pd
from creditrisk.features.binning import WoEBinner
from creditrisk.models.pd_model import PDModel, load_pd_config

PROJECT_ROOT = Path(__file__).resolve().parents[3]
TRAIN_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "train.parquet"
WOE_BINNER_PATH = PROJECT_ROOT / "outputs" / "models" / "woe_binner.pkl"
IV_SUMMARY_PATH = PROJECT_ROOT / "outputs" / "tables" / "iv_summary.csv"
OUTPUT_MODELS_DIR = PROJECT_ROOT / "outputs" / "models"
OUTPUT_TABLES_DIR = PROJECT_ROOT / "outputs" / "tables"


def main():
    print(f"Loading train dataset from: {TRAIN_DATA_PATH}...")
    df_train = pd.read_parquet(TRAIN_DATA_PATH)
    print(f"Train dataset loaded ({len(df_train):,} rows).")

    print(f"Loading pre-fitted WoEBinner from: {WOE_BINNER_PATH}...")
    woe_binner = WoEBinner.load(WOE_BINNER_PATH)

    print(f"Loading IV summary table from: {IV_SUMMARY_PATH}...")
    iv_table = pd.read_csv(IV_SUMMARY_PATH)

    cfg = load_pd_config()
    model_a_exclude = cfg.get("model_a_exclude", ["grade", "sub_grade", "int_rate"])

    # 1. Fit Model A (Borrower Fundamentals — Excludes Grade, Sub-Grade, Int-Rate)
    print("\nFitting Model A (Excluding LendingClub Risk Pricing: grade, sub_grade, int_rate)...")
    model_a = PDModel()
    model_a.fit(df_train, woe_binner, iv_table, exclude_cols=model_a_exclude)

    model_a_path = OUTPUT_MODELS_DIR / "pd_model_a.pkl"
    model_a.save(model_a_path)
    print(f"Model A saved to: {model_a_path}")

    summary_a = model_a.summary()
    coef_a_path = OUTPUT_TABLES_DIR / "pd_model_a_coefs.csv"
    summary_a.to_csv(coef_a_path, index=False)
    print(f"Model A coefficient table saved to: {coef_a_path}")

    # 2. Fit Model B (Full Model — Includes All Features IV >= 0.02)
    print("\nFitting Model B (Full Feature Model — Includes All Features IV >= 0.02)...")
    model_b = PDModel()
    model_b.fit(df_train, woe_binner, iv_table, exclude_cols=None)

    model_b_path = OUTPUT_MODELS_DIR / "pd_model_b.pkl"
    model_b.save(model_b_path)
    print(f"Model B saved to: {model_b_path}")

    summary_b = model_b.summary()
    coef_b_path = OUTPUT_TABLES_DIR / "pd_model_b_coefs.csv"
    summary_b.to_csv(coef_b_path, index=False)
    print(f"Model B coefficient table saved to: {coef_b_path}")

    print("\n" + "=" * 70)
    print("               MODEL A COEFFICIENT SUMMARY (FUNDAMENTALS)             ")
    print("=" * 70)
    print(summary_a.to_string(index=False))

    print("\n" + "=" * 70)
    print("               MODEL B COEFFICIENT SUMMARY (FULL MODEL)               ")
    print("=" * 70)
    print(summary_b.to_string(index=False))


if __name__ == "__main__":
    main()
