"""BKS Studio — Analytics Dashboard
Vendite, ordini, revenue per collezione, conversioni.
Dati da Shopify Admin API — aggiornamento manuale su richiesta.
"""
from __future__ import annotations

import os
import sys
from collections import defaultdict
from datetime import datetime, date, timedelta
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="BKS Analytics", page_icon="◉", layout="wide")

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

BKS_COLLECTIONS = {
    "bks-hours": ("BKS Hours", "#c8c4be"),
    "bks-origin": ("BKS Origin", "#489808"),
    "bks-glyph": ("BKS Glyph", "#d4a030"),
    "bks-marker": ("BKS Marker", "#c04418"),
    "bks-riviera": ("BKS Riviera", "#0ca898"),
    "bks-pulse": ("BKS Pulse", "#8888cc"),
    "bks-token": ("BKS Token", "#9828d8"),
    "bks-flag": ("BKS Flag", "#c82020"),
}


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


def env(k: str, fallback: str = "") -> str:
    return os.environ.get(k, fallback)


def shopify_headers() -> dict[str, str]:
    return {
        "X-Shopify-Access-Token": env("SHOPIFY_ADMIN_TOKEN"),
        "Content-Type": "application/json",
    }


def shopify_base() -> str:
    domain = env("SHOPIFY_MYSHOPIFY_DOMAIN")
    version = env("SHOPIFY_API_VERSION", "2025-01")
    return f"https://{domain}/admin/api/{version}"


@st.cache_data(ttl=300)
def fetch_orders(days: int = 30) -> list[dict]:
    since = (datetime.utcnow() - timedelta(days=days)).isoformat() + "Z"
    orders = []
    url = f"{shopify_base()}/orders.json?status=any&created_at_min={since}&limit=250&fields=id,created_at,total_price,financial_status,line_items,tags"
    try:
        while url:
            r = requests.get(url, headers=shopify_headers(), timeout=15, verify=False)
            if not r.ok:
                break
            batch = r.json().get("orders", [])
            orders.extend(batch)
            link = r.headers.get("Link", "")
            url = None
            for part in link.split(","):
                if 'rel="next"' in part:
                    url = part.strip().strip("<>").split(";")[0].strip()
                    break
    except Exception:
        pass
    return orders


@st.cache_data(ttl=600)
def fetch_products_summary() -> list[dict]:
    products = []
    url = f"{shopify_base()}/products.json?limit=250&fields=id,title,handle,product_type,tags,variants"
    try:
        while url:
            r = requests.get(url, headers=shopify_headers(), timeout=15, verify=False)
            if not r.ok:
                break
            products.extend(r.json().get("products", []))
            link = r.headers.get("Link", "")
            url = None
            for part in link.split(","):
                if 'rel="next"' in part:
                    url = part.strip().strip("<>").split(";")[0].strip()
                    break
    except Exception:
        pass
    return products


def collection_from_product(product: dict) -> str:
    tags = product.get("tags", "")
    handle = product.get("handle", "")
    for coll_handle in BKS_COLLECTIONS:
        slug = coll_handle.replace("bks-", "")
        if slug in tags.lower() or slug in handle.lower():
            return coll_handle
    return "other"


def build_order_metrics(orders: list[dict]) -> dict:
    if not orders:
        return {"total_revenue": 0, "order_count": 0, "avg_order": 0, "paid": 0}
    paid = [o for o in orders if o.get("financial_status") == "paid"]
    total_rev = sum(float(o.get("total_price", 0)) for o in paid)
    return {
        "total_revenue": round(total_rev, 2),
        "order_count": len(orders),
        "paid_count": len(paid),
        "avg_order": round(total_rev / len(paid), 2) if paid else 0,
    }


def build_daily_revenue(orders: list[dict]) -> pd.DataFrame:
    daily: dict[str, float] = defaultdict(float)
    for o in orders:
        if o.get("financial_status") == "paid":
            day = o.get("created_at", "")[:10]
            daily[day] += float(o.get("total_price", 0))
    if not daily:
        return pd.DataFrame(columns=["Data", "Revenue €"])
    rows = sorted(daily.items())
    return pd.DataFrame(rows, columns=["Data", "Revenue €"]).set_index("Data")


def build_top_products(orders: list[dict], limit: int = 10) -> pd.DataFrame:
    counts: dict[str, int] = defaultdict(int)
    revenue: dict[str, float] = defaultdict(float)
    for o in orders:
        if o.get("financial_status") != "paid":
            continue
        for item in o.get("line_items", []):
            title = item.get("title", "n/d")
            qty = int(item.get("quantity", 0))
            price = float(item.get("price", 0)) * qty
            counts[title] += qty
            revenue[title] += price
    if not counts:
        return pd.DataFrame(columns=["Prodotto", "Venduto", "Revenue €"])
    rows = [{"Prodotto": k, "Venduto": counts[k], "Revenue €": round(revenue[k], 2)} for k in counts]
    df = pd.DataFrame(rows).sort_values("Venduto", ascending=False).head(limit)
    return df.reset_index(drop=True)


