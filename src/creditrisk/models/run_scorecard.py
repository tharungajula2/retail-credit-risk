"""
run_scorecard.py
----------------
Execution script that builds point-based scorecards and 8-tier master rating grade tables
for Model A (borrower fundamentals) and Model B (full model) on the training set.
"""

from pathlib import Path
import pandas as pd
from creditrisk.features.binning import WoEBinner
from creditrisk.models.pd_model import PDModel
from creditrisk.models.scorecard import build_rating_grades, build_scorecard, score_dataset

PROJECT_ROOT = Path(__file__).resolve().parents[3]
TRAIN_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "train.parquet"
WOE_BINNER_PATH = PROJECT_ROOT / "outputs" / "models" / "woe_binner.pkl"
MODEL_A_PATH = PROJECT_ROOT / "outputs" / "models" / "pd_model_a.pkl"
MODEL_B_PATH = PROJECT_ROOT / "outputs" / "models" / "pd_model_b.pkl"
OUTPUT_TABLES_DIR = PROJECT_ROOT / "outputs" / "tables"


def main():
    print(f"Loading training data from: {TRAIN_DATA_PATH}...")
    df_train = pd.read_parquet(TRAIN_DATA_PATH)
    print(f"Train dataset loaded ({len(df_train):,} rows).")

    print(f"Loading pre-fitted WoEBinner from: {WOE_BINNER_PATH}...")
    woe_binner = WoEBinner.load(WOE_BINNER_PATH)

    print(f"Loading Model A from: {MODEL_A_PATH}...")
    model_a = PDModel.load(MODEL_A_PATH)

    print(f"Loading Model B from: {MODEL_B_PATH}...")
    model_b = PDModel.load(MODEL_B_PATH)

    # 1. Process Model A
    print("\n--- MODEL A (BORROWER FUNDAMENTALS) SCORECARD & RATING GRADES ---")
    scorecard_a = build_scorecard(model_a, woe_binner, model_name="model_a", output_dir=OUTPUT_TABLES_DIR)
    scores_a = score_dataset(df_train, scorecard_a, woe_binner)
    rating_a, rank_a_holds = build_rating_grades(scores_a, df_train["default_12m"], n_grades=8, model_name="model_a", output_dir=OUTPUT_TABLES_DIR)

    print("\nModel A Master Rating Grades Table:")
    print(rating_a.to_string(index=False))
    print(f"\nModel A Rank-Ordering Monotonicity Holds: {rank_a_holds}")

    # 2. Process Model B
    print("\n--- MODEL B (FULL MODEL WITH RISK PRICING) SCORECARD & RATING GRADES ---")
    scorecard_b = build_scorecard(model_b, woe_binner, model_name="model_b", output_dir=OUTPUT_TABLES_DIR)
    scores_b = score_dataset(df_train, scorecard_b, woe_binner)
    rating_b, rank_b_holds = build_rating_grades(scores_b, df_train["default_12m"], n_grades=8, model_name="model_b", output_dir=OUTPUT_TABLES_DIR)

    print("\nModel B Master Rating Grades Table:")
    print(rating_b.to_string(index=False))
    print(f"\nModel B Rank-Ordering Monotonicity Holds: {rank_b_holds}")


if __name__ == "__main__":
    main()
