---
title: "Retail Credit Risk and Modelling in India"
subtitle: "How an Indian lender decides, prices, provisions and capitalises the millions of small loans it will never individually judge"
spine: "Retail credit risk replaces judgement about one borrower with measurement of many, so every decision downstream is a bet on a rate rather than on a person."
date: 2026-08-04
slug: "retail-credit-risk-and-modelling-india"
archetype: system
tags: [credit-risk, retail-banking, india, rbi, scorecards, ecl, irac, basel, pd-lgd-ead, model-risk]
readingTime: 65
passes: [65, 85, 30]
prerequisites: ["basic probability", "natural logarithms", "reading a table of percentages", "Indian number system: 1 lakh = 100,000 and 1 crore = 100 lakh = 10,000,000"]
series: "Risk Systems"
seriesOrder: 1
status: draft
---

# Retail Credit Risk and Modelling in India

### How an Indian lender decides, prices, provisions and capitalises the millions of small loans it will never individually judge

> Retail credit risk is the discipline of replacing a judgement about one borrower with a measurement of many: nobody can know whether *this* account will stop paying, but anyone with enough history can know what fraction of accounts like it will — and every decision a lender makes, from sanction to price to provision to recovery, is built on that fraction.

---

# HOW TO READ THIS

| Pass | What you do | Budget |
|---|---|---|
| 1 · Understand | Read the prose only. Skip every callout, table and worked example. You are after the shape of the system: where the numbers come from and who consumes them. | 65 min |
| 2 · Verify | Reproduce every 🧮 WORKED calculation by hand, on paper, with a calculator. If a number does not come out, the misunderstanding is yours or the note's — find out which. | 85 min |
| 3 · Recall | §1, §17, §18, §19 only. Numbers, traps, self-test, formulas. Repeat until §18 tier 1 is instant. | 30 min |

All amounts are in Indian rupees (₹). One lakh is 100,000; one crore is 100 lakh, or 10,000,000. The regulator throughout is the Reserve Bank of India (RBI), the central bank that writes the prudential rules for banks and non-banking financial companies.

---

# §1 · THE NUMBERS

**These are the thresholds, floors and risk weights that the rest of the subject is built on; where a figure is a rule of thumb rather than a rule, the row says so.**

| Quantity | Value | Why it matters |
|---|---|---|
| Non-performing asset (NPA) trigger, term loan | Interest or principal overdue more than 90 days | The single most consequential number in Indian credit; every PD model is a model of this event |
| NPA trigger, credit card | Minimum amount due unpaid for 90 days from the statement payment due date | Cards have their own clock, running off the statement rather than an instalment |
| "Out of order" trigger, cash credit / overdraft | Outstanding above sanctioned limit or drawing power for 90 continuous days, OR no credits for 90 days, OR credits insufficient to cover interest debited in the previous 90 days | Revolving facilities cannot be measured in missed instalments, so a three-limbed test replaces days past due |
| Special Mention Account (SMA) buckets | SMA-0: 1–30 days overdue · SMA-1: 31–60 · SMA-2: 61–90 | The pre-NPA early-warning ladder; roll rates through these buckets are the fastest honest signal in a portfolio |
| Level of NPA classification | Borrower level — if one facility is NPA, all facilities of that borrower are NPA | A single defaulted credit card contaminates the same customer's housing loan |
| NPA upgradation condition | Entire arrears of interest and principal repaid, across all facilities of the borrower | Partial payment does not upgrade; this makes cure a discrete, all-or-nothing event |
| NPA sub-categories | Sub-standard: NPA for up to 12 months · Doubtful: 12 months in sub-standard · Loss: identified as uncollectable | Ageing drives provisioning under the incurred-loss regime |
| Expected credit loss (ECL) framework commencement | 1 April 2027, under the RBI (Commercial Banks – Asset Classification, Provisioning and Income Recognition) Directions, 2026, notified 27 April 2026 | Replaces incurred-loss provisioning for commercial banks while *retaining* the NPA definition |
| ECL transition add-back to core capital | Fractions 4/5, 3/5, 2/5, 1/5 of the day-one shortfall across FY2027-28 to FY2030-31 | The capital hit is spread over four years rather than taken at once |
| Significant increase in credit risk (SICR) backstop | 30 days past due, rebuttable; for revolving facilities, continuously above sanctioned limit or drawing power for up to 60 days | The trigger that moves an account from 12-month to lifetime loss allowance |
| Regulatory floor on 12-month PD | 0.03% | No exposure may be modelled as riskless |
| Regulatory backstop loss given default (LGD) | 65% secured portion, 70% unsecured portion; 30% where collateral is cash, gold, central or state government securities, LIC policies, Kisan Vikas Patra or National Savings Certificates | Applies where a bank cannot reliably estimate LGD itself |
| Prudential provisioning floor, unsecured retail | Stage 1: 1.00% · Stage 2: 5% · Stage 3: 25% in year one, 100% thereafter | The regulatory backstop under a modelled number; it frequently binds |
| Prudential floor, secured retail | Stage 1: 0.40% · Stage 2: 5% | Binding on good-quality secured books where modelled ECL is tiny |
| Prudential floor, individual housing loan | Stage 1: 0.25% · Stage 2: 1.50% | The lowest floor in the schedule, reflecting collateral |
| Minimum capital to risk-weighted assets ratio (CRAR), banks | 9%, or 11.5% including the 2.5% capital conservation buffer; minimum common equity tier 1 (CET1) 5.5%, or 8% with the buffer; tier 1 7% | India runs above the global Basel minimum of 8% |
| Minimum CRAR, non-banking financial companies | 15% for the middle layer and above, with tier 2 capped at 100% of tier 1; upper-layer entities also hold CET1 of 9% | Non-bank lenders are capitalised far more heavily per rupee of asset |
| Risk weight, regulatory retail portfolio | 75% | The base rate for qualifying small, granular exposures |
| Regulatory retail qualifying thresholds | Aggregate exposure to one counterparty ≤ ₹10 crore; no counterparty above 0.2% of the portfolio; small-business turnover ≤ ₹500 crore | Fail any one and the exposure leaves the 75% bucket |
| Risk weight, personal loans and credit card revolvers | 125% | Unsecured consumer credit is deliberately penalised |
| Credit card transactor definition and reward | Balance repaid in full at every scheduled due date, including the three-day grace period, for the previous 12 months → 75% instead of 125% | Behavioural, not product-based; one day of delinquency resets the twelve-month clock |
| Risk weight, individual housing loan, first two loans | 20% at loan-to-value (LTV) ≤50%, 25% at 50–60%, 30% at 60–80%, 40% at 80–90%; add 5 percentage points if total outstanding is ₹3 crore or above | Capital now moves with LTV in fine steps rather than in two coarse bands |
| Risk weight, individual housing loan, third onward | 30% / 35% / 45% / 60% across the same LTV bands | Investor mortgages cost roughly half as much again in capital |
| Credit conversion factor (CCF), unconditionally cancellable commitments | 5% for the first three years from 1 April 2027, then 10% | Unused credit card limits stop being free of capital |
| Risk weight on NPAs, unsecured portion net of provisions | 150% if specific provisions are under 20%; 100% at 20% or more; 50% at 50% or more | Provisioning buys capital relief on defaulted assets |
| Gold loan LTV ceilings, from 1 April 2026 | 85% up to ₹2.5 lakh, 80% for ₹2.5–5 lakh, 75% above ₹5 lakh | India's most collateral-efficient retail product, and the only one where LTV is capped by ticket size |
| Credit bureau reporting cadence | Fortnightly, on the 15th and last day of each month, since 1 January 2025; ₹100 per day compensation if a data complaint is unresolved beyond 30 days | Determines how stale the single most predictive data source can be |

**You can now:**
- Quote the NPA trigger, the SICR backstop, the retail risk weights and the unsecured retail provisioning floors without looking them up.
- Recognise when a claimed risk weight, LGD or provisioning rate is outside what the Indian rulebook permits.

---

# §2 · THE MAP

**Indian retail credit risk is one data layer feeding three decision points, which produce three risk parameters, which are consumed by three different businesses — pricing, provisioning and capital — under a regulator that lets you model the second but not the third.**

```
                       DATA
   application form | 4 credit information companies
   own-account behaviour | Account Aggregator | macro
                          |
     +--------------------+--------------------+
     v                    v                    v
 [ ACQUIRE ]          [ MANAGE ]           [ COLLECT ]
 apply / score /      limit / renew /      SMA / NPA /
 KFS / sanction  -->  re-price / block --> recover / sell
     |                    |                    |
 application          behavioural          collections
 scorecard            scorecard            score
     +--------------------+--------------------+
                          v
              PD   x   LGD   x   EAD
             (odds)   (severity) (exposure)
                          |
       same three parameters, three calibrations
     +--------------------+--------------------+
     v                    v                    v
  PRICING            PROVISIONS            CAPITAL
  spread over        IRACP until           RBI Standardised
  benchmark,         31 Mar 2027,          Approach only:
  RAROC              ECL from              fixed risk
                     1 Apr 2027,           weights.
                     + prudential          No internal
                       floors              models permitted
     +--------------------+--------------------+
                          v
      MONITOR: Gini | PSI | vintage | GNPA | roll rates
                          |
                          +---> redevelop ---> DATA
```

Three structural facts hold the diagram together, and the third is specific to India.

First, the three parameters are estimated once conceptually but calibrated three times numerically: pricing wants today's odds, provisioning wants today's odds plus a macroeconomic forecast, and capital in most jurisdictions wants a long-run average stressed to a downturn.

Second, the feedback loop is *censored* — outcomes are observed only on borrowers who were sanctioned, so the data that trains tomorrow's model was selected by today's.

Third, and unusually, the right-hand branch of the diagram does not use the bank's models at all. The RBI has implemented only the Standardised Approach for credit risk capital, in which risk weights come from a supervisory table. The Internal Ratings Based approach, under which a bank's own PD and LGD estimates feed a capital formula, is not available to Indian banks. Modelling effort therefore pays for itself through pricing, provisioning and selection — never through a lower capital charge on a given exposure.

📘 **DEFINE — Retail exposure**
An exposure to an individual or a very small business, small enough relative to the lender that it is managed as one of a large pool of similar exposures rather than assessed individually. The RBI formalises this as the *regulatory retail portfolio*, which an exposure joins only by passing four tests at once: it is to an individual, a Hindu Undivided Family or a small business with turnover up to ₹500 crore (orientation); it is a revolving credit, term loan, lease, small-business facility or education loan (product); the aggregate exposure to that counterparty is at most ₹10 crore (low value); and no single counterparty exceeds 0.2% of the whole retail portfolio (granularity). The consequence is statistical rather than legal: because exposures are homogeneous and numerous, the law of large numbers applies to the *rate* of default even though each individual outcome is unknowable. Everything in this note follows from that one property.

**You can now:**
- Draw the whole system from memory: data → three decisions → three parameters → three consumers → monitoring → back to data.
- State the four qualifying criteria for the regulatory retail portfolio.
- Explain why modelling skill in an Indian bank is rewarded through pricing and provisions but not through capital.

---

# §3 · THE LOSS EQUATION

**Every number in retail credit risk is either an input to expected loss, an output of it, or a check on it.**

Expected loss is the product of three independent questions asked about the same account. Will it default? If it does, what fraction of the amount owed will never be recovered? And how much will be owed at that moment, which is not the same as how much is owed now. Multiply the three and you have the average loss to expect from an account of this type, per year or per lifetime depending on the horizon of the first term.

$$EL = PD \times LGD \times EAD$$

- $EL$ — expected loss, in rupees: the mean loss over many accounts like this one.
- $PD$ — probability of default, a number between 0 and 1, for a stated horizon, usually 12 months.
- $LGD$ — loss given default, the fraction of exposure not recovered after costs and discounting.
- $EAD$ — exposure at default, the rupee amount outstanding at the moment default occurs.

The word *expected* is doing heavy lifting. Expected loss is a mean, and no individual account ever experiences it: an account either defaults or it does not. A ₹5,00,000 personal loan with a 4% PD and a 70% LGD has an expected loss of ₹14,000, but the actual loss is either nil (96% of the time) or about ₹3,50,000 (4% of the time). The ₹14,000 is a price, not a prediction.

🧮 **WORKED — Expected loss on one loan and on a book of a thousand**

| Step | Calculation | Result |
|---|---|---|
| 1. Exposure at default | Drawn ₹4,50,000 + 25% of ₹2,00,000 undrawn | ₹5,00,000 |
| 2. Probability of default, 12 months | From the scorecard | 0.04 |
| 3. Loss given default | 1 − 30% recovery | 0.70 |
| 4. Expected loss, one account | 0.04 × 0.70 × 5,00,000 | **₹14,000** |
| 5. Book of 1,000 such accounts | 1,000 × 14,000 | **₹1.40 crore** |
| 6. Expected number of defaults | 1,000 × 0.04 | 40 |
| 7. Loss per defaulting account | 0.70 × 5,00,000 | ₹3,50,000 |
| 8. Check: 40 × 3,50,000 | Must equal step 5 | **₹1.40 crore ✓** |

