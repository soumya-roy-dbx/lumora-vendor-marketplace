#!/usr/bin/env python3
"""Export REAL job-run output (every notebook cell + its output) as Markdown.

For each bundle job, takes the latest run (or a given run id), exports every
notebook task with `databricks jobs export-run`, decodes the embedded notebook
model and writes evidence/runs/<job>/<task>.md: cell source + the output the
cell actually produced (stdout, tables, errors). Pipeline tasks are recorded
with their update id and state (see export_pipelines.py for event logs).

  python3 evidence/tools/export_job_runs.py <job_key>=<job_id>[:<run_id>] ...
"""
import base64
import html
import json
import os
import re
import subprocess
import sys
import urllib.parse
from datetime import datetime, timezone

PROFILE = os.environ.get("DATABRICKS_PROFILE", "DEFAULT")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "runs")
MAX_ROWS = 40


def cli(*args):
    out = subprocess.run(["databricks", *args, "-p", PROFILE, "-o", "json"], capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(out.stderr or out.stdout)
    return json.loads(out.stdout)


def ts(ms):
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC") if ms else "-"


def md_table(item):
    schema = item.get("schema") or []
    cols = [c.get("name", f"c{i}") for i, c in enumerate(schema)] or [f"c{i}" for i in range(len((item.get("data") or [[]])[0]))]
    rows = item.get("data") or []
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for r in rows[:MAX_ROWS]:
        lines.append("| " + " | ".join("" if v is None else str(v).replace("|", "\\|").replace("\n", " ")[:120] for v in r) + " |")
    if len(rows) > MAX_ROWS:
        lines.append(f"\n_… {len(rows) - MAX_ROWS} more rows (truncated)_")
    return "\n".join(lines)


def render_result(r):
    if not r:
        return ""
    items = r.get("data") if r.get("type") == "listResults" else [r]
    parts = []
    for it in items or []:
        t, data = it.get("type"), it.get("data")
        if t == "table":
            parts.append(md_table(it))
        elif t in ("ansi", "text"):
            parts.append("```text\n" + str(data).rstrip()[:6000] + "\n```")
        elif t == "html":
            txt = re.sub(r"<[^>]+>", " ", str(data)); txt = html.unescape(re.sub(r"\s+", " ", txt)).strip()
            if txt:
                parts.append("```text\n" + txt[:3000] + "\n```")
        elif t == "error" or it.get("errorSummary"):
            parts.append("```text\nERROR: " + str(it.get("errorSummary") or data)[:3000] + "\n```")
    if r.get("type") == "error" or r.get("errorSummary"):
        parts.append("```text\nERROR: " + re.sub(r"\x1b\[[0-9;]*m", "", str(r.get("errorSummary") or r.get("data")))[:3000] + "\n```")
    return "\n\n".join(p for p in parts if p)


def export_task(job_key, task, run_url):
    d = cli("jobs", "export-run", str(task["run_id"]), "--views-to-export", "CODE")
    content = d["views"][0]["content"]
    m = re.search(r"__DATABRICKS_NOTEBOOK_MODEL = '([^']+)'", content)
    model = json.loads(urllib.parse.unquote(base64.b64decode(m.group(1)).decode()))
    st = task["state"]
    lines = [f"# {job_key} / {task['task_key']}",
             "",
             f"- **Notebook:** `{task['notebook_task']['notebook_path'].split('/files/')[-1]}`",
             f"- **Task run id:** `{task['run_id']}` · **Result:** `{st.get('result_state')}`",
             f"- **Started:** {ts(task.get('start_time'))} · **Ended:** {ts(task.get('end_time'))}",
             f"- **Job run:** {run_url}",
             "",
             "_Exported from the job run with `databricks jobs export-run` — cell source followed by the output the cell produced in that run._",
             ""]
    for i, c in enumerate(model["commands"], 1):
        src = (c.get("command") or "").rstrip()
        if not src.strip():
            continue
        lines += [f"## Cell {i}", "", "```python", src, "```", ""]
        out = render_result(c.get("results"))
        if out:
            lines += ["**Output:**", "", out, ""]
    os.makedirs(os.path.join(OUT, job_key), exist_ok=True)
    path = os.path.join(OUT, job_key, f"{task['task_key']}.md")
    open(path, "w").write("\n".join(lines))
    return path


def main():
    for arg in sys.argv[1:]:
        job_key, rest = arg.split("=")
        job_id, _, run_id = rest.partition(":")
        if not run_id:
            run_id = str(cli("jobs", "list-runs", "--job-id", job_id, "--limit", "1")[0]["run_id"])
        run = cli("jobs", "get-run", run_id)
        summary = [f"# Job run: {run['run_name']}", "",
                   f"- **Job id:** `{job_id}` · **Run id:** `{run_id}`",
                   f"- **State:** `{run['state'].get('life_cycle_state')}` / `{run['state'].get('result_state')}`",
                   f"- **Started:** {ts(run.get('start_time'))} · **Ended:** {ts(run.get('end_time'))}",
                   f"- **Run page:** {run.get('run_page_url')}", "",
                   "| Task | Type | Result | Started | Ended | Evidence |", "|---|---|---|---|---|---|"]
        for t in sorted(run["tasks"], key=lambda t: t.get("start_time") or 0):
            kind = "notebook" if "notebook_task" in t else ("pipeline" if "pipeline_task" in t else "other")
            ev = ""
            if kind == "notebook" and t["state"].get("result_state"):
                try:
                    ev = f"[{t['task_key']}.md]({t['task_key']}.md)"; export_task(job_key, t, run.get("run_page_url"))
                except Exception as e:  # keep going; record why
                    ev = f"export failed: {str(e)[:80]}"
            elif kind == "pipeline":
                ev = f"pipeline `{t['pipeline_task']['pipeline_id']}` — see ../../pipelines/"
            summary.append(f"| {t['task_key']} | {kind} | {t['state'].get('result_state')} | {ts(t.get('start_time'))} | {ts(t.get('end_time'))} | {ev} |")
        os.makedirs(os.path.join(OUT, job_key), exist_ok=True)
        open(os.path.join(OUT, job_key, "README.md"), "w").write("\n".join(summary) + "\n")
        print("exported", job_key, run_id)


if __name__ == "__main__":
    main()
