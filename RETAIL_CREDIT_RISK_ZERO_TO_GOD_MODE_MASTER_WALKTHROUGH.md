# Retail Credit Risk — Zero → Hero → God Mode Master Walkthrough

## A continuous technical + domain script for the `retail-credit-risk` project

**Purpose of this document**

This is not a generic credit-risk textbook and it is not a generic Python repository tour. It is a single continuous walkthrough designed to explain the actual `retail-credit-risk` project from first principles all the way to expert-level discussion.

The source of truth for project behavior is the repository evidence captured in:

- `RETAIL_CREDIT_RISK_WALKTHROUGH_SOURCEPACK.md`
- `RETAIL_CREDIT_RISK_SME_MAP.md`
- `PROJECT_TRUTH_retail-credit-risk.md`

Whenever this script moves beyond what the repository literally implements, that expansion is called out as **SME context** or **real-world bank extension**. The project itself includes a mix of full-dataset implementations, synthetic demonstrations, micro-sample demonstrations, and cross-sectional proxies. Those distinctions are preserved throughout.

---

# Opening: What I built, in one sentence

I built an end-to-end retail credit risk modelling and analytics system in Python on **466,285 historical unsecured consumer loans**, covering **12-month default target engineering, PD scorecard development, LGD modelling, EAD, expected loss, IFRS 9 staging and ECL, US CECL comparison, Basel III IRB capital, model validation, stability monitoring, vintage analytics, reporting, and a RAG-based credit-risk analyst interface**.

That one sentence sounds dense because credit risk itself is dense. So instead of starting with code, I want to start with the business problem.

A lender gives money today and receives cash back over time. The lender does not know with certainty whether the borrower will repay. Credit risk is the discipline of converting that uncertainty into measurable quantities that can support underwriting, pricing, provisioning, capital, and portfolio management.

At the center of the project are three quantities:

- **PD — Probability of Default:** How likely is the borrower to default?
- **LGD — Loss Given Default:** If default happens, what proportion of exposure will be lost?
- **EAD — Exposure At Default:** How much money will be outstanding when default occurs?

Those three quantities combine into the classic expected-loss relationship:

\[
EL = PD 	imes LGD 	imes EAD
\]

But a real credit-risk system cannot stop at that formula. We also need to answer:

- What exactly counts as a default?
- Over what horizon?
- Which borrower variables are allowed into the model?
- How do we prevent target leakage?
- How do we split development and out-of-time samples?
- How do we transform variables into a stable scorecard?
- How do we validate discrimination and calibration?
- How do we monitor drift?
- How do we estimate recovery severity?
- How do accounting frameworks such as IFRS 9 use 12-month versus lifetime risk?
- How does regulatory capital differ from accounting provisions?
- How do we communicate all of this to a risk committee?

That is what the repository is structured to demonstrate.

---

# Part I — The Project Before the Models

## 1. The raw portfolio

The primary dataset is the public LendingClub unsecured term-loan dataset covering originations from **2007 through 2014**.

The raw file contains:

- **466,285 loans**
- **75 original attributes**

After target engineering, the project works with 79 columns because it adds derived target and timing fields.

The portfolio has:

- **50,968 ever-defaulted loans**, or about **10.93%**
- **16,018 loans that default within the 12-month performance window**, or about **3.44%**

This distinction matters immediately.

“Ever default” and “12-month default” are not the same target.

An account can survive the first year and default later. If my PD model is intended to estimate the probability of default over 12 months, then an account that defaults in month 25 is not a 12-month default. It may still matter for lifetime loss modelling, but it is not a positive label for the 12-month PD target.

That is the first important modelling discipline in this project: **the target must match the horizon of the risk estimate**.

The main raw-data work is represented in the `src/creditrisk/data/` package.

Important files include:

- `schema.py`
- `target.py`
- `sampling.py`
- `inspect_raw.py`
- `target_qa.py`

The repository then persists processed modelling partitions as parquet files under `data/processed/`.

---

## 2. Why target engineering is harder than it sounds

Many beginner credit-risk examples assume the dataset already gives a clean binary column such as `defaulted_12m`.

This dataset does not.

The source data includes fields such as origination date, loan status, last payment date, and last credit pull date. The project therefore has to infer a default-timing relationship and then decide whether the estimated default falls inside the 12-month performance horizon.

The relevant implementation is in `src/creditrisk/data/target.py`.

Conceptually, the project does the following:

1. Parse LendingClub date fields.
2. Identify default-type outcomes from loan status.
3. Estimate a default date using available payment timing information.
4. Calculate months from origination to estimated default.
5. Set `default_12m = 1` only when the default falls inside the 12-month window.

The source documentation also highlights a date-parsing issue that had to be handled carefully: century rollover behavior in LendingClub month-year strings.

This is a good place to explain a broader modelling principle.

A credit model is only as meaningful as its target. If the target is noisy, ambiguous, or inconsistent with the intended prediction horizon, even a sophisticated algorithm will be learning the wrong problem.

In this project, the target-engineering layer is not a small preprocessing step. It is part of the credit-risk methodology.

---

## 3. Anti-leakage governance

One of the most important files in the entire repository is `src/creditrisk/data/schema.py`.

Why?

Because credit modelling datasets often contain variables that are highly predictive only because they are observed **after** the lending decision.

For example, fields related to:

- principal received
- recoveries
- last payment date
- outstanding principal
- post-origination status

may tell us a great deal about whether an account ultimately defaulted.

But if the model is supposed to make an origination-time prediction, those variables were not available at origination.

Using them would create **target leakage**.

The repository addresses this by classifying variables in `config/variables.yaml`.

The source pack groups them into categories such as:

- application-time variables
- sparse application variables
- outcome variables
- identifiers
- free-text fields
- all-null fields
- cohort anchor

The key governance function is `assert_no_leakage()`.

That makes the modelling philosophy explicit:

> A PD scorecard should be built from information that was available when the credit decision was made.

This sounds obvious, but leakage is one of the easiest ways to create a model with impressive validation metrics that collapses in real use.

So when I walk through this project, I would make one point very clear: the repo does not treat feature selection as merely “choose the most predictive columns.” It first establishes whether a variable is **eligible** for PD modelling at all.

---

## 4. Development, test, and out-of-time samples

The project does not randomly split all 466,285 loans into train and test and call it a day.

Instead, it uses time.

The development cohort consists of **2007–2013 vintages**, totaling **230,657 loans**.

That development cohort is then split 80/20 with stratification:

- **Train:** 184,525 loans
- **Test:** 46,132 loans

The **2014 vintage** is held out as an **out-of-time, or OOT, sample**:

- **OOT:** 235,628 loans

This matters because credit risk changes with time.

Borrower mix changes.
Underwriting policy changes.
Pricing changes.
Economic conditions change.
Data capture changes.
Portfolio seasoning changes.

A model can perform well on a random holdout from the same historical pool and still fail on the next vintage.

That is why OOT validation is particularly important in credit-risk work.

The implementation lives in `src/creditrisk/data/sampling.py`, with configuration in `config/sampling.yaml`.

The project truth also makes an important correction: **the OOT sample is 2014, not 2015**. There is no 2015 origination cohort in the raw data used by the repository.

That is exactly the kind of detail I would state confidently in an interview because it is grounded in the repository.

---

# Part II — From Raw Variables to a Credit Scorecard

## 5. The variables that matter

The project starts with many potential application-time attributes, but the final PD scorecards use selected subsets.

Examples of variables documented in the source pack include:

- `loan_amnt`
- `term`
- `int_rate`
- `installment`
- `grade`
- `sub_grade`
- `emp_length`
- `home_ownership`
- `annual_inc`
- `verification_status`
- `purpose`
- `dti`
- `delinq_2yrs`
- `inq_last_6mths`
- `revol_util`
- `revol_bal`
- `total_acc`

Each variable has a business interpretation.

`dti` is debt-to-income ratio. It is a proxy for how much of the borrower’s income is already committed to debt obligations.

`inq_last_6mths` is recent hard-credit inquiry activity. More inquiries can indicate active credit seeking.

`revol_util` is revolving utilization. High utilization can signal balance-sheet stress.

`annual_inc` is income capacity, although its relationship with risk is not always perfectly linear.

`term` distinguishes 36-month and 60-month loans. Longer terms can have different risk dynamics because the borrower remains exposed to financial shocks for longer.

`grade`, `sub_grade`, and `int_rate` are especially interesting because they already embed information from LendingClub’s own pricing and credit-risk process.

That leads directly to the distinction between the project’s two PD models.

---

## 6. Why the project uses Weight of Evidence

The core feature-engineering class is `WoEBinner` in `src/creditrisk/features/binning.py`.

The project transforms variables using **Weight of Evidence**, or WoE.

At a high level, WoE compares the concentration of good accounts and bad accounts inside a bin.

For bin \(i\):

\[
WoE_i =
\ln\left(
rac{\% 	ext{ non-defaults in bin }i}
{\% 	ext{ defaults in bin }i}
ight)
\]

The project uses the convention shown in its own source documentation, so the sign should be interpreted consistently with that implementation.

Why bin at all?

Because many credit-risk relationships are not naturally linear.

Suppose DTI rises from 5% to 15%.
The impact on risk may be modest.

Suppose it rises from 35% to 45%.
The impact may be much stronger.

A raw linear coefficient assumes a constant marginal effect unless we transform the variable.

Binning lets the model represent different risk regions more naturally.

