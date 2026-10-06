# Databricks notebook source
# MAGIC %run ./00_config

# COMMAND ----------
# =============================================================================
# 15_metric_views
#
# Semantic layer: Unity Catalog METRIC VIEWS over the Gold tables. Measures are
# defined ONCE here and reused by Genie, the AI/BI dashboard and plain SQL
# (MEASURE(`Total Annual Spend`)), instead of every consumer re-deriving them.
#
#   mv_vendor_coverage  coverage x vendor x contract — vendor-selection metrics
#   mv_contract_spend   contracts x vendor — spend / renewal metrics
#
# Column masks (01/14 + pipeline) still apply: for users outside lumora_finance the spend
# measures evaluate over masked (NULL) cost, so they can't be re-aggregated.
# =============================================================================

# COMMAND ----------

# CATALOG / SCHEMA / FQ come from 00_config

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE VIEW {FQ}.mv_vendor_coverage
WITH METRICS
LANGUAGE YAML
AS $$
version: 1.1
comment: "Vendor coverage metrics: how many vendors/products/records cover each data type, region and therapeutic area."
source: {FQ}.coverage
joins:
  - name: v
    source: {FQ}.vendors
    on: source.vendor_id = v.vendor_id
  - name: ct
    source: {FQ}.contracts
    on: source.vendor_id = ct.vendor_id
dimensions:
  - name: Vendor
    expr: v.vendor_name
  - name: Vendor HQ
    expr: v.headquarters
  - name: Analytical Platform
    expr: CASE WHEN v.is_analytical_platform THEN 'Platform' ELSE 'File/API delivery' END
  - name: Data Type
    expr: source.data_type
    comment: "HCP, HCO, Claims, Patient, Clinical Trial, Publication, Social Media, Rx/Medication"
  - name: Region
    expr: source.geographic_region
  - name: Therapeutic Area
    expr: source.indication_ta
  - name: Coverage Type
    expr: source.coverage_type
  - name: Contract Status
    expr: ct.status
measures:
  - name: Total Coverage
    expr: SUM(source.counts)
    comment: "Sum of covered records (e.g. HCP count) across the selected slice."
  - name: Vendor Count
    expr: COUNT(DISTINCT source.vendor_id)
  - name: Product Count
    expr: COUNT(DISTINCT source.product_id)
  - name: Region Count
    expr: COUNT(DISTINCT source.geographic_region)
  - name: Avg Coverage per Vendor
    expr: SUM(source.counts) / COUNT(DISTINCT source.vendor_id)
$$
""")
print("Created mv_vendor_coverage.")

# COMMAND ----------

spark.sql(f"""
CREATE OR REPLACE VIEW {FQ}.mv_contract_spend
WITH METRICS
LANGUAGE YAML
AS $$
version: 1.1
comment: "Vendor contract spend and renewal metrics. Cost is column-masked for users outside lumora_finance."
source: {FQ}.contracts
joins:
  - name: v
    source: {FQ}.vendors
    on: source.vendor_id = v.vendor_id
dimensions:
  - name: Vendor
    expr: v.vendor_name
  - name: Vendor HQ
    expr: v.headquarters
  - name: Contract Status
    expr: source.status
  - name: Contract End Date
    expr: to_date(source.contract_end)
  - name: Contract End Month
    expr: DATE_TRUNC('MONTH', to_date(source.contract_end))
measures:
  - name: Total Annual Spend
    expr: SUM(source.annual_cost_usd)
  - name: Avg Contract Value
    expr: AVG(source.annual_cost_usd)
  - name: Contract Count
    expr: COUNT(source.contract_id)
  - name: Expiring Soon Contracts
    expr: COUNT_IF(source.status = 'Expiring Soon')
  - name: Expired Contracts
    expr: COUNT_IF(source.status = 'Expired')
  - name: Spend at Risk
    expr: SUM(CASE WHEN source.status = 'Expiring Soon' THEN source.annual_cost_usd END)
    comment: "Annual spend on contracts that are expiring soon (renewal decisions pending)."
$$
""")
print("Created mv_contract_spend.")

# COMMAND ----------

# MAGIC %md ## Verify — query measures with MEASURE()

# COMMAND ----------

display(spark.sql(f"""
SELECT `Vendor`, MEASURE(`Total Coverage`) AS total_coverage
FROM {FQ}.mv_vendor_coverage
WHERE `Data Type` = 'HCP' AND `Region` = 'Egypt'
GROUP BY ALL ORDER BY total_coverage DESC
"""))
display(spark.sql(f"""
SELECT `Contract Status`, MEASURE(`Contract Count`) AS contracts, MEASURE(`Total Annual Spend`) AS spend
FROM {FQ}.mv_contract_spend GROUP BY ALL
"""))
