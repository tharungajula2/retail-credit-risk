"""
run_stability.py
----------------
Execution script that runs score PSI (Population Stability Index) and feature CSI
(Characteristic Stability Index) comparing Train (2007-2013) vs OOT (2014).
Saves CSV tables and decile PSI plots.
"""

from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
from creditrisk.features.binning import WoEBinner
from creditrisk.models.pd_model import PDModel
from creditrisk.models.scorecard import score_dataset
from creditrisk.validation.stability import csi, get_stability_band, psi

PROJECT_ROOT = Path(__file__).resolve().parents[3]
TRAIN_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "train.parquet"
OOT_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "oot.parquet"
WOE_BINNER_PATH = PROJECT_ROOT / "outputs" / "models" / "woe_binner.pkl"
MODEL_A_PATH = PROJECT_ROOT / "outputs" / "models" / "pd_model_a.pkl"
MODEL_B_PATH = PROJECT_ROOT / "outputs" / "models" / "pd_model_b.pkl"

SCORECARD_A_PATH = PROJECT_ROOT / "outputs" / "tables" / "scorecard_model_a.csv"
SCORECARD_B_PATH = PROJECT_ROOT / "outputs" / "tables" / "scorecard_model_b.csv"

OUTPUT_TABLES_DIR = PROJECT_ROOT / "outputs" / "tables"
OUTPUT_FIGURES_DIR = PROJECT_ROOT / "outputs" / "figures"


def main():
    OUTPUT_TABLES_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading train and oot datasets...")
    train_df = pd.read_parquet(TRAIN_DATA_PATH)
    oot_df = pd.read_parquet(OOT_DATA_PATH)

    print(f"Loading pre-fitted WoEBinner from: {WOE_BINNER_PATH}...")
    woe_binner = WoEBinner.load(WOE_BINNER_PATH)

    model_a = PDModel.load(MODEL_A_PATH)
    model_b = PDModel.load(MODEL_B_PATH)

    scorecard_a = pd.read_csv(SCORECARD_A_PATH)
    scorecard_b = pd.read_csv(SCORECARD_B_PATH)

    models_info = [
        {"name": "model_a", "model": model_a, "scorecard": scorecard_a},
        {"name": "model_b", "model": model_b, "scorecard": scorecard_b},
    ]

    psi_summary_rows = []
    csi_summary_rows = []

    print("\n" + "=" * 70)
    print("               RUNNING POPULATION STABILITY INDEX (PSI)               ")
    print("=" * 70)

    for info in models_info:
        m_name = info["name"]
        m_obj = info["model"]
        sc_df = info["scorecard"]

        # Score datasets
        train_scores = score_dataset(train_df, sc_df, woe_binner)
        oot_scores = score_dataset(oot_df, sc_df, woe_binner)

        psi_val, psi_detail = psi(train_scores, oot_scores, n_bins=10)
        band = get_stability_band(psi_val)

        psi_summary_rows.append(
            {
                "model": m_name,
                "score_psi": psi_val,
                "stability_band": band,
            }
        )

        print(f"{m_name.upper()} Score PSI (Train vs OOT 2014): {psi_val:.4f} -> [{band.upper()}]")

        # Plot PSI decile distribution bar chart
        plt.figure(figsize=(9, 5))
        x_indices = range(len(psi_detail))
        width = 0.35
        plt.bar([i - width/2 for i in x_indices], psi_detail["expected_pct"] * 100, width=width, label="Train (Expected)", color="#1f77b4")
        plt.bar([i + width/2 for i in x_indices], psi_detail["actual_pct"] * 100, width=width, label="OOT 2014 (Actual)", color="#ff7f0e")

        plt.title(f"Score Distribution PSI: {m_name.upper()} (PSI = {psi_val:.4f} - {band.upper()})", fontsize=12, fontweight="bold")
        plt.xlabel("Score Decile Interval (Fixed Train Edges)", fontsize=10)
        plt.ylabel("Percentage of Population (%)", fontsize=10)
        plt.xticks(x_indices, [f"D{i+1}" for i in x_indices], fontsize=9)
        plt.legend(fontsize=10)
        plt.grid(axis="y", linestyle="--", alpha=0.5)
        plt.tight_layout()

        fig_path = OUTPUT_FIGURES_DIR / f"psi_{m_name}.png"
        plt.savefig(fig_path, dpi=300)
        plt.close()

        # Compute CSI for every model feature
        for feature in m_obj.features_:
            csi_val, _ = csi(train_df, oot_df, feature, woe_binner)
            csi_band = get_stability_band(csi_val)

            csi_summary_rows.append(
                {
                    "model": m_name,
                    "variable": feature,
                    "csi": csi_val,
                    "stability_band": csi_band,
                }
            )

    # Save summary tables
    psi_summary_df = pd.DataFrame(psi_summary_rows)
    psi_path = OUTPUT_TABLES_DIR / "psi_summary.csv"
    psi_summary_df.to_csv(psi_path, index=False)

    csi_summary_df = pd.DataFrame(csi_summary_rows).sort_values(["model", "csi"], ascending=[True, False]).reset_index(drop=True)
    csi_path = OUTPUT_TABLES_DIR / "csi_by_variable.csv"
    csi_summary_df.to_csv(csi_path, index=False)

    print(f"\nPSI Summary Table saved to: {psi_path}")
    print(f"CSI Table saved to: {csi_path}")

    print("\n" + "=" * 70)
    print("                    SCORE PSI SUMMARY TABLE                    ")
    print("=" * 70)
    print(psi_summary_df.to_string(index=False))

    print("\n" + "=" * 70)
    print("               CHARACTERISTIC STABILITY INDEX (CSI) TABLE             ")
    print("=" * 70)
    print(csi_summary_df.to_string(index=False))


if __name__ == "__main__":
    main()
