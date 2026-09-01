"""
inspect_raw.py
--------------
Audits the raw LendingClub dataset in chunks without loading the entire 229 MB
file into memory at once. Generates a data inventory summarizing missing values,
cardinality, value counts for categorical fields, and date boundaries.
"""

from collections import Counter
from pathlib import Path
import pandas as pd

# Define relative workspace paths so the script can run from any working directory
PROJECT_ROOT = Path(__file__).resolve().parents[3]
RAW_DATA_PATH = PROJECT_ROOT / "datasets" / "loan_data_2007_2014.csv"
OUTPUT_REPORT_PATH = PROJECT_ROOT / "outputs" / "reports" / "data_inventory.txt"

# Specific categorical fields requiring full frequency distribution checks
CATEGORICAL_COLS = [
    "loan_status",
    "term",
    "grade",
    "home_ownership",
    "verification_status",
    "initial_list_status",
    "purpose",
    "application_type",
]

# Specific date fields requiring range boundaries and sample values
DATE_COLS = [
    "issue_d",
    "last_pymnt_d",
    "earliest_cr_line",
    "last_credit_pull_d",
]

CHUNK_SIZE = 50000


def main():
    print(f"Reading first 5 rows to inspect schema from: {RAW_DATA_PATH}")

    # Inspect first 5 rows to get column names and dtypes quickly
    sample_df = pd.read_csv(RAW_DATA_PATH, nrows=5, low_memory=False)
    columns = list(sample_df.columns)
    sample_dtypes = sample_df.dtypes.to_dict()

    print(f"Total columns found: {len(columns)}")

    # Initialize aggregators across chunks
    total_rows = 0
    missing_counts = Counter()
    
    # Store unique value sets per column to calculate exact cardinality
    unique_sets = {col: set() for col in columns}

    # Store categorical frequency counters
    cat_counters = {col: Counter() for col in CATEGORICAL_COLS if col in columns}

    # Process dataset chunk by chunk to maintain a low memory footprint
    chunk_reader = pd.read_csv(RAW_DATA_PATH, chunksize=CHUNK_SIZE, low_memory=False)

    for i, chunk in enumerate(chunk_reader):
        total_rows += len(chunk)
        print(f"Processing chunk {i + 1} ({total_rows:,} rows processed so far)...")

        # Accumulate null counts per column
        for col in columns:
            null_count = chunk[col].isna().sum()
            missing_counts[col] += int(null_count)

            # Update unique sets (dropna to exclude NaN from unique value counting)
            valid_series = chunk[col].dropna()
            unique_sets[col].update(valid_series.unique())

        # Accumulate categorical value counts
        for col in CATEGORICAL_COLS:
            if col in chunk.columns:
                counts = chunk[col].value_counts(dropna=False).to_dict()
                cat_counters[col].update(counts)

    # Format the inventory report output
    lines = []
    lines.append("==================================================")
    lines.append("         LENDINGCLUB RAW DATA INVENTORY REPORT     ")
    lines.append("==================================================\n")
    lines.append(f"Source File: {RAW_DATA_PATH.name}")
    lines.append(f"Total Rows: {total_rows:,}")
    lines.append(f"Total Columns: {len(columns)}\n")

    lines.append("--------------------------------------------------")
    lines.append("1. COLUMN METADATA, MISSING VALUES & CARDINALITY")
    lines.append("--------------------------------------------------")
    lines.append(f"{'Col #':<6} {'Column Name':<30} {'Sample Dtype':<15} {'Missing Count':<15} {'Missing %':<12} {'Unique Count':<12}")
    lines.append("-" * 90)

    for idx, col in enumerate(columns, start=1):
        missing = missing_counts[col]
        missing_pct = (missing / total_rows) * 100
        unique_cnt = len(unique_sets[col])
        dtype_str = str(sample_dtypes.get(col, "unknown"))
        lines.append(
            f"{idx:<6} {col:<30} {dtype_str:<15} {missing:<15,} {missing_pct:<12.2f}% {unique_cnt:<12,}"
        )

    lines.append("\n--------------------------------------------------")
    lines.append("2. CATEGORICAL VALUE COUNTS")
    lines.append("--------------------------------------------------")

    for col in CATEGORICAL_COLS:
        lines.append(f"\n--- Value Counts for: {col} ---")
        if col in cat_counters:
            for val, count in cat_counters[col].most_common():
                pct = (count / total_rows) * 100
                lines.append(f"  {str(val):<35} : {count:>10,} ({pct:6.2f}%)")
        else:
            lines.append("  [Column not present in dataset]")

    lines.append("\n--------------------------------------------------")
    lines.append("3. DATE COLUMNS SUMMARY (Min, Max, Sample Values)")
    lines.append("--------------------------------------------------")

    for col in DATE_COLS:
        lines.append(f"\n--- Date Column: {col} ---")
        if col in unique_sets:
            # Sort non-null distinct string values for date inspecting
            distinct_vals = [str(v) for v in unique_sets[col] if pd.notna(v)]
            
            # Convert to datetime to find true min and max date ranges accurately (e.g. 'Jun-14' -> %b-%y)
            parsed_dates = pd.to_datetime(distinct_vals, format="%b-%y", errors="coerce")
            valid_dates = parsed_dates.dropna()

            if not valid_dates.empty:
                min_date = valid_dates.min().strftime("%b-%Y")
                max_date = valid_dates.max().strftime("%b-%Y")
            else:
                min_date = "N/A"
                max_date = "N/A"

            first_5_sample = distinct_vals[:5]
            lines.append(f"  Min Date       : {min_date}")
            lines.append(f"  Max Date       : {max_date}")
            lines.append(f"  First 5 Distinct: {first_5_sample}")
        else:
            lines.append("  [Column not present in dataset]")

    report_content = "\n".join(lines)

    # Ensure destination directory exists
    OUTPUT_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report_content)

    print(f"\nData inventory successfully saved to: {OUTPUT_REPORT_PATH}")
    print("\n--- REPORT PREVIEW ---")
    print(report_content[:2500])


if __name__ == "__main__":
    main()
