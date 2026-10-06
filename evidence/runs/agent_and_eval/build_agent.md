# agent_and_eval / build_agent

- **Notebook:** `notebooks/05_build_agent`
- **Task run id:** `612976661148893` · **Result:** `SUCCESS`
- **Started:** 2026-10-06 07:11:12 UTC · **Ended:** 2026-10-06 07:14:12 UTC
- **Job run:** https://fevm-aws-serverless-ws-sr.cloud.databricks.com/?o=7474651022795245#job/104088374467144/run/295096389310523

_Exported from the job run with `databricks jobs export-run` — cell source followed by the output the cell produced in that run._

## Cell 1

```python
# =============================================================================
# 05_build_agent
#
# Phase 4 (code-first): log the multi-agent supervisor (agent/agent.py) to
# MLflow with the right resources for auth passthrough, validate it in-notebook
# on a structured question (-> Genie) and an unstructured one (-> docs), then
# register it to Unity Catalog. Deployment to a serving endpoint is done in 06.
# =============================================================================
```

## Cell 2

```python
%pip install --quiet -U databricks-langchain "langchain>=0.3" "langchain-core>=0.3" "langgraph>=0.6.0" "langgraph-prebuilt>=0.6.0" databricks-vectorsearch "mlflow[databricks]>=3.1"
dbutils.library.restartPython()
```

**Output:**

```text
[43mNote: you may need to restart the kernel using %restart_python or dbutils.library.restartPython() to use updated packages.[0m
```

## Cell 3

```python
%run ./00_config
```

## Cell 5

```python
import os
os.environ["LLM_ENDPOINT"] = LLM_ENDPOINT
os.environ["GENIE_SPACE_ID"] = GENIE_SPACE_ID
os.environ["VS_INDEX"] = VS_INDEX

# agent.py lives one level up from this notebook in the synced bundle files.
import sys
NB_DIR = os.path.dirname(dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get())
AGENT_PATH = "/Workspace" + NB_DIR.rsplit("/", 1)[0] + "/agent/agent.py"
print("agent.py:", AGENT_PATH)
```

**Output:**

```text
agent.py: /Workspace/Users/soumya.r@databricks.com/.bundle/lumora_vendor_marketplace/dev/files/agent/agent.py
```

## Cell 6

```python
# Quick smoke test of the graph BEFORE logging (fail fast on import/wiring).
import importlib.util
spec = importlib.util.spec_from_file_location("agent", AGENT_PATH)
agent_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent_mod)

resp = agent_mod.AGENT.predict(
    messages=[{"role": "user", "content": "Which vendors provide HCP data in Egypt?"}]
)
print("STRUCTURED (->Genie):")
print(resp.messages[-1].content[:900])
```

**Output:**

```text
STRUCTURED (->Genie):
|    | vendor_name         |   hcp_coverage | coverage_type   | contract_status   | contract_end   |
|---:|:--------------------|---------------:|:----------------|:------------------|:---------------|
|  0 | MediReach Analytics |          45429 | HCP count       | Active            | 2027-12-26     |
|  1 | OncoReach           |          37004 | HCP count       | Expired           | 2024-08-05     |
|  2 | AfriHealth Data     |          20903 | HCP count       | Expired           | 2025-11-08     |
```

## Cell 7

```python
resp2 = agent_mod.AGENT.predict(
    messages=[{"role": "user", "content": "Summarize MediReach Analytics' contract terms and how they derive HCP counts."}]
)
print("UNSTRUCTURED (->docs):")
print(resp2.messages[-1].content[:900])
```

**Output:**

