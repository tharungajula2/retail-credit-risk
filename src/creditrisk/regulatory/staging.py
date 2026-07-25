"""
staging.py
----------
IFRS 9 Staging and Significant Increase in Credit Risk (SICR) classification module.

Stage 3 (Credit-Impaired / Default): Loan is in default (ever_default == 1 or 90+ DPD). PD = 1.0.
Stage 2 (SICR): Loan triggered SICR but not in default:
  (a) Quantitative: Current 12m PD >= 2.0x Origination PD (grade-level proxy) OR Current 12m PD > 0.06.
  (b) Backstop: 30+ DPD (Late 16-30 days, Late 31-120 days).
Stage 1 (Performing): All other healthy loans.
"""

from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union
import numpy as np
import pandas as pd
import yaml

from creditrisk.features.binning import WoEBinner
from creditrisk.models.ead_model import get_portfolio_ead
from creditrisk.models.pd_model import PDModel

PROJECT_ROOT = Path(__file__).resolve().parents[3]
CONFIG_PATH = PROJECT_ROOT / "config" / "ifrs9.yaml"
DEFAULT_SUMMARY_PATH = PROJECT_ROOT / "outputs" / "tables" / "staging_summary.csv"


def load_ifrs9_config(config: Union[Dict[str, Any], Path, str] = CONFIG_PATH) -> Dict[str, Any]:
    """Loads IFRS 9 configuration parameters."""
    if isinstance(config, (str, Path)):
        path = Path(config)
        if not path.exists():
            # Return default dictionary if file not found
            return {
                "sicr_relative_threshold": 2.0,
                "sicr_absolute_pd": 0.06,
                "dpd_backstop_days": 30,
                "default_statuses": ["Charged Off", "Default", "Late (31-120 days)"]
            }
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    elif isinstance(config, dict):
        return config
    else:
        raise TypeError("Config must be a dictionary or file path.")


def assign_ifrs9_stages(
    df: pd.DataFrame,
    pd_model: Optional[PDModel] = None,
    woe_binner_pd: Optional[WoEBinner] = None,
    config: Union[Dict[str, Any], Path, str] = CONFIG_PATH
) -> pd.DataFrame:
    """
    Classifies portfolio loans into IFRS 9 Stage 1, Stage 2, or Stage 3.

    New Columns Created:
    - current_pd_12m  : Predicted 12-month PD (or 1.0 for Stage 3 defaults)
    - origination_pd  : Grade-level average PD proxy at origination
    - pd_ratio        : current_pd_12m / origination_pd
    - sicr_quant_flag : 1 if pd_ratio >= 2.0 OR current_pd_12m > 0.06
    - sicr_dpd_flag   : 1 if 30+ DPD / Late status
    - stage           : 'Stage 1', 'Stage 2', or 'Stage 3'

    Parameters
    ----------
    df : pd.DataFrame
        Loan portfolio DataFrame.
    pd_model : Optional[PDModel]
        Fitted PD Model B instance.
    woe_binner_pd : Optional[WoEBinner]
        Pre-fitted PD WoEBinner instance.
    config : dict or Path
        IFRS 9 configuration.

    Returns
    -------
    pd.DataFrame
        Copy of DataFrame augmented with IFRS 9 staging variables.
    """
    cfg = load_ifrs9_config(config)
    rel_thresh = cfg.get("sicr_relative_threshold", 2.0)
    abs_thresh = cfg.get("sicr_absolute_pd", 0.06)

    df_out = df.copy()

    # 1. Obtain current 12-month PD predictions if pd_hat is not already provided
    if "current_pd_12m" not in df_out.columns:
        if "pd_hat" in df_out.columns:
            df_out["current_pd_12m"] = df_out["pd_hat"]
        elif pd_model is not None and woe_binner_pd is not None:
            df_out["current_pd_12m"] = pd_model.predict_pd(df_out, woe_binner_pd)
        else:
            raise ValueError("Must provide 'pd_hat' column or (pd_model, woe_binner_pd) arguments.")

    # Clamp predicted PD to [0, 1]
    df_out["current_pd_12m"] = np.clip(df_out["current_pd_12m"], 0.0, 1.0)

    # 2. Derive origination PD proxy: grade-level average PD at issue (if not already present)
    if "origination_pd" not in df_out.columns:
        if "grade" in df_out.columns:
            grade_avg_pd = df_out.groupby("grade")["current_pd_12m"].transform("mean")
            df_out["origination_pd"] = grade_avg_pd
        else:
            df_out["origination_pd"] = float(df_out["current_pd_12m"].mean())

    # Avoid zero division
    valid_orig_pd = np.maximum(df_out["origination_pd"], 1e-4)
    df_out["pd_ratio"] = df_out["current_pd_12m"] / valid_orig_pd

    # 3. Identify Stage 3 defaults
    if "ever_default" in df_out.columns:
        is_stage3 = (df_out["ever_default"] == 1)
    elif "loan_status" in df_out.columns:
        def_statuses = set(cfg.get("default_statuses", ["Charged Off", "Default", "Late (31-120 days)"]))
        is_stage3 = df_out["loan_status"].isin(def_statuses)
    else:
        is_stage3 = pd.Series(False, index=df_out.index)

    # Set PD = 1.0 for Stage 3 defaults
    df_out["current_pd_12m"] = np.where(is_stage3, 1.0, df_out["current_pd_12m"])

    # 4. Identify 30+ DPD Backstop (Stage 2 Trigger)
    is_30dpd = pd.Series(False, index=df_out.index)
    if "loan_status" in df_out.columns:
        status_str = df_out["loan_status"].astype(str)
        is_30dpd = status_str.str.contains("Late", case=False, na=False)
    if "days_past_due" in df_out.columns:
        is_30dpd = is_30dpd | (df_out["days_past_due"] >= 30)

    df_out["sicr_dpd_flag"] = is_30dpd.astype(int)

    # 5. Identify Quantitative SICR (Stage 2 Trigger)
    is_quant_sicr = (df_out["pd_ratio"] >= rel_thresh) | (df_out["current_pd_12m"] > abs_thresh)
    df_out["sicr_quant_flag"] = is_quant_sicr.astype(int)

    # Combine Stage 2 triggers (Quantitative OR Backstop DPD)
    is_stage2 = (~is_stage3) & (is_quant_sicr | is_30dpd)

    # 6. Assign final IFRS 9 Stage (if not already assigned)
    if "stage" not in df_out.columns:
        df_out["stage"] = np.where(is_stage3, "Stage 3", np.where(is_stage2, "Stage 2", "Stage 1"))

    # Calculate EAD if not present
    if "ead" not in df_out.columns:
        df_out["ead"] = get_portfolio_ead(df_out)

    return df_out


