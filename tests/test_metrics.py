"""
test_metrics.py
---------------
Unit tests for statistical validation metrics in src/creditrisk/validation/metrics.py.
"""

import numpy as np
import pytest
from creditrisk.validation.metrics import (
    brier_score,
    calibration_table,
    gini_auc,
    hosmer_lemeshow,
    ks_statistic,
)


def test_perfect_model_gives_auc_one_and_gini_one():
    """
    Verifies that a perfect classifier achieves AUC = 1.0 and Gini = 1.0.
    """
    y_true = np.array([0, 0, 0, 1, 1, 1])
    pd_pred = np.array([0.05, 0.10, 0.15, 0.80, 0.85, 0.90])

    auc, gini = gini_auc(y_true, pd_pred)

    assert auc == 1.0
    assert gini == 1.0


def test_random_model_gives_auc_half_and_gini_zero():
    """
    Verifies that a random classifier gives AUC approx 0.5 and Gini approx 0.0.
    """
    np.random.seed(42)
    y_true = np.random.choice([0, 1], size=1000, p=[0.9, 0.1])
    pd_pred = np.random.uniform(0, 1, size=1000)

    auc, gini = gini_auc(y_true, pd_pred)

    assert 0.45 <= auc <= 0.55
    assert -0.10 <= gini <= 0.10


def test_ks_statistic_bounded_between_zero_and_one():
    """
    Verifies that the Kolmogorov-Smirnov statistic is bounded between 0.0 and 1.0.
    """
    y_true = np.array([0, 0, 1, 1, 0, 1, 0, 1])
    pd_pred = np.array([0.1, 0.2, 0.7, 0.8, 0.3, 0.9, 0.15, 0.65])

    ks_stat, cutoff = ks_statistic(y_true, pd_pred)

    assert 0.0 <= ks_stat <= 1.0
    assert 0.0 <= cutoff <= 1.0


def test_well_calibrated_synthetic_set_passes_hosmer_lemeshow():
    """
    Verifies that a well-calibrated synthetic dataset where y_true is drawn directly from
    binomial probabilities p_i yields a high Hosmer-Lemeshow p-value (> 0.05).
    """
    np.random.seed(42)
    n_samples = 10000

    # Probabilities evenly spread between 0.01 and 0.20
    pd_pred = np.random.uniform(0.01, 0.20, size=n_samples)

    # Generate y_true according to true probability pd_pred
    y_true = np.random.binomial(n=1, p=pd_pred)

    hl_stat, p_val = hosmer_lemeshow(y_true, pd_pred, n_bins=10)

    # Well-calibrated model should NOT reject null hypothesis (p > 0.05)
    assert p_val > 0.05, f"Hosmer-Lemeshow test failed on calibrated dataset: p_val = {p_val:.4f}"
