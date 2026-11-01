"""Synthetic boundary tests for dated LGD/EAD evidence only."""

from __future__ import annotations

from decimal import Decimal
import unittest

from creditrisk.data.lgd_ead_foundation import validate_ead_record, validate_lgd_record


def lgd_record():
    return {
        "loan_id": "synthetic-L1",
        "decision_at": "2024-01-01T09:00:00+00:00",
        "default_event_date": "2024-06-01",
        "default_event_type": "charge_off",
        "default_event_source": "synthetic-event-ledger",
        "earliest_default_confirmed": True,
        "exposure_at_default": "1000.00",
        "recovery_cashflows": [{"date": "2024-08-01", "amount": "200.00"}],
        "workout_cost_cashflows": [{"date": "2024-09-01", "amount": "10.00"}],
        "discount_rate_annual": "0.10",
        "discount_rate_as_of": "2024-06-01",
        "discount_rate_source": "synthetic-rate-policy",
        "observed_through": "2025-01-01",
        "as_of_date": "2025-01-01",
        "workout_complete": True,
        "workout_closed_on": "2024-12-01",
        "features": {"grade": "B"},
        "feature_observed_at": {"grade": "2024-01-01T08:00:00+00:00"},
    }


def ead_record(product="revolving"):
    return {
        "loan_id": "synthetic-E1",
        "product_type": product,
        "observation_at": "2024-01-01T08:00:00+00:00",
        "decision_at": "2024-01-01T09:00:00+00:00",
        "default_at": "2024-06-01T09:00:00+00:00",
        "default_event_type": "charge_off",
        "default_event_source": "synthetic-event-ledger",
        "earliest_default_confirmed": True,
        "as_of_at": "2024-12-01T09:00:00+00:00",
        "drawn_at_observation": "400.00",
        "undrawn_at_observation": "600.00" if product == "revolving" else "0.00",
        "credit_limit_at_observation": "1000.00" if product == "revolving" else None,
        "drawn_at_default": "640.00",
        "credit_limit_at_default": "1000.00" if product == "revolving" else None,
        "features": {"grade": "B"},
        "feature_observed_at": {"grade": "2024-01-01T08:00:00+00:00"},
    }


class LGDContractTests(unittest.TestCase):
    def test_closed_workout_is_eligible_with_dated_evidence(self):
        result = validate_lgd_record(lgd_record(), {"grade"})
        self.assertTrue(result.label_eligible)
        self.assertEqual(result.exposure_at_default, Decimal("1000.00"))
        self.assertEqual(result.recovery_cashflows[0].amount, Decimal("200.00"))

    def test_complete_zero_recovery_requires_explicit_empty_ledgers(self):
        row = lgd_record()
        row["recovery_cashflows"] = []
        row["workout_cost_cashflows"] = []
        self.assertTrue(validate_lgd_record(row, {"grade"}).label_eligible)

    def test_open_workout_is_valid_but_not_label_eligible(self):
        row = lgd_record()
        row["workout_complete"] = False
        row["workout_closed_on"] = None
        self.assertFalse(validate_lgd_record(row, {"grade"}).label_eligible)

    def test_missing_and_unexpected_schema_are_rejected(self):
        row = lgd_record()
        del row["recovery_cashflows"]
        with self.assertRaisesRegex(ValueError, "missing=.*recovery_cashflows"):
            validate_lgd_record(row, {"grade"})
        row = lgd_record()
        row["recoveries"] = 200
        with self.assertRaisesRegex(ValueError, "unexpected=.*recoveries"):
            validate_lgd_record(row, {"grade"})

    def test_missing_recovery_ledger_is_not_assumed_zero(self):
        row = lgd_record()
        row["recovery_cashflows"] = None
        with self.assertRaisesRegex(ValueError, "explicit list"):
            validate_lgd_record(row, {"grade"})

    def test_cashflows_outside_observation_window_are_rejected(self):
        for field, day in (("recovery_cashflows", "2024-05-31"),
                           ("workout_cost_cashflows", "2025-01-02")):
            with self.subTest(field=field, day=day):
                row = lgd_record()
                row[field][0]["date"] = day
                with self.assertRaisesRegex(ValueError, "outside default-to-observation"):
                    validate_lgd_record(row, {"grade"})

    def test_incomplete_or_contradictory_close_is_rejected(self):
        row = lgd_record()
        row["workout_complete"] = False
        with self.assertRaisesRegex(ValueError, "incomplete workout"):
            validate_lgd_record(row, {"grade"})
        row = lgd_record()
        row["workout_closed_on"] = "2024-07-01"
        with self.assertRaisesRegex(ValueError, "follow cashflows"):
            validate_lgd_record(row, {"grade"})

    def test_bad_default_or_exposure_is_rejected(self):
        for field, value in (("default_event_date", "2025-02-01"),
                             ("exposure_at_default", "0"),
                             ("exposure_at_default", "-1"),
                             ("exposure_at_default", None)):
            with self.subTest(field=field, value=value):
                row = lgd_record()
                row[field] = value
                with self.assertRaises(ValueError):
                    validate_lgd_record(row, {"grade"})

    def test_unconfirmed_earliest_default_is_rejected(self):
        row = lgd_record()
        row["earliest_default_confirmed"] = False
        with self.assertRaisesRegex(ValueError, "earliest_default_confirmed"):
            validate_lgd_record(row, {"grade"})

    def test_invalid_cashflow_and_rate_are_rejected(self):
        for field, value in (("recovery_cashflows", [{"date": "2024-08-01", "amount": "-1"}]),
                             ("discount_rate_annual", None),
                             ("discount_rate_annual", "NaN"),
                             ("discount_rate_source", "")):
            with self.subTest(field=field):
                row = lgd_record()
                row[field] = value
                with self.assertRaises(ValueError):
                    validate_lgd_record(row, {"grade"})

    def test_discount_rate_cannot_come_from_after_default(self):
        row = lgd_record()
        row["discount_rate_as_of"] = "2024-06-02"
        with self.assertRaisesRegex(ValueError, "cannot follow default_event_date"):
            validate_lgd_record(row, {"grade"})

    def test_over_recovery_requires_reconciliation(self):
        row = lgd_record()
        row["recovery_cashflows"][0]["amount"] = "1000.01"
        with self.assertRaisesRegex(ValueError, "gross recoveries exceed"):
            validate_lgd_record(row, {"grade"})

    def test_future_and_outcome_features_are_rejected(self):
        row = lgd_record()
        row["feature_observed_at"]["grade"] = "2024-01-02T00:00:00+00:00"
        with self.assertRaisesRegex(ValueError, "after decision_at"):
            validate_lgd_record(row, {"grade"})
        row = lgd_record()
        row["features"]["recoveries"] = "200"
        row["feature_observed_at"]["recoveries"] = row["decision_at"]
        with self.assertRaisesRegex(ValueError, "forbidden=.*recoveries"):
            validate_lgd_record(row, {"grade", "recoveries"})


