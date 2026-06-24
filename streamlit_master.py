#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BakAbo/BKS master monitoring panel."""

from __future__ import annotations

import csv
import os
import socket
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from ecommerce_automation.agent_routine import payload as agent_routine_payload
from ecommerce_automation.catalog_db import payload as catalog_db_payload
from ecommerce_automation.catalog_live_sync import payload as catalog_live_sync_payload
from ecommerce_automation.daily_web_update import payload as daily_web_update_payload
from ecommerce_automation.config import settings as master_settings
from ecommerce_automation.google_merchant_monitor import payload as google_merchant_payload
from ecommerce_automation.growth_crm import payload as growth_crm_payload
from ecommerce_automation.legal_guardrails import payload as legal_guardrails_payload
from ecommerce_automation.market_sense import payload as market_sense_payload
from ecommerce_automation.master_actions import payload as master_actions_payload
from ecommerce_automation.member_tryon import payload as member_tryon_payload
from ecommerce_automation.master_agent import reply as agent_reply
from ecommerce_automation.network_monitor import payload as network_monitor_payload
from ecommerce_automation.official_inbox import payload as official_inbox_payload
from ecommerce_automation.photo_studio import payload as photo_studio_payload
from ecommerce_automation.realtime_control import payload as realtime_payload
from ecommerce_automation.sales_channels import payload as sales_channels_payload
from ecommerce_automation.social_campaigns import payload as social_campaigns_payload
from ecommerce_automation.theme_optimizer import payload as theme_optimizer_payload
from ecommerce_automation.weekly_goals import payload as weekly_goals_payload

from bks_assets import (
    ACTIVE_ASSETS_PATH,
    active_catalog_csv,
    active_image_factory_dir,
    active_theme_zip,
    discover_catalog_csvs,
    discover_theme_zips,
    latest_catalog_csv,
    latest_theme_zip,
    relative_to_base,
    save_active_assets,
)


BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
OUTPUT_DIR = BASE_DIR / "output"
LIVE_AUDIT_CSV = OUTPUT_DIR / "live_site_audit" / "live_pages.csv"
LIVE_AUDIT_MD = OUTPUT_DIR / "live_site_audit" / "live_site_audit.md"


@dataclass(frozen=True)
class Service:
    phase: str
    name: str
    port: int
    url: str
    launcher: str
    role: str


SERVICES = (
    Service("01", "BKS Studio (Streamlit)", 8501, "http://localhost:8501", "01_START_CATALOG_ENGINE.bat", "App principale — Catalogo, SEO, Social, Image Factory"),
    Service("02", "Tryon AI Engine", 8010, "http://127.0.0.1:8010", "05_START_TRYON_ENGINE.bat", "Camerino AI — virtual try-on, member area"),
    Service("03", "Master Panel", 8600, "http://127.0.0.1:8600", "", "Hub centrale — agente, progressione, azioni"),
)

PROJECT_PHASES = (
    {"fase": "01", "nome": "Asset attivi", "obiettivo": "Scegli tema e CSV aggiornati", "comando": "Master > File", "output": "output/bks_active_assets.json", "stato": "pronto", "guida": "README.md"},
    {"fase": "02", "nome": "Catalogo", "obiettivo": "SEO, tag canonici, dati prodotto puliti", "comando": "01_START_CATALOG_ENGINE.bat", "output": "output/products_export_updated.csv", "stato": "pronto", "guida": "01_CATALOGO/README.md"},
    {"fase": "03", "nome": "Collezioni", "obiettivo": "8 BKS collections + product type pages, regole e template", "comando": "python tools/create_collections.py", "output": "output/bks_collection_plan_v20.csv", "stato": "operativa", "guida": "02_COLLEZIONI/README.md"},
    {"fase": "04", "nome": "Metafields", "obiettivo": "bks.collection/design/drop/series aggiornati", "comando": "python tools/create_metafields.py", "output": "output/populate_metafields_log.csv", "stato": "operativa", "guida": "03_METAFIELDS_METAOBJECTS/README.md"},
    {"fase": "05", "nome": "Tema Shopify TM04", "obiettivo": "TM04 live v7 — 78 sezioni/asset, tutte le pagine, product.json default, policy template, contact", "comando": "python scripts/deploy_theme_section.py", "output": "04_TEMA_SHOPIFY/", "stato": "pronto", "guida": "04_TEMA_SHOPIFY/README.md"},
    {"fase": "06", "nome": "Testi e policy", "obiettivo": "About ✓ · FAQ ✓ · Contact ✓ · Policy template ✓ · footer links ✓", "comando": "python tools/export_site_texts.py", "output": "output/site_texts_v1", "stato": "pronto", "guida": "05_TESTI_POLICY/README.md"},
    {"fase": "07", "nome": "Image Factory", "obiettivo": "Mockup, shooting AI, QA, export immagini", "comando": "BAKABO_IMAGE_FACTORY_v1.1", "output": "BAKABO_IMAGE_FACTORY_v1.1/output", "stato": "integrata", "guida": "BAKABO_IMAGE_FACTORY_v1.1"},
    {"fase": "08", "nome": "Analytics", "obiettivo": "GA4/GTM, Merchant, efficienza marketing", "comando": "python tools/audit_live_site.py", "output": "output/live_site_audit", "stato": "operativa", "guida": "06_ANALYTICS_MERCHANT/README.md"},
    {"fase": "09", "nome": "Social PM", "obiettivo": "FB · IG · Pinterest · Amazon Merch · Telegram · TikTok — tutto GA4", "comando": "Social Hub (pagina 03)", "output": "output/social/", "stato": "operativa", "guida": "pages/03_Social.py"},
    {"fase": "10", "nome": "Deploy & Member Area", "obiettivo": "Import CSV, Metal Tier live, camerino AI, push tema", "comando": "python scripts/deploy_theme_section.py", "output": "tema + catalogo live", "stato": "da eseguire", "guida": "scripts/deploy_theme_section.py"},
)

STATUS_PROGRESS = {
    "pronto": 100,
    "integrata": 100,
    "attivo": 90,
    "operativa": 78,
    "monitoraggio": 68,
    "verifica": 55,
    "da eseguire": 18,
}


def load_local_env(path: Path = ENV_PATH) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def resolve_asset_path(path_value: str | Path) -> Path:
    path = Path(path_value)
    return path if path.is_absolute() else BASE_DIR / path


def file_info(path_value: str | Path) -> dict[str, Any]:
    path = resolve_asset_path(path_value)
    display = relative_to_base(path)
    if not path.exists():
        return {"file": display, "exists": False, "size_mb": "", "updated": ""}
    stat = path.stat()
    return {
        "file": display,
        "exists": True,
        "size_mb": round(stat.st_size / 1024 / 1024, 2),
        "updated": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
    }


def phase_records() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for phase in PROJECT_PHASES:
        status = str(phase["stato"])
        rows.append(
            {
                "phase_id": phase["fase"],
                "name": phase["nome"],
                "status": status,
                "progress": STATUS_PROGRESS.get(status, 40),
                "objective": phase["obiettivo"],
                "command": phase["comando"],
                "output": phase["output"],
            }
        )
    return rows


