# end_to_end / setup_and_generate_raw

- **Notebook:** `notebooks/01_setup_and_generate_raw`
- **Task run id:** `683950840369129` · **Result:** `SUCCESS`
- **Started:** 2026-10-06 06:59:25 UTC · **Ended:** 2026-10-06 06:59:51 UTC
- **Job run:** https://fevm-aws-serverless-ws-sr.cloud.databricks.com/?o=7474651022795245#job/789028661266524/run/1002479881266291

_Exported from the job run with `databricks jobs export-run` — cell source followed by the output the cell produced in that run._

## Cell 1

```python
%run ./00_config
```

## Cell 3

```python
# =============================================================================
# 01_setup_and_generate_raw
#
# Lumora Clinical Research (fictional CRO) — Vendor Data Marketplace
# Stage 0: governed landing zone + synthetic RAW data.
#
#   1. Schema + UC Volume (raw landing zone for vendor-catalog exports)
#   2. Governance functions (column masks / row filter) — created FIRST because
#      the Lakeflow ingest pipeline attaches mask_cost to contracts.annual_cost_usd
#   3. Generate 18 fictional vendor-catalog exports as raw JSON in the Volume
#
# Ingestion (Bronze -> Silver -> Gold) is NOT done here: the Lakeflow Declarative
# Pipeline `pipelines/ingest_vendor_catalog.py` picks these files up with
# Auto Loader. All data is synthetic; vendor names are fictional.
# =============================================================================
```

## Cell 4

```python
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA} "
          f"COMMENT 'Lumora Clinical Research (fictional CRO) — governed third-party data vendor marketplace (synthetic data).'")
spark.sql(f"CREATE VOLUME IF NOT EXISTS {CATALOG}.{SCHEMA}.{RAW_VOLUME} "
          f"COMMENT 'Raw vendor-catalog exports landed by vendor managers (stand-in for a shared document folder). Auto Loader source.'")
print("Schema + volume ready:", RAW_PATH)
```

**Output:**

```text
Schema + volume ready: /Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/raw_vendor_catalogs
```

## Cell 5

```python
# ---- Governance functions (Unity Catalog) -----------------------------------
# is_member() covers workspace-local groups; is_account_group_member() covers
# account groups — either grants clear-text access.
IS_PRIV = f"(is_member('{PRIV_GROUP}') OR is_account_group_member('{PRIV_GROUP}'))"

spark.sql(f"""
CREATE OR REPLACE FUNCTION {FQ}.mask_cost(cost BIGINT)
RETURNS BIGINT
COMMENT 'Column mask: annual contract cost visible only to {PRIV_GROUP}; NULL for everyone else.'
RETURN CASE WHEN {IS_PRIV} THEN cost ELSE NULL END
""")
spark.sql(f"""
CREATE OR REPLACE FUNCTION {FQ}.mask_email(email STRING)
RETURNS STRING
COMMENT 'Column mask: full email for {PRIV_GROUP}; first letter + domain for everyone else.'
RETURN CASE WHEN {IS_PRIV} THEN email
            ELSE concat(left(email, 1), '***@', split_part(email, '@', 2)) END
""")
spark.sql(f"""
CREATE OR REPLACE FUNCTION {FQ}.mask_phone(phone STRING)
RETURNS STRING
COMMENT 'Column mask: full phone for {PRIV_GROUP}; last 4 digits only for everyone else.'
RETURN CASE WHEN {IS_PRIV} THEN phone ELSE concat('***-***-', right(phone, 4)) END
""")
spark.sql(f"""
CREATE OR REPLACE FUNCTION {FQ}.filter_contacts(contact_type STRING)
RETURNS BOOLEAN
COMMENT 'Row filter: Commercial/Pricing contacts visible only to {PRIV_GROUP}.'
RETURN {IS_PRIV} OR contact_type <> 'Commercial/Pricing'
""")
display(spark.sql(f"SHOW USER FUNCTIONS IN {FQ}"))
```

**Output:**

| function |
|---|
| aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.filter_contacts |
| aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.mask_cost |
| aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.mask_email |
| aws_serverless_ws_sr_catalog.lumora_vendor_marketplace.mask_phone |

## Cell 6

