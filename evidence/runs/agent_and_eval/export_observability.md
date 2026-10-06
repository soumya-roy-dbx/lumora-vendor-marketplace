# agent_and_eval / export_observability

- **Notebook:** `notebooks/09_export_observability`
- **Task run id:** `358153134130664` · **Result:** `SUCCESS`
- **Started:** 2026-10-06 07:19:14 UTC · **Ended:** 2026-10-06 07:20:02 UTC
- **Job run:** https://fevm-aws-serverless-ws-sr.cloud.databricks.com/?o=7474651022795245#job/104088374467144/run/295096389310523

_Exported from the job run with `databricks jobs export-run` — cell source followed by the output the cell produced in that run._

## Cell 1

```python
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
```

## Cell 2

```python
%pip install --quiet -U "mlflow[databricks]>=3.1"
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
```

**Output:**

```text
Experiment: /Users/soumya.r@databricks.com/lumora_genie_eval id= 1765197035583318
```

## Cell 6

```python
# ---- Traces -> Delta --------------------------------------------------------
traces = mlflow.search_traces(experiment_ids=[EXPERIMENT_ID], max_results=500)
print("traces fetched:", len(traces), "| columns:", list(traces.columns) if hasattr(traces, "columns") else "n/a")
_write(traces, "mlflow_traces")
```

**Output:**

```text
/home/spark-be28871f-1f48-46dd-b564-a3/.ipykernel/67/command-5623723460998487-3908901755:2: FutureWarning: Parameter 'experiment_ids' is deprecated. Please use 'locations' instead.
  traces = mlflow.search_traces(experiment_ids=[EXPERIMENT_ID], max_results=500)
```

```text
traces fetched: 20 | columns: ['trace_id', 'trace', 'client_request_id', 'state', 'request_time', 'execution_duration', 'request', 'response', 'trace_metadata', 'tags', 'spans', 'assessments']
[mlflow_traces] wrote 20 rows; columns: ['trace_id', 'trace', 'client_request_id', 'state', 'request_time', 'execution_duration', 'request', 'response', 'trace_metadata', 'tags', 'spans', 'assessments']
```

## Cell 7

```python
# ---- Evaluation runs (+ metrics) -> Delta -----------------------------------
runs = mlflow.search_runs(experiment_ids=[EXPERIMENT_ID], max_results=500)
print("runs fetched:", len(runs), "| columns:", list(runs.columns) if hasattr(runs, "columns") else "n/a")
_write(runs, "mlflow_eval_runs")
```

**Output:**

```text
runs fetched: 4 | columns: ['run_id', 'experiment_id', 'status', 'artifact_uri', 'start_time', 'end_time', 'metrics.correctness/mean', 'metrics.safety/mean', 'metrics.relevance_to_query/mean', 'tags.mlflow.databricks.jobType', 'tags.mlflow.databricks.cluster.info', 'tags.mlflow.user', 'tags.mlflow.source.name', 'tags.mlflow.databricks.jobID', 'tags.mlflow.runName', 'tags.mlflow.runColor', 'tags.mlflow.databricks.notebook.commandID', 'tags.mlflow.databricks.workspaceURL', 'tags.mlflow.databricks.notebookRevisionID', 'tags.mlflow.databricks.cluster.libraries', 'tags.mlflow.databricks.jobRunID', 'tags.mlflow.databricks.cluster.id', 'tags.mlflow.databricks.notebookID', 'tags.mlflow.databricks.notebookPath', 'tags.mlflow.runType', 'tags.mlflow.databricks.workspaceID', 'tags.mlflow.databricks.webappURL', 'tags.mlflow.source.type']
[mlflow_eval_runs] wrote 4 rows; columns: ['run_id', 'experiment_id', 'status', 'artifact_uri', 'start_time', 'end_time', 'metrics_correctness_mean', 'metrics_safety_mean', 'metrics_relevance_to_query_mean', 'tags_mlflow_databricks_jobType', 'tags_mlflow_databricks_cluster_info', 'tags_mlflow_user', 'tags_mlflow_source_name', 'tags_mlflow_databricks_jobID', 'tags_mlflow_runName', 'tags_mlflow_runColor', 'tags_mlflow_databricks_notebook_commandID', 'tags_mlflow_databricks_workspaceURL', 'tags_mlflow_databricks_notebookRevisionID', 'tags_mlflow_databricks_cluster_libraries', 'tags_mlflow_databricks_jobRunID', 'tags_mlflow_databricks_cluster_id', 'tags_mlflow_databricks_notebookID', 'tags_mlflow_databricks_notebookPath', 'tags_mlflow_runType', 'tags_mlflow_databricks_workspaceID', 'tags_mlflow_databricks_webappURL', 'tags_mlflow_source_type']
```

