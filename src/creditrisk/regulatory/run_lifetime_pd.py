"""
run_lifetime_pd.py
------------------
Execution script to build portfolio lifetime PD term structure and discrete hazard curve (months 1..60).
"""

from pathlib import Path
import pandas as pd

from creditrisk.data.target import build_target
from creditrisk.regulatory.lifetime_pd import build_hazard_curve

PROJECT_ROOT = Path(__file__).resolve().parents[3]
RAW_DATA_PATH = PROJECT_ROOT / "datasets" / "loan_data_2007_2014.csv"
OUTPUT_TABLE_PATH = PROJECT_ROOT / "outputs" / "tables" / "lifetime_pd_term_structure.csv"
OUTPUT_FIGURE_PATH = PROJECT_ROOT / "outputs" / "figures" / "lifetime_pd_curve.png"


def main():
    print(f"Loading raw loan dataset from: {RAW_DATA_PATH}...")
    df_raw = pd.read_csv(RAW_DATA_PATH, low_memory=False)
    print(f"Loaded dataset ({len(df_raw):,} total loans).")

    print("Building target default dates and months_to_default...")
    df_target = build_target(df_raw)

    print("Building 60-month discrete-time hazard curve and lifetime PD term structure...")
    term_table = build_hazard_curve(
        df_target,
        max_months=60,
        output_path=OUTPUT_TABLE_PATH,
        fig_path=OUTPUT_FIGURE_PATH
    )

    selected_months = [6, 12, 18, 24, 36, 48, 60]
    sub_table = term_table[term_table["month"].isin(selected_months)].copy()

    print("\n" + "=" * 80)
    print(" PORTFOLIO LIFETIME PD TERM STRUCTURE (SELECTED MILESTONE MONTHS)")
    print("=" * 80)
    print(sub_table.to_string(index=False))
    print("=" * 80)


if __name__ == "__main__":
    main()
