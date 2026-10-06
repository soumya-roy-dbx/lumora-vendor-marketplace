"""
Lumora Vendor Marketplace — Multi-Agent Supervisor (code-first, Mosaic AI Agent Framework).

A LangGraph supervisor routes each question to the right worker:
  • genie — structured NL->SQL over the governed vendor Delta tables
            (which vendors cover HCP in Egypt, contracts expiring, counts...)
  • docs  — semantic retrieval over unstructured vendor documents
            (summarize a contract, how HCP counts are derived, refresh cadence...)
The supervisor decides who answers (can consult both), then a final node
synthesizes a business-friendly answer. Exposed as an MLflow ChatAgent so it
logs, registers to UC, and deploys to a serving endpoint unchanged.

State is a local TypedDict (with an append reducer) rather than
mlflow.langchain.chat_agent_langgraph.ChatAgentState, to avoid that helper's
version gate on the serverless runtime.
"""

import os
from typing import Annotated, Any, Optional, TypedDict

import mlflow
from databricks_langchain import ChatDatabricks, VectorSearchRetrieverTool
from databricks_langchain.genie import GenieAgent
from langgraph.graph import END, StateGraph
from mlflow.pyfunc import ChatAgent
from mlflow.types.agent import ChatAgentMessage, ChatAgentResponse, ChatContext

mlflow.langchain.autolog()

# ---------------------------------------------------------------------------
# Config (overridable via env at deploy time)
# ---------------------------------------------------------------------------
# The supervisor's INTERNAL reasoning calls use the model directly. Guardrails
# belong at the user-input boundary (a gatewayed endpoint the app calls for the
# user's turn, or Agent Bricks' input guardrails) — NOT wrapped around every
# internal call, where a strict safety classifier can false-positive on benign
# vendor data and break legitimate runs.
# This file runs INSIDE the serving container, so it can't %run 00_config.
# The values below are baked in when notebook 05 logs the agent. Either edit
# the three defaults here to match your workspace, OR (recommended) rely on
# notebook 05 setting these env vars from 00_config before logging.
LLM_ENDPOINT = os.environ.get("LLM_ENDPOINT", "databricks-claude-sonnet-4-5")
GENIE_SPACE_ID = os.environ.get("GENIE_SPACE_ID", "PUT_YOUR_GENIE_SPACE_ID_HERE")
VS_INDEX = os.environ.get(
    "VS_INDEX", "main.lumora_vendor_marketplace.vendor_docs_index"
)

llm = ChatDatabricks(endpoint=LLM_ENDPOINT)


# ---------------------------------------------------------------------------
# Graph state
# ---------------------------------------------------------------------------
def _append(left, right):
    return (left or []) + (right or [])


class AgentState(TypedDict, total=False):
    messages: Annotated[list, _append]
    next: str
    step: int


def _clean(messages: list) -> list:
    """Reduce to role/content dicts for LLM calls (drop 'name' etc.)."""
    out = []
    for m in messages:
        if isinstance(m, dict):
            out.append({"role": m.get("role", "user"), "content": m.get("content", "")})
        else:
            out.append({"role": getattr(m, "role", "user"), "content": getattr(m, "content", "")})
    return out


def _latest_user_text(messages: list) -> str:
    for m in reversed(messages):
        role = m.get("role") if isinstance(m, dict) else getattr(m, "role", None)
        if role == "user":
            return m.get("content") if isinstance(m, dict) else m.content
    last = messages[-1]
    return last.get("content") if isinstance(last, dict) else last.content


# ---------------------------------------------------------------------------
# Worker 1 — Genie (structured NL->SQL)
# ---------------------------------------------------------------------------
genie_agent = GenieAgent(
    genie_space_id=GENIE_SPACE_ID,
    genie_agent_name="Genie",
    description="Structured vendor questions answered via SQL over governed Delta tables.",
)


def genie_worker(state: AgentState):
    result = genie_agent.invoke({"messages": _clean(state["messages"])})
    last = result["messages"][-1]
    content = last.content if hasattr(last, "content") else last["content"]
    return {"messages": [{"role": "assistant", "content": content, "name": "genie"}]}


# ---------------------------------------------------------------------------
# Worker 2 — Docs (semantic retrieval over unstructured vendor documents)
# ---------------------------------------------------------------------------
doc_retriever = VectorSearchRetrieverTool(
    index_name=VS_INDEX,
    num_results=4,
    tool_name="vendor_document_search",
    tool_description="Searches unstructured vendor documents (contracts, dictionaries, methodology, onboarding).",
)

DOCS_SYSTEM = (
    "Answer using ONLY the retrieved document excerpts below. Cite the vendor and "
    "document type. If the excerpts don't cover it, say so."
)


def docs_worker(state: AgentState):
    query = _latest_user_text(state["messages"])
    docs = doc_retriever.invoke(query)
    if hasattr(docs, "content"):
        context = docs.content
    elif isinstance(docs, list):
        context = "\n\n---\n\n".join(
            (d.page_content if hasattr(d, "page_content") else str(d)) for d in docs
        )
    else:
        context = str(docs)
    if not (context and context.strip()):
        return {"messages": [{"role": "assistant", "content": "No matching vendor documents were found.", "name": "docs"}]}
    prompt = [
        {"role": "system", "content": DOCS_SYSTEM},
        {"role": "user", "content": f'Retrieved excerpts:\n"""\n{context}\n"""\n\nQuestion: {query}'},
    ]
    answer = llm.invoke(prompt).content
    if not (answer and answer.strip()):
        # never return empty — fall back to the grounded excerpts
        answer = "Relevant document excerpts:\n\n" + context[:1500]
    return {"messages": [{"role": "assistant", "content": answer, "name": "docs"}]}


