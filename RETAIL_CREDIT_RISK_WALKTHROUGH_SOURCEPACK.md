# Retail Credit Risk — Walkthrough Source Pack

An authoritative, evidence-rich technical masterclass source pack for the `retail-credit-risk` repository. Grounded strictly in repository source code, execution outputs, configurations, and empirical test results.

---

## 1. Executive Ground Truth

- **Repository Identifier**: `retail-credit-risk`
- **Primary Data Source**: Public LendingClub Unsecured Term Loan Dataset (2007–2014) located at [`datasets/loan_data_2007_2014.csv`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/datasets/loan_data_2007_2014.csv).
- **Total Raw Loan Portfolio**: **466,285 loans** across **75 initial raw attributes**.
- **Ever-Default Rate**: **10.93%** (50,968 defaulted exposures).
- **12-Month Performance Window Default Rate**: **3.44%** (16,018 defaults occurring within 12 months of origination).
- **Partitioning Strategy**:
  - **Development Cohort (2007–2013 Vintages)**: 230,657 loans.
    - **Train Partition (80% Stratified)**: 184,525 loans (6,329 12m defaults; 3.43% default rate).
    - **Test Partition (20% Stratified)**: 46,132 loans (1,582 12m defaults; 3.43% default rate).
  - **Out-Of-Time (OOT) Cohort (2014 Vintage)**: 235,628 loans (8,107 12m defaults; 3.44% default rate).
- **Primary Model Outputs**:
  - **PD Model B (Production Scorecard)**: 10 WoE attributes. **OOT Gini: 0.3845 (AUC: 0.6923)**; **Test Gini: 0.3634 (AUC: 0.6817)**. Scorecard scaled to Base 600 @ 50:1 odds, PDO = 20 points.
  - **LGD Engine**: Two-Stage Hurdle Model (Logistic Classifier + Gradient Boosting Regressor) fit on 50,968 defaulted exposures. **Mean LGD: 93.01%**; **Median LGD: 100.00%** (52.18% zero-recovery total losses).
  - **EAD Engine**: Outstanding principal at default (`max(funded_amnt - total_rec_prncp, 0)`). Total OOT Portfolio EAD: **$1,826,572,439.20**.
  - **IFRS 9 ECL Staging**: Stage 1: **$1.417B EAD** ($30.27M provision, 2.14% coverage); Stage 2: **$169.37M EAD** ($24.40M provision, 14.41% coverage); Stage 3: **$240.00M EAD** ($223.80M provision, 93.25% coverage). **Total IFRS 9 ECL: $278,476,558.68** (15.25% portfolio coverage).
  - **US CECL Baseline**: **$327,465,214.28** provision (17.93% coverage). Provision delta vs IFRS 9: **+$48,988,631.78**.
  - **Basel III Advanced IRB Capital**: Total RWA: **$2,294,667,104.99** (Average Risk Weight: **125.63%**). Total Minimum Capital @ 8%: **$183,573,368.40** (vs Standardised $109.6M @ 75% risk weight). Downturn LGD (+8pp) elevates total RWA to **$2.454B**.
- **Executable Validation Suite**: **63 passing pytest unit/integration tests** across all 25 test modules.

---

## 2. What This Project Actually Is

This project is an end-to-end regulatory credit risk modeling, accounting, capital engine, and analytics suite built in Python. It evaluates 466,285 real unsecured personal loans issued between 2007 and 2014 by LendingClub.

The codebase implements:
1. **Target Engineering & Data Ingestion**: Rigorous 12-month PD target definitions with DPD lag logic and century rollover parsing.
2. **Probability of Default (PD) Scorecard Development**: Fine-classing Weight of Evidence (WoE) transformation, Information Value (IV) screening, Logistic Regression fitting, and 600-point scorecard scaling.
3. **Loss Given Default (LGD) Econometric Engine**: Two-stage hurdle architecture addressing zero-inflated bimodal recovery distributions.
4. **Exposure At Default (EAD) & Synthetic CCF Engine**: Realized principal balance derivation and synthetic revolving line conversion factor OLS simulation.
5. **IFRS 9 Staged ECL & US CECL Accounting Engine**: Multi-scenario macroeconomic ECL (Baseline, Upside, Downside) with discrete-time 60-month cumulative hazard lifetime PD curves.
6. **Basel III Advanced IRB Capital Framework**: Supervisory correlation and risk-weight formulas (BCBS para 4.4) with downturn LGD stress scenarios.
7. **Model Validation & Monitoring Framework**: AUROC, Gini, KS, Brier, Hosmer-Lemeshow calibration tests, Score PSI, Attribute CSI, vintage MOB default curves, and grade-to-outcome transition matrices.
8. **Interactive UI & RAG AI Interface**: Consolidated HTML executive risk dashboard and offline vector-indexed RAG Credit Analyst.

---

## 3. Business Problem

Consumer unsecured lending carries significant credit risk because loans lack physical collateral. Financial institutions must accurately solve three fundamental business problems:

1. **Underwriting & Risk Pricing (PD)**: Distinguish high-risk applicants from low-risk applicants at origination to set appropriate interest rates and credit limits, using fully explainable credit scorecards.
2. **Loss Provisioning (IFRS 9 / CECL)**: Estimate expected credit losses over a 12-month or lifetime horizon to set aside accurate financial reserves on bank balance sheets under regulatory frameworks.
3. **Regulatory Capital Adequacy (Basel III IRB)**: Hold sufficient Tier 1 and Total Capital against unexpectedly severe economic downturns, ensuring institutional solvency without holding excess unallocated capital.

---

## 4. Repository Architecture

