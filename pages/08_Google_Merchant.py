"""BKS Google Merchant Center — monitoring + fix panel."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import bks_nav

st.set_page_config(page_title="Google Merchant · BKS", page_icon="🛒", layout="wide")
bks_nav.render("merchant")

try:
    from streamlit_master import inject_bks_theme
    inject_bks_theme()
except Exception:
    pass

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("Google Merchant Center")
st.caption("GMC ID: 5295165689 · bakabo.club")

# ── Load last sync report ───────────────────────────────────────────────────────
SYNC_REPORT = ROOT / "output" / "channel_sync_report.json"

def load_report() -> dict:
    if SYNC_REPORT.exists():
        return json.loads(SYNC_REPORT.read_text(encoding="utf-8"))
    return {}

report = load_report()

# ── Status cards ───────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)

with col1:
    shopify = report.get("shopify", {})
    st.metric("Shopify active", shopify.get("active", "—"))
    st.caption(f"draft: {shopify.get('draft', '—')}")

with col2:
    printify = report.get("printify", {})
    st.metric("Printify total", printify.get("total", "—"))
    st.caption(f"linked to Shopify: {printify.get('published_linked', '—')}")

with col3:
    gmc = report.get("gmc", {})
    ag = gmc.get("age_group_ok", "?")
    gn = gmc.get("gender_ok", "?")
    chk = gmc.get("checked", 5)
    st.metric("GMC attributes (sample)", f"{ag}/{chk}")
    st.caption(f"gender: {gn}/{chk} · condition set")

with col4:
    sync_at = report.get("sync_at", "")
    if sync_at:
        dt = datetime.fromisoformat(sync_at.replace("Z", "+00:00"))
        label = dt.strftime("%d/%m %H:%M UTC")
    else:
        label = "Never"
    st.metric("Last sync", label)
    st.caption(f"feed bump: {report.get('feed_bump', '—')}")

st.divider()

# ── Issue table ─────────────────────────────────────────────────────────────────
st.subheader("Issue Status")

issues = [
    {
        "Issue": "identifier_exists = no (POD)",
        "Impatto": "96.4K Not Approved → migliorerà",
        "Fix": "✅ Metafield impostato — 203/203",
        "Azione": "Attendi re-crawl Google (24-72h)",
    },
    {
        "Issue": "age_group / gender / condition",
        "Impatto": "Taglia/Genere/Età mancanti",
        "Fix": "✅ 203/203 — adult/male·female·unisex/new",
        "Azione": "Attendi re-crawl Google",
    },
    {
        "Issue": "Dati inventario locale (76.5%)",
        "Impatto": "26.9K listings flaggati",
        "Fix": "⚠️ Google Business Profile — non Shopify",
        "Azione": "business.google.com → Sede → tipo → Area di servizio",
    },
    {
        "Issue": "Pagina prodotto non disponibile (27.4%)",
        "Impatto": "9.6K URL stale in cache Google",
        "Fix": "⏳ Auto-fix con re-crawl",
        "Azione": "Attendi 24-48h dopo feed bump",
    },
    {
        "Issue": "Korea business registration",
        "Impatto": "24 prodotti bloccati per Corea",
        "Fix": "⚠️ Rimuovi mercato Corea del Sud",
        "Azione": "GMC → Settings → Countries → Remove South Korea",
    },
]

import pandas as pd
st.dataframe(pd.DataFrame(issues), use_container_width=True, hide_index=True)

st.divider()

# ── Local Inventory Feed ────────────────────────────────────────────────────────
st.subheader("Local Inventory Feed")

_LOCAL_INV_OUTPUT = ROOT / "output" / "google_local_inventory_feed.tsv"
_LOCAL_INV_SUMMARY = ROOT / "output" / "google_local_inventory_summary.json"

_local_tab, _biz_tab, _korea_tab = st.tabs(["Feed Generator", "Business Profile Fix", "Korea Fix"])

with _local_tab:
    st.markdown("""
