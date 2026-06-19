from __future__ import annotations

import json
import socket
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import streamlit as st

from ecommerce_automation.member_tryon import (
    DATABASE_ROOT,
    INCOMING_DIR,
    LOGS_DIR,
    PRESETS_DIR,
    PRESETS_FILE,
    PREVIEWS_DIR,
    ensure_workspace,
    load_presets,
    pending_count,
)
from streamlit_master import inject_bks_theme, port_open


TRYON_PORT = 8010
TRYON_URL = "http://127.0.0.1:8010"


def _preset_card(preset: dict, col: Any) -> None:
    img_path = PRESETS_DIR / preset.get("preview_file", "")
    with col:
        st.markdown(
            f"""<div style="border-top:2px solid {preset.get('accent','#2f6f6b')};
            background:rgba(250,250,247,0.03);padding:10px 12px;margin-bottom:8px">
            <span style="font-family:'DM Mono',monospace;font-size:0.60rem;
            letter-spacing:0.12em;text-transform:uppercase;
            color:{preset.get('accent','#2f6f6b')}">{preset.get('id','')}</span><br>
            <span style="color:#fafaf7;font-size:0.88rem;font-weight:300">
            {preset.get('label','')}</span>
            </div>""",
            unsafe_allow_html=True,
        )
        if img_path.exists():
            st.image(str(img_path), use_container_width=True)
        st.caption(preset.get("role", ""))
        best = preset.get("best_for", [])
        if best:
            st.markdown(
                "<span style='font-family:DM Mono,monospace;font-size:0.58rem;"
                "letter-spacing:0.08em;color:rgba(250,250,247,0.50)'>"
                + " · ".join(best[:4])
                + "</span>",
                unsafe_allow_html=True,
            )


def _read_logs(max_entries: int = 20) -> list[dict]:
    entries: list[dict] = []
    if not LOGS_DIR.exists():
        return entries
    for log_file in sorted(LOGS_DIR.glob("requests_*.jsonl"), reverse=True)[:3]:
        for line in reversed(log_file.read_text(encoding="utf-8").splitlines()):
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                pass
            if len(entries) >= max_entries:
                return entries
    return entries


def _pending_files() -> list[dict]:
    if not INCOMING_DIR.exists():
        return []
    rows = []
    for f in sorted(INCOMING_DIR.iterdir(), reverse=True):
        if not f.is_file():
            continue
        stat = f.stat()
        rows.append({
            "file": f.name,
            "size_kb": round(stat.st_size / 1024, 1),
            "received": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
        })
    return rows


# ── page ──────────────────────────────────────────────────────────────────────

st.set_page_config(page_title="BKS — Camerino", page_icon="◎", layout="wide")
inject_bks_theme()

from typing import Any  # noqa: E402 — after set_page_config

ensure_workspace()

st.title("Try-On ◎ BKS Members")
st.caption("Gestione coda richieste, preset sfondo, engine status. Dati reali in I:\\BKS database\\members_tryon\\")

engine_online = port_open(TRYON_PORT)
pending = pending_count()
presets_data = load_presets()

# ── KPIs ──
cols = st.columns(5)
cols[0].metric("Engine :8010", "◎ ONLINE" if engine_online else "✕ OFFLINE")
cols[1].metric("Richieste in coda", pending)
cols[2].metric("Preset sfondo", presets_data.get("presets_count", len(presets_data.get("presets", []))))
cols[3].metric("Default preset", presets_data.get("default", "—"))
cols[4].metric("Modalità", "queue v1")

if not engine_online:
    st.warning("Tryon Engine offline. Avvia [2] dal Master Control o usa 05_START_TRYON_ENGINE.bat")
    if st.button("Apri pagina engine", use_container_width=True):
        st.link_button("→ Tryon Engine Health", f"{TRYON_URL}/health")

st.divider()

# ── tabs ──
tabs = st.tabs(["Coda richieste", "Preset sfondo", "Log richieste", "Workspace"])

# ── tab 1: coda ──
with tabs[0]:
    st.subheader(f"Incoming — {pending} file in attesa")
    if pending == 0:
        st.info("Nessuna richiesta in coda.")
    else:
        rows = _pending_files()
        st.dataframe(
            pd.DataFrame(rows),
            width="stretch",
            hide_index=True,
            column_config={
                "size_kb": st.column_config.NumberColumn("KB", format="%.1f"),
            },
        )
        st.caption(
            "v1 — elaborazione manuale: apri la foto, genera con gpt-image-1 + preset scelto, "
            "salva in previews/, notifica il membro via email. "
            "Render automatico non ancora attivo per design."
        )
        st.markdown(f"**Cartella:** `{INCOMING_DIR}`")

# ── tab 2: preset ──
with tabs[1]:
    st.subheader("Preset sfondo Camerino BKS")
    if not PRESETS_FILE.exists():
        st.error(f"File preset non trovato: {PRESETS_FILE}")
    else:
        raw = json.loads(PRESETS_FILE.read_text(encoding="utf-8"))
        presets_list = raw.get("presets", [])
        recommendation = raw.get("recommendation", {})

        rec_cols = st.columns(4)
        labels = [("default", "Default"), ("most_bks_identity", "BKS identity"), ("social_campaign", "Social"), ("high_impact_optional", "High impact")]
        for col, (key, label) in zip(rec_cols, labels):
            col.metric(label, recommendation.get(key, "—"))

        st.divider()
        grid = st.columns(len(presets_list))
        for preset, col in zip(presets_list, grid):
            _preset_card(preset, col)

# ── tab 3: log ──
with tabs[2]:
    st.subheader("Log richieste recenti")
    entries = _read_logs(30)
    if not entries:
        st.info("Nessun log disponibile.")
    else:
        display = [
            {
                "request_id": e.get("request_id", ""),
                "received_at": e.get("received_at", ""),
                "status": e.get("status", ""),
                "item": e.get("item_title", ""),
                "photo": e.get("incoming_photo", ""),
                "cart_items": e.get("cart_item_count", 0),
            }
            for e in entries
        ]
        st.dataframe(pd.DataFrame(display), width="stretch", hide_index=True)
        st.caption("Email cliente non loggata (solo hash SHA-256 a 16 char). Foto cancellate dopo elaborazione.")

# ── tab 4: workspace ──
with tabs[3]:
    st.subheader("Workspace — I:\\BKS database\\members_tryon\\")
    dirs = {
        "incoming": INCOMING_DIR,
        "previews": PREVIEWS_DIR,
        "logs": LOGS_DIR,
        "presets": PRESETS_DIR,
    }
    for name, path in dirs.items():
        exists = path.exists()
        files = list(path.iterdir()) if exists else []
        file_count = sum(1 for f in files if f.is_file())
        st.markdown(
            f"""<div style="border-left:2px solid {'#489808' if exists else '#c82020'};
            padding:6px 12px;margin:4px 0;font-family:'DM Mono',monospace;font-size:0.72rem;
            color:#fafaf7">
            <b>{name}/</b>&nbsp;&nbsp;
            <span style="color:rgba(250,250,247,0.50)">{file_count} file — {path}</span>
            </div>""",
            unsafe_allow_html=True,
        )

    st.divider()
    st.caption(
        "Presets JSON e PNG sono versionati nella directory presets/. "
        "Foto incoming e previews non entrano mai nel git repository (policy GDPR)."
    )
    st.link_button("→ Apri Tryon Engine", TRYON_URL, disabled=not engine_online)
