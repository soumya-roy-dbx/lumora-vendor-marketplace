# end_to_end / generate_vendor_docs

- **Notebook:** `notebooks/03_generate_vendor_docs`
- **Task run id:** `272478380225772` · **Result:** `SUCCESS`
- **Started:** 2026-10-06 07:01:33 UTC · **Ended:** 2026-10-06 07:02:16 UTC
- **Job run:** https://fevm-aws-serverless-ws-sr.cloud.databricks.com/?o=7474651022795245#job/789028661266524/run/1002479881266291

_Exported from the job run with `databricks jobs export-run` — cell source followed by the output the cell produced in that run._

## Cell 1

```python
%run ./00_config
```

## Cell 3

```python
# =============================================================================
# 03_generate_vendor_docs
#
# Phase 3 (part 1): generate realistic UNSTRUCTURED vendor documents — the
# free-text content (data dictionaries, vendor materials, and contracts) that
# structured tables can't answer, for semantic retrieval.
#
# Per vendor we write markdown docs into a UC Volume:
#   - contract_summary   (terms, dates, SLAs, delivery, restrictions — cost redacted)
#   - data_dictionary    (field definitions per data type)
#   - methodology        (how counts are derived, refresh cadence, known gaps)
#   - onboarding_guide   (access + delivery instructions)
#
# Content is derived from the SAME structured Gold data so the two halves stay
# consistent — this is the corpus for the retrieval / knowledge arm of the
# multi-agent supervisor (Phase 4). Grounds questions like:
#   "Summarize MediReach's contract terms" · "How does AfriHealth derive HCP
#   counts?" · "What's the refresh cadence for claims data?"
# =============================================================================
```

## Cell 4

```python
# CATALOG / SCHEMA come from 00_config
DOCS_VOLUME = "vendor_documents"
DOCS_PATH = f"/Volumes/{CATALOG}/{SCHEMA}/{DOCS_VOLUME}"

spark.sql(f"CREATE VOLUME IF NOT EXISTS {CATALOG}.{SCHEMA}.{DOCS_VOLUME} "
          f"COMMENT 'Unstructured vendor documents (contracts, data dictionaries, methodology, onboarding) for semantic retrieval.'")
```

## Cell 5

