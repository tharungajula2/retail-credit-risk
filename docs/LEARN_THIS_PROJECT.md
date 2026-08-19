# LEARN THIS PROJECT: Comprehensive Retail Credit Risk Onboarding Manual

Welcome to `retail-credit-risk`. This repository is a production-grade, end-to-end regulatory credit risk engineering system built in Python. It evaluates **466,285 consumer unsecured term loans** originated by LendingClub between 2007 and 2014.

This document is your single, self-contained guide to mastering the whole codebase from zero. By reading this manual, you will be fully prepared to:
1. **Defend every modelling decision and metric** in a senior credit risk engineering interview.
2. **Execute, debug, and modify the pipeline by hand** without relying on an AI assistant.

---

## 1. What This Is (In 5 Sentences)

1. This system addresses the core retail banking problem of evaluating credit risk and estimating financial loss reserves on consumer unsecured term loans using a historical LendingClub dataset of **466,285 exposures** originated between 2007 and 2014.
2. It models the three fundamental credit risk parameters: **Probability of Default (PD)** (the likelihood a borrower defaults within 12 months), **Loss Given Default (LGD)** (the percentage of exposure lost if default occurs), and **Exposure At Default (EAD)** (the outstanding dollar balance at default).
3. Under international accounting standards (**IFRS 9 / Ind AS 109**), a bank uses these outputs to stage loans into Stage 1 (12-month expected loss for performing loans), Stage 2 (lifetime expected loss for loans with a Significant Increase in Credit Risk), and Stage 3 (credit-impaired default loss), while comparing results against US **CECL** (Day-1 lifetime loss).
4. Under international banking capital standards (**Basel III**), a bank uses PD, LGD, and EAD within the **Advanced Internal Ratings-Based (IRB)** formula to calculate **Risk-Weighted Assets (RWA)** and set aside regulatory capital reserves (Minimum CET1 4.5%, Tier 1 6.0%, Total Capital 8.0%).
5. In daily banking operations, credit risk engineers and portfolio managers use these model outputs for automated underwriting decisions, setting risk-adjusted loan pricing, monitoring portfolio credit deterioration, and producing financial reporting statements for regulatory auditors.

---

## 2. The Repository Map

### Directory Structure
```
retail-credit-risk/
├── config/                      # YAML configuration files for models, targets, & staging
│   ├── ai.yaml
│   ├── ifrs9.yaml
│   ├── macro_scenarios.yaml
│   ├── pd_model.yaml
│   ├── sampling.yaml
│   ├── target_definition.yaml
│   └── variables.yaml
├── datasets/                    # Local raw data storage (Git-ignored)
│   └── loan_data_2007_2014.csv  # 466,285 raw loan records (114 MB)
├── data/processed/              # Cleaned & partitioned Parquet datasets
│   ├── train.parquet            # 184,525 rows (2007-2013, 80% train split)
│   ├── test.parquet             # 46,132 rows (2007-2013, 20% test split)
│   └── oot.parquet              # 235,628 rows (2014 out-of-time split)
├── docs/                        # Project documentation & management presentations
│   ├── LEARN_THIS_PROJECT.md    # THIS onboarding & technical manual
│   ├── MODEL_DOCUMENTATION.md   # Model development document
│   └── MANAGEMENT_DECK.md       # Executive summary deck
├── outputs/                     # Generated model artifacts, tables, & figures
│   ├── figures/                 # ROC, KS, LGD, and lifetime PD PNG plots
│   ├── models/                  # Pickled binners (.pkl), models, & RAG vector index
│   ├── reports/                 # Interactive HTML risk dashboard & data inventory
│   └── tables/                  # 35 CSV tables containing all quantitative results
├── src/creditrisk/              # Primary Python package source code
│   ├── ai/                      # Vector RAG indexer & LLM credit analyst interface
│   ├── data/                    # Raw inspection, date parsing, target engineering, & sampling
│   ├── features/                # Monotonic Weight of Evidence (WoE) binning engine
│   ├── models/                  # Logit PD, 600-pt scorecard, two-stage LGD, EAD, CCF, & calibration
│   ├── monitoring/              # Vintage MOB default curves, roll-rate proxy, & transition matrix
│   ├── regulatory/              # Lifetime hazard PD, IFRS 9 staging, ECL, CECL, & Basel capital
│   ├── reporting/               # Dashboard data builder & HTML dashboard renderer
│   └── validation/              # Discrimination (AUC/Gini/KS), calibration (HL), & stability (PSI/CSI)
├── tests/                       # Unit testing suite (pytest)
├── pyproject.toml               # Package build configuration & dependencies
├── requirements.txt             # Virtual environment dependencies
└── PROJECT_TRUTH_retail-credit-risk.md # Ground truth reference file
```

### Subpackage Concept Map (`src/creditrisk/`)

- [src/creditrisk/data](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/data) — **Data Engineering**: Cleans raw data, applies century-fix date parsing, constructs 12-month PD target labels, and executes stratified temporal sampling.
- [src/creditrisk/features](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/features) — **Feature Engineering**: Implements monotonic Weight of Evidence (WoE) binning and Information Value (IV) attribute selection.
- [src/creditrisk/models](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models) — **Core Model Building**: Fits statsmodels Logistic PD regression, scales scorecards to 600 points, trains two-stage LGD hurdle models, calculates EAD, and simulates CCF.
- [src/creditrisk/validation](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/validation) — **Model Diagnostics**: Evaluates discriminatory power (AUROC, Gini, KS), calibration (Brier score, Hosmer-Lemeshow test), and stability (PSI, CSI).
- [src/creditrisk/regulatory](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory) — **Regulatory Compliance**: Builds 60-month lifetime PD hazard curves, assigns IFRS 9 stages, computes multi-scenario ECL vs US CECL, and calculates Basel III IRB RWA.
- [src/creditrisk/monitoring](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/monitoring) — **Portfolio Surveillance**: Tracks vintage Months-On-Book (MOB) default curves, cross-sectional delinquency roll-rate proxies, and credit rating transition matrices.
- [src/creditrisk/reporting](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/reporting) — **Business Intelligence**: Compiles metrics into JSON structure and renders a single self-contained interactive HTML executive risk dashboard.
- [src/creditrisk/ai](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/ai) — **Generative AI Assistant**: Indexes documentation and tables into vector embeddings for offline Retrieval-Augmented Generation (RAG) querying via Gemini.

---

## 3. The Stage-by-Stage Pipeline

The repository executes through 14 sequential Python script stages. Every stage reads inputs from previous steps and writes immutable output artifacts to `data/processed/`, `outputs/tables/`, or `outputs/models/`.

