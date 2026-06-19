"""BKS Studio — Social & Marketplace Hub
Gestione centralizzata: Meta (FB+IG), Pinterest, Amazon Merch, Telegram.
Tutto tracciato GA4 via UTM — direttive Google.
"""
from __future__ import annotations
import csv, json, os, sys
from datetime import datetime, date
from pathlib import Path
from urllib.parse import urlencode

import requests
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import bks_nav

st.set_page_config(page_title="BKS Social Hub", page_icon="📣", layout="wide")
bks_nav.render("social")
OUTPUT_DIR = BASE_DIR / "output"
SOCIAL_DIR = OUTPUT_DIR / "social"
SOCIAL_DIR.mkdir(parents=True, exist_ok=True)

POSTS_CSV        = SOCIAL_DIR / "social_posts_queue.csv"
AMZN_CSV         = SOCIAL_DIR / "amazon_merch_designs.csv"
PINTEREST_CSV    = SOCIAL_DIR / "pinterest_pins_queue.csv"
TG_HISTORY       = SOCIAL_DIR / "telegram_history.json"

# ── Env ───────────────────────────────────────────────────────────────────────
def _load_env() -> None:
    p = BASE_DIR / ".env"
    if not p.exists(): return
    for raw in p.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line: continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

_load_env()

# ── Costanti brand ─────────────────────────────────────────────────────────────
BKS_COLLS   = ["hours","glyph","marker","riviera","pulse","token","flag","origin"]
BKS_SHOP    = "https://bakabo.club"
GA4_ID      = "bakabo-9a8c5"
GA4_PROP    = "483501489"
GTM_ID      = "GTM-PF5Z85KS"
MC_ID       = "5295165689"
PLATFORMS   = ["facebook","instagram","pinterest","amazon","telegram","tiktok"]

# ── ENV keys ──────────────────────────────────────────────────────────────────
def env(k: str, fallback: str = "") -> str:
    return os.environ.get(k, fallback)

def env_ok(*keys: str) -> bool:
    return all(bool(env(k)) for k in keys)

# ── UTM builder ───────────────────────────────────────────────────────────────
def build_utm(url: str, source: str, medium: str, campaign: str, content: str = "", term: str = "") -> str:
    params: dict[str, str] = {"utm_source": source, "utm_medium": medium, "utm_campaign": campaign}
    if content: params["utm_content"] = content
    if term:    params["utm_term"]    = term
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}{urlencode(params)}"

# ── Post CSV helpers ───────────────────────────────────────────────────────────
POST_FIELDS = ["id","created_at","platform","phase","collection","objective","format","publish_date","status","message","cta","url","utm_campaign"]

def load_posts() -> list[dict]:
    if not POSTS_CSV.exists(): return []
    with POSTS_CSV.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def save_posts(rows: list[dict]) -> None:
    with POSTS_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=POST_FIELDS, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)

def add_post(row: dict) -> None:
    rows = load_posts()
    row.setdefault("id", f"p-{datetime.now():%Y%m%d%H%M%S}")
    row.setdefault("created_at", datetime.now().strftime("%Y-%m-%d %H:%M"))
    rows.append({f: row.get(f,"") for f in POST_FIELDS})
    save_posts(rows)

# ── Amazon Merch helpers ───────────────────────────────────────────────────────
AMZN_FIELDS = ["id","collection","design_name","asin","marketplace","tier","status","bsr","royalty_usd","notes","last_checked"]

def load_designs() -> list[dict]:
    if not AMZN_CSV.exists(): return []
    with AMZN_CSV.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def save_designs(rows: list[dict]) -> None:
    with AMZN_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=AMZN_FIELDS, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)

# ── Pinterest CSV helpers ──────────────────────────────────────────────────────
PIN_FIELDS = ["id","collection","board","title","description","image_url","link","publish_date","status"]

def load_pins() -> list[dict]:
    if not PINTEREST_CSV.exists(): return []
    with PINTEREST_CSV.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def save_pins(rows: list[dict]) -> None:
    with PINTEREST_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=PIN_FIELDS, extrasaction="ignore")
        w.writeheader(); w.writerows(rows)

# ── Telegram helper ────────────────────────────────────────────────────────────
def tg_send(token: str, chat_id: str, text: str) -> tuple[bool, str]:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}, timeout=10)
        if r.ok and r.json().get("ok"):
            return True, "Inviato"
        return False, r.text[:200]
    except Exception as e:
        return False, str(e)

def tg_info(token: str) -> dict:
    try:
        r = requests.get(f"https://api.telegram.org/bot{token}/getMe", timeout=8)
        if r.ok and r.json().get("ok"):
            return r.json().get("result", {})
    except: pass
    return {}

def tg_history() -> list[dict]:
    if not TG_HISTORY.exists(): return []
    try: return json.loads(TG_HISTORY.read_text(encoding="utf-8"))
    except: return []

