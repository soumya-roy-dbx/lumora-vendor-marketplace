#!/usr/bin/env python3
"""Create the Agent Bricks layer and wire permissions for the app.

  1. Knowledge Assistant over the vendor-documents Volume (72 synthetic docs)
  2. Supervisor Agent with two tools: the Genie space (structured facts) and the
     Knowledge Assistant (documents)
  3. Grants for the app's service principal — the supervisor runs sub-agents ON
     BEHALF OF the caller, so the app SP needs every downstream resource:
     supervisor + KA endpoints (CAN_QUERY), Genie space (CAN_RUN), UC read access.
     (The SQL warehouse and Lakebase grants come from the app's bundle resources.)

Idempotent: re-uses agents that already exist by display name.
Writes agent_bricks/agents.json with the ids and endpoint names.

  python3 agent_bricks/create_agents.py
"""
import json
import os
import subprocess
import sys
import time

PROFILE = os.environ.get("DATABRICKS_PROFILE", "DEFAULT")
CATALOG = os.environ.get("CATALOG", "aws_serverless_ws_sr_catalog")
SCHEMA = os.environ.get("SCHEMA", "lumora_vendor_marketplace")
WAREHOUSE_ID = os.environ.get("WAREHOUSE_ID", "2cc7c1b1bd1873ce")
APP_NAME = os.environ.get("APP_NAME", "lumora-data-marketplace")
HERE = os.path.dirname(os.path.abspath(__file__))
GENIE_SPACE_ID = open(os.path.join(HERE, "..", "genie", "space_id.txt")).read().strip()
DOCS_PATH = f"/Volumes/{CATALOG}/{SCHEMA}/vendor_documents/"

KA_NAME = "Lumora Vendor Docs KA"
SUP_NAME = "LumoraVendorMarketplaceSupervisor"


def cli(*args, body=None, ok_fail=False):
    cmd = ["databricks", *args, "-p", PROFILE, "-o", "json"]
    if body is not None:
        cmd += ["--json", json.dumps(body)]
    out = subprocess.run(cmd, capture_output=True, text=True)
    if out.returncode != 0:
        if ok_fail:
            return None
        sys.exit(f"FAILED: {' '.join(args)}\n{out.stderr or out.stdout}")
    return json.loads(out.stdout) if out.stdout.strip() else {}


def sql(stmt):
    r = cli("api", "post", "/api/2.0/sql/statements",
            body={"warehouse_id": WAREHOUSE_ID, "statement": stmt, "wait_timeout": "50s"})
    print(f"  SQL {r.get('status', {}).get('state')}: {stmt}")


# ---- 1. Knowledge Assistant ------------------------------------------------
kas = cli("knowledge-assistants", "list-knowledge-assistants") or []
ka = next((k for k in kas if k.get("display_name") == KA_NAME), None)
if not ka:
    ka = cli("knowledge-assistants", "create-knowledge-assistant", KA_NAME,
             "Answers questions from Lumora's vendor documents: contract summaries, data dictionaries, "
             "sourcing methodology and onboarding guides.",
             "--instructions", "Answer only from the vendor documents and cite the document. If the documents "
                               "do not contain the answer, say so. Do not answer table-style counting questions.")
if not cli("knowledge-assistants", "list-knowledge-sources", ka["name"]):
    cli("knowledge-assistants", "create-knowledge-source", ka["name"],
        body={"display_name": "Lumora_Vendor_Docs",
              "description": "Per-vendor contract summaries, data dictionaries, sourcing methodology, and onboarding guides.",
              "source_type": "files", "files": {"path": DOCS_PATH}})
print("KA:", ka["id"], ka.get("endpoint_name"))

