# LGD/EAD dated evidence foundation

**Status:** Validated on synthetic records only. The original LendingClub CSV and a dated default, balance, limit and recovery ledger are unavailable. This [validator](../src/creditrisk/data/lgd_ead_foundation.py) is separate from the historical [LGD target](../src/creditrisk/models/lgd_data.py), [two-stage model](../src/creditrisk/models/lgd_model.py), [term-loan EAD proxy](../src/creditrisk/models/ead_model.py) and [synthetic CCF demo](../src/creditrisk/models/ccf_demo.py). Their behavior and saved metrics are unchanged.

## Normalized input contracts

These names define **new required evidence**, not columns claimed to exist in the historical LendingClub snapshot. Both functions accept a mapping, reject missing and unexpected fields, and return immutable validated records. Money and rates use finite decimal strings, integers or `Decimal`; floating-point inputs, negatives and silent imputation are rejected. Dates are ISO `YYYY-MM-DD`; timestamps are timezone-aware ISO 8601. `features` and `feature_observed_at` must have identical keys. Only caller-approved predictors observed no later than `decision_at` are allowed; known outcome and servicing fields remain forbidden even if approved.

| Contract | Required evidence and checks | Result |
|---|---|---|
| `validate_lgd_record(row, approved_features)` | Loan ID; decision timestamp; qualifying default type, date, named source and explicit earliest-event confirmation; **positive exposure at default**; explicit lists of `{date, amount}` recoveries and workout costs; non-negative annual discount rate, its source and as-of date no later than default; observation and as-of dates; explicit workout-completion boolean and closure date. Cashflows must fall between default and the observed endpoint. Gross recoveries above exposure require reconciliation. Completed workouts must close after their last cashflow and by the observation endpoint. | `ValidatedLGD` stores dated cashflows and `label_eligible=True` only for a closed, observed workout. An incomplete workout remains valid evidence but is **not** a final LGD training label. No LGD value or discount factor is calculated. |
| `validate_ead_record(row, approved_features)` | Loan ID; product type (`term` or `revolving`); observation, decision, default and as-of timestamps in that order; qualifying default type, named source and earliest-event confirmation; non-negative drawn balances at observation/default; explicit undrawn commitment and limits where relevant. Revolving balances must reconcile with their dated limits. A term loan must have zero undrawn commitment and no revolving limit. | `ValidatedEAD` retains the **observed balance at default**. For a revolver with stable limit and positive undrawn commitment, it also computes realized `CCF = (drawn_at_default - drawn_at_observation) / undrawn_at_observation`. A changed limit, zero undrawn or net repayment gets `realized_ccf=None` and an explicit reason. Term loans have no CCF. |

An empty LGD cashflow list means the source affirmatively supplies no such transactions through the observation endpoint; `None` or an omitted list is invalid. This distinction prevents an incomplete or missing recovery history from becoming zero loss recovery. The supplied `discount_rate_annual` is an **effective annual decimal rate** for a future, separately approved economic-loss calculation. Its source/as-of date are validated, but this module does not claim a regulatory discounting policy. Each normalized record's provenance must be authenticated outside this module; the source-name string alone is not authentication.

The validators use the [PD foundation's qualifying event types and prohibited predictor fields](../src/creditrisk/data/pd_foundation.py) so the same dated-default concepts can be aligned later. `earliest_default_confirmed` is a required assertion from the supplying event source, **not proof of that source's integrity**. The validators do not assert that a PD record and an LGD/EAD record came from the same event ledger. A future adapter must reconcile loan IDs, default definitions, first-event dates, currencies and observation cutoffs before joining records.

## Integration boundary

The existing LGD model fits `has_recovery` and a conditional recovery-rate target. A future authenticated adapter could pass only `ValidatedLGD.label_eligible` workouts into a **separately specified** target calculation, then reuse the existing train-only WoE and two-stage estimator. That calculation must decide how to discount dated recoveries and costs, handle cure and over-recovery, and map economic loss to the model's bounded target. The validator deliberately does not make those policy choices. An independent chronological validation set and decision-time feature evidence would still be required.

For EAD, the validated default balance can serve as an observed historical outcome. The existing term-loan [EAD ratio](../src/creditrisk/models/ead_model.py) remains a cumulative principal proxy, not a measured balance at default or a revolving CCF. Prospective EAD would need a reporting-date balance and a supported amortization/draw assumption; the CCF demonstration cannot be trained on term loans. [ECL and capital runners](../src/creditrisk/regulatory/expected_loss.py) still consume historical proxies and have **not** been switched to these records.

## Synthetic verification

The [focused tests](../tests/test_lgd_ead_foundation.py) cover dated valid records, explicit zero recovery, incomplete workout, missing/negative/inconsistent money, cashflows outside the workout, contradictory closure, over-recovery, feature leakage, term versus revolving exposure, limit reconciliation, zero undrawn, limit changes and net repayment. They do not reproduce any historical model or portfolio figure.

```powershell
$env:PYTHONPATH = 'src'
python -m unittest discover -s tests -p test_lgd_ead_foundation.py -v
```
