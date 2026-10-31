"""Evidence-based 12-month PD labels for a dated loan observation panel.

This module is deliberately separate from the historical LendingClub pipeline.
It cannot turn a single current-status snapshot into dated default evidence.
"""

from __future__ import annotations

from calendar import monthrange
from dataclasses import dataclass
from datetime import date, datetime
from typing import Iterable, Mapping, Sequence


# Outcome, servicing, identity, and derived fields are never decision-time predictors.
PROHIBITED_PD_FEATURES = frozenset({
    "loan_id", "id", "member_id", "url", "issue_d", "origination_date",
    "decision_at", "observed_through", "observed_status",
    "event_history_complete", "default_event_date", "default_event_type",
    "default_event_source", "loan_status", "last_pymnt_d", "last_pymnt_amnt",
    "last_credit_pull_d", "next_pymnt_d", "pymnt_plan", "out_prncp",
    "out_prncp_inv", "total_pymnt", "total_pymnt_inv", "total_rec_prncp",
    "total_rec_int", "total_rec_late_fee", "recoveries",
    "collection_recovery_fee", "ever_default", "est_default_date",
    "months_to_default", "default_12m", "label_state", "stage", "ead",
    "lgd", "lgd_hat", "pd_hat", "ecl", "cecl",
})

UNDATED_DEFAULT_STATUSES = frozenset({
    "Charged Off", "Default", "Late (31-120 days)",
    "Does not meet the credit policy. Status:Charged Off",
})

QUALIFYING_DEFAULT_TYPES = frozenset({
    "90_plus_dpd", "charge_off", "bankruptcy", "unlikeliness_to_pay",
})

REQUIRED_FIELDS = frozenset({
    "loan_id", "origination_date", "decision_at", "observed_through",
    "event_history_complete", "default_event_date", "default_event_type",
    "default_event_source", "observed_status",
})


def _date(value: object, field: str) -> date:
    if isinstance(value, datetime):
        raise ValueError(f"{field} requires a date, not a timestamp")
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


def _timestamp(value: object, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value) if isinstance(value, str) else value
    except ValueError as exc:
        raise ValueError(f"{field} requires an ISO 8601 timestamp") from exc
    if not isinstance(parsed, datetime) or parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError(f"{field} requires a timezone-aware ISO 8601 timestamp")
    return parsed


def add_calendar_months(day: date, months: int) -> date:
    """Add whole calendar months, clamping a missing month-end day."""
    if months < 1:
        raise ValueError("performance_months must be positive")
    month_index = day.year * 12 + day.month - 1 + months
    year, zero_based_month = divmod(month_index, 12)
    month = zero_based_month + 1
    return date(year, month, min(day.day, monthrange(year, month)[1]))


@dataclass(frozen=True)
class Cohort:
    name: str
    start: date  # inclusive origination date
    end: date    # exclusive origination date

    def __post_init__(self) -> None:
        if (not self.name or not isinstance(self.start, date) or not isinstance(self.end, date)
                or isinstance(self.start, datetime) or isinstance(self.end, datetime)
                or self.start >= self.end):
            raise ValueError("cohort requires a name and start < end")


@dataclass(frozen=True)
class PDPolicy:
    as_of_date: date
    cohorts: tuple[Cohort, ...]
    performance_months: int = 12
    approved_features: frozenset[str] = frozenset()

    def __post_init__(self) -> None:
        if not isinstance(self.as_of_date, date) or isinstance(self.as_of_date, datetime):
            raise ValueError("as_of_date must be a date")
        if self.performance_months < 1 or not self.cohorts:
            raise ValueError("policy requires positive months and at least one cohort")
        if len({cohort.name for cohort in self.cohorts}) != len(self.cohorts):
            raise ValueError("cohort names must be unique")
        ordered = sorted(self.cohorts, key=lambda cohort: cohort.start)
        if any(left.end > right.start for left, right in zip(ordered, ordered[1:])):
            raise ValueError("cohorts must not overlap")
        if self.approved_features & PROHIBITED_PD_FEATURES:
            raise ValueError("approved_features contains prohibited outcome or identity fields")


@dataclass(frozen=True)
class PDLabel:
    loan_id: str
    cohort: str | None
    performance_start: date  # default must occur strictly after this date
    performance_end: date    # default on this anniversary is in-window
    observed_through: date
    default_12m: int | None  # None is never silently coerced to zero
    label_state: str


def assign_cohort(origination_date: date, policy: PDPolicy) -> str | None:
    """Assign an issue date to one non-overlapping chronological cohort."""
    for cohort in policy.cohorts:
        if cohort.start <= origination_date < cohort.end:
            return cohort.name
    return None


