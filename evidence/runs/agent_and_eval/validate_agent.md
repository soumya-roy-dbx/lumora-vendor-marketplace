# agent_and_eval / validate_agent

- **Notebook:** `notebooks/07_validate_agent`
- **Task run id:** `260770629799633` · **Result:** `SUCCESS`
- **Started:** 2026-10-06 07:14:12 UTC · **Ended:** 2026-10-06 07:16:26 UTC
- **Job run:** https://fevm-aws-serverless-ws-sr.cloud.databricks.com/?o=7474651022795245#job/104088374467144/run/295096389310523

_Exported from the job run with `databricks jobs export-run` — cell source followed by the output the cell produced in that run._

## Cell 1

```python
# =============================================================================
# 07_validate_agent
#
# Validate the multi-agent supervisor's ACTUAL routed answers without waiting
# on the (slow-provisioning) serving endpoint: import agent.py directly, run a
# structured question (should route to Genie) and an unstructured one (should
# route to the doc retriever), and write the answers + routing trace to a Delta
# table so they can be read back via SQL.
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
import os, importlib.util
os.environ["LLM_ENDPOINT"] = LLM_ENDPOINT
os.environ["GENIE_SPACE_ID"] = GENIE_SPACE_ID
os.environ["VS_INDEX"] = VS_INDEX

NB_DIR = os.path.dirname(dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get())
AGENT_PATH = "/Workspace" + NB_DIR.rsplit("/", 1)[0] + "/agent/agent.py"
spec = importlib.util.spec_from_file_location("agent", AGENT_PATH)
agent_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent_mod)
```

## Cell 6

```python
QUESTIONS = [
    "Which vendors provide HCP data in Egypt?",
    "How does AfriHealth Data derive its HCP counts, and how often is the data refreshed?",
    "Which vendor contracts are expiring soon and what do they cost annually?",
]

rows = []
for q in QUESTIONS:
    resp = agent_mod.AGENT.predict(messages=[{"role": "user", "content": q}])
    msgs = resp.messages
    # worker messages carry a name (genie/docs); the final synthesis is 'assistant'
    routed = [m.name for m in msgs if getattr(m, "name", None) in ("genie", "docs")]
    final = msgs[-1].content if msgs else ""
    rows.append({"question": q, "routed_to": ",".join(routed) or "(none)", "final_answer": final})
    print("Q:", q)
    print("  routed_to:", routed)
    print("  answer:", final[:300].replace("\n", " "), "...\n")
```

**Output:**

```text
Q: Which vendors provide HCP data in Egypt?
  routed_to: ['genie']
  answer: |    | Vendor              |   hcp_coverage | |---:|:--------------------|---------------:| |  0 | MediReach Analytics |          45429 | |  1 | OncoReach           |          37004 | |  2 | AfriHealth Data     |          20903 | ...

[NOTICE] Using a notebook authentication token. Recommended for development only. For improved performance, please use Service Principal based authentication. To disable this message, pass disable_notice=True.
Q: How does AfriHealth Data derive its HCP counts, and how often is the data refreshed?
  routed_to: ['docs']
  answer: Based on the retrieved documents:  **Vendor:** AfriHealth Data  **Sourcing Methodology (from Methodology & Coverage Notes):** AfriHealth Data compiles its HCP records from a combination of: - Licensed primary sources - Public registries - Partner feeds  Records are de-duplicated against a master ide ...

Q: Which vendor contracts are expiring soon and what do they cost annually?
  routed_to: ['genie']
  answer: |    | vendor_name           | contract_end   | annual_cost_usd   | |---:|:----------------------|:---------------|:------------------| |  0 | GlobalTrials Registry | 2026-11-06     |                   | |  1 | TrialSphere Global    | 2026-11-18     |                   | |  2 | PubSignal Ltd         ...
```

## Cell 7

```python
from pyspark.sql import Row
df = spark.createDataFrame([Row(**r) for r in rows])
df.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(
    f"{FQ}.agent_validation"
)
print("wrote", df.count(), "validation rows.")
```

**Output:**

```text
wrote 3 validation rows.
```
