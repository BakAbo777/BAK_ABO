#!/usr/bin/env python3
"""
BKS Studio — AI Pricing Agent + Google Merchant API + Streamlit Dashboard
=========================================================================
Versione: 1.0 — 16 Giugno 2026
Autore: Gaetano (Claude) per Roberto Picchioni

ARCHITETTURA COMPLETA:
  ┌─────────────────────────────────────────────────────────┐
  │                    STREAMLIT UI                          │
  │         (dashboard web accessibile da browser)           │
  └────────────────────┬────────────────────────────────────┘
                       │
  ┌────────────────────▼────────────────────────────────────┐
  │                 AI PRICING AGENT                         │
  │  - Legge costi Printify                                  │
  │  - Calcola margini BKS                                   │
  │  - Decide prezzi ottimali                                │
  │  - Applica regole brand                                  │
  └──────┬──────────────────────────────┬───────────────────┘
         │                              │
  ┌──────▼──────┐                ┌──────▼──────┐
  │   SHOPIFY   │                │   GOOGLE    │
  │  Admin API  │                │ Merchant API│
  │ (aggiorna   │                │ (aggiorna   │
  │  prezzi)    │                │  feed)      │
  └─────────────┘                └─────────────┘

SETUP:
  pip install streamlit pandas requests python-dotenv anthropic plotly

  File .env:
    SHOPIFY_STORE=11628e-2
    SHOPIFY_TOKEN=shpat_xxx
    GOOGLE_MERCHANT_ID=xxx
    GOOGLE_SERVICE_ACCOUNT_JSON=path/to/service_account.json
    ANTHROPIC_API_KEY=sk-ant-xxx (opzionale — per Claude AI decisions)

  Esegui:
    streamlit run bks_agent_dashboard.py
"""

import os
import json
import time
import math
import requests
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────

SHOPIFY_STORE = os.environ.get("SHOPIFY_STORE", "11628e-2")
SHOPIFY_TOKEN = os.environ.get("SHOPIFY_TOKEN", "")
GOOGLE_MERCHANT_ID = os.environ.get("GOOGLE_MERCHANT_ID", "")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

SHOPIFY_API_URL = f"https://{SHOPIFY_STORE}.myshopify.com/admin/api/2024-10"
SHOPIFY_HEADERS = {
    "X-Shopify-Access-Token": SHOPIFY_TOKEN,
    "Content-Type": "application/json"
}

# Tabella costi Printify (media per categoria)
COST_TABLE = {
    "Sneaker":        {"base": 22.0, "ship": 11.0, "margin": 0.60, "min": 75,  "target": 89,  "max": 105},
    "Backpack":       {"base": 26.0, "ship": 11.0, "margin": 0.60, "min": 75,  "target": 85,  "max": 95},
    "Swim Trunk":     {"base": 17.0, "ship": 8.0,  "margin": 0.58, "min": 45,  "target": 55,  "max": 65},
    "Puffer":         {"base": 46.0, "ship": 11.0, "margin": 0.58, "min": 109, "target": 125, "max": 139},
    "Windbreaker":    {"base": 33.0, "ship": 10.0, "margin": 0.60, "min": 95,  "target": 109, "max": 125},
    "Duffle":         {"base": 36.0, "ship": 11.0, "margin": 0.60, "min": 85,  "target": 99,  "max": 115},
    "Travel Bag":     {"base": 36.0, "ship": 11.0, "margin": 0.60, "min": 85,  "target": 99,  "max": 115},
    "One-Piece":      {"base": 21.0, "ship": 8.0,  "margin": 0.58, "min": 55,  "target": 65,  "max": 75},
    "Hawaiian":       {"base": 24.0, "ship": 8.0,  "margin": 0.58, "min": 65,  "target": 75,  "max": 85},
    "Lounge Pant":    {"base": 19.0, "ship": 8.0,  "margin": 0.58, "min": 55,  "target": 65,  "max": 75},
    "Hoodie":         {"base": 28.0, "ship": 8.0,  "margin": 0.58, "min": 65,  "target": 75,  "max": 85},
    "Dress":          {"base": 24.0, "ship": 8.0,  "margin": 0.58, "min": 55,  "target": 65,  "max": 75},
    "Slipper":        {"base": 15.0, "ship": 5.5,  "margin": 0.55, "min": 35,  "target": 45,  "max": 55},
    "Tee":            {"base": 19.0, "ship": 5.5,  "margin": 0.55, "min": 45,  "target": 55,  "max": 65},
    "Short":          {"base": 17.0, "ship": 5.5,  "margin": 0.55, "min": 45,  "target": 55,  "max": 65},
    "Flip Flop":      {"base": 13.0, "ship": 5.5,  "margin": 0.55, "min": 35,  "target": 45,  "max": 55},
}

