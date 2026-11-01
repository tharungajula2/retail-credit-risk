"""Synthetic-only boundaries for the reporting-date evidence gate."""

from __future__ import annotations

from copy import deepcopy
from datetime import date
from decimal import Decimal
import unittest

from creditrisk.regulatory.reporting_input_gate import validate_basel_input, validate_ecl_input


def estimate(value: str, basis: str, **extra: object) -> dict[str, object]:
    return {"loan_id": "synthetic-loan-1", "value": value, "basis": basis,
            "observed_at": "2024-12-30T08:00:00+00:00",
            "available_at": "2024-12-30T09:00:00+00:00",
            "source": "synthetic-model-register", **extra}


def ead(basis: str) -> dict[str, object]:
    return {"loan_id": "synthetic-loan-1", "amount": "1000.00", "currency": "USD", "unit": "currency_units",
            "basis": basis, "observed_at": "2024-12-31T08:00:00+00:00",
            "available_at": "2024-12-31T09:00:00+00:00",
            "source": "synthetic-exposure-forecast"}


def common(basis: str) -> dict[str, object]:
    return {"loan_id": "synthetic-loan-1", "reporting_date": "2024-12-31",
            "reporting_at": "2024-12-31T18:00:00+00:00",
            "status_observed_at": "2024-12-31T12:00:00+00:00",
            "status_available_at": "2024-12-31T12:30:00+00:00",
            "status_source": "synthetic-account-panel", "defaulted": False,
            "currency": "USD", "ead": ead(basis)}


def ecl(stage: int = 1) -> dict[str, object]:
    row = common("prospective_default_exposure")
    row.update({"stage": stage, "stage_assessed_at": "2024-12-31T13:00:00+00:00",
                "stage_available_at": "2024-12-31T13:30:00+00:00",
                "stage_source": "synthetic-stage-assessment",
                "initial_risk_observed_at": "2023-01-01T10:00:00+00:00",
                "initial_risk_available_at": "2023-01-01T11:00:00+00:00",
                "current_risk_observed_at": "2024-12-31T11:00:00+00:00",
                "current_risk_available_at": "2024-12-31T11:30:00+00:00",
                "risk_comparison_source": "synthetic-risk-assessment",
                "expected_life_end": "2027-12-31",
                "pd": estimate("0.04", "forward_12m" if stage == 1 else "forward_lifetime",
                               window_start="2024-12-31",
                               window_end="2025-12-31" if stage == 1 else "2027-12-31"),
                "lgd": estimate("0.4", "prospective_economic"),
                "effective_interest_rate": "0.08",
                "eir_observed_at": "2023-01-01T10:00:00+00:00",
                "eir_available_at": "2023-01-01T11:00:00+00:00",
                "eir_source": "synthetic-contract",
                "scenario_observed_at": "2024-12-30T08:00:00+00:00",
                "scenario_available_at": "2024-12-30T09:00:00+00:00",
                "scenario_source": "synthetic-scenario-set"})
    return row


def basel(approach: str = "irb_other_retail") -> dict[str, object]:
    irb = approach == "irb_other_retail"
    row = common("regulatory_default_exposure" if irb else "regulatory_exposure")
    row.update({"approach": approach, "jurisdiction": "synthetic-jurisdiction",
                "rulebook_version": "synthetic-2024", "rulebook_effective_on": "2024-01-01",
                "rulebook_available_at": "2024-01-01T00:00:00+00:00",
                "rulebook_source": "synthetic-rulebook",
                "retail_eligibility_observed_at": "2024-12-31T12:00:00+00:00",
                "retail_eligibility_available_at": "2024-12-31T12:30:00+00:00",
                "retail_eligibility_source": "synthetic-eligibility-review",
                "pd": estimate("0.04", "regulatory_one_year", window_start="2024-12-31",
                               window_end="2025-12-31") if irb else None,
                "lgd": estimate("0.4", "regulatory_downturn") if irb else None,
                "irb_authorisation_available_at": "2024-01-01T00:00:00+00:00" if irb else None,
                "irb_authorisation_source": "synthetic-authorisation" if irb else None})
    return row