## Cell 8

```python
# ---- Show what a business user can now query (robust SELECT *) --------------
print("=== eval runs ===")
display(spark.sql(f"SELECT * FROM {CATALOG}.{SCHEMA}.mlflow_eval_runs ORDER BY start_time DESC"))
print("=== recent traces ===")
display(spark.sql(f"SELECT * FROM {CATALOG}.{SCHEMA}.mlflow_traces LIMIT 10"))
```

**Output:**

```text
=== eval runs ===
```

| run_id | experiment_id | status | artifact_uri | start_time | end_time | metrics_correctness_mean | metrics_safety_mean | metrics_relevance_to_query_mean | tags_mlflow_databricks_jobType | tags_mlflow_databricks_cluster_info | tags_mlflow_user | tags_mlflow_source_name | tags_mlflow_databricks_jobID | tags_mlflow_runName | tags_mlflow_runColor | tags_mlflow_databricks_notebook_commandID | tags_mlflow_databricks_workspaceURL | tags_mlflow_databricks_notebookRevisionID | tags_mlflow_databricks_cluster_libraries | tags_mlflow_databricks_jobRunID | tags_mlflow_databricks_cluster_id | tags_mlflow_databricks_notebookID | tags_mlflow_databricks_notebookPath | tags_mlflow_runType | tags_mlflow_databricks_workspaceID | tags_mlflow_databricks_webappURL | tags_mlflow_source_type |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| c21cf7a9dda14e7d8c2fb2a1ec7c4cfb | 1765197035583318 | FINISHED | dbfs:/databricks/mlflow-tracking/1765197035583318/c21cf7a9dda14e7d8c2fb2a1ec7c4cfb/artifacts | 2026-10-06T07:18:17.619Z | 2026-10-06T07:19:10.333Z | 1.0 | 1.0 | 1.0 | notebook | {"cluster_name":"","spark_version":"client.6.2-aarch64-scala2.13","autotermination_minutes":120} | soumya.r@databricks.com | jobs/104088374467144/run/889923944044603 | 104088374467144 | hilarious-fawn-469 | #7d54b2 | 1001791270145150_5971765716651783606_org-7474651022795245-job-104088374467144-run-889923944044603-action-690479961857562 | https://fevm-aws-serverless-ws-sr.cloud.databricks.com | 1791271150455 | {"installable":[],"redacted":[]} | 889923944044603 | 1006-071114-d594mbib-v2n | 1765197035583239 | /Users/soumya.r@databricks.com/.bundle/lumora_vendor_marketplace/dev/files/notebooks/08_mlflow_eval | genai_evaluate | 7474651022795245 | https://fevm-aws-serverless-ws-sr.cloud.databricks.com | JOB |
| 25ef2f9071d443febf7f8eda857cc442 | 1765197035583318 | FINISHED | dbfs:/databricks/mlflow-tracking/1765197035583318/25ef2f9071d443febf7f8eda857cc442/artifacts | 2026-10-06T06:55:37.979Z | 2026-10-06T06:56:30.637Z | 0.75 | 1.0 | 1.0 | notebook | {"cluster_name":"","spark_version":"client.6.2-aarch64-scala2.13","autotermination_minutes":120} | soumya.r@databricks.com | jobs/104088374467144/run/891995759686762 | 104088374467144 | casual-vole-13 | #479a5f | 1001791269360821_6178217974720788440_org-7474651022795245-job-104088374467144-run-891995759686762-action-690479961857562 | https://fevm-aws-serverless-ws-sr.cloud.databricks.com | 1791269790791 | {"installable":[],"redacted":[]} | 891995759686762 | 1006-065412-awzqsolm-v2n | 1765197035583239 | /Users/soumya.r@databricks.com/.bundle/lumora_vendor_marketplace/dev/files/notebooks/08_mlflow_eval | genai_evaluate | 7474651022795245 | https://fevm-aws-serverless-ws-sr.cloud.databricks.com | JOB |
| b8238c2ed8ac422983a4237f92aa4d2e | 1765197035583318 | FINISHED | dbfs:/databricks/mlflow-tracking/1765197035583318/b8238c2ed8ac422983a4237f92aa4d2e/artifacts | 2026-10-06T06:46:55.885Z | 2026-10-06T06:47:42.591Z | 0.5 | 1.0 | 1.0 | notebook | {"cluster_name":"","spark_version":"client.6.2-aarch64-scala2.13","autotermination_minutes":120} | soumya.r@databricks.com | jobs/104088374467144/run/350008842295247 | 104088374467144 | auspicious-wolf-141 | #da4c4c | 1001791268383618_9017273401344423238_org-7474651022795245-job-104088374467144-run-350008842295247-action-690479961857562 | https://fevm-aws-serverless-ws-sr.cloud.databricks.com | 1791269262717 | {"installable":[],"redacted":[]} | 350008842295247 | 1006-063949-2uydb2tr-v2n | 1765197035583239 | /Users/soumya.r@databricks.com/.bundle/lumora_vendor_marketplace/dev/files/notebooks/08_mlflow_eval | genai_evaluate | 7474651022795245 | https://fevm-aws-serverless-ws-sr.cloud.databricks.com | JOB |
| 475e54d85fd24fcb8639b7bce6425f3e | 1765197035583318 | FINISHED | dbfs:/databricks/mlflow-tracking/1765197035583318/475e54d85fd24fcb8639b7bce6425f3e/artifacts | 2026-10-06T06:46:24.167Z | 2026-10-06T06:47:13.940Z | 0.5 | 1.0 | 1.0 | notebook | {"cluster_name":"","spark_version":"client.6.2-aarch64-scala2.13","autotermination_minutes":120} | soumya.r@databricks.com | jobs/104088374467144/run/98434640387817 | 104088374467144 | omniscient-sloth-135 | #5387dd | 1001791268511382_8069670699635828546_org-7474651022795245-job-104088374467144-run-98434640387817-action-6904799618575625 | https://fevm-aws-serverless-ws-sr.cloud.databricks.com | 1791269234080 | {"installable":[],"redacted":[]} | 98434640387817 | 1006-063939-2ejshugr-v2n | 1765197035583239 | /Users/soumya.r@databricks.com/.bundle/lumora_vendor_marketplace/dev/files/notebooks/08_mlflow_eval | genai_evaluate | 7474651022795245 | https://fevm-aws-serverless-ws-sr.cloud.databricks.com | JOB |

