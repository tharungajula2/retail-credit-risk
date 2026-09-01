"""
schema.py
---------
Schema governance and anti-leakage module.

Provides utility functions to load variable classification configurations,
retrieve PD-eligible feature candidate lists, assert target leakage protection,
and validate complete dataset schema coverage.
"""

from pathlib import Path
from typing import Any, Dict, List
import pandas as pd
import yaml

# Path to the central variable classification configuration
CONFIG_PATH = Path(__file__).resolve().parents[3] / "config" / "variables.yaml"


def load_variable_config(config_path: Path = CONFIG_PATH) -> Dict[str, List[str]]:
    """
    Loads and returns the variable classification dictionary from variables.yaml.

    Parameters
    ----------
    config_path : Path, optional
        Path to the YAML configuration file.

    Returns
    -------
    Dict[str, List[str]]
        Dictionary mapping category names to lists of column names.
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Variable configuration file not found at: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    return config


def get_pd_eligible_columns(config_path: Path = CONFIG_PATH) -> List[str]:
    """
    Returns all application-time feature candidates eligible for PD modeling
    (combining baseline application_time and sparse_application columns).

    Parameters
    ----------
    config_path : Path, optional
        Path to the YAML configuration file.

    Returns
    -------
    List[str]
        List of column names safe for Probability of Default modeling.
    """
    config = load_variable_config(config_path)
    app_time = config.get("application_time", [])
    sparse_app = config.get("sparse_application", [])
    
    # Preserve order while combining lists
    return app_time + sparse_app


def assert_no_leakage(columns: List[str], config_path: Path = CONFIG_PATH) -> None:
    """
    Asserts that no post-origination outcome columns or database identifiers
    are present in the provided feature column list.

    Parameters
    ----------
    columns : List[str]
        List of feature column names to validate.

    Raises
    ------
    ValueError
        If any outcome or identifier column is detected in the input column list.
    """
    config = load_variable_config(config_path)
    outcome_cols = set(config.get("outcome", []))
    identifier_cols = set(config.get("identifier", []))

    # Identify prohibited columns present in the input feature list
    leaked_outcomes = set(columns).intersection(outcome_cols)
    leaked_identifiers = set(columns).intersection(identifier_cols)

    leaked_all = sorted(list(leaked_outcomes.union(leaked_identifiers)))

    if leaked_all:
        raise ValueError(
            f"Target leakage violation detected! Prohibited columns found: {leaked_all}"
        )


def validate_schema_coverage(df: pd.DataFrame, config_path: Path = CONFIG_PATH) -> None:
    """
    Validates that every column in the input DataFrame is classified in variables.yaml,
    and every classified column exists in the input DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame whose columns are being validated.

    Raises
    ------
    ValueError
        If unclassified columns exist in df or expected classified columns are missing.
    """
    config = load_variable_config(config_path)

    # Flatten all classified columns from the YAML config
    all_classified = set()
    for col_list in config.values():
        all_classified.update(col_list)

    df_cols = set(df.columns)

    unclassified_cols = df_cols - all_classified
    missing_cols = all_classified - df_cols

    error_messages = []
    if unclassified_cols:
        error_messages.append(
            f"Unclassified column(s) present in DataFrame: {sorted(list(unclassified_cols))}"
        )

    if missing_cols:
        error_messages.append(
            f"Classified column(s) missing from DataFrame: {sorted(list(missing_cols))}"
        )

    if error_messages:
        raise ValueError("Schema coverage validation failed:\n" + "\n".join(error_messages))
