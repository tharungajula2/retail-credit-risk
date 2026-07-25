"""
run_calibration.py
------------------
Execution script that applies Intercept Recalibration and Platt Scaling to Model A
using the TEST dataset (preserving OOT as an un-leaked evaluation benchmark).
Appends recalibrated model rows to validation_summary.csv and updates calibration plots.
"""

from pathlib import Path
import pandas as pd
from creditrisk.features.binning import WoEBinner
from creditrisk.models.calibration import fit_intercept_recalibration, fit_platt_scaling
from creditrisk.models.pd_model import PDModel
from creditrisk.validation.metrics import (
    brier_score,
    gini_auc,
    hosmer_lemeshow,
    ks_statistic,
)
from creditrisk.validation.plots import calibration_plot

PROJECT_ROOT = Path(__file__).resolve().parents[3]
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
WOE_BINNER_PATH = PROJECT_ROOT / "outputs" / "models" / "woe_binner.pkl"
MODEL_A_PATH = PROJECT_ROOT / "outputs" / "models" / "pd_model_a.pkl"

OUTPUT_TABLES_DIR = PROJECT_ROOT / "outputs" / "tables"
OUTPUT_FIGURES_DIR = PROJECT_ROOT / "outputs" / "figures"
VAL_SUMMARY_PATH = OUTPUT_TABLES_DIR / "validation_summary.csv"


def main():
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

    # 1. Fit Recalibration variants on TEST dataset (avoiding OOT leakage)
    print("\nFitting Intercept Recalibration on TEST sample...")
    recal_intercept_model = fit_intercept_recalibration(model_a, woe_binner, test_df, target_col="default_12m")

    print("Fitting Platt Scaling on TEST sample...")
    recal_platt_model = fit_platt_scaling(model_a, woe_binner, test_df, target_col="default_12m")

    recal_models = {
        "model_a_recal_intercept": recal_intercept_model,
        "model_a_recal_platt": recal_platt_model,
    }

    new_rows = []

    # 2. Evaluate recalibrated models across train, test, oot
    for model_name, model in recal_models.items():
        for sample_name, df_sample in datasets.items():
            print(f"Evaluating {model_name} on {sample_name.upper()} sample ({len(df_sample):,} rows)...")

            y_true = df_sample["default_12m"].values
            pd_pred = model.predict_pd(df_sample, woe_binner)

            auc, gini = gini_auc(y_true, pd_pred)
            ks_stat, _ = ks_statistic(y_true, pd_pred)
            brier = brier_score(y_true, pd_pred)
            _, hl_pvalue = hosmer_lemeshow(y_true, pd_pred, n_bins=10)

            new_rows.append(
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

            # Update calibration plot for recalibrated model
            calibration_plot(y_true, pd_pred, model_name, sample_name, OUTPUT_FIGURES_DIR)

    # 3. Update master validation_summary.csv
    existing_val_df = pd.read_csv(VAL_SUMMARY_PATH)
    
    # Filter out any prior recal rows if re-running
    existing_clean = existing_val_df[~existing_val_df["model"].str.contains("recal")].copy()

    new_val_df = pd.DataFrame(new_rows)
    updated_val_df = pd.concat([existing_clean, new_val_df], ignore_index=True)

    updated_val_df.to_csv(VAL_SUMMARY_PATH, index=False)
    print(f"\nUpdated master validation table saved to: {VAL_SUMMARY_PATH}")

    print("\n" + "=" * 80)
    print("                     COMPLETE MASTER VALIDATION SUMMARY TABLE                   ")
    print("=" * 80)
    print(updated_val_df.to_string(index=False))


if __name__ == "__main__":
    main()
