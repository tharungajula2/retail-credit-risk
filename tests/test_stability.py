"""
test_stability.py
------------------
Unit tests for PSI and CSI calculation functions in src/creditrisk/validation/stability.py.
"""

import numpy as np
import pandas as pd
import pytest
from creditrisk.features.binning import WoEBinner
from creditrisk.validation.stability import csi, get_stability_band, psi


def test_identical_distributions_give_psi_near_zero():
    """
    Verifies that identical expected and actual distributions yield PSI ~ 0.0.
    """
    np.random.seed(42)
    expected = pd.Series(np.random.normal(600, 20, 10000))
    actual = pd.Series(np.random.normal(600, 20, 10000))

    psi_val, _ = psi(expected, actual, n_bins=10)

    assert psi_val < 0.01, f"PSI for identical distributions was unexpectedly high: {psi_val:.4f}"
    assert get_stability_band(psi_val) == "stable"


def test_large_shifted_distribution_gives_psi_greater_than_025():
    """
    Verifies that a large shift in population distribution yields PSI > 0.25 (significant shift).
    """
    np.random.seed(42)
    expected = pd.Series(np.random.normal(600, 20, 10000))
    # Large shift in mean from 600 to 500
    actual = pd.Series(np.random.normal(500, 20, 10000))

    psi_val, _ = psi(expected, actual, n_bins=10)

    assert psi_val > 0.25, f"PSI for large shift was unexpectedly low: {psi_val:.4f}"
    assert get_stability_band(psi_val) == "significant shift"