class ReportingInputGateTests(unittest.TestCase):
    def test_valid_stage_one_and_two(self):
        for stage, horizon in ((1, "forward_12m"), (2, "forward_lifetime")):
            with self.subTest(stage=stage):
                result = validate_ecl_input(ecl(stage))
                self.assertEqual(result.pd_horizon, horizon)
                self.assertEqual(result.exposure, Decimal("1000.00"))
                self.assertEqual(result.reporting_date, date(2024, 12, 31))

    def test_short_maturity_truncates_stage_one_pd_window(self):
        row = ecl()
        row["expected_life_end"] = "2025-06-30"
        row["pd"]["window_end"] = "2025-06-30"
        validate_ecl_input(row)

    def test_valid_irb_and_standardised_are_distinct(self):
        self.assertEqual(validate_basel_input(basel()).pd_horizon, "regulatory_one_year")
        self.assertIsNone(validate_basel_input(basel("standardised_retail")).pd_horizon)

    def test_missing_or_unexpected_evidence_fails_closed(self):
        row = ecl()
        del row["eir_source"]
        with self.assertRaisesRegex(ValueError, "missing=.*eir_source"):
            validate_ecl_input(row)
        row = ecl()
        row["legacy_fallback"] = "0.93"
        with self.assertRaisesRegex(ValueError, "unexpected=.*legacy_fallback"):
            validate_ecl_input(row)

    def test_future_and_out_of_order_evidence_is_rejected(self):
        mutations = (
            ("pd", "available_at", "2025-01-01T00:00:00+00:00", "unavailable"),
            ("lgd", "observed_at", "2025-01-01T00:00:00+00:00", "unavailable"),
            ("ead", "available_at", "2025-01-01T00:00:00+00:00", "unavailable"),
            (None, "scenario_available_at", "2025-01-01T00:00:00+00:00", "unavailable"),
            (None, "stage_assessed_at", "2025-01-01T00:00:00+00:00", "unavailable"),
            (None, "status_available_at", "2025-01-01T00:00:00+00:00", "unavailable"),
            (None, "current_risk_available_at", "2025-01-01T00:00:00+00:00", "unavailable"),
            (None, "initial_risk_observed_at", "2025-01-01T00:00:00+00:00", "unavailable"),
            ("pd", "available_at", "2024-12-29T00:00:00+00:00", "precedes"),
        )
        for section, field, value, message in mutations:
            with self.subTest(section=section, field=field):
                row = ecl()
                target = row if section is None else row[section]
                target[field] = value
                with self.assertRaisesRegex(ValueError, message):
                    validate_ecl_input(row)

    def test_reporting_status_must_be_current_and_explicit(self):
        row = ecl()
        row["status_observed_at"] = "2024-12-30T12:00:00+00:00"
        with self.assertRaisesRegex(ValueError, "on reporting_date"):
            validate_ecl_input(row)
        row = ecl()
        row["defaulted"] = None
        with self.assertRaisesRegex(ValueError, "explicit reporting-date boolean"):
            validate_ecl_input(row)
        row = ecl()
        row["status_available_at"] = "2024-12-31T14:00:00+00:00"
        with self.assertRaisesRegex(ValueError, "must follow available status"):
            validate_ecl_input(row)

    def test_parameter_loan_ids_must_match(self):
        for section in ("pd", "lgd", "ead"):
            with self.subTest(section=section):
                row = ecl()
                row[section]["loan_id"] = "another-loan"
                with self.assertRaisesRegex(ValueError, f"{section}.loan_id must match"):
                    validate_ecl_input(row)

    def test_pd_horizon_and_measurement_dates_are_checked(self):
        for field, value, message in (("basis", "forward_lifetime", "pd.basis"),
                                      ("window_start", "2024-01-01", "measurement window"),
                                      ("window_end", "2026-01-01", "measurement window")):
            with self.subTest(field=field):
                row = ecl()
                row["pd"][field] = value
                with self.assertRaisesRegex(ValueError, message):
                    validate_ecl_input(row)

    def test_lgd_ead_prospective_basis_currency_and_units(self):
        for section, field, value, message in (
            ("lgd", "basis", "realized_workout", "lgd.basis"),
            ("ead", "basis", "realized_default_balance", "ead.basis"),
            ("ead", "currency", "EUR", "currency or unit"),
            ("ead", "unit", "thousands", "currency or unit"),
            ("ead", "amount", "-1", "ead.amount"),
        ):
            with self.subTest(section=section, field=field):
                row = ecl()
                row[section][field] = value
                with self.assertRaisesRegex(ValueError, message):
                    validate_ecl_input(row)

    def test_stage_three_and_defaulted_capital_are_unsupported(self):
        row = ecl()
        row["stage"] = 3
        row["defaulted"] = True
        with self.assertRaisesRegex(ValueError, "Stage 1/2 only"):
            validate_ecl_input(row)
        row = basel()
        row["defaulted"] = True
        with self.assertRaisesRegex(ValueError, "separate regulatory treatment"):
            validate_basel_input(row)

    def test_regulatory_policy_and_approach_evidence(self):
        for section, field, value, message in (
            (None, "rulebook_effective_on", "2025-01-01", "not effective"),
            (None, "rulebook_available_at", "2025-01-01T00:00:00+00:00", "unavailable"),
            (None, "retail_eligibility_available_at", "2025-01-01T00:00:00+00:00", "unavailable"),
            (None, "irb_authorisation_source", None, "irb_authorisation_source"),
            ("lgd", "basis", "prospective_economic", "lgd.basis"),
            ("pd", "window_end", "2026-12-31", "measurement window"),
        ):
            with self.subTest(field=field):
                row = basel()
                target = row if section is None else row[section]
                target[field] = value
                with self.assertRaisesRegex(ValueError, message):
                    validate_basel_input(row)
        row = basel("standardised_retail")
        row["pd"] = deepcopy(basel()["pd"])
        with self.assertRaisesRegex(ValueError, "must not be supplied IRB"):
            validate_basel_input(row)

    def test_invalid_numeric_or_timezone_values(self):
        for section, field, value, message in (
            ("pd", "value", "1.01", "pd.value"),
            ("lgd", "value", "NaN", "lgd.value"),
            ("ead", "amount", 1.5, "ead.amount"),
            ("pd", "observed_at", "2024-12-30T08:00:00", "timezone-aware"),
        ):
            with self.subTest(field=field):
                row = ecl()
                row[section][field] = value
                with self.assertRaisesRegex(ValueError, message):
                    validate_ecl_input(row)


if __name__ == "__main__":
    unittest.main()