Two things follow immediately. Expected loss is a cost of doing business, so it belongs in the price, not in the capital: a lender charging enough spread to cover ₹14,000 per loan is not taking risk on the average, it is taking risk on the *variation around* the average. That variation is unexpected loss, and it is the thing capital exists for.

🔍 **WHY THIS IS TRUE — Capital covers only the surprise**
The natural assumption is that capital is held against losses. It is not; it is held against losses *beyond those already paid for*. Expected loss is charged to customers in the interest spread and recognised in the accounts as a provision, so by the time a loss arrives at its expected size it has been funded twice over. What destroys a lender is a year in which realised losses are three or five times the expected level, because nothing has been set aside for the excess. In India this split is visible in the balance sheet itself: provisions sit against the loan book and absorb expected loss, while the CRAR — the ratio of capital to risk-weighted assets, minimum 9% and 11.5% with the buffer — sits above it and absorbs the surprise. A lender that confused the two would either under-provide and over-capitalise, or the reverse, and could not explain either number to a supervisor.

⚖️ **TRADE-OFF — Where you put conservatism**
Conservatism has to live in one of the three parameters, and the choice is not neutral. Padding PD raises expected loss and changes who gets sanctioned, because PD drives the cut-off. Padding LGD raises expected loss roughly proportionally but leaves the approve/decline ranking untouched, since LGD rarely varies much within a product. Padding EAD raises everything and also distorts limit-setting. The usual resolution is to keep PD as unbiased as the data allows and place conservatism in LGD and EAD, so that the ranking used for decisions stays clean. The RBI has effectively made the same choice for lenders that cannot estimate their own severity, prescribing backstop LGDs of 65% secured and 70% unsecured — deliberately harsh numbers that penalise not knowing.

► **IN ONE LINE** — Expected loss is a price; unexpected loss is a risk; confusing the two is the single most expensive error in the subject.

**You can now:**
- Compute expected loss for an account and a portfolio and check the two against each other.
- Say precisely why expected loss belongs in pricing and provisions while unexpected loss belongs in capital.

---

# §4 · WHAT "DEFAULT" MEANS IN INDIA

**PD is not a probability of loss, it is a probability of a defined event, and in India that event has a single legal definition — the non-performing asset — which the accounting framework has now adopted verbatim.**

An amount is *overdue* the moment it is not paid on its due date. The clock then runs. For a term loan, the account becomes a non-performing asset when interest or principal has been overdue for more than 90 days. For a credit card, the account becomes an NPA when the minimum amount due shown on the statement remains unpaid for 90 days from the statement's payment due date. For agricultural loans tied to crop cycles the rule is seasonal rather than daily: two crop seasons overdue for short-duration crops, one for long-duration crops.

Revolving facilities cannot be measured in missed instalments, so cash credit and overdraft accounts use a three-limbed *out of order* test instead. The account is out of order if the outstanding balance stays above the sanctioned limit or drawing power for 90 continuous days, or if there are no credits at all for 90 days, or if the credits that do arrive are not enough to cover the interest debited over the previous 90 days. Any one limb is sufficient. The third limb is the subtle one: an account can be inside its limit, receiving money every month, and still be non-performing because the money is not even covering interest.

📘 **DEFINE — Special Mention Account (SMA)**
The pre-NPA early-warning classification that every Indian lender must maintain and report. For loans other than revolving facilities: SMA-0 is 1 to 30 days overdue, SMA-1 is 31 to 60 days, SMA-2 is 61 to 90 days. For cash credit and overdraft accounts the ladder runs on the out-of-order condition instead, with SMA-1 covering 31 to 60 days out of order and SMA-2 covering 61 to 90. The buckets are conventional rather than natural — nothing changes about a borrower on the 31st day — but they are universal in India, so roll rates, early-warning systems and supervisory reporting are all expressed in them. The boundary between SMA-2 and NPA is not a step on a ladder but the edge of a cliff, because crossing it changes income recognition, provisioning, capital and the borrower's bureau record simultaneously.

Two Indian rules make classification harsher than a naive reading suggests. Classification is applied at the *borrower* level, not the facility level: if any one exposure to a borrower is NPA, every exposure to that borrower is NPA, including facilities that have never missed a payment. And the day-end process is definitive — an account is flagged overdue as part of the day-end run for the due date, and becomes NPA on the calendar date whose day-end run finds it 90 days overdue. There is no month-end smoothing and no discretion about the date.

🔴 **TRAP — "The borrower paid something, so the account should improve"**
The wrong belief is that partial repayment upgrades a defaulted account. It does not. An NPA may be upgraded to standard only when the *entire* arrears of interest and principal are repaid, and where the borrower has more than one facility, only when the arrears on *all* facilities are cleared. Borrower and co-borrower are jointly and severally liable for this purpose. The correction matters for modelling because it makes cure a discrete, lumpy, all-or-nothing event rather than a gradual recovery, which in turn makes the distribution of outcomes after default sharply bimodal and makes any LGD model built on average behaviour misleading.

Default is not the same as loss, because accounts cure. A borrower who reaches 90 days overdue and then clears the arrears in full has defaulted and produced no loss at all. Cure rates are high enough to change everything: on secured retail lending they commonly run at a third to a half of defaults, and on unsecured they are lower but far from zero. This is why LGD is modelled rather than assumed to be one.

✅ **CHECK — Definition consistency**
Take the default flag used to build the model, the flag used to classify accounts as NPA for supervisory reporting, and the flag that will drive Stage 3 under the ECL framework, and run all three over the same month of data. Pass condition: the three populations agree to within a few percent, and every disagreement traces to a documented rule rather than a surprise. Under the 2026 Directions this test is easier to pass than it would be elsewhere, because the accounting definition of default is *defined as* NPA status — but only if the model was built on the NPA event and at borrower level. A model trained on facility-level 90 days past due will systematically under-count defaults relative to the borrower-level regulatory definition.

**You can now:**
- State the NPA trigger for a term loan, a credit card and a cash credit account, and the three limbs of the out-of-order test.
- Explain why borrower-level classification makes a single small default expensive.
- Explain a cure and why the all-or-nothing upgradation rule makes LGD bimodal.

---

# §5 · WINDOWS, VINTAGES AND THE SHAPE OF THE DATA

**A credit model is trained on a photograph of the past taken at one moment and a verdict delivered some months later, and almost every serious modelling error is an error in choosing those two moments.**

The photograph is the *observation point*: a date at which you freeze everything known about an account — application data, bureau data, balances, payment history. The verdict is the *outcome window*: a fixed period after the observation point during which you watch for the default event. An account that becomes NPA at any time inside the window is a *bad*; one that never does is a *good*. The model learns the relationship between the photograph and the verdict, and it can only ever predict over the window length on which it was trained.

Window length is a genuine trade-off rather than a technical detail. Twelve months is the standard for unsecured personal loans and cards because it captures most of the emergence and keeps the development sample recent. Housing loans need 24 months or more, because their defaults arrive slowly. But a long window means the most recent usable observation point is that far in the past, so a housing model trained on a 24-month window is built on borrowers from at least two years ago, and it inherits their economy, their property prices and their competitive environment.

🔍 **WHY THIS IS TRUE — Loss runs on vintage time, not calendar time**
Read a portfolio by calendar month and you will see the delinquency rate rise and fall and blame the economy. Read it by *vintage* — grouping accounts by the month they were disbursed and measuring performance by months-on-book — and something else appears: nearly every retail portfolio has a characteristic hump. Bad rates start near zero, since nobody becomes 90 days overdue in month one, climb steeply to a peak somewhere between 9 and 18 months for unsecured products, then flatten as the surviving population self-selects toward good payers. A calendar-time chart mixes vintages at different points on that hump, so a book growing at 30% a year looks better than it is, simply because it is full of young accounts that have not had time to fail. The economy is real, but seasoning explains more month-to-month movement than the economy does, and separating the two is the first job of portfolio analysis.

## Where Indian retail data comes from

Four sources matter, and their properties differ sharply.

*Application data* is what the borrower tells you: income, employment, residence, and the identity documents behind it — permanent account number, Aadhaar-based verification, bank statements. It is rich, cheap and partly self-reported, which is exactly the combination that produces optimistic models.

*Bureau data* comes from the four credit information companies (CICs) licensed under the Credit Information Companies (Regulation) Act, 2005 — TransUnion CIBIL, Experian, Equifax and CRIF High Mark. Every lender must be a member of all of them and must report to all of them. Since 1 January 2025 reporting is fortnightly, on the 15th and last day of each month, in a prescribed Uniform Credit Reporting Format with separate schemas for consumer, commercial and microfinance segments. Bureau scores conventionally run from 300 to 900.

*Own-account behaviour* — how this customer has actually paid you — is the single most predictive source available, and the reason behavioural scorecards outrank application scorecards by a wide margin.

*Consented external data* arrives through the Account Aggregator framework, under which a customer can authorise the sharing of bank statements and other financial data between regulated entities. It is the closest thing in India to income verification for the self-employed and informally employed, who are a large share of borrowers and are invisible to salary-slip underwriting.

📘 **DEFINE — Indeterminates**
Accounts whose outcome is neither clearly good nor clearly bad within the window: typically those that reached SMA-1 or SMA-2 but never became NPA, or that closed early for reasons unrelated to credit. They are usually excluded from scorecard development, on the reasoning that counting them as goods teaches the model that near-misses are fine and counting them as bads teaches it that a single late payment is fatal. Exclusion is not free — a large indeterminate population means the model is trained on a sharpened version of reality and its predicted odds need recalibrating back onto the full population. The rule of thumb is that indeterminates above roughly 5–10% of the sample deserve a written justification rather than a default exclusion.

Three sampling decisions follow. The sample must be drawn at a point in time or across a band of adjacent months, not pooled across years, or the model will fit the economy rather than the borrower. Bads are rare — a 4% bad rate means 96 rows of noise for every 4 rows of signal — so they are often kept in full while goods are randomly sampled down, which speeds estimation but shifts the intercept and requires a correction. And the sample must be a snapshot of *accounts*, not of applications, unless the model's job is to score applications.

$$\beta_0^{corrected} = \hat{\beta}_0 - \ln\left(\frac{\rho_1}{\rho_0}\right)$$

- $\hat{\beta}_0$ — the intercept estimated on the oversampled data.
- $\rho_1$ — the sampling fraction applied to bads, usually 1, meaning all were kept.
- $\rho_0$ — the sampling fraction applied to goods, for example 0.1 if one in ten was kept.
- Only the intercept moves; the slope coefficients are unaffected by this kind of sampling, which is why the correction is safe.

✅ **CHECK — Is the outcome window long enough?**
Plot the cumulative bad rate for a mature vintage against months-on-book. Pass condition: at the chosen window length the curve has flattened enough that extending it by six more months would add less than about 10% to the cumulative bad rate. If the curve is still climbing steeply at the cut-off, the window is short, the model is being trained on early defaulters only, and it will rank fraud and severe distress well while ranking ordinary credit deterioration poorly.

**You can now:**
- Design an observation point and outcome window for a given product and defend the length.
- Name the four Indian retail data sources and state which is most predictive and why.
- Correct the intercept of a model fitted on an oversampled sample.

---

# §6 · BUILDING A SCORECARD

**A scorecard is a logistic regression on transformed variables, converted into integer points, and almost all of the craft is in the transformation rather than the regression.**

Start with the target. You have a table of accounts, one row each, with a binary flag from §5 — bad or good — and a few hundred candidate variables: age, declared and verified income, employment type, time at current address, time with the lender, and bureau attributes such as the number of active trade lines, utilisation of revolving limits, number of credit enquiries in recent months, and any prior write-offs, settlements or suit-filed records. The model must estimate the log-odds of being bad as a linear function of these, which is what logistic regression does.

$$\ln\left(\frac{p}{1-p}\right) = \beta_0 + \beta_1 x_1 + \dots + \beta_k x_k$$

- $p$ — probability that the account is bad within the outcome window.
- $\frac{p}{1-p}$ — the odds of being bad; note that lenders conventionally quote *good:bad* odds, which is the reciprocal.
- $\beta_0$ — intercept, setting the overall level of risk.
- $\beta_i$ — coefficient on the $i$-th variable, the change in log-odds per unit of $x_i$.

Raw variables go in badly. Declared income is skewed and partly fictional, age is non-monotonic in risk, missing values are informative rather than absent, and outliers drag coefficients. The industry answer is to *bin* every variable into a handful of ranges and replace each range with a single number encoding its riskiness: the weight of evidence.

## Weight of evidence and information value

Binning happens in two stages. *Fine classing* cuts the variable into twenty or so narrow bins and plots the bad rate of each. *Coarse classing* merges adjacent bins until the pattern is monotonic or at least defensible, every bin holds at least about 5% of the sample, and each bin's bad rate differs meaningfully from its neighbours'. Missing values usually become their own bin, because "declined to state income" is a fact about the applicant.

$$WOE_i = \ln\left(\frac{g_i / G}{b_i / B}\right)$$

- $g_i, b_i$ — count of goods and bads in bin $i$.
- $G, B$ — total goods and total bads in the sample.
- A positive weight of evidence means the bin holds proportionally more goods than the book average, so it is *safer* than average. Some houses put bads on top, flipping every sign; either convention works provided one is used throughout.

$$IV = \sum_i \left(\frac{g_i}{G} - \frac{b_i}{B}\right) \times WOE_i$$

