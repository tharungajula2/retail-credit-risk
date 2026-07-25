"""
test_pd_model.py
----------------
Unit tests for PDModel in src/creditrisk/models/pd_model.py.
"""

import numpy as np
import pandas as pd
import pytest
from creditrisk.features.binning import WoEBinner
from creditrisk.models.pd_model import PDModel


def test_pd_model_leakage_guard_fires():
    """
    Verifies that PDModel.fit raises ValueError when an outcome feature
    such as 'recoveries' is passed in the IV table / feature list.
    """
    df = pd.DataFrame(
        {
            "loan_amnt": [1000, 2000, 3000] * 10,
            "recoveries": [0.0, 100.0, 0.0] * 10,
            "default_12m": [0, 1, 0] * 10,
        }
    )

    binner = WoEBinner()
    binner.fit(df[["loan_amnt"]], df["default_12m"])

    # Create IV table containing 'recoveries'
    iv_table = pd.DataFrame(
        {
            "variable": ["loan_amnt", "recoveries"],
            "IV": [0.10, 0.50],
        }
    )

    model = PDModel()
    with pytest.raises(ValueError, match="Target leakage violation detected"):
        model.fit(df, binner, iv_table)


def test_pd_model_predictions_bounded_between_0_and_1():
    """
    Verifies that predicted PD probabilities from PDModel are strictly bounded between 0.0 and 1.0.
    """
    np.random.seed(42)
    n_samples = 100
    df = pd.DataFrame(
        {
            "annual_inc": np.random.uniform(20000, 100000, n_samples),
            "dti": np.random.uniform(5, 35, n_samples),
            "default_12m": np.random.choice([0, 1], size=n_samples, p=[0.9, 0.1]),
        }
    )

    binner = WoEBinner(min_bin_pct=0.05)
    binner.fit(df[["annual_inc", "dti"]], df["default_12m"])

    iv_table = binner.get_iv_table()

    model = PDModel()
    model.fit(df, binner, iv_table)

    predicted_pds = model.predict_pd(df, binner)

    assert len(predicted_pds) == n_samples
    assert np.all(predicted_pds >= 0.0), "Predicted PD contains values < 0.0"
    assert np.all(predicted_pds <= 1.0), "Predicted PD contains values > 1.0"