def services_snapshot() -> dict[str, dict[str, Any]]:
    return {
        service.name.lower().replace(" ", "_"): {
            "configured": port_open(service.port),
            "status": "online" if port_open(service.port) else "offline",
            "port": service.port,
            "url": service.url,
            "role": service.role,
        }
        for service in SERVICES
    }


def safe_theme_payload() -> dict[str, Any]:
    try:
        return theme_optimizer_payload(master_settings)
    except Exception as exc:
        return {"summary": {"status": "error", "goal": str(exc)}, "checks": [], "files": {}}


def light_theme_snapshot() -> dict[str, Any]:
    output_zip = active_theme_zip()
    zip_exists = output_zip is not None and Path(output_zip).exists()
    return {
        "summary": {
            "status": "ready" if zip_exists else "missing",
            "goal": "TM04_live_bks_sections_member_area_camerino",
            "output_zip": relative_to_base(output_zip) if output_zip else None,
        }
    }


def safe_sales_channels_payload() -> dict[str, Any]:
    try:
        return sales_channels_payload(master_settings)
    except Exception as exc:
        return {"summary": {"active": 0, "partial": 0, "planned": 0, "missing": 0, "error": str(exc)}, "rows": []}


def safe_catalog_payload() -> dict[str, Any]:
    try:
        return catalog_db_payload(master_settings)
    except Exception as exc:
        return {"summary": {"ok": False, "rows": 0, "products": 0, "handles": 0, "error": str(exc)}, "products": []}


def safe_social_campaigns_payload(snapshot: dict[str, Any]) -> dict[str, Any]:
    try:
        return social_campaigns_payload(master_settings, snapshot)
    except Exception as exc:
        return {"summary": {"channels": 0, "ready": 0, "partial": 0, "planned": 0, "error": str(exc)}, "channels": [], "languages": []}


def safe_trust_payload() -> dict[str, Any]:
    try:
        return google_merchant_payload(master_settings)
    except Exception as exc:
        return {"summary": {"status": "error", "needs_fix": 0, "blockers": 0, "error": str(exc)}, "merchant": {}}


def safe_network_payload() -> dict[str, Any]:
    try:
        return network_monitor_payload(master_settings, live=False)
    except Exception as exc:
        return {"summary": {"status": "error", "needs_fix": 0, "error": str(exc)}}


def safe_official_inbox_payload() -> dict[str, Any]:
    try:
        return official_inbox_payload(master_settings)
    except Exception as exc:
        return {"summary": {"status": "missing_email", "configured": 0, "needs_attention": 0, "error": str(exc)}}


def safe_photo_studio_payload(snapshot: dict[str, Any]) -> dict[str, Any]:
    try:
        return photo_studio_payload(master_settings, snapshot)
    except Exception as exc:
        return {"summary": {"ready": 0, "p0": 0, "error": str(exc)}}


def safe_growth_crm_payload(snapshot: dict[str, Any]) -> dict[str, Any]:
    try:
        return growth_crm_payload(master_settings, snapshot)
    except Exception as exc:
        return {"summary": {"attention": 0, "ready": 0, "error": str(exc)}}


def safe_legal_payload(snapshot: dict[str, Any]) -> dict[str, Any]:
    try:
        return legal_guardrails_payload(master_settings, snapshot)
    except Exception as exc:
        return {"summary": {"customer_needs": 0, "status": "error", "error": str(exc)}}


def safe_market_sense_payload(snapshot: dict[str, Any]) -> dict[str, Any]:
    try:
        return market_sense_payload(master_settings, snapshot)
    except Exception as exc:
        return {"summary": {"market_sense": 0, "signals": 0, "recommendations": 0, "error": str(exc)}}


def safe_weekly_goals_payload(snapshot: dict[str, Any]) -> dict[str, Any]:
    try:
        return weekly_goals_payload(master_settings, snapshot)
    except Exception as exc:
        return {"summary": {"week": "", "pass": 0, "total": 0, "error": str(exc)}, "rows": []}


def safe_member_tryon_payload() -> dict[str, Any]:
    try:
        return member_tryon_payload(master_settings)
    except Exception as exc:
        return {"summary": {"status": "error", "pending_requests": 0, "presets_count": 0, "error": str(exc)}}


def safe_catalog_live_sync_payload() -> dict[str, Any]:
    try:
        return catalog_live_sync_payload(master_settings, services={}, references=None, live=False)
    except Exception as exc:
        return {"summary": {"status": "error", "live": False, "error": str(exc)}}


def safe_daily_web_update_payload(snapshot: dict[str, Any]) -> dict[str, Any]:
    try:
        return daily_web_update_payload(master_settings, snapshot)
    except Exception as exc:
        return {"summary": {"status": "error", "sources": 0, "ok": 0, "error": str(exc)}}


def safe_agent_routine_payload(snapshot: dict[str, Any]) -> dict[str, Any]:
    try:
        return agent_routine_payload(master_settings, snapshot)
    except Exception as exc:
        return {
            "summary": {"steps": 0, "ready": 0, "attention": 0, "next_step": str(exc)},
            "rows": [],
            "cost_guards": [],
            "next_step": {},
        }


def safe_actions_payload(snapshot: dict[str, Any] | None = None) -> dict[str, Any]:
    try:
        return master_actions_payload(master_settings, snapshot or {})
    except Exception as exc:
        return {
            "summary": {"total": 0, "pass": 0, "needs_fix": 0, "blocked": 0, "error": str(exc)},
            "next_action": {"title": "Errore lettura azioni", "why": str(exc), "do": "Controlla log Python."},
            "actions": [],
        }


def safe_realtime_payload(phases: list[dict[str, Any]], actions: dict[str, Any]) -> dict[str, Any]:
    try:
        return realtime_payload(master_settings, phases, [], [{"event_type": "streamlit.master", "payload": {"status": "open"}}])
    except Exception:
        progress = round(sum(int(row["progress"]) for row in phases) / len(phases)) if phases else 0
        next_action = actions.get("next_action", {}) if isinstance(actions, dict) else {}
        return {
            "summary": {
                "mode": "streamlit_local",
                "status": "ready",
                "progress": progress,
                "poll_seconds": 0,
                "updated_at": datetime.now().isoformat(timespec="seconds"),
                "next_action": next_action.get("title", "Agente pronto"),
                "current_event": "streamlit.local",
            },
            "stages": [
                {"stage": row["name"], "status": row["status"], "progress": row["progress"], "signal": row["phase_id"], "detail": row["objective"]}
                for row in phases
            ],
        }