- $IV$ — information value, a single number summarising how much a variable separates goods from bads before any other variable is considered.
- Each term is non-negative, because the difference in proportions and the log-ratio always share a sign.

🧮 **WORKED — Weight of evidence and information value for one characteristic**

Sample: 90,000 goods, 10,000 bads (10% bad rate). Characteristic: number of credit bureau enquiries in the last six months.

| Bin | Goods / Bads | %G, %B, WOE, contribution |
|---|---|---|
| 0 enquiries | 22,500 / 1,200 | %G 0.250, %B 0.120, WOE = ln(2.0833) = 0.7340, contrib = (0.130)(0.7340) = 0.0954 |
| 1–2 | 27,000 / 3,000 | %G 0.300, %B 0.300, WOE = ln(1.0000) = 0.0000, contrib = 0.0000 |
| 3–5 | 22,500 / 1,800 | %G 0.250, %B 0.180, WOE = ln(1.3889) = 0.3285, contrib = (0.070)(0.3285) = 0.0230 |
| 6 or more | 18,000 / 4,000 | %G 0.200, %B 0.400, WOE = ln(0.5000) = −0.6931, contrib = (−0.200)(−0.6931) = 0.1386 |
| **Total** | 90,000 / 10,000 | **IV = 0.0954 + 0 + 0.0230 + 0.1386 = 0.2570** |

An information value of 0.257 sits in the medium band: a genuinely useful variable, not a dominant one. The conventional bands are below 0.02 useless, 0.02 to 0.1 weak, 0.1 to 0.3 medium, 0.3 to 0.5 strong, and above 0.5 suspect — a variable that looks too good is usually a consequence of the default rather than a predictor of it. Note the second bin, whose weight of evidence is exactly zero: its bad rate matches the book's, so it carries no information and could be merged with a neighbour without loss.

Once every variable is replaced by its weight of evidence, the regression is fitted on the transformed columns. This buys four things at once: the relationship is linear by construction, outliers are capped inside their bins, missing values have a coefficient, and every fitted coefficient should come out positive under the convention above, which turns sign checks into a free diagnostic. Variables are then selected by a mixture of information value, stepwise procedures, correlation screening — rules of thumb put the pairwise limit around 0.5 to 0.7 — and business judgement, aiming for a final model of roughly 8 to 15 characteristics.

## From probability to points

Nobody runs a lending business on log-odds. The fitted model is rescaled to an integer score using two conventions: a reference score at reference odds, and the number of points that doubles the odds.

$$Score = Offset + Factor \times \ln(odds), \qquad Factor = \frac{PDO}{\ln 2}$$

- $odds$ — good:bad odds at the account's fitted probability.
- $PDO$ — points to double the odds, conventionally 20.
- $Offset$ — chosen so a reference score corresponds to reference odds: $Offset = S_0 - Factor \times \ln(odds_0)$.

🧮 **WORKED — Scaling a model to points**

| Step | Calculation | Result |
|---|---|---|
| 1. Choose conventions | 700 points = 40:1 good:bad, PDO = 20 | — |
| 2. Factor | 20 ÷ ln 2 = 20 ÷ 0.693147 | 28.854 |
| 3. Offset | 700 − 28.854 × ln 40 = 700 − 28.854 × 3.68888 | 593.55 |
| 4. Score an account at 15:1 odds | 593.55 + 28.854 × ln 15 = 593.55 + 28.854 × 2.70805 | **672** |
| 5. Its bad rate | 1 ÷ (1 + 15) | 6.25% |
| 6. Verify the doubling | Score 720 → odds = exp((720 − 593.55) ÷ 28.854) = exp(4.3823) | **80:1 ✓** |

Points are then distributed across characteristics so each attribute contributes a whole number, which is what makes a scorecard readable: an applicant scores 34 points for enquiry count, 51 for bureau utilisation, and so on, summing to 672. The distribution formula spreads the intercept evenly across the $n$ characteristics.

$$Points_i = -\left(\beta_i \times WOE_i + \frac{\beta_0}{n}\right) \times Factor + \frac{Offset}{n}$$

Two points of hygiene about scale. The scorecard's internal score is not the bureau score, even when both run in the hundreds; the bureau score is one *input* to the scorecard, and treating the two as interchangeable produces a model that is largely a copy of the bureau's with added noise. And the reference odds are a choice, not a fact, so a score of 700 means nothing until the scaling convention behind it is stated.

## Reject inference

The training sample contains only accounts that were sanctioned, but the model will be applied to everyone who applies. If yesterday's cut-off declined the worst 40% of applicants, then the relationship between characteristics and default has been observed only on the surviving 60%, and it is being extrapolated into a region where it was never measured. This is *reject inference*: the family of techniques for assigning presumed outcomes to declined applications so they can enter development.

The common methods are parcelling — score the rejects with a known-good/known-bad model, then assign bad flags randomly in proportion to the expected bad rate at each score, usually inflated by a factor of two to four — augmentation, which reweights accepts so each stands in for the rejects that resemble it, and simple extrapolation of the bad-rate curve beyond the cut-off. All three share a defect.

🔴 **TRAP — "Reject inference fixes selection bias"**
The wrong belief is that reject inference recovers the missing information. It cannot: the outcomes of declined applicants were never observed, and no algorithm creates data. What reject inference does is make an *assumption* about the rejected region explicit, consistent and auditable, so the model's behaviour below the cut-off follows a stated rule rather than an accident of extrapolation. The genuine cure is different and expensive: deliberately sanction a small random sample of applicants who would otherwise be declined, and observe what happens. Those *swap-in test* accounts are the only unbiased evidence about the declined population, and portfolios that fund them are the ones whose cut-offs can be moved with confidence.

⚖️ **TRADE-OFF — Logistic regression versus gradient boosting**
A gradient-boosted tree ensemble will usually beat a well-built scorecard on the development sample, commonly by 2 to 5 Gini points, and often by less than that out of time. The costs are concrete: the model cannot be read as points, monotonicity must be imposed as an explicit constraint or the model will happily learn that risk falls and then rises with income for no reason, reasons for rejection must be reconstructed after the fact from attribution methods, and independent validation takes longer. In India the balance is tilted slightly further toward the machine-learning model on rich alternative data — device, transaction and Account Aggregator feeds — and slightly further away from it on thin-file applicants, where the uplift is smallest and the explanation burden is highest.

**You can now:**
- Bin a variable, compute its weight of evidence and information value, and judge whether it earns a place.
- Convert fitted log-odds into a points-based scorecard and verify the doubling property.
- State what reject inference can and cannot do, and name the only unbiased remedy.

---

# §7 · DISCRIMINATION VERSUS CALIBRATION

**A model does two separable jobs — putting accounts in the right order, and attaching the right number to each — and it can do either one perfectly while failing the other completely.**

*Discrimination* is rank ordering: given two accounts, does the model put the one that defaults below the one that does not? *Calibration* is level: of all the accounts the model assigns a 4% PD, do about 4% actually default? Discrimination is a property of the ranking and survives any monotonic transformation of the score. Calibration is a property of the mapping from score to probability and can be destroyed or repaired without touching the ranking at all.

The distinction matters because different consumers need different things. A sanction cut-off needs discrimination: it only has to know who is worse than whom. Pricing and provisioning need calibration, because they multiply the PD by real money. A model with a Gini of 0.5 and PDs that are uniformly half of reality will make good sanctioning decisions and catastrophically under-provision.

🔍 **WHY THIS IS TRUE — Recalibration is nearly free, redevelopment is not**
Because calibration concerns only the level, it can usually be fixed by shifting the intercept — a single additive constant in log-odds space, equivalently a parallel shift in points. A book whose central tendency has drifted from a 3% to a 4.5% bad rate needs its intercept moved by ln(0.045/0.955) − ln(0.03/0.97) = −3.052 − (−3.476) = 0.424 in log-odds, and the ranking is untouched. Discrimination cannot be repaired this way: if the model has stopped separating goods from bads, no transformation of its output restores the separation, because the information is simply not in the score. This asymmetry is why monitoring reports rank-order statistics and calibration statistics separately, and why a fall in Gini is a redevelopment trigger while a drift in observed default rate is usually a recalibration one.

📘 **DEFINE — Point-in-time versus through-the-cycle**
A *point-in-time* (PIT) PD estimates the probability of default over a stated horizon given everything known today, including where the economy currently stands; it rises in downturns and falls in booms. A *through-the-cycle* (TTC) PD estimates a long-run average for a grade of borrower, deliberately insensitive to the current state of the cycle; it moves only when the borrower's own quality changes. Neither is more correct — they answer different questions. The ECL framework requires PIT estimates, because it asks what losses are actually expected now, and the RBI reinforces this by requiring that risk parameters derived from historical observed default rates be adjusted for current conditions and forecasts. Capital in India needs neither, because risk weights are fixed by rule. In practice no real model is purely one or the other, and the honest description of most is "somewhere in between, and closer to PIT than the documentation claims".

⚖️ **TRADE-OFF — Procyclicality**
Choosing PIT gives provisions that are accurate and volatile; choosing TTC gives provisions that are stable and, in a downturn, too small. Every regime picks a point on this line and adds machinery to compensate: on the accounting side, multiple probability-weighted macroeconomic scenarios; on the capital side, a countercyclical capital buffer the RBI can switch on when credit growth runs hot. There is no setting that is simultaneously accurate, stable and simple.

**You can now:**
- Say which decisions require rank ordering only and which require correct levels.
- Compute an intercept shift that recalibrates a model to a new central tendency.
- Distinguish PIT from TTC and say which the Indian provisioning regime demands.

---

# §8 · MEASURING A MODEL

**Four numbers cover almost all model monitoring: Gini for ranking, KS for separation at a point, PSI for population drift, and observed-versus-expected default rate for calibration.**

The *receiver operating characteristic* (ROC) curve plots, for every possible score cut-off, the cumulative fraction of bads captured against the cumulative fraction of goods rejected. A useless model produces the diagonal; a perfect model produces the top-left corner. The area under that curve (AUC) is the probability that a randomly chosen bad scores worse than a randomly chosen good. Gini rescales it so useless is 0 and perfect is 1.

$$Gini = 2 \times AUC - 1$$

Typical ranges, as rules of thumb rather than standards: an application scorecard on thin data lands around 0.35 to 0.55; a behavioural scorecard with six months of own-account payment history lands around 0.60 to 0.80. The gap is the value of watching someone pay.

🧮 **WORKED — Gini from a five-band score distribution**

Bands are equal fifths of the population, worst-scoring first. Distribution of bads: 40%, 25%, 15%, 12%, 8%. Distribution of goods: 18%, 19%, 20%, 21%, 22%.

| Step | Cumulative goods (x) → cumulative bads (y) | Trapezoid area |
|---|---|---|
| 1 | 0.00 → 0.18, y 0.00 → 0.40 | 0.5 × (0.00+0.40) × 0.18 = 0.03600 |
| 2 | 0.18 → 0.37, y 0.40 → 0.65 | 0.5 × (0.40+0.65) × 0.19 = 0.09975 |
| 3 | 0.37 → 0.57, y 0.65 → 0.80 | 0.5 × (0.65+0.80) × 0.20 = 0.14500 |
| 4 | 0.57 → 0.78, y 0.80 → 0.92 | 0.5 × (0.80+0.92) × 0.21 = 0.18060 |
| 5 | 0.78 → 1.00, y 0.92 → 1.00 | 0.5 × (0.92+1.00) × 0.22 = 0.21120 |
| Sum | AUC | 0.67255 |
| Final | Gini = 2 × 0.67255 − 1 | **0.345** |

A Gini of 0.345 is a weak but usable application scorecard. The same table gives the Kolmogorov–Smirnov statistic almost free: KS is the largest vertical gap between the cumulative bad and cumulative good distributions, here at band 3 where bads are at 0.80 and goods at 0.57, giving KS = 0.23, usually quoted as 23. KS answers a narrower question than Gini — how good is the single best cut-off — which is why it survives in operational reporting despite Gini being the better summary.

$$KS = \max_s \left| F_{bad}(s) - F_{good}(s) \right|$$

- $F_{bad}(s)$ — fraction of bads scoring at or below $s$.
- $F_{good}(s)$ — fraction of goods scoring at or below $s$.

The Population Stability Index answers a different question entirely: not "is the model still right" but "is the model still being asked about the same people". It compares the score distribution of a recent cohort with the distribution at development.

$$PSI = \sum_i (A_i - E_i) \times \ln\left(\frac{A_i}{E_i}\right)$$

- $A_i$ — actual proportion of the recent population in band $i$.
- $E_i$ — expected proportion, from the development sample.
- Both must be proportions summing to 1, and no band may be empty, which is why bands are usually deciles of the development distribution.

🧮 **WORKED — Population Stability Index**

| Band | Expected → Actual | Contribution |
|---|---|---|
| 1 | 0.20 → 0.12 | (−0.08) × ln(0.60) = (−0.08)(−0.51083) = 0.040866 |
| 2 | 0.20 → 0.18 | (−0.02) × ln(0.90) = (−0.02)(−0.10536) = 0.002107 |
| 3 | 0.20 → 0.22 | (0.02) × ln(1.10) = (0.02)(0.09531) = 0.001906 |
| 4 | 0.20 → 0.24 | (0.04) × ln(1.20) = (0.04)(0.18232) = 0.007293 |
| 5 | 0.20 → 0.24 | (0.04) × ln(1.20) = 0.007293 |
| **Total** | | **PSI = 0.0595** |