class EADContractTests(unittest.TestCase):
    def test_revolving_ccf_uses_stable_limit_and_dated_balances(self):
        result = validate_ead_record(ead_record(), {"grade"})
        self.assertEqual(result.realized_ccf, Decimal("0.4"))
        self.assertIsNone(result.ccf_ineligible_reason)
        self.assertEqual(result.drawn_at_default, Decimal("640.00"))

    def test_term_loan_has_no_ccf(self):
        result = validate_ead_record(ead_record("term"), {"grade"})
        self.assertIsNone(result.realized_ccf)
        self.assertEqual(result.ccf_ineligible_reason, "term_loan_no_ccf")

    def test_zero_undrawn_and_limit_change_are_ineligible_for_ccf(self):
        row = ead_record()
        row["drawn_at_observation"] = "1000"
        row["undrawn_at_observation"] = "0"
        row["drawn_at_default"] = "900"
        result = validate_ead_record(row, {"grade"})
        self.assertEqual(result.ccf_ineligible_reason, "no_undrawn_commitment")
        row = ead_record()
        row["credit_limit_at_default"] = "1200"
        self.assertEqual(validate_ead_record(row, {"grade"}).ccf_ineligible_reason, "limit_changed")

    def test_net_repayment_is_not_clipped_to_zero_ccf(self):
        row = ead_record()
        row["drawn_at_default"] = "300"
        result = validate_ead_record(row, {"grade"})
        self.assertIsNone(result.realized_ccf)
        self.assertEqual(result.ccf_ineligible_reason, "net_repayment_before_default")

    def test_missing_negative_and_inconsistent_exposure_are_rejected(self):
        for field, value in (("drawn_at_default", None),
                             ("drawn_at_default", "-1"),
                             ("undrawn_at_observation", "-1"),
                             ("drawn_at_observation", "1100"),
                             ("undrawn_at_observation", "500"),
                             ("credit_limit_at_default", "500")):
            with self.subTest(field=field, value=value):
                row = ead_record()
                row[field] = value
                with self.assertRaises(ValueError):
                    validate_ead_record(row, {"grade"})

    def test_term_loan_cannot_claim_undrawn_commitment(self):
        row = ead_record("term")
        row["undrawn_at_observation"] = "100"
        with self.assertRaisesRegex(ValueError, "term loan requires zero undrawn"):
            validate_ead_record(row, {"grade"})

    def test_reversed_or_future_exposure_dates_are_rejected(self):
        for field, value in (("observation_at", "2024-07-01T00:00:00+00:00"),
                             ("default_at", "2024-01-01T08:30:00+00:00"),
                             ("as_of_at", "2024-01-01T08:00:00+00:00")):
            with self.subTest(field=field):
                row = ead_record()
                row[field] = value
                with self.assertRaisesRegex(ValueError, "require observation_at"):
                    validate_ead_record(row, {"grade"})

    def test_ead_requires_confirmed_default_event(self):
        row = ead_record()
        row["earliest_default_confirmed"] = False
        with self.assertRaisesRegex(ValueError, "earliest_default_confirmed"):
            validate_ead_record(row, {"grade"})

    def test_future_and_default_features_are_rejected(self):
        row = ead_record()
        row["feature_observed_at"]["grade"] = row["default_at"]
        with self.assertRaisesRegex(ValueError, "after decision_at"):
            validate_ead_record(row, {"grade"})
        row = ead_record()
        row["features"]["drawn_at_default"] = "640"
        row["feature_observed_at"]["drawn_at_default"] = row["decision_at"]
        with self.assertRaisesRegex(ValueError, "forbidden=.*drawn_at_default"):
            validate_ead_record(row, {"grade", "drawn_at_default"})
        row = ead_record()
        row["features"]["credit_limit_at_default"] = "1000"
        row["feature_observed_at"]["credit_limit_at_default"] = row["decision_at"]
        with self.assertRaisesRegex(ValueError, "forbidden=.*credit_limit_at_default"):
            validate_ead_record(row, {"grade", "credit_limit_at_default"})

    def test_schema_requires_explicit_limits_and_rejects_extra_snapshot_fields(self):
        row = ead_record()
        del row["credit_limit_at_default"]
        with self.assertRaisesRegex(ValueError, "missing=.*credit_limit_at_default"):
            validate_ead_record(row, {"grade"})
        row = ead_record()
        row["out_prncp"] = "640"
        with self.assertRaisesRegex(ValueError, "unexpected=.*out_prncp"):
            validate_ead_record(row, {"grade"})


if __name__ == "__main__":
    unittest.main()