# ---- 2. Supervisor Agent ---------------------------------------------------
sups = cli("supervisor-agents", "list-supervisor-agents") or []
sup = next((s for s in sups if s.get("display_name") == SUP_NAME), None)
if not sup:
    sup = cli("supervisor-agents", "create-supervisor-agent", SUP_NAME,
              "--description", "Lumora vendor data marketplace assistant: routes structured vendor/coverage/"
                               "contract questions to Genie and document questions to the Knowledge Assistant.",
              "--instructions", "Route every question to exactly the right tool. Structured questions (which/list/"
                                "how many/compare vendors by data type, region, coverage count, contract status/"
                                "cost/expiry) go to the Genie tool and must list every vendor it returns. Document "
                                "questions (contract terms, methodology, refresh cadence, field definitions, "
                                "onboarding) go to the Knowledge Assistant. Never invent vendors or numbers; if a "
                                "value is masked, say it is masked for the user's role.")
if not cli("supervisor-agents", "list-tools", sup["name"]):
    cli("supervisor-agents", "create-tool", sup["name"], f"genie-{GENIE_SPACE_ID}",
        body={"tool_type": "genie_space",
              "description": "Structured questions from tables — which/list/how many/compare vendors by data type, "
                             "region, coverage count, or contract status/cost/expiry.",
              "genie_space": {"id": GENIE_SPACE_ID}})
    cli("supervisor-agents", "create-tool", sup["name"], f"ka-{ka['id']}",
        body={"tool_type": "knowledge_assistant",
              "description": "Document questions — contract terms/SLAs, how a vendor derives its counts, refresh "
                             "cadence, field definitions, onboarding/access.",
              "knowledge_assistant": {"knowledge_assistant_id": ka["id"]}})
print("Supervisor:", sup["supervisor_agent_id"], sup.get("endpoint_name"))

# ---- wait for both serving endpoints to be READY ---------------------------
def endpoint_name(kind, obj):
    for _ in range(90):
        fresh = (cli("knowledge-assistants", "get-knowledge-assistant", obj["name"]) if kind == "ka"
                 else cli("supervisor-agents", "get-supervisor-agent", obj["name"]))
        ep = fresh.get("endpoint_name")
        if ep:
            st = cli("serving-endpoints", "get", ep, ok_fail=True) or {}
            ready = st.get("state", {}).get("ready")
            print(f"  {kind} endpoint {ep}: {ready}")
            if ready == "READY":
                return ep
        time.sleep(20)
    sys.exit(f"{kind} endpoint not ready")

ka_ep = endpoint_name("ka", ka)
sup_ep = endpoint_name("sup", sup)

# ---- 3. Grants for the app service principal -------------------------------
app = cli("apps", "get", APP_NAME)
sp = app["service_principal_client_id"]
print("App SP:", sp)
for ep in (ka_ep, sup_ep):
    ep_id = cli("serving-endpoints", "get", ep)["id"]
    cli("api", "patch", f"/api/2.0/permissions/serving-endpoints/{ep_id}",
        body={"access_control_list": [{"service_principal_name": sp, "permission_level": "CAN_QUERY"}]})
    print(f"  CAN_QUERY on {ep}")
cli("api", "patch", f"/api/2.0/permissions/genie/{GENIE_SPACE_ID}",
    body={"access_control_list": [{"service_principal_name": sp, "permission_level": "CAN_RUN"}]})
print("  CAN_RUN on Genie space")
sql(f"GRANT USE CATALOG ON CATALOG {CATALOG} TO `{sp}`")
sql(f"GRANT USE SCHEMA, SELECT, READ VOLUME ON SCHEMA {CATALOG}.{SCHEMA} TO `{sp}`")
sql(f"GRANT EXECUTE ON SCHEMA {CATALOG}.{SCHEMA} TO `{sp}`")   # mask functions

out = {"knowledge_assistant_id": ka["id"], "ka_endpoint": ka_ep,
       "supervisor_agent_id": sup["supervisor_agent_id"], "supervisor_endpoint": sup_ep,
       "genie_space_id": GENIE_SPACE_ID, "app_service_principal": sp}
json.dump(out, open(os.path.join(HERE, "agents.json"), "w"), indent=2)
print(json.dumps(out, indent=2))
