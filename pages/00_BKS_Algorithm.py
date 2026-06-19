"""BKS Algorithm — Control Center
Pannello operativo principale: scoring prodotti, salute collezioni, coda priorità, gate pubblicazione.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

st.set_page_config(
    page_title="BKS ◎ Algorithm",
    page_icon="◎",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── BKS CSS ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&display=swap');
html, body, [data-testid="stAppViewContainer"] {
    background: #0A0A0A !important;
    color: #FAFAF7;
    font-family: 'DM Mono', monospace;
}
[data-testid="stHeader"] { background: #0A0A0A !important; }
[data-testid="stMetricValue"] {
    font-size: 2rem !important;
    font-family: 'DM Mono', monospace;
    color: #FAFAF7;
    font-weight: 300;
}
[data-testid="stMetricLabel"] {
    font-size: 0.65rem !important;
    letter-spacing: .12em;
    text-transform: uppercase;
    color: #888;
}
.bks-header {
    border-bottom: 1px solid #1E1E1E;
    padding: 1.5rem 0 1rem;
    margin-bottom: 2rem;
}
.bks-header h1 {
    font-size: 1.1rem;
    letter-spacing: .20em;
    text-transform: uppercase;
    color: #FAFAF7;
    font-weight: 300;
    margin: 0;
}
.bks-header span { color: #888; font-size: 0.75rem; letter-spacing: .08em; }
.coll-card {
    border-left: 3px solid var(--accent);
    background: rgba(255,255,255,0.03);
    border-radius: 4px;
    padding: 10px 14px;
    margin-bottom: 6px;
}
.coll-name {
    font-size: 0.65rem;
    letter-spacing: .14em;
    text-transform: uppercase;
    color: var(--accent);
    font-weight: 500;
}
.coll-score {
    font-size: 1.4rem;
    font-weight: 300;
    color: #FAFAF7;
}
.coll-meta { font-size: 0.65rem; color: #666; margin-top: 2px; }
.tier-P0 { background: #2a0808; color: #ff6b6b; border-radius:2px; padding:1px 6px; font-size:0.65rem; letter-spacing:.08em; }
.tier-P1 { background: #2a1a00; color: #ffa94d; border-radius:2px; padding:1px 6px; font-size:0.65rem; letter-spacing:.08em; }
.tier-P2 { background: #1a1a0a; color: #ffe066; border-radius:2px; padding:1px 6px; font-size:0.65rem; letter-spacing:.08em; }
.tier-P3 { background: #0a1a0a; color: #69db7c; border-radius:2px; padding:1px 6px; font-size:0.65rem; letter-spacing:.08em; }
.gate-pass { color: #69db7c; font-size: 0.85rem; letter-spacing:.06em; }
.gate-fail { color: #ff6b6b; font-size: 0.85rem; letter-spacing:.06em; }
.issue-tag {
    display:inline-block;
    background:#1a1010;
    color:#ff8787;
    border-radius:2px;
    padding:1px 5px;
    font-size:0.60rem;
    margin:1px;
    letter-spacing:.05em;
}
[data-testid="stDataFrame"] table { font-size: 0.75rem !important; }
[data-testid="stButton"] > button {
    background: #1A1A1A;
    color: #FAFAF7;
    border: 1px solid #2E2E2E;
    border-radius: 2px;
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: .10em;
    text-transform: uppercase;
    padding: 6px 16px;
}
[data-testid="stButton"] > button:hover { border-color: #C9B79C; color: #C9B79C; }
[data-testid="stTextInput"] input {
    background: #111;
    border: 1px solid #2E2E2E;
    color: #FAFAF7;
    font-family: 'DM Mono', monospace;
}
.divider { border-top: 1px solid #1E1E1E; margin: 1.5rem 0; }
.section-label {
    font-size: 0.60rem;
    letter-spacing: .18em;
    text-transform: uppercase;
    color: #555;
    margin-bottom: .8rem;
}
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="bks-header">
  <h1>◎ BKS Algorithm — Control Center</h1>
  <span>Scoring prodotti · Salute collezioni · Coda priorità · Gate pubblicazione</span>
</div>
""", unsafe_allow_html=True)

