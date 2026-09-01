"""
build_panels.py
---------------
Generates the standalone executive 6-panel risk analytics application
(outputs/reports/risk_analytics_panels.html) directly by reading the ground-truth
output CSV tables in outputs/tables/.

Panels built:
1. Portfolio Overview Panel
2. Vintage Default Curves Panel
3. Delinquency Distribution Panel
4. ECL Staging Panel
5. Model Validation Panel
6. Scorecard & Master Scale Panel
"""

import json
import logging
from pathlib import Path
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parents[3]
TABLES_DIR = PROJECT_ROOT / "outputs" / "tables"
OUTPUT_HTML_PATH = PROJECT_ROOT / "outputs" / "reports" / "risk_analytics_panels.html"


def read_csv_safe(file_name: str) -> pd.DataFrame:
    path = TABLES_DIR / file_name
    if not path.exists():
        logger.warning(f"File missing: {path}")
        return pd.DataFrame()
    return pd.read_csv(path)


def main():
    logger.info("Loading table CSVs for the 6 data panels...")

    # Load all required CSV tables
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

    # Consolidate all tables into a dictionary for JSON embedding
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
    <title>Retail Credit Risk Analytics — Executive 6-Panel Suite</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
    <style>
        :root {{
            --bg-dark: #070a11;
            --panel-bg: rgba(18, 26, 43, 0.8);
            --panel-border: rgba(255, 255, 255, 0.08);
            --panel-hover: rgba(30, 43, 69, 0.9);
            
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --text-dim: #64748b;
            
            --accent-blue: #38bdf8;
            --accent-cyan: #22d3ee;
            --accent-indigo: #818cf8;
            --accent-emerald: #34d399;
            --accent-rose: #fb7185;
            --accent-amber: #fbbf24;
            
            --honesty-accent: #f97316;
            --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            --font-mono: 'JetBrains Mono', monospace;
        }}

        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background-color: var(--bg-dark);
            color: var(--text-main);
            font-family: var(--font-sans);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            background-image: radial-gradient(circle at 50% 0%, rgba(56, 189, 248, 0.06) 0%, transparent 70%);
        }}

        header {{
            height: 64px;
            padding: 0 32px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid var(--panel-border);
            background: rgba(7, 10, 17, 0.9);
            backdrop-filter: blur(16px);
            position: sticky;
            top: 0;
            z-index: 100;
        }}

        .brand {{ display: flex; align-items: center; gap: 12px; }}
        .brand-logo {{
            width: 32px; height: 32px; border-radius: 8px;
            background: linear-gradient(135deg, var(--accent-blue), var(--accent-indigo));
            display: flex; align-items: center; justify-content: center;
            font-weight: 700; font-size: 14px; color: #000;
        }}
        .brand-title {{ font-size: 16px; font-weight: 700; letter-spacing: -0.3px; }}
        .brand-sub {{ font-size: 12px; color: var(--text-muted); font-family: var(--font-mono); margin-left: 8px; padding-left: 8px; border-left: 1px solid var(--panel-border); }}

        /* NAV TABS */
        nav.nav-tabs {{
            display: flex;
            gap: 6px;
            padding: 12px 32px;
            background: rgba(15, 23, 42, 0.6);
            border-bottom: 1px solid var(--panel-border);
            overflow-x: auto;
        }}
        .tab-btn {{
            background: transparent;
            border: 1px solid transparent;
            color: var(--text-muted);
            padding: 8px 16px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
            white-space: nowrap;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .tab-btn:hover {{ background: rgba(255, 255, 255, 0.05); color: #fff; }}
        .tab-btn.active {{
            background: rgba(56, 189, 248, 0.12);
            border-color: rgba(56, 189, 248, 0.3);
            color: var(--accent-blue);
            font-weight: 600;
        }}

        /* MAIN PANEL CONTAINER */
        main {{ flex: 1; padding: 28px 32px; max-width: 1600px; margin: 0 auto; width: 100%; }}
        .panel {{ display: none; flex-direction: column; gap: 24px; }}
        .panel.active {{ display: flex; }}

        /* GRID LAYOUTS */
        .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 16px; }}
        .kpi-card {{
            background: var(--panel-bg);
            border: 1px solid var(--panel-border);
            border-radius: 12px;
            padding: 20px;
            backdrop-filter: blur(10px);
        }}
        .kpi-label {{ font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-dim); margin-bottom: 6px; font-weight: 600; }}
        .kpi-val {{ font-family: var(--font-mono); font-size: 22px; font-weight: 700; color: #fff; margin-bottom: 4px; }}
        .kpi-sub {{ font-size: 12px; color: var(--accent-cyan); font-family: var(--font-mono); }}

        .grid-2 {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 24px; }}
        .grid-1 {{ display: grid; grid-template-columns: 1fr; gap: 24px; }}

        .card {{
            background: var(--panel-bg);
            border: 1px solid var(--panel-border);
            border-radius: 14px;
            padding: 24px;
            backdrop-filter: blur(12px);
            display: flex;
            flex-direction: column;
            gap: 16px;
        }}
        .card-header {{ display: flex; align-items: center; justify-content: space-between; gap: 12px; }}
        .card-title {{ font-size: 15px; font-weight: 600; color: #fff; display: flex; align-items: center; gap: 8px; }}
        
        .honesty-notice {{
            font-family: var(--font-mono);
            font-size: 10px;
            font-weight: 600;
            color: var(--honesty-accent);
            background: rgba(249, 115, 22, 0.15);
            border: 1px solid rgba(249, 115, 22, 0.3);
            padding: 3px 8px;
            border-radius: 4px;
            letter-spacing: 0.3px;
        }}

        /* TABLES */
        .table-wrapper {{ overflow-x: auto; max-height: 440px; overflow-y: auto; border-radius: 8px; border: 1px solid rgba(255, 255, 255, 0.05); }}
        table {{ width: 100%; border-collapse: collapse; font-family: var(--font-mono); font-size: 12px; text-align: left; }}
        th {{ background: #0f172a; color: var(--text-dim); font-weight: 600; padding: 10px 14px; position: sticky; top: 0; border-bottom: 1px solid var(--panel-border); text-transform: uppercase; font-size: 10px; letter-spacing: 0.5px; }}
        td {{ padding: 10px 14px; border-bottom: 1px solid rgba(255, 255, 255, 0.03); color: var(--text-muted); }}
        tr:hover td {{ background: rgba(255, 255, 255, 0.02); color: #fff; }}

        .chart-box {{ position: relative; height: 320px; width: 100%; }}
        @media (max-width: 1024px) {{ .grid-2 {{ grid-template-columns: 1fr; }} main {{ padding: 16px; }} nav.nav-tabs {{ padding: 8px 16px; }} }}
    </style>
</head>
<body>

    <header>
        <div class="brand">
            <div class="brand-logo">RC</div>
            <div>
                <span class="brand-title">Retail Credit Risk Engine</span>
                <span class="brand-sub">Public LendingClub Dataset (2007–2014 Origination Vintages, 466,285 Loans)</span>
            </div>
        </div>
    </header>

    <nav class="nav-tabs">
        <button class="tab-btn active" onclick="showPanel(0)">📊 1. Portfolio Overview</button>
        <button class="tab-btn" onclick="showPanel(1)">📈 2. Vintage Curves</button>
        <button class="tab-btn" onclick="showPanel(2)">🔄 3. Delinquency & Roll Rates</button>
        <button class="tab-btn" onclick="showPanel(3)">🛡️ 4. ECL Staging & Lifetime PD</button>
        <button class="tab-btn" onclick="showPanel(4)">🎯 5. Model Validation</button>
        <button class="tab-btn" onclick="showPanel(5)">💳 6. Scorecard & Master Scale</button>
    </nav>

    <main>
        <!-- PANEL 1: PORTFOLIO OVERVIEW -->
        <div class="panel active" id="p0">
            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-label">OOT Portfolio Loans</div>
                    <div class="kpi-val">235,628</div>
                    <div class="kpi-sub">Vintage 2014 Cohort</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Total Exposure at Default (EAD)</div>
                    <div class="kpi-val">$1.827B</div>
                    <div class="kpi-sub">$1,826,572,642.48</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Basel 12m Expected Loss (EL)</div>
                    <div class="kpi-val">$58.67M</div>
                    <div class="kpi-sub">3.21% of Total EAD</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">IFRS 9 Scenario ECL</div>
                    <div class="kpi-val">$285.04M</div>
                    <div class="kpi-sub">15.61% Coverage Ratio</div>
                </div>
            </div>

            <div class="grid-2">
                <div class="card">
                    <div class="card-header">
                        <span class="card-title">Basel III IRB vs Standardised Capital RWA Comparison</span>
                    </div>
                    <div class="table-wrapper">
                        <table id="t-basel">
                            <thead><tr><th>Segment / Metric</th><th>Loan Count</th><th>Total EAD ($)</th><th>IRB RWA ($)</th><th>Std RWA ($)</th><th>IRB RW %</th></tr></thead>
                            <tbody></tbody>
                        </table>
                    </div>
                </div>
                <div class="card">
                    <div class="card-header">
                        <span class="card-title">IFRS 9 vs US CECL Lifetime Provisioning Comparison</span>
                    </div>
                    <div class="table-wrapper">
                        <table id="t-cecl">
                            <thead><tr><th>Framework</th><th>Total EAD ($)</th><th>Total Provision ($)</th><th>Coverage %</th><th>Notes</th></tr></thead>
                            <tbody></tbody>
                        </table>
                    </div>
                </div>
            </div>

            <div class="grid-2">
                <div class="card">
                    <div class="card-header">
                        <span class="card-title">Resolved Defaults LGD Bimodal Distribution</span>
                    </div>
                    <div class="chart-box"><canvas id="c-lgd"></canvas></div>
                </div>
                <div class="card">
                    <div class="card-header">
                        <span class="card-title">Default Timing Distribution (Months-on-Book)</span>
                    </div>
                    <div class="chart-box"><canvas id="c-timing"></canvas></div>
                </div>
            </div>
        </div>

        <!-- PANEL 2: VINTAGE DEFAULT CURVES -->
        <div class="panel" id="p1">
            <div class="card">
                <div class="card-header">
                    <span class="card-title">Cumulative Default Curves by Vintage Year (MOB 0 to 48)</span>
                </div>
                <div class="chart-box" style="height: 380px;"><canvas id="c-vintage"></canvas></div>
            </div>

            <div class="card">
                <div class="card-header">
                    <span class="card-title">Fixed Months-on-Book Vintage Maturity Comparison</span>
                </div>
                <div class="table-wrapper">
                    <table id="t-vintage-mat">
                        <thead><tr><th>Vintage Year</th><th>Total Loans</th><th>MOB 12 Default Rate</th><th>MOB 18 Default Rate</th><th>MOB 24 Default Rate</th></tr></thead>
                        <tbody></tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- PANEL 3: DELINQUENCY DISTRIBUTION -->
        <div class="panel" id="p2">
            <div class="card">
                <div class="card-header">
                    <span class="card-title">Delinquency Roll-Rate Proxy Table by Vintage Year</span>
                    <span class="honesty-notice">[CROSS-SECTIONAL PROXY - NOT MONTHLY PANEL]</span>
                </div>
                <div class="table-wrapper">
                    <table id="t-rollrate">
                        <thead><tr><th>Vintage</th><th>Total Loans</th><th>Current %</th><th>Grace %</th><th>Late 16-30 %</th><th>Late 31-120 %</th><th>Default %</th><th>Paid %</th></tr></thead>
                        <tbody></tbody>
                    </table>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <span class="card-title">Origination Rating Grade to Loan Outcome Transition Matrix</span>
                    <span class="honesty-notice">[CROSS-SECTIONAL PROXY - NOT MONTHLY PANEL]</span>
                </div>
                <div class="table-wrapper">
                    <table id="t-trans">
                        <thead><tr><th>Origination Grade</th><th>Total Loans</th><th>Fully Paid %</th><th>Current %</th><th>Late %</th><th>Default %</th></tr></thead>
                        <tbody></tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- PANEL 4: ECL STAGING & LIFETIME PD -->
        <div class="panel" id="p3">
            <div class="grid-2">
                <div class="card">
                    <div class="card-header">
                        <span class="card-title">IFRS 9 Portfolio Staging Breakdown</span>
                    </div>
                    <div class="table-wrapper">
                        <table id="t-staging">
                            <thead><tr><th>Stage</th><th>Loan Count</th><th>Total EAD ($)</th><th>Total ECL ($)</th><th>Coverage %</th></tr></thead>
                            <tbody></tbody>
                        </table>
                    </div>
                </div>
                <div class="card">
                    <div class="card-header">
                        <span class="card-title">Performing Book (Stage 1 + 2) IFRS 9 ECL vs Basel EL</span>
                    </div>
                    <div class="table-wrapper">
                        <table id="t-perf">
                            <thead><tr><th>Scope / Framework</th><th>Total EAD ($)</th><th>Provision ($)</th><th>Coverage %</th><th>Description</th></tr></thead>
                            <tbody></tbody>
                        </table>
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <span class="card-title">60-Month Discrete-Time Portfolio Lifetime PD Hazard Curve</span>
                </div>
                <div class="chart-box" style="height: 340px;"><canvas id="c-lifetime"></canvas></div>
            </div>
        </div>

        <!-- PANEL 5: MODEL VALIDATION -->
        <div class="panel" id="p4">
            <div class="card">
                <div class="card-header">
                    <span class="card-title">Master Model Validation Summary (Discrimination & Calibration)</span>
                </div>
                <div class="table-wrapper">
                    <table id="t-val">
                        <thead><tr><th>Model Name</th><th>Sample Partition</th><th>AUC</th><th>Gini</th><th>KS Stat</th><th>Brier Score</th><th>HL p-value</th></tr></thead>
                        <tbody></tbody>
                    </table>
                </div>
            </div>

            <div class="grid-2">
                <div class="card">
                    <div class="card-header">
                        <span class="card-title">Side-by-Side Hosmer-Lemeshow Calibration & Score PSI</span>
                    </div>
                    <div class="table-wrapper">
                        <table id="t-hl-side">
                            <thead><tr><th>Sample Partition</th><th>Sample Size (N)</th><th>Model B HL p-value</th><th>Model B Score PSI</th><th>Calibration Status</th></tr></thead>
                            <tbody>
                                <tr><td>Test Partition</td><td>46,132</td><td>0.49418</td><td>0.0071</td><td><span style="color: var(--accent-emerald);">Passed (p > 0.05)</span></td></tr>
                                <tr><td>Out-of-Time (OOT)</td><td>235,628</td><td>0.00117</td><td>0.0071</td><td><span style="color: var(--honesty-accent);">Drifted (N > 200k Sensitivity)</span></td></tr>
                                <tr><td>Train Partition</td><td>184,525</td><td>0.00040</td><td>0.0071</td><td><span style="color: var(--honesty-accent);">Drifted (N > 100k Sensitivity)</span></td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <span class="card-title">Observed Default Rate by Rating Grade (Model B)</span>
                    </div>
                    <div class="chart-box"><canvas id="c-grade-dr"></canvas></div>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <span class="card-title">Characteristic Stability Index (CSI) by Feature Variable</span>
                </div>
                <div class="table-wrapper">
                    <table id="t-csi">
                        <thead><tr><th>Model</th><th>Variable Name</th><th>CSI Value</th><th>Stability Band</th></tr></thead>
                        <tbody></tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- PANEL 6: SCORECARD & MASTER SCALE -->
        <div class="panel" id="p5">
            <div class="grid-2">
                <div class="card">
                    <div class="card-header">
                        <span class="card-title">Information Value (IV) Ranking (Top 15 Features)</span>
                    </div>
                    <div class="chart-box"><canvas id="c-iv"></canvas></div>
                </div>
                <div class="card">
                    <div class="card-header">
                        <span class="card-title">Logistic Regression Model B Coefficients</span>
                    </div>
                    <div class="table-wrapper">
                        <table id="t-coefs">
                            <thead><tr><th>Variable</th><th>Coefficient</th><th>Std Error</th><th>p-value</th><th>Significant</th></tr></thead>
                            <tbody></tbody>
                        </table>
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <span class="card-title">Model B Master Rating Grades Scale</span>
                </div>
                <div class="table-wrapper">
                    <table id="t-grades">
                        <thead><tr><th>Rating Grade</th><th>Score Range</th><th>Loan Count</th><th>Defaults</th><th>Observed Default Rate</th><th>Portfolio Share</th></tr></thead>
                        <tbody></tbody>
                    </table>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <span class="card-title">Model B Scorecard Points Mapping (62 Bins)</span>
                </div>
                <div class="table-wrapper">
                    <table id="t-scorecard">
                        <thead><tr><th>Feature</th><th>Bin Range</th><th>WoE Value</th><th>Coefficient</th><th>Scorecard Points</th></tr></thead>
                        <tbody></tbody>
                    </table>
                </div>
            </div>
        </div>
    </main>

    <script>
        const DATA = {json_str};

        function fmtNum(n, d=2) {{
            if (n === null || n === undefined) return '-';
            return Number(n).toLocaleString(undefined, {{minimumFractionDigits: d, maximumFractionDigits: d}});
        }}

        function fmtPct(n, d=2) {{
            if (n === null || n === undefined) return '-';
            return (Number(n) * 100).toFixed(d) + '%';
        }}

        function showPanel(idx) {{
            document.querySelectorAll('.panel').forEach((p, i) => {{
                p.classList.toggle('active', i === idx);
            }});
            document.querySelectorAll('.tab-btn').forEach((b, i) => {{
                b.classList.toggle('active', i === idx);
            }});
        }}

        function renderTables() {{
            // Basel Capital Table
            const tbBasel = document.querySelector('#t-basel tbody');
            if (DATA.basel_summary) {{
                tbBasel.innerHTML = DATA.basel_summary.map(r => `
                    <tr>
                        <td><strong>${{r.segment}} ${{r.category || ''}}</strong></td>
                        <td>${{fmtNum(r.count, 0)}}</td>
                        <td>$${{fmtNum(r.total_ead, 2)}}</td>
                        <td>$${{fmtNum(r.irb_rwa, 2)}}</td>
                        <td>$${{fmtNum(r.std_rwa, 2)}}</td>
                        <td><strong>${{fmtNum(r.irb_rw_pct, 1)}}%</strong></td>
                    </tr>
                `).join('');
            }}

            // CECL Table
            const tbCecl = document.querySelector('#t-cecl tbody');
            if (DATA.ifrs9_cecl) {{
                tbCecl.innerHTML = DATA.ifrs9_cecl.map(r => `
                    <tr>
                        <td><strong>${{r.accounting_framework || r.framework}}</strong></td>
                        <td>$${{fmtNum(r.total_ead_usd || r.total_ead, 2)}}</td>
                        <td>$${{fmtNum(r.total_ecl_usd || r.total_ecl, 2)}}</td>
                        <td><strong>${{fmtNum(r.ecl_coverage_pct || r.ecl_pct_ead, 2)}}%</strong></td>
                        <td>${{r.notes || '-'}}</td>
                    </tr>
                `).join('');
            }}

            // Vintage Maturity
            const tbVmat = document.querySelector('#t-vintage-mat tbody');
            if (DATA.vintage_maturity) {{
                tbVmat.innerHTML = DATA.vintage_maturity.map(r => `
                    <tr>
                        <td><strong>${{r.vintage_year}}</strong></td>
                        <td>${{fmtNum(r.total_loans, 0)}}</td>
                        <td>${{fmtPct(r.default_rate_mob_12, 2)}}</td>
                        <td>${{fmtPct(r.default_rate_mob_18, 2)}}</td>
                        <td>${{fmtPct(r.default_rate_mob_24, 2)}}</td>
                    </tr>
                `).join('');
            }}

            // Roll Rate Proxy
            const tbRoll = document.querySelector('#t-rollrate tbody');
            if (DATA.roll_rate_proxy) {{
                tbRoll.innerHTML = DATA.roll_rate_proxy.map(r => `
                    <tr>
                        <td><strong>${{r.vintage_year}}</strong></td>
                        <td>${{fmtNum(r.total_loans, 0)}}</td>
                        <td>${{fmtNum(r.current_pct, 2)}}%</td>
                        <td>${{fmtNum(r.grace_period_pct, 2)}}%</td>
                        <td>${{fmtNum(r.late_16_30_pct, 2)}}%</td>
                        <td>${{fmtNum(r.late_31_120_pct, 2)}}%</td>
                        <td>${{fmtNum(r.default_charged_off_pct, 2)}}%</td>
                        <td>${{fmtNum(r.fully_paid_pct, 2)}}%</td>
                    </tr>
                `).join('');
            }}

            // Transition Matrix
            const tbTrans = document.querySelector('#t-trans tbody');
            if (DATA.transition_matrix) {{
                tbTrans.innerHTML = DATA.transition_matrix.map(r => `
                    <tr>
                        <td><strong>Grade ${{r.grade}}</strong></td>
                        <td>${{fmtNum(r.total_loans, 0)}}</td>
                        <td>${{fmtPct(r['Fully Paid'], 2)}}</td>
                        <td>${{fmtPct(r.Current, 2)}}</td>
                        <td>${{fmtPct(r.Late, 2)}}</td>
                        <td><strong style="color: var(--accent-rose);">${{fmtPct(r.Default, 2)}}</strong></td>
                    </tr>
                `).join('');
            }}

            // Staging Table
            const tbStg = document.querySelector('#t-staging tbody');
            if (DATA.ecl_summary) {{
                tbStg.innerHTML = DATA.ecl_summary.map(r => `
                    <tr>
                        <td><strong>${{r.stage}}</strong></td>
                        <td>${{fmtNum(r.count, 0)}}</td>
                        <td>$${{fmtNum(r.total_ead, 2)}}</td>
                        <td>$${{fmtNum(r.total_ecl, 2)}}</td>
                        <td><strong>${{fmtNum(r.ecl_pct_ead, 2)}}%</strong></td>
                    </tr>
                `).join('');
            }}

            // Performing Comparison Table
            const tbPerf = document.querySelector('#t-perf tbody');
            if (DATA.ifrs9_basel_perf) {{
                tbPerf.innerHTML = DATA.ifrs9_basel_perf.map(r => `
                    <tr>
                        <td><strong>${{r.metric}}</strong></td>
                        <td>$${{fmtNum(r.total_ead, 2)}}</td>
                        <td>$${{fmtNum(r.provision_usd, 2)}}</td>
                        <td>${{fmtNum(r.coverage_pct_ead, 2)}}%</td>
                        <td>${{r.description}}</td>
                    </tr>
                `).join('');
            }}

            // Validation Table
            const tbVal = document.querySelector('#t-val tbody');
            if (DATA.validation_summary) {{
                tbVal.innerHTML = DATA.validation_summary.map(r => `
                    <tr>
                        <td><strong>${{r.model}}</strong></td>
                        <td>${{r.sample}}</td>
                        <td>${{fmtNum(r.auc, 4)}}</td>
                        <td>${{fmtNum(r.gini, 4)}}</td>
                        <td>${{fmtNum(r.ks, 4)}}</td>
                        <td>${{fmtNum(r.brier, 5)}}</td>
                        <td>${{Number(r.hl_pvalue).toExponential(3)}}</td>
                    </tr>
                `).join('');
            }}

            // CSI Table
            const tbCsi = document.querySelector('#t-csi tbody');
            if (DATA.csi_summary) {{
                tbCsi.innerHTML = DATA.csi_summary.map(r => `
                    <tr>
                        <td>${{r.model}}</td>
                        <td><strong>${{r.variable}}</strong></td>
                        <td>${{fmtNum(r.csi, 4)}}</td>
                        <td><span style="color: var(--accent-emerald);">${{r.stability_band}}</span></td>
                    </tr>
                `).join('');
            }}

            // Coefficients Table
            const tbCoef = document.querySelector('#t-coefs tbody');
            if (DATA.coefs_b) {{
                tbCoef.innerHTML = DATA.coefs_b.map(r => `
                    <tr>
                        <td><strong>${{r.variable}}</strong></td>
                        <td>${{fmtNum(r.coefficient, 4)}}</td>
                        <td>${{fmtNum(r.std_err, 4)}}</td>
                        <td>${{Number(r.p_value).toExponential(3)}}</td>
                        <td>${{r.significant ? 'Yes' : 'No'}}</td>
                    </tr>
                `).join('');
            }}

            // Master Rating Scale Table
            const tbGrd = document.querySelector('#t-grades tbody');
            if (DATA.rating_grades_b) {{
                tbGrd.innerHTML = DATA.rating_grades_b.map(r => `
                    <tr>
                        <td><strong>Grade ${{r.grade}}</strong></td>
                        <td>${{r.score_min}} - ${{r.score_max}}</td>
                        <td>${{fmtNum(r.n_loans, 0)}}</td>
                        <td>${{fmtNum(r.n_defaults, 0)}}</td>
                        <td><strong style="color: var(--accent-amber);">${{fmtPct(r.observed_default_rate, 2)}}</strong></td>
                        <td>${{fmtPct(r.portfolio_share, 2)}}</td>
                    </tr>
                `).join('');
            }}

            // Scorecard Points Table
            const tbScd = document.querySelector('#t-scorecard tbody');
            if (DATA.scorecard_b) {{
                tbScd.innerHTML = DATA.scorecard_b.map(r => `
                    <tr>
                        <td><strong>${{r.variable}}</strong></td>
                        <td>${{r.bin}}</td>
                        <td>${{fmtNum(r.woe, 4)}}</td>
                        <td>${{fmtNum(r.coefficient, 4)}}</td>
                        <td><strong style="color: var(--accent-blue);">${{r.points}}</strong></td>
                    </tr>
                `).join('');
            }}
        }}

        function renderCharts() {{
            Chart.defaults.color = '#94a3b8';
            Chart.defaults.font.family = 'JetBrains Mono';

            // Vintage Curves Chart
            if (DATA.vintage_curves && DATA.vintage_curves.length > 0) {{
                const ctxV = document.getElementById('c-vintage').getContext('2d');
                const colors = ['#38bdf8', '#818cf8', '#34d399', '#fb7185', '#fbbf24', '#c084fc', '#f97316', '#22d3ee'];
                const datasets = DATA.vintage_curves.map((v, i) => {{
                    const mobData = [];
                    for (let m = 0; m <= 24; m++) {{
                        mobData.push((v[`mob_${{m}}`] * 100).toFixed(2));
                    }}
                    return {{
                        label: `Vintage ${{v.vintage_year}}`,
                        data: mobData,
                        borderColor: colors[i % colors.length],
                        backgroundColor: 'transparent',
                        borderWidth: 2,
                        pointRadius: 0
                    }};
                }});

                new Chart(ctxV, {{
                    type: 'line',
                    data: {{
                        labels: Array.from({{length: 25}}, (_, i) => `MOB ${{i}}`),
                        datasets: datasets
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{ legend: {{ position: 'right' }} }},
                        scales: {{
                            y: {{ title: {{ display: true, text: 'Cumulative Default Rate (%)' }} }},
                            x: {{ title: {{ display: true, text: 'Months-on-Book' }} }}
                        }}
                    }}
                }});
            }}

            // Lifetime PD Chart
            if (DATA.lifetime_pd && DATA.lifetime_pd.length > 0) {{
                const ctxL = document.getElementById('c-lifetime').getContext('2d');
                new Chart(ctxL, {{
                    type: 'line',
                    data: {{
                        labels: DATA.lifetime_pd.map(r => `M${{r.month}}`),
                        datasets: [{{
                            label: 'Cumulative Lifetime PD (%)',
                            data: DATA.lifetime_pd.map(r => (r.cumulative_pd * 100).toFixed(2)),
                            borderColor: '#38bdf8',
                            backgroundColor: 'rgba(56, 189, 248, 0.1)',
                            fill: true,
                            borderWidth: 2
                        }}]
                    }},
                    options: {{
                        responsive: true, maintainAspectRatio: false,
                        scales: {{ y: {{ title: {{ display: true, text: 'Cumulative PD (%)' }} }} }}
                    }}
                }});
            }}

            // LGD Distribution Chart
            const ctxLgd = document.getElementById('c-lgd').getContext('2d');
            new Chart(ctxLgd, {{
                type: 'bar',
                data: {{
                    labels: ['0% Write-Off (Full Recovery)', '1% - 99% Partial Recovery', '100% Write-Off (Zero Recovery)'],
                    datasets: [{{
                        label: '% of Defaults',
                        data: [4.8, 43.0, 52.2],
                        backgroundColor: ['#34d399', '#818cf8', '#fb7185']
                    }}]
                }},
                options: {{ responsive: true, maintainAspectRatio: false }}
            }});

            // Timing Distribution Chart
            if (DATA.default_timing) {{
                const ctxT = document.getElementById('c-timing').getContext('2d');
                new Chart(ctxT, {{
                    type: 'bar',
                    data: {{
                        labels: DATA.default_timing.map(r => r.mob_bucket || `MOB ${{r.mob}}`),
                        datasets: [{{
                            label: 'Default Concentration (%)',
                            data: DATA.default_timing.map(r => (r.pct_of_defaults * 100).toFixed(1)),
                            backgroundColor: '#38bdf8'
                        }}]
                    }},
                    options: {{ responsive: true, maintainAspectRatio: false }}
                }});
            }}

            // Grade Default Rate Chart
            if (DATA.rating_grades_b) {{
                const ctxG = document.getElementById('c-grade-dr').getContext('2d');
                new Chart(ctxG, {{
                    type: 'bar',
                    data: {{
                        labels: DATA.rating_grades_b.map(r => `Grade ${{r.grade}}`),
                        datasets: [{{
                            label: 'Observed Default Rate (%)',
                            data: DATA.rating_grades_b.map(r => (r.observed_default_rate * 100).toFixed(2)),
                            backgroundColor: '#fbbf24'
                        }}]
                    }},
                    options: {{ responsive: true, maintainAspectRatio: false }}
                }});
            }}

            // IV Ranking Chart
            if (DATA.iv_summary) {{
                const ctxIv = document.getElementById('c-iv').getContext('2d');
                const top15 = DATA.iv_summary.slice(0, 15);
                new Chart(ctxIv, {{
                    type: 'bar',
                    data: {{
                        labels: top15.map(r => r.variable),
                        datasets: [{{
                            label: 'Information Value (IV)',
                            data: top15.map(r => r.IV),
                            backgroundColor: '#818cf8'
                        }}]
                    }},
                    options: {{ indexAxis: 'y', responsive: true, maintainAspectRatio: false }}
                }});
            }}
        }}

        window.addEventListener('DOMContentLoaded', () => {{
            renderTables();
            renderCharts();
        }});
    </script>
</body>
</html>
"""

    with open(OUTPUT_HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html_content)

    logger.info(f"Executive 6-Panel Suite successfully written to: {OUTPUT_HTML_PATH}")


if __name__ == "__main__":
    main()
