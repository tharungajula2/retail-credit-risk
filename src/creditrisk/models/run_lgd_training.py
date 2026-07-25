"""
run_lgd_training.py
-------------------
Execution script to train and evaluate the Two-Stage Loss Given Default (LGD) model.
"""

from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split

from creditrisk.data.target import build_target
from creditrisk.models.lgd_data import build_lgd_base
from creditrisk.models.lgd_model import (
    CANDIDATE_FEATURES,
    TwoStageLGD,
    evaluate_lgd_model
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
RAW_DATA_PATH = PROJECT_ROOT / "datasets" / "loan_data_2007_2014.csv"
MODEL_PATH = PROJECT_ROOT / "outputs" / "models" / "lgd_model.pkl"
CALIB_TABLE_PATH = PROJECT_ROOT / "outputs" / "tables" / "lgd_calibration.csv"
SCATTER_FIG_PATH = PROJECT_ROOT / "outputs" / "figures" / "lgd_pred_vs_actual.png"


def main():
    print(f"Loading raw loan dataset from: {RAW_DATA_PATH}...")
    df_raw = pd.read_csv(RAW_DATA_PATH, low_memory=False)
    
    print("Building target flags and Basel LGD base...")
    df_target = build_target(df_raw)
    lgd_base = build_lgd_base(df_target)
    
    print(f"Extracted {len(lgd_base):,} defaulted loans for LGD modeling.")

    # Application-time candidate features
    X = lgd_base[CANDIDATE_FEATURES].copy()
    y_has_recovery = lgd_base["has_recovery"]
    y_recovery_rate = lgd_base["recovery_rate"]
    y_lgd = lgd_base["lgd"]

    # 80/20 train/test split stratified on has_recovery
    print("Splitting defaulted loans 80/20 (stratified on has_recovery, random_state=42)...")
    X_train, X_test, y_has_rec_train, y_has_rec_test, y_rec_train, y_rec_test, y_lgd_train, y_lgd_test = (
        train_test_split(
            X,
            y_has_recovery,
            y_recovery_rate,
            y_lgd,
            test_size=0.20,
            random_state=42,
            stratify=y_has_recovery
        )
    )

    print(f"LGD Train set size: {len(X_train):,} loans")
    print(f"LGD Test set size : {len(X_test):,} loans")

    # Fit TwoStageLGD model
    print("\nFitting Two-Stage LGD Model (Stage 1 Logistic Regression + Stage 2 GradientBoostingRegressor)...")
    model = TwoStageLGD(regressor_type="gbr", random_state=42)
    stage1_metrics = model.fit(X_train, y_has_rec_train, y_rec_train)

    print(f"Stage 1 Classifier AUC  : {stage1_metrics['auc']:.4f}")
    print(f"Stage 1 Classifier Gini : {stage1_metrics['gini']:.4f}")

    # Save model
    model.save(MODEL_PATH)

    # Evaluate on test set
    print("\nEvaluating LGD Model on Test Set...")
    metrics, calib_summary = evaluate_lgd_model(
        model,
        X_test,
        y_lgd_test,
        y_rec_test,
        calib_table_path=CALIB_TABLE_PATH,
        scatter_fig_path=SCATTER_FIG_PATH
    )

    print("=" * 60)
    print(" LGD MODEL EVALUATION RESULTS (TEST SET)")
    print("=" * 60)
    print(f"Stage 1 AUC                     : {stage1_metrics['auc']:.4f}")
    print(f"Stage 1 Gini                    : {stage1_metrics['gini']:.4f}")
    print(f"Stage 2 Recovery MAE            : {metrics['stage2_mae']:.4f}")
    print(f"Overall LGD MAE                 : {metrics['overall_mae']:.4f}")
    print(f"Portfolio Mean Actual LGD       : {metrics['portfolio_mean_actual_lgd']:.4f}")
    print(f"Portfolio Mean Predicted LGD    : {metrics['portfolio_mean_pred_lgd']:.4f}")
    print("=" * 60)

    print("\nLGD Calibration Table (Deciles of Predicted LGD):")
    print(calib_summary.to_string(index=False))


if __name__ == "__main__":
    main()
