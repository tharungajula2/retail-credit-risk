# Retail Credit Risk Modeling System: Master Flow & Architecture

## Section 1 — What this project is

This repository implements an end-to-end regulatory credit risk engineering system for retail consumer unsecured term loans. The codebase evaluates a historical open dataset from LendingClub covering **466,285 loans** originated between 2007 and 2014. The pipeline processes raw loan records, engineers 12-month default targets, partitions temporal samples, fits Weight of Evidence feature binning, builds logistic Probability of Default (PD) scorecards, trains two-stage Loss Given Default (LGD) hurdle models, estimates Exposure At Default (EAD), and projects discrete-time 60-month lifetime PD hazard curves.

The system generates regulatory compliance outputs under international financial accounting and banking capital standards. For accounting provisions under International Financial Reporting Standard 9 (IFRS 9 / Ind AS 109), it stages active loan exposures into Stage 1, Stage 2, and Stage 3 based on Significant Increase in Credit Risk (SICR) criteria and computes staged Expected Credit Loss (ECL), while comparing figures against US Current Expected Credit Losses (CECL) lifetime provisioning. For regulatory capital under the Basel III Advanced Internal Ratings-Based (IRB) framework, it calculates Risk-Weighted Assets (RWA), minimum capital ratios (Common Equity Tier 1, Tier 1, Total Capital), and downturn LGD stress scenarios. Commercial banks use these outputs for credit underwriting thresholds, risk-adjusted capital allocation, allowance for credit loss reporting, and regulatory capital adequacy auditing.

---

## Section 2 — Repository map

```
retail-credit-risk/
├── config/                      # YAML configuration files controlling pipeline parameters
│   ├── ai.yaml                  # Configures RAG embedding model, chunk sizes, and Gemini API settings
│   ├── ifrs9.yaml               # Sets IFRS 9 staging thresholds (SICR PD ratio = 2.0, PD ceiling = 0.06, 30 DPD backstop)
│   ├── macro_scenarios.yaml     # Defines GDP growth and unemployment rates for Baseline, Upside, and Downside ECL scenarios
│   ├── pd_model.yaml            # Specifies candidate features for Logistic PD Model A (7 features) and Model B (10 features)
│   ├── sampling.yaml           # Sets vintage years for Development (2007–2013) vs OOT (2014), 80/20 train split ratio, and random seed 42
│   ├── target_definition.yaml   # Defines default statuses (Charged Off, Default, Late 31-120), DPD lag (3m), and performance window (12m)
│   └── variables.yaml           # Lists raw target column, numeric/categorical features, and drop candidate columns
├── datasets/                    # Local raw dataset storage (excluded from version control via .gitignore)
│   └── loan_data_2007_2014.csv  # Raw LendingClub dataset containing 466,285 loan rows and 75 raw columns (114 MB)
├── data/processed/              # Cleaned, binned, and partitioned binary Parquet storage
│   ├── train.parquet            # Stratified development training set containing 184,525 loans (80% split of 2007–2013 vintages)
│   ├── test.parquet             # Stratified development testing set containing 46,132 loans (20% split of 2007–2013 vintages)
│   └── oot.parquet              # Out-of-time validation set containing 235,628 loans (100% of 2014 vintage)
├── docs/                        # Technical documentation, architectural manuals, and regulatory references
│   ├── LEARN_THIS_PROJECT.md    # Comprehensive self-contained onboarding and technical interview preparation guide
│   ├── MODEL_DOCUMENTATION.md   # Formal model development document describing methodology and validation results
│   ├── MANAGEMENT_DECK.md       # Executive presentation summary covering key findings and business impacts
│   ├── basel_retail_curves.md   # Mathematical specification of Basel III retail IRB correlation and risk weight formulas
│   └── PROJECT_FLOW_MASTER.md   # THIS file: master pipeline architecture, stage walkthrough, and explicit formulas
├── outputs/                     # Generated model binaries, validation figures, analytical CSV tables, and reports
│   ├── figures/                 # Generated PNG plots (ROC curves, KS separation plots, LGD decile calibration, lifetime PD curves)
│   ├── models/                  # Pickled fitted model objects (.pkl), binner rules, and RAG vector index files (.npy, .json)
│   ├── reports/                 # Compiled JSON dashboard metrics data and standalone interactive HTML risk dashboard report
│   └── tables/                  # 35 exported analytical CSV tables containing all validation, staging, ECL, and capital outputs
├── src/creditrisk/              # Core Python source code package structured into specialized functional subpackages
│   ├── ai/                      # Vector RAG indexing, semantic retriever, and LLM-assisted credit risk analyst agent
│   ├── data/                    # Raw data loading, century-fix date parsing, 12-month PD target label creation, and sampling
│   ├── features/                # Quantile binning, monotonic WoE transformation, and Information Value feature selection
│   ├── models/                  # Statsmodels Logistic PD estimation, 600-pt scorecard scaling, two-stage LGD hurdle, EAD, and CCF
│   ├── monitoring/              # Vintage MOB default curves, cross-sectional delinquency roll-rate proxy, and rating transitions
│   ├── regulatory/              # 60-month lifetime PD hazard curves, IFRS 9 SICR staging, staged ECL, CECL, and Basel III IRB capital
│   ├── reporting/               # Dashboard metric JSON serialization and single-file HTML risk dashboard renderer
│   └── validation/              # Discrimination metrics (AUC, Gini, KS), calibration (Brier, HL test), and stability (PSI, CSI)
├── tests/                       # Unit testing suite executed via pytest verifying schema integrity and pipeline functions
├── pyproject.toml               # Python package configuration, build metadata, setuptools instructions, and dependency bounds
├── requirements.txt             # Direct Python library dependencies with minimum version specifications
└── PROJECT_TRUTH_retail-credit-risk.md # Ground truth reference file recording repository metrics, commits, and verified facts
```

