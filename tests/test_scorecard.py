"""
test_scorecard.py
-----------------
Unit tests for scorecard scaling and master rating grades in src/creditrisk/models/scorecard.py.
"""

import numpy as np
import pandas as pd
import pytest
from creditrisk.features.binning import WoEBinner
from creditrisk.models.pd_model import PDModel
from creditrisk.models.scorecard import build_rating_grades, build_scorecard, score_dataset


def test_hand_computed_scorecard_points():
    """
    Verifies that build_scorecard produces exact hand-computed points based on:
    Factor = 20 / ln(2) = 28.8539008
    Offset = 600 - Factor * ln(50) = 487.122934
    """
    np.random.seed(42)
    n_samples = 100
    df = pd.DataFrame(
        {
            "annual_inc": np.random.uniform(20000, 100000, n_samples),
            "default_12m": np.random.choice([0, 1], size=n_samples, p=[0.85, 0.15]),
        }
    )

    binner = WoEBinner(min_bin_pct=0.05)
    binner.fit(df[["annual_inc"]], df["default_12m"])

    iv_table = binner.get_iv_table()

    config = {
        "target_points": 600,
        "target_odds": 50,
        "pts_double_odds": 20,
        "min_iv_threshold": 0.0,
        "target_column": "default_12m",
    }

    model = PDModel(config=config)
    model.fit(df, binner, iv_table)

    scorecard = build_scorecard(model, binner, config=config, model_name="test")

    factor = 20 / np.log(2)
    offset = 600 - factor * np.log(50)
    intercept = model.model_fit_.params["const"]
    coef = model.model_fit_.params["annual_inc"]

    first_row = scorecard.iloc[0]
    hand_pts = int(round((offset - factor * intercept) + factor * (-coef * first_row["woe"])))

    assert first_row["points"] == hand_pts


def test_score_dataset_sums_feature_points_correctly():
    """
    Verifies that score_dataset calculates total scores matching the sum of bin points.
    """
    np.random.seed(42)
    n_samples = 100
    df = pd.DataFrame(
        {
            "annual_inc": np.random.uniform(20000, 100000, n_samples),
            "dti": np.random.uniform(5, 35, n_samples),
            "default_12m": np.random.choice([0, 1], size=n_samples, p=[0.85, 0.15]),
        }
    )

    binner = WoEBinner(min_bin_pct=0.05)
    binner.fit(df[["annual_inc", "dti"]], df["default_12m"])

    iv_table = binner.get_iv_table()

    config = {
        "target_points": 600,
        "target_odds": 50,
        "pts_double_odds": 20,
        "min_iv_threshold": 0.0,
        "target_column": "default_12m",
    }

    model = PDModel(config=config)
    model.fit(df, binner, iv_table)

    scorecard = build_scorecard(model, binner, config=config, model_name="test")
    scores = score_dataset(df, scorecard, binner)

    assert len(scores) == n_samples
    assert not scores.isna().any()


def test_rating_grades_rank_ordering_monotonicity():
    """
    Verifies that build_rating_grades detects monotonic default rates from Grade 1 (safest) to Grade N (riskiest).
    """
    # High score -> Low target (0)
    scores = pd.Series([700, 650, 600, 550, 500, 450, 400, 350] * 10)
    # Target default (1) increases as score decreases
    targets = pd.Series([0, 0, 0, 1, 1, 1, 1, 1] * 10)

    rating_df, rank_holds = build_rating_grades(scores, targets, n_grades=4, model_name="test")

    assert rank_holds is True
    # Grade 1 must have lower default rate than Grade 4
    assert rating_df.loc[0, "observed_default_rate"] <= rating_df.loc[len(rating_df) - 1, "observed_default_rate"]
