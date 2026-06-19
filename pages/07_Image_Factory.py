"""BKS Studio — Image Factory Launcher
Avvia la Image Factory come app Streamlit separata e fornisce link diretto.
"""
from __future__ import annotations
import sys, subprocess
from pathlib import Path

import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import bks_nav

st.set_page_config(page_title="BKS Image Factory", page_icon="🎨", layout="wide")
bks_nav.render("factory")
FACTORY_DIR = BASE_DIR / "BAKABO_IMAGE_FACTORY_v1.1"
FACTORY_APP = FACTORY_DIR / "app.py"
FACTORY_PORT = 8502

# ── BKS CSS ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.bks-factory-hero {
    background: linear-gradient(135deg,#0A0A0A 60%,#1A0A00 100%);
    border: 1px solid #C9B79C40;
    border-radius: 8px;
    padding: 2rem;
    margin-bottom: 1.5rem;
    text-align: center;
}
.bks-factory-hero h1 { font-size:2.2rem; letter-spacing:.12em; color:#FAFAF7; }
.bks-factory-hero p  { color:#C9B79C; font-size:.95rem; }
.bks-launch-url {
    font-family: monospace;
    font-size: 1.1rem;
    color: #C9B79C;
    background: #111;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    display: inline-block;
    margin: 0.5rem 0;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="bks-factory-hero">
  <h1>🎨 BAKABO IMAGE FACTORY</h1>
  <p>Generazione immagini AI · Background removal · SEO batch · Catalog sync</p>
</div>
""", unsafe_allow_html=True)

# ── Check se la factory esiste ─────────────────────────────────────────────
if not FACTORY_APP.exists():
    st.error(f"Image Factory non trovata in: {FACTORY_DIR}")
    st.info("Assicurati che la directory `BAKABO_IMAGE_FACTORY_v1.1/` esista nella root del progetto.")
    st.stop()

# ── Trova Python nel venv ──────────────────────────────────────────────────
def _find_python() -> Path | None:
    for venv in (".venv_catalog", ".venv_dashboard", ".venv"):
        p = BASE_DIR / venv / "Scripts" / "python.exe"
        if p.exists():
            return p
    return None

PYTHON_EXE = _find_python()

# ── Check se porta 8502 è in uso (= factory già avviata) ──────────────────
import socket
def _port_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", port)) == 0

factory_running = _port_open(FACTORY_PORT)

# ── UI principale ─────────────────────────────────────────────────────────
col_status, col_launch = st.columns([3, 1])

with col_status:
    if factory_running:
        st.success(f"🟢 Image Factory attiva su porta {FACTORY_PORT}")
        st.markdown(f'<span class="bks-launch-url">http://localhost:{FACTORY_PORT}</span>', unsafe_allow_html=True)
        st.markdown(f"**[→ Apri Image Factory](http://localhost:{FACTORY_PORT})**")
    else:
        st.warning(f"⚪ Image Factory non avviata (porta {FACTORY_PORT} libera)")
        if not PYTHON_EXE:
            st.error("Python venv non trovato. Avvia prima `01_START_CATALOG_ENGINE.bat`.")

with col_launch:
    if factory_running:
        if st.button("🔄 Apri nel browser", width="stretch", type="primary"):
            import webbrowser
            webbrowser.open(f"http://localhost:{FACTORY_PORT}")
    else:
        if PYTHON_EXE and st.button("▶️ Avvia Factory", width="stretch", type="primary"):
            cmd = [str(PYTHON_EXE), "-m", "streamlit", "run", str(FACTORY_APP),
                   "--server.port", str(FACTORY_PORT),
                   "--server.headless", "true",
                   "--browser.gatherUsageStats", "false"]
            subprocess.Popen(cmd, cwd=str(FACTORY_DIR),
                             creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform=="win32" else 0)
            import time; time.sleep(3)
            st.rerun()

st.divider()

# ── Moduli disponibili ────────────────────────────────────────────────────
st.subheader("Moduli Image Factory v1.1")
modules = [
    ("🎨", "image_generator",    "Genera immagini AI tramite API (DALL-E, Stable Diffusion)"),
    ("✂️", "background_remover", "Rimozione sfondo automatica per prodotti AOP"),
    ("📋", "catalog_lookup",     "Ricerca e abbinamento prodotti da catalogo Shopify"),
    ("🔍", "collection_detector","Rilevamento collezione BKS dal contenuto immagine"),
    ("🔎", "image_analyzer",     "Analisi qualità e composizione immagini"),
    ("🎯", "image_director",     "Direzione artistica BKS per prompt generation"),
    ("📦", "manifest",           "Gestione manifest produzione e asset tracking"),
    ("🖨️", "printify_client",    "Upload immagini e sync diretta con Printify"),
    ("💡", "prompt_builder",     "Costruttore prompt ottimizzato per stile BKS"),
    ("✅", "quality_validator",   "Validazione qualità output prima dell'upload"),
    ("🏷️", "seo_generator",      "Generazione SEO title/description da immagine"),
    ("🛍️", "shopify_client",     "Sync prodotti e metafield su Shopify"),
]

cols = st.columns(3)
for i, (icon, name, desc) in enumerate(modules):
    mod_path = FACTORY_DIR / "modules" / f"{name}.py"
    exists = mod_path.exists()
    with cols[i % 3]:
        status = "🟢" if exists else "⚪"
        st.markdown(f"{status} {icon} **{name}**")
        st.caption(desc)

st.divider()

# ── Info cartella ─────────────────────────────────────────────────────────
with st.expander("Info directory"):
    st.code(str(FACTORY_DIR), language=None)
    if FACTORY_DIR.exists():
        items = sorted(FACTORY_DIR.iterdir())
        for item in items:
            size = f"{item.stat().st_size//1024} KB" if item.is_file() else "dir"
            st.text(f"  {'📄' if item.is_file() else '📁'} {item.name}  ({size})")
