# end_to_end / enrich_for_genie

- **Notebook:** `notebooks/02_enrich_for_genie`
- **Task run id:** `969160322657040` · **Result:** `SUCCESS`
- **Started:** 2026-10-06 07:00:54 UTC · **Ended:** 2026-10-06 07:01:33 UTC
- **Job run:** https://fevm-aws-serverless-ws-sr.cloud.databricks.com/?o=7474651022795245#job/789028661266524/run/1002479881266291

_Exported from the job run with `databricks jobs export-run` — cell source followed by the output the cell produced in that run._

## Cell 1

```python
%run ./00_config
```

## Cell 3

```python
# =============================================================================
# 02_enrich_for_genie
#
# Genie "ontology" layer. Table + column COMMENTs on the Gold model are declared
# in the Lakeflow pipeline (pipelines/ingest_vendor_catalog.py), next to the
# data. This notebook adds the business-friendly denormalized view Genie leans
# on for the most common question class (vendor x data type x region), and
# prints the comments Genie will ground on.
# =============================================================================
```

## Cell 4

```python
spark.sql(f"""
CREATE OR REPLACE VIEW {FQ}.vendor_coverage_enriched
COMMENT 'Denormalized vendor coverage: vendor name + data type + region + count + contract status. Best single source for "which vendors offer <data type> in <region>" questions.'
AS
SELECT v.vendor_id, v.vendor_name, v.vendor_description, v.headquarters,
       v.is_analytical_platform,
       c.data_type, c.geographic_region, c.coverage_type, c.counts, c.indication_ta,
       ct.status AS contract_status, ct.contract_end, ct.annual_cost_usd
FROM {FQ}.coverage c
JOIN {FQ}.vendors v USING (vendor_id)
LEFT JOIN {FQ}.contracts ct USING (vendor_id)
""")
print("Created view vendor_coverage_enriched.")
```

**Output:**

```text
Created view vendor_coverage_enriched.
```

## Cell 5

```python
# Grounding metadata Genie sees (declared in the pipeline)
display(spark.sql(f"""
SELECT table_name, comment FROM {CATALOG}.information_schema.tables
WHERE table_schema = '{SCHEMA}' AND table_name IN
  ('vendors','contracts','data_products','coverage','data_elements','vendor_coverage_enriched')
ORDER BY table_name"""))
display(spark.sql(f"""
SELECT table_name, column_name, comment FROM {CATALOG}.information_schema.columns
WHERE table_schema = '{SCHEMA}' AND table_name IN ('coverage','contracts') ORDER BY table_name, ordinal_position"""))
```

**Output:**

| table_name | comment |
|---|---|
| contracts | Contract terms per vendor: start/end dates, status, and annual cost. Use to answer renewal, expiry, and spend questions. |
| coverage | Geographic and volume coverage per vendor data product. THE table to answer which vendors cover a given data type in a g |
| data_elements | Field-level data elements available per vendor product (e.g. HCP has NPI/ID, Specialty, Email). available=false means th |
| data_products | Data products offered by each vendor. A vendor offers one product per data type (HCP, HCO, Claims, etc.). |
| vendor_coverage_enriched | Denormalized vendor coverage: vendor name + data type + region + count + contract status. Best single source for "which  |
| vendors | One row per third-party data vendor in the Lumora data marketplace. The authoritative list of vendors and their firmogra |

| table_name | column_name | comment |
|---|---|---|
| contracts | vendor_id | Vendor identifier (join key to vendors). |
| contracts | contract_id | Contract identifier. |
| contracts | contract_start | Contract start date (ISO yyyy-mm-dd). |
| contracts | contract_end | Contract end date (ISO yyyy-mm-dd). Filter for upcoming renewals. |
| contracts | status | Contract status: Active, Expiring Soon (ends within ~120 days), or Expired. |
| contracts | annual_cost_usd | Annual contract cost in USD. Masked to NULL for users outside the finance group. |
| contracts | renewal_owner | Team accountable for the renewal decision. |
| coverage | vendor_id | Vendor identifier (join key to vendors). |
| coverage | coverage_id | Coverage row identifier. |
| coverage | product_id | Product identifier (join key to data_products). |
| coverage | data_type | Data type covered (HCP, HCO, Claims, Patient, Clinical Trial, Publication, Social Media, Rx/Medication). |
| coverage | geographic_region | Country or region this coverage applies to (e.g. US, EU, Egypt, Argentina, Nigeria, Japan). Use this to filter vendors b |
| coverage | coverage_type | What the count measures, e.g. HCP count, HCO count, Claims volume. |
| coverage | counts | Number of records the vendor covers for this data type in this region (e.g. HCP count). |
| coverage | indication_ta | Therapeutic area of the covered records. |

## Cell 6

```python
print("Flagship question as deterministic SQL — Which vendors cover HCP data in Egypt?")
display(spark.sql(f"""
SELECT DISTINCT vendor_name, coverage_type, counts
FROM {FQ}.vendor_coverage_enriched
WHERE data_type = 'HCP' AND geographic_region = 'Egypt'
ORDER BY counts DESC"""))
```

**Output:**

```text
Flagship question as deterministic SQL — Which vendors cover HCP data in Egypt?
```

| vendor_name | coverage_type | counts |
|---|---|---|
| MediReach Analytics | HCP count | 45429 |
| OncoReach | HCP count | 37004 |
| AfriHealth Data | HCP count | 20903 |
