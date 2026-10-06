#!/usr/bin/env python3
"""Create (or update) the Lumora Vendor Data Marketplace Genie space via REST.

Self-contained: needs only the Databricks CLI (authenticated profile). The space
covers the Gold tables, the enriched view, the metric views (semantic layer) and
the masked vendor_contacts table, with instructions, certified example SQL and
benchmarks.

  python3 genie/create_space.py                 # create, writes genie/space_id.txt
  python3 genie/create_space.py --update        # PATCH the existing space
  python3 genie/create_space.py --dry-run       # print serialized_space
"""
import json
import os
import subprocess
import sys
import uuid

PROFILE = os.environ.get("DATABRICKS_PROFILE", "DEFAULT")
CATALOG = os.environ.get("CATALOG", "aws_serverless_ws_sr_catalog")
SCHEMA = os.environ.get("SCHEMA", "lumora_vendor_marketplace")
WAREHOUSE_ID = os.environ.get("WAREHOUSE_ID", "2cc7c1b1bd1873ce")
FQ = f"{CATALOG}.{SCHEMA}"
HERE = os.path.dirname(os.path.abspath(__file__))
ID_FILE = os.path.join(HERE, "space_id.txt")

TITLE = "Lumora Vendor Data Marketplace"
DESCRIPTION = (
    "Ask natural-language questions about Lumora Clinical Research's third-party data vendors: "
    "which vendors cover a data type (HCP, HCO, Claims, Patient, Clinical Trial, Publication, "
    "Social Media, Rx) in a country/region or therapeutic area, coverage counts, data elements, "
    "contracts and renewals. Backed by governed Delta tables and metric views, so answers are "
    "deterministic and complete across all vendors. Contract cost and contact PII are "
    "column-masked for users outside lumora_finance."
)
INSTRUCTIONS = (
    "You are Lumora Clinical Research's third-party data (3PD) vendor marketplace assistant. "
    "Answer from the governed vendor-catalog objects using SQL. Guidelines:\n"
    "- For 'which vendors offer/cover <data type> in <region>' questions, filter on data type and "
    "region and return EVERY matching vendor (never rank-and-cut or omit vendors) with coverage counts. "
    "Prefer mv_vendor_coverage with MEASURE(`Total Coverage`), or vendor_coverage_enriched.\n"
    "- For counts, totals and KPIs prefer the metric views: mv_vendor_coverage (Total Coverage, Vendor "
    "Count, Product Count, Region Count) and mv_contract_spend (Total Annual Spend, Spend at Risk, "
    "Contract Count, Expiring Soon Contracts). Query measures with MEASURE(`<name>`) and GROUP BY ALL.\n"
    "- Data types: HCP, HCO, Claims, Patient, Clinical Trial, Publication, Social Media, Rx/Medication. "
    "Synonyms: physicians/doctors/healthcare professionals -> HCP; hospitals/organizations -> HCO; "
    "prescriptions -> Rx/Medication.\n"
    "- Contract status is Active, Expiring Soon (ends within ~120 days) or Expired.\n"
    "- Contract cost and contact email/phone are protected by Unity Catalog column masks. If cost or "
    "spend comes back NULL, say the value is masked for the user's role (finance-only) — do not say "
    "the data is missing and never estimate it.\n"
    "- State the filters you applied and summarize in business language. If nothing matches, say so."
)
TABLES = [f"{FQ}.{t}" for t in [
    "mv_vendor_coverage", "mv_contract_spend", "vendor_coverage_enriched", "vendors", "coverage",
    "data_products", "data_elements", "contracts", "vendor_contacts"]]