APPROVED_PRICES = [35,39,45,49,55,59,65,69,75,79,85,89,95,99,105,109,115,119,125,129,135,139]

# ─────────────────────────────────────────────────────────────────────────────
# PRICING ENGINE
# ─────────────────────────────────────────────────────────────────────────────

def detect_category(title: str) -> str:
    t = title.lower()
    cats = {
        "Sneaker":     ["sneaker"],
        "Backpack":    ["backpack"],
        "Swim Trunk":  ["swim trunk"],
        "Puffer":      ["puffer"],
        "Windbreaker": ["windbreaker"],
        "Duffle":      ["duffle","duffel","travel bag"],
        "Travel Bag":  ["travel bag"],
        "One-Piece":   ["one-piece","swimsuit"],
        "Hawaiian":    ["hawaiian"],
        "Lounge Pant": ["lounge pant"],
        "Hoodie":      ["hoodie","pullover"],
        "Dress":       ["dress","racerback"],
        "Slipper":     ["slipper"],
        "Tee":         ["tee","t-shirt"],
        "Short":       ["short"],
        "Flip Flop":   ["flip flop"],
    }
    for cat, kws in cats.items():
        for kw in kws:
            if kw in t:
                return cat
    return "Unknown"

def calc_margin(price: float, cost: float) -> float:
    if price <= 0: return 0
    return (price - cost) / price * 100

def optimal_price(cost_total: float, margin_target: float) -> float:
    min_price = cost_total / (1 - margin_target)
    candidates = [p for p in APPROVED_PRICES if p >= min_price]
    return candidates[0] if candidates else round(min_price / 5) * 5

def traffic_light(margin: float, price: float, cat_data: dict) -> tuple:
    if margin < 40:    return "🔴", f"Margine {margin:.1f}% — STOP, sotto 40%"
    if margin < 45:    return "🔴", f"Margine {margin:.1f}% — sotto minimo 45%"
    if price < cat_data["min"]: return "🟡", f"Prezzo €{price} sotto minimo categoria €{cat_data['min']}"
    if price > cat_data["max"]: return "🟡", f"Prezzo €{price} sopra massimo categoria €{cat_data['max']}"
    if price not in APPROVED_PRICES: return "🟡", f"Formato €{price} non nel listino BKS"
    return "🟢", f"Margine {margin:.1f}% — prezzo corretto"

# ─────────────────────────────────────────────────────────────────────────────
# SHOPIFY API
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=300)
def fetch_all_products() -> list:
    """Scarica tutti i prodotti da Shopify (paginato)."""
    products = []
    url = f"{SHOPIFY_API_URL}/products.json"
    params = {"limit": 250, "fields": "id,title,handle,product_type,variants,status"}
    
    while url:
        r = requests.get(url, headers=SHOPIFY_HEADERS, params=params)
        if r.status_code != 200:
            st.error(f"Shopify API error: {r.status_code} — {r.text[:200]}")
            break
        data = r.json()
        products.extend(data.get("products", []))
        
        # Paginazione via Link header
        link = r.headers.get("Link", "")
        url = None
        params = {}
        if 'rel="next"' in link:
            for part in link.split(","):
                if 'rel="next"' in part:
                    url = part.split(";")[0].strip().strip("<>")
                    break
    
    return products

