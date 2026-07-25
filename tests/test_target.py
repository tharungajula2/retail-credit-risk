"""
test_target.py
--------------
Unit tests for date parsing and target flag construction routines in target.py.
"""

import pandas as pd
import pytest
from creditrisk.data.target import build_target, parse_lc_date


def test_parse_lc_date_handles_1968_century_rollover():
    """
    Verifies that parse_lc_date correctly converts 2-digit year 'Dec-68' to 1968-12-01
    instead of defaulting to 2068-12-01.
    """
    raw_dates = pd.Series(["Dec-68", "Jan-14"])
    parsed = parse_lc_date(raw_dates)

    # Dec-68 must equal 1968-12-01
    assert parsed.iloc[0] == pd.Timestamp("1968-12-01")
    assert parsed.iloc[1] == pd.Timestamp("2014-01-01")


def test_build_target_on_synthetic_data():
    """
    Verifies build_target logic on a synthetic dataset with known target outcomes.
    """
    synthetic_data = pd.DataFrame(
        {
            "issue_d": ["Jan-14", "Jan-14", "Jan-12"],
            "loan_status": ["Fully Paid", "Charged Off", "Charged Off"],
            "last_pymnt_d": ["Jan-15", "Jun-14", "Dec-13"],
        }
    )

    config = {
        "default_statuses": ["Charged Off", "Default"],
        "days_past_due_lag_months": 3,
        "performance_window_months": 12,
    }

    result = build_target(synthetic_data, config)

    # Loan 1: Fully Paid -> ever_default = 0, default_12m = 0
    assert result.loc[0, "ever_default"] == 0
    assert result.loc[0, "default_12m"] == 0
    assert result.loc[0, "vintage_year"] == 2014
    assert result.loc[0, "vintage_quarter"] == "2014Q1"

    # Loan 2: Charged Off, issue Jan-14, last_pymnt Jun-14 -> est_default = Sep-14 (8 months) <= 12m -> default_12m = 1
    assert result.loc[1, "ever_default"] == 1
    assert result.loc[1, "months_to_default"] == 8
    assert result.loc[1, "default_12m"] == 1

    # Loan 3: Charged Off, issue Jan-12, last_pymnt Dec-13 -> est_default = Mar-14 (26 months) > 12m -> default_12m = 0
    assert result.loc[2, "ever_default"] == 1
    assert result.loc[2, "months_to_default"] == 26
    assert result.loc[2, "default_12m"] == 0
