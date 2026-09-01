# Model Development Document — Retail Unsecured Credit Risk Suite

**Document reference:** MDD-RCR-001  
**Version:** 1.0  
**Classification:** Internal — Model Risk Management  
**Review cycle:** Annual (or upon material model change)  
**Regulatory alignment:** SR 11-7 (Federal Reserve / OCC Model Risk Management Guidance)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Model Purpose and Scope](#2-model-purpose-and-scope)
3. [Data](#3-data)
4. [PD Model](#4-pd-model)
5. [LGD Model](#5-lgd-model)
6. [EAD / CCF](#6-ead--ccf)
7. [Basel III Capital Calculation](#7-basel-iii-capital-calculation)
8. [IFRS 9 ECL Calculation](#8-ifrs-9-ecl-calculation)
9. [Ongoing Monitoring Framework](#9-ongoing-monitoring-framework)
10. [AI Analyst Overlay](#10-ai-analyst-overlay)
11. [Limitations and Assumptions](#11-limitations-and-assumptions)
12. [Governance and Version Control](#12-governance-and-version-control)

---

## 1. Executive Summary

This document describes the retail unsecured credit risk model suite built on the LendingClub public dataset (2007-2014, 466,285 issued loans). The suite produces the three Basel parameter estimates -- Probability of Default (PD), Loss Given Default (LGD), and Exposure at Default (EAD) -- and uses them as inputs to two downstream capital and provisioning engines: a **Basel III IRB capital** calculator and an **IFRS 9 / CECL Expected Credit Loss (ECL)** engine.

The production PD model (Model B) is a logistic regression on Weight-of-Evidence (WoE)-transformed features, scaled to a scorecard with points-to-double-odds calibration. On the 2014 out-of-time (OOT) validation cohort (235,628 loans), it achieves a **Gini coefficient of 0.3845** and **AUC of 0.6923**. The LGD model is a fractional response regression on resolved defaults; portfolio mean LGD is **0.930** (93.0%). EAD uses observed drawdown ratios (mean CCF 0.719 overall).

Portfolio-level results on the 235,628 loan OOT cohort:

| Metric | Value |
|---|---|
| Total EAD | $1,826,572,642 |
| Basel 12-month Expected Loss (EL) | $58,666,169 (3.21% of EAD) |
| Basel IRB Risk-Weighted Assets (RWA) | $2,294,666,891 |
| Average IRB Risk Weight | 125.6% |
| IFRS 9 ECL (scenario-weighted) | $285,037,851 (15.61% of EAD) |
| CECL Provision (US GAAP) | $327,465,235 (17.93% of EAD) |

---

## 2. Model Purpose and Scope

### 2.1 Intended Use

| Component | Purpose | Primary Consumer |
|---|---|---|
| PD Model | Score-rank obligors; estimate 12-month probability of default | Originations decisioning, capital, IFRS 9 staging |
| LGD Model | Estimate loss rate conditional on default | EL calculation, Basel capital, ECL provisioning |
| EAD / CCF | Estimate exposure at time of default from drawn balance | EL calculation, capital, ECL provisioning |
| Basel Capital Engine | Compute IRB and Standardised RWA; minimum capital requirements | Regulatory capital reporting |
| IFRS 9 / CECL Engine | Compute staged ECL under three economic scenarios | Financial statement provisioning |

### 2.2 Out-of-Scope Statements

The following uses are **explicitly not supported** by this model suite:

- **Pricing or originations cut-off decisions in production.** The suite is a demonstration on historical data; it has not been through a bank-grade change-management and deployment process.
- **Stress testing / DFAST / CCAR.** Macroeconomic scenario conditioning is limited to IFRS 9 scalar PD multipliers; full macro-econometric sensitivity is out of scope.
- **Revolving / secured products.** The data and calibration cover unsecured personal instalment loans only.
- **Regulatory submissions without independent validation.** SR 11-7 requires an independent model validation before any regulatory capital submission.
- **Real-time scoring.** No real-time inference pipeline exists; the suite is batch-oriented.

---

## 3. Data

### 3.1 Source

**Dataset:** LendingClub Loan Data (publicly available on Kaggle)  
**Vintage coverage:** April 2007 - September 2014  
**Raw loans:** 466,285  
**Product type:** Unsecured personal instalment loans (36-month and 60-month terms)

### 3.2 Target Definition

The outcome variable is **12-month default**, defined as: the loan status is `Charged Off`, `Default`, or `Does Not Meet the Credit Policy: Status: Charged Off` within 12 months of the observation month.

**Rationale for 12-month window.** LendingClub's `last_pymnt_d` field represents the date of the most recent payment, which provides a reliable proxy for default timing. A 12-month window aligns with Basel III's prescribed PD horizon for retail exposures (BCBS para 4.4) and with the IFRS 9 Stage 1 measurement horizon. Shorter windows produce insufficient defaults in early vintages; longer windows introduce material right-censoring for 2013-2014 originations.

### 3.3 Target Sensitivity

| Window | Default Rate |
|---|---|
| 12 months (selected) | 3.44% |
| Ever-default (lifecycle) | 8.25% (2014 vintage, partial maturity) |

Vintage-level 12-month default rates range from 3.18% (2013) to 6.56% (2008 financial crisis), confirming cyclicality in the book.

### 3.4 Train / Test / OOT Split

| Sample | N Loans | Defaults | Default Rate | Period |
|---|---|---|---|---|
| Train | 184,525 | 6,329 | 3.43% | Apr-2008 - Sep-2013 |
| Test | 46,132 | 1,582 | 3.43% | Apr-2008 - Sep-2013 |
| Out-of-Time (OOT) | 235,628 | 8,107 | 3.44% | Apr-2014 - Sep-2014 |

Train/test are a stratified 80/20 random split within the pre-2014 population. OOT is the entire 2014 origination cohort held completely out of model development -- it represents a true temporal hold-out, testing the model on a different economic period.

### 3.5 Leakage Controls

A schema validation guard (`schema.py`) enforces that no post-origination fields (payment history, account balance updates, delinquency timestamps, etc.) are available at scoring time. Only origination-time fields are permitted as model inputs. This guard runs as a pre-processing step in all training pipelines and raises an exception if any post-origination column is detected in the feature set.

---

## 4. PD Model

### 4.1 Methodology Overview

The PD model uses **Weight of Evidence (WoE) binning** followed by **logistic regression**. WoE transforms each predictor into a monotone binned numeric encoding:

```
WoE_bin = ln(Distribution_Events_bin / Distribution_Non-Events_bin)
```

This encoding handles non-linearity and missing values natively (missing gets its own bin), produces bounded inputs suitable for logistic regression, and makes coefficient signs interpretable: all coefficients are negative (higher WoE = lower credit risk = higher score).

**Two candidate models** were developed:

| Model | Features | Train AUC | Test AUC | OOT AUC | OOT Gini | HL p-value (test) |
|---|---|---|---|---|---|---|
| Model A | 7 | 0.6507 | 0.6484 | 0.6357 | 0.2715 | 0.236 |
| **Model B** | **10** | **0.6839** | **0.6817** | **0.6923** | **0.3845** | **0.494** |

**Decision: Model B is deployed.** It outperforms Model A on all metrics, including the OOT cohort (OOT AUC 0.6923 vs 0.6357), demonstrating superior generalisation to unseen data. Critically, Model B's Hosmer-Lemeshow p-value on test (0.494) fails to reject the null hypothesis of calibration, indicating well-calibrated probabilities. Model A's HL p-value of 0.236 on test is borderline.

### 4.2 Feature Selection

Variables were screened by **Information Value (IV)**:

| Variable | IV | Strength |
|---|---|---|
| `grade` | 0.294 | Medium |
| `int_rate` | 0.277 | Medium |
| `inq_last_6mths` | 0.076 | Weak |
| `sub_grade` | 0.074 | Weak |
| `annual_inc` | 0.060 | Weak |
| `purpose` | 0.051 | Weak |
| `home_ownership` | 0.034 | Weak |
| `dti` | 0.023 | Weak |
| `term` | 0.025 | Weak |
| `revol_util` | 0.021 | Weak |

No variable exceeded the conventional "strong" threshold of IV > 0.50, which is expected: LendingClub's own internal grade already captures much of the default signal. The ten selected variables collectively capture diverse dimensions of credit risk (bureau-derived grade, pricing signal via interest rate, utilisation behaviour, income, purpose, tenure, and revolving credit usage).

### 4.3 Model B Coefficients

All coefficients are **negative**, confirming the expected directional relationship: higher WoE -> lower default risk -> higher score.

| Variable | Coefficient | Std Error | p-value | Significant |
|---|---|---|---|---|
| `const` | -3.3384 | 0.0135 | < 0.001 | Yes |
| `grade` | -0.6177 | 0.0660 | < 0.001 | Yes |
| `int_rate` | -0.2358 | 0.0699 | < 0.001 | Yes |
| `inq_last_6mths` | -0.7480 | 0.0458 | < 0.001 | Yes |
| `sub_grade` | -0.1068 | 0.0626 | 0.088 | No |
| `annual_inc` | -0.9202 | 0.0583 | < 0.001 | Yes |
| `purpose` | -0.7180 | 0.0577 | < 0.001 | Yes |
| `home_ownership` | -0.4658 | 0.0753 | < 0.001 | Yes |
| `term` | -0.0168 | 0.0907 | 0.853 | No |
| `dti` | -0.4887 | 0.0861 | < 0.001 | Yes |
| `revol_util` | -0.2239 | 0.0948 | 0.018 | Yes |

`sub_grade` and `term` are not individually significant at the 5% level but are retained because: (i) they contribute information in conjunction with correlated variables (`grade`, `int_rate`); (ii) removal degrades OOT Gini; (iii) the collinearity is expected and documented.

### 4.4 Scorecard Scaling

The logistic regression score is transformed to a traditional credit scorecard using **points-to-double-odds (PDO) scaling**:

```
Score = Offset + Factor x ln(p / (1 - p))

Factor = PDO / ln(2)
Offset = Target_Score - Factor x ln(Target_Odds)
```

The scorecard is calibrated so that **score 600 corresponds to odds of 50:1** (1 default per 50 goods) with **20 points-to-double-odds**. The resulting score range in the OOT cohort is 522-639.

### 4.5 Rating Grade Master Scale

Model B scores are mapped to an internal 8-grade master scale:

| Grade | Score Range | N Loans | Observed Default Rate |
|---|---|---|---|
| 1 (Best) | 614-639 | 21,930 | 0.86% |
| 2 | 604-613 | 23,998 | 1.34% |
| 3 | 597-603 | 22,475 | 1.94% |
| 4 | 591-596 | 21,074 | 2.52% |
| 5 | 584-590 | 24,353 | 3.08% |
| 6 | 577-583 | 22,564 | 4.31% |
| 7 | 568-576 | 23,203 | 5.19% |
| 8 (Worst) | 522-567 | 24,928 | 7.72% |

The monotone relationship between grade and observed default rate confirms scorecard rank-ordering.

### 4.6 PD Model Validation Results

| Dataset | AUC | Gini | KS | Brier Score |
|---|---|---|---|---|
| Train | 0.6839 | 0.3678 | 0.2736 | 0.0326 |
| Test | 0.6817 | 0.3634 | 0.2728 | 0.0326 |
| **OOT** | **0.6923** | **0.3845** | **0.2843** | **0.0327** |

The OOT Gini (0.3845) **exceeds** the in-sample Gini (0.3678), indicating the model has not overfit. The KS statistic of 0.2843 on OOT confirms meaningful separation. Brier score consistency across all samples (0.0326-0.0327) confirms probability calibration is stable across time periods.

### 4.7 Lifetime PD Term Structure

From the Kaplan-Meier survival function estimated on the full 466,285 loan population:

| Month | Cumulative PD |
|---|---|
| 1 | 0.08% |
| 6 | 0.70% |
| 12 | 3.44% |
| 18 | 6.70% |
| 24 | 8.82% |
| 36 | 10.64% |
| 48 | 10.88% |
| 60 | 10.93% |

The 12-month cumulative PD of 3.44% matches the OOT observed default rate exactly, validating the survival model calibration. The plateau from month 36-60 reflects loan maturity: most defaults occur in the first 24 months, and the hazard rate drops near zero after month 36.

---

## 5. LGD Model

### 5.1 Definition

LGD measures the fraction of EAD lost in the event of default:

```
LGD = 1 - Recovery Rate
Recovery Rate = Total Post-Default Recoveries / EAD at Default
```

### 5.2 Data

**Defaulted population:** 50,968 loans with resolved outcomes (status `Charged Off` or `Default`).
Only 3 loans had zero EAD at default and were excluded (EAD cannot be zero denominator).

### 5.3 Distribution

| Statistic | Value |
|---|---|
| Mean LGD | 0.930 |
| Median LGD | 1.000 |
| Std Dev | 0.110 |
| Fraction total loss (LGD = 1.0) | 52.2% |
| Fraction zero loss (LGD = 0.0) | 0.35% |
| Fraction with any post-default recovery | 47.8% |

The **median LGD of 1.0** reflects the structural characteristic of unsecured personal loans: the majority of defaulted loans recover nothing. Roughly half of defaulters (47.8%) achieve some recovery, keeping the mean LGD at 0.930 rather than 1.0.

### 5.4 Methodology

A **fractional response regression (FRR)** is used, appropriate for outcomes bounded on [0, 1] with mass at the boundaries. The model specification is:

```
E[LGD | X] = G(X'beta)
```

where G(.) is the logistic link function. Predictors include loan amount, term, interest rate, sub-grade, and the ratio of recoveries to funded amount.

### 5.5 Calibration -- Decile Analysis

| Decile | N | Mean Predicted LGD | Mean Actual LGD | Abs Error |
|---|---|---|---|---|
| 1 (lowest LGD) | 1,020 | 0.9065 | 0.9148 | 0.0082 |
| 2 | 1,019 | 0.9178 | 0.9177 | 0.0001 |
| 3 | 1,019 | 0.9226 | 0.9230 | 0.0004 |
| 4 | 1,020 | 0.9262 | 0.9248 | 0.0014 |
| 5 | 1,019 | 0.9294 | 0.9244 | 0.0049 |
| 6 | 1,019 | 0.9323 | 0.9352 | 0.0028 |
| 7 | 1,020 | 0.9354 | 0.9313 | 0.0041 |
| 8 | 1,019 | 0.9387 | 0.9368 | 0.0019 |
| 9 | 1,019 | 0.9429 | 0.9437 | 0.0008 |
| 10 (highest LGD) | 1,020 | 0.9498 | 0.9524 | 0.0026 |

The model is **well-calibrated across all deciles**, with absolute errors below 1 percentage point in every bucket. Rank-ordering is preserved.

### 5.6 LGD by Lending Club Grade

| Grade | Mean PD | Mean LGD | EL Rate |
|---|---|---|---|
| A | 1.10% | 93.44% | 0.97% |
| B | 2.05% | 93.57% | 1.74% |
| C | 3.54% | 93.68% | 2.97% |
| D | 5.05% | 93.32% | 4.23% |
| E | 6.31% | 92.52% | 5.30% |
| F | 8.35% | 92.03% | 6.91% |
| G | 8.23% | 92.07% | 7.10% |

LGD is marginally lower for higher-risk grades (Grade A 93.44% vs Grade G 92.07%). Higher-risk borrowers tend to carry 60-month loans and default earlier relative to their loan term, when outstanding balances are a larger fraction of funded amount but recoveries are proportionally similar.

### 5.7 Downturn LGD Adjustment (Basel III)

Basel III IRB requires a "downturn" LGD conservative relative to the long-run average. An **8 percentage point add-on** is applied:

| Approach | Mean LGD | IRB RWA | Risk Weight | Min Capital (8%) |
|---|---|---|---|---|
| Average LGD | 0.9339 | $2,294,666,891 | 125.6% | $183,573,351 |
| Downturn LGD (+8pp) | 0.9992 | $2,453,921,077 | 134.3% | $196,313,686 |
| **Delta** | +6.5pp | +$159,254,186 | +8.7pp | +$12,740,335 |

The downturn add-on increases minimum capital by approximately $12.7 million (6.9%).

---

## 6. EAD / CCF

### 6.1 Definition

For drawn instalment loans, EAD equals the outstanding balance at time of default:

```
EAD = Outstanding_Balance_at_Default
CCF = EAD / Funded_Amount  (Credit Conversion Factor)
```

CCF is the fraction of the originally funded amount that remains outstanding at default, reflecting the amortisation that has occurred prior to the default event.

### 6.2 CCF Observations by Segment

| Segment | Mean EAD | Median EAD | Mean CCF | Median CCF |
|---|---|---|---|---|
| **Overall** | **$10,782** | **$9,141** | **0.719** | **0.769** |
| 36-month term | $7,765 | $6,379 | 0.662 | 0.702 |
| 60-month term | $16,233 | $15,482 | 0.823 | 0.859 |

60-month loans have materially higher CCF (0.823 vs 0.662) because they amortise more slowly: a default at month 18 leaves a much larger outstanding balance on a 5-year loan than on a 3-year loan.

By grade (defaulted loans):

| Grade | Mean EAD | Mean CCF |
|---|---|---|
| A | $7,466 | 0.608 |
| B | $8,098 | 0.639 |
| C | $9,858 | 0.708 |
| D | $11,189 | 0.744 |
| E | $14,299 | 0.802 |
| F | $15,880 | 0.834 |
| G | $17,438 | 0.847 |

Higher-risk grades show higher CCF, reflecting that riskier borrowers tend to carry 60-month loans.

> **Note on CCF Regression:** A synthetic linear regression CCF model (intercept 0.198, utilisation coefficient 0.475) is included as a demonstration only (marked SYNTHETIC in `SYNTHETIC_ccf_summary.csv`). The production EAD estimates use **observed drawdown ratios directly**. The regression model requires validation on a revolving product before production use.

---

## 7. Basel III Capital Calculation

### 7.1 Framework

The Basel III IRB capital formula for retail exposures (BCBS paragraph 4.4) is:

```
K = LGD x N[(1-R)^(-0.5) x G(PD) + (R/(1-R))^0.5 x G(0.999)] - PD x LGD

Where:
  R   = Correlation = 0.03 x (1-exp(-35xPD))/(1-exp(-35))
                    + 0.16 x [1-(1-exp(-35xPD))/(1-exp(-35))]
  N() = Standard normal CDF
  G() = Standard normal inverse CDF
  K   = Capital requirement (fraction of EAD)
  RWA = K x 12.5 x EAD
```

The Standardised Approach uses a flat 75% risk weight for all retail exposures (BCBS paragraph 3.6).

### 7.2 Portfolio Capital Summary

| Grade | EAD ($M) | IRB RWA ($M) | IRB Risk Weight | Std RWA ($M) |
|---|---|---|---|---|
| A | 221.2 | 208.4 | 94.2% | 165.9 |
| B | 389.7 | 449.9 | 115.5% | 292.3 |
| C | 508.1 | 659.3 | 129.7% | 381.1 |
| D | 403.0 | 547.8 | 135.9% | 302.3 |
| E | 215.9 | 300.4 | 139.2% | 161.9 |
| F | 66.5 | 96.6 | 145.3% | 49.9 |
| G | 22.2 | 32.3 | 145.7% | 16.6 |
| **Total** | **1,826.6** | **2,294.7** | **125.6%** | **1,369.9** |

### 7.3 Minimum Capital Requirements

Based on IRB RWA of $2,294,666,891:

| Requirement | Rate | Amount |
|---|---|---|
| Total Minimum Capital (Pillar 1) | 8.0% | $183,573,351 |
| Minimum Tier 1 Capital | 6.0% | $137,680,013 |
| Minimum CET1 Capital | 4.5% | $103,260,010 |

The IRB approach generates **68% more RWA** than the Standardised approach ($2,295M vs $1,370M). This is expected for a high-LGD retail unsecured book: the IRB formula is sensitive to LGD, and with mean LGD of 0.934, the per-loan capital requirement is substantial.

---

## 8. IFRS 9 ECL Calculation

### 8.1 Framework

IFRS 9 requires a **three-stage** ECL measurement approach based on significant increases in credit risk (SICR) since origination:

| Stage | Population | ECL Horizon | Trigger |
|---|---|---|---|
| Stage 1 | Performing, no SICR | 12-month ECL | No SICR detected |
| Stage 2 | Performing, SICR detected | Lifetime ECL | PD_12m > 7.64% threshold |
| Stage 3 | Credit-impaired (defaulted) | Lifetime ECL | Default state |

**SICR threshold:** A loan migrates from Stage 1 to Stage 2 when its model PD_12m exceeds **7.64%** (the portfolio 85th percentile of PD, a common industry proxy for SICR).

### 8.2 Staging Results

| Stage | N Loans | % Portfolio | EAD ($M) | % EAD | Mean PD_12m |
|---|---|---|---|---|---|
| Stage 1 | 189,633 | 80.5% | 1,417.2 | 77.6% | 2.73% |
| Stage 2 | 26,554 | 11.3% | 169.4 | 9.3% | 7.64% |
| Stage 3 | 19,441 | 8.3% | 240.0 | 13.1% | 100% |
| **Total** | **235,628** | **100%** | **1,826.6** | **100%** | -- |

### 8.3 ECL by Stage

| Stage | EAD ($M) | ECL ($M) | Coverage Ratio |
|---|---|---|---|
| Stage 1 | 1,417.2 | 30.3 | 2.14% |
| Stage 2 | 169.4 | 24.4 | 14.41% |
| Stage 3 | 240.0 | 223.8 | 93.25% |
| **Total** | **1,826.6** | **278.5** | **15.25%** |

Stage 3 coverage of 93.25% reflects the high LGD for defaulted unsecured loans.

### 8.4 Economic Scenario Weighting

IFRS 9 requires ECL to be probability-weighted across multiple forward-looking economic scenarios:

| Scenario | PD Multiplier | Weight | Scenario ECL ($M) | ECL as % EAD |
|---|---|---|---|---|
| Upside | 0.85x | 20% | 270.3 | 14.80% |
| Baseline | 1.00x | 50% | 278.5 | 15.25% |
| Downside | 1.50x | 30% | 305.8 | 16.74% |
| **Probability-Weighted (Reported)** | -- | **100%** | **285.0** | **15.61%** |

The reported IFRS 9 ECL of **$285,037,851** reflects the scenario-weighted expected loss. The baseline ECL of $278.5M is uplifted by 2.4% when the downside scenario is folded in.

### 8.5 IFRS 9 vs CECL Comparison

| Framework | Horizon | ECL ($M) | Coverage |
|---|---|---|---|
| Basel 12m EL | 12-month | 58.7 | 3.21% |
| IFRS 9 (Staged, scenario-weighted) | Mixed (12m/Lifetime) | 285.0 | 15.61% |
| US GAAP CECL (ASC 326) | Lifetime (Day-1, all loans) | 327.5 | 17.93% |
| CECL vs IFRS 9 Delta | Lifetime Stage 1 uplift | 48.6 | +2.66pp |

CECL requires a Day-1 lifetime provision for **all** performing loans (no staging), which explains the incremental $48.6M vs IFRS 9.

---

## 9. Ongoing Monitoring Framework

### 9.1 Population Stability Index (PSI)

| Model | Score PSI | Stability Band |
|---|---|---|
| Model A | 0.0046 | Stable (< 0.10) |
| **Model B** | **0.0071** | **Stable (< 0.10)** |

Both models are well within the "stable" threshold (PSI < 0.10). PSI in the range 0.10-0.25 triggers enhanced monitoring; PSI > 0.25 requires model redevelopment.

### 9.2 Characteristic Stability Index (CSI) -- Model B

| Variable | CSI | Stability |
|---|---|---|
| `dti` | 0.0416 | Stable |
| `purpose` | 0.0362 | Stable |
| `int_rate` | 0.0315 | Stable |
| `grade` | 0.0293 | Stable |
| `sub_grade` | 0.0264 | Stable |
| `term` | 0.0258 | Stable |
| `revol_util` | 0.0140 | Stable |
| `home_ownership` | 0.0101 | Stable |
| `inq_last_6mths` | 0.0087 | Stable |
| `annual_inc` | 0.0057 | Stable |

All variables are stable (CSI < 0.10). No variable shows evidence of population shift between the development and OOT samples.

### 9.3 Vintage Performance Monitoring

| Vintage | 12m Default Rate | 18m Default Rate | 24m Default Rate |
|---|---|---|---|
| 2007 | 5.14% | 13.93% | 19.40% |
| 2008 | 6.56% | 11.41% | 15.25% |
| 2009 | 4.64% | 7.33% | 9.88% |
| 2010 | 3.45% | 6.17% | 8.32% |
| 2011 | 3.55% | 6.51% | 8.97% |
| 2012 | 3.73% | 7.17% | 10.19% |
| 2013 | 3.18% | 6.34% | 9.29% |
| 2014 | 3.44% | 6.77% | 8.14% |

The 2007-2008 vintages show elevated default rates attributable to the global financial crisis. Post-2009 vintages stabilise in the 3-4% 12-month range. Default rates plateau after approximately month 36 for all vintages.

### 9.4 Recommended Monitoring Schedule

| Metric | Frequency | Action Threshold |
|---|---|---|
| Score PSI | Monthly | PSI > 0.10: enhanced review; > 0.25: redevelopment |
| CSI by variable | Quarterly | CSI > 0.10: investigate; > 0.25: redevelop feature |
| Gini / AUC (recent originations) | Quarterly | Gini drop > 5pp from baseline: validation review |
| Hosmer-Lemeshow calibration | Semi-annual | p-value < 0.05: recalibration required |
| LGD back-test (actual vs predicted) | Annual | Mean abs error > 3pp: LGD recalibration |
| Vintage curves | Monthly | 12m rate > 2x expected: escalation to CRO |

---

## 10. AI Analyst Overlay

### 10.1 Purpose

An experimental AI-assisted analyst (`src/creditrisk/ai/analyst.py`) is included as a decision-support tool. It is **not a model** for regulatory capital or provisioning purposes. It performs two functions:

1. **Regulatory Q&A (RAG):** Answers questions about Basel III and IFRS 9 regulations by retrieving relevant passages from a local vector index built over the knowledge-base PDFs (`rag_index.py`). Uses `all-MiniLM-L6-v2` embeddings (sentence-transformers, fully local, no API calls for retrieval).

2. **Quantitative analysis:** Answers portfolio-level capital and ECL questions by calling pre-built Python tools (`tools.py`) that wrap the Basel capital formula and ECL engine with live portfolio data.

### 10.2 Architecture

```
User Question
     |
     +-- RAG Retriever (cosine similarity, threshold >= 0.30)
     |    +-- Regulatory passages from knowledge_base/ PDFs
     |
     +-- Gemini Function-Calling
          +-- tool: calculate_basel_capital(pd, lgd, ead, ...)
          +-- tool: calculate_ecl(pd, lgd, ead, stage, ...)
          +-- tool: get_portfolio_summary()
```

A **relevance guardrail** (cosine similarity threshold 0.30) prevents the model from generating regulatory citations when no sufficiently relevant passage exists. Questions below threshold receive a "no regulatory context found" response rather than a hallucinated answer.

### 10.3 Configuration

Model name is configured in `config/ai.yaml` as `gemini_model: "gemini-flash-latest"`. If the configured model returns HTTP 404, the analyst automatically lists available models supporting `generateContent` and prompts the user to update the config.

### 10.4 Limitations

- The AI analyst must **not** be used to make regulatory capital or provisioning decisions without human expert review.
- RAG retrieval covers only the curated local knowledge base; it does not access live regulatory updates.
- Function-calling tool results are deterministic (they call Python model functions directly), but the natural-language wrapper is probabilistic. Always verify numerical outputs against `outputs/tables/`.

---

## 11. Limitations and Assumptions

### 11.1 Data Limitations

| Limitation | Implication |
|---|---|
| Single platform (LendingClub only) | Model may not generalise to other unsecured lenders with different underwriting standards |
| US consumer loans | Geographic scope restricted to US; capital calibration not validated for other jurisdictions |
| Historical data 2007-2014 | Model trained pre-2015; post-2015 structural changes (fintech, COVID credit cycle, rate environment) not reflected |
| No full bureau data | True creditworthiness signals proxied by platform-assigned `grade` and `int_rate` |
| Right-censoring | 2014 vintage loans have only 6 months of observed performance in OOT; lifetime default rates estimated from survival curves |

### 11.2 Modelling Assumptions

| Assumption | Justification |
|---|---|
| Constant LGD across time | LGD estimated on resolved defaults; no time-variation in recovery rates modelled |
| PD independence across loans | Logistic regression assumes independence; systematic credit cycle effects not explicitly modelled |
| EAD = Outstanding Balance | For fully drawn instalment loans this is exact; no undrawn commitments exist |
| SICR threshold is percentile-based | 85th percentile PD is an industry proxy; a bank would calibrate to their own book |
| IFRS 9 discount rate = EIR | ECL computed at the Effective Interest Rate; actual EIR requires contractual cash flow modelling |
| CCF regression is synthetic | CCF linear regression uses synthetic training data; not applied to production EAD estimates |

### 11.3 Out-of-Scope Risks

- **Concentration risk:** The IRB formula does not capture concentration risk; a Pillar 2 ICAAP would be required.
- **Operational risk:** Not modelled.
- **Market / ALM risk:** Not modelled.
- **Behavioural risk (prepayment):** No prepayment model; early repayment reduces actual EAD below projected.

---

## 12. Governance and Version Control

### 12.1 SR 11-7 Model Risk Management Alignment

| SR 11-7 Requirement | Implementation |
|---|---|
| Model definition and purpose | Sections 1-2 define model purpose, intended use, and scope |
| Conceptual soundness | Sections 4-8 document methodology, assumptions, and economic rationale |
| Data quality and integrity | Section 3 documents data sourcing, target construction, split rationale, and leakage controls |
| Ongoing monitoring | Section 9 defines monitoring metrics, frequencies, and escalation thresholds |
| Model limitations | Section 11 explicitly enumerates data and methodological limitations |
| Outcome analysis / back-testing | OOT validation (AUC, Gini, KS, HL test, LGD decile analysis) in Sections 4-5 |

### 12.2 Items Requiring Independent Validation Before Production Use

The following must be completed by an independent model validation function before use for regulatory capital reporting or financial statement provisioning:

1. **Independent replication:** Recreate model outputs from raw data using the documented methodology
2. **Challenger model assessment:** Develop and benchmark at least one alternative PD specification
3. **Sensitivity analysis:** Stress key assumptions (LGD +/-10pp, SICR threshold +/-2pp)
4. **Calibration back-test:** Validate predicted vs observed default rates on a further hold-out (post-2014 if available)
5. **Governance sign-off:** CRO / Chief Model Risk Officer approval documented in model inventory

### 12.3 File Structure

| Path | Description |
|---|---|
| `src/creditrisk/pd/` | PD feature engineering, WoE binning, model training |
| `src/creditrisk/lgd/` | LGD data preparation, fractional response regression |
| `src/creditrisk/ead/` | EAD / CCF calculation |
| `src/creditrisk/capital/` | Basel III IRB and Standardised RWA |
| `src/creditrisk/ifrs9/` | IFRS 9 staging, ECL engine, CECL comparison |
| `src/creditrisk/ai/` | RAG index, AI analyst, CLI |
| `src/creditrisk/reporting/` | Dashboard data assembly, HTML report |
| `outputs/tables/` | All model output CSVs (source of truth for this document) |
| `outputs/reports/` | dashboard_data.json, risk_dashboard.html |
| `knowledge_base/` | Regulatory PDFs indexed by the RAG system |
| `config/ai.yaml` | AI model configuration |
| `docs/MODEL_DOCUMENTATION.md` | This document |

### 12.4 Change Log

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0 | 2026-07-24 | Model Development Team | Initial release |

---

*All numerical values are sourced directly from `outputs/tables/*.csv` and `outputs/reports/dashboard_data.json`. No figures have been estimated or invented.*