```python
# ---- Phase 1a: generate synthetic vendor catalogs ---------------------------
# Hand-authored dimensions + controlled randomness so the demo's flagship
# questions ("which vendors cover HCP data in Egypt?") have real, non-trivial
# answers with genuine overlap and genuine gaps across vendors.
import json, random, os
from datetime import date, timedelta

random.seed(42)

DATA_TYPES = ["HCP", "HCO", "Claims", "Patient", "Clinical Trial", "Publication", "Social Media", "Rx/Medication"]
REGIONS = ["US", "EU", "UK", "Canada", "Brazil", "Argentina", "Egypt", "South Africa",
           "Nigeria", "Kenya", "India", "China", "Japan", "Australia", "Germany", "France"]
INDICATIONS = ["Oncology", "Cardiology", "Immunology", "Neurology", "Rare Disease",
               "Endocrinology", "Infectious Disease", "Respiratory"]

# 18 fictional vendors, each with an archetype and a "home" region bias.
VENDOR_DEFS = [
    ("MediReach Analytics",      "HCP and HCO reference data with global affiliations.", 2009, "US",   True,  ["HCP","HCO","Publication"],        ["US","EU","UK","Canada","Egypt","South Africa"]),
    ("ClaimStream Data Co",      "De-identified medical & pharmacy claims at scale.",     2012, "US",   True,  ["Claims","Rx/Medication","Patient"], ["US","Canada","Brazil"]),
    ("TrialSphere Global",       "Clinical trial intelligence and investigator data.",    2015, "UK",   True,  ["Clinical Trial","HCP","Publication"],["US","EU","UK","India","China","Argentina"]),
    ("PatientGraph",             "Longitudinal patient journey and outcomes data.",       2017, "EU",   False, ["Patient","Claims"],               ["EU","Germany","France","UK"]),
    ("PharmaGeo Insights",       "Geographic HCP density and prescribing footprints.",    2010, "US",   True,  ["HCP","Rx/Medication"],            ["US","EU","Egypt","Nigeria","Kenya","South Africa","Argentina"]),
    ("PubSignal Ltd",            "Biomedical publication and KOL signal data.",           2013, "UK",   False, ["Publication","HCP"],              ["US","EU","UK","Japan","Australia"]),
    ("GlobalHCP Registry",       "Verified HCP master data across emerging markets.",     2016, "EU",   True,  ["HCP","HCO"],                      ["Egypt","Nigeria","Kenya","South Africa","India","Brazil","Argentina"]),
    ("RxPatterns",               "Retail & specialty Rx dispensing patterns.",            2011, "US",   True,  ["Rx/Medication","Claims"],         ["US","Canada"]),
    ("VoxPatient Social",        "Patient sentiment and social listening data.",          2018, "US",   False, ["Social Media","Patient"],         ["US","EU","UK","Brazil"]),
    ("CardioData Partners",      "Cardiology-focused HCP and outcomes data.",             2014, "EU",   True,  ["HCP","Patient","Clinical Trial"], ["EU","Germany","France","US"]),
    ("OncoReach",                "Oncology HCP, HCO and trial site intelligence.",        2016, "US",   True,  ["HCP","HCO","Clinical Trial"],     ["US","EU","Japan","China","Egypt"]),
    ("AfriHealth Data",          "Emerging-markets HCP/HCO and claims coverage.",         2019, "South Africa", True, ["HCP","HCO","Claims"],       ["South Africa","Nigeria","Kenya","Egypt"]),
    ("LatAm MedInsights",        "Latin America HCP, patient and claims data.",           2015, "Brazil", True, ["HCP","Patient","Claims"],        ["Brazil","Argentina"]),
    ("APAC HealthLink",          "Asia-Pacific HCP and prescribing data.",                2017, "Japan", True,  ["HCP","Rx/Medication"],           ["Japan","China","India","Australia"]),
    ("ImmunoData",               "Immunology KOLs, trials and publications.",             2018, "US",   False, ["HCP","Clinical Trial","Publication"],["US","EU","UK"]),
    ("PayerLens",                "Payer, formulary and claims analytics.",                2012, "US",   True,  ["Claims","HCO"],                   ["US"]),
    ("NeuroGraph",               "Neurology patient journeys and HCP networks.",          2016, "EU",   False, ["Patient","HCP"],                  ["EU","UK","US","Canada"]),
    ("GlobalTrials Registry",    "Worldwide clinical trial and site registry.",           2010, "UK",   True,  ["Clinical Trial","HCO"],           ["US","EU","UK","India","China","Brazil","Argentina","Egypt","South Africa"]),
]

DATA_ELEMENTS_BY_TYPE = {
    "HCP": ["NPI/ID","Full name","Specialty","Affiliation","Email","Phone","Address","License number"],
    "HCO": ["Org ID","Org name","Facility type","Bed count","Address","Parent org"],
    "Claims": ["Claim ID","Procedure code","Diagnosis code","Service date","Payer","Amount"],
    "Patient": ["Patient token","Age band","Gender","Diagnosis","Treatment","Outcome"],
    "Clinical Trial": ["Trial ID","Phase","Sponsor","Investigator","Site","Indication","Status"],
    "Publication": ["PubMed ID","Title","Authors","Journal","Date","Citations"],
    "Social Media": ["Post ID","Platform","Sentiment","Topic","Date"],
    "Rx/Medication": ["Drug name","NDC","Strength","Days supply","Prescriber","Fill date"],
}

def _rand_contract():
    start = date.today() - timedelta(days=random.randint(200, 1300))
    end = start + timedelta(days=random.choice([365, 730, 1095]))
    today = date.today()   # status is relative to the run date, so 'Expiring Soon' stays meaningful
    if end < today:
        status = "Expired"
    elif end < today + timedelta(days=120):
        status = "Expiring Soon"
    else:
        status = "Active"
    return start.isoformat(), end.isoformat(), status, random.choice([75000,120000,180000,250000,400000])

vendor_exports = []
for i, (name, desc, est, hq, is_platform, dtypes, regions) in enumerate(VENDOR_DEFS, start=1):
    vid = f"V{i:03d}"
    products, coverage, elements = [], [], []
    for j, dt in enumerate(dtypes, start=1):
        pid = f"{vid}-P{j:02d}"
        products.append({
            "product_id": pid, "product_name": f"{name.split()[0]} {dt} Data",
            "data_type": dt, "indication_ta": random.choice(INDICATIONS),
            "description": f"{dt} data product from {name}.",
        })
        # coverage: this product covers a subset of the vendor's regions
        covered = random.sample(regions, k=max(1, int(len(regions) * random.uniform(0.5, 1.0))))
        for r in covered:
            base = {"HCP": 50000, "HCO": 8000, "Claims": 2_000_000, "Patient": 500_000,
                    "Clinical Trial": 1200, "Publication": 300_000, "Social Media": 1_500_000,
                    "Rx/Medication": 3_000_000}.get(dt, 10000)
            coverage.append({
                "coverage_id": f"{pid}-{r[:3].upper()}", "product_id": pid, "data_type": dt,
                "geographic_region": r,
                "coverage_type": f"{dt} count" if dt in ("HCP","HCO","Patient","Clinical Trial") else f"{dt} volume",
                "counts": int(base * random.uniform(0.2, 1.4)),
                "indication_ta": random.choice(INDICATIONS),
            })
        for attr in DATA_ELEMENTS_BY_TYPE.get(dt, []):
            elements.append({
                "element_id": f"{pid}-{attr[:4].upper().replace('/','')}",
                "product_id": pid, "data_type": dt, "category": dt, "attribute": attr,
                "available": random.random() > 0.15,
            })
    cs, ce, cstatus, cost = _rand_contract()
    vendor_exports.append({
        "vendor_id": vid, "vendor_name": name, "vendor_description": desc,
        "year_established": est, "headquarters": hq, "is_analytical_platform": is_platform,
        "website": f"https://www.{name.split()[0].lower()}-data.example.com",
        "contract": {"contract_id": f"{vid}-C1", "contract_start": cs, "contract_end": ce,
                     "status": cstatus, "annual_cost_usd": cost, "renewal_owner": "Data Governance Team"},
        "products": products, "coverage": coverage, "data_elements": elements,
    })

print(f"Generated {len(vendor_exports)} synthetic vendor catalogs "
      f"({sum(len(v['coverage']) for v in vendor_exports)} coverage rows, "
      f"{sum(len(v['products']) for v in vendor_exports)} products).")
```

