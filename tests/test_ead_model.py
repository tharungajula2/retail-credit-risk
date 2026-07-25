"""
test_ead_model.py
-----------------
Unit tests for EAD logic and helper functions in src/creditrisk/models/ead_model.py.
"""

import numpy as np
import pandas as pd
import pytest
from creditrisk.models.ead_model import build_ead_term, get_portfolio_ead


def test_build_ead_term_math_and_bounds():
    """
    Tests ead = max(funded - principal_repaid, 0), clipping of ead_ratio in [0, 1],
    and filtering for ever_default == 1.
    """
    df_synthetic = pd.DataFrame({
        "ever_default": [1, 1, 1, 0],
        "funded_amnt": [10000, 10000, 5000, 10000],
        "total_rec_prncp": [2000, 12000, 0, 1000]
    })

    ead_df = build_ead_term(df_synthetic)

    # 1. Verify ever_default == 1 filtering
    assert len(ead_df) == 3
    assert (ead_df["ever_default"] == 1).all()

    # 2. Row 0: 10000 funded, 2000 repaid -> ead = 8000, ead_ratio = 0.8
    row0 = ead_df.iloc[0]
    assert row0["funded"] == 10000.0
    assert row0["principal_repaid"] == 2000.0
    assert row0["ead"] == 8000.0
    assert row0["ead_ratio"] == 0.8

    # 3. Row 1: 10000 funded, 12000 repaid -> ead = 0.0 (clipped at 0), ead_ratio = 0.0
    row1 = ead_df.iloc[1]
    assert row1["ead"] == 0.0
    assert row1["ead_ratio"] == 0.0

    # 4. Row 2: 5000 funded, 0 repaid -> ead = 5000, ead_ratio = 1.0
    row2 = ead_df.iloc[2]
    assert row2["ead"] == 5000.0
    assert row2["ead_ratio"] == 1.0


def test_get_portfolio_ead_branching():
    """
    Tests get_portfolio_ead selects actual ead for defaulted loans (ever_default == 1)
    and out_prncp for performing loans (ever_default == 0).
    """
    df_portfolio = pd.DataFrame({
        "ever_default": [1, 0, 1, 0],
        "funded_amnt": [10000, 15000, 5000, 20000],
        "total_rec_prncp": [2000, 5000, 1000, 10000],
        "out_prncp": [9999, 10000, 8888, 10000]
    })

    ead_series = get_portfolio_ead(df_portfolio)

    # Index 0: Defaulted -> max(10000 - 2000, 0) = 8000
    assert ead_series.iloc[0] == 8000.0

    # Index 1: Performing -> out_prncp = 10000
    assert ead_series.iloc[1] == 10000.0

    # Index 2: Defaulted -> max(5000 - 1000, 0) = 4000
    assert ead_series.iloc[2] == 4000.0

    # Index 3: Performing -> out_prncp = 10000
    assert ead_series.iloc[3] == 10000.0
