"""Reporting-date evidence checks for illustrative ECL and capital workflows.

This is an admission contract, not an ECL or regulatory-capital calculator.
Sources and policy assertions must be authenticated by a future data adapter.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Mapping

from creditrisk.data.pd_foundation import add_calendar_months


_COMMON = {"loan_id", "reporting_date", "reporting_at", "status_observed_at", "status_available_at",
           "status_source", "defaulted", "currency", "ead"}
_ECL = _COMMON | {"stage", "stage_assessed_at", "stage_available_at", "stage_source", "expected_life_end",
                  "initial_risk_observed_at", "initial_risk_available_at",
                  "current_risk_observed_at", "current_risk_available_at", "risk_comparison_source",
                  "pd", "lgd", "effective_interest_rate", "eir_observed_at", "eir_available_at",
                  "eir_source", "scenario_observed_at", "scenario_available_at", "scenario_source"}
_BASEL = _COMMON | {"approach", "jurisdiction", "rulebook_version",
                    "rulebook_effective_on", "rulebook_available_at", "rulebook_source",
                    "retail_eligibility_observed_at", "retail_eligibility_available_at",
                    "retail_eligibility_source",
                    "pd", "lgd", "irb_authorisation_available_at", "irb_authorisation_source"}
_PD = {"loan_id", "value", "basis", "window_start", "window_end", "observed_at",
       "available_at", "source"}
_LGD = {"loan_id", "value", "basis", "observed_at", "available_at", "source"}
_EAD = {"loan_id", "amount", "currency", "unit", "basis", "observed_at", "available_at",
        "source"}


@dataclass(frozen=True)
class ValidatedReportingInput:
    """Evidence admitted for a named *illustrative* calculation pathway only."""

    loan_id: str
    purpose: str
    reporting_date: date
    currency: str
    exposure: Decimal
    pd_horizon: str | None


def _schema(value: object, fields: set[str], name: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise ValueError(f"{name} must be a mapping")
    missing = fields - value.keys()
    unexpected = value.keys() - fields
    if missing or unexpected:
        raise ValueError(f"{name} schema: missing={sorted(missing)}, unexpected={sorted(map(str, unexpected))}")
    return value


def _name(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} needs a non-empty evidence source or identifier")
    return value.strip()


def _day(value: object, field: str) -> date:
    if isinstance(value, datetime):
        raise ValueError(f"{field} needs a date, not a timestamp")
    if isinstance(value, str):
        try:
            parsed = date.fromisoformat(value)
            if parsed.isoformat() == value:
                return parsed
        except ValueError:
            pass
    elif isinstance(value, date):
        return value
    raise ValueError(f"{field} needs YYYY-MM-DD or a date")


def _instant(value: object, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value) if isinstance(value, str) else value
    except ValueError as exc:
        raise ValueError(f"{field} needs a timezone-aware ISO 8601 timestamp") from exc
    if not isinstance(parsed, datetime) or parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field} needs a timezone-aware ISO 8601 timestamp")
    return parsed


def _number(value: object, field: str, *, maximum: Decimal | None = None) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (str, int, Decimal)):
        raise ValueError(f"{field} needs a finite decimal string, integer, or Decimal")
    try:
        number = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"{field} needs a finite decimal") from exc
    if not number.is_finite() or number < 0 or (maximum is not None and number > maximum):
        raise ValueError(f"{field} must be finite and between 0 and {maximum or 'infinity'}")
    return number


def _available(value: object, field: str, cutoff: datetime) -> datetime:
    instant = _instant(value, field)
    if instant > cutoff:
        raise ValueError(f"{field} is unavailable at reporting_at")
    return instant


def _evidence_dates(row: Mapping[str, object], name: str, cutoff: datetime) -> datetime:
    observed = _available(row[f"{name}_observed_at"], f"{name}_observed_at", cutoff)
    available = _available(row[f"{name}_available_at"], f"{name}_available_at", cutoff)
    if available < observed:
        raise ValueError(f"{name}_available_at precedes {name}_observed_at")
    return observed


def _dated_estimate(value: object, fields: set[str], name: str,
                    cutoff: datetime, loan_id: str) -> Mapping[str, object]:
    item = _schema(value, fields, name)
    if item["loan_id"] != loan_id:
        raise ValueError(f"{name}.loan_id must match reporting loan_id")
    observed = _available(item["observed_at"], f"{name}.observed_at", cutoff)
    available = _available(item["available_at"], f"{name}.available_at", cutoff)
    if available < observed:
        raise ValueError(f"{name}.available_at precedes observed_at")
    _name(item["source"], f"{name}.source")
    return item


def _common(row: Mapping[str, object], cutoff: datetime) -> tuple[str, date, str, Decimal, object]:
    loan_id = _name(row["loan_id"], "loan_id")
    reporting_date = _day(row["reporting_date"], "reporting_date")
    if cutoff.date() != reporting_date:
        raise ValueError("reporting_at must fall on reporting_date")
    status_at = _evidence_dates(row, "status", cutoff)
    if status_at.astimezone(cutoff.tzinfo).date() != reporting_date:
        raise ValueError("status_observed_at must be on reporting_date")
    _name(row["status_source"], "status_source")
    if type(row["defaulted"]) is not bool:
        raise ValueError("defaulted must be an explicit reporting-date boolean")
    currency = row["currency"]
    if (not isinstance(currency, str) or len(currency) != 3
            or any(letter not in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" for letter in currency)):
        raise ValueError("currency must be an uppercase three-letter code")
    ead = _dated_estimate(row["ead"], _EAD, "ead", cutoff, loan_id)
    if ead["currency"] != currency or ead["unit"] != "currency_units":
        raise ValueError("ead currency or unit is incompatible with the reporting record")
    amount = _number(ead["amount"], "ead.amount")
    return loan_id, reporting_date, currency, amount, ead["basis"]


def _pd(value: object, cutoff: datetime, loan_id: str, reporting_date: date,
        expected_basis: str, expected_end: date) -> None:
    pd = _dated_estimate(value, _PD, "pd", cutoff, loan_id)
    _number(pd["value"], "pd.value", maximum=Decimal(1))
    if pd["basis"] != expected_basis:
        raise ValueError(f"pd.basis must be {expected_basis}")
    if (_day(pd["window_start"], "pd.window_start") != reporting_date
            or _day(pd["window_end"], "pd.window_end") != expected_end):
        raise ValueError("pd measurement window must match the reporting-date horizon")


def _lgd(value: object, cutoff: datetime, loan_id: str, expected_basis: str) -> None:
    lgd = _dated_estimate(value, _LGD, "lgd", cutoff, loan_id)
    _number(lgd["value"], "lgd.value", maximum=Decimal(1))
    if lgd["basis"] != expected_basis:
        raise ValueError(f"lgd.basis must be {expected_basis}; realized workout labels are not forecasts")


def validate_ecl_input(row: Mapping[str, object]) -> ValidatedReportingInput:
    """Admit dated Stage 1/2 inputs; do not assert Ind AS/IFRS 9 compliance."""
    row = _schema(row, _ECL, "ECL")
    cutoff = _instant(row["reporting_at"], "reporting_at")
    loan_id, day, currency, exposure, ead_basis = _common(row, cutoff)
    stage = row["stage"]
    if stage not in (1, 2) or type(stage) is bool or row["defaulted"]:
        raise ValueError("ECL gate supports performing Stage 1/2 only; defaulted/Stage 3 needs a separate cash-shortfall contract")
    stage_assessed = _available(row["stage_assessed_at"], "stage_assessed_at", cutoff)
    stage_available = _available(row["stage_available_at"], "stage_available_at", cutoff)
    if stage_available < stage_assessed:
        raise ValueError("stage_available_at precedes stage_assessed_at")
    _name(row["stage_source"], "stage_source")
    initial_risk = _evidence_dates(row, "initial_risk", cutoff)
    current_risk = _evidence_dates(row, "current_risk", cutoff)
    if initial_risk >= current_risk:
        raise ValueError("initial risk evidence must precede current risk evidence")
    status_available = _instant(row["status_available_at"], "status_available_at")
    current_risk_available = _instant(row["current_risk_available_at"], "current_risk_available_at")
    initial_risk_available = _instant(row["initial_risk_available_at"], "initial_risk_available_at")
    if stage_assessed < max(status_available, initial_risk_available, current_risk_available):
        raise ValueError("stage_assessed_at must follow available status and risk evidence")
    _name(row["risk_comparison_source"], "risk_comparison_source")
    life_end = _day(row["expected_life_end"], "expected_life_end")
    if life_end <= day:
        raise ValueError("expected_life_end must follow reporting_date")
    anniversary = add_calendar_months(day, 12)
    horizon = "forward_12m" if stage == 1 else "forward_lifetime"
    window_end = min(anniversary, life_end) if stage == 1 else life_end
    _pd(row["pd"], cutoff, loan_id, day, horizon, window_end)
    _lgd(row["lgd"], cutoff, loan_id, "prospective_economic")
    if ead_basis != "prospective_default_exposure":
        raise ValueError("ead.basis must be prospective_default_exposure for performing ECL")
    _number(row["effective_interest_rate"], "effective_interest_rate")
    eir_observed = _available(row["eir_observed_at"], "eir_observed_at", cutoff)
    if _available(row["eir_available_at"], "eir_available_at", cutoff) < eir_observed:
        raise ValueError("eir_available_at precedes eir_observed_at")
    _name(row["eir_source"], "eir_source")
    scenario_observed = _available(row["scenario_observed_at"], "scenario_observed_at", cutoff)
    if _available(row["scenario_available_at"], "scenario_available_at", cutoff) < scenario_observed:
        raise ValueError("scenario_available_at precedes scenario_observed_at")
    _name(row["scenario_source"], "scenario_source")
    return ValidatedReportingInput(loan_id, "illustrative_ecl", day, currency, exposure, horizon)


def validate_basel_input(row: Mapping[str, object]) -> ValidatedReportingInput:
    """Admit dated performing retail inputs for an explicitly named approach."""
    row = _schema(row, _BASEL, "Basel")
    cutoff = _instant(row["reporting_at"], "reporting_at")
    loan_id, day, currency, exposure, ead_basis = _common(row, cutoff)
    if row["defaulted"]:
        raise ValueError("defaulted capital exposures need a separate regulatory treatment")
    _name(row["jurisdiction"], "jurisdiction")
    _name(row["rulebook_version"], "rulebook_version")
    _name(row["rulebook_source"], "rulebook_source")
    _available(row["rulebook_available_at"], "rulebook_available_at", cutoff)
    _evidence_dates(row, "retail_eligibility", cutoff)
    _name(row["retail_eligibility_source"], "retail_eligibility_source")
    if _day(row["rulebook_effective_on"], "rulebook_effective_on") > day:
        raise ValueError("rulebook is not effective at reporting_date")
    approach = row["approach"]
    if approach == "irb_other_retail":
        _name(row["irb_authorisation_source"], "irb_authorisation_source")
        _available(row["irb_authorisation_available_at"], "irb_authorisation_available_at", cutoff)
        _pd(row["pd"], cutoff, loan_id, day, "regulatory_one_year", add_calendar_months(day, 12))
        _lgd(row["lgd"], cutoff, loan_id, "regulatory_downturn")
        if ead_basis != "regulatory_default_exposure":
            raise ValueError("ead.basis must be regulatory_default_exposure for IRB")
        horizon = "regulatory_one_year"
    elif approach == "standardised_retail":
        if (row["pd"] is not None or row["lgd"] is not None
                or row["irb_authorisation_source"] is not None
                or row["irb_authorisation_available_at"] is not None):
            raise ValueError("standardised retail must not be supplied IRB PD/LGD/authorisation")
        if ead_basis != "regulatory_exposure":
            raise ValueError("ead.basis must be regulatory_exposure for standardised retail")
        horizon = None
    else:
        raise ValueError("approach must be irb_other_retail or standardised_retail")
    return ValidatedReportingInput(loan_id, f"illustrative_{approach}", day, currency, exposure, horizon)
