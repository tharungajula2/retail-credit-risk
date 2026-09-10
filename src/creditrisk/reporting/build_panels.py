"""
build_panels.py
---------------
Generates the unified standalone master credit risk application:
- docs/index.html (Primary entrypoint for GitHub Pages / URL sharing)
- index.html (Root entrypoint mirror)

Merges Executive Analytics (6 simplified panels) and Pipeline Flow Architecture (12 expandable stages).
"""

import json
import logging
from pathlib import Path
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
TABLES_DIR = PROJECT_ROOT / "outputs" / "tables"
DOCS_HTML_PATH = PROJECT_ROOT / "docs" / "index.html"
ROOT_HTML_PATH = PROJECT_ROOT / "index.html"


def read_csv_safe(file_name: str) -> pd.DataFrame:
    path = TABLES_DIR / file_name
    if not path.exists():
        logger.warning(f"File missing: {path}")
        return pd.DataFrame()
    return pd.read_csv(path)


def main():
    logger.info("Loading output CSV tables for the master application...")

    sample_summary = read_csv_safe("sample_summary.csv")
    target_rec = read_csv_safe("target_reconciliation.csv")
    target_vintage = read_csv_safe("target_summary_by_vintage.csv")
    ead_summary = read_csv_safe("ead_summary.csv")
    basel_summary = read_csv_safe("basel_capital_summary.csv")
    basel_downturn = read_csv_safe("basel_downturn_comparison.csv")
    ifrs9_cecl = read_csv_safe("ifrs9_vs_cecl.csv")
    ifrs9_basel_perf = read_csv_safe("ifrs9_vs_basel_performing.csv")
    default_timing = read_csv_safe("default_timing_distribution.csv")
    lgd_summary = read_csv_safe("lgd_distribution_summary.csv")
    lgd_calib = read_csv_safe("lgd_calibration.csv")
    vintage_curves = read_csv_safe("vintage_curves.csv")
    vintage_maturity = read_csv_safe("vintage_maturity_comparison.csv")
    roll_rate_proxy = read_csv_safe("roll_rate_proxy.csv")
    transition_matrix = read_csv_safe("transition_matrix.csv")
    ecl_summary = read_csv_safe("ecl_summary.csv")
    staging_summary = read_csv_safe("staging_summary.csv")
    lifetime_pd = read_csv_safe("lifetime_pd_term_structure.csv")
    validation_summary = read_csv_safe("validation_summary.csv")
    psi_summary = read_csv_safe("psi_summary.csv")
    csi_summary = read_csv_safe("csi_by_variable.csv")
    scorecard_b = read_csv_safe("scorecard_model_b.csv")
    coefs_b = read_csv_safe("pd_model_b_coefs.csv")
    iv_summary = read_csv_safe("iv_summary.csv")
    rating_grades_b = read_csv_safe("rating_grades_model_b.csv")
    synthetic_ccf = read_csv_safe("SYNTHETIC_ccf_summary.csv")

    data_store = {
        "sample_summary": sample_summary.to_dict(orient="records"),
        "target_rec": target_rec.to_dict(orient="records"),
        "target_vintage": target_vintage.to_dict(orient="records"),
        "ead_summary": ead_summary.to_dict(orient="records"),
        "basel_summary": basel_summary.to_dict(orient="records"),
        "basel_downturn": basel_downturn.to_dict(orient="records"),
        "ifrs9_cecl": ifrs9_cecl.to_dict(orient="records"),
        "ifrs9_basel_perf": ifrs9_basel_perf.to_dict(orient="records"),
        "default_timing": default_timing.to_dict(orient="records"),
        "lgd_summary": lgd_summary.to_dict(orient="records"),
        "lgd_calib": lgd_calib.to_dict(orient="records"),
        "vintage_curves": vintage_curves.to_dict(orient="records"),
        "vintage_maturity": vintage_maturity.to_dict(orient="records"),
        "roll_rate_proxy": roll_rate_proxy.to_dict(orient="records"),
        "transition_matrix": transition_matrix.to_dict(orient="records"),
        "ecl_summary": ecl_summary.to_dict(orient="records"),
        "staging_summary": staging_summary.to_dict(orient="records"),
        "lifetime_pd": lifetime_pd.to_dict(orient="records"),
        "validation_summary": validation_summary.to_dict(orient="records"),
        "psi_summary": psi_summary.to_dict(orient="records"),
        "csi_summary": csi_summary.to_dict(orient="records"),
        "scorecard_b": scorecard_b.to_dict(orient="records"),
        "coefs_b": coefs_b.to_dict(orient="records"),
        "iv_summary": iv_summary.to_dict(orient="records"),
        "rating_grades_b": rating_grades_b.to_dict(orient="records"),
        "synthetic_ccf": synthetic_ccf.to_dict(orient="records"),
    }

    json_str = json.dumps(data_store)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Retail Credit Risk Engine — Executive Suite</title>
    <meta name="description" content="Static single-page interactive credit risk modeling system for LendingClub 466,285 loans (2007-2014). No backend or database required.">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
    <style>
        :root {{
            --bg-dark: #090d16;
            --bg-card: #111827;
            --bg-card-hover: #1f2937;
            --border-color: rgba(255, 255, 255, 0.08);
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
            --text-dim: #6b7280;
            --accent-cyan: #38bdf8;
            --accent-blue: #60a5fa;
            --accent-emerald: #34d399;
            --accent-rose: #fb7185;
            --accent-amber: #fbbf24;
            --accent-purple: #c084fc;
            --font-sans: 'Inter', system-ui, -apple-system, sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
        }}

        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{ background-color: var(--bg-dark); color: var(--text-main); font-family: var(--font-sans); line-height: 1.5; font-size: 14px; min-height: 100vh; }}
        a {{ color: var(--accent-cyan); text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}

        /* TOP NAVIGATION */
        nav.main-mode-tabs {{
            display: flex; align-items: center; justify-content: space-between;
            background: #0f172a; border-bottom: 1px solid var(--border-color);
            padding: 0 24px; height: 60px; position: sticky; top: 0; z-index: 100;
        }}
        .brand {{ display: flex; align-items: center; gap: 12px; font-weight: 700; font-size: 16px; color: #fff; }}
        .brand-badge {{ background: rgba(56, 189, 248, 0.15); color: var(--accent-cyan); padding: 4px 8px; border-radius: 4px; font-size: 11px; font-family: var(--font-mono); text-transform: uppercase; }}
        
        .mode-nav-btns {{ display: flex; gap: 8px; }}
        .mode-tab-btn {{
            background: transparent; border: none; color: var(--text-muted); padding: 8px 16px;
            font-size: 13px; font-weight: 600; border-radius: 6px; cursor: pointer; transition: all 0.2s;
        }}
        .mode-tab-btn:hover {{ background: rgba(255, 255, 255, 0.05); color: #fff; }}
        .mode-tab-btn.active {{ background: rgba(56, 189, 248, 0.15); color: var(--accent-cyan); }}

        .repo-link {{ font-family: var(--font-mono); font-size: 12px; color: var(--text-muted); border: 1px solid var(--border-color); padding: 6px 12px; border-radius: 6px; }}
        .repo-link:hover {{ border-color: var(--accent-cyan); color: #fff; text-decoration: none; }}

        /* SUB NAVIGATION FOR ANALYTICS */
        nav.sub-panel-tabs {{
            display: flex; gap: 6px; padding: 12px 24px; background: #0b1120;
            border-bottom: 1px solid var(--border-color); overflow-x: auto;
        }}
        .sub-tab-btn {{
            background: transparent; border: 1px solid transparent; color: var(--text-muted);
            padding: 6px 14px; font-size: 12px; font-weight: 500; border-radius: 6px; cursor: pointer; white-space: nowrap; transition: all 0.2s;
        }}
        .sub-tab-btn:hover {{ color: var(--text-main); background: rgba(255, 255, 255, 0.04); }}
        .sub-tab-btn.active {{ background: var(--bg-card); color: var(--accent-cyan); border-color: rgba(56, 189, 248, 0.3); font-weight: 600; }}

        /* CONTENT CONTAINERS */
        main {{ padding: 24px; max-width: 1600px; margin: 0 auto; }}
        .mode-section {{ display: none; }}
        .mode-section.active {{ display: block; }}
        .panel {{ display: none; }}
        .panel.active {{ display: block; }}

        /* CARDS & GRIDS */
        .grid-2 {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-bottom: 20px; }}
        .grid-3 {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 20px; }}
        .grid-4 {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 20px; }}
        .grid-2 > *, .grid-3 > *, .grid-4 > * {{ min-width: 0; }}
        @media (max-width: 1024px) {{ .grid-2, .grid-3, .grid-4 {{ grid-template-columns: 1fr; }} }}

        .card {{
            background: var(--bg-card); border: 1px solid var(--border-color);
            border-radius: 10px; padding: 20px; margin-bottom: 20px; min-width: 0; width: 100%;
        }}
        .card-header {{ display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px; }}
        .card-title {{ font-size: 15px; font-weight: 600; color: #fff; display: flex; align-items: center; gap: 8px; }}
        .card-subtitle {{ font-size: 12px; color: var(--text-muted); margin-bottom: 16px; line-height: 1.4; }}

        /* TRUTH BADGES */
        .truth-badge {{
            display: inline-block; font-family: var(--font-mono); font-size: 10px; font-weight: 700;
            padding: 3px 8px; border-radius: 4px; text-transform: uppercase; letter-spacing: 0.5px; margin-left: 8px;
        }}
        .proxy-badge {{ background: rgba(251, 191, 36, 0.15); color: var(--accent-amber); border: 1px solid rgba(251, 191, 36, 0.3); }}
        .synthetic-badge {{ background: rgba(192, 132, 252, 0.15); color: var(--accent-purple); border: 1px solid rgba(192, 132, 252, 0.3); }}
        .fixture-badge {{ background: rgba(251, 113, 133, 0.15); color: var(--accent-rose); border: 1px solid rgba(251, 113, 133, 0.3); }}
        .illustrative-badge {{ background: rgba(56, 189, 248, 0.15); color: var(--accent-cyan); border: 1px solid rgba(56, 189, 248, 0.3); }}

        /* KPI CARDS */
        .kpi-card {{
            background: var(--bg-card); border: 1px solid var(--border-color);
            border-radius: 8px; padding: 16px; display: flex; flex-direction: column; gap: 4px; min-width: 0;
        }}
        .kpi-label {{ font-size: 11px; font-weight: 600; text-transform: uppercase; color: var(--text-dim); letter-spacing: 0.5px; }}
        .kpi-val {{ font-size: 24px; font-weight: 700; color: #fff; font-family: var(--font-mono); }}
        .kpi-sub {{ font-size: 11px; color: var(--text-muted); }}

        /* ONE LINE SUMMARY STRIP */
        .summary-strip {{
            background: #0f172a; border: 1px solid var(--border-color); border-radius: 8px;
            padding: 12px 18px; margin-bottom: 20px; font-family: var(--font-mono); font-size: 12px;
            color: var(--accent-cyan); text-align: center; font-weight: 500;
        }}

        /* SCORECARD STEPPER */
        .scorecard-stepper {{
            display: flex; align-items: center; justify-content: space-between; background: #0f172a;
            border: 1px solid var(--border-color); border-radius: 8px; padding: 12px 20px;
            margin-bottom: 20px; font-family: var(--font-mono); font-size: 12px; overflow-x: auto; gap: 12px;
        }}
        .scorecard-stepper span.step-item {{ color: var(--text-main); font-weight: 600; white-space: nowrap; }}
        .scorecard-stepper span.step-arrow {{ color: var(--accent-cyan); font-weight: 700; }}

        /* TABLES */
        .table-wrapper {{ overflow-x: auto; max-height: 440px; overflow-y: auto; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.05); width: 100%; }}
        table {{ width: 100%; border-collapse: collapse; font-family: var(--font-mono); font-size: 12px; text-align: left; }}
        th {{ background: #0f172a; color: var(--text-muted); padding: 10px 14px; font-weight: 600; border-bottom: 1px solid var(--border-color); position: sticky; top: 0; z-index: 10; white-space: nowrap; }}
        td {{ padding: 10px 14px; border-bottom: 1px solid rgba(255, 255, 255, 0.03); color: var(--text-main); white-space: nowrap; }}
        td.wrap-cell, td:last-child {{ white-space: normal; min-width: 160px; }}
        tr:hover td {{ background: rgba(255, 255, 255, 0.02); }}

        /* CHART CONTAINER */
        .chart-container {{ position: relative; height: 320px; width: 100%; min-width: 0; }}

        /* PIPELINE WORKFLOW */
        .workflow-header {{ margin-bottom: 24px; text-align: center; }}
        .workflow-header h2 {{ font-size: 24px; font-weight: 700; color: #fff; margin-bottom: 8px; }}
        .workflow-header p {{ color: var(--text-muted); max-width: 800px; margin: 0 auto; font-size: 14px; }}

        .workflow-container {{ display: flex; flex-direction: column; gap: 14px; position: relative; max-width: 1200px; margin: 0 auto; }}
        
        .stage-step-card {{
            background: var(--bg-card); border: 1px solid var(--border-color);
            border-radius: 10px; overflow: hidden; transition: all 0.2s ease;
        }}
        .stage-step-card:hover {{ border-color: rgba(56, 189, 248, 0.4); box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4); }}

        .step-summary {{
            padding: 16px 20px; display: flex; align-items: center; justify-content: space-between;
            cursor: pointer; background: #131d31; user-select: none;
        }}
        .step-summary:hover {{ background: #1a2640; }}
        
        .step-left {{ display: flex; align-items: center; gap: 16px; }}
        .step-badge {{
            background: rgba(56, 189, 248, 0.15); color: var(--accent-cyan);
            font-family: var(--font-mono); font-size: 12px; font-weight: 700;
            padding: 6px 10px; border-radius: 6px; border: 1px solid rgba(56, 189, 248, 0.3);
            white-space: nowrap;
        }}
        .step-title-text {{ font-size: 15px; font-weight: 600; color: #fff; }}
        .step-module {{ font-family: var(--font-mono); font-size: 11px; color: var(--text-dim); margin-top: 2px; }}
        
        .step-right {{ display: flex; align-items: center; gap: 16px; }}
        .step-metric-preview {{ font-family: var(--font-mono); font-size: 12px; color: var(--accent-emerald); background: rgba(52, 211, 153, 0.1); padding: 4px 10px; border-radius: 4px; }}
        .chevron {{ color: var(--text-muted); font-weight: 700; transition: transform 0.2s; }}
        .stage-step-card.open .chevron {{ transform: rotate(180deg); color: var(--accent-cyan); }}

        .step-details {{
            display: none; padding: 20px; border-top: 1px solid var(--border-color);
            background: #0f172a; grid-template-columns: repeat(2, 1fr); gap: 16px;
        }}
        .stage-step-card.open .step-details {{ display: grid; }}
        @media (max-width: 768px) {{ .step-details {{ grid-template-columns: 1fr; }} }}

        .detail-block {{ background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 6px; padding: 12px 14px; }}
        .detail-label {{ font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; font-family: var(--font-mono); }}
        .detail-label.input-lbl {{ color: var(--accent-blue); }}
        .detail-label.happens-lbl {{ color: var(--accent-cyan); }}
        .detail-label.why-lbl {{ color: var(--accent-amber); }}
        .detail-label.output-lbl {{ color: var(--accent-emerald); }}

        .detail-val {{ font-size: 12px; line-height: 1.5; color: var(--text-main); }}

        .flow-connector {{ text-align: center; color: var(--accent-cyan); opacity: 0.5; font-size: 16px; margin: -6px 0; }}

        /* IMPLEMENTATION BOUNDARY STRIP AT BOTTOM */
        .boundary-strip {{
            background: #0b1120; border: 1px solid var(--border-color); border-radius: 8px;
            padding: 16px 20px; margin-top: 30px; font-size: 12px; color: var(--text-muted);
            display: flex; flex-wrap: wrap; gap: 16px; justify-content: space-between; align-items: center;
        }}
        .boundary-item {{ display: flex; align-items: center; gap: 8px; }}
        .boundary-item strong {{ color: #fff; }}
    </style>
</head>
<body>

    <!-- MAIN NAVIGATION TABS -->
    <nav class="main-mode-tabs">
        <div class="brand">
            <span>RETAIL CREDIT RISK ENGINE</span>
            <span class="brand-badge">BASEL III & IFRS 9 / CECL</span>
        </div>
        <div class="mode-nav-btns">
            <button class="mode-tab-btn active" id="tab-analytics" onclick="switchMode('analytics')">Executive Analytics</button>
            <button class="mode-tab-btn" id="tab-pipeline" onclick="switchMode('pipeline')">Pipeline Architecture</button>
        </div>
        <a href="https://github.com/tharungajula2/retail-credit-risk" target="_blank" class="repo-link">GitHub Repository ↗</a>
    </nav>

    <!-- MODE 1: EXECUTIVE ANALYTICS -->
    <div id="mode-analytics" class="mode-section active">
        <nav class="sub-panel-tabs">
            <button class="sub-tab-btn active" onclick="showPanel(0)">1. Portfolio & Capital</button>
            <button class="sub-tab-btn" onclick="showPanel(1)">2. Vintage Analysis</button>
            <button class="sub-tab-btn" onclick="showPanel(2)">3. Delinquency</button>
            <button class="sub-tab-btn" onclick="showPanel(3)">4. ECL & Lifetime PD</button>
            <button class="sub-tab-btn" onclick="showPanel(4)">5. Validation</button>
            <button class="sub-tab-btn" onclick="showPanel(5)">6. Scorecard</button>
        </nav>

        <main>
            <!-- PANEL 0: PORTFOLIO & CAPITAL -->
            <div class="panel active" id="panel-0">
                <div class="grid-4">
                    <div class="kpi-card">
                        <div class="kpi-label">2014 OOT Exposure (EAD)</div>
                        <div class="kpi-val">$1.827B</div>
                        <div class="kpi-sub">235,628 loans in 2014 Out-of-Time cohort</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-label">IFRS 9 Staged ECL</div>
                        <div class="kpi-val">$278.48M</div>
                        <div class="kpi-sub">15.25% overall portfolio coverage ratio</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-label">US CECL Provision</div>
                        <div class="kpi-val">$327.47M</div>
                        <div class="kpi-sub">+$48.99M (+17.6%) vs IFRS 9 (Day-1 Lifetime)</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-label">Basel IRB Risk-Weighted Assets</div>
                        <div class="kpi-val">$2.295B</div>
                        <div class="kpi-sub">125.63% avg Risk Weight ($183.6M capital @ 8%)</div>
                    </div>
                </div>

                <div class="summary-strip">
                    466,285 LendingClub loans → PD / LGD / EAD → validation → IFRS 9 / CECL / Basel III → monitoring and reporting
                </div>

                <div class="grid-2">
                    <div class="card">
                        <div class="card-header">
                            <span class="card-title">Basel III IRB vs Standardised Capital RWA Comparison</span>
                        </div>
                        <div class="card-subtitle">
                            Quantifies regulatory capital surcharges under Advanced IRB (BCBS para 4.4) driven by 93.01% mean LGD penalty vs flat 75% Standardised risk weight across rating grades.
                        </div>
                        <div class="table-wrapper">
                            <table id="t-basel">
                                <thead><tr><th>Rating Grade / Segment</th><th>Loan Count</th><th>Total EAD ($)</th><th>IRB RWA ($)</th><th>Std RWA ($)</th><th>IRB Risk Weight (%)</th></tr></thead>
                                <tbody></tbody>
                            </table>
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-header">
                            <span class="card-title">IFRS 9 vs US CECL Lifetime Provisioning Comparison <span class="truth-badge illustrative-badge">ILLUSTRATIVE SCENARIO ASSUMPTIONS</span></span>
                        </div>
                        <div class="card-subtitle">
                            Compares 12-month regulatory EL ($58.67M), staged IFRS 9 ECL ($278.48M), and Day-1 lifetime US CECL ($327.47M). Illustrative scenario weights: 50% Baseline / 20% Upside / 30% Downside (demonstrated on 3-loan fixture).
                        </div>
                        <div class="table-wrapper">
                            <table id="t-cecl">
                                <thead><tr><th>Accounting Framework</th><th>Total EAD ($)</th><th>Total Provision ($)</th><th>Coverage %</th><th>Horizon & Scope Notes</th></tr></thead>
                                <tbody></tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>

            <!-- PANEL 1: VINTAGE ANALYSIS -->
            <div class="panel" id="panel-1">
                <div class="card">
                    <div class="card-header">
                        <span class="card-title">Cumulative Default Curves by Origination Vintage (MOB 0 to 24)</span>
                    </div>
                    <div class="card-subtitle">
                        Months-On-Book (MOB) measures loan age so origination cohorts (2007–2014) can be evaluated at equivalent maturity milestones across macroeconomic cycles.
                    </div>
                    <div class="chart-container">
                        <canvas id="c-vintage"></canvas>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <span class="card-title">Fixed Months-on-Book Vintage Maturity Comparison</span>
                    </div>
                    <div class="card-subtitle">
                        Compares cumulative Probability of Default (PD) rates at fixed maturity milestones (MOB 12, 18, 24) across vintages to eliminate seasoning bias.
                    </div>
                    <div class="table-wrapper">
                        <table id="t-vintage-mat">
                            <thead><tr><th>Origination Vintage</th><th>Total Loans</th><th>MOB 12 Default Rate (%)</th><th>MOB 18 Default Rate (%)</th><th>MOB 24 Default Rate (%)</th></tr></thead>
                            <tbody></tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- PANEL 2: DELINQUENCY -->
            <div class="panel" id="panel-2">
                <div class="card">
                    <div class="card-header">
                        <span class="card-title">Delinquency Status Distribution by Vintage Year <span class="truth-badge proxy-badge">CROSS-SECTIONAL PROXY — NOT MONTHLY PANEL DATA</span></span>
                    </div>
                    <div class="card-subtitle">
                        Cross-sectional breakdown of portfolio loan status across origination cohorts. Displays current status proportions and cumulative resolution outcomes.
                    </div>
                    <div class="table-wrapper">
                        <table id="t-rollrate">
                            <thead><tr><th>Vintage Year</th><th>Total Loans</th><th>Current (%)</th><th>Grace Period (%)</th><th>Late 16-30 DPD (%)</th><th>Late 31-120 DPD (%)</th><th>Default / Charged-Off (%)</th><th>Fully Paid (%)</th></tr></thead>
                            <tbody></tbody>
                        </table>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <span class="card-title">Origination Rating Grade Outcome Distribution <span class="truth-badge fixture-badge">2-LOAN FIXTURE DEMONSTRATION</span></span>
                    </div>
                    <div class="card-subtitle">
                        Demonstration outcome matrix illustrating grade migration tracking logic on sample data fixture.
                    </div>
                    <div class="table-wrapper">
                        <table id="t-trans">
                            <thead><tr><th>Rating Grade</th><th>Total Loans</th><th>Fully Paid (%)</th><th>Current (%)</th><th>Late (%)</th><th>Default (%)</th></tr></thead>
                            <tbody></tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- PANEL 3: ECL & LIFETIME PD -->
            <div class="panel" id="panel-3">
                <div class="grid-3" style="margin-bottom: 20px;">
                    <div class="kpi-card">
                        <div class="kpi-label">Stage 1 (Performing)</div>
                        <div class="kpi-val">189,633</div>
                        <div class="kpi-sub">80.48% count ($1.417B EAD, $30.27M 12m ECL)</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-label">Stage 2 (SICR)</div>
                        <div class="kpi-val">26,554</div>
                        <div class="kpi-sub">11.27% count ($169.37M EAD, $24.40M Lifetime ECL)</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-label">Stage 3 (Credit-Impaired)</div>
                        <div class="kpi-val">19,441</div>
                        <div class="kpi-sub">8.25% count ($240.00M EAD, $223.80M Lifetime ECL)</div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <span class="card-title">IFRS 9 Portfolio Staging Breakdown</span>
                    </div>
                    <div class="card-subtitle">
                        Classifies portfolio into Stage 1 (12m ECL), Stage 2 (Lifetime ECL after SICR: relative PD ratio ≥ 2.0x, current 12m PD > 6.0%, or 30+ DPD), and Stage 3 (Credit-Impaired / Default).
                    </div>
                    <div class="table-wrapper">
                        <table id="t-staging">
                            <thead><tr><th>IFRS 9 Stage</th><th>Loan Count</th><th>Total EAD ($)</th><th>Total ECL Provision ($)</th><th>Coverage Ratio (%)</th></tr></thead>
                            <tbody></tbody>
                        </table>
                    </div>
                </div>

                <div class="grid-2">
                    <div class="card">
                        <div class="card-header">
                            <span class="card-title">Performing Book (Stage 1 + 2) IFRS 9 ECL vs Basel EL</span>
                        </div>
                        <div class="card-subtitle">
                            Compares 12m regulatory EL ($48.47M, 3.05% coverage) vs staged performing ECL ($54.68M, 3.45% coverage) on 216,187 performing loans ($1.587B EAD).
                        </div>
                        <div class="table-wrapper">
                            <table id="t-perf">
                                <thead><tr><th>Regulatory / Accounting Scope</th><th>Performing EAD ($)</th><th>Total Provision ($)</th><th>Coverage %</th><th>Description</th></tr></thead>
                                <tbody></tbody>
                            </table>
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-header">
                            <span class="card-title">60-Month Discrete-Time Portfolio Lifetime PD Hazard Curve</span>
                        </div>
                        <div class="card-subtitle">
                            Plots marginal monthly hazard rates (peaking at Month 14 @ 0.63%) and cumulative lifetime PD (10.93% at Month 60).
                        </div>
                        <div class="chart-container">
                            <canvas id="c-lifetime"></canvas>
                        </div>
                    </div>
                </div>
            </div>

            <!-- PANEL 4: VALIDATION -->
            <div class="panel" id="panel-4">
                <div class="grid-4" style="margin-bottom: 20px;">
                    <div class="kpi-card">
                        <div class="kpi-label">2014 OOT AUROC</div>
                        <div class="kpi-val">0.692</div>
                        <div class="kpi-sub">Model B Out-of-Time discrimination</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-label">2014 OOT Gini</div>
                        <div class="kpi-val">0.385</div>
                        <div class="kpi-sub">+11.3 Gini points lift over Model A (0.271)</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-label">2014 OOT KS Stat</div>
                        <div class="kpi-val">28.43%</div>
                        <div class="kpi-sub">Maximum cumulative default separation</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-label">Score PSI</div>
                        <div class="kpi-val">0.0071</div>
                        <div class="kpi-sub">Population Stability Index (Project target &lt; 0.10)</div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <span class="card-title">Master Model Validation Summary</span>
                    </div>
                    <div class="card-subtitle">
                        Evaluates discrimination (AUROC, Gini, KS) and decile calibration (Brier score, Hosmer-Lemeshow p-value) for Model A (7 WoE baseline) and Model B across Train (2007–2013), Test, and 2014 OOT.
                    </div>
                    <div class="table-wrapper">
                        <table id="t-val">
                            <thead><tr><th>Model Name</th><th>Sample Partition</th><th>AUROC</th><th>Gini Coefficient</th><th>KS Statistic</th><th>Brier Score</th><th>HL Test p-value</th></tr></thead>
                            <tbody></tbody>
                        </table>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <span class="card-title">Feature Characteristic Stability Index (CSI)</span>
                    </div>
                    <div class="card-subtitle">
                        Monitors characteristic stability across individual scorecard variables between training and 2014 OOT production cohorts (Project target CSI &lt; 0.10).
                    </div>
                    <div class="table-wrapper">
                        <table id="t-csi">
                            <thead><tr><th>Model Name</th><th>Variable Name</th><th>CSI Value</th><th>Stability Assessment Band</th></tr></thead>
                            <tbody></tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- PANEL 5: SCORECARD -->
            <div class="panel" id="panel-5">
                <div class="scorecard-stepper">
                    <span class="step-item">1. Raw Borrower Attributes</span>
                    <span class="step-arrow">→</span>
                    <span class="step-item">2. WoE Monotonic Binning</span>
                    <span class="step-arrow">→</span>
                    <span class="step-item">3. Logistic Regression</span>
                    <span class="step-arrow">→</span>
                    <span class="step-item">4. Integer Scaling (PDO=20, Base 600 @ 50:1)</span>
                    <span class="step-arrow">→</span>
                    <span class="step-item">5. 8 Master Rating Grades</span>
                </div>

                <div class="card" style="background: #0f172a;">
                    <div class="card-header">
                        <span class="card-title">Model Architecture Comparison: Model A vs Model B</span>
                    </div>
                    <div class="card-subtitle" style="margin-bottom: 0;">
                        <strong>Model A:</strong> Fits 7 borrower-fundamental features (dti, purpose, term, revol_util, home_ownership, inq_last_6mths, annual_inc) achieving 0.271 OOT Gini.<br>
                        <strong>Model B:</strong> Adds LendingClub risk pricing variables (grade, sub_grade, int_rate) raising OOT Gini to 0.385 (+11.3 Gini points lift).
                    </div>
                </div>

                <div class="grid-2">
                    <div class="card">
                        <div class="card-header">
                            <span class="card-title">Information Value (IV) Ranking (Top 15 Features)</span>
                        </div>
                        <div class="card-subtitle">
                            Quantifies predictive strength per candidate variable from outputs/tables/iv_summary.csv. Top predictors: grade (IV 0.2937) and int_rate (IV 0.2772).
                        </div>
                        <div class="chart-container">
                            <canvas id="c-iv"></canvas>
                        </div>
                    </div>

                    <div class="card">
                        <div class="card-header">
                            <span class="card-title">Logistic Regression Model B Coefficients</span>
                        </div>
                        <div class="card-subtitle">
                            Estimated log-odds coefficients, standard errors, and p-values. Note: sub_grade (p=0.088) and term (p=0.853) are not statistically significant at α = 0.05.
                        </div>
                        <div class="table-wrapper">
                            <table id="t-coefs">
                                <thead><tr><th>Scorecard Feature</th><th>Coefficient (&beta;)</th><th>Std Error</th><th>p-value</th><th>Statistical Significance</th></tr></thead>
                                <tbody></tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <span class="card-title">Rating Master Scale Calibration (Grades 1 to 8)</span>
                    </div>
                    <div class="card-subtitle">
                        Maps integer score ranges (522 to 639) into 8 master rating grades under Points-to-Double-Odds (PDO = 20, Base Score 600 at 50:1 odds). Default rates increase monotonically from 0.86% to 7.72%.
                    </div>
                    <div class="table-wrapper">
                        <table id="t-grades">
                            <thead><tr><th>Master Rating Grade</th><th>Scorecard Point Range</th><th>Loan Count</th><th>Observed Default Rate (%)</th></tr></thead>
                            <tbody></tbody>
                        </table>
                    </div>
                </div>
            </div>

            <!-- IMPLEMENTATION BOUNDARY STRIP -->
            <div class="boundary-strip">
                <div class="boundary-item"><strong>FULL DATA:</strong> PD / LGD / EAD / validation / staging / capital / monitoring (2007–2014 LendingClub)</div>
                <div class="boundary-item"><span class="truth-badge proxy-badge">PROXY:</span> Delinquency vintage status</div>
                <div class="boundary-item"><span class="truth-badge synthetic-badge">SYNTHETIC:</span> Revolving CCF (5k accounts)</div>
                <div class="boundary-item"><span class="truth-badge fixture-badge">FIXTURE:</span> Macro ECL (3-loan test fixture)</div>
                <div class="boundary-item"><span class="truth-badge illustrative-badge">INTEGRATED:</span> Gemini LLM API (when configured)</div>
            </div>
        </main>
    </div>

    <!-- MODE 2: PIPELINE ARCHITECTURE WORKFLOW -->
    <div id="mode-pipeline" class="mode-section">
        <main>
            <div class="workflow-header">
                <h2>End-to-End Credit Risk Pipeline Architecture</h2>
                <p>An interactive, 12-stage sequential walkthrough illustrating how 466,285 raw LendingClub loans are ingested, audited, binned, modeled, scaled into scorecards, extended into LGD/EAD, and combined into Basel III IRB capital &amp; IFRS 9 / US CECL accounting provisions.</p>
            </div>

            <div class="workflow-container" id="workflow-steps">
                <!-- Dynamic 12 Expandable Steps generated via JS -->
            </div>
        </main>
    </div>

    <script>
        const DATA = {json_str};
        const REPO_BASE = "https://github.com/tharungajula2/retail-credit-risk/blob/main/";

        const PIPELINE_STAGES = [
            {{
                step: 1,
                title: "Raw Data Ingestion & Data Inventory Audit",
                module: "src/creditrisk/data/inspect_raw.py",
                preview: "466,285 raw loans → 75 attributes",
                input: "466,285 raw LendingClub loan origination records (2007–2014) in datasets/loan_data_2007_2014.csv with 75 initial attributes.",
                happens: "Reads raw CSV data in 50,000-row memory-safe chunks to prevent system RAM spikes. Audits missing data rates, validates schema data types, checks issue date boundaries (2007–2014), and logs field cardinality.",
                why: "Raw borrower datasets contain missing values, inconsistent formats, and unformatted dates. Rigorous initial inventory auditing prevents data corruption from propagating downstream into credit scorecards.",
                output: "outputs/reports/data_inventory.txt (466,285 valid loan rows logged, 15 attributes identified with 100% missing values)."
            }},
            {{
                step: 2,
                title: "Schema Hygiene & Target Anti-Leakage Guardrails",
                module: "src/creditrisk/data/schema.py",
                preview: "assert_no_leakage active",
                input: "466,285 loan records containing 75 raw candidate fields.",
                happens: "Strips out post-origination outcome attributes (such as recoveries, total_rec_prncp, last_pymnt_d, collection_recovery_fee). Enforces programmatic assertions (assert_no_leakage) ensuring only application-time features enter models.",
                why: "SR 11-7 model governance rules strictly prohibit using future post-origination performance data to predict origination credit risk, which would cause severe forward-looking target leakage.",
                output: "Clean PD-eligible feature set of 50 pre-origination candidate attributes."
            }},
            {{
                step: 3,
                title: "Default Target Construction & Performance Window",
                module: "src/creditrisk/data/target.py",
                preview: "50,968 ever-default (10.93%) → 16,018 12m default (3.44%)",
                input: "466,285 clean loan records.",
                happens: "Constructs the binary default flag ever_default (10.93%, 50,968 loans) based on charge-off status. Infers default timing using last_pymnt_d + 3 months DPD lag and creates a 12-month performance window target default_12m (3.44%, 16,018 loans).",
                why: "Basel III (BCBS para 447) and IFRS 9 Stage 1 require a standardized 12-month observation horizon for point-in-time Probability of Default (PD) estimation.",
                output: "outputs/tables/target_reconciliation.csv (466,285 total loans → 50,968 ever-defaults → 16,018 12-month defaults)."
            }},
            {{
                step: 4,
                title: "Stratified Train / Test & Out-of-Time (OOT) Temporal Splitting",
                module: "src/creditrisk/data/sampling.py",
                preview: "Train: 184.5k | Test: 46.1k | OOT (2014): 235.6k",
                input: "466,285 labeled loan records spanning origination vintages 2007 through 2014.",
                happens: "Partitions the historical development cohort (2007–2013, 230,657 loans) into an 80/20 stratified Train (184,525 loans) and Test (46,132 loans) split. Holds out the entire 2014 origination vintage (235,628 loans) as a true Out-of-Time (OOT) validation cohort.",
                why: "Validates model stability across macroeconomic cycles and prevents overfitting by testing on future vintages not seen during model estimation.",
                output: "outputs/tables/sample_summary.csv (Train: 184,525 | Test: 46,132 | OOT: 235,628 loans)."
            }},
            {{
                step: 5,
                title: "Weight of Evidence (WoE) Classing & Information Value (IV) Screening",
                module: "src/creditrisk/features/run_binning.py",
                preview: "Top IVs: grade (0.294), int_rate (0.277)",
                input: "184,525 training records with continuous and categorical candidate features.",
                happens: "Bins continuous attributes into monotonic WoE categories with Laplace smoothing, isolating missing values into distinct risk categories. Calculates Information Value (IV) to rank predictive strength and screens out weak variables.",
                why: "Credit risk features (like debt-to-income or interest rate) have non-linear risk profiles; WoE transformation forces linear log-odds scaling for logistic regression while enforcing IV governance screening (IV between 0.02 and 0.50).",
                output: "outputs/tables/iv_summary.csv (Top features: grade IV=0.294, int_rate IV=0.277, inq_last_6mths IV=0.076)."
            }},
            {{
                step: 6,
                title: "Scorecard Model Estimation, PDO Scaling & Master Scale Alignment",
                module: "src/creditrisk/models/run_pd_model.py",
                preview: "8 Rating Grades | Scores 522-639",
                input: "WoE-transformed training dataset with screened risk features.",
                happens: "Fits Logistic Regression Model A (baseline) and Model B (incorporating grade/rate pricing). Scales WoE coefficients into a 600-point Points-to-Double-Odds (PDO=20) integer scorecard and maps scores (522–639) into 8 master rating grades.",
                why: "Bank underwriting engines require integer points for automated credit decisioning, while risk management requires discrete rating grades (1–8) to standardize pricing, provisioning, and capital allocation.",
                output: "outputs/tables/scorecard_model_b.csv & outputs/tables/rating_grades_model_b.csv (8 rating grades with monotonic default rates from 0.86% to 7.72%)."
            }},
            {{
                step: 7,
                title: "Two-Stage Hurdle LGD & Realized EAD Drawdown Analytics",
                module: "src/creditrisk/models/run_lgd_training.py",
                preview: "Mean LGD: 93.01% | Median LGD: 100.0%",
                input: "50,968 resolved defaulted loan records.",
                happens: "Fits a Two-Stage Hurdle LGD Model (Stage 1 Logistic Classifier for recovery incidence P(recovery > 0) + Stage 2 GradientBoostingRegressor for recovery magnitude given recovery > 0) to handle the 52.18% zero-recovery write-off spike. Computes EAD drawdowns.",
                why: "Unsecured personal loans carry zero collateral, resulting in severe bimodality (52.18% zero recovery, mean LGD 93.01%). Two-stage hurdle architecture models recovery incidence separately from conditional magnitude.",
                output: "outputs/tables/lgd_calibration.csv & outputs/tables/ead_summary.csv (Mean LGD 93.01%, median LGD 100.0%, 52.18% total loss)."
            }},
            {{
                step: 8,
                title: "Regulatory Layer (Basel III IRB Capital & IFRS 9 / US CECL Provisions)",
                module: "src/creditrisk/regulatory/run_staging.py",
                preview: "ECL: $278.48M (15.25%) | IRB RWA: $2.295B (125.63%)",
                input: "Model predictions (PD, LGD, EAD) for the 2014 OOT portfolio cohort (235,628 loans).",
                happens: "Computes IFRS 9 3-Stage Expected Credit Loss (ECL) across illustrative weighted macroeconomic scenarios (50% Base, 20% Upside, 30% Downside, demonstrated on 3-loan fixture) and compares against US CECL lifetime provisions. Calculates Basel III IRB Risk-Weighted Assets (RWA) via BCBS para 4.4 formula.",
                why: "Basel III regulatory capital ensures bank solvency during extreme economic crises, while IFRS 9 and US CECL accounting standards mandate balance sheet credit loss provisioning.",
                output: "outputs/tables/ecl_summary.csv ($278.48M IFRS 9 ECL) & outputs/tables/basel_capital_summary.csv ($2.295B IRB RWA, $183.6M regulatory capital @ 8%)."
            }},
            {{
                step: 9,
                title: "Comprehensive Model Validation Battery (Discrimination & Calibration)",
                module: "src/creditrisk/validation/run_validation.py",
                preview: "2014 OOT Gini: 0.385 | AUC: 0.692 | KS: 28.43%",
                input: "Fitted PD Model predictions across Train, Test, and 2014 OOT cohorts.",
                happens: "Evaluates rank-ordering discrimination power (AUROC, Gini coefficient, KS statistic) and decile calibration accuracy (Brier score, Hosmer-Lemeshow chi-square test across deciles).",
                why: "Model validation rules mandate performance tracking (Model B OOT Gini 0.385 vs Model A 0.271) before scorecards can be used in live credit decisioning.",
                output: "outputs/tables/validation_summary.csv (Model B OOT Gini: 0.3845, AUC: 0.6923, KS: 0.2843, Brier: 0.03268)."
            }},
            {{
                step: 10,
                title: "Portfolio Monitoring, Stability Index (PSI/CSI) & Vintage Seasoning",
                module: "src/creditrisk/monitoring/run_transitions.py",
                preview: "Score PSI: 0.0071 (Stable) | 8 Vintages",
                input: "OOT prediction distributions, feature values, and historical vintage cohorts (2007–2014).",
                happens: "Calculates Population Stability Index (PSI = 0.0071) and Characteristic Stability Index (CSI) to detect population drift between development and production cohorts. Constructs Months-On-Book (MOB 0–24) cumulative default curves across origination vintages.",
                why: "Monitors whether underwriting quality degrades or population demographics shift over time (Project target PSI < 0.10 indicates high stability).",
                output: "outputs/tables/psi_summary.csv (Score PSI = 0.0071, stable) & outputs/tables/vintage_curves.csv (8 vintage curves, 2007–2014)."
            }},
            {{
                step: 11,
                title: "Master Interactive Reporting Suite & Single-File Application Deployment",
                module: "src/creditrisk/reporting/build_panels.py",
                preview: "docs/index.html & index.html generated",
                input: "35 ground-truth summary CSV tables in outputs/tables/.",
                happens: "Consolidates model outputs into a unified JSON data store and injects it into a single-file, interactive static HTML application (index.html & docs/index.html) with Chart.js visualizations.",
                why: "Provides executive management, regulators, and model validation teams an instant, interactive portal to inspect portfolio risk, capital adequacy, and model metrics without needing backend servers.",
                output: "docs/index.html & index.html (100% static single-page web application)."
            }},
            {{
                step: 12,
                title: "RAG AI Credit Analyst & Local Embedding Retrieval Engine",
                module: "src/creditrisk/ai/rag_index.py",
                preview: "sentence-transformers/all-MiniLM-L6-v2 (384-d)",
                input: "Regulatory PDFs, documentation chunks, local MiniLM-L6-v2 embeddings, and Python execution tools.",
                happens: "Embeds credit risk documentation into 384-dimensional local vectors using sentence-transformers and performs cosine similarity retrieval. Connects Gemini LLM agent for natural language querying when configured (with local retrieval and offline fallback).",
                why: "Allows credit executives and auditors to query complex IRB capital, IFRS 9 staging, and scorecard mechanics using natural language.",
                output: "src/creditrisk/ai/rag_index.py (384-d local MiniLM vector search + Gemini tool integration)."
            }}
        ];

        /* MODE SWITCHING */
        function switchMode(mode) {{
            document.querySelectorAll('.mode-tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.mode-section').forEach(s => s.classList.remove('active'));

            document.getElementById('tab-' + mode).classList.add('active');
            document.getElementById('mode-' + mode).classList.add('active');

            if (mode === 'pipeline') {{
                renderWorkflow();
            }}

            window.location.hash = mode;
        }}

        function showPanel(idx) {{
            document.querySelectorAll('.sub-tab-btn').forEach((b, i) => {{
                b.classList.toggle('active', i === idx);
            }});
            document.querySelectorAll('.panel').forEach((p, i) => {{
                p.classList.toggle('active', i === idx);
            }});
            window.location.hash = 'analytics-p' + idx;
        }}

        /* POPULATE ANALYTICS TABLES WITH CORRECT DATA BINDINGS */
        function populateTables() {{
            // 1. Basel Capital Table (#t-basel)
            const bBody = document.querySelector('#t-basel tbody');
            if (bBody && DATA.basel_summary) {{
                bBody.innerHTML = DATA.basel_summary.map(r => {{
                    const segLabel = (r.segment === 'By Grade' || r.segment === 'Grade') ? `Grade ${{r.category}}` : 'Portfolio Overall';
                    return `
                        <tr>
                            <td><strong>${{segLabel}}</strong></td>
                            <td>${{(r.count || 0).toLocaleString()}}</td>
                            <td>$${{((r.total_ead || 0)/1e6).toFixed(2)}}M</td>
                            <td>$${{((r.irb_rwa || 0)/1e6).toFixed(2)}}M</td>
                            <td>$${{((r.std_rwa || 0)/1e6).toFixed(2)}}M</td>
                            <td><strong style="color:var(--accent-blue);">${{(r.irb_rw_pct || 0).toFixed(1)}}%</strong></td>
                        </tr>
                    `;
                }}).join('');
            }}

            // 2. CECL Table (#t-cecl)
            const cBody = document.querySelector('#t-cecl tbody');
            if (cBody && DATA.ifrs9_cecl) {{
                const portfolioEAD = 1826572642.48; // Total EAD $1,826.57M
                cBody.innerHTML = DATA.ifrs9_cecl.map(r => {{
                    const prov = r.total_provision_usd || 0;
                    const covPct = r.coverage_pct_ead !== undefined ? r.coverage_pct_ead : (prov / portfolioEAD * 100);
                    return `
                        <tr>
                            <td><strong>${{r.accounting_framework}}</strong></td>
                            <td>$${{(portfolioEAD/1e6).toFixed(2)}}M</td>
                            <td>$${{(prov/1e6).toFixed(2)}}M</td>
                            <td><strong style="color:var(--accent-cyan);">${{covPct.toFixed(2)}}%</strong></td>
                            <td>${{r.notes || r.horizon_scope || ''}}</td>
                        </tr>
                    `;
                }}).join('');
            }}

            // 3. Vintage Maturity Table (#t-vintage-mat)
            const vmBody = document.querySelector('#t-vintage-mat tbody');
            if (vmBody && DATA.vintage_maturity) {{
                vmBody.innerHTML = DATA.vintage_maturity.map(r => {{
                    const mob12 = r.default_rate_mob_12_pct !== undefined ? r.default_rate_mob_12_pct : (r.default_rate_mob_12 * 100);
                    const mob18 = r.default_rate_mob_18_pct !== undefined ? r.default_rate_mob_18_pct : (r.default_rate_mob_18 * 100);
                    const mob24 = r.default_rate_mob_24_pct !== undefined ? r.default_rate_mob_24_pct : (r.default_rate_mob_24 * 100);
                    return `
                        <tr>
                            <td><strong>Vintage ${{r.vintage_year}}</strong></td>
                            <td>${{(r.total_loans || 0).toLocaleString()}}</td>
                            <td>${{mob12.toFixed(2)}}%</td>
                            <td>${{mob18.toFixed(2)}}%</td>
                            <td><strong style="color:var(--accent-rose);">${{mob24.toFixed(2)}}%</strong></td>
                        </tr>
                    `;
                }}).join('');
            }}

            // 4. Roll Rate Proxy Table (#t-rollrate)
            const rrBody = document.querySelector('#t-rollrate tbody');
            if (rrBody && DATA.roll_rate_proxy) {{
                rrBody.innerHTML = DATA.roll_rate_proxy.map(r => `
                    <tr>
                        <td><strong>Vintage ${{r.vintage_year}}</strong></td>
                        <td>${{(r.total_loans || 0).toLocaleString()}}</td>
                        <td>${{(r.current_pct || 0).toFixed(1)}}%</td>
                        <td>${{(r.grace_period_pct || 0).toFixed(1)}}%</td>
                        <td>${{(r.late_16_30_pct || 0).toFixed(1)}}%</td>
                        <td>${{(r.late_31_120_pct || 0).toFixed(1)}}%</td>
                        <td><strong style="color:var(--accent-rose);">${{(r.default_charged_off_pct || 0).toFixed(1)}}%</strong></td>
                        <td>${{(r.fully_paid_pct || 0).toFixed(1)}}%</td>
                    </tr>
                `).join('');
            }}

            // 5. Transition Matrix Table (#t-trans)
            const trBody = document.querySelector('#t-trans tbody');
            if (trBody && DATA.transition_matrix) {{
                trBody.innerHTML = DATA.transition_matrix.map(r => `
                    <tr>
                        <td><strong>Grade ${{r.grade}}</strong></td>
                        <td>${{(r.total_loans || 0).toLocaleString()}}</td>
                        <td>${{((r['Fully Paid'] || 0)*100).toFixed(1)}}%</td>
                        <td>${{((r['Current'] || 0)*100).toFixed(1)}}%</td>
                        <td>${{((r['Late'] || 0)*100).toFixed(1)}}%</td>
                        <td><strong style="color:var(--accent-rose);">${{((r['Default'] || 0)*100).toFixed(1)}}%</strong></td>
                    </tr>
                `).join('');
            }}

            // 6. Staging Summary Table (#t-staging)
            const stBody = document.querySelector('#t-staging tbody');
            const stagingData = (DATA.ecl_summary && DATA.ecl_summary.length > 0) ? DATA.ecl_summary : DATA.staging_summary;
            if (stBody && stagingData) {{
                stBody.innerHTML = stagingData.map(r => `
                    <tr>
                        <td><strong>${{r.stage}}</strong></td>
                        <td>${{(r.count || 0).toLocaleString()}}</td>
                        <td>$${{((r.total_ead || 0)/1e6).toFixed(2)}}M</td>
                        <td>$${{((r.total_ecl || 0)/1e6).toFixed(2)}}M</td>
                        <td><strong style="color:var(--accent-cyan);">${{(r.ecl_pct_ead || r.coverage_pct || (r.coverage_ratio*100) || 0).toFixed(2)}}%</strong></td>
                    </tr>
                `).join('');
            }}

            // 7. Performing Staging vs Basel Table (#t-perf)
            const pfBody = document.querySelector('#t-perf tbody');
            if (pfBody && DATA.ifrs9_basel_perf) {{
                pfBody.innerHTML = DATA.ifrs9_basel_perf.map(r => `
                    <tr>
                        <td><strong>${{r.metric || r.scope}}</strong></td>
                        <td>$${{((r.total_ead || 0)/1e6).toFixed(2)}}M</td>
                        <td>$${{((r.provision_usd || 0)/1e6).toFixed(2)}}M</td>
                        <td><strong style="color:var(--accent-blue);">${{(r.coverage_pct_ead || 0).toFixed(2)}}%</strong></td>
                        <td>${{r.description || ''}}</td>
                    </tr>
                `).join('');
            }}

            // 8. Validation Summary Table (#t-val)
            const vBody = document.querySelector('#t-val tbody');
            if (vBody && DATA.validation_summary) {{
                vBody.innerHTML = DATA.validation_summary.map(r => {{
                    const modelName = r.model === 'model_a' ? 'Model A (Baseline - 7 WoE)' : 'Model B (Grade/Rate Included)';
                    let samplePart = r.sample;
                    if (r.sample === 'train') samplePart = 'Train (2007-2013)';
                    else if (r.sample === 'test') samplePart = 'Test (In-Time)';
                    else if (r.sample === 'oot') samplePart = '2014 OOT (Out-of-Time)';

                    const ksFormatted = (r.ks * 100).toFixed(2) + '%';
                    const brierFormatted = r.brier.toFixed(5);
                    const hlFormatted = r.hl_pvalue < 0.0001 ? r.hl_pvalue.toExponential(4) : r.hl_pvalue.toFixed(5);

                    return `
                        <tr>
                            <td><strong>${{modelName}}</strong></td>
                            <td>${{samplePart}}</td>
                            <td><strong style="color:var(--accent-emerald);">${{(r.auc || 0).toFixed(4)}}</strong></td>
                            <td>${{(r.gini || 0).toFixed(4)}}</td>
                            <td>${{ksFormatted}}</td>
                            <td>${{brierFormatted}}</td>
                            <td>${{hlFormatted}}</td>
                        </tr>
                    `;
                }}).join('');
            }}

            // 9. CSI Table (#t-csi)
            const csBody = document.querySelector('#t-csi tbody');
            if (csBody && DATA.csi_summary) {{
                csBody.innerHTML = DATA.csi_summary.map(r => `
                    <tr>
                        <td><strong>${{r.model === 'model_a' ? 'Model A' : 'Model B'}}</strong></td>
                        <td><strong>${{r.variable}}</strong></td>
                        <td>${{(r.csi || 0).toFixed(4)}}</td>
                        <td><span style="color:var(--accent-emerald);">${{r.stability_band || 'stable'}}</span></td>
                    </tr>
                `).join('');
            }}

            // 10. Coefs Table (#t-coefs)
            const coBody = document.querySelector('#t-coefs tbody');
            if (coBody && DATA.coefs_b) {{
                coBody.innerHTML = DATA.coefs_b.map(r => {{
                    const pVal = r.p_value || 0;
                    let sigText = '';
                    if (pVal < 0.001) sigText = 'Yes (p < 0.001)';
                    else if (pVal < 0.01) sigText = 'Yes (p < 0.01)';
                    else if (pVal < 0.05) sigText = 'Yes (p < 0.05)';
                    else sigText = `No (p = ${{pVal.toFixed(4)}})`;

                    const sigColor = pVal < 0.05 ? 'var(--accent-emerald)' : 'var(--accent-rose)';

                    return `
                        <tr>
                            <td><strong>${{r.variable}}</strong></td>
                            <td>${{(r.coefficient || 0).toFixed(4)}}</td>
                            <td>${{(r.std_err || 0).toFixed(4)}}</td>
                            <td>${{pVal < 0.0001 ? pVal.toExponential(3) : pVal.toFixed(5)}}</td>
                            <td><span style="color:${{sigColor}};">${{sigText}}</span></td>
                        </tr>
                    `;
                }}).join('');
            }}

            // 11. Rating Grades Table (#t-grades)
            const gBody = document.querySelector('#t-grades tbody');
            if (gBody && DATA.rating_grades_b) {{
                gBody.innerHTML = DATA.rating_grades_b.map(r => `
                    <tr>
                        <td><strong>Grade ${{r.grade}}</strong></td>
                        <td>${{r.score_min}} - ${{r.score_max}}</td>
                        <td>${{(r.n_loans || 0).toLocaleString()}}</td>
                        <td><strong style="color:var(--accent-rose);">${{((r.observed_default_rate || 0)*100).toFixed(2)}}%</strong></td>
                    </tr>
                `).join('');
            }}
        }}

        /* CHART INITIALIZATIONS WITH DYNAMIC SCALING & CORRECT KEYS */
        function initCharts() {{
            // 1. Vintage Chart (#c-vintage)
            const ctxVintage = document.getElementById('c-vintage');
            if (ctxVintage && DATA.vintage_curves && DATA.vintage_curves.length > 0) {{
                const colors = ['#38bdf8', '#22d3ee', '#818cf8', '#34d399', '#fb7185', '#fbbf24', '#a855f7', '#ec4899'];
                
                // Extract MOB 0 to 24 columns for each vintage
                const mobs = Array.from({{length: 25}}, (_, i) => 'mob_' + i);
                const datasets = DATA.vintage_curves.map((row, idx) => {{
                    const dataPoints = mobs.map(m => (row[m] !== undefined ? (row[m] * 100) : 0));
                    return {{
                        label: 'Vintage ' + row.vintage_year,
                        data: dataPoints,
                        borderColor: colors[idx % colors.length],
                        borderWidth: 2,
                        fill: false,
                        tension: 0.2
                    }};
                }});

                new Chart(ctxVintage, {{
                    type: 'line',
                    data: {{
                        labels: Array.from({{length: 25}}, (_, i) => 'MOB ' + i),
                        datasets: datasets
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{ labels: {{ color: '#94a3b8' }} }}
                        }},
                        scales: {{
                            y: {{
                                title: {{ display: true, text: 'Cumulative Default Rate (%)', color: '#94a3b8' }},
                                ticks: {{ color: '#64748b', callback: v => v.toFixed(1) + '%' }}
                            }},
                            x: {{
                                title: {{ display: true, text: 'Months on Book (MOB)', color: '#94a3b8' }},
                                ticks: {{ color: '#64748b' }}
                            }}
                        }}
                    }}
                }});
            }}

            // 2. Lifetime Hazard Chart (#c-lifetime)
            const ctxLife = document.getElementById('c-lifetime');
            if (ctxLife && DATA.lifetime_pd && DATA.lifetime_pd.length > 0) {{
                new Chart(ctxLife, {{
                    type: 'line',
                    data: {{
                        labels: DATA.lifetime_pd.map(r => 'M' + r.month),
                        datasets: [
                            {{
                                label: 'Cumulative Lifetime PD (%)',
                                data: DATA.lifetime_pd.map(r => (r.cumulative_pd * 100).toFixed(2)),
                                borderColor: '#38bdf8',
                                borderWidth: 2,
                                yAxisID: 'y'
                            }},
                            {{
                                label: 'Marginal Hazard Rate (%)',
                                data: DATA.lifetime_pd.map(r => (r.hazard * 100).toFixed(2)),
                                borderColor: '#fbbf24',
                                borderWidth: 1.5,
                                borderDash: [4, 4],
                                yAxisID: 'y1'
                            }}
                        ]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{ labels: {{ color: '#94a3b8' }} }}
                        }},
                        scales: {{
                            y: {{
                                type: 'linear', display: true, position: 'left',
                                title: {{ display: true, text: 'Cumulative Lifetime PD (%)', color: '#38bdf8' }},
                                ticks: {{ color: '#64748b' }}
                            }},
                            y1: {{
                                type: 'linear', display: true, position: 'right',
                                title: {{ display: true, text: 'Marginal Hazard Rate (%)', color: '#fbbf24' }},
                                grid: {{ drawOnChartArea: false }},
                                ticks: {{ color: '#64748b' }}
                            }},
                            x: {{ ticks: {{ color: '#64748b' }} }}
                        }}
                    }}
                }});
            }}

            // 3. IV Ranking Chart (#c-iv)
            const ctxIv = document.getElementById('c-iv');
            if (ctxIv && DATA.iv_summary && DATA.iv_summary.length > 0) {{
                const top15Iv = DATA.iv_summary.slice(0, 15);
                new Chart(ctxIv, {{
                    type: 'bar',
                    data: {{
                        labels: top15Iv.map(r => r.variable),
                        datasets: [{{
                            label: 'Information Value (IV)',
                            data: top15Iv.map(r => r.IV),
                            backgroundColor: '#34d399'
                        }}]
                    }},
                    options: {{
                        indexAxis: 'y',
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{ labels: {{ color: '#94a3b8' }} }}
                        }},
                        scales: {{
                            x: {{
                                title: {{ display: true, text: 'Information Value (IV)', color: '#94a3b8' }},
                                ticks: {{ color: '#64748b' }}
                            }},
                            y: {{ ticks: {{ color: '#64748b' }} }}
                        }}
                    }}
                }});
            }}
        }}

        /* WORKFLOW RENDERER FOR PIPELINE MODE */
        function renderWorkflow() {{
            const container = document.getElementById('workflow-steps');
            if (!container) return;

            container.innerHTML = PIPELINE_STAGES.map((s, idx) => `
                <div class="stage-step-card ${{idx === 0 ? 'open' : ''}}" id="step-card-${{s.step}}">
                    <div class="step-summary" onclick="toggleStep(${{s.step}})">
                        <div class="step-left">
                            <span class="step-badge">STEP ${{String(s.step).padStart(2, '0')}} OF 12</span>
                            <div>
                                <div class="step-title-text">${{s.title}}</div>
                                <div class="step-module">${{s.module}}</div>
                            </div>
                        </div>
                        <div class="step-right">
                            <span class="step-metric-preview">${{s.preview}}</span>
                            <span class="chevron">▼</span>
                        </div>
                    </div>
                    <div class="step-details">
                        <div class="detail-block">
                            <div class="detail-label input-lbl">INPUT DATA & ARTEFACT</div>
                            <div class="detail-val">${{s.input}}</div>
                        </div>
                        <div class="detail-block">
                            <div class="detail-label output-lbl">OUTPUT ARTEFACT & METRIC</div>
                            <div class="detail-val"><code>${{s.output}}</code></div>
                        </div>
                        <div class="detail-block">
                            <div class="detail-label happens-lbl">WHAT HAPPENS (OPERATION)</div>
                            <div class="detail-val">${{s.happens}}</div>
                        </div>
                        <div class="detail-block">
                            <div class="detail-label why-lbl">WHY (DOMAIN & REGULATORY DRIVER)</div>
                            <div class="detail-val">${{s.why}}</div>
                        </div>
                    </div>
                </div>
                ${{idx < PIPELINE_STAGES.length - 1 ? '<div class="flow-connector">↓</div>' : ''}}
            `).join('');
        }}

        function toggleStep(stepNum) {{
            const card = document.getElementById('step-card-' + stepNum);
            if (card) card.classList.toggle('open');
        }}

        /* INITIALIZATION */
        window.addEventListener('DOMContentLoaded', () => {{
            populateTables();
            initCharts();
            renderWorkflow();

            // Hash Routing
            const hash = window.location.hash.replace('#', '');
            if (hash === 'pipeline') {{
                switchMode('pipeline');
            }} else if (hash.startsWith('analytics-p')) {{
                switchMode('analytics');
                const panelIdx = parseInt(hash.replace('analytics-p', ''), 10);
                if (!isNaN(panelIdx)) showPanel(panelIdx);
            }} else {{
                switchMode('analytics');
            }}
        }});
    </script>
</body>
</html>
"""

    DOCS_HTML_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DOCS_HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)
    logger.info(f"Successfully generated master application at {DOCS_HTML_PATH}")

    with open(ROOT_HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)
    logger.info(f"Successfully mirrored master application at {ROOT_HTML_PATH}")


if __name__ == "__main__":
    main()
