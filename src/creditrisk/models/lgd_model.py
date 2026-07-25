"""
lgd_model.py
------------
Two-stage Loss Given Default (LGD) model implementation.

Stage 1: Logistic Regression predicting P(has_recovery == 1).
Stage 2: Regressor predicting recovery_rate given has_recovery == 1.
Combined prediction: expected_recovery = P(has_recovery == 1) * E[recovery_rate | recovery]
                     LGD_hat = 1 - expected_recovery (clipped to [0, 1])
"""

import pickle
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import mean_absolute_error, roc_auc_score

from creditrisk.features.binning import WoEBinner

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_MODEL_PATH = PROJECT_ROOT / "outputs" / "models" / "lgd_model.pkl"
DEFAULT_CALIB_TABLE_PATH = PROJECT_ROOT / "outputs" / "tables" / "lgd_calibration.csv"
DEFAULT_SCATTER_FIG_PATH = PROJECT_ROOT / "outputs" / "figures" / "lgd_pred_vs_actual.png"

CANDIDATE_FEATURES = [
    "loan_amnt", "term", "grade", "sub_grade", "int_rate", "purpose",
    "home_ownership", "annual_inc", "dti", "emp_length",
    "verification_status", "inq_last_6mths", "revol_util"
]


class TwoStageLGD:
    """
    Two-Stage Hurdle Model for Loss Given Default (LGD).

    Stage 1: Logistic Regression predicting recovery occurrence P(has_recovery == 1).
    Stage 2: GradientBoostingRegressor predicting recovery rate given has_recovery == 1.

    Justification for Stage 2 choice:
    GradientBoostingRegressor non-parametrically models complex non-linear feature interactions
    and skewed recovery rate distributions directly without forcing restrictive logit-symmetry
    assumptions on non-Gaussian residuals.
    """

    def __init__(self, regressor_type: str = "gbr", random_state: int = 42):
        self.regressor_type = regressor_type
        self.random_state = random_state
        self.stage1_clf = LogisticRegression(random_state=random_state, max_iter=1000)
        
        if regressor_type == "gbr":
            self.stage2_reg = GradientBoostingRegressor(
                n_estimators=100, learning_rate=0.05, max_depth=3, random_state=random_state
            )
        else:
            raise ValueError(f"Unsupported regressor_type: {regressor_type}")
            
        self.woe_binner: Optional[WoEBinner] = None
        self.feature_names: List[str] = []
        self.is_fitted: bool = False

    def fit_recovery_classifier(self, X: pd.DataFrame, y_has_recovery: pd.Series) -> Dict[str, float]:
        """
        Fits Stage 1 Logistic Regression predicting P(has_recovery == 1).
        """
        self.stage1_clf.fit(X, y_has_recovery)
        y_prob = self.stage1_clf.predict_proba(X)[:, 1]
        
        auc = float(roc_auc_score(y_has_recovery, y_prob))
        gini = 2.0 * auc - 1.0
        return {"auc": auc, "gini": gini}

    def fit_recovery_regressor(self, X_recovered: pd.DataFrame, recovery_rate_recovered: pd.Series):
        """
        Fits Stage 2 Regressor on loans with has_recovery == 1. Target = recovery_rate.
        """
        self.stage2_reg.fit(X_recovered, recovery_rate_recovered)

    def fit(self, X: pd.DataFrame, y_has_recovery: pd.Series, recovery_rate: pd.Series) -> Dict[str, float]:
        """
        Fits WoE Binner, Stage 1 Classifier, and Stage 2 Regressor on training data.
        """
        self.feature_names = list(X.columns)
        
        # 1. Fit new WoEBinner on LGD training data using y_has_recovery as target
        self.woe_binner = WoEBinner()
        self.woe_binner.fit(X, y_has_recovery)
        X_woe = self.woe_binner.transform(X)

        # 2. Stage 1: Fit Classifier
        stage1_metrics = self.fit_recovery_classifier(X_woe, y_has_recovery)

        # 3. Stage 2: Fit Regressor on positive recoveries only
        recovered_mask = (y_has_recovery == 1)
        X_woe_recovered = X_woe[recovered_mask]
        rec_rate_recovered = recovery_rate[recovered_mask]

        self.fit_recovery_regressor(X_woe_recovered, rec_rate_recovered)
        
        self.is_fitted = True
        return stage1_metrics

    def predict_lgd(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predicts expected LGD:
        p_rec = P(has_recovery == 1)
        rr_hat = predicted recovery rate given has_recovery == 1
        exp_rr = p_rec * rr_hat
        lgd_hat = 1 - exp_rr (clipped to [0, 1])
        """
        if not self.is_fitted or self.woe_binner is None:
            raise ValueError("Model is not fitted. Call fit() before predict_lgd().")

        X_feat = X[self.feature_names] if self.feature_names else X
        X_woe = self.woe_binner.transform(X_feat)
        
        # Stage 1: P(has_recovery == 1)
        p_rec = self.stage1_clf.predict_proba(X_woe)[:, 1]

        # Stage 2: predicted recovery rate given recovery
        rr_hat = self.stage2_reg.predict(X_woe)
        rr_hat = np.clip(rr_hat, 0.0, 1.0)

        # Expected recovery rate and LGD
        exp_rr = p_rec * rr_hat
        lgd_hat = np.clip(1.0 - exp_rr, 0.0, 1.0)

        return lgd_hat

    def save(self, file_path: Union[str, Path] = DEFAULT_MODEL_PATH):
        """Serializes fitted model to disk."""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump(self, f)
        print(f"Saved TwoStageLGD model to: {path}")

    @classmethod
    def load(cls, file_path: Union[str, Path] = DEFAULT_MODEL_PATH) -> "TwoStageLGD":
        """Loads serialized model from disk."""
        path = Path(file_path)
        with open(path, "rb") as f:
            model = pickle.load(f)
        return model


def evaluate_lgd_model(
    model: TwoStageLGD,
    X_test: pd.DataFrame,
    y_test_lgd: pd.Series,
    y_test_recovery_rate: pd.Series,
    calib_table_path: Union[str, Path] = DEFAULT_CALIB_TABLE_PATH,
    scatter_fig_path: Union[str, Path] = DEFAULT_SCATTER_FIG_PATH
) -> Tuple[Dict[str, float], pd.DataFrame]:
    """
    Evaluates two-stage LGD model on test set:
    - MAE actual vs predicted LGD
    - Overall portfolio mean actual vs predicted LGD
    - Decile calibration table
    - Scatter plot saving
    """
    pred_lgd = model.predict_lgd(X_test)
    actual_lgd = y_test_lgd.values

    mae = float(mean_absolute_error(actual_lgd, pred_lgd))
    overall_mean_actual = float(np.mean(actual_lgd))
    overall_mean_pred = float(np.mean(pred_lgd))

    # Stage 2 MAE on recovered subset
    has_rec_mask = (y_test_recovery_rate > 0) | ((1 - y_test_lgd) > 0)
    X_test_woe = model.woe_binner.transform(X_test)
    pred_rr_given_rec = np.clip(model.stage2_reg.predict(X_test_woe[has_rec_mask]), 0.0, 1.0)
    actual_rr_given_rec = y_test_recovery_rate[has_rec_mask].values
    stage2_mae = float(mean_absolute_error(actual_rr_given_rec, pred_rr_given_rec))

    # Build calibration table by deciles of predicted LGD
    eval_df = pd.DataFrame({"actual_lgd": actual_lgd, "predicted_lgd": pred_lgd})
    eval_df["decile"] = pd.qcut(eval_df["predicted_lgd"], q=10, labels=False, duplicates="drop") + 1

    calib_summary = (
        eval_df.groupby("decile")
        .agg(
            count=("actual_lgd", "count"),
            mean_predicted_lgd=("predicted_lgd", "mean"),
            mean_actual_lgd=("actual_lgd", "mean")
        )
        .reset_index()
    )
    calib_summary["abs_error"] = (calib_summary["mean_predicted_lgd"] - calib_summary["mean_actual_lgd"]).abs()

    # Save calibration table
    calib_table_path = Path(calib_table_path)
    calib_table_path.parent.mkdir(parents=True, exist_ok=True)
    calib_summary.to_csv(calib_table_path, index=False)

    # Plot predicted vs actual scatter / decile comparison
    scatter_fig_path = Path(scatter_fig_path)
    scatter_fig_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 5.5))
    ax.scatter(eval_df["predicted_lgd"], eval_df["actual_lgd"], alpha=0.15, color="#1f77b4", s=10, label="Loans")
    ax.plot(calib_summary["mean_predicted_lgd"], calib_summary["mean_actual_lgd"], 'ro-', linewidth=2, label="Decile Means")
    ax.plot([0, 1], [0, 1], 'k--', alpha=0.7, label="Perfect Calibration Line")
    ax.set_xlabel("Predicted LGD", fontsize=11)
    ax.set_ylabel("Actual LGD", fontsize=11)
    ax.set_title("LGD Model: Predicted vs Actual Calibration", fontsize=13, pad=12)
    ax.legend(loc="upper left")
    ax.grid(True, linestyle="--", alpha=0.5)

    plt.tight_layout()
    fig.savefig(scatter_fig_path, dpi=300)
    plt.close(fig)

    metrics = {
        "overall_mae": mae,
        "stage2_mae": stage2_mae,
        "portfolio_mean_actual_lgd": overall_mean_actual,
        "portfolio_mean_pred_lgd": overall_mean_pred,
    }

    return metrics, calib_summary
