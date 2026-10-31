# PD target foundation: dated evidence and observation windows

**Status:** synthetic-fixture implementation only. This module has not labelled or validated any LendingClub loan. It is intentionally separate from [`target.py`](../src/creditrisk/data/target.py) and [`sampling.py`](../src/creditrisk/data/sampling.py); historical output tables remain unchanged.

## 1. Provenance boundary

The repository's scripts expect `datasets/loan_data_2007_2014.csv` ([`run_sampling.py`](../src/creditrisk/data/run_sampling.py), [`inspect_raw.py`](../src/creditrisk/data/inspect_raw.py)). That file and the `datasets/` directory are absent from the fresh clone and ignored by [`.gitignore`](../.gitignore). The committed [`data_inventory.txt`](../outputs/reports/data_inventory.txt) reports a **historical** input of 466,285 rows and 75 columns, with `id`, `issue_d`, `loan_status`, `last_pymnt_d`, `last_credit_pull_d` and financial/credit fields. [`config/variables.yaml`](../config/variables.yaml) is a candidate feature and outcome dictionary, not a checksum or authenticated source manifest. `README.md` names LendingClub on Kaggle but supplies no exact dataset version or download record.

Two public source leads are the [Kaggle Lending Club Loan Data dataset](https://www.kaggle.com/datasets/wendykan/lending-club-loan-data) and [All Lending Club loan data](https://www.kaggle.com/wordsforthewise/lending-club), which describes additional cleaning and broader years. They are **candidates**, not authenticated matches for the missing CSV. Row count or a similar filename cannot establish identity, including for any `Analytics-ML-Portfolio` copy. No source file, row-level comparison, SHA-256, licence chain or fixed extraction snapshot is available in this clone. No dataset was downloaded for this work.

The prior path from raw data to saved metrics is: [`inspect_raw.py`](../src/creditrisk/data/inspect_raw.py) inventory → [`target.py`](../src/creditrisk/data/target.py) final-status/last-payment proxy → [`run_sampling.py`](../src/creditrisk/data/run_sampling.py) Parquet development/test/2014 cohorts → [`run_binning.py`](../src/creditrisk/features/run_binning.py) training WoE → [`run_pd_model.py`](../src/creditrisk/models/run_pd_model.py) models A/B → [`run_validation.py`](../src/creditrisk/validation/run_validation.py) saved metrics. The raw and intermediate inputs required to replay this chain are missing.

## 2. Why the old 12-month label is unsuitable for revalidation

The historical builder calls a final `loan_status` a default, estimates its timing as `last_pymnt_d + 3 months`, substitutes issue date if payment date is missing, and labels every other row zero. A latest payment date is not a confirmed default event; a final status does not tell whether default happened within 12 months; and unresolved or insufficiently observed loans must not silently become non-defaults. [`target.py` lines 89–125](../src/creditrisk/data/target.py), [`target_definition.yaml`](../config/target_definition.yaml). The old split checks ID disjointness, but cannot repair incorrect or censored labels. Historical AUC/Gini remain saved outputs, **not validation of the corrected target**.

## 3. Corrected estimand and evidence contract

For a loan originated on calendar date **D**, the performance window is **(D, D + 12 calendar months]**. A positive target requires the **earliest confirmed qualifying default** after D and on or before the anniversary. The code accepts `90_plus_dpd`, `charge_off`, `bankruptcy`, or `unlikeliness_to_pay` only when a dated event and a named source are provided. For a no-default label, the account must be observable through the anniversary and its source must assert complete qualifying-event history over that interval. Otherwise the target is missing (`None`), with a disposition explaining why. A current/final “Charged Off” or similar status without a dated event receives `undated_default`, never a positive or negative label. An event after the anniversary can support zero **only** if the earlier event history is complete.

The observation endpoint is `observed_through`, capped by the explicit `as_of_date`. An event beyond the endpoint or before/at origination is rejected. The anniversary is computed by calendar-month addition, clamping month ends; for example, 29 February 2024 + 12 months = 28 February 2025. These are deliberate conventions, and a real-data adapter must verify them against its event definitions.

| Normalized field | Requirement |
|---|---|
| `loan_id` | Unique non-empty identifier, used for QA only. |
| `origination_date` | ISO `YYYY-MM-DD` date; performance clock starts here. |
| `decision_at` | Timezone-aware ISO timestamp at which predictors must have been known, no later than origination date. |
| `observed_through` | Last date of reliable account/event observation, no later than policy `as_of_date`. |
| `event_history_complete` | Explicit **boolean from the event source** confirming earliest qualifying defaults would be captured through `observed_through`; never inferred from snapshot status. |
| `default_event_date`, `default_event_type`, `default_event_source` | All present together for a qualifying event, or all `None`; date and named source are mandatory for positive labels. |
| `observed_status` | Optional status at observation endpoint, used only to prevent an undated default-like status from being mislabelled zero. |
| `features`, `feature_observed_at` | Required mappings when selected predictors are checked. Each selected feature needs an availability timestamp at or before `decision_at`. |

The module's [`validate_dataset_schema`](../src/creditrisk/data/pd_foundation.py) rejects missing fields, duplicate IDs, invalid or inconsistent dates, incomplete event evidence, unqualified event types, prohibited outcome/servicing fields, features outside `PDPolicy.approved_features`, and future predictor timestamps. `build_pd_12m_labels` returns `PDLabel` records with `default_12m` as `1`, `0`, or `None`, a `label_state`, the explicit window dates and assigned cohort. Modelling code must exclude `None` labels and observations outside a named cohort, and report those exclusions.

## 4. Chronological cohorts and feature availability

`PDPolicy` takes named, **non-overlapping** issue-date intervals `[start, end)`. A future real-data protocol can reserve `[2007-01-01, 2014-01-01)` for development and `[2014-01-01, 2015-01-01)` for a 2014 issue-year holdout; this code does not claim that such a dataset exists or run a training split. Cohort assignment is based solely on the origination date. Explicit as-of and observation coverage checks prevent a future record from supplying a label at an earlier cut-off.

Predictors must be explicitly listed in `PDPolicy.approved_features` and have per-row evidence of availability no later than `decision_at`. Outcome fields such as `loan_status`, recoveries, repayments, observation endpoints and identifiers are blocked even if supplied with a misleading timestamp. `grade`, `sub_grade`, `int_rate`, funded amounts and other historically labelled “application time” variables must be verified against the **actual decision point** before approval: their presence in a snapshot or in [`variables.yaml`](../config/variables.yaml) is insufficient proof of availability at application decision. All input feature timestamps should use one documented business timezone; the module compares timezone-aware instants.

## 5. Synthetic example and focused tests

[`tests/test_pd_foundation.py`](../tests/test_pd_foundation.py) supplies synthetic records with dated events, explicit observation coverage and time-stamped features. It tests an event inside/on/outside the 12-month boundary, short follow-up, incomplete history, undated charged-off status, cohort edges, leap-day arithmetic, future observation/event rejection, feature leakage and schema failures. It does not assert any LendingClub metric.

From the repository root, using an available Python 3.11+ interpreter:

```powershell
python -m unittest discover -s tests -p test_pd_foundation.py -v
```

`unittest` and the module use the Python standard library. Existing PD/LGD/EAD scripts still call the historical target. There is no adapter from `loan_data_2007_2014.csv` to this evidence schema because the missing snapshot has no authenticated, dated default-event ledger or observation panel.

## 6. Required evidence before real-data validation

1. Obtain an authorised, versioned source with exact URL, licence/terms, extraction date, filename, byte size, SHA-256, row count and schema. Do not substitute a similar LendingClub dataset by name or count.
2. Determine whether it contains **dated earliest default events** and reliable per-loan observation endpoints. If only final status and latest-payment date exist, retain the corrected module as synthetic teaching code and make no new real-data PD performance claim.
3. Verify predictor timestamps at the actual decision point. Freeze the cohort/as-of protocol before fitting; document exclusions for censoring, undated events and missing fields.
4. Only after these checks, create a source-specific adapter, rerun target reconciliation, fit WoE on development data alone, and evaluate on a genuinely independent later cohort.

The current [`README.md`](../README.md), [`PROJECT_TRUTH_retail-credit-risk.md`](../PROJECT_TRUTH_retail-credit-risk.md) and archived [`MODEL_DOCUMENTATION.md`](archive/MODEL_DOCUMENTATION.md) retain unsupported production-grade and historical-performance language. They are preserved for the planned final documentation pass; none of their saved numbers have been replaced or reinterpreted as results of this module.