Below the 0.10 threshold, so the population has shifted but not alarmingly — and note the shift is favourable, with fewer applicants in the worst band. PSI is unsigned, so it flags movement without saying whether the movement is good news; the decomposition by band, not the headline, is what you read. The same arithmetic applied to a single input variable rather than the score is the Characteristic Stability Index, and it is how you find out *which* variable moved.

✅ **CHECK — The monitoring pack that actually catches failure**
Monthly: PSI on the score, characteristic stability on every input, approval rate, and score distribution by sourcing channel — direct, digital, and direct selling agent, which behave very differently. Quarterly: Gini on the most recent mature vintage, observed versus expected default rate by score band, and override rate. Pass condition for the calibration test: observed default rate falls inside a binomial confidence interval around expected in at least 80% of score bands, with no systematic pattern of misses in one direction. A model that fails in one direction across every band is miscalibrated and needs an intercept shift; a model that fails randomly across bands is under-powered rather than biased.

🔴 **TRAP — "Gini fell, so the model is broken"**
The wrong belief is that a falling Gini always means model degradation. Gini is a property of the model *and* the population it is measured on: tighten the cut-off and Gini on the sanctioned book falls mechanically, because you have removed the worst accounts, which were the easiest to rank. This is *range restriction*, and it means a sanctioned-book Gini is not comparable across periods with different approval rates. The correction is to measure discrimination on the through-the-door population wherever the data exists, and to interpret sanctioned-book Gini only alongside the approval rate that produced it.

**You can now:**
- Compute Gini, KS and PSI by hand from a banded table.
- Say which statistic answers which question, and which failure each one detects.
- Explain why a sanctioned-book Gini falls when the cut-off is tightened.

---

# §9 · LOSS GIVEN DEFAULT AND EXPOSURE AT DEFAULT

**PD gets the attention and LGD gets the money: a housing book's expected loss is driven far more by how long enforcement takes and what the property fetches than by how many borrowers stop paying.**

Loss given default is one minus the recovery rate, where recovery is measured properly: all cash received after default, net of the costs of collecting it, discounted back to the default date. Each qualification removes several percentage points of illusion. Cash arrives over years, so discounting matters; legal fees, valuation, auction costs and collection agency commissions are real; and post-default interest that is charged but never paid is not recovery.

$$LGD = 1 - \frac{\sum_t \frac{R_t - C_t}{(1+d)^t}}{EAD}$$

- $R_t$ — cash recovered in period $t$ after default.
- $C_t$ — direct and allocated indirect costs of recovery in period $t$.
- $d$ — discount rate; under the ECL framework the effective interest rate on the exposure.
- $EAD$ — exposure at the moment of default, the denominator.

Two structural features make retail LGD awkward. Its distribution is *bimodal*: most defaults resolve either near-fully — a cure, or a secured sale that clears the debt — or near-totally, an unsecured write-off with a token recovery. An average LGD of 30% may describe almost no individual account. And LGD depends on the same conditions as PD and in the same direction: property prices fall, so defaults rise and recoveries shrink together.

## How recovery actually works in India

The route depends entirely on the security.

*Gold loans* recover fastest and most completely, because the collateral is already in the lender's vault and can be auctioned under a prescribed process. This is why LTV ceilings on gold are the most generous in Indian retail — 85% up to ₹2.5 lakh, 80% for ₹2.5 to ₹5 lakh, 75% above ₹5 lakh, from 1 April 2026 — and why gold gets its own provisioning category with a Stage 2 floor of 1.50% rather than the 5% that most products carry.

*Vehicle loans* recover through repossession and resale, typically within months, at a resale value that has already depreciated sharply from the purchase price.

*Housing loans* recover through enforcement under the Securitisation and Reconstruction of Financial Assets and Enforcement of Security Interest Act, 2002 — universally called SARFAESI — which lets a secured lender enforce without going to court: a 60-day demand notice under section 13(2), then possession and sale. It applies only to secured debts of ₹1 lakh or more and not to agricultural land. Where SARFAESI does not apply, or is contested, recovery moves to a Debts Recovery Tribunal for claims of ₹20 lakh and above, or to the ordinary civil courts below that, and the timeline stretches from months into years.

*Unsecured loans and cards* recover through persuasion, settlement, and finally sale — either to an asset reconstruction company in exchange for security receipts, or as a written-off pool to a debt purchaser. Prices for aged unsecured paper are a rule of thumb rather than a rate, and move sharply with the funding conditions of the buyers.

📘 **DEFINE — Regulatory backstop LGD**
The severity a lender must assume when it cannot reliably estimate its own. Under the 2026 ECL Directions the backstop is 65% on the secured portion and 70% on the unsecured portion — deliberately punitive, since a well-secured retail book realistically loses far less than 65% of the secured part. A concession applies to a narrow list of high-quality collateral: cash, gold in bullion or jewellery form, central and state government securities, LIC policies, Kisan Vikas Patra and National Savings Certificates, where the backstop drops to 30%. The design intent is transparent — a bank that invests in recovery data gets to use its own numbers, and a bank that does not pays for the ignorance. Note also what does *not* count as security for this purpose in the related capital rules: land, buildings, plant, machinery and current assets are excluded from the eligible-collateral list used to define the secured portion of an NPA for risk weighting, so an exposure can be commercially secured and regulatorily unsecured at the same time.

Exposure at default asks how much will be owed when default happens, which differs from today's balance for two reasons. On amortising loans the balance falls, so EAD is read off the amortisation schedule. On revolving products — credit cards, overdrafts, cash credit — the balance *rises*, because a borrower heading into distress draws on remaining headroom. This is captured by the credit conversion factor.

$$EAD = B + CCF \times (L - B)$$

- $B$ — current drawn balance.
- $L$ — the committed limit.
- $L - B$ — undrawn headroom.
- $CCF$ — credit conversion factor, the fraction of headroom expected to be drawn before default.

The regulatory CCFs changed materially with the 2026 capital Directions, and the change matters most for cards. Commitments that the lender can cancel unconditionally at any time — which is how most credit card limits are documented — previously attracted a zero conversion factor and therefore no capital at all on the unused line. From 1 April 2027 they attract 5%, rising to 10% after three years. Other commitments attract 30% for the first three years and 40% thereafter where the original maturity is up to a year, and 40% throughout where it is longer. A lender's own estimate may be higher, and should be: observed drawdown in the twelve months before default on a distressed card portfolio typically far exceeds 10% of headroom.

⚖️ **TRADE-OFF — Cutting limits to cut exposure**
Reducing unused limits reduces EAD immediately and mechanically, which reduces expected loss, provisions and now capital. It also reduces revenue from customers who would have borrowed profitably, damages the relationship with good customers who experience the cut as an insult, and, in aggregate, removes household liquidity at exactly the moment when limit-cutting programmes tend to run, which is during stress. The usual compromise is targeted: cut headroom only where behavioural score has deteriorated and utilisation is already high, capturing most of the exposure benefit at a fraction of the relationship cost.

✅ **CHECK — Is the LGD estimate honest?**
Take a cohort of defaults old enough to be fully resolved and compare the LGD predicted at default with the LGD ultimately realised, discounted at the same rate. Pass condition: the mean realised LGD sits within the model's stated confidence range, and — separately — the *distribution* is reproduced, not just the mean. A model that gets the average right by predicting 30% for everything, when reality is 60% of accounts at 5% and 40% at 67%, will price and provision individual segments wrongly in both directions.

**You can now:**
- Compute LGD with costs and discounting and explain why each adjustment lowers the recovery.
- Name the four Indian recovery routes and rank them by speed.
- Compute EAD from a drawn balance, a limit and a credit conversion factor, and state the new factors for cancellable commitments.

---

# §10 · PORTFOLIO MECHANICS

**A retail book is a flow system, and the fastest reliable read on its health is not the stock of bad loans but the rate at which accounts move between SMA buckets.**

Every month, each account sits in a bucket — standard, SMA-0, SMA-1, SMA-2, NPA — and moves to another. The matrix of those movements is the *transition matrix*, and the probabilities of falling one bucket further behind are the *roll rates*. Roll rates are the earliest honest signal in the system: they respond within a month or two of a change in underwriting or the economy, while the stock of NPAs takes at least three months to reflect the same change, and write-offs take longer still.

🧮 **WORKED — Forecasting write-off from roll rates**

Roll rates: standard→SMA-0 = 8%, SMA-0→SMA-1 = 50%, SMA-1→SMA-2 = 60%, SMA-2→NPA = 75%, NPA→write-off = 95%. All figures in ₹ crore.

| Starting bucket | Balance × chained roll rates | Expected write-off |
|---|---|---|
| Standard | 1,000 × 0.08 × 0.50 × 0.60 × 0.75 × 0.95 = 1,000 × 0.01710 | 17.10 |
| SMA-0 | 80 × 0.50 × 0.60 × 0.75 × 0.95 = 80 × 0.21375 | 17.10 |
| SMA-1 | 40 × 0.60 × 0.75 × 0.95 = 40 × 0.42750 | 17.10 |
| SMA-2 | 20 × 0.75 × 0.95 = 20 × 0.71250 | 14.25 |
| NPA | 12 × 0.95 | 11.40 |
| **Total** | | **₹76.95 crore** |

Read the middle column rather than the total. The ₹12 crore sitting in NPA contributes almost as much loss as the entire ₹1,000 crore of standard balances, because it is 95% certain to be lost while the standard book is 1.71% likely to get there. This is the arithmetic behind the whole design of collections: effort spent stopping an account rolling from SMA-0 to SMA-1 is worth roughly four times the same effort at SMA-2, because it removes the account from the chain earlier and because far more accounts are available to save.

🔍 **WHY THIS IS TRUE — Why gross NPA ratios lie in a growing book**
The headline gross NPA ratio divides today's non-performing balance by today's total advances. In a book growing at 25% a year, the denominator is fresh and the numerator is not: the accounts capable of being 90 days overdue were disbursed at least three months ago, when the book was smaller. The ratio therefore falls purely because of growth, and keeps falling until growth stops — at which point it jumps, and the jump gets blamed on the economy. Two corrections exist. *Lagged* delinquency divides today's bad balance by the balance as it stood some months ago, aligning numerator and denominator. *Vintage* analysis avoids the problem entirely by never mixing cohorts. A book whose gross NPA ratio is flat while its vintage curves are deteriorating is heading for trouble on a delay. The distortion is amplified in India by *technical write-offs*, which remove balances from the numerator without any cash being recovered, so gross NPA can fall for two independent cosmetic reasons at once.

📘 **DEFINE — Flow rate, cure rate and provision coverage**
The *flow rate* is the proportion of a bucket moving to the next-worse bucket next month; it is the same object as a roll rate, read from the perspective of accounts leaving rather than arriving. The *cure rate* is the proportion moving back toward standard, which in India means clearing the entire arrears across all facilities of the borrower. The two are not complements, because accounts can also stay put, close, or be written off. The *provision coverage ratio* is the stock of provisions divided by the stock of gross NPAs, and it is the single number that says how much of the recognised bad book has already been paid for. Cure rates are the most volatile item in the pack, since they respond to collections staffing, to seasonal payment patterns around harvests and festivals, and to any change in restructuring policy — which means an unexplained rise in cure rate is more often an operational change than an improvement in customer health.

Three portfolio effects distort almost every headline number, and naming them is most of the work of explaining a variance. *Seasoning* is the vintage curve of §5: a young book looks good. *Mix* is composition drift — if the share of unsecured personal loans or of digitally sourced business rises, the portfolio bad rate rises even though no segment's rate changed. *Attrition* is selective exit: good borrowers refinance away when rates fall or when a competitor offers a balance transfer, leaving a worse residual population, so a book can deteriorate without a single account deteriorating.

**You can now:**
- Chain roll rates into a write-off forecast and identify which bucket carries the loss.
- Explain why gross NPA ratios flatter growing books, and name two corrections plus the write-off distortion.
- Decompose a rise in portfolio bad rate into seasoning, mix and attrition before blaming credit quality.

---

# §11 · PROVISIONING: FROM INCURRED LOSS TO EXPECTED CREDIT LOSS

**Indian provisioning is mid-migration: until 31 March 2027 a bank provides against losses that have already been signalled by ageing, and from 1 April 2027 it must provide against losses it expects, with a schedule of regulatory floors underneath every modelled number.**

The old regime, universally called IRACP after its three components — income recognition, asset classification and provisioning — is mechanical and backward-looking. An account becomes NPA at 90 days, ages through sub-standard, doubtful and loss, and attracts a provision rate set by that ageing and by whether the exposure is secured. Standard assets carry a small flat provision. Income on an NPA stops accruing and is recognised only on receipt. The regime's virtue is that it cannot be gamed by modelling; its defect is the one that showed up worldwide after 2008, which is that nothing is provided until deterioration has already happened.