---

## Section 3 — End-to-End Master Flow

This section details the 16 sequential execution stages of the retail credit risk modeling system from raw data ingest to reporting and AI indexing.

```
      [datasets/loan_data_2007_2014.csv (466,285 rows)]
                            │
                            ▼
   ┌─────────────────────────────────────────────────┐
   │  Stage 1: Target Engineering & Date Parsing     │
   └─────────────────────────────────────────────────┘
```

**What happens** — Converts string dates into datetime objects with century-rollover corrections and constructs binary 12-month default target flags (`default_12m`). The process determines whether a loan defaulted within its first 12 months of life.

**How it's done** — Parses `issue_d` and `last_pymnt_d` strings using `%b-%y`. Pandas parses two-digit years like '68' as 2068, so any parsed year greater than 2049 has 100 years subtracted to evaluate to 1968. Loans with status `Charged Off`, `Default`, `Late (31-120 days)`, or `Does not meet credit policy` are flagged `ever_default = 1`. Estimated default date is set to `last_pymnt_d` plus a 3-month Days Past Due (DPD) lag. Months to default is calculated as whole elapsed months between `issue_d` and `est_default_date`. The binary target `default_12m` is set to 1 if `ever_default == 1` and `0 <= months_to_default <= 12`.

**Formula**

$$\text{default\_12m} = \mathbb{I}\left(\text{ever\_default} = 1 \;\wedge\; 0 \le \text{months\_to\_default} \le 12\right)$$

**Key numbers** — Raw load: 466,285 total loans; Ever Default: 50,968 loans (10.93%); 12-Month Default: 16,018 loans (3.44% portfolio 12m default rate).

**Why this choice** — A fixed 12-month performance window standardizes risk measurement across loan cohorts regardless of total observation age.

**Honest caveat** — Default event timing is inferred from `last_pymnt_d` plus 3 months lag because raw LendingClub data lacks an explicit default date column.

**Files** — target.py, run_target_generation.py, target_definition.yaml.

---

```
   [Cleaned DataFrame (466,285 rows)]
                   │
                   ▼
   ┌──────────────────────────────────────────────┐
   │  Stage 2: Sampling & Temporal Partitioning   │
   └──────────────────────────────────────────────┘
```

**What happens** — Partitions the total dataset into development and out-of-time validation sets based on loan origination year, then performs an 80/20 stratified split on the development sample.

**How it's done** — Filters loans by `issue_d` year. Loans originated between 2007 and 2013 form the Development cohort (230,657 loans). Loans originated in 2014 form the Out-Of-Time (OOT) validation cohort (235,628 loans). Development loans undergo an 80/20 stratified random split based on `default_12m` using `random_state=42`. Partitions are saved as binary Parquet files.

**Key numbers** — Train set: 184,525 loans (3.43% default rate); Test set: 46,132 loans (3.43% default rate); OOT set: 235,628 loans (3.44% default rate).

**Why this choice** — Temporal out-of-time partitioning tests model performance on future unobserved macroeconomic cohorts, preventing random-sampling data leakage across origination years.

**Honest caveat** — The OOT sample uses 2014 vintage data because zero loans from 2015 exist in the repository dataset.

**Files** — sampling.py, run_sampling.py, sampling.yaml.

---

```
   [data/processed/train.parquet]
                   │
                   ▼
   ┌──────────────────────────────────────────────┐
   │  Stage 3: Feature Binning & WoE Transformation│
   └──────────────────────────────────────────────┘
```