# ── Load algorithm ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=120, show_spinner=False)
def _load_algorithm() -> tuple[dict, list[dict], list[dict], list[dict]]:
    from ecommerce_automation.bks_algorithm import BKSAlgorithm
    algo = BKSAlgorithm()
    summary = algo.summary()
    rows = algo.to_rows()
    health = [
        {
            "handle": h.handle,
            "accent": h.accent,
            "product_count": h.product_count,
            "avg_score": h.avg_score,
            "ready_count": h.ready_count,
            "critical_count": h.critical_count,
            "status": h.status,
        }
        for h in algo.collection_health()
    ]
    priority = algo.to_rows()  # sorted by score asc done in priority_queue
    priority_rows = sorted(rows, key=lambda r: r["score"])[:25]
    return summary, rows, health, priority_rows


if st.button("⟳ Refresh", key="refresh_algo"):
    st.cache_data.clear()
    st.rerun()

with st.spinner("Calcolo in corso…"):
    try:
        summary, all_rows, health_data, priority_rows = _load_algorithm()
        algo_ok = True
    except Exception as exc:
        st.error(f"Algoritmo non disponibile: {exc}")
        algo_ok = False

if not algo_ok:
    st.stop()

# ── Key metrics ────────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Overview prodotti</div>', unsafe_allow_html=True)
m1, m2, m3, m4, m5, m6 = st.columns(6)
m1.metric("Prodotti", summary.get("total", 0))
m2.metric("Score medio", f"{summary.get('avg_score', 0):.1f}")
m3.metric("P3 READY", summary.get("ready", 0), delta=None, help="Score ≥ 75 — pronti per gate")
m4.metric("P2 REFINE", summary.get("refine", 0), help="Score 55–74")
m5.metric("P1 FIX", summary.get("fix", 0), help="Score 35–54")
m6.metric("P0 CRITICAL", summary.get("critical", 0), delta=None, help="Score < 35")

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── Collection Health ──────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Salute collezioni</div>', unsafe_allow_html=True)

cols8 = st.columns(8)
status_icons = {"ok": "✓", "warn": "◐", "critical": "!", "empty": "○"}

