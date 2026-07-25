"""
test_basel_capital.py
---------------------
Unit tests verifying Basel III IRB capital formula calculations and benchmark values.
"""

import numpy as np
import pytest
from scipy.stats import norm

from creditrisk.regulatory.basel_capital import (
    basel_capital_k,
    basel_correlation,
    risk_weighted_assets,
    standardised_rwa
)


def test_basel_correlation_and_capital_k_benchmark():
    """
    Verifies basel_correlation and basel_capital_k against hand-computed benchmark values
    for PD = 0.01 (1.0%) and LGD = 0.45 (45%).
    """
    pd_val = 0.01
    lgd_val = 0.45
    ead_val = 10000.0

    # 1. Manual reference computation for correlation R
    denom = 1.0 - np.exp(-35.0)
    factor = (1.0 - np.exp(-35.0 * pd_val)) / denom
    r_expected = 0.03 * factor + 0.16 * (1.0 - factor)

    r_calc = basel_correlation(pd_val)
    np.testing.assert_allclose(r_calc, r_expected, rtol=1e-5)

    # 2. Manual reference computation for Capital K
    g_pd = norm.ppf(pd_val)
    g_999 = norm.ppf(0.999)
    term1 = (1.0 / np.sqrt(1.0 - r_expected)) * g_pd
    term2 = np.sqrt(r_expected / (1.0 - r_expected)) * g_999
    conditional_pd = norm.cdf(term1 + term2)
    k_expected = lgd_val * conditional_pd - pd_val * lgd_val

    k_calc = basel_capital_k(pd_val, lgd_val)
    np.testing.assert_allclose(k_calc, k_expected, rtol=1e-5)

    # 3. Verify RWA = K * 12.5 * EAD
    rwa_calc, rw_pct_calc = risk_weighted_assets(pd_val, lgd_val, ead_val)
    expected_rwa = k_expected * 12.5 * ead_val
    expected_rw_pct = k_expected * 12.5 * 100.0

    np.testing.assert_allclose(rwa_calc, expected_rwa, rtol=1e-5)
    np.testing.assert_allclose(rw_pct_calc, expected_rw_pct, rtol=1e-5)

    # 4. Verify Standardised RWA = 0.75 * EAD
    std_rwa_calc = standardised_rwa(ead_val)
    assert std_rwa_calc == 7500.0


def test_pd_floor_and_lgd_cap():
    """
    Tests that PD is floored at 0.0003 and LGD is capped at 1.0.
    """
    # PD = 0.0001 (below 0.0003 floor) should evaluate identically to PD = 0.0003
    k_floored = basel_capital_k(0.0001, 0.50)
    k_floor_ref = basel_capital_k(0.0003, 0.50)
    assert k_floored == k_floor_ref

    # LGD = 1.5 (above 1.0 cap) should evaluate identically to LGD = 1.0
    k_capped = basel_capital_k(0.05, 1.50)
    k_cap_ref = basel_capital_k(0.05, 1.00)
    assert k_capped == k_cap_ref
