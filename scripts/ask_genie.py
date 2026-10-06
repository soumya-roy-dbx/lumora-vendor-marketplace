"""Ask a Genie space a question via the Conversation API and print SQL + result.
Usage: python3 scripts/ask_genie.py <space_id> "question" """
import json, os, subprocess, sys, time
PROFILE = os.environ.get("DATABRICKS_PROFILE", "DEFAULT")

def api(method, path, body=None):
    cmd = ["databricks", "api", method, path, "-p", PROFILE] + (["--json", json.dumps(body)] if body else [])
    return json.loads(subprocess.run(cmd, capture_output=True, text=True).stdout or "{}")

sid, q = sys.argv[1], sys.argv[2]
m = api("post", f"/api/2.0/genie/spaces/{sid}/start-conversation", {"content": q})
cid, mid = m["conversation_id"], m["message_id"]
for _ in range(60):
    msg = api("get", f"/api/2.0/genie/spaces/{sid}/conversations/{cid}/messages/{mid}")
    if msg.get("status") in ("COMPLETED", "FAILED", "CANCELLED"): break
    time.sleep(3)
print("STATUS:", msg.get("status"))
for a in msg.get("attachments", []) or []:
    if a.get("text"): print("TEXT:", a["text"].get("content", "")[:500])
    if a.get("query"):
        print("SQL:", a["query"].get("query"))
        r = api("get", f"/api/2.0/genie/spaces/{sid}/conversations/{cid}/messages/{mid}/attachments/{a['attachment_id']}/query-result")
        sr = r.get("statement_response", {})
        print("ROWS:", (sr.get("result") or {}).get("data_array"))
