"""BKS Studio — BAKABO IMAGE FACTORY v1.1
Streamlit dashboard for AI-powered product image generation.
"""
import streamlit as st
import json
from pathlib import Path

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BKS Image Factory",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Brand CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  :root {
    --onyx: #0A0A0A;
    --salt: #FAFAF7;
    --dune: #C9B79C;
    --shadow: #242833;
  }

  /* ── Main area: dark background, light text ── */
  .stApp { background: var(--onyx) !important; color: var(--salt) !important; }
  .main .block-container { background: var(--onyx) !important; color: var(--salt) !important; }

  /* All text in main area */
  .stApp p, .stApp span, .stApp label, .stApp div,
  .stApp h1, .stApp h2, .stApp h3, .stApp h4,
  .stApp .stMarkdown, .stApp .stText,
  .stApp [data-testid="stMetricLabel"],
  .stApp [data-testid="stMetricValue"],
  .stApp [data-testid="stMetricDelta"] {
    color: var(--salt) !important;
  }

  /* Input fields */
  .stApp input, .stApp textarea, .stApp select {
    background: #1A1A1A !important;
    color: var(--salt) !important;
    border: 1px solid #3A3A3A !important;
  }

  /* Buttons */
  .stApp .stButton > button {
    background: var(--shadow) !important;
    color: var(--salt) !important;
    border: 1px solid var(--dune) !important;
  }
  .stApp .stButton > button:hover {
    background: var(--dune) !important;
    color: var(--onyx) !important;
  }

  /* Metrics */
  .stApp [data-testid="metric-container"] {
    background: #1A1A1A !important;
    border: 1px solid #2A2A2A !important;
    border-radius: 6px;
    padding: 12px !important;
  }

  /* Selectbox, multiselect */
  .stApp [data-baseweb="select"] * { background: #1A1A1A !important; color: var(--salt) !important; }

  /* Tabs */
  .stApp [data-baseweb="tab"] { color: var(--salt) !important; }
  .stApp [data-baseweb="tab"][aria-selected="true"] {
    border-bottom: 2px solid var(--dune) !important;
    color: var(--dune) !important;
  }

  /* Expander */
  .stApp [data-testid="stExpander"] {
    background: #1A1A1A !important;
    border: 1px solid #2A2A2A !important;
  }

  /* File uploader */
  .stApp [data-testid="stFileUploader"] {
    background: #1A1A1A !important;
    border: 1px dashed #3A3A3A !important;
    color: var(--salt) !important;
  }

  /* Divider */
  .stApp hr { border-color: #2A2A2A !important; }

  /* Sidebar */
  section[data-testid="stSidebar"] {
    background: #050505 !important;
    color: var(--salt);
  }
  section[data-testid="stSidebar"] .stMarkdown,
  section[data-testid="stSidebar"] label,
  section[data-testid="stSidebar"] p,
  section[data-testid="stSidebar"] span,
  section[data-testid="stSidebar"] div,
  section[data-testid="stSidebar"] .stRadio label { color: var(--salt) !important; }

  /* Sidebar radio active */
  section[data-testid="stSidebar"] [data-testid="stRadio"] label[data-checked="true"] {
    color: var(--dune) !important;
  }
  .bks-header {
    background: var(--onyx); color: var(--salt);
    padding: 1.2rem 2rem; margin-bottom: 2rem;
    display: flex; align-items: center; gap: 1.5rem;
  }
  .bks-logo-left  { color: var(--salt); font-size: 2rem; font-weight: 700; letter-spacing: -.05em; }
  .bks-logo-right { color: var(--dune); font-size: 2rem; font-weight: 700; letter-spacing: -.05em; }
  .bks-badge {
    background: var(--shadow); color: var(--dune);
    padding: .2rem .7rem; font-size: .7rem; letter-spacing: .15em; text-transform: uppercase;
  }
  .qa-score { font-size: 2.5rem; font-weight: 700; }
  .qa-pass  { color: #2F6F4F; }
  .qa-fail  { color: #A33B2A; }
  .bks-page-kicker {
    color: var(--dune) !important;
    font-size: .72rem;
    letter-spacing: .18em;
    text-transform: uppercase;
    margin-bottom: .25rem;
  }
  .bks-lab-hero {
    border: 1px solid #2A2A2A;
    background: linear-gradient(135deg, #111111 0%, #171717 58%, #20242B 100%);
    padding: 1.4rem 1.5rem;
    border-radius: 6px;
    margin-bottom: 1rem;
  }
  .bks-lab-hero h1 {
    font-size: 2rem;
    line-height: 1.1;
    margin: 0 0 .45rem 0;
    letter-spacing: 0;
  }
  .bks-lab-hero p {
    color: #CFCFC9 !important;
    margin: 0;
    max-width: 820px;
  }
  .bks-lab-meta {
    display: flex;
    flex-wrap: wrap;
    gap: .5rem;
    margin-top: 1rem;
  }
  .bks-chip {
    display: inline-flex;
    align-items: center;
    border: 1px solid #343434;
    background: #151515;
    color: #FAFAF7 !important;
    border-radius: 999px;
    padding: .32rem .62rem;
    font-size: .78rem;
  }
  .bks-chip.good { border-color: #2F6F4F; color: #9EE1BE !important; }
  .bks-chip.warn { border-color: #A97126; color: #F0C889 !important; }
  .bks-chip.block { border-color: #A33B2A; color: #F2A294 !important; }
  .bks-panel {
    border: 1px solid #2A2A2A;
    background: #111111;
    border-radius: 6px;
    padding: 1rem;
    min-height: 100%;
  }
  .bks-panel-title {
    font-size: .78rem;
    color: var(--dune) !important;
    letter-spacing: .12em;
    text-transform: uppercase;
    margin-bottom: .6rem;
  }
  .bks-muted { color: #A7A7A0 !important; font-size: .88rem; }
  .bks-step-grid {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: .75rem;
    margin: .8rem 0 1rem 0;
  }
  .bks-step {
    border: 1px solid #2A2A2A;
    background: #101010;
    border-radius: 6px;
    padding: .8rem;
  }
  .bks-step strong { display: block; margin-bottom: .25rem; }
  .bks-path {
    word-break: break-all;
    color: #BFBFB8 !important;
    font-family: ui-monospace, SFMono-Regular, Consolas, monospace;
    font-size: .76rem;
  }
  .bks-swatch-row {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: .55rem;
    margin: .65rem 0 1rem 0;
  }
  .bks-swatch-card {
    border: 1px solid #2A2A2A;
    background: #101010;
    border-radius: 6px;
    padding: .55rem;
    min-height: 98px;
  }
  .bks-swatch-color {
    height: 42px;
    border-radius: 4px;
    border: 1px solid rgba(255,255,255,.24);
    margin-bottom: .45rem;
  }
  .bks-swatch-card strong {
    display: block;
    font-size: .78rem;
    margin-bottom: .12rem;
  }
  .bks-mock-preview {
    border: 1px solid #2A2A2A;
    border-radius: 6px;
    padding: 1rem;
    min-height: 170px;
    display: grid;
    place-items: center;
    text-align: center;
    margin-top: .55rem;
  }
  .bks-mock-preview span {
    display: inline-block;
    border: 1px solid rgba(0,0,0,.12);
    background: rgba(255,255,255,.72);
    color: #0A0A0A !important;
    border-radius: 4px;
    padding: .45rem .65rem;
    font-weight: 700;
  }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎨 BKS IMAGE FACTORY")
    st.markdown("---")
    nav_pages = [
        "📊 Dashboard",
        "🖨️ Printify Products",
        "✂️ Background Removal",
        "🔍 Collection Detection",
        "📸 Shooting Generator",
        "✅ Quality Control",
        "🚀 Shopify Export",
        "⚙️ Settings",
    ]
    nav_slugs = {
        "📊 Dashboard": "dashboard",
        "🖨️ Printify Products": "printify-products",
        "✂️ Background Removal": "background-removal",
        "🔍 Collection Detection": "collection-detection",
        "📸 Shooting Generator": "shooting-generator",
        "✅ Quality Control": "quality-control",
        "🚀 Shopify Export": "shopify-export",
        "⚙️ Settings": "settings",
    }
    slug_to_page = {slug: label for label, slug in nav_slugs.items()}
    query_page = st.query_params.get("page", "")
    default_page = slug_to_page.get(query_page, nav_pages[0])
    page = st.radio(
        "Navigation",
        nav_pages,
        index=nav_pages.index(default_page),
        key="nav_page",
        label_visibility="collapsed",
    )
    if st.query_params.get("page") != nav_slugs[page]:
        st.query_params["page"] = nav_slugs[page]
    st.markdown("---")
    st.markdown("<small style='color:#9A9A9A'>v1.1 · BKS Studio · 2026</small>", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="bks-header">
  <span class="bks-logo-left">BAK</span><span class="bks-logo-right">ABO</span>
  <span class="bks-badge">IMAGE FACTORY v1.1</span>
</div>
""", unsafe_allow_html=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PAGE: DASHBOARD
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if page == "📊 Dashboard":
    st.title("Dashboard")
    from config.settings import OPENAI_API_KEY, PRINTIFY_API_TOKEN, SHOPIFY_STORE, SHOPIFY_ACCESS_TOKEN

    # ── Live store info ───────────────────────────────────────────────────
    store_name = ""
    store_url  = ""
    printify_shop_name = ""
    printify_shop_id   = ""

    if PRINTIFY_API_TOKEN:
        try:
            from modules.printify_client import _get as p_get, resolve_shop_id
            sid  = resolve_shop_id()
            data = p_get("/shops.json")
            raw  = data if isinstance(data, list) else data.get("data", [])
            for s in raw:
                if isinstance(s, dict) and str(s.get("id","")) == str(sid):
                    printify_shop_name = s.get("title","")
                    break
            printify_shop_id = sid
        except Exception:
            pass

    if SHOPIFY_STORE and SHOPIFY_ACCESS_TOKEN:
        try:
            import requests as _req
            r = _req.get(
                f"https://{SHOPIFY_STORE}/admin/api/2024-01/shop.json",
                headers={"X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN},
                timeout=8, verify=False
            )
            if r.ok:
                shop_data  = r.json().get("shop", {})
                store_name = shop_data.get("name", "")
                store_url  = shop_data.get("domain", SHOPIFY_STORE)
        except Exception:
            pass

    # ── Status cards ──────────────────────────────────────────────────────
    st.markdown("""
    <style>
    .bks-status-card {
        background: #111111;
        border: 1px solid #2A2A2A;
        border-radius: 8px;
        padding: 16px 20px;
        margin-bottom: 8px;
    }
    .bks-status-dot-on  { color: #2ECC71; font-size: 1.1rem; }
    .bks-status-dot-off { color: #E74C3C; font-size: 1.1rem; }
    .bks-store-name { font-size: 1.1rem; font-weight: 600; color: #FAFAF7; }
    .bks-store-sub  { font-size: 0.8rem; color: #9A9A9A; margin-top: 2px; }
    .bks-store-url  { font-size: 0.75rem; color: #C9B79C; }
    </style>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)

    with c1:
        dot = "🟢" if OPENAI_API_KEY else "🔴"
        label = "Connected" if OPENAI_API_KEY else "Missing API key"
        masked = (OPENAI_API_KEY[:8] + "...") if OPENAI_API_KEY else "—"
        st.markdown(f"""
        <div class="bks-status-card">
          <div class="bks-store-name">{dot} OpenAI</div>
          <div class="bks-store-sub">{label}</div>
          <div class="bks-store-url">{masked}</div>
        </div>""", unsafe_allow_html=True)

    with c2:
        dot = "🟢" if PRINTIFY_API_TOKEN else "🔴"
        label = f"Shop: {printify_shop_name}" if printify_shop_name else ("Connected" if PRINTIFY_API_TOKEN else "Missing token")
        sub   = f"ID: {printify_shop_id}" if printify_shop_id else "—"
        st.markdown(f"""
        <div class="bks-status-card">
          <div class="bks-store-name">{dot} Printify</div>
          <div class="bks-store-sub">{label}</div>
          <div class="bks-store-url">{sub}</div>
        </div>""", unsafe_allow_html=True)

    with c3:
        dot   = "🟢" if (SHOPIFY_STORE and store_name) else ("🟡" if SHOPIFY_STORE else "🔴")
        label = store_name if store_name else ("Token set" if SHOPIFY_STORE else "Missing credentials")
        url   = f"https://{store_url}" if store_url else SHOPIFY_STORE
        st.markdown(f"""
        <div class="bks-status-card">
          <div class="bks-store-name">{dot} Shopify — bakabo.club</div>
          <div class="bks-store-sub">{label}</div>
          <div class="bks-store-url">{url}</div>
        </div>""", unsafe_allow_html=True)

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Workflow")
        st.markdown("""
1. **Printify Products** — load and download mockups
2. **Background Removal** — clean cutout PNG
3. **Collection Detection** — assign BKS editorial collection
4. **Shooting Generator** — generate editorial images via OpenAI
5. **Quality Control** — score each image 0–100
6. **Shopify Export** — CSV or API upload
""")
    with col2:
        st.subheader("8 BKS Collections")
        for col_name in ["Hours", "Glyph", "Marker", "Riviera",
                          "Pulse", "Token", "Flag", "Folklore"]:
            st.markdown(f"• **BKS {col_name}**")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PAGE: PRINTIFY PRODUCTS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
elif page == "🖨️ Printify Products":
    st.title("Printify Products")
    from config.settings import PRINTIFY_API_TOKEN, PRINTIFY_SHOP_ID, SOURCE_DIR
    from modules.printify_client import _safe_slug

    if not PRINTIFY_API_TOKEN:
        st.error("PRINTIFY_API_TOKEN not set in .env")
        st.stop()

    col_a, col_b, col_c = st.columns([2, 1, 1])
    with col_b:
        st.checkbox("Show drafts/hidden", value=False, key="show_all_products")
    with col_c:
        st.checkbox("Show all brands", value=False, key="show_all_brands")
    with col_a:
        pass
    if st.button("🔄 Load Products from Printify"):
        with st.spinner("Connecting to Printify..."):
            try:
                from modules.printify_client import load_all_products, extract_product_info, _safe_slug
                show_all  = st.session_state.get("show_all_products", False)
                bks_only  = not st.session_state.get("show_all_brands", False)
                products  = load_all_products(published_only=not show_all, bks_only=bks_only)
                st.session_state["printify_products"] = products
                filters = []
                if not show_all:  filters.append("published")
                if bks_only:      filters.append("BKS only")
                label = " · ".join(filters) if filters else "all"
                st.success(f"Loaded {len(products)} products ({label})")
            except Exception as e:
                st.error(f"Error: {e}")

    products = st.session_state.get("printify_products", [])
    if products:
        import pandas as pd
        df = pd.DataFrame([{
            "Title":    p.get("title"),
            "ID":       p.get("id"),
            "Variants": len(p.get("variants", [])),
            "Images":   len(p.get("images", [])),
        } for p in products])
        st.dataframe(df, use_container_width=True)

        from modules.printify_client import download_mockups

        # ── Single product download ───────────────────────────────────────
        st.markdown("#### Single product")
        selected_title = st.selectbox("Select product", df["Title"].tolist())
        if st.button("⬇️ Download mockups for selected product"):
            sel = next(p for p in products if p["title"] == selected_title)
            with st.spinner(f"Downloading mockups for {selected_title}..."):
                paths = download_mockups(sel)
            st.success(f"Downloaded {len(paths)} mockups")
            st.session_state["downloaded_mockups"] = [str(p) for p in paths]

        # Show last downloaded mockups in a grid
        mockups = st.session_state.get("downloaded_mockups", [])
        if mockups:
            cols_per_row = 4
            for i in range(0, len(mockups), cols_per_row):
                row_cols = st.columns(cols_per_row)
                for j, p in enumerate(mockups[i:i+cols_per_row]):
                    row_cols[j].image(p, use_container_width=True)
                    row_cols[j].caption(f"#{i+j+1} · {Path(p).name[:30]}")

        st.divider()

        # ── Bulk download ALL ─────────────────────────────────────────────
        st.markdown("#### Bulk download — all products")
        already_done = [
            p["title"] for p in products
            if any((SOURCE_DIR / _safe_slug(p.get("title",""))).rglob("*_mockup_01.*"))
        ]
        remaining = len(products) - len(already_done)
        st.caption(f"**{len(already_done)}** products already downloaded · **{remaining}** remaining")

        col_bulk1, col_bulk2 = st.columns([2, 1])
        with col_bulk2:
            skip_existing = st.checkbox("Skip already downloaded", value=True, key="skip_existing")
        with col_bulk1:
            if st.button(f"⬇️ Download ALL {len(products)} products", type="primary"):
                bar     = st.progress(0.0)
                status  = st.empty()
                total   = len(products)
                done    = 0
                errors  = []
                all_paths = []

                for i, prod in enumerate(products):
                    slug = _safe_slug(prod.get("title", ""))
                    dest = SOURCE_DIR / slug

                    if skip_existing and list(dest.glob("*_mockup_01.*")):
                        done += 1
                        bar.progress(done / total)
                        status.text(f"[{done}/{total}] Skipped: {prod['title'][:50]}")
                        continue

                    try:
                        status.text(f"[{i+1}/{total}] Downloading: {prod['title'][:50]}...")
                        paths = download_mockups(prod, dest_dir=dest)
                        all_paths.extend(paths)
                        done += 1
                    except Exception as e:
                        errors.append(f"{prod['title']}: {e}")
                    bar.progress((i + 1) / total)

                bar.progress(1.0)
                status.empty()
                st.success(f"✅ Done — {done} products, {len(all_paths)} total images downloaded")
                if errors:
                    with st.expander(f"⚠️ {len(errors)} errors"):
                        for err in errors:
                            st.text(err)
                st.session_state["bulk_download_done"] = True

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PAGE: BACKGROUND REMOVAL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
elif page == "✂️ Background Removal":
    from config.settings import COLLECTION_PALETTE, CUTOUT_DIR, SOURCE_DIR
    from pathlib import Path
    from modules.background_remover import remove_background_safe, compare_original_cutout
    from modules.catalog_lookup import match_product_for_image, safe_slug, source_image_options, split_tags
    from datetime import datetime, timezone
    from html import escape
    import json
    import tempfile

    st.markdown("""
    <div class="bks-page-kicker">BKS Production Lab</div>
    <div class="bks-lab-hero">
      <h1>Background Removal — Safe Mode</h1>
      <p>Cutout QA station for product assets. The default workflow protects product edges, blocks risky transparent masks, and keeps original mockups available for AI generation.</p>
      <div class="bks-lab-meta">
        <span class="bks-chip good">Product-safe default</span>
        <span class="bks-chip warn">Manual approval required</span>
        <span class="bks-chip">White, shadow, transparent, checkerboard</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    def _image_profile(path: Path) -> dict:
        try:
            from PIL import Image
            with Image.open(path) as img:
                width, height = img.size
                mode = img.mode
        except Exception:
            width, height, mode = 0, 0, "unknown"
        size_mb = path.stat().st_size / (1024 * 1024) if path.exists() else 0
        return {"size": f"{width} x {height}", "mode": mode, "mb": f"{size_mb:.2f} MB"}

    def _decision_from(result: dict, metrics: dict, warnings: list[str]) -> tuple[str, str, str]:
        critical = any(
            needle in warning.lower()
            for warning in warnings
            for needle in ["risk", "missing", "very little", "pixel loss"]
        )
        if result.get("mode") == "fallback_original":
            return (
                "Blocked",
                "block",
                "Transparent output was blocked; use white/shadow output or retry with a cleaner source.",
            )
        if not metrics:
            return ("Review", "warn", "Metrics unavailable; inspect the image manually.")
        if metrics.get("grade", "").startswith("❌") or critical:
            return ("Review", "warn", "Inspect details before using this asset in production.")
        return ("Ready", "good", "Ready for manual approval after visual inspection.")

    def _download_asset(label: str, path: Path) -> None:
        if path.exists():
            suffix = path.suffix.lower()
            mime = (
                "application/json" if suffix == ".json" else
                "image/png" if suffix == ".png" else
                "image/jpeg"
            )
            st.download_button(
                label,
                data=path.read_bytes(),
                file_name=path.name,
                mime=mime,
            )

    def _background_profiles(collection: str = "") -> dict[str, dict[str, str]]:
        profiles = {
            "bone": {
                "label": "Bone commerce",
                "hex": "#EFEAE0",
                "use": "warm Shopify/product card background",
            },
            "salt": {
                "label": "Salt white",
                "hex": "#FAFAF7",
                "use": "clean marketplace-ready background",
            },
            "dune": {
                "label": "Dune editorial",
                "hex": "#C9B79C",
                "use": "warm BKS studio mockup background",
            },
            "shadow": {
                "label": "Shadow graphite",
                "hex": "#242833",
                "use": "dark premium card background",
            },
            "onyx": {
                "label": "Onyx black",
                "hex": "#0A0A0A",
                "use": "high contrast editorial background",
            },
        }
        if collection and collection in COLLECTION_PALETTE:
            profiles = {
                f"{collection}-collection": {
                    "label": f"{collection.title()} collection",
                    "hex": COLLECTION_PALETTE[collection]["bg"],
                    "use": "collection-native background color",
                },
                **profiles,
            }
        return profiles

    def _render_background_swatches(profiles: dict[str, dict[str, str]], active_key: str) -> None:
        cards = []
        for key, profile in profiles.items():
            active_style = "border-color:#C9B79C; box-shadow:0 0 0 1px #C9B79C inset;" if key == active_key else ""
            cards.append(
                f"""
                <div class="bks-swatch-card" style="{active_style}">
                  <div class="bks-swatch-color" style="background:{escape(profile["hex"])}"></div>
                  <strong>{escape(profile["label"])}</strong>
                  <span class="bks-muted">{escape(profile["hex"])} · {escape(profile["use"])}</span>
                </div>
                """
            )
        st.markdown(f'<div class="bks-swatch-row">{"".join(cards)}</div>', unsafe_allow_html=True)

    def _write_qa_decision(
        slug_value: str,
        package_data: dict,
        status: str,
        asset_key: str,
        notes: str,
        checks: dict[str, bool],
    ) -> Path:
        review_dir = CUTOUT_DIR / slug_value
        review_dir.mkdir(parents=True, exist_ok=True)
        decision_path = review_dir / "qa_decision.json"
        outputs_data = package_data.get("outputs", {})
        payload = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": status,
            "approved_asset_key": asset_key,
            "approved_asset_path": outputs_data.get(asset_key, ""),
            "source_path": package_data.get("src", ""),
            "slug": slug_value,
            "decision": package_data.get("decision", ""),
            "mode": package_data.get("result", {}).get("mode", ""),
            "background": package_data.get("background", {}),
            "metrics": package_data.get("metrics", {}),
            "warnings": package_data.get("warnings", []),
            "checks": checks,
            "notes": notes.strip(),
            "outputs": outputs_data,
        }
        decision_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        return decision_path

    src = None
    slug = None
    match = None
    source_label = ""

    stage_col, ops_col = st.columns([1.25, 1])

    with stage_col:
        st.markdown('<div class="bks-panel-title">01 Source</div>', unsafe_allow_html=True)
        tab_downloaded, tab_upload = st.tabs(["Source library", "Manual upload"])

        with tab_downloaded:
            options = source_image_options(SOURCE_DIR)
            if options:
                selected_name = st.selectbox(
                    f"Select from {len(options)} downloaded mockups",
                    list(options.keys()),
                )
                if selected_name:
                    src = options[selected_name]
                    source_label = selected_name
                    match = match_product_for_image(src)
                    slug = safe_slug(match.handle if match else src.stem)[:60]
            else:
                st.info("No mockups downloaded yet. Go to Printify Products, then download mockups.")

        with tab_upload:
            uploaded = st.file_uploader("Upload product image", type=["jpg", "jpeg", "png", "webp"])
            if uploaded:
                tmp = Path(tempfile.mkdtemp())
                src = tmp / uploaded.name
                src.write_bytes(uploaded.read() if hasattr(uploaded, "read") else bytes(uploaded))
                source_label = uploaded.name
                match = match_product_for_image(src)
                slug = safe_slug(src.stem)[:60]

        if src:
            profile = _image_profile(src)
            st.image(str(src), caption=source_label or src.name, width="stretch")
            product_title = match.title if match else src.stem
            product_collection = match.collection if match else "manual"
            product_type = match.product_type if match else "unknown"
            tag_count = len(split_tags(match.tags)) if match else 0
            st.markdown(f"""
            <div class="bks-step-grid">
              <div class="bks-step"><strong>Product</strong><span class="bks-muted">{escape(product_title)}</span></div>
              <div class="bks-step"><strong>Collection</strong><span class="bks-muted">{escape(product_collection)}</span></div>
              <div class="bks-step"><strong>Type</strong><span class="bks-muted">{escape(product_type)}</span></div>
            </div>
            <div class="bks-step-grid">
              <div class="bks-step"><strong>Image</strong><span class="bks-muted">{profile["size"]}</span></div>
              <div class="bks-step"><strong>Mode</strong><span class="bks-muted">{profile["mode"]}</span></div>
              <div class="bks-step"><strong>File</strong><span class="bks-muted">{profile["mb"]} · {tag_count} tags</span></div>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(f'<div class="bks-path">{escape(str(src))}</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="bks-panel">
              <div class="bks-panel-title">Waiting for source</div>
              <p class="bks-muted">Choose a downloaded Printify mockup or upload a clean product image.</p>
            </div>
            """, unsafe_allow_html=True)

    with ops_col:
        st.markdown('<div class="bks-panel-title">02 Cutout protocol</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="bks-step-grid" style="grid-template-columns: 1fr;">
          <div class="bks-step"><strong>Reference first</strong><span class="bks-muted">AI generation uses the original mockup unless a cutout is manually approved.</span></div>
          <div class="bks-step"><strong>Protect edges</strong><span class="bks-muted">Thin product details are recovered from the original edge map.</span></div>
          <div class="bks-step"><strong>QA gate</strong><span class="bks-muted">Risky transparent masks are blocked and replaced with original-based review outputs.</span></div>
        </div>
        """, unsafe_allow_html=True)

        presets = {
            "Product-safe": {
                "preserve": True,
                "fallback": True,
                "minimum": 4.0,
                "note": "Best default for footwear, straps, garments and detailed graphics.",
            },
            "Balanced": {
                "preserve": True,
                "fallback": True,
                "minimum": 3.0,
                "note": "Good when the product is cleanly separated from the background.",
            },
            "Strict transparent": {
                "preserve": False,
                "fallback": True,
                "minimum": 5.0,
                "note": "Use only when you need a cleaner alpha mask and can inspect manually.",
            },
        }
        preset = st.radio("Preset", list(presets.keys()), horizontal=True)
        cfg = presets[preset]
        st.caption(cfg["note"])

        st.markdown('<div class="bks-panel-title">03 Output mockup profile</div>', unsafe_allow_html=True)
        background_profiles = _background_profiles(match.collection if match else "")
        background_options = {
            f'{profile["label"]} · {profile["hex"]}': key
            for key, profile in background_profiles.items()
        }
        default_background_key = (
            f"{match.collection}-collection"
            if match and f"{match.collection}-collection" in background_profiles
            else "bone"
        )
        default_background_label = next(
            label for label, key in background_options.items()
            if key == default_background_key
        )
        selected_background_label = st.selectbox(
            "Commercial mockup background",
            list(background_options.keys()),
            index=list(background_options.keys()).index(default_background_label),
            help="This color is applied to the generated commercial JPG and shadow JPG. Transparent PNG stays transparent.",
        )
        background_key = background_options[selected_background_label]
        background_profile = background_profiles[background_key]
        background_hex = background_profile["hex"]
        _render_background_swatches(background_profiles, background_key)
        st.markdown(f"""
        <div class="bks-mock-preview" style="background:{escape(background_hex)}">
          <span>{escape(background_profile["label"])} · {escape(background_hex)}</span>
        </div>
        <div class="bks-step-grid" style="grid-template-columns: 1fr 1fr;">
          <div class="bks-step"><strong>Generated commercial JPG</strong><span class="bks-muted">uses {escape(background_profile["label"])} / {escape(background_hex)}</span></div>
          <div class="bks-step"><strong>Transparent PNG</strong><span class="bks-muted">no color applied; QA only after mask review</span></div>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("Advanced controls", expanded=False):
            preserve_edges = st.checkbox(
                "Preserve product edges",
                value=cfg["preserve"],
                help="Expands the recovered product edge slightly so thin details are not eaten by the mask.",
            )
            fallback_original = st.checkbox(
                "Block risky cutouts",
                value=cfg["fallback"],
                help="If the transparent mask looks too aggressive, keep original-based outputs instead of a damaged cutout.",
            )
            min_opaque_pct = st.slider(
                "Minimum visible product area",
                min_value=1.0,
                max_value=20.0,
                value=cfg["minimum"],
                step=0.5,
                help="Raise this when the product should occupy a large part of the frame.",
            )

        run_cutout = st.button("Run cutout QA package", type="primary", disabled=not bool(src and slug))

    if src and slug and run_cutout:
        out_dir = CUTOUT_DIR / slug
        with st.spinner("Building cutout QA package..."):
            result = remove_background_safe(
                src,
                out_dir,
                slug,
                preserve_edges=preserve_edges,
                fallback_original=fallback_original,
                min_opaque_pct=min_opaque_pct,
                background_hex=background_hex,
                background_name=background_key,
            )

        outputs = result.get("outputs", {}) if result.get("success") else {}
        metrics = {}
        cutout = outputs.get("cutout_safe")
        if cutout and cutout.exists():
            metrics = compare_original_cutout(src, cutout)
        warnings = result.get("warnings", [])
        decision, tone, decision_note = _decision_from(result, metrics, warnings)

        st.session_state["background_removal_package"] = {
            "src": str(src),
            "slug": slug,
            "source_label": source_label,
            "result": {
                "success": result.get("success", False),
                "mode": result.get("mode", ""),
                "error": result.get("error", ""),
            },
            "outputs": {k: str(v) for k, v in outputs.items()},
            "metrics": metrics,
            "warnings": warnings,
            "decision": decision,
            "tone": tone,
            "decision_note": decision_note,
            "background": result.get("background", {}),
        }

        if result.get("success"):
            st.session_state["white_bg_path"] = str(outputs.get("commercial_bg") or outputs.get("white_bg", ""))
            st.session_state["cutout_outputs"] = {k: str(v) for k, v in outputs.items()}
            st.session_state["cutout_path"] = "" if result.get("mode") == "fallback_original" else str(outputs.get("cutout_safe", ""))
        else:
            st.session_state["cutout_path"] = ""

    package = st.session_state.get("background_removal_package")
    if package and src and package.get("src") == str(src):
        result_meta = package.get("result", {})
        if not result_meta.get("success"):
            st.error(result_meta.get("error", "Unknown error"))
        else:
            outputs = {k: Path(v) for k, v in package.get("outputs", {}).items()}
            metrics = package.get("metrics", {})
            warnings = package.get("warnings", [])
            tone = package.get("tone", "warn")
            decision = package.get("decision", "Review")
            decision_note = package.get("decision_note", "")
            result_background = package.get("background", {})
            result_background_name = result_background.get("name", "background")
            result_background_hex = result_background.get("hex", "#FAFAF7")

            st.markdown("---")
            st.markdown('<div class="bks-panel-title">03 QA decision</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="bks-lab-meta">
              <span class="bks-chip {tone}">{escape(decision)}</span>
              <span class="bks-chip">Mode: {escape(result_meta.get("mode", "cutout"))}</span>
              <span class="bks-chip">Mockup: {escape(result_background_name)} · {escape(result_background_hex)}</span>
              <span class="bks-chip">Asset set: {len(outputs)} files</span>
            </div>
            <p class="bks-muted">{escape(decision_note)}</p>
            """, unsafe_allow_html=True)

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Opaque area", f"{metrics.get('retention_pct', 0)}%")
            m2.metric("Transparent area", f"{metrics.get('transparent_pct', 0)}%")
            m3.metric("Edge sharpness", metrics.get("edge_sharpness", "n/a"))
            m4.metric("Grade", metrics.get("grade", "n/a"))

            if warnings:
                with st.expander(f"Review warnings ({len(warnings)})", expanded=True):
                    for warning in warnings:
                        st.warning(warning)
            else:
                st.success("No automatic warnings. Inspect the checkerboard preview before approving.")

            st.markdown('<div class="bks-panel-title">04 Approval gate</div>', unsafe_allow_html=True)
            st.caption("Approve only after visual inspection. The decision is saved next to the generated assets.")
            qa_slug = package.get("slug", slug)
            check_a, check_b, check_c = st.columns(3)
            intact_edges = check_a.checkbox("Product intact", key=f"qa_intact_{qa_slug}")
            clean_background = check_b.checkbox("No visible residue", key=f"qa_clean_{qa_slug}")
            print_readable = check_c.checkbox("Print/logo readable", key=f"qa_print_{qa_slug}")
            notes = st.text_area("QA notes", key=f"qa_notes_{qa_slug}", height=80)
            checks = {
                "product_intact": intact_edges,
                "no_visible_residue": clean_background,
                "print_logo_readable": print_readable,
            }
            all_checks = all(checks.values())
            transparent_allowed = (
                result_meta.get("mode") != "fallback_original"
                and outputs.get("cutout_safe")
                and outputs["cutout_safe"].exists()
            )

            approve_a, approve_b, approve_c = st.columns(3)
            if approve_a.button(
                "Approve transparent PNG",
                disabled=not (all_checks and transparent_allowed),
                key=f"approve_transparent_{qa_slug}",
            ):
                decision_path = _write_qa_decision(qa_slug, package, "approved_transparent", "cutout_safe", notes, checks)
                st.session_state["approved_cutout_path"] = package["outputs"].get("cutout_safe", "")
                st.success(f"Transparent asset approved: {decision_path.name}")
            if approve_b.button(
                "Approve commercial/shadow only",
                disabled=not all_checks,
                key=f"approve_commercial_{qa_slug}",
            ):
                decision_path = _write_qa_decision(qa_slug, package, "approved_commercial", "commercial_bg", notes, checks)
                st.session_state["approved_cutout_path"] = ""
                st.session_state["approved_commercial_path"] = package["outputs"].get("commercial_bg") or package["outputs"].get("white_bg", "")
                st.success(f"Commercial asset approved: {decision_path.name}")
            if approve_c.button("Reject output", key=f"reject_cutout_{qa_slug}"):
                decision_path = _write_qa_decision(qa_slug, package, "rejected", "", notes, checks)
                st.session_state["approved_cutout_path"] = ""
                st.warning(f"Output rejected: {decision_path.name}")

            existing_decision = CUTOUT_DIR / qa_slug / "qa_decision.json"
            if existing_decision.exists():
                st.markdown(f'<div class="bks-path">QA decision: {escape(str(existing_decision))}</div>', unsafe_allow_html=True)
                _download_asset("Download QA decision", existing_decision)

            tabs = st.tabs(["QA review", "Commercial outputs", "Transparent mask", "Mask diagnostics", "Files"])

            with tabs[0]:
                left, right = st.columns(2)
                left.image(str(src), caption="Original reference", width="stretch")
                if outputs.get("checkerboard") and outputs["checkerboard"].exists():
                    right.image(str(outputs["checkerboard"]), caption="Checkerboard alpha review", width="stretch")
                elif outputs.get("white_bg") and outputs["white_bg"].exists():
                    right.image(str(outputs["white_bg"]), caption="Review output", width="stretch")

            with tabs[1]:
                out_a, out_b = st.columns(2)
                commercial_path = outputs.get("commercial_bg") or outputs.get("white_bg")
                if commercial_path and commercial_path.exists():
                    out_a.image(
                        str(commercial_path),
                        caption=f"commercial_bg · {result_background_name} · {result_background_hex}",
                        width="stretch",
                    )
                    _download_asset("Download commercial background", commercial_path)
                if outputs.get("shadow") and outputs["shadow"].exists():
                    out_b.image(
                        str(outputs["shadow"]),
                        caption=f"shadow · {result_background_name} · {result_background_hex}",
                        width="stretch",
                    )
                    _download_asset("Download shadow version", outputs["shadow"])

            with tabs[2]:
                if result_meta.get("mode") == "fallback_original":
                    st.error("Transparent mask blocked. Do not use this as a transparent Shopify asset.")
                elif outputs.get("cutout_safe") and outputs["cutout_safe"].exists():
                    st.image(str(outputs["cutout_safe"]), caption="cutout_safe.png", width="stretch")
                    _download_asset("Download transparent PNG", outputs["cutout_safe"])

            with tabs[3]:
                diag_a, diag_b = st.columns(2)
                if outputs.get("edge_review") and outputs["edge_review"].exists():
                    diag_a.image(str(outputs["edge_review"]), caption="Black/white edge review", width="stretch")
                    _download_asset("Download edge review", outputs["edge_review"])
                if outputs.get("alpha_mask") and outputs["alpha_mask"].exists():
                    diag_b.image(str(outputs["alpha_mask"]), caption="Alpha mask review", width="stretch")
                    _download_asset("Download alpha mask", outputs["alpha_mask"])

            with tabs[4]:
                for key, path in outputs.items():
                    if path.exists():
                        st.markdown(f"**{key}**")
                        st.markdown(f'<div class="bks-path">{escape(str(path))}</div>', unsafe_allow_html=True)
                        _download_asset(f"Download {key}", path)
    elif src:
        st.markdown("---")
        st.markdown("""
        <div class="bks-panel">
          <div class="bks-panel-title">03 QA package</div>
          <p class="bks-muted">Run the cutout package to generate white background, shadow, transparent PNG, and checkerboard review assets.</p>
        </div>
        """, unsafe_allow_html=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PAGE: COLLECTION DETECTION
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
elif page == "🔍 Collection Detection":
    st.title("Collection Detection")
    from config.settings import OPENAI_API_KEY, SOURCE_DIR
    from modules.catalog_lookup import match_product_for_image, source_image_options

    src = None
    match = None

    tab_existing, tab_upload = st.tabs(["📂 Use downloaded mockups", "⬆️ Upload new image"])
    with tab_existing:
        options = source_image_options(SOURCE_DIR)
        if options:
            selected = st.selectbox("Select downloaded mockup", list(options.keys()))
            src = options[selected]
            match = match_product_for_image(src)
            st.image(str(src), width=320)
        else:
            st.info("No downloaded mockups found. Use Printify Products first.")

    with tab_upload:
        uploaded = st.file_uploader("Upload product image", type=["jpg","jpeg","png","webp"])
        if uploaded:
            import tempfile
            tmp = Path(tempfile.mkdtemp())
            src = tmp / uploaded.name
            src.write_bytes(uploaded.read() if hasattr(uploaded, "read") else bytes(uploaded))
            match = None

    title_in = st.text_input("Product title", match.title if match else "")
    tags_in = st.text_input("Tags", match.tags if match else "")

    if src and st.button("🔍 Detect Collection"):
        from pathlib import Path

        with st.spinner("Analyzing..."):
            from modules.image_analyzer import analyze_product_image, extract_palette
            from modules.collection_detector import detect

            tags_list = [t.strip() for t in tags_in.split(",") if t.strip()]

            if OPENAI_API_KEY:
                analysis = analyze_product_image(src)
            else:
                palette = extract_palette(src)
                analysis = {"product_type": "unknown", "collection": "unknown",
                            "palette": palette, "gender": "unisex"}

            detection = detect(image_path=src, analysis=analysis,
                               title=title_in, tags=tags_list)

        col1, col2 = st.columns([1, 2])
        col1.image(str(src), use_container_width=True)

        with col2:
            coll = detection["collection"].upper()
            conf = int(detection["confidence"] * 100)
            src_  = detection["source"]
            st.markdown(f"## 🏷️ **{coll}**")
            st.metric("Confidence", f"{conf}%", delta=src_)
            if analysis.get("palette"):
                st.markdown("**Detected palette:**")
                cols = st.columns(len(analysis["palette"][:5]))
                for i, hex_c in enumerate(analysis["palette"][:5]):
                    cols[i].markdown(
                        f'<div style="background:{hex_c};height:40px;border-radius:4px"></div>'
                        f'<small>{hex_c}</small>', unsafe_allow_html=True
                    )
            st.markdown(f"**Product type:** {analysis.get('product_type','?')}")
            st.markdown(f"**Gender:** {analysis.get('gender','?')}")
            st.session_state["detected_collection"] = detection["collection"]
            st.session_state["detected_analysis"]   = analysis
            st.session_state["selected_source_image"] = str(src)
            st.session_state["selected_product_title"] = title_in
            st.session_state["selected_product_tags"] = tags_in
            if match:
                st.session_state["selected_product_type"] = match.product_type

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PAGE: SHOOTING GENERATOR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
elif page == "📸 Shooting Generator":
    st.title("Shooting Generator")
    from config.settings import COLLECTIONS, SOURCE_DIR
    from modules.catalog_lookup import match_product_for_image, source_image_options

    col1, col2 = st.columns([1, 2])
    with col1:
        source_path = None
        match = None
        source_mode = st.radio("Source", ["Downloaded mockup", "Upload"], horizontal=True)
        if source_mode == "Downloaded mockup":
            options = source_image_options(SOURCE_DIR)
            if options:
                preferred = st.session_state.get("selected_source_image", "")
                labels = list(options.keys())
                default_index = 0
                for idx, label in enumerate(labels):
                    if str(options[label]) == preferred:
                        default_index = idx
                        break
                selected = st.selectbox("Product image", labels, index=default_index)
                source_path = options[selected]
                match = match_product_for_image(source_path)
                st.image(str(source_path), width=260)
            else:
                st.info("No downloaded mockups found. Use Printify Products first.")
        else:
            uploaded = st.file_uploader("Product image", type=["jpg","jpeg","png","webp"])
            if uploaded:
                import tempfile
                tmp = Path(tempfile.mkdtemp())
                source_path = tmp / uploaded.name
                source_path.write_bytes(uploaded.read() if hasattr(uploaded, "read") else bytes(uploaded))

        default_title = (
            st.session_state.get("selected_product_title")
            or (match.title if match else "")
            or "BKS Product"
        )
        default_tags = st.session_state.get("selected_product_tags") or (match.tags if match else "")
        title_in = st.text_input("Product title", default_title)
        tags_in = st.text_area("Tags", default_tags, height=90)
        default_collection = (
            st.session_state.get("detected_collection")
            or (match.collection if match else "")
            or "folklore"
        )
        collection = st.selectbox("Collection", COLLECTIONS,
                                   index=COLLECTIONS.index(
                                       default_collection
                                   ) if default_collection in COLLECTIONS else 0)
        product_types = [
            "lounge-pants","swim-trunks","one-piece-swimsuit","puffer-jacket",
            "windbreaker","pullover-hoodie","racerback-dress","athletic-shorts",
            "sneakers","backpack","travel-bag","flip-flop","cozy-slipper","womens-tee",
        ]
        default_product_type = (
            st.session_state.get("selected_product_type")
            or (match.product_type if match else "")
            or "lounge-pants"
        )
        product_type = st.selectbox(
            "Product type",
            product_types,
            index=product_types.index(default_product_type) if default_product_type in product_types else 0,
        )
        slots = st.multiselect("Slots to generate", [
            "product_front","product_back","editorial_square",
            "editorial_4x5","hero_banner","texture_detail"
        ], default=["editorial_4x5","hero_banner"])
        count   = st.slider("Variants per slot", 1, 4, 1)
        dry_run = st.checkbox("Dry run (prompts only — no API cost)", value=True)

    with col2:
        if st.button("🚀 Generate", use_container_width=True):
            if not source_path:
                st.warning("Select or upload a product image first.")
                st.stop()

            from pathlib import Path
            from modules.image_director import run_product

            progress_bar = st.progress(0.0)
            status_text  = st.empty()

            def cb(step: str, pct: float):
                progress_bar.progress(pct)
                status_text.text(step)

            result = run_product(
                source_image=Path(source_path),
                product_title=title_in,
                tags=[t.strip() for t in tags_in.split(",") if t.strip()],
                slots=slots,
                count=count,
                dry_run=dry_run,
                progress_cb=cb,
                collection_override=collection,
                product_type_override=product_type,
            )
            st.session_state["last_result"] = result
            st.success("Done!")

        result = st.session_state.get("last_result")
        if result:
            st.markdown("### Results")
            st.markdown(f"**Collection:** {result['collection'].upper()}  |  **Type:** {result['product_type']}")

            tabs = st.tabs([s.replace("_"," ").title() for s in (result.get("generated") or {}).keys()])
            for tab, (slot, gen_list) in zip(tabs, (result.get("generated") or {}).items()):
                with tab:
                    for i, g in enumerate(gen_list, 1):
                        st.markdown(f"**Variant {i}** — {g['status']}")
                        if g.get("output_jpg") and Path(str(g["output_jpg"])).exists():
                            st.image(str(g["output_jpg"]), width=300)
                        with st.expander("Prompt"):
                            st.code(g["prompt"])

            with st.expander("SEO"):
                seo = result.get("seo", {})
                st.text_input("SEO Title",       seo.get("seo_title",""))
                st.text_area("Meta Description", seo.get("seo_description",""))
                st.text_input("Handle",          seo.get("handle",""))
                st.text_input("Tags",            seo.get("tags",""))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PAGE: QUALITY CONTROL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
elif page == "✅ Quality Control":
    st.title("Quality Control")
    from modules.quality_validator import validate, score_label

    uploaded = st.file_uploader("Upload image to validate", type=["jpg","jpeg","png"])
    dry_run  = st.checkbox("Dry run (score = 100, no API call)", value=False)

    if uploaded and st.button("▶️ Validate"):
        import tempfile
        from pathlib import Path
        tmp = Path(tempfile.mkdtemp())
        src = tmp / uploaded.name
        src.write_bytes(uploaded.read() if hasattr(uploaded, "read") else bytes(uploaded))

        with st.spinner("Validating..."):
            result = validate(src, dry_run=dry_run)

        c1, c2 = st.columns([1, 2])
        c1.image(str(src), use_container_width=True)
        with c2:
            score = result["score"]
            label = score_label(score)
            st.markdown(f'<p class="qa-score {"qa-pass" if result["approved"] else "qa-fail"}">{score}/100</p>',
                        unsafe_allow_html=True)
            st.markdown(f"**{label}**")
            if result.get("issues"):
                st.error("Issues: " + " · ".join(result["issues"]))
            for k, v in (result.get("criteria") or {}).items():
                icon = "✅" if v.get("pass") else "❌"
                st.markdown(f"{icon} **{k.title()}** — {v.get('note','')}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PAGE: SHOPIFY EXPORT
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
elif page == "🚀 Shopify Export":
    st.title("Shopify Export")
    from modules.shopify_client import build_shopify_csv
    from config.settings import SHOPIFY_STORE

    result = st.session_state.get("last_result")
    if not result:
        st.info("Run the Shooting Generator first to produce images.")
        st.stop()

    seo   = result.get("seo", {})
    col   = result.get("collection", "")
    ptype = result.get("product_type", "")

    st.markdown(f"**Product:** {seo.get('handle','?')}  |  **Collection:** {col.upper()}")

    assets = []
    for slot, gen_list in (result.get("generated") or {}).items():
        for i, g in enumerate(gen_list, 1):
            if g.get("output_jpg") and Path(str(g["output_jpg"])).exists():
                assets.append({
                    "handle":         seo.get("handle",""),
                    "image_src":      str(g["output_jpg"]),
                    "image_position": len(assets) + 1,
                    "image_alt":      seo.get("alt_texts", {}).get(slot, ""),
                })

    if not assets:
        st.warning("No approved images found. Run Shooting Generator first.")
        st.stop()

    import pandas as pd
    st.dataframe(pd.DataFrame(assets), use_container_width=True)

    csv_str = build_shopify_csv(assets)
    st.download_button("⬇️ Download shopify_import.csv", csv_str,
                        file_name="shopify_import.csv", mime="text/csv")

    # ── Manifest download ──────────────────────────────────────────────────
    if result.get("manifest"):
        import json
        mf = result["manifest"]
        if isinstance(mf.get("json"), Path) and mf["json"].exists():
            st.download_button("⬇️ Download manifest.json",
                               mf["json"].read_text(encoding="utf-8"),
                               file_name="manifest.json", mime="application/json")
        if isinstance(mf.get("csv"), Path) and mf["csv"].exists():
            st.download_button("⬇️ Download manifest.csv",
                               mf["csv"].read_text(encoding="utf-8"),
                               file_name="manifest.csv", mime="text/csv")

    if SHOPIFY_STORE:
        product_id = st.text_input("Shopify Product ID (for direct API upload)")
        if product_id and st.button("🚀 Upload via API"):
            from modules.shopify_client import upload_image
            for i, a in enumerate(assets, 1):
                with st.spinner(f"Uploading image {i}/{len(assets)}..."):
                    try:
                        upload_image(product_id, Path(a["image_src"]),
                                     alt=a["image_alt"], position=a["image_position"])
                        st.success(f"Image {i} uploaded")
                    except Exception as e:
                        st.error(f"Image {i} error: {e}")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# PAGE: SETTINGS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
elif page == "⚙️ Settings":
    st.title("Settings")
    from config.settings import (
        OPENAI_API_KEY, PRINTIFY_API_TOKEN, PRINTIFY_SHOP_ID,
        SHOPIFY_STORE, SHOPIFY_ACCESS_TOKEN, REMOVE_BG_API_KEY,
        QA_THRESHOLD, OPENAI_IMAGE_MODEL
    )

    def _mask(s: str) -> str:
        return s[:6] + "..." + s[-4:] if len(s) > 12 else "***" if s else "❌ not set"

    st.subheader("API Keys")
    col1, col2 = st.columns(2)
    col1.markdown(f"**OpenAI:**  `{_mask(OPENAI_API_KEY)}`")
    col1.markdown(f"**Printify:** `{_mask(PRINTIFY_API_TOKEN)}`")
    col1.markdown(f"**Printify Shop ID:** `{PRINTIFY_SHOP_ID or '❌ not set'}`")
    col2.markdown(f"**Shopify Store:** `{SHOPIFY_STORE or '❌ not set'}`")
    col2.markdown(f"**Shopify Token:** `{_mask(SHOPIFY_ACCESS_TOKEN)}`")
    col2.markdown(f"**remove.bg:** `{_mask(REMOVE_BG_API_KEY)}`")

    st.divider()
    st.subheader("Generation")
    st.markdown(f"- **Model:** `{OPENAI_IMAGE_MODEL}`")
    st.markdown(f"- **QA Threshold:** `{QA_THRESHOLD}/100`")
    st.markdown(f"- **Quality:** `high`")

    st.divider()
    st.subheader("Edit .env")
    st.info("Edit `.env` in the project root, then restart the app.")
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        with st.expander("View .env (keys hidden)"):
            for line in env_path.read_text().splitlines():
                if "=" in line and not line.startswith("#"):
                    k, _, v = line.partition("=")
                    masked = _mask(v) if v else "❌ empty"
                    st.text(f"{k} = {masked}")
                else:
                    st.text(line)
