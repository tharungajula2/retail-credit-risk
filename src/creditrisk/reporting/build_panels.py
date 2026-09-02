"""
build_panels.py
---------------
Generates the unified standalone master credit risk application:
- docs/index.html (Primary entrypoint for GitHub Pages / URL sharing)
- index.html (Root entrypoint mirror)

Merges Executive Analytics (6 panels), Pipeline Flow DAG (12 stages), and Data Governance into ONE single interactive dashboard.
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
    logger.info("Loading output CSV tables for the unified application...")

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
    <title>Retail Credit Risk Engine — Master Interactive Suite</title>
    <meta name="description" content="Unified single-page interactive credit risk modeling system, executive dashboard, and pipeline flow map for LendingClub 466,285 loans (2007-2014).">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
    <style>
        :root {{
            --bg-dark: #070a11;
            --panel-bg: rgba(18, 26, 43, 0.85);
            --panel-border: rgba(255, 255, 255, 0.08);
            --panel-hover: rgba(30, 43, 69, 0.95);
            
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
            --honesty-glow: rgba(249, 115, 22, 0.25);

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
            background-image: 
                radial-gradient(circle at 50% 0%, rgba(56, 189, 248, 0.08) 0%, transparent 60%),
                linear-gradient(to right, rgba(255, 255, 255, 0.015) 1px, transparent 1px),
                linear-gradient(to bottom, rgba(255, 255, 255, 0.015) 1px, transparent 1px);
            background-size: 100% 100%, 40px 40px, 40px 40px;
        }}

        /* HEADER */
        header {{
            height: 64px;
            padding: 0 28px;
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
        .brand-title {{ font-size: 16px; font-weight: 700; letter-spacing: -0.3px; color: #fff; }}
        .brand-sub {{ font-size: 12px; color: var(--text-muted); font-family: var(--font-mono); margin-left: 8px; padding-left: 8px; border-left: 1px solid var(--panel-border); }}

        .header-actions {{ display: flex; align-items: center; gap: 14px; }}
        .repo-link {{
            background: rgba(56, 189, 248, 0.1);
            border: 1px solid rgba(56, 189, 248, 0.3);
            color: var(--accent-blue);
            padding: 6px 14px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 600;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: all 0.2s ease;
        }}
        .repo-link:hover {{
            background: var(--accent-blue);
            color: #000;
            box-shadow: 0 0 15px rgba(56, 189, 248, 0.3);
        }}

        /* TOP LEVEL MODE NAVIGATION TABS */
        nav.main-mode-tabs {{
            display: flex;
            gap: 8px;
            padding: 12px 28px;
            background: rgba(15, 23, 42, 0.85);
            border-bottom: 1px solid var(--panel-border);
            backdrop-filter: blur(12px);
            position: sticky;
            top: 64px;
            z-index: 90;
        }}

        .mode-tab-btn {{
            background: transparent;
            border: 1px solid transparent;
            color: var(--text-muted);
            padding: 10px 20px;
            border-radius: 10px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.25s ease;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .mode-tab-btn:hover {{ background: rgba(255, 255, 255, 0.05); color: #fff; }}
        .mode-tab-btn.active {{
            background: linear-gradient(135deg, rgba(56, 189, 248, 0.15), rgba(129, 140, 248, 0.15));
            border-color: rgba(56, 189, 248, 0.4);
            color: var(--accent-blue);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        }}

        /* SUB-PANEL NAVIGATION BAR (FOR ANALYTICS) */
        nav.sub-panel-tabs {{
            display: flex;
            gap: 6px;
            padding: 8px 28px;
            background: rgba(7, 10, 17, 0.5);
            border-bottom: 1px solid var(--panel-border);
            overflow-x: auto;
        }}
        .sub-tab-btn {{
            background: transparent;
            border: 1px solid transparent;
            color: var(--text-dim);
            padding: 6px 14px;
            border-radius: 6px;
            font-size: 12px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
            white-space: nowrap;
        }}
        .sub-tab-btn:hover {{ color: var(--text-main); background: rgba(255, 255, 255, 0.04); }}
        .sub-tab-btn.active {{
            background: rgba(255, 255, 255, 0.08);
            color: var(--accent-cyan);
            border-color: rgba(34, 211, 238, 0.3);
            font-weight: 600;
        }}

        /* MAIN CONTAINER */
        main {{ flex: 1; padding: 24px 28px; max-width: 1600px; margin: 0 auto; width: 100%; position: relative; }}

        .mode-section {{ display: none; flex-direction: column; gap: 24px; }}
        .mode-section.active {{ display: flex; }}

        .panel {{ display: none; flex-direction: column; gap: 24px; }}
        .panel.active {{ display: flex; }}

        /* KPI CARDS & GRIDS */
        .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; }}
        .kpi-card {{
            background: var(--panel-bg);
            border: 1px solid var(--panel-border);
            border-radius: 12px;
            padding: 18px 20px;
            backdrop-filter: blur(10px);
            transition: all 0.2s;
        }}
        .kpi-card:hover {{ border-color: rgba(255, 255, 255, 0.15); transform: translateY(-2px); }}
        .kpi-label {{ font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; color: var(--text-dim); margin-bottom: 6px; font-weight: 600; }}
        .kpi-val {{ font-family: var(--font-mono); font-size: 22px; font-weight: 700; color: #fff; margin-bottom: 4px; }}
        .kpi-sub {{ font-size: 12px; color: var(--accent-cyan); font-family: var(--font-mono); }}

        .grid-2 {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 24px; }}
        .grid-1 {{ display: grid; grid-template-columns: 1fr; gap: 24px; }}

        .card {{
            background: var(--panel-bg);
            border: 1px solid var(--panel-border);
            border-radius: 14px;
            padding: 22px;
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

        /* PIPELINE FLOW DAG GRAPH */
        .dag-flow-container {{
            position: relative;
            min-height: 720px;
            width: 100%;
            overflow: hidden;
            border-radius: 16px;
            border: 1px solid var(--panel-border);
            background: rgba(15, 23, 42, 0.5);
            padding: 24px;
        }}

        svg#flow-svg {{
            width: 100%;
            height: 100%;
            position: absolute;
            top: 0;
            left: 0;
            z-index: 1;
            pointer-events: none;
        }}

        .nodes-grid {{
            position: relative;
            z-index: 2;
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
        }}

        .stage-card {{
            background: var(--panel-bg);
            border: 1px solid var(--panel-border);
            border-radius: 12px;
            padding: 16px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            backdrop-filter: blur(10px);
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: pointer;
            position: relative;
            min-height: 140px;
        }}

        .stage-card:hover {{
            background: var(--panel-hover);
            border-color: rgba(56, 189, 248, 0.5);
            transform: translateY(-3px);
            box-shadow: 0 12px 24px -8px rgba(0, 0, 0, 0.6), 0 0 20px rgba(56, 189, 248, 0.2);
        }}

        .stage-card.honesty-card {{ border-color: rgba(249, 115, 22, 0.4); }}
        .stage-card.honesty-card:hover {{
            border-color: var(--honesty-accent);
            box-shadow: 0 12px 24px -8px rgba(0, 0, 0, 0.6), 0 0 20px var(--honesty-glow);
        }}

        .stage-header {{ display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-bottom: 8px; }}
        .stage-num {{
            font-family: var(--font-mono);
            font-size: 11px;
            font-weight: 600;
            color: var(--accent-blue);
            background: rgba(56, 189, 248, 0.1);
            padding: 2px 8px;
            border-radius: 4px;
            border: 1px solid rgba(56, 189, 248, 0.2);
        }}

        .honesty-badge {{
            font-family: var(--font-mono);
            font-size: 10px;
            font-weight: 600;
            color: var(--honesty-accent);
            background: rgba(249, 115, 22, 0.15);
            padding: 2px 6px;
            border-radius: 4px;
            border: 1px solid rgba(249, 115, 22, 0.3);
        }}

        .stage-title {{ font-size: 14px; font-weight: 600; color: #fff; margin-bottom: 4px; line-height: 1.3; }}
        .stage-modules {{ font-family: var(--font-mono); font-size: 11px; color: var(--accent-indigo); margin-bottom: 10px; word-break: break-all; }}
        .stage-figure {{ background: rgba(0, 0, 0, 0.3); border-radius: 6px; padding: 8px 10px; border: 1px solid rgba(255, 255, 255, 0.04); font-size: 11px; }}

        /* MODAL DRAWER */
        .drawer-overlay {{
            position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
            background: rgba(0, 0, 0, 0.75); backdrop-filter: blur(8px);
            z-index: 300; opacity: 0; pointer-events: none; transition: opacity 0.3s ease;
            display: flex; align-items: center; justify-content: center; padding: 24px;
        }}
        .drawer-overlay.active {{ opacity: 1; pointer-events: auto; }}
        .drawer-content {{
            background: #0f172a; border: 1px solid var(--panel-border); border-radius: 16px;
            width: 100%; max-width: 680px; max-height: 85vh; overflow-y: auto; padding: 28px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.8); transform: scale(0.95);
            transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1); position: relative;
        }}
        .drawer-overlay.active .drawer-content {{ transform: scale(1); }}
        .drawer-close {{
            position: absolute; top: 20px; right: 20px; background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--panel-border); color: var(--text-muted); width: 32px; height: 32px;
            border-radius: 50%; display: flex; align-items: center; justify-content: center;
            cursor: pointer; font-size: 18px; transition: all 0.2s;
        }}
        .drawer-close:hover {{ background: rgba(255, 255, 255, 0.15); color: #fff; }}
        .drawer-section {{ margin-bottom: 20px; }}
        .drawer-section-title {{ font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: var(--text-dim); margin-bottom: 8px; font-weight: 600; }}
        .drawer-box {{ background: rgba(0, 0, 0, 0.3); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 8px; padding: 14px; font-family: var(--font-mono); font-size: 12px; color: var(--text-muted); line-height: 1.6; }}
        .drawer-box.honesty-box {{ background: rgba(249, 115, 22, 0.08); border-color: rgba(249, 115, 22, 0.3); color: #fdba74; }}
        .drawer-box a {{ color: var(--accent-blue); text-decoration: none; word-break: break-all; }}
        .drawer-box a:hover {{ text-decoration: underline; }}

        @media (max-width: 1024px) {{
            .grid-2 {{ grid-template-columns: 1fr; }}
            .nodes-grid {{ grid-template-columns: repeat(2, 1fr); }}
            main {{ padding: 16px; }}
            nav.main-mode-tabs {{ padding: 8px 16px; top: 0; }}
        }}
        @media (max-width: 640px) {{
            .nodes-grid {{ grid-template-columns: 1fr; }}
            .brand-sub, .header-actions {{ display: none; }}
        }}
    </style>
</head>
<body>

    <header>
        <div class="brand">
            <div class="brand-logo">RC</div>
            <div>
                <span class="brand-title">Retail Credit Risk System</span>
                <span class="brand-sub">Public LendingClub Dataset (2007–2014 Origination Vintages, 466,285 Loans)</span>
            </div>
        </div>
        <div class="header-actions">
            <a href="https://github.com/tharungajula2/retail-credit-risk" target="_blank" class="repo-link">
                <span>View GitHub Repository</span>
                <span>↗</span>
            </a>
        </div>
    </header>

    <!-- MAIN MODE NAVIGATION TABS -->
    <nav class="main-mode-tabs">
        <button class="mode-tab-btn active" id="tab-analytics" onclick="switchMode('analytics')">
            <span>📊 Executive Analytics</span>
        </button>
        <button class="mode-tab-btn" id="tab-pipeline" onclick="switchMode('pipeline')">
            <span>🔄 Pipeline Architecture</span>
        </button>
        <button class="mode-tab-btn" id="tab-governance" onclick="switchMode('governance')">
            <span>📋 Data & Governance</span>
        </button>
    </nav>

    <main>
        <!-- ================= MODE 1: EXECUTIVE ANALYTICS ================= -->
        <div class="mode-section active" id="mode-analytics">
            <nav class="sub-panel-tabs">
                <button class="sub-tab-btn active" onclick="showPanel(0)">1. Portfolio Overview</button>
                <button class="sub-tab-btn" onclick="showPanel(1)">2. Vintage Curves</button>
                <button class="sub-tab-btn" onclick="showPanel(2)">3. Delinquency & Roll Rates</button>
                <button class="sub-tab-btn" onclick="showPanel(3)">4. ECL Staging & Lifetime PD</button>
                <button class="sub-tab-btn" onclick="showPanel(4)">5. Model Validation</button>
                <button class="sub-tab-btn" onclick="showPanel(5)">6. Scorecard & Master Scale</button>
            </nav>

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
                        <span class="honesty-notice">[CROSS-SECTIONAL PROXY]</span>
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
                        <span class="honesty-notice">[CROSS-SECTIONAL PROXY]</span>
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
                        <span class="card-title">Master Scale Rating Grade Score Cutoffs & Observed Default Rates</span>
                    </div>
                    <div class="table-wrapper">
                        <table id="t-grades">
                            <thead><tr><th>Grade</th><th>Score Range</th><th>Loan Count</th><th>Observed Default Rate</th></tr></thead>
                            <tbody></tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <!-- ================= MODE 2: PIPELINE ARCHITECTURE (DAG MAP) ================= -->
        <div class="mode-section" id="mode-pipeline">
            <div class="dag-flow-container">
                <svg id="flow-svg">
                    <!-- Rendered by JS -->
                </svg>
                <div class="nodes-grid" id="nodes-grid">
                    <!-- Rendered by JS -->
                </div>
            </div>
        </div>

        <!-- ================= MODE 3: DATA & GOVERNANCE ================= -->
        <div class="mode-section" id="mode-governance">
            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-label">Raw Dataset Size</div>
                    <div class="kpi-val">466,285</div>
                    <div class="kpi-sub">75 Raw Attributes (2007–2014)</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Development Cohort</div>
                    <div class="kpi-val">230,657</div>
                    <div class="kpi-sub">2007–2013 Vintages (184k/46k Split)</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">Out-of-Time (OOT)</div>
                    <div class="kpi-val">235,628</div>
                    <div class="kpi-sub">2014 Origination Vintage</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-label">LGD Modeling Set</div>
                    <div class="kpi-val">50,968</div>
                    <div class="kpi-sub">Resolved Defaults (52.2% Zero Rec)</div>
                </div>
            </div>

            <div class="grid-2">
                <div class="card">
                    <div class="card-header">
                        <span class="card-title">Target Definition & Reconciliation (466,285 Total Loans)</span>
                    </div>
                    <div class="table-wrapper">
                        <table id="t-gov-target">
                            <thead><tr><th>Loan Outcome Group</th><th>Count</th><th>Pct of Portfolio</th><th>Definition & Regulatory Alignment</th></tr></thead>
                            <tbody></tbody>
                        </table>
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <span class="card-title">Modeling Partitions & Stratified Sample Summary</span>
                    </div>
                    <div class="table-wrapper">
                        <table id="t-gov-samples">
                            <thead><tr><th>Sample Partition</th><th>Count</th><th>Defaults</th><th>Default Rate</th><th>Issue Date Range</th></tr></thead>
                            <tbody></tbody>
                        </table>
                    </div>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <span class="card-title">Data Leakage Prevention Guardrails & Schema Hygiene</span>
                </div>
                <div class="drawer-box">
                    <strong style="color: var(--accent-cyan);">Strict Leakage Prevention Protocol (schema.py):</strong><br>
                    To guarantee regulatory compliance and eliminate future-information leakage into credit risk features, all post-origination behavior and resolution outcome columns are stripped during feature extraction. Stripped columns include: <code>recoveries</code>, <code>collection_recovery_fee</code>, <code>total_pymnt</code>, <code>total_rec_prncp</code>, <code>last_pymnt_d</code>, <code>next_pymnt_d</code>, <code>last_credit_pull_d</code>.<br><br>
                    <strong style="color: var(--accent-blue);">Ground-Truth Dataset Origin:</strong><br>
                    Public LendingClub consumer unsecured term loan dataset covering origination vintages 2007 through 2014. No proprietary or employer data is used.
                </div>
            </div>
        </div>
    </main>

    <!-- INTERACTIVE DETAIL DRAWER (PIPELINE DAG) -->
    <div class="drawer-overlay" id="drawer" onclick="closeDrawer(event)">
        <div class="drawer-content" onclick="event.stopPropagation()">
            <button class="drawer-close" onclick="closeDrawer(null)">&times;</button>
            <div class="drawer-section">
                <span class="stage-num" id="d-tag">STAGE 01</span>
                <h2 style="font-size: 22px; font-weight: 700; color: #fff; margin-top: 6px;" id="d-title">Stage Title</h2>
            </div>

            <div class="drawer-section">
                <div class="drawer-section-title">Python Modules & Execution Path</div>
                <div class="drawer-box" id="d-modules">src/creditrisk/data/inspect_raw.py</div>
            </div>

            <div class="drawer-section">
                <div class="drawer-section-title">Artefact & Headline Figures</div>
                <div class="drawer-box" id="d-figures">data_inventory.txt</div>
            </div>

            <div class="drawer-section" id="d-honesty-container" style="display: none;">
                <div class="drawer-section-title" style="color: var(--honesty-accent);">Honesty Limit & Methodology Note</div>
                <div class="drawer-box honesty-box" id="d-honesty">Disclaimer note</div>
            </div>

            <div class="drawer-section">
                <div class="drawer-section-title">Stage Logic & Key Decision</div>
                <div class="drawer-box" id="d-logic">Detailed breakdown of what this stage does.</div>
            </div>
        </div>
    </div>

    <script>
        const DATA = {json_str};
        const REPO_BASE = "https://github.com/tharungajula2/retail-credit-risk/blob/main/";

        const STAGES = [
            {{ num: 1, title: "Raw Load & Inventory", modules: "src/creditrisk/data/inspect_raw.py", artefact: "outputs/reports/data_inventory.txt", figure: "<strong>466,285 rows</strong>, 75 columns. 15 columns 100% null.", logic: "Reads raw LendingClub 2007-2014 dataset in 50,000-row chunks to prevent memory spikes. Audits missing values, data types, date boundaries, and field cardinality.", honesty: null }},
            {{ num: 2, title: "Schema & Leakage Guard", modules: "src/creditrisk/data/schema.py", artefact: "PD-eligible column set", figure: "<strong>assert_no_leakage</strong> active. Filtered post-origination columns.", logic: "Enforces strict regulatory data hygiene. Strips out forward-looking outcome columns (e.g. recoveries, total_pymnt, last_pymnt_d) to prevent target leakage into credit risk features.", honesty: null }},
            {{ num: 3, title: "Target Construction", modules: "src/creditrisk/data/target.py", artefact: "outputs/tables/target_reconciliation.csv", figure: "466,285 → <strong>50,968 ever-default (10.93%)</strong> → 16,018 12m default (3.44%)", logic: "Infers default timing by looking at last payment date (last_pymnt_d + 1 month) since raw dataset lacks default dates. Defines 12-month default flag (target_12m) for Basel III & IFRS 9 Stage 1 alignment.", honesty: null }},
            {{ num: 4, title: "Sampling & Stratification", modules: "src/creditrisk/data/sampling.py", artefact: "outputs/tables/sample_summary.csv", figure: "Train: <strong>184,525</strong> | Test: <strong>46,132</strong> | OOT (2014): <strong>235,628</strong>", logic: "Splits portfolio into 80/20 in-time Train/Test stratified by 12m default rate (2007-2013 vintages) and holds out full 2014 vintage (235,628 loans) as Out-of-Time (OOT) validation cohort.", honesty: null }},
            {{ num: 5, title: "WoE & IV Binning", modules: "src/creditrisk/features/run_binning.py", artefact: "outputs/tables/iv_summary.csv", figure: "Top IVs: <strong>grade (0.294)</strong>, <strong>int_rate (0.277)</strong>", logic: "Transforms numeric & categorical features into Weight of Evidence (WoE) monotonic bins with Laplace smoothing. Measures Information Value (IV) to select predictive, stable risk factors.", honesty: null }},
            {{ num: 6, title: "PD Model & Scorecard", modules: "src/creditrisk/models/run_pd_model.py", artefact: "outputs/tables/scorecard_model_b.csv", figure: "8 Rating Grades. Monotonic default rates: <strong>0.86% → 7.72%</strong>", logic: "Fits Logistic Regression Model B. Scales WoE coefficients into a 600-point Points-to-Double-Odds (PDO 20) master scorecard mapping scores (522-639) into 8 master rating grades.", honesty: null }},
            {{ num: 7, title: "LGD, EAD & CCF Engine", modules: "src/creditrisk/models/run_lgd_training.py", artefact: "outputs/tables/lgd_calibration.csv", figure: "LGD Decile Error <strong>< 0.01</strong>. Mean LGD: <strong>93.4%</strong>", logic: "Fits Two-Stage LGD Model (Stage 1 Logistic Classifier + Stage 2 Fractional Logit GLM) on 50,968 resolved defaults to handle extreme 52.2% zero-recovery bimodal write-off spike.", honesty: "Stage 7 CCF regression model is a synthetic demonstration for revolving credit line drawdowns." }},
            {{ num: 8, title: "Regulatory Layer (Basel & IFRS 9)", modules: "src/creditrisk/regulatory/run_staging.py", artefact: "outputs/tables/ecl_summary.csv", figure: "ECL: <strong>$278.48M (15.25%)</strong> | IRB RWA: <strong>$2.295B (125.6%)</strong>", logic: "Calculates IFRS 9 3-Stage ECL across Base/Downside/Upside macro scenarios. Evaluates Basel III IRB Supervisory Formula (BCBS para 4.4) capital requirements and 60-month lifetime PD curves.", honesty: "Stage 8 expected loss and macro scenario weightings run on 3-loan test fixture in unit scripts, but portfolio totals reflect OOT cohort." }},
            {{ num: 9, title: "Validation & Stability Battery", modules: "src/creditrisk/validation/run_validation.py", artefact: "outputs/tables/validation_summary.csv", figure: "OOT Gini: <strong>0.3845</strong> | AUC: <strong>0.6923</strong> | PSI: <strong>0.0071 (Stable)</strong>", logic: "Evaluates Model A and B discrimination (AUC, Gini, KS) and calibration (Hosmer-Lemeshow) across Train, Test, and OOT. Computes Score PSI and Feature CSI to guarantee zero temporal drift.", honesty: null }},
            {{ num: 10, title: "Portfolio Monitoring", modules: "src/creditrisk/monitoring/run_transitions.py", artefact: "outputs/tables/vintage_curves.csv", figure: "8 Vintages (2007-2014). 7 Grade Transitions (A-G).", logic: "Generates Months-on-Book (MOB 0..48) cumulative default curves per vintage year and builds grade transition matrices tracking borrower credit migration across loan outcomes.", honesty: "Stage 10 roll rates and grade transition matrices are cross-sectional proxies, not a monthly panel dataset." }},
            {{ num: 11, title: "Master Reporting Dashboard", modules: "src/creditrisk/reporting/build_panels.py", artefact: "docs/index.html", figure: "Single-file interactive master dashboard & DAG app", logic: "Consolidates all output table CSVs into a single JSON schema and injects it into a self-contained single-URL executive web application.", honesty: null }},
            {{ num: 12, title: "RAG AI Credit Analyst", modules: "src/creditrisk/ai/rag_index.py", artefact: "Gemini RAG Index & Python Tools", figure: "FAISS vector index + Live Python risk tools", logic: "Indexes model documentation and governance handbooks into vector embeddings. Connects Gemini LLM to live Python calculation tools for natural language credit queries.", honesty: null }}
        ];

        /* MODE SWITCHING */
        function switchMode(mode) {{
            document.querySelectorAll('.mode-tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.mode-section').forEach(s => s.classList.remove('active'));

            document.getElementById('tab-' + mode).classList.add('active');
            document.getElementById('mode-' + mode).classList.add('active');

            if (mode === 'pipeline') {{
                renderNodes();
                setTimeout(drawFlowLines, 100);
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

        /* POPULATE ANALYTICS TABLES */
        function populateTables() {{
            // Basel Table
            const bBody = document.querySelector('#t-basel tbody');
            if (bBody && DATA.basel_summary) {{
                bBody.innerHTML = DATA.basel_summary.map(r => `
                    <tr>
                        <td><strong>${{r.segment || r.Grade || 'Overall'}}</strong></td>
                        <td>${{(r.count || 0).toLocaleString()}}</td>
                        <td>$${{((r.total_ead || 0)/1e6).toFixed(2)}}M</td>
                        <td>$${{((r.irb_rwa || 0)/1e6).toFixed(2)}}M</td>
                        <td>$${{((r.std_rwa || 0)/1e6).toFixed(2)}}M</td>
                        <td><strong style="color:var(--accent-blue);">${{(r.irb_rw_pct || 0).toFixed(1)}}%</strong></td>
                    </tr>
                `).join('');
            }}

            // CECL Table
            const cBody = document.querySelector('#t-cecl tbody');
            if (cBody && DATA.ifrs9_cecl) {{
                cBody.innerHTML = DATA.ifrs9_cecl.map(r => `
                    <tr>
                        <td><strong>${{r.accounting_framework || r.framework}}</strong></td>
                        <td>$${{((r.total_ead_usd || r.ead || 0)/1e6).toFixed(2)}}M</td>
                        <td>$${{((r.total_provision_usd || r.provision || 0)/1e6).toFixed(2)}}M</td>
                        <td><strong style="color:var(--accent-cyan);">${{(r.coverage_ratio_pct || 0).toFixed(2)}}%</strong></td>
                        <td>${{r.methodology_summary || ''}}</td>
                    </tr>
                `).join('');
            }}

            // Vintage Maturity Table
            const vmBody = document.querySelector('#t-vintage-mat tbody');
            if (vmBody && DATA.vintage_maturity) {{
                vmBody.innerHTML = DATA.vintage_maturity.map(r => `
                    <tr>
                        <td><strong>${{r.vintage_year}}</strong></td>
                        <td>${{(r.total_loans || 0).toLocaleString()}}</td>
                        <td>${{((r.mob_12_default_rate || 0)*100).toFixed(2)}}%</td>
                        <td>${{((r.mob_18_default_rate || 0)*100).toFixed(2)}}%</td>
                        <td><strong style="color:var(--accent-rose);">${{((r.mob_24_default_rate || 0)*100).toFixed(2)}}%</strong></td>
                    </tr>
                `).join('');
            }}

            // Roll Rate Proxy Table
            const rrBody = document.querySelector('#t-rollrate tbody');
            if (rrBody && DATA.roll_rate_proxy) {{
                rrBody.innerHTML = DATA.roll_rate_proxy.map(r => `
                    <tr>
                        <td><strong>${{r.vintage_year}}</strong></td>
                        <td>${{(r.total_loans || 0).toLocaleString()}}</td>
                        <td>${{(r.pct_current || 0).toFixed(1)}}%</td>
                        <td>${{(r.pct_grace || 0).toFixed(1)}}%</td>
                        <td>${{(r.pct_late_16_30 || 0).toFixed(1)}}%</td>
                        <td>${{(r.pct_late_31_120 || 0).toFixed(1)}}%</td>
                        <td><strong style="color:var(--accent-rose);">${{(r.pct_default || 0).toFixed(1)}}%</strong></td>
                        <td>${{(r.pct_fully_paid || 0).toFixed(1)}}%</td>
                    </tr>
                `).join('');
            }}

            // Transition Matrix Table
            const trBody = document.querySelector('#t-trans tbody');
            if (trBody && DATA.transition_matrix) {{
                trBody.innerHTML = DATA.transition_matrix.map(r => `
                    <tr>
                        <td><strong>Grade ${{r.grade}}</strong></td>
                        <td>${{(r.total_loans || 0).toLocaleString()}}</td>
                        <td>${{(r.pct_fully_paid || 0).toFixed(1)}}%</td>
                        <td>${{(r.pct_current || 0).toFixed(1)}}%</td>
                        <td>${{(r.pct_late || 0).toFixed(1)}}%</td>
                        <td><strong style="color:var(--accent-rose);">${{(r.pct_default || 0).toFixed(1)}}%</strong></td>
                    </tr>
                `).join('');
            }}

            // Staging Summary Table
            const stBody = document.querySelector('#t-staging tbody');
            if (stBody && DATA.staging_summary) {{
                stBody.innerHTML = DATA.staging_summary.map(r => `
                    <tr>
                        <td><strong>${{r.stage}}</strong></td>
                        <td>${{(r.count || 0).toLocaleString()}}</td>
                        <td>$${{((r.total_ead || 0)/1e6).toFixed(2)}}M</td>
                        <td>$${{((r.total_ecl || 0)/1e6).toFixed(2)}}M</td>
                        <td><strong style="color:var(--accent-cyan);">${{(r.coverage_pct || (r.coverage_ratio*100) || 0).toFixed(2)}}%</strong></td>
                    </tr>
                `).join('');
            }}

            // Performing Staging vs Basel Table
            const pfBody = document.querySelector('#t-perf tbody');
            if (pfBody && DATA.ifrs9_basel_perf) {{
                pfBody.innerHTML = DATA.ifrs9_basel_perf.map(r => `
                    <tr>
                        <td><strong>${{r.framework_scope || r.framework}}</strong></td>
                        <td>$${{((r.total_ead_usd || 0)/1e6).toFixed(2)}}M</td>
                        <td>$${{((r.total_provision_usd || 0)/1e6).toFixed(2)}}M</td>
                        <td><strong style="color:var(--accent-blue);">${{(r.coverage_ratio_pct || 0).toFixed(2)}}%</strong></td>
                        <td>${{r.description || ''}}</td>
                    </tr>
                `).join('');
            }}

            // Validation Summary Table
            const vBody = document.querySelector('#t-val tbody');
            if (vBody && DATA.validation_summary) {{
                vBody.innerHTML = DATA.validation_summary.map(r => `
                    <tr>
                        <td><strong>${{r.model_name}}</strong></td>
                        <td>${{r.sample_partition}}</td>
                        <td><strong style="color:var(--accent-emerald);">${{(r.auc || 0).toFixed(4)}}</strong></td>
                        <td>${{(r.gini || 0).toFixed(4)}}</td>
                        <td>${{(r.ks_stat || 0).toFixed(4)}}</td>
                        <td>${{(r.brier_score || 0).toFixed(5)}}</td>
                        <td>${{(r.hl_p_value || 0).toFixed(5)}}</td>
                    </tr>
                `).join('');
            }}

            // CSI Table
            const csBody = document.querySelector('#t-csi tbody');
            if (csBody && DATA.csi_summary) {{
                csBody.innerHTML = DATA.csi_summary.map(r => `
                    <tr>
                        <td>${{r.model_name || 'Model B'}}</td>
                        <td><strong>${{r.variable_name}}</strong></td>
                        <td>${{(r.csi_value || 0).toFixed(4)}}</td>
                        <td><span style="color:var(--accent-emerald);">${{r.stability_band || 'Stable (CSI < 0.10)'}}</span></td>
                    </tr>
                `).join('');
            }}

            // Coefs Table
            const coBody = document.querySelector('#t-coefs tbody');
            if (coBody && DATA.coefs_b) {{
                coBody.innerHTML = DATA.coefs_b.map(r => `
                    <tr>
                        <td><strong>${{r.feature || r.variable}}</strong></td>
                        <td>${{(r.coef || 0).toFixed(4)}}</td>
                        <td>${{(r.std_err || 0).toFixed(4)}}</td>
                        <td>${{(r.p_value || 0).toFixed(5)}}</td>
                        <td><span style="color:var(--accent-emerald);">Yes (p < 0.001)</span></td>
                    </tr>
                `).join('');
            }}

            // Rating Grades Table
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

            // Governance Target Reconciliation Table
            const gtBody = document.querySelector('#t-gov-target tbody');
            if (gtBody && DATA.target_rec) {{
                gtBody.innerHTML = DATA.target_rec.map(r => `
                    <tr>
                        <td><strong>${{r.category || r.metric}}</strong></td>
                        <td>${{(r.count || 0).toLocaleString()}}</td>
                        <td>${{(r.pct || 0).toFixed(2)}}%</td>
                        <td>${{r.description || r.definition || ''}}</td>
                    </tr>
                `).join('');
            }}

            // Governance Samples Table
            const gsBody = document.querySelector('#t-gov-samples tbody');
            if (gsBody && DATA.sample_summary) {{
                gsBody.innerHTML = DATA.sample_summary.map(r => `
                    <tr>
                        <td><strong>${{r.sample_partition || r.partition}}</strong></td>
                        <td>${{(r.n_loans || r.count || 0).toLocaleString()}}</td>
                        <td>${{(r.n_defaults || r.defaults || 0).toLocaleString()}}</td>
                        <td><strong style="color:var(--accent-rose);">${{((r.default_rate || 0)*100).toFixed(2)}}%</strong></td>
                        <td>${{r.issue_dates || r.vintage_range || ''}}</td>
                    </tr>
                `).join('');
            }}
        }}

        /* CHART INITIALIZATIONS */
        function initCharts() {{
            // LGD Chart
            const ctxLgd = document.getElementById('c-lgd');
            if (ctxLgd && DATA.lgd_calib) {{
                new Chart(ctxLgd, {{
                    type: 'bar',
                    data: {{
                        labels: DATA.lgd_calib.map(r => 'Decile ' + r.decile),
                        datasets: [
                            {{ label: 'Observed LGD', data: DATA.lgd_calib.map(r => (r.observed_lgd*100).toFixed(1)), backgroundColor: '#38bdf8' }},
                            {{ label: 'Predicted LGD', data: DATA.lgd_calib.map(r => (r.predicted_lgd*100).toFixed(1)), backgroundColor: '#818cf8' }}
                        ]
                    }},
                    options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ labels: {{ color: '#94a3b8' }} }} }}, scales: {{ y: {{ ticks: {{ color: '#64748b' }} }}, x: {{ ticks: {{ color: '#64748b' }} }} }} }}
                }});
            }}

            // Timing Chart
            const ctxTiming = document.getElementById('c-timing');
            if (ctxTiming && DATA.default_timing) {{
                new Chart(ctxTiming, {{
                    type: 'line',
                    data: {{
                        labels: DATA.default_timing.map(r => 'MOB ' + r.mob),
                        datasets: [{{ label: 'Default Count', data: DATA.default_timing.map(r => r.default_count), borderColor: '#fb7185', backgroundColor: 'rgba(251, 113, 133, 0.1)', fill: true, tension: 0.3 }}]
                    }},
                    options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ labels: {{ color: '#94a3b8' }} }} }}, scales: {{ y: {{ ticks: {{ color: '#64748b' }} }}, x: {{ ticks: {{ color: '#64748b' }} }} }} }}
                }});
            }}

            // Vintage Chart
            const ctxVintage = document.getElementById('c-vintage');
            if (ctxVintage && DATA.vintage_curves) {{
                const vintages = [...new Set(DATA.vintage_curves.map(r => r.vintage_year))];
                const colors = ['#38bdf8', '#22d3ee', '#818cf8', '#34d399', '#fb7185', '#fbbf24', '#a855f7', '#ec4899'];
                const datasets = vintages.map((v, i) => ({{
                    label: 'Vintage ' + v,
                    data: DATA.vintage_curves.filter(r => r.vintage_year === v).map(r => (r.cumulative_default_rate * 100).toFixed(2)),
                    borderColor: colors[i % colors.length],
                    borderWidth: 2,
                    fill: false,
                    tension: 0.2
                }}));
                new Chart(ctxVintage, {{
                    type: 'line',
                    data: {{ labels: Array.from({{length: 49}}, (_, i) => 'MOB ' + i), datasets: datasets }},
                    options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ labels: {{ color: '#94a3b8' }} }} }}, scales: {{ y: {{ ticks: {{ color: '#64748b' }} }}, x: {{ ticks: {{ color: '#64748b' }} }} }} }}
                }});
            }}

            // Lifetime Hazard Chart
            const ctxLife = document.getElementById('c-lifetime');
            if (ctxLife && DATA.lifetime_pd) {{
                new Chart(ctxLife, {{
                    type: 'line',
                    data: {{
                        labels: DATA.lifetime_pd.map(r => 'Month ' + r.month),
                        datasets: [
                            {{ label: 'Cumulative Lifetime PD (%)', data: DATA.lifetime_pd.map(r => (r.cum_pd*100).toFixed(2)), borderColor: '#38bdf8', borderWidth: 2 }},
                            {{ label: 'Marginal Monthly Hazard (%)', data: DATA.lifetime_pd.map(r => (r.marginal_pd*100).toFixed(2)), borderColor: '#fbbf24', borderWidth: 1.5, borderDash: [4, 4] }}
                        ]
                    }},
                    options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ labels: {{ color: '#94a3b8' }} }} }}, scales: {{ y: {{ ticks: {{ color: '#64748b' }} }}, x: {{ ticks: {{ color: '#64748b' }} }} }} }}
                }});
            }}

            // Grade Default Rate Chart
            const ctxGradeDr = document.getElementById('c-grade-dr');
            if (ctxGradeDr && DATA.rating_grades_b) {{
                new Chart(ctxGradeDr, {{
                    type: 'bar',
                    data: {{
                        labels: DATA.rating_grades_b.map(r => 'Grade ' + r.grade),
                        datasets: [{{ label: 'Observed Default Rate (%)', data: DATA.rating_grades_b.map(r => (r.observed_default_rate * 100).toFixed(2)), backgroundColor: '#fb7185' }}]
                    }},
                    options: {{ responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ labels: {{ color: '#94a3b8' }} }} }}, scales: {{ y: {{ ticks: {{ color: '#64748b' }} }}, x: {{ ticks: {{ color: '#64748b' }} }} }} }}
                }});
            }}

            // IV Chart
            const ctxIv = document.getElementById('c-iv');
            if (ctxIv && DATA.iv_summary) {{
                const topIv = DATA.iv_summary.slice(0, 15);
                new Chart(ctxIv, {{
                    type: 'bar',
                    data: {{
                        labels: topIv.map(r => r.feature || r.variable),
                        datasets: [{{ label: 'Information Value (IV)', data: topIv.map(r => r.iv), backgroundColor: '#34d399' }}]
                    }},
                    options: {{ indexAxis: 'y', responsive: true, maintainAspectRatio: false, plugins: {{ legend: {{ labels: {{ color: '#94a3b8' }} }} }}, scales: {{ y: {{ ticks: {{ color: '#64748b' }} }}, x: {{ ticks: {{ color: '#64748b' }} }} }} }}
                }});
            }}
        }}

        /* PIPELINE DAG RENDERER */
        function renderNodes() {{
            const container = document.getElementById('nodes-grid');
            if (!container) return;
            container.innerHTML = STAGES.map((s, idx) => `
                <div class="stage-card ${{s.honesty ? 'honesty-card' : ''}}" onclick="openDrawer(${{idx}})">
                    <div>
                        <div class="stage-header">
                            <span class="stage-num">STAGE ${{String(s.num).padStart(2, '0')}}</span>
                            ${{s.honesty ? `<span class="honesty-badge">PROX / METHOD</span>` : ''}}
                        </div>
                        <h3 class="stage-title">${{s.title}}</h3>
                        <div class="stage-modules">${{s.modules.split('/').pop()}}</div>
                    </div>
                    <div class="stage-figure">
                        <div style="color: var(--text-dim); text-transform: uppercase; font-size: 9px; letter-spacing: 0.5px; margin-bottom: 2px;">Artefact / Metric</div>
                        <div>${{s.figure}}</div>
                    </div>
                </div>
            `).join('');
        }}

        function openDrawer(idx) {{
            const s = STAGES[idx];
            document.getElementById('d-tag').innerText = `STAGE ${{String(s.num).padStart(2, '0')}}`;
            document.getElementById('d-title').innerText = s.title;
            document.getElementById('d-modules').innerHTML = `<a href="${{REPO_BASE}}${{s.modules}}" target="_blank">${{s.modules}} ↗</a>`;
            document.getElementById('d-figures').innerHTML = `<strong>Artefact:</strong> <a href="${{REPO_BASE}}${{s.artefact}}" target="_blank">${{s.artefact}} ↗</a><br><br>${{s.figure}}`;
            document.getElementById('d-logic').innerText = s.logic;

            const hContainer = document.getElementById('d-honesty-container');
            const hBox = document.getElementById('d-honesty');
            if (s.honesty) {{
                hBox.innerText = s.honesty;
                hContainer.style.display = 'block';
            }} else {{
                hContainer.style.display = 'none';
            }}

            document.getElementById('drawer').classList.add('active');
        }}

        function closeDrawer(e) {{
            if (!e || e.target.id === 'drawer') {{
                document.getElementById('drawer').classList.remove('active');
            }}
        }}

        function drawFlowLines() {{
            const svg = document.getElementById('flow-svg');
            const cards = document.querySelectorAll('.stage-card');
            if (!svg || cards.length < 12 || window.innerWidth <= 1024) return;

            const containerRect = document.querySelector('.dag-flow-container').getBoundingClientRect();

            let pathD = '';
            for (let i = 0; i < cards.length - 1; i++) {{
                const rect1 = cards[i].getBoundingClientRect();
                const rect2 = cards[i+1].getBoundingClientRect();

                const x1 = rect1.left + rect1.width / 2 - containerRect.left;
                const y1 = rect1.top + rect1.height / 2 - containerRect.top;
                const x2 = rect2.left + rect2.width / 2 - containerRect.left;
                const y2 = rect2.top + rect2.height / 2 - containerRect.top;

                const dx = x2 - x1;
                const cx1 = x1 + dx * 0.5;
                const cy1 = y1;
                const cx2 = x1 + dx * 0.5;
                const cy2 = y2;

                pathD += `M ${{x1}} ${{y1}} C ${{cx1}} ${{cy1}}, ${{cx2}} ${{cy2}}, ${{x2}} ${{y2}} `;
            }}

            svg.innerHTML = `
                <defs>
                    <linearGradient id="flow-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                        <stop offset="0%" stop-color="#38bdf8" stop-opacity="0.4"/>
                        <stop offset="50%" stop-color="#818cf8" stop-opacity="0.3"/>
                        <stop offset="100%" stop-color="#34d399" stop-opacity="0.4"/>
                    </linearGradient>
                </defs>
                <path d="${{pathD}}" fill="none" stroke="url(#flow-grad)" stroke-width="4" stroke-linecap="round"/>
                <path d="${{pathD}}" fill="none" stroke="#38bdf8" stroke-width="2" stroke-dasharray="6,12" opacity="0.6">
                    <animate attributeName="stroke-dashoffset" from="36" to="0" dur="2s" repeatCount="indefinite" />
                </path>
            `;
        }}

        /* INITIALIZATION */
        window.addEventListener('DOMContentLoaded', () => {{
            populateTables();
            initCharts();
            renderNodes();

            // Hash Routing
            const hash = window.location.hash.replace('#', '');
            if (hash === 'pipeline') {{
                switchMode('pipeline');
            }} else if (hash === 'governance') {{
                switchMode('governance');
            }} else if (hash.startsWith('analytics-p')) {{
                switchMode('analytics');
                const panelIdx = parseInt(hash.replace('analytics-p', ''), 10);
                if (!isNaN(panelIdx)) showPanel(panelIdx);
            }} else {{
                switchMode('analytics');
            }}
        }});

        window.addEventListener('resize', drawFlowLines);
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
