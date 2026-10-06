# agent_and_eval / mlflow_eval

- **Notebook:** `notebooks/08_mlflow_eval`
- **Task run id:** `889923944044603` · **Result:** `SUCCESS`
- **Started:** 2026-10-06 07:16:26 UTC · **Ended:** 2026-10-06 07:19:14 UTC
- **Job run:** https://fevm-aws-serverless-ws-sr.cloud.databricks.com/?o=7474651022795245#job/104088374467144/run/295096389310523

_Exported from the job run with `databricks jobs export-run` — cell source followed by the output the cell produced in that run._

## Cell 1

```python
# =============================================================================
# 08_mlflow_eval
#
# Phase 5 — MLflow observability: a prompt testbed, evaluation, and tracing.
#   1. Prompt Registry — register the supervisor's prompts as versioned assets.
#   2. Evaluation      — score the agent on an eval set of representative
#                        question types, with LLM judges (correctness, relevance,
#                        safety) — the "test before you ship" gate.
#   3. Tracing         — the agent already emits MLflow traces (autolog); confirm
#                        they're captured (incl. the genie/docs routing spans).
# =============================================================================
```

## Cell 2

```python
%pip install --quiet -U databricks-langchain "langchain>=0.3" "langchain-core>=0.3" "langgraph>=0.6.0" "langgraph-prebuilt>=0.6.0" databricks-vectorsearch databricks-agents "mlflow[databricks]>=3.1"
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
import os, importlib.util
import mlflow

os.environ["LLM_ENDPOINT"] = LLM_ENDPOINT
os.environ["GENIE_SPACE_ID"] = GENIE_SPACE_ID
os.environ["VS_INDEX"] = VS_INDEX

# CATALOG / SCHEMA come from 00_config
mlflow.set_registry_uri("databricks-uc")
mlflow.set_experiment(EXPERIMENT_PATH)   # from 00_config

NB_DIR = os.path.dirname(dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get())
AGENT_PATH = "/Workspace" + NB_DIR.rsplit("/", 1)[0] + "/agent/agent.py"
spec = importlib.util.spec_from_file_location("agent", AGENT_PATH)
agent_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent_mod)
```

**Output:**

```text
[1;38;5;208mIf you are using MLflow Tracing, you can migrate your traces to Unity Catalog for unlimited storage, fine-grained access controls, and queryability from notebooks, SQL, and dashboards. [94mLearn more: https://docs.databricks.com/aws/en/mlflow3/genai/tracing/migrate-traces-to-uc[0m
```

## Cell 6

```python
# ---- 1. Prompt Registry: version the agent's prompts ------------------------
# So prompts become governed, comparable assets you tune + test before shipping,
# instead of a hard-coded string buried in code.
registered = {}
for pname, template in [
    ("lumora_supervisor_router", agent_mod.SUPERVISOR_SYSTEM),
    ("lumora_docs_grounding", agent_mod.DOCS_SYSTEM),
    ("lumora_answer_combine", agent_mod.COMBINE_SYSTEM),
]:
    p = mlflow.genai.register_prompt(
        name=f"{CATALOG}.{SCHEMA}.{pname}",
        template=template,
        commit_message="Initial version from agent.py",
    )
    registered[pname] = p.version
    print(f"registered prompt {pname} -> v{p.version}")
```

**Output:**

```text
registered prompt lumora_supervisor_router -> v4
registered prompt lumora_docs_grounding -> v4
registered prompt lumora_answer_combine -> v4
```

## Cell 7

