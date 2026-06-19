"""BKS Studio — Catalog Engine (Streamlit)
Sostituisce catalog_engine.py (Flask). Stesse funzionalità, UI Streamlit.
"""
from __future__ import annotations
import csv, json, os, re, shutil, sys, zipfile
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
import streamlit as st

# ── Path bootstrap ─────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "BKS_SKILL" / "tools"))

st.set_page_config(page_title="BKS Catalog", page_icon="📦", layout="wide")

st.markdown("""
<style>
[data-testid="stMetricValue"] { font-size: 1.6rem !important; }
[data-testid="stMetricLabel"] { font-size: 0.75rem !important; letter-spacing: .08em; text-transform: uppercase; opacity: .6; }
.bks-badge { display:inline-block; padding:2px 8px; border-radius:2px; font-size:11px; font-weight:600; letter-spacing:.06em; }
.bks-ok   { background:#D4EDDA; color:#155724; }
.bks-warn { background:#FFF3CD; color:#856404; }
.bks-err  { background:#F8D7DA; color:#721C24; }
</style>
""", unsafe_allow_html=True)

# ── Imports progetto ───────────────────────────────────────────────────────────
try:
    from bks_assets import active_catalog_csv, active_catalog_db, discover_catalog_csvs, save_active_assets
    from tools.enrich_shopify_catalog import enrich
    from ecommerce_automation.catalog_db import fetch_all_rows as db_fetch_all_rows
    from ecommerce_automation.catalog_db import meta as db_meta
except ImportError as e:
    st.error(f"Modulo mancante: {e}")
    st.stop()

try:
    import shipping_sync as _ss
except ImportError:
    _ss = None

# ── Costanti ──────────────────────────────────────────────────────────────────
INPUT_DIR     = BASE_DIR / "input"
OUTPUT_DIR    = BASE_DIR / "output"
CATALOG_DIR   = BASE_DIR / "collezioni_csv"
UPDATED_CSV   = OUTPUT_DIR / "products_export_updated.csv"
SEO_REPORT    = OUTPUT_DIR / "seo_report.csv"
PACKAGE_ZIP   = OUTPUT_DIR / "bakabo_export_package.zip"
AI_INDEX      = OUTPUT_DIR / "bks_ai_index.json"
SHIPPING_SYNC = OUTPUT_DIR / "bks_shipping_sync.json"
SKILL_DIR     = BASE_DIR / "BKS_SKILL"
_PFY_BASE     = "https://api.printify.com/v1"
_PFY_COLLS    = ["hours", "glyph", "marker", "riviera", "pulse", "token", "flag", "origin"]
_TRANSP       = {"backpack","puffer","windbreaker","swim trunk","swimtrunk","one-piece","onepiece","swimsuit"}
_BANNER_SLOTS = ["hero_main","hero_secondary","collection_banner","editorial_block","product_feature"]

# ── Funzioni backend (no Flask) ────────────────────────────────────────────────

def _load_env() -> None:
    p = BASE_DIR / ".env"
    if not p.exists(): return
    for raw in p.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line: continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

def _pfy_get(token: str, path: str, timeout: int = 25) -> Any:
    headers = {"Authorization": f"Bearer {token}", "User-Agent": "BKS-Catalog/2.0"}
    try:
        r = requests.get(f"{_PFY_BASE}{path}", headers=headers, timeout=timeout, verify=True)
    except requests.exceptions.SSLError:
        r = requests.get(f"{_PFY_BASE}{path}", headers=headers, timeout=timeout, verify=False)
    if not r.ok:
        raise RuntimeError(f"Printify HTTP {r.status_code}: {r.text[:200]}")
    return r.json()

def _pfy_shop(token: str) -> tuple[str, str]:
    """Ritorna (shop_id, shop_title) per bakabo.club."""
    shops = _pfy_get(token, "/shops.json", timeout=15)
    if not isinstance(shops, list) or not shops:
        raise RuntimeError("Nessun shop trovato.")
    by_id = {str(s["id"]): s for s in shops}
    saved = os.environ.get("PRINTIFY_SHOP_ID", "").strip()
    if saved and saved in by_id:
        return saved, str(by_id[saved].get("title", saved))
    pref = os.environ.get("PRINTIFY_SHOP_TITLE", "bakabo.club")
    words = [w for w in re.split(r"[\s,]+", pref.lower()) if len(w) > 3]
    for s in shops:
        hay = (str(s.get("title","")) + " " + str(s.get("sales_channel",""))).lower()
        if any(w in hay for w in words):
            return str(s["id"]), str(s.get("title",""))
    for s in shops:
        if str(s.get("sales_channel","")) in ("shopify","etsy"):
            return str(s["id"]), str(s.get("title",""))
    s0 = shops[0]; return str(s0["id"]), str(s0.get("title",""))