```python
import os, random
random.seed(7)
os.makedirs(DOCS_PATH, exist_ok=True)

FQ = f"{CATALOG}.{SCHEMA}"
vendors = {r["vendor_id"]: r.asDict() for r in spark.table(f"{FQ}.vendors").collect()}
# Contract documents are SOURCE documents (supplied alongside each vendor's raw
# export), so dates/terms are rendered from the raw landing zone. The contract
# COST is deliberately NOT written into any document: documents are retrievable
# by every user through Vector Search / the Knowledge Assistant, which would
# bypass the column mask on contracts.annual_cost_usd. (Caught by the MLflow
# correctness eval: an earlier version leaked cost through the docs path.)
_raw = spark.read.option("multiLine", "true").json(RAW_PATH).select("vendor_id", "contract.*")
contracts = {r["vendor_id"]: r.asDict() for r in _raw.collect()}

# products & coverage grouped by vendor
from collections import defaultdict
prod_by_v = defaultdict(list)
for r in spark.table(f"{FQ}.data_products").collect():
    prod_by_v[r["vendor_id"]].append(r.asDict())
cov_by_v = defaultdict(list)
for r in spark.table(f"{FQ}.coverage").collect():
    cov_by_v[r["vendor_id"]].append(r.asDict())
elem_by_v = defaultdict(list)
for r in spark.table(f"{FQ}.data_elements").collect():
    elem_by_v[r["vendor_id"]].append(r.asDict())

REFRESH = ["daily", "weekly", "monthly", "quarterly"]
DELIVERY = ["secure SFTP drop", "Snowflake share", "S3 delivery", "REST API", "Delta Sharing"]
SLA = ["99.5%", "99.9%", "99.0%"]

def contract_doc(vid):
    v, c = vendors[vid], contracts[vid]
    prods = ", ".join(sorted({p["data_type"] for p in prod_by_v[vid]}))
    return f"""# Contract Summary — {v['vendor_name']}

**Vendor:** {v['vendor_name']}
**Contract ID:** {c['contract_id']}
**Term:** {c['contract_start']} to {c['contract_end']}
**Status:** {c['status']}
**Annual cost:** restricted — held in the governed `contracts` table and visible to Finance (lumora_finance) only
**Renewal owner:** {c['renewal_owner']}

## Scope of data
This master agreement covers the following data types delivered by {v['vendor_name']}: {prods}.
Delivery is via {random.choice(DELIVERY)} on a {random.choice(REFRESH)} refresh cadence, with a
data-availability SLA of {random.choice(SLA)}.

## Key terms
- **Permitted use:** internal analytics and reporting across Clinical, Commercial, and Corporate teams. Onward
  redistribution to third parties is prohibited without written consent.
- **Data residency:** processed within the Lumora governed Databricks environment; no vendor data may be exported
  to ungoverned storage.
- **Termination:** either party may terminate with 90 days' written notice; data must be destroyed within 30 days
  of termination.
- **Renewal:** auto-renews for successive 12-month terms unless cancelled 60 days before {c['contract_end']}.

## Notes
{"This contract is expiring soon — begin renewal review now." if c['status']=='Expiring Soon' else "This contract has lapsed; a renewal or replacement is required before further use." if c['status']=='Expired' else "Contract is active and in good standing."}
"""

def dictionary_doc(vid):
    v = vendors[vid]
    lines = [f"# Data Dictionary — {v['vendor_name']}", "",
             f"Field-level definitions for data products delivered by {v['vendor_name']}.", ""]
    by_type = defaultdict(list)
    for e in elem_by_v[vid]:
        by_type[e["data_type"]].append(e)
    for dt, elems in sorted(by_type.items()):
        lines.append(f"## {dt}")
        lines.append("")
        lines.append("| Field | Delivered | Definition |")
        lines.append("|---|---|---|")
        for e in elems:
            avail = "Yes" if e["available"] else "No (documented, not delivered)"
            lines.append(f"| {e['attribute']} | {avail} | The {e['attribute'].lower()} associated with each {dt} record. |")
        lines.append("")
    return "\n".join(lines)

def methodology_doc(vid):
    v = vendors[vid]
    regions = sorted({c["geographic_region"] for c in cov_by_v[vid]})
    dtypes = sorted({c["data_type"] for c in cov_by_v[vid]})
    return f"""# Methodology & Coverage Notes — {v['vendor_name']}

{v['vendor_description']}

## Sourcing methodology
{v['vendor_name']} compiles its records from a combination of licensed primary sources, public registries, and
partner feeds. Records are de-duplicated against a master identifier and validated on a {random.choice(REFRESH)}
basis. Counts reported in the catalog reflect distinct, validated records at the most recent refresh.

## Coverage
- **Data types:** {", ".join(dtypes)}
- **Geographies:** {", ".join(regions)}
- Coverage counts vary by geography; emerging markets are refreshed less frequently than core markets
  (US, EU, UK).

## Known limitations
- HCP counts in smaller geographies (e.g. {random.choice(regions) if regions else 'N/A'}) carry a wider
  confidence interval and should be treated as estimates.
- Historical depth is limited to the last {random.choice([3,5,7,10])} years for most data types.
- {"Analytical-platform delivery enables in-place querying." if v['is_analytical_platform'] else "Flat-file delivery only; no in-place query layer."}
"""

def onboarding_doc(vid):
    v = vendors[vid]
    return f"""# Onboarding & Access Guide — {v['vendor_name']}

## Requesting access
Submit an intake to the Data Governance team referencing vendor **{v['vendor_name']}** ({vid}). Access is granted
per data product and governed through Unity Catalog.

## Delivery
{"This vendor delivers via an analytical platform — request a workspace grant and query in place." if v['is_analytical_platform'] else "This vendor delivers flat files — data is ingested into the governed lakehouse on a scheduled pipeline."}

## Support
For data questions, contact the vendor's technical account team via the Data Governance liaison. For catalog or
coverage questions, use the Lumora Data Marketplace assistant.
"""

written = 0
for vid, v in vendors.items():
    stem = f"{vid}_{v['vendor_name'].replace(' ','_').replace(',','')}"
    for suffix, fn in [("contract_summary", contract_doc), ("data_dictionary", dictionary_doc),
                       ("methodology", methodology_doc), ("onboarding_guide", onboarding_doc)]:
        with open(f"{DOCS_PATH}/{stem}__{suffix}.md", "w") as f:
            f.write(fn(vid))
        written += 1

print(f"Wrote {written} documents for {len(vendors)} vendors into {DOCS_PATH}")
display(dbutils.fs.ls(DOCS_PATH))
```

