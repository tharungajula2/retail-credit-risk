# Review: ENTERPRISE_CREDIT_RISK_PYTHON_HANDBOOK.md

**Reviewer note:** every "VERIFIED" item below was actually executed in Python 3.12 / pandas 3.0 / numpy 2.4 / pydantic 2.13, not just read. Project-specific paths, row counts and repo links are excluded from review as requested.

**Overall:** the pedagogy (restaurant analogy, "spoon-fed concept" boxes, mermaid lifecycle, module ordering) is strong and the maths in Modules 3, 4 and 7 is correct. The weaknesses are concentrated in (a) code that doesn't run on current library versions, (b) one silent WOE bug, (c) missing credit-risk methodology that a real validator would immediately ask for, and (d) India-specific regulatory framing that is out of date.

---

## PART A — Code that will not run (fix first)

### A1. The Pydantic snippet (§2.1) crashes on import — VERIFIED

```
PydanticUserError: `regex` is removed. use `pattern` instead
```

Three separate v1/v2 problems in one block:

| Written | Problem | Fix |
|---|---|---|
| `regex=r"^[A-Z]{5}..."` | Removed in Pydantic v2 | `pattern=r"..."` |
| `from pydantic import validator` + `@validator` | Deprecated v1 API | `field_validator` + `@field_validator(...)` with `@classmethod` |
| `Field(..., example=750)` (§8.1) | Not a v2 keyword | `Field(..., examples=[750])` |

This matters because FastAPI has shipped Pydantic v2 for a long time — so the handbook's own Module 8 stack contradicts its own Module 2 code.

**Corrected version:**

```python
from pydantic import BaseModel, Field, field_validator
from typing import List

class BureauPayload(BaseModel):
    pan_number: str = Field(..., pattern=r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$")
    cibil_score: int = Field(..., ge=-1, le=900)   # see C4 on -1 / 0
    trade_lines: List[TradeLine]

    @field_validator("cibil_score")
    @classmethod
    def validate_cibil(cls, v: int) -> int:
        if v not in (-1, 0) and not (300 <= v <= 900):
            raise ValueError("CIBIL must be 300-900, or -1/0 for new-to-credit")
        return v
```

Also: the original `@validator('cibil_score')` only re-checked what `ge=300, le=900` already enforced — dead code.

### A2. `np.timedelta64(1, 'M')` raises — VERIFIED

In `engineer_credit_target()`:

```
ValueError: Unit M is not supported. Only unambiguous timedelta values durations
are supported. Allowed units are 'W','D','h','m','s','ms','us','ns'
```

Months aren't a fixed duration, so numpy refuses. Even where it silently worked on older versions it used 30.436875 days, not calendar months — which quietly shifts your 12-month window.

**Fix — use true calendar months:**

```python
df["months_to_last_payment"] = (
    (df["last_pymnt_date"].dt.year  - df["issue_date"].dt.year) * 12
    + (df["last_pymnt_date"].dt.month - df["issue_date"].dt.month)
)
```

### A3. `WOETransformer` re-bins at transform time — VERIFIED, and this is the serious one

`fit()` computes bin edges with `pd.qcut` but never stores them. `transform()` calls `pd.qcut` **again on the incoming data**, computing brand-new quantile edges from that data.

Test result on a drifted OOT sample:

```
TRAIN bin label:  (473286.956, 558128.287]
OOT   bin label:  (774860.979, 1029248.348]
Rows silently mapped to WOE = 0.0 : 5000 / 5000
```

**Every single OOT row got WOE = 0**, because `.fillna(0.0)` swallowed the mismatch. No exception, no warning. Your OOT Gini would be pure noise and you'd never know why.

Worse, at production scoring time:

```
Single-row API call → WOE = 0.0
```

`pd.qcut` on one row is meaningless, so a live loan application scores as portfolio-average on every feature. A silent, permanent, undetectable production failure.

**Fix — persist the edges in `fit`, use `pd.cut` in `transform`:**

```python
def fit(self, df, target_col, feature_cols):
    ...
    for col in feature_cols:
        if pd.api.types.is_numeric_dtype(df[col]):
            binned, edges = pd.qcut(df[col], q=self.num_bins,
                                    duplicates="drop", retbins=True)
            edges[0], edges[-1] = -np.inf, np.inf      # open the tails
            self.bin_edges_[col] = edges
            df_bin = binned.astype(str)
        ...

def transform(self, df):
    ...
    if col in self.bin_edges_:
        df_bin = pd.cut(df[col], bins=self.bin_edges_[col]).astype(str)
        out[col + "_woe"] = df_bin.map(woe_map)
    ...
    # do NOT silently fillna(0) — raise or route to the MISSING bin
```