**What happens** — Bucketizes continuous and categorical candidate features into bins and transforms each bin into a Weight of Evidence (WoE) value that measures default risk separation. Calculates Information Value (IV) to select predictive variables.

**How it's done** — Continuous features split into up to 20 initial quantile cuts. Adjacent bins merge iteratively until every bin holds at least 5% of the total sample (`min_bin_pct = 0.05`) and WoE values across bins move in a strictly monotonic direction (non-decreasing or non-increasing). Categorical attributes merge rare categories (< 5%) into 'OTHER'. Missing values receive a dedicated null bin. Laplace smoothing (+0.5 counts) prevents infinite log-odds. Information Value (IV) is calculated to rank predictive strength.

**Formula**

$$\text{WoE}_i = \ln\!\left( \frac{\frac{\text{non-defaults}_i + 0.5}{\text{total non-defaults} + 1.0}}{\frac{\text{defaults}_i + 0.5}{\text{total defaults} + 1.0}} \right)$$

$$\text{IV} = \sum_{i=1}^{k} \left( \%\,\text{non-defaults}_i - \%\,\text{defaults}_i \right) \cdot \text{WoE}_i$$

**Key numbers** — 48 features binned; top predictive features selected by IV (e.g. `sub_grade` IV = 0.325 [strong], `term` IV = 0.158 [medium], `dti` IV = 0.089 [medium], `annual_inc` IV = 0.052 [weak]).

**Why this choice** — WoE linearizes non-linear feature relationships against log-odds so a logistic regression can use them directly; monotonic binning stops scorecards from producing illogical score jumps across adjacent attribute values.

**Honest caveat** — Coarse quantile binning discards fine-grained feature variance within individual bin intervals.

**Files** — binning.py, run_binning.py, variables.yaml.

---

```
   [WoE-Transformed Features + train.parquet]
                       │
                       ▼
   ┌──────────────────────────────────────────────┐
   │  Stage 4: Logistic Regression PD Estimation  │
   └──────────────────────────────────────────────┘
```

**What happens** — Fits Statsmodels Logistic Regression models on WoE-transformed features to estimate the 12-month Probability of Default ($PD$).

**How it's done** — Loads WoE-transformed training features and fits Statsmodels `Logit` using Maximum Likelihood Estimation (MLE). Model A fits 7 core features (`sub_grade_woe`, `term_woe`, `home_ownership_woe`, `annual_inc_woe`, `verification_status_woe`, `purpose_woe`, `dti_woe`). Model B fits 10 features (adding `inq_last_6mths_woe`, `revol_util_woe`, `total_acc_woe`). Computes coefficient standard errors, z-scores, and p-values.

**Formula**

$$\ln\!\left(\frac{PD}{1 - PD}\right) = \alpha + \sum_{j=1}^{p} \beta_j \cdot \text{WoE}_j$$

$$PD = \frac{1}{1 + e^{-\left(\alpha + \sum_{j=1}^{p} \beta_j \cdot \text{WoE}_j\right)}}$$

**Key numbers** — Model A intercept = -3.3364; Model B intercept = -3.3392; all feature coefficients show positive signs aligned with WoE direction.

**Why this choice** — Statsmodels logistic regression produces well-calibrated probabilities bounded in $[0, 1]$ and outputs explicit asymptotic p-values required by regulatory model validation auditors.

**Honest caveat** — Linear log-odds assumption cannot automatically detect high-order non-linear feature interactions without manual cross-product terms.

**Files** — pd_model.py, run_pd_model.py, pd_model.yaml.

---

```
   [Fitted Logit Models (pd_model_a/b.pkl)]
                       │
                       ▼
   ┌──────────────────────────────────────────────┐
   │  Stage 5: Scorecard Point Scaling            │
   └──────────────────────────────────────────────┘
```

**What happens** — Translates logistic regression coefficients and WoE values into integer credit scorecard points where higher points represent lower default risk.

**How it's done** — Establishes reference scaling parameters: Base Score = 600 points at 50:1 odds ($Odds = (1-PD)/PD = 50$), with Points to Double Odds ($PDO = 20$). Calculates Factor and Offset. Distributes model intercept and feature coefficients across individual attribute bins to assign integer point values per bin.

**Formula**

$$\text{Factor} = \frac{PDO}{\ln(2)} = \frac{20}{\ln(2)} \approx 28.8539$$

$$\text{Offset} = \text{Base Score} - \text{Factor} \times \ln(50) = 600 - 28.8539 \times 3.9120 \approx 487.123$$

$$\text{Score} = \text{Offset} + \text{Factor} \times \ln\!\left(\frac{1 - PD}{PD}\right)$$

