# Lumora Clinical Research × Databricks — Governed Vendor-Data Marketplace

Business presentation for the Lumora Clinical Research (fictional CRO) governed vendor-data marketplace.
All figures marked as assumptions are illustrative, not customer data. All data in the build is synthetic.

Google Slides: https://docs.google.com/presentation/d/1FxS7cNgPotaaIvkm2yCXd2ab9bAYoDNGljdTQSRGuVo/edit  ·  PDF: `Lumora_Vendor_Marketplace_Deck.pdf`

---

## Slide 1 — From spreadsheet guesswork to governed answers

_From an 18-spreadsheet vendor hunt to a governed, complete answer in seconds._

**Speaker notes**

- *Purpose:* Open with the outcome, not the technology. Set expectations: 10 minutes of business framing, then a live demo, then the value model and next steps.
- *Talk track:* Lumora spends millions a year on third-party data and makes study-feasibility and commercial decisions on it. Today, finding out which vendor covers what, where, takes days and the answers are inconsistent. In the next 30 minutes I'll show how we turn that into a governed, instant, auditable answer — and what it is worth. Lumora is a fictional CRO and every dataset you will see is synthetic.
- *Evidence:* Reference build runs end-to-end on Databricks on synthetic data (fictional CRO and fictional vendors).
- *Transition:* That payoff rests on fixing something painful — let me start with the problem your teams hit every day.
- *Likely question:* Is this real data? — No. Everything is synthetic so it can be shared; the pipeline is identical for real vendor catalogs.

---

## Slide 2 — Today: the vendor catalog lives in spreadsheets — and so do the risks

- It's never one question: teams constantly interrogate ~18 vendors — coverage, contracts, methodology, SLAs, onboarding.
- The catalog is two kinds of data: structured spreadsheets (vendor × data type × region × counts) AND unstructured free-text files (contract terms, data dictionaries, methodology, onboarding).
- A SQL join can't answer plain-English or document questions; pasting spreadsheets + docs into a prompt can't answer either kind reliably.
- Structured answers drift and drop vendors — 1 of 3 in a real run — and document answers come back ungrounded and uncited.
- Contract cost and vendor-contact PII sit in open files; no evaluation, no audit trail; renewals slip past unnoticed.

**Speaker notes**

- *Purpose:* Make the cost of the status quo concrete for both personas.
- *Talk track:* The teams don't ask one question — they ask a constant stream about these vendors. And the answers live in two very different places: structured spreadsheets — vendor, data type, region, counts — and unstructured free-text files like contract terms, data dictionaries, methodology notes and onboarding guides. You can't SQL-join your way to the document questions, and you can't paste everything into a prompt and trust it: the structured answers drift and silently drop qualifying vendors, and the document answers are ungrounded guesses. On top of that, cost and contact PII are exposed, nothing measures answer quality, and renewals lapse.
- *Evidence:* Observed failure mode in the reference environment: the prompt-stuffing path answered the Egypt HCP question with 1 vendor instead of 3. · 72 free-text vendor documents (contract summaries, data dictionaries, methodology, onboarding) also have to be answerable, not just the tables.
- *Transition:* Here's what that costs — and what it means for the people who own it.
- *Likely question:* Why not just join the spreadsheets and run SQL? — That handles the easy, structured half only. Half the questions are answered from free-text documents, and users ask in plain English, not SQL — so you need both a governed structured layer and grounded document retrieval, which is exactly the split in the solution.

---

## Slide 3 — For the executive sponsor (COO / Chief Data & Analytics Officer)

**What you get**
- Lower 3PD spend: duplicate purchases and blind renewals surface early
- Faster study start-up: feasibility questions answered in minutes
- Lower data risk: cost and PII governed by policy, audited

**KPIs you can track**
- 3PD spend under management and % renewed with a decision
- Request turnaround time (target: same day)
- Access-policy coverage of sensitive fields (target: 100%)


**Speaker notes**