**Output:**

```text
Generated 18 synthetic vendor catalogs (126 coverage rows, 44 products).
```

## Cell 8

```python
# ---- Land raw JSON in the Volume (one file per vendor export) ----------------
# Files are written only if absent, so re-runs don't re-trigger Auto Loader on
# unchanged exports (the pipeline processes each file exactly once).
os.makedirs(RAW_PATH, exist_ok=True)
written = 0
for v in vendor_exports:
    path = f"{RAW_PATH}/{v['vendor_id']}_{v['vendor_name'].replace(' ','_')}.json"
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump(v, f, indent=2)
        written += 1
print(f"New raw files written: {written} | total in volume: {len(os.listdir(RAW_PATH))}")
display(dbutils.fs.ls(RAW_PATH))
```

**Output:**

```text
New raw files written: 0 | total in volume: 18
```

| path | name | size | modificationTime |
|---|---|---|---|
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/raw_vendor_catalogs/V001_MediReach_Analytics.json | V001_MediReach_Analytics.json | 8302 | 1791267436000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/raw_vendor_catalogs/V002_ClaimStream_Data_Co.json | V002_ClaimStream_Data_Co.json | 5919 | 1791267436000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/raw_vendor_catalogs/V003_TrialSphere_Global.json | V003_TrialSphere_Global.json | 9004 | 1791267436000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/raw_vendor_catalogs/V004_PatientGraph.json | V004_PatientGraph.json | 4860 | 1791267436000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/raw_vendor_catalogs/V005_PharmaGeo_Insights.json | V005_PharmaGeo_Insights.json | 5521 | 1791267436000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/raw_vendor_catalogs/V006_PubSignal_Ltd.json | V006_PubSignal_Ltd.json | 5448 | 1791267436000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/raw_vendor_catalogs/V007_GlobalHCP_Registry.json | V007_GlobalHCP_Registry.json | 5347 | 1791267437000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/raw_vendor_catalogs/V008_RxPatterns.json | V008_RxPatterns.json | 3939 | 1791267437000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/raw_vendor_catalogs/V009_VoxPatient_Social.json | V009_VoxPatient_Social.json | 4508 | 1791267437000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/raw_vendor_catalogs/V010_CardioData_Partners.json | V010_CardioData_Partners.json | 7415 | 1791267437000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/raw_vendor_catalogs/V011_OncoReach.json | V011_OncoReach.json | 7530 | 1791267437000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/raw_vendor_catalogs/V012_AfriHealth_Data.json | V012_AfriHealth_Data.json | 7237 | 1791267437000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/raw_vendor_catalogs/V013_LatAm_MedInsights.json | V013_LatAm_MedInsights.json | 5836 | 1791267437000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/raw_vendor_catalogs/V014_APAC_HealthLink.json | V014_APAC_HealthLink.json | 5018 | 1791267437000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/raw_vendor_catalogs/V015_ImmunoData.json | V015_ImmunoData.json | 6685 | 1791267438000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/raw_vendor_catalogs/V016_PayerLens.json | V016_PayerLens.json | 3767 | 1791267438000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/raw_vendor_catalogs/V017_NeuroGraph.json | V017_NeuroGraph.json | 4881 | 1791267438000 |
| dbfs:/Volumes/aws_serverless_ws_sr_catalog/lumora_vendor_marketplace/raw_vendor_catalogs/V018_GlobalTrials_Registry.json | V018_GlobalTrials_Registry.json | 7422 | 1791267438000 |