Two more bugs in the same class:
- The docstring claims it "handles missing values (`-9999` or NaN) by assigning them to a dedicated missing bin." It doesn't. `-9999` is lumped into the lowest quantile bin (badly polluting its WOE), and NaN only forms a group by accident because `.astype(str)` produces the literal string `"nan"`. Add an explicit missing-value branch before binning.
- `np.where(prop == 0, 0.0001, prop)` is arbitrary. Standard practice is a 0.5-count (Laplace) adjustment applied to the counts, not the proportions: `(goods_i + 0.5) / (n_good + 0.5k)`.

### A4. Docker port ≠ Cloud Run port — deployment will fail

The Dockerfile hardcodes `--port 8000`, but Cloud Run injects `$PORT` (default 8080) and health-checks that port. The `gcloud run deploy` command in §9.2 passes no `--port`, so the revision will fail to start.

```dockerfile
ENV PORT=8080
EXPOSE 8080
CMD exec uvicorn src.creditrisk.api:app --host 0.0.0.0 --port ${PORT}
```

### A5. `--workers 4` on Cloud Run

Four uvicorn workers on `--cpu=2` means four copies of your `.pkl` model in RAM inside a 2Gi container, plus CPU oversubscription. Cloud Run scales by *instances*, not workers. Use 1 worker and let Cloud Run's `--concurrency` and autoscaling do the work — this also directly contradicts Module 10.1's own OOM warning.

### A6. `@app.on_event("startup")` (§10.1) is deprecated

Correct pattern is now the lifespan context manager:

```python
from contextlib import asynccontextmanager

ML = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    ML["scorecard"] = joblib.load("outputs/models/scorecard.pkl")
    yield
    ML.clear()

app = FastAPI(lifespan=lifespan)
```

---

## PART B — Credit-risk methodology gaps

### B1. No performance-window maturity exclusion — the biggest methodological hole

The target is defined as "default within a 12-month performance window," but nothing excludes **immature vintages**. A loan issued in Nov 2014 in a dataset ending in 2014 has had ~1 month of observation. It is labelled `default_12m = 0` because it hasn't defaulted *yet* — not because it's good.

This compounds directly into the OOT design:

> OOT = the **2014 vintage** of a **2007–2014** dataset.

So the OOT sample is almost entirely immature. Its observed default rate is structurally depressed, which means the OOT Gini, the OOT calibration and the OOT PSI on the bad rate are all measuring an artefact, not model performance. A model validator would reject this in the first meeting.

**Fix:** add a maturity filter — only keep accounts where `issue_d + 12 months <= data_snapshot_date` — and move the OOT cut back so the OOT vintages are themselves fully seasoned (e.g. dev = 2007–2012, OOT = 2013, with 2014 dropped for immaturity). Also note the dev/OOT split shown is roughly 50/50, which is unusually large for OOT; 6–12 months of seasoned vintages is the norm.

### B2. `last_pymnt_d` is not the default date

The code proxies the default event with "last payment within 12 months." But charge-off typically lags the last payment by roughly 150–180 DPD. So an account whose last payment was month 11 usually charges off around month 16–17 — outside the window — yet the code labels it `default_12m = 1`. The bias runs the other way too for early-stage delinquency.

At minimum, state this explicitly as a documented approximation, and prefer a real default-date column where one exists.

### B3. §3.2 is titled "Monotonic Binning" but contains no monotonic logic

The prose is emphatic ("An FDE must force monotonic constraints!") and then the code is a plain `pd.qcut`. Add either an iterative bin-merging routine (merge adjacent bins until the bad rate is monotonic) or use `optbinning` / `scorecardpy`, which do this properly.

Also missing: a **minimum bin size constraint** (industry norm ≥ 5% of population per bin). Without it `qcut` will hand you bins with 12 bads whose WOE is statistical noise.

### B4. The coefficient-sign advice is backwards

Field Hack #3 tells you to prompt Copilot for *"positive coefficient constraints for logistic regression."* But the handbook defines `WOE = ln(Good / Bad)`, and the model predicts **bad**. Under that convention every coefficient should be **negative** (higher WOE = safer = lower log-odds of default).

