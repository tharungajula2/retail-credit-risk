"""
Tests for dashboard data consolidation module.
"""

import json
from pathlib import Path

import pytest

from creditrisk.reporting.dashboard_data import build_dashboard_json


def test_build_dashboard_json(tmp_path: Path):
    # Set output destination within tmp_path
    output_file = tmp_path / "dashboard_data.json"

    # Execute build_dashboard_json using real outputs/tables directory if present
    tables_dir = Path("outputs/tables")
    if not tables_dir.exists():
        pytest.skip("outputs/tables directory does not exist")

    data = build_dashboard_json(tables_dir=tables_dir, output_path=output_file)

    # 1. Verify JSON file was created and is non-empty
    assert output_file.exists()
    with open(output_file, "r", encoding="utf-8") as f:
        loaded_data = json.load(f)

    # 2. Check all expected top-level keys exist
    expected_keys = [
        "portfolio_headline",
        "rating_grades",
        "el_by_grade",
        "capital_by_grade",
        "staging",
        "ecl_by_stage",
        "framework_comparison",
        "vintage_curves",
        "vintage_maturity",
        "transition_matrix",
        "validation",
        "lifetime_pd",
    ]
    for key in expected_keys:
        assert key in loaded_data, f"Missing key in JSON: {key}"

    # 3. Check headline numbers are non-null
    headline = loaded_data["portfolio_headline"]
    assert headline is not None, "portfolio_headline should not be None"
    assert headline["total_loans"] is not None
    assert headline["total_ead"] is not None
    assert headline["total_rwa_irb"] is not None
    assert headline["total_ecl_ifrs9"] is not None

    # 4. Check grade tables have 7-8 rows
    rating_grades = loaded_data["rating_grades"]
    assert rating_grades is not None
    assert 7 <= len(rating_grades) <= 8, f"Expected 7-8 rows in rating_grades, got {len(rating_grades)}"

    capital_by_grade = loaded_data["capital_by_grade"]
    assert capital_by_grade is not None
    assert 7 <= len(capital_by_grade) <= 8, f"Expected 7-8 rows in capital_by_grade, got {len(capital_by_grade)}"


def test_build_dashboard_json_graceful_missing_files(tmp_path: Path):
    empty_tables_dir = tmp_path / "empty_tables"
    empty_tables_dir.mkdir()
    output_file = tmp_path / "dashboard_data_empty.json"

    data = build_dashboard_json(tables_dir=empty_tables_dir, output_path=output_file)

    # Should complete without throwing exceptions and return dict with None for missing sections
    assert output_file.exists()
    assert data["portfolio_headline"] is None
    assert data["rating_grades"] is None