**Output:**

```text
Wrote 72 documents for 18 vendors into /Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/vendor_documents
```

| path | name | size | modificationTime |
|---|---|---|---|
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/vendor_documents/V001_MediReach_Analytics__contract | V001_MediReach_Analytics__contract_summary.md | 1158 | 1791270123000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/vendor_documents/V001_MediReach_Analytics__data_dic | V001_MediReach_Analytics__data_dictionary.md | 1743 | 1791270123000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/vendor_documents/V001_MediReach_Analytics__methodol | V001_MediReach_Analytics__methodology.md | 946 | 1791270123000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/vendor_documents/V001_MediReach_Analytics__onboardi | V001_MediReach_Analytics__onboarding_guide.md | 539 | 1791270123000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/vendor_documents/V002_ClaimStream_Data_Co__contract | V002_ClaimStream_Data_Co__contract_summary.md | 1214 | 1791270121000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/vendor_documents/V002_ClaimStream_Data_Co__data_dic | V002_ClaimStream_Data_Co__data_dictionary.md | 1706 | 1791270121000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/vendor_documents/V002_ClaimStream_Data_Co__methodol | V002_ClaimStream_Data_Co__methodology.md | 934 | 1791270121000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/vendor_documents/V002_ClaimStream_Data_Co__onboardi | V002_ClaimStream_Data_Co__onboarding_guide.md | 539 | 1791270121000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/vendor_documents/V003_TrialSphere_Global__contract_ | V003_TrialSphere_Global__contract_summary.md | 1188 | 1791270122000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/vendor_documents/V003_TrialSphere_Global__data_dict | V003_TrialSphere_Global__data_dictionary.md | 1905 | 1791270122000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/vendor_documents/V003_TrialSphere_Global__methodolo | V003_TrialSphere_Global__methodology.md | 944 | 1791270123000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/vendor_documents/V003_TrialSphere_Global__onboardin | V003_TrialSphere_Global__onboarding_guide.md | 537 | 1791270123000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/vendor_documents/V004_PatientGraph__contract_summar | V004_PatientGraph__contract_summary.md | 1133 | 1791270119000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/vendor_documents/V004_PatientGraph__data_dictionary | V004_PatientGraph__data_dictionary.md | 1185 | 1791270119000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/vendor_documents/V004_PatientGraph__methodology.md | V004_PatientGraph__methodology.md | 903 | 1791270120000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/vendor_documents/V004_PatientGraph__onboarding_guid | V004_PatientGraph__onboarding_guide.md | 533 | 1791270120000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/vendor_documents/V005_PharmaGeo_Insights__contract_ | V005_PharmaGeo_Insights__contract_summary.md | 1198 | 1791270117000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/vendor_documents/V005_PharmaGeo_Insights__data_dict | V005_PharmaGeo_Insights__data_dictionary.md | 1330 | 1791270117000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/vendor_documents/V005_PharmaGeo_Insights__methodolo | V005_PharmaGeo_Insights__methodology.md | 929 | 1791270117000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/vendor_documents/V005_PharmaGeo_Insights__onboardin | V005_PharmaGeo_Insights__onboarding_guide.md | 537 | 1791270117000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/vendor_documents/V006_PubSignal_Ltd__contract_summa | V006_PubSignal_Ltd__contract_summary.md | 1166 | 1791270117000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/vendor_documents/V006_PubSignal_Ltd__data_dictionar | V006_PubSignal_Ltd__data_dictionary.md | 1261 | 1791270117000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/vendor_documents/V006_PubSignal_Ltd__methodology.md | V006_PubSignal_Ltd__methodology.md | 893 | 1791270117000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/vendor_documents/V006_PubSignal_Ltd__onboarding_gui | V006_PubSignal_Ltd__onboarding_guide.md | 535 | 1791270117000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/vendor_documents/V007_GlobalHCP_Registry__contract_ | V007_GlobalHCP_Registry__contract_summary.md | 1187 | 1791270117000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/vendor_documents/V007_GlobalHCP_Registry__data_dict | V007_GlobalHCP_Registry__data_dictionary.md | 1293 | 1791270117000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/vendor_documents/V007_GlobalHCP_Registry__methodolo | V007_GlobalHCP_Registry__methodology.md | 921 | 1791270118000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/vendor_documents/V007_GlobalHCP_Registry__onboardin | V007_GlobalHCP_Registry__onboarding_guide.md | 537 | 1791270118000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/vendor_documents/V008_RxPatterns__contract_summary. | V008_RxPatterns__contract_summary.md | 1172 | 1791270116000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/vendor_documents/V008_RxPatterns__data_dictionary.m | V008_RxPatterns__data_dictionary.md | 1138 | 1791270116000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/vendor_documents/V008_RxPatterns__methodology.md | V008_RxPatterns__methodology.md | 877 | 1791270116000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/vendor_documents/V008_RxPatterns__onboarding_guide. | V008_RxPatterns__onboarding_guide.md | 521 | 1791270116000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/vendor_documents/V009_VoxPatient_Social__contract_s | V009_VoxPatient_Social__contract_summary.md | 1194 | 1791270115000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/vendor_documents/V009_VoxPatient_Social__data_dicti | V009_VoxPatient_Social__data_dictionary.md | 1071 | 1791270116000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/vendor_documents/V009_VoxPatient_Social__methodolog | V009_VoxPatient_Social__methodology.md | 894 | 1791270116000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/vendor_documents/V009_VoxPatient_Social__onboarding | V009_VoxPatient_Social__onboarding_guide.md | 543 | 1791270116000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/vendor_documents/V010_CardioData_Partners__contract | V010_CardioData_Partners__contract_summary.md | 1205 | 1791270124000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/vendor_documents/V010_CardioData_Partners__data_dic | V010_CardioData_Partners__data_dictionary.md | 1901 | 1791270124000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/vendor_documents/V010_CardioData_Partners__methodol | V010_CardioData_Partners__methodology.md | 922 | 1791270124000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/vendor_documents/V010_CardioData_Partners__onboardi | V010_CardioData_Partners__onboarding_guide.md | 539 | 1791270124000 |

