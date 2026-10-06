# Databricks notebook source
# =============================================================================
# 13_dlt_quality_pipeline  (Lakeflow Declarative Pipeline / DLT)
#
# Phase 7, part 2 — the "deploy" half of self-service DQ. Notebook 10 authored
# the rules (NL -> SQL) and emitted the @dlt.expect strings; THIS pipeline
# actually applies them as live expectations, so the checks show up in
# Jobs & Pipelines with per-expectation pass/drop metrics.
#
# The 5 rules are the exact SQL expressions generated in notebook 10 and
# persisted to `dq_rules.sql_pass_expr`. `coverage_min_5000` is enforced with
# expect_or_drop, so the ~24/123 low-coverage rows are visibly dropped in the
# pipeline's Data Quality panel; the rest are tracked as warnings.
#
# Reads the governed Gold tables and writes *_clean tables into the same
# schema. Deployed via the `dlt_quality` pipeline in databricks.yml (serverless).
# =============================================================================

import dlt
from pyspark.sql import functions as F

# NOTE: Lakeflow/DLT pipeline notebooks cannot use `%run ./00_config`.
# Catalog/schema are passed in from the pipeline's `configuration` block in
# databricks.yml (keep those values identical to 00_config). Defaults are a
# fallback for running this notebook standalone.
CATALOG = spark.conf.get("demo.catalog", "main")
SCHEMA  = spark.conf.get("demo.schema", "lumora_vendor_marketplace")
FQ = f"{CATALOG}.{SCHEMA}"

# COMMAND ----------

# vendors -> vendors_clean
@dlt.table(
    name="vendors_clean",
    comment="Vendors that pass the self-service DQ rule (non-empty description).",
)
@dlt.expect("vendor_has_description",
            "vendor_description IS NOT NULL AND TRIM(vendor_description) != ''")
def vendors_clean():
    return spark.read.table(f"{FQ}.vendors")


# coverage -> coverage_clean
# Two rules on coverage. coverage_min_5000 is enforced (drop) so the failing
# rows are removed from the clean table and counted in the DQ metrics.
@dlt.table(
    name="coverage_clean",
    comment="Coverage rows passing DQ: positive count (warn) + >= 5000 records (enforced/drop).",
)
@dlt.expect("coverage_positive_count", "counts > 0")
@dlt.expect_or_drop("coverage_min_5000", "counts >= 5000")
def coverage_clean():
    return spark.read.table(f"{FQ}.coverage")


# contracts -> contracts_clean
@dlt.table(
    name="contracts_clean",
    comment="Contracts passing the DQ rule (end date after start date).",
)
@dlt.expect("contract_dates_valid",
            "contract_end > contract_start OR contract_end IS NULL OR contract_start IS NULL")
def contracts_clean():
    return spark.read.table(f"{FQ}.contracts")


# data_elements -> data_elements_clean
@dlt.table(
    name="data_elements_clean",
    comment="Data elements passing the DQ rule (available elements must have an attribute name).",
)
@dlt.expect("available_element_has_name",
            "available = false OR available IS NULL OR (available = true AND attribute IS NOT NULL AND TRIM(attribute) != '')")
def data_elements_clean():
    return spark.read.table(f"{FQ}.data_elements")
