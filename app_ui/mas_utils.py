"""Call the Agent Bricks Multi-Agent Supervisor endpoint (Responses API).

The MAS serving endpoint expects the Responses format ({"input": [...]}) and
returns a response object whose text lives under `output`. We POST to the
endpoint's invocations URL as the app service principal and extract the text
robustly across response shapes.
"""

import json
import os
import re

from databricks.sdk import WorkspaceClient

MAS_ENDPOINT = os.environ.get("MAS_ENDPOINT", "REPLACE_WITH_YOUR_MAS_ENDPOINT")

# The MAS emits internal routing/handoff markers like
# <name>genie-01f1...</name> / <name>LumoraVendorMarketplaceSupervisor</name>.
# Strip them so the answer reads clean.
_NAME_TAG = re.compile(r"\s*<name>.*?</name>\s*", re.DOTALL)


def _strip_tool_tables(text: str) -> str:
    """Drop the compact table dump a Genie sub-agent echoes into the stream
    (starts with "||col|col|" then one "|i|...|" row per line). The supervisor's
    own prose answer that follows is kept."""
    out, lines, i = [], text.split("\n"), 0
    while i < len(lines):
        line = lines[i]
        k = line.find("||")
        if k == -1:
            out.append(line); i += 1; continue
        head, j = line[:k], i
        while j + 1 < len(lines) and lines[j + 1].lstrip().startswith("|"):
            j += 1
        last = lines[j] if j > i else line[k:]
        tail = last[last.rfind("|") + 1:]
        out.append((head + " " + tail).strip())
        i = j + 1
    return "\n".join(out)


def _clean(text: str) -> str:
    text = _NAME_TAG.sub(" ", text)
    text = _strip_tool_tables(text)
    # collapse whitespace left behind, but keep paragraph/line breaks
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _extract_text(payload: dict) -> str:
    """Pull assistant text out of a Responses-API (or chat) style payload."""
    # Responses API: output -> [ {content: [{type:'output_text', text:...}]} ]
    parts = []
    for item in payload.get("output", []) or []:
        for c in item.get("content", []) or []:
            if isinstance(c, dict) and c.get("text"):
                parts.append(c["text"])
    if parts:
        return "\n".join(parts)
    # Some builds expose a flat convenience field
    if payload.get("output_text"):
        return payload["output_text"]
    # Fallback: chat.completions shape
    try:
        return payload["choices"][0]["message"]["content"]
    except Exception:  # noqa: BLE001
        return ""


def ask(question: str, history: list | None = None) -> str:
    """Send a question to the MAS endpoint and return the synthesized answer."""
    w = WorkspaceClient()
    msgs = (history or []) + [{"role": "user", "content": question}]
    resp = w.api_client.do(
        "POST",
        f"/serving-endpoints/{MAS_ENDPOINT}/invocations",
        body={"input": msgs},
    )
    if isinstance(resp, (bytes, str)):
        try:
            resp = json.loads(resp)
        except Exception:  # noqa: BLE001
            return str(resp)
    text = _clean(_extract_text(resp))
    return text or "I couldn't produce an answer for that. Please try rephrasing."
