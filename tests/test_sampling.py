"""
test_sampling.py
----------------
Unit tests verifying sampling splits, ID disjointness, and train/test stratification.
"""

import numpy as np
import pandas as pd
import pytest
from creditrisk.data.sampling import build_samples, split_development_oot, split_train_test


def test_build_samples_disjoint_and_complete():
    """
    Verifies that build_samples returns train, test, and oot datasets with zero ID overlap
    and 100% total row preservation on synthetic data.
    """
    synthetic_data = pd.DataFrame(
        {
            "id": list(range(1, 101)),
            "vintage_year": [2010] * 80 + [2014] * 20,
            "default_12m": [0, 1] * 40 + [0, 1] * 10,
            "issue_d": ["Jan-10"] * 80 + ["Jan-14"] * 20,
        }
    )

    config = {
        "development_vintages": [2010],
        "oot_vintages": [2014],
        "test_size": 0.2,
        "random_state": 42,
        "target_column": "default_12m",
    }

    samples = build_samples(synthetic_data, config)

    train_df = samples["train"]
    test_df = samples["test"]
    oot_df = samples["oot"]

    # 1. Total row count preservation
    assert len(train_df) + len(test_df) + len(oot_df) == 100
    assert len(train_df) == 64
    assert len(test_df) == 16
    assert len(oot_df) == 20

    # 2. Zero ID overlap across all samples
    train_ids = set(train_df["id"])
    test_ids = set(test_df["id"])
    oot_ids = set(oot_df["id"])

    assert len(train_ids.intersection(test_ids)) == 0
    assert len(train_ids.intersection(oot_ids)) == 0
    assert len(test_ids.intersection(oot_ids)) == 0


def test_train_test_stratification_holds():
    """
    Verifies that train and test default rates match within 0.1% (0.001) due to stratification.
    """
    # Create a 1,000-row synthetic dataset with a 5% default rate
    np.random.seed(42)
    defaults = [1] * 50 + [0] * 950
    np.random.shuffle(defaults)

    synthetic_dev = pd.DataFrame(
        {
            "id": list(range(1, 1001)),
            "vintage_year": [2012] * 1000,
            "default_12m": defaults,
        }
    )

    config = {
        "test_size": 0.2,
        "random_state": 42,
        "target_column": "default_12m",
    }

    train_df, test_df = split_train_test(synthetic_dev, config)

    train_rate = train_df["default_12m"].mean()
    test_rate = test_df["default_12m"].mean()

    # Stratification requirement: rates must be within 0.1% (0.001)
    rate_diff = abs(train_rate - test_rate)
    assert rate_diff <= 0.001, f"Stratification failed: train rate {train_rate:.4f} vs test rate {test_rate:.4f} (diff {rate_diff:.5f})"
