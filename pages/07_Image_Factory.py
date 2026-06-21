"""BKS Studio — Image Factory Launcher
Avvia la Image Factory come app Streamlit separata e fornisce link diretto.
Include Printify Library sync e catalog image preparation.
"""
from __future__ import annotations
import json, sys, subprocess
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

# ── Printify Library ─────────────────────────────────────────────────────────
st.subheader("Printify Library — Catalog Images")
st.caption("Scarica texture, blueprint e mockup da Printify. Usa i mockup originali come immagini catalogo — nessuna modifica.")

_pfy_tab_sync, _pfy_tab_ai, _pfy_tab_prepare, _pfy_tab_status = st.tabs(["Sync Library", "Generate AI", "Prepare (no AI)", "Status DB"])

with _pfy_tab_sync:
    st.markdown("""
**Scarica da Printify:**
- `textures/` — artwork caricati (designs applicati ai prodotti)
- `mockups/` — immagini mockup originali per ogni prodotto
- `blueprints` — modelli prodotto (brand, modello, dimensioni)
""")
    _sc1, _sc2, _sc3 = st.columns(3)
    with _sc1:
        _sync_skip_dl = st.checkbox("Solo catalogo (no download)", key="pfy_skip_dl")
    with _sc2:
        _sync_col = st.selectbox(
            "Collezione", ["tutte", "bks-hours", "bks-glyph", "bks-marker", "bks-riviera",
                           "bks-pulse", "bks-token", "bks-flag", "bks-origin"],
            key="pfy_sync_col"
        )
    with _sc3:
        _sync_mode = st.selectbox("Tipo sync", ["tutto", "solo upload/texture", "solo prodotti+blueprint"], key="pfy_sync_mode")

    if st.button("⬇ Sync Printify Library", type="primary", use_container_width=True, key="pfy_sync"):
        _cmd_sync = [sys.executable, str(BASE_DIR / "scripts" / "sync_printify_library.py")]
        if _sync_skip_dl:
            _cmd_sync.append("--skip-download")
        if _sync_col != "tutte":
            _cmd_sync += ["--collection", _sync_col]
        if _sync_mode == "solo upload/texture":
            _cmd_sync.append("--uploads-only")
        elif _sync_mode == "solo prodotti+blueprint":
            _cmd_sync.append("--products-only")
        with st.spinner("Sync in corso…"):
            _r = subprocess.run(_cmd_sync, capture_output=True, text=True, cwd=str(BASE_DIR),
                                env={**__import__("os").environ, "PYTHONUTF8": "1"})
        st.success("Completato.") if _r.returncode == 0 else st.error("Errore")
        st.text(_r.stdout[-1000:] if _r.stdout else "")
        if _r.stderr:
            st.text(_r.stderr[-300:])

with _pfy_tab_ai:
    st.markdown("""
**AI libera su:** inquadratura, ambientazione, luce, composizione, atmosfera
**AI preserva:** tipo di oggetto · texture/artwork del prodotto · materiali · colori
**Mai:** testo, loghi, label o typography sull'immagine
""")
    _ai1, _ai2, _ai3 = st.columns(3)
    with _ai1:
        _ai_col = st.selectbox(
            "Collezione", ["tutte", "bks-hours", "bks-glyph", "bks-marker", "bks-riviera",
                           "bks-pulse", "bks-token", "bks-flag", "bks-origin"],
            key="ai_col"
        )
    with _ai2:
        _ai_shots = st.selectbox("Shot per prodotto", [1, 2, 3, 4], index=1, key="ai_shots")
    with _ai3:
        _ai_force = st.checkbox("Rigenera esistenti", key="ai_force")
        _ai_dry = st.checkbox("Dry run", key="ai_dry")

    if st.button("🤖 Genera AI Catalog Images", type="primary", use_container_width=True, key="ai_gen"):
        _cmd_ai = [sys.executable, str(BASE_DIR / "scripts" / "generate_catalog_images.py"),
                   "--shots", str(_ai_shots)]
        if _ai_col != "tutte":
            _cmd_ai += ["--collection", _ai_col]
        if _ai_force:
            _cmd_ai.append("--force")
        if _ai_dry:
            _cmd_ai.append("--dry-run")
        with st.spinner("Generazione AI in corso (gpt-image-1)…"):
            _r_ai = subprocess.run(_cmd_ai, capture_output=True, text=True, cwd=str(BASE_DIR),
                                   env={**__import__("os").environ, "PYTHONUTF8": "1"})
        st.success("Completato.") if _r_ai.returncode == 0 else st.error("Errore")
        st.text(_r_ai.stdout[-1200:] if _r_ai.stdout else "")
        if _r_ai.stderr:
            st.text(_r_ai.stderr[-300:])

    # Show existing AI catalog images count
    _ai_dir = BASE_DIR / "output" / "catalog_images"
    if _ai_dir.exists():
        _ai_count = sum(1 for _ in _ai_dir.rglob("*_ai_*.jpg"))
        st.caption(f"Immagini AI generate: {_ai_count} file in output/catalog_images/")

