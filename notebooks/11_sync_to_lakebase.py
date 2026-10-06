# Databricks notebook source
# =============================================================================
# 11_sync_to_lakebase
#
# Phase 8 backend: compute the vendor "tile" summary from the governed Gold
# tables and push it into Lakebase (managed Postgres) so the app serves tiles
# with millisecond latency — Delta precompute -> Lakebase -> fast app reads.
#
# Lakebase instance name comes from 00_config (LAKEBASE_INSTANCE).
# =============================================================================

# COMMAND ----------

# MAGIC %pip install --quiet "psycopg[binary]>=3.1"
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %run ./00_config

# COMMAND ----------

# CATALOG / SCHEMA / FQ / LAKEBASE_INSTANCE / PG_SCHEMA come from 00_config

PG_DB = "databricks_postgres"

# COMMAND ----------

# ---- Build the tile summary from Gold (one row per vendor) ------------------
tiles = spark.sql(f"""
  SELECT
    v.vendor_name,
    v.vendor_description,
    (SELECT max(c.contract_end)  FROM {FQ}.contracts c     WHERE c.vendor_id = v.vendor_id) AS contract_expiry,
    (SELECT c.status             FROM {FQ}.contracts c     WHERE c.vendor_id = v.vendor_id LIMIT 1) AS contract_status,
    (SELECT count(*)             FROM {FQ}.data_products p WHERE p.vendor_id = v.vendor_id) AS no_of_products,
    (SELECT max(cv.counts)       FROM {FQ}.coverage cv     WHERE cv.vendor_id = v.vendor_id AND cv.data_type='HCP') AS hcp_count,
    (SELECT concat_ws(', ', array_sort(collect_set(cv.geographic_region))) FROM {FQ}.coverage cv WHERE cv.vendor_id = v.vendor_id) AS geographical_coverage,
    (SELECT concat_ws(', ', array_sort(collect_set(p.data_type)))          FROM {FQ}.data_products p WHERE p.vendor_id = v.vendor_id) AS data_types_offered
  FROM {FQ}.vendors v
  ORDER BY v.vendor_name
""")
tiles.write.mode("overwrite").option("overwriteSchema", "true").saveAsTable(f"{FQ}.vendor_tiles")
rows = [r.asDict() for r in tiles.collect()]
print(f"Computed {len(rows)} vendor tiles.")

# COMMAND ----------

# ---- Push into Lakebase Postgres --------------------------------------------
import uuid
import psycopg
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
PG_HOST = w.database.get_database_instance(name=LAKEBASE_INSTANCE).read_write_dns
pg_user = w.current_user.me().user_name
# Lakebase needs a database credential (a Postgres-valid token), NOT the raw OAuth token.
pg_token = w.database.generate_database_credential(
    request_id=str(uuid.uuid4()), instance_names=[LAKEBASE_INSTANCE]
).token

with psycopg.connect(host=PG_HOST, dbname=PG_DB, user=pg_user, password=pg_token,
                     sslmode="require", connect_timeout=20) as conn:
    with conn.cursor() as cur:
        cur.execute(f"CREATE SCHEMA IF NOT EXISTS {PG_SCHEMA}")
        cur.execute(f"DROP TABLE IF EXISTS {PG_SCHEMA}.vendor_tiles")
        cur.execute(f"""
            CREATE TABLE {PG_SCHEMA}.vendor_tiles (
                vendor_name TEXT, vendor_description TEXT, contract_expiry TEXT,
                contract_status TEXT, no_of_products INT, hcp_count BIGINT,
                geographical_coverage TEXT, data_types_offered TEXT
            )
        """)
        for r in rows:
            cur.execute(
                f"INSERT INTO {PG_SCHEMA}.vendor_tiles VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                (r["vendor_name"], r["vendor_description"],
                 str(r["contract_expiry"]) if r["contract_expiry"] else None,
                 r["contract_status"], r["no_of_products"], r["hcp_count"],
                 r["geographical_coverage"], r["data_types_offered"]),
            )
    conn.commit()
    with conn.cursor() as cur:
        cur.execute(f"SELECT count(*) FROM {PG_SCHEMA}.vendor_tiles")
        print("Lakebase lumora.vendor_tiles row count:", cur.fetchone()[0])
        cur.execute(f"GRANT USAGE ON SCHEMA {PG_SCHEMA} TO PUBLIC")
        cur.execute(f"GRANT SELECT ON {PG_SCHEMA}.vendor_tiles TO PUBLIC")
    conn.commit()

print("Synced vendor tiles into Lakebase.")