# ---------------------------------------------------------------------------
# Supervisor + final synthesis
# ---------------------------------------------------------------------------
OPTIONS = ["genie", "docs", "FINISH"]
MAX_STEPS = 6

SUPERVISOR_SYSTEM = (
    "You are the supervisor of the Lumora Vendor Data Marketplace assistant. "
    "Route the request to exactly one worker at a time:\n"
    "- 'genie' for STRUCTURED questions from tables (which/list/how many/compare "
    "vendors by data type, region, coverage count, or contract).\n"
    "- 'docs' for UNSTRUCTURED questions needing document text (contract terms, how "
    "counts are derived, refresh cadence, field definitions, access).\n"
    "A question may need both — call workers one after another. When the worker "
    "answers already in the conversation fully address the user, respond FINISH."
)


def supervisor_node(state: AgentState):
    step = state.get("step", 0)
    if step >= MAX_STEPS:
        return {"next": "FINISH", "step": step}
    router = llm.with_structured_output(
        {
            "title": "route",
            "type": "object",
            "properties": {"next": {"type": "string", "enum": OPTIONS}},
            "required": ["next"],
        }
    )
    decision = router.invoke([{"role": "system", "content": SUPERVISOR_SYSTEM}] + _clean(state["messages"]))
    return {"next": decision["next"], "step": step + 1}


# Combining worker outputs is the ONLY place synthesis happens, and it must never
# introduce data. A single worker's answer is already grounded (Genie = SQL over the
# tables; docs = retrieved excerpts), so we pass it through VERBATIM — re-generating it
# with an LLM is what let fabricated vendors slip in. Only when two workers both
# contributed do we combine, under a strict no-invention instruction.
COMBINE_SYSTEM = (
    "Combine the worker answers below into one response for a business user. Use ONLY "
    "the vendor names, numbers, and facts that appear in them — do NOT add, infer, or "
    "invent any vendor or value not present, and do not drop any vendor that appears. "
    "Keep it concise."
)


def final_node(state: AgentState):
    workers = [m for m in state["messages"] if isinstance(m, dict) and m.get("name") in ("genie", "docs")]
    if not workers:
        return {"messages": [{"role": "assistant", "content": "I couldn't find an answer to that.", "name": "assistant"}]}
    if len(workers) == 1:
        # grounded single-worker answer → return as-is (prevents synthesis hallucination)
        return {"messages": [{"role": "assistant", "content": workers[-1]["content"], "name": "assistant"}]}
    parts = "\n\n".join(f"[{m.get('name')}]\n{m.get('content')}" for m in workers)
    answer = llm.invoke([{"role": "system", "content": COMBINE_SYSTEM}, {"role": "user", "content": parts}]).content
    return {"messages": [{"role": "assistant", "content": answer, "name": "assistant"}]}


def build_graph():
    g = StateGraph(AgentState)
    g.add_node("supervisor", supervisor_node)
    g.add_node("genie", genie_worker)
    g.add_node("docs", docs_worker)
    g.add_node("final", final_node)
    g.set_entry_point("supervisor")
    g.add_conditional_edges(
        "supervisor", lambda s: s["next"],
        {"genie": "genie", "docs": "docs", "FINISH": "final"},
    )
    g.add_edge("genie", "supervisor")
    g.add_edge("docs", "supervisor")
    g.add_edge("final", END)
    return g.compile()


# ---------------------------------------------------------------------------
# MLflow ChatAgent wrapper
# ---------------------------------------------------------------------------
class SupervisorChatAgent(ChatAgent):
    def __init__(self):
        self.graph = build_graph()

    def predict(
        self,
        messages: list[ChatAgentMessage],
        context: Optional[ChatContext] = None,
        custom_inputs: Optional[dict[str, Any]] = None,
    ) -> ChatAgentResponse:
        import uuid

        def _to_dict(m):
            if hasattr(m, "model_dump_compat"):
                return m.model_dump_compat(exclude_none=True)
            if hasattr(m, "model_dump"):
                return m.model_dump(exclude_none=True)
            return dict(m)

        request = {"messages": [_to_dict(m) for m in messages]}
        out = []
        for chunk in self.graph.stream(request, stream_mode="updates"):
            # each chunk is {node_name: {state update}}
            for node_out in chunk.values():
                if not isinstance(node_out, dict):
                    continue
                for msg in node_out.get("messages", []):
                    if isinstance(msg, dict):
                        msg = {**msg, "id": msg.get("id") or uuid.uuid4().hex}
                        out.append(ChatAgentMessage(**msg))
                    else:
                        out.append(msg)
        return ChatAgentResponse(messages=out)


from mlflow.models import set_model  # noqa: E402

AGENT = SupervisorChatAgent()
set_model(AGENT)
