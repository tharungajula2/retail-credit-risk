"""
Build script to regenerate dashboard JSON and compile a self-contained HTML risk dashboard.
"""

import json
import logging
from pathlib import Path
from creditrisk.reporting.dashboard_data import build_dashboard_json

logger = logging.getLogger(__name__)

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Retail Credit Risk Portfolio Dashboard</title>
  <!-- Chart.js CDN -->
  <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
  <style>
    /* Institutional & Restrained Financial Dashboard Styles */
    :root {
      --bg-main: #f8fafc;
      --bg-card: #ffffff;
      --text-main: #0f172a;
      --text-muted: #475569;
      --text-light: #64748b;
      --border-color: #cbd5e1;
      --border-light: #e2e8f0;
      
      --navy-primary: #1e3a8a;
      --navy-secondary: #3b82f6;
      --slate-accent: #334155;
      
      --accent-danger: #991b1b;
      --accent-warning: #d97706;
      --accent-success: #166534;
      
      --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      background-color: var(--bg-main);
      color: var(--text-main);
      font-family: var(--font-family);
      line-height: 1.5;
      padding: 24px;
      -webkit-font-smoothing: antialiased;
    }

    .container {
      max-width: 1400px;
      margin: 0 auto;
    }

    /* Header */
    header {
      background-color: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 4px;
      padding: 20px 24px;
      margin-bottom: 24px;
    }

    .header-title-row {
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
      border-bottom: 2px solid var(--navy-primary);
      padding-bottom: 12px;
      margin-bottom: 20px;
    }

    h1 {
      font-size: 22px;
      font-weight: 700;
      color: var(--navy-primary);
      letter-spacing: -0.3px;
      text-transform: uppercase;
    }

    .as-of-date {
      font-size: 13px;
      color: var(--text-muted);
      font-weight: 500;
    }

    /* Metric Cards Grid */
    .metrics-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
    }

    .metric-card {
      background-color: #f1f5f9;
      border: 1px solid var(--border-light);
      border-left: 4px solid var(--navy-primary);
      border-radius: 2px;
      padding: 12px 16px;
    }

    .metric-label {
      font-size: 11px;
      text-transform: uppercase;
      font-weight: 600;
      color: var(--text-muted);
      letter-spacing: 0.5px;
      margin-bottom: 4px;
    }

    .metric-value {
      font-size: 20px;
      font-weight: 700;
      color: var(--text-main);
    }

    .metric-sub {
      font-size: 11px;
      color: var(--text-light);
      margin-top: 2px;
    }

    /* Dashboard Sections */
    .section-title {
      font-size: 16px;
      font-weight: 700;
      color: var(--navy-primary);
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 16px;
      border-left: 3px solid var(--navy-primary);
      padding-left: 8px;
    }

    .grid-2 {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
      margin-bottom: 24px;
    }

    .grid-3 {
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 20px;
      margin-bottom: 24px;
    }

    .card {
      background-color: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 4px;
      padding: 18px;
      display: flex;
      flex-direction: column;
    }

    .card-title {
      font-size: 14px;
      font-weight: 600;
      color: var(--slate-accent);
      margin-bottom: 14px;
      border-bottom: 1px solid var(--border-light);
      padding-bottom: 6px;
    }

    .chart-container {
      position: relative;
      flex-grow: 1;
      min-height: 260px;
      width: 100%;
    }

    /* Tables */
    table.data-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 12px;
      text-align: left;
    }

    table.data-table th {
      background-color: #f1f5f9;
      color: var(--slate-accent);
      font-weight: 600;
      text-transform: uppercase;
      font-size: 11px;
      padding: 8px 10px;
      border-bottom: 2px solid var(--border-color);
    }

    table.data-table td {
      padding: 7px 10px;
      border-bottom: 1px solid var(--border-light);
      color: var(--text-main);
    }

    table.data-table tr:hover {
      background-color: #f8fafc;
    }

    .text-right {
      text-align: right;
    }

    .text-center {
      text-align: center;
    }

    /* Transition Matrix Heatmap Table */
    .heatmap-cell {
      font-weight: 600;
    }

    /* Limitations Register / Footer */
    footer {
      background-color: #f1f5f9;
      border: 1px solid var(--border-color);
      border-radius: 4px;
      padding: 16px 20px;
      margin-top: 32px;
      font-size: 11px;
      color: var(--text-muted);
    }

    .footer-title {
      font-weight: 700;
      color: var(--navy-primary);
      text-transform: uppercase;
      margin-bottom: 6px;
      letter-spacing: 0.5px;
    }

    .footer-list {
      list-style-type: disc;
      padding-left: 18px;
      line-height: 1.6;
    }

    @media (max-width: 1024px) {
      .grid-2, .grid-3 {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>

  <div class="container">
    <!-- Header -->
    <header>
      <div class="header-title-row">
        <div>
          <h1>Retail Credit Risk Portfolio Dashboard</h1>
          <div class="as-of-date">Portfolio Risk Committee Reporting | As-of: Q4 2024</div>
        </div>
        <div style="font-size: 11px; color: var(--text-light); text-align: right;">
          RESTRICTED — INTERNAL RISK GOVERNANCE
        </div>
      </div>

      <!-- Portfolio Headline Cards -->
      <div class="metrics-grid" id="headline-grid">
        <!-- Injected via JS -->
      </div>
    </header>

    <!-- Section 2: Risk Segmentation -->
    <div class="section-title">1. Risk Segmentation</div>
    <div class="grid-2">
      <div class="card">
        <div class="card-title">Model B Rating Grade Master Scale</div>
        <div style="overflow-x: auto;">
          <table class="data-table" id="table-rating-grades">
            <thead>
              <tr>
                <th>Grade</th>
                <th>Score Range</th>
                <th class="text-right">No. Loans</th>
                <th class="text-right">Observed Default Rate</th>
              </tr>
            </thead>
            <tbody></tbody>
          </table>
        </div>
      </div>

      <div class="card">
        <div class="card-title">Observed Default Rate by Rating Grade</div>
        <div class="chart-container">
          <canvas id="chart-default-rate-grade"></canvas>
        </div>
      </div>
    </div>

    <!-- Section 3: Expected Loss & Capital -->
    <div class="section-title">2. Expected Loss & Capital</div>
    <div class="grid-3">
      <div class="card">
        <div class="card-title">Expected Loss (EL) by Grade ($)</div>
        <div class="chart-container">
          <canvas id="chart-el-by-grade"></canvas>
        </div>
      </div>

      <div class="card">
        <div class="card-title">Basel RWA: IRB vs Standardised ($)</div>
        <div class="chart-container">
          <canvas id="chart-rwa-comparison"></canvas>
        </div>
      </div>

      <div class="card">
        <div class="card-title">IRB Risk Weight (%) by Grade</div>
        <div class="chart-container">
          <canvas id="chart-rw-by-grade"></canvas>
        </div>
      </div>
    </div>

    <!-- Section 4: IFRS 9 Provisioning -->
    <div class="section-title">3. IFRS 9 & CECL Provisioning</div>
    <div class="grid-3">
      <div class="card">
        <div class="card-title">Loan Staging Distribution (Loans)</div>
        <div class="chart-container">
          <canvas id="chart-staging-donut"></canvas>
        </div>
      </div>

      <div class="card">
        <div class="card-title">ECL Provision by Stage ($)</div>
        <div class="chart-container">
          <canvas id="chart-ecl-by-stage"></canvas>
        </div>
      </div>

      <div class="card">
        <div class="card-title">Accounting Framework Provisions Comparison ($)</div>
        <div class="chart-container">
          <canvas id="chart-framework-comparison"></canvas>
        </div>
      </div>
    </div>

    <!-- Section 5: Portfolio Trends -->
    <div class="section-title">4. Portfolio Trends & Transitions</div>
    <div class="grid-3">
      <div class="card" style="grid-column: span 2;">
        <div class="card-title">Vintage Cumulative Default Curves (MOB 0–24)</div>
        <div class="chart-container">
          <canvas id="chart-vintage-curves"></canvas>
        </div>
      </div>

      <div class="card">
        <div class="card-title">Vintage Default Rate at MOB 12 (%)</div>
        <div class="chart-container">
          <canvas id="chart-vintage-mob12"></canvas>
        </div>
      </div>
    </div>

    <div class="grid-2">
      <div class="card" style="grid-column: span 2;">
        <div class="card-title">Rating Grade Transition Matrix (State Distribution at Maturity)</div>
        <div style="overflow-x: auto;">
          <table class="data-table" id="table-transition-matrix">
            <thead>
              <tr>
                <th>Origination Grade</th>
                <th class="text-right">Total Loans</th>
                <th class="text-right">Fully Paid (%)</th>
                <th class="text-right">Current (%)</th>
                <th class="text-right">Late (%)</th>
                <th class="text-right">Default (%)</th>
              </tr>
            </thead>
            <tbody></tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Section 6: Model Validation -->
    <div class="section-title">5. Model Validation & Lifetime PD</div>
    <div class="grid-2">
      <div class="card">
        <div class="card-title">Model B Performance (Train vs Test vs OOT)</div>
        <div class="chart-container">
          <canvas id="chart-model-validation"></canvas>
        </div>
      </div>

      <div class="card">
        <div class="card-title">Lifetime Cumulative PD Term Structure (%)</div>
        <div class="chart-container">
          <canvas id="chart-lifetime-pd"></canvas>
        </div>
      </div>
    </div>

    <!-- Limitations Register / Footer -->
    <footer>
      <div class="footer-title">Limitations & Governance Register</div>
      <ul class="footer-list">
        <li><strong>Credit Conversion Factor (CCF):</strong> CCF metrics utilize synthetic estimates based on standardized portfolio parameters rather than empirical draw-down history.</li>
        <li><strong>Roll-Rate Analysis:</strong> Migration probabilities use delinquency state transitions as a proxy for multi-period transition matrices.</li>
        <li><strong>Exposure at Default (EAD):</strong> EAD values are approximated using outstanding balance plus estimated unadvanced commitment drawdowns.</li>
        <li><strong>Usage Scope:</strong> Prepared exclusively for executive risk committee review and regulatory capital oversight.</li>
      </ul>
    </footer>
  </div>

  <script>
    // Embedded Data Const
    const DATA = __EMBEDDED_DATA__;

    // Institutional Chart Colors (Muted, professional Palette)
    const COLORS = {
      navy: '#1e3a8a',
      blue: '#3b82f6',
      slate: '#475569',
      slateLight: '#94a3b8',
      amber: '#d97706',
      red: '#991b1b',
      green: '#166534',
      teal: '#0d9488',
      purple: '#6b21a8',
      palette: ['#1e3a8a', '#3b82f6', '#0d9488', '#d97706', '#991b1b', '#6b21a8', '#475569', '#166534']
    };

    // Helper functions
    function formatCurrency(val) {
      if (val === null || val === undefined) return 'N/A';
      return '$' + Number(val).toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 0 });
    }

    function formatNumber(val) {
      if (val === null || val === undefined) return 'N/A';
      return Number(val).toLocaleString();
    }

    function formatPercent(val, decimals = 2) {
      if (val === null || val === undefined) return 'N/A';
      return Number(val).toFixed(decimals) + '%';
    }

    // Chart.js Global Options for Institutional Style
    Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif';
    Chart.defaults.font.size = 11;
    Chart.defaults.color = '#475569';
    Chart.defaults.plugins.legend.labels.boxWidth = 12;
    Chart.defaults.plugins.legend.labels.usePointStyle = true;

    document.addEventListener('DOMContentLoaded', () => {
      renderHeadline();
      renderRatingGrades();
      renderExpectedLossAndCapital();
      renderIFRS9Staging();
      renderTrends();
      renderValidation();
    });

    // 1. Headline
    function renderHeadline() {
      const h = DATA.portfolio_headline || {};
      const grid = document.getElementById('headline-grid');

      const items = [
        { label: 'Total Loans', val: formatNumber(h.total_loans), sub: 'Active portfolio count' },
        { label: 'Total EAD', val: formatCurrency(h.total_ead), sub: 'Exposure at default' },
        { label: 'Expected Loss (EL)', val: formatCurrency(h.total_el), sub: `EL Rate: ${formatPercent(h.el_rate)}` },
        { label: 'Basel IRB RWA', val: formatCurrency(h.total_rwa_irb), sub: `Avg RW: ${formatPercent(h.avg_risk_weight)}` },
        { label: 'IFRS 9 ECL Provision', val: formatCurrency(h.total_ecl_ifrs9), sub: `Coverage: ${formatPercent(h.ecl_coverage)}` },
        { label: 'Portfolio Mean PD / LGD', val: `${formatPercent((h.mean_pd||0)*100, 1)} / ${formatPercent((h.mean_lgd||0)*100, 1)}`, sub: 'Weighted average' }
      ];

      grid.innerHTML = items.map(item => `
        <div class="metric-card">
          <div class="metric-label">${item.label}</div>
          <div class="metric-value">${item.val}</div>
          <div class="metric-sub">${item.sub}</div>
        </div>
      `).join('');
    }

    // 2. Risk Segmentation
    function renderRatingGrades() {
      const grades = DATA.rating_grades || [];

      // Render Table
      const tbody = document.querySelector('#table-rating-grades tbody');
      tbody.innerHTML = grades.map(g => `
        <tr>
          <td style="font-weight: 600;">Grade ${g.grade}</td>
          <td>${g.score_range}</td>
          <td class="text-right">${formatNumber(g.n_loans)}</td>
          <td class="text-right">${formatPercent(g.default_rate * 100, 2)}</td>
        </tr>
      `).join('');

      // Chart: Default Rate by Grade
      new Chart(document.getElementById('chart-default-rate-grade'), {
        type: 'bar',
        data: {
          labels: grades.map(g => 'Grade ' + g.grade),
          datasets: [{
            label: 'Observed Default Rate (%)',
            data: grades.map(g => g.default_rate * 100),
            backgroundColor: COLORS.navy,
            borderRadius: 2
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            y: { title: { display: true, text: 'Default Rate (%)' }, beginAtZero: true }
          }
        }
      });
    }

    // 3. Expected Loss & Capital
    function renderExpectedLossAndCapital() {
      const elData = DATA.el_by_grade || [];
      const capData = DATA.capital_by_grade || [];

      // EL by Grade
      new Chart(document.getElementById('chart-el-by-grade'), {
        type: 'bar',
        data: {
          labels: elData.map(d => 'Grade ' + d.grade),
          datasets: [{
            label: 'Total Expected Loss ($)',
            data: elData.map(d => d.total_el),
            backgroundColor: COLORS.amber,
            borderRadius: 2
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: { y: { title: { display: true, text: 'Expected Loss ($)' }, beginAtZero: true } }
        }
      });

      // IRB vs Standardised RWA
      new Chart(document.getElementById('chart-rwa-comparison'), {
        type: 'bar',
        data: {
          labels: capData.map(d => 'Grade ' + d.grade),
          datasets: [
            { label: 'IRB RWA ($)', data: capData.map(d => d.irb_rwa), backgroundColor: COLORS.navy, borderRadius: 2 },
            { label: 'EAD Baseline ($)', data: capData.map(d => d.ead), backgroundColor: COLORS.slateLight, borderRadius: 2 }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: { y: { title: { display: true, text: 'Amount ($)' }, beginAtZero: true } }
        }
      });

      // Risk Weight by Grade
      new Chart(document.getElementById('chart-rw-by-grade'), {
        type: 'bar',
        data: {
          labels: capData.map(d => 'Grade ' + d.grade),
          datasets: [{
            label: 'IRB Risk Weight (%)',
            data: capData.map(d => d.risk_weight),
            backgroundColor: COLORS.blue,
            borderRadius: 2
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: { y: { title: { display: true, text: 'Risk Weight (%)' }, beginAtZero: true } }
        }
      });
    }

    // 4. IFRS 9 & CECL Provisioning
    function renderIFRS9Staging() {
      const staging = DATA.staging || [];
      const ecl = DATA.ecl_by_stage || [];
      const fw = DATA.framework_comparison || [];

      // Staging Donut
      new Chart(document.getElementById('chart-staging-donut'), {
        type: 'doughnut',
        data: {
          labels: staging.map(s => s.stage),
          datasets: [{
            data: staging.map(s => s.n_loans),
            backgroundColor: [COLORS.navy, COLORS.amber, COLORS.red]
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { position: 'bottom' } }
        }
      });

      // ECL by Stage
      new Chart(document.getElementById('chart-ecl-by-stage'), {
        type: 'bar',
        data: {
          labels: ecl.map(e => e.stage),
          datasets: [{
            label: 'ECL Provision ($)',
            data: ecl.map(e => e.total_ecl),
            backgroundColor: [COLORS.navy, COLORS.amber, COLORS.red],
            borderRadius: 2
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: { y: { title: { display: true, text: 'ECL ($)' }, beginAtZero: true } }
        }
      });

      // Framework Comparison
      new Chart(document.getElementById('chart-framework-comparison'), {
        type: 'bar',
        data: {
          labels: fw.map(f => f.framework),
          datasets: [{
            label: 'Total Provision ($)',
            data: fw.map(f => f.total_provision_usd),
            backgroundColor: [COLORS.slate, COLORS.navy, COLORS.teal, COLORS.amber],
            borderRadius: 2
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: { y: { title: { display: true, text: 'Provision ($)' }, beginAtZero: true } }
        }
      });
    }

    // 5. Portfolio Trends & Transitions
    function renderTrends() {
      const vCurves = DATA.vintage_curves || [];
      const vMat = DATA.vintage_maturity || [];
      const trans = DATA.transition_matrix || [];

      // Vintage Curves
      const mobKeys = Array.from({length: 25}, (_, i) => `mob_${i}`);
      const datasets = vCurves.map((v, idx) => ({
        label: `Vintage ${v.vintage_year}`,
        data: mobKeys.map(k => (v[k] || 0) * 100),
        borderColor: COLORS.palette[idx % COLORS.palette.length],
        backgroundColor: 'transparent',
        borderWidth: 2,
        pointRadius: 0
      }));

      new Chart(document.getElementById('chart-vintage-curves'), {
        type: 'line',
        data: {
          labels: Array.from({length: 25}, (_, i) => `MOB ${i}`),
          datasets: datasets
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: { y: { title: { display: true, text: 'Cumulative Default Rate (%)' }, beginAtZero: true } }
        }
      });

      // Vintage MOB 12
      new Chart(document.getElementById('chart-vintage-mob12'), {
        type: 'bar',
        data: {
          labels: vMat.map(v => v.vintage_year),
          datasets: [{
            label: 'Default Rate at MOB 12 (%)',
            data: vMat.map(v => v.default_rate_mob_12_pct),
            backgroundColor: COLORS.navy,
            borderRadius: 2
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: { y: { title: { display: true, text: 'Default Rate (%)' }, beginAtZero: true } }
        }
      });

      // Transition Matrix Heatmap Table
      const tbody = document.querySelector('#table-transition-matrix tbody');
      tbody.innerHTML = trans.map(t => {
        const defPct = t.default * 100;
        // Heatmap color intensity for Default column based on risk severity
        let bgStyle = 'background-color: #f8fafc;';
        if (defPct > 20) bgStyle = 'background-color: #fecaca; color: #7f1d1d;';
        else if (defPct > 15) bgStyle = 'background-color: #fed7aa; color: #7c2d12;';
        else if (defPct > 10) bgStyle = 'background-color: #fef08a; color: #713f12;';

        return `
          <tr>
            <td style="font-weight: 600;">Grade ${t.grade}</td>
            <td class="text-right">${formatNumber(t.total_loans)}</td>
            <td class="text-right">${formatPercent(t.fully_paid * 100, 1)}</td>
            <td class="text-right">${formatPercent(t.current * 100, 1)}</td>
            <td class="text-right">${formatPercent(t.late * 100, 1)}</td>
            <td class="text-right heatmap-cell" style="${bgStyle}">${formatPercent(defPct, 1)}</td>
          </tr>
        `;
      }).join('');
    }

    // 6. Model Validation & Lifetime PD
    function renderValidation() {
      const val = DATA.validation || {};
      const lpd = DATA.lifetime_pd || [];

      // Validation Metrics Bar
      const samples = ['train', 'test', 'oot'];
      new Chart(document.getElementById('chart-model-validation'), {
        type: 'bar',
        data: {
          labels: ['Train', 'Test', 'Out of Time (OOT)'],
          datasets: [
            { label: 'Gini', data: samples.map(s => (val[s]?.gini || 0)), backgroundColor: COLORS.navy, borderRadius: 2 },
            { label: 'KS Statistic', data: samples.map(s => (val[s]?.ks || 0)), backgroundColor: COLORS.blue, borderRadius: 2 },
            { label: 'AUC', data: samples.map(s => (val[s]?.auc || 0)), backgroundColor: COLORS.teal, borderRadius: 2 }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: { y: { title: { display: true, text: 'Metric Value' }, min: 0, max: 1.0 } }
        }
      });

      // Lifetime Cumulative PD Line
      new Chart(document.getElementById('chart-lifetime-pd'), {
        type: 'line',
        data: {
          labels: lpd.map(l => `M${l.month}`),
          datasets: [{
            label: 'Cumulative PD (%)',
            data: lpd.map(l => l.cumulative_pd * 100),
            borderColor: COLORS.navy,
            backgroundColor: 'rgba(30, 58, 138, 0.1)',
            fill: true,
            borderWidth: 2
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: { y: { title: { display: true, text: 'Cumulative PD (%)' }, beginAtZero: true } }
        }
      });
    }
  </script>
</body>
</html>
"""


def build_dashboard_html(
    json_path: Path = Path("outputs/reports/dashboard_data.json"),
    html_output_path: Path = Path("outputs/reports/risk_dashboard.html"),
):
    """Regenerates JSON data and compiles a single self-contained HTML dashboard."""
    logger.info("Regenerating dashboard JSON dataset...")
    data = build_dashboard_json(output_path=json_path)

    logger.info("Embedding JSON into HTML template...")
    embedded_json_str = json.dumps(data, indent=2)

    html_content = HTML_TEMPLATE.replace("__EMBEDDED_DATA__", embedded_json_str)

    html_output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(html_output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    logger.info(f"Self-contained HTML dashboard successfully written to {html_output_path}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    build_dashboard_html()
