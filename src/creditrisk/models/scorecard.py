"""
scorecard.py
------------
Point-based Credit Scorecard Scaling and Master Rating Grade Module.

Provides functions to:
- Convert WoE logistic regression coefficients into integer point scorecards.
- Score loan datasets by summing feature bin points.
- Construct 8-tier master rating grades ordered from safest (Grade 1) to riskiest (Grade 8).
- Verify rank-ordering monotonicity.
"""

from pathlib import Path
from typing import Any, Dict, Tuple, Union
import numpy as np
import pandas as pd
from creditrisk.features.binning import WoEBinner
from creditrisk.models.pd_model import PDModel, load_pd_config

CONFIG_PATH = Path(__file__).resolve().parents[3] / "config" / "pd_model.yaml"
OUTPUT_TABLES_DIR = Path(__file__).resolve().parents[3] / "outputs" / "pd_evidenced" / "tables"


def build_scorecard(
    pd_model: PDModel,
    woe_binner: WoEBinner,
    config: Union[Dict[str, Any], Path, str] = CONFIG_PATH,
    model_name: str = "model",
    output_dir: Path = OUTPUT_TABLES_DIR,
) -> pd.DataFrame:
    """
    Converts fitted PDModel logistic regression coefficients and WoEBinner rules
    into a point-based credit scorecard.

    Scaling Formulas:
      Factor = PDO / ln(2)
      Offset = Target_Points - Factor * ln(Target_Odds)
      Base_Points_Per_Var = (Offset - Factor * Intercept) / m
      Points_Bin = Base_Points_Per_Var + Factor * (-Coefficient * WoE)

    Parameters
    ----------
    pd_model : PDModel
        Fitted PDModel object.
    woe_binner : WoEBinner
        Fitted WoEBinner object.
    config : dict or Path
        Model configuration.
    model_name : str
        Model name identifier ('model_a' or 'model_b').
    output_dir : Path
        Directory to save the scorecard CSV.

    Returns
    -------
    pd.DataFrame
        Scorecard table with columns: variable, bin, woe, coefficient, points.
    """
    cfg = load_pd_config(config)
    p0 = cfg.get("target_points", 600)
    o0 = cfg.get("target_odds", 50)
    pdo = cfg.get("pts_double_odds", 20)

    factor = pdo / np.log(2)
    offset = p0 - factor * np.log(o0)

    summary_df = pd_model.summary()
    coef_dict = dict(zip(summary_df["variable"], summary_df["coefficient"]))

    intercept = coef_dict.get("const", 0.0)
    features = pd_model.features_
    m = len(features)

    # Distribute offset and intercept evenly across features
    base_points_per_var = (offset - factor * intercept) / m

    scorecard_rows = []

    for var in features:
        coef = coef_dict[var]
        bin_table = woe_binner.get_bin_table(var)

        for _, row in bin_table.iterrows():
            b_label = row["bin"]
            woe = row["woe"]

            # Scorecard points formula: Higher WoE (lower risk) -> Higher points
            pts_unrounded = base_points_per_var + factor * (-coef * woe)
            pts = int(round(pts_unrounded))

            scorecard_rows.append(
                {
                    "variable": var,
                    "bin": b_label,
                    "woe": woe,
                    "coefficient": coef,
                    "points": pts,
                }
            )

    scorecard_df = pd.DataFrame(scorecard_rows)

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"scorecard_{model_name}.csv"
    scorecard_df.to_csv(out_path, index=False)
    print(f"Scorecard saved to: {out_path}")

    return scorecard_df


def score_dataset(df: pd.DataFrame, scorecard: pd.DataFrame, woe_binner: WoEBinner) -> pd.Series:
    """
    Calculates the total credit score for each row in df by summing bin points.

    Parameters
    ----------
    df : pd.DataFrame
        Dataset to score.
    scorecard : pd.DataFrame
        Scorecard table produced by build_scorecard.
    woe_binner : WoEBinner
        Fitted WoEBinner object.

    Returns
    -------
    pd.Series
        Series of integer credit scores.
    """
    total_scores = pd.Series(0, index=df.index, dtype=int)
    variables = scorecard["variable"].unique()

    for var in variables:
        var_sc = scorecard[scorecard["variable"] == var]
        points_map = dict(zip(var_sc["bin"], var_sc["points"]))

        if var not in df:
            raise ValueError(f"Missing scorecard input: {var}")
        binned = woe_binner.bin_values(var, df[var])
        unknown = set(binned.dropna()) - set(points_map)
        if unknown or binned.isna().any():
            raise ValueError(f"No scorecard points for {var}: {sorted(unknown)}")
        var_pts = binned.map(points_map).astype(int)
        total_scores += var_pts

    return total_scores


def build_rating_grades(
    scores: pd.Series,
    y: pd.Series,
    n_grades: int = 8,
    model_name: str = "model",
    output_dir: Path = OUTPUT_TABLES_DIR,
) -> Tuple[pd.DataFrame, bool]:
    """
    Cuts credit scores into n_grades master rating bands (Grade 1 = Safest to Grade 8 = Riskiest).

    Returns
    -------
    Tuple[pd.DataFrame, bool]
        (rating_table, rank_ordering_holds)
    """
    df_temp = pd.DataFrame({"score": scores, "target": y})

    # Cut scores into n_grades quantile bands (higher score = safer / Grade 1)
    # Using qcut with duplicates drop
    df_temp["score_band"] = pd.qcut(df_temp["score"], q=n_grades, duplicates="drop")

    grouped = df_temp.groupby("score_band", observed=False, as_index=False).agg(
        score_min=("score", "min"),
        score_max=("score", "max"),
        n_loans=("target", "count"),
        n_defaults=("target", "sum"),
    )

    total_loans = len(df_temp)

    # Sort descending by score_min (highest scores / safest loans first)
    grouped = grouped.sort_values("score_min", ascending=False).reset_index(drop=True)
    grouped["grade"] = range(1, len(grouped) + 1)

    grouped["observed_default_rate"] = grouped["n_defaults"] / grouped["n_loans"]
    grouped["portfolio_share"] = grouped["n_loans"] / total_loans

    rating_df = grouped[
        ["grade", "score_min", "score_max", "n_loans", "n_defaults", "observed_default_rate", "portfolio_share"]
    ]

    # Check rank ordering monotonicity: default rates must increase monotonically from Grade 1 to Grade N
    def_rates = rating_df["observed_default_rate"].tolist()
    diffs = np.diff(def_rates)
    rank_ordering_holds = bool(np.all(diffs >= 0))

    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"rating_grades_{model_name}.csv"
    rating_df.to_csv(out_path, index=False)
    print(f"Rating grades saved to: {out_path}")

    return rating_df, rank_ordering_holds
