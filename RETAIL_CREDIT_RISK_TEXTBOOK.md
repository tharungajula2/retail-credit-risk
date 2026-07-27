# RETAIL CREDIT RISK & MODELLING — INTERVIEW MASTERY
### One document. Read it three times. That is the whole plan.

---

> **The one sentence that organises everything below**
>
> Every number in credit risk is an answer to one of two questions: **"what do we expect to lose?"** — which becomes a *provision* — or **"what if it's far worse than we expect?"** — which becomes *capital*. Learn which question a formula is answering and the formula stops being intimidating.

---

## HOW TO USE THIS TONIGHT

| Pass | Time | What you do |
|:--|:--|:--|
| **Pass 1** | 50 min | §1 → §14 straight through. Don't stop to memorise. Build the map. |
| **Pass 2** | 60 min | Again. Pause at every **► SAY THIS** and say it out loud. Recognition is not recall. |
| **Pass 3** | 30 min | §15 (traps), §16 (questions), §17 (formulas). Cover the answers. |
| **Morning** | 15 min | §19 only. Nothing else. |

**Sleep beats one more pass.** A tired brain retrieves badly.

---
---

# §1 · THE TWENTY NUMBERS

| # | Fact | Value |
|:--|:--|:--|
| 1 | Expected loss | **EL = PD × LGD × EAD** |
| 2 | Gini from AUC | **Gini = 2·AUC − 1** |
| 3 | Retail PD model, typical OOT Gini | **0.35 – 0.65** |
| 4 | Gini above ~0.75 on retail | **Suspect leakage** |
| 5 | KS, typical retail | **0.25 – 0.45** |
| 6 | IV — useful range | **0.10 – 0.30** medium · **>0.50 check for leakage** |
| 7 | Minimum bin size in binning | **5% of rows** |
| 8 | PSI — stable | **< 0.10** (0.10–0.25 investigate · >0.25 redevelop) |
| 9 | Hosmer–Lemeshow | **HIGH p = calibrated = PASS** |
| 10 | Basel confidence level | **99.9%**, so G(0.999) = **3.09023** |
| 11 | Basel RWA conversion | **RWA = K × 12.5 × EAD** |
| 12 | Basel PD floor | **0.03%** (0.0003) |
| 13 | Retail correlation — mortgage / QRRE / other retail | **0.15 fixed / 0.04 fixed / 0.03→0.16 PD-dependent** |
| 14 | Maturity adjustment for retail | **None.** Corporate only. |
| 15 | Standardised retail risk weight | **75%** |
| 16 | Capital ratios | CET1 **4.5%** · Tier 1 **6%** · Total **8%** of RWA, plus buffers |
| 17 | IFRS 9 stages | **1** = 12-month ECL · **2** = lifetime · **3** = lifetime, PD = 1 |
| 18 | SICR hard backstop | **30+ DPD**, rebuttable presumption |
| 19 | Lifetime PD ÷ 12-month PD, typical retail | **≈ 3×** |
| 20 | RBI ECL framework effective | **1 April 2027** (final Directions 27 Apr 2026, glide path to 2031) |

---
---

# §2 · THE MAP

Everything in credit risk flows from four parameters into two destinations.

```
        THE FOUR PARAMETERS
        ───────────────────
   PD  ·  LGD  ·  EAD  ·  (CCF, for revolving)
                 │
        ┌────────┴────────┐
        │                 │
   EXPECTED LOSS      UNEXPECTED LOSS
   EL = PD·LGD·EAD    the volatility around EL
        │                 │
        ▼                 ▼
   ┌─────────┐       ┌─────────┐
   │PROVISION│       │ CAPITAL │
   └─────────┘       └─────────┘
        │                 │
   IFRS 9 / Ind AS   Basel IRB formula
   109 / CECL /      stressed PD at 99.9%
   RBI ECL 2027      RWA = K × 12.5 × EAD
        │                 │
   Hits P&L as       Hits balance sheet
   provision charge  as required equity
```

**The single most important structural fact:**

> **Provisions cover expected loss. Capital covers unexpected loss.** The Basel formula literally subtracts EL out — *K = LGD × (stressed PD − PD)* — because the expected part is already handled by provisions and pricing. Forget the subtraction and you double-count.

**And the second:** the same PD, LGD and EAD feed *both* destinations, but on different horizons and with different conservatism. Basel wants a **downturn** LGD and a **through-the-cycle** 12-month PD. IFRS 9 wants a **point-in-time**, **forward-looking**, **lifetime** PD. Same letters, different quantities. Confusing them is the most common error in the field.

---
---

# §3 · THE FOUR PARAMETERS

### 3.1 PD — Probability of Default

The probability a borrower defaults within a stated horizon. **The horizon and the definition of default must both be stated, or the number is meaningless.**

📘 **Default definition.** Basel's reference definition: **90 days past due**, or the bank judges the obligor unlikely to pay in full without recourse to actions like realising security. Both limbs matter — the second catches restructurings and bankruptcies that never reach 90 DPD.

| Flavour | Meaning | Used by |
|:--|:--|:--|
| **Through-the-cycle (TTC)** | Long-run average across good and bad years | **Basel capital** |
| **Point-in-time (PIT)** | Reflects current conditions | **IFRS 9 / ECL** |
| **12-month** | Default within one year | Basel, IFRS 9 Stage 1 |
| **Lifetime** | Default at any point in remaining life | IFRS 9 Stage 2/3, CECL |

### 3.2 LGD — Loss Given Default

$$\text{LGD} = \frac{\max(\text{EAD} - \text{post-default recoveries},\ 0)}{\text{EAD}} \qquad \text{Recovery rate} = 1 - \text{LGD}$$

**Recoveries must be net of collection costs and discounted to the default date.** A rupee recovered after three years of legal effort is not a rupee.

| Product | Typical LGD | Why |
|:--|:--|:--|
| Residential mortgage | 10–25% | Enforceable asset that holds value |
| Auto | 40–60% | Depreciating asset, repossession costs |
| **Unsecured personal / card** | **60–95%** | Nothing to seize |

📘 **The two-stage LGD.** Real recovery distributions are **bimodal** — a large mass at zero recovery, another mass at full recovery, and little in between. A single regression on that shape fits neither peak. The standard fix is two models:

$$\widehat{\text{LGD}} = 1 - \left[P(\text{any recovery}) \times \widehat{rr}_{\,|\,\text{recovery}}\right]$$

A classifier for *whether* anything is recovered, then a regression for *how much*, conditional on something being recovered. **Saying this in an interview signals you've actually looked at recovery data.**

⚖️ **Downturn LGD.** Basel requires capital to use LGD estimated under **downturn conditions**, not the long-run average — because defaults and low recoveries happen *together*. A repossessed car sells for less in a recession, which is exactly when more cars are being repossessed. Averaging across the cycle understates the loss precisely when it matters.

### 3.3 EAD — Exposure at Default

$$\text{EAD}_{\text{term}} = \max(\text{funded} - \text{principal repaid},\ 0)$$
$$\text{EAD}_{\text{revolving}} = \text{drawn} + \text{CCF} \times \text{undrawn}$$

For a term loan EAD is nearly mechanical. For revolving products it is a **forecast**, and that is where the risk hides.

### 3.4 CCF — Credit Conversion Factor

The proportion of an **undrawn** limit expected to be drawn by the time of default.

> **Why CCF exists and why it's always high:** a borrower heading for default draws down hard first. They know they're in trouble before you do. So the exposure you actually face is far above the balance you observe today. **This is the only parameter that captures the borrower's informational advantage over the lender.**

### 3.5 The consistency rule — non-negotiable

> **PD, LGD and EAD must all be estimated on the SAME definition of default.**

Model PD at 90+ DPD but measure LGD from charge-off, and you're multiplying probabilities of one event by losses from a different event. The product is arithmetically fine and conceptually meaningless.

> **► SAY THIS** — *"The first thing I'd check on any EL implementation is whether PD, LGD and EAD share a default definition. It's the most common silent error, because nothing breaks — you just get a confidently wrong number."*

---
---

# §4 · EXPECTED VS UNEXPECTED LOSS

🧮 **The central worked example.** Portfolio of ₹100 crore, PD 3%, LGD 70%.

$$\text{EL} = 0.03 \times 0.70 \times 100\text{ cr} = \textbf{₹2.1 crore}$$

That is the **average** annual loss. It is a **cost of doing business** — you price for it in the interest rate and you provision for it. It is not a surprise, and you do not hold capital against it.