WoE then converts those bins into a log-odds-oriented representation that works well with logistic regression.

There is also a governance benefit.

A scorecard built from transparent bins is easier to inspect than a black-box transformation pipeline.

I can ask:

- What is the risk profile of low-income versus high-income bins?
- Where does DTI risk start to rise?
- Are missing values isolated?
- Are category groupings sensible?
- Does risk move monotonically?
- Are any bins suspiciously predictive?

This is why WoE remains important in traditional scorecard methodology even when more complex algorithms exist.

---

## 7. Information Value

The same binning engine calculates **Information Value**, or IV.

The project uses the standard relationship:

\[
IV =
\sum_i
(\%Good_i - \%Bad_i)
	imes WoE_i
\]

The purpose of IV here is feature screening.

The source pack reports top IV values including:

- `sub_grade`: **0.4482**
- `grade`: **0.4357**
- `int_rate`: **0.4215**
- `term`: **0.1784**
- `dti`: **0.0912**
- `inq_last_6mths`: **0.0785**
- `annual_inc`: **0.0642**
- `revol_util`: **0.0581**
- `home_ownership`: **0.0384**
- `purpose`: **0.0315**

The project configuration also documents IV interpretation bands.

The key insight is that `grade`, `sub_grade`, and `int_rate` are extremely strong predictors in this dataset.

That makes sense because they are not purely raw borrower fundamentals. They are closely tied to LendingClub’s own risk assessment and pricing.

This is why the project keeps two PD models rather than only one.

---

## 8. Model A versus Model B

The PD implementation is in `src/creditrisk/models/pd_model.py`.

The project fits logistic-regression scorecards on WoE-transformed features.

### Model A

Model A is the more fundamental borrower-characteristics model.

It uses seven attributes:

- `inq_last_6mths`
- `annual_inc`
- `purpose`
- `home_ownership`
- `term`
- `dti`
- `revol_util`

### Model B

Model B adds three LendingClub pricing/risk variables:

- `grade`
- `sub_grade`
- `int_rate`

So Model B uses ten attributes total.

Why is this comparison valuable?

Because it lets us answer two different questions.

Model A asks:

> How much rank-ordering power can I obtain from borrower and application fundamentals?

Model B asks:

> What happens when I also include the platform’s own risk grade and pricing information?

The answer from the OOT sample is clear.

Model A OOT Gini is about **0.2715**.

Model B OOT Gini is about **0.3845**.

So adding grade, sub-grade, and interest rate materially improves discrimination.

This is not magic.
It is telling us that LendingClub’s pricing and grading process already contains useful credit-risk information.

That is a valuable modelling lesson: a strong feature can be strong because it is a compact summary of other information.

But it also creates a governance question in a real underwriting setting: are these variables available at decision time, and are we comfortable relying on a pre-existing platform score or price as an input to our own model?

The project keeps both models, which makes that trade-off visible instead of hiding it.

---

## 9. Logistic regression from first principles

The project uses logistic regression for PD.

The model works with log-odds:

\[
\ln\left(rac{p}{1-p}ight)
=
eta_0 + \sum_j eta_j x_j
\]

where \(p\) is the estimated probability of default.

If the linear combination is large in the direction associated with default, the predicted PD rises.

If it moves in the opposite direction, PD falls.

The benefit of logistic regression in credit risk is not only statistical convenience.

It is also explainability.

For every input variable, we can inspect:

- the bin
- the WoE value
- the coefficient
- the contribution to log-odds
- the contribution to scorecard points

That gives a transparent chain from borrower characteristics to risk estimate.

The repository uses Statsmodels Logit for the primary scorecard fitting path, with support in the model class for scikit-learn logistic regression as well.

The output models are serialized under `outputs/models/`.

---

# Part III — Turning Probability Into a Score

## 10. Why scorecards use points

A raw PD such as 3.2% is statistically meaningful, but many lending organizations prefer an operational score.

Scores are easier to:

- set cutoffs on
- segment into grades
- explain to non-technical stakeholders
- embed into policy
- compare across time

The scorecard implementation is in `src/creditrisk/models/scorecard.py`.

The project uses:

- **Base score:** 600
- **Base odds:** 50:1
- **PDO:** 20 points

PDO means **points to double the odds**.

The factor is:

\[
Factor = rac{PDO}{\ln(2)}
\]

With PDO = 20:

\[
Factor pprox 28.8539
\]

The offset is:

\[
Offset =
BaseScore -
Factor 	imes \ln(BaseOdds)
\]

For this project:

\[
Offset pprox 487.123
\]

Then the score is derived from log-odds.

The important conceptual relationship is simple:

> Better odds of repayment correspond to a higher score, and worsening default odds push the score down.

Because the score is an affine transformation of log-odds, the ranking behavior of the logistic model is preserved.

---

## 11. Rating grades

The project turns the continuous score into an eight-grade master scale.

The source pack reports the following Model B ranges:

- Grade 1: 614–639
- Grade 2: 604–613
- Grade 3: 597–603
- Grade 4: 591–596
- Grade 5: 584–590
- Grade 6: 577–583
- Grade 7: 568–576
- Grade 8: 522–567

The empirical default rate rises as we move toward weaker grades.

That is exactly what we want from a useful rating scale.

A rating grade is not merely a pretty label.

It can support:

- underwriting policy
- pricing
- portfolio segmentation
- limit strategy
- collections prioritization
- provisioning analysis
- capital analysis
- monitoring

The source pack also frames Grade 8, below 568, as an underwriting referral or rejection interpretation.

I would present that carefully:

> In this project, the score-to-grade layer supports a decision-style interpretation, but this repository is not a live loan-origination system and should not be presented as an operational bank approval engine.

That distinction matters.

---

# Part IV — Validation: Does the Model Actually Work?

## 12. Discrimination and calibration are different questions

One of the most important ideas in model validation is that a model can rank risk well and still estimate probabilities badly.

Those are two separate questions.

**Discrimination asks:**
Can the model rank high-risk borrowers above low-risk borrowers?

**Calibration asks:**
If the model predicts 5%, do roughly 5% of those accounts actually default over the defined horizon?

The repository implements both categories of diagnostics.

The main validation file is `src/creditrisk/validation/metrics.py`.

The project calculates:

- AUROC
- Gini
- KS
- Brier score
- Hosmer-Lemeshow
- calibration adjustments

---

## 13. AUROC

Area Under the ROC Curve measures rank-ordering ability.

An intuitive interpretation is:

> If I randomly choose one default and one non-default, how often does the model rank the default as riskier?

An AUC of 0.5 corresponds to random ranking.

An AUC of 1.0 corresponds to perfect ranking.

The project reports for Model B:

- Train AUC: **0.683906**
- Test AUC: **0.681676**
- OOT AUC: **0.692260**

The OOT AUC is actually higher than the train AUC.

That can look surprising.

It does not automatically mean the OOT sample is “easier” in every sense, but the project truth gives a plausible interpretation: the 2014 vintage is differently seasoned and defaults may be more concentrated among higher-risk grades, sharpening rank-ordering in that particular sample.

The responsible conclusion is not “the model improves over time.”

The conclusion is:

> On this OOT vintage, discrimination remained stable and was slightly stronger than in development.

---

## 14. Gini

Credit-risk teams often express AUC as Gini:

\[
Gini = 2 	imes AUC - 1
\]

For Model B:

- Train Gini: **0.367812**
- Test Gini: **0.363352**
- OOT Gini: **0.384520**

For Model A:

- Train Gini: **0.301337**
- Test Gini: **0.296899**
- OOT Gini: **0.271451**

This comparison makes the incremental value of the extra Model B variables easy to see.

The OOT uplift is about 11.3 Gini points.

Again, that improvement comes from adding `grade`, `sub_grade`, and `int_rate`.

---

## 15. KS statistic

The Kolmogorov-Smirnov statistic measures the maximum separation between cumulative score distributions for defaults and non-defaults.

Model B OOT KS is approximately **0.284314**.

Model A OOT KS is approximately **0.195517**.

A higher KS indicates stronger separation between the two populations.

The repository does not use KS as a substitute for AUC or Gini.

It reports multiple diagnostics because no single metric tells the whole story.

---

## 16. Brier score and calibration

The Brier score evaluates squared error in predicted probabilities.

If I predict 0.20 and the outcome is 1, that is a large error.
If I predict 0.02 and the outcome is 0, that is a small error.

Because default is rare in this dataset, Brier scores are numerically small.

The source pack reports Model B OOT Brier around **0.032680**.

But calibration needs more than one summary number, so the project also includes the Hosmer-Lemeshow test.

---

## 17. Hosmer-Lemeshow and why large samples are tricky

The Hosmer-Lemeshow test compares observed and expected default frequencies across grouped probability buckets.

The project reports, for example:

- Model B Test HL p-value: **0.494183**
- Model B OOT HL p-value: **0.001166**

The test sample looks well calibrated under this diagnostic.
The OOT sample rejects the null much more strongly.

But the project truth correctly flags a key issue: with very large samples, tiny calibration differences can become statistically significant.

So the right interpretation is not simply:

> “Low p-value means the model is useless.”

Instead:

> The OOT sample shows statistically detectable calibration mismatch, and the test itself is sensitive at this sample size. We therefore also inspect mean calibration, Brier score, and recalibration behavior rather than relying on one test.

That is a more mature model-risk interpretation.

---

## 18. Recalibration