## Cell 9

```python
# Peek at one raw export (what Auto Loader will ingest)
print(open(f"{RAW_PATH}/{sorted(os.listdir(RAW_PATH))[0]}").read()[:1500])
```

**Output:**

```text
{
  "vendor_id": "V001",
  "vendor_name": "MediReach Analytics",
  "vendor_description": "HCP and HCO reference data with global affiliations.",
  "year_established": 2009,
  "headquarters": "US",
  "is_analytical_platform": true,
  "website": "https://www.medireach-data.example.com",
  "contract": {
    "contract_id": "V001-C1",
    "contract_start": "2024-12-26",
    "contract_end": "2027-12-26",
    "status": "Active",
    "annual_cost_usd": 180000,
    "renewal_owner": "Data Governance Team"
  },
  "products": [
    {
      "product_id": "V001-P01",
      "product_name": "MediReach HCP Data",
      "data_type": "HCP",
      "indication_ta": "Cardiology",
      "description": "HCP data product from MediReach Analytics."
    },
    {
      "product_id": "V001-P02",
      "product_name": "MediReach HCO Data",
      "data_type": "HCO",
      "indication_ta": "Rare Disease",
      "description": "HCO data product from MediReach Analytics."
    },
    {
      "product_id": "V001-P03",
      "product_name": "MediReach Publication Data",
      "data_type": "Publication",
      "indication_ta": "Neurology",
      "description": "Publication data product from MediReach Analytics."
    }
  ],
  "coverage": [
    {
      "coverage_id": "V001-P01-UK",
      "product_id": "V001-P01",
      "data_type": "HCP",
      "geographic_region": "UK",
      "coverage_type": "HCP count",
      "counts": 18372,
      "indication_ta": "Cardiology"
    },
    {
      "coverage_id": "V001-P01-EU",
```
