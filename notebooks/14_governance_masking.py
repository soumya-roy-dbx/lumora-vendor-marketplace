# Databricks notebook source
# MAGIC %run ./00_config

# COMMAND ----------
# =============================================================================
# 14_governance_masking
#
# Governance: Unity Catalog COLUMN MASKS + a ROW FILTER on vendor contact PII.
# (Contract cost is masked declaratively in the Lakeflow pipeline schema.)
#
#   1. vendor_contacts  NEW synthetic table of vendor account managers
#                       (name/email/phone = realistic PII to protect)
#   2. mask functions   created in 01 (mask_cost / mask_email / mask_phone /
#                       filter_contacts), keyed on the group `lumora_finance`
#   3. apply masks      vendor_contacts.email/phone (contracts cost: pipeline)
#   4. row filter       vendor_contacts: Commercial/Pricing contacts are only
#                       visible to lumora_finance
#
# Masks are enforced for EVERY consumer — SQL, Genie, AI/BI dashboards, metric
# views and the vendor_coverage_enriched view — evaluated as the querying user.
#
# Demo: run the verify cell outside the group (masked), add yourself to
# lumora_finance, wait ~1-2 min, re-run (clear text).
#
# Run after the ingest pipeline (needs vendors).
# =============================================================================

# COMMAND ----------

IS_PRIV = f"(is_member('{PRIV_GROUP}') OR is_account_group_member('{PRIV_GROUP}'))"

# COMMAND ----------

# MAGIC %md ## 1. Synthetic vendor contacts (fictional people, example.com domains)

# COMMAND ----------

import random

random.seed(14)
FIRST = ["Amira", "Daniel", "Priya", "Lucas", "Mei", "Omar", "Sofia", "James", "Aisha",
         "Kenji", "Elena", "Tunde", "Hannah", "Mateo", "Grace", "Yusuf", "Chloe", "Ravi"]
LAST = ["Haddad", "Okafor", "Shah", "Silva", "Tanaka", "Farouk", "Rossi", "Miller",
        "Mensah", "Sato", "Novak", "Adeyemi", "Becker", "Lopez", "Kim", "Aziz", "Martin", "Iyer"]
ROLES = [("Account Manager", "Commercial/Pricing"), ("Data Support Lead", "Technical"),
         ("Data Steward", "Technical")]

vendors = spark.table(f"{FQ}.vendors").select("vendor_id", "vendor_name", "website").orderBy("vendor_id").collect()
rows = []
for i, v in enumerate(vendors):
    domain = v.website.replace("https://www.", "")
    for j, (title, ctype) in enumerate(ROLES):
        fn, ln = random.choice(FIRST), random.choice(LAST)
        rows.append((f"{v.vendor_id}-K{j+1}", v.vendor_id, v.vendor_name, f"{fn} {ln}", title, ctype,
                     f"{fn.lower()}.{ln.lower()}@{domain}",
                     f"+1-555-{random.randint(100,999)}-{random.randint(1000,9999)}"))

# Re-runnable: drop first (a row-filtered table can't be blindly overwritten by a non-member).
spark.sql(f"DROP TABLE IF EXISTS {FQ}.vendor_contacts")
spark.createDataFrame(rows, "contact_id string, vendor_id string, vendor_name string, contact_name string, "
                            "title string, contact_type string, email string, phone string") \
     .write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{FQ}.vendor_contacts")

spark.sql(f"COMMENT ON TABLE {FQ}.vendor_contacts IS 'Named contacts at each vendor (account manager, data support, data steward). Email/phone are PII and column-masked; Commercial/Pricing contacts are row-filtered to lumora_finance.'")
spark.sql(f"ALTER TABLE {FQ}.vendor_contacts ALTER COLUMN contact_type COMMENT 'Commercial/Pricing (restricted to finance) or Technical.'")
print(f"vendor_contacts: {len(rows)} rows")

# COMMAND ----------

# MAGIC %md ## 2. Apply masks + row filter (functions created in 01)

# COMMAND ----------

# contracts.annual_cost_usd is masked in the Lakeflow pipeline schema (MASK clause).
spark.sql(f"ALTER TABLE {FQ}.vendor_contacts ALTER COLUMN email SET MASK {FQ}.mask_email")
spark.sql(f"ALTER TABLE {FQ}.vendor_contacts ALTER COLUMN phone SET MASK {FQ}.mask_phone")
spark.sql(f"ALTER TABLE {FQ}.vendor_contacts SET ROW FILTER {FQ}.filter_contacts ON (contact_type)")
print("Masks + row filter applied.")

# COMMAND ----------

# MAGIC %md ## 3. Verify (result depends on who runs this cell)

# COMMAND ----------

print("In lumora_finance:", spark.sql(f"SELECT {IS_PRIV} AS p").first().p)
display(spark.sql(f"SELECT vendor_id, status, annual_cost_usd FROM {FQ}.contracts ORDER BY vendor_id LIMIT 5"))
display(spark.sql(f"SELECT vendor_name, title, contact_type, email, phone FROM {FQ}.vendor_contacts ORDER BY contact_id LIMIT 6"))
# Masks flow through views too:
display(spark.sql(f"SELECT DISTINCT vendor_name, annual_cost_usd FROM {FQ}.vendor_coverage_enriched LIMIT 5"))