The project includes two probability-recalibration approaches in `src/creditrisk/models/calibration.py`:

- intercept recalibration
- Platt scaling

Intercept recalibration shifts the model’s baseline log-odds without changing rank ordering.

Platt scaling fits a logistic mapping on model scores or logits.

These tools are useful when discrimination remains acceptable but the observed portfolio default rate has shifted.

In production credit risk, this distinction is crucial.

Sometimes the relationship between borrowers is still rank-stable, but the entire portfolio becomes riskier or safer.

In that situation, recalibrating PD can be more appropriate than rebuilding the whole model.

---

# Part V — Stability and Monitoring

## 19. PSI: population stability

The project implements Population Stability Index in `src/creditrisk/validation/stability.py`.

Conceptually:

\[
PSI =
\sum_b
(Actual_b - Expected_b)
\ln\left(rac{Actual_b}{Expected_b}ight)
\]

The project compares train score distributions against the OOT 2014 population.

Reported values are:

- Model A score PSI: **0.004643**
- Model B score PSI: **0.007087**

Those values are small.

Within the project’s own interpretation framework, they indicate little distribution drift between the development score population and OOT.

That does not mean “there is no risk.”
It means the **score distribution** is relatively stable under this metric.

---

## 20. CSI: characteristic stability

Characteristic Stability Index applies a similar idea at feature level.

The repository calculates CSI across 17 attributes.

The source pack reports:

- highest CSI: `dti` at about **0.0416**
- lowest CSI: `annual_inc` at about **0.0057**

All are below the project’s stated 0.10 stability threshold.

The practical purpose is to answer:

> Has the borrower population changed in a way that could undermine model behavior?

If DTI distributions shift sharply, for example, the score distribution may eventually move even if the model coefficients remain fixed.

PSI tells me about the score population.
CSI helps me locate which input characteristics are moving.

---

# Part VI — LGD: What Happens After Default?

## 21. Why PD is only one part of risk

Two borrowers can have the same PD and still create very different losses.

Suppose both have a 5% chance of default.

Borrower A would leave the bank with a 20% loss if default occurs.
Borrower B would leave the bank with a 90% loss.

Those exposures are not economically equivalent.

That is why we need LGD.

\[
LGD = 1 - RecoveryRate
\]

The project builds LGD from the defaulted-loan population of **50,968 accounts**.

The main implementation is in `src/creditrisk/models/lgd_model.py`.

---

## 22. Why a one-stage regression is not ideal here

The observed recovery distribution is highly concentrated at zero recovery.

The project reports:

- mean LGD: about **93.01%**
- median LGD: **100%**
- about **52.18%** of defaulted accounts have 100% loss

That means the recovery process has two separate questions:

1. Will there be any recovery at all?
2. If there is recovery, how much?

Trying to force both questions into one ordinary regression is statistically awkward.

So the project uses a two-stage hurdle model.

---

## 23. The two-stage LGD hurdle model

### Stage 1: recovery incidence

A logistic classifier estimates:

\[
P(	ext{has recovery} = 1)
\]

This is a classification problem.

### Stage 2: recovery magnitude

For accounts with positive recovery, a Gradient Boosting Regressor estimates the conditional recovery rate:

\[
\hat{RR}_{positive}
\]

This is a regression problem.

### Combine the stages

Expected recovery becomes:

\[
E[RR]
=
P(	ext{recovery})
	imes
E[RR \mid 	ext{recovery}]
\]

Then:

\[
LGD
=
1 -
E[RR]
\]

This architecture is a strong example of how model design should follow the shape of the target distribution.

The project did not choose a two-stage model because it sounds advanced.
It chose one because zero-inflated recoveries create a natural hurdle.

---

# Part VII — EAD and CCF

## 24. Exposure at Default for term loans

For fixed-term LendingClub loans, the project calculates realized EAD from outstanding principal:

\[
EAD =
\max(
funded\_amnt - total\_rec\_prncp,
0
)
\]

The main implementation is in `src/creditrisk/models/ead_model.py`.

The OOT portfolio EAD reported by the source pack is approximately:

**$1.8266 billion**

For the defaulted-loan base, the project truth also reports average and median EAD statistics.

The key domain point is that EAD for a term loan is different from EAD for a revolving credit line.

---

## 25. Why the CCF module is synthetic

A credit card can have:

- current drawn balance
- unused limit

Before default, the borrower may draw additional funds.

So for revolving products, EAD often includes a Credit Conversion Factor:

\[
EAD =
Drawn +
CCF 	imes Undrawn
\]

LendingClub loans in this dataset are fixed-term loans, not revolving credit lines.

Therefore, the repo does **not** pretend it can estimate empirical revolving CCF from these loans.

Instead, `src/creditrisk/models/ccf_demo.py` creates a **synthetic 5,000-account revolving portfolio** and demonstrates an OLS-style CCF methodology.

This is one of the most important honesty points in the project.

The CCF model is implemented and executable, but it is a **demonstration**, not an empirical result from the LendingClub term-loan dataset.

A strong walkthrough should say that before an interviewer asks.

---

# Part VIII — Expected Loss

## 26. Bringing PD, LGD, and EAD together

At the most basic level:

\[
EL = PD 	imes LGD 	imes EAD
\]

If:

- PD = 4%
- LGD = 70%
- EAD = $10,000

then:

\[
EL = 0.04 	imes 0.70 	imes 10,000 = 280
\]

So the expected loss is $280.

But accounting frameworks do not always use one fixed PD horizon.

That is where lifetime PD and IFRS 9 enter.

---

# Part IX — Lifetime PD

## 27. From 12-month PD to a term structure

The project builds a discrete-time cumulative PD curve across months 1 to 60 in `src/creditrisk/regulatory/lifetime_pd.py`.

The source truth reports approximately:

- 1-month cumulative PD: **0.0806%**
- 12-month cumulative PD: **3.4352%**
- 24-month cumulative PD: **6.3462%**
- 36-month cumulative PD: **9.3156%**
- 60-month cumulative PD: **10.9306%**

The purpose is to move from a single one-year risk estimate to a horizon-dependent term structure.

Conceptually, if I am provisioning for a loan that may remain outstanding for several years, I need to consider default risk beyond month 12.

The project uses a discrete hazard and cumulative survival structure to build that lifetime curve.

The source truth also identifies a limitation: the lifetime PD curve is a portfolio-level hazard structure scaled to accounts rather than a full dynamic macro-conditioned hazard model.

That is a realistic place to say:

> This demonstrates the mechanics of lifetime PD, but a bank would typically build richer term structures by segment, macro scenario, and borrower state.

---

# Part X — IFRS 9 Staging

## 28. Why staging exists

IFRS 9 does not require the same provisioning horizon for every performing loan.

The framework distinguishes credit deterioration.

The project implements three stages in `src/creditrisk/regulatory/staging.py`.

### Stage 1

Performing exposures without significant increase in credit risk.

Provisioning basis: **12-month ECL**.

### Stage 2

Exposures with significant increase in credit risk.

Provisioning basis: **lifetime ECL**.

### Stage 3

Credit-impaired or defaulted exposures.

Provisioning basis: **lifetime ECL**, with default-type treatment.

The repository’s SICR logic includes:

- relative PD ratio threshold of **2.0x**
- absolute current PD threshold above **6%**
- 30+ DPD backstop
- Stage 3 default or 90+ DPD logic

These are project implementation rules.
They demonstrate SICR mechanics; they should not be presented as universal regulatory thresholds for every institution.

---

## 29. The Stage 1 / 2 / 3 portfolio

On the 2014 OOT portfolio, the project reports:

### Stage 1

- **189,633 accounts**
- about **80.48%**
- EAD about **$1.417B**
- ECL about **$30.27M**
- coverage about **2.14%**

### Stage 2

- **26,554 accounts**
- about **11.27%**
- EAD about **$169.37M**
- ECL about **$24.40M**
- coverage about **14.41%**

### Stage 3

- **19,441 accounts**
- about **8.25%**
- EAD about **$240.00M**
- ECL about **$223.80M**
- coverage about **93.25%**

Total portfolio:

- EAD about **$1.827B**
- IFRS 9 staged ECL about **$278.48M**
- coverage about **15.25%**

The stage-wise coverage ratios tell an intuitive story.

Stage 1 is low because these are performing exposures provisioned on a 12-month basis.

Stage 2 is much higher because lifetime risk is recognized after significant deterioration.

Stage 3 is extremely high because these are credit-impaired/defaulted exposures with very severe realized LGD behavior.

---

## 30. A limitation in the SICR implementation

The project truth explicitly states that historical point-in-time origination PDs are not preserved.

Therefore, the implementation uses a **grade-level average predicted PD proxy** for origination PD.

That means the relative PD ratio used in SICR is coarser than what a live bank system would normally use.

This is not a hidden flaw.

It is a data limitation and an implementation choice.

A real bank would ideally store the actual origination PD or score for each account and compare that with the current forward-looking PD.

---

# Part XI — IFRS 9 versus US CECL

## 31. The accounting difference

The project also compares IFRS 9 with US CECL.

In the project’s simplified implementation:

- IFRS 9 uses staging and 12-month versus lifetime ECL.
- CECL applies lifetime expected credit loss across performing exposures from day one.

The source pack reports:

- IFRS 9 ECL: about **$278.48M**
- CECL provision: about **$327.47M**
- difference: about **$48.99M**
- CECL coverage: about **17.93%**

