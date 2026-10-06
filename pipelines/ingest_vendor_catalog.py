# Databricks notebook source
# =============================================================================
# ingest_vendor_catalog  —  Lakeflow Declarative Pipeline (Auto Loader)
#
# Stage 1 of the journey: RAW vendor-catalog JSON in a UC Volume ->
#   bronze_vendor_catalog   streaming table  (Auto Loader, schema inference,
#                                              file-level lineage, exactly-once)
#   silver_vendor_catalog   streaming table  (typed + validated with expectations)
#   vendors / contracts / data_products / coverage / data_elements
#                           materialized views (the governed Gold model Genie,
#                                              the agent, Lakebase and BI read)
#
# Governance is declared here, next to the data: table + column comments (the
# "ontology" Genie grounds on) and the Unity Catalog column mask on contract
# cost (function created by notebook 01).
#
# Pipeline notebooks can't %run 00_config — catalog/schema/path arrive via the
# pipeline `configuration` block in databricks.yml.
# =============================================================================

import dlt
from pyspark.sql import functions as F

CATALOG = spark.conf.get("lumora.catalog")
SCHEMA = spark.conf.get("lumora.schema")
RAW_PATH = spark.conf.get("lumora.raw_path")
FQ = f"{CATALOG}.{SCHEMA}"

# COMMAND ----------

# ---- Bronze: Auto Loader over the landing Volume ---------------------------
@dlt.table(
    name="bronze_vendor_catalog",
    comment="Raw vendor-catalog exports ingested incrementally by Auto Loader (one row per JSON file), with source-file lineage.",
    table_properties={"quality": "bronze"},
)
def bronze_vendor_catalog():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("multiLine", "true")
        .option("cloudFiles.inferColumnTypes", "true")
        .load(RAW_PATH)
        .withColumn("_ingested_at", F.current_timestamp())
        .withColumn("_source_file", F.col("_metadata.file_path"))
    )

# COMMAND ----------

# ---- Silver: typed + validated --------------------------------------------
@dlt.table(
    name="silver_vendor_catalog",
    comment="Validated vendor-catalog exports: typed identifiers, one row per vendor export. Rows failing hard rules are dropped.",
    table_properties={"quality": "silver"},
)
@dlt.expect_or_drop("vendor_id_present", "vendor_id IS NOT NULL")
@dlt.expect_or_drop("vendor_name_present", "vendor_name IS NOT NULL AND trim(vendor_name) <> ''")
@dlt.expect("has_products", "size(products) > 0")
@dlt.expect("has_coverage", "size(coverage) > 0")
@dlt.expect("contract_dates_ordered", "contract.contract_end > contract.contract_start")
def silver_vendor_catalog():
    return (
        dlt.read_stream("bronze_vendor_catalog")
        .withColumn("year_established", F.col("year_established").cast("int"))
        .withColumn("is_analytical_platform", F.col("is_analytical_platform").cast("boolean"))
    )

# COMMAND ----------

# ---- Gold: the governed attribute model -------------------------------------
@dlt.table(
    name="vendors",
    comment="One row per third-party data vendor in the Lumora data marketplace. The authoritative list of vendors and their firmographics.",
    schema="""
      vendor_id STRING COMMENT 'Unique vendor identifier (e.g. V001). Join key to coverage, data_products, contracts, data_elements.',
      vendor_name STRING COMMENT 'Vendor company name (e.g. MediReach Analytics).',
      vendor_description STRING COMMENT 'Short business description of what the vendor provides.',
      year_established INT COMMENT 'Year the vendor was founded.',
      headquarters STRING COMMENT 'Vendor headquarters country/region.',
      is_analytical_platform BOOLEAN COMMENT 'True if the vendor delivers via an analytical platform (vs. flat file/API delivery).',
      website STRING COMMENT 'Vendor website (fictional example.com domain).'
    """,
    table_properties={"quality": "gold"},
)
def vendors():
    return dlt.read("silver_vendor_catalog").select(
        "vendor_id", "vendor_name", "vendor_description", "year_established",
        "headquarters", "is_analytical_platform", "website")


