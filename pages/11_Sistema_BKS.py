"""BKS SISTEMA — Drone view · Gantt editoriale anni 70/80 · v3 (24/06/2026)."""
import os
import socket
from datetime import datetime
from pathlib import Path

import streamlit as st

import bks_nav

st.set_page_config(page_title="BKS Sistema", page_icon="◈", layout="wide")
bks_nav.render("sistema")

# ─── costanti ────────────────────────────────────────────────────────────────

ROOT     = Path(__file__).resolve().parent.parent
ENV_PATH = ROOT / ".env"
TODAY    = datetime.now().strftime("%d.%m.%Y  %H:%M")

# ─── .env loader ─────────────────────────────────────────────────────────────

def _load_env() -> dict[str, str]:
    out: dict[str, str] = {}
    if not ENV_PATH.exists():
        return out
    for raw in ENV_PATH.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip(); v = v.strip().strip('"').strip("'")
        if k and v:
            out[k] = v
    return out

@st.cache_data(ttl=60, show_spinner=False)
def _env() -> dict[str, str]:
    return _load_env()

def _has(key: str) -> bool:
    return bool(_env().get(key, "").strip())

def _val(key: str, mask: bool = True) -> str:
    v = _env().get(key, "")
    if not v:
        return "—"
    if mask:
        return v[:6] + "…" if len(v) > 6 else "***"
    return v

def _pub(key: str) -> str:
    return _env().get(key, "—")

# ─── componenti sistema (aggiornato 24/06/2026) ───────────────────────────────

COMPONENTI = [
    # nome,                  area,          pct,  stato,      colore,     note
    ("Tema Shopify TM04",   "STORE",        100,  "done",    "#c8c4be", "V.22 live · 48/48 audit · Camerino v3"),
    ("Token System CSS",    "STORE",        100,  "done",    "#c8a96e", "3-layer: primitive→semantic→component · 20 file"),
    ("Member Dashboard",    "STORE",         95,  "attivo",  "#c8a96e", "Creations · BKS Verse tab · Gold ring"),
    ("AI Worker v16",       "CLOUD",         95,  "attivo",  "#9828d8", "KV+AI bindings live · /chat /social /origins"),
    ("Catalogo Prodotti",   "CATALOGO",      72,  "attivo",  "#d4a030", "202 prod · 8 coll · 63 rework pending"),
    ("BKS Origins",         "CATALOGO",      65,  "attivo",  "#489808", "42 originali · Worker → Creations tab"),
    ("Social Channels",     "MARKETING",     52,  "parziale","#c04418", "Instagram OK · Pinterest sospeso (appeal)"),
    ("Google Merchant",     "MARKETING",     42,  "pending", "#0ca898", "35.1K · limited quantity issue · Wixpa re-sub"),
    ("Quality Gate",        "CATALOGO",      20,  "pending", "#8888cc", "63 needs_rework · da riprendere dopo OpenAI reload"),
    ("BKS Verse",           "PIATTAFORMA",   32,  "pending", "#c82020", "FastAPI :8001 up · Fase 0 Luglio 2026"),
    ("Shopify Markets",     "STORE",         10,  "pending", "#3daed6", "IT/EN multilingua · fix /en/ GMC"),
]
AREE_ORDER = ["STORE", "CATALOGO", "CLOUD", "MARKETING", "PIATTAFORMA"]

# ─── servizi ─────────────────────────────────────────────────────────────────

SERVIZI_LOCALI = [
    ("BKS Studio",      "localhost",       8501),
    ("Try-On Engine",   "localhost",       8010),
]
SERVIZI_CLOUD = [
    ("Hetzner HEL",     "95.217.232.186",  8001),
    ("Hetzner Admin",   "95.217.232.186",  8099),
]
CF_WORKERS = [
    ("bks-agent (v16)",          "bks-agent.bakabo.workers.dev"),
    ("bks-account-redirect",     "account.bakabo.club"),
    ("bks-agent-refresh (cron)", "bks-agent-refresh.bakabo.workers.dev"),
]

def _ping(host: str, port: int, t: float = 0.7) -> bool:
    try:
        with socket.create_connection((host, port), timeout=t): return True
    except OSError: return False

