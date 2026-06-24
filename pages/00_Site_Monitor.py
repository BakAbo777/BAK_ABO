"""BKS Studio — Site Monitor & Control Panel
Live site health, GMC status, Worker, print panel archive, quick actions.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
import streamlit as st
import urllib3

urllib3.disable_warnings()

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
import bks_nav  # noqa: E402


def _load_env() -> None:
    p = BASE_DIR / ".env"
    if not p.exists():
        return
    for raw in p.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_load_env()

st.set_page_config(
    page_title="BKS Site Monitor",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)
bks_nav.render("monitor")

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&display=swap');
html, body, [data-testid="stAppViewContainer"] {
    background: #0A0A0A !important;
    color: #FAFAF7;
    font-family: 'DM Mono', monospace;
}
[data-testid="stHeader"]  { background: #0A0A0A !important; }
[data-testid="stSidebar"] { background: #0D0D0D !important; }

/* ── Metrics ── */
[data-testid="stMetricValue"] {
    font-size: 2rem !important;
    font-family: 'DM Mono', monospace;
    color: #FAFAF7 !important;
    font-weight: 300;
}
[data-testid="stMetricLabel"] {
    font-size: 0.65rem !important;
    letter-spacing: .12em;
    text-transform: uppercase;
    color: #aaa !important;
}
[data-testid="stMetricDelta"] { font-size: 0.7rem !important; }

/* ── Tabs ── */
[data-baseweb="tab-list"] {
    background: #111 !important;
    border-bottom: 1px solid #2a2a2a !important;
    gap: 0 !important;
}
[data-baseweb="tab"] {
    background: transparent !important;
    color: #888 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    letter-spacing: .12em !important;
    text-transform: uppercase !important;
    padding: 10px 20px !important;
    border-bottom: 2px solid transparent !important;
}
[data-baseweb="tab"]:hover { color: #FAFAF7 !important; }
[aria-selected="true"][data-baseweb="tab"] {
    color: #c9b79c !important;
    border-bottom: 2px solid #c9b79c !important;
    background: transparent !important;
}
[data-baseweb="tab-panel"] { padding-top: 1rem !important; }

/* ── Section label ── */
.section-label {
    font-size: 0.62rem;
    letter-spacing: .18em;
    text-transform: uppercase;
    color: #aaa;
    margin: 1.5rem 0 0.75rem;
    border-top: 1px solid #222;
    padding-top: 1rem;
}

/* ── Header ── */
.bks-header {
    border-bottom: 1px solid #1E1E1E;
    padding: 1rem 0 0.75rem;
    margin-bottom: 1.5rem;
}
.bks-header h1 {
    font-size: 1rem;
    letter-spacing: .22em;
    text-transform: uppercase;
    color: #FAFAF7;
    font-weight: 300;
    margin: 0;
}
.bks-header span { color: #888; font-size: 0.7rem; }

/* ── Status colours ── */
.status-ok   { color: #4cae8c; }
.status-warn { color: #d4a030; }
.status-err  { color: #c82020; }

/* ── Poem block ── */
.poem-block pre, .poem-block .stText {
    color: #ccc !important;
    font-size: 0.85rem;
}

/* ── Buttons ── */
div[data-testid="stButton"] > button {
    background: transparent;
    border: 1px solid #333;
    color: #c9b79c;
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: .1em;
    padding: 6px 14px;
}
div[data-testid="stButton"] > button:hover {
    border-color: #c9b79c;
    background: rgba(201,183,156,0.07);
    color: #FAFAF7;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] { border: 1px solid #1e1e1e; }
[data-testid="stCaption"]   { color: #aaa !important; }

/* ── Selectbox / number input ── */
[data-baseweb="select"] * { color: #FAFAF7 !important; background: #111 !important; }
[data-baseweb="input"]  input { color: #FAFAF7 !important; background: #111 !important; }
</style>
""", unsafe_allow_html=True)

