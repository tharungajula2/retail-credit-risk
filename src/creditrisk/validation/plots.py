"""
plots.py
--------
Validation Diagnostic Visualizations:
- ROC Curve Plot
- Kolmogorov-Smirnov (KS) Cumulative Separation Plot
- Probability Calibration Plot (Predicted vs Observed with 45-degree reference line)
"""

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import roc_curve
from creditrisk.validation.metrics import calibration_table, gini_auc, ks_statistic

OUTPUT_FIGURES_DIR = Path(__file__).resolve().parents[3] / "outputs" / "figures"


def roc_curve_plot(
    y_true: np.ndarray,
    pd_pred: np.ndarray,
    model_name: str,
    sample_name: str,
    output_dir: Path = OUTPUT_FIGURES_DIR,
) -> Path:
    """Generates and saves ROC Curve plot."""
    fpr, tpr, _ = roc_curve(y_true, pd_pred)
    auc, gini = gini_auc(y_true, pd_pred)

    plt.figure(figsize=(7, 6))
    plt.plot(fpr, tpr, color="#1f77b4", lw=2, label=f"ROC Curve (AUC = {auc:.4f}, Gini = {gini:.4f})")
    plt.plot([0, 1], [0, 1], color="gray", linestyle="--", lw=1, label="Random Model (AUC = 0.5)")

    plt.title(f"ROC Curve - {model_name.upper()} ({sample_name.upper()} Sample)", fontsize=12, fontweight="bold")
    plt.xlabel("False Positive Rate", fontsize=10)
    plt.ylabel("True Positive Rate", fontsize=10)
    plt.legend(loc="lower right", fontsize=10)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()

    output_dir.mkdir(parents=True, exist_ok=True)
    file_path = output_dir / f"roc_{model_name}_{sample_name}.png"
    plt.savefig(file_path, dpi=300)
    plt.close()
    return file_path


def ks_plot(
    y_true: np.ndarray,
    pd_pred: np.ndarray,
    model_name: str,
    sample_name: str,
    output_dir: Path = OUTPUT_FIGURES_DIR,
) -> Path:
    """Generates and saves Kolmogorov-Smirnov (KS) plot."""
    ks_stat, cutoff = ks_statistic(y_true, pd_pred)

    df = pd.DataFrame({"y_true": y_true, "pd_pred": pd_pred})
    df = df.sort_values("pd_pred", ascending=False).reset_index(drop=True)

    n_bad = (df["y_true"] == 1).sum()
    n_good = (df["y_true"] == 0).sum()

    cum_bad = (df["y_true"] == 1).cumsum() / n_bad
    cum_good = (df["y_true"] == 0).cumsum() / n_good
    pop_pct = np.linspace(0, 100, len(df))

    plt.figure(figsize=(8, 6))
    plt.plot(pop_pct, cum_bad, color="#d62728", lw=2, label="Cumulative Bads (Defaults)")
    plt.plot(pop_pct, cum_good, color="#2ca02c", lw=2, label="Cumulative Goods (Non-Defaults)")

    plt.title(f"KS Plot - {model_name.upper()} ({sample_name.upper()}) | KS = {ks_stat*100:.2f}%", fontsize=12, fontweight="bold")
    plt.xlabel("Percentage of Population Ranked by Risk (%)", fontsize=10)
    plt.ylabel("Cumulative Proportion", fontsize=10)
    plt.legend(loc="lower right", fontsize=10)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()

    output_dir.mkdir(parents=True, exist_ok=True)
    file_path = output_dir / f"ks_{model_name}_{sample_name}.png"
    plt.savefig(file_path, dpi=300)
    plt.close()
    return file_path


def calibration_plot(
    y_true: np.ndarray,
    pd_pred: np.ndarray,
    model_name: str,
    sample_name: str,
    output_dir: Path = OUTPUT_FIGURES_DIR,
) -> Path:
    """Generates and saves Calibration Plot (Predicted vs Observed with 45-degree ideal reference line)."""
    calib_df = calibration_table(y_true, pd_pred, n_bins=10)

    pred_pds = calib_df["mean_predicted_pd"] * 100
    obs_rates = calib_df["observed_default_rate"] * 100

    plt.figure(figsize=(7, 6))
    plt.plot(pred_pds, obs_rates, marker="o", color="#ff7f0e", lw=2, label="Model Deciles")

    # 45-degree perfect calibration line
    max_val = max(pred_pds.max(), obs_rates.max()) * 1.1
    plt.plot([0, max_val], [0, max_val], color="gray", linestyle="--", lw=1.5, label="Perfect Calibration (45° Line)")

    plt.title(f"Probability Calibration - {model_name.upper()} ({sample_name.upper()})", fontsize=12, fontweight="bold")
    plt.xlabel("Mean Predicted PD (%)", fontsize=10)
    plt.ylabel("Observed Default Rate (%)", fontsize=10)
    plt.legend(loc="upper left", fontsize=10)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()

    output_dir.mkdir(parents=True, exist_ok=True)
    file_path = output_dir / f"calibration_{model_name}_{sample_name}.png"
    plt.savefig(file_path, dpi=300)
    plt.close()
    return file_path