$$\text{Bin Point}_i = -\left( \beta_i \cdot \text{WoE}_i + \frac{\alpha}{N} \right) \cdot \text{Factor} + \frac{\text{Offset}}{N}$$

**Key numbers** — Base Score 600 at 50:1 odds ($PD = 1.96\%$); PDO 20 (score 620 = 100:1 odds / $PD = 0.99\%$).

**Why this choice** — Scorecards map log-odds into integer points that loan officers and underwriters can easily interpret and audit.

**Honest caveat** — Linear scorecard point allocation assumes risk scales proportionally across all score bands.

**Files** — scorecard.py, run_scorecard.py.

---

```
   [Predicted Probabilities across Datasets]
                       │
                       ▼
   ┌──────────────────────────────────────────────┐
   │  Stage 6: Validation & Diagnostics           │
   └──────────────────────────────────────────────┘
```

**What happens** — Evaluates rank-ordering discrimination (AUROC, Gini, KS) and probability calibration (Hosmer-Lemeshow test) across Train, Test, and OOT datasets.

**How it's done** — Computes Area Under Receiver Operating Characteristic (AUROC), Gini coefficient ($2 \cdot AUROC - 1$), and Kolmogorov-Smirnov ($KS$) separation statistic. Runs a 10-decile Hosmer-Lemeshow chi-square test comparing observed defaults vs expected defaults.

**Formula**

$$\text{Gini} = 2 \times \text{AUROC} - 1$$

$$KS = \max_{t} \left| \text{TPR}(t) - \text{FPR}(t) \right|$$

$$H = \sum_{g=1}^{10} \frac{(O_g - N_g \bar{p}_g)^2}{N_g \bar{p}_g (1 - \bar{p}_g)} \sim \chi^2_8$$

**Key numbers** —
- Model A: Train Gini = 0.3013, Test Gini = 0.2969, OOT Gini = 0.2715; Test KS = 0.2233; Test HL p-value = 0.2363.
- Model B: Train Gini = 0.3678, Test Gini = 0.3634, OOT Gini = 0.3845; Test KS = 0.2728; Test HL p-value = 0.4942.

**Why this choice** — Combining Gini, KS, and Hosmer-Lemeshow tests evaluates both rank-ordering discrimination and absolute probability accuracy.

**Honest caveat** — Model B OOT Gini (0.3845) is higher than Train Gini (0.3678) due to early seasoning default concentration in 2014; uncalibrated models fail Hosmer-Lemeshow on large OOT samples ($N=235,628$, $p = 3.08 \times 10^{-7}$) because chi-square statistics become hyper-sensitive when sample size is large.

**Files** — metrics.py, run_validation.py.

---

```
   [Uncalibrated Predicted Probabilities]
                       │
                       ▼
   ┌──────────────────────────────────────────────┐
   │  Stage 7: Probability Recalibration          │
   └──────────────────────────────────────────────┘
```

**What happens** — Recalibrates predicted default probabilities so that the mean predicted default rate matches the observed portfolio default rate without changing rank-ordering.

**How it's done** — Implements Intercept Recalibration by adjusting logit intercept $\alpha_{\text{new}} = \alpha + \ln(\bar{y}/(1-\bar{y})) - \ln(\bar{p}/(1-\bar{p}))$. Implements Platt Scaling by fitting a univariable logistic regression on raw predicted log-odds.

**Formula**

$$\alpha_{\text{new}} = \alpha + \ln\!\left(\frac{\bar{y}}{1 - \bar{y}}\right) - \ln\!\left(\frac{\bar{p}}{1 - \bar{p}}\right)$$

$$\text{PD}_{\text{recalibrated}} = \frac{1}{1 + e^{-\left(\alpha_{\text{new}} + \sum \beta_i \cdot \text{WoE}_i\right)}}$$

**Key numbers** — Re-aligns mean predicted PD to observed default rate (3.44%), restoring probability alignment on OOT data while leaving Gini and KS unchanged.

**Why this choice** — Recalibration corrects probability scale shifts caused by macroeconomic changes between training and deployment periods.

**Honest caveat** — Intercept adjustment corrects mean probability bias but cannot fix non-linear decile calibration distortions.

**Files** — calibration.py, run_calibration.py.

---

```
   [Train vs OOT Score & Feature Distributions]
                        │
                        ▼
   ┌──────────────────────────────────────────────┐
   │  Stage 8: Population & Stability Monitoring  │
   └──────────────────────────────────────────────┘
```

**What happens** — Measures population drift between baseline (Train) and actual (OOT) score distributions across the total portfolio and individual features.

**How it's done** — Divides baseline (Train) and actual (OOT) score distributions into 10 deciles. Computes Population Stability Index (PSI). Computes Characteristic Stability Index (CSI) across individual feature WoE bins. Adds epsilon smoothing ($1 \times 10^{-4}$) to prevent division-by-zero errors in empty bins.

