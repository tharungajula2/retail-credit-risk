"""Dated LGD and EAD evidence contracts, separate from historical proxies.

This module validates normalized records supplied by an authenticated source.
It cannot reconstruct default balances or recoveries from a loan-status snapshot.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Collection, Mapping

from creditrisk.data.pd_foundation import PROHIBITED_PD_FEATURES, QUALIFYING_DEFAULT_TYPES


_OUTCOME_FEATURES = PROHIBITED_PD_FEATURES | {
    "drawn_at_default", "default_at", "default_event_date", "exposure_at_default",
    "recovery_cashflows", "workout_cost_cashflows", "workout_complete",
    "workout_closed_on", "observed_through", "ccf", "realized_ccf",
    "credit_limit_at_default", "discount_rate_annual", "discount_rate_as_of",
    "earliest_default_confirmed", "default_event_source", "default_event_type",
}

_LGD_FIELDS = {
    "loan_id", "decision_at", "default_event_date", "default_event_type",
    "default_event_source", "earliest_default_confirmed", "exposure_at_default", "recovery_cashflows",
    "workout_cost_cashflows", "discount_rate_annual", "discount_rate_as_of",
    "discount_rate_source",
    "observed_through", "as_of_date", "workout_complete", "workout_closed_on",
    "features", "feature_observed_at",
}

_EAD_FIELDS = {
    "loan_id", "product_type", "decision_at", "observation_at", "default_at",
    "default_event_type", "default_event_source", "earliest_default_confirmed",
    "as_of_at", "drawn_at_observation", "undrawn_at_observation",
    "credit_limit_at_observation", "drawn_at_default", "credit_limit_at_default",
    "features", "feature_observed_at",
}


@dataclass(frozen=True)
class Cashflow:
    on: date
    amount: Decimal


@dataclass(frozen=True)
class ValidatedLGD:
    loan_id: str
    default_event_date: date
    exposure_at_default: Decimal
    recovery_cashflows: tuple[Cashflow, ...]
    workout_cost_cashflows: tuple[Cashflow, ...]
    discount_rate_annual: Decimal
    observed_through: date
    workout_complete: bool

    @property
    def label_eligible(self) -> bool:
        """Only a closed, fully observed workout can supply a final LGD label."""
        return self.workout_complete


@dataclass(frozen=True)
class ValidatedEAD:
    loan_id: str
    product_type: str
    observation_at: datetime
    default_at: datetime
    drawn_at_observation: Decimal
    undrawn_at_observation: Decimal
    drawn_at_default: Decimal
    realized_ccf: Decimal | None
    ccf_ineligible_reason: str | None


def _schema(row: Mapping[str, object], expected: set[str], kind: str) -> None:
    if not isinstance(row, Mapping):
        raise ValueError(f"{kind} record must be a mapping")
    missing = expected - row.keys()
    unexpected = row.keys() - expected
    if missing or unexpected:
        raise ValueError(f"{kind} schema: missing={sorted(map(str, missing))}, unexpected={sorted(map(str, unexpected))}")


def _identifier(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value.strip()


def _date(value: object, field: str) -> date:
    if isinstance(value, datetime):
        raise ValueError(f"{field} requires YYYY-MM-DD, not a timestamp")
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            parsed = date.fromisoformat(value)
            if value == parsed.isoformat():
                return parsed
        except ValueError:
            pass
    raise ValueError(f"{field} requires YYYY-MM-DD or a date object")


def _time(value: object, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value) if isinstance(value, str) else value
    except ValueError as exc:
        raise ValueError(f"{field} requires a timezone-aware ISO 8601 timestamp") from exc
    if not isinstance(parsed, datetime) or parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field} requires a timezone-aware ISO 8601 timestamp")
    return parsed


def _decimal(value: object, field: str, *, positive: bool = False) -> Decimal:
    # Floats can hide binary rounding in money and rates; normalized inputs use text/Decimal.
    if isinstance(value, bool) or not isinstance(value, (str, int, Decimal)):
        raise ValueError(f"{field} requires a finite decimal string, integer, or Decimal")
    try:
        result = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError(f"{field} requires a finite decimal") from exc
    if not result.is_finite() or result < 0 or (positive and result == 0):
        raise ValueError(f"{field} must be {'positive' if positive else 'non-negative'} and finite")
    return result


def _features(row: Mapping[str, object], decision_at: datetime,
              approved_features: Collection[str]) -> None:
    features = row["features"]
    observed = row["feature_observed_at"]
    if not isinstance(features, Mapping) or not isinstance(observed, Mapping):
        raise ValueError("features and feature_observed_at must be mappings")
    if features.keys() != observed.keys():
        raise ValueError("every feature needs exactly one availability timestamp")
    names = set(features)
    if not all(isinstance(name, str) for name in names):
        raise ValueError("feature names must be strings")
    forbidden = names & _OUTCOME_FEATURES
    unapproved = names - set(approved_features)
    if forbidden or unapproved:
        raise ValueError(f"features forbidden={sorted(forbidden)}, unapproved={sorted(unapproved)}")
    for name, value in features.items():
        if value is None:
            raise ValueError(f"feature {name} cannot be null")
        if _time(observed[name], f"feature_observed_at[{name}]") > decision_at:
            raise ValueError(f"feature {name} was observed after decision_at")


def _cashflows(value: object, field: str, start: date, end: date) -> tuple[Cashflow, ...]:
    if not isinstance(value, (list, tuple)):
        raise ValueError(f"{field} must be an explicit list of dated cashflows")
    result = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping) or set(item) != {"date", "amount"}:
            raise ValueError(f"{field}[{index}] requires date and amount only")
        on = _date(item["date"], f"{field}[{index}].date")
        amount = _decimal(item["amount"], f"{field}[{index}].amount", positive=True)
        if not start <= on <= end:
            raise ValueError(f"{field}[{index}] falls outside default-to-observation window")
        result.append(Cashflow(on, amount))
    return tuple(result)


def _default_evidence(row: Mapping[str, object]) -> None:
    if not isinstance(row["default_event_type"], str) or row["default_event_type"] not in QUALIFYING_DEFAULT_TYPES:
        raise ValueError("default_event_type is not a qualifying dated default")
    _identifier(row["default_event_source"], "default_event_source")
    if row["earliest_default_confirmed"] is not True:
        raise ValueError("earliest_default_confirmed must be true from the event source")


def validate_lgd_record(row: Mapping[str, object],
                        approved_features: Collection[str] = ()) -> ValidatedLGD:
    """Validate a normalized LGD workout; never infer missing cashflows as zero."""
    _schema(row, _LGD_FIELDS, "LGD")
    loan_id = _identifier(row["loan_id"], "loan_id")
    decision_at = _time(row["decision_at"], "decision_at")
    default_on = _date(row["default_event_date"], "default_event_date")
    observed_through = _date(row["observed_through"], "observed_through")
    as_of = _date(row["as_of_date"], "as_of_date")
    if decision_at.date() > default_on or not default_on <= observed_through <= as_of:
        raise ValueError("require decision_at <= default_event_date <= observed_through <= as_of_date")
    _default_evidence(row)
    exposure = _decimal(row["exposure_at_default"], "exposure_at_default", positive=True)
    rate = _decimal(row["discount_rate_annual"], "discount_rate_annual")
    rate_as_of = _date(row["discount_rate_as_of"], "discount_rate_as_of")
    if rate_as_of > default_on:
        raise ValueError("discount_rate_as_of cannot follow default_event_date")
    _identifier(row["discount_rate_source"], "discount_rate_source")
    recoveries = _cashflows(row["recovery_cashflows"], "recovery_cashflows", default_on, observed_through)
    costs = _cashflows(row["workout_cost_cashflows"], "workout_cost_cashflows", default_on, observed_through)
    if sum((cash.amount for cash in recoveries), Decimal(0)) > exposure:
        raise ValueError("gross recoveries exceed exposure_at_default; reconcile before LGD labelling")
    if type(row["workout_complete"]) is not bool:
        raise ValueError("workout_complete must be an explicit boolean")
    closed = row["workout_closed_on"]
    if row["workout_complete"]:
        closed_on = _date(closed, "workout_closed_on")
        last_cashflow = max((cash.on for cash in recoveries + costs), default=default_on)
        if not last_cashflow <= closed_on <= observed_through:
            raise ValueError("workout_closed_on must follow cashflows and precede observed_through")
    elif closed is not None:
        raise ValueError("incomplete workout cannot have workout_closed_on")
    _features(row, decision_at, approved_features)
    return ValidatedLGD(loan_id, default_on, exposure, recoveries, costs, rate,
                        observed_through, row["workout_complete"])


def validate_ead_record(row: Mapping[str, object],
                        approved_features: Collection[str] = ()) -> ValidatedEAD:
    """Validate dated exposure evidence; CCF is defined only for eligible revolvers."""
    _schema(row, _EAD_FIELDS, "EAD")
    loan_id = _identifier(row["loan_id"], "loan_id")
    product = row["product_type"]
    if not isinstance(product, str) or product not in {"term", "revolving"}:
        raise ValueError("product_type must be term or revolving")
    observation = _time(row["observation_at"], "observation_at")
    decision = _time(row["decision_at"], "decision_at")
    default = _time(row["default_at"], "default_at")
    as_of = _time(row["as_of_at"], "as_of_at")
    if not observation <= decision < default <= as_of:
        raise ValueError("require observation_at <= decision_at < default_at <= as_of_at")
    _default_evidence(row)
    drawn = _decimal(row["drawn_at_observation"], "drawn_at_observation")
    undrawn = _decimal(row["undrawn_at_observation"], "undrawn_at_observation")
    drawn_default = _decimal(row["drawn_at_default"], "drawn_at_default")
    _features(row, decision, approved_features)

    if product == "term":
        if undrawn != 0 or row["credit_limit_at_observation"] is not None or row["credit_limit_at_default"] is not None:
            raise ValueError("term loan requires zero undrawn and no revolving credit limits")
        return ValidatedEAD(loan_id, product, observation, default, drawn, undrawn,
                            drawn_default, None, "term_loan_no_ccf")

    limit = _decimal(row["credit_limit_at_observation"], "credit_limit_at_observation", positive=True)
    default_limit = _decimal(row["credit_limit_at_default"], "credit_limit_at_default", positive=True)
    if drawn > limit or drawn_default > default_limit or drawn + undrawn != limit:
        raise ValueError("drawn/undrawn balances must reconcile to dated credit limits")
    if limit != default_limit:
        ccf, reason = None, "limit_changed"
    elif undrawn == 0:
        ccf, reason = None, "no_undrawn_commitment"
    elif drawn_default < drawn:
        ccf, reason = None, "net_repayment_before_default"
    else:
        ccf, reason = (drawn_default - drawn) / undrawn, None
    return ValidatedEAD(loan_id, product, observation, default, drawn, undrawn,
                        drawn_default, ccf, reason)
