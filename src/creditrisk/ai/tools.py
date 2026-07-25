"""
Quantitative Tool Definitions for Credit Risk AI Analyst.

Exposes regulatory engine functions (Basel capital, Expected Loss, IFRS 9 ECL,
and Rating Grade lookup) as typed tool wrappers for Gemini function calling.
"""

from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

from creditrisk.regulatory.basel_capital import basel_capital_k, risk_weighted_assets


def tool_basel_capital(pd_val: float, lgd_val: float, ead_val: float) -> Dict[str, float]:
    """Calculates Basel III IRB capital requirement K, Risk Weight (%), and Risk-Weighted Assets (RWA).

    Args:
        pd_val: Probability of Default (0.0 to 1.0).
        lgd_val: Loss Given Default (0.0 to 1.0).
        ead_val: Exposure at Default ($).

    Returns:
        Dict containing capital requirement K, risk weight percentage, and total RWA ($).
    """
    k_val = basel_capital_k(pd_val, lgd_val)
    rwa, rw_pct = risk_weighted_assets(pd_val, lgd_val, ead_val)

    return {
        "capital_requirement_k": round(float(k_val), 6),
        "risk_weight_pct": round(float(rw_pct), 2),
        "rwa_usd": round(float(rwa), 2),
    }


def tool_expected_loss(pd_val: float, lgd_val: float, ead_val: float) -> Dict[str, float]:
    """Calculates 12-month regulatory Expected Loss (EL = PD * LGD * EAD).

    Args:
        pd_val: Probability of Default (0.0 to 1.0).
        lgd_val: Loss Given Default (0.0 to 1.0).
        ead_val: Exposure at Default ($).

    Returns:
        Dict containing total Expected Loss ($).
    """
    el_val = float(pd_val * lgd_val * ead_val)
    return {
        "expected_loss_usd": round(el_val, 2),
    }


def tool_ifrs9_ecl(
    pd_12m: float,
    lifetime_pd: float,
    lgd_val: float,
    ead_val: float,
    stage: int = 1
) -> Dict[str, Any]:
    """Calculates IFRS 9 Expected Credit Loss (ECL) based on loan staging.

    Stage 1: 12-month ECL = pd_12m * lgd * ead
    Stage 2: Lifetime ECL = lifetime_pd * lgd * ead
    Stage 3: Credit-Impaired ECL = 1.0 * lgd * ead (defaulted, PD = 1.0)

    Args:
        pd_12m: 12-month Probability of Default (0.0 to 1.0).
        lifetime_pd: Lifetime Probability of Default (0.0 to 1.0).
        lgd_val: Loss Given Default (0.0 to 1.0).
        ead_val: Exposure at Default ($).
        stage: IFRS 9 Stage (1, 2, or 3).

    Returns:
        Dict containing stage identifier and calculated ECL ($).
    """
    if stage == 1:
        ecl = pd_12m * lgd_val * ead_val
    elif stage == 2:
        ecl = lifetime_pd * lgd_val * ead_val
    elif stage == 3:
        ecl = 1.0 * lgd_val * ead_val
    else:
        raise ValueError("Invalid stage. Must be 1, 2, or 3.")

    return {
        "stage": stage,
        "ecl_usd": round(float(ecl), 2),
    }


def tool_score_to_pd(score: int) -> Dict[str, Any]:
    """Looks up rating grade and observed default rate for a given scorecard score.

    Args:
        score: Scorecard credit score integer.

    Returns:
        Dict containing matched grade, score range, and observed default rate.
    """
    tables_dir = Path("outputs/tables")
    grades_file = tables_dir / "rating_grades_model_b.csv"

    if not grades_file.exists():
        return {"error": "rating_grades_model_b.csv not found."}

    df = pd.read_csv(grades_file)
    for _, row in df.iterrows():
        s_min = int(row["score_min"])
        s_max = int(row["score_max"])
        if s_min <= score <= s_max:
            # Format grade as clean integer string (e.g., '1' instead of '1.0')
            raw_grade = row["grade"]
            grade_str = str(int(float(raw_grade))) if str(raw_grade).replace('.', '', 1).isdigit() else str(raw_grade)
            return {
                "score": score,
                "grade": grade_str,
                "score_range": f"{s_min}-{s_max}",
                "observed_default_rate": round(float(row["observed_default_rate"]), 4),
                "portfolio_share": round(float(row["portfolio_share"]), 4),
            }

    # If score falls outside defined master scale boundaries
    return {
        "score": score,
        "grade": "Out of Bounds",
        "message": "Score falls outside defined Model B grade boundaries (522-639).",
    }