def build_master_snapshot() -> dict[str, Any]:
    phases = phase_records()
    snapshot: dict[str, Any] = {
        "phases": phases,
        "services": services_snapshot(),
        "theme": light_theme_snapshot(),
    }
    # no-snapshot payloads first
    snapshot["trust"] = safe_trust_payload()
    snapshot["network"] = safe_network_payload()
    snapshot["official_inbox"] = safe_official_inbox_payload()
    snapshot["sales_channels"] = safe_sales_channels_payload()
    snapshot["catalog"] = safe_catalog_payload()
    # snapshot-dependent
    snapshot["crm"] = safe_growth_crm_payload(snapshot)
    snapshot["legal"] = safe_legal_payload(snapshot)
    snapshot["market"] = safe_market_sense_payload(snapshot)
    snapshot["photo_studio"] = safe_photo_studio_payload(snapshot)
    snapshot["actions"] = safe_actions_payload(snapshot)
    snapshot["realtime"] = safe_realtime_payload(phases, snapshot["actions"])
    snapshot["social_campaigns"] = safe_social_campaigns_payload(snapshot)
    snapshot["weekly_goals"] = safe_weekly_goals_payload(snapshot)
    snapshot["member_tryon"] = safe_member_tryon_payload()
    snapshot["live_sync"] = safe_catalog_live_sync_payload()
    snapshot["web_health"] = safe_daily_web_update_payload(snapshot)
    snapshot["routine"] = safe_agent_routine_payload(snapshot)
    return snapshot


def render_progression_panel(snapshot: dict[str, Any] | None = None) -> None:
    snapshot = snapshot or build_master_snapshot()
    realtime = snapshot.get("realtime", {})
    summary = realtime.get("summary", {})
    stages = realtime.get("stages", [])
    progress = int(summary.get("progress", 0) or 0)

    st.subheader("Progressione visibile")
    cols = st.columns(4)
    cols[0].metric("Stato", summary.get("status", "ready"))
    cols[1].metric("Progress", f"{progress}%")
    cols[2].metric("Evento", summary.get("current_event", "streamlit"))
    cols[3].metric("Next", summary.get("next_action", "Agente pronto"))
    st.progress(progress / 100, text=f"Avanzamento agente: {progress}%")

    if stages:
        frame = pd.DataFrame(stages)
        st.dataframe(
            frame,
            width="stretch",
            hide_index=True,
            column_config={
                "progress": st.column_config.ProgressColumn("progress", min_value=0, max_value=100, format="%d%%"),
            },
        )


def render_agent_console(snapshot: dict[str, Any] | None = None) -> None:
    snapshot = snapshot or build_master_snapshot()
    st.subheader("Domande e risposte Master")
    st.caption("Area ampia: scrivi una richiesta operativa, il Master risponde dai dati e mostra la prossima azione.")

    if "bks_master_chat" not in st.session_state:
        st.session_state.bks_master_chat = [
            {
                "role": "assistant",
                "content": "Sono pronto. Chiedimi: prima cosa da fare, progressione, Google Merchant, tema, social, catalogo o connessioni.",
            }
        ]

    history = st.container(height=460, border=True)
    with history:
        for index, item in enumerate(st.session_state.bks_master_chat[-12:]):
            role = "Tu" if item["role"] == "user" else "Master"
            st.markdown(f"**{role}**")
            st.text_area(
                role,
                value=item["content"],
                height=150 if item["role"] == "user" else 220,
                disabled=True,
                label_visibility="collapsed",
                key=f"bks-chat-{index}-{item['role']}",
            )

    question = st.text_area(
        "Domanda al Master",
        placeholder="Esempio: qual e la prima azione ora? Mostrami la progressione. Cosa blocca Google Merchant?",
        height=170,
    )
    col_send, col_clear = st.columns([2, 1])
    if col_send.button("Invia al Master", type="primary", width="stretch", disabled=not question.strip()):
        answer = agent_reply(question, snapshot)
        st.session_state.bks_master_chat.append({"role": "user", "content": question.strip()})
        st.session_state.bks_master_chat.append({"role": "assistant", "content": answer.get("reply", "")})
        st.rerun()
    if col_clear.button("Pulisci chat", width="stretch"):
        st.session_state.bks_master_chat = []
        st.rerun()


def render_system_status(snapshot: dict[str, Any] | None = None) -> None:
    snapshot = snapshot or build_master_snapshot()
    trust = snapshot.get("trust", {}).get("summary", {})
    network = snapshot.get("network", {}).get("summary", {})
    inbox = snapshot.get("official_inbox", {}).get("summary", {})
    legal = snapshot.get("legal", {}).get("summary", {})
    market = snapshot.get("market", {}).get("summary", {})
    goals = snapshot.get("weekly_goals", {}).get("summary", {})
    sync = snapshot.get("live_sync", {}).get("summary", {})
    web = snapshot.get("web_health", {}).get("summary", {})
    tryon = snapshot.get("member_tryon", {}).get("summary", {})

    def _ok(val: Any) -> str:
        return "◎ OK" if int(val or 0) == 0 else f"⚠ {int(val or 0)}"

    merchant_status = trust.get("status", "?")
    merchant_icon = "◎" if merchant_status not in {"suspended", "error", "warning"} else "⚠"

    row1 = st.columns(5)
    row1[0].metric("Google Merchant", f"{merchant_icon} {merchant_status}")
    row1[1].metric("Trust P0", _ok(trust.get("blockers", 0)))
    row1[2].metric("Network", _ok(network.get("needs_fix", 0)))
    row1[3].metric("Legal", _ok(legal.get("customer_needs", 0)))
    row1[4].metric("Inbox", inbox.get("status", "?")[:14])

    row2 = st.columns(4)
    row2[0].metric("Market score", market.get("market_sense", "?"))
    row2[1].metric(f"Goals {goals.get('week','')}", f"{goals.get('pass',0)}/{goals.get('total',0)}")
    row2[2].metric("Camerino pending", tryon.get("pending_requests", 0))
    row2[3].metric("Web health", web.get("status", "?")[:14])


_ROUTINE_STATUS_ICON = {
    "ready": "◎",
    "attention": "⚠",
    "needs_config": "⚙",
    "prepare": "◈",
    "blocked": "✕",
    "approval_required": "⬡",
}
_ROUTINE_STATUS_COLOR = {
    "ready": "#489808",
    "attention": "#d4a030",
    "needs_config": "#8888cc",
    "prepare": "#0ca898",
    "blocked": "#c82020",
    "approval_required": "#9828d8",
}