- *Purpose:* Frame value in the sponsor's language: spend, speed, risk.
- *Talk track:* For the COO or CDAO this is three things. Spend: with every vendor contract and its coverage in one governed place, you can see overlapping purchases and walk into every renewal with data. Speed: feasibility and targeting questions stop being a ticket queue. Risk: contract cost and vendor contact PII are protected by a policy in the catalog — enforced in every tool — and every query is audited.
- *Evidence:* Unity Catalog column masks and row filters enforce access per user across SQL, Genie, dashboards and apps in the reference build.
- *Transition:* Now the person who lives with this every day — the domain owner.
- *Likely question:* How do we measure it? — Turnaround and completeness are measured from day one; spend levers are tracked at each renewal.

---

## Slide 4 — For the domain owner (Head of Data Partnerships & RWD Sourcing)

**What changes for your team**
- Self-service answers from the business, with the SQL shown
- Data-quality rules written in plain English
- One place to manage vendors, coverage, contracts

**KPIs you own**
- Answer completeness and accuracy (eval-scored)
- Catalog data-quality pass rate
- Renewal pipeline: contracts expiring with spend at risk


**Speaker notes**

- *Purpose:* Show the domain owner what their day looks like and which KPIs they control.
- *Talk track:* For the head of data partnerships, the team stops being a human search engine. Business users get complete answers with the SQL that produced them. Your team writes data-quality rules in English and they run as pipeline checks. And you get a live view of renewals and spend at risk instead of a spreadsheet you maintain by hand.
- *Evidence:* Reference build: a natural-language DQ rule (coverage ≥ 5,000 records) compiled to SQL and enforced in a Lakeflow pipeline, flagging 28 of 126 coverage rows (98 kept). · Metric views define Spend at Risk and Expiring Soon Contracts once for Genie and the dashboard; 4 contracts are currently Expiring Soon.
- *Transition:* So what is all of that worth? Here are the numbers.
- *Likely question:* Does my team need to write code? — No for asking questions and writing DQ rules; the pipeline itself is deployed once as code.

---

## Slide 5 — The outcome: faster, complete, governed vendor decisions

**~$600K / year**
- Illustrative annual value: analyst time, avoided duplicate data buys, better renewals

**Days → minutes**
- Vendor-sourcing requests answered in the same session, with the SQL shown

**3 of 3 vendors**
- Complete, deterministic answers — the old pattern returned 1 of 3


> Value figures are illustrative assumptions (see value model slide), not customer data. Completeness result from the reference build.

**Speaker notes**

- *Purpose:* Lead with the three numbers the buyer cares about before any architecture.
- *Talk track:* Three outcomes. First, money: on conservative-but-realistic assumptions this is worth roughly six hundred thousand dollars a year — I'll show the math later and you can change every input. Second, speed: a request that takes an analyst about three business days becomes a same-session answer. Third, trust: asked which vendors provide HCP data in Egypt, the governed solution returns all three matching vendors every time; the spreadsheet-in-a-prompt pattern returned one.
- *Evidence:* Value model: 600 requests × 5.5 h saved × $95/h + 5% duplicate-spend avoided + 10% renewal saving on 30% of $3.6M spend. · Reference build: Genie returns MediReach 45,429 / OncoReach 37,004 / AfriHealth 20,903 HCPs for Egypt; the prompt-stuffing assistant returned only GlobalHCP Registry.
- *Transition:* And here's how it works, end to end.
- *Likely question:* Where does $600K come from? — Three levers, all assumptions you can replace; slide 9 shows each formula.

---

## Slide 6 — One integrated journey on Databricks

| 1 · Lakeflow | 2 · Unity Catalog | 3 · Lakebase | 4 · Gen AI | 5 · Genie Agent | 6 · Databricks App |
|---|---|---|---|---|---|
| Auto Loader pipeline ingests raw vendor catalogs → Bronze → Silver → Gold; DQ expectations | Lineage, comments, column masks & row filters, metric views | Millisecond serving of vendor tiles to the app | Agent Bricks supervisor + Knowledge Assistant; MLflow eval; AI Gateway guardrails | Natural language → SQL; every matching vendor, SQL shown | Marketplace UI with AI assistant, plus AI/BI dashboard with Ask Genie |

