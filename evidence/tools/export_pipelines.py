#!/usr/bin/env python3
"""Export Lakeflow pipeline execution evidence as Markdown.

For each pipeline: recent updates (id, state, times) and, for the latest
completed update, every flow's output row counts and data-quality expectation
results (passed / failed records) taken from the pipeline event log.

  python3 evidence/tools/export_pipelines.py <name>=<pipeline_id> ...
"""
import json
import os
import subprocess
import sys

PROFILE = os.environ.get("DATABRICKS_PROFILE", "DEFAULT")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pipelines")


def api(path):
    out = subprocess.run(["databricks", "api", "get", path, "-p", PROFILE], capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(out.stderr or out.stdout)
    return json.loads(out.stdout)


def main():
    os.makedirs(OUT, exist_ok=True)
    for arg in sys.argv[1:]:
        name, pid = arg.split("=")
        p = api(f"/api/2.0/pipelines/{pid}")
        ups = api(f"/api/2.0/pipelines/{pid}/updates?max_results=10").get("updates", [])
        lines = [f"# Lakeflow pipeline: {p['name']}", "",
                 f"- **Pipeline id:** `{pid}` · **Serverless:** `{p['spec'].get('serverless')}` · "
                 f"**Target:** `{p['spec'].get('catalog')}.{p['spec'].get('schema')}`",
                 f"- **Source:** `{[l.get('notebook', {}).get('path', '').split('/files/')[-1] for l in p['spec'].get('libraries', [])]}`",
                 "", "## Recent updates", "", "| Update id | State | Full refresh | Created |", "|---|---|---|---|"]
        for u in ups:
            lines.append(f"| `{u['update_id']}` | {u.get('state')} | {u.get('full_refresh', False)} | {u.get('creation_time')} |")
        completed = [u for u in ups if u.get("state") == "COMPLETED"]
        events, token = [], None
        if completed:
            for _ in range(40):
                q = f"/api/2.0/pipelines/{pid}/events?max_results=250" + (f"&page_token={token}" if token else "")
                r = api(q); events += r.get("events", []); token = r.get("next_page_token")
                if not token:
                    break
        for done in completed:
            mine = [e for e in events if e.get("origin", {}).get("update_id") == done["update_id"]]
            flows = {}
            for e in mine:
                fp = e.get("details", {}).get("flow_progress")
                if not fp:
                    continue
                f = flows.setdefault(e["origin"].get("flow_name") or e["origin"].get("dataset_name"), {})
                f.setdefault("status", fp.get("status"))   # events are newest-first: keep the final status
                m = fp.get("metrics", {})
                if m.get("num_output_rows") is not None:
                    f.setdefault("rows", m["num_output_rows"])
                if fp.get("data_quality"):
                    dq = fp["data_quality"]
                    f.setdefault("dropped", dq.get("dropped_records"))
                    for x in dq.get("expectations", []) or []:
                        f.setdefault("exp", {}).setdefault(x["name"], (x.get("passed_records"), x.get("failed_records")))
            lines += ["", f"## Completed update `{done['update_id']}` — flows", "",
                      "| Flow / dataset | Final status | Output rows | Dropped by expectations |", "|---|---|---|---|"]
            for k, f in sorted(flows.items()):
                rows = f.get("rows", "0 — no new files (Auto Loader exactly-once)" if k.endswith(("bronze_vendor_catalog", "silver_vendor_catalog")) else "")
                lines.append(f"| `{k}` | {f.get('status')} | {rows} | {f.get('dropped', '')} |")
            lines += ["", f"### Data-quality expectations — update `{done['update_id']}` (from the event log)", "",
                      "| Dataset | Expectation | Passed records | Failed records |", "|---|---|---|---|"]
            for k, f in sorted(flows.items()):
                for en, (ps, fl) in sorted((f.get("exp") or {}).items()):
                    lines.append(f"| `{k}` | `{en}` | {ps} | {fl} |")
            errs = [e for e in mine if e.get("level") == "ERROR"]
            lines += ["", f"_Events in this update: {len(mine)} · ERROR-level events: {len(errs)}_"]
        open(os.path.join(OUT, f"{name}.md"), "w").write("\n".join(lines) + "\n")
        print("exported pipeline", name)


if __name__ == "__main__":
    main()
