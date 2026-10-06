# Databricks notebook source
# =============================================================================
# 09_export_observability
#
# Persist MLflow traces + evaluation runs into governed Delta tables so they're
# SQL-queryable (SQL Editor) and browsable in Catalog Explorer, alongside the
# other lumora_vendor_marketplace tables. This is the on-ramp to Lakehouse Monitoring
# (Phase 6): once traces/eval live in Delta, you can dashboard and alert on them.
#
# Writes:
#   lumora_vendor_marketplace.mlflow_traces      (one row per agent trace)
#   lumora_vendor_marketplace.mlflow_eval_runs   (one row per evaluation run + metrics)
# =============================================================================

# COMMAND ----------

# MAGIC %pip install --quiet -U "mlflow[databricks]>=3.1"
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %run ./00_config

# COMMAND ----------

import json
import mlflow
import pandas as pd

# CATALOG / SCHEMA come from 00_config
_exp = mlflow.get_experiment_by_name(EXPERIMENT_PATH)
EXPERIMENT_ID = _exp.experiment_id if _exp else None
print("Experiment:", EXPERIMENT_PATH, "id=", EXPERIMENT_ID)


def _write(pdf: pd.DataFrame, table: str):
    """Sanitize a pandas frame (dotted col names, nested objects) and write to Delta."""
    if pdf is None or len(pdf) == 0:
        print(f"[{table}] no rows to write")
        return
    pdf = pdf.copy()
    pdf.columns = [str(c).replace(".", "_").replace("/", "_").replace(" ", "_").replace("-", "_") for c in pdf.columns]

    def _cell(v):
        if v is None:
            return None
        if isinstance(v, str):
            return v
        if isinstance(v, float) and pd.isna(v):
            return None
        if isinstance(v, (int, float, bool)):
            return v
        # lists / dicts / spans / assessments / timestamps -> JSON string
        try:
            return json.dumps(v, default=str)
        except Exception:
            return str(v)

    for c in pdf.columns:
        if pdf[c].dtype == object:
            pdf[c] = pdf[c].map(_cell)

    sdf = spark.createDataFrame(pdf)
    (sdf.write.mode("overwrite").option("overwriteSchema", "true")
        .saveAsTable(f"{CATALOG}.{SCHEMA}.{table}"))
    print(f"[{table}] wrote {sdf.count()} rows; columns: {sdf.columns}")

# COMMAND ----------

# ---- Traces -> Delta --------------------------------------------------------
traces = mlflow.search_traces(experiment_ids=[EXPERIMENT_ID], max_results=500)
print("traces fetched:", len(traces), "| columns:", list(traces.columns) if hasattr(traces, "columns") else "n/a")
_write(traces, "mlflow_traces")

# COMMAND ----------

# ---- Evaluation runs (+ metrics) -> Delta -----------------------------------
runs = mlflow.search_runs(experiment_ids=[EXPERIMENT_ID], max_results=500)
print("runs fetched:", len(runs), "| columns:", list(runs.columns) if hasattr(runs, "columns") else "n/a")
_write(runs, "mlflow_eval_runs")

# COMMAND ----------

# ---- Show what a business user can now query (robust SELECT *) --------------
print("=== eval runs ===")
display(spark.sql(f"SELECT * FROM {CATALOG}.{SCHEMA}.mlflow_eval_runs ORDER BY start_time DESC"))
print("=== recent traces ===")
display(spark.sql(f"SELECT * FROM {CATALOG}.{SCHEMA}.mlflow_traces LIMIT 10"))