```python
# ---- 2. Evaluation dataset of representative question classes ----------------
# Ground truth for the structured questions is DERIVED FROM THE GOVERNED TABLES at
# run time (as the user running the eval), so expectations never drift from the
# data — contract status is date-relative and cost is masked outside finance.
def _names(q):
    return sorted({r[0] for r in spark.sql(q).collect()})

egypt_hcp = _names(f"SELECT DISTINCT v.vendor_name FROM {FQ}.coverage c JOIN {FQ}.vendors v USING (vendor_id) "
                   f"WHERE c.data_type = 'HCP' AND c.geographic_region = 'Egypt'")
trial_vendors = _names(f"SELECT DISTINCT v.vendor_name FROM {FQ}.coverage c JOIN {FQ}.vendors v USING (vendor_id) "
                       f"WHERE c.data_type = 'Clinical Trial'")
expiring = spark.sql(f"SELECT v.vendor_name, ct.annual_cost_usd FROM {FQ}.contracts ct JOIN {FQ}.vendors v USING (vendor_id) "
                     f"WHERE ct.status = 'Expiring Soon' ORDER BY ct.contract_end").collect()
cost_facts = ([f"${r.annual_cost_usd:,}" for r in expiring] if all(r.annual_cost_usd is not None for r in expiring)
              else ["the annual cost is masked / not visible for the user's role"])
import re
_afri_doc = spark.sql(f"SELECT content FROM {FQ}.vendor_documents WHERE vendor_name = 'AfriHealth Data' "
                      f"AND content LIKE '%Sourcing methodology%'").first().content
afri_cadence = re.search(r"validated on a (\w+)", _afri_doc).group(1)
print("ground truth | egypt HCP:", egypt_hcp, "| clinical trial:", trial_vendors,
      "| expiring:", [r.vendor_name for r in expiring], "| cost facts:", cost_facts, "| AfriHealth cadence:", afri_cadence)

eval_data = [
    {
        "inputs": {"question": "Which vendors provide HCP data in Egypt?"},
        "expectations": {"expected_facts": egypt_hcp},
    },
    {
        "inputs": {"question": "Which vendors offer clinical trial data?"},
        "expectations": {"expected_facts": trial_vendors},
    },
    {
        "inputs": {"question": "Which vendor contracts are expiring soon and what do they cost annually?"},
        "expectations": {"expected_facts": [r.vendor_name for r in expiring] + cost_facts},
    },
    {
        "inputs": {"question": "How does AfriHealth Data derive its HCP counts, and how often is the data refreshed?"},
        "expectations": {"expected_facts": ["licensed primary sources / public registries / partner feeds",
                                            f"validated on a {afri_cadence} basis",
                                            "emerging markets refreshed less frequently"]},
    },
]


def predict_fn(question: str) -> str:
    resp = agent_mod.AGENT.predict(messages=[{"role": "user", "content": question}])
    return resp.messages[-1].content if resp.messages else ""
```

**Output:**

```text
ground truth | egypt HCP: ['AfriHealth Data', 'MediReach Analytics', 'OncoReach'] | clinical trial: ['CardioData Partners', 'GlobalTrials Registry', 'ImmunoData', 'OncoReach', 'TrialSphere Global'] | expiring: ['GlobalTrials Registry', 'TrialSphere Global', 'PubSignal Ltd', 'NeuroGraph'] | cost facts: ["the annual cost is masked / not visible for the user's role"] | AfriHealth cadence: weekly
```

## Cell 8

```python
# ---- 3. Run evaluation with LLM judges --------------------------------------
from mlflow.genai.scorers import Correctness, RelevanceToQuery, Safety

results = mlflow.genai.evaluate(
    data=eval_data,
    predict_fn=predict_fn,
    scorers=[Correctness(), RelevanceToQuery(), Safety()],
)
print("Evaluation complete. Metrics:")
print(results.metrics)
```

**Output:**

```text
2026/10/06 07:18:18 INFO mlflow.models.evaluation.utils.trace: Auto tracing is temporarily enabled during the model evaluation for computing some metrics and debugging. To disable tracing, call `mlflow.autolog(disable=True)`.
2026/10/06 07:18:18 INFO mlflow.genai.utils.data_validation: Testing model prediction with the first sample in the dataset. To disable this check, set the MLFLOW_GENAI_EVAL_SKIP_TRACE_VALIDATION environment variable to True.
```

```text
[NOTICE] Using a notebook authentication token. Recommended for development only. For improved performance, please use Service Principal based authentication. To disable this message, pass disable_notice=True.
[NOTICE] Using a notebook authentication token. Recommended for development only. For improved performance, please use Service Principal based authentication. To disable this message, pass disable_notice=True.
```

```text
Evaluation complete. Metrics:
{'relevance_to_query/mean': np.float64(1.0), 'correctness/mean': np.float64(1.0), 'safety/mean': np.float64(1.0)}
```

## Cell 9

```python
# ---- Confirm tracing captured the runs (incl. routing) ----------------------
import mlflow
traces = mlflow.search_traces(max_results=20)
print(f"Traces captured: {len(traces)}")
try:
    # column names vary by mlflow version — print whatever is present, robustly
    print("trace columns:", list(traces.columns))
    print(traces.head(5).to_string())
except Exception as e:
    print("trace summary unavailable:", e)
```

**Output:**

```text
Traces captured: 20
trace columns: ['trace_id', 'trace', 'client_request_id', 'state', 'request_time', 'execution_duration', 'request', 'response', 'trace_metadata', 'tags', 'spans', 'assessments']
                              trace_id                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
```
