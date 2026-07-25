"""
test_macro_scenarios.py
------------------------
Unit tests for forward-looking macroeconomic scenarios and performing-book comparison in src/creditrisk/regulatory/macro_scenarios.py.
"""

import numpy as np
import pandas as pd
import pytest
from creditrisk.regulatory.macro_scenarios import (
    load_macro_config,
    probability_weighted_ecl,
    scenario_ecl
)


def test_scenario_ordering_and_probability_weighting():
    """
    Tests:
    1. downside ECL > baseline ECL > upside ECL
    2. probability-weighted ECL lies between upside ECL and downside ECL
    3. Scenario weights sum to 1.0
    """
    cfg = load_macro_config()
    scenarios_cfg = cfg.get("scenarios", {})

    # 1. Weights sum to 1.0
    total_w = sum(sc["weight"] for sc in scenarios_cfg.values())
    assert np.isclose(total_w, 1.0)

    # Synthetic loan portfolio
    df_synthetic = pd.DataFrame({
        "stage": ["Stage 1", "Stage 2", "Stage 3"],
        "current_pd_12m": [0.02, 0.05, 1.00],
        "lifetime_pd": [0.06, 0.15, 1.00],
        "lgd_hat": [0.80, 0.80, 0.80],
        "ead": [10000.0, 10000.0, 10000.0],
        "remaining_term": [24, 24, 24],
        "int_rate": [10.0, 10.0, 10.0]
    })

    # Compute scenario ECLs
    df_upside = scenario_ecl(df_synthetic, pd_multiplier=0.85)
    df_baseline = scenario_ecl(df_synthetic, pd_multiplier=1.00)
    df_downside = scenario_ecl(df_synthetic, pd_multiplier=1.50)

    ecl_upside = df_upside["ecl"].sum()
    ecl_baseline = df_baseline["ecl"].sum()
    ecl_downside = df_downside["ecl"].sum()

    # 2. Downside ECL > Baseline ECL > Upside ECL
    assert ecl_downside > ecl_baseline
    assert ecl_baseline > ecl_upside

    # Compute probability-weighted ECL
    summary_df, weighted_total, sc_dfs = probability_weighted_ecl(df_synthetic)

    # 3. Probability-weighted total lies strictly between upside and downside
    assert ecl_upside <= weighted_total <= ecl_downside
