# Databricks notebook source
# MAGIC %run ./00_config

# COMMAND ----------
# =============================================================================
# 02_enrich_for_genie
#
# Genie "ontology" layer. Table + column COMMENTs on the Gold model are declared
# in the Lakeflow pipeline (pipelines/ingest_vendor_catalog.py), next to the
# data. This notebook adds the business-friendly denormalized view Genie leans
# on for the most common question class (vendor x data type x region), and
# prints the comments Genie will ground on.
# =============================================================================

# COMMAND ----------

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

# COMMAND ----------

# Grounding metadata Genie sees (declared in the pipeline)
display(spark.sql(f"""
SELECT table_name, comment FROM {CATALOG}.information_schema.tables
WHERE table_schema = '{SCHEMA}' AND table_name IN
  ('vendors','contracts','data_products','coverage','data_elements','vendor_coverage_enriched')
ORDER BY table_name"""))
display(spark.sql(f"""
SELECT table_name, column_name, comment FROM {CATALOG}.information_schema.columns
WHERE table_schema = '{SCHEMA}' AND table_name IN ('coverage','contracts') ORDER BY table_name, ordinal_position"""))

# COMMAND ----------

print("Flagship question as deterministic SQL — Which vendors cover HCP data in Egypt?")
display(spark.sql(f"""
SELECT DISTINCT vendor_name, coverage_type, counts
FROM {FQ}.vendor_coverage_enriched
WHERE data_type = 'HCP' AND geographic_region = 'Egypt'
ORDER BY counts DESC"""))