def render_agent_routine(snapshot: dict[str, Any] | None = None) -> None:
    snapshot = snapshot or build_master_snapshot()
    routine = snapshot.get("routine", {})
    summary = routine.get("summary", {})
    rows = routine.get("rows", [])
    next_step = routine.get("next_step", {})

    cols = st.columns(4)
    cols[0].metric("Step routine", summary.get("steps", 0))
    cols[1].metric("Ready", summary.get("ready", 0))
    cols[2].metric("Attention", summary.get("attention", 0))
    cols[3].metric("Prossimo", (summary.get("next_step", "—") or "—")[:22])

    if next_step:
        status_val = next_step.get("status", "ready")
        icon = _ROUTINE_STATUS_ICON.get(status_val, "◎")
        color = _ROUTINE_STATUS_COLOR.get(status_val, "#2f6f6b")
        st.markdown(
            f"""<div style="border-top:2px solid {color};background:rgba(250,250,247,0.03);
            padding:12px 16px;font-family:'DM Mono',monospace;margin:8px 0">
            <span style="color:{color};font-size:0.68rem;letter-spacing:0.12em;text-transform:uppercase">
            {icon} {status_val}</span><br>
            <span style="color:#fafaf7;font-size:0.88rem;font-weight:300">{next_step.get('step','')}</span><br>
            <span style="color:rgba(250,250,247,0.50);font-size:0.62rem">{next_step.get('cadence','')} — {next_step.get('approval','')}</span>
            </div>""",
            unsafe_allow_html=True,
        )

    if rows:
        display_rows = [
            {
                "#": r.get("priority", ""),
                "step": r.get("step", ""),
                "status": f"{_ROUTINE_STATUS_ICON.get(r.get('status',''), '◎')} {r.get('status', '')}",
                "cadence": r.get("cadence", ""),
                "automation": r.get("automation", ""),
                "approval": r.get("approval", ""),
            }
            for r in rows
        ]
        st.dataframe(pd.DataFrame(display_rows), width="stretch", hide_index=True)


def render_master_actions(snapshot: dict[str, Any] | None = None) -> None:
    snapshot = snapshot or build_master_snapshot()
    actions = snapshot.get("actions", {})
    summary = actions.get("summary", {})
    next_action = actions.get("next_action", {})
    cols = st.columns(4)
    cols[0].metric("Azioni", summary.get("total", 0))
    cols[1].metric("Pass", summary.get("pass", 0))
    cols[2].metric("Da fare", summary.get("needs_fix", 0))
    cols[3].metric("Bloccate", summary.get("blocked", 0))
    with st.container(border=True):
        st.markdown("#### Prima azione consigliata")
        st.write(next_action.get("title", "Agente pronto"))
        st.caption(next_action.get("why", ""))
        st.info(next_action.get("do", ""))
    rows = actions.get("actions", [])
    if rows:
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


