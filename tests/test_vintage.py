"""
test_vintage.py
---------------
Unit tests for vintage curves and seasoning analytics in src/creditrisk/monitoring/vintage.py.
"""

import numpy as np
import pandas as pd
import pytest
from creditrisk.monitoring.vintage import vintage_curves, vintage_maturity_comparison


def test_vintage_curve_monotonicity_and_bounds(tmp_path):
    """
    Tests:
    1. Cumulative default rate is monotonically non-decreasing along months-on-book.
    2. Vintage curve values lie strictly between 0 and 1.
    """
    df_synthetic = pd.DataFrame({
        "vintage_year": [2012, 2012, 2012, 2013, 2013, 2013],
        "ever_default": [1, 1, 0, 1, 0, 0],
        "months_to_default": [6, 18, np.nan, 12, np.nan, np.nan],
        "issue_d": ["Jan-12", "Jun-12", "Dec-12", "Jan-13", "May-13", "Oct-13"]
    })

    csv_file = tmp_path / "test_vintage_curves.csv"
    fig_file = tmp_path / "test_vintage_plot.png"

    matrix = vintage_curves(df_synthetic, max_mob=24, output_path=csv_file, fig_path=fig_file)

    assert csv_file.exists()
    assert fig_file.exists()

    mob_cols = [f"mob_{m}" for m in range(25)]

    for idx, row in matrix.iterrows():
        curve_vals = [row[col] for col in mob_cols]

        # 1. Bounds check
        assert all(0.0 <= v <= 1.0 for v in curve_vals)

        # 2. Monotonic non-decreasing check along MOB
        diffs = np.diff(curve_vals)
        assert (diffs >= -1e-12).all()


def test_vintage_maturity_comparison(tmp_path):
    """
    Tests vintage_maturity_comparison output table structure and fixed MOB extraction.
    """
    df_synthetic = pd.DataFrame({
        "vintage_year": [2012, 2012, 2013, 2013],
        "ever_default": [1, 0, 1, 0],
        "months_to_default": [12, np.nan, 18, np.nan],
        "issue_d": ["Jan-12", "Dec-12", "Jan-13", "Dec-13"]
    })

    mat_file = tmp_path / "test_maturity.csv"
    mat_df = vintage_maturity_comparison(df_synthetic, milestone_mobs=[12, 18], output_path=mat_file)

    assert mat_file.exists()
    assert "default_rate_mob_12" in mat_df.columns
    assert "default_rate_mob_18" in mat_df.columns
