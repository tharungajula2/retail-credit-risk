"""
run_transitions.py
------------------
Execution script for origination rating grade to outcome transition matrix and default summary by grade.
"""

from pathlib import Path
import pandas as pd

from creditrisk.data.target import build_target
from creditrisk.monitoring.transitions import default_by_grade_summary, transition_matrix

PROJECT_ROOT = Path(__file__).resolve().parents[3]
RAW_DATA_PATH = PROJECT_ROOT / "datasets" / "loan_data_2007_2014.csv"
OUTPUT_TABLE_PATH = PROJECT_ROOT / "outputs" / "tables" / "transition_matrix.csv"
OUTPUT_FIGURE_PATH = PROJECT_ROOT / "outputs" / "figures" / "transition_matrix.png"


def main():
    print(f"Loading raw loan dataset from: {RAW_DATA_PATH}...")
    df_raw = pd.read_csv(RAW_DATA_PATH, low_memory=False)
    print(f"Loaded dataset ({len(df_raw):,} total loans).")

    print("Building target flags...")
    df_target = build_target(df_raw)

    print("Generating Origination Rating Grade to Outcome Transition Matrix and Heatmap...")
    norm_matrix, counts_df = transition_matrix(
        df_target,
        output_path=OUTPUT_TABLE_PATH,
        fig_path=OUTPUT_FIGURE_PATH
    )

    print("\nGenerating Default Summary by Rating Grade...")
    default_by_grade_summary(df_target)


if __name__ == "__main__":
    main()