```text
[NOTICE] Using a notebook authentication token. Recommended for development only. For improved performance, please use Service Principal based authentication. To disable this message, pass disable_notice=True.
UNSTRUCTURED (->docs):
Based on the retrieved documents:

## Contract Terms
**Vendor:** MediReach Analytics  
**Document Type:** Contract Summary

- **Term:** 2024-12-26 to 2027-12-26 (3-year term)
- **Status:** Active
- **Auto-renewal:** Successive 12-month terms unless cancelled 60 days before 2027-12-26
- **Termination:** Either party may terminate with 90 days' written notice; data must be destroyed within 30 days
- **Permitted use:** Internal analytics and reporting across Clinical, Commercial, and Corporate teams; onward redistribution prohibited without written consent
- **Data residency:** Must be processed within Lumora governed Databricks environment; no export to ungoverned storage
- **Delivery:** S3 delivery, monthly refresh cadence, 99.0% data-availability SLA

## HCP Count Derivation
**Vendor:** MediReach Analytics  
**Document Type:** Methodology & Coverage Notes

MediReach Analytics derives HCP
```

## Cell 8

```python
# Log the agent as an MLflow model with resources for auth passthrough.
import mlflow
from mlflow.models.resources import (
    DatabricksServingEndpoint,
    DatabricksVectorSearchIndex,
    DatabricksGenieSpace,
)

resources = [
    DatabricksServingEndpoint(endpoint_name="databricks-claude-sonnet-4-5"),
    DatabricksServingEndpoint(endpoint_name="databricks-gte-large-en"),
    DatabricksVectorSearchIndex(index_name=os.environ["VS_INDEX"]),
    DatabricksGenieSpace(genie_space_id=os.environ["GENIE_SPACE_ID"]),
]

with mlflow.start_run(run_name="lumora_supervisor"):
    logged = mlflow.pyfunc.log_model(
        name="agent",
        python_model=AGENT_PATH,
        resources=resources,
        pip_requirements=[
            "databricks-langchain",
            "langchain>=0.3",
            "langchain-core>=0.3",
            "langgraph>=0.6.0",
            "langgraph-prebuilt>=0.6.0",
            "databricks-vectorsearch",
            "mlflow[databricks]>=3.1",
        ],
        input_example={"messages": [{"role": "user", "content": "Which vendors provide HCP data in Egypt?"}]},
    )
print("logged:", logged.model_uri)
```

**Output:**

```text
🔗 View Logged Model at: https://fevm-aws-serverless-ws-sr.cloud.databricks.com/ml/experiments/1765197035583236/models/m-c93377e8ce884efe828aa99ddf76c59f?o=7474651022795245
2026/10/06 07:12:55 INFO mlflow.pyfunc: Predicting on input example to validate output
```

```text
logged: models:/m-c93377e8ce884efe828aa99ddf76c59f
```

## Cell 9

```python
# Validate the LOGGED model (as it will run when served).
loaded = mlflow.pyfunc.load_model(logged.model_uri)
out = loaded.predict({"messages": [{"role": "user", "content": "List all vendors offering clinical trial data."}]})
print(out["messages"][-1]["content"][:900] if isinstance(out, dict) else out)
```

**Output:**

```text
|    | vendor_name           | headquarters   |
|---:|:----------------------|:---------------|
|  0 | CardioData Partners   | EU             |
|  1 | GlobalTrials Registry | UK             |
|  2 | ImmunoData            | US             |
|  3 | OncoReach             | US             |
|  4 | TrialSphere Global    | UK             |
```

## Cell 10

```python
# Register to Unity Catalog.
mlflow.set_registry_uri("databricks-uc")
UC_MODEL = f"{FQ}.vendor_marketplace_supervisor"
registered = mlflow.register_model(model_uri=logged.model_uri, name=UC_MODEL)
print("registered:", UC_MODEL, "version", registered.version)
dbutils.jobs.taskValues.set(key="model_version", value=registered.version)
```

**Output:**

```text
Registered model 'aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.vendor_marketplace_supervisor' already exists. Creating a new version of this model...
```

```text
🔗 Created version '3' of model 'aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.vendor_marketplace_supervisor': https://fevm-aws-serverless-ws-sr.cloud.databricks.com/explore/data/models/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/vendor_marketplace_supervisor/version/3?o=7474651022795245
```

```text
registered: aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.vendor_marketplace_supervisor version 3
```