### Sequential Execution Table

| Stage | Script File Path | Input Data / Config | Key Logic Module | Primary Output Artifact | Core Concept Taught |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1** | [src/creditrisk/data/run_target_generation.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/data/run_target_generation.py) | `datasets/loan_data_2007_2014.csv`, `config/target_definition.yaml` | [target.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/data/target.py) | `outputs/tables/target_reconciliation.csv` | 12-month PD target label definition & century-fix date parsing |
| **2** | [src/creditrisk/data/run_sampling.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/data/run_sampling.py) | Cleaned DataFrame, `config/sampling.yaml` | [sampling.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/data/sampling.py) | `data/processed/train.parquet`, `test.parquet`, `oot.parquet` | Stratified temporal sample partitioning (2007-13 Dev vs 2014 OOT) |
| **3** | [src/creditrisk/features/run_binning.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/features/run_binning.py) | `train.parquet`, `config/variables.yaml` | [binning.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/features/binning.py) | `outputs/models/woe_binner.pkl`, `outputs/tables/iv_summary.csv` | Monotonic Weight of Evidence (WoE) transformation & IV screening |
| **4** | [src/creditrisk/models/run_pd_model.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/run_pd_model.py) | `train.parquet`, `woe_binner.pkl`, `config/pd_model.yaml` | [pd_model.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/pd_model.py) | `outputs/models/pd_model_a.pkl`, `pd_model_b.pkl` | Statsmodels Logistic Regression PD estimation (Models A & B) |
| **5** | [src/creditrisk/models/run_scorecard.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/run_scorecard.py) | `pd_model_a.pkl`, `pd_model_b.pkl`, `woe_binner.pkl` | [scorecard.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/scorecard.py) | `outputs/tables/scorecard_model_a.csv`, `scorecard_model_b.csv` | Standardized scorecard scaling (600 base score, PDO=20 at 50:1 odds) |
| **6** | [src/creditrisk/validation/run_validation.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/validation/run_validation.py) | `train.parquet`, `test.parquet`, `oot.parquet`, models | [metrics.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/validation/metrics.py) | `outputs/tables/validation_summary.csv` | Discriminatory power (AUC/Gini/KS) & Hosmer-Lemeshow calibration |
| **7** | [src/creditrisk/models/run_calibration.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/run_calibration.py) | `train.parquet`, `test.parquet`, `oot.parquet`, models | [calibration.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/calibration.py) | Intercept & Platt rows in `validation_summary.csv` | Probability recalibration via intercept shift & Platt scaling |
| **8** | [src/creditrisk/validation/run_stability.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/validation/run_stability.py) | `train.parquet`, `oot.parquet`, `woe_binner.pkl` | [stability.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/validation/stability.py) | `outputs/tables/psi_summary.csv`, `csi_by_variable.csv` | Population Stability Index (PSI) & Characteristic Stability (CSI) |
| **9** | [src/creditrisk/models/run_lgd_training.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/run_lgd_training.py) | `datasets/loan_data_2007_2014.csv` (`ever_default==1`) | [lgd_model.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/lgd_model.py) | `outputs/models/lgd_model.pkl`, `lgd_distribution_summary.csv` | Two-stage hurdle LGD modeling for zero-inflated recovery distributions |
| **10** | [src/creditrisk/regulatory/run_lifetime_pd.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/run_lifetime_pd.py) | `datasets/loan_data_2007_2014.csv` | [lifetime_pd.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/lifetime_pd.py) | `outputs/tables/lifetime_pd_term_structure.csv` | Discrete-time monthly hazard curve & cumulative lifetime PD |
| **11** | [src/creditrisk/regulatory/run_staging.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/run_staging.py) | `oot.parquet`, `pd_model_b.pkl`, `config/ifrs9.yaml` | [staging.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/staging.py) | `outputs/tables/staging_summary.csv` | IFRS 9 Stage 1 / Stage 2 / Stage 3 classification via SICR rules |
| **12** | [src/creditrisk/regulatory/run_ecl.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/run_ecl.py) | `oot.parquet`, staging output, `lgd_model.pkl` | [ecl.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/ecl.py) | `outputs/tables/ecl_summary.csv`, `ifrs9_vs_cecl.csv` | Multi-scenario staged IFRS 9 ECL vs Day-1 Lifetime US CECL |
| **13** | [src/creditrisk/regulatory/run_basel_capital.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/run_basel_capital.py) | `oot.parquet`, PD predictions, `lgd_model.pkl` | [basel_capital.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/basel_capital.py) | `outputs/tables/basel_capital_summary.csv` | Basel III Advanced IRB Risk-Weighted Assets & downturn LGD stress |
| **14** | [src/creditrisk/monitoring/run_monitoring.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/monitoring/run_monitoring.py) | `datasets/loan_data_2007_2014.csv` | [vintage.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/monitoring/vintage.py), [transitions.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/monitoring/transitions.py) | `outputs/tables/vintage_curves.csv`, `transition_matrix.csv` | Months-On-Book vintage curves & origination rating transition matrix |

