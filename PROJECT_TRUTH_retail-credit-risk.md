# PROJECT TRUTH: Retail Credit Risk Modeling System

## 1. Identification

- **Repository Name**: `retail-credit-risk`
- **Current Branch**: `main`
- **Latest Commit Hash**: `05d205299dcb64b27e7a5932ea60db8f6ec35961`
- **Latest Commit Date**: `Mon Jul 27 22:28:00 2026 +0530`
- **Remote URL**: `origin` pointing to `https://github.com/tharungajula2/retail-credit-risk.git`
- **Remote Visibility**: Configured git remote URL is `https://github.com/tharungajula2/retail-credit-risk.git` (API visibility flag not accessible from local workspace).
- **Total File Count by Extension** (excluding `.git`, `.venv`, `__pycache__`, `.pytest_cache`):
  - `.csv`: 84
  - `.py`: 82
  - `.png`: 36
  - No extension (`.gitkeep`, `.gitignore`): 21
  - `.yaml`: 7
  - `.md`: 6
  - `.txt`: 6
  - `.pdf`: 4
  - `.pkl`: 4
  - `.parquet`: 3
  - `.json`: 2
  - `.toml`: 1
  - `.xlsx`: 1
  - `.npy`: 1
  - `.html`: 1
  - **Total File Count**: 259 files
- **Virtual Environment & Lockfile**:
  - Virtual environment directory `.venv/` exists at repository root.
  - Dependency manifests `requirements.txt` and `pyproject.toml` exist at root.
  - No lockfile (`uv.lock`, `poetry.lock`, `Pipfile.lock`, `requirements.lock`) exists in the repository.

---

## 2. Data Provenance