> Every stage is built and running in the reference environment on synthetic data · one Lakeflow Job runs the journey end to end.

**Speaker notes**

- *Purpose:* Give the one-picture view of the six stages and show they are connected, not siloed.
- *Talk track:* Left to right: Lakeflow lands the raw vendor-catalog files with Auto Loader and builds governed Gold tables, with data-quality expectations on the way. Unity Catalog governs them — lineage, descriptions, masks for cost and contact PII, and metric views that define each business number once. Lakebase serves the app's tiles in milliseconds. The Gen AI layer is an Agent Bricks supervisor that sends factual questions to Genie and document questions to a Knowledge Assistant, with MLflow scoring answers and AI Gateway screening prompts. Genie turns plain English into SQL. And the business sees it all through a Databricks App and an AI/BI dashboard. One copy of the data, one policy, every surface.
- *Evidence:* Same Gold tables feed Genie, the agent, Lakebase, the app and the dashboard in the reference build. · Build facts: 18 fictional vendors, 126 coverage rows, 44 products, 292 data elements, 72 vendor documents indexed in Vector Search; Auto Loader Lakeflow pipeline Bronze → Silver → Gold; 3 column masks + 1 row filter; 2 metric views; one Lakeflow Job runs the journey end to end.
- *Transition:* Let me show it live.
- *Likely question:* Why both a supervisor and Genie? — Genie answers structured questions; the Knowledge Assistant answers from documents; the supervisor routes between them.

---

## Slide 7 — Live demo: the journey a sourcing request takes

- App → "Which vendors provide HCP data in Egypt?" — all 3 vendors, with counts
- Same box → "How does AfriHealth derive its counts?" — answered from documents, cited
- Genie → expand the SQL; the same answer from a governed metric view
- Dashboard → filter HCP + Egypt; Ask Genie; spend tiles masked by role
- Guardrails → a hostile or PII-bearing prompt is blocked before the model
- MLflow → every answer traced and scored; then a DQ rule written in English

**Speaker notes**

- *Purpose:* Signal the switch to the live demo and give the audience the map of what they are about to see.
- *Talk track:* SWITCH TO THE LIVE DEMO NOW. Start in the marketplace app and ask the flagship question; point out it returns every matching vendor. Ask the document question to show routing to the Knowledge Assistant. Open Genie and expand the SQL. Show the metric view, then the dashboard: filter to HCP and Egypt, use Ask Genie, and show the spend tiles masked for a non-finance user. Show the AI Gateway blocking a hostile prompt and masking PII. Close the demo in MLflow with traces and judge scores, then write a data-quality rule in plain English. Come back to the deck for value and next steps. Live links — App: https://lumora-data-marketplace-7474651022795245.aws.databricksapps.com · Genie: https://fevm-aws-serverless-ws-sr.cloud.databricks.com/genie/rooms/01f1c14e775014ac9693c78ae663bc6c · Dashboard: https://fevm-aws-serverless-ws-sr.cloud.databricks.com/dashboardsv3/01f1c150bacd1aa3bab5046199ce019a/published. For contract renewals, ask Genie which contracts are expiring soon: 4 come back (GlobalTrials Registry, TrialSphere Global, PubSignal Ltd, NeuroGraph), and as a non-finance user Genie reports their cost as masked for your role.
- *Evidence:* All demo steps run on the reference build; Genie explains 'masked for your role' when a non-finance user asks for spend. · 4 contracts Expiring Soon: GlobalTrials Registry, TrialSphere Global, PubSignal Ltd, NeuroGraph.
- *Transition:* Back from the demo — why can you trust what you just saw?
- *Likely question:* Can business users break it? — Guardrails block unsafe prompts, masks limit what each user sees, and every answer shows its SQL.

---

## Slide 8 — Trust by design: governed data, governed AI

**Governed data**
- Contract cost visible to finance only; contact email/phone masked
- Commercial contacts row-filtered by role
- Lineage and audit for every query