The replacement is the Reserve Bank of India (Commercial Banks – Asset Classification, Provisioning and Income Recognition) Directions, 2026, notified on 27 April 2026 and effective from 1 April 2027. It applies to commercial banks other than small finance banks, payments banks and local area banks. Non-banking financial companies reached the same destination earlier by a different road, applying Ind AS 109 — the Indian version of the international accounting standard — with an RBI overlay requiring them to hold the higher of the accounting number and the IRACP number.

📘 **DEFINE — The three stages**
Every in-scope instrument sits in one of three stages, determined by how its credit risk has moved *since initial recognition*. *Stage 1* is everything that has not suffered a significant increase in credit risk, and carries a loss allowance equal to expected losses from defaults occurring in the next twelve months. *Stage 2* has suffered such an increase but is not credit-impaired, and carries expected losses over the instrument's remaining lifetime. *Stage 3* is credit-impaired, which in India means it meets the NPA definition of §4, and carries lifetime losses with interest recognised only on receipt. Two Indian refinements matter. Stage 3 is applied at *borrower* level — one impaired facility drags every other facility of that borrower into Stage 3 — while Stage 2 is applied at *facility* level. And the framework does not replace NPA classification; the two run side by side, with "default" in the ECL sense defined as NPA status, so a bank reports both a stage and an asset classification for the same account.

$$ECL = \sum_{t=1}^{T} PD_t^{marg} \times LGD_t \times EAD_t \times \frac{1}{(1+EIR)^t}$$

- $PD_t^{marg}$ — marginal probability of defaulting in period $t$, having survived to the start of it.
- $LGD_t, EAD_t$ — loss severity and exposure applicable to a default in period $t$.
- $EIR$ — the effective interest rate determined at initial recognition, the discount rate the Directions prescribe.
- $T$ — 1 for Stage 1, the remaining life for Stages 2 and 3.

Marginal PDs come from a survival construction. If $h_t$ is the conditional probability of defaulting in period $t$ given survival to its start, then survival is the running product $S_t = \prod_{k \le t}(1 - h_k)$ and the marginal default probability is $PD_t^{marg} = S_{t-1} \times h_t$.

## Where SICR comes from

The trigger from Stage 1 to Stage 2 is a *significant increase in credit risk* since initial recognition — a change in default risk over the remaining life, not an absolute level of risk. Banks implement it with documented quantitative rules, which may be rating downgrades by a stated number of notches, a defined increase in loan pricing, or a defined deterioration in the macroeconomic outlook, and the Directions require that whichever parameter is chosen be defined precisely and applied consistently. A rebuttable presumption of SICR arises at 30 days past due; for revolving facilities the presumption arises when the outstanding stays above the sanctioned limit or drawing power continuously for up to 60 days. Rebuttal is permitted only with reasonable and supportable information, must be documented and board-approved, and may not be applied mechanically.

🧮 **WORKED — Where the model binds and where the floor binds**

Twelve-month ECL, before discounting, against the Stage 1 prudential floor.

| Product and parameters | Modelled 12-month ECL | Floor and outcome |
|---|---|---|
| Unsecured personal loan, EAD ₹3,00,000, PD 2.0%, LGD 70% | 0.020 × 0.70 × 3,00,000 = **₹4,200** = 1.40% | Floor 1.00% = ₹3,000. **Model binds** |
| Vehicle loan (secured retail), EAD ₹6,00,000, PD 1.5%, LGD 25% | 0.015 × 0.25 × 6,00,000 = **₹2,250** = 0.375% | Floor 0.40% = ₹2,400. **Floor binds** |
| Individual housing loan, EAD ₹40,00,000, PD 0.8%, LGD 15% | 0.008 × 0.15 × 40,00,000 = **₹4,800** = 0.12% | Floor 0.25% = ₹10,000. **Floor binds, at 2.08× the model** |

Discounting only sharpens this. At a 16% effective interest rate with default assumed at year end, the unsecured figure falls from 1.40% to 1.40 × 0.862069 = 1.21% of exposure — still above its 1% floor — while both secured cases fall further below theirs. Any case where the floor binds on undiscounted numbers binds a fortiori once discounting is applied.

🧮 **WORKED — Twelve-month versus lifetime ECL on the same loan after SICR**

The ₹3,00,000 personal loan above deteriorates and migrates to Stage 2. Revised conditional default rates 4%, 6%, 8%. LGD 70%. Expected exposure ₹3,00,000 / ₹2,10,000 / ₹1,05,000. Effective interest rate 16%.

| Year | Marginal PD and loss | Discounted ECL |
|---|---|---|
| 1 | 0.0400; 0.0400 × 0.70 × 3,00,000 = ₹8,400; DF = 1/1.16 = 0.862069 | **₹7,241** |
| 2 | S₁ = 0.96; marginal = 0.96 × 0.06 = 0.0576; 0.0576 × 0.70 × 2,10,000 = ₹8,467; DF = 0.743163 | ₹6,292 |
| 3 | S₂ = 0.96 × 0.94 = 0.9024; marginal = 0.9024 × 0.08 = 0.072192; × 0.70 × 1,05,000 = ₹5,306; DF = 0.640658 | ₹3,399 |
| Twelve-month ECL | Year 1 only | **₹7,241** |
| Lifetime ECL | Sum of all three | **₹16,932** |
| Stage 2 floor | 5% × 3,00,000 | ₹15,000 — model binds, narrowly |
| Check | Marginals sum to 0.0400 + 0.0576 + 0.072192 = 0.169792; and 1 − 0.96 × 0.94 × 0.92 = 0.169792 | **✓** |

🔴 **TRAP — "Stage 2 is a warning; the money is all in Stage 3"**
The wrong belief is that stage allocation is a soft classification and only impairment costs real money. On this loan the allowance more than doubles on migration, and on a longer-dated product the multiple runs to five or ten times, for an account whose underlying risk may have moved only modestly. The consequence is that a small deterioration in a macroeconomic forecast can push a large block of accounts across the SICR boundary at once and produce a charge far larger than the change in expected defaults justifies. This *cliff effect* is intended rather than accidental, and it means reported provision movements must always be decomposed into stage transfers, model updates, scenario updates and volume changes before any of them is interpreted.

## The prudential floors

The distinctively Indian feature of the framework is that every modelled number sits on a regulatory backstop. The final allowance for a product category is the higher of the model's output and the prescribed floor, applied at portfolio level for Stages 1 and 2 and at individual account level for Stage 3.

| Category | Stage 1 floor | Stage 2 floor |
|---|---|---|
| Unsecured retail | 1.00% | 5% |
| Secured retail, corporate, medium enterprises, financial institutions | 0.40% | 5% |
| Small and micro enterprises, farm credit | 0.25% | 5% |
| Individual housing loans | 0.25% | 1.50% |
| Gold loans | 0.40% | 1.50% |
| Loans against term deposits, LIC policies, Kisan Vikas Patra | 0.40% | 0.40% |
| Any category not otherwise specified | 0.40% | 5% |

Stage 3 floors then escalate with time in Stage 3. For most categories the schedule runs 25% in the first year, 40% in the second, 55% in the third, 75% in the fourth and 100% thereafter, with the unsecured portion escalating faster — 40% in year one and 100% from year two. Unsecured retail has its own harsher schedule: 25% in the first year and 100% after it. Individual housing loans get the gentlest: 10% in year one rising to 100% after four years, again with the unsecured portion escalating faster. A 12-month PD used in ECL is separately floored at 0.03%.

Two further rules bite in retail. Product categories may not be mixed to soften a floor — a gold loan must be provided for as a gold loan and cannot be folded into secured retail. And where a portfolio is covered by a default loss guarantee from a lending service provider, the guarantee may be recognised across all stages only if it is integral to the contractual terms, and the allowance must be recomputed each time the guarantee is invoked and its cover shrinks.

🔍 **WHY THIS IS TRUE — Why the floors are the real model on good books**
On a high-quality secured retail book the modelled twelve-month ECL is often a third or a quarter of the applicable floor, as the housing case above shows. The consequence is that improving the model changes nothing about the reported provision for that portfolio — the floor is what is booked, and better estimation only widens the gap between what the bank believes and what it reports. Model quality therefore pays where the model is above the floor: unsecured retail, Stage 2 populations, and Stage 3, where the floor applies account by account and where the difference between a 35% and a 65% severity assumption is real money. This is the opposite of the intuition that sophistication matters most on the biggest and safest book.

The transition itself is an event in its own right. On 1 April 2027 banks fair-value the entire loan portfolio, with the difference taken to opening retained earnings rather than through profit and loss. The excess of day-one ECL over the IRACP provisions held on 31 March 2027 is the *transitional adjustment amount*, and a bank may add back a declining fraction of it to core equity capital — four-fifths in 2027-28, three-fifths, two-fifths, and one-fifth in 2030-31 — so the capital effect is spread across four years. Loans outstanding at transition must move onto the effective interest rate method by 31 March 2030.

**You can now:**
- Compute twelve-month and lifetime ECL with survival-based marginal PDs and discounting.
- Determine, for a given product and parameters, whether the model or the prudential floor is binding.
- State the SICR backstops for term and revolving facilities, and explain the borrower-level Stage 3 rule.

---

# §12 · CAPITAL: THE RBI STANDARDISED APPROACH

**Indian retail capital is a lookup, not a model: the RBI has implemented only the Standardised Approach, so the exposure's product, security, loan-to-value band and — for cards — the customer's repayment behaviour determine the risk weight, and the lender's own PD estimates never enter.**

The arithmetic is simple. Every exposure is assigned a risk weight from a supervisory table. Risk-weighted assets are the exposure, net of specific provisions, multiplied by that weight. Capital is then the required ratio applied to risk-weighted assets: a minimum CRAR of 9%, or 11.5% once the 2.5% capital conservation buffer is included, with common equity tier 1 of at least 5.5% and 8% including the buffer.

$$RWA = Exposure \times RW, \qquad Capital = RWA \times CRAR$$

- $RW$ — the supervisory risk weight for the exposure class.
- $Exposure$ — on-balance-sheet amount net of specific provisions, plus off-balance-sheet amounts converted by the applicable credit conversion factor.
- $CRAR$ — the capital ratio the bank targets; 9% is the floor and 11.5% is the practical requirement.

The retail weights that matter are few. A qualifying regulatory retail exposure attracts 75%. A personal loan or a credit card revolver attracts 125%. A credit card *transactor* — an obligor who has repaid the balance in full at every scheduled due date, including the three-day grace period, for the previous twelve months — falls into regulatory retail at 75% instead. Individual housing loans attract 20%, 25%, 30% or 40% across LTV bands of up to 50%, 50 to 60%, 60 to 80% and 80 to 90%, for a borrower's first two housing loans, with an extra 5 percentage points where the outstanding is ₹3 crore or above; the third housing loan onward attracts 30%, 35%, 45% and 60% across the same bands. Microfinance loans in the nature of consumer credit that do not qualify as regulatory retail attract 100%. Personal loans secured by gold attract 125% on the exposure value after collateral mitigation.

🧮 **WORKED — Capital on four retail exposures**

All at a 11.5% target ratio, including the capital conservation buffer.

| Exposure | Risk-weighted assets | Capital |
|---|---|---|
| First housing loan, outstanding ₹40,00,000, property valued ₹55,00,000 → LTV 72.7% → RW 30% | 40,00,000 × 0.30 = ₹12,00,000 | **₹1,38,000** |
| Credit card revolver, drawn ₹1,00,000, limit ₹3,00,000, CCF 10% on ₹2,00,000 undrawn → EAD ₹1,20,000, RW 125% | 1,20,000 × 1.25 = ₹1,50,000 | **₹17,250** |
| Same card, customer classified as transactor → RW 75% | 1,20,000 × 0.75 = ₹90,000 | **₹10,350** |
| Personal loan ₹5,00,000, RW 125% | 5,00,000 × 1.25 = ₹6,25,000 | **₹71,875** |

Per ₹100 of exposure, the housing loan consumes ₹3.45 of capital, the card revolver and the personal loan ₹14.38, and the same card in the hands of a transactor ₹8.63. The last comparison is the sharpest lever in the table: nothing about the exposure changed except twelve months of full repayments, and the capital fell by 40%.

The LTV bands create a second lever, and a cliff. On a ₹40,00,000 housing loan, the difference between an LTV of 79% and an LTV of 81% is the difference between a 30% and a 40% risk weight, which is the difference between ₹1,38,000 and ₹1,84,000 of capital — a third more capital for a two-point move. Since LTV is measured against the value at origination, adjusted downward if the property falls and only upward after at least five years and a fresh valuation, the band an exposure lands in at sanction is largely the band it stays in.

🔍 **WHY THIS IS TRUE — Why India's choice removes a whole feedback loop**
In jurisdictions that permit the Internal Ratings Based approach, a bank's own PD and LGD estimates feed a supervisory formula and a better model produces a lower capital charge on the same exposure. That creates a direct financial return to modelling, and with it a supervisory apparatus of use tests, data-history minima and downturn LGD requirements to stop the return being manufactured. The RBI has explicitly declined that route and implemented the Standardised Approach for all banks under its jurisdiction. The consequence is structural: in India, capital is a policy instrument set by the regulator on product categories, and modelling skill is rewarded only through selection, pricing and provisioning. It also means the familiar apparatus of asset correlations, 99.9th-percentile loss and downturn LGD, which dominates capital discussion elsewhere, is background theory here rather than working arithmetic.

