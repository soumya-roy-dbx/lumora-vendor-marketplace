import os
import time
import html
import streamlit as st

from lakebase_utils import query
from mas_utils import ask

PG_SCHEMA = os.environ.get("PG_SCHEMA", "lumora")

st.set_page_config(page_title="Lumora Enterprise Data Marketplace", page_icon="🧬", layout="wide")

# ---------------------------------------------------------------------------
# Styling — Lumora look: light theme, teal accent, card grid
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    header[data-testid="stHeader"] { display:none !important; }
    #MainMenu, footer { visibility:hidden; }
    .block-container { padding-top: 0.8rem !important; }
    :root { --lumora:#0E7C86; }
    .dm-metrics { display:flex; background:#fff; border:1px solid #e5e7eb; border-radius:8px; margin-bottom:18px; overflow:hidden; }
    .dm-metric { flex:1; padding:13px 16px; border-right:1px solid #e5e7eb; }
    .dm-metric:last-child { border-right:none; }
    .dm-metric .l { font-size:0.72rem; color:#6b7280; font-weight:500; }
    .dm-metric .v { font-size:1.6rem; font-weight:800; color:#111827; line-height:1.1; }
    .dm-hero-badge { display:inline-block; background:#f0fdf4; border:1px solid #bbf7d0; border-radius:999px; padding:3px 12px; font-size:0.78rem; color:#166534; margin-bottom:14px; }
    .dm-hero-title { font-size:2.1rem; font-weight:800; color:#111827; line-height:1.15; margin-bottom:10px; }
    .dm-accent { color: var(--lumora); }
    .dm-hero-desc { color:#4b5563; font-size:1rem; max-width:640px; margin-bottom:8px; }
    .dm-card-title { font-size:1.05rem; font-weight:700; color:#111827; margin-bottom:6px; }
    .dm-row { display:flex; justify-content:space-between; font-size:0.85rem; margin:4px 0; gap:10px; }
    .dm-row .k { color:#6b7280; white-space:nowrap; }
    .dm-row .v { color:#111827; font-weight:500; text-align:right; }
    .dm-wordmark { font-size:1.15rem; font-weight:800; color:var(--lumora); letter-spacing:-0.02em; }
    .dm-lakebase { font-size:0.72rem; color:#166534; background:#f0fdf4; border:1px solid #bbf7d0; border-radius:6px; padding:4px 8px; display:inline-block; }
    </style>
    """,
    unsafe_allow_html=True,
)

if "view" not in st.session_state:
    st.session_state.view = "overview"
    st.session_state.messages = []


@st.cache_data(ttl=300, show_spinner=False)
def load_tiles():
    cols, rows = query(
        f'SELECT vendor_name, vendor_description, contract_expiry, contract_status, '
        f'no_of_products, hcp_count, geographical_coverage, data_types_offered '
        f'FROM {PG_SCHEMA}.vendor_tiles ORDER BY vendor_name'
    )
    return [dict(zip(cols, r)) for r in rows]


VERTICALS = [
    ("3pd", "3rd Party Data", "#4ade80", "External vendor datasets — HCPs, HCOs, claims, patient & clinical intelligence."),
    ("commercial", "Commercial", "#60a5fa", "Sales force activity, market share, and promotional analytics."),
    ("corporate", "Corporate", "#fbbf24", "Finance, HR, operations, and enterprise reference data."),
    ("clinical", "Clinical", "#f87171", "Trial data, safety signals, regulatory submissions, outcomes."),
]

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("<div class='dm-wordmark'>Lumora Clinical Research</div>", unsafe_allow_html=True)
    st.markdown("**Data Marketplace**")
    st.caption("Internal data marketplace")
    st.markdown("<span class='dm-lakebase'>⚡ Served by Lakebase</span>", unsafe_allow_html=True)
    st.divider()
    if st.button("◇  Overview", use_container_width=True, type="primary" if st.session_state.view == "overview" else "secondary"):
        st.session_state.view = "overview"; st.rerun()
    st.markdown("<p style='font-size:0.7rem;font-weight:700;letter-spacing:0.08em;color:#9ca3af;margin:12px 0 4px;'>VERTICALS</p>", unsafe_allow_html=True)
    for key, label, _c, _d in VERTICALS:
        if st.button(label, key=f"nav_{key}", use_container_width=True, type="primary" if st.session_state.view == key else "secondary"):
            st.session_state.view = key; st.rerun()
    st.divider()
    if st.button("🔄 Reload catalog", use_container_width=True):
        load_tiles.clear(); st.rerun()

# ---------------------------------------------------------------------------
# Metrics bar
# ---------------------------------------------------------------------------
try:
    tiles = load_tiles()
    tiles_error = None
    print(f"LAKEBASE_TILES_LOADED rows={len(tiles)} instance={os.environ.get('LAKEBASE_INSTANCE')} schema={PG_SCHEMA}", flush=True)
except Exception as exc:  # noqa: BLE001
    import traceback
    tiles, tiles_error = [], str(exc)
    print("LAKEBASE_TILE_LOAD_ERROR:", repr(exc), flush=True)
    traceback.print_exc()

metrics = [("3rd Party Vendors", len(tiles)), ("Data Verticals", 4), ("Live Sources", 1 if tiles else 0), ("Backend", "Lakebase")]
st.markdown(
    "<div class='dm-metrics'>" + "".join(
        f"<div class='dm-metric'><div class='l'>{l}</div><div class='v'>{v}</div></div>" for l, v in metrics
    ) + "</div>",
    unsafe_allow_html=True,
)

if tiles_error:
    st.warning(f"⚠️ Vendor tiles couldn't be loaded from Lakebase: {tiles_error}")

view = st.session_state.view

# ---------------------------------------------------------------------------
# Overview
# ---------------------------------------------------------------------------
if view == "overview":
    st.markdown("<div class='dm-hero-badge'>● Governed data, browsable in one place</div>", unsafe_allow_html=True)
    st.markdown("<div class='dm-hero-title'>Lumora' data, <span class='dm-accent'>browsable in one place.</span></div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='dm-hero-desc'>The internal catalog for governed datasets. Every vendor catalog has an "
        "owner, structured data elements, and coverage details — ask the AI assistant and get grounded, "
        "auditable answers. Tiles are served from Lakebase for millisecond loads.</div>",
        unsafe_allow_html=True,
    )
    st.write("")
    if st.button("Browse 3rd Party Data →", type="primary"):
        st.session_state.view = "3pd"; st.rerun()
    st.write(""); st.markdown("### Verticals")
    c = st.columns(2)
    for i, (key, label, color, desc) in enumerate(VERTICALS):
        with c[i % 2]:
            with st.container(border=True):
                st.markdown(f"<span style='color:{color}'>●</span> **{label}**", unsafe_allow_html=True)
                st.caption(desc)
                count = len(tiles) if key == "3pd" else 0
                st.markdown(f"**{count}** datasets")

# ---------------------------------------------------------------------------
# 3rd Party Data — AI assistant + vendor tiles
# ---------------------------------------------------------------------------
elif view == "3pd":
    st.markdown("## 3rd Party Data")
    st.caption("External vendor datasets — HCPs, HCOs, claims, patient data, and clinical intelligence.")
    st.divider()

    with st.container(border=True):
        st.markdown("### ✨ AI assistant — Interrogate the vendor catalog")
        st.caption("Answers come from a multi-agent supervisor: Genie for structured facts, a knowledge assistant for documents.")
        for m in st.session_state.messages:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])
        q = st.chat_input("e.g. \"Which vendors provide HCP data in Egypt?\"")
        if q:
            st.session_state.messages.append({"role": "user", "content": q})
            with st.chat_message("user"):
                st.markdown(q)
            with st.chat_message("assistant"):
                with st.spinner("Thinking…"):
                    try:
                        _t0 = time.time()
                        ans = ask(q, [m for m in st.session_state.messages[:-1]])
                        print(f"ASSISTANT_ANSWERED endpoint={os.environ.get('MAS_ENDPOINT')} secs={time.time() - _t0:.1f} "
                              f"q={q!r} answer={ans[:400]!r}", flush=True)
                    except Exception as exc:  # noqa: BLE001
                        print(f"ASSISTANT_ERROR endpoint={os.environ.get('MAS_ENDPOINT')} q={q!r} error={exc!r}", flush=True)
                        ans = f"⚠️ Couldn't reach the agent endpoint: {exc}"
                st.markdown(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})

    st.divider()
    if tiles_error:
        st.error(f"Couldn't load vendor tiles from Lakebase: {tiles_error}")
    elif not tiles:
        st.info("No vendor tiles found in Lakebase yet.")
    else:
        cols = st.columns(3)
        for i, t in enumerate(tiles):
            with cols[i % 3]:
                with st.container(border=True):
                    st.markdown(f"<div class='dm-card-title'>🏷️ {html.escape(t['vendor_name'] or '')}</div>", unsafe_allow_html=True)
                    desc = (t.get("vendor_description") or "Not Available")
                    st.markdown(
                        f"<div class='dm-row'><span class='k'>📝 Description</span><span class='v'>{html.escape((desc[:70] + '…') if len(desc) > 70 else desc)}</span></div>"
                        f"<div class='dm-row'><span class='k'>⏳ Contract Expires</span><span class='v'>{html.escape(str(t.get('contract_expiry') or 'N/A'))}</span></div>"
                        f"<div class='dm-row'><span class='k'>📦 Products</span><span class='v'>{t.get('no_of_products') or 'N/A'}</span></div>"
                        f"<div class='dm-row'><span class='k'>🌍 Coverage</span><span class='v'>{html.escape((t.get('geographical_coverage') or 'N/A')[:40])}</span></div>"
                        f"<div class='dm-row'><span class='k'>👥 HCPs</span><span class='v'>{t.get('hcp_count') or 'N/A'}</span></div>",
                        unsafe_allow_html=True,
                    )
                    with st.popover("View details", use_container_width=True):
                        st.markdown(f"**{t['vendor_name']}**")
                        st.caption(f"Data types: {t.get('data_types_offered') or 'N/A'}")
                        st.text(desc)
                        st.markdown(f"**Contract:** {t.get('contract_status') or 'N/A'} · expires {t.get('contract_expiry') or 'N/A'}")

# ---------------------------------------------------------------------------
# Placeholders
# ---------------------------------------------------------------------------
elif view in ("commercial", "corporate"):
    st.markdown(f"## {view.title()}")
    st.info(f"🔒 **{view.title()}** isn't connected yet — this vertical will be powered by Microsoft Purview.")
elif view == "clinical":
    st.markdown("## Clinical")
    st.info("Internal clinical data products — trial data, safety signals, and outcomes. Coming soon.")
