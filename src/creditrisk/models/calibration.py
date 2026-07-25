"""
calibration.py
--------------
Probability Recalibration Module for Credit Risk Models.

Functions:
- fit_intercept_recalibration: Freezes all slope coefficients (preserving rank-ordering) and fits a single intercept parameter so mean predicted PD equals observed default rate on calibration data.
- fit_platt_scaling: Fits a 2-parameter logistic regression (slope multiplier + intercept shift) on model logits.
"""

from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union
import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.linear_model import LogisticRegression
from creditrisk.features.binning import WoEBinner
from creditrisk.models.pd_model import PDModel


class RecalibratedPDModel:
    """
    Wrapper around a fitted PDModel that applies intercept recalibration or Platt scaling
    to output recalibrated Probability of Default (PD) estimates.
    """

    def __init__(
        self,
        base_pd_model: PDModel,
        recal_type: str = "intercept",
        intercept_shift: float = 0.0,
        platt_slope: float = 1.0,
        platt_intercept: float = 0.0,
    ):
        self.base_model = base_pd_model
        self.recal_type = recal_type
        self.intercept_shift = intercept_shift
        self.platt_slope = platt_slope
        self.platt_intercept = platt_intercept
        self.features_ = base_pd_model.features_

    def predict_pd(self, df: pd.DataFrame, woe_binner: WoEBinner) -> np.ndarray:
        """
        Predicts recalibrated Probability of Default (PD).
        """
        X_raw = df[self.features_]
        X_woe = woe_binner.transform(X_raw)

        # Get base model raw logit (linear predictor including base intercept)
        base_res = self.base_model.model_fit_
        base_params = base_model_params = base_res.params

        # Compute linear predictor: const + sum(coef * woe)
        X_const = sm.add_constant(X_woe, has_constant="add")
        base_logit = np.dot(X_const.values, base_params.values)

        if self.recal_type == "intercept":
            # Apply single intercept shift: logit_new = base_logit + shift
            recal_logit = base_logit + self.intercept_shift
        elif self.recal_type == "platt":
            # Apply Platt scaling: logit_new = platt_slope * base_logit + platt_intercept
            recal_logit = self.platt_slope * base_logit + self.platt_intercept
        else:
            recal_logit = base_logit

        # Sigmoid conversion to probability: 1 / (1 + exp(-recal_logit))
        recal_pd = 1.0 / (1.0 + np.exp(-recal_logit))
        return recal_pd


def fit_intercept_recalibration(
    pd_model: PDModel,
    woe_binner: WoEBinner,
    calib_df: pd.DataFrame,
    target_col: str = "default_12m",
) -> RecalibratedPDModel:
    """
    Re-estimates ONLY the intercept parameter so mean predicted PD matches the observed default rate.
    Freezes all slope coefficients, preserving Gini, AUC, and rank-ordering.
    """
    X_raw = calib_df[pd_model.features_]
    X_woe = woe_binner.transform(X_raw)

    base_res = pd_model.model_fit_
    base_params = base_res.params

    # Separate base intercept and slope linear predictor
    intercept_base = base_params.get("const", 0.0)
    slopes_params = base_params.drop("const")

    # Compute un-intercepted linear predictor (sum of woe * coef)
    eta_slopes = np.dot(X_woe.values, slopes_params.values)

    y_calib = calib_df[target_col].values

    # Fit statsmodels Logit with constant and offset=eta_slopes
    # Logit(y) = alpha + offset(eta_slopes)
    ones_const = np.ones(len(y_calib))
    logit_recal = sm.Logit(y_calib, ones_const, offset=eta_slopes)
    res_recal = logit_recal.fit(disp=False)

    alpha_new = res_recal.params[0]
    intercept_shift = float(alpha_new - intercept_base)

    return RecalibratedPDModel(
        base_pd_model=pd_model,
        recal_type="intercept",
        intercept_shift=intercept_shift,
    )


def fit_platt_scaling(
    pd_model: PDModel,
    woe_binner: WoEBinner,
    calib_df: pd.DataFrame,
    target_col: str = "default_12m",
) -> RecalibratedPDModel:
    """
    Fits 2-parameter Platt scaling (slope multiplier + intercept shift) on base model logits.
    """
    X_raw = calib_df[pd_model.features_]
    X_woe = woe_binner.transform(X_raw)

    base_res = pd_model.model_fit_
    X_const = sm.add_constant(X_woe, has_constant="add")
    base_logit = np.dot(X_const.values, base_res.params.values)

    y_calib = calib_df[target_col].values

    # Fit LogisticRegression on base_logit as single feature
    lr = LogisticRegression(C=1e5, solver="lbfgs")
    lr.fit(base_logit.reshape(-1, 1), y_calib)

    platt_slope = float(lr.coef_[0][0])
    platt_intercept = float(lr.intercept_[0])

    return RecalibratedPDModel(
        base_pd_model=pd_model,
        recal_type="platt",
        platt_slope=platt_slope,
        platt_intercept=platt_intercept,
    )