### End-to-End Data Flow Diagram
```
                     [Raw Dataset: loan_data_2007_2014.csv (466,285 rows)]
                                       │
                                       ▼
                     [Stage 1: Target Engineering (target.py)]
                     ├── Parses dates (century fix: '68' -> 1968)
                     └── Creates default_12m target (3.44% default rate)
                                       │
                                       ▼
                     [Stage 2: Sampling & Partitioning (sampling.py)]
                     ├── Dev Cohort (2007-13: 230,657) ──► Train (184,525) / Test (46,132)
                     └── Out-Of-Time Cohort (2014)       ──► OOT (235,628)
                                       │
                                       ▼
                     [Stage 3: Feature Binning & WoE (binning.py)]
                     ├── Quantile binning + Monotonic WoE merge (>= 5% size)
                     └── Calculates Information Value (IV) across 48 features
                                       │
                                       ▼
                     [Stage 4: PD Model Training (pd_model.py)]
                     ├── Fits Statsmodels Logit (Model A: 7 feat, Model B: 10 feat)
                     └── Outputs p-values, z-scores, and model pickles (.pkl)
                                       │
                                       ▼
                     [Stage 5: Scorecard Scaling (scorecard.py)]
                     ├── Base Score = 600 @ 50:1 odds, PDO = 20
                     └── Translates WoE features into integer score points
                                       │
                                       ▼
              ┌────────────────────────┴────────────────────────┐
              ▼                                                 ▼
[Stages 6-8: Diagnostics & Stability]            [Stage 9: LGD Hurdle Model (lgd_model.py)]
├── Validates AUC / Gini / KS / HL              ├── Stage 1 Logit: P(Recovery > 0)
├── Applies Intercept & Platt Calibration       ├── Stage 2 GBDT: Recovery Rate | Recovery
└── Computes PSI (<0.01) & CSI (<0.05)           └── Outputs Mean LGD (93.01%) on 50,968 defaults
              │                                                 │
              └────────────────────────┬────────────────────────┘
                                       │
                                       ▼
                     [Stage 10: Lifetime PD Curve (lifetime_pd.py)]
                     └── Builds 60-month discrete-time cumulative hazard PD curve
                                       │
                                       ▼
                     [Stage 11: IFRS 9 Staging (staging.py)]
                     ├── Stage 1: Performing (189,633 loans / 80.48%)
                     ├── Stage 2: SICR (PD Ratio >= 2.0 or PD > 6% / 26,554 loans / 11.27%)
                     └── Stage 3: Default / DPD >= 90 (19,441 loans / 8.25%)
                                       │
                                       ▼
              ┌────────────────────────┴────────────────────────┐
              ▼                                                 ▼
[Stage 12: Staged ECL & CECL (ecl.py)]           [Stage 13: Basel III Capital (basel_capital.py)]
├── Staged IFRS 9 ECL: $278.48M (15.25% cov)    ├── IRB RWA: $2.295B (125.63% Risk Weight)
└── Day-1 CECL ECL:    $327.47M (17.93% cov)    └── Minimum Total Capital (8%): $183.57M
              │                                                 │
              └────────────────────────┬────────────────────────┘
                                       │
                                       ▼
                     [Stage 14: Dashboard & RAG Analyst]
                     ├── Renders interactive HTML report (risk_dashboard.html)
                     └── Indexes embeddings for offline LLM RAG agent
```

---

## 4. Main Modules Deep-Dive

Here is a deep-dive into the 15 core modules driving the system.