**Formula**

$$\text{PSI} = \sum_{b=1}^{10} \left( \%\,\text{Actual}_b - \%\,\text{Baseline}_b \right) \cdot \ln\!\left(\frac{\%\,\text{Actual}_b}{\%\,\text{Baseline}_b}\right)$$

**Key numbers** — Model A Score PSI = 0.0046; Model B Score PSI = 0.0071 (both < 0.10, indicating stable distributions); Max CSI = `dti` (0.0416); Min CSI = `annual_inc` (0.0057).

**Why this choice** — PSI and CSI are standard regulatory metrics that alert risk officers when population shifts invalidate scorecard scoring.

**Honest caveat** — Static decile bin boundaries fixed from baseline training data may obscure localized population shifts within bins.

**Files** — stability.py, run_stability.py.

---

```
   [Defaulted Loan Subset (50,968 rows)]
                   │
                   ▼
   ┌──────────────────────────────────────────────┐
   │  Stage 9: Two-Stage Hurdle LGD Modeling      │
   └──────────────────────────────────────────────┘
```

**What happens** — Models Loss Given Default ($LGD$) on defaulted loans using a two-stage hurdle architecture to handle zero-inflated recovery distributions.

**How it's done** — Filters dataset to 50,968 defaulted loans (`ever_default == 1`). Stage 1 trains a Logistic Classifier to estimate recovery occurrence $P(\text{recovery} > 0)$. Stage 2 trains a Gradient Boosting Regressor strictly on positive recoveries ($\text{recovery} > 0$) to estimate recovery rate ($\hat{RR}_{\text{pos}}$). Combined expected $LGD = 1 - [P(\text{recovery} > 0) \cdot \hat{RR}_{\text{pos}}]$. Evaluated on 80/20 train/test split.

**Formula**

$$\text{LGD} = 1 - \left( P(\text{recovery} > 0) \times \hat{RR}_{\text{pos}} \right)$$

**Key numbers** — 50,968 defaulted loans; Mean LGD = 93.01% (0.930055); Median LGD = 1.0; Mean Recovery Rate = 6.99%; **52.18% point-mass at 100% loss** ($LGD = 1.0$ / zero recovery); 0.35% at $LGD = 0.0$; Stage 1 AUC = 0.6416; overall decile MAE = 0.00245 - 0.00406.

**Why this choice** — A two-stage hurdle model accounts for zero-inflation (52.18% of defaults yielding zero recovery), which violates standard single linear or beta regression assumptions.

**Honest caveat** — Combining two separate model predictions introduces compound estimation variance in expected recovery outputs.

**Files** — lgd_model.py, run_lgd_training.py, lgd_data.py.

---

```
   [Loan Balances & Synthetic Revolving Data]
                       │
                       ▼
   ┌──────────────────────────────────────────────┐
   │  Stage 10: EAD & Synthetic CCF Analytics     │
   └──────────────────────────────────────────────┘
```

**What happens** — Computes Exposure At Default ($EAD$) for fixed-term consumer loans and simulates Credit Conversion Factor ($CCF$) estimation for revolving credit lines.

**How it's done** — For fixed-term amortizing loans, $EAD$ is computed directly as outstanding principal at default: $EAD = \max(\text{funded\_amnt} - \text{total\_rec\_prncp}, 0)$. For revolving credit lines, a synthetic 5,000-account revolving portfolio simulates undrawn commitment drawdowns: $CCF = (EAD - \text{Drawn}) / (\text{Limit} - \text{Drawn})$. Fits OLS regression predicting CCF from credit limit and utilization.

**Formula**

$$\text{EAD}_{\text{term}} = \max\!\left( \text{funded\_amnt} - \text{total\_rec\_prncp}, 0 \right)$$

$$\text{CCF}_{\text{revolving}} = \frac{\text{EAD} - \text{Drawn}}{\text{Limit} - \text{Drawn}}$$

**Key numbers** — Mean EAD on defaulted loans = $10,781.56; Median EAD = $9,141.37; Mean EAD Ratio = 0.7193; Synthetic Revolving CCF mean = 0.4288 (OLS Intercept = 0.1977, Utilisation Coef = 0.4753).

**Why this choice** — Fixed-term loans carry zero undrawn credit commitment, so $EAD$ equals outstanding principal; synthetic CCF demonstrates revolving line modeling methodology.

**Honest caveat** — Revolving CCF analysis is executed on a synthetic 5,000-account dataset because LendingClub term loans lack undrawn line commitments. Output table is explicitly named `SYNTHETIC_ccf_summary.csv`.