This creates a useful teaching point.

Two accounting frameworks can use similar underlying risk quantities and still produce different provision timing because the recognition rules differ.

That is why credit-risk modelling is not only about statistical prediction.

The model output feeds accounting policy.

---

# Part XII — Macroeconomic Scenarios

## 32. Forward-looking ECL

IFRS 9 requires forward-looking information.

The project contains `config/macro_scenarios.yaml` and `src/creditrisk/regulatory/macro_scenarios.py`.

It defines three scenarios:

- Baseline: 50% weight
- Upside: 20% weight
- Downside: 30% weight

With project-specific PD multipliers:

- Baseline: 1.0x
- Upside: 0.85x
- Downside: 1.50x

But here the project truth gives an essential limitation.

The script `run_macro_scenarios.py` executes on a **three-loan test fixture**, not the entire 235,628-loan OOT portfolio.

So the correct claim is:

> The repo implements and executes scenario-weighted ECL mechanics as a micro-sample demonstration.

It would be incorrect to say that the reported full-portfolio ECL numbers are already generated by a full macro-scenario simulation over the entire OOT population.

A real bank extension would connect forward-looking macro variables to PD, LGD, or transition behavior through calibrated econometric relationships and run scenario-weighted lifetime ECL across the full portfolio.

---

# Part XIII — Basel III IRB Capital

## 33. Provisioning is not capital

This is an important conceptual transition.

Expected credit loss is about expected loss recognition.

Regulatory capital is about resilience against unexpected loss.

The project implements a Basel III Advanced IRB-style capital framework in `src/creditrisk/regulatory/basel_capital.py`.

The model uses:

- PD
- LGD
- EAD
- supervisory asset correlation
- a 99.9% tail-confidence transformation

to derive a capital factor and risk-weighted assets.

The repository reports:

- IRB RWA: about **$2.295B**
- average IRB risk weight: about **125.63%**
- minimum total capital at 8%: about **$183.57M**

The project also reports a standardized comparison:

- standardized RWA: about **$1.370B**
- standardized risk weight: **75%**
- total capital at 8%: about **$109.6M**

The IRB result is higher in this portfolio because the LGD assumption is extremely severe.

---

## 34. Downturn LGD stress

The repository also applies an **+8 percentage point downturn LGD add-on** as a stress demonstration.

That raises RWA to about **$2.454B**.

The total-capital increase is about **$12.74M**.

This is useful because it shows the sensitivity of regulatory capital to loss severity.

Again, in a real institution, downturn LGD would typically be empirically calibrated to recessionary recovery behavior rather than represented by a fixed add-on.

The project makes that limitation explicit.

---

# Part XIV — Portfolio Monitoring

## 35. Vintage analysis

The monitoring package includes `src/creditrisk/monitoring/vintage.py`.

Vintage analysis groups loans by origination cohort and observes cumulative default behavior by Months on Book, or MOB.

Why is that useful?

Imagine 2012 loans behave well, 2013 loans deteriorate, and 2014 loans deteriorate even faster.

That pattern can tell us:

- underwriting policy changed
- borrower mix changed
- acquisition channels changed
- pricing changed
- macro conditions changed

Vintage curves make the timing of credit deterioration visible.

The repo generates vintage MOB analytics and supporting output tables.

---

## 36. Roll-rate limitation

The repository also includes `roll_rates.py`.

But the source truth is explicit:

The raw LendingClub data is **cross-sectional**, not a longitudinal monthly panel.

Therefore the project cannot produce a true month-to-month DPD migration matrix such as:

Current → 30 DPD → 60 DPD → 90 DPD → cure

for the same account over consecutive monthly snapshots.

Instead, `roll_rates.py` creates a **cross-sectional delinquency distribution proxy by vintage**.

That is a demonstration of the concept, not a substitute for true longitudinal roll-rate modelling.

---

## 37. Transition matrix limitation

Similarly, `transitions.py` builds an **origination rating grade to final/resolution outcome transition matrix**.

That is useful, but it is not a monthly rating migration matrix.

The correct statement is:

> The repository implements a grade-to-outcome transition view using available snapshot data.

A real monitoring system would maintain account-level monthly state history and estimate empirical transition probabilities across states and time horizons.

---

# Part XV — Reporting and the Executive Risk View

## 38. Why reporting is part of the model system

A model is not complete when it produces a `.pkl` file.

A model has to be understood.

Risk committees care about:

- portfolio size
- default rate
- score distribution
- model performance
- calibration
- stability
- provisions
- capital
- stage movement
- exceptions
- limitations

The project includes a reporting layer under `src/creditrisk/reporting/`.

`dashboard_data.py` aggregates model outputs into a consolidated JSON structure.

`build_panels.py` renders a standalone interactive HTML application.

The final app is written to:

- `docs/index.html`
- `index.html`

The dashboard is self-contained from the perspective of application serving: it does not require a backend server.

The source pack describes Vanilla JavaScript and Chart.js via CDN for the frontend visualization layer.

So this is not a Next.js application.
It is a generated standalone HTML risk dashboard.

That distinction is important when presenting the architecture.

---

## 39. What the dashboard represents

The source pack describes panels for:

- executive risk committee views
- rating/master-scale exploration
- validation diagnostics
- IFRS 9 staging
- Basel III capital comparison
- pipeline DAG/data-flow visualization

The most important design idea is that the dashboard is generated from model output artifacts.

It is not manually typed presentation data.

That means the reporting layer is downstream of the analytics.

The build flow is roughly:

model and regulatory scripts
→ CSV tables and artifacts
→ dashboard payload
→ generated HTML application

The verified command is:

```powershell
.\.venv\Scripts\python.exe src/creditrisk/reporting/build_panels.py
```

The audit confirmed that this command completed successfully.

---

# Part XVI — The RAG Credit Analyst

## 40. What “AI” means in this repo

The repository uses classical statistical and machine-learning methods for core credit-risk modelling.

Generative AI is a separate layer under `src/creditrisk/ai/`.

The AI package contains:

- `rag_index.py`
- `retriever.py`
- `tools.py`
- `analyst.py`
- `run_analyst.py`

The repository creates vector embeddings from project documentation using `sentence-transformers/all-MiniLM-L6-v2`.

Those embeddings are persisted under `outputs/models/rag_index/`.

The retriever performs semantic similarity search over the indexed chunks.

Then the Credit Analyst can combine retrieved context with Gemini-based LLM interaction when an API key is available.

The project also includes deterministic/offline fallback behavior.

So the correct description is:

> The credit-risk models themselves are not generative AI. The generative-AI component is a RAG-based analyst interface layered on top of project documentation and exact output artifacts.

That is a much more precise claim than saying “the project is AI-driven.”

---

## 41. Live versus offline AI behavior

The audit verified the local vector index and offline retrieval components.

Live Gemini responses were not verified because they require:

`GEMINI_API_KEY`

The project truth therefore classifies the RAG analyst as running with manual steps for live LLM inference.

That is the right boundary to state.

---

# Part XVII — Repository Architecture

## 42. The repo as a layered system

At a high level:

```text
config/
    modelling, sampling, target, IFRS 9, macro, AI settings

datasets/
    raw LendingClub data

data/processed/
    train, test, OOT parquet partitions

src/creditrisk/data/
    schema, target, sampling, QA

src/creditrisk/features/
    WoE binning, IV

src/creditrisk/models/
    PD, scorecard, calibration, LGD, EAD, CCF demo

src/creditrisk/validation/
    AUC, Gini, KS, Brier, HL, PSI, CSI, plots

src/creditrisk/regulatory/
    lifetime PD, staging, ECL, CECL comparison, Basel capital, macro scenarios

src/creditrisk/monitoring/
    vintage, roll-rate proxy, transitions

src/creditrisk/reporting/
    dashboard payload + HTML generation

src/creditrisk/ai/
    RAG indexing, retrieval, tools, LLM analyst

tests/
    25 test modules

outputs/
    models, tables, figures, reports, vector index

docs/index.html
index.html
```

This organization mirrors the credit-risk lifecycle.

Data comes in.
Targets and eligible features are established.
Models are trained.
Models are validated.
Risk quantities are converted into accounting and capital measures.
Portfolio behavior is monitored.
Outputs are reported.
The AI layer provides a conversational interface over the evidence.

---

# Part XVIII — How I Would Walk the Repository in the IDE

## 43. Start with configuration, not the models

I would first open:

- `config/target_definition.yaml`
- `config/variables.yaml`
- `config/sampling.yaml`
- `config/pd_model.yaml`
- `config/ifrs9.yaml`
- `config/macro_scenarios.yaml`
- `config/ai.yaml`

Why?

Because configuration tells us the operating assumptions.

Before reading model code, I want to know:

- What is default?
- Which variables are allowed?
- What is the OOT period?
- What are scorecard parameters?
- What are SICR thresholds?
- What are scenario weights?

That creates the mental model.

---

## 44. Then inspect target and sampling

Next I would open:

- `src/creditrisk/data/target.py`
- `src/creditrisk/data/sampling.py`
- `src/creditrisk/data/schema.py`

At this point, I can explain:

- the dependent variable
- the time horizon
- the leakage boundary
- the development/OOT design

Only after that would I move to modelling.

---

## 45. Then feature engineering

Open:

- `src/creditrisk/features/binning.py`

Explain:

- fine/coarse grouping concept
- WoE
- IV
- missing values
- transformation into model-ready features

