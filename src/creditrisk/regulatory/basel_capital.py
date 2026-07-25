"""
basel_capital.py
----------------
Basel III Internal Ratings-Based (IRB) and Standardised Approach regulatory capital engine
for retail exposures.

Implements:
- Basel asset correlation R for "Other Retail" exposures.
- Capital requirement K under 99.9% Vasicek single-index asymptotic risk factor model.
- Risk-Weighted Assets (RWA) and Risk Weights (IRB vs Standardised 75%).
- Downturn LGD adjustment using supervisory add-on approach.
- Minimum Capital requirements (Total 8%, Tier 1 6%, CET1 4.5%).
"""

from pathlib import Path
from typing import Any, Dict, Tuple, Union
import numpy as np
import pandas as pd
from scipy.stats import norm

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SUMMARY_PATH = PROJECT_ROOT / "outputs" / "tables" / "basel_capital_summary.csv"
DEFAULT_DOWNTURN_PATH = PROJECT_ROOT / "outputs" / "tables" / "basel_downturn_comparison.csv"

# Regulatory floors and constraints
BASEL_PD_FLOOR = 0.0003  # 0.03% PD floor


def basel_correlation(pd: Union[float, np.ndarray, pd.Series]) -> Union[float, np.ndarray, pd.Series]:
    """
    Calculates Basel asset correlation R for 'Other Retail' exposures.

    Formula:
    R = 0.03 * (1 - exp(-35 * PD)) / (1 - exp(-35))
        + 0.16 * (1 - (1 - exp(-35 * PD)) / (1 - exp(-35)))
    """
    pd_arr = np.asarray(pd, dtype=float)
    denom = 1.0 - np.exp(-35.0)
    factor = (1.0 - np.exp(-35.0 * pd_arr)) / denom

    r = 0.03 * factor + 0.16 * (1.0 - factor)
    return float(r) if np.ndim(pd) == 0 else r


def basel_correlation_qrre(pd: Union[float, np.ndarray, pd.Series]) -> Union[float, np.ndarray, pd.Series]:
    """
    Calculates Basel asset correlation R for Qualifying Revolving Retail Exposures (QRRE).

    Basel QRRE rules specify a flat correlation of R = 0.04 (4.0%) for credit cards / revolving lines.

    PORTFOLIO NOTE:
    LendingClub term instalment loans are classified under 'Other Retail' (using basel_correlation),
    which features a PD-dependent asset correlation curve ranging between 0.03 and 0.16.
    `basel_correlation_qrre` is provided for completeness when evaluating revolving portfolios.
    """
    pd_arr = np.asarray(pd, dtype=float)
    r = np.full_like(pd_arr, 0.04) if np.ndim(pd) > 0 else 0.04
    return float(r) if np.ndim(pd) == 0 else r



def basel_capital_k(
    pd: Union[float, np.ndarray, pd.Series],
    lgd: Union[float, np.ndarray, pd.Series]
) -> Union[float, np.ndarray, pd.Series]:
    """
    Calculates Basel capital requirement K (fraction of EAD) under 99.9% confidence.

    Floors PD at 0.0003 (Basel PD floor) and caps LGD at 1.0.

    Formula:
    K = LGD * N( (1/sqrt(1-R)) * G(PD) + sqrt(R/(1-R)) * G(0.999) ) - PD * LGD
    where N is standard normal CDF, G is inverse standard normal CDF (ppf).
    """
    pd_arr = np.maximum(np.asarray(pd, dtype=float), BASEL_PD_FLOOR)
    lgd_arr = np.minimum(np.maximum(np.asarray(lgd, dtype=float), 0.0), 1.0)

    r = basel_correlation(pd_arr)

    g_pd = norm.ppf(pd_arr)
    g_999 = norm.ppf(0.999)

    term1 = (1.0 / np.sqrt(1.0 - r)) * g_pd
    term2 = np.sqrt(r / (1.0 - r)) * g_999

    conditional_pd = norm.cdf(term1 + term2)
    k = lgd_arr * conditional_pd - pd_arr * lgd_arr

    # Clamp K to non-negative
    k_clamped = np.maximum(k, 0.0)
    return float(k_clamped) if np.ndim(pd) == 0 and np.ndim(lgd) == 0 else k_clamped


def downturn_lgd(
    lgd: Union[float, np.ndarray, pd.Series],
    floor: float = 0.0,
    method: str = "supervisory"
) -> Union[float, np.ndarray, pd.Series]:
    """
    Calculates Downturn LGD using a supervisory add-on approach.

    DOCUMENTED LIMITATION:
    A commercial bank derives downturn LGD empirically from recession-period recovery data
    (e.g., 2008-2009 economic downturn window). In this implementation, we apply a standard
    supervisory proxy add-on (+8 percentage points), capped strictly at 1.0.

    Formula:
    downturn_LGD = min(1.0, max(LGD, floor) + 0.08)
    """
    lgd_arr = np.maximum(np.asarray(lgd, dtype=float), floor)
    dt_lgd = np.minimum(1.0, lgd_arr + 0.08)
    return float(dt_lgd) if np.ndim(lgd) == 0 else dt_lgd