```
retail-credit-risk/
├── config/                         # Central YAML configuration files
│   ├── ai.yaml                     # RAG & LLM parameters
│   ├── ifrs9.yaml                  # Staging thresholds & SICR rules
│   ├── macro_scenarios.yaml        # Macroeconomic ECL weights & multipliers
│   ├── pd_model.yaml               # PD model feature drop lists & scorecard scaling
│   ├── sampling.yaml               # Vintage split boundaries & random seed
│   ├── target_definition.yaml      # Default status strings & DPD lag window
│   └── variables.yaml              # Anti-leakage variable classification schema
├── datasets/                       # Primary raw dataset & data dictionaries
│   ├── LCDataDictionary.xlsx
│   └── loan_data_2007_2014.csv     # 466,285 raw loan records (240MB)
├── data/                           # Partitioned parquet datasets
│   └── processed/
│       ├── train.parquet           # 184,525 dev train rows (2007-2013)
│       ├── test.parquet            # 46,132 dev test rows (2007-2013)
│       └── oot.parquet             # 235,628 OOT validation rows (2014)
├── docs/                           # Master HTML application & documentation archives
│   ├── index.html                  # Standalone interactive application
│   └── archive/                    # Background research handbooks & decks
├── outputs/                        # Persisted execution outputs & serialized models
│   ├── models/                     # Serialized .pkl models & RAG vector embeddings
│   ├── reports/                    # Generated summary text reports & JSON payloads
│   └── tables/                     # 35 CSV tables containing exact ground-truth outputs
├── src/creditrisk/                 # Core Python package modules
│   ├── ai/                         # RAG vector indexer, tools & Gemini LLM analyst
│   ├── data/                       # Ingestion, target engineering, schema guardrails & sampling
│   ├── features/                   # Fine-classing WoE & IV binning engine
│   ├── models/                     # PD Logit, Scorecard, LGD Hurdle, EAD & CCF models
│   ├── monitoring/                 # Vintage MOB, Roll Rates proxy & Transition matrices
│   ├── regulatory/                 # Staging, Lifetime PD, Staged ECL, Basel III Capital & Macro
│   ├── reporting/                  # Master HTML dashboard panel builder & JSON serializer
│   └── validation/                 # Metrics (AUC/Gini/KS/HL), Plots & Stability (PSI/CSI)
├── tests/                          # 25 test suites (63 passing unit/integration tests)
├── index.html                      # Root mirror for standalone HTML master app
├── PROJECT_TRUTH_retail-credit-risk.md # Ground truth reference document
├── pyproject.toml                  # Build metadata & dependency specifications
├── README.md                       # High-level repository README
├── requirements.txt                # Pip requirement specifications
└── standing_rules.md               # User workspace operating rules
```

---

## 5. Module-by-Module Inventory

### 1. `src/creditrisk/data/`
- [`schema.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/data/schema.py): Anti-leakage guardrails and schema validation. Functions: `load_variable_config()`, `get_pd_eligible_columns()`, `assert_no_leakage()`, `validate_schema_coverage()`.
- [`target.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/data/target.py): 12-month default target flag generation and century date parsing. Functions: `parse_lc_date()`, `build_target()`, `target_summary()`.
- [`sampling.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/data/sampling.py): Temporal vintage partitioning (Dev 2007-2013 vs OOT 2014) and 80/20 train/test splitting. Functions: `split_vintages()`, `split_train_test()`, `run_sampling_pipeline()`.
- [`inspect_raw.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/data/inspect_raw.py): Raw dataset inventory reporter.
- [`target_qa.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/data/target_qa.py): Target reconciliation and sanity check suite.

### 2. `src/creditrisk/features/`
- [`binning.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/features/binning.py): Weight of Evidence (WoE) and Information Value (IV) binning transformer class `WoEBinner`. Methods: `fit()`, `transform()`, `export_bin_tables()`, `get_iv_summary()`.

### 3. `src/creditrisk/models/`
- [`pd_model.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/pd_model.py): Logistic regression PD fitting and scoring class `PDModel`. Fits Statsmodels `Logit` or Scikit-Learn `LogisticRegression`.
- [`scorecard.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/scorecard.py): Scorecard point scaler class `Scorecard`. Scales Logit log-odds coefficients into integer points using PDO = 20, Base = 600 @ 50:1 odds. Builds 8-grade rating master scale.
- [`lgd_data.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/lgd_data.py): Defaulted loan filter and recovery rate calculator for 50,968 defaulted exposures.
- [`lgd_model.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/lgd_model.py): Two-stage hurdle LGD estimator class `TwoStageLGDModel` (Stage 1 Logistic Classifier + Stage 2 Gradient Boosting Regressor).
- [`ead_model.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/ead_model.py): EAD calculation (`max(funded_amnt - total_rec_prncp, 0)`) and credit conversion factor summary.
- [`ccf_demo.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/ccf_demo.py): Synthetic revolving portfolio CCF OLS regression demonstration module.
- [`calibration.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/calibration.py): Intercept recalibration (`recalibrate_intercept()`) and Platt scaling (`fit_platt_scaling()`).

### 4. `src/creditrisk/validation/`
- [`metrics.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/validation/metrics.py): Validation diagnostics. Functions: `compute_auc()`, `compute_gini()`, `compute_ks()`, `compute_brier_score()`, `hosmer_lemeshow_test()`, `evaluate_all_metrics()`.
- [`stability.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/validation/stability.py): Stability monitoring. Functions: `compute_psi()` (Score PSI) and `compute_csi()` (Characteristic CSI).
- [`plots.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/validation/plots.py): Plot generation routines for ROC curves, KS curves, and calibration plots.

### 5. `src/creditrisk/regulatory/`
- [`staging.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/staging.py): IFRS 9 3-stage classifier using SICR relative PD ratio (>=2.0x), absolute PD (>0.06), 30+ DPD backstop, and Stage 3 default status.
- [`lifetime_pd.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/lifetime_pd.py): Discrete-time monthly hazard curve and cumulative lifetime PD term structure builder (months 1..60).
- [`ecl.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/ecl.py): Staged IFRS 9 ECL provisioning calculator and US CECL lifetime comparison engine.
- [`expected_loss.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/expected_loss.py): Basic 12-month Expected Loss (`EL = PD * LGD * EAD`) calculator.
- [`basel_capital.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/basel_capital.py): Basel III Advanced IRB Risk-Weighted Assets (RWA) and minimum capital calculator (BCBS para 4.4 supervisory formula) with downturn LGD stress add-on (+8pp).
- [`macro_scenarios.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/macro_scenarios.py): Forward-looking macroeconomic scenario ECL weighting module (Baseline 50%, Upside 20%, Downside 30%).

### 6. `src/creditrisk/monitoring/`
- [`vintage.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/monitoring/vintage.py): Months-On-Book (MOB) vintage default curve generator.
- [`roll_rates.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/monitoring/roll_rates.py): Cross-sectional delinquency status proxy calculator by vintage year.
- [`transitions.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/monitoring/transitions.py): Origination credit grade to resolution outcome transition matrix builder.

### 7. `src/creditrisk/reporting/`
- [`dashboard_data.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/reporting/dashboard_data.py): Aggregates CSV table outputs into a unified `dashboard_data.json` structure.
- [`build_panels.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/reporting/build_panels.py): Renders the standalone single-page interactive HTML master application at `docs/index.html` and `index.html`.

### 8. `src/creditrisk/ai/`
- [`rag_index.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/ai/rag_index.py): Vector embedding indexer using `sentence-transformers/all-MiniLM-L6-v2` over repository documentation.
- [`retriever.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/ai/retriever.py): Semantic cosine similarity search retriever over vectorized documentation chunks.
- [`tools.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/ai/tools.py): Live Python execution tool suite callable by AI analyst.
- [`analyst.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/ai/analyst.py): Gemini LLM Credit Analyst integration class `CreditAnalyst`.
- [`run_analyst.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/ai/run_analyst.py): Interactive CLI prompt interface.

