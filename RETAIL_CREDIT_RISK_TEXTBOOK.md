# THE RETAIL CREDIT RISK ANALYTICS PROJECT
## A Complete, Self-Contained Textbook and Build Manual

### From zero knowledge to full command of the domain, the engineering, and the artefact you built

---

**What this document is.** This is the complete record and explanation of the Retail Credit Risk Analytics Suite — a working system that takes 466,285 raw Lending Club loans and produces Basel III regulatory capital, IFRS 9 expected credit loss provisions, a portfolio monitoring layer, an institutional dashboard, an AI analyst grounded in real regulatory documents, and a full SR 11-7 model documentation pack.

**What it assumes.** Nothing. Not credit risk, not banking, not Python, not the command line, not Git. Every term is defined at first use. Every formula is derived and explained. Every command is given in full with the expected output. Every error that occurred during the build is reproduced, diagnosed, and fixed.

**The promise.** You should not need to open the repository, the dataset, the IDE, a regulatory PDF, or a search engine to understand anything written here. If you find yourself needing to, that is a defect in this document, not in you.

---

## HOW TO READ THIS BOOK

There are three ways through, depending on what you need today.

**If you are learning the domain from scratch** — read Part I straight through, slowly. It is a self-contained course in retail credit risk as it is actually practised in 2026. It contains no code. Then read Part IV, where the domain concepts become real numbers on a real portfolio.

**If you are preparing for an interview tomorrow** — read Part VII first (the interview compendium), then Part I Chapter 15 (the one-page formula sheet), then skim the "What actually happened" boxes in Part IV so the numbers are in your mouth. Then come back and do the full read.

**If you are rebuilding or extending the project** — Part II (engineering), Part III (the data), and Part IV (the stage-by-stage build with every exact prompt) are your working manual. Part V is the error registry; when something breaks, look there first.

### Typographic conventions used throughout

| Marker | Meaning |
|---|---|
| 📘 **CONCEPT** | A domain idea explained from first principles. No prior knowledge assumed. |
| 💻 **COMMAND** | Something you type into PowerShell. Given verbatim, with expected output. |
| 🤖 **PROMPT** | Text pasted to the IDE coding agent. Reproduced exactly as it was used. |
| ✅ **WHAT GOOD LOOKS LIKE** | The result that means the step succeeded, and how to recognise it. |
| 📊 **WHAT ACTUALLY HAPPENED** | The real output from the real build, with real numbers. |
| 🔴 **ERROR** | Something that genuinely broke, why, and the exact fix. |
| ❓ **THE QUESTIONS** | The comprehension questions asked at that point, with full answers. |
| ⚠️ **HONESTY NOTE** | A limitation, approximation, or overclaim risk. These are the most valuable paragraphs in the book. |

### The single most important sentence in this document

> The project is credible not because the models are clever, but because every limitation is named out loud before anyone has to ask.

Everything else follows from that.

---

## TABLE OF CONTENTS

**PART I — THE DOMAIN FROM ZERO**
1. What a bank is, and why lending is a risk business
2. The language of default: delinquency, DPD, charge-off, recovery, cure
3. The three parameters: PD, LGD, EAD — and the fourth, CCF
4. Expected loss versus unexpected loss: the split that organises everything
5. Basel: what it is, why it exists, Standardised versus IRB
6. The Basel IRB supervisory formula, derived term by term
7. IFRS 9 and Ind AS 109: staging, SICR, and expected credit loss
8. CECL: the American cousin, and why it always provisions more
9. Scorecards: Weight of Evidence, Information Value, and points scaling
10. Model validation: discrimination, calibration, stability
11. Portfolio monitoring: vintage curves, roll rates, transition matrices
12. Model risk governance: SR 11-7 and the three lines of defence
13. The Indian regulatory context: RBI, Ind AS 109, and what CPRA teams do
14. Where this all sits in a real bank's org chart
15. The one-page formula sheet

**PART II — THE ENGINEERING FROM ZERO**
16. The machine: Windows, PowerShell, paths, and the filesystem
17. Python, virtual environments, and package management
18. Project architecture: why `src/creditrisk/` and not the root
19. Git and GitHub: the save-history for code
20. Testing with pytest: why every stage shipped with tests
21. Config as data: YAML, and why nothing is hardcoded
22. Working with an IDE coding agent: the standing rules discipline

**PART III — THE DATA**
23. The Lending Club dataset: provenance, shape, and honest limits
24. The complete variable dictionary, classified
25. The loan status taxonomy and what each value means

**PART IV — THE BUILD: TWELVE STAGES**
- Stage 0 — The workbench
- Stage 1 — Data foundation and the 12-month target
- Stage 2 — Sampling and the WoE/IV engine
- Stage 3 — The PD scorecard
- Stage 4 — The validation battery
- Stage 5 — LGD
- Stage 6 — EAD and CCF
- Stage 7 — Expected loss and Basel capital
- Stage 8 — IFRS 9 ECL
- Stage 9 — Portfolio monitoring
- Stage 10 — The dashboard
- Stage 11 — The AI analyst
- Stage 12 — Documentation and the management deck
- Stage 13 — GitHub and publication

**PART V — THE ERROR REGISTRY**

**PART VI — THE LIMITATIONS REGISTER**

**PART VII — THE INTERVIEW COMPENDIUM**

**PART VIII — THE SECOND PASS: how to actually learn this**

**APPENDICES** — glossary, command reference, file map, standing rules, prompt library

---
---

# PART I — THE DOMAIN FROM ZERO

*This part contains no code. It is a course in retail credit risk. Read it slowly. Everything in Part IV is an application of something in here.*

---

## Chapter 1 — What a bank is, and why lending is a risk business

### 1.1 The business model, stated plainly

A bank takes money from people who have it (depositors, bondholders, shareholders) and gives it to people who want it (borrowers), charging the second group more than it pays the first. The difference is called the **net interest margin**, and it is most of how a commercial bank makes money.

That sounds simple, and it would be, except for one fact: **some borrowers do not pay it back.**

If a bank lends ₹100 to a hundred people at 15% interest, and all hundred repay, it collects ₹11,500 against ₹10,000 lent — a ₹1,500 gain before costs. If seven of them never repay a rupee, it collects roughly ₹10,695 against ₹10,000 lent, and after funding costs and operating expenses it may well have lost money. The entire profitability of a lending business is decided in that gap between the interest earned and the losses suffered.

So the central question of a bank is not "how do we lend more?" It is:

> **How much will we lose, when, on which loans, and do we have enough money set aside to survive it?**

Credit risk analytics is the discipline that answers that question with numbers instead of intuition.

### 1.2 Retail versus wholesale

Lending splits into two very different worlds.

**Wholesale (or corporate) credit risk** concerns loans to companies. There are relatively few of them, each is large, and each is analysed individually — you can afford to have an analyst read the borrower's financial statements, meet management, and assign a rating by judgement. The statistics are thin (you may have a few hundred defaults in a decade) and the models are correspondingly structural rather than purely empirical.

**Retail credit risk** concerns loans to individuals — personal loans, credit cards, auto loans, home loans, consumer durable finance. There are millions of them, each small, and no human reads any individual file. The only tractable approach is statistical: you build a model on hundreds of thousands of past loans and apply it to every new applicant automatically.

This project is entirely retail. That matters, because it determines everything downstream:

- You have **lots of data** (466,285 loans here), so empirical models work.
- Individual loans are **small**, so per-loan precision matters less than **portfolio-level accuracy**.
- Defaults are **frequent enough to model** (3–4% per year here, versus perhaps 0.5% for investment-grade corporates).
- Regulation gives retail its **own formulas**, distinct from corporate ones — you will see this in Chapter 6.

The job description this project was built against — Credit Portfolio Risk Analytics (CPRA) Retail, at HDFC Bank — sits squarely in this world.

### 1.3 The four things a retail risk team is actually asked to produce

Strip away the vocabulary and a retail credit risk analytics team exists to deliver four things:

**1. Risk parameter estimates.** For every loan in the book: how likely is it to default (PD), how much will we lose if it does (LGD), and how much will be outstanding at that moment (EAD). These three numbers are the raw material for everything else.

**2. Regulatory capital.** Using those parameters, compute how much shareholder money the bank must hold in reserve to satisfy the banking regulator. This is the **Basel** framework. Capital is expensive — it is money that cannot be lent out — so getting this right has direct commercial consequences.

**3. Accounting provisions.** Using the same parameters differently, compute how much loss the bank must recognise *today* in its published accounts for losses it expects in the future. This is **IFRS 9** (called **Ind AS 109** in India, **CECL** in the United States). This directly reduces reported profit, so it is scrutinised by auditors, investors, and the board.

**4. Portfolio insight.** Dashboards, vintage analysis, early warning indicators, and presentations that tell senior management whether the book is getting better or worse, and where.

Every one of the twelve stages in Part IV serves one of those four outputs. When you lose the thread, come back to this list.

### 1.4 The distinction that trips everyone up: capital versus provisions

These two are constantly confused, so fix the difference now.

**Provisions** are for the losses you *expect*. If you lend to a thousand people and history says thirty-four of them will default, that is not a surprise — it is a predictable cost of the business, like electricity. You charge for it in the interest rate, and you book it as an expense. Provisions are an **accounting** concept, governed by accounting standards (IFRS 9 / Ind AS 109 / CECL). They reduce profit.

**Capital** is for the losses you do *not* expect. In a bad year — a recession, a pandemic, a regional employment collapse — defaults do not run at 3.4%, they run at 9%. That excess above the expected level is **unexpected loss**, and you cannot price it into a loan because by definition you do not know when it will arrive. Instead you require the bank's *shareholders* to keep a permanent cushion of their own money in the business, big enough to absorb it without the bank failing. Capital is a **prudential** concept, governed by the banking regulator (Basel / RBI). It does not reduce profit; it constrains how much you can lend.

> **The one-line version:** Expected loss is a cost you charge for. Unexpected loss is a shock you hold capital against.

Chapter 4 makes this precise. Chapters 5–8 build both.

---

## Chapter 2 — The language of default

Before any modelling, the vocabulary. Every one of these terms appears in the code, the regulations, and the interview.

### 2.1 Delinquency and days past due (DPD)

A loan has a scheduled payment date each month. If the borrower misses it, the loan becomes **delinquent**. How delinquent is measured in **days past due (DPD)** — the number of days since the oldest unpaid instalment was due.

The industry standard buckets:

| Bucket | Meaning |
|---|---|
| **Current** | Paying on time. No missed instalment. |
| **1–29 DPD** | Missed by a few days or weeks. Often administrative — a failed direct debit, a salary delay. Most of these cure. |
| **30–59 DPD** | One full instalment missed. This is the first bucket that genuinely signals distress. |
| **60–89 DPD** | Two instalments missed. Serious. |
| **90+ DPD** | Three instalments missed. **This is the regulatory definition of default.** |

The progression from one bucket to the next is called **rolling**. A loan that goes from 30 DPD to 60 DPD has "rolled forward"; one that returns to Current has **cured**. The rates at which loans roll and cure are a portfolio's early-warning system — see Chapter 11.

### 2.2 What "default" formally means

Both Basel and IFRS 9 use essentially the same definition of default, and it has two limbs:

**Limb 1 — the objective test.** The borrower is more than **90 days past due** on a material obligation.

**Limb 2 — the unlikeliness-to-pay test.** The bank considers the borrower **unlikely to pay** in full without recourse to actions such as realising security — even if they are not yet 90 DPD. Triggers include bankruptcy filing, distressed restructuring, or the bank selling the debt at a material credit-related loss.

In practice, for a retail portfolio, the 90 DPD test does most of the work.

⚠️ **HONESTY NOTE — the definition used in this project.** The Lending Club dataset does not give days past due directly; it gives a *status string*. The build treated these four statuses as default:

- `Charged Off`
- `Default`
- `Late (31-120 days)`
- `Does not meet the credit policy. Status:Charged Off`

Including `Late (31-120 days)` is *broader* than the strict 90-DPD regulatory line, because a loan at 31 days is not yet 90 days past due. This was a deliberate, conservative choice — most Lending Club loans at 31–120 DPD go on to charge off, so treating them as bad predicts where they end up. Critically, the choice was put in a **config file** rather than hardcoded, and a **sensitivity test** was run under the strict definition. The result: the overall 12-month default rate moved from 3.435% to 3.423% — a difference of 0.012 percentage points. The choice does not materially affect any conclusion, and being able to say that with a number is worth more than the choice itself.

### 2.3 Charge-off, write-off, and recovery

When a bank concludes that a defaulted loan will not be repaid through normal collections, it **charges off** (or **writes off**) the balance — it removes the asset from its books and recognises the loss.

This is not necessarily the end. The bank (or a debt-purchasing agency it sells to) may continue to pursue the borrower. Any money that arrives after charge-off is a **recovery**. Recoveries are usually small and slow for unsecured lending, and can be substantial for secured lending where collateral is sold.

In the Lending Club data:
- `total_rec_prncp` — principal repaid *before* default (normal amortisation).
- `recoveries` — money collected *after* charge-off. This is the true recovery.
- `collection_recovery_fee` — the cost of collecting it.

The distinction between those first two columns is the single most important data subtlety in Stage 5, and getting it wrong produces a flattering, wrong LGD. See §Stage 5.2.

### 2.4 Vintage, seasoning, and months on book

A **vintage** (or **cohort**) is the set of loans originated in the same period — the 2013 vintage, the 2012 Q3 vintage. Grouping by vintage is the fundamental analytical move in retail credit, because loans of the same age are comparable and loans of different ages are not.

**Months on book (MOB)** is how long a loan has existed. A loan issued in January 2013 has MOB = 12 in January 2014.

**Seasoning** is the observed pattern that default risk is not constant across a loan's life. Brand-new loans almost never default (the borrower has just been underwritten and has made no payments to miss). Risk rises, peaks, then declines as the surviving borrowers prove themselves.

📊 **WHAT ACTUALLY HAPPENED — the seasoning curve on this portfolio:**

| Months to default | Defaults | % of all defaults |
|---|---|---|
| 0–1 | 376 | 0.74% |
| 2–3 | 0 | 0.00% |
| 4–6 | 2,888 | 5.67% |
| 7–9 | 5,586 | 10.96% |
| 10–12 | 7,168 | 14.06% |
| **13–18** | **15,244** | **29.91%** |
| 19–24 | 9,874 | 19.37% |
| 25–36 | 8,456 | 16.59% |
| 37+ | 1,376 | 2.70% |

The classic hump. Around **44% of all defaults occur between months 10 and 18**, and only 31.4% occur within the first twelve months. This single table is used three separate times later: it justifies the 12-month window (Stage 1), it explains why EAD ratios are high (Stage 6), and it *becomes* the lifetime PD term structure (Stage 8).

The empty 2–3 month bucket is not a bug. Default date was estimated as last payment date plus three months; a loan that made even one payment therefore cannot show a default before month 4. The 376 loans at month 0 are those that never made a single payment.

### 2.5 Right-censoring: the trap that catches everyone

This is the most important statistical concept in Chapter 2, and it caused the first real insight of the project.

Data was extracted in **January 2016**. Loans issued in 2009 had six and a half years to go bad. Loans issued in December 2014 had thirteen months. If you simply count "what fraction of each vintage has ever defaulted," the recent vintages look magnificent — not because they are better, but because **they have not had time to fail yet**. Their outcomes are **right-censored**: cut off on the right-hand side of the time axis.

📊 **WHAT ACTUALLY HAPPENED:**

| Vintage | Loans | Lifetime ("ever") default rate | 12-month default rate |
|---|---|---|---|
| 2007 | 603 | 26.20% | 5.14% |
| 2008 | 2,393 | 20.73% | 6.56% |
| 2009 | 5,281 | — | 4.64% |
| 2010 | 12,537 | — | 3.45% |
| 2011 | 21,721 | — | 3.55% |
| 2012 | 53,367 | 15.62% | 3.74% |
| 2013 | 134,755 | 13.69% | 3.18% |
| 2014 | 235,628 | **8.25%** | **3.44%** |
| **Overall** | **466,285** | **10.93%** | **3.435%** |

Read the last two rows against each other. On a lifetime basis, 2014 (8.25%) looks nearly twice as safe as 2012 (15.62%). On a twelve-month basis they are almost identical (3.44% vs 3.74%). The lifetime difference is **entirely an artefact of censoring**. The twelve-month figures are comparable because every vintage was given the same clock.

> **This is the entire argument for a fixed performance window,** and it is the hinge on which the whole project turns. Chapter 3 and Stage 1 make it operational.

⚠️ **HONESTY NOTE.** The 12-month rates are uncensored *here* only because the snapshot (Jan 2016) sits thirteen months past the last origination (Dec 2014). Push originations into 2015 and censoring returns even for the 12-month window. The property comes from this dataset's geometry, not from the method itself.

---

## Chapter 3 — The three parameters (and the fourth)

Every credit loss calculation in every framework in the world decomposes into the same three quantities. Learn these and you have the skeleton of the entire discipline.

### 3.1 PD — Probability of Default

**Definition.** The probability that a given borrower will default within a specified time horizon.

The horizon is not optional decoration; it *is* the definition. "PD" with no horizon is meaningless. The two horizons that matter:

- **12-month PD** — probability of default within the next twelve months. This is what Basel's capital formula consumes, and what IFRS 9 Stage 1 consumes.
- **Lifetime PD** — probability of default at any point over the loan's entire remaining contractual life. This is what IFRS 9 Stage 2 and Stage 3 consume, and what CECL consumes for everything.

📘 **CONCEPT — why 12 months specifically?**

Basel's capital framework is built on a one-year horizon by construction: it asks "how bad could losses get over the next year, at 99.9% confidence?" and sizes capital to survive that. The input to that question must therefore be a one-year default probability.

IFRS 9 independently arrived at the same number for its Stage 1 provision: healthy loans carry a provision equal to the losses expected from defaults occurring in the next twelve months.

Two frameworks, same input. This is why a lifetime "ever defaulted" flag — which is what naive tutorials build — **cannot feed either framework**. It is the wrong quantity. Fixing this was Stage 1 of the project, and it is the reason Stages 7 and 8 were possible at all.

**Point-in-time versus through-the-cycle.** A **point-in-time (PIT)** PD reflects current economic conditions — it rises in recessions. A **through-the-cycle (TTC)** PD averages across an economic cycle and is deliberately stable. Basel IRB generally wants something closer to TTC (capital should not swing wildly with the cycle); IFRS 9 explicitly wants PIT with forward-looking adjustment (provisions *should* respond to conditions). Knowing which you have built, and being able to say so, is a standard interview probe.

### 3.2 LGD — Loss Given Default

**Definition.** Given that a loan has defaulted, the fraction of the exposure that is ultimately lost, after all recoveries and collection costs.

$$\text{LGD} = 1 - \text{Recovery Rate} = \frac{\text{Loss}}{\text{Exposure at Default}}$$

Three things to know:

**It is measured only on defaulted loans.** A loan that never defaulted has no loss to measure. So LGD trains on a much smaller population than PD — here, 50,968 defaulted loans rather than all 466,285.

**The denominator matters enormously.** LGD is loss divided by **exposure at default**, not by the original loan amount. If a borrower took ₹10,000, repaid ₹2,000 in normal instalments, then defaulted owing ₹8,000, and the bank recovered ₹500 — the loss is ₹7,500 and the LGD is 7,500 ÷ 8,000 = **93.75%**. It is *not* 7,500 ÷ 10,000 = 75%. The ₹2,000 already repaid was never at risk; counting it as "recovery" flatters LGD and understates loss. This exact error was made and corrected during the build — see Stage 5.2.

**Secured versus unsecured is the whole story.** A defaulted mortgage recovers most of its value by selling the house — LGD might be 20–30%. A defaulted unsecured personal loan has no collateral to seize; the bank chases the borrower and usually gets little.

📊 **WHAT ACTUALLY HAPPENED:** mean LGD on this unsecured book was **93.01%**, median **100%**, with **52.18%** of all defaults being total losses (LGD exactly 1.0). That is brutal, and it is exactly why unsecured personal loans carry 15%+ interest rates: the lender must earn enough on the performing loans to cover near-total losses on the ones that fail.

**Downturn LGD.** Basel requires that capital be computed using LGD estimated for **economic downturn conditions**, not the long-run average. The reason is a correlation argument: in a recession, defaults rise *and* recoveries fall at the same time — collateral is worth less, collections are harder, more borrowers are chasing the same buyers. Using average LGD would understate exactly the scenario that capital exists to cover. "Which LGD goes into the capital formula?" is a classic interview trap; the answer is **downturn, not average**.

### 3.3 EAD — Exposure at Default

**Definition.** The amount expected to be outstanding and owed to the bank at the moment default occurs.

For a **term loan** — a fixed-instalment personal loan or auto loan — this is easy. The borrower cannot re-borrow; the balance only goes down. EAD is essentially the outstanding principal:

$$\text{EAD} = \text{Funded Amount} - \text{Principal Repaid}$$

For a **revolving facility** — a credit card, an overdraft, a line of credit — this is hard and interesting. The borrower has a *limit* and a *drawn balance*, and a distressed borrower tends to draw down more of their available limit in the months before defaulting. Exposure at default can therefore be substantially **higher** than the balance today.

📊 **WHAT ACTUALLY HAPPENED:** the average EAD ratio (fraction of the original loan still outstanding at default) was around 0.7–0.85, and it varied in two explainable ways:
- **60-month loans showed higher EAD ratios than 36-month loans** (~0.82 vs ~0.66). Longer loans amortise more slowly, so more is still owed when they go bad. This is a real reason longer terms are riskier, beyond simply having more time to fail.
- **EAD ratio rose across grades A→G** (Grade A defaulters had paid down ~39% of principal; Grade G defaulters only ~15%). Riskier borrowers default *earlier*, before amortising much. This is a **double penalty** — higher PD *and* higher EAD — which compounds in the expected loss calculation.

### 3.4 CCF — Credit Conversion Factor

**Definition.** For a revolving facility, the fraction of the currently **undrawn** limit that converts into drawn exposure by the time of default.

$$\text{EAD}_{\text{revolving}} = \text{Drawn Balance} + \text{CCF} \times \text{Undrawn Limit}$$

A worked example. A credit card has a ₹100,000 limit with ₹30,000 currently drawn, so ₹70,000 undrawn. If the estimated CCF is 0.37, then:

$$\text{EAD} = 30{,}000 + 0.37 \times 70{,}000 = 30{,}000 + 25{,}900 = ₹55{,}900$$

The bank's exposure is nearly double today's balance, because a distressed borrower will draw down before failing.

⚠️ **HONESTY NOTE — the project's largest scoping limitation.** Lending Club loans are **term loans**. There is no credit limit, no undrawn amount, and therefore nothing to convert. A CCF model cannot be honestly fitted on this data. Claiming one would be an overclaim that a credit interviewer would catch in seconds.

What the build did instead: it constructed a **clearly labelled synthetic revolving sub-portfolio** to demonstrate the CCF methodology — the simulation, the realised-CCF calculation, a fitted model, and a worked EAD example — with every output file prefixed `SYNTHETIC_` and every table carrying a header declaring it a demonstration. This proves the capability without pretending the data supported it. That distinction is a **credibility signal**, not a weakness. It is the difference between a candidate who claims a CCF model and one who says: *"here is real EAD for term loans, and here is a CCF framework I built to demonstrate the revolving methodology — the data could not support fitting it for real, and here is exactly why."*

### 3.5 The consistency rule that binds them together

LGD is *loss ÷ EAD*. Expected loss is *PD × LGD × EAD*. If the EAD sitting inside the LGD denominator is computed differently from the EAD you later multiply by, the terms do not cancel correctly and expected loss is simply wrong.

The build therefore used the **identical** definition — `funded_amnt − total_rec_prncp`, floored at zero — in both `lgd_data.py` and `ead_model.py`, with a code comment in each pointing at the other. This is not fussiness; it is what makes Stage 7 arithmetically valid.

---

## Chapter 4 — Expected loss versus unexpected loss

### 4.1 The central equation

$$\boxed{\text{Expected Loss} = \text{PD} \times \text{LGD} \times \text{EAD}}$$

Read it as a sentence: *the chance it goes bad, times the fraction you lose when it does, times how much is on the table.*

A worked example, using this project's portfolio averages:
- PD = 3.45%
- LGD = 93.39%
- EAD = ₹7,752 (mean per loan)

$$\text{EL per loan} = 0.0345 \times 0.9339 \times 7{,}752 = ₹249.8$$

Across 235,628 loans, that aggregates to **₹58.67 million** of expected loss on a **₹1.83 billion** book — an expected loss rate of **3.21% of exposure**.

📊 **WHAT ACTUALLY HAPPENED — expected loss by rating grade (2014 out-of-time portfolio):**

| Grade | Loans | Total EAD | Total EL | EL % of EAD | Mean PD | Mean LGD |
|---|---|---|---|---|---|---|
| A | 36,108 | ₹221,209,241 | ₹2,138,197 | 0.97% | 1.10% | 93.44% |
| B | 61,935 | ₹389,715,719 | ₹6,793,881 | 1.74% | 2.05% | 93.57% |
| C | 66,565 | ₹508,147,784 | ₹15,101,496 | 2.97% | 3.54% | 93.68% |
| D | 42,991 | ₹403,007,109 | ₹17,029,659 | 4.23% | 5.05% | 93.32% |
| E | 20,121 | ₹215,856,557 | ₹11,436,735 | 5.30% | 6.31% | 92.52% |
| F | 6,223 | ₹66,470,619 | ₹4,591,984 | 6.91% | 8.35% | 92.03% |
| G | 1,685 | ₹22,165,613 | ₹1,574,216 | 7.10% | 8.23% | 92.07% |
| **Total** | **235,628** | **₹1,826,572,642** | **₹58,666,169** | **3.21%** | **3.45%** | **93.39%** |

Two things to read out of that table, because they are exactly what an interviewer will ask.

**The gradient is clean and monotonic** — 0.97% to 7.10%. That is the model doing its job: it sorts risk, and the sorting is validated by actual outcomes.

**The gradient is driven entirely by PD, not LGD.** PD moves 1.10% → 8.35% (a factor of 7.6). LGD barely moves at all — 93.44% → 92.07%. For unsecured lending, LGD is essentially a constant and PD does all the discriminating. This is a structural property of the asset class: there is no collateral whose value varies by borrower quality, so loss severity is roughly uniform.

### 4.2 Unexpected loss and why capital exists

Expected loss is an average, and averages are not what kill banks. Consider a bank that expects 3.4% defaults, prices for it, provisions for it, and is doing everything right. Then 2008 arrives and the rate is 9%. The additional 5.6 percentage points was not priced, not provisioned, and not expected. That is **unexpected loss**.

You cannot charge for unexpected loss in the interest rate, because you do not know which year it will arrive in. Instead, the regulator requires the bank's owners to keep a permanent buffer of their own money in the business, large enough to absorb it.

📘 **CONCEPT — the loss distribution.** Imagine simulating next year a thousand times. Most years the portfolio loses close to 3.2%. Some years it loses 2%. A few years it loses 8%, and one year in a thousand it loses something extreme.

Plot the frequency of each outcome and you get a right-skewed **loss distribution**:

- The **mean** of that distribution is expected loss → covered by provisions and pricing.
- The **99.9th percentile** is the loss in a one-in-a-thousand-year bad year.
- The **gap between them** is unexpected loss → covered by capital.

Basel's IRB formula is nothing more than a closed-form way of computing that 99.9th percentile from PD and LGD. Chapter 6 derives it.

### 4.3 The two-track picture

Everything from here forks into two tracks that share the same three inputs:

```
                    PD, LGD, EAD
                    /           \
                   /             \
      PD × LGD × EAD          Basel IRB formula
              |                       |
      EXPECTED LOSS            CAPITAL REQUIREMENT K
              |                       |
      → accounting provision    → RWA = K × 12.5 × EAD
        (IFRS 9 / Ind AS 109)    → minimum capital = 8% of RWA
              |                       |
      reduces reported PROFIT   constrains LENDING CAPACITY
```

Stage 7 builds the right-hand track. Stage 8 builds the left-hand one, elaborated with IFRS 9's staging logic.
---

## Chapter 5 — Basel: what it is and why it exists

### 5.1 A short history, because it explains the design

Banks fail. When they fail they take depositors' money, other banks, and often the economy with them. After a series of international banking crises in the 1970s, central bank governors of the major economies formed the **Basel Committee on Banking Supervision (BCBS)**, headquartered at the Bank for International Settlements in Basel, Switzerland.

The BCBS has no legal power. It publishes standards; national regulators (the RBI in India, the Fed and OCC in the US, the PRA in the UK) then write them into binding local rules. This is why you hear "Basel III as implemented by RBI" — the framework is international, the enforcement is national.

**Basel I (1988)** was crude: assets were sorted into a handful of buckets with fixed risk weights (0% for government bonds, 50% for mortgages, 100% for corporate loans), and banks held 8% capital against the weighted total. It was simple and it worked, but it was blind to actual risk — a loan to a rock-solid company and a loan to a failing one carried identical capital.

**Basel II (2004)** introduced **risk sensitivity**. Banks with sufficient data and modelling capability were permitted to use their *own* estimates of PD, LGD, and EAD, plugged into a supervisory formula, to determine capital. This is the **Internal Ratings-Based (IRB)** approach, and it is the reason credit risk analytics became a profession.

**Basel III (2010–2017)**, written after the 2008 crisis, raised the quantity and quality of required capital, added liquidity requirements, added a leverage ratio backstop, and — in the 2017 "finalisation" package often called the Basel III endgame — constrained IRB modelling with input floors and an output floor, because supervisors concluded that banks had been using internal models to shave capital too aggressively.

The two documents that matter for this project, and which were indexed into the AI analyst's knowledge base in Stage 11:
- **bcbs128** — *International Convergence of Capital Measurement and Capital Standards* (Basel II, comprehensive version, 2006). Contains the PD/LGD/EAD definitions and the original retail risk-weight functions.
- **d424** — *Basel III: Finalising post-crisis reforms* (2017). Contains the current calibrations, floors, and the revised standardised approach.

### 5.2 The three pillars

Basel is organised into three pillars, and knowing the structure is worth a sentence in an interview.

**Pillar 1 — Minimum capital requirements.** The formulas. Credit risk, market risk, operational risk. This is the quantitative core and what this project builds.

**Pillar 2 — Supervisory review.** The regulator's own assessment of whether Pillar 1 was enough for *this particular bank*, including risks Pillar 1 does not capture (concentration risk, interest rate risk in the banking book, stress testing). The regulator can require more capital than the formula produces.

**Pillar 3 — Market discipline.** Mandatory public disclosure, so investors and counterparties can assess the bank themselves.

### 5.3 Risk-weighted assets and the capital ratio

The unit of account in Basel is not the loan amount; it is **risk-weighted assets (RWA)**.

$$\text{RWA} = \text{Risk Weight} \times \text{EAD}$$

A ₹100 loan with a 75% risk weight contributes ₹75 of RWA. The bank must then hold capital equal to a percentage of total RWA:

| Requirement | Minimum |
|---|---|
| Common Equity Tier 1 (CET1) | 4.5% of RWA |
| Tier 1 capital | 6.0% of RWA |
| Total capital | 8.0% of RWA |

Plus buffers on top: a capital conservation buffer (2.5%), a countercyclical buffer (0–2.5%, set by national regulators), and surcharges for systemically important banks. India's RBI adds its own calibration; Indian minimums have historically run above the Basel floor.

**Why the number 12.5 appears everywhere.** The IRB formula produces a **capital requirement K**, expressed as a fraction of EAD. To convert that into an RWA figure consistent with the 8% ratio, you multiply by 1/0.08 = **12.5**:

$$\text{RWA} = K \times 12.5 \times \text{EAD} \qquad\text{and equivalently}\qquad \text{Risk Weight} = K \times 12.5$$

So if K = 0.06, the risk weight is 75%, and 8% of the resulting RWA gives back exactly K × EAD. The 12.5 is not a modelling constant — it is a unit conversion.

### 5.4 Standardised versus IRB

**The Standardised Approach (SA)** assigns risk weights from a regulatory table, based on exposure class and (for some classes) external credit ratings. No modelling. For unrated retail exposures that meet the regulatory retail criteria, the risk weight is a flat **75%**.

$$\text{RWA}_{\text{SA}} = 0.75 \times \text{EAD}$$

**The Internal Ratings-Based Approach (IRB)** lets the bank estimate risk parameters itself and feeds them into the supervisory formula. It comes in two flavours:

- **Foundation IRB (F-IRB)** — the bank estimates PD; the supervisor prescribes LGD and EAD.
- **Advanced IRB (A-IRB)** — the bank estimates PD, LGD *and* EAD.

**For retail exposures there is no foundation option** — retail IRB is always advanced. The bank must estimate all three. This is precisely why a retail CPRA team exists and why the job description lists PD, LGD, and CCF estimation as responsibility number one.

### 5.5 The counterintuitive finding this project produced

📊 **WHAT ACTUALLY HAPPENED — IRB versus Standardised on this portfolio:**

| Approach | Total RWA | Average risk weight | Minimum capital (8%) |
|---|---|---|---|
| Standardised (flat 75%) | ₹1,369,929,482 | 75.00% | ₹109.6M |
| **IRB (Other Retail)** | **₹2,294,666,891** | **125.63%** | **₹183.6M** |
| **Difference** | **+₹924.7M (+67%)** | **+50.6 pp** | **+₹74.0M** |

The IRB approach produced **67% more RWA** than the flat standardised weight.

This is counterintuitive and it is the strongest single finding in the project. The naive assumption — and the one most banks operate on — is that IRB *saves* capital, because that is the commercial incentive for adopting it. Here it costs substantially more.

**The mechanism, stated precisely.** IRB is risk-sensitive: it reads the *actual* parameters of this book — mean PD 3.45% and mean LGD **93.4%** — and prices capital against them. The 93% LGD is the dominant driver. The standardised 75% is one-size-fits-all, calibrated for a diversified retail book with mixed secured and unsecured exposures and typical recovery rates. Applied to a pure unsecured book with near-total loss severity, it is **lenient**.

The general lesson, which is the sentence to have ready: **IRB rewards genuinely safe books with lower capital and penalises genuinely risky ones. Standardised treats everyone the same.** A bank running this product on the standardised approach is structurally undercapitalised relative to its economic risk.

---

## Chapter 6 — The Basel IRB supervisory formula, derived

This is the mathematical core of Pillar 1 credit risk. It looks intimidating and it is not. Every term has a plain-English job.

### 6.1 The idea in one paragraph

We want the loss in a one-in-a-thousand bad year. Imagine every borrower's fate is driven partly by a single shared economic factor (the state of the economy) and partly by their own idiosyncratic luck. In a bad economy, everyone's default probability rises together. So: push the shared factor to its 99.9th-percentile worst value, recompute each borrower's default probability *conditional* on that terrible economy, and multiply by LGD. The difference between that stressed loss and the expected loss is the capital you need.

That is the **Asymptotic Single Risk Factor (ASRF)** model. The entire Basel formula is that paragraph written in symbols.

### 6.2 The notation

- $N(x)$ — the **standard normal cumulative distribution function**. Feed it a number, get back the probability that a standard normal random variable is below it. $N(0) = 0.5$, $N(1.96) = 0.975$.
- $G(p)$ — the **inverse** of $N$, also called the quantile or percent-point function. Feed it a probability, get back the threshold. $G(0.5) = 0$, $G(0.999) = 3.0902$.
- $R$ — the **asset correlation**. How much borrowers' fortunes move together. Prescribed by the supervisor, not estimated by the bank.
- $\text{PD}$, $\text{LGD}$ — as defined in Chapter 3.

### 6.3 Step 1 — the correlation

For **"Other Retail"** exposures (personal instalment loans, auto loans — everything retail that is not a mortgage and not a qualifying revolving facility):

$$R = 0.03 \cdot \frac{1 - e^{-35 \cdot \text{PD}}}{1 - e^{-35}} + 0.16 \cdot \left(1 - \frac{1 - e^{-35 \cdot \text{PD}}}{1 - e^{-35}}\right)$$

Let $w = \dfrac{1 - e^{-35\cdot\text{PD}}}{1 - e^{-35}}$. Then simply $R = 0.03w + 0.16(1-w)$ — a weighted blend of 0.03 and 0.16.

Since $e^{-35} \approx 6.3 \times 10^{-16}$, the denominator is essentially 1, so $w \approx 1 - e^{-35\cdot\text{PD}}$.

- At **PD → 0**: $w → 0$, so $R → 0.16$ (the maximum).
- At **PD → 1**: $w → 1$, so $R → 0.03$ (the minimum).

📘 **CONCEPT — why does correlation *fall* as PD rises?** This surprises people. The supervisory logic: a borrower who is already highly likely to default is being driven by their own personal circumstances — they are in trouble regardless of the economy. A borrower who is very safe will only default if something systemic goes wrong. So high-PD borrowers are *more idiosyncratic* and low-PD borrowers are *more systematic*. Lower correlation means less capital, because losses are less likely to arrive all at once.

**The other retail curves.** Basel defines three retail sub-classes with different correlations:

| Sub-class | Correlation | Examples |
|---|---|---|
| **Residential mortgages** | Fixed **0.15** | Home loans |
| **Qualifying Revolving Retail (QRRE)** | Fixed **0.04** | Credit cards, revolving facilities meeting specific criteria |
| **Other Retail** | PD-dependent, **0.03 → 0.16** | Personal loans, auto loans, everything else |

🔴 **ERROR — this distinction caused a real test failure during the build.** See Stage 7.4 in Part IV. The short version: reference values of K ≈ 0.0286 at PD=0.01 and R ≈ 0.0356 were supplied as a verification benchmark, but those are **QRRE** numbers (flat R = 0.04), while the code correctly implemented the **Other Retail** curve, which gives R = 0.1216 at PD = 0.01 — roughly 3.4× higher. Three of four reference tests failed. The code was right; the benchmark was wrong. Lending Club loans are term instalment loans, which are unambiguously Other Retail. **The test was fixed, not the formula.**

Hand-verification at PD = 0.01, so you can reproduce it:

$$w = \frac{1 - e^{-0.35}}{1 - e^{-35}} = \frac{1 - 0.70469}{1} = 0.29531$$
$$R = 0.03(0.29531) + 0.16(0.70469) = 0.008859 + 0.112751 = \mathbf{0.12161}$$

### 6.4 Step 2 — the conditional (stressed) default probability

$$\text{PD}_{\text{stressed}} = N\!\left( \frac{G(\text{PD}) + \sqrt{R} \cdot G(0.999)}{\sqrt{1-R}} \right)$$