def stream_subprocess(args: list[str], timeout: int = 300) -> int | None:
    """Stream subprocess stdout line-by-line into a Streamlit code block."""
    import queue
    import threading

    output_box = st.empty()
    lines: list[str] = []

    proc = subprocess.Popen(
        [sys.executable, *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        cwd=BASE_DIR,
        encoding="utf-8",
        errors="replace",
    )

    q: queue.Queue[str | None] = queue.Queue()

    def _reader(pipe: Any, q: Any) -> None:
        for line in pipe:
            q.put(line)
        q.put(None)

    t = threading.Thread(target=_reader, args=(proc.stdout, q), daemon=True)
    t.start()

    import time
    deadline = time.time() + timeout
    done = False
    while not done and time.time() < deadline:
        try:
            line = q.get(timeout=0.1)
        except queue.Empty:
            continue
        if line is None:
            done = True
        else:
            lines.append(line)
            output_box.code("".join(lines[-80:]), language="text")

    proc.wait()
    return proc.returncode


def render_theme_upgrade_panel() -> None:
    """Realtime Theme Upgrade procedure panel."""
    st.subheader("Theme Upgrade — Procedura Realtime")
    st.caption(f"Tema live: 202392961362 · TM04 BKS v20/06/2026 · Pre-publish gate: armocromia/tipografo/copy/photo/commercial")

    # Stato ultimo upgrade (legge dal log se esiste)
    log_path = BASE_DIR / "output" / "theme_upgrade_log.txt"

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Tema live", "202392961362")
    col2.metric("Versione", "20/06/2026")
    col3.metric("Gate", "5/5 ✅")
    col4.metric("Worker", "v20/06/2026")
    col5.metric("Immagini", "Piano: in corso")

    st.divider()

    # ── Tab procedure ─────────────────────────────────────────────────────────
    upgrade_tabs = st.tabs(["Deploy Tema", "Immagini Sito", "AI Worker", "Log ultimo run"])

    with upgrade_tabs[0]:
        st.markdown("**Push file tema → live theme 202392961362**")
        st.caption("Esegue: backup versione + pre-publish gate (5 skill) + push 20 file modificati/nuovi")
        if st.button("▶ Esegui Theme Upgrade completo", type="primary", key="btn_theme_upgrade", width="stretch"):
            with st.container(border=True):
                rc = stream_subprocess(["scripts/theme_upgrade_20jun2026.py"], timeout=180)
                if rc == 0:
                    st.success("Theme Upgrade completato — 20/20 file pushati ✅")
                else:
                    st.error(f"Errore durante il push (exit {rc}) — controlla il log sopra")

    with upgrade_tabs[1]:
        st.markdown("**Genera immagini sito (editorial 1536×1024 + piano 1024×1024)**")
        st.caption("usa gpt-image-1 — costo API ~$0.08 per immagine. Le editorial esistono già (2026-06-19).")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            if st.button("Genera Piano (mancanti)", key="btn_gen_piano", width="stretch"):
                with st.container(border=True):
                    rc = stream_subprocess(["scripts/generate_site_images.py", "--type", "piano"], timeout=600)
                    if rc == 0:
                        st.success("Piano squares generati ✅")
                    else:
                        st.error(f"Errore generazione (exit {rc})")
        with col_b:
            if st.button("Rigenera Editorial (tutte)", key="btn_gen_editorial", width="stretch"):
                with st.container(border=True):
                    rc = stream_subprocess(["scripts/generate_site_images.py", "--type", "editorial"], timeout=600)
                    if rc == 0:
                        st.success("Editorial generate ✅")
                    else:
                        st.error(f"Errore generazione (exit {rc})")
        with col_c:
            if st.button("Upload immagini → Shopify", key="btn_upload_imgs", width="stretch"):
                with st.container(border=True):
                    rc = stream_subprocess(["scripts/upload_site_images.py"], timeout=300)
                    if rc == 0:
                        st.success("Immagini caricate su Shopify ✅")
                    else:
                        st.error(f"Errore upload (exit {rc})")

        # Mostra manifest immagini esistenti
        manifest_path = BASE_DIR / "output" / "site_images" / "manifest.json"
        if manifest_path.exists():
            import json
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            rows_img = [
                {
                    "filename": k,
                    "collection": v.get("collection", ""),
                    "type": v.get("type", ""),
                    "uploaded": "✅" if v.get("shopify_url") else "—",
                    "generated": v.get("generated_at", "")[:10] if v.get("generated_at") else "—",
                }
                for k, v in manifest.items()
            ]
            st.dataframe(pd.DataFrame(rows_img), width="stretch", hide_index=True)

    with upgrade_tabs[2]:
        st.markdown("**Deploy BKS AI Worker → Cloudflare**")
        st.caption("Worker: bks-agent.bakabo.workers.dev · 23,839 chars · Tier Metal v20/06/2026")
        if st.button("▶ Deploy Worker Cloudflare", type="primary", key="btn_deploy_worker", width="stretch"):
            with st.container(border=True):
                rc = stream_subprocess(["scripts/_deploy_worker.py"], timeout=60)
                if rc == 0:
                    st.success("Worker deployato ✅")
                else:
                    st.error(f"Errore deploy (exit {rc})")

    with upgrade_tabs[3]:
        st.markdown("**Log ultimo run**")
        if log_path.exists():
            st.code(log_path.read_text(encoding="utf-8", errors="replace")[-8000:], language="text")
        else:
            st.info("Nessun log disponibile — esegui un upgrade per generare il log.")


def render_theme_bks_page() -> None:
    st.title("Tema BKS")
    st.caption("Hero BKS, effetti globali, grid collection, trust strip e ZIP pronto.")
    data = safe_theme_payload()
    summary = data.get("summary", {})
    files = data.get("files", {})
    cols = st.columns(4)
    cols[0].metric("Patch", summary.get("status", "unknown"))
    cols[1].metric("Output", "ready" if summary.get("output_zip") else "missing")
    cols[2].metric("Hero", "BKS")
    cols[3].metric("Effetti", "global")
    zip_rel = summary.get("output_zip", "")
    if zip_rel:
        st.write(zip_rel)
        output = BASE_DIR / zip_rel
        if output.exists() and output.is_file():
            st.download_button("Scarica ZIP tema", output.read_bytes(), file_name=output.name, mime="application/zip", width="stretch")
    st.dataframe(pd.DataFrame(data.get("checks", [])), width="stretch", hide_index=True)
    st.dataframe(pd.DataFrame([{"file": key, "path": value} for key, value in files.items()]), width="stretch", hide_index=True)


def render_direct_dialogue() -> None:
    """Direct AI dialogue + real-time authorizations panel."""
    st.subheader("Dialogo Diretto — BKS AI")
    st.caption("Chat diretta con il sistema BKS. Autorizza azioni, dai comandi, ricevi risposte operative in realtime.")

    import json as _json

    # ── Authorization queue ───────────────────────────────────────────────────
    auth_q_path = BASE_DIR / "output" / "bks_auth_queue.json"
    if auth_q_path.exists():
        try:
            queue_items = _json.loads(auth_q_path.read_text(encoding="utf-8"))
        except Exception:
            queue_items = []
    else:
        queue_items = []

    if queue_items:
        st.markdown("#### Azioni in attesa di autorizzazione")
        for item in queue_items:
            with st.container(border=True):
                c1, c2, c3 = st.columns([4, 1, 1])
                c1.markdown(f"**{item.get('action', '?')}**  \n`{item.get('detail', '')}`")
                if c2.button("✅ Autorizza", key=f"auth_{item.get('id', '')}"):
                    item["status"] = "approved"
                    auth_q_path.write_text(_json.dumps(queue_items, indent=2, ensure_ascii=False), encoding="utf-8")
                    st.success("Autorizzato!")
                    st.rerun()
                if c3.button("✕ Nega", key=f"deny_{item.get('id', '')}"):
                    item["status"] = "denied"
                    auth_q_path.write_text(_json.dumps(queue_items, indent=2, ensure_ascii=False), encoding="utf-8")
                    st.warning("Negato.")
                    st.rerun()
        st.divider()

    # ── Chat con AI (usa OpenAI via .env) ─────────────────────────────────────
    if "bks_direct_chat" not in st.session_state:
        st.session_state.bks_direct_chat = [
            {
                "role": "assistant",
                "content": "Dialogo diretto attivo. Scrivi un'azione da eseguire, una domanda operativa, o autorizza un'operazione in coda.",
            }
        ]

    history_box = st.container(height=420, border=True)
    with history_box:
        for idx, msg in enumerate(st.session_state.bks_direct_chat[-14:]):
            role_label = "Roberto" if msg["role"] == "user" else "BKS AI"
            color = "#d4a030" if msg["role"] == "user" else "#2f6f6b"
            st.markdown(
                f'<div style="border-left:3px solid {color};padding:6px 12px;margin-bottom:8px;'
                f'font-family:\'DM Mono\',monospace;font-size:0.78rem">'
                f'<span style="color:{color};font-size:0.60rem;letter-spacing:0.1em;text-transform:uppercase">'
                f'{role_label}</span><br>{msg["content"]}</div>',
                unsafe_allow_html=True,
            )

    user_msg = st.text_area(
        "Messaggio",
        placeholder="Esempio: esegui upgrade tema · crea immagini piano · verifica worker · autorizza push...",
        height=100,
        key="direct_chat_input",
        label_visibility="collapsed",
    )

    col_send, col_clear, col_cmd = st.columns([2, 1, 1])

    if col_send.button("Invia", type="primary", key="btn_direct_send", disabled=not user_msg.strip(), width="stretch"):
        load_local_env()
        api_key = os.environ.get("OPENAI_API_KEY", "")
        if not api_key:
            st.error("OPENAI_API_KEY non configurata in .env")
        else:
            import urllib.request
            import urllib.error

            system_prompt = """\
Sei BKS Ops AI — assistente operativo diretto per BKS Studio / bakabo.club.
Sistema: Shopify TM04 v20/06/2026, 674 prodotti, 8 collezioni, Cloudflare Worker bks-agent.
Tier Metal: Lead (0 ordini) → Iron (1-2) → Brass (3-5) → Silver (6-10) → Gold (11+).
Comandi disponibili: upgrade_tema | genera_immagini | deploy_worker | check_status | sync_catalog.
Rispondi in italiano, sintetico, operativo. Se l'utente chiede di eseguire un'azione: conferma che la stai eseguendo e specifica il comando shell preciso."""

            messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.bks_direct_chat[-10:]]
            messages.append({"role": "user", "content": user_msg.strip()})

            payload = _json.dumps({
                "model": "gpt-4o",
                "temperature": 0.3,
                "messages": [{"role": "system", "content": system_prompt}] + messages,
            }).encode()

            req = urllib.request.Request(
                "https://api.openai.com/v1/chat/completions",
                data=payload,
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            )
            with st.spinner("BKS AI sta rispondendo..."):
                try:
                    with urllib.request.urlopen(req, timeout=30) as resp:
                        result = _json.loads(resp.read())
                        reply = result["choices"][0]["message"]["content"].strip()
                except Exception as exc:
                    reply = f"Errore chiamata AI: {exc}"

            st.session_state.bks_direct_chat.append({"role": "user", "content": user_msg.strip()})
            st.session_state.bks_direct_chat.append({"role": "assistant", "content": reply})
            st.rerun()

    if col_clear.button("Pulisci", key="btn_direct_clear", width="stretch"):
        st.session_state.bks_direct_chat = []
        st.rerun()

    with col_cmd:
        if st.button("Esegui last cmd", key="btn_run_last_cmd", width="stretch"):
            # Run last command mentioned in chat
            last = next(
                (m["content"] for m in reversed(st.session_state.bks_direct_chat) if m["role"] == "assistant"),
                None,
            )
            if last:
                import re
                cmd_match = re.search(r"`([^`]+\.py[^`]*)`", last)
                if cmd_match:
                    cmd_args = cmd_match.group(1).split()
                    with st.container(border=True):
                        stream_subprocess(cmd_args, timeout=300)