**Files** — ead_model.py, ccf_demo.py.

---

```
   [Historical Performance Data (Months 1..60)]
                        │
                        ▼
   ┌──────────────────────────────────────────────┐
   │  Stage 11: Lifetime PD Term Structure        │
   └──────────────────────────────────────────────┘
```

**What happens** — Constructs discrete-time monthly hazard curves across loan tenures (months 1..60) and derives cumulative lifetime PD term structures.

**How it's done** — Calculates monthly marginal hazard rates $h(t) = \text{Defaults}(t) / \text{Active}(t-1)$ across 60 months of loan age. Derives cumulative survival probabilities $S(t) = \prod_{k=1}^{t} (1 - h(k))$ and cumulative lifetime default probabilities $PD_{\text{lifetime}}(t) = 1 - S(t)$. Individual account 12-month PDs scale the portfolio hazard curve via multiplicative ratio $(PD_{12m, i} / PD_{12m, \text{portfolio}})$.

**Formula**

$$h(t) = \frac{\text{Defaults}_t}{\text{Active}_{t-1}}$$

$$S(t) = \prod_{k=1}^{t} \left(1 - h(k)\right)$$

$$PD_{\text{lifetime}}(t) = 1 - S(t)$$

$$h_i(t) = h_{\text{portfolio}}(t) \times \frac{PD_{12m, i}}{PD_{12m, \text{portfolio}}}$$

**Key numbers** — Cumulative portfolio PD curve: Month 1 = 0.0806%; Month 12 = 3.4352%; Month 24 = 6.3462%; Month 36 = 9.3156%; Month 60 = 10.9306%.

**Why this choice** — Discrete-time hazard curves capture non-constant monthly default timing over loan life rather than assuming a flat annual default hazard.

**Honest caveat** — The portfolio hazard curve is scaled unconditionality across accounts without incorporating forward-looking macro covariate paths per month.

**Files** — lifetime_pd.py, run_lifetime_pd.py.

---

```
   [data/processed/oot.parquet + PD Predictions]
                          │
                          ▼
   ┌──────────────────────────────────────────────┐
   │  Stage 12: IFRS 9 Staging & SICR Engine      │
   └──────────────────────────────────────────────┘
```

**What happens** — Classifies loan exposures into IFRS 9 Stage 1, Stage 2, or Stage 3 based on quantitative PD deterioration, absolute PD ceilings, and qualitative backstops.

**How it's done** — Compares current predicted 12-month PD against origination PD (approximated by credit grade average). Stage 3 is assigned if loan is defaulted or $\text{days\_past\_due} \ge 90$. Stage 2 is assigned if Significant Increase in Credit Risk (SICR) is triggered: $PD_{\text{ratio}} = PD_{\text{current}} / PD_{\text{origination}} \ge 2.0$, or $PD_{\text{current}} > 0.06$, or $\text{days\_past\_due} \ge 30$. Remaining exposures are assigned Stage 1.

**Formula**

$$\text{SICR Trigger} = \left( \frac{PD_{\text{current}}}{PD_{\text{origination}}} \ge 2.0 \right) \;\lor\; \left( PD_{\text{current}} > 0.06 \right) \;\lor\; \left( \text{DPD} \ge 30 \right)$$

**Key numbers** — 2014 OOT Portfolio (235,628 loans, $1.827B EAD):
- Stage 1: 189,633 loans (80.48%), $1,417,203,102.50 EAD, Mean 12m PD = 2.73%.
- Stage 2: 26,554 loans (11.27%), $169,366,224.20 EAD, Mean 12m PD = 7.64%.
- Stage 3: 19,441 loans (8.25%), $240,003,112.50 EAD, Mean 12m PD = 100.00%.

**Why this choice** — Combining quantitative relative PD shift (2.0x), absolute PD threshold (6.0%), and 30-day DPD backstop enforces strict IFRS 9 regulatory compliance.

**Honest caveat** — Origination PD is approximated using credit grade averages because historical origination scorecards were not preserved in the raw dataset.

**Files** — staging.py, run_staging.py, ifrs9.yaml.

---

```
   [Staged Portfolio + LGD Model + Hazard Curves]
                         │
                         ▼
   ┌──────────────────────────────────────────────┐
   │  Stage 13: Staged ECL & US CECL Provisioning │
   └──────────────────────────────────────────────┘
```

**What happens** — Calculates staged Expected Credit Loss ($ECL$) provisions under IFRS 9 and compares reserves against US CECL Day-1 lifetime accounting.