now = datetime.now().strftime("%Y-%m-%d  %H:%M")
st.markdown(f"""
<div class="bks-header">
  <h1>◈ BKS Site Monitor</h1>
  <span>Live control panel &nbsp;·&nbsp; {now}</span>
</div>
""", unsafe_allow_html=True)

DOMAIN = os.environ.get("SHOPIFY_MYSHOPIFY_DOMAIN", "")
TOKEN  = os.environ.get("SHOPIFY_ADMIN_TOKEN", "")
HDR    = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
API    = f"https://{DOMAIN}/admin/api/2025-01"
GQL    = f"https://{DOMAIN}/admin/api/2025-01/graphql.json"

WORKER_URL = "https://bks-agent.bakabo.workers.dev"

SITE_PAGES = [
    ("/", "Home"),
    ("/collections/all", "Catalog"),
    ("/collections/bks-hours", "Hours"),
    ("/collections/bks-glyph", "Glyph"),
    ("/collections/bks-marker", "Marker"),
    ("/collections/bks-riviera", "Riviera"),
    ("/collections/bks-pulse", "Pulse"),
    ("/collections/bks-token", "Token"),
    ("/collections/bks-flag", "Flag"),
    ("/collections/bks-origin", "Origin"),
    ("/pages/bks-members-entry", "Members Entry"),
    ("/pages/bks-members", "Members Dashboard"),
    ("/pages/bks-puffer-jacket", "Puffer Jacket"),
    ("/pages/bks-windbreaker", "Windbreaker"),
    ("/pages/bks-hawaiian-shirt", "Hawaiian Shirt"),
    ("/pages/bks-hoodie", "Hoodie"),
    ("/pages/bks-sneakers", "Sneakers"),
    ("/pages/bks-swim-trunks", "Swim Trunks"),
    ("/pages/bks-faq", "FAQ"),
    ("/pages/about-bakabo-1", "About"),
]

BKS_COLLECTIONS = [
    ("bks-hours",   "BKS Hours",   "#c8c4be"),
    ("bks-glyph",   "BKS Glyph",   "#d4a030"),
    ("bks-marker",  "BKS Marker",  "#c04418"),
    ("bks-riviera", "BKS Riviera", "#0ca898"),
    ("bks-pulse",   "BKS Pulse",   "#8888cc"),
    ("bks-token",   "BKS Token",   "#9828d8"),
    ("bks-flag",    "BKS Flag",    "#c82020"),
    ("bks-origin",  "BKS Origin",  "#489808"),
]


# ── Data loaders ──────────────────────────────────────────────────────────────
@st.cache_data(ttl=120, show_spinner=False)
def load_shopify_summary() -> dict:
    try:
        r = requests.get(f"{API}/products/count.json", headers=HDR, timeout=10, verify=False)
        total = r.json().get("count", 0) if r.ok else 0
        return {"total_products": total, "ok": True}
    except Exception as e:
        return {"total_products": 0, "ok": False, "error": str(e)}


@st.cache_data(ttl=60, show_spinner=False)
def load_gmc_report() -> dict:
    path = BASE_DIR / "output" / "gmc_sync_report.json"
    if not path.exists():
        return {"alerts": 0, "ok": 0, "total": 0, "ts": "N/A", "loaded": False}
    try:
        d = json.loads(path.read_text(encoding="utf-8"))
        return {
            "alerts": d.get("alerts", 0),
            "ok": d.get("ok", 0),
            "total": d.get("total_active", 0),
            "ts": d.get("timestamp", "?")[:16].replace("T", " "),
            "loaded": True,
        }
    except Exception:
        return {"alerts": "?", "ok": "?", "total": "?", "ts": "?", "loaded": False}


@st.cache_data(ttl=60, show_spinner=False)
def load_worker_health() -> dict:
    try:
        r = requests.get(f"{WORKER_URL}/health", timeout=8, verify=False)
        if r.ok:
            d = r.json()
            svcs = d.get("services", [])
            all_ok = all(s.get("ok") for s in svcs)
            return {
                "ok": True, "status": d.get("status", "?"),
                "version": d.get("worker", {}).get("endpoint", WORKER_URL),
                "kv": d.get("kv", {}).get("ok", False),
                "ai": d.get("ai", {}).get("ok", False),
                "services": svcs, "all_services_ok": all_ok,
            }
        return {"ok": False, "status": r.status_code}
    except Exception as e:
        return {"ok": False, "error": str(e)[:60]}


