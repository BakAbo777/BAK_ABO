"""BKS Studio — Marketing Hub
Offerte, sconti, coupon, campagne, UTM builder.
Gestione centralizzata delle leve di marketing.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, date, timedelta
from pathlib import Path
from urllib.parse import urlencode

import requests
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import bks_nav

st.set_page_config(page_title="BKS Marketing", page_icon="◈", layout="wide")
bks_nav.render("marketing")
MARKETING_DIR = BASE_DIR / "output" / "marketing"
MARKETING_DIR.mkdir(parents=True, exist_ok=True)

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

MEMBER_TIERS = {
    "Lead": 0,
    "Iron": 5,
    "Brass": 10,
    "Silver": 15,
    "Gold": 20,
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


def fetch_discount_codes() -> list[dict]:
    try:
        r = requests.get(
            f"{shopify_base()}/discount_codes.json?limit=50",
            headers=shopify_headers(),
            timeout=10,
            verify=False,
        )
        if r.ok:
            return r.json().get("discount_codes", [])
    except Exception:
        pass
    return []


def fetch_price_rules() -> list[dict]:
    try:
        r = requests.get(
            f"{shopify_base()}/price_rules.json?limit=50",
            headers=shopify_headers(),
            timeout=10,
            verify=False,
        )
        if r.ok:
            return r.json().get("price_rules", [])
    except Exception:
        pass
    return []


def create_price_rule(title: str, pct: float, usage_limit: int | None, ends_at: str | None) -> dict | None:
    payload: dict = {
        "price_rule": {
            "title": title,
            "value_type": "percentage",
            "value": f"-{pct}",
            "customer_selection": "all",
            "target_type": "line_item",
            "target_selection": "all",
            "allocation_method": "across",
            "starts_at": datetime.utcnow().isoformat() + "Z",
        }
    }
    if usage_limit:
        payload["price_rule"]["usage_limit"] = usage_limit
    if ends_at:
        payload["price_rule"]["ends_at"] = ends_at + "T23:59:59Z"
    try:
        r = requests.post(
            f"{shopify_base()}/price_rules.json",
            headers=shopify_headers(),
            json=payload,
            timeout=15,
            verify=False,
        )
        if r.ok:
            return r.json().get("price_rule")
    except Exception as e:
        st.error(f"Errore API: {e}")
    return None


def create_discount_code(price_rule_id: int, code: str) -> dict | None:
    try:
        r = requests.post(
            f"{shopify_base()}/price_rules/{price_rule_id}/discount_codes.json",
            headers=shopify_headers(),
            json={"discount_code": {"code": code}},
            timeout=10,
            verify=False,
        )
        if r.ok:
            return r.json().get("discount_code")
    except Exception as e:
        st.error(f"Errore codice: {e}")
    return None


# ─────────────────────────────────────────────────────────────
# UI
# ─────────────────────────────────────────────────────────────

st.title("◈ BKS Marketing Hub")
st.caption("Offerte, sconti, coupon, UTM builder — gestione centralizzata delle leve di conversione.")

tabs = st.tabs(["Active Offers", "Create Offer", "Member Discounts", "UTM Builder", "Email Triggers"])

# ── TAB 1 — Active Offers ────────────────────────────────────
with tabs[0]:
    st.subheader("Regole sconto attive")
    if st.button("Aggiorna lista", key="refresh_rules"):
        st.cache_data.clear()

    rules = fetch_price_rules()
    if rules:
        for rule in rules:
            ends_raw = rule.get("ends_at")
            ends_str = ends_raw[:10] if ends_raw else "∞"
            status = "🟢 attiva"
            if ends_raw:
                try:
                    if datetime.fromisoformat(ends_raw.replace("Z", "+00:00")).replace(tzinfo=None) < datetime.utcnow():
                        status = "🔴 scaduta"
                except Exception:
                    pass
            col1, col2, col3, col4 = st.columns([3, 2, 1, 1])
            col1.markdown(f"**{rule.get('title', 'n/d')}**")
            col2.markdown(f"Sconto: `{rule.get('value', '?')}%`")
            col3.markdown(f"Scade: {ends_str}")
            col4.markdown(status)
            st.divider()
    else:
        st.info("Nessuna regola attiva o API non configurata.")

# ── TAB 2 — Create Offer ─────────────────────────────────────
with tabs[1]:
    st.subheader("Crea nuova offerta")
    col1, col2 = st.columns(2)
    with col1:
        offer_title = st.text_input("Nome offerta (interno)", value=f"BKS-DROP-{date.today().strftime('%d%m')}")
        offer_code = st.text_input("Codice sconto (pubblico)", value=f"BKS{date.today().strftime('%m%y')}")
        offer_pct = st.slider("Percentuale sconto", 5, 50, 15, step=5)
    with col2:
        has_limit = st.checkbox("Limite utilizzi")
        usage_limit = st.number_input("Massimo utilizzi", min_value=1, value=100) if has_limit else None
        has_end = st.checkbox("Data scadenza")
        ends_date = str(st.date_input("Scade il", value=date.today() + timedelta(days=7))) if has_end else None

    if st.button("🎯 Crea offerta Shopify", type="primary"):
        with st.spinner("Creando regola sconto..."):
            rule = create_price_rule(offer_title, offer_pct, int(usage_limit) if usage_limit else None, ends_date)
            if rule:
                code_obj = create_discount_code(rule["id"], offer_code.upper())
                if code_obj:
                    st.success(f"✓ Offerta creata! Codice: **{code_obj['code']}** — {offer_pct}% su tutti i prodotti")
                    st.code(f"bakabo.club/?discount={code_obj['code']}", language="text")
                else:
                    st.warning("Regola creata ma errore nel codice sconto. Verifica Shopify admin.")
            else:
                st.error("Errore creazione. Verifica token API Shopify.")

# ── TAB 3 — Member Discounts ─────────────────────────────────
with tabs[2]:
    st.subheader("Sconti per tier membership")
    st.markdown("Struttura sconti automatici per livello Metal. Ogni tier ha un codice dedicato da comunicare via email.")

    tier_cols = st.columns(len(MEMBER_TIERS))
    for col, (tier, pct) in zip(tier_cols, MEMBER_TIERS.items()):
        with col:
            if pct > 0:
                code = f"BKS{tier.upper()}"
                st.metric(tier, f"{pct}% off", delta=None)
                st.code(code, language="text")
                if st.button(f"Crea {code}", key=f"create_tier_{tier}"):
                    with st.spinner(f"Creando sconto {tier}..."):
                        rule = create_price_rule(f"BKS Member {tier}", pct, None, None)
                        if rule:
                            dc = create_discount_code(rule["id"], code)
                            if dc:
                                st.success(f"✓ {code} creato")
            else:
                st.metric(tier, "0% (free)", delta=None)
                st.caption("Tier base — nessuno sconto")

    st.divider()
    st.subheader("Codici tier attivi")
    all_rules = fetch_price_rules()
    tier_rules = [r for r in all_rules if any(t in r.get("title", "") for t in MEMBER_TIERS.keys())]
    if tier_rules:
        for r in tier_rules:
            st.write(f"• **{r['title']}** — {r.get('value', '?')}%")
    else:
        st.info("Nessun codice tier trovato. Usa i bottoni sopra per crearli.")

# ── TAB 4 — UTM Builder ───────���──────────────────────────────
with tabs[3]:
    st.subheader("UTM Link Builder")
    st.caption("Genera URL tracciati per tutte le campagne marketing. Copia e usa in post/email.")

    col1, col2 = st.columns(2)
    with col1:
        base_url = st.text_input("URL base", value="https://bakabo.club/collections/all")
        source = st.selectbox("Source", ["instagram", "facebook", "telegram", "email", "tiktok", "pinterest", "google"])
        medium = st.selectbox("Medium", ["social", "cpc", "email", "organic", "referral", "story", "reel"])
    with col2:
        campaign = st.text_input("Campaign", value=f"bks-drop-{date.today().strftime('%m%y')}")
        content = st.text_input("Content (A/B test)", value="")
        term = st.text_input("Term (keyword)", value="")

    params = {"utm_source": source, "utm_medium": medium, "utm_campaign": campaign}
    if content:
        params["utm_content"] = content
    if term:
        params["utm_term"] = term
    full_url = f"{base_url}?{urlencode(params)}"

    st.code(full_url, language="text")
    st.caption(f"Link pronto per {source} / {medium}")

    st.divider()
    st.subheader("Quick UTM per ogni collezione")
    for handle, (name, color) in BKS_COLLECTIONS.items():
        url = f"https://bakabo.club/collections/{handle}?utm_source=instagram&utm_medium=social&utm_campaign=bks-{handle}-{date.today().strftime('%m%y')}"
        st.write(f"**{name}**")
        st.code(url, language="text")

# ── TAB 5 — Email Triggers ───────���───────────────────────────
with tabs[4]:
    st.subheader("Trigger email membership")
    st.caption("Trigger email definiti nella Members Skill. Usa come checklist per la configurazione Shopify Email / Klaviyo.")

    triggers = [
        {"evento": "Welcome Lead", "quando": "Prima registrazione", "oggetto": "Benvenuto nel club BKS", "tier": "Lead"},
        {"evento": "Tier Iron", "quando": "1° acquisto completato", "oggetto": "Hai guadagnato Iron — il tuo 5% ti aspetta", "tier": "Iron"},
        {"evento": "Tier Brass", "quando": "3 acquisti totali", "oggetto": "Sei arrivato a Brass — sconto 10% attivo", "tier": "Brass"},
        {"evento": "Tier Silver", "quando": "€300 spesi", "oggetto": "Silver member — benvenuto nell'élite BKS", "tier": "Silver"},
        {"evento": "Tier Gold", "quando": "€800 spesi", "oggetto": "Gold: sei al vertice del club BKS", "tier": "Gold"},
        {"evento": "Drop reminder", "quando": "72h prima del drop", "oggetto": "Nuovo drop BKS — accesso anticipato per te", "tier": "tutti"},
        {"evento": "Cart abandonment", "quando": "6h dopo abbandono carrello", "oggetto": "Il tuo capo BKS ti aspetta", "tier": "tutti"},
        {"evento": "Post-purchase", "quando": "24h dopo acquisto", "oggetto": "Il tuo ordine è in stampa — grazie", "tier": "tutti"},
        {"evento": "Win-back", "quando": "90 giorni senza acquisti", "oggetto": "Ci manchi — ecco una sorpresa per te", "tier": "tutti"},
    ]

    for t in triggers:
        with st.expander(f"**{t['evento']}** — {t['quando']}"):
            c1, c2 = st.columns([2, 1])
            c1.write(f"📧 Oggetto: *{t['oggetto']}*")
            c2.write(f"Tier: **{t['tier']}**")
            disc = MEMBER_TIERS.get(t["tier"])
            if disc and disc > 0:
                c1.code(f"BKS{t['tier'].upper()}", language="text")