def stage_summary(
    df: pd.DataFrame,
    output_path: Union[str, Path] = DEFAULT_SUMMARY_PATH
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Computes count, % of loans, total EAD, % of EAD, and mean PD per stage.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame processed via assign_ifrs9_stages containing 'stage', 'ead', 'current_pd_12m'.
    output_path : str or Path
        Destination CSV filepath.

    Returns
    -------
    Tuple[pd.DataFrame, Dict[str, Any]]
        Summary DataFrame and metrics dictionary.
    """
    for col in ["stage", "ead", "current_pd_12m"]:
        if col not in df.columns:
            raise KeyError(f"Missing required column '{col}' for stage summary.")

    total_count = len(df)
    total_ead = float(df["ead"].sum())

    summary_df = (
        df.groupby("stage")
        .agg(
            count=("ead", "count"),
            total_ead=("ead", "sum"),
            mean_pd_12m=("current_pd_12m", "mean")
        )
        .reset_index()
    )

    summary_df["count_pct"] = (summary_df["count"] / total_count * 100.0) if total_count > 0 else 0.0
    summary_df["ead_pct"] = (summary_df["total_ead"] / total_ead * 100.0) if total_ead > 0 else 0.0

    # Ensure Stage 1, Stage 2, Stage 3 order
    stage_order = {"Stage 1": 1, "Stage 2": 2, "Stage 3": 3}
    summary_df["order"] = summary_df["stage"].map(stage_order).fillna(4)
    summary_df = summary_df.sort_values("order").drop(columns=["order"]).reset_index(drop=True)

    # Total row
    total_row = pd.DataFrame([{
        "stage": "Total",
        "count": total_count,
        "count_pct": 100.0,
        "total_ead": total_ead,
        "ead_pct": 100.0,
        "mean_pd_12m": float(df["current_pd_12m"].mean())
    }])

    summary_combined = pd.concat([summary_df, total_row], ignore_index=True)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary_combined.to_csv(output_path, index=False)

    print("=" * 70)
    print(" IFRS 9 STAGING SUMMARY TABLE")
    print("=" * 70)
    print(summary_combined.to_string(index=False))
    print("=" * 70)
    print(f"Saved IFRS 9 staging summary to: {output_path}")

    metrics = {
        "total_count": total_count,
        "total_ead": total_ead,
        "stage1_ead_pct": float(summary_df.loc[summary_df["stage"] == "Stage 1", "ead_pct"].values[0]) if "Stage 1" in summary_df["stage"].values else 0.0,
        "stage2_ead_pct": float(summary_df.loc[summary_df["stage"] == "Stage 2", "ead_pct"].values[0]) if "Stage 2" in summary_df["stage"].values else 0.0,
        "stage3_ead_pct": float(summary_df.loc[summary_df["stage"] == "Stage 3", "ead_pct"].values[0]) if "Stage 3" in summary_df["stage"].values else 0.0,
    }

    return summary_combined, metrics