@st.cache_data(ttl=90, show_spinner=False)
def check_site_pages() -> list[dict]:
    results = []
    for path, label in SITE_PAGES:
        t0 = time.time()
        try:
            r = requests.get(f"https://bakabo.club{path}", timeout=8, verify=False, allow_redirects=True)
            ms = int((time.time() - t0) * 1000)
            results.append({"path": path, "label": label, "status": r.status_code, "ms": ms})
        except Exception as e:
            results.append({"path": path, "label": label, "status": 0, "ms": 0, "error": str(e)[:40]})
        time.sleep(0.15)
    return results


def load_print_panels() -> list[dict]:
    panels_root = BASE_DIR / "output" / "printify_panels"
    if not panels_root.exists():
        return []
    panels = []
    for col_dir in sorted(panels_root.iterdir()):
        if not col_dir.is_dir():
            continue
        meta_path = col_dir / "metadata.json"
        if meta_path.exists():
            try:
                items = json.loads(meta_path.read_text(encoding="utf-8"))
                for item in items:
                    item["_path"] = str(col_dir / item["file"])
                    item["_col_dir"] = col_dir.name
                    panels.append(item)
            except Exception:
                pass
    return panels


def load_poems() -> dict:
    path = BASE_DIR / "output" / "collection_poems.json"
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


# ── TOP METRICS ROW ───────────────────────────────────────────────────────────
shopify = load_shopify_summary()
gmc     = load_gmc_report()
worker  = load_worker_health()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Products", shopify.get("total_products", "—"))
alert_count = gmc.get("alerts", "?")
c2.metric("GMC Alerts", alert_count,
          delta="0 alerts" if alert_count == 0 else f"{alert_count} to fix",
          delta_color="normal" if alert_count == 0 else "inverse")
c3.metric("Worker", "Online" if worker.get("ok") else "Offline")
c4.metric("KV Store", "OK" if worker.get("kv") else "—")
c5.metric("AI Binding", "OK" if worker.get("ai") else "—")

if gmc.get("loaded"):
    st.caption(f"GMC report: {gmc['ts']} · {gmc['ok']}/{gmc['total']} products OK")

# ── TABS ──────────────────────────────────────────────────────────────────────
tab_site, tab_gmc, tab_worker, tab_panels, tab_poems, tab_actions = st.tabs([
    "Site Health", "GMC / Prices", "Worker", "Print Panels", "Verse Poems", "Quick Actions"
])

# ── TAB: SITE HEALTH ──────────────────────────────────────────────────────────
with tab_site:
    st.markdown('<div class="section-label">Live page status</div>', unsafe_allow_html=True)

    col_check, col_note = st.columns([1, 4])
    with col_check:
        run_check = st.button("Run live check", key="site_check")

    if run_check:
        st.cache_data.clear()

    with st.spinner("Checking pages…"):
        page_results = check_site_pages()

    ok_count  = sum(1 for p in page_results if p["status"] == 200)
    err_count = len(page_results) - ok_count

    col_a, col_b = st.columns(2)
    col_a.metric("Pages OK", f"{ok_count}/{len(page_results)}")
    if err_count:
        col_b.metric("Errors", err_count, delta_color="inverse")

    # Table
    rows = []
    for p in page_results:
        s = p["status"]
        if s == 200:    sym = "✓"
        elif s == 429:  sym = "~"   # rate limited = likely OK
        elif s == 0:    sym = "✗"
        else:           sym = "!"
        rows.append({
            "Page": p["label"],
            "Path": p["path"],
            "Status": f"{sym} {s}" if s else f"✗ ERR",
            "Latency (ms)": p.get("ms", "—"),
        })

    import pandas as pd
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, height=500)

