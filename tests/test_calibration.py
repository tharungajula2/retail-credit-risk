"""
test_calibration.py
-------------------
Unit tests for probability recalibration functions in src/creditrisk/models/calibration.py.
"""

import numpy as np
import pandas as pd
import pytest
from creditrisk.features.binning import WoEBinner
from creditrisk.models.calibration import fit_intercept_recalibration, fit_platt_scaling
from creditrisk.models.pd_model import PDModel
from creditrisk.validation.metrics import gini_auc


def test_intercept_recalibration_aligns_mean_pd_and_preserves_auc():
    """
    Verifies that fit_intercept_recalibration aligns the mean predicted PD to the observed default rate
    on the calibration set while preserving exact ROC-AUC / Gini rank ordering.
    """
    np.random.seed(42)
    n_samples = 200

    train_df = pd.DataFrame(
        {
            "annual_inc": np.random.uniform(20000, 100000, n_samples),
            "dti": np.random.uniform(5, 35, n_samples),
            "default_12m": np.random.choice([0, 1], size=n_samples, p=[0.8, 0.2]),
        }
    )

    binner = WoEBinner(min_bin_pct=0.05)
    binner.fit(train_df[["annual_inc", "dti"]], train_df["default_12m"])
    iv_table = binner.get_iv_table()

    config = {
        "target_points": 600,
        "target_odds": 50,
        "pts_double_odds": 20,
        "min_iv_threshold": 0.0,
        "target_column": "default_12m",
    }

    base_model = PDModel(config=config)
    base_model.fit(train_df, binner, iv_table)

    # Create a calibration set with lower default rate (10% vs 20%)
    calib_df = pd.DataFrame(
        {
            "annual_inc": np.random.uniform(20000, 100000, n_samples),
            "dti": np.random.uniform(5, 35, n_samples),
            "default_12m": np.random.choice([0, 1], size=n_samples, p=[0.9, 0.1]),
        }
    )

    base_pds = base_model.predict_pd(calib_df, binner)
    base_auc, base_gini = gini_auc(calib_df["default_12m"].values, base_pds)

    recal_model = fit_intercept_recalibration(base_model, binner, calib_df, target_col="default_12m")
    recal_pds = recal_model.predict_pd(calib_df, binner)
    recal_auc, recal_gini = gini_auc(calib_df["default_12m"].values, recal_pds)

    # 1. AUC and Gini must be identical (rank-ordering preserved)
    assert abs(recal_auc - base_auc) < 1e-5
    assert abs(recal_gini - base_gini) < 1e-5

    # 2. Mean predicted PD must closely align to observed default rate on calibration set
    obs_rate = calib_df["default_12m"].mean()
    mean_recal_pd = recal_pds.mean()
    assert abs(mean_recal_pd - obs_rate) < 0.01
