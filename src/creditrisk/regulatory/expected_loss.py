"""
expected_loss.py
----------------
Expected Loss (EL) calculation engine: EL = PD * LGD * EAD.

Integrates the deployment PD Model (Model B), Two-Stage LGD Model, and EAD module
to calculate baseline expected loss across loan portfolios and produce regulatory/risk
summary breakdowns by rating grade and vintage year.
"""

from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union
import numpy as np
import pandas as pd

from creditrisk.features.binning import WoEBinner
from creditrisk.models.ead_model import get_portfolio_ead
from creditrisk.models.lgd_model import TwoStageLGD
from creditrisk.models.pd_model import PDModel

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SUMMARY_PATH = PROJECT_ROOT / "outputs" / "tables" / "expected_loss_summary.csv"


def compute_expected_loss(
    df: pd.DataFrame,
    pd_model: PDModel,
    lgd_model: TwoStageLGD,
    woe_binner_pd: WoEBinner,
    woe_binner_lgd: Optional[WoEBinner] = None
) -> pd.DataFrame:
    """
    Computes Expected Loss (EL = PD * LGD * EAD) for every loan in the DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Loan portfolio DataFrame containing feature columns and loan status.
    pd_model : PDModel
        Fitted Probability of Default model (Model B).
    lgd_model : TwoStageLGD
        Fitted Two-Stage Loss Given Default model.
    woe_binner_pd : WoEBinner
        Pre-fitted WoE binner for PD features.
    woe_binner_lgd : Optional[WoEBinner]
        Optional WoE binner for LGD (defaults to lgd_model.woe_binner).

    Returns
    -------
    pd.DataFrame
        Copy of input DataFrame augmented with `pd_hat`, `lgd_hat`, `ead`, and `el`.
    """
    df_out = df.copy()

    # 1. Predict Probability of Default (PD) using Model B
    df_out["pd_hat"] = pd_model.predict_pd(df_out, woe_binner_pd)
    df_out["pd_hat"] = np.clip(df_out["pd_hat"], 0.0, 1.0)

    # 2. Predict Loss Given Default (LGD) using TwoStageLGD
    df_out["lgd_hat"] = lgd_model.predict_lgd(df_out)

    # 3. Calculate Exposure At Default (EAD)
    df_out["ead"] = get_portfolio_ead(df_out)

    # 4. Expected Loss: EL = PD * LGD * EAD
    df_out["el"] = df_out["pd_hat"] * df_out["lgd_hat"] * df_out["ead"]

    return df_out


def portfolio_el_summary(
    df: pd.DataFrame,
    output_path: Union[str, Path] = DEFAULT_SUMMARY_PATH
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Computes total EAD, total EL, and EL % of EAD, broken down by rating grade and vintage year.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame processed via compute_expected_loss containing `pd_hat`, `lgd_hat`, `ead`, `el`.
    output_path : str or Path
        Destination filepath for summary CSV.

    Returns
    -------
    Tuple[pd.DataFrame, Dict[str, Any]]
        Summary breakdown DataFrame and overall portfolio metrics dictionary.
    """
    for col in ["pd_hat", "lgd_hat", "ead", "el"]:
        if col not in df.columns:
            raise KeyError(f"Missing required Expected Loss column '{col}'. Run compute_expected_loss first.")

    total_count = len(df)
    total_ead = float(df["ead"].sum())
    total_el = float(df["el"].sum())
    el_pct_ead = float((total_el / total_ead * 100.0) if total_ead > 0 else 0.0)

    portfolio_metrics = {
        "portfolio_count": total_count,
        "mean_pd": float(df["pd_hat"].mean()),
        "mean_lgd": float(df["lgd_hat"].mean()),
        "mean_ead": float(df["ead"].mean()),
        "total_ead": total_ead,
        "total_el": total_el,
        "el_pct_ead": el_pct_ead
    }

    # 1. Overall Summary Row
    overall_row = pd.DataFrame([{
        "segment": "Overall",
        "category": "All Portfolio",
        "count": total_count,
        "total_ead": total_ead,
        "total_el": total_el,
        "el_pct_ead": el_pct_ead,
        "mean_pd": portfolio_metrics["mean_pd"],
        "mean_lgd": portfolio_metrics["mean_lgd"]
    }])

    # 2. Breakdown by Grade
    grade_rows = []
    if "grade" in df.columns:
        g_summary = (
            df.groupby("grade")
            .agg(
                count=("el", "count"),
                total_ead=("ead", "sum"),
                total_el=("el", "sum"),
                mean_pd=("pd_hat", "mean"),
                mean_lgd=("lgd_hat", "mean")
            )
            .reset_index()
        )
        g_summary["el_pct_ead"] = np.where(g_summary["total_ead"] > 0, g_summary["total_el"] / g_summary["total_ead"] * 100.0, 0.0)
        g_summary.insert(0, "segment", "By Grade")
        g_summary.rename(columns={"grade": "category"}, inplace=True)
        grade_rows.append(g_summary)

    # 3. Breakdown by Vintage Year
    vintage_rows = []
    if "vintage_year" in df.columns or "issue_d" in df.columns:
        v_col = "vintage_year" if "vintage_year" in df.columns else "issue_d"
        v_summary = (
            df.groupby(v_col)
            .agg(
                count=("el", "count"),
                total_ead=("ead", "sum"),
                total_el=("el", "sum"),
                mean_pd=("pd_hat", "mean"),
                mean_lgd=("lgd_hat", "mean")
            )
            .reset_index()
        )
        v_summary["el_pct_ead"] = np.where(v_summary["total_ead"] > 0, v_summary["total_el"] / v_summary["total_ead"] * 100.0, 0.0)
        v_summary.insert(0, "segment", "By Vintage")
        v_summary.rename(columns={v_col: "category"}, inplace=True)
        vintage_rows.append(v_summary)

    # Combine into single table
    summary_dfs = [overall_row] + grade_rows + vintage_rows
    summary_combined = pd.concat(summary_dfs, ignore_index=True)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary_combined.to_csv(output_path, index=False)

    print("=" * 75)
    print(" EXPECTED LOSS (EL = PD * LGD * EAD) PORTFOLIO SUMMARY")
    print("=" * 75)
    print(f"Total Portfolio Loans        : {portfolio_metrics['portfolio_count']:,}")
    print(f"Mean Predicted PD            : {portfolio_metrics['mean_pd']:.4f} ({portfolio_metrics['mean_pd']*100:.2f}%)")
    print(f"Mean Predicted LGD           : {portfolio_metrics['mean_lgd']:.4f} ({portfolio_metrics['mean_lgd']*100:.2f}%)")
    print(f"Mean EAD                     : ${portfolio_metrics['mean_ead']:,.2f}")
    print(f"Total Portfolio EAD          : ${portfolio_metrics['total_ead']:,.2f}")
    print(f"Total Expected Loss (EL)     : ${portfolio_metrics['total_el']:,.2f}")
    print(f"Portfolio EL % of EAD        : {portfolio_metrics['el_pct_ead']:.2f}%")
    print("=" * 75)
    print(f"Saved Expected Loss summary to: {output_path}")

    return summary_combined, portfolio_metrics
