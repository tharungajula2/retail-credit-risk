"""
test_lgd_model.py
-----------------
Unit tests for the TwoStageLGD model in src/creditrisk/models/lgd_model.py.
"""

import numpy as np
import pandas as pd
import pytest
from creditrisk.models.lgd_model import TwoStageLGD, CANDIDATE_FEATURES


def test_two_stage_lgd_bounds_and_combination():
    """
    Tests that predict_lgd output is strictly bounded in [0, 1],
    and checks combination logic: lgd = 1 - (p_rec * rr_hat).
    """
    np.random.seed(42)
    n_samples = 200

    # Create synthetic dataset with candidate features
    synthetic_data = {
        "loan_amnt": np.random.randint(1000, 35000, n_samples),
        "term": np.random.choice([" 36 months", " 60 months"], n_samples),
        "grade": np.random.choice(["A", "B", "C", "D", "E"], n_samples),
        "sub_grade": np.random.choice(["A1", "B2", "C3", "D4"], n_samples),
        "int_rate": np.random.uniform(5.0, 25.0, n_samples),
        "purpose": np.random.choice(["debt_consolidation", "credit_card", "other"], n_samples),
        "home_ownership": np.random.choice(["RENT", "MORTGAGE", "OWN"], n_samples),
        "annual_inc": np.random.uniform(30000, 120000, n_samples),
        "dti": np.random.uniform(5.0, 35.0, n_samples),
        "emp_length": np.random.choice(["10+ years", "2 years", "< 1 year"], n_samples),
        "verification_status": np.random.choice(["Verified", "Source Verified", "Not Verified"], n_samples),
        "inq_last_6mths": np.random.randint(0, 5, n_samples),
        "revol_util": np.random.uniform(10.0, 90.0, n_samples),
    }
    df_synthetic = pd.DataFrame(synthetic_data)
    y_has_rec = pd.Series(np.random.choice([0, 1], n_samples, p=[0.5, 0.5]))
    y_rec_rate = pd.Series(np.where(y_has_rec == 1, np.random.uniform(0.1, 0.8, n_samples), 0.0))

    model = TwoStageLGD(random_state=42)
    stage1_metrics = model.fit(df_synthetic, y_has_rec, y_rec_rate)

    assert "auc" in stage1_metrics
    assert model.is_fitted

    preds = model.predict_lgd(df_synthetic)

    # 1. Bounds check: all predictions must lie in [0, 1]
    assert np.all(preds >= 0.0)
    assert np.all(preds <= 1.0)

    # 2. Check stage outputs explicitly
    X_woe = model.woe_binner.transform(df_synthetic)
    p_rec = model.stage1_clf.predict_proba(X_woe)[:, 1]
    rr_hat = np.clip(model.stage2_reg.predict(X_woe), 0.0, 1.0)
    expected_lgd = np.clip(1.0 - (p_rec * rr_hat), 0.0, 1.0)

    np.testing.assert_allclose(preds, expected_lgd, rtol=1e-5)


def test_zero_recovery_prediction_lgd_near_one():
    """
    Tests that if Stage 1 predicts P(has_recovery) near 0, predicted LGD is near 1.
    """
    model = TwoStageLGD(random_state=42)
    
    # Mock fitted status and mock stage predictions
    class DummyBinner:
        def transform(self, X):
            return X

    class DummyClassifier:
        def predict_proba(self, X):
            # Return near-zero recovery probability (0.01)
            return np.column_stack([np.full(len(X), 0.99), np.full(len(X), 0.01)])

    class DummyRegressor:
        def predict(self, X):
            return np.full(len(X), 0.5)

    model.woe_binner = DummyBinner()
    model.stage1_clf = DummyClassifier()
    model.stage2_reg = DummyRegressor()
    model.is_fitted = True

    df_dummy = pd.DataFrame({"feat1": [1.0, 2.0]})
    lgd_preds = model.predict_lgd(df_dummy)

    # p_rec = 0.01, rr_hat = 0.5 -> expected recovery = 0.005 -> lgd = 0.995
    assert np.allclose(lgd_preds, 0.995)