_… 32 more rows (truncated)_

## Cell 6

```python
# ---- Parse docs into a Delta table (text + metadata) ------------------------
# This table is the substrate for BOTH candidate retrieval paths:
#   (a) a Vector Search index built on top of it, and
#   (b) any Genie/parse-based document approach.
from pyspark.sql import functions as F

docs = (spark.read.text(DOCS_PATH, wholetext=True)
        .withColumn("path", F.col("_metadata.file_path"))
        .withColumn("file_name", F.element_at(F.split(F.col("path"), "/"), -1))
        .withColumn("vendor_id", F.regexp_extract(F.col("file_name"), r"^(V\d+)_", 1))
        .withColumn("doc_type", F.regexp_extract(F.col("file_name"), r"__(.+)\.md$", 1))
        .withColumnRenamed("value", "content")
        .withColumn("doc_id", F.expr("uuid()")))

docs = docs.join(spark.table(f"{FQ}.vendors").select("vendor_id", "vendor_name"), "vendor_id", "left")
docs.select("doc_id", "vendor_id", "vendor_name", "doc_type", "file_name", "content") \
    .write.mode("overwrite").option("overwriteSchema", "true") \
    .option("delta.enableChangeDataFeed", "true") \
    .saveAsTable(f"{FQ}.vendor_documents")

print("vendor_documents rows:", spark.table(f"{FQ}.vendor_documents").count())
display(spark.sql(f"SELECT vendor_name, doc_type, length(content) AS chars FROM {FQ}.vendor_documents ORDER BY vendor_name, doc_type LIMIT 12"))
```

**Output:**

```text
vendor_documents rows: 72
```

| vendor_name | doc_type | chars |
|---|---|---|
| APAC HealthLink | contract_summary | 1183 |
| APAC HealthLink | data_dictionary | 1322 |
| APAC HealthLink | methodology | 901 |
| APAC HealthLink | onboarding_guide | 527 |
| AfriHealth Data | contract_summary | 1184 |
| AfriHealth Data | data_dictionary | 1707 |
| AfriHealth Data | methodology | 927 |
| AfriHealth Data | onboarding_guide | 527 |
| CardioData Partners | contract_summary | 1201 |
| CardioData Partners | data_dictionary | 1899 |
| CardioData Partners | methodology | 920 |
| CardioData Partners | onboarding_guide | 535 |
