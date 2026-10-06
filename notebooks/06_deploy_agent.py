# Databricks notebook source
# =============================================================================
# 06_deploy_agent
#
# Phase 4 (deploy): deploy the registered supervisor model to a Mosaic AI
# agent serving endpoint (Agent Framework). Review App + REST endpoint come
# for free, so you can chat with it and it's callable from an app.
# =============================================================================

# COMMAND ----------

# MAGIC %pip install --quiet -U databricks-agents "mlflow[databricks]>=3.1"
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %run ./00_config

# COMMAND ----------

import mlflow
from databricks import agents
from mlflow.tracking import MlflowClient

mlflow.set_registry_uri("databricks-uc")
UC_MODEL = f"{FQ}.vendor_marketplace_supervisor"

# Latest registered version.
client = MlflowClient(registry_uri="databricks-uc")
version = max(int(v.version) for v in client.search_model_versions(f"name='{UC_MODEL}'"))
print(f"Deploying {UC_MODEL} v{version} ...")

deployment = agents.deploy(
    UC_MODEL,
    version,
    scale_to_zero=True,
    tags={"demo": "lumora_genie", "phase": "4"},
)
print("Endpoint:", deployment.endpoint_name)
print("Review App:", getattr(deployment, "review_app_url", "(see serving UI)"))

# COMMAND ----------

# Note: the endpoint takes several minutes to come online. Validate with:
#   databricks serving-endpoints get <endpoint_name>
# then query it as a chat endpoint with the flagship questions.
