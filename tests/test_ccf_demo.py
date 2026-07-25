"""
test_ccf_demo.py
----------------
Unit tests for the synthetic revolving CCF module in src/creditrisk/models/ccf_demo.py.
"""

import numpy as np
import pandas as pd
import pytest
from creditrisk.models.ccf_demo import (
    compute_realised_ccf,
    ead_revolving,
    simulate_revolving_portfolio
)


def test_ccf_bounded_and_ead_calculation():
    """
    Tests that computed realised CCF is bounded in [0, 1] and ead_revolving = drawn + ccf * undrawn.
    """
    df_synth = simulate_revolving_portfolio(n=1000, seed=42)
    df_def = compute_realised_ccf(df_synth)

    # 1. CCF bounds check
    assert np.all(df_def["ccf"] >= 0.0)
    assert np.all(df_def["ccf"] <= 1.0)

    # 2. Worked EAD function check
    drawn = 30000.0
    undrawn = 70000.0
    ccf = 0.40
    expected_ead = 30000.0 + 0.40 * 70000.0  # = 58000.0
    
    calc_ead = ead_revolving(drawn, undrawn, ccf)
    assert calc_ead == expected_ead


def test_higher_utilisation_produces_higher_drawdown():
    """
    Tests that higher observation utilisation produces higher simulated CCF/drawdown.
    """
    df_synth = simulate_revolving_portfolio(n=5000, seed=42)
    df_def = compute_realised_ccf(df_synth)

    low_util = df_def[df_def["utilisation"] < 0.40]["ccf"].mean()
    high_util = df_def[df_def["utilisation"] > 0.60]["ccf"].mean()

    assert high_util > low_util
