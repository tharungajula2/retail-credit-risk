# Retail Credit Risk — SME Companion & Domain Mapping

This companion document maps the implementation evidence in `retail-credit-risk` directly to fundamental banking, econometric, regulatory, and credit-risk domain principles. It provides the exact bridge needed to explain **what the code does** alongside **the underlying domain theory behind it**.

---

## 1. Project-to-SME Mapping Matrix

| Project Concept | Repo Evidence | SME Concept | Why It Matters | Real-World Bank Extension |
|---|---|---|---|---|
| **PD Target Window** | [`src/creditrisk/data/target.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/data/target.py#L65) | 12-Month Performance Window | Basel III (BCBS para 447) and IFRS 9 require a standard 12-month horizon for point-in-time default estimation. | Banks use multi-year observation windows for lifetime PD modeling under Stage 2 IFRS 9. |
| **WoE Feature Classing** | [`src/creditrisk/features/binning.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/features/binning.py#L35) | Monotonic Log-Odds Transformation | Transforms non-linear continuous and categorical features into monotonic linear log-odds ratios for logistic regression. | Handles missing data as distinct credit risk categories without imputation bias. |
| **Information Value (IV)** | [`outputs/tables/iv_summary.csv`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/outputs/tables/iv_summary.csv) | Predictive Feature Screening | Quantifies discriminatory strength per feature before model fitting, screening out weak or overfitted variables. | Enforces strict IV thresholds (0.02 - 0.50) in model governance validation. |
| **Scorecard PDO Scaling** | [`src/creditrisk/models/scorecard.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/scorecard.py#L20) | Logit Points-to-Double-Odds Alignment | Converts log-odds coefficients into integer points (PDO=20, Base 600 @ 50:1 odds) for non-technical stakeholders. | Enables instant point addition on credit applications for automated underwriting logic. |
| **Rating Master Scale** | [`outputs/tables/rating_grades_model_b.csv`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/outputs/tables/rating_grades_model_b.csv) | Internal Risk Rating Grades (Grade 1–8) | Groups continuous PDs into discrete master scale bands to standardize credit policy, pricing, and capital allocation. | Aligns internal bank rating grades to external rating agency scales (e.g., S&P/Moody's). |
| **Two-Stage Hurdle LGD** | [`src/creditrisk/models/lgd_model.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/lgd_model.py#L38) | Zero-Inflated Bimodal Recovery Estimation | Addresses zero-inflation (52.18% 100% loss) by separating recovery occurrence classification from magnitude estimation. | Incorporates collateral haircut models, cure rates, and legal recovery collection costs. |
| **Realized EAD** | [`src/creditrisk/models/ead_model.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/ead_model.py#L25) | Drawn Balance at Default | EAD represents total exposure at the time of default (`max(funded_amnt - total_rec_prncp, 0)`). | For revolving lines (credit cards), EAD includes undrawn commitment times Credit Conversion Factor ($\text{EAD} = \text{Drawn} + \text{CCF} \cdot \text{Undrawn}$). |
| **IFRS 9 SICR Staging** | [`src/creditrisk/regulatory/staging.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/staging.py#L48) | Significant Increase in Credit Risk | Classifies exposures into Stage 1 (12m ECL), Stage 2 (Lifetime ECL), or Stage 3 (Impaired) using relative PD ratios (2.0x) and DPD backstops (30+ DPD). | Prevents cliff-edge provision spikes by recognizing lifetime losses as credit degrades. |
| **US CECL Baseline** | [`outputs/tables/ifrs9_vs_cecl.csv`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/outputs/tables/ifrs9_vs_cecl.csv) | Current Expected Credit Losses (FASB ASC 326) | CECL requires Day-1 lifetime ECL provisioning across all performing exposures regardless of SICR status. | Quantifies provision differences between US GAAP (CECL) and global IFRS 9 standards. |
| **Basel III Advanced IRB** | [`src/creditrisk/regulatory/basel_capital.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/basel_capital.py#L25) | Supervisory Capital Formula (BCBS para 4.4) | Computes Risk-Weighted Assets (RWA) and minimum capital at 99.9% confidence over a 1-year horizon under systemic stress. | Standardised Approach applies flat 75% risk weight; IRB penalizes high-LGD portfolios with 125.6% risk weight. |
| **Discriminatory Power** | [`src/creditrisk/validation/metrics.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/validation/metrics.py#L20) | AUROC, Gini Coefficient, KS Statistic | Evaluates the model's ability to rank-order default risk across borrowers regardless of absolute calibration. | Regulatory validation requires Gini > 0.30 and KS > 0.20 for retail PD scorecards. |
| **Hosmer-Lemeshow Test** | [`src/creditrisk/validation/metrics.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/validation/metrics.py#L115) | Goodness-of-Fit Calibration | Compares observed default counts against expected predicted defaults across deciles. | High sample sizes cause HL chi-square inflation; recalibration adjusts intercept to match portfolio base rates. |
| **Population Drift (PSI)** | [`src/creditrisk/validation/stability.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/validation/stability.py#L15) | Population Stability Index | Monitors shifts in borrower score distributions between development and out-of-time production cohorts. | Score PSI > 0.25 triggers mandatory model refitting under SR 11-7 model governance rules. |
| **Vintage MOB Seasoning** | [`src/creditrisk/monitoring/vintage.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/monitoring/vintage.py#L25) | Months-On-Book Cumulative Default Curves | Tracks default accumulation by loan age to identify underwriting vintage quality degradation. | Identifies peak default hazard windows (typically months 12 to 24 in consumer term loans). |

---

## 2. Technical SME Deep Dives

### A. Probability of Default (PD) & Scorecard Econometrics
- **Mathematical Principle**: Logistic regression models log-odds as a linear combination of WoE-binned attributes:
  $$\ln \left( \frac{p}{1-p} \right) = \beta_0 + \sum_{j=1}^{M} \beta_j \cdot \text{WoE}_{j}$$
- **SME Rationale**: Continuous attributes (e.g. `dti`, `annual_inc`) have non-monotonic or non-linear relationships with credit risk. Binned WoE forces monotonic log-odds scaling while isolating missing data into separate bins without synthetic imputation.
- **Scorecard Scaling Formula**:
  $$\text{Score} = \text{Offset} - \text{Factor} \cdot \ln \left( \frac{p}{1-p} \right)$$
  - Setting PDO = 20 means adding 20 scorecard points reduces odds of default by 50%.
  - Setting Base Score = 600 at 50:1 odds ($p = 0.0196$) establishes an intuitive operational baseline.

### B. Loss Given Default (LGD) Hurdle Architecture
- **Mathematical Principle**: Unsecured consumer recoveries are zero-inflated (52.18% of defaulted loans experience zero recovery). A single linear regression models boundary spikes poorly.
- **Hurdle Solution**:
  1. **Stage 1 (Binary Recovery Incidence)**: $P(\text{has\_recovery} = 1)$ estimated via Logistic Classifier.
  2. **Stage 2 (Conditional Recovery Magnitude)**: $\hat{RR}_{\text{pos}}$ estimated via Gradient Boosting Regressor strictly on $RR > 0$.
  3. **Expected LGD**:
     $$\text{LGD} = 1 - \left( P(\text{has\_recovery} = 1) \cdot \hat{RR}_{\text{pos}} \right)$$

### C. IFRS 9 Staging & US CECL Accounting Comparison
- **IFRS 9 3-Stage Model**:
  - **Stage 1**: Performing loans -> 12-month ECL provision.
  - **Stage 2**: Significant Increase in Credit Risk (SICR) -> Lifetime ECL provision. Triggered when $\text{PD}_{\text{current}} / \text{PD}_{\text{origination}} \ge 2.0x$, $\text{PD}_{\text{current}} > 6.0\%$, or $\text{DPD} \ge 30$.
  - **Stage 3**: Defaulted exposures -> Lifetime ECL provision on net exposure ($\text{PD} = 1.0$).
- **US CECL Model (FASB ASC 326)**:
  - Eliminates staging and SICR triggers. Reserves Day-1 Lifetime ECL across **all performing exposures**.
- **Portfolio Impact**: US CECL requires **$327.47M** in provisions vs **$278.48M** under IFRS 9, resulting in a **+$48.99M (+17.6%)** provision delta due to Stage 1 lifetime accounting.

### D. Basel III Advanced IRB Capital & Risk-Weight Dynamics
- **BCBS Para 4.4 Supervisory IRB Formula**:
  - Systemic asset correlation $R$ scales dynamically between 3% and 16% based on PD.
  - Conditional capital factor $K$ evaluates portfolio loss at the 99.9th percentile confidence limit under a 1-in-1,000 year macroeconomic shock.
  - $\text{RWA} = K \cdot 12.5 \cdot \text{EAD}$.
- **Standardised vs. IRB Penalty**:
  - Basel III Standardised approach applies a flat **75.0%** risk weight to retail unsecured exposures ($1.370B RWA, $109.6M capital @ 8%).
  - Advanced IRB formula incorporates actual portfolio LGD (**93.01%**), producing an average risk weight of **125.63%** ($2.295B RWA, $183.57M capital @ 8%).
  - **Domain Insight**: Advanced IRB properly penalizes high-loss unsecured portfolios by requiring +67.5% more regulatory capital than the Standardised benchmark.

---

## 3. Executive Talking Points & Interview Answers

1. **Why does Model B outperform Model A on OOT data?**  
   "Model B incorporates LendingClub's credit risk pricing variables (`grade`, `sub_grade`, `int_rate`), raising the Out-Of-Time Gini from 0.2715 to 0.3845 (+11.3 Gini points). The fine-classing WoE binning remains stable across vintages without over-fitting."

2. **Why is mean LGD 93.01% in this portfolio?**  
   "52.18% of defaulted exposures experience zero recoveries post charge-off. Unsecured consumer loans carry no collateral, so once an account defaults and defaults past 90 days, recovery rates drop precipitously."

3. **How does the repository handle anti-leakage governance?**  
   "`src/creditrisk/data/schema.py` enforces `assert_no_leakage()`, validating that post-origination fields like `total_rec_prncp`, `recoveries`, and `last_pymnt_d` are strictly prohibited from entering PD scorecards."
