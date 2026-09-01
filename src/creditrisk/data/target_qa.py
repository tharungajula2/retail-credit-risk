"""
target_qa.py
------------
Quality assurance module for the 12-month default target definition.

Performs four primary QA audits:
1. Exact mathematical reconciliation bridge.
2. Negative default timing anomaly inspection.
3. Default seasoning curve calculation and visualization.
4. Sensitivity testing against a strict default status definition.

Also generates quarterly default rate trend visualizations.
"""

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from creditrisk.data.target import build_target, load_target_config

PROJECT_ROOT = Path(__file__).resolve().parents[3]
RAW_DATA_PATH = PROJECT_ROOT / "datasets" / "loan_data_2007_2014.csv"
OUTPUTS_TABLES = PROJECT_ROOT / "outputs" / "tables"
OUTPUTS_FIGURES = PROJECT_ROOT / "outputs" / "figures"


def run_target_qa():
    OUTPUTS_TABLES.mkdir(parents=True, exist_ok=True)
    OUTPUTS_FIGURES.mkdir(parents=True, exist_ok=True)

    print(f"Loading raw dataset from: {RAW_DATA_PATH}...")
    df_raw = pd.read_csv(RAW_DATA_PATH, low_memory=False)

    print("Building baseline target variables...")
    df = build_target(df_raw)

    total_loans = len(df)
    non_default_cnt = (df["ever_default"] == 0).sum()
    ever_default_cnt = (df["ever_default"] == 1).sum()

    # Breakdown of ever_default loans
    def_12m_1_cnt = ((df["ever_default"] == 1) & (df["months_to_default"] >= 0) & (df["months_to_default"] <= 12)).sum()
    def_12m_0_gt12_cnt = ((df["ever_default"] == 1) & (df["months_to_default"] > 12)).sum()
    negative_anomaly_cnt = ((df["ever_default"] == 1) & (df["months_to_default"] < 0)).sum()
    missing_anomaly_cnt = ((df["ever_default"] == 1) & (df["est_default_date"].isna())).sum()

    # 1. RECONCILIATION BRIDGE
    bridge_rows = [
        {"item": "Total Loans", "count": total_loans, "pct_of_total": 100.0},
        {"item": "- Non-Default (Current, Paid, etc.)", "count": non_default_cnt, "pct_of_total": (non_default_cnt / total_loans) * 100},
        {"item": "= Ever Default", "count": ever_default_cnt, "pct_of_total": (ever_default_cnt / total_loans) * 100},
        {"item": "   of which: default_12m = 1 (months 0 to 12)", "count": def_12m_1_cnt, "pct_of_total": (def_12m_1_cnt / total_loans) * 100},
        {"item": "   of which: default_12m = 0 (months > 12)", "count": def_12m_0_gt12_cnt, "pct_of_total": (def_12m_0_gt12_cnt / total_loans) * 100},
        {"item": "   of which: NEGATIVE timing anomaly", "count": negative_anomaly_cnt, "pct_of_total": (negative_anomaly_cnt / total_loans) * 100},
        {"item": "   of which: MISSING est_default_date", "count": missing_anomaly_cnt, "pct_of_total": (missing_anomaly_cnt / total_loans) * 100},
    ]

    reconciled_sum = non_default_cnt + def_12m_1_cnt + def_12m_0_gt12_cnt + negative_anomaly_cnt + missing_anomaly_cnt

    print("\n" + "=" * 65)
    print("           1. TARGET RECONCILIATION BRIDGE           ")
    print("=" * 65)
    reconcil_df = pd.DataFrame(bridge_rows)
    print(reconcil_df.to_string(index=False))

    if reconciled_sum != total_loans:
        raise ValueError(
            f"Reconciliation error! Sum of sub-components ({reconciled_sum:,}) does not equal total loans ({total_loans:,})."
        )
    print(f"\nReconciliation verified: {reconciled_sum:,} == {total_loans:,} (100% exact match).")

    reconcil_path = OUTPUTS_TABLES / "target_reconciliation.csv"
    reconcil_df.to_csv(reconcil_path, index=False)

    # 2. ANOMALY DETAIL
    print("\n" + "=" * 65)
    print("           2. ANOMALY DETAIL (Negative Months to Default)     ")
    print("=" * 65)
    neg_anomalies = df[(df["ever_default"] == 1) & (df["months_to_default"] < 0)]
    frac_of_ever_default = (len(neg_anomalies) / ever_default_cnt) * 100 if ever_default_cnt > 0 else 0.0
    print(f"Total Negative Anomalies Found: {len(neg_anomalies):,}")
    print(f"Percentage of Ever Default Loans: {frac_of_ever_default:.4f}%")

    if not neg_anomalies.empty:
        sample_cols = ["id", "issue_d", "last_pymnt_d", "est_default_date", "loan_status"]
        sample_rows = neg_anomalies[sample_cols].head(10)
        print("\n10 Sample Negative Anomaly Rows:")
        print(sample_rows.to_string(index=False))

    # 3. THE SEASONING CURVE
    print("\n" + "=" * 65)
    print("           3. THE SEASONING CURVE (Default Timing)     ")
    print("=" * 65)
    defaults_only = df[df["ever_default"] == 1].copy()
    
    # Exclude negative anomalies for positive seasoning curve bucketing
    valid_defaults = defaults_only[defaults_only["months_to_default"] >= 0].copy()

    bins = [-0.1, 1, 3, 6, 9, 12, 18, 24, 36, 999]
    labels = ["0-1", "2-3", "4-6", "7-9", "10-12", "13-18", "19-24", "25-36", "37+"]

    valid_defaults["seasoning_bucket"] = pd.cut(
        valid_defaults["months_to_default"], bins=bins, labels=labels
    )

    seasoning_counts = valid_defaults["seasoning_bucket"].value_counts().reindex(labels, fill_value=0).reset_index()
    seasoning_counts.columns = ["months_to_default_bucket", "n_defaults"]
    seasoning_counts["pct_of_all_defaults"] = (seasoning_counts["n_defaults"] / ever_default_cnt) * 100

    print(seasoning_counts.to_string(index=False))

    pct_in_first_12m = (def_12m_1_cnt / ever_default_cnt) * 100
    print(f"\nPercentage of all defaults occurring in first 12 months: {pct_in_first_12m:.2f}%")

    seasoning_table_path = OUTPUTS_TABLES / "default_timing_distribution.csv"
    seasoning_counts.to_csv(seasoning_table_path, index=False)

    # Plot Seasoning Bar Chart
    plt.figure(figsize=(10, 5))
    plt.bar(seasoning_counts["months_to_default_bucket"], seasoning_counts["pct_of_all_defaults"], color="#1f77b4", edgecolor="black")
    plt.title("Loan Seasoning Curve: Timing of Defaults After Origination", fontsize=13, fontweight="bold")
    plt.xlabel("Months to Default Bucket", fontsize=11)
    plt.ylabel("Percentage of Total Defaults (%)", fontsize=11)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    for idx, row in seasoning_counts.iterrows():
        plt.text(idx, row["pct_of_all_defaults"] + 0.5, f"{row['pct_of_all_defaults']:.1f}%", ha="center", fontsize=9)
    plt.tight_layout()
    seasoning_fig_path = OUTPUTS_FIGURES / "default_timing_distribution.png"
    plt.savefig(seasoning_fig_path, dpi=300)
    plt.close()
    print(f"Seasoning bar chart saved to: {seasoning_fig_path}")

    # 4. SENSITIVITY TEST
    print("\n" + "=" * 65)
    print("           4. SENSITIVITY TEST (Strict Definition)     ")
    print("=" * 65)
    
    # Strict config removes 'Late (31-120 days)'
    baseline_cfg = load_target_config()
    strict_cfg = baseline_cfg.copy()
    strict_cfg["default_statuses"] = [
        s for s in baseline_cfg["default_statuses"] if s != "Late (31-120 days)"
    ]

    df_strict = build_target(df_raw, config=strict_cfg)

    # Group by vintage_year
    base_summary = df.groupby("vintage_year", as_index=False).agg(
        n_loans=("loan_status", "count"),
        baseline_default_12m=("default_12m", "sum")
    )
    base_summary["baseline_default_12m_rate"] = base_summary["baseline_default_12m"] / base_summary["n_loans"]

    strict_summary = df_strict.groupby("vintage_year", as_index=False).agg(
        strict_default_12m=("default_12m", "sum")
    )
    strict_summary["strict_default_12m_rate"] = (
        strict_summary["strict_default_12m"] / base_summary["n_loans"]
    )

    sens_df = pd.merge(base_summary, strict_summary[["vintage_year", "strict_default_12m", "strict_default_12m_rate"]], on="vintage_year")
    print(sens_df[["vintage_year", "n_loans", "baseline_default_12m_rate", "strict_default_12m_rate"]].to_string(index=False))

    overall_baseline_rate = (df["default_12m"].sum() / total_loans) * 100
    overall_strict_rate = (df_strict["default_12m"].sum() / total_loans) * 100

    print(f"\nOverall Baseline 12-Month Default Rate : {overall_baseline_rate:.3f}%")
    print(f"Overall Strict 12-Month Default Rate   : {overall_strict_rate:.3f}%")

    sens_path = OUTPUTS_TABLES / "target_sensitivity.csv"
    sens_df.to_csv(sens_path, index=False)

    # 5. VINTAGE QUARTER PLOT
    print("\nGenerating Vintage Quarter Default Rate Plot...")
    q_summary = df.groupby("vintage_quarter", as_index=False).agg(
        n_loans=("loan_status", "count"),
        n_default_12m=("default_12m", "sum")
    )
    q_summary["default_12m_rate"] = (q_summary["n_default_12m"] / q_summary["n_loans"]) * 100

    plt.figure(figsize=(14, 6))
    plt.plot(q_summary["vintage_quarter"], q_summary["default_12m_rate"], marker="o", color="#d62728", linewidth=2)
    plt.title("12-Month Default Rate Trend by Vintage Quarter (2007Q2 - 2014Q4)", fontsize=13, fontweight="bold")
    plt.xlabel("Vintage Quarter", fontsize=11)
    plt.ylabel("12-Month Default Rate (%)", fontsize=11)
    plt.xticks(rotation=45, ha="right", fontsize=9)
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    q_fig_path = OUTPUTS_FIGURES / "default_rate_by_vintage_quarter.png"
    plt.savefig(q_fig_path, dpi=300)
    plt.close()
    print(f"Quarterly trend plot saved to: {q_fig_path}")


if __name__ == "__main__":
    run_target_qa()