Then show `outputs/tables/iv_summary.csv` if available in the local repo.

---

## 46. Then PD and scorecard

Open:

- `src/creditrisk/models/pd_model.py`
- `src/creditrisk/models/scorecard.py`
- `src/creditrisk/models/run_pd_model.py`
- `src/creditrisk/models/run_scorecard.py`

Explain Model A and Model B.

Then trace outputs:

- model pickle
- coefficient table
- scorecard table
- rating grades

---

## 47. Then validation and stability

Open:

- `src/creditrisk/validation/metrics.py`
- `src/creditrisk/validation/stability.py`
- `src/creditrisk/models/calibration.py`

Explain the distinction between:

- discrimination
- calibration
- stability

Then connect to:

- AUC
- Gini
- KS
- Brier
- HL
- PSI
- CSI

This section is where the project moves from “I trained a model” to “I understand model risk.”

---

## 48. Then LGD and EAD

Open:

- `src/creditrisk/models/lgd_data.py`
- `src/creditrisk/models/lgd_model.py`
- `src/creditrisk/models/ead_model.py`
- `src/creditrisk/models/ccf_demo.py`

Explain:

- defaulted-loan recovery base
- hurdle modelling
- outstanding principal
- revolving versus term-loan EAD
- why CCF is synthetic

---

## 49. Then accounting and capital

Open:

- `src/creditrisk/regulatory/lifetime_pd.py`
- `src/creditrisk/regulatory/staging.py`
- `src/creditrisk/regulatory/ecl.py`
- `src/creditrisk/regulatory/macro_scenarios.py`
- `src/creditrisk/regulatory/basel_capital.py`

This is where I connect model outputs to financial consequences.

I would explain that PD is not an isolated ML target.

It becomes an input to:

- staging
- ECL
- CECL comparison
- IRB capital

That is the point at which the repository becomes a credit-risk system rather than simply a classification project.

---

## 50. Then monitoring and reporting

Open:

- `src/creditrisk/monitoring/vintage.py`
- `src/creditrisk/monitoring/roll_rates.py`
- `src/creditrisk/monitoring/transitions.py`
- `src/creditrisk/reporting/dashboard_data.py`
- `src/creditrisk/reporting/build_panels.py`

Then show the HTML output.

Explain what is genuinely longitudinal and what is only a cross-sectional proxy.

---

## 51. Finish with the AI layer

Open:

- `src/creditrisk/ai/rag_index.py`
- `src/creditrisk/ai/retriever.py`
- `src/creditrisk/ai/tools.py`
- `src/creditrisk/ai/analyst.py`

Explain the separation:

credit model engine
≠
LLM analyst

The LLM analyst is an interface over model knowledge and project artifacts.

---

# Part XIX — Testing and Reproducibility

## 52. The test suite

The audit reports:

**63 passed tests across 25 test modules**

The covered areas include:

- schema and leakage
- target engineering
- sampling
- WoE/IV
- PD model
- scorecard
- calibration
- validation metrics
- PSI/CSI
- LGD data and model
- EAD
- synthetic CCF
- lifetime PD
- IFRS 9 staging
- ECL
- expected loss
- Basel capital
- Basel reference checks
- macro scenarios
- vintage analytics
- transitions
- dashboard payload
- AI analyst
- RAG

That is valuable because it shows the repository is not only a notebook or a static set of charts.

The major analytic components have executable tests.

The verified test command is:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Result:

```text
63 passed, 1 warning in 156.36s
```

The warning relates to the upstream `google.generativeai` package deprecation.

---

## 53. Reproducibility boundary

The project truth notes:

- Python 3.11+
- raw dataset expected under `datasets/`
- raw CSV is excluded by `.gitignore`
- fixed random seeds are used
- no notebooks are required
- scripts resolve project paths relative to the repository
- dependencies are declared in `requirements.txt` and `pyproject.toml`

This is important because reproducibility is not the same as “clone and run with zero setup.”

The raw dataset is not committed.

A new user must obtain the dataset and place it in the expected location.

That is a normal and honest reproducibility boundary.

---

# Part XX — What Is Implemented, What Is Demonstrated, What Is a Proxy

## 54. Full implementations on the available data

The source pack classifies the following as implemented:

- 12-month target engineering
- WoE / IV binning
- PD Models A and B
- scorecard scaling
- model validation
- calibration tools
- PSI / CSI
- two-stage LGD
- realized EAD
- lifetime PD
- IFRS 9 staging and staged ECL
- CECL comparison
- Basel III IRB-style capital
- vintage analytics
- dashboard generation
- RAG vector analyst

These all have code and execution evidence.

---

## 55. Demonstrations

The repo explicitly treats the following as demonstrations:

### Revolving CCF

Synthetic 5,000-account portfolio.

Reason: LendingClub loans are fixed-term and do not contain undrawn revolving commitments.

### Multi-scenario macro ECL

The scenario mechanism executes on a three-loan fixture.

Reason: it demonstrates the methodology but is not a full-portfolio forward-looking macro engine.

### Expected-loss micro-sample script

Also demonstrated on a small fixture in the source truth.

These are still useful.
They simply should not be described as full-portfolio empirical results.

---

## 56. Cross-sectional proxies

### Roll-rate proxy

Built from snapshot delinquency distributions.

Not a true monthly migration matrix.

### Transition matrix

Origination grade to resolution outcome.

Not a monthly grade migration matrix.

This distinction is a strength because it shows awareness of what the data structure permits.

---

# Part XXI — What a Real Bank Would Add

## 57. Monthly account panel data

A bank would typically retain monthly snapshots with fields such as:

- current balance
- utilization
- arrears
- days past due
- delinquency bucket
- payment amount
- limit
- score
- rating
- cure status

That would enable true roll-rate and transition modelling.

---

## 58. Behavioral scorecards

This project is primarily anchored in origination/application-time credit risk.

A bank would also build behavioral models using post-origination account behavior.

Examples:

- recent missed payments
- balance growth
- utilization trends
- payment-to-balance ratio
- cash advances
- over-limit events
- internal transaction behavior

Behavioral models are important for account management, collections, limit decisions, and early warning.

---

## 59. Richer ECL macroeconomics

A production IFRS 9 system would usually include scenario-dependent macro variables such as:

- unemployment
- GDP
- interest rates
- house prices
- inflation
- sector-specific stress factors

Those variables would affect PD, LGD, transitions, or lifetime curves through calibrated relationships.

The current project demonstrates scenario weighting but does not claim that full econometric macro engine.

---

## 60. Empirical downturn LGD

The project uses a fixed +8pp stress add-on.

A real bank would estimate downturn LGD from recessionary recovery experience, collateral behavior, cure patterns, collection timelines, and possibly regulatory floors or policy overlays.

---

## 61. True origination PD history

A bank would store the exact score and PD assigned at origination.

That would make SICR comparisons account-specific.

The current repository uses a grade-level proxy because the original point-in-time PD history is unavailable.

---

## 62. Governance and approval workflow

A complete bank environment would add:

- model inventory
- model owner
- independent validation
- approval committees
- model change control
- challenger benchmarks
- periodic monitoring thresholds
- issue remediation
- data lineage
- audit trail
- production deployment controls
- access controls

The repository demonstrates many technical ingredients but is not a bank governance platform.

---

# Part XXII — Interview Defense

## 63. “Why logistic regression? Why not XGBoost?”

Because the project is not only optimizing predictive power.

It is demonstrating a transparent retail-credit-risk scorecard.

Logistic regression with WoE gives:

- understandable variable effects
- direct log-odds interpretation
- stable point scaling
- easy reason-code style decomposition
- strong governance transparency

A tree model may improve discrimination, but it changes the explainability and governance trade-off.

The project does use Gradient Boosting where the target shape makes it useful: the second stage of LGD recovery magnitude.

So the modelling philosophy is not “always use logistic regression.”

It is:

> Match the model architecture to the problem and the governance requirement.

---

## 64. “Why is Model B stronger?”

Because Model B adds `grade`, `sub_grade`, and `int_rate`.

Those fields already summarize part of LendingClub’s credit-risk assessment and pricing.

That is why Model B’s OOT Gini rises to about 0.3845 versus Model A’s 0.2715.

The result is intuitive and evidence-backed.

---

## 65. “Is 0.3845 Gini good?”

I would avoid giving a universal yes/no without context.

The useful answer is:

> It is materially better than Model A in this dataset and remains stable in the 2014 OOT cohort. Whether it is sufficient for a production credit decision depends on product, portfolio, economics, reject inference, policy, benchmark models, calibration, and governance standards.

That is stronger than quoting a generic threshold.

---

## 66. “Your OOT HL test fails. Is calibration broken?”

The OOT HL p-value is low.

That indicates statistically detectable mismatch in grouped observed versus expected defaults.

However, the sample is extremely large, and HL is sensitive to sample size.

So I would inspect:

- observed-to-predicted default rate
- Brier score
- calibration plot
- bucket-level deviations
- intercept recalibration
- stability

The project includes recalibration tools for exactly this reason.

---

## 67. “Why is LGD so high?”

The empirical portfolio is unsecured and has weak recoveries after default.

About 52.18% of defaulted accounts have zero recovery, producing median LGD of 100%.

That is why a hurdle model is appropriate.

I would also add that this is a property of this dataset and its recovery definitions, not a universal LGD for all consumer lending.

---

## 68. “Why is CCF synthetic?”

Because the primary data is fixed-term LendingClub loans.