for i, h in enumerate(health_data):
    with cols8[i]:
        icon = status_icons.get(h["status"], "·")
        bar_color = h["accent"] if h["status"] == "ok" else (
            "#ffa94d" if h["status"] == "warn" else
            ("#ff6b6b" if h["status"] == "critical" else "#333")
        )
        st.markdown(f"""
        <div class="coll-card" style="--accent:{h['accent']};">
          <div class="coll-name">{icon} {h['handle'].upper()}</div>
          <div class="coll-score" style="color:{bar_color}">{h['avg_score']}</div>
          <div class="coll-meta">{h['product_count']} prod · {h['ready_count']} ready</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# ── Main tabs ──────────────────────────────────────────────────────────────────
tab_queue, tab_all, tab_gate, tab_export = st.tabs([
    "Priority Queue",
    "All Products",
    "Publication Gate",
    "Export"
])

# ── Priority Queue tab ─────────────────────────────────────────────────────────
with tab_queue:
    st.markdown('<div class="section-label">Top 25 — urgenti per primo</div>', unsafe_allow_html=True)

    df_prio = pd.DataFrame(priority_rows)
    if not df_prio.empty:
        def _tier_badge(tier: str) -> str:
            return f'<span class="tier-{tier}">{tier}</span>'

        display_cols = ["handle", "title", "collection", "score", "seo", "images", "data", "tier", "issues"]
        df_show = df_prio[display_cols].copy() if all(c in df_prio.columns for c in display_cols) else df_prio

        def _color_score(val: float) -> str:
            if val >= 75:
                return "color: #69db7c"
            if val >= 55:
                return "color: #ffe066"
            if val >= 35:
                return "color: #ffa94d"
            return "color: #ff6b6b"

        styled = df_show.style.map(
            lambda v: _color_score(v) if isinstance(v, (int, float)) else "",
            subset=pd.IndexSlice[:, ["score", "seo", "images", "data"]]
        ).set_properties(**{"font-size": "0.72rem", "font-family": "DM Mono, monospace"})

        st.dataframe(styled, use_container_width=True, height=520)
    else:
        st.info("Nessun prodotto trovato.")

# ── All Products tab ───────────────────────────────────────────────────────────
with tab_all:
    col_filter, col_tier, col_sort = st.columns([3, 2, 2])
    with col_filter:
        coll_filter = st.selectbox("Collezione", ["Tutte"] + list(["hours","glyph","marker","riviera","pulse","token","flag","origin"]))
    with col_tier:
        tier_filter = st.selectbox("Tier", ["Tutti", "P0", "P1", "P2", "P3"])
    with col_sort:
        sort_by = st.selectbox("Ordina per", ["score", "seo", "images", "data", "handle"])

    df_all = pd.DataFrame(all_rows)
    if not df_all.empty:
        if coll_filter != "Tutte":
            df_all = df_all[df_all["collection"] == coll_filter]
        if tier_filter != "Tutti":
            df_all = df_all[df_all["tier"] == tier_filter]
        ascending = sort_by == "handle"
        df_all = df_all.sort_values(sort_by, ascending=ascending)

        st.caption(f"{len(df_all)} prodotti")
        st.dataframe(
            df_all.style.map(
                lambda v: ("color:#69db7c" if v >= 75 else "color:#ffe066" if v >= 55 else "color:#ffa94d" if v >= 35 else "color:#ff6b6b")
                if isinstance(v, (int, float)) else "",
                subset=pd.IndexSlice[:, ["score", "seo", "images", "data"]] if all(c in df_all.columns for c in ["score","seo","images","data"]) else pd.IndexSlice[:, []]
            ).set_properties(**{"font-size": "0.72rem", "font-family": "DM Mono, monospace"}),
            use_container_width=True,
            height=600,
        )
    else:
        st.info("Nessun prodotto con i filtri selezionati.")

# ── Publication Gate tab ───────────────────────────────────────────────────────
with tab_gate:
    st.markdown('<div class="section-label">Pre-publication gate — verifica singolo prodotto</div>', unsafe_allow_html=True)
    st.markdown("""
    <p style="font-size:0.72rem;color:#666;margin-bottom:1rem">
    Prima di pubblicare su Shopify: armocromista · tipografo · copy · photo studio · commercial strategy devono confermare.
    </p>
    """, unsafe_allow_html=True)

    handle_input = st.text_input("Handle prodotto", placeholder="es. bks-glyph-cross-puffer")

    if handle_input.strip():
        try:
            from ecommerce_automation.bks_algorithm import BKSAlgorithm
            algo_check = BKSAlgorithm()
            result = algo_check.gate_check(handle_input.strip())

            col_res, col_detail = st.columns([1, 2])
            with col_res:
                if result["pass"]:
                    st.markdown(f'<div class="gate-pass">✓ GATE PASS — score {result.get("total_score",0)}</div>', unsafe_allow_html=True)
                    st.success("Prodotto pronto per la pubblicazione. Avvia le skill pre-publish.")
                else:
                    st.markdown(f'<div class="gate-fail">✗ GATE FAIL — score {result.get("total_score",0)}</div>', unsafe_allow_html=True)
                    st.error("Prodotto non pronto. Correggi le issue prima di pubblicare.")

            with col_detail:
                checks = result.get("checks", {})
                for check, passed in checks.items():
                    icon = "✓" if passed else "✗"
                    color = "#69db7c" if passed else "#ff6b6b"
                    st.markdown(f'<span style="color:{color};font-size:0.75rem;font-family:DM Mono">{icon} {check}</span><br>', unsafe_allow_html=True)

            issues = result.get("issues", [])
            if issues:
                st.markdown("**Issues:**")
                tags_html = " ".join(f'<span class="issue-tag">{i}</span>' for i in issues)
                st.markdown(tags_html, unsafe_allow_html=True)
        except Exception as exc:
            st.error(f"Gate check error: {exc}")

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-label">P3 Ready — prodotti che passano il gate</div>', unsafe_allow_html=True)

    ready_rows = [r for r in all_rows if r.get("tier") == "P3"]
    if ready_rows:
        st.dataframe(
            pd.DataFrame(ready_rows)[["handle", "title", "collection", "score", "published"]],
            use_container_width=True,
        )
    else:
        st.info("Nessun prodotto P3 ready. Lavora sulla priority queue.")

# ── Export tab ─────────────────────────────────────────────────────────────────
with tab_export:
    st.markdown('<div class="section-label">Export scores CSV</div>', unsafe_allow_html=True)
    if st.button("Esporta bks_algorithm_scores.csv"):
        try:
            from ecommerce_automation.bks_algorithm import BKSAlgorithm
            out = BKSAlgorithm().export_csv()
            st.success(f"Esportato: {out}")
        except Exception as exc:
            st.error(str(exc))

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-label">Debug info</div>', unsafe_allow_html=True)
    st.json(summary, expanded=False)
