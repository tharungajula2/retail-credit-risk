"""
test_lifetime_pd.py
-------------------
Unit tests for Lifetime PD term structure calculation and scaling logic in src/creditrisk/regulatory/lifetime_pd.py.
"""

import numpy as np
import pandas as pd
import pytest
from creditrisk.regulatory.lifetime_pd import (
    build_hazard_curve,
    compute_remaining_term,
    scale_lifetime_to_account
)


def test_build_hazard_curve_properties(tmp_path):
    """
    Tests hazard in [0, 1], survival is non-increasing, cumulative PD is non-decreasing.
    """
    df_synthetic = pd.DataFrame({
        "ever_default": [1, 1, 1, 1, 0, 0, 0, 0, 0, 0],
        "months_to_default": [3, 6, 12, 24, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
    })

    fig_file = tmp_path / "test_fig.png"
    csv_file = tmp_path / "test_table.csv"

    term_table = build_hazard_curve(df_synthetic, max_months=36, output_path=csv_file, fig_path=fig_file)

    assert csv_file.exists()
    assert fig_file.exists()

    # 1. Hazard values strictly between 0 and 1
    assert (term_table["hazard"] >= 0.0).all()
    assert (term_table["hazard"] <= 1.0).all()

    # 2. Survival is non-increasing
    surv_diffs = np.diff(term_table["survival"].values)
    assert (surv_diffs <= 1e-12).all()

    # 3. Cumulative PD is non-decreasing
    cum_pd_diffs = np.diff(term_table["cumulative_pd"].values)
    assert (cum_pd_diffs >= -1e-12).all()

    # Total lifetime cumulative PD at month 36 should equal 4/10 = 0.40
    assert np.isclose(term_table.iloc[-1]["cumulative_pd"], 0.40)


def test_scaling_preserves_12m_point():
    """
    Tests that scaling multiplicatively preserves the 12-month PD point exactly
    when remaining_term == 12.
    """
    term_table = pd.DataFrame({
        "month": [6, 12, 24, 36],
        "cumulative_pd": [0.05, 0.10, 0.18, 0.25]
    })

    pd_12m = 0.08  # Account's predicted 12m PD

    # Case A: remaining_term = 12 -> scaled lifetime PD must equal pd_12m (0.08) exactly
    scaled_12m = scale_lifetime_to_account(pd_12m, remaining_term=12, term_structure=term_table)
    assert np.isclose(scaled_12m, pd_12m)

    # Case B: remaining_term = 36 -> scaling = 0.08 / 0.10 = 0.8. 0.25 * 0.8 = 0.20
    scaled_36m = scale_lifetime_to_account(pd_12m, remaining_term=36, term_structure=term_table)
    assert np.isclose(scaled_36m, 0.20)


def test_remaining_term_clamping():
    """
    Tests remaining_term floored at 1 and capped at original term.
    """
    df_loans = pd.DataFrame({
        "issue_d": ["Jan-15", "Dec-10"],  # Jan-15 (13m elapsed by Jan-16), Dec-10 (61m elapsed)
        "term": [" 36 months", " 36 months"]
    })

    rem_terms = compute_remaining_term(df_loans, snapshot_date="2016-01-31")

    # Row 0: 36 - 12 = 24 months
    assert rem_terms.iloc[0] == 24

    # Row 1: 36 - 61 = -25 -> floored at 1
    assert rem_terms.iloc[1] == 1