Read it in three moves:

1. $G(\text{PD})$ converts the default probability into a **default threshold** on a standard normal scale. If PD = 3.45%, then $G(0.0345) = -1.818$: a borrower defaults when their latent creditworthiness falls below −1.818.
2. $\sqrt{R} \cdot G(0.999)$ is the **economic shock**. $G(0.999) = 3.0902$ is the one-in-a-thousand bad outcome of the shared factor; $\sqrt{R}$ scales it by how exposed this borrower is to that shared factor.
3. Dividing by $\sqrt{1-R}$ renormalises for the idiosyncratic part, and $N(\cdot)$ converts back into a probability.

The result: the default rate you would observe in a 99.9th-percentile bad year.

### 6.5 Step 3 — the capital requirement K

$$K = \text{LGD} \cdot \text{PD}_{\text{stressed}} - \text{PD} \cdot \text{LGD} = \text{LGD}\left(\text{PD}_{\text{stressed}} - \text{PD}\right)$$

**Stressed loss minus expected loss.** That subtraction is the entire conceptual payload of the formula: capital covers only the *unexpected* part, because the expected part is already handled by provisions and pricing. If you forget the subtraction, you double-count.

For corporate exposures there is an additional **maturity adjustment** term, because a longer-dated corporate loan can suffer credit-quality migration losses before default. **Retail exposures have no maturity adjustment** — retail IRB omits it entirely. That is a small, precise fact that impresses when produced at the right moment.

### 6.6 Step 4 — RWA and risk weight

$$\text{RWA} = K \times 12.5 \times \text{EAD} \qquad \text{Risk Weight} = K \times 12.5$$

### 6.7 Floors

- **PD floor: 0.03%** (0.0003). No exposure may be treated as safer than three basis points.
- **LGD:** capped at 1.0 in the implementation; Basel III finalisation also introduced input floors for LGD by exposure type.
- For **defaulted exposures**, K is computed differently — broadly as the excess of downturn LGD over the bank's best estimate of expected loss, floored at zero.

### 6.8 The complete worked example

Take PD = 1%, LGD = 45%, EAD = ₹100,000, Other Retail.

| Step | Computation | Result |
|---|---|---|
| Correlation | $0.03(0.29531) + 0.16(0.70469)$ | $R = 0.12161$ |
| $G(\text{PD})$ | $G(0.01)$ | $-2.32635$ |
| $G(0.999)$ | — | $3.09023$ |
| $\sqrt{R}$ | $\sqrt{0.12161}$ | $0.34873$ |
| $\sqrt{1-R}$ | $\sqrt{0.87839}$ | $0.93722$ |
| Numerator | $-2.32635 + 0.34873 \times 3.09023$ | $-1.24887$ |
| Divide | $-1.24887 / 0.93722$ | $-1.33254$ |
| $\text{PD}_{\text{stressed}}$ | $N(-1.33254)$ | $0.09135$ |
| $K$ | $0.45 \times (0.09135 - 0.01)$ | $\mathbf{0.03661}$ |
| Risk weight | $0.03661 \times 12.5$ | $\mathbf{45.8\%}$ |
| RWA | $0.03661 \times 12.5 \times 100{,}000$ | **₹45,760** |
| Capital at 8% | $0.08 \times 45{,}760$ | **₹3,661** |

Note the sanity check: capital = K × EAD = 0.03661 × 100,000 = ₹3,661. The 12.5 and the 8% cancel exactly, as they must.

📊 **WHAT ACTUALLY HAPPENED — why every grade in this project showed high risk weights.** Even Grade A, with PD ≈ 1.1%, produced a risk weight near 94%. Substitute LGD = 0.934 instead of 0.45 into the example above and K roughly doubles. The high risk weights are entirely attributable to the 93% LGD, and they are correct.

### 6.9 Downturn LGD in practice

Basel requires downturn LGD for capital. A real bank derives it empirically from recovery data observed during recession windows (2008–09, for instance).

This project used a documented **supervisory proxy**:

$$\text{LGD}_{\text{downturn}} = \min\left(1.0,\ \max(\text{LGD}, \text{floor}) + 0.08\right)$$

An 8 percentage-point add-on, capped at 1.0. Because the average LGD was already 93%, most loans hit the 1.0 cap, so the capital increase was modest. **The size of the change was never the point** — the point was demonstrating the *rule* that capital uses downturn LGD rather than average LGD, and documenting honestly that the add-on is a proxy rather than an empirical estimate.

📊 The downturn recomputation raised total RWA by approximately **₹159.25 million**, lifting the average portfolio risk weight from 125.63% to **134.35%** and increasing minimum capital by roughly **₹12.7 million (+6.94%)**.

---

## Chapter 7 — IFRS 9 and Ind AS 109: expected credit loss

### 7.1 The problem IFRS 9 was written to solve

Before 2018, accounting for loan losses used an **incurred loss** model: a bank could only provision once there was objective evidence that a loss had already occurred. In practice this meant provisions were tiny going into the 2008 crisis and then exploded afterwards — the accounting recognised losses long after the risk had built up. Regulators and standard-setters called this **"too little, too late."**

**IFRS 9 Financial Instruments** (effective 2018 globally; adopted in India as **Ind AS 109**) replaced it with an **expected credit loss (ECL)** model. From the moment a loan is originated, a bank must recognise a provision for losses it *expects*, forward-looking, before any evidence of impairment exists.

### 7.2 The three stages

The organising idea of IFRS 9 impairment is **staging**, and it is driven by *change in credit risk since origination* — not by absolute risk level.

| Stage | Condition | Provision | Interest recognised on |
|---|---|---|---|
| **Stage 1** | Performing; no significant deterioration since origination | **12-month ECL** | Gross carrying amount |
| **Stage 2** | Significant Increase in Credit Risk (SICR) since origination, but not credit-impaired | **Lifetime ECL** | Gross carrying amount |
| **Stage 3** | Credit-impaired (defaulted) | **Lifetime ECL** | **Net** carrying amount (gross minus provision) |

📘 **CONCEPT — the key subtlety, which is a standard interview question.** Staging is **relative to origination**, not absolute. A borrower who was risky when you lent to them and is *still* the same risk stays in Stage 1 — you knew what you were buying and you priced it. A borrower who was safe at origination and whose risk has since **doubled** moves to Stage 2, even if their absolute PD is still lower than the first borrower's. IFRS 9 is measuring *deterioration*, not *danger*.

**Why the provision jumps so much at Stage 2.** Nothing about the loan's contractual terms changed. The horizon changed — from twelve months to the entire remaining life. On this portfolio, lifetime PD ran roughly **3.1× the 12-month PD**, so the provision multiplies by roughly that factor the instant a loan trips SICR. That cliff is deliberate: it forces banks to recognise deterioration early and visibly.

### 7.3 SICR — Significant Increase in Credit Risk

IFRS 9 does not prescribe a SICR test; it requires one and lets banks design it. Standard industry practice, and what this project implemented, is a multi-limb test:

**(a) Quantitative / relative.** Current lifetime (or 12-month, as a proxy) PD compared to the PD expected at origination for that point in the loan's life. Trigger if the ratio exceeds a threshold.

**(b) Quantitative / absolute.** A backstop on the absolute level, so extremely risky loans are captured even if the relative test does not fire.

**(c) The 30-DPD rebuttable presumption.** IFRS 9 contains an explicit presumption that credit risk has increased significantly once a loan is **more than 30 days past due**. A bank may rebut this with evidence, but must otherwise apply it. This is a hard backstop that no model can override.

**(d) Qualitative triggers.** Watchlist status, forbearance, restructuring.

📊 **WHAT ACTUALLY HAPPENED — the SICR configuration used** (`config/ifrs9.yaml`):

```yaml
sicr_relative_threshold: 2.0      # current 12m PD >= 2.0 x origination PD
sicr_absolute_pd: 0.06            # OR current 12m PD > 6.0%
dpd_backstop_days: 30             # OR 30+ DPD forces Stage 2
```

⚠️ **HONESTY NOTE.** The dataset has no per-loan PD at origination — only a single snapshot. Origination PD was therefore **proxied by the grade-level average PD at issue**. This is a documented approximation. A real implementation would store the PD assigned at underwriting for every loan and compare against it directly.

📊 Resulting staging distribution: approximately **80% Stage 1, 11% Stage 2, 8% Stage 3** by loan count. Stages 2 and 3 together were 19% of loans but **22% of exposure** — risk concentrates in the deteriorated buckets, which is exactly the concentration IFRS 9 staging is designed to surface early.

### 7.4 Computing ECL

Per loan, by stage:

$$\text{ECL}_{\text{Stage 1}} = \text{PD}_{12m} \times \text{LGD} \times \text{EAD}$$
$$\text{ECL}_{\text{Stage 2}} = \text{PD}_{\text{lifetime}} \times \text{LGD} \times \text{EAD}$$
$$\text{ECL}_{\text{Stage 3}} = 1.0 \times \text{LGD} \times \text{EAD} \quad (\text{PD} = 1)$$

Then **discounting**. IFRS 9 requires ECL to be a present value, discounted at the **effective interest rate (EIR)** — the rate that exactly discounts the loan's expected cash flows to its carrying amount. Losses expected in three years are worth less today than losses expected next month.

⚠️ **HONESTY NOTE.** The build used the contractual `int_rate` as an EIR proxy and discounted by the average expected time-to-default drawn from the term structure, rather than performing a full cashflow-level EIR computation. This is documented in the limitations register as a **simplified EIR discounting**.

### 7.5 Lifetime PD from the seasoning curve

Basel only ever needed a 12-month PD. IFRS 9 Stage 2 needs the probability of default over the loan's whole remaining life. This is the one genuinely new quantity the accounting framework demands.

📘 **CONCEPT — discrete-time hazard.** The **hazard** at month $m$ is the probability of defaulting *in* month $m$, given survival to the start of it:

$$h(m) = \frac{\text{defaults occurring in month } m}{\text{loans still alive at the start of month } m}$$

Chain the survival probabilities:

$$S(m) = \prod_{k=1}^{m} \left(1 - h(k)\right) \qquad\qquad \text{Cumulative PD}(m) = 1 - S(m)$$

That is a **life table** — the same mathematics an actuary uses for mortality, applied to loans.

📊 **WHAT ACTUALLY HAPPENED — the portfolio lifetime PD term structure:**

| Month | Loans at risk | Defaults | Monthly hazard | Survival | Cumulative PD |
|---|---|---|---|---|---|
| 6 | 464,326 | 1,305 | 0.002811 | 0.993000 | **0.7000%** |
| **12** | 452,806 | 2,539 | 0.005607 | 0.965648 | **3.4352%** |
| 18 | 437,211 | 2,188 | 0.005004 | 0.932955 | **6.7045%** |
| 24 | 426,453 | 1,304 | 0.003058 | 0.911779 | **8.8221%** |
| 36 | 417,002 | 309 | 0.000741 | 0.893644 | **10.6356%** |
| 48 | 415,576 | 36 | 0.000087 | 0.891172 | **10.8828%** |
| 60 | 415,331 | 2 | 0.000005 | 0.890719 | **10.9281%** |

✅ **THE CRITICAL SANITY CHECK.** Cumulative PD at month 12 = **3.4352%**, which matches the independently-computed Stage 1 twelve-month default rate of **3.435%** to four decimal places. Two entirely different calculations agreeing to that precision means the hazard curve is constructed correctly and everything downstream rests on solid ground. When you build a term structure, this is the check to run before anything else.

**The headline multiple:** 36-month lifetime PD (10.6356%) ÷ 12-month PD (3.4352%) = **3.096×**. Peak monthly hazard falls between months 10 and 16, topping out at 0.6335% in month 14. Beyond month 36 the hazard collapses and the curve asymptotes to the full-life default rate of 10.93%.

**Scaling to individual loans.** The portfolio curve gives the *shape* of default timing. Each loan has its own *level* (its model PD). The build scaled multiplicatively so that each loan's curve passes through its own 12-month PD at month 12, then read the cumulative PD at that loan's remaining term. Remaining term = original term minus months elapsed since issue as of the reporting date, floored at 1 and capped at the original term.

### 7.6 Forward-looking macroeconomic scenarios

IFRS 9 explicitly forbids a single point estimate. The reported provision must be a **probability-weighted** average across multiple economic scenarios. This is what puts the "expected" into expected credit loss doing real work — you are provisioning for a recession that has not happened yet, weighted by how likely you think it is.

📊 **WHAT ACTUALLY HAPPENED** (`config/macro_scenarios.yaml`):

| Scenario | PD multiplier | Weight |
|---|---|---|
| Baseline | 1.00 | 0.50 |
| Upside | 0.85 | 0.20 |
| Downside | 1.50 | 0.30 |

The probability-weighted ECL lands **above** the pure baseline, because the 30%-weighted downside outweighs the 20%-weighted upside. That asymmetry is by design — IFRS 9 is deliberately conservative in the forward-looking dimension.

⚠️ **HONESTY NOTE.** A real bank links these scenarios to published GDP, unemployment, and house price forecasts through a fitted satellite model that translates macro variables into PD shifts. This project used **direct PD multipliers** as a documented simplification, because it had no macro time series joined to the loan data.

---

## Chapter 8 — CECL, and why it always provisions more

### 8.1 The American standard

The United States did not adopt IFRS 9. FASB wrote its own standard: **Current Expected Credit Losses (CECL)**, ASU 2016-13, effective for large filers from 2020.

CECL agrees with IFRS 9 on the diagnosis (incurred loss was too little, too late) and disagrees on the cure.

### 8.2 The one difference that matters

**IFRS 9 has staging. CECL does not.**

Under CECL, **every** loan carries a **lifetime** expected credit loss provision from day one of origination. There is no Stage 1 relief, no 12-month bucket, no SICR test to design or defend.

| Dimension | IFRS 9 / Ind AS 109 | CECL |
|---|---|---|
| Staging | Three stages | None |
| Provision on a healthy new loan | 12-month ECL | **Lifetime ECL** |
| SICR test required | Yes | No |
| Discounting | At EIR, required | Permitted, various methods |
| Day-one provision | Small | **Large** |
| Complexity | Higher (staging machinery) | Lower conceptually, larger numbers |

### 8.3 The consequence, with this project's numbers

📊 **WHAT ACTUALLY HAPPENED — the three-framework comparison on the same ₹1.83B book:**

| Framework | Provision | Why |
|---|---|---|
| **Basel Expected Loss** | **₹58.67M** | 12-month horizon, forward-looking only, no Stage 3 impairment |
| **IFRS 9 ECL** | **₹278.48M** | 12m for Stage 1, lifetime for Stage 2, full impairment on Stage 3 (₹223.8M) |
| **CECL** | **₹327.47M** | Lifetime on everything from day one |

The ordering is always Basel EL < IFRS 9 < CECL, and each step has a clean reason:

**Why IFRS 9 exceeds Basel EL.** Three effects stacked. (1) IFRS 9 books the *full* loss on already-defaulted Stage 3 loans — ₹223.8M here — while Basel EL is purely forward-looking and does not. (2) IFRS 9 applies a *lifetime* horizon to Stage 2, while Basel is always 12-month. (3) IFRS 9 discounts at EIR.

**Why CECL exceeds IFRS 9.** No staging relief. On this book, the Stage 1 provision rose from **₹30.27M** under IFRS 9's 12-month treatment to **₹79.26M** under CECL's lifetime treatment for the same 189,633 performing loans — an extra **₹49M** of provision arising purely from the choice of accounting framework, with no change whatsoever to the loans.

⚠️ **HONESTY NOTE — the like-for-like comparison.** Comparing IFRS 9's *total* ECL to Basel EL is apples-to-oranges, because the IFRS 9 total is dominated by the ₹223.8M of already-defaulted Stage 3 loans that Basel EL does not count at all. The build therefore added `ecl_performing_only()` — IFRS 9 ECL restricted to Stage 1 + Stage 2 loans, which is the same population Basel EL covers. On that basis the two frameworks came out at roughly **₹54.7M (IFRS 9) versus ₹58.67M (Basel EL)** — very close. That near-equality is the real validation: it proves both engines are internally consistent and that the headline gap is purely staging and Stage 3 treatment, not a bug in one of them.

Being able to explain, with numbers, why the same portfolio provisions three different ways under three regimes is rare and it is genuinely valuable in an interview.

---

## Chapter 9 — Scorecards: WoE, IV, and points scaling

### 9.1 Why a scorecard and not a gradient-boosted tree

A gradient-boosted tree would score slightly better on this data. It was not used, and the reason is not ignorance.

A regulated retail PD model must be **explainable** to a regulator and a credit committee, **stable** over time, **auditable** line by line, and **documentable** in a model development pack. The industry-standard structure that delivers all four is the **Weight of Evidence scorecard**: bin every variable, replace each value with the WoE of its bin, fit a logistic regression on the WoE values, then linearly rescale the log-odds into a familiar points score.

The result is linear, monotonic, and fully inspectable. Every point a borrower gains or loses traces to one specific bin of one specific variable. That property is non-negotiable in regulated lending — it is what lets a bank answer "why was I declined?" and what lets a validator reproduce the model by hand.

In practice, banks often build a **challenger** ML model alongside the scorecard to measure how much predictive power the interpretability constraint costs. That is a legitimate next step, noted in this project's future-work section.

### 9.2 Binning

**Binning** (or **coarse classification**) means chopping each variable into a small number of bands.

For a **numeric** variable: start with many fine quantile bins (the build started with 20), then merge adjacent bins until two conditions hold — WoE is **monotonic** across bins, and every bin holds at least **5%** of rows.

For a **categorical** variable: each level is its own bin; levels holding under 5% of rows are merged into `OTHER`. **Monotonicity is not enforced on categoricals** — there is no natural ordering to `purpose` or `home_ownership`.

**Missing values always get their own bin.** This is one of the quiet superpowers of the approach: you never impute, never drop rows, and "missingness" becomes an honest, measurable risk signal in its own right. Sometimes not having a value *is* the information.

📘 **CONCEPT — why monotonicity matters to a regulator.** If higher income maps to lower risk in bins 1, 2, and 4 but *higher* risk in bin 3, you have a zigzag. It is almost always noise, it will not replicate out of time, and — decisively — you cannot defend it to a credit committee. "Why does the model penalise people earning ₹8–10 lakh but reward those earning ₹6–8 lakh and ₹10–12 lakh?" has no good answer. Merge until it is monotonic.

### 9.3 Weight of Evidence

For each bin:

$$\text{WoE} = \ln\left( \frac{\text{\% of all NON-defaulters in this bin}}{\text{\% of all defaulters in this bin}} \right)$$

- **Positive WoE** → this bin holds proportionally more good accounts → **safer** than portfolio average.
- **Negative WoE** → proportionally more defaulters → **riskier**.
- **WoE = 0** → exactly average.

The transformation does three things at once: it puts every variable — numeric, categorical, missing-riddled — onto **one common log-odds scale**; it **linearises** the relationship between the variable and risk (so a linear model is appropriate); and it makes **outliers harmless**, because an extreme value simply lands in the top bin.

**Laplace / continuity correction.** If a bin contains zero defaulters, the ratio is infinite and $\ln$ blows up. Adding 0.5 to each cell count before computing proportions prevents this. The build used this throughout.

### 9.4 Information Value

Summing WoE across a variable's bins, weighted by the difference in distributions, gives one number for the whole variable:

$$\text{IV} = \sum_{\text{bins}} \left( \%\text{good} - \%\text{bad} \right) \times \text{WoE}$$

The industry rule of thumb, used essentially unchanged across every bank:

| IV | Interpretation |
|---|---|
| < 0.02 | Useless — drop it |
| 0.02 – 0.10 | Weak |
| 0.10 – 0.30 | Medium — useful |
| 0.30 – 0.50 | Strong |
| **> 0.50** | **Suspiciously strong — check for leakage before celebrating** |

That last row is a genuine diagnostic. If `recoveries` had accidentally slipped into the feature set, its IV would have come back around 2.0 and given the game away instantly.

📊 **WHAT ACTUALLY HAPPENED — the IV finding that shaped the whole project.** Strip out `grade`, `sub_grade`, and `int_rate`, and the *strongest* remaining borrower-fundamental variable was `inq_last_6mths` at IV **0.076** — merely "weak". Income, DTI, and home ownership all landed in weak-to-useless territory. Meanwhile `grade` came in at IV **0.294** and `int_rate` at **0.277**.

The interpretation is the interesting part: **Lending Club had already priced most of the risk into `grade` and `int_rate`**. Those are not borrower facts; they are the *output of Lending Club's own risk model*, formed at origination. What remains for raw borrower attributes to explain is genuinely thin. This observation drove the Model A / Model B design in Stage 3.

### 9.5 The logistic regression

With every variable WoE-transformed, fit:

$$\ln\left(\frac{p}{1-p}\right) = \beta_0 + \beta_1 \text{WoE}_1 + \beta_2 \text{WoE}_2 + \cdots + \beta_k \text{WoE}_k$$

where $p$ is the probability of default.

📘 **CONCEPT — every coefficient should be negative.** High WoE means a *safer* bin. Higher predicted PD means *riskier*. So as WoE rises, predicted default must **fall** — a negative coefficient. A **positive** coefficient would say "safer borrowers default more," which is nonsensical and always indicates a broken bin, a data problem, or severe multicollinearity. Checking coefficient signs is the fastest smoke test on a fitted scorecard. Both models in this project came out fully negative.

The build used `statsmodels.Logit` rather than scikit-learn, deliberately — statsmodels returns standard errors, p-values, and Wald confidence intervals, which are exactly what a model validator will ask to see.

### 9.6 Points scaling

Banks do not hand a credit committee a probability of 0.0347. They hand them a **score** — 680, 720 — which humans can reason about. The conversion is a cosmetic linear transform of the log-odds, defined by three chosen constants:

- **Target points** (base score) — e.g. 600
- **Target odds** at that score — e.g. 50:1 (fifty goods per bad)
- **PDO** (Points to Double the Odds) — e.g. 20

$$\text{Factor} = \frac{\text{PDO}}{\ln 2} = \frac{20}{0.6931} = 28.8539$$
$$\text{Offset} = \text{Target Points} - \text{Factor} \times \ln(\text{Target Odds}) = 600 - 28.8539 \times \ln(50) = 600 - 112.877 = 487.1229$$

Per-bin points, with the intercept distributed evenly across the $m$ variables in the model:

$$\text{Base Points} = \frac{\text{Offset} - \text{Factor} \times \beta_0}{m}$$
$$\text{Points}_{\text{bin}} = \text{round}\left( \text{Base Points} + \text{Factor} \times \left(-\beta_j \times \text{WoE}_{\text{bin}}\right) \right)$$

A borrower's total score is simply the **sum of their bin points across all variables**.

📘 **CONCEPT — what the scaling does and does not do.** It changes **nothing** about the model. Not the ranking, not the probabilities, not the discrimination. It is a change of units, exactly like Celsius to Fahrenheit. What it buys is interpretability: "twenty points doubles your odds of being good" is a sentence a credit officer can use. That is the entire purpose.

### 9.7 Rating grades

The final step: cut the continuous score into a small number of **rating grades** — the bank's master scale — each with an observed default rate.

📊 **WHAT ACTUALLY HAPPENED — Model A rating grades (borrower fundamentals only):**

| Grade | Score min | Score max | Loans | Defaults | Observed default rate | Portfolio share |
|---|---|---|---|---|---|---|
| 1 (safest) | 605 | 629 | 21,671 | 263 | 1.21% | 11.74% |
| 2 | 598 | 604 | 22,485 | 390 | 1.73% | 12.19% |
| 3 | 593 | 597 | 21,786 | 476 | 2.18% | 11.81% |
| 4 | 588 | 592 | 23,621 | 633 | 2.68% | 12.80% |
| 5 | 583 | 587 | 24,493 | 815 | 3.33% | 13.27% |
| 6 | 578 | 582 | 21,698 | 867 | 4.00% | 11.76% |
| 7 | 570 | 577 | 24,729 | 1,197 | 4.84% | 13.40% |
| 8 (riskiest) | 503 | 569 | 24,042 | 1,688 | **7.02%** | 13.03% |

📊 **Model B rating grades (including grade and int_rate):**

| Grade | Score min | Score max | Loans | Defaults | Observed default rate | Portfolio share |
|---|---|---|---|---|---|---|
| 1 (safest) | 614 | 645 | 21,949 | 187 | **0.85%** | 11.89% |
| 2 | 604 | 613 | 22,695 | 292 | 1.29% | 12.30% |
| 3 | 596 | 603 | 24,410 | 467 | 1.91% | 13.23% |
| 4 | 590 | 595 | 20,170 | 517 | 2.56% | 10.93% |
| 5 | 583 | 589 | 23,468 | 759 | 3.23% | 12.72% |
| 6 | 575 | 582 | 25,365 | 1,068 | 4.21% | 13.75% |
| 7 | 566 | 574 | 23,210 | 1,236 | 5.33% | 12.58% |
| 8 (riskiest) | 524 | 565 | 23,258 | 1,803 | **7.75%** | 12.60% |

**Rank ordering holds strictly and monotonically in both.** This is the single most basic validation a scorecard must pass: every worse grade must actually default more than the grade above it. If it breaks anywhere, a bin needs merging.

Model B shows the wider spread — 0.85% to 7.75% versus Model A's 1.21% to 7.02% — which is better discrimination, and Chapter 10 and Stage 3 explain exactly why, and why it is not the unambiguous good news it looks like.
---

## Chapter 10 — Model validation: the three questions

A model that ranks borrowers is not automatically a good model. Validation asks three separate questions, and a model can pass one while catastrophically failing another. This chapter is the most directly interview-relevant in Part I, because "model validation" is what a Model Risk team does all day.

### 10.1 Question one — DISCRIMINATION: can it tell good from bad?

**AUC (Area Under the ROC Curve).** Take one random defaulter and one random non-defaulter. AUC is the probability that the model assigns a higher PD to the defaulter. 0.5 is a coin flip; 1.0 is perfect.

**Gini coefficient.** A linear rescaling of AUC that credit risk universally prefers:

$$\text{Gini} = 2 \times \text{AUC} - 1$$

0 is random, 1 is perfect. Retail PD models on out-of-time data typically land between **0.35 and 0.65**. Above roughly 0.75 on a retail book, **suspect leakage** — something in your features is telling you the answer.

**KS statistic (Kolmogorov–Smirnov).** The largest vertical gap between the cumulative distribution of defaulters and the cumulative distribution of non-defaulters, as you sweep the score. Interpreted as: *at the single best possible cut-off, how far apart are the two populations?* Retail models typically see 0.25–0.45. Reported here as a percentage.

📘 **CONCEPT — direction matters.** If you feed the metric a *probability of default* (higher = worse), you get the Gini. If you accidentally feed it a *credit score* (higher = better), you get the negative of it. A negative Gini almost always means a sign flip, not a broken model.

### 10.2 Question two — CALIBRATION: when it says 3%, do 3% default?

This is where models quietly fail, and it matters more than discrimination for regulatory purposes, because **Basel and IFRS 9 multiply by the PD**. A model that ranks perfectly but predicts 2% when the truth is 4% will make the bank hold roughly half the capital it should.

**Calibration table.** Bin predicted PD into deciles. For each decile, compare mean predicted PD against actual observed default rate. They should track closely.

**Hosmer–Lemeshow test.** The formal version of the same idea. Chi-square statistic comparing observed and expected defaults across deciles, converted to a p-value.

> **Read the p-value backwards from what you are used to.** A **high** p-value means "no evidence of miscalibration" — the model **passes**. A **low** p-value (< 0.05) means the observed and predicted differ more than chance allows — the model **fails**.

**Brier score.** Mean squared error of the probability forecasts. Lower is better; it blends discrimination and calibration into one number.

⚠️ **A caveat worth carrying.** Hosmer–Lemeshow is sensitive to sample size. On 235,628 loans, even a commercially trivial miscalibration will produce a tiny p-value. The honest read is always: look at the *calibration table* to judge the size of the error, and use HL to judge whether it is systematic. This is exactly what happened in Stage 4 — and note that even the *train* samples showed HL p-values around 0.001 despite being the fitting data, which is itself the sample-size effect at work.

### 10.3 Question three — STABILITY: does it still work next year?

**PSI (Population Stability Index).** Compares the distribution of the model *score* between the development sample and a later sample.

$$\text{PSI} = \sum_{\text{bins}} (\%_{\text{actual}} - \%_{\text{expected}}) \times \ln\left(\frac{\%_{\text{actual}}}{\%_{\text{expected}}}\right)$$

| PSI | Interpretation |
|---|---|
| < 0.10 | Stable — no action |
| 0.10 – 0.25 | Moderate shift — investigate |
| > 0.25 | Significant shift — model may need redevelopment |

**CSI (Characteristic Stability Index).** The identical calculation applied to each *input variable* individually rather than the output score.

📘 **CONCEPT — why you must compute both, and never only PSI.** This is the subtlest lesson in the whole project and it produced a real finding.

PSI looks at the *score*. If two input variables shift in ways that partially offset, or if the WoE `MISSING` bin quietly absorbs a change, the score distribution can look perfectly stable while the underlying population has lurched. Per-variable CSI is what exposes it.

📊 **WHAT ACTUALLY HAPPENED.** Score PSI came in around **0.01** — rock stable, apparently nothing to see. Per-variable CSI told a completely different story: `tot_cur_bal` and `total_rev_hi_lim` both showed CSI ≈ **3.96**, an enormous shift.

The cause: Lending Club did not collect those two bureau fields until late 2012. They are **100% missing** in the 2007–2011 development vintages and **>99% populated** by 2014. The WoE binner had put all the early rows in a single `MISSING` bin; at scoring time on 2014 data the loans suddenly landed in populated bins that the model had barely learned from. The score distribution absorbed it; the variable had not.

That structural shift was almost certainly what broke Model A's out-of-time calibration. The resolution — dropping both variables as data-collection artefacts rather than features — is Stage 4.3.

### 10.4 Out-of-time versus out-of-sample

**Out-of-sample** means a random hold-out from the same period as training. It tests for **overfitting**.

**Out-of-time (OOT)** means an entirely different time period — here, all of 2014, held out completely while the model was fitted on 2007–2013. It tests for **temporal robustness**, which is the thing that actually matters, because a deployed model runs on *future* borrowers, not on a random subset of past ones.

A model can pass out-of-sample beautifully and fail out-of-time. That is precisely what happened to Model A.

### 10.5 The complete validation results

📊 **WHAT ACTUALLY HAPPENED — the master validation table** (`outputs/tables/validation_summary.csv`, after dropping the two unstable variables):

| Model | Sample | ROC-AUC | Gini | KS | Brier | Hosmer–Lemeshow p |
|---|---|---|---|---|---|---|
| model_a | train | 0.6507 | 0.3013 | 21.93% | 0.03278 | 0.00115 |
| model_a | test | 0.6485 | 0.2969 | 22.33% | 0.03283 | **0.23634** ✅ |
| model_a | **oot** | 0.6357 | 0.2715 | 19.55% | 0.03296 | **3.08 × 10⁻⁷** ❌ |
| model_b | train | 0.6839 | 0.3678 | 27.36% | 0.03263 | 0.00040 |
| model_b | test | 0.6817 | 0.3634 | 27.28% | 0.03264 | **0.49418** ✅ |
| model_b | **oot** | 0.6923 | **0.3845** | 28.43% | 0.03268 | 0.00117 |
| model_a_recal_intercept | test | 0.6485 | 0.2969 | 22.33% | 0.03283 | 0.23947 ✅ |
| model_a_recal_intercept | **oot** | 0.6357 | **0.2715** | 19.55% | 0.03296 | 9.37 × 10⁻⁷ ❌ |
| model_a_recal_platt | test | 0.6485 | 0.2969 | 22.33% | 0.03283 | 0.21723 ✅ |
| model_a_recal_platt | **oot** | 0.6357 | **0.2715** | 19.55% | 0.03296 | 1.82 × 10⁻⁵ ❌ |

Six things to read out of this table, in order of interview value:

**1. No overfitting anywhere.** Train Gini 0.3013 → test 0.2969 for Model A; 0.3678 → 0.3634 for Model B. A drop of four-tenths of a Gini point is nothing. The models are not memorising.

**2. Model B improves out of time.** Gini rises from 0.3634 (test) to 0.3845 (OOT). A model getting *better* on unseen future data is unusual and reflects that 2014 was a large, clean, well-graded vintage.

**3. Model A's OOT calibration is a catastrophic failure.** p = 3.08 × 10⁻⁷, having started at 2.11 × 10⁻¹⁵ before the unstable variables were dropped. It ranks (Gini 0.27) but its *numbers* are wrong out of time.

**4. Recalibration preserved discrimination exactly.** OOT Gini is **0.2715 across all three Model A variants**, identical to four decimals. That is the proof recalibration behaved correctly — it moves the *level*, never the *ranking*. If Gini had moved, something would have been wrong.

**5. Recalibration did not fix it.** Intercept recalibration moved the OOT p-value from 3×10⁻⁷ to only 9×10⁻⁷, because the intercept shift required was tiny (Δα = +0.0048). Platt scaling, with two parameters, reached 1.82×10⁻⁵ and still failed.

**6. Therefore the miscalibration is a *shape* problem, not a *level* problem.** The average PD is fine; the model is wrong in particular deciles. No single-parameter (or two-parameter) rescaling can fix a shape error. The *relationship* between borrower fundamentals and default shifted between 2007–2013 and 2014, not just the base rate.

### 10.6 Recalibration technique

📘 **CONCEPT — intercept recalibration versus Platt scaling.**

**Intercept recalibration** re-estimates *only* $\beta_0$, freezing every slope. Mechanically: compute the linear predictor without the intercept, $\eta = \sum_j \beta_j \text{WoE}_j$, then fit a one-parameter logistic regression of the outcome on a constant, using $\eta$ as a fixed **offset**. This shifts every PD up or down by the same amount in log-odds space and provably leaves AUC, Gini, and KS untouched.

**Platt scaling** fits two parameters: $p_{\text{new}} = \text{logistic}(a \cdot \text{logit}(p_{\text{old}}) + b)$. More flexible, but it *rescales the slopes*.

📊 On this project, Platt achieved a marginally better OOT p-value (1.82×10⁻⁵ vs 9.37×10⁻⁷) and **intercept recalibration was still preferred**. The reason is specific to scorecards: Platt's slope factor of $a = 0.941$ would rescale every variable's contribution, **distorting the integer point values** and breaking the PDO = 20 relationship that makes the scorecard interpretable. Intercept recalibration changed only the baseline constant (Δα = +0.0048), leaving every bin's points intact. Choosing the mathematically slightly worse option for a sound structural reason, and being able to explain why, is a mature answer.

⚠️ **THE LEAKAGE TRAP IN RECALIBRATION — a classic interview probe.** Recalibration was fitted on the **test** sample and *reported* on **OOT**. If you recalibrate *on* OOT and then report OOT calibration, the number is guaranteed to look good and means precisely nothing — you have fitted to the thing you are measuring. The split used here is the honest one.

### 10.7 The conclusion, and why it is a strength

> **Model B is the deployment model. Model A is the interpretability benchmark.** Model A proves that default risk can be modelled from borrower fundamentals alone, but its out-of-time calibration instability makes it unsuitable for setting capital. This is documented, not swept away.

Model B remains calibrated out of time because it is anchored by `grade`, and Lending Club **re-fitted grade each year to current conditions**. Grade therefore carries a temporal adjustment that pure borrower fundamentals do not.

This sentence is worth more in an interview than any Gini number, because it demonstrates judgement rather than technique. Everyone can fit a model. Being able to say "I built two, found that the more intellectually honest one failed out-of-time calibration, diagnosed why, attempted two standard remedies, documented that neither worked and the reason, and deployed the other with the trade-off written down" is what a model risk team is actually hiring for.

---

## Chapter 11 — Portfolio monitoring

Building a model is a project. Running a portfolio is a job. Monitoring is the ongoing-surveillance layer that answers, every month: **is the book getting better or worse, and where?**

### 11.1 Vintage curves

Plot cumulative default rate against **months on book**, one line per origination cohort. Because the x-axis is loan *age* rather than calendar time, cohorts become directly comparable — the censoring problem from Chapter 2 disappears.

**How to read one.** All lines rise (defaults accumulate). Crisis vintages sit highest. The signal is the *ordering at a fixed age*: if the 2013 line sits **below** the 2010 line at month 12, underwriting tightened; if above, it loosened.

📊 **WHAT ACTUALLY HAPPENED — the maturity comparison at fixed MOB.** Twelve-month default rates fell from **6.56% (2008)** to **3.18% (2013)** while originations grew from 2,393 to 134,755 loans — a roughly **50% improvement in default rate while volume grew about 400×**. That combination is genuinely notable: most platforms that scale that aggressively see credit quality deteriorate. Systematic underwriting discipline is the defensible interpretation.

The methodological point matters as much as the finding: raw lifetime rates would have made 2008 look catastrophic and 2014 look pristine, purely from censoring. Holding months-on-book fixed strips that artefact out. **That control is what makes the claim defensible.**

### 11.2 Roll rates

Of the loans that were 30 DPD this month, what fraction rolled to 60 DPD next month, what fraction cured back to Current, and what fraction stayed put?

Roll rates are the classic **early warning** indicator, because they move *before* defaults do. A rising 30→60 roll rate this quarter is next quarter's default spike, visible one bucket ahead.

⚠️ **HONESTY NOTE — a genuine limitation of this project.** A true roll-rate matrix requires **monthly panel data**: the same loan tracked state-to-state across time (Current → 30 DPD → 60 DPD → default). Lending Club provides a **single snapshot** — one row per loan with its status as of extraction. There is no month-to-month history.

The build therefore constructed a **status-distribution proxy by vintage** and labelled it explicitly as such in the code, the output file (`roll_rate_proxy.csv`), the dashboard footer, and the limitations register.

The interview answer this earns: *"A proper roll-rate matrix needs loan-month panel data. With a single snapshot I approximated using the status distribution by vintage, and I labelled it a proxy everywhere it appears. If I had the panel, I would build the transition counts directly and monitor the 30→60 roll monthly as the early-warning trigger."* Knowing the limit of your own data is a senior trait.

### 11.3 Transition matrices

A **rating migration matrix** gives the probability of moving from each rating grade to each other grade (or to default) over a fixed period. The diagonal is stability; mass below the diagonal is deterioration.

⚠️ **HONESTY NOTE.** A true migration matrix requires **periodic re-rating** of the same borrower. This dataset has an origination grade and a final status, and nothing in between. The build therefore produced an **origination-grade-to-final-outcome matrix** — rows are origination grades A–G, columns are final outcomes (Fully Paid, Current, Late, Default), row-normalised to sum to 1.0. This is a valid and common variant, and it was documented as such rather than described as a migration matrix.