**Causa dell'errore**: Google Business Profile ha una sede fisica (Via Monte Vettore 1, Terni)
→ GMC si aspetta un Local Inventory Feed per quella sede.
**BKS è online-only/POD** → il feed marca tutto `out_of_stock` per eliminare l'errore.
""")

    col_gen, col_status = st.columns([2, 1])
    with col_gen:
        store_code = st.text_input(
            "Store code (da Google Business Profile)",
            value="BKS_TERNI",
            help="Trovalo in: business.google.com → Profilo → Codice negozio",
        )

    with col_status:
        if _LOCAL_INV_OUTPUT.exists():
            import json as _json
            _s = _json.loads(_LOCAL_INV_SUMMARY.read_text(encoding="utf-8")) if _LOCAL_INV_SUMMARY.exists() else {}
            st.metric("Feed", f"{_s.get('total_rows', '?')} righe")
            st.caption(_s.get("generated_at", "")[:16].replace("T", " "))
        else:
            st.metric("Feed", "Non generato")

    if st.button("⬇ Genera Local Inventory Feed", use_container_width=True, type="primary"):
        with st.spinner("Fetching prodotti Shopify e generando TSV..."):
            result = subprocess.run(
                [sys.executable,
                 str(ROOT / "scripts" / "generate_local_inventory_feed.py"),
                 "--store-code", store_code],
                capture_output=True, text=True, cwd=str(ROOT),
                env={**__import__("os").environ, "PYTHONUTF8": "1"},
            )
        if result.returncode == 0:
            st.success("Feed generato.")
            st.text(result.stdout[-600:] if result.stdout else "")
        else:
            st.error("Errore generazione feed")
            st.text(result.stderr[:500])

    if _LOCAL_INV_OUTPUT.exists():
        with open(_LOCAL_INV_OUTPUT, "rb") as _f:
            st.download_button(
                "⬇ Scarica google_local_inventory_feed.tsv",
                data=_f,
                file_name="google_local_inventory_feed.tsv",
                mime="text/tab-separated-values",
                use_container_width=True,
            )
        st.markdown("""
**Come caricare su GMC:**
1. [merchants.google.com](https://merchants.google.com) → Contenuto → Feed → `+`
2. Tipo: **Inventario locale dei prodotti**
3. Nome: `bks-local-inventory`
4. Carica il file TSV scaricato sopra
5. Attendi crawl Google (24–72h) — errore scomparirà
""")

with _biz_tab:
    st.info("Alternativa rapida: cambia Business Profile da Sede fisica → Area di servizio. Google smette di aspettarsi inventory fisico.")
    st.markdown("""
**Passi:**
1. Apri [business.google.com](https://business.google.com)
2. Seleziona la sede **BKS Studio / Via Monte Vettore 1, Terni**
3. Modifica profilo → **Tipo di attività**
4. Cambia in **"Area di servizio"** (non Sede fisica)
5. Imposta area: **Italia** (o Terni + raggio)
6. Salva

✅ Shopify local inventory sync è già **OFF** — nessuna azione Shopify richiesta.
""")

with _korea_tab:
    st.warning("24 prodotti bloccati per mancanza di registrazione commerciale coreana.")
    st.markdown("""
**Fix:**
1. [merchants.google.com](https://merchants.google.com) → Impostazioni → Paesi target
2. Trova **South Korea (KR)** → Rimuovi / disabilita
3. Oppure: Shopify → Google & YouTube → Settings → Markets → Remove Korea

Rimuovere la Corea elimina completamente i 24 prodotti flaggati.
""")

st.divider()

st.divider()

# ── Run scripts ──────────────────────────────────────────────────────────────────
st.subheader("Automazione")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔄 Full Channel Sync", use_container_width=True):
        with st.spinner("Sync in corso..."):
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "full_channel_sync.py")],
                capture_output=True, text=True, cwd=str(ROOT),
                env={**__import__("os").environ, "PYTHONUTF8": "1"},
            )
            if result.returncode == 0:
                st.success("Sync completato")
                report = load_report()
                st.rerun()
            else:
                st.error(result.stderr[:400])

with col2:
    if st.button("🏷️ Fix GMC Attributes", use_container_width=True):
        with st.spinner("Impostando metafields..."):
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "fix_google_merchant_attributes.py")],
                capture_output=True, text=True, cwd=str(ROOT),
                env={**__import__("os").environ, "PYTHONUTF8": "1"},
            )
            if result.returncode == 0:
                st.success("Attributi GMC aggiornati: 203/203")
            else:
                st.error(result.stderr[:400])
            st.text(result.stdout[-500:] if result.stdout else "—")

with col3:
    if st.button("📊 Refresh Skill Registry", use_container_width=True):
        with st.spinner("Rebuilding skill index..."):
            result = subprocess.run(
                [sys.executable, "-c",
                 "import sys; sys.path.insert(0,''); from ecommerce_automation.skill_registry import skill_rows, registry_path; from pathlib import Path; rows=skill_rows(Path('.')); print(f'{len(rows)} skills found')"],
                capture_output=True, text=True, cwd=str(ROOT),
            )
            st.success(result.stdout.strip() or "Done")

# ── Printify gap ─────────────────────────────────────────────────────────────────
if printify.get("total"):
    total_pfy = printify["total"]
    linked = printify.get("published_linked", 0)
    gap = total_pfy - linked
    if gap > 0:
        st.divider()
        st.subheader("Printify → Shopify gap")
        st.info(f"**{gap} prodotti Printify** non pubblicati su Shopify ({total_pfy} totali, {linked} collegati).")
        st.caption("Usa Printify dashboard per pubblicare i prodotti mancanti, oppure archivia quelli non più in uso.")
