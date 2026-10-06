# Lumora Clinical Research — Governed Third-Party Data Vendor Marketplace on Databricks

> **Industry:** Life sciences · Contract Research Organization (CRO)
> **Customer (fictional):** Lumora Clinical Research — a mid-size global CRO.
> **Data:** 100% synthetic. Vendor names, contacts, contracts and documents are fictional.

## The business problem

Lumora's feasibility, real-world-evidence and commercial teams constantly ask *"which
third-party data vendor covers **this** data type, in **this** country, for **this**
therapeutic area?"* — e.g. **"Which vendors provide HCP (healthcare professional) data in
Egypt?"** The vendor catalog lives in spreadsheets on a shared drive. A homegrown assistant
pastes those spreadsheets into an LLM prompt, so:

- answers are **incomplete and inconsistent** (in a live failure it named 1 vendor instead of 3),
- nobody can see the SQL or reproduce an answer,
- **contract cost and vendor-contact PII** are visible to anyone who can open the files,
- there is no evaluation, no guardrails, and renewals slip.

**The reframe:** "who covers HCP in Egypt?" is a *structured filter*, not a search problem.
Land the catalog as governed tables and the question becomes a deterministic query that
returns **every** matching vendor, every time — then layer Gen AI on top for documents and
conversation, with governance enforced by the platform rather than by each app.

## The integrated data journey

```
 raw vendor-catalog JSON (UC Volume)
        │  Lakeflow Declarative Pipeline · Auto Loader (exactly-once, schema inference, expectations)
        ▼
 bronze_vendor_catalog ─► silver_vendor_catalog ─► Gold MVs: vendors · contracts · data_products · coverage · data_elements
        │  Unity Catalog: comments (Genie ontology) · column mask on cost · contacts PII masks + row filter · metric views
        ├──────────────► Genie Agent (NL→SQL over tables + metric views)  ─┐
        ├──────────────► 72 vendor documents → Vector Search / Knowledge Assistant ─┤─► Agent Bricks Supervisor
        ├──────────────► Lakebase Postgres (vendor_tiles, ms reads)  ─────┐        │   (+ MLflow eval, AI Gateway)
        └──────────────► AI/BI dashboard (metric views, Ask Genie)        ▼        ▼
                                                        Databricks App: Lumora Data Marketplace (tiles + AI assistant)
```

## Requirement → build → evidence

| Stage | What runs | Code | Execution evidence (text) |
|---|---|---|---|
| **Lakeflow — ingest** | Auto Loader declarative pipeline (Bronze streaming table → Silver with expectations → Gold materialized views); second DQ-expectations pipeline; one Lakeflow Job orchestrating the whole journey | [`pipelines/ingest_vendor_catalog.py`](pipelines/ingest_vendor_catalog.py), [`notebooks/13_dlt_quality_pipeline.py`](notebooks/13_dlt_quality_pipeline.py), [`databricks.yml`](databricks.yml) | [`evidence/pipelines/`](evidence/pipelines/), [`evidence/runs/end_to_end/`](evidence/runs/end_to_end/) |
| **Unity Catalog — govern** | Schema/volume, comments, lineage, column mask on contract cost (declared in the pipeline), PII masks + row filter on contacts, metric views, least-privilege grants for the app | [`notebooks/01_setup_and_generate_raw.py`](notebooks/01_setup_and_generate_raw.py), [`notebooks/14_governance_masking.py`](notebooks/14_governance_masking.py), [`notebooks/15_metric_views.py`](notebooks/15_metric_views.py) | [`evidence/sql_evidence.md`](evidence/sql_evidence.md) §2–3 |
| **Lakebase — operational serving** | Lakebase instance (bundle resource) serving `vendor_tiles` to the app with OAuth credentials | [`notebooks/11_sync_to_lakebase.py`](notebooks/11_sync_to_lakebase.py), [`app_ui/lakebase_utils.py`](app_ui/lakebase_utils.py) | [`evidence/runs/end_to_end/sync_to_lakebase.md`](evidence/runs/end_to_end/sync_to_lakebase.md), [`evidence/platform_status.md`](evidence/platform_status.md) |
| **ML / Gen AI** | Vector Search over 72 docs; Agent Bricks Knowledge Assistant + Supervisor; code-first LangGraph supervisor registered to UC; MLflow prompt registry, tracing, LLM-judge eval; AI Gateway guardrails; LLM-authored DQ rules | [`notebooks/03`](notebooks/03_generate_vendor_docs.py)–[`09`](notebooks/09_export_observability.py), [`agent/agent.py`](agent/agent.py), [`agent_bricks/create_agents.py`](agent_bricks/create_agents.py), [`notebooks/10_data_quality.py`](notebooks/10_data_quality.py) | [`evidence/agent_bricks_responses.md`](evidence/agent_bricks_responses.md), [`evidence/ai_gateway_guardrails.md`](evidence/ai_gateway_guardrails.md), [`evidence/mlflow_evaluation.md`](evidence/mlflow_evaluation.md), [`evidence/runs/agent_and_eval/`](evidence/runs/agent_and_eval/) |
| **Genie Agent** | One Genie space over Gold tables, view, metric views and masked contacts, with instructions, certified SQL and benchmarks | [`genie/create_space.py`](genie/create_space.py) | [`evidence/genie_conversations.md`](evidence/genie_conversations.md) |
| **Databricks App** | Streamlit marketplace: Lakebase-served vendor tiles + AI assistant calling the supervisor; plus an AI/BI dashboard with Ask Genie | [`app_ui/`](app_ui/), [`dashboards/build_dashboard.py`](dashboards/build_dashboard.py) | [`evidence/platform_status.md`](evidence/platform_status.md), [`evidence/app_logs.md`](evidence/app_logs.md) |