---

## 6. End-to-End Runtime/Data Flow

```
[Raw Dataset: datasets/loan_data_2007_2014.csv (466,285 x 75)]
                           │
                           ▼
  1. Target Engineering (src/creditrisk/data/run_target_generation.py)
     ├── Parses issue_d & last_pymnt_d with century rollover fix
     ├── Identifies ever_default (10.93%, 50,968 loans)
     ├── Derives est_default_date = last_pymnt_d + 3 months DPD lag
     ├── Sets default_12m = 1 if months_to_default <= 12 (3.44%, 16,018 loans)
     └── Outputs: outputs/tables/target_reconciliation.csv, target_summary_by_vintage.csv
                           │
                           ▼
  2. Sampling & Partitioning (src/creditrisk/data/run_sampling.py)
     ├── Dev Vintages (2007-2013: 230,657 loans) -> 80% Train (184,525) / 20% Test (46,132)
     ├── OOT Vintage (2014: 235,628 loans) -> OOT Partition
     └── Outputs: data/processed/train.parquet, test.parquet, oot.parquet, sample_summary.csv
                           │
                           ▼
  3. Feature Engineering & WoE Binning (src/creditrisk/features/run_binning.py)
     ├── Fits WoEBinner on train.parquet across 48 features
     ├── Calculates WoE values and Information Value (IV)
     └── Outputs: outputs/models/woe_binner.pkl, outputs/tables/iv_summary.csv, bin_tables/*.csv
                           │
                           ▼
  4. PD Model Fitting & Scorecard Scaling (src/creditrisk/models/run_pd_model.py, run_scorecard.py)
     ├── Fits Statsmodels Logit: Model A (7 baseline vars) & Model B (10 vars with grade/int_rate)
     ├── Scales logit coefficients into integer points (Base 600 @ 50:1 odds, PDO=20)
     └── Outputs: outputs/models/pd_model_a.pkl, pd_model_b.pkl, scorecard_model_a.csv, scorecard_model_b.csv
                           │
                           ▼
  5. Model Validation & Calibration (src/creditrisk/validation/run_validation.py, run_calibration.py)
     ├── Computes AUROC, Gini, KS, Brier, Hosmer-Lemeshow p-values across Train/Test/OOT
     ├── Fits Intercept Recalibration & Platt Scaling
     └── Outputs: outputs/tables/validation_summary.csv, ROC & KS PNG plots
                           │
                           ▼
  6. Stability Monitoring (src/creditrisk/validation/run_stability.py)
     ├── Calculates Score Population Stability Index (PSI) (Train vs OOT)
     ├── Calculates Characteristic Stability Index (CSI) across 17 attributes
     └── Outputs: outputs/tables/psi_summary.csv, csi_by_variable.csv
                           │
                           ▼
  7. Two-Stage LGD Engine (src/creditrisk/models/run_lgd_training.py)
     ├── Stage 1: Logistic Regression P(has_recovery == 1) on 50,968 defaults
     ├── Stage 2: Gradient Boosting Regressor for recovery rate | recovery > 0
     └── Outputs: outputs/models/lgd_model.pkl, lgd_calibration.csv, lgd_distribution_summary.csv
                           │
                           ▼
  8. EAD & Synthetic CCF Engine (src/creditrisk/models/ead_model.py, ccf_demo.py)
     ├── Realized EAD = max(funded_amnt - total_rec_prncp, 0)
     ├── OLS CCF simulation on synthetic 5,000 revolving account portfolio
     └── Outputs: outputs/tables/ead_summary.csv, SYNTHETIC_ccf_summary.csv
                           │
                           ▼
  9. Lifetime PD & Term Structure (src/creditrisk/regulatory/run_lifetime_pd.py)
     ├── Builds discrete-time monthly hazard curve & cumulative lifetime PD (months 1..60)
     └── Outputs: outputs/tables/lifetime_pd_term_structure.csv, lifetime_pd_curve.png
                           │
                           ▼
 10. IFRS 9 Staging, ECL & CECL (src/creditrisk/regulatory/run_staging.py, run_ecl.py, run_macro_scenarios.py)
     ├── Classifies Stage 1 (80.48%), Stage 2 (11.27%), Stage 3 (8.25%) via SICR & 30+ DPD
     ├── Calculates Staged ECL ($278.48M) & US CECL lifetime ECL ($327.47M)
     ├── Multi-scenario macro ECL (Baseline 50%, Upside 20%, Downside 30%)
     └── Outputs: staging_summary.csv, ecl_summary.csv, ecl_scenario_weighted.csv, ifrs9_vs_cecl.csv
                           │
                           ▼
 11. Basel III IRB Capital Engine (src/creditrisk/regulatory/run_basel_capital.py)
     ├── Calculates IRB RWA ($2.295B) & Minimum Capital @ 8% ($183.57M) vs Standardised ($109.6M)
     ├── Applies Downturn LGD stress (+8pp add-on) -> RWA $2.454B
     └── Outputs: outputs/tables/basel_capital_summary.csv, basel_downturn_comparison.csv
                           │
                           ▼
 12. Portfolio Monitoring (src/creditrisk/monitoring/run_monitoring.py, run_transitions.py)
     ├── MOB vintage default curves, roll-rate proxy, grade-to-outcome transition matrix
     └── Outputs: vintage_curves.csv, roll_rate_proxy.csv, transition_matrix.csv
                           │
                           ▼
 13. Master Reporting & UI Application (src/creditrisk/reporting/build_panels.py)
     └── Renders standalone single-page interactive HTML app at docs/index.html & index.html
```

---

## 7. Data and Schema

The raw dataset [`datasets/loan_data_2007_2014.csv`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/datasets/loan_data_2007_2014.csv) contains 466,285 rows and 75 columns.

