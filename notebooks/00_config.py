# Databricks notebook source
# =============================================================================
# 00_config  —  EDIT THIS FILE FOR YOUR WORKSPACE, then run the notebooks in order.
#
# Every batch notebook in this project starts with `%run ./00_config`, so this
# is the ONE place you set your catalog, schema, and resource names. Values you
# fill in *as you go* (Genie space id, supervisor endpoint) are marked below.
# The values committed here are the ones the reference build ran with (FEVM).
#
# See README.md for the full run order.
# =============================================================================

# ---- 1. Unity Catalog target  (REQUIRED — set before notebook 01) ----------
# The catalog must let you CREATE SCHEMA / TABLE / VOLUME / FUNCTION.
CATALOG = "aws_serverless_ws_sr_catalog"     # <-- CHANGE ME to your catalog
SCHEMA  = "lumora_vendor_marketplace"        # schema this project creates

# ---- 2. Foundation models  (defaults work on most Databricks workspaces) ---
LLM_ENDPOINT = "databricks-claude-sonnet-4-5"   # pay-per-token FM (agent + DQ rules)
EMBED_MODEL  = "databricks-gte-large-en"         # embeddings for Vector Search

# ---- 3. Vector Search  (REQUIRED before notebook 04) -----------------------
VS_ENDPOINT = "vector_search_endpoint_name"      # <-- an existing Vector Search endpoint

# ---- 4. Genie space id  (fill in AFTER genie/create_spaces.py) -------------
GENIE_SPACE_ID = "01f1c14e775014ac9693c78ae663bc6c"   # from genie/create_space.py (genie/space_id.txt)

# ---- 5. Lakebase  (instance is created by the bundle: database_instances) --
LAKEBASE_INSTANCE = "lumora-marketplace-db"
PG_SCHEMA = "lumora"                              # Postgres schema for the served tiles

# ---- 6. MLflow experiment  (name only; path/id resolved automatically) -----
EXPERIMENT_NAME = "lumora_genie_eval"

# ---- 7. Governance  ---------------------------------------------------------
# Members of this group see contract cost + full vendor-contact PII; everyone
# else sees masked values (notebook 01 creates the functions, 14 applies them).
PRIV_GROUP = "lumora_finance"

# =============================================================================
# Derived — you normally don't edit below here.
# =============================================================================
FQ = f"{CATALOG}.{SCHEMA}"
VS_INDEX = f"{FQ}.vendor_docs_index"
RAW_VOLUME = "raw_vendor_catalogs"
RAW_PATH = f"/Volumes/{CATALOG}/{SCHEMA}/{RAW_VOLUME}"

try:
    _user = spark.sql("select current_user()").first()[0]
    EXPERIMENT_PATH = f"/Users/{_user}/{EXPERIMENT_NAME}"
except Exception:
    EXPERIMENT_PATH = f"/Shared/{EXPERIMENT_NAME}"

print(
    f"[config] target={FQ} | LLM={LLM_ENDPOINT} | VS endpoint={VS_ENDPOINT} | "
    f"index={VS_INDEX} | Genie={GENIE_SPACE_ID or '(set after genie step)'} | "
    f"Lakebase={LAKEBASE_INSTANCE}"
)