def render_overview_page() -> None:
    st.title("BKS Master — Hub")
    st.caption("Agente AI, progressione fasi, azioni consigliate. Usa la sidebar per le pagine operative.")

    service_states = [port_open(service.port) for service in SERVICES]
    theme_path = active_theme_zip()
    catalog_path = active_catalog_csv()
    snapshot = build_master_snapshot()
    _, live_summary = read_live_audit()
    catalog_summary = snapshot.get("catalog", {}).get("summary", {})

    cols = st.columns(5)
    cols[0].metric("Servizi online", f"{sum(service_states)}/{len(SERVICES)}")
    cols[1].metric("Tema TM04", "OK" if (theme_path and Path(theme_path).exists()) else "missing")
    cols[2].metric("CSV catalogo", "OK" if (catalog_path and Path(catalog_path).exists()) else "missing")
    cols[3].metric("Prodotti DB", catalog_summary.get("products", "n/d"))
    cols[4].metric("Audit live", live_summary.get("checked", 0) if live_summary else "n/d")

    st.divider()
    render_system_status(snapshot)
    st.divider()

    main_tabs = st.tabs(["Progressione", "Theme Upgrade", "Dialogo Diretto", "Azioni", "Agente"])

    with main_tabs[0]:
        render_progression_panel(snapshot)
        render_agent_routine(snapshot)

    with main_tabs[1]:
        render_theme_upgrade_panel()

    with main_tabs[2]:
        render_direct_dialogue()

    with main_tabs[3]:
        render_master_actions(snapshot)

    with main_tabs[4]:
        render_agent_console(snapshot)


def critical_files() -> tuple[tuple[str, str | Path | None], ...]:
    return (
        ("Catalogo attivo", active_catalog_csv()),
        ("Tema Shopify attivo", active_theme_zip()),
        ("Image Factory v1.1", active_image_factory_dir()),
        ("Asset config", ACTIVE_ASSETS_PATH),
        ("Collection plan", "output/bks_collection_plan_v20.csv"),
        ("Template assignment", "output/bks_collection_template_assignment_v20.csv"),
        ("Payload collection", "output/bks_collection_payloads_v20.json"),
        ("Audit live", "output/live_site_audit/live_site_audit.md"),
        ("Prompt immagini", "output/bks_collection_image_prompts_v20.md"),
    )


def port_open(port: int) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=1.0):
            return True
    except OSError:
        return False


def start_launcher(launcher: str) -> tuple[bool, str]:
    path = BASE_DIR / launcher
    if not path.exists():
        return False, f"Launcher non trovato: {launcher}"
    try:
        subprocess.Popen(
            ["cmd", "/c", "start", "", str(path)],
            cwd=str(BASE_DIR),
            shell=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as exc:
        return False, str(exc)
    return True, f"Avvio richiesto: {launcher}"


def run_command(args: list[str], timeout: int = 180) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=BASE_DIR,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )


def read_live_audit() -> tuple[pd.DataFrame, dict[str, int]]:
    if not LIVE_AUDIT_CSV.exists():
        return pd.DataFrame(), {}
    rows = list(csv.DictReader(LIVE_AUDIT_CSV.open(encoding="utf-8")))
    if not rows:
        return pd.DataFrame(), {}
    frame = pd.DataFrame(rows)
    statuses = pd.to_numeric(frame["status"], errors="coerce").fillna(0).astype(int)
    summary = {
        "checked": int(len(frame)),
        "ok": int(((statuses >= 200) & (statuses < 400)).sum()),
        "not_found": int((statuses == 404).sum()),
        "throttled": int((statuses == 429).sum()),
        "expected_gtm": int(frame["expected_gtm"].eq("yes").sum() if "expected_gtm" in frame.columns else 0),
        "legacy_gtm": int(frame["legacy_gtm"].astype(str).ne("").sum() if "legacy_gtm" in frame.columns else 0),
    }
    return frame, summary


def render_services() -> None:
    st.subheader("Servizi locali")
    rows = []
    for service in SERVICES:
        online = port_open(service.port)
        rows.append(
            {
                "fase": service.phase,
                "servizio": service.name,
                "porta": service.port,
                "stato": "online" if online else "offline",
                "ruolo": service.role,
            }
        )
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)

    cols = st.columns(len(SERVICES))
    for index, service in enumerate(SERVICES):
        with cols[index]:
            st.markdown(f"**{service.phase} {service.name}**")
            st.caption(service.role)
            if service.launcher:
                if st.button(f"Avvia {service.phase}", key=f"start-{service.phase}-{index}", width="stretch"):
                    ok, message = start_launcher(service.launcher)
                    st.success(message) if ok else st.error(message)
            else:
                st.caption("Avviato da 00_START_BKS_MASTER.bat")
            st.link_button(f"Apri {service.phase}", service.url, width="stretch")


def render_command_center() -> None:
    st.subheader("Pannello comandi generale")
    render_services()

    st.divider()
    st.write("Comandi rapidi")
    cmd_cols = st.columns(3)
    with cmd_cols[0]:
        if st.button("Completa SEO/tag catalogo", width="stretch"):
            with st.spinner("Aggiornamento CSV in corso..."):
                result = run_command(["tools/enrich_shopify_catalog.py", "--set-active"], timeout=240)
            st.success("Catalogo aggiornato.") if result.returncode == 0 else st.error("Aggiornamento catalogo fallito.")
            if result.stdout or result.stderr:
                st.code((result.stdout + "\n" + result.stderr)[-4000:], language="text")
    with cmd_cols[1]:
        if st.button("Ottimizza tema attivo", width="stretch"):
            with st.spinner("Ottimizzazione tema in corso..."):
                result = run_command(["tools/optimize_shopify_theme.py", "--set-active"], timeout=240)
            st.success("Tema aggiornato.") if result.returncode == 0 else st.error("Ottimizzazione tema fallita.")
            if result.stdout or result.stderr:
                st.code((result.stdout + "\n" + result.stderr)[-4000:], language="text")
    with cmd_cols[2]:
        if st.button("Audit live/GTM", width="stretch"):
            with st.spinner("Audit live in corso..."):
                result = run_command(["tools/audit_live_site.py"], timeout=240)
            st.success("Audit completato.") if result.returncode == 0 else st.error("Audit fallito.")
            if result.stdout or result.stderr:
                st.code((result.stdout + "\n" + result.stderr)[-4000:], language="text")


def render_phase_map() -> None:
    st.subheader("Fasi operative")
    st.dataframe(
        pd.DataFrame(PROJECT_PHASES),
        width="stretch",
        hide_index=True,
    )


