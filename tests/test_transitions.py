"""
test_transitions.py
-------------------
Unit tests for rating-grade transition matrix in src/creditrisk/monitoring/transitions.py.
"""

import numpy as np
import pandas as pd
import pytest
from creditrisk.monitoring.transitions import default_by_grade_summary, transition_matrix


def test_transition_matrix_row_sums_and_monotonicity(tmp_path):
    """
    Tests:
    1. Each row of the row-normalized transition matrix sums to 1.0.
    2. Higher-risk grade (e.g. Grade G) has a higher default column probability than lower-risk grade (Grade A).
    """
    df_synthetic = pd.DataFrame({
        "grade": ["A", "A", "A", "A", "G", "G", "G", "G"],
        "loan_status": [
            "Fully Paid", "Current", "Current", "Charged Off",  # Grade A: 1/4 default = 0.25
            "Fully Paid", "Charged Off", "Charged Off", "Default" # Grade G: 3/4 default = 0.75
        ]
    })

    csv_file = tmp_path / "test_trans.csv"
    fig_file = tmp_path / "test_trans.png"

    norm_matrix, counts_df = transition_matrix(df_synthetic, output_path=csv_file, fig_path=fig_file)

    assert csv_file.exists()
    assert fig_file.exists()

    # 1. Row sums check (each row must sum to 1.0)
    row_sums = norm_matrix.sum(axis=1).values
    np.testing.assert_allclose(row_sums, 1.0, rtol=1e-5)

    # 2. Monotonic pattern check: Grade G default probability > Grade A default probability
    p_def_A = norm_matrix.loc["A", "Default"]
    p_def_G = norm_matrix.loc["G", "Default"]

    assert p_def_G > p_def_A


def test_default_by_grade_summary():
    """
    Tests default_by_grade_summary output structure.
    """
    df_synthetic = pd.DataFrame({
        "grade": ["A", "B"],
        "loan_status": ["Fully Paid", "Charged Off"]
    })

    summary = default_by_grade_summary(df_synthetic)

    assert "grade" in summary.columns
    assert "default_rate_pct" in summary.columns
    assert summary.loc[summary["grade"] == "B", "default_rate_pct"].values[0] == 100.0
