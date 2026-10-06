# Databricks notebook source
# =============================================================================
# 05_build_agent
#
# Phase 4 (code-first): log the multi-agent supervisor (agent/agent.py) to
# MLflow with the right resources for auth passthrough, validate it in-notebook
# on a structured question (-> Genie) and an unstructured one (-> docs), then
# register it to Unity Catalog. Deployment to a serving endpoint is done in 06.
# =============================================================================

# COMMAND ----------

# MAGIC %pip install --quiet -U databricks-langchain "langchain>=0.3" "langchain-core>=0.3" "langgraph>=0.6.0" "langgraph-prebuilt>=0.6.0" databricks-vectorsearch "mlflow[databricks]>=3.1"
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %run ./00_config

# COMMAND ----------

import os
os.environ["LLM_ENDPOINT"] = LLM_ENDPOINT
os.environ["GENIE_SPACE_ID"] = GENIE_SPACE_ID
os.environ["VS_INDEX"] = VS_INDEX

# agent.py lives one level up from this notebook in the synced bundle files.
import sys
NB_DIR = os.path.dirname(dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get())
AGENT_PATH = "/Workspace" + NB_DIR.rsplit("/", 1)[0] + "/agent/agent.py"
print("agent.py:", AGENT_PATH)

# COMMAND ----------

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

# COMMAND ----------

resp2 = agent_mod.AGENT.predict(
    messages=[{"role": "user", "content": "Summarize MediReach Analytics' contract terms and how they derive HCP counts."}]
)
print("UNSTRUCTURED (->docs):")
print(resp2.messages[-1].content[:900])

# COMMAND ----------

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

# COMMAND ----------

# Validate the LOGGED model (as it will run when served).
loaded = mlflow.pyfunc.load_model(logged.model_uri)
out = loaded.predict({"messages": [{"role": "user", "content": "List all vendors offering clinical trial data."}]})
print(out["messages"][-1]["content"][:900] if isinstance(out, dict) else out)

# COMMAND ----------

# Register to Unity Catalog.
mlflow.set_registry_uri("databricks-uc")
UC_MODEL = f"{FQ}.vendor_marketplace_supervisor"
registered = mlflow.register_model(model_uri=logged.model_uri, name=UC_MODEL)
print("registered:", UC_MODEL, "version", registered.version)
dbutils.jobs.taskValues.set(key="model_version", value=registered.version)