def render_project_manager() -> None:
    st.subheader("Project Manager — BKS Studio")

    catalog = safe_catalog_payload()
    actions_data = safe_actions_payload()
    theme_zip = active_theme_zip()
    catalog_csv = active_catalog_csv()
    cat_sum = catalog.get("summary", {})
    next_act = actions_data.get("next_action", {})

    svc_online = sum(1 for s in services_snapshot().values() if s["status"] == "online")

    cols = st.columns(5)
    cols[0].metric("Servizi", f"{svc_online}/3", delta=None)
    cols[1].metric("Prodotti DB", cat_sum.get("products", "n/d"))
    cols[2].metric("Handles", cat_sum.get("handles", "n/d"))
    cols[3].metric("Tema", "TM04 OK" if (theme_zip and Path(theme_zip).exists()) else "missing")
    cols[4].metric("CSV", Path(catalog_csv).name[:18] if (catalog_csv and Path(catalog_csv).exists()) else "missing")

    st.divider()

    phase_rows = []
    for p in PROJECT_PHASES:
        out_raw = p["output"]
        out_path = BASE_DIR / out_raw
        file_ok = out_path.exists()
        phase_rows.append({
            "fase": p["fase"],
            "nome": p["nome"],
            "stato": p["stato"],
            "avanzamento": STATUS_PROGRESS.get(str(p["stato"]), 40),
            "output": "OK" if file_ok else "—",
            "comando": p["comando"],
        })

    st.dataframe(
        pd.DataFrame(phase_rows),
        width="stretch",
        hide_index=True,
        column_config={
            "avanzamento": st.column_config.ProgressColumn("avanzamento", min_value=0, max_value=100, format="%d%%"),
            "output": st.column_config.TextColumn("file", width="small"),
        },
    )

    if next_act:
        st.divider()
        with st.container(border=True):
            st.markdown(f"**Prossima azione — {next_act.get('title', '')}**")
            if next_act.get("why"):
                st.caption(next_act["why"])
            if next_act.get("do"):
                st.info(next_act["do"])


def render_management_panel() -> None:
    st.subheader("Gestione — Servizi & Asset")
    render_system_status()
    st.divider()
    management_tabs = st.tabs(["Servizi & Comandi", "Asset attivi", "Monitoraggio"])
    with management_tabs[0]:
        render_command_center()
    with management_tabs[1]:
        render_critical_files()
    with management_tabs[2]:
        render_monitoring()


def format_asset_option(path: Path) -> str:
    if not path.exists():
        return f"{path.name} - missing"
    updated = datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
    size_mb = path.stat().st_size / 1024 / 1024
    return f"{path.name} - {updated} - {size_mb:.2f} MB"


def option_index(options: list[Path], selected: Path) -> int:
    selected_resolved = selected.resolve()
    for index, option in enumerate(options):
        if option.resolve() == selected_resolved:
            return index
    return 0


def render_asset_selectors() -> None:
    st.subheader("Asset attivi")
    theme_options = discover_theme_zips()
    catalog_options = discover_catalog_csvs()

    current_theme = active_theme_zip()
    current_catalog = active_catalog_csv()

    if current_theme and current_theme.exists() and all(path.resolve() != current_theme.resolve() for path in theme_options):
        theme_options.insert(0, current_theme)
    if current_catalog and current_catalog.exists() and all(path.resolve() != current_catalog.resolve() for path in catalog_options):
        catalog_options.insert(0, current_catalog)

    col_theme, col_catalog = st.columns(2)
    selected_theme = current_theme
    selected_catalog = current_catalog

    with col_theme:
        if theme_options:
            selected_theme = st.selectbox(
                "Tema Shopify",
                theme_options,
                index=option_index(theme_options, current_theme or theme_options[0]),
                format_func=format_asset_option,
            )
            latest = latest_theme_zip()
            st.caption(f"Ultimo rilevato: {relative_to_base(latest)}")
        else:
            st.warning("Nessuno ZIP tema trovato in 04_TEMA_SHOPIFY.")

    with col_catalog:
        if catalog_options:
            selected_catalog = st.selectbox(
                "Catalogo CSV",
                catalog_options,
                index=option_index(catalog_options, current_catalog or catalog_options[0]),
                format_func=format_asset_option,
            )
            latest = latest_catalog_csv()
            st.caption(f"Ultimo rilevato: {relative_to_base(latest)}")
        else:
            st.warning("Nessun CSV catalogo trovato.")

    if st.button("Usa selezione come asset attivi", width="stretch", disabled=not (theme_options and catalog_options)):
        save_active_assets(
            theme_zip=selected_theme,
            catalog_csv=selected_catalog,
            image_factory_dir=active_image_factory_dir(),
        )
        st.success("Asset attivi aggiornati.")
        st.rerun()


def render_critical_files() -> None:
    render_asset_selectors()
    st.subheader("File critici")
    st.dataframe(
        pd.DataFrame(
            [
                {"nome": label, **file_info(relative)} if relative is not None else {"nome": label, "file": "", "exists": False, "size_mb": "", "updated": ""}
                for label, relative in critical_files()
            ]
        ),
        width="stretch",
        hide_index=True,
    )


def render_monitoring() -> None:
    st.subheader("Monitoraggio live")
    frame, summary = read_live_audit()
    if summary:
        cols = st.columns(6)
        cols[0].metric("URL controllati", summary["checked"])
        cols[1].metric("HTTP ok", summary["ok"])
        cols[2].metric("404", summary["not_found"])
        cols[3].metric("429", summary["throttled"])
        cols[4].metric("GTM atteso", summary["expected_gtm"])
        cols[5].metric("GTM legacy", summary["legacy_gtm"])
    else:
        st.info("Nessun audit live disponibile.")

    if st.button("Esegui audit live/GTM", width="stretch"):
        with st.spinner("Audit live in corso..."):
            result = run_command(["tools/audit_live_site.py"], timeout=240)
        if result.returncode == 0:
            st.success("Audit completato.")
        else:
            st.error(f"Audit fallito con exit code {result.returncode}.")
        output = "\n".join(part for part in [result.stdout, result.stderr] if part.strip())
        if output:
            st.code(output[-6000:], language="text")

    if not frame.empty:
        st.dataframe(
            frame[["url", "status", "title", "expected_gtm", "legacy_gtm", "welcome_placeholder", "error"]],
            width="stretch",
            hide_index=True,
        )


