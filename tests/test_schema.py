"""
test_schema.py
--------------
Unit tests for schema validation and anti-leakage guardrails in src/creditrisk/data/schema.py.
"""

import pandas as pd
import pytest
from creditrisk.data.schema import (
    assert_no_leakage,
    get_pd_eligible_columns,
    load_variable_config,
    validate_schema_coverage,
)


def test_assert_no_leakage_raises_on_leakage_column():
    """
    Verifies that assert_no_leakage raises ValueError when an outcome column
    such as 'recoveries' is passed in the feature list.
    """
    feature_list_with_leakage = ["loan_amnt", "int_rate", "recoveries"]

    with pytest.raises(ValueError, match="Target leakage violation detected"):
        assert_no_leakage(feature_list_with_leakage)


def test_assert_no_leakage_passes_on_clean_list():
    """
    Verifies that assert_no_leakage executes without raising an exception when
    only valid application-time features are provided.
    """
    clean_pd_features = ["loan_amnt", "int_rate", "grade", "annual_inc"]

    # Should complete cleanly without raising any ValueError
    assert_no_leakage(clean_pd_features)


def test_validate_schema_coverage_catches_unclassified_column():
    """
    Verifies that validate_schema_coverage raises ValueError when a DataFrame
    contains an unknown or unclassified column.
    """
    # Obtain all valid classified columns from variables.yaml
    config = load_variable_config()
    all_classified_cols = []
    for category_cols in config.values():
        all_classified_cols.extend(category_cols)

    # Build a DataFrame with all valid columns PLUS one unclassified column
    test_columns = all_classified_cols + ["unapproved_secret_feature"]
    dummy_df = pd.DataFrame(columns=test_columns)

    with pytest.raises(ValueError, match="Unclassified column"):
        validate_schema_coverage(dummy_df)