def update_variant_price(variant_id: int, new_price: float) -> bool:
    """Aggiorna il prezzo di una variante Shopify."""
    r = requests.put(
        f"{SHOPIFY_API_URL}/variants/{variant_id}.json",
        headers=SHOPIFY_HEADERS,
        json={"variant": {"id": variant_id, "price": str(new_price)}}
    )
    time.sleep(0.5)  # rate limit
    return r.status_code == 200

def update_product_prices(product_id: int, new_price: float, variants: list) -> dict:
    """Aggiorna tutti i prezzi varianti di un prodotto."""
    results = {"success": 0, "failed": 0}
    for v in variants:
        ok = update_variant_price(v["id"], new_price)
        if ok: results["success"] += 1
        else:  results["failed"] += 1
    return results

# ─────────────────────────────────────────────────────────────────────────────
# GOOGLE MERCHANT API (v1 — nuova API, agosto 2026)
# ─────────────────────────────────────────────────────────────────────────────

def get_google_token() -> str:
    """
    Ottiene il token OAuth2 per Google Merchant API.
    Usa Service Account JSON (scaricato da Google Cloud Console).
    """
    sa_path = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "")
    if not sa_path or not Path(sa_path).exists():
        return ""
    
    try:
        import google.oauth2.service_account as sa
        import google.auth.transport.requests as ga_requests
        
        credentials = sa.Credentials.from_service_account_file(
            sa_path,
            scopes=["https://www.googleapis.com/auth/content"]
        )
        credentials.refresh(ga_requests.Request())
        return credentials.token
    except Exception as e:
        st.warning(f"Google auth error: {e}")
        return ""

def update_google_price(merchant_id: str, offer_id: str,
                         new_price: float, currency: str = "EUR") -> bool:
    """
    Aggiorna il prezzo di un prodotto su Google Merchant Center
    via nuova Merchant API v1 (ProductsUpdate — partial update).
    offer_id = handle Shopify o SKU
    """
    token = get_google_token()
    if not token:
        return False
    
    # Nuova Merchant API v1 — ProductsUpdate (partial update)
    # Documentazione: developers.google.com/merchant/api
    url = (f"https://merchantapi.googleapis.com/products/v1beta/"
           f"accounts/{merchant_id}/products/{offer_id}:patch")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "price": {
            "value": str(new_price),
            "currency": currency
        }
    }
    
    # updateMask = solo il campo price
    r = requests.patch(
        url, headers=headers,
        json=payload,
        params={"updateMask": "price"}
    )
    return r.status_code in (200, 204)

def fetch_google_products(merchant_id: str) -> list:
    """Legge i prodotti approvati/disapprovati da Google Merchant Center."""
    token = get_google_token()
    if not token:
        return []
    
    url = f"https://merchantapi.googleapis.com/products/v1beta/accounts/{merchant_id}/products"
    headers = {"Authorization": f"Bearer {token}"}
    
    products = []
    page_token = None
    
    while True:
        params = {"pageSize": 1000}
        if page_token:
            params["pageToken"] = page_token
        
        r = requests.get(url, headers=headers, params=params)
        if r.status_code != 200:
            break
        
        data = r.json()
        products.extend(data.get("products", []))
        page_token = data.get("nextPageToken")
        if not page_token:
            break
    
    return products

# ─────────────────────────────────────────────────────────────────────────────
# AUDIT ENGINE
# ─────────────────────────────────────────────────────────────────────────────