There is no undrawn revolving commitment.

Rather than fake an empirical CCF estimate, the repo separates:

- realized EAD on term loans
- a synthetic revolving CCF demonstration

That is a data-appropriate design choice.

---

## 69. “Why can’t you show real roll rates?”

Because a true roll-rate matrix requires longitudinal monthly states for the same account.

The dataset is a snapshot.

The repo therefore builds a cross-sectional delinquency proxy and grade-to-outcome transitions instead.

A bank implementation would require monthly panel history.

---

## 70. “Why use 2014 as OOT?”

Because 2014 is the latest origination vintage in the source data used by the repository.

The development sample uses 2007–2013 and 2014 is held out.

There is no 2015 vintage in the dataset.

---

## 71. “Why is IRB risk weight higher than the 75% standardized comparison?”

Because the project’s IRB calculation is sensitive to the severe LGD profile.

Mean LGD is about 93%, so the IRB formula produces an average risk weight around 125.63%.

The standardized comparison uses a flat 75% weight.

The point of the comparison is to show how internal risk parameters can drive capital away from a flat benchmark.

---

# Part XXIII — A Complete End-to-End Narrative

## 72. The system in one flow

Now I can tell the whole project as one continuous chain.

A raw LendingClub loan enters the dataset with origination, borrower, bureau, pricing, and later performance fields.

The first task is not modelling.
The first task is defining the target.

The target engine determines whether the account is an ever-default and whether default occurs inside a 12-month performance window.

Then schema governance separates origination-time features from post-outcome features so the PD model cannot cheat with future information.

The data is divided temporally.

2007–2013 becomes the development cohort.
That cohort is split into train and test.
2014 is held out as out-of-time validation.

Application variables are binned.
Each bin receives a Weight of Evidence transformation.
Information Value helps quantify feature strength.

Two PD scorecards are then fitted.

Model A uses borrower/application fundamentals.
Model B adds LendingClub grade, sub-grade, and interest rate.

Both are logistic regression models on WoE features.

The logistic coefficients are converted into a 600-point score using a 20-point PDO scale and 50:1 base odds.

Scores are grouped into eight rating grades.

The models are validated using AUC, Gini, KS, Brier score, Hosmer-Lemeshow calibration tests, and recalibration tools.

Then stability is checked using PSI on scores and CSI on input characteristics between the development and OOT populations.

PD tells us how likely default is.

For severity, the project takes the 50,968 ever-defaulted accounts and models LGD.

Because recoveries are zero-inflated, it uses a two-stage hurdle architecture: first estimate whether any recovery occurs, then estimate the amount of recovery conditional on positive recovery.

EAD for the term loans is based on outstanding principal.

A separate synthetic CCF module demonstrates how revolving-line EAD could be estimated when undrawn limits exist.

PD, LGD, and EAD combine into expected loss.

The repository then builds a 60-month lifetime PD term structure so it can move beyond a one-year horizon.

That term structure feeds IFRS 9 staging.

Stage 1 uses 12-month ECL.
Stage 2 uses lifetime ECL after significant increase in credit risk.
Stage 3 represents credit-impaired/defaulted exposures.

The OOT portfolio produces about $278.48M of staged IFRS 9 ECL.

The same portfolio is also compared under a CECL-style lifetime provisioning approach, producing a higher provision of about $327.47M.

A macro-scenario module demonstrates baseline, upside, and downside scenario weighting on a small test fixture.

The Basel capital layer takes risk parameters into an IRB-style unexpected-loss framework.

Because LGD is severe, the project produces IRB RWA of about $2.295B and total capital at 8% of about $183.57M.

A downturn LGD stress increases that requirement further.

Portfolio monitoring then looks at score stability, attribute stability, vintage default behavior, cross-sectional delinquency proxies, and grade-to-outcome transitions.

Finally, reporting scripts aggregate model outputs into a standalone interactive HTML dashboard.

A RAG-based Credit Analyst sits on top of project documentation and output artifacts, enabling semantic retrieval and optional Gemini-based conversational interaction.

That is the system.

It begins with raw loan records and ends with an interpretable set of risk measures, accounting provisions, regulatory capital analytics, monitoring outputs, executive reporting, and a conversational analysis layer.

---

# Part XXIV — Exact Numbers Worth Memorizing

You do not need to memorize every number in the repository.

But the following are useful anchors:

### Portfolio

- 466,285 raw loans
- 75 raw attributes
- 50,968 ever defaults
- 10.93% ever-default rate
- 16,018 12-month defaults
- 3.44% 12-month default rate

### Development design

- 230,657 development loans, 2007–2013
- 184,525 train
- 46,132 test
- 235,628 OOT loans, 2014

### PD Model B

- OOT AUC: 0.692260
- OOT Gini: 0.384520
- OOT KS: 0.284314
- Test HL p-value: 0.494183
- OOT HL p-value: 0.001166

### Stability

- Model B PSI: 0.007087
- maximum CSI approximately 0.0416

### LGD

- 50,968 defaulted accounts
- mean LGD: ~93.01%
- median LGD: 100%
- 52.18% zero-recovery / 100%-loss accounts

### IFRS 9

- Stage 1: 189,633 accounts
- Stage 2: 26,554 accounts
- Stage 3: 19,441 accounts
- OOT portfolio EAD: ~$1.827B
- IFRS 9 ECL: ~$278.48M
- portfolio coverage: ~15.25%

### CECL

- CECL provision: ~$327.47M
- delta versus IFRS 9: ~$48.99M

### Basel

- IRB RWA: ~$2.295B
- average IRB risk weight: ~125.63%
- minimum total capital at 8%: ~$183.57M
- downturn RWA: ~$2.454B

### QA

- 63 tests passed
- 25 test modules
- dashboard build command verified

---

# Part XXV — What Not to Claim

## 73. Do not call this a live production bank platform

It is a production-structured portfolio project with executable code and generated artifacts.

It is not connected to a live core banking system.

---

## 74. Do not claim empirical revolving CCF from LendingClub

The CCF module is synthetic.

---

## 75. Do not claim true monthly roll-rate matrices

The dataset is cross-sectional.

The project uses proxies.

---

## 76. Do not claim OOT 2015

OOT is 2014.

---

## 77. Do not claim full-portfolio macroeconomic scenario ECL

The scenario script is demonstrated on a three-loan fixture.

---

## 78. Do not describe the core scorecard as generative AI

The core PD model is classical logistic regression on WoE features.

The generative AI component is the RAG analyst layer.

---

# Part XXVI — Why This Project Matters

This project is useful because it connects four levels that are often shown separately.

### Level 1: Statistical modelling

- logistic regression
- WoE
- IV
- gradient boosting
- calibration
- PSI/CSI

### Level 2: Credit-risk domain

- PD
- LGD
- EAD
- scorecards
- vintages
- default windows
- recovery

### Level 3: Finance and regulation

- IFRS 9
- CECL
- lifetime PD
- SICR
- staged ECL
- Basel IRB
- RWA
- capital

### Level 4: Engineering

- package structure
- configuration
- parquet partitions
- serialized models
- generated artifacts
- tests
- dashboard build
- RAG index

The project becomes much stronger when all four layers are explained together.

---

# Part XXVII — A Short Version I Can Say in an Interview

“I built a Python retail-credit-risk system on 466,285 LendingClub loans. I first engineered a 12-month default target and enforced anti-leakage rules so only origination-time variables could enter PD modelling. I split 2007–2013 as development and held 2014 out for OOT validation.

I then built WoE-binned logistic scorecards. The stronger Model B adds LendingClub grade, sub-grade, and interest rate and achieved a 0.3845 OOT Gini and 0.2843 KS. I scaled the model into a 600-point scorecard with PDO 20 and eight rating grades, then validated discrimination, calibration, and stability using AUC, Gini, KS, Brier, Hosmer-Lemeshow, PSI, and CSI.

For loss severity, I built a two-stage hurdle LGD model because more than half of defaults had zero recoveries. EAD is outstanding principal for the term loans, while revolving CCF is demonstrated separately on synthetic data because the LendingClub portfolio has no undrawn lines.

From there I extended the system into a 60-month lifetime PD curve, IFRS 9 staging and ECL, CECL comparison, and Basel III IRB-style capital. The 2014 OOT portfolio has about $1.827B EAD, about $278.48M IFRS 9 ECL, and about $2.295B IRB RWA. Finally, I added vintage and stability monitoring, a generated HTML risk dashboard, and a RAG-based credit analyst over the project documentation and outputs.

The key thing is that I distinguish carefully between what is implemented on the full dataset, what is demonstrated on synthetic or micro-sample data, and what would require richer bank production data such as monthly account panels.”

---

# Part XXVIII — The “God Mode” Understanding

At expert level, the project is not really about one model.

It is about **measurement discipline across a credit lifecycle**.

A scorecard is only meaningful if:

- the target is defined correctly
- feature timing is controlled
- sampling is time-aware
- discrimination is validated
- calibration is monitored
- population drift is understood

PD is only economically meaningful when paired with:

- loss severity
- exposure
- time horizon

Expected loss is only financially meaningful when mapped to:

- accounting recognition rules
- lifetime versus 12-month horizons
- deterioration logic
- scenario weighting

Capital is only meaningful when separated from expected loss and interpreted as protection against unexpected stress.

Monitoring is only meaningful when the data structure supports the claim being made.

And reporting is only trustworthy when it traces back to reproducible model artifacts.