**How it's done** — Calculates IFRS 9 staged provisions: Stage 1 $ECL = PD_{12m} \times LGD \times EAD$; Stage 2 $ECL = PD_{\text{lifetime}} \times LGD \times EAD$; Stage 3 $ECL = 1.0 \times LGD \times EAD$. Under US CECL, Day-1 lifetime ECL ($PD_{\text{lifetime}} \times LGD \times EAD$) is applied across all performing loans (Stages 1 and 2). Also applies macro scenario weighting (Baseline 50%, Upside 20%, Downside 30%).

**Formula**

$$\text{ECL}_{\text{Stage 1}} = PD_{12m} \times LGD \times EAD$$

$$\text{ECL}_{\text{Stage 2}} = PD_{\text{lifetime}} \times LGD \times EAD$$

$$\text{ECL}_{\text{Stage 3}} = 1.0 \times LGD \times EAD$$

$$\text{ECL}_{\text{CECL}} = \sum_{i \in \text{All Loans}} PD_{\text{lifetime}, i} \times LGD_i \times EAD_i$$

**Key numbers** —
- Stage 1 ECL = $30,272,767.11 (2.14% coverage).
- Stage 2 ECL = $24,404,482.89 (14.41% coverage).
- Stage 3 ECL = $223,799,308.68 (93.25% coverage).
- Total IFRS 9 Staged ECL = **$278,476,558.68** (15.25% portfolio coverage).
- US CECL Lifetime ECL = **$327,465,214.28** (17.93% portfolio coverage).
- CECL vs IFRS 9 Provision Delta = **+$48,988,631.78** (+$48.99M higher under CECL due to Stage 1 lifetime reserves).
- Macro Scenario Weighted ECL (3-loan test fixture) = $9,384.73 (Baseline $4,618.18, Upside $1,810.18, Downside $2,956.36).

**Why this choice** — Dual calculation quantifies the exact financial impact of IFRS 9 staged provisioning versus US CECL Day-1 lifetime accounting.

**Honest caveat** — Macro scenario weighting script (`run_macro_scenarios.py`) and expected loss summary script (`run_expected_loss.py`) run on a 3-loan test fixture dataframe rather than processing all 235,628 OOT loans.

**Files** — ecl.py, run_ecl.py, run_macro_scenarios.py, run_expected_loss.py, macro_scenarios.yaml.

---

```
   [PD Predictions + LGD Model + Portfolio Balances]
                           │
                           ▼
   ┌──────────────────────────────────────────────────┐
   │  Stage 14: Basel III Capital & Downturn Stress   │
   └──────────────────────────────────────────────────┘
```

**What happens** — Calculates Basel III Advanced Internal Ratings-Based (IRB) Risk-Weighted Assets ($RWA$), minimum capital requirements, and downturn LGD stress impacts.

**How it's done** — Applies the Basel III Corporate/Retail IRB capital formula incorporating correlation $R$, maturity adjustment $b(PD)$, and capital factor $K$. Calculates IRB $RWA = K \times 12.5 \times EAD$ and compares against Standardised 75% retail risk weight. Evaluates minimum capital ratios (CET1 4.5%, Tier 1 6.0%, Total Capital 8.0%). Applies $+8\%$ downturn LGD add-on ($LGD_{\text{downturn}} = \min(LGD + 0.08, 1.0)$) to stress capital reserves.

**Formula**

$$R = 0.03 \times \frac{1 - e^{-50 \cdot PD}}{1 - e^{-50}} + 0.16 \times \left(1 - \frac{1 - e^{-50 \cdot PD}}{1 - e^{-50}}\right)$$

$$b = \left(0.11852 - 0.05478 \times \ln(PD)\right)^2$$

$$K = \left[ LGD \times N\!\left( \frac{G(PD)}{\sqrt{1 - R}} + \sqrt{\frac{R}{1 - R}} \cdot G(0.999) \right) - PD \times LGD \right] \times \frac{1 + (M - 2.5)b}{1 - 1.5b}$$

$$RWA = K \times 12.5 \times EAD$$

$$\text{Capital}_{\text{Total}} = 0.08 \times RWA$$

**Key numbers** —
- Total IRB RWA = **$2,294,667,104.99** ($2.295B).
- Total Standardised RWA = $1,369,929,329.40 ($1.370B).
- IRB Portfolio Risk Weight = **125.63%** (vs Standardised 75.0%).
- Minimum CET1 Capital (4.5%) = $103,260,019.72 ($103.26M).
- Minimum Tier 1 Capital (6.0%) = $137,680,026.30 ($137.68M).
- Minimum Total Capital (8.0%) = $183,573,368.40 ($183.57M).
- Downturn LGD (+8pp) Total RWA = **$2,453,921,334.39** ($2.454B, Risk Weight 134.35%).
- Downturn Minimum Total Capital Increase = **+$12,740,338.35** (+$12.74M).