# ─────────────────────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────────────────────

st.title("◉ BKS Analytics")
st.caption("Revenue, ordini, top prodotti — dati da Shopify Admin API.")

# Controls
col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([2, 1, 1])
with col_ctrl1:
    period = st.selectbox("Periodo", ["Ultimi 7 giorni", "Ultimi 30 giorni", "Ultimi 90 giorni"], index=1)
with col_ctrl2:
    days_map = {"Ultimi 7 giorni": 7, "Ultimi 30 giorni": 30, "Ultimi 90 giorni": 90}
    days = days_map[period]
with col_ctrl3:
    if st.button("🔄 Aggiorna dati"):
        st.cache_data.clear()
        st.rerun()

# Load data
with st.spinner("Caricamento ordini Shopify..."):
    orders = fetch_orders(days)
    products = fetch_products_summary()

metrics = build_order_metrics(orders)

# KPIs
st.divider()
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Revenue", f"€{metrics['total_revenue']:,.2f}")
k2.metric("Ordini totali", metrics["order_count"])
k3.metric("Ordini pagati", metrics.get("paid_count", 0))
k4.metric("Valore medio ordine", f"€{metrics['avg_order']:,.2f}")
k5.metric("Prodotti catalogo", len(products))

# Revenue trend chart
st.divider()
st.subheader(f"Revenue giornaliera — {period}")
daily_df = build_daily_revenue(orders)
if not daily_df.empty:
    st.line_chart(daily_df)
else:
    st.info("Nessun dato ordine disponibile. Verifica token Shopify Admin.")

# Top products
st.subheader("Top prodotti per volume")
top_df = build_top_products(orders)
if not top_df.empty:
    col_chart, col_table = st.columns([3, 2])
    with col_chart:
        chart_df = top_df.set_index("Prodotto")[["Venduto"]].head(8)
        st.bar_chart(chart_df)
    with col_table:
        st.dataframe(top_df, hide_index=True, use_container_width=True)
else:
    st.info("Nessun prodotto venduto nel periodo selezionato.")

# Orders by status
st.divider()
st.subheader("Ordini per stato")
if orders:
    status_counts: dict[str, int] = defaultdict(int)
    for o in orders:
        status_counts[o.get("financial_status", "unknown")] += 1
    status_df = pd.DataFrame([
        {"Stato": k, "Ordini": v} for k, v in sorted(status_counts.items(), key=lambda x: -x[1])
    ])
    st.dataframe(status_df, hide_index=True, use_container_width=True)
else:
    st.info("Nessun ordine nel periodo.")

# Product catalog summary
st.divider()
st.subheader("Catalogo prodotti")
if products:
    ptype_counts: dict[str, int] = defaultdict(int)
    for p in products:
        ptype_counts[p.get("product_type", "—") or "—"] += 1
    type_df = pd.DataFrame([
        {"Tipo prodotto": k, "N° prodotti": v}
        for k, v in sorted(ptype_counts.items(), key=lambda x: -x[1])
    ])
    col_cat, col_stat = st.columns([2, 1])
    with col_cat:
        st.bar_chart(type_df.set_index("Tipo prodotto"))
    with col_stat:
        total_variants = sum(
            len(p.get("variants", [])) for p in products
        )
        st.metric("Prodotti totali", len(products))
        st.metric("Varianti totali", total_variants)
        st.metric("Tipi prodotto", len(ptype_counts))
else:
    st.info("Impossibile caricare il catalogo.")

# Raw orders
st.divider()
with st.expander("Dettaglio ordini (raw)"):
    if orders:
        rows = []
        for o in orders:
            rows.append({
                "ID": o.get("id"),
                "Data": o.get("created_at", "")[:10],
                "Revenue €": float(o.get("total_price", 0)),
                "Stato": o.get("financial_status"),
                "Tag": o.get("tags", ""),
            })
        raw_df = pd.DataFrame(rows).sort_values("Data", ascending=False)
        st.dataframe(raw_df, hide_index=True, use_container_width=True)
    else:
        st.info("Nessun ordine da mostrare.")

# Links
st.divider()
c1, c2, c3 = st.columns(3)
c1.link_button("Shopify Analytics →", "https://admin.shopify.com/store/bakabo/analytics")
c2.link_button("Google Analytics →", "https://analytics.google.com")
c3.link_button("Google Merchant →", "https://merchants.google.com")