But 2.1 crore is a mean. Some years it's 1.2 crore. In a severe recession it might be 7 crore. **That variability is unexpected loss, and it is what capital exists for.**

```
Probability
    │        ╱▔▔╲
    │       ╱    ╲
    │      ╱      ╲
    │     ╱        ╲___
    │   ╱               ╲______
    └──┴────┴──────────────────┴────────► Loss
       │    │                  │
       0   EL              99.9th %ile
           2.1cr            e.g. 9cr
           ↑                    ↑
      PROVISIONS           ←CAPITAL→
                          (the gap: 6.9cr)
```

> **Capital = 99.9th percentile loss − expected loss.** That subtraction *is* the Basel formula. Everything in §6 is machinery for computing the right-hand tail.

**Why 99.9%?** It's a one-in-a-thousand-year loss. The implicit target is a solvency standard roughly consistent with an investment-grade credit rating for the bank itself. A bank that holds capital for a 1-in-1000 year event fails about once every thousand years — which regulators judged acceptable.

---
---

# §5 · BASEL — THE ARCHITECTURE

### 5.1 Why it exists

Banks compete. A bank holding 12% capital is safer but earns lower returns on equity than one holding 4%. Without a common floor, competition drives capital down until someone fails and takes the system with them. **Basel is a coordination device: everyone holds the minimum, so nobody is punished for prudence.**

### 5.2 The three pillars

| Pillar | Content |
|:--|:--|
| **Pillar 1** | Minimum capital requirements — the formulas. Credit, market, operational risk. |
| **Pillar 2** | Supervisory review — ICAAP, stress testing, risks Pillar 1 misses (concentration, interest rate risk in the banking book) |
| **Pillar 3** | Market discipline — mandatory public disclosure so markets can price the bank's risk |

### 5.3 Capital ratios

$$\text{Capital ratio} = \frac{\text{eligible capital}}{\text{RWA}} \qquad \text{RWA} = \sum \text{exposure} \times \text{risk weight}$$

| Tier | Minimum | What it is |
|:--|:--|:--|
| **CET1** | 4.5% of RWA | Common equity — the loss-absorbing core |
| **Tier 1** | 6% | CET1 + additional Tier 1 (perpetual instruments) |
| **Total** | 8% | Tier 1 + Tier 2 (subordinated debt) |
| **+ Capital conservation buffer** | 2.5% CET1 | Breach it and dividends/bonuses are restricted, not banned |

🇮🇳 **India runs tighter.** RBI's minimum CRAR for Indian banks is **9%**, above the Basel 8%, plus the 2.5% conservation buffer — so **11.5%** in practice.

### 5.4 Standardised vs IRB

| | **Standardised (SA)** | **Internal Ratings Based (IRB)** |
|:--|:--|:--|
| Risk weights | Prescribed by supervisor | Computed from the bank's own PD (and, under Advanced IRB, own LGD/EAD) |
| Retail RW | **75%** flat for regulatory retail | Whatever the formula gives |
| Approval needed | No | Yes — supervisory approval, extensive validation |
| Incentive | Simple | Intended to reward better risk measurement with lower capital |

🔴 **THE TRAP — "IRB always gives less capital than Standardised."**

**False, and this is a genuinely good interview answer.** IRB gives less capital only when the portfolio is genuinely low-risk. Feed the formula a high PD *or* a high LGD and IRB produces risk weights **far above** the flat 75%.

🧮 **Watch what LGD does.** Other Retail, PD = 1%:

| LGD | R | K | **Risk weight** |
|--:|--:|--:|--:|
| 45% | 0.1216 | 0.0366 | **45.8%** |
| 90% | 0.1216 | 0.0732 | **91.5%** |

**K is exactly linear in LGD** — double LGD, double the capital. So an unsecured book with 90% LGD gets a risk weight above the 75% standardised floor even at a *1% PD*. On unsecured retail, IRB is frequently the more expensive treatment, and that is the formula working correctly, not a bug.

> **► SAY THIS** — *"IRB isn't a capital discount, it's a risk-sensitivity mechanism. On a high-LGD unsecured book it produces higher risk weights than the 75% standardised retail weight, because K is linear in LGD. If a bank's IRB output is below Standardised on unsecured retail, I'd want to see the LGD estimation before I believed it."*

---
---

# §6 · THE IRB FORMULA, DERIVED

It looks intimidating. It is four steps and every term has a plain job.

### 6.1 The idea in one paragraph

Every borrower's fate is driven partly by **one shared economic factor** and partly by their **own idiosyncratic luck**. In a bad economy everyone's PD rises together. So: push the shared factor to its **99.9th-percentile worst** value, recompute each borrower's PD *conditional on that terrible economy*, multiply by LGD, and subtract the expected loss. What's left is capital.

That is the **Asymptotic Single Risk Factor (ASRF)** model. The whole formula is that paragraph in symbols.

📘 **Notation.** *N(x)* = standard normal CDF (feed a number, get a probability). *G(p)* = its inverse (feed a probability, get a threshold). *G(0.999) = 3.09023.* *R* = asset correlation, **prescribed by the supervisor, never estimated by the bank**.

### 6.2 Step 1 — correlation

