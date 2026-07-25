"""
test_ecl.py
-----------
Unit tests for IFRS 9 ECL, EIR discounting, and US CECL provisions in src/creditrisk/regulatory/ecl.py.
"""

import numpy as np
import pandas as pd
import pytest
from creditrisk.regulatory.ecl import compute_cecl, compute_ecl, ecl_summary


def test_stage3_and_stage2_ecl_calculation():
    """
    Tests:
    1. Stage 3 ECL = lgd * ead (PD = 1.0)
    2. Stage 2 ECL uses lifetime_pd
    3. CECL total provision >= IFRS 9 total provision
    """
    df_synthetic = pd.DataFrame({
        "stage": ["Stage 1", "Stage 2", "Stage 3"],
        "current_pd_12m": [0.02, 0.05, 1.00],
        "lifetime_pd": [0.06, 0.15, 1.00],
        "lgd_hat": [0.80, 0.80, 0.80],
        "ead": [10000.0, 10000.0, 10000.0],
        "remaining_term": [24, 24, 24],
        "int_rate": [10.0, 10.0, 10.0]
    })

    df_ecl = compute_ecl(df_synthetic)

    # 1. Stage 3 ECL must equal lgd * ead = 0.80 * 10000 = 8000.0 exactly
    row_stg3 = df_ecl[df_ecl["stage"] == "Stage 3"].iloc[0]
    assert np.isclose(row_stg3["ecl"], 8000.0)

    # 2. Stage 2 ECL must use lifetime_pd (0.15) * 0.80 * 10000 * discount_factor
    row_stg2 = df_ecl[df_ecl["stage"] == "Stage 2"].iloc[0]
    expected_stg2 = 0.15 * 0.80 * 10000.0 * row_stg2["discount_factor"]
    assert np.isclose(row_stg2["ecl"], expected_stg2)

    # 3. Stage 1 ECL must use current_pd_12m (0.02)
    row_stg1 = df_ecl[df_ecl["stage"] == "Stage 1"].iloc[0]
    expected_stg1 = 0.02 * 0.80 * 10000.0 * row_stg1["discount_factor"]
    assert np.isclose(row_stg1["ecl"], expected_stg1)

    # 4. CECL total provision check
    df_cecl = compute_cecl(df_synthetic)
    total_ifrs9 = df_ecl["ecl"].sum()
    total_cecl = df_cecl["cecl"].sum()

    # US CECL applies lifetime_pd to Stage 1, so CECL total >= IFRS 9 total
    assert total_cecl >= total_ifrs9
