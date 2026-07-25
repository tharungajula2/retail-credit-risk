"""
SYNTHETIC DEMONSTRATION. Lending Club loans are term loans with no undrawn
limit. This module simulates a revolving sub-portfolio to demonstrate the
CCF methodology used for credit cards / lines of credit. Not for production.

ccf_demo.py
-----------
Credit Conversion Factor (CCF) demonstration module for revolving exposures.
"""

from pathlib import Path
from typing import Any, Dict, Tuple, Union
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SUMMARY_PATH = PROJECT_ROOT / "outputs" / "tables" / "SYNTHETIC_ccf_summary.csv"
DEFAULT_FIGURE_PATH = PROJECT_ROOT / "outputs" / "figures" / "SYNTHETIC_ccf_distribution.png"


def simulate_revolving_portfolio(n: int = 5000, seed: int = 42) -> pd.DataFrame:
    """
    Simulates a synthetic revolving portfolio to demonstrate CCF modeling.

    SYNTHETIC DEMONSTRATION NOTICE:
    LendingClub features fixed-term loans. This dataset is artificially generated
    to illustrate revolving CCF mechanics.

    Parameters
    ----------
    n : int
        Number of synthetic revolving accounts to generate.
    seed : int
        Random seed for reproducibility.

    Returns
    -------
    pd.DataFrame
        Synthetic portfolio containing credit_limit, drawn_balance, undrawn_balance,
        utilisation, default_flag, and drawn_at_default.
    """
    rng = np.random.default_rng(seed)

    # 1. Credit limits between $1,000 and $50,000
    credit_limit = rng.uniform(1000, 50000, size=n)

    # 2. Utilisation between 5% and 95%
    utilisation = rng.beta(a=2, b=3, size=n)
    drawn_balance = credit_limit * utilisation
    undrawn_balance = np.maximum(credit_limit - drawn_balance, 0.0)

    # 3. Default flag (~15% default rate, higher probability for high utilisation)
    def_logit = -2.5 + 2.5 * utilisation + rng.normal(0, 0.5, size=n)
    def_prob = 1.0 / (1.0 + np.exp(-def_logit))
    default_flag = (rng.uniform(0, 1, size=n) < def_prob).astype(int)

    # 4. Drawn at default for defaulted loans: distressed borrowers draw down more undrawn credit
    # Base CCF depends positively on utilisation + noise
    latent_ccf = 0.20 + 0.50 * utilisation + rng.normal(0, 0.15, size=n)
    true_ccf = np.clip(latent_ccf, 0.0, 1.0)

    # Additional drawdown at default = undrawn_balance * true_ccf
    additional_drawdown = undrawn_balance * true_ccf
    drawn_at_default = np.where(
        default_flag == 1,
        drawn_balance + additional_drawdown,
        drawn_balance
    )

    df_synth = pd.DataFrame({
        "credit_limit": credit_limit,
        "drawn_balance": drawn_balance,
        "undrawn_balance": undrawn_balance,
        "utilisation": utilisation,
        "default_flag": default_flag,
        "drawn_at_default": drawn_at_default
    })

    return df_synth


def compute_realised_ccf(df: pd.DataFrame) -> pd.DataFrame:
    """
    Computes realised CCF for defaulted accounts:
    ccf = (drawn_at_default - drawn_balance) / undrawn_balance, clipped to [0, 1].

    Parameters
    ----------
    df : pd.DataFrame
        Synthetic revolving DataFrame containing default_flag, drawn_at_default,
        drawn_balance, undrawn_balance.

    Returns
    -------
    pd.DataFrame
        Defaulted subset with derived realised `ccf` column.
    """
    df_def = df[df["default_flag"] == 1].copy()
    if len(df_def) == 0:
        raise ValueError("No defaulted accounts found in input DataFrame.")

    # Guard against zero undrawn balance
    valid_undrawn_mask = df_def["undrawn_balance"] > 0
    additional_draw = df_def["drawn_at_default"] - df_def["drawn_balance"]

    raw_ccf = np.where(
        valid_undrawn_mask,
        additional_draw / df_def["undrawn_balance"],
        0.0
    )
    df_def["ccf"] = np.clip(raw_ccf, 0.0, 1.0)
    return df_def