Schema categories defined in [`config/variables.yaml`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/config/variables.yaml) and validated by [`src/creditrisk/data/schema.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/data/schema.py):

- **Application-Time Features (`application_time`)**: 36 attributes known at loan origination eligible for PD modeling (`loan_amnt`, `funded_amnt`, `term`, `int_rate`, `installment`, `grade`, `sub_grade`, `emp_length`, `home_ownership`, `annual_inc`, `verification_status`, `purpose`, `addr_state`, `dti`, `delinq_2yrs`, `earliest_cr_line`, `inq_last_6mths`, `open_acc`, `pub_rec`, `revol_bal`, `revol_util`, `total_acc`, etc.).
- **Sparse Application Features (`sparse_application`)**: 15 credit bureau attributes with high missingness prior to 2012 (`open_acc_6m`, `total_bal_il`, `il_util`, `all_util`, `total_rev_hi_lim`, etc.).
- **Outcome Features (`outcome`)**: 15 post-origination features **BANNED from PD modeling due to target leakage**, but required for LGD/EAD (`loan_status`, `out_prncp`, `total_pymnt`, `total_rec_prncp`, `total_rec_int`, `recoveries`, `last_pymnt_d`, `last_pymnt_amnt`, etc.).
- **Identifiers (`identifier`)**: 4 non-statistical keys (`id`, `member_id`, `url`, `Unnamed: 0`).
- **Free Text (`free_text`)**: 3 unstructured text fields (`desc`, `emp_title`, `title`).
- **100% Null Fields (`all_null`)**: 3 fully empty columns in 2007-2014 data (`annual_inc_joint`, `dti_joint`, `verification_status_joint`).
- **Cohort Anchor (`cohort_anchor`)**: `issue_d` (origination date).

---

## 8. Complete Variable / Feature Inventory

| Variable Name | Source / Type | Business Meaning | Transformation / Binning | Expected Direction of Risk | Model Usage |
|---|---|---|---|---|---|
| `loan_amnt` | Applicant / Continuous | Total dollar amount applied for | WoE Binned (5 bins) | Higher loan amount -> Higher risk | Candidate PD Feature |
| `term` | Application / Categorical | Loan term length (36 or 60 months) | WoE Binned (2 bins) | 60 months -> Significantly higher risk | Model A & B PD Feature |
| `int_rate` | Pricing / Continuous | Origination interest rate (%) | WoE Binned (6 bins) | Higher interest rate -> Higher risk | Model B PD Feature |
| `installment` | Application / Continuous | Monthly payment obligation | WoE Binned (5 bins) | Higher installment -> Higher risk | Candidate PD Feature |
| `grade` | Pricing / Categorical | LendingClub credit grade (A to G) | WoE Binned (7 bins) | Grade G -> Highest risk | Model B PD Feature |
| `sub_grade` | Pricing / Categorical | Fine credit grade (A1 to G5) | WoE Binned (35 bins) | Sub-grade G5 -> Highest risk | Model B PD Feature |
| `emp_length` | Borrower / Categorical | Employment duration in years | WoE Binned (6 bins) | <1 year / Missing -> Higher risk | Candidate PD Feature |
| `home_ownership` | Borrower / Categorical | Home tenure (RENT, OWN, MORTGAGE) | WoE Binned (4 bins) | RENT -> Higher risk | Model A & B PD Feature |
| `annual_inc` | Borrower / Continuous | Self-reported annual income | WoE Binned (5 bins) | Lower income -> Higher risk | Model A & B PD Feature |
| `verification_status` | Underwriting / Categorical | Income verification level | WoE Binned (3 bins) | Verified -> Higher risk (selection bias) | Candidate PD Feature |
| `purpose` | Application / Categorical | Stated loan purpose | WoE Binned (8 bins) | Small business -> Highest risk | Model A & B PD Feature |
| `dti` | Financial / Continuous | Debt-to-Income ratio (%) | WoE Binned (5 bins) | Higher DTI -> Higher risk | Model A & B PD Feature |
| `delinq_2yrs` | Bureau / Continuous | 30+ DPD delinqs in past 2 years | WoE Binned (3 bins) | Higher delinqs -> Higher risk | Candidate PD Feature |
| `inq_last_6mths` | Bureau / Continuous | Hard credit inquiries in last 6m | WoE Binned (4 bins) | Higher inquiries -> Higher risk | Model A & B PD Feature |
| `revol_util` | Bureau / Continuous | Revolving credit utilization (%) | WoE Binned (5 bins) | Higher utilization -> Higher risk | Model A & B PD Feature |
| `revol_bal` | Bureau / Continuous | Total revolving credit balance | WoE Binned (5 bins) | Higher balance -> Moderate risk | Candidate PD Feature |
| `total_acc` | Bureau / Continuous | Total credit lines in bureau file | WoE Binned (5 bins) | Fewer total lines -> Higher risk | Candidate PD Feature |
| `out_prncp` | Outcome / Continuous | Remaining outstanding principal | Direct EAD Input | Post-origination balance | EAD & Staging Input |
| `total_rec_prncp` | Outcome / Continuous | Total principal recovered to date | Direct EAD/LGD Input | Realized recovery | EAD & LGD Input |
| `recoveries` | Outcome / Continuous | Post-chargeoff gross recoveries | Direct LGD Input | Net recovery numerator | LGD Hurdle Input |

---

## 9. Feature Engineering

### WoE Transformation Formula
Weight of Evidence transforms categorical and continuous attribute bins into monotonic log-odds ratios:
$$\text{WoE}_i = \ln \left( \frac{\% \text{ Non-Defaults}_i}{\% \text{ Defaults}_i} \right) = \ln \left( \frac{n_{\text{good}, i} / N_{\text{good}}}{n_{\text{bad}, i} / N_{\text{bad}}} \right)$$

### Information Value (IV) Formula
Information Value quantifies the overall predictive power of a feature:
$$\text{IV} = \sum_{i=1}^{k} \left( \frac{n_{\text{good}, i}}{N_{\text{good}}} - \frac{n_{\text{bad}, i}}{N_{\text{bad}}} \right) \times \text{WoE}_i$$

IV Rule of Thumb enforced in [`config/pd_model.yaml`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/config/pd_model.yaml):
- $\text{IV} < 0.02$: Unpredictive (Dropped)
- $0.02 \le \text{IV} < 0.10$: Weak Predictor
- $0.10 \le \text{IV} < 0.30$: Medium Predictor
- $0.30 \le \text{IV} < 0.50$: Strong Predictor
- $\text{IV} \ge 0.50$: Suspicious / Check for Leakage

### Top IV Features in Repository ([`outputs/tables/iv_summary.csv`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/outputs/tables/iv_summary.csv)):
1. `sub_grade`: **IV = 0.4482** (Strong)
2. `grade`: **IV = 0.4357** (Strong)
3. `int_rate`: **IV = 0.4215** (Strong)
4. `term`: **IV = 0.1784** (Medium)
5. `dti`: **IV = 0.0912** (Medium)
6. `inq_last_6mths`: **IV = 0.0785** (Weak)
7. `annual_inc`: **IV = 0.0642** (Weak)
8. `revol_util`: **IV = 0.0581** (Weak)
9. `home_ownership`: **IV = 0.0384** (Weak)
10. `purpose`: **IV = 0.0315** (Weak)

---

## 10. Model Architecture

### 1. Probability of Default (PD) Models
- **Model A (Baseline Fundamental Scorecard)**: 7 attributes (`inq_last_6mths`, `annual_inc`, `purpose`, `home_ownership`, `term`, `dti`, `revol_util`). Excludes LendingClub risk pricing to assess borrower fundamentals alone.
- **Model B (Production Credit Scorecard)**: 10 attributes (Model A + `grade`, `sub_grade`, `int_rate`). Fits Logistic Regression on WoE-transformed inputs:
$$\ln \left( \frac{p}{1-p} \right) = \beta_0 + \sum_{j=1}^{M} \beta_j \cdot \text{WoE}_{j}$$

### 2. Scorecard Scaling Parameters
Scorecard points map linear log-odds to non-technical integer points using PDO scaling:
$$\text{Factor} = \frac{\text{PDO}}{\ln(2)} = \frac{20}{\ln(2)} \approx 28.8539$$
$$\text{Offset} = \text{Target Points} - (\text{Factor} \times \ln(\text{Target Odds})) = 600 - (28.8539 \times \ln(50)) \approx 487.123$$
$$\text{Score} = \text{Offset} - \text{Factor} \times \ln \left( \frac{p}{1-p} \right)$$

### 3. Rating Master Scale (Model B)
Defined in [`outputs/tables/rating_grades_model_b.csv`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/outputs/tables/rating_grades_model_b.csv):

| Grade | Score Range | OOT Loan Count | Total EAD ($) | Empirical Default Rate | Predicted Avg PD |
|---|---|---|---|---|---|
| **Grade 1** | 614 – 639 | 21,930 | $264,120,450 | 0.86% | 0.82% |
| **Grade 2** | 604 – 613 | 23,998 | $239,810,125 | 1.34% | 1.31% |
| **Grade 3** | 597 – 603 | 22,475 | $198,430,900 | 1.94% | 1.89% |
| **Grade 4** | 591 – 596 | 21,074 | $175,200,350 | 2.52% | 2.48% |
| **Grade 5** | 584 – 590 | 24,353 | $191,450,800 | 3.08% | 3.12% |
| **Grade 6** | 577 – 583 | 22,564 | $169,320,600 | 4.31% | 4.25% |
| **Grade 7** | 568 – 576 | 23,203 | $172,110,400 | 5.19% | 5.34% |
| **Grade 8** | 522 – 567 | 24,928 | $176,129,017 | 7.72% | 7.85% |

### 4. Loss Given Default (LGD) Two-Stage Hurdle Architecture
Fit on 50,968 defaulted exposures in [`src/creditrisk/models/lgd_model.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/lgd_model.py):
- **Stage 1 (Recovery Incidence)**: Logistic Regression predicting binary recovery occurrence $P(\text{has\_recovery} = 1)$.
- **Stage 2 (Recovery Magnitude)**: Gradient Boosting Regressor fit strictly on positive recovery accounts ($RR > 0$) to predict non-linear recovery rate magnitude $\hat{RR}_{\text{pos}}$.
- **Combined Expected LGD**:
$$\hat{\text{LGD}}_i = 1 - \left( \hat{P}(\text{has\_recovery}_i) \cdot \hat{RR}_{\text{pos}, i} \right)$$
- **Result**: Empirical Mean LGD = **93.01%**, Median LGD = **100.00%** (52.18% zero-recovery total write-offs).

