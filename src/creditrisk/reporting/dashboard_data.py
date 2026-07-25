"""
Dashboard Data Layer Consolidation Module.

Reads output CSV tables generated across credit risk pipelines and consolidates
them into a single structured JSON file for consumption by the dashboard UI.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)


def _read_csv_safe(file_path: Path) -> Optional[pd.DataFrame]:
    """Reads a CSV file safely, logging a warning if missing or corrupt."""
    if not file_path.exists():
        logger.warning(f"File not found: {file_path}. Skipping this section.")
        return None
    try:
        return pd.read_csv(file_path)
    except Exception as exc:
        logger.warning(f"Failed to read {file_path}: {exc}. Skipping this section.")
        return None


def _build_portfolio_headline(tables_dir: Path) -> Optional[Dict[str, Any]]:
    """Assembles portfolio headline metrics from summary CSV files."""
    el_df = _read_csv_safe(tables_dir / "expected_loss_summary.csv")
    basel_df = _read_csv_safe(tables_dir / "basel_capital_summary.csv")
    ecl_df = _read_csv_safe(tables_dir / "ecl_summary.csv")
    cecl_df = _read_csv_safe(tables_dir / "ifrs9_vs_cecl.csv")

    # If all source files are missing, skip section
    if el_df is None and basel_df is None and ecl_df is None:
        return None

    headline: Dict[str, Any] = {}

    # Total loans & EAD from basel or expected loss or ecl
    total_loans = None
    total_ead = None
    total_el = None
    mean_pd = None
    mean_lgd = None
    el_rate = None

    if basel_df is not None:
        overall_basel = basel_df[basel_df["segment"] == "Overall"]
        if not overall_basel.empty:
            total_loans = int(overall_basel["count"].values[0])
            total_ead = float(overall_basel["total_ead"].values[0])

    if el_df is not None:
        overall_el = el_df[el_df["segment"] == "Overall"]
        if not overall_el.empty:
            if total_loans is None:
                total_loans = int(overall_el["count"].values[0])
            if total_ead is None:
                total_ead = float(overall_el["total_ead"].values[0])
            total_el = float(overall_el["total_el"].values[0])
            el_rate = float(overall_el["el_pct_ead"].values[0])
            mean_pd = float(overall_el["mean_pd"].values[0])
            mean_lgd = float(overall_el["mean_lgd"].values[0])

    # Capital metrics
    total_rwa_irb = None
    total_rwa_std = None
    avg_risk_weight = None

    if basel_df is not None:
        overall_basel = basel_df[basel_df["segment"] == "Overall"]
        if not overall_basel.empty:
            total_rwa_irb = float(overall_basel["irb_rwa"].values[0])
            total_rwa_std = float(overall_basel["std_rwa"].values[0])
            avg_risk_weight = float(overall_basel["irb_rw_pct"].values[0])

    # ECL metrics
    total_ecl_ifrs9 = None
    ecl_coverage = None
    if ecl_df is not None:
        tot_ecl_row = ecl_df[ecl_df["stage"] == "Total Portfolio"]
        if not tot_ecl_row.empty:
            total_ecl_ifrs9 = float(tot_ecl_row["total_ecl"].values[0])
            ecl_coverage = float(tot_ecl_row["coverage_ratio"].values[0]) * 100.0

    total_ecl_cecl = None
    if cecl_df is not None:
        cecl_row = cecl_df[cecl_df["accounting_framework"].str.contains("CECL", case=False, na=False)]
        if not cecl_row.empty:
            total_ecl_cecl = float(cecl_row["total_provision_usd"].values[0])

    headline = {
        "total_loans": total_loans,
        "total_ead": round(total_ead, 2) if total_ead is not None else None,
        "total_el": round(total_el, 2) if total_el is not None else None,
        "el_rate": round(el_rate, 2) if el_rate is not None else None,
        "total_rwa_irb": round(total_rwa_irb, 2) if total_rwa_irb is not None else None,
        "total_rwa_std": round(total_rwa_std, 2) if total_rwa_std is not None else None,
        "avg_risk_weight": round(avg_risk_weight, 2) if avg_risk_weight is not None else None,
        "total_ecl_ifrs9": round(total_ecl_ifrs9, 2) if total_ecl_ifrs9 is not None else None,
        "total_ecl_cecl": round(total_ecl_cecl, 2) if total_ecl_cecl is not None else None,
        "ecl_coverage": round(ecl_coverage, 2) if ecl_coverage is not None else None,
        "mean_pd": round(mean_pd, 4) if mean_pd is not None else None,
        "mean_lgd": round(mean_lgd, 4) if mean_lgd is not None else None,
    }
    return headline


def _build_rating_grades(tables_dir: Path) -> Optional[List[Dict[str, Any]]]:
    """Reads rating grades summary for Model B."""
    df = _read_csv_safe(tables_dir / "rating_grades_model_b.csv")
    if df is None:
        return None

    grades = []
    for _, row in df.iterrows():
        try:
            g_str = str(int(row["grade"]))
        except (ValueError, TypeError):
            g_str = str(row["grade"])
        grades.append({
            "grade": g_str,
            "score_range": f"{int(row['score_min'])}-{int(row['score_max'])}",
            "n_loans": int(row["n_loans"]),
            "default_rate": round(float(row["observed_default_rate"]), 4),
        })
    return grades


def _build_el_by_grade(tables_dir: Path) -> Optional[List[Dict[str, Any]]]:
    """Reads expected loss by rating grade."""
    df = _read_csv_safe(tables_dir / "expected_loss_summary.csv")
    if df is None:
        return None

    grade_df = df[df["segment"] == "By Grade"]
    if grade_df.empty:
        return None

    res = []
    for _, row in grade_df.iterrows():
        res.append({
            "grade": str(row["category"]),
            "count": int(row["count"]),
            "total_ead": round(float(row["total_ead"]), 2),
            "total_el": round(float(row["total_el"]), 2),
            "el_pct_ead": round(float(row["el_pct_ead"]), 2),
            "mean_pd": round(float(row["mean_pd"]), 4),
            "mean_lgd": round(float(row["mean_lgd"]), 4),
        })
    return res


def _build_capital_by_grade(tables_dir: Path) -> Optional[List[Dict[str, Any]]]:
    """Reads Basel capital metrics by rating grade."""
    df = _read_csv_safe(tables_dir / "basel_capital_summary.csv")
    if df is None:
        return None

    grade_df = df[df["segment"] == "By Grade"]
    if grade_df.empty:
        return None

    res = []
    for _, row in grade_df.iterrows():
        res.append({
            "grade": str(row["category"]),
            "ead": round(float(row["total_ead"]), 2),
            "irb_rwa": round(float(row["irb_rwa"]), 2),
            "risk_weight": round(float(row["irb_rw_pct"]), 2),
        })
    return res


def _build_staging(tables_dir: Path) -> Optional[List[Dict[str, Any]]]:
    """Reads IFRS 9 staging summary."""
    df = _read_csv_safe(tables_dir / "staging_summary.csv")
    if df is None:
        return None

    res = []
    for _, row in df.iterrows():
        res.append({
            "stage": str(row["stage"]),
            "n_loans": int(row["count"]),
            "ead": round(float(row["total_ead"]), 2),
            "mean_pd": round(float(row["mean_pd_12m"]), 4),
        })
    return res


def _build_ecl_by_stage(tables_dir: Path) -> Optional[List[Dict[str, Any]]]:
    """Reads ECL breakdown by stage."""
    df = _read_csv_safe(tables_dir / "ecl_summary.csv")
    if df is None:
        return None

    res = []
    for _, row in df.iterrows():
        res.append({
            "stage": str(row["stage"]),
            "count": int(row["count"]),
            "total_ead": round(float(row["total_ead"]), 2),
            "total_ecl": round(float(row["total_ecl"]), 2),
            "coverage_ratio": round(float(row["coverage_ratio"]), 4),
        })
    return res


def _build_framework_comparison(tables_dir: Path) -> Optional[List[Dict[str, Any]]]:
    """Reads Accounting Framework comparison (Basel EL vs IFRS 9 vs CECL)."""
    df = _read_csv_safe(tables_dir / "ifrs9_vs_cecl.csv")
    if df is None:
        return None

    res = []
    for _, row in df.iterrows():
        res.append({
            "framework": str(row["accounting_framework"]),
            "horizon_scope": str(row["horizon_scope"]),
            "total_provision_usd": round(float(row["total_provision_usd"]), 2),
            "coverage_pct_ead": round(float(row["coverage_pct_ead"]), 2),
            "notes": str(row["notes"]),
        })
    return res


def _build_vintage_curves(tables_dir: Path) -> Optional[List[Dict[str, Any]]]:
    """Reads cumulative default rates across MOBs by vintage year."""
    df = _read_csv_safe(tables_dir / "vintage_curves.csv")
    if df is None:
        return None

    res = []
    mob_cols = [c for c in df.columns if c.startswith("mob_")]
    for _, row in df.iterrows():
        item = {
            "vintage_year": int(row["vintage_year"]),
            "total_loans": int(row["total_loans"]),
        }
        for mob in mob_cols:
            item[mob] = round(float(row[mob]), 4)
        res.append(item)
    return res


def _build_vintage_maturity(tables_dir: Path) -> Optional[List[Dict[str, Any]]]:
    """Reads default rates at fixed MOB milestones (12, 18, 24)."""
    df = _read_csv_safe(tables_dir / "vintage_maturity_comparison.csv")
    if df is None:
        return None

    res = []
    for _, row in df.iterrows():
        res.append({
            "vintage_year": int(row["vintage_year"]),
            "total_loans": int(row["total_loans"]),
            "default_rate_mob_12_pct": round(float(row["default_rate_mob_12_pct"]), 2),
            "default_rate_mob_18_pct": round(float(row["default_rate_mob_18_pct"]), 2),
            "default_rate_mob_24_pct": round(float(row["default_rate_mob_24_pct"]), 2),
        })
    return res


def _build_transition_matrix(tables_dir: Path) -> Optional[List[Dict[str, Any]]]:
    """Reads rating grade transition probability matrix."""
    df = _read_csv_safe(tables_dir / "transition_matrix.csv")
    if df is None:
        return None

    res = []
    for _, row in df.iterrows():
        res.append({
            "grade": str(row["grade"]),
            "total_loans": int(row["total_loans"]),
            "fully_paid": round(float(row["Fully Paid"]), 4),
            "current": round(float(row["Current"]), 4),
            "late": round(float(row["Late"]), 4),
            "default": round(float(row["Default"]), 4),
        })
    return res


def _build_validation(tables_dir: Path) -> Optional[Dict[str, Any]]:
    """Extracts key validation metrics for Model B across train/test/oot samples."""
    df = _read_csv_safe(tables_dir / "validation_summary.csv")
    if df is None:
        return None

    model_b_df = df[df["model"] == "model_b"]
    if model_b_df.empty:
        return None

    metrics = {}
    for _, row in model_b_df.iterrows():
        sample = str(row["sample"])
        metrics[sample] = {
            "auc": round(float(row["auc"]), 4),
            "gini": round(float(row["gini"]), 4),
            "ks": round(float(row["ks"]), 4),
        }
    return metrics


def _build_lifetime_pd(tables_dir: Path) -> Optional[List[Dict[str, Any]]]:
    """Reads lifetime cumulative PD curve for selected milestone months."""
    df = _read_csv_safe(tables_dir / "lifetime_pd_term_structure.csv")
    if df is None:
        return None

    milestone_months = [1, 6, 12, 18, 24, 36, 48, 60]
    sub_df = df[df["month"].isin(milestone_months)]
    if sub_df.empty:
        # Fallback to all or first 12 months if milestones not exact
        sub_df = df.head(12)

    res = []
    for _, row in sub_df.iterrows():
        res.append({
            "month": int(row["month"]),
            "n_at_risk": int(row["n_at_risk"]),
            "n_defaults": int(row["n_defaults"]),
            "hazard": round(float(row["hazard"]), 6),
            "survival": round(float(row["survival"]), 4),
            "cumulative_pd": round(float(row["cumulative_pd"]), 4),
        })
    return res


def build_dashboard_json(
    tables_dir: Path = Path("outputs/tables"),
    output_path: Path = Path("outputs/reports/dashboard_data.json"),
) -> Dict[str, Any]:
    """Consolidates output CSV tables into a single dashboard JSON dataset.

    Args:
        tables_dir: Path to directory containing source CSV tables.
        output_path: Destination path for consolidated JSON file.

    Returns:
        Dict representing the structured dashboard data.
    """
    logger.info(f"Assembling dashboard data from {tables_dir}")

    dashboard_data: Dict[str, Any] = {
        "portfolio_headline": _build_portfolio_headline(tables_dir),
        "rating_grades": _build_rating_grades(tables_dir),
        "el_by_grade": _build_el_by_grade(tables_dir),
        "capital_by_grade": _build_capital_by_grade(tables_dir),
        "staging": _build_staging(tables_dir),
        "ecl_by_stage": _build_ecl_by_stage(tables_dir),
        "framework_comparison": _build_framework_comparison(tables_dir),
        "vintage_curves": _build_vintage_curves(tables_dir),
        "vintage_maturity": _build_vintage_maturity(tables_dir),
        "transition_matrix": _build_transition_matrix(tables_dir),
        "validation": _build_validation(tables_dir),
        "lifetime_pd": _build_lifetime_pd(tables_dir),
    }

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(dashboard_data, f, indent=2)

    logger.info(f"Dashboard data successfully saved to {output_path}")
    return dashboard_data


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    build_dashboard_json()