def fit_ccf_model(df_def: pd.DataFrame) -> Tuple[LinearRegression, Dict[str, float], pd.DataFrame]:
    """
    Fits an OLS Linear Regression modeling realised CCF on utilisation and credit_limit.

    Returns
    -------
    Tuple[LinearRegression, Dict[str, float], pd.DataFrame]
        Fitted model, evaluation metrics, and summary DataFrame.
    """
    if "ccf" not in df_def.columns:
        df_def = compute_realised_ccf(df_def)

    X = df_def[["utilisation", "credit_limit"]]
    y = df_def["ccf"]

    model = LinearRegression()
    model.fit(X, y)

    y_pred = np.clip(model.predict(X), 0.0, 1.0)
    mae = float(mean_absolute_error(y, y_pred))

    metrics = {
        "count_defaulted": len(df_def),
        "intercept": float(model.intercept_),
        "coef_utilisation": float(model.coef_[0]),
        "coef_credit_limit": float(model.coef_[1]),
        "mean_actual_ccf": float(y.mean()),
        "mean_predicted_ccf": float(y_pred.mean()),
        "mae": mae
    }

    summary_df = pd.DataFrame([{
        "NOTICE": "[SYNTHETIC DEMONSTRATION ONLY - NOT PRODUCTION DATA]",
        "count_defaulted": metrics["count_defaulted"],
        "mean_actual_ccf": metrics["mean_actual_ccf"],
        "mean_predicted_ccf": metrics["mean_predicted_ccf"],
        "mae": metrics["mae"],
        "intercept": metrics["intercept"],
        "coef_utilisation": metrics["coef_utilisation"],
        "coef_credit_limit": metrics["coef_credit_limit"]
    }])

    return model, metrics, summary_df


def ead_revolving(drawn: float, undrawn: float, ccf: float) -> float:
    """
    Calculates EAD for revolving exposure:
    EAD = drawn + (ccf * undrawn)
    """
    ccf_clipped = max(0.0, min(1.0, ccf))
    return float(drawn + ccf_clipped * undrawn)


def run_ccf_demonstration(
    summary_path: Union[str, Path] = DEFAULT_SUMMARY_PATH,
    fig_path: Union[str, Path] = DEFAULT_FIGURE_PATH
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Executes full synthetic CCF workflow, saves tables/plots, and prints worked EAD example.
    """
    # 1. Simulate portfolio
    df_synth = simulate_revolving_portfolio(n=5000, seed=42)

    # 2. Compute realised CCF on defaults
    df_def = compute_realised_ccf(df_synth)

    # 3. Fit CCF regression model
    model, metrics, summary_df = fit_ccf_model(df_def)

    # 4. Save table with SYNTHETIC_ prefix and header notice
    summary_path = Path(summary_path)
    fig_path = Path(fig_path)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    fig_path.parent.mkdir(parents=True, exist_ok=True)

    summary_df.to_csv(summary_path, index=False)

    # 5. Plot histogram of realised CCF
    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.hist(df_def["ccf"], bins=20, range=(0.0, 1.0), color="#ff7f0e", edgecolor="black", alpha=0.8)
    ax.set_title("[SYNTHETIC DEMONSTRATION] Realised CCF Distribution (Revolving Defaults)", fontsize=13, pad=12)
    ax.set_xlabel("Credit Conversion Factor (CCF)", fontsize=11)
    ax.set_ylabel("Number of Accounts", fontsize=11)
    ax.grid(axis="y", linestyle="--", alpha=0.5)

    plt.tight_layout()
    fig.savefig(fig_path, dpi=300)
    plt.close(fig)

    # 6. Worked EAD Example
    card_limit = 100000.0
    card_drawn = 30000.0
    card_undrawn = card_limit - card_drawn
    card_util = card_drawn / card_limit

    # Predict CCF using fitted model
    pred_ccf_example = float(model.predict([[card_util, card_limit]])[0])
    pred_ccf_example = max(0.0, min(1.0, pred_ccf_example))
    worked_ead = ead_revolving(card_drawn, card_undrawn, pred_ccf_example)

    worked_example = {
        "card_limit": card_limit,
        "card_drawn": card_drawn,
        "card_undrawn": card_undrawn,
        "card_util": card_util,
        "predicted_ccf": pred_ccf_example,
        "resulting_ead": worked_ead
    }

    print("=" * 75)
    print(" [SYNTHETIC DEMONSTRATION ONLY] REVOLVING CCF & EAD WORKED EXAMPLE")
    print("=" * 75)
    print(f"Credit Card Limit          : ${card_limit:,.2f}")
    print(f"Drawn Balance at Obs       : ${card_drawn:,.2f}")
    print(f"Undrawn Commitment         : ${card_undrawn:,.2f}")
    print(f"Observation Utilisation    : {card_util * 100:.1f}%")
    print(f"Predicted CCF              : {pred_ccf_example:.4f} ({pred_ccf_example * 100:.2f}% undrawn drawdown)")
    print(f"Resulting EAD              : ${worked_ead:,.2f}")
    print("=" * 75)

    return summary_df, worked_example