EXAMPLES = [
    ("Which vendors cover HCP data in Egypt?",
     f"SELECT `Vendor`, MEASURE(`Total Coverage`) AS hcp_coverage FROM {FQ}.mv_vendor_coverage "
     f"WHERE `Data Type` = 'HCP' AND `Region` = 'Egypt' GROUP BY ALL ORDER BY hcp_coverage DESC"),
    ("Which vendors offer Claims data, and in which regions?",
     f"SELECT v.vendor_name, collect_set(c.geographic_region) AS regions FROM {FQ}.coverage c "
     f"JOIN {FQ}.vendors v USING (vendor_id) WHERE c.data_type = 'Claims' GROUP BY v.vendor_name ORDER BY v.vendor_name"),
    ("Which vendor contracts are expiring soon, and what do they cost?",
     f"SELECT v.vendor_name, ct.contract_end, ct.annual_cost_usd FROM {FQ}.contracts ct "
     f"JOIN {FQ}.vendors v USING (vendor_id) WHERE ct.status = 'Expiring Soon' ORDER BY ct.contract_end"),
    ("How many vendors cover each region for HCP data?",
     f"SELECT `Region`, MEASURE(`Vendor Count`) AS vendors FROM {FQ}.mv_vendor_coverage "
     f"WHERE `Data Type` = 'HCP' GROUP BY ALL ORDER BY vendors DESC"),
    ("What is our spend at risk on contracts expiring soon?",
     f"SELECT `Vendor`, `Contract End Date`, MEASURE(`Spend at Risk`) AS spend_at_risk FROM {FQ}.mv_contract_spend "
     f"WHERE `Contract Status` = 'Expiring Soon' GROUP BY ALL"),
    ("Who is the technical contact at AfriHealth?",
     f"SELECT vendor_name, contact_name, title, email, phone FROM {FQ}.vendor_contacts "
     f"WHERE contact_type = 'Technical' AND vendor_name ILIKE '%AfriHealth%'"),
]
BENCHMARKS = [
    ("Which vendors provide HCP data in Egypt?",
     f"SELECT DISTINCT v.vendor_name FROM {FQ}.coverage c JOIN {FQ}.vendors v USING (vendor_id) "
     f"WHERE c.data_type = 'HCP' AND c.geographic_region = 'Egypt'"),
    ("Who can give me claims data in Brazil and Argentina?",
     f"SELECT DISTINCT v.vendor_name, c.geographic_region FROM {FQ}.coverage c JOIN {FQ}.vendors v USING (vendor_id) "
     f"WHERE c.data_type = 'Claims' AND c.geographic_region IN ('Brazil','Argentina')"),
    ("List all vendors offering clinical trial data.",
     f"SELECT DISTINCT v.vendor_name FROM {FQ}.coverage c JOIN {FQ}.vendors v USING (vendor_id) "
     f"WHERE c.data_type = 'Clinical Trial'"),
    ("How many contracts are expiring soon?",
     f"SELECT MEASURE(`Expiring Soon Contracts`) FROM {FQ}.mv_contract_spend"),
]


def _id(seed: str) -> str:
    return uuid.uuid5(uuid.NAMESPACE_URL, seed).hex


def serialized_space() -> dict:
    return {
        "version": 2,
        "instructions": {
            "text_instructions": [{"id": _id("instructions"), "content": [INSTRUCTIONS]}],
            "example_question_sqls": sorted(
                [{"id": _id(q), "question": [q], "sql": [s]} for q, s in EXAMPLES], key=lambda x: x["id"]),
        },
        "data_sources": {"tables": sorted([{"identifier": t} for t in TABLES], key=lambda x: x["identifier"])},
        "benchmarks": {"questions": sorted(
            [{"id": _id("bm:" + q), "question": [q], "answer": [{"format": "SQL", "content": [s]}]}
             for q, s in BENCHMARKS], key=lambda x: x["id"])},
    }


def api(method, path, body):
    out = subprocess.run(["databricks", "api", method, path, "-p", PROFILE, "--json", json.dumps(body)],
                         capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit(f"{method} {path} failed: {out.stderr or out.stdout}")
    return json.loads(out.stdout or "{}")


if __name__ == "__main__":
    space = serialized_space()
    if "--dry-run" in sys.argv:
        print(json.dumps(space, indent=2)); sys.exit(0)
    body = {"title": TITLE, "description": DESCRIPTION, "warehouse_id": WAREHOUSE_ID,
            "serialized_space": json.dumps(space)}
    if "--update" in sys.argv:
        sid = open(ID_FILE).read().strip()
        api("patch", f"/api/2.0/genie/spaces/{sid}", body)
        print("updated space_id:", sid)
    else:
        sid = api("post", "/api/2.0/genie/spaces", body)["space_id"]
        open(ID_FILE, "w").write(sid + "\n")
        print("space_id:", sid)