# ── TAB: GMC / PRICES ─────────────────────────────────────────────────────────
with tab_gmc:
    st.markdown('<div class="section-label">Google Merchant Center — price ladder</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Products", gmc.get("total", "—"))
    c2.metric("Price OK", gmc.get("ok", "—"))
    c3.metric("Alerts", gmc.get("alerts", "—"))

    if gmc.get("alerts") == 0:
        st.success("All 202 products on the approved price ladder. No alerts.")
    else:
        st.warning(f"{gmc['alerts']} products have price alerts — run the fix script in Quick Actions.")

    st.markdown("**Approved price ladder:**")
    st.markdown("""
| Product type | Price |
|---|---|
| Racerback Dress | $65.00 |
| Tee (Cut & Sew) | $49.00 |
| Hawaiian Shirt | $79.00 |
| Pullover Hoodie | $79.00 |
| Windbreaker Jacket | $109.00 |
| Sneakers Flag 03 | $75.00 |
| All others | Cost × 1.67 min |
""")

# ── TAB: WORKER ───────────────────────────────────────────────────────────────
with tab_worker:
    st.markdown('<div class="section-label">Cloudflare Worker v5 — bks-agent</div>', unsafe_allow_html=True)

    if st.button("Refresh Worker Status", key="worker_refresh"):
        st.cache_data.clear()
        worker = load_worker_health()

    if worker.get("ok"):
        st.success(f"Worker online — {WORKER_URL}")
        col_w1, col_w2 = st.columns(2)
        col_w1.metric("Status",   worker.get("status", "?"))
        col_w2.metric("Services", "All OK" if worker.get("all_services_ok") else "Issues")

        svcs = worker.get("services", [])
        if svcs:
            st.markdown("**Service pings:**")
            for s in svcs:
                icon = "✓" if s.get("ok") else "✗"
                lat  = s.get("latency_ms", s.get("status", "?"))
                st.markdown(f"- {icon} **{s['name']}** — status {s.get('status', '?')} · {lat}ms")
    else:
        st.error(f"Worker offline or unreachable: {worker.get('error', worker.get('status', '?'))}")

    st.markdown(f"""
**Endpoints:**
- Health: `{WORKER_URL}/health`
- AI Ask: `{WORKER_URL}/ask`
- Social: `{WORKER_URL}/social`
- Catalog refresh: `{WORKER_URL}/refresh` (POST)
""")

# ── TAB: PRINT PANELS ─────────────────────────────────────────────────────────
with tab_panels:
    st.markdown('<div class="section-label">Printify print panels — AOP tiles generated by gpt-image-1</div>',
                unsafe_allow_html=True)

    panels = load_print_panels()
    if not panels:
        st.info("No print panels yet. Run: `python scripts/generate_print_panels.py --collection all`")
    else:
        st.caption(f"{len(panels)} panels generated · Review, approve, then upload to Printify manually")

        cols = st.columns(4)
        for i, panel in enumerate(panels):
            col = cols[i % 4]
            img_path = Path(panel.get("_path", ""))
            with col:
                if img_path.exists():
                    try:
                        st.image(str(img_path), caption=f"{panel.get('label', panel.get('collection', '?'))} · {panel.get('date', '')}",
                                 use_container_width=True)
                    except Exception:
                        st.markdown(f"**{panel.get('label', '?')}**")
                else:
                    st.markdown(f"**{panel.get('label', '?')}** _(file missing)_")
                approved = panel.get("approved", False)
                st.caption("✓ Approved" if approved else "Pending review")

# ── TAB: VERSE POEMS ──────────────────────────────────────────────────────────
with tab_poems:
    st.markdown('<div class="section-label">BKS Verse — collection poems archive</div>',
                unsafe_allow_html=True)

    poems = load_poems()
    if not poems:
        st.info("No poems archive found at output/collection_poems.json")
    else:
        handles = list(poems.items())
        rows = [handles[i:i+2] for i in range(0, len(handles), 2)]
        for row in rows:
            left, right = st.columns(2)
            for col_widget, (handle, data) in zip([left, right], row):
                col_info   = next((c for c in BKS_COLLECTIONS if c[0] == handle), (handle, handle, "#888"))
                col_accent = col_info[2]
                col_name   = col_info[1]
                lines_html = "<br>".join(data.get("lines", []))
                with col_widget:
                    st.markdown(
                        f"<div style='border:1px solid #1e1e1e;border-top:3px solid {col_accent};"
                        f"padding:1.2rem 1.4rem;border-radius:4px;margin-bottom:1rem;'>"
                        f"<span style='color:{col_accent};font-size:0.62rem;letter-spacing:.15em;"
                        f"text-transform:uppercase;'>◈ {col_name}</span>"
                        f"<p style='color:#FAFAF7;font-size:1rem;font-weight:500;margin:0.5rem 0 0.75rem;'>"
                        f"{data.get('title','')}</p>"
                        f"<p style='color:#ccc;font-size:0.82rem;line-height:1.8;margin:0 0 0.8rem;'>"
                        f"{lines_html}</p>"
                        f"<span style='color:#555;font-size:0.68rem;letter-spacing:.08em;'>"
                        f"— BKS Verse</span>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

# ── TAB: QUICK ACTIONS ────────────────────────────────────────────────────────
with tab_actions:
    st.markdown('<div class="section-label">Quick actions — run scripts from panel</div>',
                unsafe_allow_html=True)

    st.warning("Actions run in the background. Check terminal output for results.")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("**Price & GMC**")
        if st.button("Run GMC Sync", key="run_gmc"):
            with st.spinner("Running GMC sync…"):
                result = subprocess.run(
                    [sys.executable, str(BASE_DIR / "scripts" / "gmc_daily_sync.py")],
                    capture_output=True, text=True, cwd=str(BASE_DIR), timeout=60
                )
            if result.returncode == 0:
                st.success("GMC sync completed.")
                st.cache_data.clear()
            else:
                st.error(f"Error: {result.stderr[-300:]}")

        if st.button("Run Price Fix", key="run_price_fix"):
            with st.spinner("Applying price fixes…"):
                result = subprocess.run(
                    [sys.executable, str(BASE_DIR / "scripts" / "fix_price_alerts.py")],
                    capture_output=True, text=True, cwd=str(BASE_DIR), timeout=120
                )
            output = (result.stdout + result.stderr)[-600:]
            if result.returncode == 0:
                st.success("Price fixes applied.")
                st.text(output)
                st.cache_data.clear()
            else:
                st.error(f"Error: {output}")

    with c2:
        st.markdown("**Print Panels**")
        col_select = st.selectbox(
            "Collection", ["all"] + [c[0] for c in BKS_COLLECTIONS], key="panel_col"
        )
        variants = st.number_input("Variants", 1, 3, 1, key="panel_variants")
        if st.button("Generate Print Panels", key="run_panels"):
            with st.spinner(f"Generating panels for {col_select}… (may take 2-3 min)"):
                result = subprocess.run(
                    [sys.executable, str(BASE_DIR / "scripts" / "generate_print_panels.py"),
                     "--collection", col_select, "--variants", str(variants)],
                    capture_output=True, text=True, cwd=str(BASE_DIR), timeout=300
                )
            if result.returncode == 0:
                st.success("Panels generated.")
                st.text(result.stdout[-400:])
            else:
                st.error(result.stderr[-300:])

    with c3:
        st.markdown("**Site**")
        if st.button("Clear All Caches", key="clear_cache"):
            st.cache_data.clear()
            st.success("Caches cleared.")
            st.rerun()

        if st.button("Refresh Site Check", key="refresh_site"):
            st.cache_data.clear()
            st.rerun()

    # Recent output files
    st.markdown('<div class="section-label">Recent output files</div>', unsafe_allow_html=True)
    out_dir = BASE_DIR / "output"
    if out_dir.exists():
        recent = sorted(out_dir.rglob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True)[:8]
        for f in recent:
            rel = f.relative_to(BASE_DIR)
            mtime = datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            size = f.stat().st_size // 1024
            st.markdown(f"`{rel}` — {mtime} — {size}KB")
