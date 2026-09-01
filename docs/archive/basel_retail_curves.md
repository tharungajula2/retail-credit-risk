# Basel III Retail Exposure Classification: Other Retail vs. QRRE

## Overview & Regulatory Scope

Under the Basel III Internal Ratings-Based (IRB) framework for retail exposures (BCBS CRE30), risk-weighted asset (RWA) calculations rely on asset correlation ($R$), which models the sensitivity of borrower defaults to systemic macroeconomic shocks. 

Basel defines distinct asset correlation formulas depending on the structural product type:

1. **Other Retail (Term Instalment Loans)**: Applies to fixed-term, non-revolving consumer instalment loans (e.g., personal loans, auto loans).
2. **Qualifying Revolving Retail Exposures (QRRE)**: Applies to revolving credit facilities (e.g., credit cards, overdraft lines).

---

## Asset Correlation Formulas

### 1. Other Retail Asset Correlation Curve (Used for LendingClub)

For term instalment loans, asset correlation decreases smoothly as Probability of Default (PD) increases, spanning between **16.0%** (for very low risk) down to **3.0%** (for very high risk):

$$R_{\text{Other Retail}} = 0.03 \times \left( \frac{1 - e^{-35 \times \text{PD}}}{1 - e^{-35}} \right) + 0.16 \times \left( 1 - \frac{1 - e^{-35 \times \text{PD}}}{1 - e^{-35}} \right)$$

- **At $\text{PD} = 0.1\%$**: $R \approx 15.55\%$
- **At $\text{PD} = 1.0\%$**: $R \approx 12.16\%$
- **At $\text{PD} = 5.0\%$**: $R \approx 5.26\%$

#### Economic Rationale
For low-PD instalment borrowers, macro-economic downturns drive systemic defaults, resulting in higher correlation. For high-PD instalment borrowers, defaults are predominantly driven by idiosyncratic, borrower-specific financial distress, yielding lower systemic correlation.

---

### 2. QRRE Asset Correlation (Revolving Credit Cards)

For revolving credit facilities meeting QRRE eligibility criteria, Basel prescribes a **flat fixed correlation**:

$$R_{\text{QRRE}} = 0.04 \quad (4.0\%)$$

- **At $\text{PD} = 1.0\%$**: $R = 4.00\%$

#### Economic Rationale
Revolving facilities exhibit high borrower-controlled utilisation dynamics and continuous re-underwriting flexibility, justifying a flat 4.0% systemic correlation ceiling under regulatory rules.

---

## Portfolio Classification Rationale for LendingClub

LendingClub loans are fixed-term, fully amortizing instalment loans (36-month and 60-month terms) with no undrawn commitments or revolving drawdown capabilities. Therefore:

- **Mandatory Classification**: LendingClub loans are classified under **Other Retail**.
- **Regulatory Compliance**: Portfolio capital calculations strictly utilize the `basel_correlation` (Other Retail) curve. `basel_correlation_qrre` is maintained strictly as an auxiliary function for comparative benchmarking.