That is the real story of the repository.

It is a demonstration of how retail credit risk becomes a system:

**data → target → eligible features → scorecard → validation → stability → loss severity → exposure → lifetime risk → provisioning → capital → monitoring → reporting → analyst interface**

Once you understand that chain, the individual Python files stop looking like isolated modules.

They become different layers of the same risk-management problem.

---

# Appendix A — Verified execution commands

```powershell
# Activate environment
.\.venv\Scripts\Activate.ps1

# Test suite
.\.venv\Scripts\python.exe -m pytest

# Rebuild dashboard
.\.venv\Scripts\python.exe src/creditrisk/reporting/build_panels.py
```

The audit result was:

```text
63 passed, 1 warning in 156.36s
```

---

# Appendix B — Main pipeline commands

```powershell
python src/creditrisk/data/run_target_generation.py
python src/creditrisk/data/run_sampling.py

python src/creditrisk/features/run_binning.py

python src/creditrisk/models/run_pd_model.py
python src/creditrisk/models/run_scorecard.py

python src/creditrisk/validation/run_validation.py
python src/creditrisk/models/run_calibration.py
python src/creditrisk/validation/run_stability.py

python src/creditrisk/models/run_lgd_training.py
python src/creditrisk/models/ccf_demo.py

python src/creditrisk/regulatory/run_lifetime_pd.py
python src/creditrisk/regulatory/run_staging.py
python src/creditrisk/regulatory/run_ecl.py
python src/creditrisk/regulatory/run_basel_capital.py
python src/creditrisk/regulatory/run_macro_scenarios.py

python src/creditrisk/monitoring/run_monitoring.py
python src/creditrisk/monitoring/run_transitions.py

python src/creditrisk/reporting/build_panels.py
```

---

# Appendix C — High-value files to know

| File | Why it matters |
|---|---|
| `config/variables.yaml` | Defines application-time versus outcome fields and leakage boundaries |
| `config/target_definition.yaml` | Defines default-status and performance-window assumptions |
| `config/sampling.yaml` | Defines development and OOT split logic |
| `config/pd_model.yaml` | Scorecard configuration and feature-selection rules |
| `config/ifrs9.yaml` | Staging and SICR thresholds |
| `config/macro_scenarios.yaml` | Scenario weights and PD multipliers |
| `src/creditrisk/data/schema.py` | Anti-leakage guardrails |
| `src/creditrisk/data/target.py` | 12-month default target |
| `src/creditrisk/data/sampling.py` | Train/test/OOT partitioning |
| `src/creditrisk/features/binning.py` | WoE and IV engine |
| `src/creditrisk/models/pd_model.py` | PD logistic-regression implementation |
| `src/creditrisk/models/scorecard.py` | PDO/base-score scaling and rating grades |
| `src/creditrisk/models/calibration.py` | Recalibration tools |
| `src/creditrisk/models/lgd_model.py` | Two-stage LGD hurdle model |
| `src/creditrisk/models/ead_model.py` | Outstanding-principal EAD |
| `src/creditrisk/models/ccf_demo.py` | Synthetic revolving CCF demonstration |
| `src/creditrisk/validation/metrics.py` | AUC, Gini, KS, Brier, HL |
| `src/creditrisk/validation/stability.py` | PSI and CSI |
| `src/creditrisk/regulatory/lifetime_pd.py` | 60-month cumulative PD term structure |
| `src/creditrisk/regulatory/staging.py` | IFRS 9 staging and SICR |
| `src/creditrisk/regulatory/ecl.py` | Staged ECL and CECL comparison |
| `src/creditrisk/regulatory/basel_capital.py` | IRB-style RWA and capital |
| `src/creditrisk/monitoring/vintage.py` | MOB vintage analytics |
| `src/creditrisk/monitoring/roll_rates.py` | Cross-sectional delinquency proxy |
| `src/creditrisk/monitoring/transitions.py` | Grade-to-outcome matrix |
| `src/creditrisk/reporting/dashboard_data.py` | Reporting payload assembly |
| `src/creditrisk/reporting/build_panels.py` | Standalone HTML app builder |
| `src/creditrisk/ai/rag_index.py` | Embedding index generation |
| `src/creditrisk/ai/retriever.py` | Semantic retrieval |
| `src/creditrisk/ai/analyst.py` | Credit Analyst LLM integration |

---

# Appendix D — Final mental model

If I had to compress the entire project into one diagram, it would be:

```text
Public LendingClub data
        ↓
Target engineering
        ↓
Leakage-safe feature universe
        ↓
Temporal development / OOT split
        ↓
WoE + IV
        ↓
Logistic PD scorecard
        ↓
600-point scale + rating grades
        ↓
Discrimination + calibration validation
        ↓
PSI / CSI stability
        ↓
LGD hurdle model + EAD
        ↓
Expected Loss
        ↓
Lifetime PD
        ↓
IFRS 9 staging + ECL
        ↓
CECL comparison
        ↓
Basel IRB-style capital
        ↓
Vintage / proxy monitoring
        ↓
Generated HTML reporting
        ↓
RAG Credit Analyst
```

That is the project from zero to god mode.


---

# Appendix E — Variable-by-Variable Credit-Risk Intuition

This appendix is designed for the moment when someone points at a field and asks, “Why should this matter for credit risk?”

The explanations below stay anchored to the variables explicitly documented in the walkthrough source pack. They are not an attempt to invent a complete bank data dictionary beyond the repository.

## `loan_amnt`

This is the amount requested or funded for the loan.

At first glance it may seem obvious that larger loans are riskier, but that is not automatically true. A $25,000 loan to a high-income borrower may be safer than a $5,000 loan to a highly leveraged borrower.

So the important modelling question is not only loan size in isolation. It is how loan size interacts with borrower capacity, term, payment burden, and the risk profile of the applicant.

In the project, `loan_amnt` is treated as a candidate PD feature and WoE-binned.

## `term`

This captures loan tenor, such as 36 versus 60 months.

A longer term changes risk in several ways.

The borrower remains exposed to unemployment, illness, income shocks, and other changes for longer. The loan also amortizes more slowly, so exposure can remain outstanding for longer.

The project includes `term` in both Model A and Model B.

Its IV is materially stronger than many ordinary borrower variables in the source pack, which is consistent with tenor carrying useful risk information in this dataset.

## `int_rate`

Interest rate is especially important in Model B.

It is not simply a borrower characteristic. It also reflects how LendingClub priced the loan.

That means it can contain embedded information from the platform’s own risk assessment.

This explains why adding `int_rate` together with `grade` and `sub_grade` improves Model B.

A real-world governance question would be whether the organization wants its own model to depend on a pre-existing pricing output. In this repository, the point of Model A versus Model B is precisely to make that distinction visible.

## `installment`

Monthly installment is the contractual payment amount.

Economically, installment burden matters because borrowers have to service that cash outflow every month.

But installment by itself is incomplete.

A $1,000 monthly installment can be manageable for one borrower and impossible for another.

That is why affordability concepts often combine payment obligations with income or existing debt burden.

In this project, installment is documented as a candidate PD feature rather than one of the final Model A/B core variables.

## `grade`

`grade` is LendingClub’s coarse credit grade, A through G.

It is a strong feature because it summarizes a prior credit-risk assessment.

The source pack reports IV around 0.4357, placing it among the strongest predictors in the project.

Model B includes it.
Model A intentionally does not.

## `sub_grade`

`sub_grade` is the finer-grained version of grade, such as A1 through G5.

It is the strongest IV feature reported in the source pack, around 0.4482.

That makes intuitive sense because it contains finer resolution than the broad grade.

Again, because it is itself a risk-ranking output from LendingClub, its strength must be interpreted as partially carrying information from an upstream credit process.

## `emp_length`

Employment length proxies stability of employment history.

The relationship with credit risk is rarely perfectly monotonic.

Very short employment can signal instability, but long tenure does not guarantee low default risk.

Missing employment information can itself behave differently from observed categories.

The project therefore bins this variable rather than assuming a simple linear relationship.

## `home_ownership`

Home ownership categories include states such as rent, own, and mortgage.

This field can proxy household balance-sheet structure and financial stability, but it should never be interpreted causally from the scorecard alone.

The project includes `home_ownership` in both Model A and Model B.

The source pack notes that renters show higher risk in the project’s binning interpretation.

## `annual_inc`

Annual income represents repayment capacity.

Higher income can generally support larger obligations, but raw income is highly skewed and not perfectly comparable across households, geographies, and debt burdens.

That is why income becomes much more meaningful when interpreted with DTI, installment, loan size, and other credit attributes.

The project WoE-bins `annual_inc` and uses it in both Model A and Model B.

## `verification_status`

This indicates the income-verification category.

A naive expectation might be that “verified” should always mean safer.

But the source pack explicitly notes a counterintuitive risk direction caused by selection effects.

Higher-risk or more complex borrowers may be more likely to receive verification in the first place.

This is a good example of why model relationships should be observed empirically rather than imposed from intuition.

## `purpose`

Loan purpose captures the stated use of funds.

Different purposes can have different risk behavior because they reflect different borrower needs and financial circumstances.

The project groups purpose categories through WoE binning and includes the variable in both Model A and Model B.

The source pack identifies small-business purpose as a higher-risk segment in this dataset.

## `dti`

Debt-to-income ratio is one of the clearest affordability variables in the project.

It measures existing debt burden relative to income.