✅ **What it confirmed:** the default-column probability rises monotonically from Grade A to Grade G. Grade A lands mostly in Fully Paid / Current; Grade G shows a much fatter default column. It is the whole model confirmed in one picture — origination grade genuinely predicts final outcome.

### 11.4 The monitoring cadence a real bank runs

For completeness, since this is what "post-deployment monitoring" means on a CV:

| Frequency | Activity |
|---|---|
| Monthly | PSI on score, CSI on each variable, delinquency buckets, roll rates, new-business quality |
| Quarterly | Discrimination (Gini/KS) on the most recent closed performance window; override rates; vintage curve refresh |
| Annually | Full validation cycle; calibration to central tendency; recalibration decision |
| Trigger-based | PSI > 0.25, Gini drop > 20% relative, HL failure, material portfolio strategy change → out-of-cycle review |

---

## Chapter 12 — Model risk governance

### 12.1 What model risk is

**Model risk** is the risk of loss arising from decisions based on incorrect or misused model output. It has two sources: the model may be **wrong** (bad data, bad assumptions, bad maths), or it may be **used wrongly** (applied outside its intended population, or its output misinterpreted).

### 12.2 SR 11-7

**SR 11-7** is US Federal Reserve / OCC supervisory guidance on Model Risk Management (2011). It has become the de facto global template, cited by banks far outside the US — including in India — because no better articulation exists.

Its three pillars:

**1. Robust model development, implementation, and use.** Clear statement of purpose, sound design, quality data, rigorous testing, and **documentation sufficient for an independent party to reproduce the model**.

**2. Effective validation.** Performed by parties **independent** of the developers, covering conceptual soundness, ongoing monitoring, and outcomes analysis (backtesting and benchmarking).

**3. Governance, policies, and controls.** Model inventory, defined roles, board and senior management oversight, and an audit function checking that the framework itself is working.

### 12.3 The three lines of defence

| Line | Who | Role |
|---|---|---|
| **First** | Business / model developers | Own the risk. Build and use the models correctly. |
| **Second** | Independent Model Validation, Risk Management | Challenge. Validate independently. Set standards. |
| **Third** | Internal Audit | Assure that the first two lines are actually doing their jobs. |

A model development document — like the one Stage 12 produced — is the artefact the **first line** writes so that the **second line** can do its work.

### 12.4 What a model development document must contain

This is the specification Stage 12.1 was built against, and it is a genuinely useful checklist:

1. Executive summary
2. Model purpose, intended use, and explicit **out-of-scope** statements
3. Data: source, size, target definition and rationale, sampling, **leakage controls**
4. Methodology, with justification for the approach chosen
5. Development results: features, coefficients, signs, diagnostics
6. Validation results: discrimination, calibration, stability, on all samples
7. **Limitations and assumptions register**
8. Governance: ownership, approval, monitoring plan, recalibration triggers
9. Reproducibility: how to rebuild every number from raw data

📘 **CONCEPT — why the limitations register is a strength, not a confession.** Inexperienced candidates hide weaknesses. Experienced risk professionals lead with them. A validator who finds an undisclosed limitation concludes the developer either did not know or was concealing — both fatal. A validator who reads a thorough limitations register concludes the developer understands their own model better than the validator does. **Naming your own weaknesses first is the single strongest credibility signal in model risk.**

---

## Chapter 13 — The Indian regulatory context

### 13.1 Who regulates what

The **Reserve Bank of India (RBI)** is the banking regulator. It implements Basel through its Master Circular on Basel III Capital Regulations, with Indian-specific calibrations that have historically been *more* conservative than the international minimums.

**Ind AS 109** is the Indian adoption of IFRS 9, converged and substantially identical in substance. Indian banks' transition to Ind AS has followed a different and slower path than corporates', with RBI managing the timing — which is precisely why "Ind AS, IFRS 9, and CECL frameworks" appears as a single bullet on the job description: an Indian bank risk team must be fluent in all three.

**IRACP norms** — Income Recognition, Asset Classification and Provisioning — are RBI's own long-standing rules, which classify assets as Standard, Sub-Standard, Doubtful, or Loss, with prescribed provisioning percentages. Indian banks currently run IRACP alongside expected-credit-loss thinking, and the interaction between the two is live regulatory territory. Being aware that both exist marks you as someone who has thought about the Indian context specifically rather than reading only Western material.

### 13.2 What a CPRA Retail team actually does

Mapping the job description this project was built against, bullet by bullet, onto the artefact:

| JD responsibility | Where the project answers it |
|---|---|
| Estimate PD, LGD, CCF for risk management and regulatory reporting | Stages 3–6: WoE scorecard, two-stage LGD, term EAD, labelled synthetic CCF |
| Build risk dashboards across multiple dimensions; portfolio performance, outlook | Stages 9–10: vintage curves, transition matrix, institutional HTML dashboard |
| Basel capital computation, Standardised and Advanced IRB | Stage 7: both approaches, verified against reference values |
| Provisioning under Ind AS, IFRS 9, CECL | Stage 8: full ECL engine, staging, lifetime PD, macro scenarios, CECL contrast |
| Prepare presentations and conduct reviews with senior management | Stage 12: SR 11-7 model documentation pack and management deck |
| Hands-on Python experience is a must | The entire build: a tested, importable, reproducible Python package |

Every bullet is answered by working, tested, documented code.

---

## Chapter 14 — Where this sits in a real bank

A brief orientation, because it helps to know who you would be talking to.

**Business / Product** owns the P&L for personal loans, cards, auto. Wants volume and approval rates.

**Credit Policy** sets the rules — cut-off scores, eligibility, exposure limits. Consumes the scorecard.

**Credit Portfolio Risk Analytics (CPRA)** — this seat — builds and maintains the models, computes the parameters, produces the capital and provision numbers, and monitors the book.

**Independent Model Validation** challenges CPRA's models. Different reporting line, by design.

**Finance / Controllers** book the provisions into the published accounts and answer to the auditors.

**Treasury / Capital Management** consumes RWA to manage the capital ratios and plan issuance.

**Internal Audit** checks the whole apparatus.

**The regulator (RBI)** inspects, questions, and can require more capital or model remediation.

Notice how many of these functions consume the *same three numbers* — PD, LGD, EAD — for different purposes. That is why the parameters are estimated once, centrally, and governed tightly.

---

## Chapter 15 — The one-page formula sheet

Everything quantitative in this book, in one place.

**Expected loss**
$$\text{EL} = \text{PD} \times \text{LGD} \times \text{EAD}$$

**Exposure at default**
$$\text{EAD}_{\text{term}} = \max(\text{Funded} - \text{Principal Repaid},\ 0)$$
$$\text{EAD}_{\text{revolving}} = \text{Drawn} + \text{CCF} \times \text{Undrawn}$$

**Loss given default**
$$\text{LGD} = \frac{\max(\text{EAD} - \text{Post-default recoveries},\ 0)}{\text{EAD}} \qquad \text{Recovery Rate} = 1 - \text{LGD}$$

**Two-stage LGD**
$$\widehat{\text{LGD}} = 1 - \left[ P(\text{recovery}) \times \widehat{rr}_{\,|\,\text{recovery}} \right]$$

**Weight of Evidence and Information Value**
$$\text{WoE}_{\text{bin}} = \ln\frac{\%\text{good}_{\text{bin}}}{\%\text{bad}_{\text{bin}}} \qquad \text{IV} = \sum_{\text{bins}} (\%\text{good} - \%\text{bad}) \cdot \text{WoE}$$

**Scorecard scaling**
$$\text{Factor} = \frac{\text{PDO}}{\ln 2} \qquad \text{Offset} = \text{TargetPoints} - \text{Factor}\cdot\ln(\text{TargetOdds})$$
$$\text{Points}_{\text{bin}} = \text{BasePoints} + \text{Factor}\cdot(-\beta_j \cdot \text{WoE}_{\text{bin}}), \qquad \text{BasePoints} = \frac{\text{Offset} - \text{Factor}\cdot\beta_0}{m}$$

**Basel Other Retail correlation**
$$R = 0.03\cdot\frac{1-e^{-35\text{PD}}}{1-e^{-35}} + 0.16\cdot\left(1 - \frac{1-e^{-35\text{PD}}}{1-e^{-35}}\right)$$
QRRE: $R = 0.04$ fixed.  Residential mortgage: $R = 0.15$ fixed.

**Basel capital requirement**
$$K = \text{LGD}\left[ N\!\left(\frac{G(\text{PD}) + \sqrt{R}\,G(0.999)}{\sqrt{1-R}}\right) - \text{PD} \right]$$
$$\text{RWA} = K \times 12.5 \times \text{EAD} \qquad \text{Risk Weight} = K \times 12.5$$
PD floor 0.0003. No maturity adjustment for retail.

**Standardised retail**
$$\text{RWA}_{\text{SA}} = 0.75 \times \text{EAD}$$

**Downturn LGD (supervisory proxy used here)**
$$\text{LGD}_{\text{downturn}} = \min\!\left(1.0,\ \max(\text{LGD},\text{floor}) + 0.08\right)$$

**Discrete-time hazard and lifetime PD**
$$h(m) = \frac{d_m}{n_m} \qquad S(m) = \prod_{k=1}^{m}(1-h(k)) \qquad \text{PD}_{\text{cum}}(m) = 1 - S(m)$$

**IFRS 9 ECL by stage**
$$\text{ECL}_1 = \text{PD}_{12m}\cdot\text{LGD}\cdot\text{EAD} \qquad \text{ECL}_2 = \text{PD}_{\text{life}}\cdot\text{LGD}\cdot\text{EAD} \qquad \text{ECL}_3 = \text{LGD}\cdot\text{EAD}$$
$$\text{ECL}_{\text{reported}} = \sum_s w_s \cdot \text{ECL}(s) \quad \text{over macro scenarios } s$$

**CECL**
$$\text{CECL} = \text{PD}_{\text{life}} \cdot \text{LGD} \cdot \text{EAD} \quad \text{for every loan, always}$$

**Validation**
$$\text{Gini} = 2\cdot\text{AUC} - 1 \qquad \text{KS} = \max_s\left| F_{\text{bad}}(s) - F_{\text{good}}(s) \right|$$
$$\text{PSI} = \sum_{\text{bins}} (\%_a - \%_e)\ln\frac{\%_a}{\%_e} \qquad \text{Brier} = \frac{1}{n}\sum (p_i - y_i)^2$$
Hosmer–Lemeshow: high p = calibrated. PSI < 0.10 stable.

**Capital ratios**
CET1 ≥ 4.5% of RWA · Tier 1 ≥ 6% · Total ≥ 8% (plus buffers)
---
---

# PART II — THE ENGINEERING FROM ZERO

*This part assumes you have never opened a terminal. If you already ship code, skim it — but read Chapter 22, which is about working with an IDE agent and is the newest skill here.*

---

## Chapter 16 — The machine: Windows, PowerShell, and paths

### 16.1 What PowerShell is

**PowerShell** is a window where you type instructions instead of clicking. Press the **Windows key**, type `powershell`, press Enter. A blue window opens with a blinking cursor.

> 💡 Nothing you type here can break your computer. The worst realistic case is an error message, and **errors are information, not failure**. Read them; they almost always say exactly what is wrong.

### 16.2 The three commands that do 90% of the work

💻 **COMMAND — where am I?**
```powershell
pwd
```
Prints the current directory.

💻 **COMMAND — go somewhere**
```powershell
cd "D:\0000_after portfolio_24726\0_vizier\vizier\retail-credit-risk"
```
`cd` = change directory. **The quotes are mandatory when the path contains spaces.** Without them PowerShell reads `D:\0000_after` as the entire path and fails. This is the single most common beginner error on Windows.

**Success prints nothing.** Silence means it worked; the prompt line simply now ends with the new location.

💻 **COMMAND — what is in here?**
```powershell
dir
```
Lists files and folders. Variants used in this build:

```powershell
dir -Recurse -File | Select-Object FullName, Length | Format-Table -AutoSize
```
Every file underneath, with sizes.

```powershell
Get-ChildItem knowledge_base -File | Select-Object Name, @{N='MB';E={[math]::Round($_.Length/1MB,1)}}
```
Files in one folder with sizes in megabytes. The `@{N=...;E=...}` syntax is a **calculated property** — `N` is the column name, `E` is the expression that computes it.

```powershell
Get-Content ".\loan_data_2007_2014.csv" -TotalCount 1
```
Prints only the **first line** of a file. Essential when the file is 228 MB and you only need the header row — never open a file that size in Excel or Notepad.

### 16.3 Paths: absolute and relative

An **absolute path** starts from a drive letter and is unambiguous: `D:\projects\retail-credit-risk\config\variables.yaml`.

A **relative path** starts from wherever you currently are: `config/variables.yaml` means "the config folder inside my current directory". `.` means here; `..` means one level up.

Windows uses backslashes, everything else uses forward slashes, and Python accepts both. Prefer forward slashes in code for portability.

### 16.4 Execution policy

🔴 **ERROR — "running scripts is disabled on this system"**

Windows blocks PowerShell scripts by default as a security measure, which will bite you the first time you try to activate a virtual environment.

**Fix, run once, answer `Y`:**
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

`RemoteSigned` means: scripts you wrote locally may run; scripts downloaded from the internet must be signed. `-Scope CurrentUser` means this affects only your account, not the whole machine, which is why it does not require administrator rights.

---

## Chapter 17 — Python, virtual environments, and packages

### 17.1 Checking Python exists

💻 **COMMAND**
```powershell
python --version
```

**Should print:** `Python 3.11.9` or any 3.11+.

🔴 **If it opens the Microsoft Store, or says "not recognized":** Python is not installed or is not on your PATH. Download the Windows installer from python.org, run it, and — this is the step everyone misses — **tick "Add python.exe to PATH"** on the first screen before clicking Install. Then close PowerShell entirely, reopen it, and try again. A terminal only reads PATH when it starts, so an already-open window will not see the change.

⚠️ **A note on version, since it appears in every test output in this book.** The build ran on **Python 3.14.5**. Very new Python versions occasionally lack pre-built wheels for scientific packages, forcing slow source compilation or outright failure. If you are starting fresh and given the choice, **3.11 or 3.12 is the safer pick** for a data-science stack. Nothing in this project broke because of 3.14, but it is a known risk worth knowing.

### 17.2 The virtual environment

💻 **COMMAND**
```powershell
python -m venv .venv
```
Takes 10–20 seconds. Prints nothing.

📘 **CONCEPT — what a virtual environment actually is.** A private box for one project's Python libraries.

Suppose one project needs pandas 1.5 and another needs pandas 2.2. Installed globally, they fight, and one of them breaks — possibly weeks later, invisibly, with a subtly wrong answer rather than an error. A virtual environment gives each project its own isolated copy of Python and its own library folder. They cannot interfere.

The `.venv` folder is that box. You never open it, never edit it, never commit it to version control. You just **step inside it**.

💻 **COMMAND — step inside**
```powershell
.\.venv\Scripts\Activate.ps1
```

Prints nothing, but your prompt line now begins with **`(.venv)`**.

> 💡 **That `(.venv)` prefix is your single most important status indicator.** If you open a fresh terminal and do not see it, you are outside the box, and every `pip install` and `python` command will hit the wrong Python. Ninety percent of "it worked yesterday" problems are a forgotten activation.

### 17.3 Installing packages

💻 **COMMAND**
```powershell
python -m pip install --upgrade pip
pip install numpy pandas scikit-learn scipy statsmodels matplotlib pytest
```

The second takes 1–3 minutes and scrolls a lot of text. Ends with `Successfully installed ...`.

**What each library is for, since these six are the whole quantitative toolkit:**

| Library | Job in this project |
|---|---|
| **numpy** | Fast numeric arrays. The substrate everything else sits on. |
| **pandas** | DataFrames — tables with named columns. Holds the loan data. |
| **scikit-learn** | Machine learning. Logistic regression, gradient boosting, train/test splits, ROC-AUC. |
| **scipy** | Scientific computing. Supplies the normal CDF and its inverse — the `N` and `G` in the Basel formula. |
| **statsmodels** | Statistical modelling with **inference**. Returns coefficients *with standard errors and p-values*, which scikit-learn does not. Essential for a defensible scorecard. |
| **matplotlib** | Plotting. Every PNG figure. |
| **pytest** | The test framework. |

Added later as needed: **PyYAML** (config files), **pyarrow** (Parquet), **pypdf** + **sentence-transformers** (RAG index), **google-generativeai** (Gemini).

⚠️ Notice that no cloud service, database, or Docker container is required for Stages 0–10. It is plain Python on a laptop. Zero cost, zero infrastructure. Cloud appears only in Stage 11, and even there it is a single free API key.

---

## Chapter 18 — Project architecture

### 18.1 The folder structure

```
retail-credit-risk/
├── config/                    # YAML configuration - all thresholds and choices
├── data/
│   ├── raw/                   # immutable landing zone (gitignored)
│   ├── interim/               # intermediate transformations (gitignored)
│   └── processed/             # model-ready parquet samples (gitignored)
├── datasets/                  # the raw 228 MB CSV (gitignored)
├── docs/                      # model documentation, management deck
├── knowledge_base/            # regulatory PDFs for RAG (gitignored)
├── notebooks/                 # exploratory analysis only - never the source of truth
├── outputs/
│   ├── figures/               # PNG charts
│   ├── models/                # serialised .pkl models (gitignored)
│   ├── reports/               # dashboard HTML + JSON
│   └── tables/                # CSV result tables (committed - small)
├── src/creditrisk/            # THE PACKAGE - all real code lives here
│   ├── data/                  # loading, schema, target definition, sampling
│   ├── features/              # WoE binning, IV
│   ├── models/                # PD, scorecard, LGD, EAD, CCF, calibration
│   ├── regulatory/            # expected loss, Basel, IFRS 9, lifetime PD, macro
│   ├── validation/            # metrics, plots, validation runner
│   ├── monitoring/            # vintage, roll rates, transitions
│   ├── reporting/             # dashboard data + build
│   └── ai/                    # RAG index, retriever, tools, analyst
├── tests/                     # pytest suite - one file per module
├── .gitignore
├── pyproject.toml
├── requirements.txt
├── standing_rules.md
└── README.md
```

### 18.2 Why the code lives in `src/creditrisk/` and not the project root

Four reasons, and this is a real interview question about engineering judgement:

**1. It avoids import shadowing.** If you put a file called `data.py` or `models.py` at the project root, Python may resolve `import data` to *your* file instead of a library's, producing confusing failures. Namespacing everything under `creditrisk` makes collisions impossible.

**2. It makes the code importable from anywhere.** Any notebook, script, or test can write `from creditrisk.models.pd_model import PDModel` and get exactly the same code. There is one definition of everything.

**3. It forces the separation between code and outputs.** Notebooks become *reports that call the package*, not the place where the logic lives. This is precisely how banks work — and it is the difference between "run these 903 cells in the right order" and "run one command."

**4. It makes tests possible.** You cannot unit-test a notebook cell. You can unit-test a function in a module.

### 18.3 `pyproject.toml` and editable install

`pyproject.toml` declares the project as an installable package, telling Python that the source lives under `src/`.

💻 **COMMAND**
```powershell
pip install -e .
```

📘 **CONCEPT — what `-e` does.** The `-e` flag means **editable** (development) install. Instead of *copying* your source into the environment's `site-packages` folder, pip creates a **link** back to `src/creditrisk/`.

The consequence: `import creditrisk` works from any script, notebook, or test anywhere on the machine — **and when you edit the source, the change is live immediately, with no reinstall.** Without this, `from creditrisk...` simply raises `ModuleNotFoundError`.

🔴 **ERROR encountered in this build:** the agent referred to `pip install -e .` before `pyproject.toml` existed. Imports failed until it was created. If `from creditrisk...` raises `ModuleNotFoundError`, check in order: (a) is `(.venv)` showing? (b) does `pyproject.toml` exist? (c) has `pip install -e .` been run inside this venv?

---

## Chapter 19 — Git and GitHub

### 19.1 What Git is

**Git** is a save-history for code. Every meaningful change gets a snapshot you can return to. It is also what makes work shareable — and for a portfolio project, GitHub is where an interviewer will actually look.

💻 **COMMAND — initialise**
```powershell
git --version      # if "not recognized", install from git-scm.com and reopen PowerShell
git init
```
Prints: `Initialized empty Git repository in ...`

### 19.2 The three states

A file is in one of three places:

| State | Meaning | Command to move it forward |
|---|---|---|
| **Working directory** | Edited but not marked for saving | `git add` |
| **Staging area (index)** | Marked to be included in the next snapshot | `git commit` |
| **Repository** | Permanently recorded in history | `git push` (to send to GitHub) |

💻 **The everyday loop**
```powershell
git status                    # what changed, and what state is it in
git add .                     # stage everything
git commit -m "message"       # snapshot it with a description
git push                      # send to GitHub
```

### 19.3 `.gitignore` — and the 228 MB near-miss

`.gitignore` lists patterns Git should refuse to track.

🔴 **A REAL PROBLEM CAUGHT IN THIS BUILD.** The initial `.gitignore` excluded `data/`, but the raw CSV had been placed in `datasets/`. **Git was tracking a 228 MB file.** The source-control panel showed 32 pending changes.

**Why this had to be fixed before the first commit, not after:**
- Git stores the complete content of every version of every file, **forever**. Commit a 228 MB file once and the repository is permanently bloated — every future clone downloads it.
- **GitHub hard-rejects any single file over 100 MB.** The push would simply fail.
- Undoing it requires rewriting history (`filter-branch` or `filter-repo`), which is genuinely unpleasant.
- Separately and independently: **raw borrower records do not belong in a code repository at all.** They contain incomes, debt ratios, and payment behaviour. That is a data governance issue regardless of file size.

A second problem was caught at the same moment: a folder of third-party course notebooks (`365_course_files/`) was sitting inside the repo. Publishing someone else's paid course material as part of your portfolio is both an IP problem and a credibility problem. It was moved off the project entirely.

📊 **THE FINAL `.gitignore` — and the one clever line in it:**

| Pattern | Reason |
|---|---|
| `.venv/` | Environment, rebuildable, huge |
| `data/`, `datasets/` | Raw borrower data — size and governance |
| `knowledge_base/`, `*.pdf` | 5.3 MB of regulatory PDFs, freely re-downloadable |
| `outputs/models/`, `*.pkl` | Serialised binaries, regenerable |
| `*.csv` | Blocks the 228 MB raw file |
| `!outputs/tables/*.csv` | **The exception that re-allows the small result tables** |
| `.env`, any key file | Secrets. Never. |
| `__pycache__/`, `*.pyc`, `*.egg-info/` | Build artefacts |
| `.ipynb_checkpoints/` | Notebook autosaves |

That `!outputs/tables/*.csv` line is the interesting one. A leading `!` **negates** a previous rule. The effect: the blanket `*.csv` rule still blocks the enormous raw dataset, but the small summary tables are allowed through — which is what lets the dashboard render on GitHub Pages without anyone cloning the repo.

📊 **WHAT ACTUALLY HAPPENED:** commit `306a869` — **139 files, 13,017 insertions**. Verified before pushing: zero hits on PDFs, `.venv`, `data/`, `datasets/`, `outputs/models/`, `.env`, or the API key.

### 19.4 Pushing to GitHub

1. Go to **github.com** → **New repository**
2. Name it cleanly — `retail-credit-risk`
3. **Public** (a recruiter must be able to see it)
4. **Do not** tick "Add a README" or "Add .gitignore" — you already have both, and adding them creates an immediate merge conflict
5. Create

💻 **COMMAND**
```powershell
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO.git
git branch -M main
git push -u origin main
```

🔴 **If it asks for a password:** GitHub no longer accepts account passwords on the command line. It wants a **Personal Access Token** (Settings → Developer settings → Personal access tokens). Typing your account password will simply fail. If a browser window opens asking you to authorise Git, that is the normal first-time flow — say yes.

### 19.5 GitHub Pages — the highest-leverage two minutes

1. Repo → **Settings** → **Pages**
2. Source: **main** branch, **/ (root)** → Save
3. Wait ~1 minute

Your dashboard is then live at:
`https://yourname.github.io/repo-name/outputs/reports/risk_dashboard.html`

That link goes on the CV and in emails to recruiters. They click, they see an institutional risk dashboard, before you have said a word.

---

## Chapter 20 — Testing with pytest

### 20.1 Why every stage shipped with tests

Not because tests are virtuous, but because of a specific property: **a test is an assertion about behaviour that fails loudly when a later change breaks it.**

In a twelve-stage pipeline where Stage 8 consumes Stage 1's output, a silent error in Stage 1 corrupts everything downstream and you will not notice until a number looks odd four stages later. Tests are the tripwires.

They also serve a second purpose specific to *this* project: they are the evidence that the model was tested. SR 11-7 asks for it, and a validator will ask to see it.

💻 **COMMAND**
```powershell
pytest tests/test_schema.py -v      # one file, verbose
pytest tests/                       # everything
```

📊 The full suite finished at **39 passing tests**.

### 20.2 The four kinds of test used

**1. Structural / guard tests.** `assert_no_leakage` raises `ValueError` when `'recoveries'` appears in a feature list. This test protects the single most important invariant in the project.

**2. Mathematical identity tests.** `tool_expected_loss(0.03, 0.9, 10000) == 270.0`. Hand-computed, unambiguous. If this fails, the arithmetic is broken.

**3. Property tests.** Predicted LGD must lie in [0, 1]. Survival must be non-increasing. Cumulative PD must be non-decreasing. Every row of the transition matrix must sum to 1.0. Sample IDs must be disjoint. These assert *invariants* rather than specific values, and they catch whole classes of bug.

**4. Regulatory reference tests.** Verify the Basel K against published benchmark values. This is the strongest kind: it certifies against an external authority rather than against your own expectations.

### 20.3 The test that failed, and why that was the best moment in the build

🔴 Stage 7.3 added `tests/test_basel_reference.py` with four regulatory benchmark cases. **Three of the four failed.**

The investigation showed the *code* was right and the *benchmark* was wrong — the supplied reference values were QRRE (flat R = 0.04) while the implementation correctly used the Other Retail PD-dependent curve. Lending Club term loans are Other Retail. The **test** was corrected, not the formula.

📘 **Why this matters more than a passing test would have.** It caught a mismatch that a human eye reading the code would never have noticed, *before* wrong numbers could propagate into every capital figure in the project. And the fix forced a genuine Basel distinction — Other Retail versus QRRE — into the open, which became a talking point. That is exactly what a validation test is for.

### 20.4 Mocking, and its limits

`tests/test_analyst.py` **mocked** the Gemini API — replaced the live call with a fake that returns a canned response. This lets tests run offline, fast, free, and deterministically in CI.

⚠️ **But mocked means the model was faked.** Six mocked tests passing proved the *plumbing* was correct — the tools compute the right maths, routing works, the guardrail fires. It did **not** prove the API connected. This distinction became concrete in Stage 11, where all tests passed and the live CLI immediately returned a 404. **"It should work" and "I ran it and here is the output" are different claims,** and only the second is worth making in an interview.

---

## Chapter 21 — Config as data

Every threshold, list, and judgement call in this project lives in a **YAML** file under `config/`, never hardcoded.

📘 **CONCEPT — why this matters beyond tidiness.**

**Reproducibility.** The config file *is* the specification. Anyone can read `config/ifrs9.yaml` and know exactly what SICR rules were applied, without reading code.

**Sensitivity analysis becomes trivial.** Want to know what happens under the strict 90-DPD default definition? Change one line, re-run, compare. That is how the target sensitivity test was produced. It is the difference between *"I chose this"* and *"I chose this, and here is precisely what the alternative would have cost."*

**Governance.** A model risk team wants to see the assumptions listed in one place, dated and version-controlled — not scattered across twelve Python files as magic numbers.

The config files used:

| File | Contents |
|---|---|
| `variables.yaml` | All 75 columns classified into 7 categories — the leakage guard |
| `target_definition.yaml` | Default statuses, 12-month window, 3-month DPD lag, snapshot date |
| `sampling.yaml` | Development vintages, OOT vintage, test size, random seed, target column |
| `pd_model.yaml` | Excluded features per model, min IV, scorecard scaling constants, unstable-variable drop list |
| `ifrs9.yaml` | SICR relative threshold, absolute PD threshold, DPD backstop |
| `macro_scenarios.yaml` | Three scenarios with PD multipliers and weights |
| `ai.yaml` | Gemini model name (so a deprecation is a config change, not a code change) |

**Parquet** was used for the processed samples rather than CSV: it is columnar, compressed, preserves dtypes exactly, and loads far faster. 466,285 rows load in under a second. It requires the `pyarrow` package.

---

## Chapter 22 — Working with an IDE coding agent

The project was built in **Antigravity**, an IDE with a built-in AI coding agent. This is a genuinely new skill and worth treating as one.

### 22.1 The standing rules

The single most important artefact in the engineering half of this project. **Pasted at the top of every single prompt**, without exception.

🤖 **THE STANDING RULES**
```
STANDING RULES — follow these in every task:
- I am on Windows. Use PowerShell syntax for all commands.
- The virtual environment at .\.venv is already active. Use it. Do not create another.
- Do NOT install any package without first telling me what it is and why.
- Do NOT start any long-running process (servers, watchers, dashboards) unless I ask.
- Before you write a file, tell me in plain English: what the file does, why it
  exists, and how it fits the project. After you write it, walk me through it.
- Never invent column names, file paths, or data values. If you need to know
  something about the data, INSPECT it first and show me what you found.
- Do one task at a time. Stop and report. Do not run ahead to the next step.
- Write code a junior analyst could read. Comments explain WHY, not WHAT.
```

**Why each line is there:**

| Rule | Failure it prevents |
|---|---|
| PowerShell syntax | Agents default to bash; `ls -la` and `export VAR=` simply fail on Windows |
| Use the existing venv | Agents create a second environment, then packages land in the wrong place and imports break mysteriously |
| Ask before installing | Silent dependency creep; you end up with 200 packages and no idea which matter |
| No long-running processes | A dev server left running burns agent credits and blocks the terminal |
| Explain before and after writing | Forces the agent to make its reasoning inspectable — and is how *you* learn |
| Never invent — inspect first | **The most important rule.** Hallucinated column names are the #1 agent failure mode in data work |
| One task at a time | Prevents a cascade of half-correct changes you cannot untangle |
| Junior-readable code | You will read this in six months in an interview room |

### 22.2 The anatomy of a good prompt

Every prompt in Part IV follows the same five-part shape, and copying that shape is most of the skill:

1. **TASK:** one sentence stating the goal
2. **Exact file paths** to create — never "create a module for X"
3. **Function signatures** with argument names and return types
4. **The maths, written out** — formulas, thresholds, edge-case handling
5. **Tests to write**, then: **run it and show me [specific output]**

That last clause is what turns a code generator into a collaborator: it forces the agent to *execute* and *report*, so you see reality rather than intention.

### 22.3 The discipline that separates learning from accumulating

> **Never accept code you cannot explain.**

After the agent does anything:

> *"Explain what you just wrote, line by line, as if I have never programmed before. What would break if I changed it?"*

Then write one sentence in your own words. That habit is literally the difference between "used an AI IDE" and "became an engineer".

### 22.4 What the agent got right, and what it got wrong

Honest accounting from this build, because it calibrates expectations.

**Right:** every module was written correctly on the first or second attempt; it wrote genuinely good tests; it caught a real bug on its own (the 1916 date rollover — see Stage 1.7); its explanations of its own code were accurate; it correctly implemented the Basel formula even when handed mismatched reference values.

**Wrong, or needing correction:** it initially used the wrong LGD denominator (original loan amount rather than exposure at default) until challenged; it referenced `pip install -e .` before creating `pyproject.toml`; it read a **stale CSV** left over from a 3-loan unit test into the dashboard headline and did not notice the absurdity; it used a deprecated Gemini model name; it **overstated a result** in Stage 4, describing an improvement from 10⁻¹⁵ to 10⁻⁷ as fixing a calibration failure when 10⁻⁷ still fails decisively.

📘 **The pattern in those failures is the lesson.** The agent is strong at *writing code to a specification* and weak at *judging whether a result is sensible*. It will not notice that a headline number is nonsense, that a 10⁻⁷ p-value is not a pass, or that a CSV is stale. **Judgement stays with you.** That is not a criticism of the tool; it is the correct division of labour, and knowing it is what makes the tool safe to use.

---
---

# PART III — THE DATA

---

## Chapter 23 — The Lending Club dataset

### 23.1 What it is

**Lending Club** was a US peer-to-peer lending platform. Borrowers applied for unsecured personal loans; investors funded them. Lending Club published loan-level performance data, which became the standard public dataset for retail credit risk teaching and research.