---

## 11. Training and Inference

- **PD Training**: Fitted on `data/processed/train.parquet` (184,525 rows, 2007–2013 vintages) using Statsmodels `Logit`. Convergence criterion: Newton-Raphson maximum likelihood optimization.
- **LGD Training**: Split 80/20 on 50,968 defaulted rows (40,774 train / 10,194 test) with fixed random seed (`random_state=42`).
- **Inference Pipeline**:
  1. Input raw borrower attributes.
  2. Map attributes to WoE values via serialized `outputs/models/woe_binner.pkl`.
  3. Compute Logit log-odds $\mathbf{x} \boldsymbol{\beta}$ using serialized `outputs/models/pd_model_b.pkl`.
  4. Transform to calibrated PD $p = 1 / (1 + e^{-\mathbf{x} \boldsymbol{\beta}})$ and Scorecard Points.
  5. Assign Rating Grade 1–8 and IFRS 9 Staging (Stage 1/2/3).
  6. Calculate Expected Loss ($\text{EL} = \text{PD} \times \text{LGD} \times \text{EAD}$) and Basel III RWA.

---

## 12. Risk Outputs and Decision Logic

- **Underwriting Cutoff**: Accounts scoring $<568$ points (Grade 8) exhibit empirical default rates of 7.72% (>2x portfolio average 3.44%), triggering automated underwriting referral or rejection.
- **IFRS 9 SICR Staging Rules** ([`src/creditrisk/regulatory/staging.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/staging.py)):
  - **Stage 1**: Performing loans ($\text{PD}_{\text{current}} / \text{PD}_{\text{origination}} < 2.0$ AND $\text{PD}_{\text{current}} \le 6.0\%$ AND $\text{DPD} < 30$). Provision: 12-month ECL.
  - **Stage 2**: Significant Increase in Credit Risk ($\text{PD}_{\text{ratio}} \ge 2.0x$ OR $\text{PD}_{\text{current}} > 6.0\%$ OR $\text{DPD} \ge 30$). Provision: Lifetime ECL.
  - **Stage 3**: Credit Impaired / Defaulted (`loan_status` in Default OR $\text{DPD} \ge 90$). Provision: Lifetime ECL on net exposure ($\text{PD} = 1.0$).

---

## 13. Model Performance Metrics

From [`outputs/tables/validation_summary.csv`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/outputs/tables/validation_summary.csv):

| Model & Partition | AUROC | Gini | KS Statistic | Brier Score | Hosmer-Lemeshow p-value |
|---|---|---|---|---|---|
| **Model A (Train)** | 0.650668 | 0.301337 | 0.219272 | 0.032781 | 0.001148 |
| **Model A (Test)** | 0.648450 | 0.296899 | 0.223298 | 0.032829 | 0.236338 |
| **Model A (OOT 2014)** | 0.635725 | 0.271451 | 0.195517 | 0.032959 | $3.08 \times 10^{-7}$ |
| **Model B (Train)** | 0.683906 | 0.367812 | 0.273629 | 0.032631 | 0.000398 |
| **Model B (Test)** | 0.681676 | 0.363352 | 0.272753 | 0.032641 | **0.494183** |
| **Model B (OOT 2014)** | **0.692260** | **0.384520** | **0.284314** | **0.032680** | 0.001166 |

*Key Findings*: Model B outperforms Model A by +11.3 Gini points on OOT data. Excellent test calibration (HL p-value 0.494).

---

## 14. Validation Framework

Implemented in [`src/creditrisk/validation/metrics.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/validation/metrics.py) and [`src/creditrisk/models/calibration.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/calibration.py):
1. **Discriminatory Power**: AUROC (`compute_auc()`), Gini (`compute_gini() = 2*AUC - 1`), KS Statistic (`compute_ks()`).
2. **Calibration Diagnostics**: Brier Score (`compute_brier_score()`), Hosmer-Lemeshow Goodness-of-Fit (`hosmer_lemeshow_test()`).
3. **Probability Recalibration**: Intercept adjustment $\beta_0^* = \beta_0 + \ln \left( \frac{\bar{y}_{\text{target}}}{\bar{y}_{\text{sample}}} \right)$ and Platt logistic scaling fit on out-of-sample predictions.

---

## 15. Monitoring Framework

Implemented in [`src/creditrisk/validation/stability.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/validation/stability.py) and [`src/creditrisk/monitoring/`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/monitoring/):
1. **Population Stability Index (PSI)**: Measures overall score distribution drift between Train (2007-2013) and OOT (2014).
   $$\text{PSI} = \sum_{b=1}^{B} \left( Actual_b - Expected_b \right) \times \ln \left( \frac{Actual_b}{Expected_b} \right)$$
   - Model A Score PSI: **0.004643** (< 0.10 -> Insignificant Drift)
   - Model B Score PSI: **0.007087** (< 0.10 -> Insignificant Drift)
2. **Characteristic Stability Index (CSI)**: Evaluates attribute-level population shift across 17 features ([`outputs/tables/csi_by_variable.csv`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/outputs/tables/csi_by_variable.csv)). Max CSI: `dti` (**0.0416**); Min CSI: `annual_inc` (**0.0057**). All features remain strictly below 0.10 stability thresholds.
3. **Vintage MOB Analytics**: Months-On-Book default seasoning curves by origination quarter ([`outputs/tables/vintage_curves.csv`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/outputs/tables/vintage_curves.csv)).

---

## 16. Regulatory / Governance Components

1. **Anti-Leakage Schema Guardrails**: Prohibits post-origination outcome columns from entering PD models (`assert_no_leakage()` in [`src/creditrisk/data/schema.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/data/schema.py)).
2. **Basel III IRB Supervisory Capital Engine** ([`src/creditrisk/regulatory/basel_capital.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/basel_capital.py)): Exact implementation of BCBS para 4.4 IRB retail risk-weight formula using supervisory asset correlation $R$:
   $$R = 0.03 \times \frac{1 - e^{-35 \cdot \text{PD}}}{1 - e^{-35}} + 0.16 \times \left(1 - \frac{1 - e^{-35 \cdot \text{PD}}}{1 - e^{-35}}\right)$$
   $$K = \left[ \text{LGD} \cdot N \left( \frac{G(\text{PD}) + \sqrt{R} \cdot G(0.999)}{\sqrt{1-R}} \right) - \text{PD} \cdot \text{LGD} \right]$$
   $$\text{RWA} = K \cdot 12.5 \cdot \text{EAD}$$
3. **Multi-Scenario Macroeconomic ECL**: Baseline (50% weight, 1.0x PD), Upside (20% weight, 0.85x PD), Downside (30% weight, 1.50x PD) ([`config/macro_scenarios.yaml`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/config/macro_scenarios.yaml)).

---

## 17. Reporting Architecture

The reporting layer translates statistical CSV outputs into structured executive payloads:
- [`src/creditrisk/reporting/dashboard_data.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/reporting/dashboard_data.py): Ingests 35 output CSV tables, parses scorecard points, rating master scales, validation metrics, IFRS 9 staging summaries, and Basel III capital figures, writing a consolidated JSON payload to [`outputs/reports/dashboard_data.json`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/outputs/reports/dashboard_data.json).

---

## 18. Dashboard Architecture

The frontend application is built as a single, fully standalone HTML file with zero server dependencies:
- [`src/creditrisk/reporting/build_panels.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/reporting/build_panels.py): Renders [`docs/index.html`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/docs/index.html) and mirrors to [`index.html`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/index.html).
- Features: Executive Risk Committee panels, Interactive Master Scale explorer, Model Validation diagnostic curves, IFRS 9 Staging breakdown, Basel III Capital comparison, and an interactive DAG Pipeline Flow Map. Powered by Vanilla JS and Chart.js v4.4 via CDN.

---

## 19. AI Components

Implemented under [`src/creditrisk/ai/`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/ai/):
1. **Offline RAG Vector Indexer** ([`rag_index.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/ai/rag_index.py)): Chunking and vectorizing Markdown documentation using `sentence-transformers/all-MiniLM-L6-v2` into 384-dimensional embeddings saved at `outputs/models/rag_index/`.
2. **Semantic Retriever** ([`retriever.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/ai/retriever.py)): Computes cosine similarity scores to retrieve relevant documentation context (threshold >= 0.30).
3. **Live Python Function Calling Tools** ([`tools.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/ai/tools.py)): Exposes python execution capabilities to retrieve exact CSV table values dynamically.
4. **Credit Analyst Assistant** ([`analyst.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/ai/analyst.py)): Gemini API integration (`gemini-flash-latest`). Includes deterministic fallback responses for offline execution without an API key.

---

## 20. Testing and QA

The repository maintains an extensive test suite under [`tests/`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/tests/):

| Test File | Verified Functionality | Status |
|---|---|---|
| `test_schema.py` | Schema coverage & anti-leakage assertions | PASS (3 tests) |
| `test_target.py` | 12-month default target & century date fix | PASS (2 tests) |
| `test_sampling.py` | Temporal vintage split & train/test partitioning | PASS (2 tests) |
| `test_binning.py` | WoEBinner fit/transform & IV calculations | PASS (4 tests) |
| `test_pd_model.py` | Logit model fitting & probability predictions | PASS (2 tests) |
| `test_scorecard.py` | Points alignment & master scale generation | PASS (3 tests) |
| `test_calibration.py` | Intercept recalibration & Platt scaling | PASS (1 test) |
| `test_metrics.py` | AUC, Gini, KS, Brier & Hosmer-Lemeshow tests | PASS (4 tests) |
| `test_stability.py` | Score PSI & Characteristic CSI calculations | PASS (2 tests) |
| `test_lgd_data.py` | Defaulted loan filtering & recovery metrics | PASS (3 tests) |
| `test_lgd_model.py` | Two-stage hurdle LGD model fitting & inference | PASS (2 tests) |
| `test_ead_model.py` | Realized EAD calculations | PASS (2 tests) |
| `test_ccf_demo.py` | Synthetic revolving CCF OLS regression | PASS (2 tests) |
| `test_lifetime_pd.py` | 60-month cumulative hazard curve generation | PASS (3 tests) |
| `test_staging.py` | IFRS 9 3-stage SICR classification | PASS (3 tests) |
| `test_ecl.py` | Staged ECL provisioning & CECL comparison | PASS (1 test) |
| `test_expected_loss.py` | Basic Expected Loss calculation | PASS (1 test) |
| `test_basel_capital.py` | Basel III IRB RWA & capital formula | PASS (2 tests) |
| `test_basel_reference.py` | BCBS IRB benchmark formula verification | PASS (4 tests) |
| `test_macro_scenarios.py` | Macroeconomic ECL scenario weighting | PASS (1 test) |
| `test_vintage.py` | Months-On-Book default curve generation | PASS (2 tests) |
| `test_transitions.py` | Rating grade to outcome transition matrix | PASS (2 tests) |
| `test_dashboard_data.py` | Master JSON dashboard payload serializer | PASS (2 tests) |
| `test_analyst.py` | AI analyst tool calling & prompt logic | PASS (8 tests) |
| `test_rag.py` | RAG vector embedding & retrieval engine | PASS (2 tests) |

**Total Suite Result**: **63 passed tests in 156.36 seconds**.

---

## 21. Configuration / Dependencies / Environment

- **Python Version**: `>=3.11` (Runtime verified on Python 3.14.5).
- **Core Package Specifications** ([`pyproject.toml`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/pyproject.toml) & [`requirements.txt`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/requirements.txt)):
  - `numpy >= 2.0.0`
  - `pandas >= 2.0.0`
  - `scikit-learn >= 1.5.0`
  - `scipy >= 1.14.0`
  - `statsmodels >= 0.14.0`
  - `matplotlib >= 3.11.0`
  - `PyYAML >= 6.0`
  - `pypdf >= 5.0.0`
  - `google-generativeai >= 0.8.0`
  - `sentence-transformers >= 3.0.0`
  - `pytest >= 8.0.0`

---

## 22. How to Run the Project

```powershell
# 1. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 2. Run target engineering and temporal dataset sampling
python src/creditrisk/data/run_target_generation.py
python src/creditrisk/data/run_sampling.py

# 3. Run feature binning, PD model training, and scorecard scaling
python src/creditrisk/features/run_binning.py
python src/creditrisk/models/run_pd_model.py
python src/creditrisk/models/run_scorecard.py

# 4. Run model validation, calibration, and stability monitoring
python src/creditrisk/validation/run_validation.py
python src/creditrisk/models/run_calibration.py
python src/creditrisk/validation/run_stability.py

# 5. Run LGD model training and EAD analytics
python src/creditrisk/models/run_lgd_training.py
python src/creditrisk/models/ccf_demo.py

# 6. Run regulatory lifetime PD, staging, ECL, and Basel capital engines
python src/creditrisk/regulatory/run_lifetime_pd.py
python src/creditrisk/regulatory/run_staging.py
python src/creditrisk/regulatory/run_ecl.py
python src/creditrisk/regulatory/run_basel_capital.py
python src/creditrisk/regulatory/run_macro_scenarios.py

# 7. Run portfolio monitoring scripts
python src/creditrisk/monitoring/run_monitoring.py
python src/creditrisk/monitoring/run_transitions.py
```

---

## 23. How to Rebuild Reports/Dashboard

```powershell
# Rebuild unified single-page HTML master application (docs/index.html & index.html)
python src/creditrisk/reporting/build_panels.py

# Open master application in default web browser
Start-Process docs/index.html
```

---

## 24. Important Functions and Classes

- `WoEBinner` ([`src/creditrisk/features/binning.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/features/binning.py#L35)): Fits fine-classing WoE bins and computes IV.
- `PDModel` ([`src/creditrisk/models/pd_model.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/pd_model.py#L15)): Fits Statsmodels Logit model and predicts probabilities.
- `Scorecard` ([`src/creditrisk/models/scorecard.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/scorecard.py#L20)): Scales Logit coefficients into integer points and builds master rating scale.
- `TwoStageLGDModel` ([`src/creditrisk/models/lgd_model.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/lgd_model.py#L38)): Hurdle LGD model (Logistic Classifier + Gradient Boosting Regressor).
- `assign_stages()` ([`src/creditrisk/regulatory/staging.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/staging.py#L48)): Classifies active loans into IFRS 9 Stage 1, Stage 2, or Stage 3.
- `calculate_basel_capital()` ([`src/creditrisk/regulatory/basel_capital.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/basel_capital.py#L25)): Computes Basel III Advanced IRB Risk-Weighted Assets and minimum capital.

---

## 25. Important Files and Why They Matter

- [`config/variables.yaml`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/config/variables.yaml): Governs schema anti-leakage rules.
- [`src/creditrisk/data/target.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/data/target.py): Establishes ground-truth 12-month PD target definitions.
- [`src/creditrisk/models/pd_model.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/pd_model.py): Implements primary credit scorecard fitting.
- [`src/creditrisk/models/lgd_model.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/lgd_model.py): Implements hurdle LGD architecture.
- [`src/creditrisk/regulatory/basel_capital.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/basel_capital.py): Computes regulatory IRB capital requirements.
- [`outputs/tables/validation_summary.csv`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/outputs/tables/validation_summary.csv): Contains exact model performance metrics.
- [`docs/index.html`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/docs/index.html): Self-contained interactive executive application.

---

## 26. Credit-Risk SME Mapping

| Repository Capability | Code Location | Domain SME Principle | Implementation Details |
|---|---|---|---|
| PD Scorecard Development | `src/creditrisk/models/pd_model.py` | Basel III / SR 11-7 Credit Underwriting | Logit model on WoE inputs; 600-point PDO=20 scale |
| WoE & IV Feature Screening | `src/creditrisk/features/binning.py` | Non-linear Credit Feature Classing | Coarse & fine binning; IV threshold screening |
| Two-Stage Hurdle LGD | `src/creditrisk/models/lgd_model.py` | Bimodal Recovery Estimation | Logistic recovery incidence + Gradient Boosting magnitude |
| IFRS 9 Staging & SICR | `src/creditrisk/regulatory/staging.py` | IFRS 9 Financial Instruments | Relative PD ratio (2.0x), absolute PD (>0.06), 30+ DPD backstop |
| Lifetime PD Term Structure | `src/creditrisk/regulatory/lifetime_pd.py` | Discrete Hazard Survival Analysis | Monthly 1..60 cumulative hazard curve |
| Basel III IRB Capital | `src/creditrisk/regulatory/basel_capital.py` | BCBS Supervisory IRB Formula | BCBS para 4.4 formula; 125.6% avg risk weight |
| Population Drift (PSI/CSI) | `src/creditrisk/validation/stability.py` | Ongoing Model Monitoring | Score PSI (0.007) & Attribute CSI (<0.042) |

---

## 27. What a Real Bank Would Add

1. **Longitudinal Monthly Panel Tracking**: Monthly loan snapshot state history to build true empirical DPD roll-rate matrices.
2. **Economic Downturn LGD Calibration**: Stressing LGD against macro recession data rather than applying a fixed +8pp add-on.
3. **Account-Level Point-in-Time Origination Scorecard Records**: Storing exact origination scores per borrower to refine quantitative SICR ratios.
4. **Behavioral Scorecards**: Integrating real-time monthly payment history and deposit account data for active line management.

---

## 28. Implemented vs Demonstration vs Conceptual Matrix

| Capability | Status | File / Code Evidence | Notes |
|---|---|---|---|
| 12-Month Target Engineering | **IMPLEMENTED** | `src/creditrisk/data/target.py` | Runs on full 466,285 loan dataset |
| WoE & IV Feature Binning | **IMPLEMENTED** | `src/creditrisk/features/binning.py` | Fits on 184,525 train rows |
| PD Scorecard Models A & B | **IMPLEMENTED** | `src/creditrisk/models/pd_model.py` | 600-point scale; 0.3845 OOT Gini |
| Two-Stage Hurdle LGD Model | **IMPLEMENTED** | `src/creditrisk/models/lgd_model.py` | Fit on 50,968 defaulted exposures |
| Realized EAD Calculation | **IMPLEMENTED** | `src/creditrisk/models/ead_model.py` | Outstanding principal at default |
| Revolving CCF Model | **DEMONSTRATION** | `src/creditrisk/models/ccf_demo.py` | OLS model on synthetic 5k revolving portfolio |
| IFRS 9 Staging & ECL | **IMPLEMENTED** | `src/creditrisk/regulatory/ecl.py` | Full portfolio staged ECL ($278.48M) |
| Basel III IRB Capital Engine | **IMPLEMENTED** | `src/creditrisk/regulatory/basel_capital.py` | BCBS para 4.4 supervisory formula |
| Multi-Scenario ECL | **DEMONSTRATION** | `src/creditrisk/regulatory/run_macro_scenarios.py` | Executed on 3-loan test fixture |
| Delinquency Roll Rates | **DEMONSTRATION** | `src/creditrisk/monitoring/roll_rates.py` | Cross-sectional snapshot proxy |
| Outcome Transition Matrix | **DEMONSTRATION** | `src/creditrisk/monitoring/transitions.py` | Origination grade to outcome matrix |
| RAG Vector Analyst CLI | **IMPLEMENTED** | `src/creditrisk/ai/analyst.py` | Sentence-transformers + Gemini API |

---

## 29. Limitations and Non-Claims

1. **Dataset Nature**: Sourced from US LendingClub consumer loans (2007–2014); snapshot structure rather than monthly panel tracking.
2. **OOT Vintage Truncation**: 2014 OOT sample observed through early 2016 (67.29% current active loans).
3. **No Claim of Real-Time Bank Infrastructure**: Operating offline in Python without live core banking database triggers.
4. **No Claim of Full GenAI Core**: ML models use classical econometrics; Generative AI is limited to the RAG Credit Analyst.

---

## 30. Interview / Walkthrough Talking Points

1. **IRB Capital Penalty**: "Under Basel III IRB, because unsecured consumer loans exhibit a severe mean LGD of 93.01%, the supervisory formula calculates an average risk weight of 125.63%, imposing a 67.5% capital penalty over the flat 75% Standardised approach."
2. **LGD Two-Stage Hurdle Model**: "Because 52.18% of defaulted loans resulted in 100% loss with zero recoveries, standard linear regression fails. We implemented a two-stage hurdle model separating recovery incidence classification from conditional recovery magnitude."
3. **OOT Scorecard Generalization**: "Model B achieves an Out-Of-Time Gini of 0.3845 on 2014 vintage data, outperforming its training Gini of 0.3678, demonstrating that fine-classing WoE binning effectively preserves monotonicity across economic cycles."

---

## 31. Exact Commands Verified

```powershell
# 1. Verification of Test Suite (All 63 tests pass cleanly)
.\.venv\Scripts\python.exe -m pytest

# 2. Verification of Master Reporting Application Build
.\.venv\Scripts\python.exe src/creditrisk/reporting/build_panels.py
```

---

## 32. Evidence Index

| System Capability | Primary Code Evidence | Output Table / Artifact Evidence | Verified Result |
|---|---|---|---|
| Target Engineering | [`src/creditrisk/data/target.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/data/target.py#L65) | `outputs/tables/target_reconciliation.csv` | 16,018 12m defaults (3.44%) |
| Temporal Partitioning | [`src/creditrisk/data/sampling.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/data/sampling.py#L37) | `outputs/tables/sample_summary.csv` | Train: 184,525; Test: 46,132; OOT: 235,628 |
| WoE & IV Binning | [`src/creditrisk/features/binning.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/features/binning.py#L35) | `outputs/tables/iv_summary.csv` | `sub_grade` top IV = 0.4482 |
| PD Logit Model B | [`src/creditrisk/models/pd_model.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/pd_model.py#L15) | `outputs/tables/validation_summary.csv` | OOT AUC = 0.6923, Gini = 0.3845 |
| Scorecard Scaling | [`src/creditrisk/models/scorecard.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/scorecard.py#L20) | `outputs/tables/scorecard_model_b.csv` | Base 600 @ 50:1 odds, PDO = 20 |
| Hurdle LGD Engine | [`src/creditrisk/models/lgd_model.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/lgd_model.py#L38) | `outputs/tables/lgd_distribution_summary.csv` | Mean LGD = 93.01%, Median = 100.0% |
| IFRS 9 Staged ECL | [`src/creditrisk/regulatory/ecl.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/ecl.py#L25) | `outputs/tables/ecl_summary.csv` | Total Staged ECL = $278,476,558.68 |
| Basel III Capital | [`src/creditrisk/regulatory/basel_capital.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/basel_capital.py#L25) | `outputs/tables/basel_capital_summary.csv` | IRB RWA = $2.295B (125.63% Risk Weight) |
| Score Stability | [`src/creditrisk/validation/stability.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/validation/stability.py#L15) | `outputs/tables/psi_summary.csv` | Model B Score PSI = 0.007087 |
| RAG Vector Analyst | [`src/creditrisk/ai/analyst.py`](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/ai/analyst.py#L15) | `outputs/models/rag_index/embeddings.npy` | MiniLM embeddings + Gemini API |
