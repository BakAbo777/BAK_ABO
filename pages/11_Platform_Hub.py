"""BKS Platform Hub — dropdown + app embedded o card live."""
from __future__ import annotations

import os
import socket
from pathlib import Path

import requests
import streamlit as st
import streamlit.components.v1 as components
import urllib3

urllib3.disable_warnings()

st.set_page_config(page_title="BKS — Platform Hub", page_icon="◎", layout="wide")

try:
    from streamlit_master import inject_bks_theme
    inject_bks_theme()
except Exception:
    pass

try:
    import bks_nav
    bks_nav.render("hub")
except Exception:
    pass

# ── env ──────────────────────────────────────────────────────────────────────
_env = Path(__file__).resolve().parent.parent / ".env"
if _env.exists():
    for _line in _env.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _v = _line.split("=", 1)
            if _k.strip() not in os.environ:
                os.environ[_k.strip()] = _v.strip().strip('"').strip("'")

DOMAIN   = os.environ.get("SHOPIFY_MYSHOPIFY_DOMAIN", "11628e-2.myshopify.com")
TOKEN    = os.environ.get("SHOPIFY_ADMIN_TOKEN", "")
VER      = os.environ.get("SHOPIFY_API_VERSION", "2025-01")
PTOKEN   = os.environ.get("PRINTIFY_API_TOKEN", "")
YT_CH    = os.environ.get("YOUTUBE_CHANNEL_ID", "UCv3DoOzXJU_C99GTi55D0Sg")
CF_ACC   = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "e796d289f744035eee2641e853d8a5af")
GMC_ID   = os.environ.get("GOOGLE_MERCHANT_ID", "5295165689")
META_BID = os.environ.get("META_BUSINESS_ID", "2070678923161271")


def port_open(port: int) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.8):
            return True
    except OSError:
        return False


# ── Apps catalog ─────────────────────────────────────────────────────────────
APPS: list[dict] = [
    # LOCAL — embed via iframe
    {
        "id": "catalog_engine",
        "label": "◎ BKS Studio — Catalog Engine",
        "group": "LOCAL",
        "port": 8501,
        "url": "http://localhost:8501",
        "desc": "Catalogo, SEO, Image Factory, Social — app locale",
        "color": "#2f6f6b",
    },
    {
        "id": "tryon_engine",
        "label": "◎ Try-On Engine — Camerino AI",
        "group": "LOCAL",
        "port": 8010,
        "url": "http://127.0.0.1:8010",
        "desc": "Virtual try-on, member area — app locale",
        "color": "#8888cc",
    },
    # EXTERNAL — card + open button
    {
        "id": "bakabo_store",
        "label": "🌐 bakabo.club — Store Live",
        "group": "STORE",
        "url": "https://bakabo.club",
        "admin_url": "https://bakabo.club",
        "desc": "Shopify store live — bakabo.club",
        "color": "#c8c4be",
        "api": "shopify_store",
    },
    {
        "id": "shopify_admin",
        "label": "🛍 Shopify Admin",
        "group": "STORE",
        "url": f"https://admin.shopify.com/store/11628e-2",
        "desc": "Shopify Admin — prodotti, ordini, temi, app",
        "color": "#95BF47",
        "api": "shopify_admin",
    },
    {
        "id": "printify",
        "label": "🖨 Printify — Print on Demand",
        "group": "STORE",
        "url": "https://printify.com/app/store/products/12030061",
        "desc": "Printify shop 12030061 — 674 prodotti",
        "color": "#19d1bf",
        "api": "printify",
    },
    {
        "id": "gmc",
        "label": "🛒 Google Merchant Center",
        "group": "MARKETING",
        "url": f"https://merchants.google.com/mc/overview?a={GMC_ID}",
        "desc": f"GMC ID {GMC_ID} — feed Shopping, Performance Max",
        "color": "#4285F4",
        "api": None,
    },
    {
        "id": "youtube",
        "label": "▶ YouTube Studio",
        "group": "MARKETING",
        "url": f"https://studio.youtube.com/channel/{YT_CH}",
        "desc": "@BakAboClub — 12 video, Art in transfiguration (BKS)",
        "color": "#FF0000",
        "api": None,
    },
    {
        "id": "meta",
        "label": "📘 Meta Business Suite",
        "group": "MARKETING",
        "url": f"https://business.facebook.com/{META_BID}",
        "desc": "Facebook / Instagram — Meta Business",
        "color": "#1877F2",
        "api": None,
    },
    {
        "id": "cloudflare",
        "label": "☁ Cloudflare Dashboard",
        "group": "TECH",
        "url": f"https://dash.cloudflare.com/{CF_ACC}",
        "desc": "Workers, KV, R2, DNS — bakabo.club zone",
        "color": "#F48120",
        "api": None,
    },
    {
        "id": "heygen",
        "label": "🎬 HeyGen",
        "group": "TECH",
        "url": "https://app.heygen.com",
        "desc": "Avatar video, HyperFrames — Roberto Picchioni avatar",
        "color": "#6C5CE7",
        "api": None,
    },
    {
        "id": "ga4",
        "label": "📊 Google Analytics 4",
        "group": "ANALYTICS",
        "url": "https://analytics.google.com",
        "desc": "GA4 property — bakabo.club traffic & events",
        "color": "#E37400",
        "api": None,
    },
    {
        "id": "translate_adapt",
        "label": "🌍 Translate & Adapt",
        "group": "STORE",
        "url": "https://admin.shopify.com/store/11628e-2/apps/translate-and-adapt",
        "desc": "App Shopify localizzazione IT/EN — disabilitare widget Selecty",
        "color": "#5C6AC4",
        "api": None,
    },
]

