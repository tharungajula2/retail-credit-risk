# Retail Credit Risk Analytics Suite

> An end-to-end Basel III IRB capital + IFRS 9 / CECL provisioning model built on 466,285 real LendingClub loans (2007–2014), with a PD scorecard, LGD fractional regression, EAD drawdown analysis, interactive dashboard, and an AI credit analyst.

---

## Headline Results

| Metric | Value |
|---|---|
| Portfolio loans (OOT cohort) | 235,628 |
| Total Exposure at Default | **$1,826,572,642** |
| PD Model OOT Gini / AUC | **0.3845 / 0.6923** |
| Portfolio mean LGD | **93.4%** (median 100%) |
| Basel 12m Expected Loss | **$58,666,169** (3.21% of EAD) |
| Basel IRB RWA | **$2,294,666,891** (avg risk weight 125.6%) |
| IFRS 9 ECL (scenario-weighted) | **$285,037,851** (15.61% of EAD) |
| CECL Provision | **$327,465,235** (17.93% of EAD) |

**Three things worth knowing before you read further:**
1. IRB capital is 68% *higher* than the Standardised approach for this book — because 93% LGD means the IRB formula correctly prices what a flat 75% Standardised weight ignores.
2. 52.2% of resolved defaults are total write-offs (LGD = 1.0). The median outcome of an unsecured personal loan default is a complete loss.
3. The PD model OOT Gini (0.3845) *exceeds* its training Gini (0.3678) — the model generalises forward in time without overfitting.

---

## Architecture

```
data/raw/                        <- LendingClub CSV (not tracked in git)
datasets/                        <- Processed datasets for each model stage
        |
        v
src/creditrisk/
  pd/           <- WoE binning, IV screening, logistic regression scorecard
  lgd/          <- Fractional response regression on resolved defaults
  ead/          <- Observed CCF drawdown ratios by term and grade
  capital/      <- Basel III IRB formula (BCBS para 4.4) + Standardised
  ifrs9/        <- 3-stage ECL, 3-scenario weighting, CECL comparison
  reporting/    <- dashboard_data.py (JSON assembly) + build_dashboard.py (HTML)
  ai/           <- RAG index (sentence-transformers), AI analyst (Gemini API)
        |
        v
outputs/
  tables/       <- 35 CSVs — the ground truth for all reported numbers
  reports/      <- dashboard_data.json, risk_dashboard.html
        |
        v
docs/
  MODEL_DOCUMENTATION.md   <- SR 11-7 style model development document
  MANAGEMENT_DECK.md        <- Credit committee presentation (markdown slides)
```

---

## Quickstart

### 1. Setup

```powershell
# Clone the repo and activate the virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

### 2. Run the Pipeline (in order)

```powershell
# Step 1: PD model — trains Model A and Model B, selects B
python src/creditrisk/pd/train.py

# Step 2: LGD model — fractional response regression on resolved defaults
python src/creditrisk/lgd/train.py

# Step 3: EAD — observed CCF drawdown ratios
python src/creditrisk/ead/calculate.py

# Step 4: Basel III capital — IRB + Standardised RWA
python src/creditrisk/capital/calculate.py

# Step 5: IFRS 9 + CECL — staged ECL with scenario weighting
python src/creditrisk/ifrs9/calculate.py

# Step 6: Build dashboard data and HTML report
python src/creditrisk/reporting/dashboard_data.py
python src/creditrisk/reporting/build_dashboard.py
```

### 3. Open the Dashboard

```powershell
# Self-contained HTML — no server needed, works by double-click
Start-Process outputs/reports/risk_dashboard.html
```

The dashboard embeds `dashboard_data.json` directly in the HTML (`<script>const DATA = {...}</script>`), so it works from the local filesystem with no web server.

### 4. Run the AI Analyst

```powershell
# Set your Gemini API key (one time)
$env:GEMINI_API_KEY = "your-api-key-here"

# Build the RAG index (first run only — downloads ~80MB model, then cached)
python src/creditrisk/ai/rag_index.py