Business presentation: [`deck/Lumora_Vendor_Marketplace_Deck.pdf`](deck/Lumora_Vendor_Marketplace_Deck.pdf) (text + speaker notes: [`deck/deck.md`](deck/deck.md)).

## How to run it

Prereqs: Databricks CLI ≥ 0.27x authenticated to a workspace with serverless, Unity Catalog,
Lakebase and Agent Bricks; a Vector Search endpoint; a secret `llm_secrets/anthropic_api_key`
for the AI Gateway external model (or swap it for any provider). Set catalog/schema in
[`notebooks/00_config.py`](notebooks/00_config.py) and [`databricks.yml`](databricks.yml).

```bash
databricks bundle deploy                        # pipelines, jobs, Lakebase instance, AI Gateway endpoint, app
databricks bundle run end_to_end                # 01 → Auto Loader pipeline → 02 → 14 → 15 · 03 → 04 · 10 → DQ pipeline · 11
python3 genie/create_space.py                   # Genie space  → paste id into 00_config GENIE_SPACE_ID
python3 agent_bricks/create_agents.py           # Knowledge Assistant + Supervisor + app SP grants → agent_bricks/agents.json
databricks bundle deploy --var supervisor_endpoint=<from agents.json>
databricks bundle run marketplace               # deploy the app
databricks bundle run agent_and_eval            # code-first agent build, validation, MLflow eval + export
python3 dashboards/build_dashboard.py           # AI/BI dashboard (published with viewer credentials)
python3 evidence/tools/export_job_runs.py ...   # regenerate the evidence (see evidence/README.md)
```

Create a group `lumora_finance` to see unmasked contract cost and contact PII; everyone
else gets masked values automatically (SQL, Genie, metric views, dashboard, app).

## Repository layout

| Path | Purpose |
|---|---|
| `notebooks/` | Numbered notebooks run by the Lakeflow Jobs (`00_config` is the single config) |
| `pipelines/` | Lakeflow Declarative Pipeline (Auto Loader ingest) |
| `genie/`, `agent_bricks/`, `dashboards/` | API-driven setup of the Genie space, Agent Bricks agents and AI/BI dashboard |
| `agent/` | Code-first LangGraph supervisor (Mosaic AI Agent Framework) |
| `app_ui/` | Databricks App (Streamlit) |
| `evidence/` | **Execution evidence as text** — exported job runs, pipeline event logs, live query/agent/Genie/gateway output |
| `deck/` | Business presentation (PDF + Markdown with speaker notes) |
