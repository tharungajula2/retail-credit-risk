"""Synthetic evidence tests for the separate PD foundation module."""

import sys
import unittest
from datetime import date
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from creditrisk.data.pd_foundation import (  # noqa: E402
    Cohort,
    PDPolicy,
    add_calendar_months,
    build_pd_12m_labels,
    validate_dataset_schema,
)


POLICY = PDPolicy(
    as_of_date=date(2016, 1, 31),
    cohorts=(
        Cohort("development", date(2007, 1, 1), date(2014, 1, 1)),
        Cohort("oot", date(2014, 1, 1), date(2015, 1, 1)),
    ),
    approved_features=frozenset({"annual_inc"}),
)


def loan(**changes):
    row = {
        "loan_id": "synthetic-1",
        "origination_date": "2014-01-15",
        "decision_at": "2014-01-14T17:00:00+00:00",
        "observed_through": "2015-01-15",
        "event_history_complete": True,
        "default_event_date": None,
        "default_event_type": None,
        "default_event_source": None,
        "observed_status": "Current",
    }
    row.update(changes)
    return row


class PDFoundationTests(unittest.TestCase):
    def test_default_inside_and_on_twelve_month_anniversary(self):
        rows = [
            loan(loan_id="inside", default_event_date="2014-06-01",
                 default_event_type="90_plus_dpd", default_event_source="synthetic monthly panel"),
            loan(loan_id="anniversary", default_event_date="2015-01-15",
                 default_event_type="charge_off", default_event_source="synthetic event ledger"),
        ]
        labels = build_pd_12m_labels(rows, POLICY)
        self.assertEqual([item.default_12m for item in labels], [1, 1])
        self.assertEqual(labels[0].performance_end, date(2015, 1, 15))

    def test_default_after_window_is_nondefault_only_with_complete_history(self):
        row = loan(observed_through="2015-02-01", default_event_date="2015-01-16",
                   default_event_type="charge_off", default_event_source="synthetic event ledger")
        label = build_pd_12m_labels([row], POLICY)[0]
        self.assertEqual((label.default_12m, label.label_state), (0, "observed_nondefault"))
        row["event_history_complete"] = False
        self.assertIsNone(build_pd_12m_labels([row], POLICY)[0].default_12m)

    def test_unresolved_or_incomplete_followup_is_not_a_zero(self):
        short = loan(observed_through="2014-12-31")
        incomplete = loan(event_history_complete=False)
        for row in (short, incomplete):
            with self.subTest(row=row):
                label = build_pd_12m_labels([row], POLICY)[0]
                self.assertIsNone(label.default_12m)
                self.assertEqual(label.label_state, "censored_or_incomplete")

    def test_undated_default_status_cannot_confirm_twelve_month_event(self):
        label = build_pd_12m_labels([loan(observed_status="Charged Off")], POLICY)[0]
        self.assertIsNone(label.default_12m)
        self.assertEqual(label.label_state, "undated_default")

    def test_chronological_cohort_boundaries_and_no_overlap(self):
        rows = [
            loan(loan_id="last-dev", origination_date="2013-12-31",
                 decision_at="2013-12-30T17:00:00+00:00"),
            loan(loan_id="first-oot", origination_date="2014-01-01",
                 decision_at="2013-12-31T17:00:00+00:00"),
            loan(loan_id="outside", origination_date="2015-01-01",
                 decision_at="2014-12-31T17:00:00+00:00"),
        ]
        self.assertEqual([item.cohort for item in build_pd_12m_labels(rows, POLICY)],
                         ["development", "oot", None])
        with self.assertRaisesRegex(ValueError, "overlap"):
            PDPolicy(date(2016, 1, 31), (
                Cohort("a", date(2013, 1, 1), date(2014, 2, 1)),
                Cohort("b", date(2014, 1, 1), date(2015, 1, 1)),
            ))

    def test_calendar_month_window_clamps_leap_day(self):
        self.assertEqual(add_calendar_months(date(2024, 2, 29), 12), date(2025, 2, 28))
        self.assertEqual(add_calendar_months(date(2024, 1, 31), 1), date(2024, 2, 29))

    def test_future_default_event_and_observation_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "future default event"):
            build_pd_12m_labels([loan(default_event_date="2015-01-16",
                                     default_event_type="charge_off",
                                     default_event_source="synthetic ledger")], POLICY)
        with self.assertRaisesRegex(ValueError, "future or inconsistent"):
            build_pd_12m_labels([loan(observed_through="2016-02-01")], POLICY)

    def test_feature_timing_and_outcome_feature_guard(self):
        valid = loan(features={"annual_inc": 50000},
                     feature_observed_at={"annual_inc": "2014-01-14T16:00:00+00:00"})
        self.assertEqual(build_pd_12m_labels([valid], POLICY, ["annual_inc"])[0].default_12m, 0)
        valid["feature_observed_at"]["annual_inc"] = "2014-01-14T18:00:00+00:00"
        with self.assertRaisesRegex(ValueError, "future-data leakage"):
            build_pd_12m_labels([valid], POLICY, ["annual_inc"])
        with self.assertRaisesRegex(ValueError, "prohibited"):
            build_pd_12m_labels([valid], POLICY, ["loan_status"])
        with self.assertRaisesRegex(ValueError, "not approved"):
            build_pd_12m_labels([valid], POLICY, ["grade"])

    def test_schema_requires_dated_supported_event_and_unique_ids(self):
        missing = loan()
        del missing["observed_through"]
        with self.assertRaisesRegex(ValueError, "missing required fields"):
            validate_dataset_schema([missing], POLICY)
        with self.assertRaisesRegex(ValueError, "duplicate loan_id"):
            validate_dataset_schema([loan(), loan()], POLICY)
        with self.assertRaisesRegex(ValueError, "needs date, type and source"):
            validate_dataset_schema([loan(default_event_date="2014-05-01")], POLICY)
        with self.assertRaisesRegex(ValueError, "unqualified default event type"):
            validate_dataset_schema([loan(default_event_date="2014-05-01",
                                          default_event_type="fully_paid",
                                          default_event_source="synthetic ledger")], POLICY)
        with self.assertRaisesRegex(ValueError, "YYYY-MM-DD"):
            validate_dataset_schema([loan(origination_date="Jan-14")], POLICY)


if __name__ == "__main__":
    unittest.main()