def validate_dataset_schema(
    rows: Iterable[Mapping[str, object]],
    policy: PDPolicy,
    selected_features: Sequence[str] = (),
) -> list[Mapping[str, object]]:
    """Validate event evidence, observation dates and feature availability.

    `event_history_complete=True` is a source-level assertion that the earliest
    qualifying default through `observed_through` would be in this record.
    It must not be inferred from a final `loan_status` string.
    """
    features = tuple(selected_features)
    if len(set(features)) != len(features):
        raise ValueError("selected_features contains duplicates")
    forbidden = set(features) & PROHIBITED_PD_FEATURES
    if forbidden:
        raise ValueError(f"post-decision or outcome features prohibited: {sorted(forbidden)}")
    unapproved = set(features) - policy.approved_features
    if unapproved:
        raise ValueError(f"selected features are not approved by the policy: {sorted(unapproved)}")

    materialized = list(rows)
    seen_ids: set[str] = set()
    for index, row in enumerate(materialized):
        if not isinstance(row, Mapping):
            raise ValueError(f"row {index} must be a mapping")
        missing = REQUIRED_FIELDS - row.keys()
        if missing:
            raise ValueError(f"row {index} missing required fields: {sorted(missing)}")
        loan_id = str(row["loan_id"]).strip()
        if not loan_id or loan_id == "None" or loan_id in seen_ids:
            raise ValueError(f"row {index} has a missing or duplicate loan_id")
        seen_ids.add(loan_id)

        originated = _date(row["origination_date"], "origination_date")
        observed = _date(row["observed_through"], "observed_through")
        decided = _timestamp(row["decision_at"], "decision_at")
        if decided.date() > originated or originated > observed or observed > policy.as_of_date:
            raise ValueError(f"row {index} has a future or inconsistent observation date")
        if type(row["event_history_complete"]) is not bool:
            raise ValueError(f"row {index} requires boolean event_history_complete")
        if row["observed_status"] is not None and not isinstance(row["observed_status"], str):
            raise ValueError(f"row {index} requires a textual observed_status or None")

        event_fields = ("default_event_date", "default_event_type", "default_event_source")
        present = [row[field] is not None and row[field] != "" for field in event_fields]
        if any(present) and not all(present):
            raise ValueError(f"row {index} needs date, type and source for a default event")
        if all(present):
            event_date = _date(row["default_event_date"], "default_event_date")
            if not originated < event_date <= observed:
                raise ValueError(f"row {index} has a pre-origination or future default event")
            if (not isinstance(row["default_event_type"], str)
                    or row["default_event_type"] not in QUALIFYING_DEFAULT_TYPES):
                raise ValueError(f"row {index} has an unqualified default event type")
            if not isinstance(row["default_event_source"], str) or not row["default_event_source"].strip():
                raise ValueError(f"row {index} needs a non-empty default event source")

        if features:
            values = row.get("features")
            timestamps = row.get("feature_observed_at")
            if not isinstance(values, Mapping) or not isinstance(timestamps, Mapping):
                raise ValueError(f"row {index} needs features and feature_observed_at mappings")
            for feature in features:
                if feature not in values or feature not in timestamps:
                    raise ValueError(f"row {index} missing selected feature or its timestamp: {feature}")
                available = _timestamp(timestamps[feature], f"feature_observed_at[{feature}]")
                if available > decided:
                    raise ValueError(f"row {index} has future-data leakage in {feature}")
    return materialized


def build_pd_12m_labels(
    rows: Iterable[Mapping[str, object]],
    policy: PDPolicy,
    selected_features: Sequence[str] = (),
) -> list[PDLabel]:
    """Label only evidenced defaults and fully observed non-defaults.

    A missing event date with a default-like snapshot status remains unknown.
    A non-default requires complete event history through the 12-month end.
    """
    evidence = validate_dataset_schema(rows, policy, selected_features)
    labels = []
    for row in evidence:
        start = _date(row["origination_date"], "origination_date")
        end = add_calendar_months(start, policy.performance_months)
        observed = _date(row["observed_through"], "observed_through")
        event = row["default_event_date"]
        event_date = _date(event, "default_event_date") if event is not None and event != "" else None

        if event_date is not None and event_date <= end:
            value, state = 1, "observed_default"
        elif event_date is None and row["observed_status"] in UNDATED_DEFAULT_STATUSES:
            value, state = None, "undated_default"
        elif observed >= end and row["event_history_complete"]:
            value, state = 0, "observed_nondefault"
        else:
            value, state = None, "censored_or_incomplete"

        labels.append(PDLabel(
            loan_id=str(row["loan_id"]).strip(),
            cohort=assign_cohort(start, policy),
            performance_start=start,
            performance_end=end,
            observed_through=observed,
            default_12m=value,
            label_state=state,
        ))
    return labels