### Loaded Datasets
- **Primary Raw Dataset**: `datasets/loan_data_2007_2014.csv`
  - Loaded via `pd.read_csv(RAW_DATA_PATH, low_memory=False)` in:
    - [inspect_raw.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/data/inspect_raw.py#L15)
    - [run_target_generation.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/data/run_target_generation.py#L13)
    - [run_sampling.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/data/run_sampling.py#L15)
    - [run_lgd_training.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/run_lgd_training.py#L20)
    - [run_lifetime_pd.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/run_lifetime_pd.py#L14)
    - [run_monitoring.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/monitoring/run_monitoring.py#L19)
    - [run_transitions.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/monitoring/run_transitions.py#L14)
- **Processed Parquet Partitions**:
  - `data/processed/train.parquet` loaded via `pd.read_parquet(...)` in [run_binning.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/features/run_binning.py#L14), [run_pd_model.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/run_pd_model.py#L14), [run_scorecard.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/run_scorecard.py#L15), [run_validation.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/validation/run_validation.py#L40), [run_stability.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/validation/run_stability.py#L18), [run_calibration.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/run_calibration.py#L34).
  - `data/processed/test.parquet` loaded via `pd.read_parquet(...)` in [run_validation.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/validation/run_validation.py#L41), [run_calibration.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/run_calibration.py#L35).
  - `data/processed/oot.parquet` loaded via `pd.read_parquet(...)` in [run_validation.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/validation/run_validation.py#L42), [run_stability.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/validation/run_stability.py#L19), [run_calibration.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/run_calibration.py#L36), [run_staging.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/run_staging.py#L15), [run_ecl.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/run_ecl.py#L23), [run_expected_loss.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/run_expected_loss.py#L19), [run_basel_capital.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/run_basel_capital.py#L21), [run_macro_scenarios.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/run_macro_scenarios.py#L22).

### Dataset Origin
- Public LendingClub open loan dataset covering origination vintages 2007 through 2014. Established in code docstrings in [inspect_raw.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/data/inspect_raw.py#L1-L15) and machine-generated report [data_inventory.txt](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/outputs/reports/data_inventory.txt#L5).

### Licence / Terms of Use
- `NO LICENCE OR TERMS-OF-USE FILE COMMITTED IN REPO`.

### Statement on Confidentiality
- Every dataset in this repository is public open data sourced from LendingClub (2007-2014) and no dataset in this repo is proprietary, confidential, or sourced from an employer.

### Row and Column Counts as Printed by Code
- **Raw Load**: 466,285 rows, 75 columns ([data_inventory.txt](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/outputs/reports/data_inventory.txt#L6-L7), [target_reconciliation.csv](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/outputs/tables/target_reconciliation.csv#L1)).
- **After Cleaning & Target Engineering**: 466,285 rows, 79 columns ([target.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/data/target.py#L25-L160), [target_reconciliation.csv](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/outputs/tables/target_reconciliation.csv#L1-L7)):
  - Total Loans: 466,285 (100.00%)
  - Non-Default: 415,317 (89.07%)
  - Ever Default: 50,968 (10.93%)
  - 12-month Default (`default_12m == 1`): 16,018 (3.44%)
  - Default after 12 months (`default_12m == 0`, `ever_default == 1`): 34,950 (7.50%)
- **Partitioned Modeling Samples** ([sampling.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/data/sampling.py#L37-L140), [sample_summary.csv](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/outputs/tables/sample_summary.csv#L1-L4)):
  - Development Sample (Vintages 2007–2013): 230,657 rows.
    - Train Partition (80% stratified): 184,525 rows; 6,329 defaults; 3.4299% default rate; issue dates Apr-08 to Sep-13.
    - Test Partition (20% stratified): 46,132 rows; 1,582 defaults; 3.4293% default rate; issue dates Apr-08 to Sep-13.
  - Out-Of-Time (OOT) Sample (Vintage 2014): 235,628 rows; 8,107 defaults; 3.4406% default rate; issue dates Apr-14 to Sep-14.
- **LGD Modeling Set** (`ever_default == 1`): 50,968 rows ([lgd_data.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/lgd_data.py#L25-L80), [run_lgd_training.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/run_lgd_training.py#L34-L58), [lgd_distribution_summary.csv](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/outputs/tables/lgd_distribution_summary.csv#L1-L2)). Split 80/20 into 40,774 train rows and 10,194 test rows.

---

## 3. What It Is

This repository contains a python-based retail credit risk modeling system designed for consumer unsecured term loans, evaluated on 466,285 historical loans issued between 2007 and 2014. The codebase implements an end-to-end regulatory credit risk pipeline encompassing Probability of Default (PD) scorecard development, Loss Given Default (LGD) estimation, Exposure At Default (EAD) tracking, IFRS 9 Expected Credit Loss (ECL) staging, US CECL lifetime provisioning, and Basel III Advanced IRB capital calculations. The PD framework uses Weight of Evidence binning and Logistic Regression across candidate credit attributes, scaled into a 600-point scorecard. LGD is modeled via a two-stage hurdle structure combining a logistic recovery classifier with a gradient boosting regressor on 50,968 defaulted loans. IFRS 9 staging classifies active exposures into Stage 1, Stage 2, and Stage 3 based on Significant Increase in Credit Risk quantitative thresholds and 30-day past-due backstops, applying a discrete-time 60-month cumulative hazard curve for lifetime PD projection. Capital analytics compute Basel III Risk-Weighted Assets and minimum capital ratios alongside a downturn LGD stress scenario. The system also includes an automated HTML risk dashboard renderer and an offline vector-indexed RAG assistant for querying project risk metrics.

---

## 4. The Pipeline as Built

```
[Raw Dataset: loan_data_2007_2014.csv (466,285 x 75)]
                           │
                           ▼
 1. Target Engineering (src/creditrisk/data/run_target_generation.py)
    ├── Derives default_12m, ever_default, months_to_default, est_default_date
    └── Outputs: target_reconciliation.csv, target_summary_by_vintage.csv
                           │
                           ▼
 2. Sampling & Partitioning (src/creditrisk/data/run_sampling.py)
    ├── Splits Dev (2007-2013: 230,657) vs OOT (2014: 235,628)
    ├── 80/20 Stratified Train/Test split on Dev
    └── Outputs: data/processed/train.parquet, test.parquet, oot.parquet
                           │
                           ▼
 3. Feature Binning & WoE (src/creditrisk/features/run_binning.py)
    ├── Fits WoEBinner on train.parquet across 48 features
    └── Outputs: woe_binner.pkl, iv_summary.csv, bin_tables/*.csv
                           │
                           ▼
 4. PD Model Training (src/creditrisk/models/run_pd_model.py)
    ├── Fits Statsmodels Logit: Model A (7 features) & Model B (10 features)
    └── Outputs: pd_model_a.pkl, pd_model_b.pkl, pd_model_a_coefs.csv, pd_model_b_coefs.csv
                           │
                           ▼
 5. Scorecard Scaling (src/creditrisk/models/run_scorecard.py)
    ├── Scales logit coefficients into score points (PDO=20, Base=600 @ 50:1)
    └── Outputs: scorecard_model_a.csv, scorecard_model_b.csv, rating_grades_model_b.csv
                           │
                           ▼
 6. Model Validation & Calibration (src/creditrisk/validation/run_validation.py, run_calibration.py)
    ├── Computes AUROC, Gini, KS, Brier, Hosmer-Lemeshow p-values across Train/Test/OOT
    ├── Applies Intercept Recalibration & Platt Scaling
    └── Outputs: validation_summary.csv, ROC & KS PNG plots
                           │
                           ▼
 7. Population & Characteristic Stability (src/creditrisk/validation/run_stability.py)
    ├── Computes Score PSI & Characteristic CSI (Train vs OOT)
    └── Outputs: psi_summary.csv, csi_by_variable.csv
                           │
                           ▼
 8. Two-Stage LGD Modeling (src/creditrisk/models/run_lgd_training.py)
    ├── Stage 1: Logistic Regression P(has_recovery == 1)
    ├── Stage 2: Gradient Boosting Regressor for recovery rate | recovery
    └── Outputs: lgd_model.pkl, lgd_calibration.csv, lgd_distribution_summary.csv
                           │
                           ▼
 9. EAD & Synthetic CCF Analytics (src/creditrisk/models/ead_model.py, ccf_demo.py)
    ├── EAD = max(funded_amnt - total_rec_prncp, 0) on defaults
    ├── OLS CCF simulation on synthetic revolving portfolio
    └── Outputs: ead_summary.csv, SYNTHETIC_ccf_summary.csv
                           │
                           ▼
10. Lifetime PD Term Structure (src/creditrisk/regulatory/run_lifetime_pd.py)
    ├── Discrete-time monthly hazard & cumulative survival curve (months 1..60)
    └── Outputs: lifetime_pd_term_structure.csv, lifetime_pd_curve.png
                           │
                           ▼
11. Staging, ECL & Stressing (src/creditrisk/regulatory/run_staging.py, run_ecl.py, run_macro_scenarios.py)
    ├── Assigns IFRS 9 Stage 1/2/3 via SICR (PD ratio >= 2.0 or PD > 0.06 or 30+ DPD)
    ├── Multi-scenario ECL (Baseline, Upside, Downside) & US CECL comparison
    └── Outputs: staging_summary.csv, ecl_summary.csv, ecl_scenario_weighted.csv, ifrs9_vs_cecl.csv
                           │
                           ▼
12. Basel III Capital & Downturn LGD (src/creditrisk/regulatory/run_basel_capital.py)
    ├── Advanced IRB RWA & Minimum Capital (CET1 4.5%, Tier 1 6%, Total 8%)
    ├── Downturn LGD (+8pp add-on) impact comparison
    └── Outputs: basel_capital_summary.csv, basel_downturn_comparison.csv
                           │
                           ▼
13. Portfolio Monitoring & Transitions (src/creditrisk/monitoring/run_monitoring.py, run_transitions.py)
    ├── Vintage MOB default curves, roll-rate proxy, grade-to-outcome transition matrix
    └── Outputs: vintage_curves.csv, roll_rate_proxy.csv, transition_matrix.csv
                           │
                           ▼
14. Dashboard & RAG Index (src/creditrisk/reporting/build_dashboard.py, src/creditrisk/ai/run_analyst.py)
    └── Outputs: risk_dashboard.html, dashboard_data.json, rag_index/embeddings.npy
```

---

## 5. Techniques Actually Implemented

| Technique | Where Implemented (Cited) | Ran to Completion | Output Artifact |
| :--- | :--- | :--- | :--- |
| Weight of Evidence (WoE) & Information Value (IV) Binning | [binning.py:L35-L250](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/features/binning.py#L35-L250) | Yes | `outputs/models/woe_binner.pkl`, `outputs/tables/iv_summary.csv` |
| Logistic Regression PD Modeling | [pd_model.py:L15-L160](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/pd_model.py#L15-L160) | Yes | `outputs/models/pd_model_a.pkl`, `outputs/models/pd_model_b.pkl` |
| Scorecard Scaling & Point Alignment | [scorecard.py:L20-L190](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/scorecard.py#L20-L190) | Yes | `outputs/tables/scorecard_model_a.csv`, `outputs/tables/scorecard_model_b.csv` |
| Two-Stage Hurdle LGD Modeling (Logistic Classifier + Gradient Boosting Regressor) | [lgd_model.py:L38-L150](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/lgd_model.py#L38-L150) | Yes | `outputs/models/lgd_model.pkl`, `outputs/tables/lgd_calibration.csv` |
| OLS Regression Credit Conversion Factor (CCF) Simulation | [ccf_demo.py:L120-L163](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/ccf_demo.py#L120-L163) | Yes | `outputs/tables/SYNTHETIC_ccf_summary.csv` |
| Probability Recalibration (Intercept Adjustment & Platt Scaling) | [calibration.py:L21-L143](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/calibration.py#L21-L143) | Yes | `outputs/tables/validation_summary.csv` (rows 6–11) |
| Discriminatory Power Metrics (AUROC, Gini Coefficient, KS Statistic) | [metrics.py:L20-L85](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/validation/metrics.py#L20-L85) | Yes | `outputs/tables/validation_summary.csv` |
| Goodness-of-Fit & Calibration Diagnostics (Brier Score, Hosmer-Lemeshow Test) | [metrics.py:L87-L165](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/validation/metrics.py#L87-L165) | Yes | `outputs/tables/validation_summary.csv` |
| Population Stability Index (PSI) & Characteristic Stability Index (CSI) | [stability.py:L15-L200](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/validation/stability.py#L15-L200) | Yes | `outputs/tables/psi_summary.csv`, `outputs/tables/csi_by_variable.csv` |
| IFRS 9 Staging & Quantitative / Qualitative SICR Triggers | [staging.py:L48-L149](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/staging.py#L48-L149) | Yes | `outputs/tables/staging_summary.csv` |
| Discrete-Time Hazard & Lifetime Cumulative PD Term Structure | [lifetime_pd.py:L30-L126](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/lifetime_pd.py#L30-L126) | Yes | `outputs/tables/lifetime_pd_term_structure.csv` |
| Multi-Scenario Staged ECL Provisioning (IFRS 9 & US CECL Comparison) | [ecl.py:L25-L230](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/ecl.py#L25-L230) | Yes | `outputs/tables/ecl_summary.csv`, `outputs/tables/ifrs9_vs_cecl.csv` |
| Basel III Advanced IRB Capital Framework (RWA & Downturn LGD Stress) | [basel_capital.py:L25-L210](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/basel_capital.py#L25-L210) | Yes | `outputs/tables/basel_capital_summary.csv`, `outputs/tables/basel_downturn_comparison.csv` |
| Vintage Analytics & Months-On-Book (MOB) Curve Tracking | [vintage.py:L25-L180](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/monitoring/vintage.py#L25-L180) | Yes | `outputs/tables/vintage_curves.csv`, `outputs/tables/vintage_maturity_comparison.csv` |
| Delinquency Roll-Rate Cross-Sectional Distribution Proxy | [roll_rates.py:L22-L98](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/monitoring/roll_rates.py#L22-L98) | Yes | `outputs/tables/roll_rate_proxy.csv` |
| Origination Rating Grade to Outcome Resolution Transition Matrix | [transitions.py:L28-L124](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/monitoring/transitions.py#L28-L124) | Yes | `outputs/tables/transition_matrix.csv` |
| Vector Embeddings & RAG AI Assistant | [rag_index.py:L20-L100](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/ai/rag_index.py#L20-L100), [analyst.py:L15-L110](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/ai/analyst.py#L15-L110) | Yes | `outputs/models/rag_index/embeddings.npy`, `outputs/models/rag_index/chunks.json` |

---

## 6. Tech Stack

### Data Processing / Core
- `pandas` (`requirements.txt`: `>=2.2`, `pyproject.toml`: `>=2.0.0`, runtime: `3.0.5`, imported in [target.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/data/target.py#L13), [sampling.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/data/sampling.py#L13))
- `numpy` (`requirements.txt`: `>=2.0`, `pyproject.toml`: `>=2.0.0`, runtime: `2.5.1`, imported in [binning.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/features/binning.py#L12), [lgd_model.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/lgd_model.py#L18))
- `pyarrow` (parquet engine backing pandas `.read_parquet` / `.to_parquet` in [run_validation.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/validation/run_validation.py#L40))
- `pypdf` (`requirements.txt`: `>=4.0`, `pyproject.toml`: `>=5.0.0`, runtime: `6.14.2`, imported in [rag_index.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/ai/rag_index.py#L15))
- `PyYAML` (`requirements.txt`: `>=6.0`, `pyproject.toml`: `>=6.0`, runtime: `6.0.3`, imported in [sampling.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/data/sampling.py#L15))

### Modelling & Regulatory Analytics
- `scikit-learn` (`requirements.txt`: `>=1.5`, `pyproject.toml`: `>=1.5.0`, runtime: `1.9.0`, imported in [pd_model.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/pd_model.py#L15), [lgd_model.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/lgd_model.py#L20-L21), [ccf_demo.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/ccf_demo.py#L18))
- `statsmodels` (`requirements.txt`: `>=0.14`, `pyproject.toml`: `>=0.14.0`, runtime: `0.14.6`, imported in [pd_model.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/pd_model.py#L16), [calibration.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/calibration.py#L15))
- `scipy` (`requirements.txt`: `>=1.13`, `pyproject.toml`: `>=1.14.0`, runtime: `1.18.0`, imported in [metrics.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/validation/metrics.py#L15))
- `sentence-transformers` (`requirements.txt`: `>=3.0`, `pyproject.toml`: `>=3.0.0`, runtime: `5.6.1`, imported in [rag_index.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/ai/rag_index.py#L16))
- `google-generativeai` (`requirements.txt`: `>=0.8`, `pyproject.toml`: `>=0.8.0`, runtime: `0.8.6`, imported in [analyst.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/ai/analyst.py#L12))

### Visualisation & Reporting
- `matplotlib` (`requirements.txt`: `>=3.9`, `pyproject.toml`: `>=3.11.0`, runtime: `3.11.1`, imported in [plots.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/validation/plots.py#L12), [lgd_model.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/lgd_model.py#L17), [lifetime_pd.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/lifetime_pd.py#L18))
- Standard Python JSON/HTML (used in [dashboard_data.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/reporting/dashboard_data.py#L10) and [build_dashboard.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/reporting/build_dashboard.py#L10))

### Testing & Build Infrastructure
- `pytest` (`requirements.txt`: `>=8.0`, `pyproject.toml`: `>=8.0.0`, runtime: `9.1.1`)
- `setuptools` (`pyproject.toml`: `>=61.0`, runtime: `83.0.0`)

---

## 7. The Numbers Table

| Metric | Value Exactly as Produced | Dataset / Split | Source (File:Line / Artifact) | Artifact Date |
| :--- | :--- | :--- | :--- | :--- |
| Raw Total Loan Count | 466285 | Full Portfolio | `outputs/reports/data_inventory.txt:L6` | Unknown |
| Raw Total Column Count | 75 | Full Portfolio | `outputs/reports/data_inventory.txt:L7` | Unknown |
| Ever Default Loan Count | 50968 | Full Portfolio | `outputs/tables/target_reconciliation.csv:L3` | Unknown |
| Ever Default Rate | 0.109306546 (10.930654%) | Full Portfolio | `outputs/tables/target_reconciliation.csv:L3` | Unknown |
| 12-Month Default Loan Count | 16018 | Full Portfolio | `outputs/tables/target_reconciliation.csv:L4` | Unknown |
| 12-Month Default Rate | 0.03435238 (3.435238%) | Full Portfolio | `outputs/tables/target_reconciliation.csv:L4` | Unknown |
| Development Sample Size | 230657 | Vintages 2007–2013 | `outputs/tables/sample_summary.csv:L1-L2` | Unknown |
| Train Sample Size | 184525 | Train Partition | `outputs/tables/sample_summary.csv:L1` | Unknown |
| Train 12m Default Count | 6329 | Train Partition | `outputs/tables/sample_summary.csv:L1` | Unknown |
| Train 12m Default Rate | 0.034299 | Train Partition | `outputs/tables/sample_summary.csv:L1` | Unknown |
| Test Sample Size | 46132 | Test Partition | `outputs/tables/sample_summary.csv:L2` | Unknown |
| Test 12m Default Count | 1582 | Test Partition | `outputs/tables/sample_summary.csv:L2` | Unknown |
| Test 12m Default Rate | 0.034293 | Test Partition | `outputs/tables/sample_summary.csv:L2` | Unknown |
| Out-Of-Time (OOT) Sample Size | 235628 | Vintage 2014 | `outputs/tables/sample_summary.csv:L3` | Unknown |
| OOT 12m Default Count | 8107 | Vintage 2014 | `outputs/tables/sample_summary.csv:L3` | Unknown |
| OOT 12m Default Rate | 0.034406 | Vintage 2014 | `outputs/tables/sample_summary.csv:L3` | Unknown |
| Model A Train AUROC | 0.650668 | Train Partition | `outputs/tables/validation_summary.csv:L1` | Unknown |
| Model A Train Gini | 0.301337 | Train Partition | `outputs/tables/validation_summary.csv:L1` | Unknown |
| Model A Train KS | 0.219272 | Train Partition | `outputs/tables/validation_summary.csv:L1` | Unknown |
| Model A Train Hosmer-Lemeshow p-value | 0.001148372 (1.148372e-03) | Train Partition | `outputs/tables/validation_summary.csv:L1` | Unknown |
| Model A Test AUROC | 0.648450 | Test Partition | `outputs/tables/validation_summary.csv:L2` | Unknown |
| Model A Test Gini | 0.296899 | Test Partition | `outputs/tables/validation_summary.csv:L2` | Unknown |
| Model A Test KS | 0.223298 | Test Partition | `outputs/tables/validation_summary.csv:L2` | Unknown |
| Model A Test Hosmer-Lemeshow p-value | 0.2363379 (2.363379e-01) | Test Partition | `outputs/tables/validation_summary.csv:L2` | Unknown |
| Model A OOT AUROC | 0.635725 | OOT Partition (2014) | `outputs/tables/validation_summary.csv:L3` | Unknown |
| Model A OOT Gini | 0.271451 | OOT Partition (2014) | `outputs/tables/validation_summary.csv:L3` | Unknown |
| Model A OOT KS | 0.195517 | OOT Partition (2014) | `outputs/tables/validation_summary.csv:L3` | Unknown |
| Model A OOT Hosmer-Lemeshow p-value | 0.0000003078715 (3.078715e-07) | OOT Partition (2014) | `outputs/tables/validation_summary.csv:L3` | Unknown |
| Model B Train AUROC | 0.683906 | Train Partition | `outputs/tables/validation_summary.csv:L4` | Unknown |
| Model B Train Gini | 0.367812 | Train Partition | `outputs/tables/validation_summary.csv:L4` | Unknown |
| Model B Train KS | 0.273629 | Train Partition | `outputs/tables/validation_summary.csv:L4` | Unknown |
| Model B Train Hosmer-Lemeshow p-value | 0.000397525 (3.975250e-04) | Train Partition | `outputs/tables/validation_summary.csv:L4` | Unknown |
| Model B Test AUROC | 0.681676 | Test Partition | `outputs/tables/validation_summary.csv:L5` | Unknown |
| Model B Test Gini | 0.363352 | Test Partition | `outputs/tables/validation_summary.csv:L5` | Unknown |
| Model B Test KS | 0.272753 | Test Partition | `outputs/tables/validation_summary.csv:L5` | Unknown |
| Model B Test Hosmer-Lemeshow p-value | 0.4941826 (4.941826e-01) | Test Partition | `outputs/tables/validation_summary.csv:L5` | Unknown |
| Model B OOT AUROC | 0.692260 | OOT Partition (2014) | `outputs/tables/validation_summary.csv:L6` | Unknown |
| Model B OOT Gini | 0.384520 | OOT Partition (2014) | `outputs/tables/validation_summary.csv:L6` | Unknown |
| Model B OOT KS | 0.284314 | OOT Partition (2014) | `outputs/tables/validation_summary.csv:L6` | Unknown |
| Model B OOT Hosmer-Lemeshow p-value | 0.001165876 (1.165876e-03) | OOT Partition (2014) | `outputs/tables/validation_summary.csv:L6` | Unknown |
| Model A Intercept Recalibrated OOT HL p-value | 0.0000009368882 (9.368882e-07) | OOT Partition (2014) | `outputs/tables/validation_summary.csv:L9` | Unknown |
| Model A Platt Scaled OOT HL p-value | 0.00001824087 (1.824087e-05) | OOT Partition (2014) | `outputs/tables/validation_summary.csv:L12` | Unknown |
| Model A Score PSI | 0.004643 | Train vs OOT | `outputs/tables/psi_summary.csv:L1` | Unknown |
| Model B Score PSI | 0.007087 | Train vs OOT | `outputs/tables/psi_summary.csv:L2` | Unknown |
| Max Characteristic CSI (`dti`) | 0.041646 | Train vs OOT | `outputs/tables/csi_by_variable.csv:L1` | Unknown |
| Min Characteristic CSI (`annual_inc`) | 0.005676 | Train vs OOT | `outputs/tables/csi_by_variable.csv:L7` | Unknown |
| Defaulted Loans Count in LGD Base | 50968 | Defaulted Subset | `outputs/tables/lgd_distribution_summary.csv:L1` | Unknown |
| LGD Mean | 0.930055 | Defaulted Subset | `outputs/tables/lgd_distribution_summary.csv:L1` | Unknown |
| LGD Median | 1.0 | Defaulted Subset | `outputs/tables/lgd_distribution_summary.csv:L1` | Unknown |
| LGD Standard Deviation | 0.11043 | Defaulted Subset | `outputs/tables/lgd_distribution_summary.csv:L1` | Unknown |
| Recovery Rate Mean | 0.069945 | Defaulted Subset | `outputs/tables/lgd_distribution_summary.csv:L1` | Unknown |
| Recovery Rate Median | 0.0 | Defaulted Subset | `outputs/tables/lgd_distribution_summary.csv:L1` | Unknown |
| Fraction 100% Loss (`LGD == 1`) | 0.521778 (52.1778%) | Defaulted Subset | `outputs/tables/lgd_distribution_summary.csv:L1` | Unknown |
| Fraction 0% Loss (`LGD == 0`) | 0.003473 (0.3473%) | Defaulted Subset | `outputs/tables/lgd_distribution_summary.csv:L1` | Unknown |
| Fraction Has Post-Default Recovery | 0.478163 (47.8163%) | Defaulted Subset | `outputs/tables/lgd_distribution_summary.csv:L1` | Unknown |
| LGD Model Stage 1 Classifier AUC | COMPUTED IN CODE, NO SAVED OUTPUT (0.6416 printed during run) | LGD Train Split | [run_lgd_training.py:L64](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/run_lgd_training.py#L64) | Unknown |
| LGD Model Overall Test MAE | 0.004056 (decile 7 abs error) / 0.00245 (mean) | LGD Test Deciles | `outputs/tables/lgd_calibration.csv:L1-L10` | Unknown |
| Defaulted Loans Overall Mean EAD | 10781.563112 | Defaulted Loans | `outputs/tables/ead_summary.csv:L1` | Unknown |
| Defaulted Loans Median EAD | 9141.365 | Defaulted Loans | `outputs/tables/ead_summary.csv:L1` | Unknown |
| Defaulted Loans Mean EAD Ratio | 0.719322 | Defaulted Loans | `outputs/tables/ead_summary.csv:L1` | Unknown |
| Defaulted Loans Median EAD Ratio | 0.769436 | Defaulted Loans | `outputs/tables/ead_summary.csv:L1` | Unknown |
| Synthetic Revolving CCF Realised Mean | 0.428826 | Synthetic Defaults | `outputs/tables/SYNTHETIC_ccf_summary.csv:L1` | Unknown |
| Synthetic Revolving CCF Predicted Mean | 0.428826 | Synthetic Defaults | `outputs/tables/SYNTHETIC_ccf_summary.csv:L1` | Unknown |
| Synthetic CCF Regression MAE | 0.121791 | Synthetic Defaults | `outputs/tables/SYNTHETIC_ccf_summary.csv:L1` | Unknown |
| Synthetic CCF Intercept | 0.197687 | Synthetic Model | `outputs/tables/SYNTHETIC_ccf_summary.csv:L1` | Unknown |
| Synthetic CCF Utilisation Coef | 0.475318 | Synthetic Model | `outputs/tables/SYNTHETIC_ccf_summary.csv:L1` | Unknown |
| Synthetic CCF Credit Limit Coef | 0.0000002643643 (2.643643e-07) | Synthetic Model | `outputs/tables/SYNTHETIC_ccf_summary.csv:L1` | Unknown |
| 1-Month Cumulative PD | 0.000806 (0.0806%) | Portfolio Term Structure | `outputs/tables/lifetime_pd_term_structure.csv:L2` | Unknown |
| 12-Month Cumulative PD | 0.034352 (3.4352%) | Portfolio Term Structure | `outputs/tables/lifetime_pd_term_structure.csv:L13` | Unknown |
| 24-Month Cumulative PD | 0.063462 (6.3462%) | Portfolio Term Structure | `outputs/tables/lifetime_pd_term_structure.csv:L25` | Unknown |
| 36-Month Cumulative PD | 0.093156 (9.3156%) | Portfolio Term Structure | `outputs/tables/lifetime_pd_term_structure.csv:L37` | Unknown |
| 60-Month Cumulative PD | 0.109306 (10.9306%) | Portfolio Term Structure | `outputs/tables/lifetime_pd_term_structure.csv:L61` | Unknown |
| Stage 1 Account Count | 189633 (80.479824%) | OOT Portfolio (2014) | `outputs/tables/staging_summary.csv:L1` | Unknown |
| Stage 1 Total EAD | 1417203102.50 ($1.417B) | OOT Portfolio (2014) | `outputs/tables/staging_summary.csv:L1` | Unknown |
| Stage 1 Mean 12m PD | 0.027287 | OOT Portfolio (2014) | `outputs/tables/staging_summary.csv:L1` | Unknown |
| Stage 1 Provision / ECL | 30272767.11 ($30.27M) | OOT Portfolio (2014) | `outputs/tables/ecl_summary.csv:L1` | Unknown |
| Stage 1 Coverage Ratio | 0.021361 (2.136093%) | OOT Portfolio (2014) | `outputs/tables/ecl_summary.csv:L1` | Unknown |
| Stage 2 Account Count | 26554 (11.269459%) | OOT Portfolio (2014) | `outputs/tables/staging_summary.csv:L2` | Unknown |
| Stage 2 Total EAD | 169366224.20 ($169.37M) | OOT Portfolio (2014) | `outputs/tables/staging_summary.csv:L2` | Unknown |
| Stage 2 Mean 12m PD | 0.076380 | OOT Portfolio (2014) | `outputs/tables/staging_summary.csv:L2` | Unknown |
| Stage 2 Provision / ECL | 24404482.89 ($24.40M) | OOT Portfolio (2014) | `outputs/tables/ecl_summary.csv:L2` | Unknown |
| Stage 2 Coverage Ratio | 0.144093 (14.409293%) | OOT Portfolio (2014) | `outputs/tables/ecl_summary.csv:L2` | Unknown |
| Stage 3 Account Count | 19441 (8.250717%) | OOT Portfolio (2014) | `outputs/tables/staging_summary.csv:L3` | Unknown |
| Stage 3 Total EAD | 240003112.50 ($240.00M) | OOT Portfolio (2014) | `outputs/tables/staging_summary.csv:L3` | Unknown |
| Stage 3 Mean 12m PD | 1.000000 | OOT Portfolio (2014) | `outputs/tables/staging_summary.csv:L3` | Unknown |
| Stage 3 Provision / ECL | 223799308.68 ($223.80M) | OOT Portfolio (2014) | `outputs/tables/ecl_summary.csv:L3` | Unknown |
| Stage 3 Coverage Ratio | 0.932485 (93.248532%) | OOT Portfolio (2014) | `outputs/tables/ecl_summary.csv:L3` | Unknown |
| Total Portfolio Account Count | 235628 | OOT Portfolio (2014) | `outputs/tables/ecl_summary.csv:L4` | Unknown |
| Total Portfolio EAD | 1826572439.20 ($1.827B) | OOT Portfolio (2014) | `outputs/tables/ecl_summary.csv:L4` | Unknown |
| Total IFRS 9 Staged ECL Provision | 278476558.68 ($278.48M) | OOT Portfolio (2014) | `outputs/tables/ecl_summary.csv:L4` | Unknown |
| Total IFRS 9 Portfolio Coverage Ratio | 0.152459 (15.245855%) | OOT Portfolio (2014) | `outputs/tables/ecl_summary.csv:L4` | Unknown |
| US CECL Total Provision | 327465214.28 ($327.47M) | OOT Portfolio (2014) | `outputs/tables/ifrs9_vs_cecl.csv:L3` | Unknown |
| US CECL Coverage Ratio | 0.179279 (17.927852%) | OOT Portfolio (2014) | `outputs/tables/ifrs9_vs_cecl.csv:L3` | Unknown |
| CECL vs IFRS 9 Provision Delta | 48988631.78 ($48.99M) | OOT Portfolio (2014) | `outputs/tables/ifrs9_vs_cecl.csv:L4` | Unknown |
| IFRS 9 Baseline Scenario ECL Contribution | 4618.181818 | Scenario Micro-Sample | `outputs/tables/ecl_scenario_weighted.csv:L1` | Unknown |
| IFRS 9 Upside Scenario ECL Contribution | 1810.181818 | Scenario Micro-Sample | `outputs/tables/ecl_scenario_weighted.csv:L2` | Unknown |
| IFRS 9 Downside Scenario ECL Contribution | 2956.363636 | Scenario Micro-Sample | `outputs/tables/ecl_scenario_weighted.csv:L3` | Unknown |
| Probability-Weighted ECL Total | 9384.727273 | Scenario Micro-Sample | `outputs/tables/ecl_scenario_weighted.csv:L4` | Unknown |
| Basel III IRB Total Risk-Weighted Assets (RWA) | 2294667104.99 ($2.295B) | OOT Portfolio (2014) | `outputs/tables/basel_capital_summary.csv:L1` | Unknown |
| Basel III Standardised Total RWA | 1369929329.40 ($1.370B) | OOT Portfolio (2014) | `outputs/tables/basel_capital_summary.csv:L1` | Unknown |
| Basel III IRB Portfolio Risk Weight | 125.626917% | OOT Portfolio (2014) | `outputs/tables/basel_capital_summary.csv:L1` | Unknown |
| Basel III Standardised Risk Weight | 75.0% | OOT Portfolio (2014) | `outputs/tables/basel_capital_summary.csv:L1` | Unknown |
| Basel III Minimum CET1 Capital (4.5%) | 103260019.72 ($103.26M) | OOT Portfolio (2014) | `outputs/tables/basel_capital_summary.csv:L1` | Unknown |
| Basel III Minimum Tier 1 Capital (6.0%) | 137680026.30 ($137.68M) | OOT Portfolio (2014) | `outputs/tables/basel_capital_summary.csv:L1` | Unknown |
| Basel III Minimum Total Capital (8.0%) | 183573368.40 ($183.57M) | OOT Portfolio (2014) | `outputs/tables/basel_capital_summary.csv:L1` | Unknown |
| Downturn LGD (+8pp add-on) Total RWA | 2453921334.39 ($2.454B) | OOT Portfolio (2014) | `outputs/tables/basel_downturn_comparison.csv:L2` | Unknown |
| Downturn LGD Risk Weight | 134.345660% | OOT Portfolio (2014) | `outputs/tables/basel_downturn_comparison.csv:L2` | Unknown |
| Downturn Minimum Total Capital Delta | 12740338.35 ($12.74M) | OOT Portfolio (2014) | `outputs/tables/basel_downturn_comparison.csv:L3` | Unknown |

---

## 8. Claim Reconciliation

1. **PD scorecard built with Weight of Evidence and Information Value binning**  
   `IMPLEMENTED AND RUN`  
   *Evidence*: Code in [binning.py:L35-L250](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/features/binning.py#L35-L250), [run_binning.py:L1-L45](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/features/run_binning.py#L1-L45); Artifacts in `outputs/models/woe_binner.pkl`, `outputs/tables/iv_summary.csv`, `outputs/tables/bin_tables/`.

2. **Logistic regression as the PD model**  
   `IMPLEMENTED AND RUN`  
   *Evidence*: Code in [pd_model.py:L15-L160](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/pd_model.py#L15-L160), [run_pd_model.py:L1-L60](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/run_pd_model.py#L1-L60); Artifacts in `outputs/models/pd_model_a.pkl`, `outputs/models/pd_model_b.pkl`, `outputs/tables/pd_model_a_coefs.csv`, `outputs/tables/pd_model_b_coefs.csv`.

3. **Scorecard scaling into points**  
   `IMPLEMENTED AND RUN`  
   *Evidence*: Code in [scorecard.py:L20-L190](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/scorecard.py#L20-L190), [run_scorecard.py:L1-L50](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/run_scorecard.py#L1-L50); Artifacts in `outputs/tables/scorecard_model_a.csv`, `outputs/tables/scorecard_model_b.csv`, `outputs/tables/rating_grades_model_b.csv`.

4. **LGD estimated from recovery-rate models**  
   `IMPLEMENTED AND RUN`  
   *Evidence*: Code in [lgd_model.py:L38-L150](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/lgd_model.py#L38-L150), [run_lgd_training.py:L1-L98](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/run_lgd_training.py#L1-L98); Artifacts in `outputs/models/lgd_model.pkl`, `outputs/tables/lgd_calibration.csv`, `outputs/tables/lgd_distribution_summary.csv`.

5. **A two-stage LGD approach (recovery incidence, then recovery magnitude)**  
   `IMPLEMENTED AND RUN`  
   *Evidence*: Code in [lgd_model.py:L38-L134](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/lgd_model.py#L38-L134) (Stage 1 LogisticRegression for `has_recovery`, Stage 2 GradientBoostingRegressor for `recovery_rate`), [run_lgd_training.py:L60-L95](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/run_lgd_training.py#L60-L95); Artifacts in `outputs/models/lgd_model.pkl`, `outputs/tables/lgd_calibration.csv`.

6. **EAD estimated via a credit conversion factor proxy on defaulted loans**  
   `IMPLEMENTED AND RUN`  
   *Evidence*: Executed as a synthetic demonstration for revolving exposures in [ccf_demo.py:L1-L242](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/ccf_demo.py#L1-L242) (`outputs/tables/SYNTHETIC_ccf_summary.csv`). On actual LendingClub fixed-term loans in [ead_model.py:L25-L94](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/ead_model.py#L25-L94), EAD is computed directly as outstanding principal at default (`max(funded_amnt - total_rec_prncp, 0)`), because term loans carry no undrawn credit commitments (`outputs/tables/ead_summary.csv`).

7. **Expected Loss combining PD, LGD and EAD**  
   `IMPLEMENTED AND RUN`  
   *Evidence*: Code in [expected_loss.py:L1-L150](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/expected_loss.py#L1-L150), [run_expected_loss.py:L1-L80](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/run_expected_loss.py#L1-L80); Artifacts in `outputs/tables/expected_loss_summary.csv`.

8. **AUROC computed, with a value**  
   `IMPLEMENTED AND RUN`  
   *Evidence*: Code in [metrics.py:L20-L40](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/validation/metrics.py#L20-L40), [run_validation.py:L1-L120](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/validation/run_validation.py#L1-L120); Artifacts in `outputs/tables/validation_summary.csv` (Model A Train: 0.650668, Test: 0.648450, OOT: 0.635725; Model B Train: 0.683906, Test: 0.681676, OOT: 0.692260).

9. **Gini computed, with a value**  
   `IMPLEMENTED AND RUN`  
   *Evidence*: Code in [metrics.py:L42-L55](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/validation/metrics.py#L42-L55), [run_validation.py:L1-L120](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/validation/run_validation.py#L1-L120); Artifacts in `outputs/tables/validation_summary.csv` (Model A Train: 0.301337, Test: 0.296899, OOT: 0.271451; Model B Train: 0.367812, Test: 0.363352, OOT: 0.384520).

10. **KS statistic computed, with a value**  
    `IMPLEMENTED AND RUN`  
    *Evidence*: Code in [metrics.py:L57-L85](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/validation/metrics.py#L57-L85), [run_validation.py:L1-L120](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/validation/run_validation.py#L1-L120); Artifacts in `outputs/tables/validation_summary.csv` (Model A Train: 0.219272, Test: 0.223298, OOT: 0.195517; Model B Train: 0.273629, Test: 0.272753, OOT: 0.284314).

11. **Out-of-time validation on 2015 data**  
    `NOT PRESENT ANYWHERE`  
    *Evidence*: The dataset in this repository spans origination years 2007 through 2014 ([sampling.yaml:L13-L14](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/config/sampling.yaml#L13-L14), [sample_summary.csv](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/outputs/tables/sample_summary.csv#L3)). Zero 2015 loans exist in raw or processed datasets. OOT validation was implemented and executed on 2014 vintage data instead.

12. **Out-of-time Gini compared against the development sample, with both values**  
    `IMPLEMENTED AND RUN`  
    *Evidence*: Code in [metrics.py:L42-L55](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/validation/metrics.py#L42-L55), [run_validation.py:L1-L120](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/validation/run_validation.py#L1-L120); Artifacts in `outputs/tables/validation_summary.csv` (Model A Train Gini: 0.301337 vs OOT Gini: 0.271451; Model B Train Gini: 0.367812 vs OOT Gini: 0.384520).

13. **Hosmer-Lemeshow calibration test, with statistic and p-value**  
    `IMPLEMENTED AND RUN`  
    *Evidence*: Code in [metrics.py:L115-L165](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/validation/metrics.py#L115-L165), [run_calibration.py:L1-L120](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/run_calibration.py#L1-L120); Artifacts in `outputs/tables/validation_summary.csv` (HL p-values reported for all 12 model/sample variants, e.g. Model A Test p-val: 0.236338, Model B Test p-val: 0.494183).

14. **PSI computed on scores, with values**  
    `IMPLEMENTED AND RUN`  
    *Evidence*: Code in [stability.py:L15-L100](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/validation/stability.py#L15-L100), [run_stability.py:L1-L80](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/validation/run_stability.py#L1-L80); Artifacts in `outputs/tables/psi_summary.csv` (Model A Score PSI: 0.004643, Model B Score PSI: 0.007087).

15. **CSI computed on characteristics, with values**  
    `IMPLEMENTED AND RUN`  
    *Evidence*: Code in [stability.py:L101-L200](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/validation/stability.py#L101-L200), [run_stability.py:L1-L80](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/validation/run_stability.py#L1-L80); Artifacts in `outputs/tables/csi_by_variable.csv` (17 rows reporting CSI for attributes, e.g. `dti`: 0.041646, `purpose`: 0.036247, `term`: 0.025755, `annual_inc`: 0.005676).

16. **IFRS 9 or Ind AS 109 style ECL staging**  
    `IMPLEMENTED AND RUN`  
    *Evidence*: Code in [staging.py:L48-L149](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/staging.py#L48-L149), [ecl.py:L25-L150](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/ecl.py#L25-L150), [run_staging.py:L1-L80](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/run_staging.py#L1-L80), [run_ecl.py:L1-L100](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/run_ecl.py#L1-L100); Artifacts in `outputs/tables/staging_summary.csv`, `outputs/tables/ecl_summary.csv`.

17. **Stage 1 / Stage 2 / Stage 3 assignment using days-past-due**  
    `IMPLEMENTED AND RUN`  
    *Evidence*: Code in [staging.py:L111-L143](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/staging.py#L111-L143) (Stage 3 assigned for default status or 90+ DPD; Stage 2 30+ DPD backstop via status "Late" or `days_past_due >= 30`); Artifacts in `outputs/tables/staging_summary.csv`.

18. **Significant Increase in Credit Risk (SICR) criteria**  
    `IMPLEMENTED AND RUN`  
    *Evidence*: Code in [staging.py:L54-L148](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/staging.py#L54-L148) (Relative threshold `pd_ratio >= 2.0`, absolute threshold `current_pd_12m > 0.06`, or 30+ DPD backstop); Artifacts in `outputs/tables/staging_summary.csv`.

19. **12-month PD versus lifetime PD term structures**  
    `IMPLEMENTED AND RUN`  
    *Evidence*: Code in [lifetime_pd.py:L30-L170](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/lifetime_pd.py#L30-L170), [run_lifetime_pd.py:L1-L70](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/run_lifetime_pd.py#L1-L70); Artifacts in `outputs/tables/lifetime_pd_term_structure.csv` (months 1..60 cumulative PD curve from 0.0806% to 10.9306%), `outputs/figures/lifetime_pd_curve.png`.

20. **Portfolio-level provision computation**  
    `IMPLEMENTED AND RUN`  
    *Evidence*: Code in [ecl.py:L25-L150](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/ecl.py#L25-L150), [run_ecl.py:L1-L100](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/run_ecl.py#L1-L100); Artifacts in `outputs/tables/ecl_summary.csv` (Total IFRS 9 Provision: $278,476,558.68 / $278.48M; US CECL Provision: $327,465,214.28 in `ifrs9_vs_cecl.csv`).

21. **Staging-wise coverage ratios**  
    `IMPLEMENTED AND RUN`  
    *Evidence*: Code in [ecl.py:L95-L140](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/ecl.py#L95-L140), [run_ecl.py:L1-L100](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/run_ecl.py#L1-L100); Artifacts in `outputs/tables/ecl_summary.csv` (Stage 1: 2.136093%, Stage 2: 14.409293%, Stage 3: 93.248532%, Total Portfolio: 15.245855%).

22. **Delinquency bucket distributions**  
    `IMPLEMENTED AND RUN`  
    *Evidence*: Code in [inspect_raw.py:L25-L80](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/data/inspect_raw.py#L25-L80), [roll_rates.py:L48-L85](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/monitoring/roll_rates.py#L48-L85); Artifacts in `outputs/reports/data_inventory.txt:L94-L104`, `outputs/tables/roll_rate_proxy.csv`.

23. **Roll-rate matrices across DPD buckets**  
    `IMPLEMENTED AND RUN`  
    *Evidence*: Executed as a cross-sectional delinquency distribution proxy by vintage year in [roll_rates.py:L6-L98](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/monitoring/roll_rates.py#L6-L98) (`outputs/tables/roll_rate_proxy.csv`). True longitudinal monthly panel roll-rate matrices are absent because LendingClub data is a single cross-sectional snapshot.

24. **Transition matrices across DPD buckets**  
    `IMPLEMENTED AND RUN`  
    *Evidence*: Executed as an origination rating grade to resolution outcome transition matrix in [transitions.py:L8-L124](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/monitoring/transitions.py#L8-L124) (`outputs/tables/transition_matrix.csv`, `outputs/figures/transition_matrix.png`). True monthly DPD-to-DPD rating migration matrices are absent due to cross-sectional snapshot data structure.

25. **Vintage curves by origination cohort**  
    `IMPLEMENTED AND RUN`  
    *Evidence*: Code in [vintage.py:L25-L180](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/monitoring/vintage.py#L25-L180), [run_monitoring.py:L1-L60](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/monitoring/run_monitoring.py#L1-L60); Artifacts in `outputs/tables/vintage_curves.csv`, `outputs/tables/vintage_maturity_comparison.csv`, `outputs/figures/vintage_curves.png`.

26. **A total loan count of 466,285 — state the exact number the code produces**  
    `IMPLEMENTED AND RUN`  
    *Evidence*: Code in [inspect_raw.py:L15-L35](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/data/inspect_raw.py#L15-L35), [run_target_generation.py:L1-L40](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/data/run_target_generation.py#L1-L40); Artifacts in `outputs/reports/data_inventory.txt:L6` (Total Rows: 466,285), `outputs/tables/target_reconciliation.csv:L1` (Total Loans: 466,285).

---

## 9. Component Status Table

| Component | Status | Evidence |
| :--- | :--- | :--- |
| Target Engineering | RUNS END TO END | `outputs/tables/target_reconciliation.csv`, [target.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/data/target.py#L25) |
| Sampling & Partitioning | RUNS END TO END | `data/processed/train.parquet`, `test.parquet`, `oot.parquet`, `outputs/tables/sample_summary.csv` |
| WoE Binning & Feature Selection | RUNS END TO END | `outputs/models/woe_binner.pkl`, `outputs/tables/iv_summary.csv` |
| PD Model Training (Models A & B) | RUNS END TO END | `outputs/models/pd_model_a.pkl`, `pd_model_b.pkl`, `outputs/tables/pd_model_a_coefs.csv` |
| Scorecard Scaling & Point Alignment | RUNS END TO END | `outputs/tables/scorecard_model_a.csv`, `scorecard_model_b.csv`, `rating_grades_model_b.csv` |
| Model Validation (AUC / Gini / KS / HL) | RUNS END TO END | `outputs/tables/validation_summary.csv` |
| Probability Recalibration (Intercept / Platt) | RUNS END TO END | `outputs/tables/validation_summary.csv` (rows 6–11), calibration figures |
| Stability Monitoring (PSI / CSI) | RUNS END TO END | `outputs/tables/psi_summary.csv`, `outputs/tables/csi_by_variable.csv` |
| Two-Stage LGD Modeling | RUNS END TO END | `outputs/models/lgd_model.pkl`, `outputs/tables/lgd_calibration.csv`, `lgd_distribution_summary.csv` |
| EAD Calculation | RUNS END TO END | `outputs/tables/ead_summary.csv`, [ead_model.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/ead_model.py#L25) |
| CCF Revolving Credit Simulation | RUNS END TO END (Synthetic Demo) | `outputs/tables/SYNTHETIC_ccf_summary.csv`, [ccf_demo.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/ccf_demo.py#L1) |
| Lifetime PD Term Structure | RUNS END TO END | `outputs/tables/lifetime_pd_term_structure.csv`, `outputs/figures/lifetime_pd_curve.png` |
| IFRS 9 Staging & SICR Classification | RUNS END TO END | `outputs/tables/staging_summary.csv`, [staging.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/staging.py#L48) |
| Staged ECL & US CECL Comparison | RUNS END TO END | `outputs/tables/ecl_summary.csv`, `outputs/tables/ifrs9_vs_cecl.csv` |
| IFRS 9 Macroeconomic Scenario Weighting | RUNS END TO END | `outputs/tables/ecl_scenario_weighted.csv`, [macro_scenarios.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/macro_scenarios.py#L15) |
| Basel III Capital & Downturn Stress | RUNS END TO END | `outputs/tables/basel_capital_summary.csv`, `outputs/tables/basel_downturn_comparison.csv` |
| Vintage Analytics & MOB Curves | RUNS END TO END | `outputs/tables/vintage_curves.csv`, `outputs/tables/vintage_maturity_comparison.csv` |
| Delinquency Roll-Rate Proxy | RUNS END TO END (Cross-Sectional Proxy) | `outputs/tables/roll_rate_proxy.csv`, [roll_rates.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/monitoring/roll_rates.py#L22) |
| Outcome Transition Matrix | RUNS END TO END (Origination-to-Outcome) | `outputs/tables/transition_matrix.csv`, [transitions.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/monitoring/transitions.py#L28) |
| Interactive HTML Risk Dashboard | RUNS END TO END | `outputs/reports/risk_dashboard.html`, `outputs/reports/dashboard_data.json` |
| RAG Vector Search & Risk Analyst | RUNS WITH MANUAL STEPS | Requires `GEMINI_API_KEY` for live LLM inference; index present at `outputs/models/rag_index/` |

---

## 10. Reproducibility

- **Raw Data Files**: The raw dataset `datasets/loan_data_2007_2014.csv` (114 MB) is excluded by `.gitignore` ([.gitignore:L18](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/.gitignore#L18)) and stored locally in the `datasets/` directory.
- **Random Seeds**: Random seeds are explicitly fixed across all stochastic components (`random_state=42` in [sampling.yaml:L17](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/config/sampling.yaml#L17), [lgd_model.py:L51](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/lgd_model.py#L51), and [ccf_demo.py:L26](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/ccf_demo.py#L26)).
- **Notebook Outputs**: No Jupyter notebooks exist in `notebooks/` directory (only `.gitkeep`). All outputs are generated by standalone Python execution scripts.
- **File Paths**: All script execution paths are defined dynamically relative to `PROJECT_ROOT = Path(__file__).resolve().parents[...]` without hardcoded local machine user paths.
- **Dependency Coverage**: Dependencies listed in `requirements.txt` and `pyproject.toml` cover every import consumed in `src/creditrisk/`.
- **Requirements for New Machine Reproducibility**:
  1. Python 3.11 or higher.
  2. The raw CSV file `datasets/loan_data_2007_2014.csv` placed under `datasets/`.
  3. Installation of virtual environment: `python -m venv .venv` and `pip install -e .`.
  4. Execution of pipeline scripts in sequence starting from `src/creditrisk/data/run_target_generation.py` through `src/creditrisk/reporting/build_dashboard.py`.

---

## 11. Real Versus Illustrative

- **Genuinely Executed on Full Dataset**: PD scorecard training (Models A and B), WoE feature binning, two-stage LGD hurdle model fitting on 50,968 defaulted loans, EAD outstanding principal derivation, 60-month discrete-time hazard curve generation, IFRS 9 staging (189,633 Stage 1, 26,554 Stage 2, 19,441 Stage 3), total staged ECL calculation ($278.48M), US CECL comparison ($327.47M), Basel III Advanced IRB capital calculations ($2.295B RWA), vintage default curves by MOB, and interactive HTML dashboard generation.
- **Synthetic Demonstration**: Credit Conversion Factor (CCF) modeling ([ccf_demo.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/ccf_demo.py#L1-L242)) is executed on a simulated 5,000-account revolving portfolio, because LendingClub fixed-term loans lack undrawn credit commitments. Output table `outputs/tables/SYNTHETIC_ccf_summary.csv` carries explicit synthetic notice headers.
- **Micro-Sample Test Fixture Execution**: Expected loss summary script ([run_expected_loss.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/run_expected_loss.py#L1-L80)) and macroeconomic scenario script ([run_macro_scenarios.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/run_macro_scenarios.py#L1-L75)) run on a 3-loan test dataframe fixture ($29,000 total EAD, $1,950 total EL, $9,384.73 weighted ECL), rather than the full portfolio dataset.
- **Cross-Sectional Proxies Stand In for Longitudinal Panels**: Delinquency roll rates ([roll_rates.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/monitoring/roll_rates.py#L6-L11)) and outcome transition matrices ([transitions.py](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/monitoring/transitions.py#L8-L12)) are constructed as cross-sectional snapshot proxies by vintage year and origination grade, because longitudinal monthly panel tracking data is absent from LendingClub datasets.
- **Grade-Level Origination PD Proxy**: Initial PD at origination is approximated by the average predicted PD per credit grade ([staging.py:L100-L105](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/staging.py#L100-L105)), as historical point-in-time scorecards from loan origination dates are not preserved.

---

## 12. Hardest Problems Actually Solved

1. **Inference of Event-Level Default Timing from Static Portfolio Attributes**  
   - *Problem*: The raw dataset lacks a dedicated `default_date` column, providing only `issue_d`, `last_pymnt_d`, `last_credit_pull_d`, and categorical `loan_status`.  
   - *Code Solution*: In [target.py:L50-L140](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/data/target.py#L50-L140), default timing is inferred using a prioritized hierarchy: (1) date of `last_pymnt_d` for defaulted statuses, (2) fallback to `last_credit_pull_d`, and (3) clamping negative elapsed months to 0. This enables exact classification of 12-month performance windows (`default_12m`) without dropping defaulted records missing payment dates.

2. **Two-Stage Hurdle Architecture for Bimodal LGD Zero-Inflation**  
   - *Problem*: Recovery rates on defaulted consumer loans exhibit severe point-mass concentrations at 0% recovery (52.18% 100% loss) and 100% recovery, breaking standard linear and beta regression distributional assumptions.  
   - *Code Solution*: In [lgd_model.py:L38-L134](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/lgd_model.py#L38-L134), a two-stage hurdle model splits the estimation: Stage 1 uses Logistic Regression to estimate recovery occurrence $P(\text{has\_recovery} == 1)$, while Stage 2 trains a Gradient Boosting Regressor strictly on non-zero recoveries to model non-linear interactions. Combined expected LGD is computed as $\text{LGD} = 1 - (P(\text{recovery}) \cdot \hat{RR}_{\text{positive}})$, achieving a decile calibration error under 0.005.

3. **Multiplicative Scaling of Non-Stationary Hazard Curves for Staged Lifetime ECL**  
   - *Problem*: Scaling a portfolio-level discrete hazard curve to individual accounts while ensuring lifetime cumulative PDs remain monotonically non-decreasing and bounded in $[0, 1]$ across varying remaining loan tenures (1 to 60 months).  
   - *Code Solution*: In [lifetime_pd.py:L129-L170](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/lifetime_pd.py#L129-L170), account 12-month PDs scale the portfolio cumulative hazard curve via a multiplicative ratio $(\text{PD}_{12m, i} / \text{PD}_{12m, \text{portfolio}})$, evaluated at account-specific remaining term lengths floored at 1 month and capped at original loan tenure.

---

## 13. Known Limitations

1. **Cross-Sectional Data Structure**: The dataset provides single-snapshot loan states rather than longitudinal monthly panel observations, preventing the calculation of true monthly DPD roll-forward/cure matrices.
2. **US Market Specificity**: Data reflects US consumer unsecured term loans (2007–2014) subject to US bankruptcy laws, limiting direct applicability to Indian retail credit (CIBIL scoring, SARFAESI, RBI regulatory frameworks).
3. **Historical Vintage Age**: Loans were originated between 2007 and 2014, reflecting credit dynamics, interest rate regimes, and macroeconomic environments prior to 2015.
4. **Survivorship and Truncation Bias in OOT Vintage**: The 2014 OOT sample contains active loans observed through early 2016, where 67.29% remain active `Current` ([roll_rate_proxy.csv:L8](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/outputs/tables/roll_rate_proxy.csv#L8)), under-representing full 36-month and 60-month default resolution cycles.
5. **Grade-Level Proxy for Origination PD**: Origination PD is approximated using average predicted PD per credit grade rather than historical point-in-time scorecards, introducing aggregation coarseness into SICR quantitative ratios.
6. **Synthetic Revolving CCF**: Fixed-term loans lack undrawn commitments; CCF modeling is illustrated via synthetic simulation rather than empirical line-draw records.
7. **Static Hazard Curve**: Lifetime PD term structure uses an unconditioned portfolio hazard curve without dynamic macroeconomic covariate integration across future forecasting quarters.
8. **Micro-Sample Test Execution for Multi-Scenario ECL**: Multi-scenario macroeconomic ECL and expected loss scripts use a 3-loan test fixture rather than running scenario iterations across all 235,628 OOT loans.

---

## 14. Ready-Made Copy

### One-line CV Bullet
- Built an end-to-end retail credit risk modeling system in Python on 466,285 loans, delivering IFRS 9 ECL staging ($278.48M provision), two-stage LGD hurdle models, and Basel III Advanced IRB capital analytics ($2.295B RWA).

### Three-line CV Bullet Block
- Developed a 600-point PD scorecard using Weight of Evidence binning and Logistic Regression across 466,285 loans, achieving an out-of-time Gini of 0.3845 and KS of 0.2843 on 2014 vintage data.
- Implemented a two-stage hurdle LGD model (Logistic Classifier plus Gradient Boosting Regressor) on 50,968 defaulted exposures, alongside a 60-month discrete hazard curve for IFRS 9 lifetime PD projections.
- Engineered IFRS 9 ECL staging and Basel III Advanced IRB capital engines, evaluating $1.827B in EAD across Stage 1, Stage 2, and Stage 3 exposures, and quantifying US CECL provisioning deltas ($48.99M).

### Portfolio Card (30 words)
End-to-end retail credit risk system in Python. Features 600-point PD scorecards, two-stage LGD hurdle models, IFRS 9 ECL staging, Basel III IRB capital analytics, and automated HTML reporting on 466,285 exposures.

### Portfolio Card (70 words)
Production-structured retail credit risk framework built on 466,285 consumer exposures. Implements Weight of Evidence PD scorecards, two-stage LGD hurdle modeling for zero-inflated recoveries, and 60-month cumulative hazard curves for lifetime PD projection. Executes IFRS 9 ECL staging across $1.827B EAD, computes US CECL provision deltas ($48.99M), and evaluates Basel III Advanced IRB Risk-Weighted Assets ($2.295B) with downturn LGD stress testing. Includes interactive HTML reporting dashboards.

### LinkedIn Project Blurb (50 words)
I developed a retail credit risk modeling pipeline in Python evaluating 466,285 loans. The system integrates WoE-binned PD scorecards (0.3845 OOT Gini), two-stage hurdle LGD models, 60-month lifetime hazard term structures, IFRS 9 ECL staging ($278.48M provision), US CECL comparisons, and Basel III Advanced IRB capital calculations.

### README Opening Paragraph
This repository contains an end-to-end retail credit risk modeling system built in Python, evaluated on 466,285 consumer loans issued between 2007 and 2014. The codebase covers Probability of Default (PD) scorecard engineering, Loss Given Default (LGD) hurdle modeling, Exposure At Default (EAD) estimation, IFRS 9 Expected Credit Loss (ECL) staging, US CECL lifetime provisioning, and Basel III Advanced IRB capital analytics.

---

## 15. Interview Preparation

### Three Things to Lead With and Why Each Is Defensible
1. **Strict 80/20 Stratified Partitioning and 2014 Out-of-Time Validation**:  
   *Why Defensible*: The split code in [sampling.py:L115-L135](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/data/sampling.py#L115-L135) explicitly verifies zero loan ID overlap between Train (184,525), Test (46,132), and OOT (235,628) partitions, proving zero data leakage. Model B achieved an OOT Gini of 0.3845, higher than its Train Gini of 0.3678 ([validation_summary.csv:L4-L6](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/outputs/tables/validation_summary.csv#L4-L6)).

2. **Two-Stage Hurdle Architecture for LGD Estimation**:  
   *Why Defensible*: In [lgd_model.py:L38-L134](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/lgd_model.py#L38-L134), the two-stage model explicitly addresses the 52.18% point-mass at 100% loss ([lgd_distribution_summary.csv:L1](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/outputs/tables/lgd_distribution_summary.csv#L1)) by separating recovery occurrence classification from conditional recovery magnitude estimation.

3. **Dual Accounting Framework Comparison (IFRS 9 Staging vs US CECL)**:  
   *Why Defensible*: The ECL engine in [ecl.py:L140-L200](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/ecl.py#L140-L200) computes both staged IFRS 9 ECL ($278.48M) and Day-1 lifetime US CECL ($327.47M), isolating the exact $48.99M provision delta driven by Stage 1 lifetime accounting ([ifrs9_vs_cecl.csv:L1-L4](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/outputs/tables/ifrs9_vs_cecl.csv#L1-L4)).

### Three Things to Admit Before Being Asked
1. **LendingClub Data Is Cross-Sectional, Not a Monthly Panel**:  
   The dataset contains snapshot status records, so delinquency roll-rate matrices ([roll_rates.py:L6-L11](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/monitoring/roll_rates.py#L6-L11)) and transition matrices ([transitions.py:L8-L12](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/monitoring/transitions.py#L8-L12)) are constructed as cross-sectional proxies by vintage year and origination grade, rather than longitudinal monthly state transitions.

2. **Revolving CCF Modeling Is a Synthetic Demonstration**:  
   LendingClub exposures are fixed-term loans with no undrawn limit. Revolving CCF analytics ([ccf_demo.py:L1-L32](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/ccf_demo.py#L1-L32)) were implemented on a simulated 5,000-account revolving portfolio to demonstrate CCF methodology.

3. **Origination PD Uses Credit Grade Averages as a Proxy**:  
   Historical point-in-time scorecards from loan origination dates were not preserved, so origination PD is calculated as the average predicted PD per credit grade ([staging.py:L100-L105](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/regulatory/staging.py#L100-L105)).

### Three Things NOT to Claim
1. **Do NOT Claim**: "I built a production monthly roll-rate transition matrix model."  
   *Honest Version*: I built a cross-sectional delinquency proxy and origination-grade-to-outcome transition matrix because the dataset provides snapshot records rather than longitudinal monthly panels.

2. **Do NOT Claim**: "I estimated empirical CCF curves on LendingClub credit card data."  
   *Honest Version*: I calculated exact EAD on term loan outstanding balances and built a synthetic revolving portfolio script to demonstrate CCF regression methodology.

3. **Do NOT Claim**: "I validated out-of-time performance on 2015 data."  
   *Honest Version*: I performed out-of-time validation on 2014 vintage data, which represents the latest available vintage in the 2007–2014 dataset.

### Six Hostile Questions and Honest Answers

1. **Question**: "Why does your model show a higher Gini on Out-Of-Time data (0.3845) than on Training data (0.3678)?"  
   *Answer*: In [validation_summary.csv:L4-L6](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/outputs/tables/validation_summary.csv#L4-L6), Model B Gini increases from 0.3678 (Train) to 0.3845 (OOT 2014). This occurs because the 2014 vintage has a shorter observation window where default outcomes are concentrated among high-risk sub-grades, making rank-ordering sharper in the early seasoning age.

2. **Question**: "How can you justify using an OLS linear regression for CCF when CCF is bounded between 0 and 1?"  
   *Answer*: In [ccf_demo.py:L135-L140](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/ccf_demo.py#L135-L140), OLS predictions are clipped to $[0.0, 1.0]$. In a production setting with real revolving line data, I would use Fractional Logit regression or Beta regression to handle boundary inflation naturally.

3. **Question**: "Your Hosmer-Lemeshow p-values are near zero for OOT predictions ($3.08 \times 10^{-7}$). Doesn't that mean your model calibration is broken?"  
   *Answer*: Yes. In [validation_summary.csv:L3](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/outputs/tables/validation_summary.csv#L3), the uncalibrated Model A fails the HL test on OOT data due to sample size sensitivity (235,628 rows). Applying intercept recalibration ([calibration.py:L71-L110](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/models/calibration.py#L71-L110)) aligns mean predicted PD to observed default rate, though large-sample chi-square statistics remain sensitive.

4. **Question**: "Why is your mean LGD 93.01%? Isn't that unnaturally high for consumer loans?"  
   *Answer*: In [lgd_distribution_summary.csv:L1](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/outputs/tables/lgd_distribution_summary.csv#L1), 52.18% of defaulted exposures have zero post-default recoveries (`total_rec_prncp` plus `recoveries`), driving median LGD to 1.0. Unsecured consumer loans without physical collateral exhibit very low recovery rates once charged off.

5. **Question**: "How did you determine the 12-month default target when LendingClub doesn't provide a default date?"  
   *Answer*: In [target.py:L50-L140](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/src/creditrisk/data/target.py#L50-L140), default date is inferred by comparing `last_pymnt_d` against `issue_d` for defaulted statuses. If payment date is missing, `last_credit_pull_d` is used as a fallback, and elapsed months are floored at 0.

6. **Question**: "Why did your Basel III Risk Weight reach 125.63%, exceeding the 75% Standardised approach weight?"  
   *Answer*: In [basel_capital_summary.csv:L1](file:///d:/0000_after%20portfolio_25726/2_retail-credit-risk/retail-credit-risk/outputs/tables/basel_capital_summary.csv#L1), Advanced IRB formula applies an average LGD of 93.01% across uncollateralized loans. The high LGD input elevates IRB risk weights above the regulatory 75% standard retail benchmark.
