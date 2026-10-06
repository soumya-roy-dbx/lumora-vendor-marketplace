# end_to_end / data_quality_rules

- **Notebook:** `notebooks/10_data_quality`
- **Task run id:** `73650703758901` · **Result:** `SUCCESS`
- **Started:** 2026-10-06 07:01:33 UTC · **Ended:** 2026-10-06 07:02:41 UTC
- **Job run:** https://fevm-aws-serverless-ws-sr.cloud.databricks.com/?o=7474651022795245#job/789028661266524/run/1002479881266291

_Exported from the job run with `databricks jobs export-run` — cell source followed by the output the cell produced in that run._

## Cell 1

```python
%pip install --quiet "databricks-sdk[openai]>=0.57.0"
dbutils.library.restartPython()
```

**Output:**

```text
[43mNote: you may need to restart the kernel using %restart_python or dbutils.library.restartPython() to use updated packages.[0m
```

## Cell 2

```python
%run ./00_config
```

## Cell 4

```python
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
```

## Cell 5

```python
from databricks.sdk import WorkspaceClient
from datetime import datetime, timezone
import re

# CATALOG / SCHEMA / FQ come from 00_config
SERVING_ENDPOINT = LLM_ENDPOINT

openai_client = WorkspaceClient().serving_endpoints.get_open_ai_client()
```

**Output:**

```text
/home/spark-f96b3112-2760-4f3c-9387-73/.ipykernel/68/command-5623723460998348-1596481806:8: DeprecationWarning: get_open_ai_client() is deprecated. Please install the databricks-openai package and use 'from databricks_openai import DatabricksOpenAI' instead. See https://api-docs.databricks.com/python/databricks-ai-bridge/latest/databricks_openai.html for more information.
  openai_client = WorkspaceClient().serving_endpoints.get_open_ai_client()
```

## Cell 6

```python
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
```

## Cell 7

```python
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
```

**Output:**

```text

### vendor_has_description  (vendors)
    NL: Every vendor must have a non-empty description.
    -> SQL PASS expr: vendor_description IS NOT NULL AND TRIM(vendor_description) != ''
    preview: 18/18 pass, 0 FAIL

### coverage_positive_count  (coverage)
    NL: Every coverage record must have a positive count.
    -> SQL PASS expr: counts > 0
    preview: 126/126 pass, 0 FAIL

### coverage_min_5000  (coverage)
    NL: Every coverage record should cover at least 5,000 records (counts >= 5000).
    -> SQL PASS expr: counts >= 5000
    preview: 98/126 pass, 28 FAIL
    sample failing rows ('is this what you expected?'):
       {'vendor_id': 'V007', 'coverage_id': 'V007-P02-EGY', 'product_id': 'V007-P02', 'data_type': 'HCO', 'geographic_region': 'Egypt', 'coverage_type': 'HCO count', 'counts': 4995, 'indication_ta': 'Infectious Disease'}
       {'vendor_id': 'V015', 'coverage_id': 'V015-P02-UK', 'product_id': 'V015-P02', 'data_type': 'Clinical Trial', 'geographic_region': 'UK', 'coverage_type': 'Clinical Trial count', 'counts': 1158, 'indication_ta': 'Respiratory'}
       {'vendor_id': 'V015', 'coverage_id': 'V015-P02-US', 'product_id': 'V015-P02', 'data_type': 'Clinical Trial', 'geographic_region': 'US', 'coverage_type': 'Clinical Trial count', 'counts': 387, 'indication_ta': 'Oncology'}

### contract_dates_valid  (contracts)
    NL: A contract's end date must be after its start date.
    -> SQL PASS expr: contract_end > contract_start
    preview: 18/18 pass, 0 FAIL

### available_element_has_name  (data_elements)
    NL: Any data element marked as available must have a non-empty attribute name.
    -> SQL PASS expr: (available = false OR available IS NULL OR (available = true AND attribute IS NOT NULL AND TRIM(attribute) != ''))
    preview: 292/292 pass, 0 FAIL
```

## Cell 8

```python
# ---- Step 3: persist confirmed rules + results to governed Delta -------------
from pyspark.sql import Row
df = spark.createDataFrame([Row(**x) for x in rows])

df.select("rule_name", "target_table", "nl_rule", "sql_pass_expr", "dlt_expectation") \
  .write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{FQ}.dq_rules")

df.select("rule_name", "target_table", "total_rows", "passing_rows", "failing_rows", "pct_pass", "run_at") \
  .write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{FQ}.dq_results")

print("\nWrote dq_rules + dq_results.")
display(spark.table(f"{FQ}.dq_results"))
```

**Output:**

```text

Wrote dq_rules + dq_results.
```

| rule_name | target_table | total_rows | passing_rows | failing_rows | pct_pass | run_at |
|---|---|---|---|---|---|---|
| vendor_has_description | vendors | 18 | 18 | 0 | 100.0 | 2026-10-06T07:02:18.107Z |
| coverage_positive_count | coverage | 126 | 126 | 0 | 100.0 | 2026-10-06T07:02:18.107Z |
| coverage_min_5000 | coverage | 126 | 98 | 28 | 77.8 | 2026-10-06T07:02:18.107Z |
| contract_dates_valid | contracts | 18 | 18 | 0 | 100.0 | 2026-10-06T07:02:18.107Z |
| available_element_has_name | data_elements | 292 | 292 | 0 | 100.0 | 2026-10-06T07:02:18.107Z |

## Cell 9

```python
# ---- Step 4: the "deploy" artifact — Lakeflow/DLT expectations per rule -------
print("Generated Lakeflow (DLT) expectations to deploy these as pipeline constraints:\n")
for x in rows:
    print(x["dlt_expectation"])
```

**Output:**

```text
Generated Lakeflow (DLT) expectations to deploy these as pipeline constraints:

@dlt.expect_or_drop("vendor_has_description", "vendor_description IS NOT NULL AND TRIM(vendor_description) != ''")
@dlt.expect_or_drop("coverage_positive_count", "counts > 0")
@dlt.expect_or_drop("coverage_min_5000", "counts >= 5000")
@dlt.expect_or_drop("contract_dates_valid", "contract_end > contract_start")
@dlt.expect_or_drop("available_element_has_name", "(available = false OR available IS NULL OR (available = true AND attribute IS NOT NULL AND TRIM(attribute) != ''))")
```