def tg_save_history(entry: dict) -> None:
    hist = tg_history()
    hist.insert(0, entry)
    TG_HISTORY.write_text(json.dumps(hist[:50], ensure_ascii=False, indent=2), encoding="utf-8")

# ── CSS BKS ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.plat-card {
    border:1px solid #2A2A2A; border-radius:6px;
    padding:1rem; margin-bottom:.5rem;
    background:#111;
}
.plat-ok   { border-left: 3px solid #1A6840; }
.plat-warn { border-left: 3px solid #9B2A1A; }
.plat-idle { border-left: 3px solid #5A5A5A; }
.utm-box {
    background:#0D0D0D; border:1px solid #2A2A2A;
    border-radius:4px; padding:.75rem;
    font-family:monospace; font-size:.8rem;
    word-break:break-all; color:#C9B79C;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar — Google directives ────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📊 Google Directives")

    ga4_ok  = bool(env("GA4_MEASUREMENT_ID") or GA4_ID)
    gtm_ok  = bool(GTM_ID)
    mc_ok   = bool(env("GOOGLE_MERCHANT_ID") or MC_ID)

    st.markdown(f"**GA4** {'🟢' if ga4_ok else '🔴'} `{GA4_ID}`")
    st.markdown(f"**GTM** {'🟢' if gtm_ok else '🔴'} `{GTM_ID}`")
    st.markdown(f"**Merchant** {'🟡' if not env('GOOGLE_MERCHANT_ID') else '🟢'} `{MC_ID}`")

    st.divider()
    st.markdown("**UTM Standard BKS**")
    st.caption("source: piattaforma")
    st.caption("medium: social / referral")
    st.caption("campaign: collezione-bks")
    st.caption("content: formato-post")

    st.divider()
    st.markdown("**Linee guida contenuto**")
    st.caption("✅ E-E-A-T: expertise, autenticità")
    st.caption("✅ Alt text su ogni immagine")
    st.caption("✅ Titoli ≤ 60 char (SEO)")
    st.caption("✅ Descrizioni 150–160 char")
    st.caption("✅ Ogni link ha UTM GA4")
    st.caption("✅ Nessun contenuto YMYL senza fonte")

# ── Main ──────────────────────────────────────────────────────────────────────
st.title("📣 BKS Social & Marketplace Hub")
st.caption("Facebook · Instagram · Pinterest · Amazon Merch · Telegram · TikTok — tutto tracciato GA4")

t_over, t_meta, t_pinterest, t_amazon, t_telegram, t_tiktok, t_analytics = st.tabs([
    "🌐 Overview", "📘 Meta (FB+IG)", "📌 Pinterest", "🛒 Amazon Merch", "✈️ Telegram", "🎵 TikTok", "📊 Analytics"
])

# ══════════════════════════════════════════════════════════════════════════════
# OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
with t_over:
    st.subheader("Status piattaforme")

    platforms_status = [
        ("📘 Facebook",   "FACEBOOK_PAGE_ID",                    "https://www.facebook.com/bakabofirm/",      "social",   "facebook"),
        ("📷 Instagram",  "INSTAGRAM_BUSINESS_ID",               "https://www.instagram.com/bakabofirm/",     "social",   "instagram"),
        ("📌 Pinterest",  "PINTEREST_ACCESS_TOKEN",              "https://pinterest.com/bakabofirm/",         "social",   "pinterest"),
        ("🛒 Amazon",     "AMAZON_MERCH_EMAIL",                  "https://merch.amazon.com/",                 "referral", "amazon"),
        ("✈️ Telegram",  "TELEGRAM_BOT_TOKEN",                  "https://t.me/",                             "referral", "telegram"),
        ("🎵 TikTok",    "TIKTOK_ADVERTISER_ID",                "https://www.tiktok.com/@bakabofirm",        "social",   "tiktok"),
    ]

    cols = st.columns(3)
    for i, (label, key, link, medium, src) in enumerate(platforms_status):
        connected = bool(env(key))
        css = "plat-ok" if connected else "plat-idle"
        badge = "🟢 Connesso" if connected else "⚪ Non configurato"
        utm_url = build_utm(BKS_SHOP, src, medium, "bks-studio-overview")
        with cols[i % 3]:
            st.markdown(f"""
<div class="plat-card {css}">
  <strong>{label}</strong><br/>
  <span style="font-size:.8rem;color:#888">{badge}</span><br/>
  <a href="{link}" target="_blank" style="font-size:.75rem;color:#C9B79C">→ Apri piattaforma</a>
</div>
""", unsafe_allow_html=True)

    st.divider()
    st.subheader("🔗 UTM Link Generator")
    st.caption("Genera link tracciati GA4 per qualsiasi contenuto BKS")

    uc1, uc2, uc3, uc4 = st.columns(4)
    utm_base   = uc1.selectbox("Pagina destinazione", [f"{BKS_SHOP}/collections/{c}" for c in BKS_COLLS] + [BKS_SHOP, f"{BKS_SHOP}/products"], label_visibility="visible")
    utm_src    = uc2.selectbox("Source", PLATFORMS)
    utm_medium = uc3.selectbox("Medium", ["social","organic","referral","email","paid_social"])
    utm_coll   = uc4.selectbox("Campaign (collezione)", BKS_COLLS + ["bks-studio","bks-drop","bks-launch"])
    utm_fmt    = uc1.selectbox("Content (formato)", ["feed-post","reel","story","pin","video","bio-link","dm","button"])
    final_url  = build_utm(utm_base, utm_src, utm_medium, utm_coll, utm_fmt)
    st.markdown(f'<div class="utm-box">{final_url}</div>', unsafe_allow_html=True)
    st.code(final_url, language=None)

    st.divider()
    st.subheader("📋 Queue posts recenti")
    posts = load_posts()
    if posts:
        import pandas as pd
        df = pd.DataFrame(posts)
        st.dataframe(df[["platform","collection","format","publish_date","status","message"]].head(20), width="stretch", hide_index=True)
    else:
        st.info("Nessun post in queue. Crea contenuto dai tab piattaforma.")

# ══════════════════════════════════════════════════════════════════════════════
# META — FACEBOOK + INSTAGRAM
# ══════════════════════════════════════════════════════════════════════════════
with t_meta:
    st.subheader("Meta Business — Facebook + Instagram")

    meta_ok = env_ok("META_BUSINESS_ID","META_ACCESS_TOKEN")
    fb_ok   = bool(env("FACEBOOK_PAGE_ID"))
    ig_ok   = bool(env("INSTAGRAM_BUSINESS_ID"))

    c1,c2,c3 = st.columns(3)
    c1.metric("Meta Business", "🟢 OK" if meta_ok else "🔴 mancante", help="META_BUSINESS_ID + META_ACCESS_TOKEN")
    c2.metric("Facebook Page", "🟢 OK" if fb_ok   else "⚪ da collegare", help="FACEBOOK_PAGE_ID")
    c3.metric("Instagram Biz", "🟢 OK" if ig_ok   else "⚪ da collegare", help="INSTAGRAM_BUSINESS_ID")

    if not meta_ok:
        st.warning("Configura `META_BUSINESS_ID` e `META_ACCESS_TOKEN` nel file `.env` per abilitare posting automatico.")
        with st.expander("Come ottenere le credenziali Meta"):
            st.markdown("""
1. Vai su [Meta Business Suite](https://business.facebook.com) → Impostazioni → Informazioni aziendali → **Business ID**
2. Vai su [Meta for Developers](https://developers.facebook.com) → La tua App → Genera **Access Token** con permessi: `pages_manage_posts`, `instagram_content_publish`, `pages_read_engagement`
3. Aggiungi in `.env`:
   ```
   META_BUSINESS_ID=xxxxxxx
   META_ACCESS_TOKEN=EAAxx...
   FACEBOOK_PAGE_ID=xxxxxxx
   INSTAGRAM_BUSINESS_ID=xxxxxxx
   ```
""")

    st.divider()
    st.subheader("✍️ Crea contenuto Meta")

    with st.form("meta_post_form"):
        mc1,mc2,mc3 = st.columns(3)
        meta_platform = mc1.selectbox("Piattaforma", ["facebook","instagram","entrambi"])
        meta_format   = mc2.selectbox("Formato", ["feed-post","reel","story","carousel","reels-series"])
        meta_coll     = mc3.selectbox("Collezione BKS", BKS_COLLS)
        meta_pub_date = st.date_input("Data pubblicazione", value=date.today())
        meta_objective= st.selectbox("Obiettivo", ["awareness","engagement","traffic","conversion","product-launch"])
        meta_headline = st.text_input("Headline (≤ 60 char per SEO Google)", max_chars=80)
        meta_msg      = st.text_area("Testo post", height=120, placeholder="BKS Studio — [collezione]. Link in bio →")
        meta_cta      = st.selectbox("CTA", ["Shop Now","Learn More","See More","Book Now","Sign Up","Contact Us"])

        # UTM auto
        meta_utm_url = build_utm(
            f"{BKS_SHOP}/collections/{meta_coll}",
            "instagram" if meta_platform=="instagram" else "facebook",
            "social", meta_coll, meta_format
        )
        st.markdown(f"**UTM link automatico:**")
        st.code(meta_utm_url, language=None)

        # Google content check
        char_count = len(meta_headline)
        if char_count > 60:
            st.warning(f"⚠️ Headline {char_count}/60 char — Google preferisce ≤ 60 per SEO")
        elif char_count > 0:
            st.success(f"✅ Headline {char_count}/60 char — OK Google")

        if st.form_submit_button("Aggiungi alla queue", type="primary"):
            if meta_msg:
                for plat in (["facebook","instagram"] if meta_platform=="entrambi" else [meta_platform]):
                    add_post({
                        "platform":     plat,
                        "phase":        "09",
                        "collection":   meta_coll,
                        "objective":    meta_objective,
                        "format":       meta_format,
                        "publish_date": str(meta_pub_date),
                        "status":       "draft",
                        "message":      meta_msg,
                        "cta":          meta_cta,
                        "url":          meta_utm_url,
                        "utm_campaign": meta_coll,
                    })
                st.success(f"Post aggiunto alla queue per {meta_platform}!")
            else:
                st.error("Inserisci il testo del post")

    st.divider()
    st.subheader("📋 Queue Meta")
    meta_posts = [p for p in load_posts() if p.get("platform") in ("facebook","instagram")]
    if meta_posts:
        import pandas as pd
        df_meta = pd.DataFrame(meta_posts)
        edited = st.data_editor(df_meta, width="stretch", hide_index=True, num_rows="dynamic")
        c_a, c_b = st.columns(2)
        if c_a.button("Salva modifiche", key="save_meta"):
            other = [p for p in load_posts() if p.get("platform") not in ("facebook","instagram")]
            save_posts(other + edited.to_dict("records"))
            st.success("Salvato!")
        if c_b.button("Esporta CSV Meta", key="exp_meta"):
            st.download_button("⬇️ Download", df_meta.to_csv(index=False).encode(), "meta_posts.csv", "text/csv")
    else:
        st.info("Nessun post Meta in queue.")

    st.divider()
    st.subheader("🛍️ Meta Commerce — Catalogo prodotti")
    st.caption("Il catalogo BKS deve essere sincronizzato con Meta Commerce Manager per Product Tags e Shopping.")
    mc_cols = st.columns(3)
    mc_cols[0].info("**Pixel Meta** `GTM-PF5Z85KS`\nInstallato via GTM")
    mc_cols[1].info("**Catalogo prodotti**\nShopify → Meta via feed XML/CSV\nURL: bakabo.myshopify.com/collections/all.atom")
    mc_cols[2].info("**Pixel eventi**\nViewContent · AddToCart\nPurchase tracciati via GTM")

# ══════════════════════════════════════════════════════════════════════════════
# PINTEREST
# ══════════════════════════════════════════════════════════════════════════════
with t_pinterest:
    st.subheader("Pinterest Business — Boards & Rich Pins")

    pin_ok = bool(env("PINTEREST_ACCESS_TOKEN"))
    pa1,pa2,pa3 = st.columns(3)
    pa1.metric("Pinterest API", "🟢 OK" if pin_ok else "⚪ da collegare")
    pa2.metric("Rich Pins", "🟡 verifica", help="Validare su Pinterest Rich Pin Validator")
    pa3.metric("Shopping Catalog", "⚪ da attivare", help="Shopify → Pinterest Catalog")

    if not pin_ok:
        with st.expander("Come configurare Pinterest Business"):
            st.markdown("""
1. [Pinterest Business Hub](https://business.pinterest.com) → Account → Richiedi accesso API
2. Crea app su [Pinterest Developers](https://developers.pinterest.com)
3. Genera **Access Token** con scopes: `boards:read`, `boards:write`, `pins:read`, `pins:write`
4. Aggiungi in `.env`: `PINTEREST_ACCESS_TOKEN=xxxxx`
5. **Rich Pins** → valida URL: `https://developers.pinterest.com/tools/url-debugger/`
6. **Product Catalog** → Pinterest Business Hub → Catalogs → Connetti Shopify feed
""")

    st.divider()
    st.subheader("📌 Board Structure BKS")
    boards = [
        ("BKS Hours Collection",   "hours",    "Collezione Hours — orologi e tempo. AOP premium streetwear."),
        ("BKS Glyph Collection",   "glyph",    "Collezione Glyph — simboli e glifi. Design contemporaneo."),
        ("BKS Marker Collection",  "marker",   "Collezione Marker — linee e segni. Streetwear contemporaneo."),
        ("BKS Riviera Collection", "riviera",  "Collezione Riviera — sole e mare. Stile mediterraneo."),
        ("BKS Pulse Collection",   "pulse",    "Collezione Pulse — ritmo e energia. Drop esclusivi."),
        ("BKS Token Collection",   "token",    "Collezione Token — simboli e valore. Limited edition."),
        ("BKS Flag Collection",    "flag",     "Collezione Flag — bandiere e identità. Global streetwear."),
        ("BKS Folklore Collection","folklore", "Collezione Folklore — radici e tradizione. Heritage AOP."),
        ("BKS Studio — All Drops", "",         "Tutti i drop BKS Studio — bakabo.club"),
    ]
    import pandas as pd
    df_boards = pd.DataFrame([{"Board": b[0], "Slug": b[1], "Descrizione SEO": b[2], "URL": build_utm(f"{BKS_SHOP}/collections/{b[1]}" if b[1] else BKS_SHOP, "pinterest","social",b[1] or "bks-studio","pin-board")} for b in boards])
    st.dataframe(df_boards, width="stretch", hide_index=True)

    st.divider()
    st.subheader("📌 Crea Pin")
    with st.form("pin_form"):
        pc1,pc2 = st.columns(2)
        pin_board = pc1.selectbox("Board", [b[0] for b in boards])
        pin_coll  = pc2.selectbox("Collezione", BKS_COLLS)
        pin_title = st.text_input("Titolo Pin (≤ 60 char — SEO Google)", max_chars=70)
        pin_desc  = st.text_area("Descrizione (150–160 char per SEO)", max_chars=200, height=80,
                                  placeholder="BKS Studio — [design]. Premium AOP streetwear. Scopri la collezione [nome] su bakabo.club #bks #streetwear")
        pin_img   = st.text_input("URL immagine (1:1 o 2:3 per Pinterest)", placeholder="https://bakabo.club/cdn/shop/...")
        pin_date  = st.date_input("Data pubblicazione", key="pin_date")

        pin_utm = build_utm(f"{BKS_SHOP}/collections/{pin_coll}", "pinterest","social", pin_coll, "pin-feed")
        st.caption(f"Link UTM: `{pin_utm}`")

        # Check lunghezza
        desc_len = len(pin_desc)
        if 150 <= desc_len <= 160:
            st.success(f"✅ Descrizione {desc_len}/160 char — perfetta per SEO")
        elif desc_len > 0:
            st.info(f"ℹ️ Descrizione {desc_len}/160 char — target 150-160")

        if st.form_submit_button("Aggiungi Pin alla queue", type="primary"):
            if pin_title and pin_img:
                pins = load_pins()
                pins.append({f: "" for f in PIN_FIELDS} | {
                    "id":           f"pin-{datetime.now():%Y%m%d%H%M%S}",
                    "collection":   pin_coll,
                    "board":        pin_board,
                    "title":        pin_title,
                    "description":  pin_desc,
                    "image_url":    pin_img,
                    "link":         pin_utm,
                    "publish_date": str(pin_date),
                    "status":       "draft",
                })
                save_pins(pins)
                st.success("Pin aggiunto!")
            else:
                st.error("Titolo e URL immagine obbligatori")

    pins = load_pins()
    if pins:
        st.divider()
        df_pins = pd.DataFrame(pins)
        st.dataframe(df_pins[["board","collection","title","publish_date","status"]], width="stretch", hide_index=True)
        st.download_button("⬇️ Esporta pins CSV", pd.DataFrame(pins).to_csv(index=False).encode(), "bks_pinterest_pins.csv", "text/csv")

# ══════════════════════════════════════════════════════════════════════════════
# AMAZON MERCH ON DEMAND
# ══════════════════════════════════════════════════════════════════════════════
with t_amazon:
    st.subheader("🛒 Amazon Merch on Demand")
    st.caption("Pubblica design BKS su Amazon Merch → royalties passive + visibilità globale.")

    amzn_email  = bool(env("AMAZON_MERCH_EMAIL"))
    amzn_status = env("AMAZON_MERCH_TIER", "Standard")

    aa1,aa2,aa3,aa4 = st.columns(4)
    aa1.metric("Account",  "🟢 Set" if amzn_email else "⚪ Email non set")
    aa2.metric("Tier",     amzn_status)
    aa3.metric("Mercati",  "US · UK · DE · FR · IT")
    aa4.metric("Royalties","→ Merch portal")

    if not amzn_email:
        with st.expander("Setup Amazon Merch on Demand"):
            st.markdown("""
1. Richiedi accesso su [merch.amazon.com](https://merch.amazon.com) con account Amazon esistente
2. Usa email `bakabofirm@gmail.com` per richiedere accesso
3. Dopo l'approvazione, aggiungi in `.env`:
   ```
   AMAZON_MERCH_EMAIL=bakabofirm@gmail.com
   AMAZON_MERCH_TIER=Standard
   ```
4. **Tier progression:** Standard (10 slot) → Premium (25) → Pro (100+)
5. **Taglia file:** PNG 15×18 pollici, 300 DPI, trasparente, max 25 MB
""")

    st.divider()
    st.subheader("📐 Specifiche design Amazon Merch")
    spec_cols = st.columns(3)
    spec_cols[0].info("**File:** PNG con sfondo trasparente\n**Risoluzione:** 4500×5400 px (300 DPI)\n**Max:** 25 MB")
    spec_cols[1].info("**Area stampa safe:** 14×16.5 pollici\n**Colori:** RGB (sRGB IEC61966-2.1)\n**Nessun:** testo illeggibile, content violazione")
    spec_cols[2].info("**Prodotti:** T-shirt, Sweatshirt, Hoodie, PopSocket, Tote, Phone cover\n**Tier Standard:** 10 design attivi")

    st.divider()
    st.subheader("📋 Design tracker")

    # Form aggiungi design
    with st.form("amzn_form"):
        af1,af2,af3 = st.columns(3)
        amzn_coll   = af1.selectbox("Collezione BKS", BKS_COLLS)
        amzn_design = af2.text_input("Nome design")
        amzn_market = af3.multiselect("Marketplace", ["US","UK","DE","FR","IT","ES","JP"], default=["US","DE","IT"])
        amzn_asin   = st.text_input("ASIN (dopo approvazione)", placeholder="B0XXXXXXXXXX")
        amzn_notes  = st.text_area("Note", height=60)
        amzn_royalty= st.number_input("Royalty USD (per vendita)", min_value=0.0, value=3.50, step=0.10)

        if st.form_submit_button("Traccia design", type="primary"):
            if amzn_design:
                designs = load_designs()
                for mkt in (amzn_market or ["US"]):
                    designs.append({f:"" for f in AMZN_FIELDS} | {
                        "id":           f"amzn-{datetime.now():%Y%m%d%H%M%S}-{mkt}",
                        "collection":   amzn_coll,
                        "design_name":  amzn_design,
                        "asin":         amzn_asin,
                        "marketplace":  mkt,
                        "tier":         amzn_status,
                        "status":       "pending" if not amzn_asin else "live",
                        "royalty_usd":  str(amzn_royalty),
                        "notes":        amzn_notes,
                        "last_checked": datetime.now().strftime("%Y-%m-%d"),
                    })
                save_designs(designs)
                st.success(f"Design '{amzn_design}' tracciato per {', '.join(amzn_market or ['US'])}!")
            else:
                st.error("Inserisci il nome del design")

    designs = load_designs()
    if designs:
        import pandas as pd
        df_amzn = pd.DataFrame(designs)
        edited_amzn = st.data_editor(df_amzn, width="stretch", hide_index=True, num_rows="dynamic")
        col_s, col_d = st.columns(2)
        if col_s.button("Salva", key="save_amzn"):
            save_designs(edited_amzn.to_dict("records"))
            st.success("Salvato!")
        col_d.download_button("⬇️ Esporta", pd.DataFrame(designs).to_csv(index=False).encode(), "amazon_merch.csv", "text/csv")

        # Summary
        st.divider()
        live = sum(1 for d in designs if d.get("status")=="live")
        total_royalty = sum(float(d.get("royalty_usd",0) or 0) for d in designs if d.get("status")=="live")
        sc1,sc2,sc3 = st.columns(3)
        sc1.metric("Design live", live)
        sc2.metric("Design pending", len(designs)-live)
        sc3.metric("Royalty potenziale/vendita", f"${total_royalty:.2f}")
    else:
        st.info("Nessun design tracciato. Aggiungi il primo design dalla form.")

    st.divider()
    with st.expander("🔗 Link Amazon Merch con UTM GA4"):
        for mkt, domain in [("US","amazon.com"),("IT","amazon.it"),("DE","amazon.de"),("UK","amazon.co.uk")]:
            url = build_utm(f"https://www.{domain}/s?k=bks+studio+streetwear", "amazon","referral","amazon-merch",f"search-{mkt.lower()}")
            st.code(url, language=None)

# ══════════════════════════════════════════════════════════════════════════════
# TELEGRAM
# ══════════════════════════════════════════════════════════════════════════════
with t_telegram:
    st.subheader("✈️ Telegram — Bot Notifiche BKS")
    st.caption("Bot per drop announcements, restock alert, comunicazioni community.")

    tg_token   = env("TELEGRAM_BOT_TOKEN")
    tg_chat    = env("TELEGRAM_CHAT_ID")
    tg_channel = env("TELEGRAM_CHANNEL_ID")

    t1,t2,t3 = st.columns(3)
    t1.metric("Bot Token",    "🟢 Set" if tg_token   else "⚪ mancante")
    t2.metric("Chat/User ID", "🟢 Set" if tg_chat    else "⚪ mancante")
    t3.metric("Channel ID",   "🟢 Set" if tg_channel else "⚪ opzionale")

    if tg_token:
        bot_info = tg_info(tg_token)
        if bot_info:
            st.success(f"🤖 Bot: **@{bot_info.get('username','')}** — {bot_info.get('first_name','')}")
        else:
            st.error("Token non valido o bot non raggiungibile.")
    else:
        with st.expander("Come creare il BKS Telegram Bot"):
            st.markdown("""
1. Cerca **@BotFather** su Telegram → `/newbot`
2. Nome: `BKS Studio Bot` → Username: `BKSStudioBot`
3. Copia il **token** e aggiungi in `.env`: `TELEGRAM_BOT_TOKEN=123456:ABCxxx`
4. Per il Chat ID:
   - Aggiungi il bot al canale/gruppo
   - Vai su `https://api.telegram.org/bot<TOKEN>/getUpdates`
   - Copia il `chat.id` dal JSON → `TELEGRAM_CHAT_ID=xxxxxxx`
5. Opzionale: `TELEGRAM_CHANNEL_ID=-100xxxxxxx` (canale pubblico, inizia con -100)
""")

    st.divider()
    st.subheader("📤 Invia messaggio")

    # Template messaggi
    msg_templates = {
        "🚀 Nuovo Drop": f"🚀 *BKS STUDIO — NUOVO DROP*\n\nCollezione [NOME] è live su bakabo.club\n→ {build_utm(BKS_SHOP+'/collections/drop', 'telegram','referral','bks-drop','tg-announcement')}\n\n#BKS #streetwear #bakabo",
        "⚡ Restock Alert": f"⚡ *RESTOCK ALERT*\n\n[PRODOTTO] è tornato disponibile.\n→ {build_utm(BKS_SHOP, 'telegram','referral','restock','tg-alert')}\n\nQuantità limitata. #BKS",
        "🎁 Offerta Esclusiva": f"🎁 *OFFERTA ESCLUSIVA — Solo oggi*\n\n[DESCRIZIONE OFFERTA]\n→ {build_utm(BKS_SHOP, 'telegram','referral','promo','tg-promo')}\n\n#BKS #sale",
        "📸 Behind the scenes": "📸 *Behind the Scenes — BKS Studio*\n\n[DESCRIZIONE CONTENUTO]\n\n#BKS #streetwear #fashion",
        "📣 Annuncio custom": "",
    }

    tg_template = st.selectbox("Template", list(msg_templates.keys()))
    tg_text = st.text_area("Testo messaggio (Markdown Telegram)", value=msg_templates.get(tg_template,""), height=150)
    tg_target = st.radio("Destinatario", ["Chat ID", "Channel ID"], horizontal=True)
    target_id = tg_chat if tg_target == "Chat ID" else tg_channel

    col_send, col_test = st.columns(2)
    if col_send.button("📤 Invia ora", type="primary", disabled=not (tg_token and target_id)):
        ok, msg = tg_send(tg_token, target_id, tg_text)
        if ok:
            st.success(f"✅ Inviato!")
            tg_save_history({"ts": datetime.now().isoformat(), "target": target_id[:10]+"...", "text": tg_text[:100], "ok": True})
        else:
            st.error(f"❌ Errore: {msg}")

    if col_test.button("🔔 Test ping", disabled=not tg_token):
        test_id = tg_chat or tg_channel
        if test_id:
            ok, msg = tg_send(tg_token, test_id, "🔔 *BKS Bot* — test connessione ✅")
            if ok: st.success("Test inviato!")
            else: st.error(msg)
        else:
            st.warning("Configura TELEGRAM_CHAT_ID o TELEGRAM_CHANNEL_ID")

    if not (tg_token and target_id):
        st.warning("Configura TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID nel file .env")

    # History
    history = tg_history()
    if history:
        st.divider()
        st.markdown("#### Ultimi 10 messaggi inviati")
        import pandas as pd
        st.dataframe(pd.DataFrame(history[:10]), width="stretch", hide_index=True)

    st.divider()
    st.subheader("🤖 Comandi bot pianificati")
    st.caption("Da implementare in futuro con python-telegram-bot webhook")
    commands_df = {
        "Comando":   ["/catalog","/drop","/price","/colls","/subscribe","/help"],
        "Risposta":  [
            "Lista collezioni BKS con link UTM",
            "Ultimi drop disponibili su bakabo.club",
            "Prezzo prodotto per fascia",
            "Lista tutte le 8 collezioni BKS",
            "Iscriviti alle notifiche drop",
            "Lista comandi disponibili"
        ],
        "Status": ["pianificato"]*6
    }
    import pandas as pd
    st.dataframe(pd.DataFrame(commands_df), width="stretch", hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# TIKTOK
# ══════════════════════════════════════════════════════════════════════════════
with t_tiktok:
    st.subheader("🎵 TikTok Business")
    st.caption("Content calendar, TikTok Shop sync, Pixel tracking.")

    tt_ok = env_ok("TIKTOK_ADVERTISER_ID","TIKTOK_ACCESS_TOKEN")
    tc1,tc2 = st.columns(2)
    tc1.metric("TikTok Business", "🟢 OK" if tt_ok else "⚪ da collegare")
    tc2.metric("TikTok Shop",     "⚪ da attivare", help="Richiede account TikTok Shop")

    if not tt_ok:
        with st.expander("Setup TikTok Business"):
            st.markdown("""
1. [TikTok Business Center](https://business.tiktok.com) → Settings → Ottieni **Advertiser ID**
2. Crea API app su [TikTok for Developers](https://developers.tiktok.com)
3. Genera **Access Token** con scope: `video.publish`, `user.info.basic`
4. Aggiungi in `.env`: `TIKTOK_ADVERTISER_ID=xxxxx` e `TIKTOK_ACCESS_TOKEN=xxxxx`
""")

    st.divider()
    st.subheader("📅 Content calendar TikTok")
    with st.form("tiktok_form"):
        tt1,tt2 = st.columns(2)
        tt_coll   = tt1.selectbox("Collezione", BKS_COLLS)
        tt_format = tt2.selectbox("Formato", ["reel-15s","reel-30s","reel-60s","duet","stitch","live"])
        tt_msg    = st.text_area("Caption TikTok (max 150 char)", max_chars=150,
                                  placeholder="BKS Studio — [design]. Link bio. #bks #streetwear #aop")
        tt_date   = st.date_input("Publish date", key="tt_date")
        tt_utm    = build_utm(f"{BKS_SHOP}/collections/{tt_coll}", "tiktok","social",tt_coll,tt_format)
        st.caption(f"UTM: `{tt_utm}`")

        if st.form_submit_button("Aggiungi a queue", type="primary"):
            if tt_msg:
                add_post({
                    "platform": "tiktok", "phase": "09",
                    "collection": tt_coll, "format": tt_format,
                    "publish_date": str(tt_date), "status": "draft",
                    "message": tt_msg, "url": tt_utm,
                    "utm_campaign": tt_coll,
                })
                st.success("Aggiunto alla queue!")
            else: st.error("Inserisci la caption")

    tt_posts = [p for p in load_posts() if p.get("platform")=="tiktok"]
    if tt_posts:
        import pandas as pd
        st.dataframe(pd.DataFrame(tt_posts)[["collection","format","publish_date","status","message"]], width="stretch", hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# ANALYTICS — GOOGLE DIRECTIVES
# ══════════════════════════════════════════════════════════════════════════════
with t_analytics:
    st.subheader("📊 Google Analytics 4 — Direttive Globali")
    st.caption("Tutti i link social usano UTM per tracciamento GA4. Merchant Center come source of truth.")

    ga1,ga2,ga3,ga4 = st.columns(4)
    ga1.metric("GA4 Property", GA4_ID)
    ga2.metric("GA4 ID",       GA4_PROP)
    ga3.metric("GTM Container",GTM_ID)
    ga4.metric("Merchant ID",  env("GOOGLE_MERCHANT_ID") or MC_ID)

    st.divider()
    st.subheader("📋 UTM Coverage — tutti i canali")
    import pandas as pd
    utms = []
    for coll in BKS_COLLS[:4]:
        url_base = f"{BKS_SHOP}/collections/{coll}"
        for src, med, fmt in [
            ("facebook","social","feed-post"),
            ("instagram","social","reel"),
            ("pinterest","social","pin-feed"),
            ("amazon","referral","search"),
            ("telegram","referral","tg-announcement"),
            ("tiktok","social","reel-30s"),
        ]:
            utms.append({
                "Collezione": coll,
                "Piattaforma": src,
                "URL tracciato": build_utm(url_base, src, med, coll, fmt)
            })

    df_utms = pd.DataFrame(utms)
    st.dataframe(df_utms, width="stretch", hide_index=True)
    st.download_button("⬇️ Esporta UTM matrix", df_utms.to_csv(index=False).encode(), "bks_utm_matrix.csv", "text/csv")

    st.divider()
    st.subheader("✅ Checklist Google Directives per ogni post")
    checklist = [
        ("UTM tracciato su ogni link esterno → bakabo.club", True),
        ("Alt text su ogni immagine (SEO + accessibilità)", True),
        ("Headline ≤ 60 char su Facebook e Pinterest",       True),
        ("Descrizione 150–160 char su Pinterest (Rich Pin)", True),
        ("Nessun contenuto YMYL senza fonte verificata",     True),
        ("E-E-A-T: mostra autenticità brand (studio shots)", True),
        ("Structured data (Product Schema) su Shopify",      True),
        ("GA4 eventi: ViewContent, AddToCart tracciati",     True),
        ("Merchant Center prodotti approvati (no penalità)", True),
        ("Copyright: solo immagini BKS originali",           True),
        ("Telegram messaggi: link sempre con UTM",           True),
        ("Amazon ASIN tracciato in dashboard BKS",           True),
    ]
    for item, done in checklist:
        icon = "✅" if done else "⬜"
        st.markdown(f"{icon} {item}")

    st.divider()
    st.subheader("📅 Post frequency target")
    freq_data = {
        "Piattaforma": ["Facebook","Instagram","Pinterest","TikTok","Telegram","Amazon Merch"],
        "Frequenza":   ["3×/settimana","1×/giorno","5×/giorno","1×/giorno","1×/settimana (drop only)","1 design/settimana"],
        "Tipo contenuto": ["prodotto+collezione","reel+carousel","pin prodotto","reel lifestyle","drop announcement","nuovo design"],
        "Obiettivo GA4": ["traffic","engagement+traffic","traffic+conversion","awareness","retention","conversione"],
    }
    st.dataframe(pd.DataFrame(freq_data), width="stretch", hide_index=True)