def read_rows(path: Path) -> tuple[list[dict], list[str]]:
    if not path.exists(): return [], []
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        rd = csv.DictReader(fh)
        return list(rd), rd.fieldnames or []

def catalog_rows(path: Path) -> list[dict]:
    """Legge dal DB BKS se è la sorgente della CSV attiva, altrimenti fa fallback sul CSV (query agile, no doppio parsing)."""
    db_path = active_catalog_db()
    if path and db_meta(db_path).get("source") == path.name:
        rows = db_fetch_all_rows(db_path)
        if rows:
            return rows
    return read_rows(path)[0]

def split_tags(v: str) -> list[str]:
    return [t.strip() for t in (v or "").split(",") if t.strip()]

def tag_value(tags: list[str], prefix: str) -> str:
    for t in tags:
        if t.lower().startswith(prefix.lower()):
            return t.split(":", 1)[1].strip()
    return ""

def product_rows(rows: list[dict]) -> list[dict]:
    return [r for r in rows if (r.get("Title") or "").strip()]

def _needs_transp(title: str, ptype: str = "") -> bool:
    return any(w in (title+" "+ptype).lower() for w in _TRANSP)

def _best_img(images: list[dict]) -> str:
    if not images: return ""
    pngs = [i["src"] for i in images if i.get("src","").lower().endswith(".png")]
    return pngs[0] if pngs else images[0].get("src","")

def catalog_summary(path: Path) -> dict:
    rows = catalog_rows(path)
    prods = product_rows(rows)
    img_rows = [r for r in rows if (r.get("Image Src") or "").strip()]
    return {
        "rows": len(rows), "products": len(prods),
        "handles": len({(r.get("Handle") or "").strip() for r in rows if (r.get("Handle") or "").strip()}),
        "image_rows": len(img_rows),
        "missing_seo_title": sum(1 for r in prods if not (r.get("SEO Title") or "").strip()),
        "missing_seo_desc":  sum(1 for r in prods if not (r.get("SEO Description") or "").strip()),
        "missing_alt":       sum(1 for r in img_rows if not (r.get("Image Alt Text") or "").strip()),
        "types": dict(Counter((r.get("Type") or "Unspecified").strip() for r in prods).most_common(10)),
    }

def curation_stats(path: Path) -> dict:
    rows = catalog_rows(path)
    prods = product_rows(rows)
    keep = Counter(); by_ser = Counter(); by_type = Counter(); ser = Counter(); stat = Counter()
    for r in prods:
        tags = split_tags(r.get("Tags", ""))
        s = (r.get("Status") or "").strip().lower() or "empty"
        stat[s] += 1
        col = tag_value(tags, "collection:") or tag_value(tags, "series:") or "unassigned"
        pt = tag_value(tags, "type:") or (r.get("Type") or "unassigned")
        ser[col] += 1
        if "curation:keep" in {t.lower() for t in tags} or s == "active":
            keep["✓ Keep"] += 1; by_ser[col] += 1; by_type[pt] += 1
        elif s == "draft": keep["✗ Draft"] += 1
        else: keep["— Empty"] += 1
    return {"products": len(prods), "keep": dict(keep), "by_series": dict(by_ser.most_common(10)), "by_type": dict(by_type.most_common(10)), "status": dict(stat.most_common(10))}