with _pfy_tab_prepare:
    st.markdown("""
Prepara le immagini catalogo dai mockup scaricati. **Nessuna modifica ai mockup originali.**
Ridimensiona a 2000×2000 px max · JPEG 90% · salva in `output/catalog_images/`
""")
    _pc1, _pc2, _pc3 = st.columns(3)
    with _pc1:
        _prep_col = st.selectbox(
            "Collezione", ["tutte", "bks-hours", "bks-glyph", "bks-marker", "bks-riviera",
                           "bks-pulse", "bks-token", "bks-flag", "bks-origin"],
            key="pfy_prep_col"
        )
    with _pc2:
        _prep_upload = st.checkbox("Upload su Shopify", key="pfy_upload_shopify")
    with _pc3:
        _prep_dry = st.checkbox("Dry run", key="pfy_prep_dry")

    if st.button("▶ Prepara Catalog Images", type="primary", use_container_width=True, key="pfy_prepare"):
        _cmd_prep = [sys.executable, str(BASE_DIR / "scripts" / "prepare_catalog_images.py")]
        if _prep_col != "tutte":
            _cmd_prep += ["--collection", _prep_col]
        if _prep_upload:
            _cmd_prep.append("--upload-to-shopify")
        if _prep_dry:
            _cmd_prep.append("--dry-run")
        with st.spinner("Preparazione in corso…"):
            _r2 = subprocess.run(_cmd_prep, capture_output=True, text=True, cwd=str(BASE_DIR),
                                 env={**__import__("os").environ, "PYTHONUTF8": "1"})
        st.success("Completato.") if _r2.returncode == 0 else st.error("Errore")
        st.text(_r2.stdout[-1000:] if _r2.stdout else "")

with _pfy_tab_status:
    try:
        sys.path.insert(0, str(BASE_DIR))
        from bks_assets import active_catalog_db
        from ecommerce_automation import catalog_db as _cdb
        _db_p = active_catalog_db()
        _lib_s = _cdb.printify_library_summary(_db_p)
        if _lib_s.get("ok"):
            _lc1, _lc2, _lc3, _lc4 = st.columns(4)
            _lc1.metric("Textures", _lib_s["uploads"], f"{_lib_s['uploads_downloaded']} scaricate")
            _lc2.metric("Blueprints", _lib_s["blueprints"])
            _lc3.metric("Prodotti", _lib_s["products"])
            _lc4.metric("Con mockup", _lib_s["products_with_mockups"])
            if _lib_s.get("by_collection"):
                st.markdown("**Per collezione:**")
                for _col, _cnt in _lib_s["by_collection"].items():
                    st.text(f"  {_col}: {_cnt}")
        else:
            st.info("Libreria vuota — esegui Sync prima.")
    except Exception as _e:
        st.warning(f"DB non disponibile: {_e}")

    _pfy_lib_dir = BASE_DIR / "output" / "printify_library"
    if _pfy_lib_dir.exists():
        _tex_count = len(list((_pfy_lib_dir / "textures").glob("*.*"))) if (_pfy_lib_dir / "textures").exists() else 0
        _mok_count = sum(1 for _ in (_pfy_lib_dir / "mockups").rglob("*.jpg")) + \
                     sum(1 for _ in (_pfy_lib_dir / "mockups").rglob("*.png")) \
                     if (_pfy_lib_dir / "mockups").exists() else 0
        st.caption(f"File su disco: {_tex_count} texture, {_mok_count} mockup")
    else:
        st.caption("Directory libreria non ancora creata.")

