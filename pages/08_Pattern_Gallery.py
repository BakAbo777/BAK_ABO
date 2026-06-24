"""BKS Pattern Gallery — catalogo certificato delle pezze BKS."""
import json
from pathlib import Path
import streamlit as st

try:
    from streamlit_master import inject_bks_theme
    inject_bks_theme()
except Exception:
    pass

st.set_page_config(page_title="BKS Pattern Gallery", layout="wide")

ROOT         = Path(__file__).parent.parent
PATTERNS_FILE = ROOT / "output" / "bks_patterns.json"

COLLECTION_LABELS = {
    "flag":     "BKS Flag",
    "glyph":    "BKS Glyph",
    "hours":    "BKS Hours",
    "marker":   "BKS Marker",
    "origin":   "BKS Origin",
    "pulse":    "BKS Pulse",
    "riviera":  "BKS Riviera",
    "token":    "BKS Token",
    "folklore": "BKS Origin",
    "unknown":  "BKS Studio",
}

COLLECTION_COLORS = {
    "flag": "#c82020", "glyph": "#d4a030", "hours": "#c8c4be",
    "marker": "#c04418", "origin": "#489808", "pulse": "#8888cc",
    "riviera": "#0ca898", "token": "#9828d8", "folklore": "#489808",
    "unknown": "#888888",
}

@st.cache_data(ttl=300)
def load_registry():
    if not PATTERNS_FILE.exists():
        return None
    return json.loads(PATTERNS_FILE.read_text(encoding="utf-8"))

def score_badge(score: int) -> str:
    if score >= 22:
        return f"⬛ {score}/25 EXCELLENT"
    elif score >= 20:
        return f"▪ {score}/25 GOOD"
    else:
        return f"· {score}/25 DRAFT"

def main():
    st.markdown("## BKS Pattern Gallery")
    st.markdown("*Catalogo certificato delle pezze BKS — ogni pattern è un'opera numerata.*")

    registry = load_registry()
    if not registry:
        st.error("Registry non trovato. Esegui: `python scripts/generate_pattern_registry.py`")
        return

    meta    = registry.get("_meta", {})
    stats   = meta.get("stats", {})
    patterns = registry.get("patterns", {})

    # ── Stats strip ──────────────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Pezze totali", stats.get("total", 0))
    col2.metric("Excellent (≥22)", stats.get("score_distribution", {}).get("excellent", 0))
    col3.metric("Good (20-21)",    stats.get("score_distribution", {}).get("good", 0))
    col4.metric("Draft (<20)",     stats.get("score_distribution", {}).get("draft", 0))

    st.divider()

    # ── Filtri ───────────────────────────────────────────────────────────────
    f1, f2, f3 = st.columns([2, 2, 1])
    with f1:
        collections = sorted(set(p["collection"] for p in patterns.values()))
        col_options = ["Tutte"] + [COLLECTION_LABELS.get(c, c.title()) for c in collections]
        col_filter  = st.selectbox("Collezione", col_options)
    with f2:
        score_options = ["Tutti", "Excellent (≥22)", "Good (≥20)", "Draft (<20)"]
        score_filter  = st.selectbox("Qualità", score_options)
    with f3:
        status_filter = st.selectbox("Stato", ["Tutti", "Active", "Draft"])

    # ── Filtra ───────────────────────────────────────────────────────────────
    items = list(patterns.items())
    if col_filter != "Tutte":
        rev_labels = {v: k for k, v in COLLECTION_LABELS.items()}
        col_key = rev_labels.get(col_filter, col_filter.lower())
        items = [(pid, p) for pid, p in items if p["collection"] == col_key]
    if score_filter == "Excellent (≥22)":
        items = [(pid, p) for pid, p in items if p["quality_score"] >= 22]
    elif score_filter == "Good (≥20)":
        items = [(pid, p) for pid, p in items if 20 <= p["quality_score"] < 22]
    elif score_filter == "Draft (<20)":
        items = [(pid, p) for pid, p in items if p["quality_score"] < 20]
    if status_filter == "Active":
        items = [(pid, p) for pid, p in items if p["status"] == "active"]
    elif status_filter == "Draft":
        items = [(pid, p) for pid, p in items if p["status"] == "draft"]

    st.caption(f"{len(items)} pezze trovate")
    st.divider()

    # ── Grid ─────────────────────────────────────────────────────────────────
    cols_per_row = 3
    for i in range(0, len(items), cols_per_row):
        row = items[i:i + cols_per_row]
        cols = st.columns(cols_per_row)
        for j, (pid, p) in enumerate(row):
            col  = p["collection"]
            color = COLLECTION_COLORS.get(col, "#888")
            score = p["quality_score"]
            n_products = len(p.get("products", []))
            label = COLLECTION_LABELS.get(col, col.title())
            with cols[j]:
                st.markdown(f"""
<div style="border:1px solid {color}33; border-left:3px solid {color};
            padding:14px 16px; margin-bottom:8px; background:#0d0c0a;">
  <div style="font-size:11px; color:{color}; letter-spacing:2px; text-transform:uppercase;
              margin-bottom:4px;">{label}</div>
  <div style="font-size:18px; font-weight:600; color:#faf8f5;
              letter-spacing:1px; margin-bottom:8px;">{pid}</div>
  <div style="font-size:11px; color:#faf8f566;">{score_badge(score)}</div>
  <div style="font-size:11px; color:#faf8f544; margin-top:4px;">
    {n_products} {'prodotto' if n_products == 1 else 'prodotti'} &nbsp;·&nbsp;
    {p['status'].upper()}
  </div>
  <div style="font-size:11px; color:#faf8f555; margin-top:6px;
              font-style:italic; line-height:1.4;">
    {p.get('feedback', '')[:80]}{'...' if len(p.get('feedback','')) > 80 else ''}
  </div>
</div>
""", unsafe_allow_html=True)
                with st.expander("Prodotti derivati"):
                    for prod in p.get("products", []):
                        shopify_id = prod.get("shopify_id", "")
                        title = prod.get("title", "—")
                        visible = "✓" if prod.get("visible") else "draft"
                        link = f"https://bakabo.club/admin/products/{shopify_id}" if shopify_id else "#"
                        st.markdown(f"[{title}]({link}) — {visible}")

    st.divider()
    st.caption(f"Registry v{meta.get('version', '?')} · generato {meta.get('generated_at', '')[:10]}")

    # ── Export ───────────────────────────────────────────────────────────────
    if st.button("Rigenera registry"):
        import subprocess
        result = subprocess.run(
            ["python", "scripts/generate_pattern_registry.py"],
            capture_output=True, text=True, cwd=str(ROOT)
        )
        if result.returncode == 0:
            st.success(result.stdout)
            st.cache_data.clear()
            st.rerun()
        else:
            st.error(result.stderr)

if __name__ == "__main__":
    main()