def generate_ai_index(csv_path: Path) -> None:
    rows = catalog_rows(csv_path)
    prods = product_rows(rows)
    sg: dict[str, Any] = {"man": {"XS":{"chest":"86-91","waist":"71-76"},"S":{"chest":"91-96","waist":"76-81"},"M":{"chest":"96-101","waist":"81-86"},"L":{"chest":"101-106","waist":"86-91"},"XL":{"chest":"106-111","waist":"91-96"},"unit":"cm"},"woman":{"XS":{"chest":"78-83","waist":"60-65"},"S":{"chest":"83-88","waist":"65-70"},"M":{"chest":"88-93","waist":"70-75"},"L":{"chest":"93-98","waist":"75-80"},"XL":{"chest":"98-103","waist":"80-85"},"unit":"cm"}}
    for g in ("man","woman"):
        p = SKILL_DIR / "size_guides" / f"{g}.json"
        if p.exists():
            try: sg[g] = json.loads(p.read_text(encoding="utf-8"))
            except: pass
    colls: dict[str, list] = {}; banners = {s:[] for s in _BANNER_SLOTS}
    for i, r in enumerate(prods):
        tags = split_tags(r.get("Tags",""))
        col = tag_value(tags,"collection:") or tag_value(tags,"series:") or "unassigned"
        handle = (r.get("Handle") or "").strip(); title = (r.get("Title") or "").strip()
        gender = "woman" if any(t in {"woman","women","female"} for t in (t.lower() for t in tags)) else "man"
        slot = _BANNER_SLOTS[i % len(_BANNER_SLOTS)]
        entry = {"handle":handle,"title":title,"collection":col,"type":(r.get("Type") or "AOP").strip(),"gender":gender,"image":(r.get("Image Src") or "").strip(),"needs_transparent_bg":_needs_transp(title,(r.get("Type") or "")),"banner_slot":slot,"tags":tags,"price":(r.get("Variant Price") or "").strip(),"seo_title":(r.get("SEO Title") or "").strip(),"seo_description":(r.get("SEO Description") or "").strip(),"size_guide":sg.get(gender,{}),"page_links":{"shopify":f"https://bakabo.club/products/{handle}","collection":f"https://bakabo.club/collections/{col}"}}
        colls.setdefault(col,[]).append(entry); banners[slot].append(handle)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    AI_INDEX.write_text(json.dumps({"generated_at":datetime.now().isoformat(),"csv_source":csv_path.name,"total_products":len(prods),"collections":colls,"banner_assignments":banners,"size_guides":sg,"asset_base":"https://bakabo.club"},ensure_ascii=False,indent=2),encoding="utf-8")

def run_enrichment(source: Path) -> tuple[bool, str]:
    try:
        CATALOG_DIR.mkdir(parents=True, exist_ok=True); OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        stem = source.stem.removesuffix("_SEO_TAGS_READY")
        ready = CATALOG_DIR / f"{stem}_SEO_TAGS_READY.csv"
        enrich(source, ready, SEO_REPORT)
        shutil.copy2(ready, UPDATED_CSV)
        with zipfile.ZipFile(PACKAGE_ZIP,"w",zipfile.ZIP_DEFLATED) as pkg:
            if ready.exists(): pkg.write(ready, arcname=ready.name)
            if SEO_REPORT.exists(): pkg.write(SEO_REPORT, arcname=SEO_REPORT.name)
        save_active_assets(catalog_csv=ready)
        generate_ai_index(ready)
        return True, f"✅ Completato → {ready.name}"
    except Exception as exc:
        return False, f"❌ {type(exc).__name__}: {exc}"

# ── Init env + session state ──────────────────────────────────────────────────
_load_env()
for k in ("pfy_products","pfy_shop","pfy_total","ship_result","enrich_result"):
    if k not in st.session_state:
        st.session_state[k] = None