# ── Cached API fetches ────────────────────────────────────────────────────────
@st.cache_data(ttl=300, show_spinner=False)
def fetch_shopify_stats() -> dict:
    try:
        base = f"https://{DOMAIN}/admin/api/{VER}"
        hdr  = {"X-Shopify-Access-Token": TOKEN}
        prod = requests.get(f"{base}/products/count.json", headers=hdr, verify=False, timeout=6).json().get("count", "?")
        cust = requests.get(f"{base}/customers/count.json", headers=hdr, verify=False, timeout=6).json().get("count", "?")
        ord_ = requests.get(f"{base}/orders/count.json?status=any", headers=hdr, verify=False, timeout=6).json().get("count", "?")
        return {"products": prod, "customers": cust, "orders": ord_, "ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@st.cache_data(ttl=300, show_spinner=False)
def fetch_printify_stats() -> dict:
    try:
        hdr = {"Authorization": f"Bearer {PTOKEN}"}
        r = requests.get("https://api.printify.com/v1/shops/12030061/products.json?limit=1&page=1", headers=hdr, verify=False, timeout=8)
        total = r.json().get("total", "?")
        return {"products": total, "ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ── UI ────────────────────────────────────────────────────────────────────────
st.title("◎ Platform Hub")
st.caption("Tutti i servizi BKS — seleziona dal menu e accedi direttamente")

st.markdown("---")

# Build dropdown labels
options = [f"{a['label']}" for a in APPS]
idx = st.selectbox("Seleziona piattaforma", range(len(options)), format_func=lambda i: options[i], label_visibility="collapsed")

app = APPS[idx]

# ── Render ────────────────────────────────────────────────────────────────────
st.markdown(f"### {app['label']}")
st.caption(app["desc"])

col_btn, col_status = st.columns([3, 1])

if app["group"] == "LOCAL":
    online = port_open(app["port"])
    with col_status:
        if online:
            st.success(f"ONLINE :{app['port']}")
        else:
            st.error(f"OFFLINE :{app['port']}")
    with col_btn:
        st.link_button("Apri in nuova tab →", app["url"])

    if online:
        st.markdown("---")
        components.iframe(app["url"], height=750, scrolling=True)
    else:
        st.warning(f"Servizio non attivo su porta {app['port']}. Avvia il bat corrispondente.")

else:
    # External app
    with col_btn:
        st.link_button("Apri in nuova tab →", app["url"])
    with col_status:
        st.info("Esterno")

    st.markdown("---")

    # Live stats for apps with API
    if app.get("api") == "shopify_admin" or app.get("api") == "shopify_store":
        with st.spinner("Carico dati Shopify..."):
            stats = fetch_shopify_stats()
        if stats.get("ok"):
            c1, c2, c3 = st.columns(3)
            c1.metric("Prodotti", stats["products"])
            c2.metric("Clienti", stats["customers"])
            c3.metric("Ordini totali", stats["orders"])
        else:
            st.warning(f"API error: {stats.get('error')}")

    elif app.get("api") == "printify":
        with st.spinner("Carico dati Printify..."):
            pstats = fetch_printify_stats()
        if pstats.get("ok"):
            st.metric("Prodotti Printify (shop 12030061)", pstats["products"])
        else:
            st.warning(f"API error: {pstats.get('error')}")

    # Try iframe anyway — some sites allow it
    st.markdown("#### Preview (se il sito lo consente)")
    st.caption("Alcuni siti bloccano l'incorporamento. Se la preview è bianca, usa 'Apri in nuova tab'.")
    components.html(
        f'<div style="width:100%;height:680px;border:1px solid #e8e8e8;border-radius:4px;overflow:hidden;">'
        f'<iframe src="{app["url"]}" style="width:100%;height:100%;border:none;" '
        f'sandbox="allow-scripts allow-same-origin allow-forms allow-popups" loading="lazy"></iframe>'
        f'</div>',
        height=700,
    )

# ── Quick links grid ──────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("#### Accesso rapido")

groups = {}
for a in APPS:
    groups.setdefault(a["group"], []).append(a)

for group, apps in groups.items():
    st.markdown(f"**{group}**")
    cols = st.columns(len(apps))
    for col, a in zip(cols, apps):
        with col:
            is_local = a["group"] == "LOCAL"
            if is_local:
                online = port_open(a["port"])
                dot = "🟢" if online else "🔴"
                col.link_button(f"{dot} {a['label'].split('—')[0].strip()}", a["url"])
            else:
                col.link_button(a["label"].split("—")[0].strip(), a["url"])