Defaulted retail exposures move to their own treatment. The unsecured portion of an NPA, net of specific provisions and partial write-offs, attracts 150% where specific provisions are under 20% of the outstanding, 100% where they are at least 20%, and 50% where they are at least 50%. Qualifying residential real estate exposures that turn non-performing attract a flat 100% net of provisions. Provisioning therefore buys capital relief on a defaulted asset — the same rupee held as a provision reduces both the exposure and the weight applied to it.

⚖️ **TRADE-OFF — Chasing the 75% bucket**
Structuring retail lending to qualify for the regulatory retail portfolio saves 50 percentage points of risk weight against the 125% that unsecured consumer credit attracts. The qualifying conditions are real constraints, not paperwork: aggregate exposure to one counterparty at or below ₹10 crore, no counterparty above 0.2% of the whole portfolio, and the product must not be a personal loan or a non-transactor card. A lender that grows its book by writing larger unsecured tickets pushes exposures out of the bucket precisely as it grows, and a lender that shrinks its retail portfolio can breach the 0.2% granularity test without originating anything at all, because the denominator moved.

**You can now:**
- Compute risk-weighted assets and capital for a housing loan, a card and a personal loan from the RBI tables.
- Explain the transactor/revolver distinction and quantify what it is worth.
- State why Indian banks earn no capital benefit from better PD models, and what they do earn it from.

---

# §13 · MACROECONOMICS AND STRESS TESTING

**Indian retail credit models are conditional on an economy, and the ECL framework makes that conditionality mandatory: forward-looking information and multiple probability-weighted scenarios are requirements, not refinements.**

A handful of macroeconomic variables carry most of the explanatory power. Real income growth and employment conditions drive ability to pay across every product. The policy repo rate feeds through to the external benchmark to which floating-rate retail loans are linked, so a rate cycle changes instalments directly on housing and other floating-rate books. Residential property prices drive housing LGD through the equity cushion and housing PD indirectly, since a borrower in negative equity cannot sell their way out. Inflation compresses household surplus, and for the agricultural and rural book the monsoon and crop prices matter more than any of the above.

The linkage is built with *satellite models*: regressions of an observed portfolio quantity — the default rate, the roll rate, the recovery rate — on lagged macroeconomic variables. Lags are long. Deterioration in employment typically leads unsecured defaults by two to four quarters, and property prices lead housing losses by longer still, because enforcement takes time.

Because losses are convex in the economy — a two-point deterioration costs more than twice what a one-point deterioration costs — a single central forecast systematically understates expected loss. The Directions therefore require multiple scenarios, each representing a relationship between the ECL components and the relevant macroeconomic variables, with probability weights determined by the bank using historical experience and expert judgement under its governance framework, and reviewed at a documented frequency. The weighting is applied to the resulting ECLs, never to the inputs.

📘 **DEFINE — Stress test**
A projection of a portfolio's losses, revenues and capital under a prescribed adverse macroeconomic path, run to answer whether the institution stays above its capital minimum throughout. In India the practice has two layers. The RBI runs system-wide macro stress tests and publishes the results, projecting gross NPA ratios and capital ratios for the banking system under a baseline and two adverse scenarios. Individual banks run their own under the Internal Capital Adequacy Assessment Process, the Pillar 2 requirement to hold capital against risks not captured by the Pillar 1 risk weights. The output is not a forecast — the scenario is chosen to be severe and improbable — but a conditional statement of the form "if this happened, capital would fall to here". Because Indian retail capital comes from fixed risk weights, the stress bites almost entirely through provisions and through the migration of exposures into the 125% and NPA buckets, rather than through any recalculation of the weights themselves.

⚖️ **TRADE-OFF — Model sensitivity versus model stability**
A model tightly fitted to macroeconomic history responds strongly to the scenario, which supervisors like, and also responds strongly to noise in the forecast, which produces provision volatility that has no informational content. A loosely fitted model responds smoothly and can be accused of ignoring the stress. There is no resolution inside the model; the honest treatment is to report the sensitivity explicitly — how many rupees of provision per point of the driver — so the choice is visible rather than buried.

✅ **CHECK — Does the macro link survive out of sample?**
Fit the satellite model on data ending before a known shock, then project through it and compare with what happened. Pass condition: the projection captures the direction and rough magnitude of the peak, within a factor of about two. Indian retail satellite models face a specific difficulty here, and it is worth stating plainly: the record is thin. The usable stress episodes are few, and the largest of them is unusable at face value, because the 2020 moratorium and the accompanying standstill on asset classification suspended the very ageing process that defines default. Days-past-due series from that period record policy, not borrower behaviour. Any model calibrated across it without explicit adjustment will misstate both the level and the timing of stress, and the correct response is to document the treatment rather than to let the artefact pass as data.

**You can now:**
- Name the macroeconomic drivers that matter in Indian retail and which parameter each moves.
- Explain why scenarios are probability-weighted on outputs and never on inputs.
- State why a moratorium period corrupts days-past-due data and what that does to a satellite model.

---

# §14 · PRICING, LIMITS AND PROFIT

**A lending decision is not a risk decision, it is a profit decision in which risk is one of four terms, and cut-offs set on risk alone destroy value at both ends.**

The account-level economics are simple to write down. Revenue is the spread earned on the balance plus fees. Costs are the cost of funds, the operating cost of acquiring and servicing, and the expected loss. What remains must be earned on the capital the account consumes.

$$RAROC = \frac{(Revenue - Opex - EL) \times (1 - \tau)}{Capital}$$

- $RAROC$ — risk-adjusted return on capital, the return the account earns on the capital it forces the lender to hold.
- $\tau$ — the tax rate.
- $Capital$ — the regulatory capital allocated, from §12.
- The comparison point is the lender's hurdle rate, which is its cost of equity plus a margin; accounts below it consume shareholder value even when they look profitable in accounting terms.

🧮 **WORKED — RAROC on a personal loan, and what it takes to clear the hurdle**

Loan ₹5,00,000 for one year. Rate 15%. Cost of funds 7%. Acquisition and servicing 2.5% of balance. PD 4%, LGD 70%. Tax 25%. Risk weight 125%, capital held at 11.5% of risk-weighted assets.

| Step | Calculation | Result |
|---|---|---|
| 1. Net interest income | (0.15 − 0.07) × 5,00,000 | ₹40,000 |
| 2. Operating cost | 0.025 × 5,00,000 | ₹12,500 |
| 3. Expected loss | 0.04 × 0.70 × 5,00,000 | ₹14,000 |
| 4. Pre-tax profit | 40,000 − 12,500 − 14,000 | ₹13,500 |
| 5. Post-tax profit | 13,500 × 0.75 | ₹10,125 |
| 6. Capital allocated | 0.115 × (1.25 × 5,00,000) = 0.115 × 6,25,000 | ₹71,875 |
| 7. RAROC | 10,125 ÷ 71,875 | **14.1%** |
| 8. Same loan priced at 17% | NII ₹50,000 → pre-tax ₹23,500 → post-tax ₹17,625 | **24.5%** |

Step 7 is the point. At 15%, against a cost of equity that most Indian lenders put in the mid-teens, this loan roughly breaks even in economic terms and creates no value. The 125% risk weight is doing much of the damage: the same borrower economics on a 75% weight would allocate ₹43,125 of capital and produce a RAROC of 23.5%. Unsecured consumer credit in India is priced where it is priced substantially because of that weight.

🔍 **WHY THIS IS TRUE — Price rises change who accepts, not just what you earn**
Raising the rate on a risk segment does two things at once, and the second usually dominates. It increases the margin on everyone who still takes the loan, and it changes *which* applicants still take it. Borrowers with good alternatives — disproportionately the better credits — go elsewhere, while borrowers with no alternatives accept. So the observed default rate of the segment rises after a price increase even though no individual borrower changed, and the profit gain is smaller than the arithmetic predicted, sometimes negative. This is *adverse selection*, and its portfolio-level cousin is the winner's curse: across a competitive market a lender systematically wins the business its model under-prices relative to everyone else's, so a lender with a weaker model does not merely earn less — it acquires a book selected against it. Balance-transfer offers on cards and housing loans are this mechanism operating in the open.

The same logic governs cut-offs. Moving a cut-off down accepts a *swap set* — applicants previously declined, now sanctioned — whose expected profit must be evaluated as a group. The right question is never "what is the bad rate of the marginal segment" but "does the marginal segment clear the hurdle rate after loss, cost of capital and price elasticity". Some very high-risk segments clear it at high prices; some low-risk segments fail it because they are cheap to price and shop aggressively.

⚖️ **TRADE-OFF — Risk-based pricing under Indian disclosure rules**
Pricing each applicant to their own risk maximises portfolio profit and expands access, since borrowers who would be declined under a single price can be served at a higher one. It also concentrates the highest prices on the least resilient households and creates a reinforcing loop when the higher price itself raises the default rate. India permits risk-based pricing and constrains it through transparency rather than rate caps for most products: floating-rate retail loans must be linked to an external benchmark so that pass-through is mechanical rather than discretionary; every retail borrower must receive a Key Facts Statement setting out the all-in annual percentage rate including fees; penal charges must be levied as charges rather than as penal interest and may not be capitalised into the principal; and floating-rate loans to individuals for non-business purposes carry no foreclosure charges. Microfinance is the exception with hard structural limits — a household income ceiling of ₹3 lakh and a cap on total repayment obligations at 50% of monthly household income.

**You can now:**
- Compute RAROC from a rate, a cost base, expected loss and an allocated capital number.
- Quantify how much of an unsecured loan's price is driven by its risk weight.
- Explain adverse selection and the winner's curse as consequences of pricing in a competitive market.

---

# §15 · COLLECTIONS, RESTRUCTURING AND RECOVERY

**Once an account is delinquent the modelling problem changes from "will this go wrong" to "which intervention on which account recovers the most cash per hour of effort".**

Collections is a resource allocation problem with a hard constraint: there are more delinquent accounts than agent-hours. Ranking is done with a *collections score*, typically predicting the probability of self-cure without contact, or the expected recovery under each treatment. The counterintuitive use is that the highest-risk accounts are not always the ones to call. An account almost certain to self-cure wastes the call; an account almost certain to be lost wastes it too. The value is concentrated where the intervention changes the outcome, which is the middle of the distribution.

Indian conduct rules shape what the intervention can be. Recovery agents act as the lender's agents and the lender remains responsible for their conduct; contact is restricted to reasonable hours, conventionally between 8 a.m. and 7 p.m.; intimidation, humiliation and contacting people outside the agreed list are prohibited. Digital lending brings a further layer: lending service providers must be disclosed, credit limits may not be increased automatically without consent, and any default loss guarantee arrangement between a lender and a service provider is capped at 5% of the underlying loan portfolio.

📘 **DEFINE — Restructuring and compromise settlement**
*Restructuring* is a concession granted to a borrower in financial difficulty that the lender would not otherwise offer — a moratorium, a tenor extension, a rate reduction, or capitalisation of arrears. It is not generosity but a bet that a temporarily distressed borrower recovers more cash than an enforced default would, and it carries a classification consequence, since the granting of a concession because of financial difficulty is itself evidence of credit impairment. Restructured accounts follow their own upgradation path, requiring satisfactory performance over a specified period before they can move back. A *compromise settlement* is different: the lender accepts less than the full dues in full and final settlement, closing the account. Both create the same governance risk, sometimes called extend-and-pretend — a book where arrears look low because delinquency has been repeatedly restructured away — which is why restructured and settled balances are reported separately and why re-default rates on them are among the most watched numbers in a stressed book.

Recovery routes differ by an order of magnitude in speed. Gold is auctioned under a prescribed process, with the pledged gold to be returned within seven working days of closure and a ₹5,000 per day penalty for delay. Vehicles are repossessed and resold within months. Housing runs through SARFAESI, with its 60-day notice and its ₹1 lakh threshold, and where that fails through a Debts Recovery Tribunal for claims of ₹20 lakh and above. Unsecured retail runs through in-house collections, then agencies, then Lok Adalat settlements for smaller matters, and finally sale — to an asset reconstruction company against security receipts, which the selling bank then holds at a 150% risk weight, or to a debt purchaser as a written-off pool.

Two Indian markers sit alongside recovery and change behaviour. A borrower whose dues are ₹25 lakh or more and who has the means to pay but does not, or who diverts or siphons funds, may be classified a *wilful defaulter*, which carries an additional 5% provision on the lender's exposure and severe consequences for the borrower's future access to credit. And a *technical write-off* removes a balance from the books without extinguishing the claim, which flatters the gross NPA ratio while leaving recovery efforts running — a distinction that must be carried explicitly in any LGD dataset, since a written-off account is not a resolved one.

► **IN ONE LINE** — Collections is worth modelling because the marginal account saved, not the average account contacted, is where the money is.

**You can now:**
- Explain why collections effort targets the middle of the risk distribution rather than the top.
- Distinguish restructuring, compromise settlement and technical write-off, and say what each does to reported asset quality.
- Rank the Indian recovery routes by speed and name the threshold that governs each.

---

# §16 · GOVERNANCE, FAIRNESS AND MODEL RISK