st.divider()

# ── Site Images ───────────────────────────────────────────────────────────────
st.subheader("Site Images — Hero + Magazine + Piano")
st.caption("Immagini sito (non prodotto): collection hero, magazine spread, piano hero. Già cablate nei template Shopify.")

SITE_IMG_DIR  = BASE_DIR / "output" / "site_images"
SITE_MANIFEST = SITE_IMG_DIR / "manifest.json"

_SITE_IMAGES = {
    "bks-magazine-cover.png":  ("Home",     "editorial", "Magazine cover"),
    "bks-hours-editorial.png": ("Hours",    "editorial", "Hero + Magazine spread"),
    "bks-glyph-editorial.png": ("Glyph",    "editorial", "Hero + Magazine spread"),
    "bks-marker-editorial.png":("Marker",   "editorial", "Hero + Magazine spread"),
    "bks-riviera-editorial.png":("Riviera", "editorial", "Hero + Magazine spread"),
    "bks-pulse-editorial.png": ("Pulse",    "editorial", "Hero + Magazine spread"),
    "bks-token-puffer.png":    ("Token",    "editorial", "Hero + Magazine spread"),
    "bks-flag-editorial.png":  ("Flag",     "editorial", "Hero + Magazine spread"),
    "bks-origin-editorial.png":("Origin",   "editorial", "Hero + Magazine spread"),
}

def _load_manifest() -> dict:
    if SITE_MANIFEST.exists():
        import json
        return json.loads(SITE_MANIFEST.read_text(encoding="utf-8"))
    return {}

manifest_data = _load_manifest()

# Status grid
_cols = st.columns(5)
for _i, (_fname, (_coll, _type, _desc)) in enumerate(_SITE_IMAGES.items()):
    _path = SITE_IMG_DIR / _fname
    _m = manifest_data.get(_fname, {})
    _uploaded = bool(_m.get("shopify_url"))
    _exists   = _path.exists()
    with _cols[_i % 5]:
        _status = "🟢" if _uploaded else ("🟡" if _exists else "⚪")
        st.markdown(f"{_status} **{_coll}**")
        _gen_at = (_m.get("generated_at","")[:10] if _m else "")
        st.caption(f"{_desc[:24]}\n{_gen_at}")

st.markdown("")

_tab_gen, _tab_upload, _tab_guide = st.tabs(["Generate", "Upload to Shopify", "Guide"])

with _tab_gen:
    _c1, _c2, _c3 = st.columns([2, 1, 1])
    with _c1:
        _gen_type = st.selectbox(
            "Tipo", ["editorial (hero + magazine + cover)", "piano (square 1:1)", "all"],
            key="site_img_type"
        )
        _gen_type_arg = _gen_type.split(" ")[0]
    with _c2:
        _gen_force = st.checkbox("Force (rigenera)", key="site_force")
    with _c3:
        _gen_dry = st.checkbox("Dry run", key="site_dry")

    if st.button("▶ Genera Site Images", type="primary", use_container_width=True, key="gen_site"):
        _cmd = [sys.executable, str(BASE_DIR / "scripts" / "generate_site_images.py"),
                "--type", _gen_type_arg]
        if _gen_force:
            _cmd.append("--force")
        if _gen_dry:
            _cmd.append("--dry-run")
        with st.spinner("Generazione in corso (gpt-image-1)…"):
            _result = subprocess.run(
                _cmd, capture_output=True, text=True, cwd=str(BASE_DIR),
                env={**__import__("os").environ, "PYTHONUTF8": "1"},
            )
        if _result.returncode == 0:
            st.success("Completato.")
        else:
            st.error("Errore")
        st.text(_result.stdout[-800:] if _result.stdout else "")
        if _result.stderr:
            st.text(_result.stderr[-300:])
        st.rerun()

