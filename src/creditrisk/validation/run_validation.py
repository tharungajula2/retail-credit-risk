"""
run_validation.py
-----------------
Execution script that runs the validation battery for Model A and Model B
across Train, Test, and OOT datasets. Generates the master validation_summary.csv
table and exports all diagnostic plots.
"""

from pathlib import Path
import pandas as pd
from creditrisk.features.binning import WoEBinner
from creditrisk.models.pd_model import PDModel
from creditrisk.validation.metrics import (
    brier_score,
    gini_auc,
    hosmer_lemeshow,
    ks_statistic,
)
from creditrisk.validation.plots import (
    calibration_plot,
    ks_plot,
    roc_curve_plot,
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
WOE_BINNER_PATH = PROJECT_ROOT / "outputs" / "models" / "woe_binner.pkl"
MODEL_A_PATH = PROJECT_ROOT / "outputs" / "models" / "pd_model_a.pkl"
MODEL_B_PATH = PROJECT_ROOT / "outputs" / "models" / "pd_model_b.pkl"

OUTPUT_TABLES_DIR = PROJECT_ROOT / "outputs" / "tables"
OUTPUT_FIGURES_DIR = PROJECT_ROOT / "outputs" / "figures"


def main():
    OUTPUT_TABLES_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading processed datasets (train, test, oot)...")
    train_df = pd.read_parquet(PROCESSED_DATA_DIR / "train.parquet")
    test_df = pd.read_parquet(PROCESSED_DATA_DIR / "test.parquet")
    oot_df = pd.read_parquet(PROCESSED_DATA_DIR / "oot.parquet")

    datasets = {
        "train": train_df,
        "test": test_df,
        "oot": oot_df,
    }

    print(f"Loading pre-fitted WoEBinner from: {WOE_BINNER_PATH}...")
    woe_binner = WoEBinner.load(WOE_BINNER_PATH)

    print(f"Loading Model A from: {MODEL_A_PATH}...")
    model_a = PDModel.load(MODEL_A_PATH)

    print(f"Loading Model B from: {MODEL_B_PATH}...")
    model_b = PDModel.load(MODEL_B_PATH)

    models = {
        "model_a": model_a,
        "model_b": model_b,
    }

    summary_rows = []

    print("\nExecuting validation battery across 6 model-sample combinations...")

    for model_name, model in models.items():
        for sample_name, df_sample in datasets.items():
            print(f"Evaluating {model_name.upper()} on {sample_name.upper()} sample ({len(df_sample):,} rows)...")

            y_true = df_sample["default_12m"].values
            pd_pred = model.predict_pd(df_sample, woe_binner)

            # 1. Compute metrics
            auc, gini = gini_auc(y_true, pd_pred)
            ks_stat, _ = ks_statistic(y_true, pd_pred)
            brier = brier_score(y_true, pd_pred)
            _, hl_pvalue = hosmer_lemeshow(y_true, pd_pred, n_bins=10)

            summary_rows.append(
                {
                    "model": model_name,
                    "sample": sample_name,
                    "auc": auc,
                    "gini": gini,
                    "ks": ks_stat,
                    "brier": brier,
                    "hl_pvalue": hl_pvalue,
                }
            )

            # 2. Generate plots
            roc_curve_plot(y_true, pd_pred, model_name, sample_name, OUTPUT_FIGURES_DIR)
            ks_plot(y_true, pd_pred, model_name, sample_name, OUTPUT_FIGURES_DIR)
            calibration_plot(y_true, pd_pred, model_name, sample_name, OUTPUT_FIGURES_DIR)

    val_summary = pd.DataFrame(summary_rows)
    val_path = OUTPUT_TABLES_DIR / "validation_summary.csv"
    val_summary.to_csv(val_path, index=False)
    print(f"\nValidation battery completed. Master table saved to: {val_path}")

    print("\n" + "=" * 75)
    print("                      MASTER VALIDATION SUMMARY TABLE                  ")
    print("=" * 75)
    print(val_summary.to_string(index=False))


if __name__ == "__main__":
    main()