def risk_weighted_assets(
    pd: Union[float, np.ndarray, pd.Series],
    lgd: Union[float, np.ndarray, pd.Series],
    ead: Union[float, np.ndarray, pd.Series]
) -> Tuple[Union[float, np.ndarray], Union[float, np.ndarray]]:
    """
    Calculates IRB Risk-Weighted Assets (RWA) and Risk Weight (as % of EAD).

    RWA = K * 12.5 * EAD
    Risk Weight = K * 12.5 * 100%
    """
    k = basel_capital_k(pd, lgd)
    ead_arr = np.asarray(ead, dtype=float)

    rwa = k * 12.5 * ead_arr
    rw_pct = k * 12.5 * 100.0

    return rwa, rw_pct


def standardised_rwa(ead: Union[float, np.ndarray, pd.Series]) -> Union[float, np.ndarray]:
    """
    Calculates Standardised Approach RWA (flat 75% risk weight for unrated retail).
    Standardised RWA = 0.75 * EAD
    """
    ead_arr = np.asarray(ead, dtype=float)
    return 0.75 * ead_arr


def compare_downturn_capital(
    df: pd.DataFrame,
    output_path: Union[str, Path] = DEFAULT_DOWNTURN_PATH
) -> pd.DataFrame:
    """
    Recomputes portfolio IRB RWA and capital requirements twice:
    (a) using average LGD (lgd_hat)
    (b) using downturn LGD (downturn_lgd)
    Saves comparison summary to output_path.
    """
    for col in ["pd_hat", "lgd_hat", "ead"]:
        if col not in df.columns:
            raise KeyError(f"Missing required column '{col}' for Downturn LGD comparison.")

    total_ead = float(df["ead"].sum())
    
    # 1. Average LGD
    rwa_avg, _ = risk_weighted_assets(df["pd_hat"], df["lgd_hat"], df["ead"])
    total_rwa_avg = float(rwa_avg.sum())
    capital_avg = 0.08 * total_rwa_avg
    rw_avg_pct = (total_rwa_avg / total_ead * 100.0) if total_ead > 0 else 0.0

    # 2. Downturn LGD
    lgd_dt = downturn_lgd(df["lgd_hat"])
    rwa_dt, _ = risk_weighted_assets(df["pd_hat"], lgd_dt, df["ead"])
    total_rwa_dt = float(rwa_dt.sum())
    capital_dt = 0.08 * total_rwa_dt
    rw_dt_pct = (total_rwa_dt / total_ead * 100.0) if total_ead > 0 else 0.0

    diff_rwa = total_rwa_dt - total_rwa_avg
    diff_capital = capital_dt - capital_avg
    pct_increase_capital = (diff_capital / capital_avg * 100.0) if capital_avg > 0 else 0.0

    comp_df = pd.DataFrame([
        {
            "lgd_approach": "Average LGD",
            "mean_lgd": float(df["lgd_hat"].mean()),
            "total_ead": total_ead,
            "total_rwa": total_rwa_avg,
            "risk_weight_pct": rw_avg_pct,
            "min_capital_8pct": capital_avg,
            "tier1_capital_6pct": 0.06 * total_rwa_avg,
            "cet1_capital_4.5pct": 0.045 * total_rwa_avg
        },
        {
            "lgd_approach": "Downturn LGD (+8pp add-on)",
            "mean_lgd": float(np.mean(lgd_dt)),
            "total_ead": total_ead,
            "total_rwa": total_rwa_dt,
            "risk_weight_pct": rw_dt_pct,
            "min_capital_8pct": capital_dt,
            "tier1_capital_6pct": 0.06 * total_rwa_dt,
            "cet1_capital_4.5pct": 0.045 * total_rwa_dt
        },
        {
            "lgd_approach": "Downturn Capital Increase (Delta)",
            "mean_lgd": float(np.mean(lgd_dt) - df["lgd_hat"].mean()),
            "total_ead": 0.0,
            "total_rwa": diff_rwa,
            "risk_weight_pct": rw_dt_pct - rw_avg_pct,
            "min_capital_8pct": diff_capital,
            "tier1_capital_6pct": 0.06 * diff_rwa,
            "cet1_capital_4.5pct": 0.045 * diff_rwa
        }
    ])

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    comp_df.to_csv(output_path, index=False)

    print("=" * 75)
    print(" BASEL IRB CAPITAL COMPARISON: AVERAGE LGD vs DOWNTURN LGD")
    print("=" * 75)
    print(f"Average LGD Total RWA            : ${total_rwa_avg:,.2f}  (RW: {rw_avg_pct:.2f}%)")
    print(f"Downturn LGD Total RWA           : ${total_rwa_dt:,.2f}  (RW: {rw_dt_pct:.2f}%)")
    print(f"RWA Increase (Downturn Impact)   : ${diff_rwa:,.2f}")
    print("-" * 75)
    print(f"Min Capital (Average LGD)        : ${capital_avg:,.2f}")
    print(f"Min Capital (Downturn LGD)       : ${capital_dt:,.2f}")
    print(f"Capital Increase ($ / %)         : +${diff_capital:,.2f} (+{pct_increase_capital:.2f}%)")
    print("=" * 75)
    print(f"Saved Downturn LGD comparison to: {output_path}")

    return comp_df