**A model nobody can explain, challenge or retire is a liability regardless of its Gini, and in India the controls around an ECL model are themselves written into the regulation.**

*Model risk* is the risk of loss from decisions based on incorrect or misused models, and it has two sources: the model may be wrong, or it may be right and used for something it was not built for. The 2026 Directions prescribe a three-tier structure rather than leaving it to practice. Model owners in the front line develop, implement and use models, and are accountable for approval, validation and performance. The risk management and compliance function identifies and monitors risks across the model ecosystem, oversees independent validation, and enforces limits. Internal audit provides objective assurance on both and reports to the board or the audit committee. Above all three sits a board committee that must include the chief financial officer and the chief risk officer, charged with challenging the implementation strategy, ensuring data integrity across the ECL lifecycle, and guaranteeing the independence of validation.

Three specific obligations are worth holding separately because they are where implementations usually fail. A *model inventory* must catalogue every model in the ECL lifecycle with its owners, its tier, its dependencies on upstream and downstream models, and its validation status. *Risk-based tiering* must classify models by materiality so that validation intensity follows impact rather than convenience. And each model needs a documented lifecycle — development, pre-implementation validation, implementation, monitoring, independent validation, and recalibration or retirement — with a prospectus stating methodology, limitations and initial validation outcomes.

Independent validation asks three questions in order. Is the model *conceptually sound* — do the variables make sense, is the target well defined, is the estimation appropriate? Does *ongoing monitoring* show it still works, using the statistics of §8? And does *outcomes analysis* show its predictions matching reality on data it has never seen? A model can pass the third and fail the first, and that combination is the dangerous one, because it works until the regime it silently depends on changes.

✅ **CHECK — Reasons for rejection**
For every declined applicant, the lender must be able to state the main reasons for the decision. This is a Fair Practices Code obligation in India: where a loan application is rejected, the lender conveys in writing the principal reason or reasons. Pass condition: for a random sample of declines, the reasons generated are specific — "utilisation of existing revolving limits is too high", not "credit score insufficient" — tied to actual model inputs, and reproducible from the stored score record months later. A model whose reasons must be reconstructed by re-running a current version against an old application has failed this test even if the reasons sound plausible, because the record does not support the decision that was actually made.

🔴 **TRAP — "There is no fair lending law here, so fairness is not a model problem"**
The wrong belief is that the absence of an Indian equivalent to a disparate-impact statute means outcome disparities carry no consequence. Three things are true instead. Conduct regulation already reaches part of the ground: the Fair Practices Code requires non-discriminatory application of policy and written reasons for rejection, digital lending rules constrain data collection and automatic limit increases, and the Digital Personal Data Protection Act, 2023 governs the personal data on which any of this is built. Supervisory and reputational exposure does not wait for a statute. And most practically, the mechanism that produces disparities is a model-quality problem regardless of law: omitting a sensitive attribute prevents its direct use and does nothing about proxies, because a model with enough correlated inputs — postal code, device, employer type, education — reconstructs the omitted variable implicitly and does so better the more flexible it is. The correction is to test outcomes by group rather than to inspect inputs, to document the business necessity of variables producing an adverse disparity, and to look for a less discriminatory alternative of comparable predictive power. On how Indian supervisors will ultimately treat such testing, the record is thin, and any note claiming otherwise is guessing.

The last governance question is when to retire a model. The honest triggers are a sustained fall in discrimination that recalibration cannot address, a population shift large enough that the development sample no longer resembles the applicant flow, a change in the product or in the classification rules that breaks the target, and simple age. Most retail scorecards are redeveloped on a two-to-four-year cycle, not because they expire on a date, but because the accumulated drift of population, product and economy reliably exceeds tolerance in that window.

**You can now:**
- Describe the three-tier model risk structure and the board-level oversight the Directions require.
- Name the three validation questions and say which failure combination is most dangerous.
- Explain why excluding a sensitive attribute does not remove its influence, and what testing replaces it.

---

# §17 · THE TRAPS

**Every row below is a belief that is coherent, widely held, and wrong in a way that costs money.**

| What people believe | What is true |
|---|---|
| Capital is held against expected losses | Capital is held against *unexpected* losses; expected loss is covered by pricing and by provisions, which is why the provision stack and the capital stack are separate numbers |
| Default means loss | Defaults cure, often at a third to a half on secured books; that is why LGD exists as a separate parameter |
| An account improves when the borrower starts paying again | An NPA upgrades only when the entire arrears of interest and principal are cleared across *all* facilities of that borrower; cure in India is all-or-nothing |
| One late credit card does not affect the customer's other loans | NPA and Stage 3 classification are applied at borrower level, so one impaired facility drags every other facility of that borrower with it |
| A cash credit account inside its limit is performing | It is out of order, and therefore NPA, if credits over the previous 90 days do not even cover the interest debited |
| The ECL framework replaces NPA classification | It runs alongside it; "default" in the ECL Directions is *defined as* NPA status, and banks report both a stage and an asset classification |
| Better models mean lower provisions | On good secured books the prudential floor is above the modelled number, so the floor is what gets booked and better estimation changes nothing reported |
| Better models mean lower capital | Not in India. The RBI has implemented only the Standardised Approach, so risk weights come from a table and the bank's own PD never enters the capital calculation |
| Stage 1 to Stage 2 is a soft warning | It multiplies the allowance by two to ten times, and a small move in a macro forecast can push a whole cohort across the boundary at once |
| Averaging the macro scenarios and then computing ECL saves time | Loss is convex in the economy, so ECL of the average scenario is below the average of the ECLs; weight the outputs |
| A falling gross NPA ratio means improving credit | In a growing book the denominator outruns the numerator, and technical write-offs shrink the numerator without any cash arriving; use lagged ratios or vintage curves |
| A falling Gini means the model has degraded | Tightening the cut-off lowers sanctioned-book Gini mechanically through range restriction; compare only at equal approval rates |
| A high-Gini model is a good model | Gini says nothing about level; a perfectly ranked model with PDs half of reality under-provisions by half |
| Recalibration and redevelopment are the same kind of fix | Calibration is one number and nearly free; discrimination cannot be restored by any transformation of the score |
| Reject inference recovers the missing outcomes | It makes an assumption explicit; only funding a random sample of would-be declines produces real evidence |
| A very high information value is a great find | Above roughly 0.5, suspect leakage — the variable is probably a consequence of the default rather than a predictor of it |
| PSI rising is bad news | PSI is unsigned; the population may have improved. Read the band decomposition, never the headline |
| Unused credit card limits are free | From 1 April 2027 unconditionally cancellable commitments attract a 5% credit conversion factor, rising to 10% after three years |
| A card is a card for capital purposes | A transactor sits in regulatory retail at 75% and a revolver at 125%; one day of delinquency resets the twelve-month clock |
| An exposure that is commercially secured is regulatorily secured | Land, buildings, plant, machinery and current assets are not eligible collateral for defining the secured portion of an NPA for risk weighting |
| Moratorium-period data can be used like any other | The 2020 standstill suspended the ageing process that defines default, so days-past-due series from that period record policy rather than borrower behaviour |
| Raising the price on a risk segment raises its profit proportionally | It changes who accepts; the better credits leave, the observed default rate rises, and the gain shrinks or reverses |
| Collections should target the worst accounts | It should target accounts where contact changes the outcome, which is the middle, not the tail |
| Excluding sensitive attributes makes a model fair | It prevents direct use only; proxies reconstruct the excluded variable, and disparity must be tested on outcomes |
| The cut-off belongs where the bad rate becomes unacceptable | It belongs where risk-adjusted return on capital crosses the hurdle rate; some high-loss segments clear it and some low-loss segments do not |

---

# §18 · THE QUESTIONS

**If a section of this note generated no question below, it should not have been in the note.**

## Tier 1 — must be instant

| Question | Answer |
|---|---|
| The loss equation | EL = PD × LGD × EAD |
| NPA trigger, term loan and credit card | Interest or principal overdue more than 90 days; for a card, minimum amount due unpaid for 90 days from the statement payment due date |
| The three limbs of "out of order" | Outstanding above limit or drawing power for 90 continuous days; no credits for 90 days; credits insufficient to cover interest debited in the previous 90 days |
| SMA buckets | SMA-0: 1–30 days · SMA-1: 31–60 · SMA-2: 61–90 |
| Level at which NPA and Stage 3 are applied | Borrower level; Stage 2 is applied at facility level |
| NPA upgradation condition | Entire arrears of interest and principal cleared across all facilities of the borrower |
| ECL commencement and transition period | 1 April 2027; capital add-back fractions 4/5, 3/5, 2/5, 1/5 to FY2030-31 |
| SICR backstops | 30 days past due, rebuttable; revolving facilities, continuously over limit or drawing power for up to 60 days |
| Stage allowances | Stage 1: 12-month ECL. Stages 2 and 3: lifetime ECL |
| Prudential floors, unsecured retail | Stage 1: 1.00% · Stage 2: 5% · Stage 3: 25% year one, 100% after |
| Regulatory PD floor and backstop LGDs | PD 0.03%; LGD 65% secured, 70% unsecured, 30% for cash, gold, government securities, LIC, KVP, NSC |
| Minimum bank capital ratios | CRAR 9%, or 11.5% with the capital conservation buffer; CET1 5.5%, 8% with buffer; tier 1 7% |
| Risk weights: regulatory retail, personal loan, card revolver, card transactor | 75%, 125%, 125%, 75% |
| Housing risk weights, first two loans | 20% / 25% / 30% / 40% across LTV ≤50 / 50–60 / 60–80 / 80–90; +5pp if outstanding ≥ ₹3 crore |
| Weight of evidence | ln( (goods in bin ÷ total goods) ÷ (bads in bin ÷ total bads) ) |
| Gini in terms of AUC | Gini = 2 × AUC − 1 |
| PSI action thresholds | <0.10 stable; 0.10–0.25 investigate; >0.25 shifted |
| EAD on a revolving line | Drawn balance + CCF × undrawn headroom |
| Scaling factor for points | Factor = PDO ÷ ln 2; with PDO 20, Factor = 28.854 |

## Tier 2 — should be solid

| Question | Answer |
|---|---|
| Compute IV for a two-bin variable where bin A holds 30% of goods and 50% of bads | WOE_A = ln(0.6) = −0.5108; WOE_B = ln(0.7/0.5) = 0.3365; IV = (−0.2)(−0.5108) + (0.2)(0.3365) = 0.1022 + 0.0673 = 0.1695 |
| A ₹40,00,000 housing loan, PD 0.8%, LGD 15%. What is the Stage 1 provision? | Modelled ECL = ₹4,800 = 0.12%; the 0.25% floor gives ₹10,000, and the floor binds |
| A ₹3,00,000 unsecured loan, PD 2%, LGD 70%. Model or floor? | Modelled ₹4,200 = 1.40%, above the 1% floor, so the model binds — and still binds at 1.21% after discounting at 16% |
| Capital on a card with ₹1,00,000 drawn and ₹2,00,000 undrawn, at 10% CCF and 11.5% | EAD ₹1,20,000; revolver at 125% → RWA ₹1,50,000 → ₹17,250. Transactor at 75% → ₹90,000 → ₹10,350 |
| A book's central tendency moves from 3% to 4.5%; what changes in the model? | Intercept only: shift log-odds by ln(0.045/0.955) − ln(0.03/0.97) = 0.424. Ranking untouched |
| Why lifetime ECL exceeds twelve-month ECL by more than the ratio of horizons | Marginal PDs compound over survival, exposure is still outstanding in later years, and later-year conditional default rates are usually higher than the first year's |
| Chain roll rates of 8%, 50%, 60%, 75%, 95% on ₹1,000 crore of standard balance | ₹1,000 crore × 0.0171 = ₹17.10 crore of expected write-off |
| Why the same effort saves more value in SMA-0 than in SMA-2 | More accounts are available to save and each removal cancels a longer chain of roll rates |
| Why average LGD can describe no individual account | The distribution is bimodal — near-full cure or near-total loss — so the mean sits in the empty middle, an effect amplified by the all-or-nothing upgradation rule |
| Two ways to correct a gross NPA ratio in a growing book, and one Indian complication | Lag the denominator by the emergence period, or move to vintage analysis; and strip out technical write-offs, which shrink the numerator without cash |
| The one unbiased remedy for reject-inference bias | Deliberately sanction a random sample of applicants below the cut-off and observe them |
| Why an Indian bank cannot cut its capital by building a better PD model | Capital uses the Standardised Approach; risk weights come from a supervisory table and internal estimates never enter |

## Tier 3 — judgement