Higher DTI means less income headroom remains after debt commitments.

The project reports `dti` as a medium-strength IV variable and uses it in both PD models.

It also has the highest CSI among the documented monitoring variables, though still below the project’s stated stability threshold.

## `delinq_2yrs`

This captures recent delinquency history.

Past delinquency can contain information about repayment behavior.

However, the project does not automatically include every predictive bureau field in the final scorecard.

`delinq_2yrs` is documented as a candidate feature rather than a final Model A/B field.

That separation is important: predictive plausibility does not mean every feature survives final model design.

## `inq_last_6mths`

This measures recent hard-credit inquiries.

High inquiry activity can represent active credit seeking.

The project uses it in both Model A and Model B.

Its IV is weaker than the LendingClub grade/pricing variables but still useful.

## `revol_util`

Revolving utilization measures the proportion of revolving credit capacity currently used.

High utilization can indicate financial pressure or limited remaining liquidity.

The project uses `revol_util` in both PD models.

Again, binning is useful because risk may accelerate at high utilization levels rather than changing linearly.

## `revol_bal`

This is the absolute revolving balance.

Its meaning depends heavily on income, limits, and utilization.

A high balance can be entirely manageable for one borrower and severe for another.

The project documents it as a candidate feature rather than a final Model A/B variable.

## `total_acc`

This is total credit lines in the bureau file.

A very thin credit file can create uncertainty, while a very large number of accounts can also reflect complex leverage.

The project treats it as a candidate feature.

## `out_prncp`

Outstanding principal is post-origination information.

That means it is not a valid PD origination feature.

But it is economically important downstream for exposure and staging.

This is exactly why schema governance matters: a field can be valuable to the credit-risk system while still being forbidden from the PD model.

## `total_rec_prncp`

Total principal received is also an outcome field.

It enters realized EAD and LGD calculations.

Using it in an origination PD model would leak future repayment behavior.

The project’s architecture correctly keeps PD modelling eligibility separate from loss-severity and exposure calculations.

## `recoveries`

Recoveries are post-default cash collections.

They are central to LGD because loss severity depends on how much value can be recovered after default.

They are also an obvious leakage variable for origination PD.

This one field demonstrates why “feature importance” and “feature eligibility” are not the same thing.

---

# Appendix F — Model Metrics From First Principles

## AUROC

The ROC curve plots:

- true positive rate
- against false positive rate

across classification thresholds.

AUC summarizes the area under that curve.

The strength of AUC is threshold independence.

The model does not need one arbitrary approval cutoff for us to assess whether it ranks risk correctly.

## Gini

Gini is a linear transformation of AUC:

\[
Gini = 2AUC - 1
\]

So if AUC is 0.69226:

\[
Gini \approx 0.38452
\]

This is exactly the relationship seen for Model B OOT.

## KS

KS looks for the point of maximum cumulative separation between default and non-default score distributions.

Where AUC summarizes ranking across the full curve, KS highlights the strongest separation point.

## Brier score

For binary outcome \(y_i\) and predicted probability \(p_i\):

\[
Brier = \frac{1}{N}\sum_i(p_i-y_i)^2
\]

It is a proper probability-scoring rule.

A model that ranks perfectly but gives wildly exaggerated probabilities can still have poor probability accuracy.

## Hosmer-Lemeshow

The HL procedure groups observations into probability bands and compares observed versus expected events.

Its strength is interpretability.

Its weakness, especially in this project, is sensitivity to sample size.

With more than 235,000 OOT observations, small deviations can create very low p-values.

That is why the project uses multiple validation measures rather than treating HL as the only calibration test.

## PSI and CSI

PSI compares the distribution of a score or variable between a reference population and a later population.

CSI applies the same stability idea at characteristic level.

These are not performance metrics in the same sense as AUC.

A model can have low PSI and still be poorly calibrated.
A model can have high PSI and still rank well for a period.

Monitoring requires several lenses.

---

# Appendix G — Credit-Risk Concepts Behind the Code

## Application risk versus behavioral risk

The project’s PD scorecard is largely an application-risk framework.

It uses information available around origination.

A behavioral scorecard would instead use post-booking performance information.

That distinction explains why fields like payment history are excluded from PD even though they are powerful indicators of later default.

## Point-in-time versus through-the-cycle thinking

The source materials do not claim a full TTC/PIT model architecture, so this project should not be presented as implementing one.

But the distinction is useful SME context.

Point-in-time risk responds more strongly to current borrower and economic conditions.

Through-the-cycle risk is designed to be more stable across the cycle.

The project’s OOT validation and macro-scenario modules touch adjacent problems, but they do not establish a formal PIT/TTC framework.

## Expected loss versus unexpected loss

Expected loss belongs to the provisioning/economic-loss side:

\[
EL = PD \times LGD \times EAD
\]

Unexpected loss is the tail uncertainty around that expectation.

The Basel IRB-style capital module addresses the second problem by applying a stressed quantile transformation rather than simply multiplying PD, LGD, and EAD.

This is why provisioning and capital should not be conflated.

## Calibration versus rank ordering

This distinction is one of the most interview-important ideas in the entire project.

Imagine two borrowers:

- Borrower A has true risk around 2%.
- Borrower B has true risk around 8%.

A model predicting 4% and 12% ranks them correctly but is miscalibrated upward.

A model predicting 1% and 3% also ranks them correctly but is miscalibrated downward.

Gini/AUC can remain strong in both cases.

Provisioning, however, will be wrong.

That is why calibration matters especially when PD is used as an economic quantity rather than only as a ranking score.

## Stability versus accuracy

A stable model can still be inaccurate.

A drifting model can still temporarily be accurate.

PSI and CSI answer “has the population changed?”

AUC, Gini, KS answer “does the model separate risk?”

Calibration metrics answer “are the probabilities numerically aligned with outcomes?”

These are complementary questions.

---

# Appendix H — A Presenter’s Full Repository Tour Checklist

When recording a detailed walkthrough video, use this order so the narrative remains coherent.

## 1. Start at repository root

Show:

- `README.md`
- `PROJECT_TRUTH_retail-credit-risk.md`
- `pyproject.toml`
- `requirements.txt`
- `standing_rules.md`

Explain that the project truth document exists to keep portfolio claims aligned with executable evidence.

## 2. Show configuration

Open the YAML files and explain that many methodological decisions live outside hard-coded model functions.

Talk through:

- target definition
- variables
- sampling
- PD model
- IFRS 9
- macro scenarios
- AI config

## 3. Show data organization

Point out:

- raw dataset location
- processed parquet partitions
- outputs directory

Explain why raw data, processed data, models, tables, figures, and reports are separated.

## 4. Show `src/creditrisk/data`

Start with schema and leakage.

Then target.

Then sampling.

This establishes methodological correctness before modelling.

## 5. Show `src/creditrisk/features`

Explain WoE and IV.

Show the IV output table.

## 6. Show `src/creditrisk/models`

Start with PD.

Then scorecard.

Then calibration.

Then LGD.

Then EAD.

End with CCF and explicitly label it synthetic.

## 7. Show `src/creditrisk/validation`

Explain AUC, Gini, KS, Brier, HL, PSI, CSI.

Show the validation summary output.

## 8. Show `src/creditrisk/regulatory`

Move from lifetime PD to staging to ECL to CECL comparison to Basel capital.

This is the key business bridge from model output to finance.

## 9. Show `src/creditrisk/monitoring`

Explain vintage analytics first.

Then explain why roll-rate and transition views are proxies because of snapshot data.

## 10. Show `src/creditrisk/reporting`

Explain how output tables become dashboard payloads and then HTML.

Open the generated app.

## 11. Show `src/creditrisk/ai`

Explain retrieval and Gemini integration separately from the credit models.

Do not imply that the PD/LGD engine is generative AI.

## 12. Show tests last

Open `tests/`.

Explain that the audit ran the full suite and obtained 63 passes.

Then finish by showing the command that rebuilds the dashboard.

That gives the walkthrough a satisfying end:

**methodology → models → finance → monitoring → reporting → reproducibility.**

---

# Appendix I — Final Expert Summary

The deepest lesson from this project is that credit risk is not one prediction problem.

It is a chain of linked estimation and governance problems.

The 12-month target defines what PD means.

Schema rules define what information the model is allowed to know.

Temporal splitting defines whether validation resembles future use.

WoE and IV convert raw borrower variables into an interpretable scorecard representation.

Logistic regression estimates rank and probability.

Score scaling makes the model operationally consumable.

AUC, Gini, and KS test discrimination.

Brier and Hosmer-Lemeshow test probability behavior.

Recalibration handles baseline-risk shifts without necessarily rebuilding ranking logic.

PSI and CSI test population stability.

LGD estimates severity after default.

EAD estimates the money exposed at default.

Lifetime PD extends risk across contractual time.

IFRS 9 maps risk deterioration into accounting horizons.

CECL changes the timing of lifetime recognition.

Basel IRB-style capital converts risk parameters into a tail-loss capital framework.

Vintage analytics monitors cohort behavior.

Roll-rate and transition proxies demonstrate what can be done with snapshot data while making clear what cannot be done without monthly panels.

The dashboard converts technical artifacts into an executive view.

The RAG analyst converts repository evidence into a conversational interface.

And the test suite ties the whole system back to executable behavior.

That is why the repository should be presented not as “a machine-learning model,” but as a **retail credit-risk modelling and analytics system with explicit methodological boundaries**.