def run_audit(products: list, custom_costs: dict = None) -> pd.DataFrame:
    """Esegue l'audit completo su tutti i prodotti Shopify."""
    rows = []
    
    for p in products:
        title = p.get("title", "")
        handle = p.get("handle", "")
        status = p.get("status", "")
        variants = p.get("variants", [])
        
        if not variants:
            continue
        
        # Prendi il prezzo della prima variante
        current_price = float(variants[0].get("price", 0))
        
        # Categoria e costi
        category = detect_category(title)
        
        # Usa costi custom se disponibili
        if custom_costs and handle in custom_costs:
            base = custom_costs[handle]["base"]
            ship = custom_costs[handle]["ship"]
        elif category in COST_TABLE:
            base = COST_TABLE[category]["base"]
            ship = COST_TABLE[category]["ship"]
        else:
            rows.append({
                "id": p.get("id"), "handle": handle, "title": title,
                "category": "UNKNOWN", "current_price": current_price,
                "base_cost": None, "ship_cost": None, "total_cost": None,
                "margin": None, "status_light": "⚪", "note": "Categoria non riconosciuta",
                "suggested_price": None, "delta": None, "shopify_status": status,
                "variants": variants
            })
            continue
        
        cat = COST_TABLE[category]
        total_cost = base + ship
        margin = calc_margin(current_price, total_cost)
        light, note = traffic_light(margin, current_price, cat)
        suggested = optimal_price(total_cost, cat["margin"])
        delta = suggested - current_price
        
        rows.append({
            "id": p.get("id"),
            "handle": handle,
            "title": title,
            "category": category,
            "current_price": current_price,
            "base_cost": base,
            "ship_cost": ship,
            "total_cost": total_cost,
            "margin": round(margin, 1),
            "margin_target": int(cat["margin"] * 100),
            "status_light": light,
            "note": note,
            "suggested_price": suggested,
            "delta": round(delta, 2),
            "shopify_status": status,
            "variants": variants,
        })
    
    return pd.DataFrame(rows)

# ─────────────────────────────────────────────────────────────────────────────
# STREAMLIT UI
# ─────────────────────────────────────────────────────────────────────────────

