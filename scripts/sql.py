"""Tiny helper: run SQL on the demo warehouse via the Statement Execution API.
Usage: python3 scripts/sql.py "SELECT ..." """
import json, subprocess, sys

import os
WAREHOUSE = os.environ.get("WAREHOUSE_ID", "2cc7c1b1bd1873ce")
PROFILE = os.environ.get("DATABRICKS_PROFILE", "DEFAULT")

def run(stmt):
    body = json.dumps({"warehouse_id": WAREHOUSE, "statement": stmt, "wait_timeout": "50s"})
    out = subprocess.run(["databricks", "api", "post", "/api/2.0/sql/statements", "-p", PROFILE,
                          "--json", body], capture_output=True, text=True)
    r = json.loads(out.stdout or "{}")
    st = r.get("status", {})
    if st.get("state") != "SUCCEEDED":
        print(st.get("state"), st.get("error", {}).get("message", out.stderr)); return
    cols = [c["name"] for c in r["manifest"]["schema"]["columns"]]
    print(" | ".join(cols))
    for row in r.get("result", {}).get("data_array", []) or []:
        print(" | ".join("" if v is None else str(v) for v in row))

if __name__ == "__main__":
    for s in sys.argv[1:]:
        run(s)
