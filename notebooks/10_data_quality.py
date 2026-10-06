# Databricks notebook source
# MAGIC %pip install --quiet "databricks-sdk[openai]>=0.57.0"
# MAGIC dbutils.library.restartPython()

# COMMAND ----------
# MAGIC %run ./00_config

# COMMAND ----------
# =============================================================================
# 10_data_quality
#
# Phase 7 — self-service data-quality rules:
# data product owners add rules in natural language -> show sample data
# ("is this what you expected?") -> confirm -> deploy.
#
# The loop, end to end on the governed vendor tables:
#   1. NL rule  ->  the LLM generates a Spark-SQL boolean PASS expression
#   2. Preview  ->  count pass/fail + sample FAILING rows ("is this expected?")
#   3. Persist  ->  confirmed rules to `dq_rules`; results to `dq_results`
#   4. Deploy   ->  emit the equivalent Lakeflow/DLT EXPECT constraint per rule
# =============================================================================

# COMMAND ----------

from databricks.sdk import WorkspaceClient
from datetime import datetime, timezone
import re

# CATALOG / SCHEMA / FQ come from 00_config
SERVING_ENDPOINT = LLM_ENDPOINT

openai_client = WorkspaceClient().serving_endpoints.get_open_ai_client()

# COMMAND ----------

# Natural-language rules a data-product owner might type (no SQL knowledge needed).
NL_RULES = [
    {"name": "vendor_has_description", "table": "vendors",
     "rule": "Every vendor must have a non-empty description."},
    {"name": "coverage_positive_count", "table": "coverage",
     "rule": "Every coverage record must have a positive count."},
    {"name": "coverage_min_5000", "table": "coverage",
     "rule": "Every coverage record should cover at least 5,000 records (counts >= 5000)."},
    {"name": "contract_dates_valid", "table": "contracts",
     "rule": "A contract's end date must be after its start date."},
    {"name": "available_element_has_name", "table": "data_elements",
     "rule": "Any data element marked as available must have a non-empty attribute name."},
]


def nl_to_sql_expr(table: str, nl_rule: str) -> str:
    cols = [f.name for f in spark.table(f"{FQ}.{table}").schema.fields]
    prompt = (
        f"Table {FQ}.{table} has columns: {cols}.\n"
        f"Write ONE Spark SQL boolean expression that is TRUE for rows that PASS this "
        f"data-quality rule, using only those columns. Output ONLY the expression — no "
        f"explanation, no markdown, no backticks.\nRule: {nl_rule}"
    )
    resp = openai_client.chat.completions.create(
        model=SERVING_ENDPOINT,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
    )
    expr = resp.choices[0].message.content.strip()
    expr = re.sub(r"^```[a-z]*|```$", "", expr).strip()  # strip any fences
    return expr

# COMMAND ----------

# ---- Steps 1 + 2: translate each rule, then PREVIEW pass/fail + failing rows ----
rows, run_at = [], datetime.now(timezone.utc)
for r in NL_RULES:
    table, nl = r["table"], r["rule"]
    try:
        expr = nl_to_sql_expr(table, nl)
        agg = spark.sql(f"""
            SELECT count(*) total,
                   sum(CASE WHEN ({expr}) THEN 1 ELSE 0 END) passing
            FROM {FQ}.{table}
        """).first()
        total, passing = agg["total"], int(agg["passing"] or 0)
        failing = total - passing
        print(f"\n### {r['name']}  ({table})")
        print(f"    NL: {nl}")
        print(f"    -> SQL PASS expr: {expr}")
        print(f"    preview: {passing}/{total} pass, {failing} FAIL")
        if failing:
            print("    sample failing rows ('is this what you expected?'):")
            for fr in spark.sql(f"SELECT * FROM {FQ}.{table} WHERE NOT ({expr}) LIMIT 3").collect():
                print("      ", {k: fr[k] for k in fr.asDict()})
        rows.append({
            "rule_name": r["name"], "target_table": table, "nl_rule": nl,
            "sql_pass_expr": expr, "total_rows": total, "passing_rows": passing,
            "failing_rows": failing, "pct_pass": round(100.0 * passing / total, 1) if total else None,
            "dlt_expectation": f'@dlt.expect_or_drop("{r["name"]}", "{expr}")',
            "run_at": run_at,
        })
    except Exception as exc:  # noqa: BLE001 - keep going; a bad expr shouldn't fail the batch
        print(f"    [skipped {r['name']}: {exc}]")

# COMMAND ----------

# ---- Step 3: persist confirmed rules + results to governed Delta -------------
from pyspark.sql import Row
df = spark.createDataFrame([Row(**x) for x in rows])

df.select("rule_name", "target_table", "nl_rule", "sql_pass_expr", "dlt_expectation") \
  .write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{FQ}.dq_rules")

df.select("rule_name", "target_table", "total_rows", "passing_rows", "failing_rows", "pct_pass", "run_at") \
  .write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{FQ}.dq_results")

print("\nWrote dq_rules + dq_results.")
display(spark.table(f"{FQ}.dq_results"))

# COMMAND ----------

# ---- Step 4: the "deploy" artifact — Lakeflow/DLT expectations per rule -------
print("Generated Lakeflow (DLT) expectations to deploy these as pipeline constraints:\n")
for x in rows:
    print(x["dlt_expectation"])