# ── Sidebar — CSV picker ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📂 Catalogo")
    csv_files = discover_catalog_csvs()
    active    = active_catalog_csv()

    # Auto-sync: always keep the most recent CSV active (no manual action needed)
    if csv_files:
        latest_on_disk = csv_files[0]
        if active is None or not active.exists():
            save_active_assets(catalog_csv=latest_on_disk); active = latest_on_disk; st.rerun()
        elif latest_on_disk.stat().st_mtime > active.stat().st_mtime + 1:
            save_active_assets(catalog_csv=latest_on_disk); active = latest_on_disk; st.rerun()

    if csv_files:
        active_idx = next((i for i,f in enumerate(csv_files) if active and f.resolve()==active.resolve()), 0)
        sel = st.selectbox("CSV attivo", [f.name for f in csv_files], index=active_idx, label_visibility="collapsed")
        sel_path = next(f for f in csv_files if f.name == sel)
        if not active or sel_path.resolve() != active.resolve():
            save_active_assets(catalog_csv=sel_path); active = sel_path; st.rerun()
        if active and active.exists():
            st.caption(f"📄 {active.stat().st_size//1024} KB  ·  🤖 auto")
    else:
        st.warning("Nessun CSV trovato in collezioni_csv/")
        st.info("Deposita il CSV Shopify in: collezioni_csv/")

    with st.expander("📥 Importa CSV esterno"):
        up = st.file_uploader("Carica CSV", type=["csv"], label_visibility="collapsed")
        if up:
            INPUT_DIR.mkdir(parents=True, exist_ok=True)
            dest = INPUT_DIR / up.name; dest.write_bytes(up.read())
            save_active_assets(catalog_csv=dest)
            st.success(f"Caricato: {up.name}"); st.rerun()

    db_path = active_catalog_db()
    db_synced = active and db_meta(db_path).get("source") == active.name
    st.caption(f"🗄️ DB BKS {'🟢 sincronizzato' if db_synced else '🟡 non sincronizzato (esegui arricchimento)'}")

    st.divider()
    tok = os.environ.get("PRINTIFY_API_TOKEN","")
    st.markdown(f"**Printify** {'🟢' if tok else '🔴'}")
    if tok:
        shop_cached = st.session_state.get("pfy_shop")
        st.caption(shop_cached if shop_cached else "Apri tab Printify per connettere")

# ── Tabs ─────────────────────────────────────────────────────────────────────
st.title("📦 BKS Catalog Engine")
active = active_catalog_csv()