**Governed AI**
- Safety + PII guardrails at the prompt boundary
- Eval gate caught a masked-cost leak in documents before go-live
- Rate limits and usage tracking cap spend


**Speaker notes**

- *Purpose:* Address the risk objection for both personas: data access and AI behavior.
- *Talk track:* Two halves of trust. On the data side, the policy lives on the table, not in the app: finance sees contract cost, everyone else sees it masked; contact details are partially masked; commercial contacts are filtered out entirely for non-finance roles — and it's enforced the same way in SQL, Genie, the dashboard and the app. On the AI side, AI Gateway screens toxic and PII-bearing prompts, and usage is tracked and rate-limited. And the evaluation gate earns its keep: before go-live it caught a governance leak — contract cost was masked in the tables but still present in generated contract documents reachable through document search. We kept masked values out of unstructured content, re-indexed the documents and re-ran the evaluation clean. That is exactly the kind of issue an eval-gated approach finds before a user does.
- *Evidence:* Reference build: 3 column masks + 1 row filter evaluated per querying user; AI Gateway returned input_guardrail_triggered for a hateful prompt and anonymized an SSN/email. · Evaluation gate flagged cost leaking through documents; fixed by keeping masked values out of unstructured content, re-indexing, and re-running evaluation clean.
- *Transition:* So what is it worth? Here is the value model.
- *Likely question:* Do masks follow the data into Lakebase? — No; the serving table only carries non-sensitive fields by design.

---

## Slide 9 — Value model (illustrative assumptions — replace with Lumora's numbers)

| Lever | Assumption | Formula | Annual value |
|---|---|---|---|
| Analyst time on sourcing requests | 600 requests/yr; 6.0 h → 0.5 h; $95/h loaded | 600 × 5.5 h × $95 | $313,500 |
| Duplicate / overlapping data purchases avoided | $3.6M 3PD spend (18 vendors × ~$200K); 5% avoided | $3.6M × 5% | $180,000 |
| Renewal optimization | 30% of spend renews/yr; 10% negotiated saving | $3.6M × 30% × 10% | $108,000 |
| Total illustrative value | Platform run cost assumed $50K/yr (to be sized) | ≈ 12× value / cost; payback ≈ 1 month | $601,500 |
| Conservative case | Half the requests, half the time saved, half the spend levers | $78,375 + $90,000 + $54,000 | $222,375 (≈ 4.4×) |

> All inputs are illustrative assumptions, not Lumora or customer data. Run cost to be validated with a Databricks sizing.

**Speaker notes**

- *Purpose:* Quantify impact transparently so the buyer can own and adjust every input.
- *Talk track:* Three levers. Analyst time: 600 sourcing requests a year at six hours each today, half an hour of review with the solution, at a 95-dollar loaded rate — about 314 thousand. Duplicate purchases: with coverage across all vendors in one view, avoiding just 5 percent overlap on 3.6 million of spend is 180 thousand. Renewals: walking into the 30 percent of contracts that renew each year with spend-at-risk data and saving 10 percent is 108 thousand. About 600 thousand a year against an assumed 50 thousand run cost. Even if you halve every input, it is still over 220 thousand — more than four times the cost.
- *Evidence:* Formulas shown in the table; conservative case recomputed with every lever halved. · Run cost is an assumption pending a Databricks sizing.
- *Transition:* Here is what the reference build already proves.
- *Likely question:* What would you need from us to firm this up? — Request volume, time per request, 3PD spend and renewal calendar.

---

## Slide 10 — Proof points from the reference build

- Flagship question: 3 of 3 matching vendors, deterministic, SQL shown (old pattern: 1 of 3)
- Same answer from a governed metric view — one definition of "coverage"
- Non-finance users get cost masked; Genie explains "masked for your role"
- LLM-judge evaluation on 4 question classes: correctness, relevance and safety all 1.0
- Eval gate caught a governance leak (masked cost in documents) before go-live — fixed, re-indexed, re-run clean
- Guardrails: hateful prompt blocked; SSN and email anonymized before the model
- Plain-English DQ rule enforced in a Lakeflow pipeline: 28 of 126 coverage rows flagged (98 kept)
- One Lakeflow Job runs it end to end: 18 vendors, 126 coverage rows, 72 documents indexed

