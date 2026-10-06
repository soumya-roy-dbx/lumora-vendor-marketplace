# Databricks notebook source
# =============================================================================
# 07_validate_agent
#
# Validate the multi-agent supervisor's ACTUAL routed answers without waiting
# on the (slow-provisioning) serving endpoint: import agent.py directly, run a
# structured question (should route to Genie) and an unstructured one (should
# route to the doc retriever), and write the answers + routing trace to a Delta
# table so they can be read back via SQL.
# =============================================================================

# COMMAND ----------

# MAGIC %pip install --quiet -U databricks-langchain "langchain>=0.3" "langchain-core>=0.3" "langgraph>=0.6.0" "langgraph-prebuilt>=0.6.0" databricks-vectorsearch "mlflow[databricks]>=3.1"
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %run ./00_config

# COMMAND ----------

import os, importlib.util
os.environ["LLM_ENDPOINT"] = LLM_ENDPOINT
os.environ["GENIE_SPACE_ID"] = GENIE_SPACE_ID
os.environ["VS_INDEX"] = VS_INDEX

NB_DIR = os.path.dirname(dbutils.notebook.entry_point.getDbutils().notebook().getContext().notebookPath().get())
AGENT_PATH = "/Workspace" + NB_DIR.rsplit("/", 1)[0] + "/agent/agent.py"
spec = importlib.util.spec_from_file_location("agent", AGENT_PATH)
agent_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent_mod)

# COMMAND ----------

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

# COMMAND ----------

from pyspark.sql import Row
df = spark.createDataFrame([Row(**r) for r in rows])
df.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(
    f"{FQ}.agent_validation"
)
print("wrote", df.count(), "validation rows.")