Either flip the constraint to negative, or flip the WOE definition to `ln(Bad/Good)`. As written the two sections contradict each other, and constraining to positive would produce a scorecard where good behaviour lowers your score.

### B5. Scorecard section never shows the actual scorecard

Module 4 scales the *total* log-odds to a number. But a scorecard is a **points table** — points allocated per attribute bin. That table is the deliverable a bank signs off on, and it's what reason codes are computed from. It's absent.

```
Points_i = -(β_i × WOE_i + β_0 / n) × Factor + Offset / n
```
where `n` = number of characteristics in the model.

### B6. The scaling anchors don't produce the range you claim — VERIFIED

With `S0=600, Odds0=50:1, PDO=20`: `Factor = 28.85`, `Offset = 487.12`.

| PD | Score |
|---|---|
| 50.00% | 487 |
| 25.00% | 519 |
| 10.00% | 551 |
| 3.44% (your base rate) | 583 |
| 1.00% | 620 |
| 0.34% | 651 |

To reach 850 you'd need PD ≈ 0.00035%. To reach 900, PD ≈ 0.00006%. **No real applicant will ever score above ~700.** The whole portfolio compresses into roughly 480–670, which is nothing like a CIBIL-style spread.

Two fixes: (i) choose anchors calibrated to your portfolio (e.g. `S0 = 700` at `Odds0 = 20:1` with `PDO = 40` widens the spread considerably), and (ii) reconcile the ranges — the text says **300–900** (correct for CIBIL), the code clips to **300–850** (that's FICO), and the conclusion checklist says "300–850 CIBIL-style," which is a contradiction in terms.

Minor: `np.clip` destroys rank-ordering at the tails and breaks the score→PD inverse mapping used for ECL. Prefer widening the scale over clipping.

### B7. EAD is in the module title and never explained

Module 5 is "LGD **& EAD** Engine" and there is zero EAD content. Missing: the Credit Conversion Factor (CCF) for undrawn limits — which is *the* EAD question for credit cards and overdrafts, the dominant Indian retail unsecured products.

```
EAD = Drawn Balance + CCF × (Sanctioned Limit − Drawn Balance)
```

### B8. LGD recoveries aren't discounted

`LGD = 1 − (Total Recovered / EAD)` treats a rupee recovered in year 4 as equal to a rupee recovered at default. Real LGD discounts recovery cash flows back to the default date at the effective interest rate. Also missing: flooring LGD to `[0, 1]` (the two-stage formula can exceed 1 with negative recoveries after collection costs), and **downturn LGD**, which regulators require.

### B9. Lifetime ECL formula is only correct for Stage 1

`ECL = PD × LGD × EAD × DF` is the 12-month case. Lifetime ECL (Stages 2 and 3) is a sum over periods using **marginal** PDs and survival probabilities:

```
ECL_lifetime = Σ_t [ PD_marginal(t) × LGD(t) × EAD(t) × DF(t) ]
where PD_marginal(t) = S(t-1) × PD_hazard(t),  S = survival probability
```

Without this, the handbook's Module 6 can't actually compute what Module 6 claims to compute.

### B10. Module 7 promises calibration and CSI, delivers neither

The title says "Stability (PSI/**CSI**) & **Calibration** Engine." Neither appears.

- **CSI** (Characteristic Stability Index) = PSI applied per input feature, using the WOE bins. It's how you tell *which* feature drifted after PSI fires.
- **Calibration** is a separate discipline from discrimination: Platt scaling / isotonic regression, calibration to a central tendency, and backtesting with the binomial test or Hosmer-Lemeshow. A model can have Gini 0.55 and be badly mis-calibrated — and ECL depends entirely on calibration, not discrimination.

### B11. Gini ≥ 0.40 and K-S 30–50% are presented as regulatory requirements

They're industry rules of thumb, not RBI mandates. Rewrite as "typical internal validation thresholds." Also the body says K-S "30% to 50%" while the conclusion checklist says "K-S ≥ 30%" — pick one.

### B12. Missing entirely, and a validator will ask

| Topic | Why it matters |
|---|---|
| **Reject inference** | Your scorecard is fit only on *booked* loans. That's a selected sample. Parcelling / augmentation / fuzzy augmentation are the standard treatments. Zero mention. |
| **Adverse action / reason codes** | The Executive Introduction explicitly promises "RBI mandates an explicit, mathematically verifiable reason." No module ever produces one. Standard method: points-below-neutral, ranked, top 3–4 returned. |
| **Class imbalance & sampling correction** | 3.44% bad rate. If you undersample goods, the intercept must be corrected by `ln(sampling_rate)` or your PDs are systematically wrong. |
| **Basel III capital** | `basel_capital.py` is in the repo tree; no module covers RWA or the IRB correlation formula. |
| **Vintage / roll-rate / transition matrices** | `monitoring/transitions.py` is in the repo tree; no module covers it. |
| **Audit logging** | The FDE moat argument rests on "RBI-compliant audit logging." Not one line of it appears. Module 8 imports `logging` and never uses it. |

---

## PART C — India regulatory accuracy (highest-value fixes)

### C1. Ind AS 109 does **not** apply to Indian banks — Module 6 is wrong

This is the one factual error I'd most want corrected, because it's the kind of thing that gets noticed in an interview.

<cite index="3-1">Scheduled commercial banks (excluding regional rural banks) were originally scheduled for Ind AS adoption from 1 April 2018, deferred to 1 April 2019, and then deferred indefinitely by the RBI via notification dated 22 March 2019.</cite> As of 2026 banks still report under Indian GAAP and provision under the **IRACP** norms (incurred loss), not Ind AS 109.

<cite index="3-1">NBFCs follow a separate two-phase roadmap</cite> — so **NBFCs and HFCs genuinely do apply Ind AS 109 ECL**, banks do not. Module 6 currently conflates the two.

### C2. The thing Module 6 *should* be about: the RBI ECL Directions

This is live, current, and enormously relevant to what you're building.

<cite index="11-1">On 27 April 2026, the Reserve Bank of India issued the final directions on Expected Credit Loss (ECL)... These directions will be applicable for commercial banks (excluding small finance banks (SFBs), payments banks and local area banks), corresponding new banks and the State Bank of India (SBI). These directions shall come into effect from 1 April 2027.</cite>

Key features to add to the module:

- <cite index="17-1">A bank shall use a general approach consisting of three key functions — Probability of Default (PD), Loss Given Default (LGD), and Exposure at Default (EAD)</cite> — so your PD/LGD/EAD architecture maps directly onto it.
- **Prudential floors, which have no IFRS 9 equivalent.** <cite index="12-1">Whereas IFRS 9 is principle-based, RBI has introduced specific product-wise minimum provisioning floors for Stage 1 and Stage 2 exposures, acting as regulatory backstops.</cite> Your ECL engine therefore needs `final_provision = max(model_ecl, prudential_floor)` — a code change, not just a footnote.
- **Staging and NPA classification stay separate.** <cite index="14-1">While provisions would be made based on the new regime, the RBI intends to retain the existing norms for classifying loans as non-performing assets (NPAs).</cite> So the 90+ DPD NPA rule in Module 2 survives *alongside* three-stage provisioning — they are not the same thing, which the handbook currently implies.
- **Model risk management is now mandatory.** <cite index="12-1">Banks must establish board-level oversight, maintain model inventories, and implement structured validation and monitoring frameworks.</cite> This is a gift for the FDE narrative — it makes the MRM/audit-logging module a regulatory requirement rather than a nice-to-have.
- **Transition.** <cite index="12-1">Banks may spread the impact on profitability and capital adequacy over a four-year period (FY 2027-2031).</cite>

### C3. Basel — also worth a real module now

<cite index="6-1">The Reserve Bank of India (RBI) issued the (Commercial Banks – Capital Charge for Credit Risk – Standardized Approach) Directions, 2026 on April 27, 2026, effective April 01, 2027... In substance, these directions represent India's transposition of what the global banking industry has been calling Basel IV.</cite> A relevant detail for the handbook's framing: <cite index="6-1">Internal Ratings-Based approach usage is near zero</cite> in India — so Indian retail capital is standardised-approach driven, which is different from the IRB-centric material in most Western textbooks.

### C4. CIBIL `-1` and `0` will crash your API on new-to-credit applicants

`Field(..., ge=300, le=900)` rejects CIBIL's `-1` (no history) and `0` (insufficient history, <6 months). India's new-to-credit segment is enormous and is precisely the population fintech NBFCs target. As written, your validator 500s on them. Widen the bound and route NTC applicants to a separate thin-file scorecard — that's a genuinely good thing to teach.

### C5. The data localisation claim is overstated

The handbook says RBI "strictly forbids sending Indian citizens' financial records, PAN numbers, or credit reports to third-party public cloud endpoints outside the country." That's too broad. The precise position is: the RBI 2018 directive on **Storage of Payment System Data** requires payment system data to be stored in India; **CICRA 2005** governs credit information; and the **DPDP Act 2023** governs personal data generally. Tighten this — the argument is still strong, and being precise about *which* instrument applies is exactly the FDE credibility signal.

### C6. Redis bureau caching needs a compliance caveat

Field Hack #1 (24-hour TTL on raw CIBIL payloads keyed by PAN) is a real practice, but retention and reuse of credit information is constrained by CICRA 2005, your bureau contract, and purpose-limitation under DPDP. Add: cache only with contractual permission, encrypt at rest, key on a hash of PAN rather than raw PAN, and note the soft-vs-hard enquiry distinction.

### C7. `--allow-unauthenticated` undermines the whole thesis

Module 9 deploys a credit scoring endpoint open to the public internet, in a handbook whose central argument is regulatory rigour. Use `--no-allow-unauthenticated` with an IAM service account or API Gateway, plus mTLS in a bank context. Right now Module 9 contradicts the Executive Introduction.

---

## PART D — Internal contradictions and small stuff

| Location | Issue |
|---|---|
| §4.2 code vs prose | Clips to `300, 850` while text says 300–900 |
| Module 8 title vs Field Hack #2 | "<50ms" vs "Sub-20ms" |
| Field Hack #2 | **Advice is wrong.** It says "always use `async def`." For CPU-bound scoring (numpy matrix ops, sklearn `predict`), `async def` *blocks the event loop* and is the worst choice. FastAPI's plain `def` — which the Module 8 example correctly uses — runs it in a threadpool. Reword to: use `async def` only for I/O-bound work (bureau HTTP calls, Redis); use plain `def` for CPU-bound scoring. |
| §4.2 docstring | "Scales Logistic Regression log-odds" — ambiguous. State explicitly that the input is log-odds of **default**, which is what makes the minus sign correct. |
| Module 5 links | Repo tree lists `lgd_model.py`; links point to `lgd_data.py` |
| §11.1 diagram | Bottom box ends with a dangling `┬` connector going nowhere; top box right border misaligned |
| §10.2 diagram | `asia-south1a` should be `asia-south1-a` — and Cloud Run is regional/managed, you don't select zones, so the diagram is architecturally misleading. Show two *instances* behind the regional endpoint instead. |
| §2.1 | "if a dictionary has missing keys or **an** string" |
| §10.1 | "fails **catastrophic** when deployed" → catastrophically |
| §8.1 | `import logging` never used |
| Dockerfile | `build-essential` installed and never removed (bloat) — use a multi-stage build; no non-root `USER` (banks will fail this on security review); no `HEALTHCHECK`; `requirements.txt` should be fully pinned/hashed |

---

## PART E — What I'd add (in priority order)

1. **Module 6 rewrite** around the RBI ECL Directions (C1–C2). Biggest credibility win available, and it's current.
2. **A reason-codes / adverse-action module.** You promise it in the introduction and never deliver. It's also the single most FDE-flavoured thing in the whole domain — turning a scorecard into a regulator-defensible rejection letter.
3. **A model governance & audit module**: model inventory, independent validation, challenger models, immutable decision logs (application_id, model version, feature vector hash, score, decision, timestamp). RBI's ECL directions now make this mandatory, so it fits the narrative perfectly.
4. **A calibration & backtesting module** (B10) — because ECL is driven by calibration, not Gini.
5. **Reject inference** (B12).
6. **EAD/CCF section** to make Module 5's title honest (B7).
7. **A "known limitations" appendix.** Every real model document has one. Stating plainly that `last_pymnt_d` is a proxy, that the 2014 OOT vintage is immature, and that the dataset is US LendingClub data used as a stand-in for Indian retail — that honesty reads as *more* senior, not less. Right now the handbook asserts "Compiled & Verified" with a fully-ticked checklist, and a reviewer who finds A3 will discount everything else.

---

## Summary

**Fix before you learn from it:** A1, A2, **A3 (critical)**, A4, C1, C4, B4.

**Fix before you show it to anyone in the industry:** B1, B6, B10, C2, plus the Field Hack #2 async correction.

The bones are good. The `WOETransformer` bug (A3) and the immature-OOT issue (B1) are the two that would silently produce a model that looks fine and is worthless — those are worth understanding deeply, because they're exactly the failure modes real credit risk teams get burned by.