# Start the interactive analyst CLI
python src/creditrisk/ai/run_analyst.py
```

The analyst answers two kinds of question:
- **Regulatory:** retrieves from local knowledge-base PDFs using `all-MiniLM-L6-v2` embeddings (fully local, no API for retrieval)
- **Quantitative:** calls Python tools wrapping the Basel capital formula and ECL engine with live portfolio data

### 5. Run Tests

```powershell
pytest tests/ -v
```

---

## Where Outputs Land

| Path | Contents |
|---|---|
| `outputs/tables/` | 35 CSV files — one per model output table (source of truth) |
| `outputs/tables/validation_summary.csv` | AUC, Gini, KS, Brier, HL p-value for all models and samples |
| `outputs/tables/expected_loss_summary.csv` | EL by grade and overall |
| `outputs/tables/basel_capital_summary.csv` | IRB and Standardised RWA by grade |
| `outputs/tables/ecl_summary.csv` | IFRS 9 ECL by stage |
| `outputs/tables/rating_grades_model_b.csv` | 8-grade master scale with score ranges and default rates |
| `outputs/reports/dashboard_data.json` | Single JSON consolidating all tables for the dashboard |
| `outputs/reports/risk_dashboard.html` | Self-contained interactive dashboard |

---

## Project Structure

```
retail-credit-risk/
|-- README.md                          <- This file
|-- pyproject.toml                     <- Package definition
|-- requirements.txt                   <- Dependencies
|-- standing_rules.md                  <- Development conventions
|
|-- config/
|   `-- ai.yaml                        <- AI model config (gemini_model name)
|
|-- data/                              <- Raw data (not tracked)
|-- datasets/                          <- Processed ML-ready datasets
|-- knowledge_base/                    <- Regulatory PDFs for RAG index
|
|-- src/creditrisk/
|   |-- pd/                            <- PD model pipeline
|   |-- lgd/                           <- LGD model pipeline
|   |-- ead/                           <- EAD / CCF pipeline
|   |-- capital/                       <- Basel III capital engine
|   |-- ifrs9/                         <- IFRS 9 / CECL ECL engine
|   |-- reporting/                     <- Dashboard data + HTML builder
|   `-- ai/                            <- RAG index + AI analyst + CLI
|
|-- outputs/
|   |-- tables/                        <- 35 CSV output files
|   |-- reports/                       <- dashboard_data.json, risk_dashboard.html
|   `-- models/                        <- Serialised model artefacts + RAG index
|
|-- tests/                             <- pytest unit tests (8 tests)
|-- docs/
|   |-- MODEL_DOCUMENTATION.md         <- SR 11-7 model development document
|   `-- MANAGEMENT_DECK.md             <- Credit committee presentation
|
`-- notebooks/                         <- Exploratory analysis
```

---

## What Is Real vs Illustrative

| Component | Status | Notes |
|---|---|---|
| PD model (Model B) | **Production-grade** | Trained on 230k+ loans; OOT validated; Gini 0.3845 |
| LGD model | **Production-grade** | Fractional response regression on 50,968 real defaults |
| EAD (observed CCF) | **Production-grade** | Observed drawdown ratios on 50,968 defaulted loans |
| Basel IRB capital | **Production-grade** | BCBS supervisory formula implemented exactly |
| IFRS 9 / CECL ECL | **Production-grade** | 3-stage, 3-scenario; calibrated thresholds |
| CCF regression model | **Illustrative only** | Marked `SYNTHETIC` in output; requires revolving product data |
| SICR threshold | **Illustrative** | 85th percentile PD proxy; bank-specific calibration required |
| AI analyst | **Experimental** | Decision-support only; not for regulatory submissions |
| Downturn LGD add-on | **Illustrative** | +8pp flat add-on; bank would derive from stress cycle data |

> The CCF linear regression in `SYNTHETIC_ccf_summary.csv` is explicitly labelled synthetic. The production EAD estimates throughout the portfolio use **observed drawdown ratios directly**, not the regression model.

---

## Key Model Decisions

**Why Model B over Model A?**  
Model B adds `grade`, `int_rate`, and `sub_grade` to Model A's 7 variables. OOT Gini improves from 0.2715 to 0.3845 (+13 points). OOT AUC exceeds training AUC (0.6923 vs 0.6839) — no overfitting. Hosmer-Lemeshow p-value 0.494 confirms calibration. Both models are documented; no cherry-picking.

**Why a 12-month default target?**  
Aligns with Basel III retail PD horizon and IFRS 9 Stage 1. The `last_pymnt_d` field provides a clean default timing proxy. Longer windows introduce right-censoring for 2013–2014 vintages; shorter windows produce insufficient defaults for early vintages. The 12-month cumulative Kaplan-Meier PD of 3.44% matches the OOT observed default rate exactly.

**Why does IRB RWA exceed Standardised?**  
With mean LGD of 93.4%, the IRB formula's LGD-sensitivity produces risk weights of 94–146% vs the Standardised flat 75%. This is the correct result: unsecured retail with near-total loss in default is genuinely more capital-intensive than secured products.

---

## Documentation

| Document | Description |
|---|---|
| [`docs/MODEL_DOCUMENTATION.md`](docs/MODEL_DOCUMENTATION.md) | Full SR 11-7 model development document — methodology, assumptions, validation, governance |
| [`docs/MANAGEMENT_DECK.md`](docs/MANAGEMENT_DECK.md) | 13-slide credit committee presentation with all key results |
| [`outputs/reports/risk_dashboard.html`](outputs/reports/risk_dashboard.html) | Interactive portfolio dashboard — open in browser |

---

## Dependencies

Core: `pandas`, `numpy`, `scikit-learn`, `statsmodels`, `lifelines`, `scipy`  
AI: `sentence-transformers`, `google-generativeai`, `pypdf`  
Dashboard: Chart.js (CDN — the only external dependency in the HTML)  
Tests: `pytest`

All pinned in `requirements.txt`. Install with `pip install -e .`.

---

*Data source: LendingClub public loan data, Kaggle. All model outputs in `outputs/tables/`. No figures in this README or the documentation are estimated — they are read directly from model output CSVs.*