| Property | Value |
|---|---|
| File | `loan_data_2007_2014.csv` |
| Size | **228 MB** (~229 MB reported by Git) |
| Rows | **466,285** loans |
| Columns | **75** |
| Origination range | **June 2007 – December 2014** (91 distinct months, 7.5 years) |
| Snapshot / extraction | **January 2016** |
| Product | Unsecured personal instalment loans |
| Terms | **36 months (72.48%)**, 60 months (27.52%) |
| Application type | 100% INDIVIDUAL |
| Currency | USD (reported as ₹ throughout this project's outputs — a labelling convention, not a conversion) |

⚠️ **A labelling honesty note.** The outputs use the ₹ symbol throughout because the project was built for an Indian bank context. The underlying data is US dollars. Nothing was converted. If asked, say so plainly — it is a presentation choice, not a claim about currency.

### 23.2 Why this dataset, and not synthetic data

The choice was deliberate and it was the right one.

**Real data has real problems**, and dealing with them is the skill. Missing fields that appear mid-history, statuses that do not map cleanly to regulatory definitions, no default dates, no monthly panel. A synthetic generator gives you clean data and teaches you nothing about the judgement calls.

**It anchors a resume claim.** The CV already referenced a Lending Club PD/LGD/EAD framework with AUROC/Gini/KS and PSI/CSI on out-of-time data. Building on the real data made that claim *demonstrable* rather than aspirational — an interviewer asking "tell me about that framework" gets a live repository.

**Where synthetic data was used, it was labelled.** Only the CCF revolving demonstration, because Lending Club genuinely cannot support it. Every such file is prefixed `SYNTHETIC_`.

### 23.3 The five structural limitations

These recur throughout the build and they are the honest boundary of what the dataset can support.

**1. Single snapshot, not a panel.** One row per loan, showing status as of January 2016. No month-by-month history. This is the deepest limitation: it blocks true roll rates, true rating migration, and true IFRS 9 staging over time.

**2. No default date.** The file records *current status*, not *when* the loan went bad. Default timing had to be **inferred** as `last_pymnt_d + 3 months` (three months being the approximate time from missed payment to 90 DPD).

**3. Status strings, not DPD.** Default had to be defined by mapping status strings to a default/non-default flag, rather than by a clean days-past-due test.

**4. No revolving exposures.** Term loans only. No limits, no undrawn balances, so no genuine CCF.

**5. Right-censoring.** Recent vintages have incomplete outcomes. Handled by the fixed 12-month window.

**6. Fields that appear mid-history.** `tot_cur_bal`, `total_rev_hi_lim` and the entire `sparse_application` block were not collected before late 2012. This is what CSI caught in Stage 4.

---

## Chapter 24 — The complete variable dictionary

All 75 columns, classified into seven categories in `config/variables.yaml`. **This classification is the leakage guard for the entire project.**

### 24.1 `application_time` — 34 columns — known at origination, ELIGIBLE for PD

```
loan_amnt, funded_amnt, funded_amnt_inv, term, int_rate, installment,
grade, sub_grade, emp_length, home_ownership, annual_inc,
verification_status, purpose, addr_state, zip_code, dti, delinq_2yrs,
earliest_cr_line, inq_last_6mths, mths_since_last_delinq,
mths_since_last_record, open_acc, pub_rec, revol_bal, revol_util,
total_acc, initial_list_status, collections_12_mths_ex_med,
mths_since_last_major_derog, acc_now_delinq, tot_coll_amt, tot_cur_bal,
policy_code, application_type
```

**What the important ones mean:**

| Column | Meaning |
|---|---|
| `loan_amnt` / `funded_amnt` | Requested / actually funded principal |
| `term` | 36 or 60 months |
| `int_rate` | Contractual interest rate — **Lending Club's own risk pricing** |
| `grade` / `sub_grade` | A–G / A1–G5 — **Lending Club's own risk model output** |
| `annual_inc` | Self-reported annual income |
| `dti` | Debt-to-income ratio: monthly debt payments ÷ monthly income |
| `revol_util` | Revolving utilisation: how much of available revolving credit is used. A strong risk signal — high utilisation means stretched. |
| `inq_last_6mths` | Credit enquiries in the last 6 months. **The strongest clean borrower fundamental in this data** (IV 0.076). Many enquiries means shopping hard for credit, which means need. |
| `delinq_2yrs` | Number of 30+ DPD incidents in the past 2 years |
| `pub_rec` | Derogatory public records (bankruptcies, judgments) |
| `open_acc` / `total_acc` | Currently open / lifetime credit lines |
| `earliest_cr_line` | Date of first credit line — a proxy for credit history length |
| `home_ownership` | MORTGAGE 50.59%, RENT 40.42%, OWN 8.94%, OTHER/NONE/ANY ~0.05% |
| `verification_status` | Whether income was verified: Verified 36.04%, Source Verified 32.17%, Not Verified 31.79% |
| `purpose` | Stated loan purpose — debt consolidation dominates |
| `initial_list_status` | f 64.98%, w 35.02% — a platform mechanic |
| `policy_code` | Whether the loan met credit policy |

⚠️ **The `grade` / `sub_grade` / `int_rate` problem.** These are *legally* application-time features — they exist at origination and involve no leakage. But they are **Lending Club's own risk model's output**, not borrower facts. Building a scorecard on them means largely re-predicting someone else's model. Banks hit the identical issue with bureau scores. This is why Stage 3 built the model **two ways**.

### 24.2 `sparse_application` — 15 columns — application-time but heavily missing early

```
open_acc_6m, open_il_6m, open_il_12m, open_il_24m, mths_since_rcnt_il,
total_bal_il, il_util, open_rv_12m, open_rv_24m, max_bal_bc, all_util,
total_rev_hi_lim, inq_fi, total_cu_tl, inq_last_12m
```

Additional bureau attributes Lending Club began collecting later. Eligible in principle, but the missingness pattern is time-dependent, which is a modelling hazard — and two of them (`total_rev_hi_lim`, plus `tot_cur_bal` from the main block) were ultimately **dropped** after CSI exposed the structural shift.

### 24.3 `outcome` — 15 columns — post-origination — **BANNED from PD**

```
loan_status, pymnt_plan, out_prncp, out_prncp_inv, total_pymnt,
total_pymnt_inv, total_rec_prncp, total_rec_int, total_rec_late_fee,
recoveries, collection_recovery_fee, last_pymnt_d, last_pymnt_amnt,
next_pymnt_d, last_credit_pull_d
```

📘 **CONCEPT — target leakage, the number one reason credit models fail validation.**

`recoveries` is the money collected after charge-off. It is **non-zero only for loans that defaulted**. Put it in a PD model and the Gini will be spectacular — and the model is worthless, because at application time, for a new customer, that value does not exist. There is nothing to put in the box.

The tell is an implausibly good metric. IV around 2.0 or Gini above 0.9 on retail data means look for leakage before celebrating.

**These columns are not evil — they are essential.** `recoveries`, `total_rec_prncp`, and `out_prncp` are exactly what LGD and EAD need. The discipline is that they were **walled off from PD**, structurally, by code. That wall is precisely why they were clean and legitimate to use in Stages 5 and 6.

**What each means:**

| Column | Meaning |
|---|---|
| `loan_status` | Current status string. **The basis of the target definition.** |
| `out_prncp` | Outstanding principal on a still-active loan. Used as EAD for performing loans. |
| `total_rec_prncp` | Principal repaid through normal amortisation, **before** default |
| `recoveries` | Money collected **after** charge-off — the true post-default recovery |
| `last_pymnt_d` | Date of last payment. **The only clue to default timing in the entire file.** |
| `total_pymnt` | Total received (principal + interest + fees) |

### 24.4 `identifier` — 4 columns
`Unnamed: 0`, `id`, `member_id`, `url`. Database keys. No predictive content; including them would fit noise.

### 24.5 `free_text` — 3 columns
`desc`, `emp_title`, `title`. Unstructured. Out of scope for this build. A legitimate NLP extension.

### 24.6 `all_null` — 3 columns
`annual_inc_joint`, `dti_joint`, `verification_status_joint`. 100% missing because every application here is INDIVIDUAL.

### 24.7 `cohort_anchor` — 1 column
`issue_d`. The origination date. Not a feature — it is the **time axis** for vintage analysis, the 12-month window, and the train/OOT split.

### 24.8 The guard functions

`src/creditrisk/data/schema.py` turns the YAML into enforcement:

| Function | Job |
|---|---|
| `load_variable_config()` | Parse the YAML, return the category → columns mapping |
| `get_pd_eligible_columns()` | Return `application_time` + `sparse_application` |
| `assert_no_leakage(columns)` | **Raise `ValueError`** naming any `outcome` or `identifier` column found in the list |
| `validate_schema_coverage(df)` | Raise if any DataFrame column is unclassified, or any classified column is absent |

`assert_no_leakage` is then called inside `PDModel.fit()`, before fitting. Leakage is not a policy anyone has to remember; it is **structurally impossible**.

---

## Chapter 25 — The loan status taxonomy

`loan_status` is a free-text-ish categorical whose mapping to default is the single most consequential judgement call in Stage 1.

📊 **The distribution across 466,285 loans:**

| Status | Count | % | Classification |
|---|---|---|---|
| Current | — | — | Non-default (still paying) |
| Fully Paid | — | — | Non-default (completed) |
| Charged Off | — | — | **DEFAULT** |
| Late (31-120 days) | — | — | **DEFAULT** (conservative choice) |
| In Grace Period | — | — | Non-default |
| Late (16-30 days) | — | — | Non-default (minor delinquency) |
| Does not meet the credit policy. Status:Fully Paid | 1,988 | 0.43% | Non-default (legacy) |
| Does not meet the credit policy. Status:Charged Off | 761 | 0.16% | **DEFAULT** (legacy) |
| Default | 832 | 0.18% | **DEFAULT** |

**Aggregate result:** 50,968 loans (**10.931%**) ever defaulted; 415,317 (**89.069%**) did not.

**The "Does not meet the credit policy" statuses** are legacy loans originated under an older, looser policy that Lending Club subsequently retired. They are small in number and were mapped by their underlying outcome (Charged Off → default, Fully Paid → non-default).

### 25.1 Date fields and their quirks

| Field | Range | Missing | Note |
|---|---|---|---|
| `issue_d` | Jun-2007 → Dec-2014 | 0 | 91 distinct months |
| `last_pymnt_d` | Dec-2007 → **Jan-2016** | 376 | The `Jan-16` value caused a real bug — see Stage 1.7 |
| `last_credit_pull_d` | May-2007 → Jan-2016 | 42 | |
| `earliest_cr_line` | Jan-1969 → **Dec-2068** | — | Obviously wrong; a 2-digit-year parsing artefact |

🔴 **THE TWO-DIGIT YEAR PROBLEM.** Dates are stored as `%b-%y` — `Dec-68`, `Aug-14`, `Jan-16`. Pandas resolves a two-digit year `68` as **2068**, not 1968. A credit line "opened" in 2068 is nonsense.

The first fix was to subtract 100 years from any parsed year **greater than 2015**. That handled `Dec-68 → 1968-12`. But it also silently converted `Jan-16` (January 2016, a perfectly valid `last_pymnt_d`) into **1916-01**, which after adding the 3-month DPD lag produced 1916-04 and generated **782 loans with a negative months-to-default of about −1140**.

The correct fix, which the agent found on its own: raise the rollover threshold to **year > 2049**. `Dec-68` still maps to 1968; `Jan-16` correctly stays 2016. Anomalies dropped from 782 to **zero**.

📘 This is the archetypal real-data bug: not a crash, not an exception, just quietly wrong numbers that only surface because someone built a reconciliation check that counts anomalies. **The check is what found it.**
---
---

# PART IV — THE BUILD: TWELVE STAGES

## How this part is organised

Each stage follows the same rhythm, which was the working rhythm of the actual build:

1. **The concept** — the domain idea, in two or three paragraphs
2. **The steps** — each with the exact prompt used, verbatim
3. **What good looks like** — how to recognise success before seeing the answer
4. **What actually happened** — the real output, with real numbers
5. **Errors and fixes** — anything that broke
6. **📘 The questions** — the comprehension questions asked at that point, with full answers

⚠️ **A note on the question boxes.** Early in the build, these were posed as a gate: answer them before proceeding. Partway through Stage 1 that changed, at the builder's request — the tooling and the concepts arriving simultaneously was too much at once, so the questions were **answered directly** at the end of each stage instead, in boxes to read or skip. Both forms are preserved here, because the questions themselves are the most interview-relevant material in the book. **Read them as an interview preparation asset.**

### The stage map

| Stage | Build | What was new versus a standard tutorial |
|---|---|---|
| 0 | Workbench — folder, Python, venv, git | — |
| 1 | Data foundation, leakage guard, **12-month observation window** | ✅ Fixes the target definition |
| 2 | Sampling + WoE/IV binning engine with monotonicity | ✅ Automated and tested |
| 3 | PD scorecard + points scaling + rating grades | Standard idea, proper code |
| 4 | Validation battery — Gini, KS, calibration, PSI/CSI | ✅ Calibration and stability are new |
| 5 | LGD — two-stage hurdle + downturn LGD | ✅ Downturn is a Basel requirement |
| 6 | EAD / CCF, honestly scoped | ✅ Limitations register |
| 7 | **Basel capital** — SA vs AIRB, supervisory formula, RWA | ✅ Entirely new |
| 8 | **IFRS 9 ECL** — SICR, lifetime PD, macro scenarios, CECL | ✅ Entirely new, biggest differentiator |
| 9 | Monitoring — vintage curves, roll rates, transitions | ✅ Mostly new |
| 10 | Dashboard | ✅ New |
| 11 | AI layer — RAG over real Basel PDFs + tool calling | ✅ New |
| 12 | Model doc pack + management deck | ✅ New |
| 13 | GitHub + publication | — |

**Stages 7 and 8 are where this stops looking like anyone else's project.**

---
---

# STAGE 0 — The workbench

**Goal:** a working Python project folder with an isolated environment and version control. About twenty minutes.

**No agent in this stage.** These commands are typed by hand, deliberately, because the terminal is the skill and it cannot be outsourced on day one.

### 0.1 — Open PowerShell

Windows key → type `powershell` → Enter.

### 0.2 — Check Python

💻
```powershell
python --version
```
Should print `Python 3.11.9` or higher. If not, see Chapter 17.1.

### 0.3 — Create the project folder

💻
```powershell
cd "D:\0000_after portfolio_24726\0_vizier\vizier"
mkdir retail-credit-risk
cd retail-credit-risk
```

The quotes are mandatory — the path contains spaces.

### 0.4 — Create the virtual environment

💻
```powershell
python -m venv .venv
```
10–20 seconds. Prints nothing.

### 0.5 — Activate it

💻
```powershell
.\.venv\Scripts\Activate.ps1
```
Prompt now begins `(.venv)`.

🔴 **"running scripts is disabled on this system"** →
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```
Answer `Y`, then activate again.

### 0.6 — Install the libraries

💻
```powershell
python -m pip install --upgrade pip
pip install numpy pandas scikit-learn scipy statsmodels matplotlib
```

### 0.7 — Initialise git

💻
```powershell
git --version
git init
```

### 0.8 — Open the folder in the IDE

File → Open Folder → the `retail-credit-risk` directory.

The Explorer should show only `.venv` inside it. **That emptiness is deliberate** — from here, every file that appears was written in front of you.

✅ **Stage 0 complete when:** `(.venv)` shows in the prompt, `pip list` shows pandas, and `git status` says "No commits yet".

---
---

# STAGE 1 — Data foundation and the 12-month target

**This is the hinge stage.** Everything downstream depends on getting the target definition right, and it is the thing standard tutorials get wrong.

## The concept that governs Stage 1

📘 **CONCEPT.** A PD model answers: *what is the probability this borrower defaults within the next 12 months?*

To train that, **every loan needs a moment where you look at it, and a fixed window afterwards where you watch what happened.**

```
   Jan 2013                 Jan 2014                    Dec 2014
      |                        |                            |
Loan A|====== 12-month window ======|  →  Defaulted → target = 1
      |                        |
Loan B|====== 12-month window ======|  →  No default → target = 0
      |                        |
Loan C|                        |    [==== 7 months ====]  → EXCLUDED
                                     (issued too late to observe 12 months)
```

Three consequences fall out of that picture, and they are what make this project different:

**1. Loans get dropped.** Anything issued in the last twelve months of the data window cannot be used — you do not yet know its twelve-month outcome. A standard tutorial keeps them all, which quietly **mislabels them as non-defaults**.

**2. Default timing matters, and Lending Club does not provide it.** The file records a *current status* as of extraction, not a month-by-month history. For a charged-off loan we must **infer** when it went bad. `last_pymnt_d` is the standard proxy: payments stopped, plus roughly three months to reach 90 DPD. That is an approximation, it must be documented as a limitation, and **being the candidate who says that out loud is exactly the point.**

**3. You end up with a genuine 12-month PD** — the input both Basel and IFRS 9 require. Without it, Stages 7 and 8 are not possible at all.

> **The methodological flaw this fixes.** Standard tutorials define the target as `good_bad` — did this loan *ever* default across the whole history. But loans issued in 2008 had six years to fail; loans issued in 2014 had a few months. The model then quietly learns "older loans default more," which is **seasoning, not risk**. And neither Basel nor IFRS 9 can consume a lifetime "ever" flag. That single fix is the hinge of the whole project — and it is a strong interview answer, because it shows you understand *why* the definition matters rather than just how to fit a logistic regression.

---

## Step 1.0 — Identify the data file

💻
```powershell
cd "D:\000_before portfolio_22726\Datasets"
dir
Get-Content ".\loan_data_2007_2014.csv" -TotalCount 1
```

**Why this first.** Windows hides file extensions, and the file was displaying as an "XLS Worksheet" at 228 MB — which is impossible for a real `.xls` (they cap at 65,536 rows). The header row confirms both the true format and the exact column names for this vintage of the file, which determines everything the loader must handle.

📊 **WHAT ACTUALLY HAPPENED** — it printed a long comma-separated line beginning:
```
,id,member_id,loan_amnt,funded_amnt,funded_amnt_inv,term,int_rate,installment,grade,sub_grade,emp_title,emp_length,home_ownership,annual_inc,verification_status,issue_d,loan_status,pymnt_plan,url,desc,purpose,title,zip_code,addr_state,dti,delinq_2yrs,earliest_cr_line,inq_last_6mths,...
```
A genuine CSV. Note the leading comma — an unnamed index column, which becomes `Unnamed: 0`.

---

## Step 1.1 — The standing rules

Saved to `standing_rules.md`, pasted at the top of **every** subsequent agent prompt. Reproduced in full in Chapter 22.1 and Appendix D.

---

## Step 1.2 — The project skeleton

🤖 **PROMPT**
```
TASK: Create the project skeleton for a retail credit risk modelling system.

Create this folder structure inside the current project root, with a .gitkeep
file in each empty folder so git tracks them:

  config/
  data/raw/  data/interim/  data/processed/
  docs/
  notebooks/
  outputs/figures/  outputs/models/  outputs/reports/  outputs/tables/
  src/creditrisk/data/
  src/creditrisk/features/
  src/creditrisk/models/
  src/creditrisk/regulatory/
  src/creditrisk/validation/
  src/creditrisk/monitoring/
  src/creditrisk/reporting/
  tests/

Add an empty __init__.py in src/creditrisk/ and in every subfolder of it.

Also create:
1. .gitignore — must ignore .venv/, __pycache__/, *.pyc, data/ (all of it),
   outputs/models/, .ipynb_checkpoints/, .env
2. requirements.txt — numpy, pandas, scikit-learn, scipy, statsmodels,
   matplotlib, pytest (one per line, no version pins yet)
3. README.md — just a title and one-line description for now

Then explain to me, folder by folder, what each one is for and why the code
lives under src/creditrisk/ rather than in the project root.
```

📊 **WHAT ACTUALLY HAPPENED.** The skeleton was created and the agent gave an accurate folder-by-folder explanation. Its rationale for `src/` layout was correct: it avoids import ambiguity and name collisions (a root-level `data.py` or `models.py` shadows real imports), and it makes the code an importable package.

🔴 **THREE PROBLEMS CAUGHT IMMEDIATELY AFTER THIS STEP**

**(a) A 228 MB file was being tracked by Git.** `.gitignore` excluded `data/` but the CSV sat in `datasets/`. Fixed before any commit. See Chapter 19.3 for why this was urgent rather than tidy.

**(b) Third-party course notebooks were inside the repo.** A folder of paid Udemy course files would have been published as part of the portfolio piece. Moved off the project entirely.

**(c) No `pyproject.toml` existed,** so `from creditrisk...` imports could not work despite the agent discussing `pip install -e .`. Added.

---

## Step 1.3–1.4 — Data inventory and the default-definition choice

An inventory prompt profiled the raw file: row and column counts, dtypes, missingness, categorical distributions, and date ranges. Results are in Chapters 23–25.

Then a decision point.

❓ **THE QUESTION ASKED:** *How should `Late (31–120 days)` be treated?*
**ANSWER CHOSEN:** *Default — conservative, matches standard practice.*

**Why that is defensible, in two sentences you can use.** *Empirically*, most Lending Club loans sitting at 31–120 DPD go on to charge off, so treating them as bad predicts where they end up rather than mislabelling them. *Practically*, scorecard developers routinely use a "bad" definition broader than the regulatory 90 DPD precisely to capture that roll-forward.

**And critically:** the mapping went into a **config file**, not the code. Re-running the entire model under the strict 90-DPD definition became a one-line change — which is what made the sensitivity test in Step 1.7 possible. That is the difference between *"I chose this"* and *"I chose this and quantified what the alternative costs."*

---

## Step 1.5 — The leakage guard

**The most important file in Stage 1, and the one standard tutorials never build.**

🤖 **PROMPT**
```
TASK: Create the variable classification config. This is the leakage guard for
the whole project.

Create config/variables.yaml. Classify every one of the 75 columns into
exactly one category. Use these lists verbatim:

application_time:   # known when the loan is granted — eligible PD features
  loan_amnt, funded_amnt, funded_amnt_inv, term, int_rate, installment,
  grade, sub_grade, emp_length, home_ownership, annual_inc,
  verification_status, purpose, addr_state, zip_code, dti, delinq_2yrs,
  earliest_cr_line, inq_last_6mths, mths_since_last_delinq,
  mths_since_last_record, open_acc, pub_rec, revol_bal, revol_util,
  total_acc, initial_list_status, collections_12_mths_ex_med,
  mths_since_last_major_derog, acc_now_delinq, tot_coll_amt, tot_cur_bal,
  policy_code, application_type

sparse_application:   # application-time but heavily missing in early vintages
  open_acc_6m, open_il_6m, open_il_12m, open_il_24m, mths_since_rcnt_il,
  total_bal_il, il_util, open_rv_12m, open_rv_24m, max_bal_bc, all_util,
  total_rev_hi_lim, inq_fi, total_cu_tl, inq_last_12m

outcome:   # post-origination — BANNED from PD, required for LGD/EAD
  loan_status, pymnt_plan, out_prncp, out_prncp_inv, total_pymnt,
  total_pymnt_inv, total_rec_prncp, total_rec_int, total_rec_late_fee,
  recoveries, collection_recovery_fee, last_pymnt_d, last_pymnt_amnt,
  next_pymnt_d, last_credit_pull_d

identifier:   Unnamed: 0, id, member_id, url
free_text:    desc, emp_title, title
all_null:     annual_inc_joint, dti_joint, verification_status_joint
cohort_anchor: issue_d

Add a one-line comment above each category explaining what it means and why
it exists.

Then write src/creditrisk/data/schema.py with:
- load_variable_config()  -> reads the yaml, returns a dict
- get_pd_eligible_columns()  -> returns application_time + sparse_application
- assert_no_leakage(columns)  -> raises ValueError naming any outcome or
  identifier column found in the list passed to it
- validate_schema_coverage(df) -> raises if any column in df is unclassified,
  or any classified column is missing from df

Write tests in tests/test_schema.py covering: assert_no_leakage raises on
'recoveries', passes on a clean list, and validate_schema_coverage catches an
unclassified column.

Run:  pytest tests/test_schema.py -v

You will need PyYAML. Tell me before installing it.
```

✅ **WHAT GOOD LOOKS LIKE:** 3 tests pass, and the seven category counts sum to **75**.

📊 **WHAT ACTUALLY HAPPENED**
```
============================= test session starts =============================
platform win32 -- Python 3.14.5, pytest-9.1.1, pluggy-1.6.0
rootdir: D:\0000_after portfolio_24726\0_vizier\vizier\retail-credit-risk
configfile: pyproject.toml
collected 3 items
tests/test_schema.py::test_assert_no_leakage_raises_on_leakage_column PASSED [ 33%]
tests/test_schema.py::test_assert_no_leakage_passes_on_clean_list PASSED [ 66%]
tests/test_schema.py::test_validate_schema_coverage_catches_unclassified_column PASSED [100%]
============================== 3 passed in 2.34s ==============================
```

Counts: 34 + 15 + 15 + 4 + 3 + 3 + 1 = **75** ✅

---

## Step 1.6 — The target definition

🤖 **PROMPT**
```
TASK: Build the 12-month default target definition.

First create config/target_definition.yaml containing:

  default_statuses:
    - "Charged Off"
    - "Default"
    - "Late (31-120 days)"
    - "Does not meet the credit policy. Status:Charged Off"
  non_default_statuses:
    - "Fully Paid"
    - "Current"
    - "In Grace Period"
    - "Late (16-30 days)"
    - "Does not meet the credit policy. Status:Fully Paid"
  performance_window_months: 12
  days_past_due_lag_months: 3   # months from last payment to 90 DPD
  snapshot_date: "2016-01-31"

Then write src/creditrisk/data/target.py with these functions:

1. parse_lc_date(series) — parses the '%b-%y' format. CRITICAL: pandas reads
   two-digit year 68 as 2068. Any resulting year greater than 2015 must have
   100 years subtracted. Write a test proving 'Dec-68' becomes 1968-12.

2. build_target(df, config) — returns a copy of df with these new columns:
     ever_default        1 if loan_status is in default_statuses
     est_default_date    last_pymnt_d + days_past_due_lag_months, only where
                         ever_default is 1. Where last_pymnt_d is missing and
                         ever_default is 1, use issue_d (never paid).
     months_to_default   whole months from issue_d to est_default_date
     default_12m         1 if ever_default AND months_to_default <= 12, else 0
     vintage_year        year of issue_d
     vintage_quarter     year-quarter of issue_d

3. target_summary(df) — returns a DataFrame with one row per vintage_year and
   columns: n_loans, n_ever_default, ever_default_rate, n_default_12m,
   default_12m_rate. Save it to outputs/tables/target_summary_by_vintage.csv

Write tests in tests/test_target.py for parse_lc_date (the 1968 case) and for
build_target on a small hand-built DataFrame where you know the right answer.

Then run it on the full dataset and show me target_summary_by_vintage.csv.
Explain what the numbers mean.
```

📊 **WHAT ACTUALLY HAPPENED — the vintage table (the first real result of the project):**

| Vintage | Loans | Lifetime default rate | 12-month default rate |
|---|---|---|---|
| 2007 | 603 | 26.20% | 5.141% |
| 2008 | 2,393 | 20.73% | 6.561% |
| 2009 | 5,281 | — | 4.639% |
| 2010 | 12,537 | — | 3.454% |
| 2011 | 21,721 | — | 3.554% |
| 2012 | 53,367 | 15.62% | 3.735% |
| 2013 | 134,755 | 13.69% | 3.176% |
| 2014 | 235,628 | 8.25% | 3.441% |
| **Overall** | **466,285** | **10.93%** | **3.435%** |

**Three readings, and they matter:**

**The censoring story is proved, not asserted.** 2012 vs 2014: lifetime 15.62% vs 8.25%, but 12-month 3.735% vs 3.441%. The lifetime rates are *not* comparable across vintages; the 12-month rates *are*, because every vintage got the same clock. Your own data demonstrates the argument for a fixed performance window.

**The crisis is visible.** 2007 and 2008 at 5.14% and 6.56%, against 3.2–3.7% afterwards — roughly double. Small samples (603 and 2,393 loans), so do not over-read, but the direction is right and it is a sign the pipeline is not lying to you.

**The ratio is the interesting bit.** Overall ~3.4% twelve-month against ~12–15% lifetime on matured vintages. So only about a **quarter of defaults happen in year one**. Defaults are back-loaded, building through months 12–30. That shape is the **seasoning curve** — and it is precisely what Stage 8 needs to construct lifetime PD for IFRS 9. **The data already contained the answer to a question not yet asked.**

---

## Step 1.7 — Target QA and sensitivity

🤖 **PROMPT (abridged to its four demands)**
```
1. RECONCILIATION BRIDGE. Produce a table that sums exactly:
   total loans = non-default + default_12m + default beyond 12m
   + negative-timing anomalies + missing est_default_date
   Save to outputs/tables/target_reconciliation.csv

2. ANOMALY DETAIL. Count and report any negative months_to_default and any
   ever_default rows with a missing est_default_date.

3. SEASONING CURVE. Histogram months_to_default in buckets
   0-1, 2-3, 4-6, 7-9, 10-12, 13-18, 19-24, 25-36, 37+.
   Save table to outputs/tables/default_timing_distribution.csv and figure to
   outputs/figures/default_timing_distribution.png
   Then tell me: what percentage of all defaults occur in the first 12 months?

4. SENSITIVITY TEST. Recompute default_12m under a STRICT definition that
   removes "Late (31-120 days)" from default_statuses. Produce a comparison
   table by vintage_year with both rates side by side, saved to
   outputs/tables/target_sensitivity.csv. Report the overall rate under each.

Also produce default_12m_rate by vintage_QUARTER and plot it to
outputs/figures/default_rate_by_vintage_quarter.png

Run it and show me everything. Interpret the seasoning curve for me.
```

✅ **WHAT GOOD LOOKS LIKE:** the bridge sums exactly; anomalies well under 1% of `ever_default`; the seasoning histogram rises to a hump around months 6–18 then decays.
❌ **WHAT WOULD MEAN IT IS BROKEN:** a spike at 0–1 months holding most of the mass — that would mean the `last_pymnt_d` fallback was firing far too often.

🔴 **THE BUG THE AGENT FOUND ON ITS OWN, BEFORE RUNNING QA**

> **Root cause:** `parse_lc_date()` used `parsed.dt.year > 2015` as the century-rollover threshold. The raw data contains valid payment dates up to `Jan-16` (January 2016). `Jan-16` was therefore converted to **1916-01-01**; adding the 3-month DPD lag gave 1916-04-01, producing **782 false negative timing anomalies of about −1140 months**.
>
> **Fix:** change the threshold to `parsed.dt.year > 2049`. This preserves `Jan-16` as 2016-01-01 while still mapping `Dec-68` to 1968-12-01.

This is the archetypal real-data bug — no crash, no exception, just quietly wrong numbers. **The reconciliation check is what surfaced it.**

📊 **WHAT ACTUALLY HAPPENED — the reconciliation bridge:**

| Item | Loans | % of total |
|---|---|---|
| Total loans | 466,285 | 100.000% |
| − Non-default (Current, Fully Paid, Grace, Late 16-30) | 415,317 | 89.069% |
| = **Ever default** | **50,968** | **10.931%** |
|   of which `default_12m = 1` (months 0–12) | 16,018 | 3.435% |
|   of which `default_12m = 0` (months > 12) | 34,950 | 7.495% |
|   of which **negative timing anomaly** | **0** | **0.000%** |
|   of which **missing est_default_date** | **0** | **0.000%** |

$$415{,}317 + 16{,}018 + 34{,}950 = 466{,}285 \quad ✅ \text{ exact}$$

📊 **The seasoning curve** — reproduced in Chapter 2.4. Headline: **31.43%** of all lifetime defaults occur within the first twelve months (16,018 of 50,968); **43.97%** fall between months 10 and 18.

📊 **The sensitivity test — baseline vs strict definition:**

| Vintage | Loans | Baseline 12m rate | Strict 12m rate | Difference |
|---|---|---|---|---|
| 2007 | 603 | 5.141% | 5.141% | 0.000% |
| 2008 | 2,393 | 6.561% | 6.561% | 0.000% |
| 2009 | 5,281 | 4.639% | 4.639% | 0.000% |
| 2010 | 12,537 | 3.454% | 3.454% | 0.000% |
| 2011 | 21,721 | 3.554% | 3.554% | 0.000% |
| 2012 | 53,367 | 3.735% | 3.735% | 0.000% |
| 2013 | 134,755 | 3.176% | 3.176% | 0.000% |
| 2014 | 235,628 | 3.441% | 3.416% | −0.025% |
| **Overall** | **466,285** | **3.435%** | **3.423%** | **−0.012%** |

**The judgement call turned out not to matter** — 0.012 percentage points overall, concentrated entirely in 2014 because loans in earlier vintages had already resolved into Charged Off or Fully Paid. Knowing that a conclusion does not hinge on a debatable choice is genuinely valuable, and it is only knowable because the test was run.

📊 **Quarterly trend:** peaked at **8.40% in 2008Q1**, then stabilised in a tight **3.0%–3.9%** band post-2010.

📘 **Two closing notes on Stage 1.** The empty "2–3 months" bucket is arithmetic, not error — default date = last payment + 3 months, so a loan that made even one payment cannot default before month 4; the 376 loans at month 0 are those that never paid at all. And the `Late (31–120)` decision turned out not to matter, as shown above.

---

## ❓ THE STAGE 1 QUESTIONS — with full answers

**1. Why can't `recoveries` be a feature in the PD model?**

`recoveries` is money collected *after* charge-off. It is non-zero only for loans that already defaulted. It is a post-origination outcome, and at the moment you are scoring a new applicant it does not exist — there is nothing to put in the box. Including it is **target leakage**: the model would achieve a spectacular Gini by reading the answer, and would be worthless in production. Leakage is the number one reason credit models fail validation, which is why `config/variables.yaml` and `assert_no_leakage()` were built before any model.

**2. What is the difference between "ever defaulted" and "defaulted within 12 months," and why does the second one need `last_pymnt_d`?**

"Ever defaulted" asks whether the loan went bad at any point in its life. "Defaulted within 12 months" asks whether it went bad within a fixed window after origination. The first is contaminated by how long each loan has been observed; the second is not. To compute the second you need to know *when* the default occurred, and `last_pymnt_d` is the only clue in the file — the month payments stopped, plus roughly three months to reach 90 days past due.

**3. Why do Basel and IFRS 9 need a *12-month* PD specifically?**

Basel's IRB capital formula takes a one-year PD as its input by construction — capital is sized against losses over a one-year horizon. IFRS 9 Stage 1 requires exactly the same thing: twelve-month expected credit loss. Both frameworks need this number, so an "ever defaulted" flag cannot feed either one. That is why Stage 1 mattered.

**4. Why is `datasets/` in `.gitignore`?**

The file is 228 MB. Git keeps a complete copy of every version forever, so committing it once bloats the repository permanently — and GitHub hard-rejects anything over 100 MB, so the push would simply fail. Separately and independently, raw borrower records containing incomes, debt ratios, and payment behaviour do not belong in a code repository at all.

**5. What does `pip install -e .` do?**

It registers `src/creditrisk/` as an installed Python package, but by *link* rather than copy. So `import creditrisk` works from any notebook, script, or test — and when you edit the source, the change is live immediately with no reinstall.

**6. The 2014 vintage shows 8.25% lifetime default but 2012 shows 15.62%. Were 2014 loans safer?**

No. That is **right-censoring**. By the January 2016 snapshot, 2012 loans had three to four years to go bad; 2014 loans had barely twelve to eighteen months. The seasoning curve proves it — 44% of all defaults happen between months 10 and 18, and 2014 loans mostly had not reached that window. Compare the 12-month rates instead, where every vintage gets the same clock: 3.735% for 2012 against 3.441% for 2014. Almost identical. This is precisely why banks use fixed performance windows.

---
---

# STAGE 2 — Sampling and the WoE/IV engine

**The concept.** You do not feed raw numbers like "annual income = 62,400" into a credit scorecard. You chop each variable into bands and ask, for each band: *what share of good loans landed here, versus what share of bad loans?* Take the log of that ratio and you get **Weight of Evidence** — positive means safer than portfolio average, negative means riskier. Replace the raw value with its WoE and every variable is suddenly on the same scale, missing values get their own bin instead of being dropped, and outliers stop distorting anything.

Sum across bins and you get **Information Value** — one number saying how predictive the variable is overall. Below 0.02 it is noise; 0.1–0.3 is useful; above 0.5 suspect leakage.

One rule regulators care about: for ordered variables, WoE must move in **one direction** across bins. Higher income should mean lower risk at every step, not zigzag. If it zigzags, merge bins until it does not.

Full treatment in Chapter 9.

---

## Step 2.1 — Split the data first

**Binning must be learned from training data only.** Fit it on everything and the model has already seen the test set.

🤖 **PROMPT**
```
TASK: Build the sampling strategy. Splits must happen BEFORE any binning.

Create config/sampling.yaml:
  development_vintages: [2007, 2008, 2009, 2010, 2011, 2012, 2013]
  oot_vintages: [2014]
  test_size: 0.2
  random_state: 42
  target_column: default_12m

Write src/creditrisk/data/sampling.py with:

1. split_development_oot(df, config) -> (dev_df, oot_df)
   Split by vintage_year. 2007-2013 is development, 2014 is out-of-time.

2. split_train_test(dev_df, config) -> (train_df, test_df)
   Stratified 80/20 on default_12m so both halves have the same default rate.

3. build_samples(df, config) -> dict with keys train, test, oot
   Calls the above, then asserts: no loan id appears in more than one sample,
   and the three row counts sum to the original.

4. sample_summary(samples) -> DataFrame with one row per sample and columns:
   n_loans, n_defaults, default_rate, min_issue_d, max_issue_d
   Save to outputs/tables/sample_summary.csv

Write tests/test_sampling.py proving there is no overlap between samples and
that stratification holds (train and test default rates within 0.1%).

Save the three samples as parquet in data/processed/ (install pyarrow - tell
me first). Run it and show me sample_summary.csv.
```

📊 **WHAT ACTUALLY HAPPENED**

Package installed: **pyarrow 25.0.0** — for writing Parquet.

```
tests/test_sampling.py::test_build_samples_disjoint_and_complete PASSED  [ 50%]
tests/test_sampling.py::test_train_test_stratification_holds PASSED      [100%]
============================== 2 passed in 7.11s ==============================
```

| Sample | Loans | Defaults | 12m default rate | Min issue | Max issue |
|---|---|---|---|---|---|
| train | 184,525 | 6,329 | **3.4299%** | Apr-08 | Sep-13 |
| test | 46,132 | 1,582 | **3.4293%** | Apr-08 | Sep-13 |
| oot | 235,628 | 8,107 | 3.4406% | Apr-14 | Sep-14 |

$$184{,}525 + 46{,}132 + 235{,}628 = 466{,}285 \quad ✅$$

Stratification held to $|0.034299 - 0.034293| = 0.000006$ — four decimal places. Zero ID overlap. Parquet files: train 35.0 MB, test 9.08 MB, oot 25.2 MB.

**The splits are textbook.** Nothing to fix.

---

## Step 2.2 — The WoE engine

🤖 **PROMPT**
```
TASK: Build the WoE and IV binning engine. This is the core feature layer.

Write src/creditrisk/features/binning.py containing a WoEBinner class:

  fit(X, y)
    - For NUMERIC columns: start with 20 quantile bins, then merge adjacent
      bins until WoE is monotonic across bins AND every bin holds at least 5%
      of rows. Missing values always get their own separate bin.
    - For CATEGORICAL columns: each category is a bin. Merge any category
      holding under 5% of rows into a bin called "OTHER". Missing gets its
      own bin. Do NOT enforce monotonicity on categoricals.
    - For each bin compute: n, n_good, n_bad, pct_good, pct_bad, WoE, IV.
    - Use Laplace smoothing (add 0.5) so empty cells never produce infinity.
    - Store all bin tables on the object.

  transform(X) -> replaces each raw value with its bin's WoE
  iv_summary() -> one row per variable with total IV, sorted descending,
                  with a strength label (useless/weak/medium/strong/suspect)

Wire in the leakage guard: call assert_no_leakage on the column list before
fitting. It must be structurally impossible to bin an outcome column.

Fit on TRAIN ONLY. Save bin tables to outputs/tables/woe_bins_<variable>.csv
and the IV summary to outputs/tables/iv_summary.csv. Plot WoE by bin for the
top variables to outputs/figures/.

Write tests: WoE of a bin with equal good/bad proportions is ~0; IV is
non-negative; monotonicity holds on numeric bins after merging; transform
maps an unseen category to the OTHER bin without crashing.
```

📊 **WHAT ACTUALLY HAPPENED — the IV finding that shaped the whole project.**

With `grade`, `sub_grade`, and `int_rate` included, they dominated:
- `grade` — IV **0.294** (strong)
- `int_rate` — IV **0.277** (medium/strong)

Strip those out, and the strongest remaining **borrower-fundamental** variable was `inq_last_6mths` at IV **0.076** — merely "weak". Income, DTI, and home ownership all landed weak-to-useless.

📘 **The interpretation is the whole story of this dataset.** Lending Club had already priced most of the risk into `grade` and `int_rate`. Those are not borrower facts; they are the *output of Lending Club's own risk model*. What remains for raw borrower attributes to explain is genuinely thin.

This is not a defect in the data. It is a real phenomenon that banks encounter constantly with **bureau scores**: when a strong pre-existing score is available as a feature, your model largely re-predicts it. The response — and what Stage 3 did — is to **build it both ways** and be explicit about what each version demonstrates.

---

## ❓ THE STAGE 2 QUESTIONS — with full answers

**Why split before binning?**
Binning learns from data — where to cut, and what each band's risk is. If it learns from the whole dataset, the test set has already influenced the model before testing. Splitting first keeps the test set genuinely unseen, so its Gini is an honest forecast of live performance. Same reason you never scale or impute on the full dataset.

**What is Weight of Evidence actually?**
Per band: the log of (share of goods ÷ share of bads). Positive means safer than average, negative riskier. It puts every variable — income, purpose, home ownership — on one common risk scale, so a logistic regression can weigh them against each other directly, and it gives missing values their own honest bin instead of guessing a value.

**What does Information Value tell you?**
One number for a whole variable's predictive strength. Under 0.02 drop it as noise. 0.1–0.3 is solid. Over 0.5, be suspicious — it is often leakage. `grade` at 0.294 is legitimately the strongest clean predictor here; if `recoveries` had slipped in, it would show around 2.0 and give the game away instantly.

**Why do `grade` and `int_rate` dominate — the key insight.**
They are not borrower facts; they are Lending Club's *own risk model's verdict*, formed at origination. Predicting default from them is partly grading someone else's homework. That is why Stage 3 builds Model A without them — to prove you can model risk from fundamentals, which is what a bank does when it has no pre-existing score. **Real skill sits in Model A even though Model B scores higher.**

**Why out-of-time, not just out-of-sample?**
Random test data comes from the same period as training. But models are deployed on *future* borrowers. Holding out 2014 entirely simulates that: fit on 2007–2013, test on a year the model never saw. If performance holds on OOT, the model is stable over time — which is exactly what Stage 9's PSI monitoring checks in production.

---
---

# STAGE 3 — The PD scorecard

**The concept.** Once every variable is WoE-transformed they are all on the same scale, so logistic regression fits cleanly and each coefficient is directly comparable. The model outputs a probability. But banks do not hand a credit committee a probability of 0.037 — they hand them a **score**, like 680. So apply the industry-standard "points to double the odds" rescaling, then cut the score range into **rating grades**, each with its own observed default rate. That grade table is what a bank actually runs lending policy on.

The reason this beats a black box: every point a borrower gains or loses traces back to one specific bin of one specific variable. Fully explainable, which is non-negotiable in regulated lending.

---

## Step 3.1 — Fit both models

🤖 **PROMPT**
```
TASK: Fit the PD logistic regression models. Build TWO models for comparison.

First create config/pd_model.yaml:
  target_column: default_12m
  # Model A: borrower fundamentals, excludes Lending Club's own risk pricing
  model_a_exclude: [grade, sub_grade, int_rate]
  # variables dropped for weak IV (below 0.02) - applied to BOTH models
  min_iv_threshold: 0.02
  # scaling for scorecard
  target_points: 600
  target_odds: 50
  pts_double_odds: 20

Write src/creditrisk/models/pd_model.py with a PDModel class:

  fit(train_df, woe_binner, iv_table, exclude_cols=None)
    - Select features: PD-eligible, IV >= min_iv_threshold, minus exclude_cols
    - WoE-transform using the ALREADY-FITTED binner (never refit on train)
    - Fit statsmodels Logit so we get coefficients, std errors, p-values,
      Wald confidence intervals. Add a constant.
    - Store the fitted result and the final feature list.
    - assert_no_leakage on the feature list before fitting.

  summary() -> coefficient table: variable, coefficient, std_err, p_value,
               significant (p<0.05). Flag any POSITIVE coefficient - after WoE
               transform every coefficient should be negative or near zero;
               a positive one means that variable is misbehaving.
  predict_pd(df) -> probability of default, one per row

Fit BOTH:
  Model A (exclude grade/sub_grade/int_rate)
  Model B (include everything above IV threshold)

Save both as outputs/models/pd_model_a.pkl and pd_model_b.pkl.
Save both coefficient tables to outputs/tables/.

Write tests/test_pd_model.py: leakage guard fires, predicted PDs are all
between 0 and 1, and the model reproduces a known logit on tiny synthetic data.

Run it. Show me both coefficient tables side by side and flag anything with
p >= 0.05 or a positive coefficient. Tell me which variables each model kept.
```

✅ **WHAT GOOD LOOKS LIKE:** every coefficient negative or near-zero (a positive one means that variable fights the model). Most p-values under 0.05. Model B keeps grade/int_rate and leans heavily on them; Model A keeps borrower fundamentals.

📊 **WHAT ACTUALLY HAPPENED — all coefficients negative in both models.** Clean.

**Model A final features:** `dti`, `purpose`, `term`, `revol_util`, `home_ownership`, `inq_last_6mths`, `annual_inc` (after the Stage 4.3 variable drop).

**Model B final features:** the same seven, plus `int_rate`, `grade`, `sub_grade`.

**The multicollinearity finding.** In Model B, `term`, `sub_grade`, and `revol_util` all went **insignificant** (p > 0.05). Adding `grade` and `int_rate` did not add new information — it **absorbed** the information those variables were carrying, because grade already encodes them. Lending Club built `grade` *from* those inputs. This is the statistical fingerprint of what the IV analysis suggested: grade is a composite of the others, not independent signal.

---

## Step 3.2 — Build the scorecard

🤖 **PROMPT**
```
TASK: Turn the fitted models into point-based scorecards and rating grades.

Write src/creditrisk/models/scorecard.py:

  build_scorecard(pd_model, woe_binner, config)
    Convert coefficients + WoE into points per bin using:
      factor = pts_double_odds / ln(2)
      offset = target_points - factor * ln(target_odds)
      points_per_bin = -(woe * coefficient) * factor,
                       with the intercept/offset distributed across variables
    Produce a scorecard table: variable, bin, WoE, coefficient, points.
    Round points to whole numbers. Save to outputs/tables/scorecard_<model>.csv

  score_dataset(df, scorecard) -> total score per loan (sum of bin points)

  build_rating_grades(scores, y, n_grades=8)
    Cut scores into 8 bands. For each grade report: score range, n_loans,
    n_defaults, observed default rate, share of portfolio. Grades ordered
    safest (lowest PD) to riskiest. Save to outputs/tables/rating_grades_<model>.csv

Do this for BOTH models.

Then check RANK ORDERING: default rate must fall monotonically from riskiest
grade to safest. Report whether it holds for each model.

Write tests/test_scorecard.py: points sum correctly, a known WoE+coef gives
the hand-computed points, rating grades are monotonic on synthetic data.

Run it. Show me the rating grade table for BOTH models and tell me whether
rank ordering holds.
```

📊 **WHAT ACTUALLY HAPPENED — the scaling arithmetic, reproduced:**

$$\text{Factor} = \frac{20}{\ln 2} = \mathbf{28.8539}$$
$$\text{Offset} = 600 - 28.8539 \times \ln(50) = 600 - 112.877 = \mathbf{487.1229}$$
$$\text{Base Points} = \frac{487.1229 - 28.8539 \times \beta_0}{m}$$
$$\text{Points}_{\text{bin}} = \text{round}\left(\text{Base Points} + 28.8539 \times (-\beta_j \times \text{WoE}_{\text{bin}})\right)$$

```
tests/test_scorecard.py::test_hand_computed_scorecard_points PASSED      [ 33%]
tests/test_scorecard.py::test_score_dataset_sums_feature_points_correctly PASSED [ 66%]
tests/test_scorecard.py::test_rating_grades_rank_ordering_monotonicity PASSED [100%]
============================== 3 passed in 2.22s ==============================
```

**Rating grade tables for both models: see Chapter 9.7.** Both rank-order strictly and monotonically. Model A: 1.21% → 7.02%. Model B: 0.85% → 7.75%.

📘 **Reading it.** Model B separates better, exactly as predicted — a wider spread means better discrimination. But look at *why*: it is grade doing the work. **The honest interview line:**

> *"Model B scores higher, but most of its lift comes from re-using Lending Club's own risk grade. Model A is the true underwriting model — it predicts default from borrower fundamentals alone, which is what a bank builds when it does not already have a score. I kept both and documented the trade-off."*

That answer is worth more than the Gini number.

---

## ❓ THE STAGE 3 QUESTIONS — with full answers

**Why feed WoE values into logistic regression rather than raw numbers?**
After WoE, every variable is on the same log-odds scale and already linearised against risk, so one coefficient per variable captures its full effect. Raw income (tens of thousands) and DTI (a small ratio) would be on wildly different scales, and neither has a linear relationship to risk. WoE fixes both and keeps the model explainable — each coefficient says how much that variable's risk pattern matters.

**Why should every coefficient be negative?**
High WoE means a safer bin. Higher predicted PD means riskier. So as WoE rises, predicted default must fall — a negative coefficient. A positive one would mean "safer borrowers default more," which is nonsensical and signals a broken bin or a data problem. Both models came out fully negative — clean.

**What does the scorecard scaling actually do?**
It is a cosmetic linear transform of the log-odds: pick a reference score (600), reference odds (50:1), and how many points double the odds (20). It changes nothing about ranking or probabilities — it turns "log-odds = −3.3" into "score = 600," which a human can read. "Twenty points doubles your odds" is the intuition it buys.

**Why did Model B's `term` and `sub_grade` go insignificant?**
Multicollinearity. `grade` already contains the information in `sub_grade`, `int_rate`, and much of `term` — Lending Club built grade *from* those inputs. Put them in together and grade wins, leaving the others with nothing left to explain, so their p-values collapse. This is the statistical proof that grade is a composite, not independent signal.

**Why keep the lower-separation Model A at all?**
Because it is the real modelling. Model A predicts default from borrower fundamentals — income, DTI, enquiries, purpose — which is what a bank does when originating its own loans. Model B mostly re-grades Lending Club's existing score. In an interview, Model A proves you can *build* a scorecard; Model B alone proves you can copy one. **The comparison is the story.**

---
---

# STAGE 4 — The validation battery

**The single most important stage for the job description**, because "model validation" appears in it explicitly and it is what a Model Risk team does all day.

**The concept.** A model that rank-orders is not automatically good. Validation asks three separate questions — **discrimination** (can it tell good from bad?), **calibration** (when it says 3%, do 3% default?), and **stability** (does it still work on data it never saw?). Discrimination gets you a good *ranking*; calibration gets you the right *number*; stability tells you it will survive contact with next year's borrowers. Miss any one and the model fails validation.

Full treatment in Chapter 10.

---

## Step 4.1 — Discrimination and calibration

🤖 **PROMPT**
```
TASK: Build the validation battery. Score BOTH models on train, test, AND oot.

Write src/creditrisk/validation/metrics.py:

  gini_auc(y_true, pd_pred) -> (auc, gini)  where gini = 2*auc - 1
  ks_statistic(y_true, pd_pred) -> max separation between cumulative good
      and bad distributions, plus the score at which it occurs
  calibration_table(y_true, pd_pred, n_bins=10)
      Bin predicted PD into deciles. Per bin: mean predicted PD, actual
      default rate, count.
  hosmer_lemeshow(y_true, pd_pred, n_bins=10) -> chi-square stat and p-value
      (high p-value = well calibrated; this is the formal calibration test)
  brier_score(y_true, pd_pred)

Write src/creditrisk/validation/plots.py:
  roc_curve_plot, ks_plot, calibration_plot (predicted vs observed with the
  45-degree perfect-calibration line). Save PNGs to outputs/figures/.

Write src/creditrisk/validation/run_validation.py that, for BOTH models,
computes every metric on train / test / oot and assembles one master table:
  model, sample, auc, gini, ks, brier, hl_pvalue
Save to outputs/tables/validation_summary.csv and save all plots.

Write tests/test_metrics.py: a perfect model gives AUC 1.0 / Gini 1.0, a
random model gives AUC ~0.5 / Gini ~0, KS is between 0 and 1, and a
well-calibrated synthetic set passes Hosmer-Lemeshow.
```

## Step 4.2 — Stability: PSI and CSI

A companion prompt built `src/creditrisk/validation/stability.py` with score-level PSI (development versus OOT) and per-variable CSI, saving `psi_summary.csv` and `csi_by_variable.csv`.

📊 **WHAT ACTUALLY HAPPENED — and it found a real problem.**

**The good news was real.** Both models rank-order. Both pass Hosmer–Lemeshow on test (p = 0.236 and 0.494). Score PSI ≈ **0.01** — rock stable. Train→test Gini barely moves: **zero overfitting**.

**The bad news was decisive.** Model A's OOT Hosmer–Lemeshow: **p = 2.11 × 10⁻¹⁵**. Not "somewhat off." A catastrophic calibration failure on 2014 data. The *ranking* held (Gini 0.27) but the *predicted PDs* were wrong out of time. And Basel and IFRS 9 multiply capital and provisions **by that PD**.

**The CSI finding was the same story from another angle.** `tot_cur_bal` and `total_rev_hi_lim` showed CSI ≈ **3.96** — enormous. The cause: Lending Club did not collect these until late 2012, so they are 100% MISSING in early vintages and fully populated by 2014. The WoE MISSING bin absorbed it for *scoring* (hence the stable PSI), but the underlying population had genuinely lurched.

📘 **This is the lesson about PSI and CSI in one paragraph.** A stable score PSI hid an unstable variable. Only per-variable CSI exposed it. **Compute both, never just PSI.**

---

## Step 4.3 — The decision, and the refit

❓ **THE QUESTION ASKED:** *`tot_cur_bal` and `total_rev_hi_lim` shifted structurally (CSI ≈ 4). What do we do?*
**ANSWER CHOSEN:** *Drop both, refit clean models.*

**Why that is the call a validator would make.** A variable that is **100% missing across half your development window** is not a feature — it is a **data-collection artefact**. It means something structurally different in 2008 than in 2014.

🤖 **PROMPT (abridged)**
```
TASK: Drop the two structurally-unstable variables and refit everything
downstream. These variables were 100% missing before late 2012 (CSI ~3.96),
so they are unreliable features, not signal.

1. Add drop_unstable: [tot_cur_bal, total_rev_hi_lim] to config/pd_model.yaml
   and filter them in PDModel.fit() before candidate selection, preserving
   the assert_no_leakage check.
2. Refit Model A and Model B. Overwrite the model pickles, the scorecards,
   and the rating grade tables.
3. Re-run the full validation battery and CSI.
4. Confirm rank ordering still holds for both models.
```

📊 **WHAT ACTUALLY HAPPENED**

**CSI fully cleaned** — every variable in both models now under 0.05:

| Model | Variable | CSI | Status |
|---|---|---|---|
| A & B | dti | 0.0416 | stable |
| A & B | purpose | 0.0362 | stable |
| B | int_rate | 0.0315 | stable |
| B | grade | 0.0293 | stable |
| B | sub_grade | 0.0264 | stable |
| A & B | term | 0.0258 | stable |
| A & B | revol_util | 0.0140 | stable |
| A & B | home_ownership | 0.0101 | stable |
| A & B | inq_last_6mths | 0.0087 | stable |
| A & B | annual_inc | 0.0057 | stable |

**Rank ordering held** on both: Model A 1.11% → 7.02%, Model B 0.86% → 7.72%.

**Model A OOT calibration improved by eight orders of magnitude** — from 2.11 × 10⁻¹⁵ to **3.08 × 10⁻⁷**.

⚠️ **AND IT STILL FAILED.** The agent reported this as a triumph — "improved by over 10⁸×!" — and that framing is **wrong**. 10⁻⁷ is nowhere near the 0.05 threshold. The variable drop helped enormously and did not fix the problem.

📘 **This is worth pausing on as a general lesson.** A large *relative* improvement in a failing metric is not a pass. The agent optimised for the appearance of progress; the correct read is that a failing test still fails. **This is exactly the kind of judgement the tool does not supply.**

---

## Step 4.4 — Recalibration

**The remaining diagnosis.** Model A discriminates fine (OOT Gini 0.27 — it sorts borrowers correctly) but the absolute PD *level* has shifted. Banks handle this with **calibration to central tendency**: nudge the overall PD level to match observed default rates without touching the ranking. It is a routine, documented step in every scorecard's life.

🤖 **PROMPT**
```
TASK: Recalibrate Model A to fix out-of-time calibration. Model A discriminates
well (OOT Gini 0.27) but its OOT Hosmer-Lemeshow still fails (p~3e-7), meaning
the PD LEVEL drifts on 2014 data while the RANKING holds. Fix the level only.

Write src/creditrisk/models/calibration.py:

  fit_intercept_recalibration(pd_model, woe_binner, calib_df, target_col)
    Re-estimate ONLY the intercept of the logistic model so that the mean
    predicted PD matches the observed default rate on calib_df. Keep every
    slope coefficient frozen (this preserves ranking, shifts level). Use a
    one-parameter logistic fit on the model's linear predictor as offset.
    Return a recalibrated model object.

  Apply it to Model A. IMPORTANT - to avoid leakage, fit the recalibration on
  a calibration slice, not on OOT itself: recalibrate on the TEST sample, then
  report calibration on OOT as the honest out-of-time check.

Re-run validation for the recalibrated Model A on train/test/oot. Add rows to
validation_summary.csv tagged 'model_a_recal'. Overwrite the calibration plot.

Also add a Platt-scaling variant as an alternative and report which gives the
better OOT Hosmer-Lemeshow. Save the better one as pd_model_a_calibrated.pkl.

Show me the updated validation table (model_a, model_a_recal, model_b rows)
and tell me: does model_a_recal now pass Hosmer-Lemeshow (p > 0.05) on OOT?
Confirm the OOT Gini is UNCHANGED from model_a (recalibration must not move
discrimination).
```

📊 **WHAT ACTUALLY HAPPENED — the implementation:**

`fit_intercept_recalibration` computed the un-intercepted linear predictor $\eta_{\text{slopes}} = \sum_j \beta_j \cdot \text{WoE}_j$, froze every slope (guaranteeing exact Gini/AUC/KS preservation), and re-estimated a single intercept via `statsmodels.api.Logit(y, const, offset=eta_slopes)` on the **test** sample.

`fit_platt_scaling` fitted a two-parameter logistic $a \cdot \text{base\_logit} + b$.

```
tests/test_calibration.py::test_intercept_recalibration_aligns_mean_pd_and_preserves_auc PASSED [100%]
============================== 1 passed in 2.41s ==============================
```
The test asserted $|\text{AUC}_{\text{recal}} - \text{AUC}_{\text{base}}| < 10^{-5}$.

**The full validation table is in Chapter 10.5.** The three results that matter:

**1. OOT Gini identical to four decimals — 0.2715 across `model_a`, `model_a_recal_intercept`, and `model_a_recal_platt`.** Recalibration behaved exactly as designed: it moved the level, never the ranking.

**2. OOT Hosmer–Lemeshow barely moved:** 3.08 × 10⁻⁷ → 9.37 × 10⁻⁷. Still failing, massively. The reason the movement was so small: **the intercept shift required was Δα = +0.0048** — essentially nothing. The average PD was already right.

**3. Platt scaling did marginally better (1.82 × 10⁻⁵) and still failed.** Two parameters were not enough either.

📘 **THE DIAGNOSIS, which is the real finding.** Model A's OOT miscalibration is **not a level problem — it is a shape problem.** The average PD is fine; the model is wrong in *particular deciles*. No single-parameter shift, and no two-parameter rescaling, can fix a shape error. The *relationship* between borrower fundamentals and default shifted between 2007–2013 and 2014, not merely the base rate.

📘 **AND WHY INTERCEPT RECALIBRATION WAS STILL PREFERRED,** despite Platt's better number. Intercept recalibration modifies only the baseline constant (Δα = +0.0048), **preserving the exact point values assigned to every bin in the scorecard**. Platt rescales all slopes by $a = 0.941$, which would distort the integer point relationships and break the PDO = 20 property that makes a scorecard interpretable. Choosing the slightly worse metric for a sound structural reason, and being able to explain it, is a mature answer.

---

## The Stage 4 conclusion

> **Model B is the deployment model. Model A is the interpretability benchmark** — it proves risk can be modelled from fundamentals alone, but its out-of-time calibration instability makes it unsuitable for setting capital. **This is documented, not swept away.**

Model B stays calibrated because it is anchored by `grade`, which Lending Club re-fitted each year to current conditions — so grade carries a temporal adjustment that pure fundamentals do not.

**Why this is worth more than a model that quietly passed.** You found a calibration failure, traced it to a structural data shift, dropped the offending variables, attempted two standard recalibration remedies, established that neither worked, diagnosed precisely why (shape not level), and documented the deployment decision with evidence. **That is not a student project — that is the actual workflow of a validation analyst.**

We did not chase it further. Diminishing returns, and the honest answer was already in hand.

---

## ❓ THE STAGE 4 QUESTIONS — with full answers

**Discrimination versus calibration — why both?**
Discrimination asks: can the model *rank* borrowers, riskiest to safest? (Gini, KS.) Calibration asks: when it says "3% PD," do 3% actually default? (Hosmer–Lemeshow.) A model can ace one and fail the other — Model A ranked fine on OOT (Gini 0.27) but its predicted numbers were badly off (HL p ≈ 10⁻¹⁵). Ranking gets you a good sort order; calibration gets you the right number. **Basel and IFRS 9 multiply by the number, so calibration is not optional.**

**What do Gini and KS measure?**
Both measure discrimination. Gini (= 2·AUC − 1) runs from 0 (random) to 1 (perfect): overall ability to separate good from bad. KS is the single biggest gap between the cumulative good and cumulative bad curves — "at the best cut-off, how far apart are the two populations?" A Gini around 0.30 is modest but honest; on thin borrower signal, a bank would accept it.

**Why does out-of-time matter more than out-of-sample?**
Test data is the same era as training. But models run on *future* borrowers. The 2014 OOT sample is the real trial — a year the model never saw. Model B holding, and even improving, on OOT is the genuine proof of robustness; a random test split cannot show that.

**What does PSI actually detect, and why did yours stay low?**
PSI asks whether the *score distribution* shifted between development and now. Under 0.10 is stable. Yours was ≈0.01 because the WoE MISSING bin quietly absorbed the `tot_cur_bal` transition at the *score* level, even though the raw variable lurched. **Stable PSI hid an unstable variable, and only per-variable CSI exposed it.** This is why you compute both.

**Why is calibration failing worse than low Gini?**
A bank can *live with* a modestly-discriminating model — it just grades more coarsely. But a miscalibrated model puts the wrong number into the capital and provision formulas, so the bank holds the wrong amount of capital against real losses. That is a **regulatory finding**, not a performance quibble. Catching it is precisely what model validation exists to do.
---
---

# STAGE 5 — LGD (Loss Given Default)

The work changes shape entirely now. PD asked *will it default* — a yes/no on every loan. LGD asks a different question, on a much smaller population.

**The concept.** When a loan defaults you rarely lose the whole amount — you recover something through collections, settlements, asset sales. **LGD is the fraction you do not get back.** It is modelled *only on defaulted loans*, because those are the only ones where a loss actually occurred. And it uses `recoveries` and `total_rec_prncp` — the exact columns walled off from the PD model. **That wall is why they are clean here:** they never leaked into PD, so using them now is legitimate.

The wrinkle that makes LGD its own beast: recovery rates are not bell-shaped. They pile up at extremes. A single regression cannot fit that shape. So the industry standard — and what was built — is a **two-stage (hurdle) model**:

```
                          Defaulted loans
                            (only these)
                                 │
                                 ▼
                     ┌───────────────────────┐
                     │  STAGE 1: classifier  │
                     │    any recovery?      │
                     └───────────┬───────────┘
                       yes ↙           ↘ no → recovery = 0
        ┌───────────────────────┐
        │  STAGE 2: regression  │
        │  how much recovered?  │
        └───────────┬───────────┘
                    ▼
            EXPECTED LGD = 1 − P(recover) × recovery rate
```

---

## Step 5.1 — Look at the recovery data first

**Before modelling, inspect the distribution. Its shape decides everything.**

🤖 **PROMPT (abridged)**
```
TASK: Prepare the LGD dataset and inspect the recovery distribution. Do not
model yet.

Work only on DEFAULTED loans (ever_default == 1), across the full dataset
(all vintages), since LGD needs every default we can get.

Build the LGD target and report the distribution: histogram, mean, median,
fraction at 0, fraction at 1, fraction with any recovery.
```

🔴 **THE FIRST DEFINITION WAS WRONG.** The initial implementation measured loss against the **original loan amount**, treating principal repaid before default as if it were recovery. That flatters LGD badly and is not the Basel definition.

## Step 5.2 — The corrected Basel LGD definition

🤖 **THE CORRECTION**
```
Replace the LGD logic with the Basel definition — loss relative to EXPOSURE
AT DEFAULT, not the original loan amount:

  funded            = funded_amnt
  principal_repaid  = total_rec_prncp
  ead_approx        = max(funded - principal_repaid, 0)
  post_default_recov = recoveries          # post charge-off collections only
  loss              = max(ead_approx - post_default_recov, 0)
  lgd               = loss / ead_approx, clipped to [0, 1]
  if ead_approx == 0: lgd = 0.0 and ead_zero_flag = 1
  recovery_rate     = 1.0 - lgd
  has_recovery      = 1 if post_default_recov > 0 else 0

Add a code comment noting that total_rec_prncp may include minor post-default
principal repayments, and that this ead_approx definition MUST stay identical
to the one used in ead_model.py.
```

📘 **WHY THIS MATTERS — the interview answer.** *Principal the borrower already repaid before defaulting was never at risk — it is back in the bank.* Measuring loss against the *original* amount credits normal repayment as if it were loss recovery. Basel measures loss against the balance still outstanding at default (EAD), which is the money actually exposed to loss. This is also why LGD and EAD must be defined consistently: **the denominator of one is the output of the other.**

📊 **WHAT ACTUALLY HAPPENED — the corrected Basel LGD distribution:**

| Metric | Value | % |
|---|---|---|
| Defaulted loans | 50,968 | 100.0% |
| `ead_zero_flag == 1` (fully repaid before flag) | 3 | 0.006% |
| **Mean LGD (std)** | **0.9301 (0.1104)** | **93.01%** |
| **Median LGD** | **1.0000** | **100%** |
| Mean recovery rate (std) | 0.0699 (0.1104) | 6.99% |
| Median recovery rate | 0.0000 | 0.00% |
| **Fraction total loss (LGD = 1.0)** | **0.5218** | **52.18%** |
| Fraction zero loss (LGD = 0.0) | 0.0035 | 0.35% |
| Fraction with post-default recoveries | 0.4782 | 47.82% |

**Is the distribution bimodal?** No — and the honest answer is more interesting than the textbook one. It is **heavily unimodal, concentrated at LGD = 1.0**. Over 52% of defaults are complete losses because Lending Club recorded zero post-charge-off recoveries. Another ~28.6% sit between 0.85 and 0.99. Near-zero LGD accounts for only 0.35%. So: a single dominant spike at 1.0 with a long left tail down to about 0.50 — not the twin peaks textbooks describe.

📘 **This is what real unsecured LGD looks like,** and it is exactly why these loans carry 15%+ interest: the lender must earn enough on performing loans to cover near-total losses on the failures. The 52% spike is also what a single regression would smear into a meaningless ~0.9 average for everyone. **Stage 1 owns the spike; Stage 2 owns the tail.**

---

## Step 5.3 — Build the two-stage model

🤖 **PROMPT**
```
TASK: Build the two-stage LGD model on the Basel LGD dataset.

Split defaulted loans into LGD train/test (80/20, random_state=42, stratify on
has_recovery). Features = application-time variables only, WoE-transformed with
a NEW binner fit on LGD-train (LGD is a different target than PD, needs its own
binning). Candidate features: loan_amnt, term, grade, sub_grade, int_rate,
purpose, home_ownership, annual_inc, dti, emp_length, verification_status,
inq_last_6mths, revol_util. Do NOT use any outcome column except to build the
LGD target itself.

Write src/creditrisk/models/lgd_model.py with a TwoStageLGD class:

  Stage 1 - fit_recovery_classifier(X, has_recovery)
    Logistic regression predicting P(has_recovery == 1). Report AUC/Gini.

  Stage 2 - fit_recovery_regressor(X_recovered, recovery_rate_recovered)
    Fit ONLY on loans with has_recovery == 1. Target = recovery_rate. Use a
    Beta-style approach: linear regression on logit(recovery_rate) clipped to
    (0.01, 0.99), or an sklearn GradientBoostingRegressor - pick one, justify.

  predict_lgd(X):
     p_rec   = stage1 P(has_recovery)
     rr_hat  = stage2 predicted recovery_rate (given recovery)
     exp_rr  = p_rec * rr_hat
     lgd_hat = 1 - exp_rr, clipped [0,1]

  Validation for LGD (NOT Gini - LGD is continuous):
     - mean absolute error (MAE) actual vs predicted LGD, on test
     - a calibration table: bucket predicted LGD into deciles, show mean
       predicted vs mean actual per decile
     - overall mean predicted LGD vs overall actual (portfolio level)
  Save lgd calibration table to outputs/tables/lgd_calibration.csv, a
  predicted-vs-actual scatter to outputs/figures/lgd_pred_vs_actual.png, and
  the model to outputs/models/lgd_model.pkl.

Write tests/test_lgd_model.py: predict_lgd bounded [0,1]; a loan the classifier
says will not recover gets LGD near 1; two-stage combines correctly on
synthetic data.

Run it. Show me: Stage 1 AUC, Stage 2 MAE, the LGD calibration table, and the
portfolio mean predicted vs actual LGD. Tell me if predicted LGD tracks actual
across deciles.
```

⚠️ **EXPECTATION SET BEFORE RUNNING, because it is a real finding.** LGD on unsecured consumer loans is **genuinely hard to discriminate at the individual-loan level** — application data barely predicts who will recover. A modest Stage 1 AUC is not a bug; it is the reality of the asset class. What must work well is the **portfolio-level mean**, because that is what Basel EL and IFRS 9 provisions consume.

📊 **WHAT ACTUALLY HAPPENED**

**Split:** 50,968 defaulted loans → 40,774 LGD-train / 10,194 LGD-test, stratified on `has_recovery`. A **new** WoE binner was fitted on LGD-train (LGD is a different target and needs its own binning).

**Stage 2 choice:** `GradientBoostingRegressor`. Justification given: it handles non-linear feature interactions and the skewed recovery-rate distribution non-parametrically, without forcing logit symmetry on non-Gaussian residuals.

| Metric | Value |
|---|---|
| Stage 1 classifier AUC | **0.6047** |
| Stage 1 classifier Gini | 0.2093 |
| Stage 2 recovery MAE (on recovered subset) | 0.0612 |
| Overall LGD MAE | 0.0790 |
| **Portfolio mean ACTUAL LGD** | **0.9304** |
| **Portfolio mean PREDICTED LGD** | **0.9302** |

**Calibration table by decile of predicted LGD:**

| Decile | Count | Mean predicted | Mean actual | Absolute error |
|---|---|---|---|---|
| 1 | 1,020 | 0.9065 | 0.9148 | 0.0082 |
| 2 | 1,019 | 0.9178 | 0.9177 | 0.0001 |
| 3 | 1,019 | 0.9226 | 0.9230 | 0.0004 |
| 4 | 1,020 | 0.9262 | 0.9248 | 0.0014 |
| 5 | 1,019 | 0.9294 | 0.9244 | 0.0049 |
| 6 | 1,019 | 0.9323 | 0.9352 | 0.0028 |
| 7 | 1,020 | 0.9354 | 0.9313 | 0.0041 |
| 8 | 1,019 | 0.9387 | 0.9368 | 0.0019 |
| 9 | 1,019 | 0.9429 | 0.9437 | 0.0008 |
| 10 | 1,020 | 0.9498 | 0.9524 | 0.0026 |

📘 **Reading Stage 5 — three things.**

**Portfolio calibration is essentially perfect.** Predicted 0.9302 vs actual 0.9304 — a **0.02 percentage point gap**. This is the number that flows into Expected Loss and IFRS 9 provisions, and it is dead on. Decile tracking is monotonic and tight (max error 0.0082).

**Stage 1 AUC of 0.60 is modest, and that is the honest truth of the asset class.** Whether an unsecured borrower's estate produces any post-charge-off recovery is close to unpredictable from application data — it depends on collections effort, later circumstances, settlement luck. The correct interview line: *"Individual-loan recovery is barely predictable for unsecured debt, so I optimised for portfolio-level unbiasedness, which is what Basel EL and IFRS 9 actually consume — and that came out to within 0.02pp."*

**One quiet win worth noticing.** The decile spread is narrow (0.91 to 0.95). The model is **not pretending to discriminate more than the data allows** — it honestly says "almost everyone loses ~93%, with small variation." A model claiming a 0.4-to-1.0 LGD spread here would be lying. Yours does not.

---

## ❓ THE STAGE 5 QUESTIONS — with full answers

**Why is LGD modelled only on defaulted loans?**
LGD is "given that a loan defaulted, what fraction do we lose?" A loan that never defaulted has no loss to measure — including it would be meaningless. So LGD trains on ~51k defaulted loans, not all 466k. This is the structural reason PD and LGD are separate models on separate populations.

**Why against exposure-at-default, not the original loan amount?**
Principal already repaid before default was never at risk — it is back in the bank. Measuring loss against the *original* amount credits normal repayment as if it were recovery, flattering LGD. Basel measures loss against the balance still outstanding at default. This is also why LGD and EAD must be defined consistently: the denominator of one is the output of the other.

**Why two stages instead of one regression?**
The distribution has a giant spike at LGD = 1 (52% total loss) plus a spread for partial recoveries. A single regression would average across the spike and the tail, predicting ~0.9 for everyone and capturing nothing. Splitting it — "any recovery?" then "how much?" — lets each stage model a clean sub-problem. This is standard practice for any bounded, spike-heavy target.

**Why isn't LGD validated with Gini?**
Gini measures ranking of a *binary* outcome. LGD is a *continuous* fraction, so we use MAE and a predicted-vs-actual calibration table instead. The portfolio-level mean matters most, because EL = PD × LGD × EAD sums across the book — individual noise averages out, but a biased mean flows straight into miscalculated capital.

**Why is unsecured LGD so high?**
No collateral. A defaulted mortgage recovers most of its value by selling the house; a defaulted personal loan has nothing to seize, so post-charge-off collections are poor — hence 52% total losses and 93% mean LGD. This is the economic reason unsecured lending is priced at 15%+.

---
---

# STAGE 6 — EAD and CCF

The last of the three parameters, and the shortest stage — because the concept is narrow and the honest answer for this dataset is partly *"here is why it is limited."*

**The concept.** EAD is the balance you expect to be *outstanding* at the moment a loan defaults. For a **term loan** — a fixed personal loan that only pays down — this is nearly the current balance, because the borrower cannot re-draw. Easy. For a **revolving product** — a credit card or credit line — it is harder and more important: a distressed borrower tends to *draw down* their available limit right before defaulting, so EAD can exceed today's balance. The tool that captures this is the **Credit Conversion Factor**.

⚠️ **The honest part. Lending Club loans are term loans, not revolving.** There is no undrawn limit to convert. A "true" CCF model is not applicable, and pretending otherwise is the kind of overclaim that gets caught in an interview.

❓ **THE QUESTION ASKED:** *EAD is straightforward for term loans; CCF needs revolving data we do not have. Scope?*
**ANSWER CHOSEN:** *Both — real term EAD plus a labelled synthetic CCF demonstration.*

Real where the data supports it, illustrative where it does not, and the boundary stated plainly.

---

## Step 6.1 — Real EAD for the term-loan book

🤖 **PROMPT**
```
TASK: Build EAD (Exposure At Default) for the term-loan portfolio. This is the
real, data-grounded part.

Write src/creditrisk/models/ead_model.py:

1. build_ead_term(df) on DEFAULTED loans (ever_default == 1):
     funded            = funded_amnt
     principal_repaid  = total_rec_prncp
     ead               = max(funded - principal_repaid, 0)   # outstanding at default
     ead_ratio         = ead / funded                         # fraction still owed
   This is the SAME ead_approx used in LGD - import it or keep the definition
   identical so LGD and EAD stay consistent. Add a code comment saying so.

2. ead_summary(df) -> mean/median ead, mean/median ead_ratio, plus ead_ratio
   distribution by term (36 vs 60 month) and by grade. Save to
   outputs/tables/ead_summary.csv and a histogram of ead_ratio to
   outputs/figures/ead_ratio_distribution.png

3. For NON-defaulted / performing loans we still need an EAD to compute
   portfolio EL later. For a term loan the exposure at a future default is
   approximated by the CURRENT outstanding principal:
     ead_performing(df) = out_prncp   (already in the data)
   Write a function that returns EAD for ANY loan: actual ead for defaulted,
   out_prncp for performing. Call it get_portfolio_ead(df).

Write tests/test_ead_model.py: ead = funded - principal_repaid, clips at 0,
ead_ratio in [0,1], get_portfolio_ead picks the right branch per loan.

Run it. Show me ead_summary.csv and tell me: what's the average fraction of
the loan still outstanding at default, and does it differ between 36 and 60
month loans?
```

📊 **WHAT ACTUALLY HAPPENED**

2 unit tests passed (EAD arithmetic, clipping at 0, [0,1] bounds, conditional branching).

**Average EAD ratio ~0.7–0.85**, with two clean, explainable segment findings:

**By term.** 60-month loans showed EAD ratios around **0.82** versus around **0.66** for 36-month loans. Longer loans amortise more slowly, so more principal is still outstanding when they go bad. A real reason longer terms are riskier, beyond simply having more time to fail.

**By grade.** Grade A defaulters had an EAD ratio of about **0.61**; Grade G defaulters about **0.85**. Riskier borrowers default *earlier*, before amortising much principal. This is a **double penalty** — higher PD *and* higher EAD — compounding in the expected loss calculation.

Both findings tie back to the seasoning curve: defaults cluster at months 10–18, before much principal has been repaid.

---

## Step 6.2 — The labelled synthetic CCF demonstration

🤖 **PROMPT**
```
TASK: Build a CCF (Credit Conversion Factor) demonstration module for REVOLVING
exposures. This is EXPLICITLY synthetic and must be labelled as such in every
output - it demonstrates methodology, it is NOT fitted on real revolving data,
because Lending Club has none.

Write src/creditrisk/models/ccf_demo.py:

1. At the top of the file, a module docstring stating in plain terms:
   "SYNTHETIC DEMONSTRATION. Lending Club loans are term loans with no undrawn
   limit. This module simulates a revolving sub-portfolio to demonstrate the
   CCF methodology used for credit cards / lines of credit. Not for production."

2. simulate_revolving_portfolio(n=5000, seed=42) -> DataFrame with:
     credit_limit, drawn_balance (at observation), undrawn = limit - drawn,
     utilisation = drawn/limit, and a simulated drawn_at_default where
     distressed borrowers draw down MORE of their undrawn limit (make the
     draw-down depend on utilisation + noise so there's a real pattern to fit).
     default_flag for a subset.

3. compute_realised_ccf(df on defaulted rows):
     ccf = (drawn_at_default - drawn_obs) / undrawn_obs, clipped [0,1]
   Report the realised CCF distribution.

4. fit_ccf_model(df): regress realised CCF on utilisation and limit. Report
   coefficients and a simple validation (MAE, mean predicted vs actual CCF).

5. ead_revolving(drawn, undrawn, ccf) = drawn + ccf * undrawn
   Show a worked example: a card with 100k limit, 30k drawn, predicted CCF,
   resulting EAD.

Every saved file name must start with "SYNTHETIC_" and every table must carry a
header row noting it is a demonstration. Save to outputs/tables/ and figures.

Write tests/test_ccf_demo.py: ccf bounded [0,1], ead_revolving = drawn +
ccf*undrawn, higher utilisation produces higher simulated draw-down.

Run it. Show me the realised CCF summary and the worked EAD example. Remind me
in your answer that this is synthetic.
```

📊 **WHAT ACTUALLY HAPPENED.** Realised CCF landed in the expected 0.4–0.7 band; the fitted model recovered the simulated pattern; every output carried the SYNTHETIC banner.

**The worked example:**
$$\text{EAD} = 30{,}000 + 0.37 \times 70{,}000 = ₹55{,}700$$

📘 **Why this scoping is a credibility asset.** Nobody could mistake these outputs for real revolving data — which is the entire point. You have demonstrated CCF mechanics without overclaiming. **All three Basel parameters now exist and are mutually consistent**, because LGD and EAD share the identical `funded − principal_repaid` definition. That consistency is what makes Stage 7 arithmetically valid.

---

## ❓ THE STAGE 6 QUESTIONS — with full answers

**What is EAD actually?**
The balance you expect to be *owed* at the moment of default — the money genuinely exposed to loss. It is the third Basel parameter alongside PD (will it default) and LGD (what fraction is lost). Expected Loss multiplies all three.

**Why is term-loan EAD easy and revolving EAD not?**
A term loan only pays down — the borrower cannot borrow more — so exposure at default is just the outstanding balance, reconstructed as funded minus principal repaid. A credit card lets a distressed borrower *draw down more* of their limit right before defaulting, so exposure can jump above today's balance. Predicting that jump is what CCF does, and it needs revolving data.

**What does the Credit Conversion Factor capture?**
The fraction of the currently-*undrawn* limit that a borrower converts into actual debt by the time they default. A CCF of 0.5 on a ₹70k undrawn limit means they draw an extra ₹35k before going bad. EAD = current drawn + CCF × undrawn. It only exists for revolving products.

**Why does labelling the synthetic part matter so much?**
Claiming a CCF model on term-loan data would be an overclaim any credit interviewer would catch instantly — term loans have no undrawn limit to convert. Building a clearly-labelled synthetic demonstration instead shows you know the methodology *and* know when your data cannot support it. **That honesty is a credibility signal, not a weakness** — it is exactly the judgement a model-risk team is hiring for.

**Why must LGD and EAD share the same definition?**
LGD is loss ÷ EAD. If LGD's denominator and the EAD you multiply by are computed differently, Expected Loss double-counts or under-counts. We deliberately used the identical `funded − principal_repaid` for both, so PD × LGD × EAD multiplies cleanly.

**Why does EAD ratio differ between 36- and 60-month loans?**
A 60-month loan pays principal down more slowly, so at any given month more of the original balance is still owed. Since defaults cluster early (the seasoning peak at months 10–18), 60-month loans are caught with ~82% still outstanding versus ~66% for 36-month.

**Why does EAD ratio rise across grades A→G?**
Riskier borrowers default *earlier*, before amortising much principal. Grade A defaulters had paid down ~39%; Grade G defaulters only ~15%. So the riskiest loans are hit with the most exposure still outstanding — a double penalty that compounds in EL.

---
---

# STAGE 7 — Expected loss and Basel regulatory capital

This is the stage the job description's "Basel" and "capital" bullets point straight at. Two distinct things get built.

**Expected Loss** is the easy half: EL = PD × LGD × EAD, per loan, summed. It is the loss a bank expects on average and prices into every loan — not a surprise, a cost of doing business. It becomes the provision baseline.

**Regulatory capital** is the hard, interesting half, and the part almost no candidate has built. Capital does not cover expected loss (pricing does that). Capital covers **unexpected loss** — the bad-year losses beyond the average. Basel's IRB approach takes your PD and LGD, applies a supervisory correlation and a 99.9% confidence stress, and produces a **capital requirement K**. Multiply by EAD and 12.5 and you get **Risk-Weighted Assets**.

Full derivation in Chapter 6.

---

## Step 7.1 — Expected loss

🤖 **PROMPT**
```
TASK: Compute portfolio Expected Loss from the three parameters.

Write src/creditrisk/regulatory/expected_loss.py:

  compute_expected_loss(df, pd_model, lgd_model, woe_binner_pd, woe_binner_lgd)
    For every loan in the portfolio:
      pd_hat  = pd_model.predict_pd (use Model B - the deployment model)
      lgd_hat = lgd_model.predict_lgd
      ead     = get_portfolio_ead (from ead_model)
      el      = pd_hat * lgd_hat * ead
    Return df with pd_hat, lgd_hat, ead, el columns.

  portfolio_el_summary(df) -> total EAD, total EL, EL as % of EAD (the
    portfolio expected loss rate), broken down by rating grade and by
    vintage_year. Save to outputs/tables/expected_loss_summary.csv

  Use the OOT (2014) sample as the portfolio to report on, since that's the
  most recent book. Also report the portfolio-level averages: mean PD, mean
  LGD, mean EAD, total EL.

Write tests/test_expected_loss.py: el = pd*lgd*ead exactly on synthetic rows,
el is non-negative, portfolio EL sums correctly.
```

📊 **WHAT ACTUALLY HAPPENED — the full EL table is in Chapter 4.1.** Headlines:

| Metric | Value |
|---|---|
| Portfolio loans (OOT 2014) | 235,628 |
| Mean predicted PD | 3.45% |
| Mean predicted LGD | 93.39% |
| Mean EAD per loan | ₹7,751.93 |
| **Total EAD** | **₹1,826,572,642 (₹1.827B)** |
| **Total Expected Loss** | **₹58,666,169 (₹58.67M)** |
| **EL as % of EAD** | **3.21%** |

Monotonic gradient 0.97% (Grade A) → 7.10% (Grade G), driven by PD (1.10% → 8.35%) rather than LGD (flat ~93%).

---

## Step 7.2 — Basel IRB capital

🤖 **PROMPT**
```
TASK: Implement the Basel IRB regulatory capital formula for retail exposures.

Write src/creditrisk/regulatory/basel_capital.py. Implement the Basel III
retail IRB risk-weight formula. For "other retail" exposures:

  correlation R = 0.03 * (1 - exp(-35*PD)) / (1 - exp(-35))
                  + 0.16 * (1 - (1 - exp(-35*PD)) / (1 - exp(-35)))

  capital requirement K:
     K = LGD * ( N( (1/sqrt(1-R)) * G(PD) + sqrt(R/(1-R)) * G(0.999) )
                 - PD * LGD )
  where N is the standard normal CDF and G is its inverse (percent point fn).
  Use PD floored at 0.0003 (Basel PD floor) and cap LGD at 1.

  RWA = K * 12.5 * EAD
  risk_weight = K * 12.5           (as a percentage of EAD)

Functions:
  basel_correlation(pd)
  basel_capital_k(pd, lgd)
  risk_weighted_assets(pd, lgd, ead)
  portfolio_capital_summary(df) -> total RWA, total capital requirement
    (8% of RWA = minimum), plus Tier 1 (6%) and CET1 (4.5%) minimums, broken
    down by rating grade. Save outputs/tables/basel_capital_summary.csv

Also implement the STANDARDISED approach for comparison:
  Under the standardised approach, unrated retail gets a flat 75% risk weight.
  standardised_rwa(ead) = 0.75 * ead
  Compare total RWA under IRB vs Standardised. Which is lower for this book?

Write tests/test_basel_capital.py with KNOWN reference values: verify
basel_correlation and K against hand-computed values for PD=0.01, LGD=0.45
(look up or compute the expected K ~ 0.0286). Verify RWA = K*12.5*EAD.

Run it on the OOT portfolio. Show me: total RWA under IRB vs Standardised,
the risk weight by rating grade, and total capital required (8% of IRB RWA).
Explain why IRB and Standardised differ for this portfolio.
```

📊 **WHAT ACTUALLY HAPPENED — the headline finding of the entire project:**

| Approach | Total RWA | Avg risk weight | Min capital (8%) |
|---|---|---|---|
| Standardised | ₹1,369,929,482 | 75.00% | ₹109.6M |
| **IRB** | **₹2,294,666,891** | **125.63%** | **₹183.6M** |
| Difference | **+₹924.7M** | **+50.6pp** | **+₹74.0M** |

**IRB produced 67% more RWA than the flat standardised weight.**

📘 **Why this is the standout result.** The naive assumption — the one banks operate on commercially — is that IRB *saves* capital. Here it costs substantially more, and the mechanism is explainable in one sentence: **the 93% LGD.** IRB is risk-sensitive and reads the book's actual parameters; standardised is one-size-fits-all and happens to be lenient for a pure unsecured book. The general lesson: *IRB rewards genuinely safe books and penalises genuinely risky ones.*

Even Grade A showed a **94% risk weight** at PD ≈ 1.1% — high, driven entirely by the LGD, and legitimate. But high enough that the formula had to be **verified rather than trusted**.

---

## Step 7.3 — Independent verification and downturn LGD

🤖 **PROMPT**
```
TASK: Verify the Basel capital formula against an independent reference, and
add downturn LGD, which Basel requires for capital (not the average LGD).

PART 1 - VERIFICATION
Add tests/test_basel_reference.py with these EXACT regulatory reference cases.
The Basel "other retail" K for these inputs is well-established:
  PD=0.01,  LGD=0.45  -> K should be approx 0.0286  (+/- 0.001)
  PD=0.05,  LGD=0.45  -> K should be approx 0.0637  (+/- 0.001)
  PD=0.001, LGD=0.45  -> K should be approx 0.0094  (+/- 0.001)
Also verify correlation R at PD=0.01 is approx 0.0356 (+/- 0.001).
If any of these FAIL, the formula is wrong - stop and show me the mismatch.

PART 2 - DOWNTURN LGD
Basel requires capital to use DOWNTURN LGD (loss in a recession), not the
average. Add to basel_capital.py:
  downturn_lgd(lgd, floor=0.0, method="supervisory")
    Implement: downturn_LGD = min(1.0, LGD * 1.0 + 0.08)
    i.e. an 8 percentage-point downturn add-on (a common supervisory proxy),
    capped at 1.0. Document that a real bank derives this from recession-period
    recovery data; here we use a supervisory add-on.

Recompute portfolio IRB RWA and capital TWICE:
  (a) using average LGD (what we did)
  (b) using downturn LGD
Show the capital difference. Save to outputs/tables/basel_downturn_comparison.csv

Run it. First tell me: did ALL the reference verification cases pass? Then show
me the downturn vs average capital comparison.
```

🔴 **THREE OF THE FOUR REFERENCE CASES FAILED.**

The code produced R = 0.1216 at PD = 0.01 against a benchmark of 0.0356 — a factor of 3.4 apart.

**The root cause, and it was in the prompt, not the code.** The reference values supplied were **QRRE** values (Qualifying Revolving Retail Exposures, which use a *fixed* correlation of 0.04). The prompt had asked for the **Other Retail** formula, which uses the PD-dependent curve running 0.03 → 0.16. The agent implemented Other Retail faithfully and correctly. **The benchmark was mismatched to the formula.**

📘 **And there was a genuine modelling question hiding inside the bug:**

| Sub-class | Correlation | Products |
|---|---|---|
| **Other Retail** | PD-dependent, 0.03 → 0.16 (0.1216 at PD=0.01) | Personal instalment loans, auto loans |
| **QRRE** | Fixed 0.04 | Credit cards, revolving facilities |

**Lending Club loans are term instalment loans → Other Retail is the correct curve.** The code was right all along.

🤖 **THE FIX PROMPT**
```
TASK: The Basel formula in basel_capital.py is CORRECT. The reference test
values were wrong - they were QRRE values, but Lending Club term instalment
loans are "Other Retail", which uses the PD-dependent correlation curve
(0.03 to 0.16), not QRRE's fixed 0.04. Fix the TEST, not the formula.

1. Confirm the current basel_correlation uses the Other Retail curve:
     R = 0.03 * (1-exp(-35*PD))/(1-exp(-35))
       + 0.16 * (1 - (1-exp(-35*PD))/(1-exp(-35)))
   Verify by hand that at PD=0.01 this gives R approx 0.1216. Show me the
   arithmetic.

2. Replace tests/test_basel_reference.py with the CORRECT Other Retail
   reference values. Compute them yourself from the formula and hard-code the
   expected results so the test is a real regression guard.

3. Document the Other Retail vs QRRE distinction in the module docstring.
```

📊 **WHAT ACTUALLY HAPPENED.** R = 0.1216 at PD = 0.01 verified by hand, step by step. **All 39 tests in the full suite passed.** The portfolio numbers from 7.2 stood unchanged — ₹2.295B IRB RWA, 125.63% risk weight, the ₹924M gap — all intact.

**Downturn LGD comparison:** total RWA rose by **₹159.25M**, portfolio risk weight from 125.63% → **134.35%**, minimum capital up **₹12,740,335 (+6.94%)**.

📘 **Why the failed test was the best moment in the build.** It caught a mismatch that a human eye reading the code would never have noticed, *before* wrong numbers could propagate into every capital figure in the project. And the fix forced a real Basel distinction into the open, which became a talking point. **That is exactly what a validation test is for.**

---

## ❓ THE STAGE 7 QUESTIONS — with full answers

**Why does capital cover unexpected loss and not expected loss?**
Expected loss is the average you already know is coming — you price it into interest rates and hold it as provisions. You do not need *capital* for a cost you have already charged for. Capital exists for the *surprise*: the recession year when losses spike far above average. Basel sizes it so the bank survives a one-in-a-thousand-year loss event. EL → provisions; unexpected loss → capital. Two buckets, two kinds of loss.

**What does the Basel IRB formula actually do?**
It takes your PD and asks: "in a 99.9%-bad year, how high would the default rate climb?" It uses a supervisory correlation (how much borrowers default *together* in a downturn) and the normal distribution to compute that stressed default rate, then multiplies by LGD and subtracts the expected part to get K. **The whole formula is a recession simulation compressed into one equation.**

**Why did IRB RWA come out higher than Standardised?**
IRB is risk-sensitive — it reads the actual 93% LGD and 3.4% PD and prices capital accordingly. For a genuinely risky unsecured book, that means high capital. The standardised flat 75% ignores how risky the book really is, so here it is lenient. **IRB rewards safe books and punishes risky ones; standardised treats everyone the same.**

**Why does capital use downturn LGD rather than average LGD?**
Because capital is about bad years, and in a recession recoveries collapse — collateral is worth less, collections are harder — so LGD *rises* exactly when defaults rise. Using average LGD would understate capital for the scenario capital is meant to cover. Basel therefore mandates downturn LGD. A frequent interview probe: *"which LGD goes in the capital calculation?"* The answer is **downturn, not average**.

**Other Retail versus QRRE, plainly.**
Both are retail correlation curves in Basel. Other Retail (personal/instalment loans) uses a PD-dependent curve running 0.03–0.16 — correlation *falls* as PD rises. QRRE (credit cards) uses a flat 0.04. Higher correlation → more capital, because it means borrowers default *together* in downturns. Lending Club term loans are Other Retail, so at PD = 0.01 the correlation is 0.1216 — three times QRRE's 0.04.

**Why was the failed test a win?**
It caught that the reference values did not match the formula, before those wrong numbers could propagate into every capital figure. That is exactly what a validation test is *for*: catching a mismatch a human eye would miss. And the fix forced a real Basel distinction into the open.

---
---

# STAGE 8 — IFRS 9 / Ind AS 109 Expected Credit Loss

The biggest differentiator in the project, and the one most candidates cannot build. It is the second regulatory framework — the *accounting* one — and it reuses everything already made.

**The concept.** Basel decides how much *capital* a bank holds. IFRS 9 decides how much *provision* it books as an accounting expense. Same raw ingredients (PD, LGD, EAD), combined differently, plus one big idea Basel does not have: **staging**.

```
   ┌──────────────┐   SICR    ┌──────────────┐  default  ┌──────────────┐
   │   STAGE 1    │ ────────► │   STAGE 2    │ ────────► │   STAGE 3    │
   │  performing  │           │ deteriorated │           │   impaired   │
   │              │ ◄──────── │              │           │              │
   │ 12-month ECL │  recovery │ lifetime ECL │           │ lifetime ECL │
   └──────────────┘           └──────────────┘           │    PD = 1    │
                                                          └──────────────┘
```

Full treatment in Chapter 7.

---

## Step 8.1 — The lifetime PD term structure

🤖 **PROMPT**
```
TASK: Build the lifetime PD term structure. Basel used a 12-month PD; IFRS 9
Stage 2 needs cumulative PD over the loan's remaining life. We build this from
the default timing (seasoning) data computed back in Stage 1.

Write src/creditrisk/regulatory/lifetime_pd.py:

1. build_hazard_curve(df) using the defaulted loans' months_to_default from
   the target QA step. Compute a DISCRETE-TIME HAZARD for each month m:
     hazard(m) = defaults occurring in month m / loans still surviving at
     start of month m
   Compute this over months 1..60 (5-year max term). Produce a table:
   month, n_at_risk, n_defaults, hazard, survival, cumulative_pd
   where survival(m) = product of (1 - hazard(k)) for k=1..m
   and cumulative_pd(m) = 1 - survival(m).
   Save to outputs/tables/lifetime_pd_term_structure.csv and plot the
   cumulative PD curve to outputs/figures/lifetime_pd_curve.png

2. scale_lifetime_to_account(pd_12m, remaining_term, term_structure)
   For a loan with a given 12-month PD and remaining term, produce its
   lifetime PD by scaling the portfolio term structure to that loan's own
   12-month PD level (multiplicative shift so the 12-month point matches
   pd_12m, then read cumulative PD at remaining_term).

3. remaining_term(df): term in months minus months elapsed since issue as of
   the reporting date (use snapshot 2016-01-31). Floor at 1, cap at original
   term.

Write tests/test_lifetime_pd.py: hazard between 0 and 1, survival is
decreasing, cumulative_pd is increasing and approaches the lifetime rate,
scaling preserves the 12-month point.

Run it. Show me the term structure table (selected months: 6,12,18,24,36,48,60)
and tell me: what is the portfolio cumulative PD at 12, 24, and 36 months, and
how does the lifetime (36m+) PD compare to the 12-month PD?
```

✅ **THE SANITY CHECK TO WATCH FOR:** cumulative PD at 12 months must ≈ the 3.4% twelve-month rate. If it does not roughly match, the hazard is miscomputed and everything downstream is wrong.

📊 **WHAT ACTUALLY HAPPENED — the term structure table is in Chapter 7.5.** Three passed unit tests. Headlines:

| Horizon | Cumulative PD |
|---|---|
| 12 months | **3.4352%** ← matches Stage 1's 3.435% ✅ |
| 24 months | 8.8221% |
| 36 months | 10.6356% |
| 60 months | 10.9281% |

**Lifetime (36m) ÷ 12-month = 3.096×.** Peak monthly hazard between months 10 and 16, topping at 0.6335% in month 14. Beyond month 36 the hazard collapses below 0.0001 and the curve flattens.

**That 3.1× multiple is the headline number** — it is *why* Stage 2 provisions balloon the moment a loan trips SICR.

---

## Step 8.2 — SICR and staging

🤖 **PROMPT**
```
TASK: Build IFRS 9 staging with SICR (Significant Increase in Credit Risk).

Write src/creditrisk/regulatory/staging.py:

Assign each loan to Stage 1, 2, or 3 as of the reporting date using:

  Stage 3: loan is currently in default (loan_status in default set, or
           90+ DPD). PD set to 1.
  Stage 2: SICR triggered but not defaulted. Use a TWO-PART SICR test:
     (a) Quantitative: current 12-month PD is more than X times the PD at
         origination. Since we don't have origination PD per loan, proxy
         origination PD by the loan's GRADE-level average PD at issue, and
         current PD by the model PD. Trigger if current/origination >= 2.0
         (relative threshold) OR absolute current PD > 0.06.
     (b) Backstop: 30+ DPD (Late 16-30 / Late 31-120 flags) forces Stage 2
         even if quantitative test not met (IFRS 9 rebuttable presumption).
  Stage 1: everything else.

  config/ifrs9.yaml holds: sicr_relative_threshold: 2.0,
    sicr_absolute_pd: 0.06, dpd_backstop_days: 30.

  stage_summary(df) -> count and % of loans in each stage, total EAD per
  stage, mean PD per stage. Save to outputs/tables/staging_summary.csv

Write tests/test_staging.py: a defaulted loan -> Stage 3; a loan with PD 3x
origination -> Stage 2; a 30+ DPD loan -> Stage 2 via backstop; a healthy
low-PD loan -> Stage 1.
```

📊 **WHAT ACTUALLY HAPPENED.** Staging distribution: approximately **80% Stage 1, 11% Stage 2, 8% Stage 3** by loan count. Stages 2+3 held 19% of loans but **22% of exposure** — risk concentrates in the deteriorated buckets, which is exactly the concentration IFRS 9 staging exists to surface early.

---

## Step 8.3 — Assemble ECL, and the CECL contrast

🤖 **PROMPT**
```
TASK: Assemble the full IFRS 9 ECL and contrast with US CECL.

Write src/creditrisk/regulatory/ecl.py:

  compute_ecl(df, ...) per loan:
     Stage 1: ECL = pd_12m * lgd * ead
     Stage 2: ECL = lifetime_pd * lgd * ead
     Stage 3: ECL = lgd * ead   (PD = 1)
     Apply discounting: divide lifetime ECL by (1+EIR)^t using int_rate as
     the effective interest rate and expected time-to-default from the
     term structure (simple: discount by average default timing). Document
     this as a simplified EIR discounting.

  ecl_summary(df) -> total ECL, ECL by stage, ECL as % of EAD, coverage ratio
    per stage (ECL/EAD). Save outputs/tables/ecl_summary.csv

  Compare to Basel EL from Stage 7: show IFRS 9 ECL vs Basel Expected Loss
  side by side and explain why they differ (staging + lifetime horizon).

  CECL CONTRAST: add compute_cecl(df) where ALL loans use LIFETIME ECL
  regardless of stage (the key US CECL difference - no staging, lifetime from
  day one). Report total CECL provision vs total IFRS 9 ECL. Save
  outputs/tables/ifrs9_vs_cecl.csv

Write tests/test_ecl.py: stage 3 ECL = lgd*ead; stage 2 uses lifetime pd;
CECL total >= IFRS9 total (lifetime-for-all is always more conservative).
```

📊 **WHAT ACTUALLY HAPPENED — the three-framework comparison:**

| Framework | Provision on the same ₹1.83B book |
|---|---|
| Basel Expected Loss | **₹58.67M** |
| IFRS 9 ECL | **₹278.48M** |
| CECL | **₹327.47M** |

Of the IFRS 9 total, **₹223.8M is Stage 3** — loans already defaulted. The Stage 1 provision was **₹30.27M** under IFRS 9's 12-month treatment; under CECL's lifetime-for-everything it rose to **₹79.26M** for the same 189,633 performing loans. **An extra ₹49M of provision arising purely from the framework choice, with zero change to the loans.**

⚠️ **THE HONESTY FLAG RAISED AT THIS POINT.** The headline comparison is slightly apples-to-oranges: Basel EL here covers a mixed performing+defaulted population and the ₹223.8M Stage 3 chunk dominates IFRS 9. A cleaner comparison also shows **IFRS 9 ECL on performing loans only (Stage 1+2)** next to Basel EL — and those two *are* comparable. This was added in Step 8.4.

---

## Step 8.4 — Macro scenarios and the like-for-like comparison

🤖 **PROMPT**
```
TASK: Add IFRS 9 forward-looking macroeconomic scenarios and a clean
performing-book comparison. This completes Stage 8.

Write src/creditrisk/regulatory/macro_scenarios.py:

1. Define three scenarios in config/macro_scenarios.yaml:
     baseline:  pd_multiplier 1.00, weight 0.50
     upside:    pd_multiplier 0.85, weight 0.20
     downside:  pd_multiplier 1.50, weight 0.30
   (A real bank links these to GDP/unemployment forecasts; here we use direct
   PD multipliers as a documented simplification.)

2. scenario_ecl(df, scenario) -> recompute ECL with PD scaled by the
   scenario's multiplier (both 12m and lifetime PD scale).

3. probability_weighted_ecl(df, scenarios) -> the IFRS 9 reported number:
   sum of each scenario's ECL times its weight. This weighted figure is the
   actual provision a bank books.
   Save outputs/tables/ecl_scenario_weighted.csv showing each scenario's ECL,
   its weight, and the final probability-weighted ECL.

4. Add ecl_performing_only(df): IFRS 9 ECL on Stage 1+2 loans only, to sit
   next to Basel EL for a like-for-like comparison. Save both numbers to
   outputs/tables/ifrs9_vs_basel_performing.csv

Write tests/test_macro_scenarios.py: downside ECL > baseline > upside;
probability-weighted ECL lies between upside and downside; weights sum to 1.
```

📊 **WHAT ACTUALLY HAPPENED.** Downside ECL notably above baseline (the 1.5× multiplier bites); the probability-weighted figure landing **above pure baseline**, because the 30%-weighted downside outweighs the 20%-weighted upside. **That is the number a bank actually reports, and it is conservative by design.**

**The performing-only comparison:** IFRS 9 (Stage 1+2) ≈ **₹54.7M** versus Basel EL ≈ **₹58.67M**. Nearly equal.

📘 **That near-equality is the real validation of the whole regulatory layer.** It proves both engines are internally consistent, and that the headline ₹278M vs ₹58M gap is **entirely** Stage 3 treatment plus the Stage 2 lifetime effect — not a bug in either one.

---

## ❓ THE STAGE 8 QUESTIONS — with full answers

**What is the seasoning/hazard curve, and why does it matter?**
The hazard at month m is "of the loans that survived to month m, what fraction default *this* month?" Chain those together and you get cumulative PD over any horizon. The curve peaks around months 10–16 then flattens — the classic retail shape. This single curve converts a 12-month PD into a *lifetime* PD, which is the one input IFRS 9 needs that Basel never did.

**What is SICR actually?**
Significant Increase in Credit Risk — the trigger that moves a loan from Stage 1 (12-month provision) to Stage 2 (lifetime provision). It is *relative to origination*: a loan that started risky and stayed risky is fine; a loan whose risk *doubled* since you made it trips SICR. Plus a 30-DPD backstop that forces Stage 2 regardless. This "change since origination" logic is the heart of IFRS 9 and the thing it added after 2008, when banks provisioned too late.

**Why does IFRS 9 ECL exceed Basel EL?**
Three reasons stacked: IFRS 9 books the *full* loss on already-defaulted Stage 3 loans (Basel EL is forward-looking only), applies a *lifetime* horizon to Stage 2 (Basel is always 12-month), and discounts at EIR. On the *performing* book alone they are close (~₹55M vs ₹59M) — the gap is almost entirely Stage 3 and staging.

**Why does CECL exceed IFRS 9?**
CECL has no staging — every loan carries lifetime ECL from day one. IFRS 9 gives healthy Stage 1 loans a lighter 12-month provision. So CECL front-loads more reserve: the Stage 1 book jumped from ₹30M (IFRS 9) to ₹79M (CECL). Same loans, ₹49M more provision, purely from the framework choice.

**Why forward-looking scenarios?**
IFRS 9 forbids a single point estimate — it requires probability-weighted outcomes across economic scenarios, so provisions rise *before* a downturn hits, not during it. That is the "expected" in Expected Credit Loss doing real work: you are pricing in a recession that has not happened yet, weighted by how likely it is.

**Why did the performing-book comparison matter?**
Comparing IFRS 9's *total* ECL to Basel EL was unfair — the IFRS 9 total was dominated by ₹224M of already-defaulted Stage 3 loans that Basel EL does not count. Stripping to performing loans only put both frameworks on the same population, and they came out ₹55M vs ₹59M — nearly equal, with the gap being precisely the Stage 2 lifetime effect. **That near-equality is what proves both engines are internally consistent rather than one being broken.**

**Why does probability-weighted ECL exceed baseline?**
The downside (30% weight, 1.5× PD) outweighs the upside (20% weight, 0.85× PD). The asymmetry pushes the reported number above the central case **by design** — you provision for the bad scenario before it happens, weighted by its likelihood. This forward-looking conservatism is the core lesson IFRS 9 drew from banks under-provisioning going into 2008.
---
---

# STAGE 9 — Portfolio monitoring

**What we are building:** the ongoing-surveillance layer — the tools a portfolio analyst runs every month to answer *"is the book getting better or worse?"* This is the job description's "portfolio monitoring, early warning" bullet made concrete.

**The concept.** Three classic techniques. **Vintage curves** — cumulative default rate by months-on-book, one line per origination cohort; if newer vintages sit above older ones at the same age, underwriting is deteriorating. **Roll rates** — of loans 30 days late this month, what fraction rolled to 60 next month versus cured? Rising roll rates are an early warning *before* defaults show up. **Transition matrices** — the probability of moving between rating grades; the diagonal is stability, below-diagonal is migration toward default.

Full treatment in Chapter 11.

---

## Step 9.1 — Vintage curves and delinquency migration

🤖 **PROMPT**
```
TASK: Build portfolio monitoring analytics - vintage curves and roll rates.

Write src/creditrisk/monitoring/vintage.py:

1. vintage_curves(df) using months_to_default and vintage_year:
   For each vintage_year, compute cumulative default rate at each month-on-book
   (0..48). Return a matrix: rows = vintage_year, cols = month-on-book, values
   = cumulative default rate. Save to outputs/tables/vintage_curves.csv and
   plot all vintage lines on one chart (x=months on book, y=cumulative default
   rate, one line per vintage) to outputs/figures/vintage_curves.png

2. vintage_maturity_comparison(df): compare the default rate at a FIXED
   month-on-book (say month 12 and month 18) across vintages, so maturities
   are comparable. Save to outputs/tables/vintage_maturity_comparison.csv
   Report: are more recent vintages showing higher or lower default rates at
   the same age?

Write src/creditrisk/monitoring/roll_rates.py:

3. Using loan_status delinquency buckets (Current, Late 16-30, Late 31-120,
   Default/Charged Off), build a roll-rate table: of loans in each bucket,
   what fraction moved to a worse bucket vs cured vs stayed. Since we have a
   snapshot (not monthly panel), approximate using current status distribution
   by vintage as a proxy, and DOCUMENT this limitation clearly - a true roll
   rate needs monthly panel data we do not have.
   Save to outputs/tables/roll_rate_proxy.csv

Write tests/test_vintage.py: cumulative default rate is monotonic increasing
along months-on-book; vintage curve values are between 0 and 1.

Run it. Show me the vintage maturity comparison (default rate at month 12 by
vintage year) and tell me whether underwriting quality improved or deteriorated
over 2010-2013.
```

📊 **WHAT ACTUALLY HAPPENED.** `vintage_curves(df, max_mob=48)` produced the cumulative-default matrix across MOB 0–48 for vintages 2007–2014, plus `vintage_maturity_comparison` at MOB 12, 18, and 24. `roll_rate_proxy(df)` built a status distribution across standardised buckets (Current, In Grace Period, Late 16-30 DPD, Late 31-120 DPD, Default/Charged Off, Fully Paid) by vintage year.

**The finding:** twelve-month default rates fell from **6.56% (2008)** to **3.18% (2013)** while originations grew from 2,393 to 134,755 loans. Roughly a **50% improvement in default rate alongside a ~400× increase in volume**.

📘 **Why the methodology matters as much as the finding.** Raw lifetime rates would have made 2008 look catastrophic and 2014 look pristine, purely from censoring. **Holding month-on-book fixed strips that artefact out.** That control is what makes the claim defensible, and saying so is the point — *"the MOB-12 comparison is the right way to read this, because I controlled for loan age."*

⚠️ **THE ROLL-RATE LIMITATION, stated plainly.** A *true* roll-rate matrix needs monthly panel data — the same loan tracked state to state across time (Current → 30 DPD → 60 DPD → default). Lending Club gives a single snapshot, so a status-distribution proxy was built and labelled as such in the code, the filename, the dashboard footer, and the limitations register. **Knowing the limit of your own data is a senior trait.**

---

## Step 9.2 — Rating transition matrix

🤖 **PROMPT**
```
TASK: Build a rating-grade transition matrix.

Write src/creditrisk/monitoring/transitions.py:

Using the rating grades from the scorecard (Stage 3) and loan outcomes:
1. transition_matrix(df): approximate a grade-to-outcome transition. Since we
   have origination grade and final status (not periodic re-grading), build a
   matrix of: origination rating grade (rows) -> final outcome (Fully Paid,
   Current, Late, Default) as columns, with row-normalised probabilities.
   Save to outputs/tables/transition_matrix.csv and a heatmap to
   outputs/figures/transition_matrix.png
   Document that a true rating-migration matrix needs periodic re-rating; this
   is an origination-grade-to-outcome matrix (a valid and common variant).

2. default_by_grade_summary(df): observed default rate per origination grade,
   with counts, to sit alongside the matrix.

Write tests/test_transitions.py: each row of the matrix sums to 1.0; a
higher-risk grade has a higher default column probability than a lower-risk
grade.

Run it. Show me the transition matrix and confirm the monotonic pattern:
riskier origination grades should have higher default-column probabilities.
```

📊 **WHAT ACTUALLY HAPPENED.** A row-normalised matrix mapping origination grades A–G to final outcomes (Fully Paid, Current, Late, Default). The default-column probability climbed **monotonically A → G**: Grade A landing mostly in Fully Paid / Current, Grade G showing a much fatter default column. Every row summed to 1.0.

📘 **It is the whole model confirmed in one picture** — origination grade genuinely predicts final outcome. The heatmap went straight into the dashboard and the management deck.

**Stage 9 closes.** Job description point #2 — portfolio monitoring and early warning — is answered.

---
---

# STAGE 10 — The dashboard

❓ **THE QUESTION ASKED:** *Which dashboard form?*
**ANSWER CHOSEN:** *Static HTML dashboard — robust, one-click, GitHub-ready.*

**Why that was the right call.** It cannot break. It opens by double-clicking with no server, no Python running, no dependencies. And it drops straight onto GitHub Pages, so a recruiter can *see* it from a link without cloning anything. A Streamlit app is more interactive and requires someone to run a server — which means, in practice, nobody ever sees it.

---

## Step 10.1 — Assemble the dashboard data layer

**First consolidate every output CSV into one clean JSON.** This keeps the HTML simple and means a change upstream requires rebuilding exactly one file.

🤖 **PROMPT**
```
TASK: Build the dashboard data layer. Consolidate all output tables into one
JSON file the dashboard will read. Do not build the HTML yet.

Write src/creditrisk/reporting/dashboard_data.py:

  build_dashboard_json() that reads these existing files from outputs/tables/
  and assembles a single dict, saved to outputs/reports/dashboard_data.json:

    portfolio_headline:
      total_loans, total_ead, total_el, el_rate,
      total_rwa_irb, total_rwa_std, avg_risk_weight,
      total_ecl_ifrs9, total_ecl_cecl, ecl_coverage,
      mean_pd, mean_lgd
    rating_grades:        from rating_grades_model_b.csv
    el_by_grade:          from expected_loss_summary.csv
    capital_by_grade:     from basel_capital_summary.csv
    staging:              from staging_summary.csv
    ecl_by_stage:         from ecl_summary.csv
    framework_comparison: Basel EL vs IFRS9 vs CECL totals
    vintage_curves:       from vintage_curves.csv
    vintage_maturity:     from vintage_maturity_comparison.csv
    transition_matrix:    from transition_matrix.csv
    validation:           model_b gini/ks/auc on train/test/oot
    lifetime_pd:          from lifetime_pd_term_structure.csv

  Every number rounded sensibly. Handle missing files gracefully - if a file is
  absent, log it and skip that section rather than crashing.

Write tests/test_dashboard_data.py: the JSON has all expected top-level keys,
headline numbers are non-null, grade tables have 7-8 rows.

Run it. Show me the portfolio_headline block and confirm all sections loaded.
```

📊 **All 12 sections loaded.** But the headline block came back with this:

```json
{
  "total_loans": 235628,
  "total_ead": 1826572642.48,
  "total_el": 1950.0,          ← WRONG
  "el_rate": 6.72,             ← WRONG
  "total_rwa_irb": 2294666890.82,
  "total_rwa_std": 1369929481.86,
  "avg_risk_weight": 125.63,
  "total_ecl_ifrs9": 278476609.56,
  "total_ecl_cecl": 327465234.95,
  "ecl_coverage": 15.25,
  "mean_pd": 0.1167,           ← WRONG
  "mean_lgd": 0.6333           ← WRONG
}
```

🔴 **THE STALE-CSV BUG.** Total EL of ₹1,950 on a ₹1.83 billion book. Mean LGD of 63% when every other output in the project said 93%.

**Root cause:** `expected_loss_summary.csv` still contained **placeholder output from a 3-loan unit-test run** (count = 3, total_ead = 29,000, total_el = 1,950, mean_pd = 0.1167, mean_lgd = 0.6333). The real portfolio run had never overwritten it. The dashboard builder faithfully read a file that was true, just about the wrong three loans.

📘 **Neither the agent nor the automated tests caught this,** because the tests only asserted that headline values were non-null — not that they were sane. **Only a human looking at the number and thinking "that cannot be right" found it.** This is the clearest example in the whole build of where judgement lives.

## Step 10.3 — The fix

🤖 **PROMPT**
```
TASK: Fix the dashboard headline block - several values are wrong.

The headline currently shows these WRONG values:
  total_el   = 1950.0      -> should be ~58,666,169  (total Expected Loss)
  el_rate    = 6.72        -> should be ~3.21  (EL as % of EAD)
  mean_pd    = 0.1167      -> should be ~0.0345 (portfolio mean PD)
  mean_lgd   = 0.6333      -> should be ~0.9339 (portfolio mean LGD)

Root cause is almost certainly reading the wrong row/column from
expected_loss_summary.csv. Investigate:

1. Open expected_loss_summary.csv and print its exact columns and the TOTAL /
   OVERALL row. Show me what's actually in it.
2. The correct source values are:
     total_el   = the Total EL from expected_loss_summary (the OVERALL row)
     el_rate    = total_el / total_ead * 100
     mean_pd    = portfolio mean predicted PD (should be ~0.0345)
     mean_lgd   = portfolio mean predicted LGD (should be ~0.9339)
   If mean_pd / mean_lgd aren't in the summary CSV, compute them directly from
   the OOT scored portfolio rather than guessing. Pull the real numbers, do
   not hardcode.
3. Re-run build_dashboard_json and confirm the headline block now reads:
     total_el ~ 58.7M, el_rate ~ 3.21%, mean_pd ~ 3.4%, mean_lgd ~ 93%
4. Rebuild risk_dashboard.html with the corrected embedded JSON.

Also double check: the EL-by-grade panel already shows correct grade-level EL,
so cross-check that the corrected total_el equals the SUM of the grade-level
EL values. They must match. Report whether they reconcile.
```

📊 **THE CORRECTED HEADLINE:**

```json
{
  "total_loans": 235628,
  "total_ead": 1826572642.48,
  "total_el": 58666169.31,
  "el_rate": 3.21,
  "total_rwa_irb": 2294666890.82,
  "total_rwa_std": 1369929481.86,
  "avg_risk_weight": 125.63,
  "total_ecl_ifrs9": 278476609.56,
  "total_ecl_cecl": 327465234.95,
  "ecl_coverage": 15.25,
  "mean_pd": 0.0345,
  "mean_lgd": 0.9339
}
```

**And the reconciliation, which is the check that actually matters:**

| Grade | EL |
|---|---|
| A | ₹2,138,197 |
| B | ₹6,793,881 |
| C | ₹15,101,500 |
| D | ₹17,029,660 |
| E | ₹11,436,740 |
| F | ₹4,591,984 |
| G | ₹1,574,216 |
| **Sum** | **₹58,666,169.31** |
| **Reported total** | **₹58,666,169.31** |
| **Difference** | **₹0.00** ✅ |

📘 **Why the reconciliation mattered more than the corrected number.** Anyone can change a number. Proving the corrected total equals the sum of an *independently correct* panel proves the fix is **right**, not merely different.

📘 **And why internal consistency is the credibility test.** The first thing a risk interviewer does with a dashboard is sanity-check the headline against the detail. If the top card says 63% LGD and the panel below says 93%, they stop trusting the entire thing — every other number becomes suspect. Consistency is not cosmetic.

⚠️ **A second, smaller labelling issue.** The header read "As-of: Q4 2024". The data snapshot is January 2016 and the portfolio is the 2014 vintage. A dated label that does not match the data invites an awkward question. Corrected to something like *"Portfolio: 2014 origination vintage | Data as-of Jan 2016"*.

---

## Step 10.2 — Build the dashboard

🤖 **PROMPT**
```
TASK: Build a static HTML risk dashboard from outputs/reports/dashboard_data.json.

First read /mnt/skills/public/frontend-design/SKILL.md and follow its guidance
for a professional, restrained financial dashboard aesthetic (no gradients, no
gimmicks - this is a bank risk dashboard, it should look institutional).

Create outputs/reports/risk_dashboard.html - a SINGLE self-contained file:
  - All CSS inline in a <style> block. No external stylesheets.
  - Charts via Chart.js loaded from cdnjs (the ONE allowed external script).
  - Reads dashboard_data.json. IMPORTANT: since browsers block local file
    fetch, EMBED the JSON directly into the HTML as a JS const at build time
    (read the json, inline it into a <script> const DATA = {...}). So the file
    works by double-clicking with zero server.
  - No localStorage/sessionStorage.

Layout (top to bottom):
  1. Header: title "Retail Credit Risk Portfolio Dashboard", portfolio as-of
     date, and a row of headline metric cards (total EAD, EL, RWA, ECL,
     mean PD, mean LGD).
  2. Section "Risk Segmentation": rating grade table + a bar chart of default
     rate by grade.
  3. Section "Expected Loss & Capital": EL by grade (bar), Basel IRB vs
     Standardised RWA (grouped bar), risk weight by grade.
  4. Section "IFRS 9 Provisioning": staging donut (loans per stage), ECL by
     stage (bar), and the framework comparison (Basel EL vs IFRS9 vs CECL bar).
  5. Section "Portfolio Trends": vintage curves (multi-line), vintage maturity
     at MOB 12 (bar by year), transition matrix (rendered as a heatmap table
     with colour intensity by default probability).
  6. Section "Model Validation": Model B Gini/KS/AUC across train/test/oot
     (grouped bar), and lifetime PD term structure (line).
  Footer: note that CCF is synthetic, roll-rate is a proxy, EAD is approximated
  - the limitations register, shown honestly.

Institutional styling: muted palette, clear typography, generous whitespace,
data-forward. It should look like something shown to a bank risk committee.

Write a small build script src/creditrisk/reporting/build_dashboard.py that
regenerates the JSON then writes the HTML with the JSON embedded.

Run the build.
```

📊 **WHAT ACTUALLY HAPPENED.** `outputs/reports/risk_dashboard.html` — a single self-contained file. Zero web server required; the dataset is embedded inline as `const DATA = {...}`. All styling in one `<style>` block. Charts via Chart.js from a single CDN. Palette: navy `#1e3a8a`, slate `#334155`, muted amber and red accents, clean grid, generous whitespace.

📘 **The one technical constraint worth understanding.** Browsers block `fetch()` of local files (the `file://` CORS restriction) as a security measure. If the HTML tried to read `dashboard_data.json` at runtime by double-click, it would silently fail. **Embedding the JSON at build time** sidesteps this entirely — which is why the file works when emailed, when opened from a USB stick, and when served from GitHub Pages alike.

📘 **And the footer choice.** Putting the limitations register in the dashboard footer — CCF synthetic, roll-rate a proxy, EAD approximated — is the same discipline as the model documentation, applied to the artefact an executive actually looks at. It is the least likely place a candidate would volunteer weaknesses, which is exactly why it lands.

**Stage 10 closes.** A clean, internally-consistent, institutional dashboard.

---
---

# STAGE 11 — The AI analyst

The Infosys/GCP half of the job description, and the one stage with genuine cloud setup.

**What we are building.** An assistant that answers credit-risk questions two ways: by *reading real regulatory documents* (the actual Basel and IFRS 9 texts), and by *calling your own risk engines* as tools. Ask it "what is the IRB risk weight for PD 3% and LGD 90%?" and it runs your `basel_capital_k` function and returns the real number. Ask it "what does IFRS 9 say about SICR?" and it retrieves the relevant passage from the standard and answers grounded in that text, not from memory.

```
                        User question
                       (Gemini routes it)
                      ↙                  ↘
      ┌─────────────────────┐    ┌─────────────────────┐
      │   Retrieval (RAG)   │    │      Tool call      │
      │ searches Basel /    │    │  runs your actual   │
      │  IFRS 9 PDFs        │    │    risk engine      │
      └──────────┬──────────┘    └──────────┬──────────┘
                 ↘                          ↙
                  ┌──────────────────────────┐
                  │     Grounded answer      │
                  │  no hallucinated numbers │
                  └──────────────────────────┘
```

📘 **Why this is the differentiator.** Anyone can bolt a chatbot onto a project. What makes this credible is that the AI is grounded in *authoritative sources* and *calls validated code* — it **cannot hallucinate a risk weight** because it is running your formula, and it **cannot invent regulation** because it is quoting the actual document. That is the RAG (retrieval-augmented generation) pattern, and it is precisely what "AI-augmented risk analytics" means.

❓ **THE QUESTION ASKED:** *Which build for the AI layer — local, or Vertex AI on GCP?*
**ANSWER CHOSEN:** *Option A — local first, upgrade to Vertex later.*

**The reasoning.** Option A uses a free Google AI Studio API key (no GCP project, no service accounts, no `gcloud` CLI) plus local sentence-transformers embeddings and a simple local vector store. Zero cloud infrastructure; works offline once built. Option B — Gemini through Vertex AI — is more impressive to say and uses the cloud credits, but requires enabling APIs, service-account auth, and CLI configuration, which was the one piece of engineering not yet touched and the most likely to snag. **Building it working locally first means a cloud problem cannot block the whole stage;** the Vertex swap is then roughly a twenty-line change.

---

## Step 11.1 — Get the regulatory documents

Done by hand — downloading public PDFs into `retail-credit-risk/knowledge_base/`:

1. **Basel III finalisation** — search *"Basel III finalising post-crisis reforms bis.org d424"* → PDF from bis.org. Contains the IRB formulas and retail correlation curves.
2. **Basel II comprehensive framework** — search *"Basel II international convergence bis.org bcbs128"* → bis.org. Contains the PD/LGD/EAD definitions.
3. **IFRS 9 project summary** — search *"IFRS 9 financial instruments project summary ifrs.org"* → ifrs.org. The full standard is paywalled; the project summary and impairment documents are public and cover ECL/staging.
4. **BCBS guidance on credit risk and expected credit losses** — search *"BCBS guidance credit risk expected credit losses bis.org d350"* → bis.org, on ECL and SICR.

💻 **VERIFY**
```powershell
cd "D:\0000_after portfolio_24726\0_vizier\vizier\retail-credit-risk"
Get-ChildItem knowledge_base -File | Select-Object Name, @{N='MB';E={[math]::Round($_.Length/1MB,1)}}
```

📊 **RESULT**
```
Name                           MB
----                           --
bcbs128.pdf                   1.8
d350.pdf                      0.5
d424.pdf                      2.9
project-summary-july-2014.pdf 0.1
```

---

## Step 11.2 — Build the retrieval index

🤖 **PROMPT**
```
TASK: Build a local RAG index over the regulatory PDFs in knowledge_base/.
This is fully local - no cloud, no API keys needed for this step.

You will need these packages (tell me before installing):
  pypdf (read PDFs), sentence-transformers (local embeddings),
  numpy (already have it). Do NOT use any paid/cloud service here.

Write src/creditrisk/ai/rag_index.py:

1. load_documents(kb_dir) -> reads every PDF in knowledge_base/, extracts text
   page by page. Returns a list of {source, page, text} records. Skip pages
   with under 50 characters (blank/image pages).

2. chunk_documents(records, chunk_size=800, overlap=150) -> splits each page's
   text into overlapping character chunks so retrieval returns focused
   passages. Keep source + page on every chunk. Return list of chunks with a
   unique chunk_id.

3. build_embeddings(chunks) -> uses sentence-transformers model
   "all-MiniLM-L6-v2" (small, fast, runs on CPU, no download cost) to embed
   every chunk. Store as a numpy array.

4. Save the index to outputs/models/rag_index/: the chunks as JSON and the
   embedding matrix as .npy. Add build_index(kb_dir) that runs the whole
   pipeline and reports: n documents, n pages, n chunks, embedding dimension.

Write src/creditrisk/ai/retriever.py:
   Retriever class that loads the saved index and has
   search(query, k=5) -> top k chunks by cosine similarity to the query
   embedding, each with source, page, text, score.

Write tests/test_rag.py: chunking preserves source/page, chunk overlap works,
retriever returns k results sorted by score, a query about "risk weight"
retrieves a Basel chunk not an IFRS 9 chunk.

Run build_index then test a query. Show me: the index stats (docs/pages/chunks)
and the top 3 results for the query "how is the IRB risk weight calculated".
Print each result's source, page, score, and first 200 chars.
```

📘 **CONCEPT — what a RAG index actually is, in plain terms.**

**Chunking.** A 500-page PDF is too long to hand a language model. Split it into ~800-character pieces with 150 characters of overlap. The overlap matters: without it, a sentence straddling a boundary is cut in half and neither piece makes sense.

**Embedding.** Each chunk is converted into a vector of numbers — here 384 dimensions — such that chunks with similar *meaning* end up near each other in that space. The model `all-MiniLM-L6-v2` is small (~90 MB), fast, runs on CPU, and costs nothing.

**Retrieval.** A question is embedded the same way, then compared to every chunk by **cosine similarity** (the angle between vectors). The top-k closest chunks are the ones most likely to answer it. No keyword matching — this is why "how is the risk weight calculated" retrieves the formula even if the page never uses the word "calculated".

⚠️ **A practical note:** the first `sentence-transformers` install downloads the model once, and the first embedding run is slow (a few minutes on CPU for a few thousand chunks). That is normal. It is building the index once; afterwards it is fast forever. If it seems to hang, it is downloading — let it finish.

📊 **WHAT ACTUALLY HAPPENED**

**4 documents, 511 pages, 1,774 chunks, 384-dimensional vectors.** Tests passing.

The test query *"how is the IRB risk weight calculated"* returned, as its **#2 hit**, the actual Basel risk-weight formula — `RW = [LGD × N[(1-R)^-0.5 × G(PD) + ...]]` — from **bcbs128.pdf page 65**.

📘 **That is the exact formula implemented in Stage 7, retrieved from the source document.** The RAG can now ground answers in real regulation.

---

## Step 11.3 — Wire the assistant

**Get a Gemini API key (two minutes, no GCP project):**
1. Go to **aistudio.google.com/apikey**
2. Sign in with a Google account
3. **Create API key** → copy it
4. This is the free AI Studio key — separate from GCP credits, no billing setup

🤖 **PROMPT**
```
TASK: Build the AI credit-risk analyst. It answers two kinds of questions:
regulatory (via RAG over the index) and quantitative (by calling our own risk
engine functions as tools). Local Gemini via google-generativeai.

You will need the package google-generativeai (tell me before installing).

The API key must NOT be hardcoded. Read it from an environment variable
GEMINI_API_KEY. Add a note that the user sets it in PowerShell with:
  $env:GEMINI_API_KEY="their-key"
Also add GEMINI_API_KEY to .gitignore-safe handling - never write it to any file.

Write src/creditrisk/ai/tools.py - thin wrappers exposing our REAL engines as
callable tools, each with a clear docstring and typed args:
  tool_basel_capital(pd, lgd, ead) -> calls basel_capital_k + risk_weighted_assets,
    returns K, risk_weight, RWA
  tool_expected_loss(pd, lgd, ead) -> returns EL = pd*lgd*ead
  tool_ifrs9_ecl(pd_12m, lifetime_pd, lgd, ead, stage) -> returns staged ECL
  tool_score_to_pd(score) -> looks up the rating grade + observed default rate
    for a given scorecard score from rating_grades_model_b.csv
Each tool returns a dict. These call the ACTUAL functions from
creditrisk.regulatory - do not reimplement the maths.

Write src/creditrisk/ai/analyst.py - a CreditRiskAnalyst class:
  - Loads the Retriever (from 11.2) and configures Gemini.
  - ask(question) does this:
      1. Retrieve top-5 chunks from the RAG index for the question.
      2. Build a prompt: a system instruction saying "You are a credit risk
         analyst assistant. Answer using ONLY the provided regulatory context
         and the calculation tools. Cite the source document and page for
         regulatory claims. If you don't have the context, say so - never
         invent regulatory text or numbers."
      3. Pass the retrieved context + the tool definitions to Gemini and let
         it either answer from context or call a tool.
      4. Return the answer plus the list of sources (doc + page) used.
  - Guardrail: if retrieval scores are all below 0.3, tell the user the
    knowledge base doesn't cover this rather than guessing.

Write src/creditrisk/ai/run_analyst.py - a simple CLI loop: type a question,
get an answer with sources. Type 'quit' to exit.

Write tests/test_analyst.py that MOCKS the Gemini call (no real API in tests):
verify tools return correct maths (tool_expected_loss(0.03,0.9,10000)==270),
verify retrieval is invoked, verify a tool call routes to the right function.

Do NOT run the live CLI yourself. Build it, run the mocked tests, and then give
me the exact PowerShell commands to set the key and run run_analyst.py myself.
```

📊 **WHAT ACTUALLY HAPPENED — the mocked tests:**

```
test_tool_expected_loss:          PASSED   (tool_expected_loss(0.03, 0.9, 10000) == 270.0)
test_tool_basel_capital:          PASSED
test_tool_ifrs9_ecl:              PASSED
test_tool_score_to_pd:            PASSED
test_analyst_guardrail_low_score: PASSED
test_tool_call_routing:           PASSED

Summary: 6 passed in 10.45s
```

📘 **THREE DESIGN DECISIONS WORTH UNDERSTANDING.**

**The key is never in code.** It is read from an environment variable, set per-terminal-session with `$env:GEMINI_API_KEY="..."`. It is never written to a file, never committed, and does not persist across terminal windows (which is a feature, not an annoyance). The single most common way people leak credentials is committing them; this makes it structurally impossible.

**The tools call the real engines.** `tool_basel_capital` invokes the *actual* `basel_capital_k` from `creditrisk.regulatory`. It does not reimplement the maths. This is what makes the number trustworthy: the assistant is a *front end to validated code*, not a language model guessing at arithmetic.

**The relevance guardrail.** If every retrieved chunk scores below 0.30 cosine similarity, the assistant says the knowledge base does not cover the question rather than answering from the model's general memory. This is the anti-hallucination control, and it is the difference between a grounded system and a chatbot with a document theme.

---

## Step 11.4 — The 404, and the fix

💻 **RUN IT LIVE**
```powershell
cd "D:\0000_after portfolio_24726\0_vizier\vizier\retail-credit-risk"
.\.venv\Scripts\Activate.ps1
$env:GEMINI_API_KEY="paste-your-real-key-here"
.\.venv\Scripts\python.exe -m creditrisk.ai.run_analyst
```

🔴 **WHAT CAME BACK**

```
===========================================================================
 RETAIL CREDIT RISK AI ANALYST (RAG & FUNCTION CALLING ENGINE)
 Model: gemini-1.5-flash | Local Vector Index: outputs/models/rag_index/
===========================================================================
Analyst > What is the Expected Loss and Basel capital requirement for a loan
          with PD of 3.5%, LGD of 45%, and EAD of 250000?

Gemini API invocation error: 404 models/gemini-1.5-flash is not found for API
version v1beta, or is not supported for generateContent.

ANSWER:
API Error: 404 models/gemini-1.5-flash is not found...

CITATIONS / SOURCES:
 - d424.pdf   (Page 69)  [relevance score: 0.6918]
 - d424.pdf   (Page 100) [relevance score: 0.6724]
 - d424.pdf   (Page 64)  [relevance score: 0.6467]
 - bcbs128.pdf(Page 81)  [relevance score: 0.6465]
 - d424.pdf   (Page 67)  [relevance score: 0.6399]
```

📘 **Read that output carefully, because it is more informative than a clean success would have been.**

**The retrieval half already worked perfectly.** Both test questions pulled exactly the right pages — bcbs128 page 90 for retail risk-weight functions, d424 for the capital pages — with strong relevance scores. Only the *generation* step failed.

**The cause:** `gemini-1.5-flash` had been retired. Model names are not stable; providers deprecate them on their own schedule.

**And note what this proved about the tests.** All six mocked tests passed, and the live call immediately 404'd. **Mocked means the model was faked.** The plumbing was correct — tools, routing, guardrail, retrieval — and the actual API connection was untested. This is the concrete case for why "I ran it and here is the output" is a different claim from "the tests pass."

🤖 **THE FIX PROMPT**
```
TASK: The Gemini model "gemini-1.5-flash" is deprecated and returns 404. The
retrieval half of the analyst already works (citations return correctly) - only
the model name needs updating.

1. In analyst.py, change the model name from "gemini-1.5-flash" to
   "gemini-flash-latest" (this is the current always-available alias per
   Google's docs). Put the model name in config/ai.yaml as
   gemini_model: "gemini-flash-latest" and read it from there, so it's easy to
   change later without touching code.

2. Add a small helper that, if the configured model 404s, calls the API's
   list_models and prints the available models that support generateContent, so
   the user can pick a working one. This makes the tool robust to future model
   name changes.

3. Do NOT run the live API yourself. Just make the change, confirm the mocked
   tests still pass, and give me the PowerShell commands to re-run the CLI.
```

📘 **Two things about that fix are the real lesson.**

**The model name moved into config.** A future deprecation is now a one-line YAML edit, not a code change. Volatile external identifiers belong in configuration.

**The self-diagnosing fallback.** If the configured model 404s, the code calls `list_models()` and prints what *is* available. The next failure tells you its own fix. Different regions and key vintages expose different model sets, so list-and-pick is the reliable pattern.

📊 **WHAT ACTUALLY HAPPENED AFTER THE FIX — both halves working live.**

**Question 1 (tool-calling):** *"What is the Expected Loss and Basel capital requirement for a loan with PD of 3.5%, LGD of 45%, and EAD of 250000?"*

It called the actual Basel engine. **EL = ₹3,937.50** (0.035 × 0.45 × 250,000, exact), then **K = 0.0513** and **RWA = ₹160,198** from `basel_capital_k` — **and** it cited **d424.pdf page 69** for the PD floor, confirming that 3.5% clears the 0.05% minimum. A computed answer grounded in a retrieved regulation, in one response.

**Question 2 (retrieval):** *"What does Basel say about the risk-weight function for retail exposures?"*

It correctly explained the **three retail risk-weight functions**, the **QRRE R = 0.04 versus Other Retail PD-dependent correlation** distinction (the exact distinction from the Stage 7.4 bug fix), the **no-maturity-adjustment** rule for retail, and the PD floors — every claim cited to a specific document and page. It even surfaced the defaulted-exposure K formula.

**The architecture is proven: retrieval for regulation, tools for calculation, sources on everything.**

⚠️ **One warning to ignore.** `google.generativeai` emits a deprecation notice pointing at the newer `google.genai` library. It is a yellow warning, not an error; the library works. Migrating is a nice-to-have noted in the docs, not a blocker.

---
---

# STAGE 12 — Documentation and the management deck

The last stage, and the one that converts a codebase into something you *talk through* in an interview. Two deliverables, both answering the job description's "present to senior management" bullet.

❓ **THE QUESTION ASKED:** *What format for the documentation pack and management deck?*
**ANSWER CHOSEN:** *Markdown only — keep it simple.*

**Why that was right.** Markdown is version-controllable, renders beautifully on GitHub, needs no extra libraries, and diffs cleanly. A Word document and a PowerPoint deck look more "finished" but are binary blobs that git cannot diff and that nobody reads on a phone.

---

## Step 12.1 — The model documentation pack

🤖 **PROMPT**
```
TASK: Write the model documentation pack as markdown. This is an SR 11-7 style
model development document. Read the actual numbers from outputs/tables/ and
outputs/reports/dashboard_data.json - do NOT invent figures, pull the real ones.

Create docs/MODEL_DOCUMENTATION.md with these sections:

1. Executive Summary - one paragraph: what the model suite is (PD/LGD/EAD ->
   Basel capital + IFRS 9 ECL for a retail unsecured portfolio), the data
   (Lending Club 2007-2014, 466k loans), and headline results (portfolio EL,
   RWA, ECL).

2. Model Purpose & Scope - what each model does, intended use, and explicit
   out-of-scope statements.

3. Data - source, size, the 12-month target definition and WHY (cite the
   snapshot/last_pymnt_d proxy), the train/test/OOT split, leakage controls
   (the schema.py guard).

4. PD Model - methodology (WoE/IV binning, logistic regression), Model A vs
   Model B, the decision to deploy Model B, final feature list, coefficient
   signs, scorecard scaling, rating grades. Include the actual validation
   table (Gini/KS/AUC/HL on train/test/oot) and the calibration finding
   (Model A OOT calibration failure -> Model B deployed).

5. LGD Model - two-stage hurdle, Basel EAD-based definition, portfolio
   calibration result (~93% mean, predicted vs actual).

6. EAD & CCF - term-loan EAD, the synthetic CCF demonstration clearly labelled.

7. Basel Capital - Other Retail IRB formula, the reference verification, IRB
   vs Standardised RWA comparison, downturn LGD, actual RWA/capital numbers.

8. IFRS 9 ECL - staging, SICR rules, lifetime PD term structure, ECL by stage,
   macro scenarios, IFRS9 vs Basel EL vs CECL comparison with actual numbers.

9. Monitoring - PSI/CSI results, vintage curves finding, transition matrix.

10. AI Analyst - RAG over Basel/IFRS 9 docs + tool-calling architecture.

11. Limitations & Assumptions Register - a clear numbered list: EAD is
    approximated, CCF is synthetic, default timing is a proxy, roll-rate is a
    proxy, single-snapshot data, Model A calibration instability. Be honest and
    complete - this section is a strength, not a weakness.

12. Validation Summary & Governance - how the models were tested, what a real
    deployment would need next (independent validation, ongoing monitoring
    cadence, recalibration triggers).

Write in clear professional prose. Use tables for the numeric results. Keep it
accurate to what was actually built. After writing, tell me the total length
and confirm every number was pulled from an output file, not invented.
```

✅ **WHAT GOOD LOOKS LIKE:** a substantial document (15–25 pages equivalent) where **every figure traces to a real output file**. The Limitations register is the part that signals seniority.

---

## Step 12.2 — The management deck and README

🤖 **PROMPT**
```
TASK: Write the management presentation deck and the project README as markdown.
Pull real numbers from the output files - do not invent.

PART 1 - Create docs/MANAGEMENT_DECK.md structured as presentation slides
(use "---" between slides, each slide a heading + tight bullet points, the way
a credit committee deck flows). ~12-15 slides:

  Slide 1: Title - Retail Credit Risk Analytics Suite
  Slide 2: The portfolio at a glance (loans, EAD, headline EL/RWA/ECL)
  Slide 3: Approach - the PD/LGD/EAD -> Basel + IFRS 9 pipeline
  Slide 4: Risk segmentation - rating grades, default rate gradient
  Slide 5: PD model - performance and the Model A/B honesty story
  Slide 6: LGD & EAD - unsecured reality (93% LGD), key findings
  Slide 7: Basel capital - RWA, the IRB vs Standardised insight
  Slide 8: IFRS 9 provisioning - staging, ECL, the CECL contrast
  Slide 9: Portfolio trends - underwriting improved 2010-2013, vintage story
  Slide 10: The AI analyst - grounded regulatory Q&A + live calculations
  Slide 11: Key insights (3-4 headline takeaways an interviewer remembers)
  Slide 12: Limitations & next steps (honest)
  Slide 13: Tech stack & reproducibility

  Make the insights slide strong - the memorable findings: IRB costs MORE than
  Standardised for high-LGD unsecured books; 52% of defaults are total losses;
  underwriting tightened ~50% post-crisis; grade absorbs borrower fundamentals.

PART 2 - Rewrite README.md as the repo front door:
  - One-line description, the headline results, an architecture overview
  - How to reproduce: setup (venv, pip install -e .), the pipeline run order,
    where outputs land, how to open the dashboard, how to run the AI analyst
  - A "project structure" tree
  - A clear statement of what's real vs illustrative (CCF synthetic etc.)
  - Link to MODEL_DOCUMENTATION.md and the dashboard

After writing both, show me the insights slide (slide 11) and the README
headline section so I can check the framing.
```

📊 **WHAT ACTUALLY HAPPENED — Slide 11, Key Insights, exactly as written:**

> **1. IRB costs more than Standardised for high-LGD unsecured books — and that is correct.**
> The IRB approach produces $2.29B RWA vs $1.37B under the Standardised flat 75% weight — a +50.6 percentage point premium. This is not a model artefact. With mean LGD of 93.4%, the supervisory IRB formula correctly prices the concentration of loss-given-default risk that the Standardised approach ignores. A bank adopting the Standardised approach for this product is structurally undercapitalised relative to the economic risk.
>
> **2. 52% of unsecured defaults are total losses — provisioning must reflect this.**
> Of 50,968 resolved defaults, 52.2% have LGD = 1.0 (complete write-off). The median LGD is 1.0. IFRS 9's Stage 3 coverage of 93.25% is not conservative — it is the empirical outcome.
>
> **3. Underwriting tightened approximately 50% post-crisis, but scale grew 400×.**
> 12-month default rate fell from 6.56% (2008) to 3.18% (2013) while originations grew from 2,393 to 134,755. Default rates fell as volume surged — evidence of systematic underwriting discipline.
>
> **4. The borrower's grade already contains their fundamentals — additional variables add margin, not revolution.**
> The two highest-IV variables are grade (IV 0.294) and int_rate (IV 0.277) — both set by the lender. The remaining 8 variables together add ~13 Gini points (0.2715 → 0.3845). Useful, but the platform's own grade is already a strong sufficient statistic.

⚠️ **ONE CONSISTENCY ISSUE FLAGGED IN REVIEW.** The deck expresses the IRB/Standardised gap as "+50.6 percentage points" (on risk weights: 125.6% − 75%) while other places express it as a ratio ("67% higher": 2.29B ÷ 1.37B). **Both are correct, but they are two different ways of expressing the same gap, and a sharp reader will notice.** The recommendation was to pick one framing and use it everywhere — preferably *"IRB RWA is 67% higher (₹2.29B vs ₹1.37B)"*, since a ratio is cleaner than a percentage-point difference on risk weights.

📘 **Why that tiny inconsistency is worth a paragraph in a textbook.** It is exactly the sort of thing a credit committee catches. Two numbers describing the same fact, both true, presented differently in two places, reads as carelessness — and carelessness in presentation invites doubt about the analysis. **Pick one framing and hold it.**

---
---

# STAGE 13 — GitHub and publication

🤖 **PROMPT**
```
TASK: Prepare the repo for GitHub and make the first commit.

1. Run: git status  -- confirm no CSV, no .venv, no knowledge_base PDFs, no
   GEMINI_API_KEY appear. If any do, fix .gitignore first and show me.
2. Confirm .gitignore excludes: data/, datasets/, knowledge_base/, .venv/,
   outputs/models/, *.csv, *.pdf, .env, __pycache__/. Keep the dashboard HTML
   and the output TABLES (small CSVs are fine to commit if you want the
   dashboard to render on GitHub Pages - tell me which you prefer).
3. Stage everything, commit with message "Retail credit risk analytics suite:
   Basel IRB + IFRS 9 ECL + AI analyst".
4. Give me the exact commands to create a GitHub repo and push (I'll create the
   repo on github.com myself and paste you the URL).

Do NOT push yourself - just prepare the commit and give me the push commands.
```

📊 **WHAT ACTUALLY HAPPENED — the `.gitignore` audit found four problems:**

| Item | Before | After |
|---|---|---|
| `knowledge_base/` PDFs | ❌ not excluded — would have committed 5.3 MB of PDFs | ✅ excluded |
| `*.pdf` | ❌ not excluded | ✅ excluded |
| `*.egg-info/` | ❌ not excluded (pip artefact) | ✅ excluded |
| `outputs/tables/*.csv` | ❌ blocked by `*.csv` — would have omitted **all** output tables | ✅ re-allowed via `!outputs/tables/*.csv` |
| `.venv/`, `data/`, `datasets/`, `outputs/models/`, `.env`, key | ✅ already correct | ✅ kept |

**Security confirmation: zero hits on PDFs, `.venv`, `data/`, `datasets/`, `outputs/models/`, `.env`, or `GEMINI_API_KEY` in the staged tree.**

**Commit `306a869` — 139 files, 13,017 insertions.**

📘 **The `!outputs/tables/*.csv` exception is the interesting decision.** The blanket `*.csv` rule blocks the 228 MB raw dataset. The negation re-allows the small summary tables. **That is what lets the dashboard render on GitHub Pages so a recruiter can see it without cloning anything** — the raw borrower data stays out, only the aggregated results go in.

💻 **THE PUSH**
```powershell
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
git branch -M main
git push -u origin main
```

**Before running:** on github.com → New repository → name it `retail-credit-risk` → **Public** → **do not** tick "Add a README" or "Add .gitignore" (you have both; adding them creates a conflict) → Create.

**What you will see:** it uploads the 139 files (may pause on larger CSVs — normal), ending with `main -> main`. If a browser opens asking you to authorise Git with GitHub, say yes — normal first-time login.

🔴 **If it asks for a password:** GitHub no longer accepts account passwords on the command line. It wants a **Personal Access Token**. Typing your account password will fail.

💻 **THEN — GitHub Pages, two minutes, highest leverage in the project**
1. Repo → **Settings** → **Pages**
2. Source: **main** branch, **/ (root)** → Save
3. Wait ~1 minute

Live at: `https://yourname.github.io/repo-name/outputs/reports/risk_dashboard.html`

**That link goes on the CV and in emails to recruiters.** They click, they see an institutional risk dashboard, before you have said a word.

---

## The project, complete

**The full Basel + IFRS 9 stack** — 12-month PD scorecard (two models, honestly compared), two-stage LGD, term-loan EAD with labelled synthetic CCF, Expected Loss, IRB capital verified against reference values, and the complete IFRS 9 ECL engine with staging, lifetime PD, macro scenarios, and CECL contrast.

**A validation battery** that caught a real calibration failure and a real structural data shift.

**Portfolio monitoring** — vintage curves, roll-rate proxy, transition matrix.

**An institutional dashboard**, internally reconciled to the cent.

**A grounded AI analyst** doing live RAG over real Basel PDFs and calling the project's own validated engines.

**Full documentation** — an SR 11-7 pack, a management deck, and a reproducible README.

**39 passing tests. 139 files. 13,017 lines.**

Every bullet on the HDFC CPRA job description is answered by working, tested, documented code.
---
---

# PART V — THE ERROR REGISTRY

Every error encountered in this build, plus the standard ones you are likely to hit rebuilding it. **When something breaks, look here first.** Errors are information, not failure.

---

## V.1 — The errors that actually occurred in this project

### E1 — Git was tracking a 228 MB file

**Symptom.** Source control panel showing 32 pending changes; `git status` listing `loan_data_2007_2014.csv`.

**Cause.** `.gitignore` excluded `data/` but the CSV was in `datasets/`.

**Why it was urgent.** Git stores every version of every file forever, so committing once bloats the repository permanently. GitHub hard-rejects files over 100 MB, so the push would fail outright. Undoing it requires rewriting history. And separately: raw borrower records do not belong in a code repository at all.

**Fix.** Add `datasets/` to `.gitignore` **before the first commit**. Verify with `git status` that the CSV no longer appears.

**Prevention.** Write `.gitignore` before you put any data on disk, not after.

---

### E2 — Third-party course material inside the repo

**Symptom.** A `365_course_files/` folder sitting inside the project.

**Why it mattered.** Publishing someone else's paid course notebooks as part of your portfolio is both an intellectual-property problem and a credibility problem — it invites the question "how much of this is yours?"

**Fix.** Move it off the project entirely. Keep it as reference material elsewhere on the drive.

---

### E3 — `ModuleNotFoundError: No module named 'creditrisk'`

**Cause.** The agent referenced `pip install -e .` before `pyproject.toml` existed, so the package was never installed.

**Fix, in diagnostic order:**
1. Is `(.venv)` showing in your prompt? If not, `.\.venv\Scripts\Activate.ps1`
2. Does `pyproject.toml` exist at the project root?
3. Run `pip install -e .` from the project root, inside the venv.

---

### E4 — The 1916 date rollover 🔴 **the most instructive bug in the build**

**Symptom.** 782 loans with `months_to_default` of approximately **−1140**.

**Cause.** Dates are stored as `%b-%y`. Pandas reads two-digit year `68` as **2068**. The first fix subtracted 100 years from any parsed year `> 2015` — which correctly mapped `Dec-68 → 1968-12`, but **also** converted `Jan-16` (a perfectly valid January 2016 `last_pymnt_d`) into **1916-01**. Adding the 3-month DPD lag produced 1916-04, and the resulting negative durations.

**Fix.** Raise the century-rollover threshold from `> 2015` to **`> 2049`**. `Dec-68` still maps to 1968; `Jan-16` correctly stays 2016. Anomalies dropped from 782 to **zero**.

**Why it is the most instructive error here.** No crash. No exception. No stack trace. Just quietly wrong numbers that would have silently corrupted the seasoning curve, the lifetime PD term structure, and every IFRS 9 number downstream. **It was found only because the reconciliation bridge counted anomalies as an explicit line item.** Build the check that would catch the bug you have not thought of.

---

### E5 — The wrong LGD denominator

**Symptom.** LGD distribution looked implausibly favourable; no spike at 1.0.

**Cause.** Loss was measured against the **original loan amount**, treating principal repaid before default as if it were recovery.

**Fix.** Redefine against **exposure at default**:
```
ead_approx = max(funded_amnt - total_rec_prncp, 0)
loss       = max(ead_approx - recoveries, 0)
lgd        = loss / ead_approx        # clipped [0,1]
```

**Result of the fix.** Mean LGD moved to the correct **93.01%**, with the true 52.18% spike at total loss appearing. **The corrected number is far worse and far more honest.**

---

### E6 — Three of four Basel reference tests failed

**Symptom.** `test_basel_reference.py` — code produced R = 0.1216 at PD = 0.01 against a benchmark of 0.0356.

**Cause.** The reference values supplied were **QRRE** (fixed correlation 0.04), while the prompt requested and the code correctly implemented **Other Retail** (PD-dependent 0.03 → 0.16). The benchmark was mismatched to the formula.

**Fix.** **Fix the test, not the formula.** Lending Club term instalment loans are unambiguously Other Retail. R = 0.1216 at PD = 0.01 was verified by hand and hard-coded as the correct regression guard. The Other Retail vs QRRE distinction was documented in the module docstring.

**Why this was a win.** It caught the mismatch *before* wrong numbers propagated into every capital figure, and it forced a real Basel distinction into the open.

---

### E7 — The stale CSV in the dashboard headline

**Symptom.** Dashboard headline showing `total_el = 1950.0` on a ₹1.83 billion book, and `mean_lgd = 0.6333` when every other output said 0.9339.

**Cause.** `expected_loss_summary.csv` still contained placeholder output from a **3-loan unit-test run**. The real portfolio run had never overwritten it. The dashboard builder read the file faithfully.

**Fix.** Re-run `run_expected_loss.py` on the full OOT portfolio, rebuild the JSON, rebuild the HTML. Then **verify by reconciliation**: the corrected total EL must equal the sum of the (already correct) grade-level EL panel. It did, to the cent — ₹58,666,169.31.

**Why neither the agent nor the tests caught it.** The tests asserted only that headline values were *non-null*, not that they were *sane*. **Only a human looking at ₹1,950 and thinking "that cannot be right" found it.**

**Prevention.** Add magnitude assertions to tests where you know the plausible range — e.g. `assert 0.5 < mean_lgd < 1.0`, `assert total_el > 1e6`.

---

### E8 — Gemini `404 model not found`

**Symptom.**
```
Gemini API invocation error: 404 models/gemini-1.5-flash is not found for API
version v1beta, or is not supported for generateContent.
```

**Cause.** `gemini-1.5-flash` had been retired. Model names are not stable identifiers.

**Fix, three parts:**
1. Change the model name to `gemini-flash-latest` (an always-current alias).
2. **Move the name into `config/ai.yaml`** so a future deprecation is a config edit, not a code change.
3. Add a fallback helper that, on a 404, calls `list_models()` and prints the models available to this key that support `generateContent`. The next failure now tells you its own fix.

**The wider lesson.** All six mocked tests passed and the live call immediately 404'd. **Mocking proves the plumbing, not the connection.**

---

### E9 — The agent overstated a failing result

**Symptom.** After dropping the unstable variables, Model A's OOT Hosmer–Lemeshow moved from 2.11 × 10⁻¹⁵ to 3.08 × 10⁻⁷. The agent reported this as *"improved by over 10⁸×!"* and framed it as a fix.

**Why it was wrong.** 10⁻⁷ is nowhere near the 0.05 threshold. **A large relative improvement in a failing metric is not a pass.**

**Fix.** Human judgement. The correct read was that the variable drop helped enormously and did not fix the problem, which then drove the Step 4.4 recalibration work and, ultimately, the correct diagnosis (shape, not level).

**The pattern.** The agent is strong at writing code to a specification and weak at judging whether a result is *sensible*. Judgement stays with you.

---

### E10 — Inconsistent framing of the same number

**Symptom.** The management deck said "+50.6 percentage points" (risk weights: 125.6% − 75%); other documents said "67% higher" (RWA: 2.29B ÷ 1.37B).

**Why it matters.** Both are correct and they describe the same gap two different ways. A sharp reader notices, and inconsistency in presentation invites doubt about the analysis.

**Fix.** Pick one framing and hold it everywhere — *"IRB RWA is 67% higher (₹2.29B vs ₹1.37B)"* is cleaner than a percentage-point difference on risk weights.

---

## V.2 — Standard errors you are likely to hit

| Error | Cause | Fix |
|---|---|---|
| `'python' is not recognized` | Not installed, or not on PATH | Reinstall from python.org, **tick "Add python.exe to PATH"**, close and reopen the terminal |
| `running scripts is disabled on this system` | Windows execution policy | `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`, answer `Y` |
| `No module named pandas` / `pytest` | Not inside the venv, or not installed | Check for `(.venv)` in the prompt; activate; `pip install -r requirements.txt` |
| `No module named creditrisk` | Package not installed editable | `pip install -e .` from the project root, inside the venv |
| `cd` fails on a path with spaces | Missing quotes | `cd "D:\path with spaces\folder"` |
| `FileNotFoundError` on a CSV | Wrong working directory | `pwd` to check; paths in the code are relative to the project root |
| Pandas reads dates as 2068 | Two-digit year ambiguity | Rollover threshold at year > 2049 (see E4) |
| `ValueError: Bin edges must be unique` | Too many identical values for the requested quantiles | Reduce bin count, or use `duplicates="drop"` in `pd.cut` |
| `ln(0)` / infinite WoE | A bin with zero goods or zero bads | Laplace smoothing — add 0.5 to each cell before computing proportions |
| Negative Gini | Score direction flipped | The metric expects **probability of default** (higher = worse), not a credit score (higher = better) |
| `429` rate limit from Gemini | Free tier allows only a few requests per minute | Wait 30 seconds between questions |
| `API key not valid` | Key not set in *this* terminal window | `$env:GEMINI_API_KEY="..."` does not persist across windows — re-run it |
| Dashboard shows no data on double-click | Browser blocks local `fetch()` | The JSON must be **embedded** in the HTML at build time, not fetched at runtime |
| `sentence-transformers` seems to hang | First run downloads a ~90 MB model | It is downloading. Let it finish. |
| GitHub push rejected, file too large | A file over 100 MB got committed | Fix `.gitignore`, then rewrite history — far easier to prevent than to fix |
| Push asks for a password | GitHub disabled password auth | Generate a Personal Access Token in Settings → Developer settings |

---
---

# PART VI — THE LIMITATIONS REGISTER

**This is the most valuable section in the whole project.**

📘 **Why.** Inexperienced candidates hide weaknesses. Experienced risk professionals lead with them. A validator who *discovers* an undisclosed limitation concludes the developer either did not know or was concealing — both fatal. A validator who reads a thorough register concludes the developer understands their own model better than the validator does.

**Get there first. Every time.**

---

### L1 — EAD is reconstructed, not observed

**What.** EAD is computed as `funded_amnt − total_rec_prncp` rather than read from a balance field at the moment of default.

**Why.** The dataset contains no month-by-month balance history and no observed default-date balance.

**Impact.** `total_rec_prncp` may include minor *post*-default principal repayments, which would slightly understate the true exposure at default. The direction of the bias is known; the magnitude is not.

**Mitigation.** The identical definition is used in both `lgd_data.py` and `ead_model.py`, with cross-referencing code comments, so LGD and EAD remain arithmetically consistent even if both are approximate.

**What a real implementation would do.** Read the outstanding balance from the loan servicing system as at the default date.

---

### L2 — CCF is a labelled synthetic demonstration

**What.** The Credit Conversion Factor module is fitted on a **simulated** revolving sub-portfolio, not real data.

**Why.** Lending Club loans are term instalment loans with no credit limit and no undrawn amount. There is nothing to convert.

**Impact.** The CCF numbers demonstrate methodology only. They carry **no information about any real portfolio**.

**Mitigation.** Every output file is prefixed `SYNTHETIC_`; every table carries a header declaring it a demonstration; the module docstring states it in plain terms; it appears in the dashboard footer, the model documentation, and the management deck.

**Why this is a strength.** Claiming a CCF model on term-loan data would be an overclaim any credit interviewer catches immediately. Demonstrating the methodology while stating the data cannot support fitting it is the credible position.

---

### L3 — Default timing is a proxy

**What.** `est_default_date = last_pymnt_d + 3 months`.

**Why.** The dataset records a *current status* at extraction, not a default date. The three-month lag approximates the time from missed payment to 90 DPD.

**Impact.** Affects the seasoning curve, the lifetime PD term structure, and therefore every IFRS 9 Stage 2 number. A loan that made partial payments before failing will have its default date placed too late.

**Mitigation.** The lag is in `config/target_definition.yaml` and can be varied. A reconciliation bridge counts anomalies (zero after the E4 fix). The empty 2–3 month bucket is a known arithmetic consequence, documented.

**What a real implementation would do.** Read the actual default flag date from the collections system.

---

### L4 — Roll rates are a status-distribution proxy

**What.** A true roll-rate matrix requires monthly panel data — the same loan tracked Current → 30 DPD → 60 DPD → default. Only a snapshot exists.

**Impact.** The "roll rate" table shows the *distribution of current statuses by vintage*, not actual transitions. It cannot be used as a genuine early-warning indicator.

**Mitigation.** Labelled `roll_rate_proxy.csv`, documented in code, the dashboard footer, and the register.

---

### L5 — The transition matrix is origination-grade-to-outcome, not migration

**What.** A true rating-migration matrix requires **periodic re-rating** of the same borrower. This dataset has an origination grade and a final status only.

**Impact.** The matrix shows where each origination grade *ended up*, not how borrowers migrated between grades over time.

**Mitigation.** Documented as a valid and common variant, explicitly named as such rather than described as a migration matrix.

---

### L6 — Single-snapshot data blocks true IFRS 9 staging over time

**What.** IFRS 9 staging is inherently a **time-series** exercise — you compare current PD to origination PD at each reporting date and watch loans move between stages.

**Impact.** Origination PD had to be **proxied by grade-level average PD at issue**, and staging was computed at a single reporting date rather than tracked across periods. Stage migration statistics — which a real bank reports every quarter — cannot be produced.

**Mitigation.** The proxy is documented; SICR thresholds are in config; the staging logic itself is correct and would work unchanged on panel data.

---

### L7 — Model A's out-of-time calibration instability

**What.** Model A (borrower fundamentals only) fails Hosmer–Lemeshow on the 2014 out-of-time sample (p ≈ 3 × 10⁻⁷), and neither intercept recalibration nor Platt scaling fixed it.

**Diagnosis.** Not a *level* problem — a **shape** problem. The relationship between borrower fundamentals and default shifted between 2007–2013 and 2014, not merely the base rate. No one- or two-parameter rescaling can correct a shape error.

**Decision.** **Model B is the deployment model. Model A is retained as the interpretability benchmark.** Documented, not swept away.

---

### L8 — Simplified EIR discounting

**What.** IFRS 9 requires ECL discounted at the effective interest rate. This build used contractual `int_rate` as an EIR proxy and discounted by average expected time-to-default from the term structure, rather than a full cashflow-level EIR computation.

**Impact.** Modest understatement or overstatement of ECL depending on the actual timing profile. Directionally small relative to the staging effect.

---

### L9 — Macro scenarios are direct PD multipliers, not fitted

**What.** The three IFRS 9 scenarios apply fixed PD multipliers (1.00 / 0.85 / 1.50) with fixed weights (0.50 / 0.20 / 0.30).

**Why.** No macroeconomic time series was joined to the loan data.

**What a real implementation would do.** Fit a **satellite model** translating GDP growth, unemployment, and other macro variables into PD shifts, then apply published forecast scenarios.

---

### L10 — Downturn LGD is a supervisory proxy add-on

**What.** `downturn_LGD = min(1.0, LGD + 0.08)` — an 8 percentage-point add-on.

**Why.** The dataset does not isolate recession-period recovery experience cleanly enough to estimate downturn LGD empirically (only the 2007–08 vintages are crisis-era, and they are small).

**What a real implementation would do.** Estimate LGD separately on defaults resolved during identified downturn windows and use that distribution.

---

### L11 — LGD Stage 1 discrimination is weak (AUC 0.60)

**What.** The recovery classifier barely discriminates.

**Why.** This is a property of the asset class, not the model. Whether an unsecured borrower produces any post-charge-off recovery depends on collections effort, later circumstances, and settlement luck — none of which is visible in application data.

**Mitigation.** Optimised for **portfolio-level unbiasedness**, which is what Basel EL and IFRS 9 consume. Achieved: predicted 0.9302 vs actual 0.9304.

---

### L12 — Currency labelling

**What.** Outputs use the ₹ symbol; the underlying data is US dollars. No conversion was performed.

**Mitigation.** State it plainly if asked. It is a presentation convention for an Indian bank context, not a claim about currency.

---

### L13 — The dataset ends in 2014

**What.** The most recent origination is December 2014 and the snapshot is January 2016. The macro environment, underwriting standards, and consumer behaviour have all changed substantially since.

**Impact.** The models are a demonstration of methodology on historical data. They are not calibrated to any current portfolio and should not be represented as such.

---

### L14 — No independent validation

**What.** The models were developed and validated by the same party. SR 11-7 requires **independent** validation.

**What a real deployment would need next.** An independent validation team performing conceptual soundness review, outcomes analysis, benchmarking against a challenger model, and sign-off before use in regulatory reporting.

---
---

# PART VII — THE INTERVIEW COMPENDIUM

---

## VII.1 — The three things to internalise above all else

**1. Lead with the honesty stories, not the metrics.**

> *"I built it two ways — one on borrower fundamentals, one including the platform's own grade — and the fundamentals-only model failed out-of-time calibration. I traced it to a structural data shift, dropped the offending variables, tried two standard recalibration approaches, and neither fixed it because the problem was shape rather than level. So I deployed the other model and documented why."*

That answer beats any Gini number, because it shows **judgement** rather than technique. Everyone can fit a model.

**2. Own the limitations proactively.** When they start probing, get there first:

> *"EAD is reconstructed, not observed. CCF is a labelled synthetic demonstration because the data is term-only. Default timing is a `last_pymnt_d` proxy. The roll rate is a status-distribution proxy because I have a snapshot, not a panel."*

Naming your own weaknesses is the single strongest credibility signal in model risk.

**3. The IRB-versus-Standardised finding is your headline.** Most people assume IRB always saves capital. Yours proves the opposite for a high-LGD book, with the mechanism. Have it ready:

> *"IRB produced 67% more RWA than Standardised — ₹2.29B against ₹1.37B. That is counterintuitive, and the driver is the 93% LGD. IRB is risk-sensitive, so a genuinely risky unsecured book gets penalised; the flat 75% standardised weight is calibrated for a diversified retail book and happens to be lenient here. A bank running this product on Standardised is structurally undercapitalised relative to its economic risk."*

---

## VII.2 — The numbers to have in your mouth

| Quantity | Value |
|---|---|
| Loans | 466,285 |
| Columns | 75 |
| Origination window | Jun 2007 – Dec 2014 |
| Snapshot | Jan 2016 |
| Train / test / OOT | 184,525 / 46,132 / 235,628 |
| Ever-default rate | 10.93% (50,968 loans) |
| **12-month default rate** | **3.435%** |
| Defaults in first 12 months | 31.43% of all defaults |
| Peak hazard window | months 10–18 (43.97% of defaults) |
| Model B OOT Gini / KS | **0.3845 / 28.43%** |
| Model A OOT Gini | 0.2715 |
| Model A OOT Hosmer–Lemeshow | 3.08 × 10⁻⁷ (fails) |
| Score PSI | ~0.01 (stable) |
| CSI on dropped variables | ~3.96 |
| **Mean LGD** | **93.01%** (median 100%) |
| Total losses (LGD = 1.0) | **52.18%** |
| LGD predicted vs actual | 0.9302 vs 0.9304 |
| LGD Stage 1 AUC | 0.6047 |
| Portfolio EAD | **₹1.827B** |
| **Total Expected Loss** | **₹58.67M (3.21% of EAD)** |
| **IRB RWA** | **₹2.295B (125.63% avg risk weight)** |
| Standardised RWA | ₹1.370B (75%) |
| IRB capital at 8% | ₹183.6M |
| Downturn LGD impact | +₹159.25M RWA, +₹12.74M capital (+6.94%) |
| Lifetime PD (36m) | 10.6356% |
| Lifetime ÷ 12-month | **3.096×** |
| IFRS 9 staging | ~80% / 11% / 8% |
| **IFRS 9 ECL** | **₹278.48M** |
| of which Stage 3 | ₹223.8M |
| **CECL** | **₹327.47M** |
| Stage 1: IFRS 9 vs CECL | ₹30.27M vs ₹79.26M |
| Performing-only IFRS 9 vs Basel EL | ₹54.7M vs ₹58.67M |
| Basel reference verification | R = 0.1216 at PD = 0.01 (Other Retail) |
| RAG index | 4 docs, 511 pages, 1,774 chunks, 384-dim |
| Tests | 39 passing |
| Repo | 139 files, 13,017 insertions |

---

## VII.3 — Likely questions, with answers

**"Walk me through your project in two minutes."**

> *"I took 466,000 Lending Club unsecured personal loans and built the full retail credit risk stack a bank actually runs. The first thing I fixed was the target: most implementations use an 'ever defaulted' flag, which is contaminated by right-censoring and cannot feed either Basel or IFRS 9. I built a proper 12-month performance window instead. Then WoE/IV binning with enforced monotonicity, a logistic scorecard with points scaling and eight rating grades, and a full validation battery — Gini, KS, Hosmer–Lemeshow, PSI and CSI on train, test, and a 2014 out-of-time sample. Two-stage LGD came out at 93%, which is what unsecured really looks like. Then the regulatory layer: Basel IRB capital verified against reference values, and the complete IFRS 9 ECL engine with SICR staging, a lifetime PD term structure built from the seasoning curve, macro scenarios, and a CECL contrast. On top of that, monitoring, an institutional dashboard, and an AI analyst doing RAG over the actual Basel PDFs while calling my own risk engines as tools. Everything is tested and reproducible, and there is a full SR 11-7 documentation pack with a limitations register."*

**"How did you prevent target leakage?"**

> *"I classified all 75 columns in a YAML config into seven categories — application-time, sparse application, outcome, identifier, free text, all-null, and cohort anchor — before writing any model code. Then a schema module exposes `assert_no_leakage()`, which raises a ValueError if any outcome or identifier column appears in a feature list, and it is called inside the model's `fit()` method. So leakage is not a policy someone has to remember; it is structurally impossible. There is a unit test proving it fires on `recoveries`. Those outcome columns are not banned outright, though — `recoveries` and `total_rec_prncp` are exactly what LGD and EAD need. The wall is what made them clean to use there."*

**"Why is your Gini only 0.38? That seems low."**

> *"Because the borrower signal in this data is genuinely thin, and I did not inflate it. Strip out `grade` and `int_rate` — which are Lending Club's own risk model output, not borrower facts — and the strongest remaining variable is `inq_last_6mths` at an IV of 0.076, which is merely 'weak'. Income, DTI, and home ownership are weak-to-useless. That is the honest predictive content available. I could have pushed the number up with a gradient-boosted tree or by leaning harder on grade, but a regulated PD model has to be explainable, and Model B at 0.38 out-of-time — improving from 0.36 in-sample — is a stable, well-calibrated, defensible model. On thin signal, a bank would accept that and grade more coarsely."*

**"Your model ranks well but you said calibration failed. Explain."**

> *"Model A's out-of-time Hosmer–Lemeshow was 3 × 10⁻⁷. It ranked fine — Gini 0.27 — but its predicted PDs were wrong on 2014 data. That matters more than the Gini, because Basel and IFRS 9 multiply capital and provisions by the PD, so a miscalibrated model makes the bank hold the wrong amount of capital. I first traced part of it to two variables with CSI around 3.96 — `tot_cur_bal` and `total_rev_hi_lim`, which Lending Club did not collect before late 2012, so they were 100% missing in half the development window. I dropped them, which improved calibration by eight orders of magnitude and still failed. Then I recalibrated the intercept on the test sample and reported on OOT — the honest split — and confirmed Gini was unchanged to four decimals, proving the recalibration only moved level and not ranking. It barely helped, because the intercept shift needed was only 0.0048. Platt scaling did marginally better and also failed. So the diagnosis is that this is a shape problem, not a level problem: the relationship between fundamentals and default shifted, not just the base rate. Model B stayed calibrated because it is anchored by grade, which Lending Club re-fitted each year to current conditions."*

**"Why did you use PSI and CSI rather than just PSI?"**

> *"Because PSI alone lied to me. My score PSI was about 0.01 — rock stable, nothing to see. But per-variable CSI showed two variables at 3.96. The WoE MISSING bin had quietly absorbed a structural change at the score level even though the underlying population had lurched completely. A stable PSI hid an unstable variable, and that instability was what was breaking out-of-time calibration. You compute both, always."*

**"Which LGD goes into the Basel capital formula?"**

> *"Downturn LGD, not average. Capital exists for bad years, and in a recession recoveries collapse at the same time defaults rise — collateral is worth less, collections are harder. Using average LGD would understate exactly the scenario capital is meant to cover. I implemented it as a documented supervisory add-on — 8 percentage points, capped at 1.0 — and noted explicitly that a real bank derives it empirically from recession-window recovery data. On my book it added about ₹159 million of RWA and 6.9% to capital, though because average LGD was already 93% most loans hit the cap."*

**"How did you handle SICR staging?"**

> *"A two-part test plus a backstop, all in config. Quantitatively: current 12-month PD at or above 2.0× the origination PD, or absolute current PD above 6%. Plus the IFRS 9 rebuttable presumption — 30+ days past due forces Stage 2 regardless. Stage 3 is defaulted, with PD set to 1. The honest limitation is that I have no per-loan origination PD, only a snapshot, so I proxied it with grade-level average PD at issue, and that is documented. The result was about 80% Stage 1, 11% Stage 2, 8% Stage 3, with Stages 2 and 3 holding 19% of loans but 22% of exposure — risk concentrating in the deteriorated buckets, which is exactly what staging is designed to surface."*

**"How did you calibrate PD from point-in-time to through-the-cycle?"**

> *"I did not, and I would want to be precise about that. My PD is point-in-time — fitted on 2007–2013 and validated on 2014, reflecting conditions in those windows. Basel IRB generally wants something closer to through-the-cycle so capital does not swing procyclically, while IFRS 9 explicitly wants point-in-time with forward-looking adjustment. What I did build is the IFRS 9 side properly: probability-weighted macro scenarios with a 30%-weighted downside at a 1.5× PD multiplier. For a genuine TTC calibration for Basel I would need a longer default history spanning a full cycle, and I would map long-run average default rates by grade to a master scale. That is a real gap and I would flag it in the model documentation."*

**"Why did IRB give you more capital than Standardised? Isn't that backwards?"**

> See VII.1 point 3.

**"What would you do differently with more time?"**

> *"Four things, roughly in order of value. First, get loan-month panel data — that single change unlocks true roll rates, real rating migration, and IFRS 9 staging tracked over time, which are the three biggest limitations I have. Second, fit a genuine macroeconomic satellite model so the IFRS 9 scenarios are linked to GDP and unemployment forecasts rather than being direct PD multipliers. Third, build a gradient-boosted challenger model alongside the scorecard to quantify what the interpretability constraint actually costs in Gini — banks do this routinely and it is a good governance argument. Fourth, a proper through-the-cycle calibration for the Basel PD."*

**"What did the AI layer actually add?"**

> *"It answers two kinds of question and cannot hallucinate either. For regulatory questions it does retrieval over the real Basel and IFRS 9 PDFs — 1,774 chunks across 511 pages — and cites the document and page for every claim, with a relevance guardrail that refuses to answer if nothing scores above 0.30. For quantitative questions it calls my actual validated functions as tools rather than doing arithmetic itself. Live, it computed an expected loss of ₹3,937.50 and a Basel K of 0.0513 by running my engine, and cited d424 page 69 for the PD floor in the same answer. It also correctly explained the three retail risk-weight functions and the QRRE-versus-Other-Retail distinction, all cited. The point is that it is a front end to validated code and authoritative documents — not a chatbot with a finance theme."*

**"How much of this did you actually write versus the AI?"**

> The only honest answer is the true one, and it is a good answer in 2026:

> *"I specified it and the agent implemented it. Every prompt is in my chat history — I wrote the function signatures, the formulas, the test cases, and the acceptance criteria, and the agent wrote the code. What I contributed beyond that was judgement: I caught that the LGD denominator was wrong, that a headline expected loss of ₹1,950 on a ₹1.8 billion book had to be a stale file, that a Hosmer–Lemeshow of 10⁻⁷ is still a failure even though the agent called it an eight-order-of-magnitude win, and that the Basel reference values I had been given were QRRE rather than Other Retail. The agent is good at writing code to a specification and poor at knowing whether a number is sensible. That is where I sat."*

---

## VII.4 — Questions to ask them

Asking good questions is half of an interview. These are specific to this seat.

- *"Is the retail book on Standardised or IRB currently, and is there an IRB migration in progress?"*
- *"How is the Ind AS 109 ECL model governed alongside the IRACP norms — are they run in parallel, and how are the differences explained internally?"*
- *"Where does CPRA sit relative to independent model validation, and what does the challenge process look like in practice?"*
- *"What is the monitoring cadence, and what triggers an out-of-cycle recalibration?"*
- *"How are the IFRS 9 macro scenarios generated — internally, or from a published economics view?"*
- *"What does the modelling stack look like — Python, SAS, R? Is there a model deployment pipeline or is it batch?"*

---
---

# PART VIII — THE SECOND PASS

## How to actually learn this, now that it is built

The building is done. **Understanding is a different, calmer project**, and this is how to do it.

### VIII.1 — The principle

You built this while also fighting the tooling, and both arriving at once is genuinely overwhelming. That was the right order — the project exists and it works, which is the hard part. The second pass has no deadline and no infrastructure to fight. Its only goal is that **every sentence in Part VII comes out of your mouth as yours.**

### VIII.2 — The eight-week structure

**Weeks 1–2: Read, do not run.**
Read Part I of this book straight through, twice, in different weeks. No code. No repository. Just the domain. On the second read, close the book after each chapter and write down its three main ideas from memory. Where you cannot, re-read that chapter only.

**Week 3: The formula sheet by hand.**
Take Chapter 15 and re-derive each formula on paper. Specifically:
- Compute the Other Retail correlation at PD = 0.005, 0.01, 0.05, and 0.20. Watch it fall from 0.16 toward 0.03.
- Compute K by hand for PD = 1%, LGD = 45% and confirm you get 0.0366. Then do it with LGD = 93% and see the capital roughly double.
- Compute a WoE by hand for a two-bin variable you invent.
- Compute the scorecard factor and offset for PDO = 20, base 600, odds 50.

If you can do these on paper, no interviewer can shake you on the mechanics.

**Week 4: Read the code, module by module.**
One module per sitting, in dependency order: `schema.py` → `target.py` → `sampling.py` → `binning.py` → `pd_model.py` → `scorecard.py` → `metrics.py` → `calibration.py` → `lgd_data.py` → `lgd_model.py` → `ead_model.py` → `expected_loss.py` → `basel_capital.py` → `lifetime_pd.py` → `staging.py` → `ecl.py` → `macro_scenarios.py` → `vintage.py` → `transitions.py` → `dashboard_data.py` → `rag_index.py` → `analyst.py`.

For each: open the file, read it top to bottom, then write **one paragraph in your own words** in `docs/notes/` saying what it does and why it exists. Twenty-two paragraphs. That file becomes your revision document.

**Week 5: Re-run each stage, predicting the output first.**
Before running any script, write down what you expect. Then run it. Where you were wrong, that is the thing you did not understand — go back to the relevant chapter here.

**Week 6: Break things deliberately.**
This is the most effective week and the one people skip.
- Change the SICR relative threshold from 2.0 to 1.5. Re-run staging. How much does Stage 2 grow, and what happens to ECL?
- Change the downside macro weight from 0.30 to 0.50. Re-run. Which direction does provision move, and by how much?
- Change PDO from 20 to 40. Re-run the scorecard. Confirm the ranking is unchanged and only the score scale moved.
- Set the LGD to 45% instead of 93% and recompute Basel capital. Watch the IRB-versus-Standardised finding **reverse**.
- Remove `grade` from Model B and re-validate. Watch it become Model A.

Each of these turns a memorised fact into an understood mechanism.

**Week 7: Write it out cold.**
Without looking at anything, write a two-page summary of the project: what it does, how, what was found, what the limitations are. Then compare against the model documentation and see what you left out.

**Week 8: Say it out loud.**
Answer every question in Part VII.3 aloud, to a wall or a recording. Written comprehension and spoken fluency are different skills, and the interview tests the second one.

### VIII.3 — The extensions worth building next

In order of value to a CPRA interview:

1. **A gradient-boosted challenger model** with SHAP explanations, benchmarked against the scorecard. Quantifies what interpretability costs, which is a real governance conversation.
2. **A macroeconomic satellite model** linking unemployment and GDP growth to PD shifts, replacing the direct multipliers.
3. **Through-the-cycle PD calibration** with a documented mapping from PIT to TTC.
4. **Reject inference** — a genuine scorecard problem this dataset cannot support, since it contains only accepted applicants, but which every real bank must handle.
5. **A survival model (Cox proportional hazards)** for lifetime PD, as an alternative to the empirical hazard curve, with the two compared.
6. **The Vertex AI upgrade** for the analyst layer, so "deployed on Google Cloud Vertex AI" becomes true.

### VIII.4 — What to say if asked "do you fully understand every line?"

The honest answer, which is also the strong one:

> *"I specified and drove all of it, and I understand the methodology completely — I can derive the Basel formula, explain why my calibration failed and what that means, and defend every limitation. Line-by-line, there are implementation details in the plotting and the dashboard build I would need to re-read. I have been going back through it module by module since finishing, because the difference between having built something and being able to defend it is exactly the gap I am closing."*

Nobody expects total recall of a 139-file repository. **They expect you to know which parts you know.**

---
---

# APPENDICES

---

## Appendix A — Glossary

**AIRB / A-IRB** — Advanced Internal Ratings-Based. Bank estimates PD, LGD, and EAD. The only IRB option for retail.
**ASRF** — Asymptotic Single Risk Factor. The model underlying the Basel IRB formula.
**AUC** — Area Under the ROC Curve. Discrimination measure; 0.5 random, 1.0 perfect.
**Basel** — International banking regulatory framework from the Basel Committee.
**bcbs128 / d424 / d350** — Specific Basel Committee documents used in this project's RAG index.
**Brier score** — Mean squared error of probability forecasts.
**Calibration** — Whether predicted probabilities match observed frequencies.
**CCF** — Credit Conversion Factor. Fraction of an undrawn limit converted to exposure by default.
**CECL** — Current Expected Credit Losses. The US accounting standard. Lifetime ECL on everything, no staging.
**CET1** — Common Equity Tier 1. The highest-quality regulatory capital.
**Charge-off** — Removal of a defaulted loan from the balance sheet with loss recognition.
**Cohort** — See vintage.
**CPRA** — Credit Portfolio Risk Analytics.
**CSI** — Characteristic Stability Index. PSI applied to individual input variables.
**Cure** — A delinquent loan returning to current.
**Discrimination** — A model's ability to rank good borrowers above bad.
**DPD** — Days Past Due.
**EAD** — Exposure at Default.
**ECL** — Expected Credit Loss. The IFRS 9 provision.
**EIR** — Effective Interest Rate. The IFRS 9 discount rate.
**EL** — Expected Loss = PD × LGD × EAD.
**F-IRB** — Foundation IRB. Bank estimates PD only. Not available for retail.
**Gini** — 2 × AUC − 1.
**Hazard** — Probability of default in a period given survival to its start.
**Hosmer–Lemeshow** — Formal calibration test. High p-value = calibrated.
**IFRS 9** — International accounting standard for financial instruments. ECL and staging.
**Ind AS 109** — The Indian adoption of IFRS 9.
**IRACP** — Income Recognition, Asset Classification and Provisioning. RBI's own norms.
**IRB** — Internal Ratings-Based approach to regulatory capital.
**IV** — Information Value. A variable's total predictive strength.
**KS** — Kolmogorov–Smirnov statistic. Maximum separation between good and bad cumulative distributions.
**Laplace smoothing** — Adding a small constant (0.5) to cell counts to avoid ln(0).
**Leakage** — Using information unavailable at prediction time. Fatal to a credit model.
**LGD** — Loss Given Default.
**Lifetime PD** — Cumulative default probability over remaining life.
**MOB** — Months on Book. Loan age.
**Monotonicity** — WoE moving consistently in one direction across ordered bins.
**OOT** — Out-of-Time. A hold-out sample from a different period.
**PD** — Probability of Default.
**PDO** — Points to Double the Odds. Scorecard scaling constant.
**PIT** — Point-in-Time. A PD reflecting current conditions.
**Platt scaling** — Two-parameter recalibration of predicted probabilities.
**PSI** — Population Stability Index. Distribution shift in the model score.
**QRRE** — Qualifying Revolving Retail Exposures. Basel sub-class with fixed correlation 0.04.
**RAG** — Retrieval-Augmented Generation. Grounding an LLM in retrieved documents.
**Rank ordering** — Each worse grade actually defaulting more than the grade above.
**RBI** — Reserve Bank of India.
**Recovery rate** — 1 − LGD.
**Right-censoring** — Outcomes cut off because observation ended before they resolved.
**Roll rate** — Fraction of loans moving from one delinquency bucket to a worse one.
**RWA** — Risk-Weighted Assets.
**Seasoning** — The pattern of risk changing with loan age.
**SICR** — Significant Increase in Credit Risk. The IFRS 9 Stage 1 → 2 trigger.
**SR 11-7** — US supervisory guidance on Model Risk Management. The de facto global template.
**Standardised Approach (SA)** — Regulatory capital from prescribed risk weights; 75% for qualifying retail.
**TTC** — Through-the-Cycle. A PD averaged across an economic cycle.
**Vintage** — Loans originated in the same period.
**WoE** — Weight of Evidence. ln(%good ÷ %bad) for a bin.

---

## Appendix B — Command reference

```powershell
# --- Navigation -----------------------------------------------------------
pwd                                    # where am I
cd "D:\path with spaces\project"       # go somewhere (quotes if spaces)
dir                                    # list contents
dir -Recurse -File | Select-Object FullName, Length | Format-Table -AutoSize
Get-Content ".\file.csv" -TotalCount 1 # first line only
Get-ChildItem folder -File | Select-Object Name, @{N='MB';E={[math]::Round($_.Length/1MB,1)}}

# --- Python environment ---------------------------------------------------
python --version
python -m venv .venv
.\.venv\Scripts\Activate.ps1           # prompt gains (.venv)
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned   # if blocked
python -m pip install --upgrade pip
pip install numpy pandas scikit-learn scipy statsmodels matplotlib pytest
pip install -e .                       # editable install of this package
pip list                               # what is installed
deactivate                             # leave the venv

# --- Testing --------------------------------------------------------------
pytest tests/ -v                       # everything, verbose
pytest tests/test_schema.py -v         # one file

# --- Git ------------------------------------------------------------------
git init
git status
git add .
git commit -m "message"
git remote add origin https://github.com/USER/REPO.git
git branch -M main
git push -u origin main

# --- Running the project --------------------------------------------------
.\.venv\Scripts\python.exe -m creditrisk.data.target
.\.venv\Scripts\python.exe -m creditrisk.models.run_scorecard
.\.venv\Scripts\python.exe -m creditrisk.validation.run_validation
.\.venv\Scripts\python.exe -m creditrisk.regulatory.run_basel_capital
.\.venv\Scripts\python.exe -m creditrisk.reporting.build_dashboard

# --- The AI analyst -------------------------------------------------------
$env:GEMINI_API_KEY="your-key"         # per terminal window; does not persist
.\.venv\Scripts\python.exe -m creditrisk.ai.run_analyst
```

---

## Appendix C — File map

| Path | Purpose |
|---|---|
| `config/variables.yaml` | All 75 columns classified — the leakage guard |
| `config/target_definition.yaml` | Default statuses, 12-month window, DPD lag, snapshot |
| `config/sampling.yaml` | Dev/OOT vintages, test size, seed, target column |
| `config/pd_model.yaml` | Model A exclusions, min IV, scaling constants, unstable drops |
| `config/ifrs9.yaml` | SICR thresholds and DPD backstop |
| `config/macro_scenarios.yaml` | Three scenarios, multipliers, weights |
| `config/ai.yaml` | Gemini model name |
| `src/creditrisk/data/schema.py` | Config loader + `assert_no_leakage` + coverage validation |
| `src/creditrisk/data/target.py` | `parse_lc_date`, `build_target`, `target_summary` |
| `src/creditrisk/data/sampling.py` | Dev/OOT split, stratified train/test, sample summary |
| `src/creditrisk/features/binning.py` | `WoEBinner` — fit, transform, IV summary |
| `src/creditrisk/models/pd_model.py` | `PDModel` — statsmodels Logit on WoE |
| `src/creditrisk/models/scorecard.py` | Points scaling, `score_dataset`, `build_rating_grades` |
| `src/creditrisk/models/calibration.py` | Intercept recalibration and Platt scaling |
| `src/creditrisk/models/lgd_data.py` | Basel LGD target construction |
| `src/creditrisk/models/lgd_model.py` | `TwoStageLGD` hurdle model |
| `src/creditrisk/models/ead_model.py` | Term EAD, `get_portfolio_ead` |
| `src/creditrisk/models/ccf_demo.py` | **SYNTHETIC** revolving CCF demonstration |
| `src/creditrisk/validation/metrics.py` | Gini, KS, calibration table, HL, Brier |
| `src/creditrisk/validation/plots.py` | ROC, KS, calibration plots |
| `src/creditrisk/validation/stability.py` | PSI and CSI |
| `src/creditrisk/validation/run_validation.py` | Assembles `validation_summary.csv` |
| `src/creditrisk/regulatory/expected_loss.py` | EL = PD × LGD × EAD, portfolio summary |
| `src/creditrisk/regulatory/basel_capital.py` | Correlation, K, RWA, standardised, downturn LGD |
| `src/creditrisk/regulatory/lifetime_pd.py` | Hazard curve, survival, scaling, remaining term |
| `src/creditrisk/regulatory/staging.py` | IFRS 9 SICR and stage assignment |
| `src/creditrisk/regulatory/ecl.py` | ECL by stage, EIR discounting, CECL contrast |
| `src/creditrisk/regulatory/macro_scenarios.py` | Scenario ECL, probability weighting |
| `src/creditrisk/monitoring/vintage.py` | Vintage curves, maturity comparison |
| `src/creditrisk/monitoring/roll_rates.py` | Status-distribution **proxy** |
| `src/creditrisk/monitoring/transitions.py` | Origination-grade-to-outcome matrix |
| `src/creditrisk/reporting/dashboard_data.py` | Consolidates all tables into one JSON |
| `src/creditrisk/reporting/build_dashboard.py` | Writes the self-contained HTML |
| `src/creditrisk/ai/rag_index.py` | PDF load, chunk, embed, save index |
| `src/creditrisk/ai/retriever.py` | Cosine-similarity search over the index |
| `src/creditrisk/ai/tools.py` | Wrappers exposing the real engines as callable tools |
| `src/creditrisk/ai/analyst.py` | `CreditRiskAnalyst` — retrieval + tool calling + guardrail |
| `src/creditrisk/ai/run_analyst.py` | CLI loop |
| `docs/MODEL_DOCUMENTATION.md` | The SR 11-7 pack |
| `docs/MANAGEMENT_DECK.md` | The credit committee deck |
| `outputs/reports/risk_dashboard.html` | The dashboard (self-contained) |
| `outputs/reports/dashboard_data.json` | Consolidated results |
| `standing_rules.md` | The agent rules, pasted into every prompt |

---

## Appendix D — The standing rules (copy block)

```
STANDING RULES — follow these in every task:
- I am on Windows. Use PowerShell syntax for all commands.
- The virtual environment at .\.venv is already active. Use it. Do not create another.
- Do NOT install any package without first telling me what it is and why.
- Do NOT start any long-running process (servers, watchers, dashboards) unless I ask.
- Before you write a file, tell me in plain English: what the file does, why it
  exists, and how it fits the project. After you write it, walk me through it.
- Never invent column names, file paths, or data values. If you need to know
  something about the data, INSPECT it first and show me what you found.
- Do one task at a time. Stop and report. Do not run ahead to the next step.
- Write code a junior analyst could read. Comments explain WHY, not WHAT.
```

---

## Appendix E — The prompt template

Every effective prompt in this build had the same five parts. Copy the shape.

```
[STANDING RULES BLOCK]

TASK: <one sentence stating the goal>

<Exact file paths to create — never "a module for X">

Write src/creditrisk/<area>/<file>.py with:

  <function_name>(arg1, arg2) -> <return type>
    <what it does, in plain terms>
    <the maths, written out in full>
    <edge cases: what to do with missing, zero, out-of-range>

  <next function...>

Write tests/test_<file>.py: <specific assertions, with expected values
where you can hand-compute them>

Run it. Show me <the specific output that proves it worked> and tell me
<the specific question whose answer you cannot predict>.
```

**The two clauses that matter most:**
- *"Run it. Show me..."* — forces execution and reporting, so you see reality rather than intention.
- *"Tell me <question>"* — forces interpretation, and surfaces disagreements between what you expected and what the data says.

---

## Appendix F — Reproduction order

To rebuild every number from the raw CSV:

```
1.  config/variables.yaml        →  schema validation
2.  target.py                    →  default_12m, months_to_default, vintages
3.  target QA                    →  reconciliation bridge, seasoning curve, sensitivity
4.  sampling.py                  →  train / test / oot parquet
5.  binning.py (fit on TRAIN)    →  WoE bins, IV summary
6.  pd_model.py                  →  Model A and Model B
7.  scorecard.py                 →  points, rating grades
8.  run_validation.py            →  Gini, KS, HL, Brier, PSI, CSI
9.  calibration.py               →  recalibrated Model A variants
10. lgd_data.py → lgd_model.py   →  two-stage LGD
11. ead_model.py → ccf_demo.py   →  EAD + SYNTHETIC CCF
12. expected_loss.py             →  EL by grade, portfolio totals
13. basel_capital.py             →  IRB, standardised, downturn
14. lifetime_pd.py               →  hazard curve, term structure
15. staging.py                   →  IFRS 9 stages
16. ecl.py                       →  ECL by stage, CECL contrast
17. macro_scenarios.py           →  weighted ECL, performing-only comparison
18. vintage.py, roll_rates.py, transitions.py  →  monitoring
19. dashboard_data.py            →  dashboard_data.json
20. build_dashboard.py           →  risk_dashboard.html
21. rag_index.py                 →  RAG index over knowledge_base/
22. run_analyst.py               →  the AI analyst CLI
```

**The dependency that bites:** step 12 must be re-run whenever the PD or LGD models change, or the dashboard reads a stale `expected_loss_summary.csv`. That is error E7.

---

## A closing note

You built this in a handful of days, from a stalled folder to a complete, tested, documented, published system — through twelve stages, after a previous attempt collapsed at stage zero.

The models are competent. What makes the project genuinely uncommon is elsewhere: **you found a calibration failure and did not hide it. You corrected an LGD definition that flattered your numbers. You labelled the synthetic part. You wrote down every limitation before anyone asked.**

That is not a student project. That is how a risk professional works.

The second pass is where it becomes fully yours. Start with Part I, and take your time.
