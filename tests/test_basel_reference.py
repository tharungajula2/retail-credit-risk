"""
test_basel_reference.py
------------------------
Independent reference verification suite for Basel III 'Other Retail' IRB capital formulas.
"""

import pytest
from creditrisk.regulatory.basel_capital import (
    basel_capital_k,
    basel_correlation,
    basel_correlation_qrre
)


def test_other_retail_anchor_pd_001_lgd_045():
    """
    Anchor Point 1: PD = 0.01 (1.0%), LGD = 0.45 (45.0%) under 'Other Retail' curve.
    Formula computation: R ≈ 0.1216, K ≈ 0.0366.
    """
    pd_val = 0.01
    lgd_val = 0.45
    r_expected = 0.1216
    k_expected = 0.0366

    r_calc = basel_correlation(pd_val)
    k_calc = basel_capital_k(pd_val, lgd_val)

    print(f"\n[Anchor 1] PD={pd_val:.4f}, R={r_calc:.4f}, K={k_calc:.4f}")
    assert pytest.approx(r_expected, abs=0.0005) == r_calc
    assert pytest.approx(k_expected, abs=0.0005) == k_calc


def test_other_retail_anchor_pd_005_lgd_045():
    """
    Anchor Point 2: PD = 0.05 (5.0%), LGD = 0.45 (45.0%) under 'Other Retail' curve.
    Formula computation: R ≈ 0.0526, K ≈ 0.0531.
    """
    pd_val = 0.05
    lgd_val = 0.45
    r_expected = 0.0526
    k_expected = 0.0531

    r_calc = basel_correlation(pd_val)
    k_calc = basel_capital_k(pd_val, lgd_val)

    print(f"\n[Anchor 2] PD={pd_val:.4f}, R={r_calc:.4f}, K={k_calc:.4f}")
    assert pytest.approx(r_expected, abs=0.0005) == r_calc
    assert pytest.approx(k_expected, abs=0.0005) == k_calc


def test_other_retail_anchor_pd_0001_lgd_045():
    """
    Anchor Point 3: PD = 0.001 (0.1%), LGD = 0.45 (45.0%) under 'Other Retail' curve.
    Formula computation: R ≈ 0.1555, K ≈ 0.0089.
    """
    pd_val = 0.001
    lgd_val = 0.45
    r_expected = 0.1555
    k_expected = 0.0089

    r_calc = basel_correlation(pd_val)
    k_calc = basel_capital_k(pd_val, lgd_val)

    print(f"\n[Anchor 3] PD={pd_val:.4f}, R={r_calc:.4f}, K={k_calc:.4f}")
    assert pytest.approx(r_expected, abs=0.0005) == r_calc
    assert pytest.approx(k_expected, abs=0.0005) == k_calc


def test_qrre_correlation_flat():
    """Verifies QRRE correlation is flat 0.04 across all PD levels."""
    assert basel_correlation_qrre(0.01) == 0.04
    assert basel_correlation_qrre(0.05) == 0.04
