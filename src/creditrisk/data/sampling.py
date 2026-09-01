"""
sampling.py
-----------
Dataset sampling and partitioning module for retail credit risk modeling.

Provides functions to partition datasets into Development (2007-2013) and
Out-Of-Time (OOT 2014) samples, perform 80/20 stratified train/test splits,
verify zero loan ID overlap, and output summary metrics to CSV.
"""

from pathlib import Path
from typing import Any, Dict, Tuple, Union
import pandas as pd
from sklearn.model_selection import train_test_split
import yaml

CONFIG_PATH = Path(__file__).resolve().parents[3] / "config" / "sampling.yaml"
OUTPUT_TABLE_PATH = Path(__file__).resolve().parents[3] / "outputs" / "tables" / "sample_summary.csv"


def load_sampling_config(config: Union[Dict[str, Any], Path, str] = CONFIG_PATH) -> Dict[str, Any]:
    """
    Loads sampling configuration parameters from YAML file path or dict.
    """
    if isinstance(config, (str, Path)):
        path = Path(config)
        if not path.exists():
            raise FileNotFoundError(f"Sampling configuration file not found at: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    elif isinstance(config, dict):
        return config
    else:
        raise TypeError("Config must be a dictionary or a valid file path.")


def split_development_oot(df: pd.DataFrame, config: Union[Dict[str, Any], Path, str] = CONFIG_PATH) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Splits dataset into Development (2007-2013) and Out-Of-Time (OOT 2014) samples by vintage_year.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing 'vintage_year'.
    config : dict or Path
        Sampling configuration.

    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame]
        (dev_df, oot_df)
    """
    cfg = load_sampling_config(config)
    dev_vintages = set(cfg.get("development_vintages", []))
    oot_vintages = set(cfg.get("oot_vintages", []))

    dev_df = df[df["vintage_year"].isin(dev_vintages)].copy()
    oot_df = df[df["vintage_year"].isin(oot_vintages)].copy()

    return dev_df, oot_df


def split_train_test(dev_df: pd.DataFrame, config: Union[Dict[str, Any], Path, str] = CONFIG_PATH) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Performs stratified 80/20 split on the development dataset based on target_column.

    Parameters
    ----------
    dev_df : pd.DataFrame
        Development dataset.
    config : dict or Path
        Sampling configuration.

    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame]
        (train_df, test_df)
    """
    cfg = load_sampling_config(config)
    test_size = cfg.get("test_size", 0.2)
    random_state = cfg.get("random_state", 42)
    target_col = cfg.get("target_column", "default_12m")

    train_df, test_df = train_test_split(
        dev_df,
        test_size=test_size,
        random_state=random_state,
        stratify=dev_df[target_col],
    )

    return train_df.copy(), test_df.copy()


def build_samples(df: pd.DataFrame, config: Union[Dict[str, Any], Path, str] = CONFIG_PATH) -> Dict[str, pd.DataFrame]:
    """
    Constructs train, test, and oot sample DataFrames, verifying zero loan ID overlap
    and 100% row count preservation.

    Parameters
    ----------
    df : pd.DataFrame
        Target-engineered dataset.
    config : dict or Path
        Sampling configuration.

    Returns
    -------
    Dict[str, pd.DataFrame]
        Dictionary with keys 'train', 'test', 'oot'.
    """
    cfg = load_sampling_config(config)
    dev_df, oot_df = split_development_oot(df, cfg)
    train_df, test_df = split_train_test(dev_df, cfg)

    # 1. Assert zero ID overlap across samples
    train_ids = set(train_df["id"])
    test_ids = set(test_df["id"])
    oot_ids = set(oot_df["id"])

    overlap_train_test = train_ids.intersection(test_ids)
    overlap_train_oot = train_ids.intersection(oot_ids)
    overlap_test_oot = test_ids.intersection(oot_ids)

    if overlap_train_test or overlap_train_oot or overlap_test_oot:
        raise ValueError(
            f"Loan ID overlap detected between samples! "
            f"Train-Test: {len(overlap_train_test)}, Train-OOT: {len(overlap_train_oot)}, Test-OOT: {len(overlap_test_oot)}"
        )

    # 2. Assert total row count preservation
    total_split_rows = len(train_df) + len(test_df) + len(oot_df)
    if total_split_rows != len(df):
        raise ValueError(
            f"Row count mismatch! Total input rows ({len(df):,}) != sum of samples ({total_split_rows:,})."
        )

    return {
        "train": train_df,
        "test": test_df,
        "oot": oot_df,
    }


def sample_summary(samples: Dict[str, pd.DataFrame], output_path: Path = OUTPUT_TABLE_PATH) -> pd.DataFrame:
    """
    Computes sample summary metrics (n_loans, n_defaults, default_rate, min_issue_d, max_issue_d)
    for train, test, and oot datasets, exporting to CSV.

    Parameters
    ----------
    samples : Dict[str, pd.DataFrame]
        Dictionary of samples.
    output_path : Path, optional
        Destination CSV path.

    Returns
    -------
    pd.DataFrame
        Summary DataFrame.
    """
    summary_rows = []

    for name in ["train", "test", "oot"]:
        if name in samples:
            sample_df = samples[name]
            n_loans = len(sample_df)
            n_defaults = int(sample_df["default_12m"].sum())
            default_rate = n_defaults / n_loans if n_loans > 0 else 0.0

            # Determine min and max issue dates
            issue_dates = sample_df["issue_d"].dropna()
            min_issue = issue_dates.min() if not issue_dates.empty else "N/A"
            max_issue = issue_dates.max() if not issue_dates.empty else "N/A"

            summary_rows.append(
                {
                    "sample": name,
                    "n_loans": n_loans,
                    "n_defaults": n_defaults,
                    "default_rate": default_rate,
                    "min_issue_d": min_issue,
                    "max_issue_d": max_issue,
                }
            )

    summary_df = pd.DataFrame(summary_rows)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary_df.to_csv(output_path, index=False)
    print(f"Sample summary table saved to: {output_path}")

    return summary_df