@st.cache_data(ttl=25, show_spinner=False)
def _svc_status() -> dict[str, bool]:
    r: dict[str, bool] = {}
    for n, h, p in SERVIZI_LOCALI + SERVIZI_CLOUD:
        r[f"{n}:{p}"] = _ping(h, p)
    return r

# ─── vault ───────────────────────────────────────────────────────────────────

VAULT_GROUPS = [
    ("Shopify",    ["SHOPIFY_ADMIN_TOKEN","SHOPIFY_MYSHOPIFY_DOMAIN","SHOPIFY_STORE","SHOPIFY_API_VERSION"]),
    ("Printify",   ["PRINTIFY_API_TOKEN","PRINTIFY_SHOP_ID","PRINTIFY_SHOP_TITLE"]),
    ("OpenAI",     ["OPENAI_API_KEY","OPENAI_DEFAULT_MODEL","OPENAI_ORGANIZATION_ID","OPENAI_VISION_MODEL"]),
    ("Cloudflare", ["CLOUDFLARE_API_TOKEN","CLOUDFLARE_ACCOUNT_ID","CLOUDFLARE_ZONE_NAME"]),
    ("Google",     ["GOOGLE_MERCHANT_ID","GA4_PROPERTY_ID","GTM_TARGET","YOUTUBE_API_KEY","YOUTUBE_CHANNEL_ID"]),
    ("Meta",       ["META_ACCESS_TOKEN","INSTAGRAM_BUSINESS_ID","FACEBOOK_PAGE_ID","META_BUSINESS_ID"]),
    ("HeyGen",     ["HEYGEN_API_KEY","HEYGEN_AVATAR_ID","HEYGEN_VOICE_ID"]),
    ("Email",      ["OFFICIAL_INBOX_EMAIL","OFFICIAL_INBOX_IMAP_HOST","SMTP_USER","SMTP_HOST","SMTP_PORT"]),
    ("Telegram",   ["TELEGRAM_BOT_TOKEN","TELEGRAM_BOT_USERNAME","TELEGRAM_BOT_URL"]),
    ("BKS / AI",   ["BKS_ASSISTANT_PUBLIC_TOKEN","BKS_ASSISTANT_PUBLIC_ENDPOINT","OPENAI_VECTOR_STORE_ID"]),
]

# ─── CSS ─────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:ital,wght@0,300;0,400;0,500;1,300&family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,700;1,9..40,300&family=Playfair+Display:wght@900&display=swap');

section.main > div { padding-top: 0 !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }

:root {
  --ink:    #1a0e05;
  --paper:  #f0e6cc;
  --paper2: #e4d8b4;
  --rule:   #1a0e05;
  --muted:  #6b5c42;
  --on:     #1f6b2e;
  --off:    #9b2412;
  --warn:   #8b4a00;
  --bks-gold: #c8a96e;
}