@dlt.table(
    name="contracts",
    comment="Contract terms per vendor: start/end dates, status, and annual cost. Use to answer renewal, expiry, and spend questions. Cost is column-masked (finance only).",
    schema=f"""
      vendor_id STRING COMMENT 'Vendor identifier (join key to vendors).',
      contract_id STRING COMMENT 'Contract identifier.',
      contract_start STRING COMMENT 'Contract start date (ISO yyyy-mm-dd).',
      contract_end STRING COMMENT 'Contract end date (ISO yyyy-mm-dd). Filter for upcoming renewals.',
      status STRING COMMENT 'Contract status: Active, Expiring Soon (ends within ~120 days), or Expired.',
      annual_cost_usd BIGINT COMMENT 'Annual contract cost in USD. Masked to NULL for users outside the finance group.' MASK {FQ}.mask_cost,
      renewal_owner STRING COMMENT 'Team accountable for the renewal decision.'
    """,
    table_properties={"quality": "gold"},
)
def contracts():
    c = dlt.read("silver_vendor_catalog").select("vendor_id", "contract.*")
    return c.select("vendor_id", "contract_id", "contract_start", "contract_end", "status",
                    F.col("annual_cost_usd").cast("bigint").alias("annual_cost_usd"), "renewal_owner")


@dlt.table(
    name="data_products",
    comment="Data products offered by each vendor. A vendor offers one product per data type (HCP, HCO, Claims, etc.).",
    schema="""
      vendor_id STRING COMMENT 'Vendor identifier (join key to vendors).',
      product_id STRING COMMENT 'Product identifier (e.g. V001-P01).',
      product_name STRING COMMENT 'Product name.',
      data_type STRING COMMENT 'Category of data: HCP (healthcare professional), HCO (healthcare organization), Claims, Patient, Clinical Trial, Publication, Social Media, Rx/Medication.',
      indication_ta STRING COMMENT 'Primary therapeutic area the product focuses on (e.g. Oncology, Cardiology).',
      description STRING COMMENT 'Product description.'
    """,
    table_properties={"quality": "gold"},
)
def data_products():
    return (dlt.read("silver_vendor_catalog")
            .select("vendor_id", F.explode("products").alias("p"))
            .select("vendor_id", "p.product_id", "p.product_name", "p.data_type",
                    "p.indication_ta", "p.description"))


@dlt.table(
    name="coverage",
    comment="Geographic and volume coverage per vendor data product. THE table to answer which vendors cover a given data type in a given country/region. Each row = one (vendor, product, data_type, geographic_region) with a count.",
    schema="""
      vendor_id STRING COMMENT 'Vendor identifier (join key to vendors).',
      coverage_id STRING COMMENT 'Coverage row identifier.',
      product_id STRING COMMENT 'Product identifier (join key to data_products).',
      data_type STRING COMMENT 'Data type covered (HCP, HCO, Claims, Patient, Clinical Trial, Publication, Social Media, Rx/Medication).',
      geographic_region STRING COMMENT 'Country or region this coverage applies to (e.g. US, EU, Egypt, Argentina, Nigeria, Japan). Use this to filter vendors by geography.',
      coverage_type STRING COMMENT 'What the count measures, e.g. HCP count, HCO count, Claims volume.',
      counts BIGINT COMMENT 'Number of records the vendor covers for this data type in this region (e.g. HCP count).',
      indication_ta STRING COMMENT 'Therapeutic area of the covered records.'
    """,
    table_properties={"quality": "gold"},
)
@dlt.expect("coverage_positive_count", "counts > 0")
def coverage():
    return (dlt.read("silver_vendor_catalog")
            .select("vendor_id", F.explode("coverage").alias("c"))
            .select("vendor_id", "c.coverage_id", "c.product_id", "c.data_type",
                    "c.geographic_region", "c.coverage_type",
                    F.col("c.counts").cast("bigint").alias("counts"), "c.indication_ta"))


@dlt.table(
    name="data_elements",
    comment="Field-level data elements available per vendor product (e.g. HCP has NPI/ID, Specialty, Email). available=false means the element is documented but not delivered.",
    schema="""
      vendor_id STRING COMMENT 'Vendor identifier (join key to vendors).',
      element_id STRING COMMENT 'Element identifier.',
      product_id STRING COMMENT 'Product identifier (join key to data_products).',
      data_type STRING COMMENT 'Data type of the product.',
      category STRING COMMENT 'Element category.',
      attribute STRING COMMENT 'Field / attribute name (e.g. Specialty, NPI/ID).',
      available BOOLEAN COMMENT 'True if this data element is actually delivered by the vendor for this product.'
    """,
    table_properties={"quality": "gold"},
)
def data_elements():
    return (dlt.read("silver_vendor_catalog")
            .select("vendor_id", F.explode("data_elements").alias("e"))
            .select("vendor_id", "e.element_id", "e.product_id", "e.data_type",
                    "e.category", "e.attribute", F.col("e.available").cast("boolean").alias("available")))