**Other Retail** (personal instalment, auto — retail that isn't a mortgage or a qualifying revolver):

$$R = 0.03w + 0.16(1-w), \qquad w = \frac{1 - e^{-35\,\text{PD}}}{1 - e^{-35}}$$

Since $e^{-35} \approx 6.3\times10^{-16}$, the denominator is effectively 1, so $w \approx 1 - e^{-35\,\text{PD}}$.

- **PD → 0:** w → 0, so **R → 0.16** (maximum)
- **PD → 1:** w → 1, so **R → 0.03** (minimum)

📘 **Why does correlation FALL as PD rises?** This surprises everyone, and explaining it well is a strong signal.

> A borrower who is already very likely to default is failing for **personal** reasons — they're in trouble regardless of the economy. A very safe borrower will only default if something **systemic** goes wrong. So high-PD borrowers are more *idiosyncratic*; low-PD borrowers are more *systematic*. Lower correlation means losses are less likely to arrive all at once, which means less capital.

| Retail sub-class | Correlation |
|:--|:--|
| Residential mortgage | **0.15** fixed |
| Qualifying Revolving Retail (QRRE) — cards | **0.04** fixed |
| Other Retail | **0.03 → 0.16**, PD-dependent |

🔴 **A trap worth knowing.** Benchmark values quoted for "retail" are often **QRRE** numbers. At PD = 1%, QRRE gives R = 0.04 while Other Retail gives **R = 0.12161** — three times higher. Term instalment loans are unambiguously Other Retail. If a reference value disagrees with your output, check which sub-class the reference used before you touch the formula.

### 6.3 Step 2 — the stressed PD

$$\text{PD}_{\text{stressed}} = N\!\left(\frac{G(\text{PD}) + \sqrt{R}\cdot G(0.999)}{\sqrt{1-R}}\right)$$

Read it in three moves:

1. **G(PD)** converts the default probability into a **threshold** on a normal scale. At PD = 3.45%, G = −1.818: the borrower defaults when latent creditworthiness falls below −1.818.
2. **√R · G(0.999)** is the **economic shock** — the one-in-a-thousand bad draw of the shared factor, scaled by how exposed this borrower is to it.
3. **Divide by √(1−R)** to renormalise for the idiosyncratic part, then **N(·)** converts back to a probability.

Out comes the default rate you'd observe in a 99.9th-percentile bad year.

### 6.4 Steps 3 and 4 — K, RWA, risk weight

$$K = \text{LGD}\big(\text{PD}_{\text{stressed}} - \text{PD}\big) \qquad \text{RWA} = K \times 12.5 \times \text{EAD} \qquad \text{RW} = K \times 12.5$$

**That subtraction is the entire conceptual payload.** Stressed loss minus expected loss. Capital covers only the unexpected part.

**Retail has no maturity adjustment.** Corporate exposures carry an extra term because a long-dated corporate loan can lose value through credit migration before default. Retail IRB omits it entirely. *A small, precise fact that lands well when produced at the right moment.*

### 6.5 The complete worked example — reproduce this by hand

**PD = 1%, LGD = 45%, EAD = ₹1,00,000, Other Retail**

| Step | Computation | Result |
|:--|:--|--:|
| w | (1 − e^−0.35) ÷ 1 | 0.29531 |
| **R** | 0.03(0.29531) + 0.16(0.70469) | **0.12161** |
| G(PD) | G(0.01) | −2.32635 |
| G(0.999) | — | 3.09023 |
| √R | √0.12161 | 0.34873 |
| √(1−R) | √0.87839 | 0.93722 |
| Numerator | −2.32635 + 0.34873 × 3.09023 | −1.24887 |
| Divide | −1.24887 ÷ 0.93722 | −1.33254 |
| PD stressed | N(−1.33254) | **0.09135** |
| **K** | 0.45 × (0.09135 − 0.01) | **0.03662** |
| **Risk weight** | 0.03662 × 12.5 | **45.8%** |
| RWA | 0.03662 × 12.5 × 1,00,000 | **₹45,775** |
| Capital @ 8% | 0.08 × 45,775 | **₹3,662** |

✅ **The sanity check:** capital = K × EAD = 0.03662 × 1,00,000 = ₹3,662. **The 12.5 and the 8% cancel exactly** — as they must, since 12.5 = 1/0.08. If they don't cancel in your output, you have a bug.

### 6.6 Floors

- **PD floor 0.03%.** No exposure may be treated as safer than three basis points.
- **LGD** capped at 1.0; Basel III finalisation also introduced input floors by exposure type.
- **Defaulted exposures** compute K differently — broadly the excess of downturn LGD over the bank's best estimate of expected loss, floored at zero.

---
---

# §7 · SCORECARDS — WoE, IV, AND POINTS

### 7.1 Why a scorecard and not a gradient-boosted tree

A GBM would score slightly better. It is not used, and the reason isn't ignorance.

> A regulated retail PD model must be **explainable** to a regulator and a credit committee, **stable** over time, **auditable** line by line, and **documentable** in a model development pack. The structure that delivers all four is the **Weight of Evidence scorecard**.

Bin every variable → replace each value with its bin's WoE → fit a logistic regression on the WoE values → linearly rescale the log-odds into points.

The result is linear, monotonic and fully inspectable. **Every point a borrower gains or loses traces to one specific bin of one specific variable.** That's what lets a bank answer *"why was I declined?"* and lets a validator reproduce the model by hand.

**The mature version of this answer:** banks often build an ML **challenger** alongside the scorecard, specifically to measure *how much predictive power the interpretability constraint costs.* If the gap is small, interpretability is free. If it's large, that's a documented business decision, not an oversight.

### 7.2 Binning

**Numeric:** start with many fine quantile bins (say 20), then merge adjacent bins until two conditions hold — **WoE is monotonic** across bins, and **every bin holds ≥5% of rows**.

**Categorical:** each level is a bin; levels under 5% merge into `OTHER`. **Monotonicity is not enforced** — there's no natural ordering to `purpose` or `home_ownership`.

**Missing values get their own bin.** This is the quiet superpower: you never impute, never drop rows, and **missingness becomes an honest, measurable risk signal**. Sometimes not having a value *is* the information.

📘 **Why monotonicity matters to a regulator.** If higher income maps to lower risk in bins 1, 2 and 4 but *higher* risk in bin 3, you have a zigzag. It's almost always noise, it won't replicate out of time, and — decisively — you can't defend it. *"Why does the model penalise people earning ₹8–10 lakh but reward ₹6–8 lakh and ₹10–12 lakh?"* has no good answer. Merge until it's monotonic.

### 7.3 Weight of Evidence

$$\text{WoE}_{\text{bin}} = \ln\!\left(\frac{\%\text{ of all NON-defaulters in this bin}}{\%\text{ of all defaulters in this bin}}\right)$$

- **Positive WoE** → proportionally more goods → **safer** than portfolio average
- **Negative WoE** → proportionally more defaulters → **riskier**
- **WoE = 0** → exactly average

**It does three things at once:** puts every variable — numeric, categorical, missing-riddled — onto **one common log-odds scale**; **linearises** the relationship to risk (so a linear model becomes appropriate); and makes **outliers harmless**, because an extreme value simply lands in the top bin.

**Laplace correction.** A bin with zero defaulters makes the ratio infinite and ln blows up. Add 0.5 to each cell count before computing proportions.

### 7.4 Information Value

$$\text{IV} = \sum_{\text{bins}} (\%\text{good} - \%\text{bad}) \times \text{WoE}$$

| IV | Interpretation |
|:--|:--|
| < 0.02 | Useless — drop |
| 0.02 – 0.10 | Weak |
| **0.10 – 0.30** | **Medium — useful** |
| 0.30 – 0.50 | Strong |
| **> 0.50** | **Suspiciously strong — check for leakage first** |

> **That last row is a real diagnostic, not a caution.** If a post-origination field like `recoveries` accidentally slipped into your feature set, its IV would come back around 2.0 and give the game away instantly. **A suspiciously good variable is a data problem until proven otherwise.**

📘 **A finding worth understanding conceptually.** On marketplace-lending data, the strongest raw *borrower-fundamental* variables typically land in "weak" territory (IV ~0.08), while the platform's own **grade** and **interest rate** come in at IV 0.28–0.29.

**Why:** grade and rate are not borrower facts — they are the **output of someone else's risk model**, formed at origination. They've already absorbed the signal. This creates a real modelling fork:

| | **Model A — fundamentals only** | **Model B — including grade/rate** |
|:--|:--|:--|
| Inputs | Borrower attributes only | Plus the platform's own risk assessment |
| Interpretation | Genuine independent credit assessment | Partly re-learning someone else's model |
| Discrimination | Lower | Higher |
| Defensible as *your* model? | **Yes** | Contestable |

**Knowing that this trade-off exists — and that it's a judgement call rather than a technical one — is worth more than either model.**

### 7.5 The logistic regression

$$\ln\!\left(\frac{p}{1-p}\right) = \beta_0 + \beta_1\text{WoE}_1 + \cdots + \beta_k\text{WoE}_k$$

📘 **Every coefficient should be negative.** High WoE = safer bin. Higher predicted PD = riskier. So as WoE rises, predicted default must **fall** → negative coefficient.

> **A positive coefficient says "safer borrowers default more."** That's nonsense, and it always indicates a broken bin, a data problem, or severe multicollinearity. **Checking coefficient signs is the fastest smoke test on a fitted scorecard** — thirty seconds, and it catches most disasters.

**Use a package that returns standard errors, p-values and confidence intervals.** A validator will ask for them, and a model without them isn't documentable.

### 7.6 Points scaling

Banks don't hand a credit committee a probability of 0.0347. They hand them **680**. The conversion is a cosmetic linear transform of the log-odds, defined by three chosen constants: **target points** (e.g. 600), **target odds** at that score (e.g. 50:1), and **PDO** — Points to Double the Odds (e.g. 20).

$$\text{Factor} = \frac{\text{PDO}}{\ln 2} = \frac{20}{0.6931} = 28.8539$$
$$\text{Offset} = \text{TargetPoints} - \text{Factor}\ln(\text{TargetOdds}) = 600 - 28.8539\ln(50) = 487.12$$
$$\text{BasePoints} = \frac{\text{Offset} - \text{Factor}\cdot\beta_0}{m} \qquad \text{Points}_{\text{bin}} = \text{BasePoints} + \text{Factor}\cdot(-\beta_j\,\text{WoE}_{\text{bin}})$$

A borrower's score is the **sum of their bin points across all variables**.

📘 **What scaling does and doesn't do.** It changes **nothing** about the model — not the ranking, not the probabilities, not the discrimination. It's a change of units, exactly like Celsius to Fahrenheit. What it buys is one usable sentence: *"twenty points doubles your odds of being good."* That's the entire purpose.

### 7.7 Rating grades

Final step: cut the continuous score into a **master scale** of grades, each with an observed default rate.

| Grade | Observed default rate |
|:--|--:|
| 1 (safest) | 0.85% |
| 2 | 1.29% |
| 3 | 1.91% |
| 4 | 2.56% |
| 5 | 3.23% |
| 6 | 4.21% |
| 7 | 5.33% |
| 8 (riskiest) | 7.75% |

> **Rank ordering must hold strictly and monotonically.** Every worse grade must actually default more than the grade above it. **This is the most basic validation a scorecard must pass.** If it breaks anywhere, a bin needs merging. A wider spread between grade 1 and grade 8 means better discrimination.

---
---

# §8 · VALIDATION — THE THREE QUESTIONS

**A model that ranks borrowers is not automatically a good model.** Validation asks three separate questions, and a model can pass one while catastrophically failing another. **This section is what a model risk team does all day.**

### 8.1 DISCRIMINATION — can it tell good from bad?

**AUC.** Take one random defaulter and one random non-defaulter. AUC is the probability the model assigns a higher PD to the defaulter. 0.5 = coin flip, 1.0 = perfect.

**Gini = 2·AUC − 1.** What credit risk actually uses. Retail PD models out-of-time typically land **0.35–0.65**. **Above ~0.75 on a retail book, suspect leakage** — something in your features is telling you the answer.

**KS.** The largest vertical gap between the cumulative distributions of defaulters and non-defaulters as you sweep the score. Reads as: *at the single best cut-off, how far apart are the two populations?* Retail typically **0.25–0.45**.

📘 **Direction matters.** Feed the metric a **probability of default** (higher = worse) and you get Gini. Feed it a **credit score** (higher = better) and you get its negative. **A negative Gini is almost always a sign flip, not a broken model.**

### 8.2 CALIBRATION — when it says 3%, do 3% default?

> **This matters MORE than discrimination for regulatory purposes, because Basel and IFRS 9 multiply by the PD.** A model that ranks perfectly but predicts 2% when the truth is 4% makes the bank hold **roughly half** the capital it should.

**Calibration table.** Bin predicted PD into deciles; compare mean predicted PD against actual observed default rate in each. They should track closely.

**Hosmer–Lemeshow.** The formal version — chi-square across deciles, converted to a p-value.

> **► READ THE P-VALUE BACKWARDS FROM WHAT YOU'RE USED TO**
>
> **HIGH p = no evidence of miscalibration = the model PASSES.**
> **LOW p (< 0.05) = observed and predicted differ more than chance allows = FAILS.**
>
> This is the single most commonly fumbled point in credit risk interviews. In most statistics you *want* a low p-value. Here you want a high one.

**Brier score.** Mean squared error of the probability forecasts. Lower is better; blends discrimination and calibration into one number.

⚠️ **The caveat that shows sophistication.** Hosmer–Lemeshow is **highly sensitive to sample size**. On 200,000+ loans, even a commercially trivial miscalibration produces a tiny p-value — you'll often see p ≈ 0.001 on the *training* data the model was fitted to, which is the sample-size effect and nothing else.

> **The honest read:** use the **calibration table** to judge the *size* of the error and HL to judge whether it's *systematic*. **Never report HL alone on a large sample.**

### 8.3 STABILITY — does it still work next year?

**PSI (Population Stability Index)** — compares the distribution of the model **score** between development and a later sample:

$$\text{PSI} = \sum_{\text{bins}} (\%_{\text{actual}} - \%_{\text{expected}})\ln\frac{\%_{\text{actual}}}{\%_{\text{expected}}}$$

| PSI | Action |
|:--|:--|
| < 0.10 | Stable |
| 0.10 – 0.25 | Investigate |
| > 0.25 | May need redevelopment |

**CSI (Characteristic Stability Index)** — the identical calculation applied to each **input variable** individually.

> **► THE SUBTLEST AND BEST POINT IN THIS ENTIRE DOCUMENT: never compute PSI alone.**
>
> PSI looks at the **score**. If two input variables shift in ways that partially offset — or if a WoE `MISSING` bin quietly absorbs a change — **the score distribution can look perfectly stable while the underlying population has lurched.**
>
> **Real pattern:** score PSI ≈ **0.01** (rock stable, nothing to see) while two individual variables showed CSI ≈ **3.96** — an enormous shift. Cause: those two bureau fields simply weren't *collected* in the early vintages. They were 100% missing in the development data and >99% populated later. The binner had swept all early rows into a single `MISSING` bin; at scoring time the loans suddenly landed in populated bins the model had barely learned from.
>
> **The score absorbed it. The variable had not.** That structural shift is what broke out-of-time calibration — and PSI alone would never have found it.

**The resolution is instructive:** those two variables were **dropped as data-collection artefacts, not features**. A variable whose availability changes over time isn't measuring the borrower; it's measuring your data pipeline.

### 8.4 Out-of-sample vs out-of-time

| | Meaning | Tests for |
|:--|:--|:--|
| **Out-of-sample** | Random hold-out from the **same period** | **Overfitting** |
| **Out-of-time (OOT)** | An entirely **different time period** held out | **Temporal robustness** |

> **OOT is the one that matters**, because a deployed model runs on *future* borrowers, not a random subset of past ones. **A model can pass out-of-sample beautifully and fail out-of-time**, and that failure is invisible to anyone who only did a random split.

### 8.5 Reading a validation table

| Model | Sample | AUC | Gini | KS | HL p |
|:--|:--|--:|--:|--:|--:|
| A | train | 0.6507 | 0.3013 | 21.93% | 0.00115 |
| A | test | 0.6485 | 0.2969 | 22.33% | **0.236** ✅ |
| A | **oot** | 0.6357 | 0.2715 | 19.55% | **3.1×10⁻⁷** ❌ |
| B | train | 0.6839 | 0.3678 | 27.36% | 0.00040 |
| B | test | 0.6817 | 0.3634 | 27.28% | **0.494** ✅ |
| B | **oot** | 0.6923 | **0.3845** | 28.43% | 0.00117 |

**Four things to read, in order of interview value:**

1. **No overfitting.** Train Gini 0.3013 → test 0.2969. A four-hundredths drop is nothing. The model isn't memorising.
2. **Model B improves out of time** — 0.3634 → 0.3845. A model getting *better* on unseen future data is unusual and usually means the OOT vintage was large and clean.
3. **Model A's OOT calibration fails catastrophically.** It *ranks* fine (Gini 0.27) but its **numbers** are wrong out of time. **Discrimination survived; calibration didn't.** That's the distinction §8.1–8.2 exists to make.
4. **A ranking model with broken calibration cannot set capital**, because capital multiplies by the PD. It can still be used for *ordering* decisions — approve/decline cut-offs — where only rank matters.

---
---

# §9 · RECALIBRATION — WHEN A MODEL FAILS

### 9.1 The two techniques

**Intercept recalibration.** Re-estimate **only β₀**, freezing every slope. Mechanically: compute the linear predictor without the intercept, η = Σβⱼ·WoEⱼ, then fit a one-parameter logistic regression on a constant using η as a fixed **offset**.

> It shifts every PD up or down by the same amount in log-odds space and **provably leaves AUC, Gini and KS untouched.**

**Platt scaling.** Two parameters: *p_new = logistic(a · logit(p_old) + b)*. More flexible — but it **rescales the slopes**.

### 9.2 The judgement call that impresses

Suppose Platt achieves a marginally better calibration p-value than intercept recalibration. **Intercept recalibration may still be the right choice** — and being able to say why is a mature answer.

> **The reason is specific to scorecards.** Platt's slope factor (say a = 0.941) would rescale every variable's contribution, **distorting the integer point values and breaking the PDO = 20 relationship** that makes the scorecard interpretable in the first place. Intercept recalibration changes only the baseline constant, leaving every bin's points intact.
>
> **Choosing the mathematically slightly worse option for a sound structural reason, and explaining it, is exactly what a model risk team is hiring for.**

### 9.3 Level errors vs shape errors — the diagnostic

> **If recalibration doesn't fix it, the problem isn't the level. It's the shape.**

A one-parameter intercept shift and a two-parameter Platt scaling can both only move the *level* (and, for Platt, the overall slope). If neither fixes calibration, then the model isn't uniformly too high or too low — **it's wrong in particular deciles**. The *relationship* between borrower characteristics and default has changed, not just the base rate. No rescaling can repair that. **You redevelop.**

⚠️ **THE LEAKAGE TRAP — a classic interview probe.** Recalibrate on the **test** sample; report on **OOT**.

> **If you recalibrate ON the OOT sample and then report OOT calibration, the number is guaranteed to look good and means precisely nothing** — you've fitted to the thing you're measuring. Interviewers ask this to see whether you understand the difference between fitting and evaluating.

### 9.4 The answer that beats any Gini number

> **► SAY THIS**
> *"Everyone can fit a model. What I'd want to demonstrate is: I built two, found the more intellectually honest one failed out-of-time calibration, diagnosed the cause as a structural data shift rather than a modelling error, attempted two standard remedies, documented that neither worked and why — because it was a shape problem, not a level problem — and deployed the other with the trade-off written down."*
>
> **That paragraph is worth more than any performance metric**, because it demonstrates judgement rather than technique.

---
---

# §10 · IFRS 9 / IND AS 109

### 10.1 The problem it solved

Before 2018, loan loss accounting used an **incurred loss** model: provision only once there was objective evidence a loss had **already** occurred. Consequence: provisions were tiny going into 2008 and exploded afterwards. The accounting recognised losses long after the risk had built. Standard-setters called it **"too little, too late."**

**IFRS 9** (global, 2018; India as **Ind AS 109**) replaced it: from the moment a loan is originated, recognise a provision for losses you **expect**, forward-looking, before any evidence of impairment.

### 10.2 The three stages

| Stage | Condition | Provision | Interest recognised on |
|:--|:--|:--|:--|
| **1** | Performing; no significant deterioration since origination | **12-month ECL** | Gross carrying amount |
| **2** | **SICR** since origination, not yet credit-impaired | **Lifetime ECL** | Gross carrying amount |
| **3** | Credit-impaired (defaulted) | **Lifetime ECL**, PD = 1 | **Net** carrying amount |

📘 **THE KEY SUBTLETY — a standard interview question.**

> **Staging is RELATIVE to origination, not absolute.**
>
> A borrower who was risky when you lent and is *still* the same risk stays in **Stage 1** — you knew what you were buying and you priced it. A borrower who was safe at origination and whose risk has since **doubled** moves to **Stage 2**, even if their absolute PD is still *lower* than the first borrower's.
>
> **IFRS 9 measures deterioration, not danger.**

**Why the provision jumps so violently at Stage 2.** Nothing about the loan's terms changed. **The horizon changed** — twelve months to entire remaining life. Since lifetime PD typically runs **≈3× the 12-month PD** on retail, the provision roughly triples the instant a loan trips SICR. **That cliff is deliberate** — it forces early, visible recognition of deterioration.

### 10.3 SICR — the multi-limb test

IFRS 9 **requires** a SICR test but does not **prescribe** one. Standard industry practice is four limbs:

| Limb | Test |
|:--|:--|
| **(a) Quantitative, relative** | Current PD ÷ PD expected at origination for this point in life > threshold (e.g. 2.0×) |
| **(b) Quantitative, absolute** | Backstop on absolute level (e.g. 12m PD > 6%), catching extreme risk the relative test misses |
| **(c) 30-DPD backstop** | **Rebuttable presumption** in the standard: >30 days past due = SICR. Rebuttable with evidence, but no model may simply override it. |
| **(d) Qualitative** | Watchlist, forbearance, restructuring |

⚠️ **The practical difficulty worth naming:** the relative test requires **the PD assigned at underwriting, stored per loan**. Many institutions never stored it. The common workaround is proxying origination PD by the grade-level average PD at issue — **a documented approximation, not a solution.** *Naming this limitation unprompted is a strong credibility move.*

### 10.4 Lifetime PD — the hazard curve

Basel only ever needed a 12-month PD. **IFRS 9 Stage 2 needs the probability of default over the entire remaining life.** This is the one genuinely new quantity accounting demands.

📘 **Discrete-time hazard.** The hazard at month *m* is the probability of defaulting **in** month *m*, given survival to its start:

$$h(m) = \frac{\text{defaults in month } m}{\text{loans alive at start of month } m}$$

Chain the survivals:

$$S(m) = \prod_{k=1}^{m}\big(1-h(k)\big) \qquad \text{Cumulative PD}(m) = 1 - S(m)$$

**That's a life table** — the same mathematics an actuary uses for mortality, applied to loans.

🧮 **A representative retail term structure:**

| Month | Monthly hazard | Survival | Cumulative PD |
|--:|--:|--:|--:|
| 6 | 0.002811 | 0.99300 | **0.700%** |
| **12** | 0.005607 | 0.96565 | **3.435%** |
| 18 | 0.005004 | 0.93296 | 6.705% |
| 24 | 0.003058 | 0.91178 | 8.822% |
| 36 | 0.000741 | 0.89364 | **10.636%** |
| 60 | 0.000005 | 0.89072 | 10.928% |

✅ **THE CRITICAL SANITY CHECK.** Cumulative PD at month 12 = **3.435%**, which must match the independently-computed 12-month default rate — here 3.435%, to four decimals. **Two entirely different calculations agreeing to that precision proves the hazard curve is right.** Run this before anything downstream.

**The headline multiple:** 36-month lifetime PD ÷ 12-month PD = 10.636 ÷ 3.435 = **3.096×**. Peak monthly hazard falls between **months 10 and 16** — the classic retail seasoning hump — then collapses.

**Scaling to individual loans.** The portfolio curve gives the **shape** of default timing; each loan has its own **level** (its model PD). Scale multiplicatively so each loan's curve passes through its own 12-month PD at month 12, then read cumulative PD at that loan's **remaining** term.

### 10.5 Discounting and macro scenarios

**Discounting.** IFRS 9 requires ECL to be a **present value**, discounted at the **effective interest rate**. Losses expected in three years are worth less today than losses expected next month.

**Macro scenarios — IFRS 9 explicitly forbids a single point estimate.** The reported provision must be a **probability-weighted** average across multiple economic scenarios:

| Scenario | PD multiplier | Weight |
|:--|--:|--:|
| Baseline | 1.00 | 0.50 |
| Upside | 0.85 | 0.20 |
| Downside | 1.50 | 0.30 |

> **The weighted ECL lands ABOVE the pure baseline**, because the 30%-weighted downside outweighs the 20%-weighted upside. **That asymmetry is by design** — IFRS 9 is deliberately conservative in the forward-looking dimension.

⚠️ A real bank links these to published GDP, unemployment and house-price forecasts through a fitted **satellite model** translating macro variables into PD shifts. Direct multipliers are a documented simplification.

---
---

# §11 · CECL AND THE THREE-FRAMEWORK ORDERING

**The US did not adopt IFRS 9.** FASB wrote **CECL** (Current Expected Credit Losses, ASU 2016-13, effective for large filers from 2020). It agrees with IFRS 9 on the diagnosis and disagrees on the cure.

> **The one difference that matters: IFRS 9 has staging. CECL does not.**
>
> Under CECL, **every** loan carries a **lifetime** ECL from day one. No Stage 1 relief, no 12-month bucket, no SICR test to design or defend.

| | **IFRS 9 / Ind AS 109** | **CECL** |
|:--|:--|:--|
| Staging | Three stages | **None** |
| Healthy new loan | 12-month ECL | **Lifetime ECL** |
| SICR test | Required | Not needed |
| Day-one provision | Small | **Large** |
| Complexity | Higher (staging machinery) | Conceptually simpler, bigger numbers |

### The ordering, and why each step happens

🧮 **The same book, three frameworks:**

| Framework | Provision | Why |
|:--|--:|:--|
| **Basel Expected Loss** | **₹58.7M** | 12-month horizon, forward-looking only, **no Stage 3 impairment** |
| **IFRS 9 ECL** | **₹278.5M** | 12m Stage 1 + lifetime Stage 2 + **full impairment on Stage 3 (₹223.8M)** |
| **CECL** | **₹327.5M** | Lifetime on everything, day one |

> **Basel EL < IFRS 9 < CECL. Always. And each step has a clean reason.**

**Why IFRS 9 exceeds Basel EL — three effects stacked:** (1) IFRS 9 books the **full** loss on already-defaulted Stage 3 loans, which Basel EL doesn't count at all; (2) IFRS 9 applies a **lifetime** horizon to Stage 2 while Basel is always 12-month; (3) IFRS 9 **discounts** at EIR.

**Why CECL exceeds IFRS 9:** no staging relief. On the same performing population, the Stage 1 provision rose from **₹30.3M** (12-month treatment) to **₹79.3M** (lifetime treatment) — an extra ₹49M **arising purely from the choice of accounting framework, with no change whatsoever to the loans.**

⚠️ **THE LIKE-FOR-LIKE CORRECTION — and this is the mark of real rigour.**

> Comparing IFRS 9's *total* ECL to Basel EL is **apples to oranges**, because the IFRS 9 total is dominated by ₹223.8M of already-defaulted Stage 3 loans that Basel EL doesn't cover.
>
> Restrict IFRS 9 to **Stage 1 + Stage 2 only** — the same population Basel EL covers — and the two come out at roughly **₹54.7M (IFRS 9) vs ₹58.7M (Basel EL)**. Nearly equal.
>
> **That near-equality is the real validation.** It proves both engines are internally consistent, and that the headline five-fold gap is **entirely staging and Stage 3 treatment**, not a bug in either.

> **► SAY THIS**
> *"The three frameworks always order Basel EL below IFRS 9 below CECL, and the gaps are structural, not modelling differences. But comparing totals is misleading — you have to restrict IFRS 9 to the performing population before comparing it to Basel EL, because Basel EL doesn't cover defaulted exposures. Do that and they come out within a few percent, which is how you prove both engines are consistent."*

---
---

# §12 · PORTFOLIO MONITORING

**Building a model is a project. Running a portfolio is a job.** Monitoring answers, every month: *is the book getting better or worse, and where?*

| Tool | Answers |
|:--|:--|
| **Ageing / bucket report** | Where is the book **right now**? |
| **Roll rate** | Which way is it **moving**? |
| **Transition matrix** | The **full** movement pattern, including cures |
| **Vintage curve** | Is our **underwriting** getting better or worse? |

### 12.1 Vintage curves — the only honest read on a growing book

Slice by **month of origination**, plot delinquency against **months on book** rather than calendar time. This puts every cohort on the same age axis.

> **Why it's indispensable:** revenue is recognised immediately, losses arrive at months 4–15. So a fast-growing book's NPA ratio is **mathematically flattering** — the denominator explodes before the losses emerge. **A falling NPA ratio on a growing book is usually a denominator effect.**
>
> Compute **absolute** NPA rupees, then read vintages at a fixed MOB. If recent cohorts sit above older ones at the same age, underwriting has loosened — **and you see it a year before the headline ratio does.**

### 12.2 Roll rates and transition matrices

**Roll rate** = proportion of a bucket that moves to the next worse bucket next month.

**Transition matrix** = all movements from every state to every state, rows summing to 100% — **including cures**, which roll rates hide entirely.

| From ↓ / To → | Current | 1–30 | 31–60 | 61–90 | 90+ |
|:--|--:|--:|--:|--:|--:|
| **Current** | 94.6 | 4.2 | 0.0 | 0.0 | 0.0 |
| **1–30** | **52.0** | 3.8 | 43.8 | 0.0 | 0.0 |
| **31–60** | **18.0** | 30.0 | 5.0 | 46.8 | 0.0 |
| **61–90** | **6.0** | 8.0 | 10.0 | 1.0 | 75.0 |
| **90+** | 0.0 | 0.0 | 0.0 | 3.0 | **95.0** |

**Read the cure column: 52% → 18% → 6%.** Cure probability collapses with age, while cost per contact rises. **The entire return on collections effort is concentrated in the first thirty days.**

**90+ is nearly absorbing** (95% stay). Once an account is an NPA it very rarely comes back — which is *why* the collections apparatus is front-loaded.

> **► SAY THIS if asked how you'd monitor a portfolio**
> *"Four views, because each answers a different question. Ageing gives position, roll rates give direction and lead the NPA number by two to three months, the transition matrix adds cure rates which is what tells me whether collections is working, and vintage curves are the only view that controls for seasoning. I'd cut all four by product, channel and score band — portfolio-level numbers hide the segment that's actually failing."*

**That last clause matters.** Channel especially: DSA-sourced business routinely underperforms branch-sourced, because the DSA is paid for **disbursal**, not repayment.

---
---

# §13 · MODEL RISK GOVERNANCE

📘 **Model risk** = the risk of loss from decisions based on **incorrect or misused** model output. Note the two limbs: a model can be *right* and still cause loss if it's applied to a population it wasn't built for.

### 13.1 SR 11-7 — the reference framework

The US Federal Reserve's supervisory guidance on model risk management, and the global reference point even outside the US. Three pillars:

| Pillar | Content |
|:--|:--|
| **Development, implementation, use** | Sound design, documented rationale, testing, appropriate use |
| **Validation** | **Effective challenge** by parties independent of development, with authority and standing |
| **Governance** | Policies, model inventory, roles, board oversight, documentation |

> **"Effective challenge" is the phrase to know.** It means the validator must be genuinely **independent, competent, and empowered** — not a junior rubber-stamp reporting to the model owner. If validators can't say no, there is no validation.

### 13.2 The three lines of defence

| Line | Who | Owns |
|:--|:--|:--|
| **First** | Business / model development | Owns and manages the risk |
| **Second** | Independent risk / model validation | Oversees, challenges, sets standards |
| **Third** | Internal audit | Assures that lines one and two are working |

### 13.3 What a model development document must contain

The standard pack, and a fair interview question:

1. **Purpose and scope** — what decision this model supports, and what it may **not** be used for
2. **Data** — sources, period, exclusions, and **why each exclusion**
3. **Target definition** — the default definition and observation/performance windows
4. **Methodology and rationale** — including **why alternatives were rejected**
5. **Variable selection** — screening, IV, correlation, final set
6. **Estimation results** — coefficients, standard errors, signs
7. **Validation** — discrimination, calibration, stability; in-sample, out-of-sample, out-of-time
8. **Limitations** — explicit, unhedged
9. **Monitoring plan** — metrics, thresholds, review triggers, redevelopment criteria
10. **Governance** — approvals, versions, change log

> **► SAY THIS** — *"The limitations section is the one a validator reads first. A model documentation pack with no limitations section isn't a confident model, it's an incomplete one."*

### 13.4 The honesty principle

> **A model is credible not because it's clever, but because every limitation is named out loud before anyone has to ask.**
>
> Naming your own weaknesses first is **literally the job description** of a risk professional. Lead with the caveat and the interviewer stops hunting for it.

---
---

# §14 · THE INDIAN CONTEXT

### 14.1 Who regulates what

**RBI** regulates banks, NBFCs, HFCs, ARCs, payment systems, and the credit bureaus under CICRA 2005. For everything in this document, RBI is the relevant authority. **NHB** retains a role in housing finance; **SEBI** and **IRDAI** sit outside credit risk.

### 14.2 The current framework, and the one that's coming

**Today: IRAC** — Income Recognition, Asset Classification and Provisioning. An **incurred loss** regime, rule-based:

| Classification | Trigger | Provision |
|:--|:--|:--|
| Standard | No overdue | **0.40%** general |
| SMA-0 / 1 / 2 | 1–30 / 31–60 / 61–90 DPD | *(still standard)* |
| **NPA — Substandard** | **>90 DPD** | **15%** secured, **25%** unsecured |
| Doubtful D1 / D2 / D3 | 12m / 1–3y / >3y as doubtful | Secured **25/40/100%**, **unsecured portion 100%** |
| Loss | Identified, not written off | **100%** |

**Two rules that get asked constantly:**
- **Upgrade requires the ENTIRE arrears cleared** — not DPD falling below 90. Clarified by RBI in **November 2021** after lenders were upgrading on partial payment.
- **DPD must be stamped daily**, at day-end. Not monthly.

⚖️ **Coming: the ECL framework.** On **27 April 2026** RBI issued **final Directions on Asset Classification, Provisioning and Income Recognition**, moving Indian banks from incurred loss to forward-looking ECL.

| | |
|:--|:--|
| **Effective** | **1 April 2027** |
| **Applies to** | Scheduled Commercial Banks **excluding** RRBs, SFBs, Payments Banks; plus All India Financial Institutions |
| **Glide path** | Capital/P&L impact may be spread to **31 March 2031** |
| **Structure** | Three stages, SICR as the Stage 1→2 trigger — the IFRS 9 architecture |
| **Distinctively Indian** | RBI layered **product-wise prudential provisioning floors** on Stage 1 and Stage 2 as regulatory backstops |
| **Governance** | Board oversight, a designated committee including CFO and CRO, model inventories, independent validation, datasets spanning **at least one credit cycle** |

**RBI held the April 2027 date despite banks requesting a delay.**

> **► SAY THIS — probably the strongest thing you can say tomorrow**
> *"The ECL Directions are the biggest change to Indian bank provisioning in decades — final Directions April 2026, effective April 2027, glide path to 2031. Substantively it's the IFRS 9 architecture: three stages with SICR as the Stage 1 to Stage 2 trigger. What's distinctively Indian is that RBI layered prudential floors on top, because a purely principles-based framework gives banks too much room to model provisions down. And the real constraint isn't the mathematics — it's data depth and model governance. You need PD, LGD and EAD models on data spanning a full credit cycle, and most institutions' history isn't clean enough at that depth. That's why the glide path runs four years."*

### 14.3 What a retail credit portfolio analytics team actually does

Not model *development* only — mostly **estimation, monitoring and reporting**:

- Maintain PD / LGD / EAD estimates and their **annual re-estimation**
- Run the **monthly monitoring pack**: vintages, roll rates, transition matrices, PSI/CSI, override and deviation rates
- Produce **provisioning numbers** for finance, and **capital numbers** for the regulatory reporting team
- Run **stress tests** and scenario analysis for ICAAP
- Support **model validation** with data, results and documentation
- Investigate **portfolio deterioration** when a metric breaches threshold — the "why is bucket 2 up in the North?" work

> **Interview framing that lands:** *"Model development is episodic; monitoring is the job. Most of the value a portfolio analytics team creates is noticing a deterioration two months earlier than the headline number would have shown it."*

---
---

# §15 · THE FIFTEEN TRAPS

| # | The trap | The truth |
|:--|:--|:--|
| 1 | "Low HL p-value means the model is good" | **Backwards.** HIGH p = calibrated = pass. |
| 2 | "IRB always saves capital vs Standardised" | Only for genuinely low-risk books. High LGD → RW well above 75%. |
| 3 | "Correlation rises with PD" | **Falls** — 0.16 → 0.03. High-PD borrowers are idiosyncratic. |
| 4 | "Retail IRB needs a maturity adjustment" | **No.** Corporate only. |
| 5 | "Capital = stressed loss" | Capital = stressed loss **minus EL**. Forget the subtraction and you double-count. |
| 6 | "SICR means the loan is risky" | SICR is **relative to origination**. Deterioration, not danger. |
| 7 | "A high-IV variable is a great find" | IV > 0.50 on retail = **check for leakage first**. |
| 8 | "PSI is stable so the population is stable" | Compute **CSI per variable**. Offsetting shifts hide inside a stable score. |
| 9 | "Gini 0.85 — excellent model" | On retail, suspect **leakage**. Typical OOT is 0.35–0.65. |
| 10 | "Recalibrate on OOT and report OOT" | **Fitting to what you're measuring.** Recalibrate on test, report on OOT. |
| 11 | "Recalibration can fix any miscalibration" | Only **level** errors. If it fails, it's a **shape** error — redevelop. |
| 12 | "IFRS 9 total vs Basel EL is a fair comparison" | Restrict IFRS 9 to **performing** loans first. Basel EL excludes defaults. |
| 13 | "A positive scorecard coefficient is fine" | Says safer borrowers default more. **Always** a broken bin or collinearity. |
| 14 | "NPA upgrades when DPD drops below 90" | **Full arrears cleared.** RBI, Nov 2021. |
| 15 | "Provisions and capital are the same buffer" | Provisions = **expected** loss. Capital = **unexpected** loss. |

---
---

# §16 · TWENTY-FIVE QUESTIONS

*Cover the right column. Answer out loud. Then check.*

**Tier 1 — must be instant**

| Q | A |
|:--|:--|
| **1.** EL formula? | **PD × LGD × EAD** |
| **2.** Gini from AUC? | **2·AUC − 1** |
| **3.** Basel confidence level? | **99.9%**, G(0.999) = 3.09023 |
| **4.** RWA from K? | **K × 12.5 × EAD**; risk weight = K × 12.5 |
| **5.** Standardised retail risk weight? | **75%** |
| **6.** Basel PD floor? | **0.03%** |
| **7.** Other Retail correlation range? | **0.03 to 0.16**, falling as PD rises |
| **8.** QRRE and mortgage correlations? | **0.04** and **0.15**, both fixed |
| **9.** Three IFRS 9 stages? | 12-month ECL / lifetime ECL / lifetime with PD = 1 |
| **10.** SICR DPD backstop? | **30+ DPD**, rebuttable presumption |
| **11.** PSI stability threshold? | **< 0.10** stable; > 0.25 redevelop |
| **12.** IV "useful" band? | 0.10–0.30 medium; **>0.50 suspect leakage** |
| **13.** Formula: WoE? | ln(% non-defaulters in bin ÷ % defaulters in bin) |
| **14.** PDO → Factor? | **Factor = PDO ÷ ln2**; PDO 20 → 28.8539 |
| **15.** Definition of default? | **90+ DPD** OR unlikely-to-pay without recourse to realising security |

**Tier 2 — analytical**

**16. Why does asset correlation fall as PD rises?**
*Supervisory logic: a borrower already very likely to default is failing for personal reasons — they're in trouble whatever the economy does. A very safe borrower only defaults if something systemic goes wrong. So high-PD borrowers are more idiosyncratic and low-PD borrowers more systematic. Lower correlation means losses are less likely to arrive simultaneously, so less capital is required.*

**17. Your model has Gini 0.38 but Hosmer–Lemeshow p = 3×10⁻⁷ out of time. Deploy it?**
*Not for anything that multiplies by the PD. It ranks acceptably — 0.38 is a normal retail Gini — but the calibration failure means the PD levels are wrong, and Basel capital and IFRS 9 ECL both multiply by PD, so I'd be setting capital off a broken number. I could still use it for rank-ordering decisions like approve/decline cut-offs, where only the ordering matters. Before deciding I'd try intercept recalibration; if that doesn't fix it, it's a shape error rather than a level error and the model needs redevelopment. I'd also check whether HL is being driven by sample size — on 200,000 loans a trivial miscalibration produces a tiny p-value, so I'd read the calibration table to size the actual error before condemning it.*

**18. PSI is 0.01 but CSI on two variables is near 4. What's happening and what do you do?**
*The score distribution is stable while the underlying population has lurched — the two shifts are offsetting, or a WoE MISSING bin is absorbing the change. That's exactly why you never compute PSI alone. The usual cause is a data-collection change: a field that wasn't captured in the development vintages becomes populated later, so all the early rows sat in one MISSING bin and new loans land in bins the model barely learned from. If that's it, those variables are measuring my data pipeline rather than the borrower, and I'd drop them as collection artefacts and refit — not try to model around them.*

**19. Why can recalibration preserve Gini exactly?**
*Intercept recalibration re-estimates only β₀ with every slope frozen, which shifts all PDs by the same amount in log-odds space. A monotonic transformation of the scores can't change their ordering, and AUC, Gini and KS depend only on ordering. So Gini is provably unchanged — which is also the check: if Gini moves after intercept recalibration, something is wrong with the implementation.*

**20. Platt scaling calibrates slightly better than intercept recalibration. Which do you pick for a scorecard?**
*Intercept recalibration, usually. Platt fits a slope as well as an intercept, and that slope rescales every variable's contribution — which distorts the integer point values and breaks the PDO relationship that makes the scorecard interpretable. Interpretability is the entire reason we chose a scorecard over a GBM, so trading it away for a marginal calibration gain is the wrong trade. I'd document the choice and the small cost.*

**21. Why does CECL always provision more than IFRS 9?**
*No staging. Every loan carries a lifetime ECL from day one, so healthy performing loans that would sit in Stage 1 with a 12-month provision instead carry a full lifetime provision. Since lifetime PD runs around three times 12-month PD on retail, the Stage 1 population's provision multiplies. Nothing about the loans changes — the entire difference is the accounting framework.*

**22. Two variables have IV of 0.08 and 1.8. Which worries you?**
*The 1.8. On retail data, an IV above 0.5 usually means leakage — a post-origination field that encodes the outcome. I'd check when the variable is populated relative to origination before I did anything else. The 0.08 is simply weak, which is normal and unalarming; a lot of genuine borrower fundamentals sit in weak territory.*

**Tier 3 — judgement, where interviews are won**

**23. You're asked to build a PD model. Walk me through it.**
*Target first, because everything depends on it: define default — typically 90+ DPD — and set the observation and performance windows, usually twelve months, being careful about right-censoring so recent loans that haven't had time to default aren't counted as good. Then a strict split: out-of-sample for overfitting and out-of-time for temporal robustness, because OOT is what actually matters. Then variable governance — screen out anything known only after origination, which is the single biggest source of leakage. Then bin, WoE-transform, screen by IV, check correlations, fit a logistic regression on the WoE values, verify every coefficient is negative. Then scale to points and cut into grades, checking rank ordering holds monotonically. Then validate on all three axes — discrimination, calibration, stability — with PSI and per-variable CSI. Then document, including the limitations, and set the monitoring thresholds that will trigger review.*

**24. A senior colleague says your model is too conservative and is costing the bank business. Response?**
*I'd want to separate two claims, because they need different evidence. If the model is miscalibrated upward — predicting higher PDs than materialise — that's a factual question and the calibration table settles it. If it's correctly calibrated but the bank's risk appetite is set tighter than it needs to be, that's a policy decision, not a model defect, and it belongs with the credit policy committee rather than with me. Either way I'd bring the swap-set analysis: which applications would flip to approve under the proposed change, and what those segments' historical performance looks like. And I'd want the decision documented with a review trigger, because the cost of being wrong is a full vintage and we won't see it for nine months.*

**25. What's the most important thing in a model documentation pack?**
*The limitations section, and I'd argue that genuinely rather than as a nice sentiment. A validator's job is effective challenge, and the first thing they do is look for what the developer didn't say. A pack that names its own approximations — a proxied origination PD, a supervisory-proxy downturn LGD, a simplified EIR discount — tells the validator the developer understood the model's boundaries. A pack with no limitations section isn't a confident model, it's an incomplete one. And practically, leading with the caveat means the interviewer or the validator stops hunting for it.*

---
---

# §17 · FORMULA SHEET

**Expected loss**
$$\text{EL} = \text{PD}\times\text{LGD}\times\text{EAD}$$

**Exposure at default**
$$\text{EAD}_{\text{term}} = \max(\text{funded} - \text{principal repaid},\,0) \qquad \text{EAD}_{\text{revolving}} = \text{drawn} + \text{CCF}\times\text{undrawn}$$

**Loss given default**
$$\text{LGD} = \frac{\max(\text{EAD} - \text{recoveries},\,0)}{\text{EAD}} \qquad \widehat{\text{LGD}}_{\text{2-stage}} = 1 - \big[P(\text{rec})\times\widehat{rr}_{|\text{rec}}\big]$$

**WoE and IV**
$$\text{WoE} = \ln\frac{\%\text{good}}{\%\text{bad}} \qquad \text{IV} = \sum(\%\text{good}-\%\text{bad})\cdot\text{WoE}$$

**Scorecard scaling**
$$\text{Factor} = \frac{\text{PDO}}{\ln 2} \qquad \text{Offset} = \text{TargetPts} - \text{Factor}\ln(\text{TargetOdds})$$
$$\text{Points}_{\text{bin}} = \text{BasePts} + \text{Factor}\cdot(-\beta_j\text{WoE}) \qquad \text{BasePts} = \frac{\text{Offset}-\text{Factor}\cdot\beta_0}{m}$$

**Basel correlation — Other Retail**
$$R = 0.03w + 0.16(1-w), \quad w = \frac{1-e^{-35\text{PD}}}{1-e^{-35}}$$
QRRE R = 0.04 · Mortgage R = 0.15

**Basel capital**
$$K = \text{LGD}\left[N\!\left(\frac{G(\text{PD})+\sqrt{R}\,G(0.999)}{\sqrt{1-R}}\right)-\text{PD}\right] \qquad \text{RWA}=K\times12.5\times\text{EAD}$$
PD floor 0.0003 · no maturity adjustment for retail · SA retail RWA = 0.75 × EAD

**Hazard and lifetime PD**
$$h(m)=\frac{d_m}{n_m} \qquad S(m)=\prod_{k=1}^{m}(1-h(k)) \qquad \text{PD}_{\text{cum}}(m)=1-S(m)$$

**IFRS 9 ECL**
$$\text{ECL}_1=\text{PD}_{12m}\text{LGD}\cdot\text{EAD} \quad \text{ECL}_2=\text{PD}_{\text{life}}\text{LGD}\cdot\text{EAD} \quad \text{ECL}_3=\text{LGD}\cdot\text{EAD}$$
$$\text{ECL}_{\text{reported}}=\sum_s w_s\cdot\text{ECL}(s) \quad\text{over macro scenarios}$$

**CECL** — lifetime, every loan, always.

**Validation**
$$\text{Gini}=2\text{AUC}-1 \qquad \text{KS}=\max_s|F_{\text{bad}}(s)-F_{\text{good}}(s)|$$
$$\text{PSI}=\sum(\%_a-\%_e)\ln\frac{\%_a}{\%_e} \qquad \text{Brier}=\frac{1}{n}\sum(p_i-y_i)^2$$
HL: **high p = calibrated** · PSI < 0.10 stable

**Capital ratios** — CET1 ≥ 4.5% · Tier 1 ≥ 6% · Total ≥ 8% of RWA, plus buffers. India: CRAR 9% + 2.5% CCB.

---
---

# §18 · ACRONYM DECODER

| | |
|:--|:--|
| **ASRF** | Asymptotic Single Risk Factor — the model behind the Basel formula |
| **AUC** | Area Under the ROC Curve |
| **CCF** | Credit Conversion Factor |
| **CECL** | Current Expected Credit Losses (US, ASU 2016-13) |
| **CET1** | Common Equity Tier 1 |
| **CRAR** | Capital to Risk-weighted Assets Ratio |
| **CSI** | Characteristic Stability Index — PSI applied per input variable |
| **EAD** | Exposure at Default |
| **ECL** | Expected Credit Loss |
| **EIR** | Effective Interest Rate |
| **EL / UL** | Expected Loss / Unexpected Loss |
| **ICAAP** | Internal Capital Adequacy Assessment Process (Pillar 2) |
| **IRAC** | Income Recognition, Asset Classification and Provisioning (RBI) |
| **IRB** | Internal Ratings Based approach |
| **IV** | Information Value |
| **KS** | Kolmogorov–Smirnov statistic |
| **LGD** | Loss Given Default |
| **MOB** | Months on Book |
| **NPA / SMA** | Non-Performing Asset / Special Mention Account |
| **OOT** | Out of Time |
| **PD** | Probability of Default |
| **PDO** | Points to Double the Odds |
| **PIT / TTC** | Point-in-Time / Through-the-Cycle |
| **PSI** | Population Stability Index |
| **QRRE** | Qualifying Revolving Retail Exposure |
| **RWA** | Risk-Weighted Assets |
| **SICR** | Significant Increase in Credit Risk |
| **SR 11-7** | US Fed supervisory guidance on model risk management |
| **WoE** | Weight of Evidence |

---
---

# §19 · THE LAST FIFTEEN MINUTES

**Read only this.**

**Eight facts, cold:**
1. **EL = PD × LGD × EAD.** Provisions cover **expected** loss; capital covers **unexpected** loss.
2. **K = LGD × (stressed PD − PD).** The subtraction is the whole point. **RWA = K × 12.5 × EAD.**
3. Basel at **99.9%**, G(0.999) = **3.09**. Correlation **falls** as PD rises (0.16 → 0.03). **No maturity adjustment for retail.**
4. **Gini = 2·AUC − 1.** Retail OOT typically 0.35–0.65. Above 0.75, suspect leakage.
5. **Hosmer–Lemeshow: HIGH p = PASS.** And HL is sample-size sensitive — read the calibration table too.
6. **PSI < 0.10 stable. Always compute per-variable CSI as well.**
7. **IFRS 9 staging is RELATIVE to origination.** Stage 2 = lifetime ECL. 30 DPD is the rebuttable backstop.
8. **Basel EL < IFRS 9 < CECL** — and compare only on the performing population.

**Four sentences that will do more work than anything else:**

> *"Correlation falls as PD rises because a high-PD borrower is already failing for idiosyncratic reasons, while a safe borrower only defaults if something systemic goes wrong."*

> *"Never compute PSI without per-variable CSI — offsetting shifts can leave the score distribution stable while the population has lurched underneath."*

> *"If recalibration doesn't fix the miscalibration, it's a shape problem, not a level problem, and no rescaling will repair it — the model needs redevelopment."*

> *"The ECL Directions are the biggest change to Indian bank provisioning in decades — effective April 2027, IFRS 9 architecture with RBI prudential floors layered on top. The binding constraint is data depth and model governance, not the mathematics."*

**Three postures:**

- **When you don't know:** *"I don't have that threshold offhand — I'd check the current Master Direction. What I do know is the principle behind it, which is…"* **This is a strong answer.** Fabricating a number is the only fatal one.
- **When asked about your own work:** **lead with the limitation before they find it.** Naming your own approximations first is literally the job of a risk professional.
- **When stuck:** think out loud. In risk interviews **the reasoning is the answer.** A candidate who reasons cleanly to a wrong number beats one who guesses the right number silently.

---

**You know more than you think you do. Go and be the calmest person in the room.**