def render_environment() -> None:
    st.subheader("Configurazione")
    load_local_env()
    rows = [
        {"chiave": "SHOPIFY_MYSHOPIFY_DOMAIN", "stato": "set" if os.environ.get("SHOPIFY_MYSHOPIFY_DOMAIN") else "missing"},
        {"chiave": "SHOPIFY_ADMIN_TOKEN", "stato": "set" if os.environ.get("SHOPIFY_ADMIN_TOKEN") else "missing"},
        {"chiave": "SHOPIFY_API_VERSION", "stato": os.environ.get("SHOPIFY_API_VERSION", "missing")},
        {"chiave": "OPENAI_API_KEY", "stato": "set" if os.environ.get("OPENAI_API_KEY") else "missing"},
        {"chiave": "META_BUSINESS_ID", "stato": "set" if os.environ.get("META_BUSINESS_ID") else "missing"},
        {"chiave": "META_ACCESS_TOKEN", "stato": "set" if os.environ.get("META_ACCESS_TOKEN") else "missing"},
        {"chiave": "FACEBOOK_PAGE_ID", "stato": "set" if os.environ.get("FACEBOOK_PAGE_ID") else "missing"},
        {"chiave": "INSTAGRAM_BUSINESS_ID", "stato": "set" if os.environ.get("INSTAGRAM_BUSINESS_ID") else "missing"},
        {"chiave": "TIKTOK_ADVERTISER_ID", "stato": "set" if os.environ.get("TIKTOK_ADVERTISER_ID") else "missing"},
        {"chiave": "TIKTOK_ACCESS_TOKEN", "stato": "set" if os.environ.get("TIKTOK_ACCESS_TOKEN") else "missing"},
        {"chiave": "GTM target", "stato": "GTM-PF5Z85KS"},
        {"chiave": "Merchant Center", "stato": "5295165689"},
        {"chiave": "GA4 property", "stato": "bakabo-9a8c5 / 483501489"},
    ]
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


BKS_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&display=swap');

:root {
    --bks-dark: #0A0A0A;
    --bks-paper: #fafaf7;
    --bks-accent: #2f6f6b;
    --bks-accent-dim: rgba(47,111,107,0.18);
    --bks-border: rgba(250,250,247,0.08);
    --bks-border-strong: rgba(250,250,247,0.18);
    --bks-dim: rgba(250,250,247,0.50);
    --bks-mono: 'DM Mono', 'Courier New', monospace;
}

/* === app background === */
[data-testid="stApp"] {
    background: var(--bks-dark) !important;
    color: var(--bks-paper) !important;
}

/* === sidebar === */
[data-testid="stSidebar"] {
    background: #0f0f0d !important;
    border-right: 1px solid var(--bks-border) !important;
}
[data-testid="stSidebar"] * { color: var(--bks-paper) !important; }
[data-testid="stSidebarNav"] a {
    font-family: var(--bks-mono) !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    color: var(--bks-dim) !important;
    border-radius: 0 !important;
    padding: 6px 12px !important;
}
[data-testid="stSidebarNav"] a:hover,
[data-testid="stSidebarNav"] .active {
    color: var(--bks-paper) !important;
    background: var(--bks-accent-dim) !important;
    border-left: 2px solid var(--bks-accent) !important;
}

/* === headings === */
h1, h2, h3, h4 {
    font-family: var(--bks-mono) !important;
    font-weight: 400 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    color: var(--bks-paper) !important;
}
h1 { font-size: 1.1rem !important; border-bottom: 1px solid var(--bks-border-strong); padding-bottom: 8px; }
h2, h3 { font-size: 0.78rem !important; }
[data-testid="stCaption"], caption, small {
    font-family: var(--bks-mono) !important;
    font-size: 0.60rem !important;
    color: var(--bks-dim) !important;
    letter-spacing: 0.08em !important;
}

/* === metrics === */
[data-testid="metric-container"] {
    background: rgba(250,250,247,0.03) !important;
    border: 1px solid var(--bks-border) !important;
    border-top: 2px solid var(--bks-accent) !important;
    border-radius: 0 !important;
    padding: 12px !important;
}
[data-testid="stMetricLabel"] {
    font-family: var(--bks-mono) !important;
    font-size: 0.58rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: var(--bks-dim) !important;
}
[data-testid="stMetricValue"] {
    font-family: var(--bks-mono) !important;
    font-size: 1.3rem !important;
    color: var(--bks-paper) !important;
    font-weight: 300 !important;
}

/* === buttons === */
button[kind="primary"], [data-testid="baseButton-primary"] {
    background: var(--bks-accent) !important;
    color: var(--bks-paper) !important;
    border: none !important;
    border-radius: 0 !important;
    font-family: var(--bks-mono) !important;
    font-size: 0.68rem !important;
    letter-spacing: 0.10em !important;
    text-transform: uppercase !important;
}
button[kind="secondary"], [data-testid="baseButton-secondary"] {
    background: transparent !important;
    color: var(--bks-paper) !important;
    border: 1px solid var(--bks-border-strong) !important;
    border-radius: 0 !important;
    font-family: var(--bks-mono) !important;
    font-size: 0.68rem !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
}
button:hover {
    border-color: var(--bks-accent) !important;
    color: var(--bks-accent) !important;
}

/* === dataframes === */
[data-testid="stDataFrame"] iframe,
[data-testid="stDataFrame"] > div {
    border: 1px solid var(--bks-border) !important;
    border-radius: 0 !important;
}

/* === containers with border === */
[data-testid="stVerticalBlockBorderWrapper"] {
    border: 1px solid var(--bks-border) !important;
    border-top: 2px solid var(--bks-accent) !important;
    border-radius: 0 !important;
    background: rgba(250,250,247,0.02) !important;
    padding: 12px !important;
}

/* === info/success/error === */
[data-testid="stAlert"] {
    border-radius: 0 !important;
    border-left: 3px solid var(--bks-accent) !important;
    background: var(--bks-accent-dim) !important;
    font-family: var(--bks-mono) !important;
    font-size: 0.70rem !important;
}

/* === progress bar === */
[data-testid="stProgressBar"] > div > div {
    background: var(--bks-accent) !important;
    border-radius: 0 !important;
}
[data-testid="stProgressBar"] > div {
    background: rgba(250,250,247,0.08) !important;
    border-radius: 0 !important;
}

/* === text inputs === */
[data-testid="stTextArea"] textarea, [data-testid="stTextInput"] input {
    background: rgba(250,250,247,0.04) !important;
    border: 1px solid var(--bks-border-strong) !important;
    border-radius: 0 !important;
    color: var(--bks-paper) !important;
    font-family: var(--bks-mono) !important;
    font-size: 0.80rem !important;
}

/* === divider === */
hr { border-color: var(--bks-border) !important; }

/* === tabs === */
[data-testid="stTabs"] [role="tab"] {
    font-family: var(--bks-mono) !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.10em !important;
    text-transform: uppercase !important;
    color: var(--bks-dim) !important;
    border-radius: 0 !important;
    border-bottom: 2px solid transparent !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: var(--bks-paper) !important;
    border-bottom: 2px solid var(--bks-accent) !important;
    background: transparent !important;
}

/* === selectbox === */
[data-testid="stSelectbox"] select,
[data-testid="stSelectbox"] > div > div {
    background: rgba(250,250,247,0.04) !important;
    border: 1px solid var(--bks-border-strong) !important;
    border-radius: 0 !important;
    font-family: var(--bks-mono) !important;
    font-size: 0.72rem !important;
    color: var(--bks-paper) !important;
}

/* === spinner === */
[data-testid="stSpinner"] { color: var(--bks-accent) !important; }
</style>
"""


def inject_bks_theme() -> None:
    st.markdown(BKS_CSS, unsafe_allow_html=True)


def main() -> None:
    st.set_page_config(
        page_title="BKS Master",
        page_icon="◎",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_bks_theme()
    render_overview_page()


if __name__ == "__main__":
    main()