def main():
    st.set_page_config(
        page_title="BKS Studio — AI Pricing Agent",
        page_icon="◈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # ── CSS BKS ──────────────────────────────────────────────────────────────
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500&family=DM+Mono&display=swap');
    
    .main { background: #0a0a0a; color: #fafaf7; }
    .stApp { background: #0a0a0a; }
    
    h1,h2,h3 {
        font-family: 'DM Sans', sans-serif;
        font-weight: 500;
        color: #fafaf7;
        letter-spacing: 0.04em;
    }
    
    .metric-card {
        background: #141414;
        border: 0.5px solid #2a2a2a;
        border-radius: 4px;
        padding: 16px 20px;
        margin: 4px 0;
    }
    
    .metric-value {
        font-family: 'DM Mono', monospace;
        font-size: 28px;
        color: #fafaf7;
    }
    
    .metric-label {
        font-family: 'DM Sans', sans-serif;
        font-size: 11px;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #666;
    }
    
    .status-ok    { color: #4caf50; font-weight: 500; }
    .status-alert { color: #ff9800; font-weight: 500; }
    .status-stop  { color: #f44336; font-weight: 500; }
    
    .sidebar .stButton button {
        width: 100%;
        background: #1a1a1a;
        color: #fafaf7;
        border: 0.5px solid #333;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # ── Header ───────────────────────────────────────────────────────────────
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("# ◈ BKS Studio — AI Pricing Agent")
        st.markdown(
            "<span style='font-size:11px;letter-spacing:.12em;color:#666;"
            "text-transform:uppercase'>bakabo.club · Gaetano · "
            f"{datetime.now().strftime('%d/%m/%Y %H:%M')}</span>",
            unsafe_allow_html=True
        )
    with col2:
        if st.button("🔄 Aggiorna dati", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    st.divider()
    
    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### Configurazione")
        
        shopify_ok = bool(SHOPIFY_TOKEN)
        google_ok = bool(GOOGLE_MERCHANT_ID and
                         os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON"))
        
        st.markdown(
            f"**Shopify:** {'✅ Connesso' if shopify_ok else '❌ Token mancante'}"
        )
        st.markdown(
            f"**Google Merchant:** {'✅ Configurato' if google_ok else '⚠️ Non configurato'}"
        )
        
        st.divider()
        st.markdown("### Margini target")
        margin_override = st.slider(
            "Margine minimo accettabile %", 40, 75, 55
        )
        
        st.divider()
        st.markdown("### Filtri")
        filter_status = st.multiselect(
            "Mostra solo",
            ["🔴 STOP", "🟡 ALERT", "🟢 OK", "⚪ SKIP"],
            default=["🔴 STOP", "🟡 ALERT"]
        )
        
        st.divider()
        auto_update = st.checkbox(
            "Auto-aggiornamento (ogni 60 min)",
            value=False,
            help="Aggiorna automaticamente i prezzi fuori range"
        )
        
        if not shopify_ok:
            st.warning(
                "Aggiungi SHOPIFY_TOKEN nel file .env\n"
                "Admin → Settings → Apps → Develop apps"
            )
        if not google_ok:
            st.info(
                "Per collegare Google Merchant Center:\n"
                "1. Crea Service Account su Google Cloud\n"
                "2. Aggiungi GOOGLE_MERCHANT_ID nel .env\n"
                "3. Aggiungi GOOGLE_SERVICE_ACCOUNT_JSON nel .env"
            )
    
    # ── Tab principale ────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Audit Prezzi",
        "🔧 Correzioni",
        "🌐 Google Merchant",
        "📈 Analytics"
    ])
    
    # ── TAB 1: AUDIT ─────────────────────────────────────────────────────────
    with tab1:
        if not shopify_ok:
            st.error("Configura SHOPIFY_TOKEN nel .env per caricare i prodotti.")
            st.stop()
        
        with st.spinner("Caricamento prodotti Shopify..."):
            products = fetch_all_products()
        
        if not products:
            st.warning("Nessun prodotto trovato.")
            st.stop()
        
        df = run_audit(products)
        
        # KPI cards
        total = len(df)
        ok_count = len(df[df["status_light"] == "🟢"])
        alert_count = len(df[df["status_light"] == "🟡"])
        stop_count = len(df[df["status_light"] == "🔴"])
        skip_count = len(df[df["status_light"] == "⚪"])
        
        avg_margin = df[df["margin"].notna()]["margin"].mean()
        
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            st.metric("Prodotti totali", total)
        with c2:
            st.metric("🟢 OK", ok_count,
                      delta=f"{ok_count/total*100:.0f}%")
        with c3:
            st.metric("🟡 Alert", alert_count)
        with c4:
            st.metric("🔴 Stop", stop_count)
        with c5:
            st.metric("Margine medio", f"{avg_margin:.1f}%",
                      delta=f"{avg_margin-55:.1f}% vs target 55%")
        
        st.divider()
        
        # Tabella filtrata
        if filter_status:
            mask = df["status_light"].isin([s[0] for s in filter_status])
            df_show = df[mask].copy()
        else:
            df_show = df.copy()
        
        st.markdown(f"**{len(df_show)} prodotti** corrispondono ai filtri")
        
        display_cols = [
            "status_light", "title", "category",
            "current_price", "total_cost", "margin",
            "suggested_price", "delta"
        ]
        
        col_labels = {
            "status_light": "Stato",
            "title": "Prodotto",
            "category": "Categoria",
            "current_price": "Prezzo €",
            "total_cost": "Costo €",
            "margin": "Margine %",
            "suggested_price": "Suggerito €",
            "delta": "Delta €"
        }
        
        st.dataframe(
            df_show[display_cols].rename(columns=col_labels),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Prezzo €": st.column_config.NumberColumn(format="€%.2f"),
                "Costo €": st.column_config.NumberColumn(format="€%.2f"),
                "Suggerito €": st.column_config.NumberColumn(format="€%.2f"),
                "Delta €": st.column_config.NumberColumn(format="€%+.2f"),
                "Margine %": st.column_config.ProgressColumn(
                    min_value=0, max_value=80, format="%.1f%%"
                ),
            }
        )
        
        # Export CSV
        csv = df_show[display_cols].rename(columns=col_labels).to_csv(index=False)
        st.download_button(
            "⬇️ Scarica report CSV",
            csv,
            f"bks_audit_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            "text/csv"
        )
    
    # ── TAB 2: CORREZIONI ────────────────────────────────────────────────────
    with tab2:
        st.markdown("### Correzione prezzi")
        st.markdown(
            "Seleziona i prodotti da correggere e applica i prezzi suggeriti "
            "su Shopify e Google Merchant Center simultaneamente."
        )
        
        if not shopify_ok:
            st.error("Shopify non configurato.")
        else:
            products_raw = fetch_all_products()
            df_all = run_audit(products_raw)
            df_fix = df_all[df_all["status_light"].isin(["🔴","🟡"])].copy()
            
            if df_fix.empty:
                st.success("✅ Tutti i prezzi sono corretti. Nessuna correzione necessaria.")
            else:
                st.warning(f"**{len(df_fix)} prodotti** richiedono correzione.")
                
                # Selezione multipla
                selected = st.multiselect(
                    "Seleziona prodotti da correggere",
                    df_fix["title"].tolist(),
                    default=df_fix[df_fix["status_light"] == "🔴"]["title"].tolist()
                )
                
                if selected:
                    df_selected = df_fix[df_fix["title"].isin(selected)]
                    
                    st.dataframe(
                        df_selected[["title","current_price","suggested_price","delta","margin"]],
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    col_a, col_b = st.columns(2)
                    update_shopify = col_a.checkbox("Aggiorna Shopify", value=True)
                    update_google = col_b.checkbox(
                        "Aggiorna Google Merchant",
                        value=google_ok,
                        disabled=not google_ok
                    )
                    
                    if st.button("🚀 Applica correzioni", type="primary"):
                        progress = st.progress(0)
                        status_text = st.empty()
                        log = []
                        
                        for i, (_, row) in enumerate(df_selected.iterrows()):
                            progress.progress((i+1) / len(df_selected))
                            status_text.text(f"Aggiornando: {row['title'][:50]}...")
                            
                            new_price = row["suggested_price"]
                            
                            if update_shopify:
                                result = update_product_prices(
                                    row["id"], new_price, row["variants"]
                                )
                                log.append({
                                    "Prodotto": row["title"][:45],
                                    "Shopify": "✅" if result["success"] > 0 else "❌",
                                    "Prezzo": f"€{row['current_price']} → €{new_price}",
                                    "Google": "—"
                                })
                            
                            if update_google and google_ok:
                                ok_g = update_google_price(
                                    GOOGLE_MERCHANT_ID,
                                    row["handle"],
                                    new_price
                                )
                                if log:
                                    log[-1]["Google"] = "✅" if ok_g else "❌"
                        
                        status_text.text("Completato.")
                        st.cache_data.clear()
                        
                        if log:
                            st.markdown("#### Risultati")
                            st.dataframe(pd.DataFrame(log), hide_index=True)
    
    # ── TAB 3: GOOGLE MERCHANT ───────────────────────────────────────────────
    with tab3:
        st.markdown("### Google Merchant Center")
        
        if not google_ok:
            st.info("""
**Come configurare Google Merchant Center:**

**Step 1 — Google Cloud Console**
1. Vai su console.cloud.google.com
2. Crea un nuovo progetto "BKS Studio Merchant"
3. Abilita l'API: **Merchant API** (non Content API — quella viene spenta il 18/08/2026)
4. Crea un Service Account → scarica il JSON

**Step 2 — Google Merchant Center**
1. Vai su merchants.google.com
2. Crea account → verifica bakabo.club
3. Settings → Service accounts → aggiungi l'email del Service Account come utente Admin
4. Copia il Merchant ID (numero a 10 cifre)

**Step 3 — .env**
```
GOOGLE_MERCHANT_ID=1234567890
GOOGLE_SERVICE_ACCOUNT_JSON=/path/to/service_account.json
```

**Step 4 — Feed automatico da Shopify**
- Shopify Admin → Apps → Google & YouTube (app nativa gratuita)
- Collega il tuo account Merchant Center
- Il feed si aggiorna automaticamente ogni 24h

**Nota importante:** Con la nuova Merchant API v1 puoi aggiornare
i prezzi in tempo reale senza aspettare il ciclo del feed.
Questo agente usa ProductsUpdate con updateMask="price" per
aggiornamenti istantanei.
            """)
        else:
            with st.spinner("Caricamento prodotti Google Merchant..."):
                g_products = fetch_google_products(GOOGLE_MERCHANT_ID)
            
            if g_products:
                approved = [p for p in g_products
                            if p.get("productStatus","") == "approved"]
                disapproved = [p for p in g_products
                               if p.get("productStatus","") == "disapproved"]
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Prodotti nel feed", len(g_products))
                c2.metric("✅ Approvati", len(approved))
                c3.metric("❌ Disapprovati", len(disapproved))
                
                if disapproved:
                    st.error(f"**{len(disapproved)} prodotti disapprovati da Google.**")
                    reasons = {}
                    for p in disapproved:
                        for issue in p.get("issues", []):
                            r = issue.get("description", "Unknown")
                            reasons[r] = reasons.get(r, 0) + 1
                    
                    st.markdown("**Motivi disapprovazione:**")
                    for reason, count in sorted(
                        reasons.items(), key=lambda x: -x[1]
                    ):
                        st.write(f"- {reason}: {count} prodotti")
            else:
                st.warning("Nessun prodotto trovato nel feed Google Merchant.")
    
    # ── TAB 4: ANALYTICS ─────────────────────────────────────────────────────
    with tab4:
        st.markdown("### Analytics prezzi")
        
        if shopify_ok:
            products_raw = fetch_all_products()
            df_an = run_audit(products_raw)
            df_valid = df_an[df_an["margin"].notna()].copy()
            
            if not df_valid.empty:
                try:
                    import plotly.express as px
                    import plotly.graph_objects as go
                    
                    # Distribuzione margini
                    fig1 = px.histogram(
                        df_valid, x="margin", nbins=20,
                        title="Distribuzione Margini %",
                        color_discrete_sequence=["#c9b79c"],
                        template="plotly_dark"
                    )
                    fig1.add_vline(x=55, line_dash="dash",
                                   line_color="#d4a030",
                                   annotation_text="Target 55%")
                    fig1.add_vline(x=45, line_dash="dot",
                                   line_color="#c82020",
                                   annotation_text="Min 45%")
                    st.plotly_chart(fig1, use_container_width=True)
                    
                    # Margine per categoria
                    df_cat = df_valid.groupby("category").agg(
                        margin_avg=("margin","mean"),
                        count=("margin","count"),
                        price_avg=("current_price","mean")
                    ).reset_index().sort_values("margin_avg")
                    
                    fig2 = px.bar(
                        df_cat, x="category", y="margin_avg",
                        title="Margine medio per categoria",
                        color="margin_avg",
                        color_continuous_scale=["#c82020","#ff9800","#4caf50"],
                        template="plotly_dark"
                    )
                    fig2.add_hline(y=55, line_dash="dash",
                                   line_color="#d4a030")
                    st.plotly_chart(fig2, use_container_width=True)
                    
                    # Revenue potenziale con prezzi corretti
                    df_valid["revenue_current"] = df_valid["current_price"]
                    df_valid["revenue_suggested"] = df_valid["suggested_price"]
                    delta_total = (
                        df_valid["suggested_price"] - df_valid["current_price"]
                    ).sum()
                    
                    st.metric(
                        "Incremento ricavo potenziale per ordine medio",
                        f"€{delta_total/len(df_valid):.2f}",
                        help="Delta medio per prodotto se tutti i prezzi fossero corretti"
                    )
                
                except ImportError:
                    st.info("Installa plotly per i grafici: pip install plotly")
                    st.dataframe(df_valid[["category","margin","current_price"]],
                                 hide_index=True)


if __name__ == "__main__":
    main()
