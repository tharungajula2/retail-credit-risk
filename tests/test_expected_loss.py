"""
test_expected_loss.py
---------------------
Unit tests for Expected Loss calculation and portfolio aggregation engine.
"""

import numpy as np
import pandas as pd
import pytest

from creditrisk.regulatory.expected_loss import (
    compute_expected_loss,
    portfolio_el_summary
)


def test_compute_expected_loss_exact_math_and_nonnegative():
    """
    Tests that EL = PD * LGD * EAD holds exactly on synthetic rows,
    that EL is non-negative, and portfolio total EL sums correctly.
    """
    # Create mock inputs
    df_synthetic = pd.DataFrame({
        "ever_default": [0, 1, 0],
        "funded_amnt": [10000, 10000, 20000],
        "total_rec_prncp": [2000, 4000, 5000],
        "out_prncp": [8000, 0, 15000],
        "grade": ["A", "B", "C"],
        "vintage_year": [2014, 2014, 2014]
    })

    # Mock PD model, LGD model, and WoE binners
    class DummyPDModel:
        def predict_pd(self, df, woe_binner):
            return np.array([0.05, 0.20, 0.10])

    class DummyLGDModel:
        def predict_lgd(self, df):
            return np.array([0.60, 0.80, 0.50])

    pd_model = DummyPDModel()
    lgd_model = DummyLGDModel()
    woe_binner_pd = None

    df_el = compute_expected_loss(df_synthetic, pd_model, lgd_model, woe_binner_pd)

    # Check columns created
    assert "pd_hat" in df_el.columns
    assert "lgd_hat" in df_el.columns
    assert "ead" in df_el.columns
    assert "el" in df_el.columns

    # Expected values:
    # Row 0 (performing): EAD = out_prncp = 8000. EL = 0.05 * 0.60 * 8000 = 240.0
    # Row 1 (defaulted): EAD = 10000 - 4000 = 6000. EL = 0.20 * 0.80 * 6000 = 960.0
    # Row 2 (performing): EAD = out_prncp = 15000. EL = 0.10 * 0.50 * 15000 = 750.0
    expected_ead = np.array([8000.0, 6000.0, 15000.0])
    expected_el = np.array([240.0, 960.0, 750.0])

    np.testing.assert_allclose(df_el["ead"].values, expected_ead)
    np.testing.assert_allclose(df_el["el"].values, expected_el)

    # EL non-negativity check
    assert (df_el["el"] >= 0.0).all()

    # Test portfolio summary aggregation
    summary_df, metrics = portfolio_el_summary(df_el)

    assert metrics["total_ead"] == 8000.0 + 6000.0 + 15000.0  # = 29000.0
    assert np.isclose(metrics["total_el"], 1950.0)
    assert np.isclose(metrics["total_el"], df_el["el"].sum())