**Why this choice** — Advanced IRB capital modeling provides risk-sensitive capital allocation matching empirical credit risk parameters.

**Honest caveat** — High empirical unsecured LGD (93.01%) pushes Advanced IRB risk weight (125.63%) significantly above the Standardised 75% retail benchmark.

**Files** — basel_capital.py, run_basel_capital.py, basel_retail_curves.md.

---

```
   [Full Historical Portfolio (466,285 loans)]
                        │
                        ▼
   ┌──────────────────────────────────────────────────┐
   │  Stage 15: Vintage Analytics & Roll-Rate Proxy   │
   └──────────────────────────────────────────────────┘
```

**What happens** — Tracks vintage default curves by Months-On-Book (MOB), constructs cross-sectional delinquency roll-rate proxies, and generates credit grade outcome transition matrices.

**How it's done** — Groups historical loans by origination vintage year (2007–2014) and tracks cumulative default rates across elapsed MOB (months 1..60). Constructs a cross-sectional delinquency proxy grouping current status into DPD buckets (Current, 31-60 DPD, 61-90 DPD, 90+ DPD, Default). Builds an origination grade-to-resolution transition matrix tracking how loans rated A through G resolve into Fully Paid vs Defaulted outcomes.

**Key numbers** — Vintage MOB default curves show 2007–2008 vintages peaking at higher cumulative default rates (~16%) than 2011–2013 vintages (~8–10%). Grade transition matrix shows Grade A loans achieving ~92% Fully Paid vs Grade G loans achieving ~50% Fully Paid.

**Why this choice** — Vintage curves and transition matrices monitor credit deterioration trends across origination cohorts over time.

**Honest caveat** — Delinquency roll rates and transition matrices are constructed as cross-sectional snapshot proxies by vintage year and origination grade because longitudinal monthly panel tracking data is absent from LendingClub datasets.

**Files** — vintage.py, roll_rates.py, transitions.py, run_monitoring.py, run_transitions.py.

---

```
   [outputs/tables/*.csv + Documentation Markdown]
                           │
                           ▼
   ┌──────────────────────────────────────────────────┐
   │  Stage 16: Interactive Dashboard & RAG Indexing  │
   └──────────────────────────────────────────────────┘
```

**What happens** — Compiles all project metrics into a structured JSON file, renders a self-contained interactive HTML executive risk dashboard, and builds vector index embeddings for offline LLM querying.

**How it's done** — `dashboard_data.py` aggregates outputs from `outputs/tables/` into `outputs/reports/dashboard_data.json`. `build_dashboard.py` reads JSON metrics and injects them into an HTML template with inline CSS and JavaScript, outputting `outputs/reports/risk_dashboard.html`. `rag_index.py` chunks documentation and tables, computes vector embeddings using `sentence-transformers` (`all-MiniLM-L6-v2`), and saves embeddings to `outputs/models/rag_index/`. `analyst.py` queries Gemini via Google Generative AI API using retrieved vector context.

**Key numbers** — Generates a 25 KB `dashboard_data.json` and a single standalone HTML dashboard file (`risk_dashboard.html`) containing interactive tables and charts.

**Why this choice** — Rendering a zero-dependency HTML dashboard enables non-technical stakeholders to inspect interactive risk analytics without installing Python or server infrastructure.

**Honest caveat** — RAG analyst query script (`run_analyst.py`) requires a valid `GEMINI_API_KEY` environment variable for live LLM inference.

**Files** — dashboard_data.py, build_dashboard.py, rag_index.py, retriever.py, analyst.py, run_analyst.py, ai.yaml.

---

## Discrepancies and Verification Notes

The following list records every stage where runtime code execution behavior differs from static documentation assumptions:

1. **Macro Scenario and Expected Loss Micro-Sample Fixtures**: In Stage 13, `run_expected_loss.py` and `run_macro_scenarios.py` execute on a 3-loan micro-sample DataFrame test fixture ($29,000 total EAD, $1,950 total EL, $9,384.73 scenario ECL) rather than processing all 235,628 OOT loans. Full portfolio staging and ECL calculations are executed separately by `run_staging.py` and `run_ecl.py` ($278.48M total staged ECL).
2. **LGD Stage 1 Classifier AUC Metric Logging**: In Stage 9, `run_lgd_training.py` logs the Stage 1 recovery classifier AUC (`0.6416`) to standard stdout during execution, but does not export this value into `outputs/tables/lgd_calibration.csv` (which stores decile MAE calibration error figures).
3. **Absence of 2015 Out-of-Time Data**: In Stage 2, the OOT validation set uses 2014 vintage data because zero loans originated in 2015 exist in `datasets/loan_data_2007_2014.csv`.