### 1. Target Engineering (`target.py`)
- **What it does**: Parses LendingClub raw date strings with century-rollover fixes and derives binary 12-month default target flags (`default_12m`) for PD model training.
- **Key Functions**:
  - `parse_lc_date(series)` ([target.py:L37-L62](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/data/target.py#L37-L62)): Converts string dates (e.g. `'Dec-68'`) to datetime and subtracts 100 years if year > 2049 (fixing pandas 2068 century bug).
  - `build_target(df, config)` ([target.py:L65-L126](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/data/target.py#L65-L126)): Infers default date (`last_pymnt_d` + 3 months DPD lag) and flags defaults occurring within 12 months of origination.
- **The ONE Decision That Matters**: Setting the default definition to include `Charged Off`, `Default`, `Late (31-120 days)`, and `Does not meet credit policy` ([target_definition.yaml:L15-L22](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/config/target_definition.yaml#L15-L22)), ensuring early-stage bad loans are captured without inflating false positives.

### 2. Sampling & Partitioning (`sampling.py`)
- **What it does**: Partitions the 466,285 loan dataset into temporal development and out-of-time validation sets.
- **Key Functions**:
  - `create_sampling_partitions(df, config)` ([sampling.py:L37-L140](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/data/sampling.py#L37-L140)): Splits vintages 2007–2013 into Development (230,657 rows) and vintage 2014 into Out-Of-Time (235,628 rows). Performs an 80/20 stratified train/test split on Development data.
- **The ONE Decision That Matters**: Using a strict out-of-time (OOT) temporal split on the 2014 vintage rather than simple random sampling across all years, simulating true forward deployment performance.

### 3. Feature Binning & WoE Engine (`binning.py`)
- **What it does**: Transforms continuous and categorical raw attributes into Weight of Evidence (WoE) binned variables that exhibit monotonic relationships with default risk.
- **Key Functions**:
  - `WoEBinner.fit(df, y)` ([binning.py:L115-L210](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/features/binning.py#L115-L210)): Quantile-bins continuous variables, merging adjacent bins until every bin has $\ge 5\%$ of sample rows and WoE is strictly monotonic.
- **The ONE Decision That Matters**: Enforcing a strict 5% minimum bin size (`min_bin_pct = 0.05`) and monotonicity constraint ([binning.py:L23](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/features/binning.py#L23)), preventing scorecard overfitting on small sample noise.

### 4. PD Model Fitting (`pd_model.py`)
- **What it does**: Trains statsmodels Logistic Regression models on WoE-transformed features to estimate 12-month Probability of Default ($PD$).
- **Key Functions**:
  - `PDModel.fit(X, y)` ([pd_model.py:L40-L95](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/pd_model.py#L40-L95)): Fits statsmodels `Logit`, extracting explicit coefficient p-values and z-scores for statistical significance auditing.
- **The ONE Decision That Matters**: Selecting statsmodels over scikit-learn for PD estimation to obtain exact asymptotic p-values for regulatory model validation governance.

### 5. Scorecard Transformer (`scorecard.py`)
- **What it does**: Scales log-odds logistic regression coefficients into intuitive integer scorecard points.
- **Key Functions**:
  - `ScorecardTransformer.fit(pd_model, binner)` ([scorecard.py:L45-L120](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/scorecard.py#L45-L120)): Computes scaling parameters: $Factor = 20 / \ln(2) = 28.8539$ and $Offset = 600 - Factor \times \ln(50) = 487.123$. Translates WoE attribute values into bin points.
- **The ONE Decision That Matters**: Aligning scorecard scaling to 600 base points at 50:1 odds with Points to Double Odds ($PDO$) equal to 20, the standard retail banking scorecard benchmark.

### 6. Validation Diagnostics (`metrics.py`)
- **What it does**: Calculates discriminatory power and calibration statistical metrics across model partitions.
- **Key Functions**:
  - `compute_auc_gini_ks(y_true, y_pred)` ([metrics.py:L20-L85](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/validation/metrics.py#L20-L85)): Computes AUROC, $Gini = 2 \times AUC - 1$, and Kolmogorov-Smirnov ($KS = \max(TPR - FPR)$) statistics.
  - `hosmer_lemeshow_test(y_true, y_pred, n_bins=10)` ([metrics.py:L115-L165](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/validation/metrics.py#L115-L165)): Evaluates 10-decile chi-square goodness-of-fit.
- **The ONE Decision That Matters**: Evaluating KS and Gini on Out-Of-Time data to verify rank-ordering stability under changing macroeconomic conditions.

### 7. Probability Recalibration (`calibration.py`)
- **What it does**: Recalibrates predicted PDs to align mean predicted default rates with observed portfolio default rates.
- **Key Functions**:
  - `InterceptRecalibrator.fit(y_true, y_pred)` ([calibration.py:L25-L65](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/calibration.py#L25-L65)): Adjusts the logit intercept $\alpha_{new} = \alpha + \ln(\frac{\bar{y}}{1-\bar{y}}) - \ln(\frac{\bar{p}}{1-\bar{p}})$.
  - `PlattScaler.fit(y_true, y_pred)` ([calibration.py:L70-L120](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/calibration.py#L70-L120)): Fits a logistic regression on predicted log-odds.
- **The ONE Decision That Matters**: Preserving original model rank-ordering ($AUC/Gini$) intact while shifting the probability scale to match actual portfolio default rates.

### 8. Population & Characteristic Stability (`stability.py`)
- **What it does**: Measures population drift between baseline (Train) and actual (OOT) score distributions.
- **Key Functions**:
  - `compute_psi(baseline, actual, n_bins=10)` ([stability.py:L15-L100](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/validation/stability.py#L15-L100)): Calculates $PSI = \sum (Actual\% - Baseline\%) \times \ln(\frac{Actual\%}{Baseline\%})$.
  - `compute_csi(baseline_df, actual_df, binner)` ([stability.py:L101-L200](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/validation/stability.py#L101-L200)): Computes Characteristic Stability Index per variable.
- **The ONE Decision That Matters**: Using epsilon smoothing ($1 \times 10^{-4}$) for zero-count bins to prevent division-by-zero runtime exceptions in automated PSI pipelines.

### 9. Two-Stage Hurdle LGD Model (`lgd_model.py`)
- **What it does**: Models Loss Given Default ($LGD$) on defaulted loans using a two-stage hurdle architecture to handle zero-inflated recovery distributions.
- **Key Functions**:
  - `TwoStageLGDModel.fit(X, y_lgd)` ([lgd_model.py:L38-L134](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/lgd_model.py#L38-L134)): Stage 1 trains a Logistic Classifier for $P(Recovery > 0)$. Stage 2 trains a Gradient Boosting Regressor for recovery rate given non-zero recovery. Combined expected $LGD = 1 - [P(Recovery > 0) \times \hat{RR}_{pos}]$.
- **The ONE Decision That Matters**: Using a two-stage hurdle model instead of single linear regression to capture the **52.18% point-mass concentration at 100% loss** ($0\%$ recovery).

### 10. EAD Calculation (`ead_model.py`)
- **What it does**: Calculates Exposure At Default ($EAD$) for fixed-term consumer loans.
- **Key Functions**:
  - `calculate_ead(df)` ([ead_model.py:L25-L94](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/ead_model.py#L25-L94)): Derives outstanding principal at default: $EAD = \max(funded\_amnt - total\_rec\_prncp, 0)$.
- **The ONE Decision That Matters**: Recognizing that fixed-term amortizing consumer loans carry zero undrawn credit commitments, making $EAD$ equal to outstanding principal balance.

### 11. Credit Conversion Factor Simulation (`ccf_demo.py`)
- **What it does**: Demonstrates Credit Conversion Factor ($CCF$) estimation for revolving credit lines via synthetic portfolio simulation.
- **Key Functions**:
  - `run_ccf_demo()` ([ccf_demo.py:L120-L163](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/ccf_demo.py#L120-L163)): Fits OLS regression on simulated revolving data: $CCF = \frac{EAD - Drawn}{Limit - Drawn}$.
- **The ONE Decision That Matters**: Explicitly labeling the output table as `SYNTHETIC_ccf_summary.csv` to ensure regulatory transparency that LendingClub term loans lack undrawn line data.

### 12. Lifetime PD Term Structure (`lifetime_pd.py`)
- **What it does**: Builds discrete-time monthly hazard curves and projects cumulative 60-month lifetime PD curves.
- **Key Functions**:
  - `LifetimePDTermStructure.fit(df)` ([lifetime_pd.py:L30-L126](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/lifetime_pd.py#L30-L126)): Computes monthly hazard rates $h(t) = \frac{Defaults(t)}{Active(t-1)}$ and cumulative survival $S(t) = \prod_{k=1}^t (1 - h(k))$. Scales individual account 12m PD to lifetime curves via multiplicative ratio $\frac{PD_{12m, i}}{PD_{12m, portfolio}}$.
- **The ONE Decision That Matters**: Using a discrete-time empirical hazard curve across loan tenure months $1 \dots 60$ rather than assuming a constant annual default hazard.

### 13. IFRS 9 Staging & SICR Engine (`staging.py`)
- **What it does**: Classifies loan exposures into IFRS 9 Stage 1, Stage 2, or Stage 3 based on quantitative and qualitative criteria.
- **Key Functions**:
  - `IFRS9Stager.stage_portfolio(df)` ([staging.py:L48-L149](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/staging.py#L48-L149)): Assigns Stage 3 for default/90+ DPD; Stage 2 for Significant Increase in Credit Risk ($PD_{ratio} = \frac{PD_{current}}{PD_{origination}} \ge 2.0$, $PD_{current} > 0.06$, or $30+$ DPD backstop); Stage 1 for performing loans.
- **The ONE Decision That Matters**: Defining the quantitative SICR threshold as a 2.0x relative PD ratio increase or absolute 6.0% 12-month PD ceiling ([ifrs9.yaml:L10-L15](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/config/ifrs9.yaml#L10-L15)).

### 14. Staged ECL & US CECL Engine (`ecl.py`)
- **What it does**: Computes staged IFRS 9 Expected Credit Losses and compares provisions against US CECL Day-1 lifetime accounting.
- **Key Functions**:
  - `ECLEngine.calculate_ecl(df)` ([ecl.py:L25-L150](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/ecl.py#L25-L150)): Calculates Stage 1 $ECL = PD_{12m} \times LGD \times EAD$; Stage 2 $ECL = PD_{Lifetime} \times LGD \times EAD$; Stage 3 $ECL = 1.0 \times LGD \times EAD$. Computes US CECL lifetime loss across all performing loans.
- **The ONE Decision That Matters**: Quantifying the exact dollar provision delta ($+\$48.99M$) between US CECL lifetime accounting and IFRS 9 staged provisioning.

### 15. Basel III IRB Capital Engine (`basel_capital.py`)
- **What it does**: Evaluates Basel III Advanced IRB Risk-Weighted Assets ($RWA$), minimum capital ratios, and downturn LGD stress scenarios.
- **Key Functions**:
  - `BaselCapitalCalculator.calculate_capital(df)` ([basel_capital.py:L25-L210](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/basel_capital.py#L25-L210)): Implements the Basel III IRB capital formula:
    $$K = \left[ LGD \times N\left(\frac{G(PD)}{\sqrt{1-R}} + \sqrt{\frac{R}{1-R}} G(0.999)\right) - PD \times LGD \right] \times \frac{1 + (M-2.5)b}{1 - 1.5b}$$
    $$RWA = K \times 12.5 \times EAD$$
    Applies an $+8\%$ downturn LGD add-on for stress testing.
- **The ONE Decision That Matters**: Applying empirical high LGD (93.01%) within the Advanced IRB formula, demonstrating why IRB risk weights (125.63%) can exceed Standardised retail weights (75.0%).

---

## 5. Numbers I Must Know Cold

These numbers are pulled directly from `outputs/tables/*.csv` and `PROJECT_TRUTH_retail-credit-risk.md`. You must know them cold for interviews.

### Model Discrimination & Validation Metrics

| Metric / Partition | Model A (7 Features) | Model B (10 Features) | Benchmark / Quality Assessment | Source File:Line |
| :--- | :--- | :--- | :--- | :--- |
| **Train AUROC** | `0.650668` | `0.683906` | Good discrimination (> 0.65) | `outputs/tables/validation_summary.csv:L1,L4` |
| **Train Gini** | `0.301337` | `0.367812` | Model B shows strong rank-ordering | `outputs/tables/validation_summary.csv:L1,L4` |
| **Train KS Statistic** | `0.219272` | `0.273629` | Good separation (> 0.20) | `outputs/tables/validation_summary.csv:L1,L4` |
| **Train HL p-value** | `0.001148` | `0.000398` | Sensitive to large N (184k rows) | `outputs/tables/validation_summary.csv:L1,L4` |
| **Test AUROC** | `0.648450` | `0.681676` | Zero overfitting vs Train | `outputs/tables/validation_summary.csv:L2,L5` |
| **Test Gini** | `0.296899` | `0.363352` | Highly stable across split | `outputs/tables/validation_summary.csv:L2,L5` |
| **Test KS Statistic** | `0.223298` | `0.272753` | Clean separation preserved | `outputs/tables/validation_summary.csv:L2,L5` |
| **Test HL p-value** | `0.236338` | `0.494183` | **PASSES calibration** (p > 0.05) | `outputs/tables/validation_summary.csv:L2,L5` |
| **OOT AUROC (2014)** | `0.635725` | `0.692260` | Model B improves on OOT | `outputs/tables/validation_summary.csv:L3,L6` |
| **OOT Gini (2014)** | `0.271451` | `0.384520` | Strong forward generalization | `outputs/tables/validation_summary.csv:L3,L6` |
| **OOT KS Statistic** | `0.195517` | `0.284314` | Excellent separation on OOT | `outputs/tables/validation_summary.csv:L3,L6` |
| **OOT HL p-value** | `3.08e-07` | `0.001166` | Fails uncalibrated (recalibrated in Stage 7) | `outputs/tables/validation_summary.csv:L3,L6` |

### Stability Metrics (Train vs 2014 OOT)
- **Model A Score PSI**: `0.004643` (**GOOD**, far below 0.10 threshold indicating minimal score distribution shift) (`outputs/tables/psi_summary.csv:L1`).
- **Model B Score PSI**: `0.007087` (**GOOD**, highly stable score distribution) (`outputs/tables/psi_summary.csv:L2`).
- **Highest Variable CSI**: `dti` = `0.041646` (**GOOD**, slight shift in debt-to-income ratio) (`outputs/tables/csi_by_variable.csv:L1`).
- **Lowest Variable CSI**: `annual_inc` = `0.005676` (**GOOD**, stable income profile) (`outputs/tables/csi_by_variable.csv:L7`).

### Loss Given Default (LGD) Key Statistics
- **Defaulted Subpopulation Count**: **50,968 defaulted loans** (`outputs/tables/lgd_distribution_summary.csv:L1`).
- **Mean LGD**: `0.930055` (**93.01%**) — Very high loss rate typical for consumer unsecured debt (`outputs/tables/lgd_distribution_summary.csv:L1`).
- **Median LGD**: `1.000000` (**100% loss**) (`outputs/tables/lgd_distribution_summary.csv:L1`).
- **Mean Recovery Rate**: `0.069945` (**6.99%**) (`outputs/tables/lgd_distribution_summary.csv:L1`).
- **100% Loss Point-Mass (`LGD == 1.0`)**: **52.1778%** of defaulted loans have zero post-default recoveries (`outputs/tables/lgd_distribution_summary.csv:L1`).
- **0% Loss Point-Mass (`LGD == 0.0`)**: **0.3473%** of defaulted loans fully recover (`outputs/tables/lgd_distribution_summary.csv:L1`).
- **Stage 1 Recovery Classifier AUC**: `0.6416` (evaluated during execution in [run_lgd_training.py:L64](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/run_lgd_training.py#L64)).

### IFRS 9 Staging & ECL Breakdown (2014 Out-Of-Time Portfolio: 235,628 Loans, $1.827B EAD)

| Stage | Loan Count | % of Portfolio | Total EAD ($) | Mean 12m PD | Total Staged ECL ($) | Coverage Ratio (%) | Source File:Line |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Stage 1 (Performing)** | `189,633` | `80.48%` | `$1,417,203,102.50` | `2.73%` | `$30,272,767.11` | `2.14%` | `outputs/tables/staging_summary.csv:L1`, `ecl_summary.csv:L1` |
| **Stage 2 (SICR)** | `26,554` | `11.27%` | `$169,366,224.20` | `7.64%` | `$24,404,482.89` | `14.41%` | `outputs/tables/staging_summary.csv:L2`, `ecl_summary.csv:L2` |
| **Stage 3 (Default)** | `19,441` | `8.25%` | `$240,003,112.50` | `100.00%` | `$223,799,308.68` | `93.25%` | `outputs/tables/staging_summary.csv:L3`, `ecl_summary.csv:L3` |
| **Total Portfolio** | `235,628` | `100.00%` | `$1,826,572,439.20` | `5.64%` | **`$278,476,558.68`** | **`15.25%`** | `outputs/tables/ecl_summary.csv:L4` |

### Accounting Framework Comparison (IFRS 9 vs US CECL)
- **IFRS 9 Staged ECL Total**: **$278,476,558.68** (Coverage: `15.25%`) (`outputs/tables/ifrs9_vs_cecl.csv:L1`).
- **US CECL Day-1 Lifetime ECL Total**: **$327,465,214.28** (Coverage: `17.93%`) (`outputs/tables/ifrs9_vs_cecl.csv:L3`).
- **CECL vs IFRS 9 Provision Delta**: **+$48,988,631.78** (CECL requires `$48.99M` higher provisions because Stage 1 loans must hold lifetime reserves under CECL) (`outputs/tables/ifrs9_vs_cecl.csv:L4`).

### Basel III Regulatory Capital & Downturn Stress Analytics
- **Basel III Advanced IRB Total RWA**: **$2,294,667,104.99** (`$2.295B`) (`outputs/tables/basel_capital_summary.csv:L1`).
- **Basel III Standardised Total RWA**: **$1,369,929,329.40** (`$1.370B`) (`outputs/tables/basel_capital_summary.csv:L1`).
- **Basel III IRB Portfolio Risk Weight**: **`125.63%`** (Higher than Standardised 75% due to 93.01% empirical LGD) (`outputs/tables/basel_capital_summary.csv:L1`).
- **Basel III Minimum CET1 Capital (4.5%)**: **$103,260,019.72** (`$103.26M`) (`outputs/tables/basel_capital_summary.csv:L1`).
- **Basel III Minimum Tier 1 Capital (6.0%)**: **$137,680,026.30** (`$137.68M`) (`outputs/tables/basel_capital_summary.csv:L1`).
- **Basel III Minimum Total Capital (8.0%)**: **$183,573,368.40** (`$183.57M`) (`outputs/tables/basel_capital_summary.csv:L1`).
- **Downturn LGD (+8pp add-on) Total RWA**: **$2,453,921,334.39** (`$2.454B`, Risk Weight: `134.35%`) (`outputs/tables/basel_downturn_comparison.csv:L2`).
- **Downturn Minimum Total Capital Increase**: **+$12,740,338.35** (`+$12.74M`) (`outputs/tables/basel_downturn_comparison.csv:L3`).

---

## 6. Why Each Modelling Choice Was Made

Every design decision in this repo balances regulatory compliance, statistical rigor, and business interpretability.

1. **Weight of Evidence (WoE) Binning**: Implemented in [binning.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/features/binning.py) to transform continuous numerical features into monotonic discrete bins. This captures non-linear risk relationships, handles missing values naturally without imputation bias, and isolates outliers. *Honest Limitation*: Coarse quantile binning discards fine-grained feature variance within individual bin intervals.
2. **Logistic Regression for PD**: Implemented in [pd_model.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/pd_model.py) because logistic regression produces well-calibrated probabilities bounded in $[0, 1]$, guarantees monotonic risk scoring, and allows direct extraction of coefficient p-values required by regulatory auditors. *Honest Limitation*: Linear log-odds assumptions cannot automatically detect high-order non-linear feature interactions without manual cross-product terms.
3. **Scorecard Scaling (600 Points, PDO=20 at 50:1 Odds)**: Implemented in [scorecard.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/scorecard.py) to map log-odds into integer credit scores. An intuitive point scale allows non-technical underwriters and risk officers to understand credit decisions. *Honest Limitation*: Standard linear scorecard point allocation assumes log-odds scale linearly across all score ranges.
4. **Two-Stage Hurdle LGD Model**: Implemented in [lgd_model.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/lgd_model.py) to tackle the **52.18% point-mass at 100% loss** ($0\%$ recovery). Stage 1 models recovery occurrence $P(RR > 0)$, while Stage 2 estimates non-zero recovery magnitude via Gradient Boosting. *Honest Limitation*: Combining two distinct model predictions introduces compound estimation variance in expected recovery outputs.
5. **Discrete-Time Hazard Lifetime PD**: Implemented in [lifetime_pd.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/lifetime_pd.py) to build empirical monthly hazard curves $h(t)$ across loan tenures $1 \dots 60$, reflecting non-constant default timing over loan life. *Honest Limitation*: The portfolio-level hazard curve is scaled unconditionality across accounts without incorporating forward-looking macro covariate paths per month.
6. **SICR Staging Rules ($PD_{ratio} \ge 2.0$, $PD_{current} > 0.06$, $30+$ DPD)**: Implemented in [staging.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/staging.py) to comply with IFRS 9 requirements by triggering Stage 2 lifetime reserves whenever credit quality deteriorates significantly. *Honest Limitation*: Origination PD is approximated using credit grade averages due to the lack of historical origination scorecards.
7. **Basel III Advanced IRB Capital Framework**: Implemented in [basel_capital.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/basel_capital.py) to calculate risk-sensitive capital requirements based on empirical PD and LGD estimates rather than fixed 75% standard weights. *Honest Limitation*: Unsecured consumer loans with 93.01% mean LGD result in IRB risk weights (125.63%) that exceed the regulatory Standardised benchmark.

---

## 7. Honest Limitations (Things to Admit in an Interview)

In an interview, demonstrating self-awareness of repository limitations builds immense credibility. Admit these 5 points upfront:

1. **Cross-Sectional Snapshot Data vs Monthly Panel**: LendingClub data provides a single snapshot record per loan rather than longitudinal monthly panel observations. Delinquency roll-rate matrices ([roll_rates.py:L22](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/monitoring/roll_rates.py#L22)) and transition matrices ([transitions.py:L28](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/monitoring/transitions.py#L28)) are constructed as cross-sectional snapshot proxies by vintage year and origination grade.
2. **Synthetic Revolving CCF Simulation**: LendingClub exposures are fixed-term amortizing consumer loans with no undrawn commitments ($EAD = \text{outstanding principal}$). Revolving Credit Conversion Factor (CCF) modeling ([ccf_demo.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/ccf_demo.py)) is executed on a simulated 5,000-account revolving portfolio purely for methodology demonstration.
3. **Grade-Average Proxy for Origination PD**: Historical point-in-time scorecards from loan origination dates were not preserved in the dataset. Initial PD at origination is calculated as the average predicted PD per credit grade ([staging.py:L100-L105](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/staging.py#L100-L105)).
4. **OOT Gini Higher Than Train Gini (Model B)**: Model B Gini increases from `0.3678` (Train) to `0.3845` (2014 OOT) ([validation_summary.csv:L4,L6](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/outputs/tables/validation_summary.csv#L4-L6)). This occurs because the 2014 OOT vintage has a shorter observation window where defaults are concentrated among high-risk sub-grades, making early rank-ordering sharper.
5. **Hosmer-Lemeshow Test Sensitivity on Large Samples**: Uncalibrated models fail the Hosmer-Lemeshow calibration test on large sample sizes ($N=235,628$, $p = 3.08 \times 10^{-7}$) ([validation_summary.csv:L3](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/outputs/tables/validation_summary.csv#L3)) because chi-square statistics become hyper-sensitive to tiny absolute probability deviations when $N > 100,000$.

---

## 8. Run and Modify BY HAND (No AI Required)

Follow this manual runbook to set up, execute, and modify the project by hand.

### Environment Setup
```bash
# 1. Open PowerShell terminal in the repository root directory
cd "d:\0000_after portfolio_25726\2_retail-credit-risk\retail-credit-risk"

# 2. Activate virtual environment
.\.venv\Scripts\Activate.ps1

# 3. Install package in editable mode
pip install -e .
```

### Complete Pipeline Execution Sequence
Execute all 14 pipeline stages in order from terminal:
```bash
python src/creditrisk/data/run_target_generation.py
python src/creditrisk/data/run_sampling.py
python src/creditrisk/features/run_binning.py
python src/creditrisk/models/run_pd_model.py
python src/creditrisk/models/run_scorecard.py
python src/creditrisk/validation/run_validation.py
python src/creditrisk/models/run_calibration.py
python src/creditrisk/validation/run_stability.py
python src/creditrisk/models/run_lgd_training.py
python src/creditrisk/regulatory/run_lifetime_pd.py
python src/creditrisk/regulatory/run_staging.py
python src/creditrisk/regulatory/run_ecl.py
python src/creditrisk/regulatory/run_basel_capital.py
python src/creditrisk/monitoring/run_monitoring.py
python src/creditrisk/monitoring/run_transitions.py
python src/creditrisk/reporting/build_dashboard.py
```

### Configuration Controls (`config/`)
- `config/target_definition.yaml`: Controls default statuses, DPD lag months (3), and performance window (12m).
- `config/sampling.yaml`: Controls vintage years for Dev (2007–2013) vs OOT (2014), test split ratio (0.20), and random seed (42).
- `config/variables.yaml`: Lists target column, feature candidates, and categorical attributes.
- `config/pd_model.yaml`: Defines feature sets for Model A (7 features) and Model B (10 features).
- `config/ifrs9.yaml`: Controls SICR thresholds ($PD_{ratio} = 2.0$, $PD_{abs} = 0.06$, $DPD = 30$).
- `config/macro_scenarios.yaml`: Sets GDP growth and unemployment assumptions for Baseline, Upside, and Downside ECL scenarios.

---

### 5 Worked "Change This By Hand" Recipes

#### Recipe 1: Change Base Score from 600 to 650 or PDO from 20 to 30
- **Goal**: Re-scale the scorecard point system.
- **File to Edit**: [src/creditrisk/models/scorecard.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/scorecard.py#L25-L35)
- **Line Numbers**: `L25-L30`
- **Code Edit**:
  ```python
  # Change target_score from 600 to 650 and pdo from 20 to 30:
  BASE_SCORE = 650  # Was 600
  PDO = 30          # Was 20
  TARGET_ODDS = 50.0
  ```
- **Re-run Command**: `python src/creditrisk/models/run_scorecard.py`
- **Output Verified**: `outputs/tables/scorecard_model_b.csv` will contain updated integer score points.

#### Recipe 2: Change SICR PD-Ratio Threshold from 2.0x to 3.0x
- **Goal**: Make Stage 2 staging criteria stricter, moving fewer loans into Stage 2.
- **File to Edit**: [config/ifrs9.yaml](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/config/ifrs9.yaml#L10-L15) OR [src/creditrisk/regulatory/staging.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/staging.py#L54-L60)
- **Line Numbers**: `config/ifrs9.yaml:L12` or `staging.py:L56`
- **Code Edit**:
  ```yaml
  sicr_pd_ratio_threshold: 3.0  # Was 2.0
  ```
- **Re-run Commands**:
  ```bash
  python src/creditrisk/regulatory/run_staging.py
  python src/creditrisk/regulatory/run_ecl.py
  ```
- **Output Verified**: `outputs/tables/staging_summary.csv` will show Stage 2 loan count drop below 26,554, and `ecl_summary.csv` will show lower Stage 2 ECL reserves.

#### Recipe 3: Add a Feature (`installment`) to Model B
- **Goal**: Expand Model B feature set from 10 to 11 predictors.
- **File to Edit**: [config/pd_model.yaml](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/config/pd_model.yaml#L18-L25)
- **Line Numbers**: `config/pd_model.yaml:L18-L25`
- **Code Edit**:
  ```yaml
  model_b_features:
    - sub_grade_woe
    - term_woe
    - home_ownership_woe
    - annual_inc_woe
    - verification_status_woe
    - purpose_woe
    - dti_woe
    - inq_last_6mths_woe
    - revol_util_woe
    - total_acc_woe
    - installment_woe  # NEW FEATURE ADDED HERE
  ```
- **Re-run Commands**:
  ```bash
  python src/creditrisk/models/run_pd_model.py
  python src/creditrisk/models/run_scorecard.py
  python src/creditrisk/validation/run_validation.py
  ```
- **Output Verified**: `outputs/tables/pd_model_b_coefs.csv` will list 11 feature coefficients, and `validation_summary.csv` will update Model B Gini and AUC metrics.

#### Recipe 4: Change Downturn LGD Stress Add-On from +8% to +15%
- **Goal**: Increase macroeconomic stress on Basel III Downturn Risk-Weighted Assets.
- **File to Edit**: [src/creditrisk/regulatory/basel_capital.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/basel_capital.py#L140-L160)
- **Line Numbers**: `L145-L150`
- **Code Edit**:
  ```python
  # Change downturn LGD add-on:
  downturn_lgd = np.clip(lgd + 0.15, 0.0, 1.0)  # Was + 0.08
  ```
- **Re-run Command**: `python src/creditrisk/regulatory/run_basel_capital.py`
- **Output Verified**: `outputs/tables/basel_downturn_comparison.csv` will show Downturn RWA increase from `$2.454B` to a higher value.

#### Recipe 5: Change Minimum WoE Bin Percentage from 5% to 10%
- **Goal**: Create coarser, broader feature bins to enforce stronger regularization.
- **File to Edit**: [src/creditrisk/features/binning.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/features/binning.py#L23-L25)
- **Line Numbers**: `L23`
- **Code Edit**:
  ```python
  MIN_BIN_PCT = 0.10  # Was 0.05 (10% minimum bin size)
  ```
- **Re-run Commands**:
  ```bash
  python src/creditrisk/features/run_binning.py
  python src/creditrisk/models/run_pd_model.py
  python src/creditrisk/validation/run_validation.py
  ```
- **Output Verified**: `outputs/tables/iv_summary.csv` will show updated IV values based on 10% coarse bins.

---

## 9. Governance Note: Real Bank Model Controls

In a regulated tier-1 commercial bank, AI coding agents are strictly prohibited from having write access to production model repositories. Repository changes are governed under supervisory guidance frameworks like **Federal Reserve SR 11-7 / OCC 2011-12** (Model Risk Management).

Here is how governance maps to this codebase:

1. **Version Control & Code Freeze**: Every production release requires an immutable git tag and commit hash tracking (e.g. Commit `05d205299dcb...` on `main`). All stochastic pipelines must enforce explicit random seeds (`random_state=42` in [sampling.yaml:L17](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/config/sampling.yaml#L17)) to guarantee 100% deterministic reproducibility.
2. **Four-Eyes Human Peer Review**: No code edit to `src/creditrisk/` can merge to `main` without explicit pull request sign-off from two senior credit risk engineers.
3. **Model Documentation (`MODEL_DOCUMENTATION.md`)**: Comprehensive documentation detailing conceptual soundness, dataset lineage, feature selection rationale, and validation diagnostics must accompany code changes.
4. **Independent Model Validation (Model Risk Management - MRM)**: An independent validation team (separate from model developers) tests the code for conceptual soundness, backtesting accuracy, out-of-time stability ($PSI < 0.10$), and calibration. The model cannot deploy without formal MRM sign-off.
5. **Change Control & Production Deployment**: Production environment changes are restricted to parameter adjustments via version-controlled YAML files in `config/`. Editing core logic algorithms in `src/` requires formal Change Management Board (CMB) approval.

---

## 10. Glossary

- **AUROC (Area Under Receiver Operating Characteristic)**: A metric bounded between 0.5 and 1.0 measuring a model's ability to rank-order default risk.
- **Basel III**: International regulatory framework establishing bank capital adequacy, stress testing, and market liquidity standards.
- **Brier Score**: Mean squared difference between predicted probability and actual binary default outcome (lower is better calibrated).
- **CCF (Credit Conversion Factor)**: The estimated percentage of an undrawn credit line that a borrower will draw down prior to defaulting.
- **CECL (Current Expected Credit Losses)**: US GAAP accounting standard requiring immediate Day-1 lifetime expected loss provisioning for all loans.
- **CET1 (Common Equity Tier 1)**: High-quality core capital (retained earnings and common stock) expressed as a percentage of Risk-Weighted Assets (minimum 4.5%).
- **CSI (Characteristic Stability Index)**: Metric measuring population drift within individual feature attribute bins over time.
- **DPD (Days Past Due)**: The number of elapsed calendar days a borrower has missed a scheduled credit payment.
- **EAD (Exposure At Default)**: The total gross dollar exposure expected at the time a loan defaults.
- **ECL (Expected Credit Loss)**: The probability-weighted loss estimate calculated as $ECL = PD \times LGD \times EAD$.
- **Gini Coefficient**: Linear transformation of AUROC ($Gini = 2 \times AUROC - 1$) measuring rank-ordering power on a scale from 0 to 1.
- **HL Test (Hosmer-Lemeshow Test)**: Chi-square test evaluating goodness-of-fit by comparing observed vs predicted defaults across 10 deciles.
- **IFRS 9 / Ind AS 109**: International accounting standard mandating 3-stage expected loss provisioning based on credit deterioration.
- **IRB (Internal Ratings-Based Approach)**: Basel capital framework allowing banks to use internal PD and LGD models to calculate capital requirements.
- **IV (Information Value)**: Metric quantifying the predictive power of a feature ($IV < 0.02$: useless, $0.1 - 0.3$: medium, $> 0.3$: strong).
- **KS Statistic (Kolmogorov-Smirnov)**: Maximum vertical distance between cumulative distribution functions of defaulted vs non-defaulted loans.
- **LGD (Loss Given Default)**: The percentage of outstanding balance unrecovered following default and asset recovery ($LGD = 1 - Recovery Rate$).
- **MOB (Months-On-Book)**: The number of elapsed calendar months since loan origination.
- **PD (Probability of Default)**: The estimated likelihood that a borrower defaults over a specified horizon (typically 12 months).
- **PDO (Points to Double Odds)**: Scorecard scaling parameter representing the increase in score points required to double the credit odds.
- **PSI (Population Stability Index)**: Metric measuring overall score distribution shift between baseline training and actual monitoring samples ($PSI < 0.10$: stable).
- **RAG (Retrieval-Augmented Generation)**: AI architecture combining vector semantic search over documentation with an LLM for factual Q&A.
- **RWA (Risk-Weighted Assets)**: Total bank assets weighted by credit risk factors, determining minimum required regulatory capital.
- **SICR (Significant Increase in Credit Risk)**: IFRS 9 quantitative/qualitative trigger transferring loans from Stage 1 (12m ECL) to Stage 2 (Lifetime ECL).
- **WoE (Weight of Evidence)**: Log-odds transformation of feature bins measuring relative proportion of non-defaults to defaults.

---

## 11. Discrepancies Between Code and `PROJECT_TRUTH`

For absolute auditing rigor, here is a complete reconciliation flagging every minor nuance where runtime code execution behavior differs from static documentation:

1. **Macro Scenario and Expected Loss Micro-Sample Execution**:
   - *Code Behavior*: In [run_expected_loss.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/run_expected_loss.py#L1-L80) and [run_macro_scenarios.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/run_macro_scenarios.py#L1-L75), expected loss summary and scenario weighting scripts execute on a 3-loan micro-sample DataFrame test fixture ($29,000 total EAD, $1,950 total EL, $9,384.73 scenario ECL) rather than processing all 235,628 OOT loans.
   - *Full Portfolio Staged ECL*: Full portfolio staging and ECL calculations are executed separately by [run_staging.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/run_staging.py) and [run_ecl.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/run_ecl.py), generating `outputs/tables/ecl_summary.csv` ($278.48M total ECL).
2. **LGD Stage 1 Classifier AUC Metric Output Location**:
   - *Code Behavior*: In [run_lgd_training.py:L64](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/run_lgd_training.py#L64), the Stage 1 recovery classifier AUC (`0.6416`) is printed to standard stdout during execution but is not saved to a CSV table. Only decile MAE calibration figures are exported in `outputs/tables/lgd_calibration.csv`.
3. **Absence of 2015 Out-of-Time Data**:
   - *Code Behavior*: Raw and processed datasets span origination years 2007 through 2014 ([sampling.yaml:L13-L14](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/config/sampling.yaml#L13-L14)). Zero loans from 2015 exist in the repository. Out-Of-Time validation is performed exclusively on vintage 2014.