```text
=== recent traces ===
```

| trace_id | trace | client_request_id | state | request_time | execution_duration | request | response | trace_metadata | tags | spans | assessments |
|---|---|---|---|---|---|---|---|---|---|---|---|
| tr-ebbc1855b67a5c84b89839dbc11c9d06 | {"info": {"trace_id": "tr-ebbc1855b67a5c84b89839dbc11c9d06", "client_request_id": "tr-ebbc1855b67a5c84b89839dbc11c9d06", | tr-ebbc1855b67a5c84b89839dbc11c9d06 | OK | 1791271117214 | 7939 | {"messages": [{"role": "user", "content": "How does AfriHealth Data derive its HCP counts, and how often is the data ref | {"messages": [{"role": "user", "content": "How does AfriHealth Data derive its HCP counts, and how often is the data ref | {"mlflow.trace_schema.version": "3", "mlflow.databricks.workspaceURL": "https://fevm-aws-serverless-ws-sr.cloud.databric | {"mlflow.artifactLocation": "dbfs:/databricks/mlflow-tracking/1765197035583318/tr-ebbc1855b67a5c84b89839dbc11c9d06/artif | [{"trace_id": "67wYVbZ6XIS4mDnbwRydBg==", "span_id": "RlAuoH5YYuw=", "parent_span_id": null, "name": "LangGraph", "start | [{"assessment_id": "a-d1f3debcb3bc4fc985b4f7634cfadc97", "assessment_name": "relevance_to_query", "trace_id": "tr-ebbc18 |
| tr-7124d5afbde9963f31c6a55cb2f4c9ce | {"info": {"trace_id": "tr-7124d5afbde9963f31c6a55cb2f4c9ce", "client_request_id": "tr-7124d5afbde9963f31c6a55cb2f4c9ce", | tr-7124d5afbde9963f31c6a55cb2f4c9ce | OK | 1791271117208 | 29202 | {"messages": [{"role": "user", "content": "Which vendor contracts are expiring soon and what do they cost annually?"}]} | {"messages": [{"role": "user", "content": "Which vendor contracts are expiring soon and what do they cost annually?"}, { | {"mlflow.trace_schema.version": "3", "mlflow.databricks.workspaceURL": "https://fevm-aws-serverless-ws-sr.cloud.databric | {"mlflow.artifactLocation": "dbfs:/databricks/mlflow-tracking/1765197035583318/tr-7124d5afbde9963f31c6a55cb2f4c9ce/artif | [{"trace_id": "cSTVr73plj8xxqVcsvTJzg==", "span_id": "F1mqIIdbiZI=", "parent_span_id": null, "name": "LangGraph", "start | [{"assessment_id": "a-f409bc47b27c48bd81a17ef51a7e91ed", "assessment_name": "expected_facts", "trace_id": "tr-7124d5afbd |
| tr-299f9dda9d834b7baeb32ef458450a45 | {"info": {"trace_id": "tr-299f9dda9d834b7baeb32ef458450a45", "client_request_id": "tr-299f9dda9d834b7baeb32ef458450a45", | tr-299f9dda9d834b7baeb32ef458450a45 | OK | 1791271117200 | 18316 | {"messages": [{"role": "user", "content": "Which vendors provide HCP data in Egypt?"}]} | {"messages": [{"role": "user", "content": "Which vendors provide HCP data in Egypt?"}, {"role": "assistant", "content":  | {"mlflow.trace_schema.version": "3", "mlflow.databricks.workspaceURL": "https://fevm-aws-serverless-ws-sr.cloud.databric | {"mlflow.artifactLocation": "dbfs:/databricks/mlflow-tracking/1765197035583318/tr-299f9dda9d834b7baeb32ef458450a45/artif | [{"trace_id": "KZ+d2p2DS3uusy70WEUKRQ==", "span_id": "/YyYuEn0bxQ=", "parent_span_id": null, "name": "LangGraph", "start | [{"assessment_id": "a-8570b811d2214c689efed7a1e069572e", "assessment_name": "relevance_to_query", "trace_id": "tr-299f9d |
| tr-fc96f267f2f44eef0946070f7c91a121 | {"info": {"trace_id": "tr-fc96f267f2f44eef0946070f7c91a121", "client_request_id": "tr-fc96f267f2f44eef0946070f7c91a121", | tr-fc96f267f2f44eef0946070f7c91a121 | OK | 1791271117186 | 19192 | {"messages": [{"role": "user", "content": "Which vendors offer clinical trial data?"}]} | {"messages": [{"role": "user", "content": "Which vendors offer clinical trial data?"}, {"role": "assistant", "content":  | {"mlflow.trace_schema.version": "3", "mlflow.databricks.workspaceURL": "https://fevm-aws-serverless-ws-sr.cloud.databric | {"mlflow.artifactLocation": "dbfs:/databricks/mlflow-tracking/1765197035583318/tr-fc96f267f2f44eef0946070f7c91a121/artif | [{"trace_id": "/JbyZ/L0Tu8JRgcPfJGhIQ==", "span_id": "kpyl9xbG9/Y=", "parent_span_id": null, "name": "LangGraph", "start | [{"assessment_id": "a-4d4dae339a994264b071732134d8ab6d", "assessment_name": "safety", "trace_id": "tr-fc96f267f2f44eef09 |
| tr-84b081a8e7a57bdfd2b8a314ce7ac42a | {"info": {"trace_id": "tr-84b081a8e7a57bdfd2b8a314ce7ac42a", "client_request_id": "tr-84b081a8e7a57bdfd2b8a314ce7ac42a", | tr-84b081a8e7a57bdfd2b8a314ce7ac42a | OK | 1791271080026 | 212 |  |  | {"mlflow.trace_schema.version": "3", "mlflow.databricks.workspaceURL": "https://fevm-aws-serverless-ws-sr.cloud.databric | {"mlflow.artifactLocation": "dbfs:/databricks/mlflow-tracking/1765197035583318/tr-84b081a8e7a57bdfd2b8a314ce7ac42a/artif | [{"trace_id": "hLCBqOele9/SuKMUznrEKg==", "span_id": "YEhGdBorO2w=", "parent_span_id": null, "name": "GenieAgent", "star | [] |
| tr-3214b348685315078194a26c75304919 | {"info": {"trace_id": "tr-3214b348685315078194a26c75304919", "client_request_id": "tr-3214b348685315078194a26c75304919", | tr-3214b348685315078194a26c75304919 | OK | 1791269756659 | 10096 | {"messages": [{"role": "user", "content": "How does AfriHealth Data derive its HCP counts, and how often is the data ref | {"messages": [{"role": "user", "content": "How does AfriHealth Data derive its HCP counts, and how often is the data ref | {"mlflow.trace_schema.version": "3", "mlflow.databricks.workspaceURL": "https://fevm-aws-serverless-ws-sr.cloud.databric | {"mlflow.artifactLocation": "dbfs:/databricks/mlflow-tracking/1765197035583318/tr-3214b348685315078194a26c75304919/artif | [{"trace_id": "MhSzSGhTFQeBlKJsdTBJGQ==", "span_id": "80XhqPQB3MI=", "parent_span_id": null, "name": "LangGraph", "start | [{"assessment_id": "a-ad8ea330db194311bd430197f128fc5a", "assessment_name": "relevance_to_query", "trace_id": "tr-3214b3 |