.bks-mast {
  background: var(--ink); color: #f0e6cc;
  padding: 12px 28px 10px;
  display: flex; justify-content: space-between; align-items: baseline;
  border-bottom: 3px solid var(--bks-gold);
}
.bks-mast__title {
  font-family: 'Playfair Display', Georgia, serif;
  font-weight: 900; font-size: 1.85rem;
  letter-spacing: -0.01em; text-transform: uppercase;
}
.bks-mast__eyebrow {
  font-family: 'DM Mono', monospace; font-size: 9px;
  letter-spacing: 0.25em; text-transform: uppercase; opacity: 0.55; margin-bottom: 3px;
}
.bks-mast__meta {
  font-family: 'DM Mono', monospace; font-size: 9.5px;
  letter-spacing: 0.1em; text-align: right; line-height: 1.7; opacity: 0.65;
}
.bks-body {
  font-family: 'DM Sans', sans-serif;
  background: var(--paper); padding: 18px 28px 48px; color: var(--ink);
}
.bks-kpi-strip {
  display: grid; grid-template-columns: repeat(6, 1fr);
  gap: 0; border: 2px solid var(--ink); margin-bottom: 22px;
}
.bks-kpi { padding: 10px 14px; border-right: 1.5px solid var(--ink); text-align: center; }
.bks-kpi:last-child { border-right: none; }
.bks-kpi__val {
  font-family: 'Playfair Display', Georgia, serif;
  font-weight: 900; font-size: 1.75rem; line-height: 1; color: var(--ink);
}
.bks-kpi__val.hi { color: var(--on); }
.bks-kpi__lbl {
  font-family: 'DM Mono', monospace; font-size: 9px;
  letter-spacing: 0.16em; text-transform: uppercase; color: var(--muted); margin-top: 3px;
}
.bks-sec {
  border-top: 3px solid var(--ink); padding-top: 5px; margin: 20px 0 10px;
  display: flex; justify-content: space-between; align-items: baseline;
}
.bks-sec__title {
  font-family: 'DM Mono', monospace; font-size: 10px; font-weight: 500;
  letter-spacing: 0.28em; text-transform: uppercase; color: var(--ink);
}
.bks-sec__note {
  font-family: 'DM Mono', monospace; font-size: 9px; letter-spacing: 0.1em; color: var(--muted);
}
.bks-overall {
  background: var(--paper2); border: 1.5px solid var(--ink);
  padding: 9px 14px; margin-bottom: 20px;
  display: flex; align-items: center; gap: 14px;
}
.bks-overall__track { flex: 1; height: 13px; background: #cfc0a0; border: 1px solid var(--ink); }
.bks-overall__fill  { height: 100%; background: var(--ink); }
.bks-overall__label {
  font-family: 'DM Mono', monospace; font-size: 11px; font-weight: 500;
  letter-spacing: 0.1em; white-space: nowrap; color: var(--ink);
}
.bks-area-label {
  font-family: 'DM Mono', monospace; font-size: 9px; letter-spacing: 0.22em;
  text-transform: uppercase; color: var(--muted); margin: 12px 0 5px;
  border-left: 3px solid var(--ink); padding-left: 8px;
}
.bks-row {
  display: grid; grid-template-columns: 200px 1fr 50px 82px;
  align-items: center; gap: 8px; padding: 4px 0;
  border-bottom: 1px solid rgba(26,14,5,0.11);
}
.bks-row:hover { background: rgba(26,14,5,0.04); }
.bks-row__name {
  font-family: 'DM Sans', sans-serif; font-size: 12px; font-weight: 500; color: var(--ink);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.bks-row__track {
  height: 17px; background: rgba(26,14,5,0.09);
  border: 1px solid rgba(26,14,5,0.14); position: relative; overflow: hidden;
}
.bks-row__fill { height: 100%; position: absolute; left: 0; top: 0; opacity: 0.85; }
.bks-row__pct {
  font-family: 'DM Mono', monospace; font-size: 11px; font-weight: 500;
  text-align: right; color: var(--ink);
}
.bks-row__stato {
  font-family: 'DM Mono', monospace; font-size: 9px; letter-spacing: 0.08em;
  text-transform: uppercase; padding: 2px 6px; border: 1px solid currentColor; text-align: center;
}
.bks-row__stato.done    { color: var(--on);   border-color: var(--on); }
.bks-row__stato.attivo  { color: #1a4a8a;     border-color: #1a4a8a; }
.bks-row__stato.parziale{ color: var(--warn); border-color: var(--warn); }
.bks-row__stato.pending { color: var(--off);  border-color: var(--off); }
.bks-grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 4px; }
.bks-grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 16px; margin-top: 4px; }
@media (max-width: 900px) {
  .bks-grid-2, .bks-grid-3 { grid-template-columns: 1fr; }
  .bks-kpi-strip { grid-template-columns: repeat(3,1fr); }
}
.bks-panel { border: 1.5px solid var(--ink); background: var(--paper2); }
.bks-panel__head {
  background: var(--ink); color: #f0e6cc; padding: 5px 12px;
  font-family: 'DM Mono', monospace; font-size: 9px; letter-spacing: 0.22em;
  text-transform: uppercase; display: flex; justify-content: space-between; align-items: center;
}
.bks-panel__head-badge { font-size: 8px; letter-spacing: 0.1em; background: rgba(255,255,255,0.15); padding: 1px 6px; }
.bks-panel__body { padding: 10px 12px; }
.bks-svc-row {
  display: flex; align-items: center; gap: 9px; padding: 4px 0;
  border-bottom: 1px solid rgba(26,14,5,0.1);
  font-family: 'DM Sans', sans-serif; font-size: 12px; color: var(--ink);
}
.bks-svc-row:last-child { border-bottom: none; }
.bks-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.bks-dot.on  { background: var(--on); }
.bks-dot.off { background: var(--off); }
.bks-dot.dep { background: #1a4a8a; }
.bks-svc-name { flex: 1; }
.bks-svc-badge {
  font-family: 'DM Mono', monospace; font-size: 9px;
  padding: 1px 6px; border: 1px solid currentColor; letter-spacing: 0.08em;
}
.bks-svc-badge.on  { color: var(--on); }
.bks-svc-badge.off { color: var(--off); }
.bks-svc-badge.dep { color: #1a4a8a; }
.bks-vault-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 10px; }
.bks-vault-group { border: 1px solid rgba(26,14,5,0.2); }
.bks-vault-group__head {
  background: rgba(26,14,5,0.08); padding: 4px 10px;
  font-family: 'DM Mono', monospace; font-size: 9px;
  letter-spacing: 0.18em; text-transform: uppercase; color: var(--ink);
  border-bottom: 1px solid rgba(26,14,5,0.15);
}
.bks-vault-key {
  display: flex; align-items: center; gap: 7px; padding: 3px 10px;
  border-bottom: 1px solid rgba(26,14,5,0.07);
  font-family: 'DM Mono', monospace; font-size: 9.5px; color: var(--ink);
}
.bks-vault-key:last-child { border-bottom: none; }
.bks-vault-dot { width: 5px; height: 5px; border-radius: 50%; flex-shrink: 0; }
.bks-vault-dot.y { background: var(--on); }
.bks-vault-dot.n { background: var(--off); }
.bks-vault-name { flex: 1; opacity: 0.75; }
.bks-vault-status { font-size: 8px; opacity: 0.55; }
.bks-g-row {
  display: grid; grid-template-columns: 140px 1fr 90px;
  align-items: center; gap: 10px; padding: 4px 0;
  border-bottom: 1px solid rgba(26,14,5,0.1);
  font-family: 'DM Sans', sans-serif; font-size: 12px; color: var(--ink);
}
.bks-g-row:last-child { border-bottom: none; }
.bks-g-service { font-weight: 500; }
.bks-g-id { font-family: 'DM Mono', monospace; font-size: 10px; opacity: 0.65; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.bks-g-badge { font-family: 'DM Mono', monospace; font-size: 9px; padding: 1px 7px; border: 1px solid currentColor; text-align: center; letter-spacing: 0.06em; }
.bks-g-badge.ok   { color: var(--on);   border-color: var(--on); }
.bks-g-badge.warn { color: var(--warn); border-color: var(--warn); }
.bks-g-badge.off  { color: var(--off);  border-color: var(--off); }
.bks-link-row {
  display: flex; align-items: center; justify-content: space-between;
  padding: 4px 0; border-bottom: 1px solid rgba(26,14,5,0.1);
  font-family: 'DM Mono', monospace; font-size: 11px; color: var(--ink);
}
.bks-link-row:last-child { border-bottom: none; }
.bks-link-row a { color: #1a4a8a; text-decoration: none; font-size: 10px; }
.bks-link-row a:hover { text-decoration: underline; }
.bks-link-lbl { font-size: 9px; opacity: 0.55; letter-spacing: 0.1em; text-transform: uppercase; }
.bks-caption {
  font-family: 'DM Mono', monospace; font-size: 9px; letter-spacing: 0.15em;
  text-transform: uppercase; color: var(--muted); text-align: right; margin-bottom: 3px;
}
.bks-tag-new {
  display: inline-block; font-family: 'DM Mono', monospace; font-size: 8px;
  letter-spacing: 0.1em; text-transform: uppercase; padding: 1px 5px;
  background: var(--on); color: #fff; border-radius: 2px; margin-left: 5px; vertical-align: middle;
}
</style>
""", unsafe_allow_html=True)

# ─── compute ─────────────────────────────────────────────────────────────────

overall   = round(sum(c[2] for c in COMPONENTI) / len(COMPONENTI))
svc_stat  = _svc_status()
env       = _env()

# ─── MASTHEAD ─────────────────────────────────────────────────────────────────

st.markdown(f"""
<div class="bks-mast">
  <div>
    <div class="bks-mast__eyebrow">BKS Studio · bakabo.club</div>
    <div class="bks-mast__title">Sistema Monitor</div>
  </div>
  <div class="bks-mast__meta">
    DRONE VIEW · SONY α9III<br>
    {TODAY}<br>
    :8501 · Roberto Picchioni
  </div>
</div>
<div class="bks-body">
<div class="bks-caption">Vista aerea — griglia sistema operativo BKS Studio 2026 · v3</div>
""", unsafe_allow_html=True)

# ─── KPI STRIP ───────────────────────────────────────────────────────────────

online_count = sum(1 for v in svc_stat.values() if v)
done_count   = sum(1 for c in COMPONENTI if c[3] == "done")
st.markdown(f"""
<div class="bks-kpi-strip">
  <div class="bks-kpi"><div class="bks-kpi__val">202</div><div class="bks-kpi__lbl">Prodotti</div></div>
  <div class="bks-kpi"><div class="bks-kpi__val">8</div><div class="bks-kpi__lbl">Collezioni</div></div>
  <div class="bks-kpi"><div class="bks-kpi__val">V.22</div><div class="bks-kpi__lbl">Tema TM04</div></div>
  <div class="bks-kpi"><div class="bks-kpi__val">v16</div><div class="bks-kpi__lbl">AI Worker</div></div>
  <div class="bks-kpi"><div class="bks-kpi__val">{online_count}</div><div class="bks-kpi__lbl">Servizi live</div></div>
  <div class="bks-kpi"><div class="bks-kpi__val hi">{overall}%</div><div class="bks-kpi__lbl">Sistema</div></div>
</div>
""", unsafe_allow_html=True)

# ─── GANTT ROADMAP ───────────────────────────────────────────────────────────

st.markdown(f"""
<div class="bks-sec">
  <span class="bks-sec__title">Roadmap — Avanzamento lavori</span>
  <span class="bks-sec__note">{len(COMPONENTI)} componenti · {TODAY}</span>
</div>
<div class="bks-overall">
  <span class="bks-overall__label">SISTEMA &nbsp; {overall}%</span>
  <div class="bks-overall__track"><div class="bks-overall__fill" style="width:{overall}%"></div></div>
  <span class="bks-overall__label">{done_count} DONE · {sum(1 for c in COMPONENTI if c[3]=='pending')} DA FARE</span>
</div>
""", unsafe_allow_html=True)

STATO_MAP = {"done": "✓ DONE", "attivo": "● LIVE", "parziale": "◑ PART.", "pending": "○ TODO"}
for area in AREE_ORDER:
    items = [c for c in COMPONENTI if c[1] == area]
    if not items:
        continue
    st.markdown(f'<div class="bks-area-label">{area}</div>', unsafe_allow_html=True)
    for nome, _, pct, stato, col, note in items:
        st.markdown(f"""
<div class="bks-row" title="{note}">
  <div class="bks-row__name">{nome}</div>
  <div class="bks-row__track"><div class="bks-row__fill" style="width:{pct}%;background:{col}"></div></div>
  <div class="bks-row__pct">{pct}%</div>
  <div class="bks-row__stato {stato}">{STATO_MAP[stato]}</div>
</div>""", unsafe_allow_html=True)

# ─── SERVER & INFRASTRUTTURA ─────────────────────────────────────────────────

st.markdown("""
<div class="bks-sec" style="margin-top:24px">
  <span class="bks-sec__title">Server &amp; Infrastruttura</span>
  <span class="bks-sec__note">ping live — aggiornato ogni 25s</span>
</div>
<div class="bks-grid-2">
""", unsafe_allow_html=True)

# locale
loc_html = ""
for nome, host, porta in SERVIZI_LOCALI:
    up  = svc_stat.get(f"{nome}:{porta}", False)
    cls = "on" if up else "off"
    badge_txt = "ONLINE" if up else "OFFLINE"
    extra = ""
    if nome == "BKS Studio" and up:
        extra = f' · <a href="http://localhost:{porta}" target="_blank">apri ↗</a>'
    loc_html += f"""
<div class="bks-svc-row">
  <div class="bks-dot {cls}"></div>
  <span class="bks-svc-name">{nome} <small style="opacity:.5">:{porta}</small>{extra}</span>
  <span class="bks-svc-badge {cls}">{badge_txt}</span>
</div>"""

# tablet shortcut
loc_html += """
<div class="bks-svc-row" style="margin-top:8px;border-bottom:none">
  <div class="bks-dot dep"></div>
  <span class="bks-svc-name" style="font-size:11px;opacity:.7">Tablet accesso</span>
  <a href="http://192.168.1.103:8501" target="_blank" style="font-family:'DM Mono',monospace;font-size:10px;color:#1a4a8a">192.168.1.103:8501 ↗</a>
</div>"""

# cloud
cloud_html = ""
for nome, host, porta in SERVIZI_CLOUD:
    up  = svc_stat.get(f"{nome}:{porta}", False)
    cls = "on" if up else "off"
    badge_txt = "ONLINE" if up else "OFFLINE"
    cloud_html += f"""
<div class="bks-svc-row">
  <div class="bks-dot {cls}"></div>
  <span class="bks-svc-name">{nome} <small style="opacity:.5">{host}:{porta}</small></span>
  <span class="bks-svc-badge {cls}">{badge_txt}</span>
</div>"""

# CF workers (static — no TCP ping)
for nome, url in CF_WORKERS:
    cloud_html += f"""
<div class="bks-svc-row">
  <div class="bks-dot dep"></div>
  <span class="bks-svc-name">{nome} <small style="opacity:.5">{url}</small></span>
  <span class="bks-svc-badge dep">DEPLOYED</span>
</div>"""

st.markdown(f"""
<div class="bks-panel">
  <div class="bks-panel__head">PC Locale — 192.168.1.103 <span class="bks-panel__head-badge">:8501 · :8010</span></div>
  <div class="bks-panel__body">{loc_html}</div>
</div>
<div class="bks-panel">
  <div class="bks-panel__head">Cloud — Hetzner Helsinki + Cloudflare <span class="bks-panel__head-badge">v16</span></div>
  <div class="bks-panel__body">{cloud_html}</div>
</div>
</div>
""", unsafe_allow_html=True)

# ─── GOOGLE & ANALYTICS ──────────────────────────────────────────────────────

gtm_id     = _pub("GTM_TARGET")     or "GTM-PF5Z85KS"
ga4_id     = _pub("GA4_PROPERTY_ID")
gmc_id     = _pub("GOOGLE_MERCHANT_ID") or "5295165689"
yt_channel = _pub("YOUTUBE_CHANNEL_ID")

GOOGLE_ROWS = [
    ("Google Tag Manager", gtm_id,       "ok",   "Attivo — iniettato in theme.liquid"),
    ("GA4 Analytics",      ga4_id,       "ok",   "Configurato · raccolta dati attiva"),
    ("Google Merchant",    gmc_id,       "warn", "35.1K prodotti · limited_quantity issue · Wixpa re-sub 20/06"),
    ("Search Console",     "bakabo.club","warn", "TXT record da confermare in Cloudflare DNS"),
    ("YouTube",            yt_channel,   "warn", "Chiavi configurate · canale da riconnettere"),
    ("Gmail / IMAP",       _pub("OFFICIAL_INBOX_EMAIL") or "bakabofirm@gmail.com", "ok",
     f"IMAP host: {_pub('OFFICIAL_INBOX_IMAP_HOST')}"),
    ("SMTP Posta",         _pub("SMTP_USER") or "—",
     "ok" if _has("SMTP_HOST") else "off",
     f"Host: {_pub('SMTP_HOST')} · porta {_pub('SMTP_PORT')}"),
]

g_html = "".join(f"""
<div class="bks-g-row" title="{note}">
  <div class="bks-g-service">{svc}</div>
  <div class="bks-g-id">{id_val}</div>
  <div class="bks-g-badge {badge}">{"● OK" if badge=="ok" else ("⚠ WARN" if badge=="warn" else "✗ OFF")}</div>
</div>""" for svc, id_val, badge, note in GOOGLE_ROWS)

st.markdown(f"""
<div class="bks-sec" style="margin-top:24px">
  <span class="bks-sec__title">Google, Analytics &amp; Posta</span>
  <span class="bks-sec__note">bakabofirm@gmail.com</span>
</div>
<div class="bks-panel">
  <div class="bks-panel__head">Google Workspace &amp; Analytics <span class="bks-panel__head-badge">7 SERVIZI</span></div>
  <div class="bks-panel__body">{g_html}</div>
</div>
""", unsafe_allow_html=True)

# ─── CASSAFORTE CREDENZIALI ───────────────────────────────────────────────────

st.markdown("""
<div class="bks-sec" style="margin-top:24px">
  <span class="bks-sec__title">Cassaforte Credenziali</span>
  <span class="bks-sec__note">.env — stato chiavi API (valori non esposti)</span>
</div>
<div class="bks-vault-grid">
""", unsafe_allow_html=True)

total_keys = 0; configured_keys = 0
for group_name, keys in VAULT_GROUPS:
    rows_html = ""
    for k in keys:
        has = _has(k)
        total_keys += 1
        if has: configured_keys += 1
        dot_cls = "y" if has else "n"
        short_k = k.replace("_", " ").lower()
        rows_html += f"""
<div class="bks-vault-key">
  <div class="bks-vault-dot {dot_cls}"></div>
  <span class="bks-vault-name">{short_k}</span>
  <span class="bks-vault-status">{"✓" if has else "✗"}</span>
</div>"""
    configured_in_group = sum(1 for k in keys if _has(k))
    st.markdown(f"""
<div class="bks-vault-group">
  <div class="bks-vault-group__head">{group_name} &nbsp;<span style="opacity:.5">{configured_in_group}/{len(keys)}</span></div>
  {rows_html}
</div>""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

vault_pct = round(configured_keys / total_keys * 100) if total_keys else 0
st.markdown(f"""
<div class="bks-overall" style="margin-top:10px">
  <span class="bks-overall__label">CHIAVI CONFIGURATE &nbsp; {configured_keys}/{total_keys}</span>
  <div class="bks-overall__track"><div class="bks-overall__fill" style="width:{vault_pct}%"></div></div>
  <span class="bks-overall__label">{vault_pct}%</span>
</div>
""", unsafe_allow_html=True)

# ─── LINK RAPIDI ─────────────────────────────────────────────────────────────

LINKS = [
    ("Store live",      "https://bakabo.club"),
    ("Shopify Admin",   "https://admin.shopify.com/store/11628e-2"),
    ("Theme Editor",    "https://11628e-2.myshopify.com/admin/themes/202392961362/editor"),
    ("Printify",        "https://printify.com/app"),
    ("GMC",             "https://merchants.google.com"),
    ("AI Worker v16",   "https://bks-agent.bakabo.workers.dev/chat"),
    ("BKS Verse",       "https://verse.bakabo.club"),
    ("Member Area",     "https://bakabo.club/pages/bks-members"),
    ("Hetzner HEL",     "http://95.217.232.186:8001"),
    ("Tablet :8501",    "http://192.168.1.103:8501"),
    ("Gmail",           "https://mail.google.com"),
    ("Cloudflare",      "https://dash.cloudflare.com"),
    ("AI Assistant",    "https://bakabo.club/pages/bks-ai-assistant"),
    ("Pinterest",       "https://business.pinterest.com"),
]

links_html = "".join(f"""
<div class="bks-link-row">
  <span class="bks-link-lbl">{lbl}</span>
  <a href="{url}" target="_blank">{url.replace('https://','').replace('http://','')[:44]}</a>
</div>""" for lbl, url in LINKS)

st.markdown(f"""
<div class="bks-sec" style="margin-top:24px">
  <span class="bks-sec__title">Link Rapidi</span>
  <span class="bks-sec__note">{len(LINKS)} shortcut</span>
</div>
<div class="bks-panel">
  <div class="bks-panel__head">Accesso rapido — tutti i servizi</div>
  <div class="bks-panel__body">
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:0 20px">
      {links_html}
    </div>
  </div>
</div>
</div><!-- /bks-body -->
""", unsafe_allow_html=True)
