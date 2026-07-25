"""
test_binning.py
---------------
Unit tests for WoEBinner in src/creditrisk/features/binning.py.
"""

import numpy as np
import pandas as pd
import pytest
from creditrisk.features.binning import WoEBinner


def test_assert_no_leakage_raises_on_recoveries():
    """
    Verifies that WoEBinner.fit raises ValueError when an outcome column
    like 'recoveries' is passed in the DataFrame X.
    """
    df = pd.DataFrame(
        {
            "loan_amnt": [1000, 2000, 3000],
            "recoveries": [0.0, 100.0, 0.0],
        }
    )
    y = pd.Series([0, 1, 0])

    binner = WoEBinner()
    with pytest.raises(ValueError, match="Target leakage violation detected"):
        binner.fit(df, y)


def test_missing_values_get_own_bin():
    """
    Verifies that missing values (NaN) receive a dedicated 'MISSING' bin.
    """
    df = pd.DataFrame(
        {
            "annual_inc": [10000, 20000, np.nan, 40000, 50000, np.nan] * 10,
        }
    )
    y = pd.Series([0, 1, 0, 1, 0, 1] * 10)

    binner = WoEBinner(min_bin_pct=0.05)
    binner.fit(df, y)

    bin_table = binner.get_bin_table("annual_inc")
    bins = list(bin_table["bin"])

    assert "MISSING" in bins
    missing_row = bin_table[bin_table["bin"] == "MISSING"]
    assert missing_row["n"].values[0] == 20


def test_laplace_smoothing_prevents_infinity():
    """
    Verifies that Laplace smoothing (+0.5) ensures finite WoE and IV values even when
    a bin contains 0 bads or 0 goods.
    """
    # Create a feature where one bin has 0 bads
    df = pd.DataFrame(
        {
            "score": [10, 20, 30, 40, 50] * 20,
        }
    )
    # y has 0 bads for score = 10
    y = pd.Series([0, 0, 1, 0, 1] * 20)

    binner = WoEBinner(min_bin_pct=0.05)
    binner.fit(df, y)

    bin_table = binner.get_bin_table("score")

    # All WoE and IV values must be finite numbers (no inf or nan)
    assert not bin_table["woe"].isna().any()
    assert not np.isinf(bin_table["woe"]).any()
    assert not bin_table["iv_bin"].isna().any()
    assert not np.isinf(bin_table["iv_bin"]).any()


def test_numeric_monotonicity_enforced():
    """
    Verifies that numeric WoE values across non-missing bins are strictly monotonic.
    """
    np.random.seed(42)
    x_vals = np.linspace(10, 100, 200)
    # Strong positive relationship between x and default probability
    y_vals = (x_vals > 50).astype(int)

    df = pd.DataFrame({"risk_score": x_vals})
    binner = WoEBinner(min_bin_pct=0.05)
    binner.fit(df, y_vals)

    bin_table = binner.get_bin_table("risk_score")
    non_missing_woes = bin_table[bin_table["bin"] != "MISSING"]["woe"].tolist()

    # Check non-decreasing or non-increasing monotonicity
    diffs = np.diff(non_missing_woes)
    is_monotonic = bool(np.all(diffs >= 0) or np.all(diffs <= 0))
    assert is_monotonic, f"Numeric WoE values are not monotonic: {non_missing_woes}"