def portfolio_capital_summary(
    df: pd.DataFrame,
    output_path: Union[str, Path] = DEFAULT_SUMMARY_PATH
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Computes portfolio-level Basel IRB vs Standardised capital requirements.
    """
    for col in ["pd_hat", "lgd_hat", "ead"]:
        if col not in df.columns:
            raise KeyError(f"Missing required column '{col}' for Basel capital calculation.")

    df_calc = df.copy()

    df_calc["basel_k"] = basel_capital_k(df_calc["pd_hat"], df_calc["lgd_hat"])
    df_calc["irb_rwa"], df_calc["irb_rw_pct"] = risk_weighted_assets(
        df_calc["pd_hat"], df_calc["lgd_hat"], df_calc["ead"]
    )
    df_calc["std_rwa"] = standardised_rwa(df_calc["ead"])

    total_count = len(df_calc)
    total_ead = float(df_calc["ead"].sum())
    total_irb_rwa = float(df_calc["irb_rwa"].sum())
    total_std_rwa = float(df_calc["std_rwa"].sum())

    min_total_capital = 0.08 * total_irb_rwa
    min_tier1_capital = 0.06 * total_irb_rwa
    min_cet1_capital  = 0.045 * total_irb_rwa

    overall_irb_rw = (total_irb_rwa / total_ead * 100.0) if total_ead > 0 else 0.0
    overall_std_rw = 75.0

    portfolio_metrics = {
        "count": total_count,
        "total_ead": total_ead,
        "total_irb_rwa": total_irb_rwa,
        "total_std_rwa": total_std_rwa,
        "overall_irb_rw_pct": overall_irb_rw,
        "overall_std_rw_pct": overall_std_rw,
        "min_total_capital": min_total_capital,
        "min_tier1_capital": min_tier1_capital,
        "min_cet1_capital": min_cet1_capital,
        "irb_rwa_savings_vs_std": total_std_rwa - total_irb_rwa
    }

    overall_row = pd.DataFrame([{
        "segment": "Overall",
        "category": "All Portfolio",
        "count": total_count,
        "total_ead": total_ead,
        "irb_rwa": total_irb_rwa,
        "std_rwa": total_std_rwa,
        "irb_rw_pct": overall_irb_rw,
        "std_rw_pct": overall_std_rw,
        "min_total_capital_8pct": min_total_capital,
        "min_tier1_capital_6pct": min_tier1_capital,
        "min_cet1_capital_4.5pct": min_cet1_capital
    }])

    grade_rows = []
    if "grade" in df_calc.columns:
        g_summary = (
            df_calc.groupby("grade")
            .agg(
                count=("ead", "count"),
                total_ead=("ead", "sum"),
                irb_rwa=("irb_rwa", "sum"),
                std_rwa=("std_rwa", "sum")
            )
            .reset_index()
        )
        g_summary["irb_rw_pct"] = np.where(g_summary["total_ead"] > 0, g_summary["irb_rwa"] / g_summary["total_ead"] * 100.0, 0.0)
        g_summary["std_rw_pct"] = 75.0
        g_summary["min_total_capital_8pct"] = 0.08 * g_summary["irb_rwa"]
        g_summary["min_tier1_capital_6pct"] = 0.06 * g_summary["irb_rwa"]
        g_summary["min_cet1_capital_4.5pct"] = 0.045 * g_summary["irb_rwa"]
        g_summary.insert(0, "segment", "By Grade")
        g_summary.rename(columns={"grade": "category"}, inplace=True)
        grade_rows.append(g_summary)

    summary_dfs = [overall_row] + grade_rows
    summary_combined = pd.concat(summary_dfs, ignore_index=True)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary_combined.to_csv(output_path, index=False)

    return summary_combined, portfolio_metrics
