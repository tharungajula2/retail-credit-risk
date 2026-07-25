"""
test_lgd_data.py
----------------
Unit tests for Basel LGD dataset building and logic in src/creditrisk/models/lgd_data.py.
"""

import numpy as np
import pandas as pd
import pytest
from creditrisk.models.lgd_data import build_lgd_base, lgd_distribution_report


def test_build_lgd_base_basel_definition():
    """
    Tests Basel LGD calculation:
    funded 10000, principal_repaid 2000, recoveries 500 -> ead 8000, loss 7500, lgd 0.9375.
    Also tests clipping and has_recovery.
    """
    df_synthetic = pd.DataFrame({
        "ever_default": [1, 1, 1, 0],
        "funded_amnt": [10000, 10000, 5000, 10000],
        "total_rec_prncp": [2000, 0, 1000, 0],
        "recoveries": [500, 0, 6000, 0]  # row 2 has post_default_recov > ead_approx
    })

    lgd_df = build_lgd_base(df_synthetic)

    # Verify filtering for ever_default == 1
    assert len(lgd_df) == 3
    assert (lgd_df["ever_default"] == 1).all()

    # Row 0: funded=10000, prncp=2000 -> ead=8000, recov=500 -> loss=7500 -> lgd = 7500/8000 = 0.9375
    row0 = lgd_df.iloc[0]
    assert row0["funded"] == 10000.0
    assert row0["principal_repaid"] == 2000.0
    assert row0["ead_approx"] == 8000.0
    assert row0["post_default_recov"] == 500.0
    assert row0["loss"] == 7500.0
    assert row0["lgd"] == 0.9375
    assert row0["recovery_rate"] == 1 - 0.9375
    assert row0["has_recovery"] == 1
    assert row0["ead_zero_flag"] == 0

    # Row 1: funded=10000, prncp=0 -> ead=10000, recov=0 -> loss=10000 -> lgd = 1.0 (Total Loss)
    row1 = lgd_df.iloc[1]
    assert row1["ead_approx"] == 10000.0
    assert row1["loss"] == 10000.0
    assert row1["lgd"] == 1.0
    assert row1["recovery_rate"] == 0.0
    assert row1["has_recovery"] == 0
    assert row1["ead_zero_flag"] == 0

    # Row 2: funded=5000, prncp=1000 -> ead=4000, recov=6000 -> loss=0 -> lgd = 0.0 (clipped)
    row2 = lgd_df.iloc[2]
    assert row2["ead_approx"] == 4000.0
    assert row2["loss"] == 0.0
    assert row2["lgd"] == 0.0
    assert row2["recovery_rate"] == 1.0
    assert row2["has_recovery"] == 1
    assert row2["ead_zero_flag"] == 0


def test_build_lgd_base_ead_zero_edge_case():
    """
    Tests edge case where total_rec_prncp >= funded_amnt (ead_approx == 0).
    """
    df_edge = pd.DataFrame({
        "ever_default": [1, 1],
        "funded_amnt": [10000, 5000],
        "total_rec_prncp": [10000, 6000],
        "recoveries": [0, 100]
    })

    lgd_df = build_lgd_base(df_edge)
    assert (lgd_df["ead_approx"] == 0.0).all()
    assert (lgd_df["ead_zero_flag"] == 1).all()
    assert (lgd_df["lgd"] == 0.0).all()
    assert (lgd_df["recovery_rate"] == 1.0).all()


def test_lgd_distribution_report_basel(tmp_path):
    """
    Tests Basel distribution summary computation and output file creation.
    """
    df_synthetic = pd.DataFrame({
        "ever_default": [1, 1],
        "funded_amnt": [10000, 10000],
        "total_rec_prncp": [2000, 10000],
        "recoveries": [500, 0]
    })

    fig_file = tmp_path / "test_lgd_basel.png"
    csv_file = tmp_path / "test_summary_basel.csv"

    summary_table, metrics = lgd_distribution_report(df_synthetic, fig_path=fig_file, summary_path=csv_file)

    assert fig_file.exists()
    assert csv_file.exists()
    assert metrics["count_defaulted_loans"] == 2
    assert metrics["count_ead_zero"] == 1
    assert metrics["fraction_ead_zero"] == 0.5