| Question | Answer |
|---|---|
| Provisions rise 30% quarter on quarter. Where do you look, in order? | Decompose: stage transfers, then scenario weights and forecast changes, then model and assumption updates, then volume and mix, then any floor that started binding. Only the residual is genuine credit deterioration |
| The cut-off can move down 20 points. What decides it? | Expected RAROC of the swap set against the hurdle rate, after price elasticity and acceptance effects — not the swap set's bad rate |
| Sanctioned-book Gini fell from 0.42 to 0.36 over two years. Broken? | Not established. Check approval rate first for range restriction, then population stability, then discrimination on through-the-door data. Only then consider redevelopment |
| Where is modelling investment actually repaid in an Indian bank? | Selection and pricing, Stage 2 and Stage 3 provisioning where the model sits above the floor, and collections prioritisation — not capital, and not Stage 1 on well-secured books |
| A retail portfolio has no usable downturn in its history. How do you set stressed parameters? | Say so explicitly, then use a proxy portfolio, a structural link to a collateral price index, or a conservative overlay — and record the choice as judgement, because the record is thin |
| A gradient-boosted model beats the scorecard by 6 Gini points in development and 1 out of time. Ship it? | The out-of-time gap is the real uplift, and 1 point rarely repays the cost in explainability, monotonicity control and reason-code reconstruction. Investigate the development gap as evidence of overfitting or leakage |
| Where should conservatism live? | In LGD and EAD, keeping PD as unbiased as possible, so the ranking used for sanction decisions stays undistorted while provisions remain prudent |

---

# §19 · FORMULA SHEET

| Name | Formula |
|---|---|
| Expected loss | $EL = PD \times LGD \times EAD$ |
| Logistic model | $\ln\!\big(p/(1-p)\big) = \beta_0 + \sum_i \beta_i x_i$ |
| Weight of evidence | $WOE_i = \ln\!\big((g_i/G) \div (b_i/B)\big)$ |
| Information value | $IV = \sum_i (g_i/G - b_i/B) \times WOE_i$ |
| Oversampling intercept correction | $\beta_0^{corr} = \hat{\beta}_0 - \ln(\rho_1/\rho_0)$ |
| Score scaling | $Score = Offset + Factor \times \ln(odds)$ |
| Scaling factor | $Factor = PDO \div \ln 2$ |
| Scaling offset | $Offset = S_0 - Factor \times \ln(odds_0)$ |
| Points per attribute | $Points_i = -\big(\beta_i WOE_i + \beta_0/n\big) Factor + Offset/n$ |
| Gini | $Gini = 2 \times AUC - 1$ |
| Kolmogorov–Smirnov | $KS = \max_s |F_{bad}(s) - F_{good}(s)|$ |
| Population Stability Index | $PSI = \sum_i (A_i - E_i)\ln(A_i/E_i)$ |
| Loss given default | $LGD = 1 - \sum_t \frac{R_t - C_t}{(1+d)^t} \div EAD$ |
| Exposure at default | $EAD = B + CCF \times (L - B)$ |
| Survival | $S_t = \prod_{k \le t}(1 - h_k)$ |
| Marginal default probability | $PD_t^{marg} = S_{t-1} \times h_t$ |
| Expected credit loss | $ECL = \sum_{t=1}^{T} PD_t^{marg} LGD_t EAD_t (1+EIR)^{-t}$ |
| Final allowance | $Allowance = \max(ECL_{modelled},\ Floor \times Exposure)$ |
| Loan-to-value | $LTV = \text{total loan outstanding} \div \text{realisable value of property}$ |
| Risk-weighted assets | $RWA = Exposure_{net\ of\ specific\ provisions} \times RW$ |
| Capital requirement | $Capital = RWA \times CRAR$ |
| Transitional add-back | $f \times \max\big(0,\ ECL_{1\ Apr\ 2027} - IRACP_{31\ Mar\ 2027}\big)$, $f$ = 4/5, 3/5, 2/5, 1/5 |
| RAROC | $RAROC = \big[(Rev - Opex - EL)(1-\tau)\big] \div Capital$ |
| Roll-rate chain to loss | $Loss = Balance \times \prod_j r_j$ |
| Recalibration shift | $\Delta = \ln\!\frac{p_1}{1-p_1} - \ln\!\frac{p_0}{1-p_0}$ |
| Constants | $\ln 2 = 0.693147$; $Factor$ at PDO 20 $= 28.854$ |

---

# §20 · GLOSSARY

| Term | Meaning |
|---|---|
| Account Aggregator | RBI-regulated consent framework letting a customer share financial data between regulated entities |
| ACPIR Directions, 2026 | The RBI (Commercial Banks – Asset Classification, Provisioning and Income Recognition) Directions, 2026; the ECL framework, effective 1 April 2027 |
| Adverse selection | The tendency for a price rise to be accepted disproportionately by worse risks, because better risks have alternatives |
| ARC | Asset reconstruction company; buys distressed assets from lenders, often paying partly in security receipts |
| Attrition | Loss of accounts to competitors or repayment, usually selective toward better credits |
| AUC | Area under the ROC curve; probability a random bad scores worse than a random good |
| Augmentation | A reject-inference method reweighting sanctioned accounts to stand in for similar rejects |
| Bad | An account meeting the default definition inside the outcome window |
| Behavioural scorecard | A model scoring existing accounts using their own payment and usage history |
| CCF | Credit conversion factor; fraction of an off-balance-sheet or undrawn amount treated as exposure |
| CET1 | Common equity tier 1; the highest-quality capital, minimum 5.5% of RWA for Indian banks, 8% with the buffer |
| CIC | Credit information company; India's four are TransUnion CIBIL, Experian, Equifax and CRIF High Mark |
| CICRA | Credit Information Companies (Regulation) Act, 2005; the statute governing bureaus |
| Coarse classing | Merging fine bins into a final small set with stable, defensible weights of evidence |
| Collections score | A model ranking delinquent accounts by expected benefit from intervention |
| Compromise settlement | Acceptance of less than full dues in full and final settlement, closing the account |
| CRAR | Capital to risk-weighted assets ratio; minimum 9% for banks, 11.5% with the capital conservation buffer, 15% for larger NBFCs |
| Cure | Return of a defaulted account to standard status; in India requires clearing all arrears on all facilities |
| Cut-off | The score threshold at which an application is sanctioned or declined |
| DLG | Default loss guarantee; a first-loss cover from a lending service provider, capped at 5% of the loan portfolio |
| Discrimination | A model's ability to rank order goods and bads; distinct from calibration |
| Doubtful asset | An NPA that has remained in the sub-standard category for twelve months |
| DPD | Days past due |
| Drawing power | The permitted borrowing limit on a cash credit facility, computed from eligible current assets |
| DRT | Debts Recovery Tribunal; hears lender recovery claims of ₹20 lakh and above |
| EAD | Exposure at default; amount outstanding when default occurs |
| EBLR | External benchmark lending rate; the repo-linked benchmark to which floating-rate retail loans must be tied |
| ECL | Expected credit loss; the forward-looking loss allowance |
| EIR | Effective interest rate determined at initial recognition; the prescribed ECL discount rate |
| Fine classing | Initial cutting of a variable into many narrow bins before merging |
| Flow rate | Proportion of a bucket moving to the next-worse bucket in a month |
| Gini | Rescaled AUC; 0 is random, 1 is perfect ranking |
| Gross NPA ratio | Non-performing advances divided by gross advances |
| HUF | Hindu Undivided Family; a recognised borrower type that qualifies for the retail orientation criterion |
| Ind AS 109 | The Indian accounting standard on financial instruments; the ECL basis already used by NBFCs |
| Indeterminate | An account neither clearly good nor clearly bad in the outcome window |
| Information value | Single-variable measure of separation between goods and bads |
| IRACP | Income recognition, asset classification and provisioning; the incurred-loss regime in force until 31 March 2027 |
| IRB | Internal Ratings Based approach to capital; permitted in some jurisdictions, not implemented in India |
| KFS | Key Facts Statement; the mandatory disclosure of all-in cost, including annual percentage rate, for retail loans |
| KS | Kolmogorov–Smirnov statistic; largest gap between cumulative good and bad distributions |
| Lagged delinquency | Bad balance divided by a historic balance, correcting for growth |
| LGD | Loss given default; unrecovered fraction of exposure after costs and discounting |
| Lok Adalat | A statutory conciliation forum used for settling smaller recovery matters |
| LTV | Loan-to-value; total loan outstanding divided by the realisable value of the property |
| Model risk | Risk of loss from a model being wrong or misused |
| Monotonicity constraint | A restriction forcing a model's response to a variable to move in one direction only |
| Months on book | Time since disbursement; the horizontal axis of a vintage curve |
| NBFC | Non-banking financial company; a non-deposit-taking or deposit-taking lender regulated separately from banks |
| NPA | Non-performing asset; the Indian legal definition of default |
| Observation point | The date at which predictive data is frozen for model development |
| Outcome window | The period after the observation point over which default is observed |
| Out of order | The three-limbed NPA test for cash credit and overdraft accounts |
| Override | A manual decision contradicting the model's recommendation |
| Parcelling | A reject-inference method assigning bad flags to rejects in proportion to inferred odds |
| PD | Probability of default over a stated horizon; floored at 0.03% for ECL |
| PDO | Points to double the odds; the scaling convention for a scorecard |
| PIT | Point-in-time; a risk estimate conditional on current economic conditions |
| POCI | Purchased or originated credit-impaired financial asset; accounted for with a credit-adjusted effective interest rate |
| Procyclicality | The tendency of risk measures to tighten credit in downturns and loosen it in booms |
| Provision coverage ratio | Provisions held divided by gross NPAs |
| Prudential floor | The regulatory minimum provision by product and stage, below which a modelled ECL may not fall |
| PSI | Population Stability Index; measure of drift in a score distribution |
| RAROC | Risk-adjusted return on capital |
| Range restriction | Loss of measured discrimination caused by removing the worst accounts from the sample |
| Regulatory retail portfolio | The 75%-risk-weight class, entered by passing the orientation, product, low-value and granularity tests |
| Reject inference | Techniques for including declined applications in scorecard development |
| Restructuring | A concession granted because of the borrower's financial difficulty |
| Roll rate | Probability of moving from one delinquency bucket to the next-worse in a month |
| RWA | Risk-weighted assets; exposure net of specific provisions multiplied by the supervisory risk weight |
| SARFAESI | The 2002 Act allowing a secured lender to enforce security without a court, above a ₹1 lakh threshold |
| Satellite model | A regression linking a portfolio risk measure to macroeconomic variables |
| Scorecard | A model expressed as integer points per attribute, summing to a score |
| Seasoning | The tendency of default risk to follow a hump-shaped curve in months on book |
| Security receipt | The instrument an ARC issues to a selling lender; risk weighted at 150% |
| SICR | Significant increase in credit risk; the Stage 1 to Stage 2 trigger |
| SMA | Special Mention Account; the pre-NPA early-warning buckets SMA-0, SMA-1 and SMA-2 |
| Stage 1 / 2 / 3 | ECL classifications carrying 12-month ECL, lifetime ECL, and lifetime ECL on credit-impaired assets |
| Standardised Approach | Capital calculated from supervisory risk weights rather than internal models; the only approach the RBI has implemented |
| Sub-standard asset | An NPA for twelve months or less |
| Swap set | Accounts that change decision when a cut-off moves |
| Technical write-off | Removal of a balance from the books without extinguishing the claim or ending recovery efforts |
| Through-the-door | The full population of applicants, sanctioned and declined |
| Transactor | A card or charge card obligor who has repaid in full at every due date, including the three-day grace period, for twelve months |
| Transitional adjustment amount | The excess of day-one ECL over IRACP provisions at transition, partly addable back to CET1 until FY2030-31 |
| TTC | Through-the-cycle; a risk estimate deliberately insensitive to current conditions |
| UCRF | Uniform Credit Reporting Format; the prescribed bureau reporting schema |
| Unexpected loss | The excess of a tail-percentile loss over expected loss; what capital covers |
| Vintage | The cohort of accounts disbursed in a given period |
| Weight of evidence | Log-odds transformation of a bin, encoding its riskiness relative to the book |
| Wilful defaulter | A borrower with dues of ₹25 lakh or more who has the means to pay but does not, or who diverts funds; attracts an additional 5% provision |

---

# §21 · THE COMPRESSION

**Retail credit risk is the conversion of an unknowable individual outcome into a measurable population rate, and the whole subject is the discipline of keeping that rate honest.**

Everything above is one loop. You define an event — in India, the non-performing asset, at borrower level, ninety days overdue. You freeze a photograph of the borrower, wait a stated period for the verdict, fit a model that ranks and a calibration that levels, and multiply the resulting probability by a severity and an exposure. You then hand that number to three consumers who each treat it differently: pricing wants today's odds, provisioning wants today's odds under a forecast and then compares the answer with a regulatory floor, and capital ignores the model entirely and reads a risk weight from a table. Then you watch the population drift away from the one you measured, and start again.

The errors that matter are always the same four. Measuring the wrong event, by building at facility level what the rulebook defines at borrower level. Measuring on the wrong population, by forgetting that you only observe the borrowers you sanctioned. Confusing the mean with the tail, by funding expected loss with capital or unexpected loss with price. And reading a ratio whose numerator and denominator come from different moments in time.

There is a fifth error peculiar to a system in transition, and it is worth naming separately: assuming that a number computed under one regime means the same thing under the next. The provisioning basis changes on 1 April 2027 and the capital basis changes with it, while the definition of default stays exactly where it has been. Anything built on the definition survives. Anything built on the old provisioning arithmetic does not.

► **IN ONE LINE** — A retail lender cannot know which borrower will default, so it prices, provisions and capitalises against the fraction that will, and every technique in the field exists to keep that fraction accurate, current, and honestly conditioned on the rules that define it.
