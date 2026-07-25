"""
test_staging.py
---------------
Unit tests for IFRS 9 staging and SICR rules in src/creditrisk/regulatory/staging.py.
"""

import numpy as np
import pandas as pd
import pytest
from creditrisk.regulatory.staging import assign_ifrs9_stages, stage_summary


def test_ifrs9_staging_rules():
    """
    Tests:
    1. Defaulted loan -> Stage 3 (PD = 1.0)
    2. Loan with PD >= 2.0x origination -> Stage 2 (Quantitative SICR)
    3. 30+ DPD loan -> Stage 2 (Backstop)
    4. Healthy low-PD loan -> Stage 1
    """
    df_synthetic = pd.DataFrame({
        "ever_default": [1, 0, 0, 0],
        "loan_status": ["Charged Off", "Current", "Late (16-30 days)", "Current"],
        "current_pd_12m": [0.20, 0.09, 0.01, 0.015],
        "grade": ["C", "C", "A", "A"],
        "funded_amnt": [10000, 10000, 10000, 10000],
        "total_rec_prncp": [2000, 1000, 1000, 1000],
        "out_prncp": [0, 9000, 9000, 9000]
    })

    # Grade C current_pd: mean([0.20, 0.09]) = 0.145.
    # For loan 1 (Grade C): current_pd = 0.09, orig_pd = 0.145 -> pd_ratio < 2.0. But 0.09 > 0.06 (abs threshold)! -> Stage 2.
    # Let's override origination_pd explicitly for fine-grained testing:
    df_staged = assign_ifrs9_stages(df_synthetic)

    # 1. Row 0: Defaulted -> Stage 3, PD = 1.0
    assert df_staged.iloc[0]["stage"] == "Stage 3"
    assert df_staged.iloc[0]["current_pd_12m"] == 1.0

    # 2. Row 2: Late (16-30 days) -> Stage 2 via DPD backstop
    assert df_staged.iloc[2]["stage"] == "Stage 2"
    assert df_staged.iloc[2]["sicr_dpd_flag"] == 1

    # 3. Row 3: Current, low PD (0.015), Grade A -> Stage 1
    assert df_staged.iloc[3]["stage"] == "Stage 1"
    assert df_staged.iloc[3]["sicr_quant_flag"] == 0
    assert df_staged.iloc[3]["sicr_dpd_flag"] == 0


def test_pd_3x_origination_triggers_stage2():
    """
    Tests that a loan with PD 3x its origination PD triggers Stage 2 via quantitative SICR.
    """
    df_quant = pd.DataFrame({
        "ever_default": [0],
        "loan_status": ["Current"],
        "current_pd_12m": [0.045],
        "origination_pd": [0.015],  # 0.045 / 0.015 = 3.0x ratio >= 2.0x threshold
        "funded_amnt": [10000],
        "total_rec_prncp": [1000],
        "out_prncp": [9000]
    })

    df_staged = assign_ifrs9_stages(df_quant)

    assert df_staged.iloc[0]["stage"] == "Stage 2"
    assert df_staged.iloc[0]["pd_ratio"] == 3.0
    assert df_staged.iloc[0]["sicr_quant_flag"] == 1


def test_stage_summary(tmp_path):
    """
    Tests stage summary metrics table generation and CSV output.
    """
    df_synthetic = pd.DataFrame({
        "stage": ["Stage 1", "Stage 1", "Stage 2", "Stage 3"],
        "ead": [1000.0, 1000.0, 2000.0, 1000.0],
        "current_pd_12m": [0.01, 0.02, 0.08, 1.00]
    })

    csv_file = tmp_path / "test_stage_summary.csv"
    summary_df, metrics = stage_summary(df_synthetic, output_path=csv_file)

    assert csv_file.exists()
    assert metrics["total_count"] == 4
    assert metrics["total_ead"] == 5000.0
    assert metrics["stage1_ead_pct"] == 40.0  # 2000 / 5000 = 40%
    assert metrics["stage2_ead_pct"] == 40.0  # 2000 / 5000 = 40%
    assert metrics["stage3_ead_pct"] == 20.0  # 1000 / 5000 = 20%