> Results from the reference build on synthetic data; evaluation scores to be re-measured on Lumora's questions.

**Speaker notes**

- *Purpose:* Anchor the value claims in what was actually executed.
- *Talk track:* Everything on this slide was executed, not mocked. The flagship question returns all three vendors with the SQL. The metric view gives the same answer from a single governed definition. Masks work per user, and Genie tells a non-finance user the value is masked rather than inventing one. MLflow's LLM judges scored correctness, relevance and safety at 1.0 across four question classes — vendor by geography, vendor by data type, contract renewals, and document methodology — with ground truth derived from the governed tables at run time; we will re-run that on your real questions. Better still, the evaluation gate caught a governance leak before go-live: cost was masked in the tables but still visible in generated contract documents through document search. We kept masked values out of unstructured content, re-indexed, and the evaluation re-ran clean. The gateway blocked a hostile prompt and anonymized PII, and a rule written in English became a pipeline check that flagged 28 of 126 coverage rows.
- *Evidence:* Execution logs and query results are committed as text in the project repository's evidence folder. · Evaluation: 4 question classes, ground truth from governed tables at run time; correctness 1.0, relevance 1.0, safety 1.0.
- *Transition:* How do we get from here to production?
- *Likely question:* Will accuracy hold on our data? — That is what the evaluation gate is for: we score on your question set before go-live.

---

## Slide 11 — Rollout: value in 30 days, production in 90

**Days 0–30**
- Land 3–5 real vendor catalogs
- Genie on governed Gold
- Baseline turnaround & completeness

**Days 31–60**
- Masks, metric views, dashboard
- Supervisor + documents
- Eval gate on real questions

**Days 61–90**
- App to sourcing teams
- All vendors, scheduled ingest
- Track spend & renewal KPIs


**Speaker notes**

- *Purpose:* Show a low-risk, phased path where each phase delivers measurable value.
- *Talk track:* We don't boil the ocean. In the first 30 days we land a handful of real vendor catalogs and put Genie on top — enough to measure turnaround and completeness against today. Days 31 to 60 add governance, the metric layer and dashboard, the document assistant, and the evaluation gate on your real questions. By day 90 the app is in the hands of the sourcing teams with every vendor on scheduled ingestion, and we're tracking the spend and renewal KPIs.
- *Evidence:* The reference build is packaged as a Databricks Asset Bundle with a deployment guide, so phase 1 starts from working code.
- *Transition:* Which brings me to what we're asking for.
- *Likely question:* What do you need from our team? — A data owner, a few real catalogs, a workspace, and a list of real questions.

---

## Slide 12 — The ask

- Executive sponsor: approve a 30-day pilot and name a domain owner
- Domain owner: share 3–5 vendor catalogs and 20 real sourcing questions
- Together: confirm the value-model inputs and success KPIs
- Databricks: deploy the reference build in Lumora's workspace and size the run cost

**Speaker notes**

- *Purpose:* Close with a concrete, owned next step for each persona.
- *Talk track:* Four asks. From the sponsor: a 30-day pilot and a named owner. From the domain owner: a few real catalogs and twenty real questions — that becomes the evaluation set. Together we replace my assumptions with your numbers and agree the success KPIs. And we deploy the reference build in your workspace and size the run cost properly.
- *Evidence:* Pilot scope mirrors Days 0–30 of the rollout plan.
- *Transition:* Thank you — let's take questions.
- *Likely question:* How long until we see something? — A working Genie space on your catalogs within the first two weeks.

---

## Slide 13 — Closing / Q&A

**Speaker notes**

- *Purpose:* Closing slide while taking questions.
- *Talk track:* Thank you. Happy to go back into the demo for any question — Genie, masking, the dashboard, or the evaluation results.
- *Evidence:* Demo environment remains available for follow-up questions.
- *Transition:* Open Q&A.
- *Likely question:* Can we get the materials? — Yes: this deck, the walkthrough and the repository with execution evidence.