with _tab_upload:
    st.markdown("Carica su Shopify CDN. Dopo upload i template sono aggiornati automaticamente.")
    _u1, _u2 = st.columns([2, 1])
    with _u1:
        _up_type = st.selectbox("Tipo upload", ["editorial", "piano", "all"], key="up_type")
    with _u2:
        _up_col_img = st.checkbox("Aggiorna collection.image", key="up_colimg",
                                   help="Imposta hero_banner come collection image in Shopify Admin")

    if st.button("⬆ Upload Site Images → Shopify CDN", use_container_width=True, type="primary", key="upload_site"):
        _cmd2 = [sys.executable, str(BASE_DIR / "scripts" / "upload_site_images.py"),
                 "--type", _up_type]
        if _up_col_img:
            _cmd2.append("--update-collection-images")
        with st.spinner("Upload in corso…"):
            _result2 = subprocess.run(
                _cmd2, capture_output=True, text=True, cwd=str(BASE_DIR),
                env={**__import__("os").environ, "PYTHONUTF8": "1"},
            )
        if _result2.returncode == 0:
            st.success("Upload completato.")
        else:
            st.error("Errore upload")
        st.text(_result2.stdout[-800:] if _result2.stdout else "")
        st.rerun()

    if manifest_data:
        st.markdown("**CDN URLs nel manifest:**")
        for _fn, _info in manifest_data.items():
            _url = _info.get("shopify_url","")
            _icon = "🟢" if _url else "⚪"
            st.markdown(f"{_icon} `{_fn}` — {_url[:70] + '...' if len(_url)>70 else (_url or 'non caricato')}")

with _tab_guide:
    st.markdown("""
**Come funziona il pipeline site images:**

1. **Generate** — `generate_site_images.py` chiama OpenAI `gpt-image-1` e salva i PNG in `output/site_images/`
   con i nomi ESATTI attesi dai template Shopify (es. `bks-riviera-editorial.png`)

2. **Upload** — `upload_site_images.py` carica i file su Shopify Files API via GraphQL `stagedUploadsCreate`
   → ottiene CDN URL → salva in `manifest.json`

3. **Attivazione automatica** — i template JSON usano già `shopify://shop_images/{filename}`.
   Dopo l'upload, Shopify risolve i path → immagini attive senza modificare il codice tema.

**Nomi attesi dai template:**
```
bks-magazine-cover.png        → index.json cover_image
bks-hours-editorial.png       → collection.bks-hours.json hero_image
                              → index.json spread_1.image
bks-glyph-editorial.png       → collection.bks-glyph.json + spread_3
bks-marker-editorial.png      → collection.bks-marker.json + spread_4
bks-riviera-editorial.png     → collection.bks-riviera.json + spread_5
bks-pulse-editorial.png       → collection.bks-pulse.json + spread_6
bks-token-puffer.png          → collection.bks-token.json + spread_7
bks-flag-editorial.png        → collection.bks-flag.json + spread_8
bks-origin-editorial.png      → collection.bks-origin.json + spread_2
```
""")

st.divider()

# ── Info cartella ─────────────────────────────────────────────────────────
with st.expander("Info directory"):
    st.code(str(FACTORY_DIR), language=None)
    if FACTORY_DIR.exists():
        items = sorted(FACTORY_DIR.iterdir())
        for item in items:
            size = f"{item.stat().st_size//1024} KB" if item.is_file() else "dir"
            st.text(f"  {'📄' if item.is_file() else '📁'} {item.name}  ({size})")
