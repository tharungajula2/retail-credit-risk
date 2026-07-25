"""
run_monitoring.py
------------------
Execution script for portfolio monitoring analytics: vintage curves, fixed-maturity default rate comparisons,
and delinquency roll-rate proxy tables.
"""

from pathlib import Path
import pandas as pd

from creditrisk.data.target import build_target
from creditrisk.monitoring.roll_rates import roll_rate_proxy
from creditrisk.monitoring.vintage import (
    vintage_curves,
    vintage_maturity_comparison
)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
RAW_DATA_PATH = PROJECT_ROOT / "datasets" / "loan_data_2007_2014.csv"


def main():
    print(f"Loading raw loan dataset from: {RAW_DATA_PATH}...")
    df_raw = pd.read_csv(RAW_DATA_PATH, low_memory=False)
    print(f"Loaded dataset ({len(df_raw):,} loans).")

    print("Building target default dates and months_to_default...")
    df_target = build_target(df_raw)

    print("\nGenerating Vintage Curves (MOB 0..48) matrix and trend plot...")
    vintage_curves(df_target, max_mob=48)

    print("\nGenerating Vintage Maturity Comparison (MOB 12 and MOB 18)...")
    vintage_maturity_comparison(df_target, milestone_mobs=[12, 18, 24])

    print("\nGenerating Delinquency Roll-Rate Proxy Table...")
    roll_rate_proxy(df_target)


if __name__ == "__main__":
    main()