t_pfy, t_ship, t_cat, t_cur, t_seo, t_exp = st.tabs([
    "🏪 Printify", "🚚 Spedizioni", "📦 Catalogo", "✂️ Curation", "🔍 SEO", "⬇️ Export"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB PRINTIFY
# ══════════════════════════════════════════════════════════════════════════════
with t_pfy:
    tok = os.environ.get("PRINTIFY_API_TOKEN","").strip()
    if not tok:
        st.error("PRINTIFY_API_TOKEN non configurato nel file .env")
        st.stop()

    col_h, col_btn = st.columns([5,1])
    with col_h:
        if st.session_state.pfy_shop:
            st.success(f"🟢 Connesso · **{st.session_state.pfy_shop}** · {st.session_state.pfy_total or 0} prodotti")
    with col_btn:
        do_refresh = st.button("🔄 Refresh", width="stretch")

    if do_refresh or st.session_state.pfy_products is None:
        with st.spinner("Connessione a Printify bakabo.club..."):
            try:
                sid, stitle = _pfy_shop(tok)
                data = _pfy_get(tok, f"/shops/{sid}/products.json?page=1&limit=12", timeout=30)
                raw = data.get("data",[]) if isinstance(data, dict) else (data if isinstance(data, list) else [])
                prods = []
                for p in raw[:12]:
                    if not isinstance(p, dict): continue
                    title = (p.get("title") or "").strip()
                    imgs  = [i for i in (p.get("images") or []) if isinstance(i, dict) and i.get("src")]
                    varz  = [v for v in (p.get("variants") or []) if isinstance(v, dict)]
                    rp    = varz[0].get("price",0) if varz else 0
                    price = f"${rp/100:.2f}" if isinstance(rp, int) and rp > 200 else str(rp)
                    prods.append({
                        "title": title[:52],
                        "image": _best_img(imgs),
                        "price": price,
                        "visible": bool(p.get("visible", False)),
                        "collection": next((c for c in _PFY_COLLS if c in title.lower()), "—"),
                        "needs_transp": _needs_transp(title),
                    })
                total = int(data.get("last_page",1)) * int(data.get("per_page", len(raw))) if isinstance(data, dict) else len(raw)
                st.session_state.pfy_products = prods
                st.session_state.pfy_shop     = f"{stitle} (ID: {sid})"
                st.session_state.pfy_total    = total
                st.rerun()
            except Exception as e:
                st.error(f"Errore Printify: {e}")

    prods = st.session_state.pfy_products or []
    if prods:
        cols = st.columns(4)
        for i, p in enumerate(prods):
            with cols[i % 4]:
                if p["image"]:
                    st.image(p["image"], width="stretch")
                else:
                    st.markdown('<div style="height:160px;background:#111;border-radius:4px;display:flex;align-items:center;justify-content:center;color:#555;font-size:11px;">no image</div>', unsafe_allow_html=True)
                badge = "🟢" if p["visible"] else "🔴"
                transp = " 🪄" if p["needs_transp"] else ""
                st.caption(f"{badge} **{p['title']}**{transp}")
                st.caption(f"`{p['collection']}` · {p['price']}")

# ══════════════════════════════════════════════════════════════════════════════
# TAB SPEDIZIONI
# ══════════════════════════════════════════════════════════════════════════════
with t_ship:
    st.subheader("Sync spedizioni Printify → bakabo.club")
    st.caption("Scarica profili spedizione per tutti i 19 blueprint+provider, analizza margini per 13 mercati.")

    col_a, col_b = st.columns([4,1])
    with col_b:
        if st.button("🔄 Avvia sync", type="primary", width="stretch"):
            tok = os.environ.get("PRINTIFY_API_TOKEN","").strip()
            if not tok:
                st.error("Token mancante")
            elif _ss is None:
                st.error("shipping_sync non disponibile")
            else:
                with st.spinner("Sync in corso (1-3 minuti)..."):
                    try:
                        _ss.build_report(tok)
                        st.session_state.ship_result = ("ok","Sync completato con successo!")
                    except Exception as e:
                        st.session_state.ship_result = ("err", str(e))
                st.rerun()

    if st.session_state.ship_result:
        s, m = st.session_state.ship_result
        if s == "ok": st.success(m)
        else: st.error(m)

    if SHIPPING_SYNC.exists():
        data = json.loads(SHIPPING_SYNC.read_text(encoding="utf-8"))
        with col_a:
            st.caption(f"Aggiornato: {data.get('generated_at','—')[:16]}")

        import pandas as pd

        # Markets table
        markets = data.get("markets",[])
        if markets:
            df = pd.DataFrame([{
                "Mercato": m.get("country_code","—"),
                "Min ship $": f"{m.get('min_cost',0):.2f}",
                "Max ship $": f"{m.get('max_cost',0):.2f}",
                "Prodotti": m.get("product_count",0)
            } for m in markets if isinstance(m, dict)])
            st.dataframe(df, width="stretch", hide_index=True)

        # Raccomandazioni
        recs = data.get("recommendations",[])
        if recs:
            st.markdown("#### ⚠️ Raccomandazioni")
            for r in recs[:10]:
                if not isinstance(r, dict): continue
                lv = r.get("level","info")
                ic = "🔴" if lv=="critical" else "🟡" if lv=="high" else "🔵"
                st.markdown(f"{ic} **{r.get('product','—')}** — {r.get('message','')}")

        # Download
        st.download_button("⬇️ Download shipping JSON", SHIPPING_SYNC.read_bytes(), "bks_shipping_sync.json", "application/json")
    else:
        st.info("Nessun report. Clicca 'Avvia sync' per generarlo.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB CATALOGO
# ══════════════════════════════════════════════════════════════════════════════
with t_cat:
    if active is None or not active.exists():
        st.warning("Nessun catalogo attivo — carica un CSV dalla sidebar.")
    else:
        st.subheader(f"📄 {active.name}")
        summ = catalog_summary(active)

        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Righe CSV",   summ["rows"])
        c2.metric("Prodotti",    summ["products"])
        c3.metric("Handle",      summ["handles"])
        c4.metric("Img rows",    summ["image_rows"])

        c5,c6,c7 = st.columns(3)
        c5.metric("SEO Title mancanti",  summ["missing_seo_title"],  delta_color="inverse", delta=f"-{summ['missing_seo_title']}" if summ["missing_seo_title"] else None)
        c6.metric("SEO Desc mancanti",   summ["missing_seo_desc"],   delta_color="inverse", delta=f"-{summ['missing_seo_desc']}"  if summ["missing_seo_desc"]  else None)
        c7.metric("Alt text mancanti",   summ["missing_alt"],         delta_color="inverse", delta=f"-{summ['missing_alt']}"       if summ["missing_alt"]       else None)

        if summ["types"]:
            import pandas as pd
            st.markdown("#### Tipi prodotto")
            st.dataframe(pd.DataFrame(list(summ["types"].items()), columns=["Tipo","N."]), width="stretch", hide_index=True)

        st.divider()
        st.subheader("▶️ Arricchimento SEO")
        st.caption("Aggiunge SEO title/description, tag collezione, alt text. Genera CSV SHOPIFY_IMPORT_READY + SEO report + AI Index.")
        if st.button("Avvia arricchimento", type="primary", key="enrich_btn"):
            with st.spinner("Elaborazione... (alcuni minuti)"):
                ok, msg = run_enrichment(active)
                st.session_state.enrich_result = (ok, msg)
                if ok: active = active_catalog_csv()
            st.rerun()

        if st.session_state.enrich_result:
            ok, msg = st.session_state.enrich_result
            if ok: st.success(msg)
            else:  st.error(msg)

# ══════════════════════════════════════════════════════════════════════════════
# TAB CURATION
# ══════════════════════════════════════════════════════════════════════════════
with t_cur:
    if active is None or not active.exists():
        st.warning("Nessun catalogo attivo.")
    else:
        import pandas as pd
        st.subheader("Curation per collezione")
        stats = curation_stats(active)

        c1,c2 = st.columns(2)
        c1.metric("Prodotti totali", stats["products"])

        if stats["keep"]:
            df_k = pd.DataFrame(list(stats["keep"].items()), columns=["Status","N."])
            c2.dataframe(df_k, width="stretch", hide_index=True)

        if stats["by_series"]:
            st.markdown("#### Per collezione (prodotti attivi)")
            st.dataframe(pd.DataFrame(list(stats["by_series"].items()), columns=["Collezione","Attivi"]), width="stretch", hide_index=True)

        if stats["by_type"]:
            st.markdown("#### Per tipo (prodotti attivi)")
            st.dataframe(pd.DataFrame(list(stats["by_type"].items()), columns=["Tipo","Attivi"]), width="stretch", hide_index=True)

        st.markdown("#### Target collezioni")
        t1,t2,t3,t4 = st.columns(4)
        t1.metric("Min totale",90); t2.metric("Max totale",150)
        t3.metric("Min/coll",8);    t4.metric("Max/coll",22)

# ══════════════════════════════════════════════════════════════════════════════
# TAB SEO
# ══════════════════════════════════════════════════════════════════════════════
with t_seo:
    if active is None or not active.exists():
        st.warning("Nessun catalogo attivo.")
    else:
        import pandas as pd
        rows    = catalog_rows(active)
        prods   = product_rows(rows)
        no_title = [r for r in prods if not (r.get("SEO Title") or "").strip()]
        no_desc  = [r for r in prods if not (r.get("SEO Description") or "").strip()]
        no_alt   = [r for r in rows  if (r.get("Image Src") or "").strip() and not (r.get("Image Alt Text") or "").strip()]

        c1,c2,c3 = st.columns(3)
        c1.metric("Senza SEO Title",       len(no_title))
        c2.metric("Senza SEO Description", len(no_desc))
        c3.metric("Senza Alt Text",        len(no_alt))

        if no_title:
            with st.expander(f"Prodotti senza SEO Title ({len(no_title)})"):
                st.dataframe(pd.DataFrame([{"Handle": r.get("Handle",""), "Title": (r.get("Title",""))[:50]} for r in no_title[:30]]), width="stretch", hide_index=True)
        if no_desc:
            with st.expander(f"Prodotti senza SEO Description ({len(no_desc)})"):
                st.dataframe(pd.DataFrame([{"Handle": r.get("Handle",""), "Title": (r.get("Title",""))[:50]} for r in no_desc[:30]]), width="stretch", hide_index=True)

        if SEO_REPORT.exists():
            st.divider()
            st.markdown("#### SEO Report (output)")
            try:
                df_seo = pd.read_csv(SEO_REPORT, encoding="utf-8-sig")
                st.dataframe(df_seo.head(60), width="stretch", hide_index=True)
            except Exception as e:
                st.error(f"Errore lettura SEO report: {e}")

# ══════════════════════════════════════════════════════════════════════════════
# TAB EXPORT
# ══════════════════════════════════════════════════════════════════════════════
with t_exp:
    st.subheader("⬇️ Download files")

    c1,c2,c3 = st.columns(3)
    with c1:
        st.markdown("**CSV Shopify**")
        fp = UPDATED_CSV if UPDATED_CSV.exists() else active
        if fp and fp.exists():
            st.download_button("⬇️ CSV", fp.read_bytes(), fp.name, "text/csv", key="dl_csv")
            st.caption(f"{fp.stat().st_size//1024} KB · {datetime.fromtimestamp(fp.stat().st_mtime).strftime('%d/%m %H:%M')}")
        else:
            st.info("Esegui arricchimento")
    with c2:
        st.markdown("**SEO Report**")
        if SEO_REPORT.exists():
            st.download_button("⬇️ SEO", SEO_REPORT.read_bytes(), "seo_report.csv", "text/csv", key="dl_seo")
            st.caption(f"{SEO_REPORT.stat().st_size//1024} KB")
        else: st.info("Esegui arricchimento")
    with c3:
        st.markdown("**Package ZIP**")
        if PACKAGE_ZIP.exists():
            st.download_button("⬇️ ZIP", PACKAGE_ZIP.read_bytes(), "bakabo_export_package.zip", "application/zip", key="dl_zip")
            st.caption(f"{PACKAGE_ZIP.stat().st_size//1024} KB")
        else: st.info("Esegui arricchimento")

    st.divider()
    c4,c5 = st.columns(2)
    with c4:
        st.markdown("**🤖 AI Index JSON**")
        if st.button("🔁 Genera AI Index", key="gen_ai"):
            if active and active.exists():
                with st.spinner("Generazione..."):
                    generate_ai_index(active)
                st.success("AI Index aggiornato!")
            else:
                st.warning("Nessun CSV attivo")
        if AI_INDEX.exists():
            ai = json.loads(AI_INDEX.read_text(encoding="utf-8"))
            st.download_button("⬇️ AI Index", AI_INDEX.read_bytes(), "bks_ai_index.json", "application/json", key="dl_ai")
            st.caption(f"{ai.get('generated_at','—')[:16]} · {ai.get('total_products',0)} prodotti")
    with c5:
        st.markdown("**🚚 Shipping Report**")
        if SHIPPING_SYNC.exists():
            sd = json.loads(SHIPPING_SYNC.read_text(encoding="utf-8"))
            st.download_button("⬇️ Shipping", SHIPPING_SYNC.read_bytes(), "bks_shipping_sync.json", "application/json", key="dl_ship")
            st.caption(f"{sd.get('generated_at','—')[:16]}")
        else:
            st.info("Vai in tab Spedizioni")

    # ── Margin calculator ────────────────────────────────────────────────────
    st.divider()
    st.markdown("**📋 Calcolo margine BKS**")
    with st.expander("Apri calcolatore + alert critici"):
        mc1,mc2,mc3 = st.columns(3)
        retail    = mc1.number_input("Retail (USD)", 0.0, 999.0, 65.0, 1.0)
        base_cost = mc2.number_input("Base cost (USD)", 0.0, 200.0, 15.0, 0.5)
        shipping  = mc3.number_input("Shipping (USD)", 0.0, 50.0, 8.0, 0.5)
        net       = retail * 0.971 - 0.30
        total     = base_cost + shipping
        margin    = (net - total) / net * 100 if net > 0 else 0
        tier = ("🟢 Premium 65%+" if margin>=65 else "🟡 Standard 55-65%" if margin>=55
                else "🟠 Minimo 45-55%" if margin>=45 else "🔴 DRAFT (<45%)")
        mc1.metric("Net revenue", f"${net:.2f}")
        mc2.metric("Margine", f"{margin:.1f}%")
        mc3.metric("Tier", tier)

        biz = SKILL_DIR / "business" / "bakabo-business.json"
        if biz.exists():
            alerts = json.loads(biz.read_text(encoding="utf-8")).get("critical_alerts",[])
            if alerts:
                st.markdown("##### Alert critici attivi")
                for a in alerts:
                    lv = a.get("severity","").upper()
                    ic = "🔴" if lv=="CRITICAL" else "🟡" if lv=="HIGH" else "🔵"
                    st.markdown(f"{ic} **{a.get('product','—')}** — {a.get('issue','—')}")
                    st.caption(f"→ {a.get('action','—')}")
