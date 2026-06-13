#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BakAbo/BKS master monitoring panel."""

from __future__ import annotations

import csv
import json
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

from ecommerce_automation.config import settings as master_settings
from ecommerce_automation.master_actions import payload as master_actions_payload
from ecommerce_automation.master_agent import reply as agent_reply
from ecommerce_automation.realtime_control import payload as realtime_payload
from ecommerce_automation.theme_optimizer import payload as theme_optimizer_payload

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
SOCIAL_POSTS_CSV = OUTPUT_DIR / "social_posts_queue.csv"
SOCIAL_POST_FIELDS = [
    "id",
    "created_at",
    "platform",
    "phase",
    "collection",
    "objective",
    "format",
    "publish_date",
    "status",
    "message",
    "cta",
    "url",
    "utm_campaign",
]


@dataclass(frozen=True)
class Service:
    phase: str
    name: str
    port: int
    url: str
    launcher: str
    role: str


SERVICES = (
    Service("01", "Catalog Engine", 5000, "http://localhost:5000", "01_START_CATALOG_ENGINE.bat", "CSV, immagini prodotto, SEO export"),
    Service("02", "Automation Console", 8501, "http://localhost:8501", "02_START_COLLECTIONS_DASHBOARD.bat", "Collection, immagini AI, Analytics, Merchant"),
    Service("03", "Metafields Runner", 8502, "http://localhost:8502", "03_START_METAFIELDS_RUNNER.bat", "Metafields, metaobjects, popolamento prodotto"),
    Service("04", "Image Factory v1.1", 8503, "http://localhost:8503", "04_START_IMAGE_FACTORY.bat", "Mockup, shooting AI, QA, export immagini"),
)

SOCIAL_LINKS = {
    "Facebook": "https://www.facebook.com/bakabofirm/",
    "Instagram": "https://www.instagram.com/bakabofirm/",
    "TikTok": "https://www.tiktok.com/@bakabofirm",
}

PROJECT_PHASES = (
    {"fase": "01", "nome": "Asset attivi", "obiettivo": "Scegli tema e CSV aggiornati", "comando": "Master > File", "output": "output/bks_active_assets.json", "stato": "pronto", "guida": "README.md"},
    {"fase": "02", "nome": "Catalogo", "obiettivo": "SEO, tag canonici, dati prodotto puliti", "comando": "01_START_CATALOG_ENGINE.bat", "output": "output/products_export_updated.csv", "stato": "pronto", "guida": "01_CATALOGO/README.md"},
    {"fase": "03", "nome": "Collezioni", "obiettivo": "25 collection, regole, template e SEO", "comando": "02_START_COLLECTIONS_DASHBOARD.bat", "output": "output/bks_collection_plan_v20.csv", "stato": "operativa", "guida": "02_COLLEZIONI/README.md"},
    {"fase": "04", "nome": "Metafields", "obiettivo": "bks.collection/design/drop/series aggiornati", "comando": "03_START_METAFIELDS_RUNNER.bat", "output": "output/populate_metafields_log.csv", "stato": "operativa", "guida": "03_METAFIELDS_METAOBJECTS/README.md"},
    {"fase": "05", "nome": "Tema Shopify", "obiettivo": "ZIP pronto, card mobile proporzionate, SEO fallback", "comando": "tools/optimize_shopify_theme.py", "output": "04_TEMA_SHOPIFY/BKS_TM03_clean_12JUN2026_SEO_READY.zip", "stato": "pronto", "guida": "04_TEMA_SHOPIFY/README.md"},
    {"fase": "06", "nome": "Testi e policy", "obiettivo": "About, FAQ, Contact, Shipping, policy footer", "comando": "output/site_texts_v1", "output": "05_TESTI_POLICY", "stato": "verifica", "guida": "05_TESTI_POLICY/README.md"},
    {"fase": "07", "nome": "Image Factory", "obiettivo": "Mockup, shooting, QA, export immagini", "comando": "04_START_IMAGE_FACTORY.bat", "output": "BAKABO_IMAGE_FACTORY_v1.1/output", "stato": "integrata", "guida": "BAKABO_IMAGE_FACTORY_v1.1"},
    {"fase": "08", "nome": "Analytics", "obiettivo": "GA4/GTM, Merchant, efficienza marketing", "comando": "Automation > Analytics", "output": "output/live_site_audit", "stato": "monitoraggio", "guida": "06_ANALYTICS_MERCHANT/README.md"},
    {"fase": "09", "nome": "Social PM", "obiettivo": "Facebook, Instagram, TikTok e calendario target", "comando": "Master > Project Manager", "output": "social plan", "stato": "attivo", "guida": "Project Manager"},
    {"fase": "10", "nome": "Deploy", "obiettivo": "Upload tema, import CSV, audit, publish", "comando": "07_DEPLOY_CHECK", "output": "tema + catalogo live", "stato": "da eseguire", "guida": "07_DEPLOY_CHECK/README.md"},
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
    output_zip = BASE_DIR / "04_TEMA_SHOPIFY" / "BKS_TM03_LIGHT_TRUST_TIMER_READY.zip"
    return {
        "summary": {
            "status": "ready" if output_zip.exists() else "missing",
            "goal": "hero_bks_global_effects_trust_theme",
            "output_zip": relative_to_base(output_zip),
        }
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
    snapshot["actions"] = safe_actions_payload(snapshot)
    snapshot["realtime"] = safe_realtime_payload(phases, snapshot["actions"])
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
            use_container_width=True,
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
    if col_send.button("Invia al Master", type="primary", use_container_width=True, disabled=not question.strip()):
        answer = agent_reply(question, snapshot)
        st.session_state.bks_master_chat.append({"role": "user", "content": question.strip()})
        st.session_state.bks_master_chat.append({"role": "assistant", "content": answer.get("reply", "")})
        st.rerun()
    if col_clear.button("Pulisci chat", use_container_width=True):
        st.session_state.bks_master_chat = []
        st.rerun()


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
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


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
    st.write(summary.get("output_zip", ""))
    output = BASE_DIR / summary.get("output_zip", "")
    if output.exists():
        st.download_button("Scarica ZIP tema", output.read_bytes(), file_name=output.name, mime="application/zip", use_container_width=True)
    st.dataframe(pd.DataFrame(data.get("checks", [])), use_container_width=True, hide_index=True)
    st.dataframe(pd.DataFrame([{"file": key, "path": value} for key, value in files.items()]), use_container_width=True, hide_index=True)


def render_overview_page() -> None:
    st.title("BKS MASTER STREAMLIT")
    st.caption("Interfaccia principale con progressione visibile, Q&A ampia e pagine operative nella sidebar.")

    service_states = [port_open(service.port) for service in SERVICES]
    theme_path = active_theme_zip()
    catalog_path = active_catalog_csv()
    snapshot = build_master_snapshot()
    _, live_summary = read_live_audit()
    cols = st.columns(4)
    cols[0].metric("Servizi online", f"{sum(service_states)}/{len(SERVICES)}")
    cols[1].metric("Tema zip", "ok" if theme_path.exists() else "missing")
    cols[2].metric("CSV catalogo", "ok" if catalog_path.exists() else "missing")
    cols[3].metric("Audit live", live_summary.get("checked", 0) if live_summary else "n/d")

    render_progression_panel(snapshot)
    render_agent_console(snapshot)
    render_master_actions(snapshot)


def critical_files() -> tuple[tuple[str, str | Path], ...]:
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
        "expected_gtm": int((frame.get("expected_gtm", "") == "yes").sum()),
        "legacy_gtm": int(frame.get("legacy_gtm", pd.Series(dtype=str)).astype(str).ne("").sum()),
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
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    cols = st.columns(len(SERVICES))
    for index, service in enumerate(SERVICES):
        with cols[index]:
            st.markdown(f"**{service.phase} {service.name}**")
            st.caption(service.role)
            if st.button(f"Avvia {service.phase}", key=f"start-{service.phase}", use_container_width=True):
                ok, message = start_launcher(service.launcher)
                st.success(message) if ok else st.error(message)
            st.link_button(f"Apri {service.phase}", service.url, use_container_width=True)


def render_command_center() -> None:
    st.subheader("Pannello comandi generale")
    render_services()

    st.divider()
    st.write("Comandi rapidi")
    cmd_cols = st.columns(3)
    with cmd_cols[0]:
        if st.button("Completa SEO/tag catalogo", use_container_width=True):
            with st.spinner("Aggiornamento CSV in corso..."):
                result = run_command(["tools/enrich_shopify_catalog.py", "--set-active"], timeout=240)
            st.success("Catalogo aggiornato.") if result.returncode == 0 else st.error("Aggiornamento catalogo fallito.")
            if result.stdout or result.stderr:
                st.code((result.stdout + "\n" + result.stderr)[-4000:], language="text")
    with cmd_cols[1]:
        if st.button("Ottimizza tema attivo", use_container_width=True):
            with st.spinner("Ottimizzazione tema in corso..."):
                result = run_command(["tools/optimize_shopify_theme.py", "--set-active"], timeout=240)
            st.success("Tema aggiornato.") if result.returncode == 0 else st.error("Ottimizzazione tema fallita.")
            if result.stdout or result.stderr:
                st.code((result.stdout + "\n" + result.stderr)[-4000:], language="text")
    with cmd_cols[2]:
        if st.button("Audit live/GTM", use_container_width=True):
            with st.spinner("Audit live in corso..."):
                result = run_command(["tools/audit_live_site.py"], timeout=240)
            st.success("Audit completato.") if result.returncode == 0 else st.error("Audit fallito.")
            if result.stdout or result.stderr:
                st.code((result.stdout + "\n" + result.stderr)[-4000:], language="text")


def render_phase_map() -> None:
    st.subheader("Fasi operative")
    st.dataframe(
        pd.DataFrame(PROJECT_PHASES),
        use_container_width=True,
        hide_index=True,
    )


def social_account_rows() -> list[dict[str, str]]:
    load_local_env()
    return [
        {
            "canale": "Meta Business",
            "account": os.environ.get("META_BUSINESS_ID", "da collegare"),
            "credential": "META_BUSINESS_ID / META_ACCESS_TOKEN",
            "stato": "set" if os.environ.get("META_BUSINESS_ID") and os.environ.get("META_ACCESS_TOKEN") else "missing",
        },
        {
            "canale": "Facebook Page",
            "account": os.environ.get("FACEBOOK_PAGE_ID", SOCIAL_LINKS["Facebook"]),
            "credential": "FACEBOOK_PAGE_ID",
            "stato": "set" if os.environ.get("FACEBOOK_PAGE_ID") else "link pronto",
        },
        {
            "canale": "Instagram Business",
            "account": os.environ.get("INSTAGRAM_BUSINESS_ID", SOCIAL_LINKS["Instagram"]),
            "credential": "INSTAGRAM_BUSINESS_ID",
            "stato": "set" if os.environ.get("INSTAGRAM_BUSINESS_ID") else "link pronto",
        },
        {
            "canale": "TikTok Business",
            "account": os.environ.get("TIKTOK_ADVERTISER_ID", SOCIAL_LINKS["TikTok"]),
            "credential": "TIKTOK_ADVERTISER_ID / TIKTOK_ACCESS_TOKEN",
            "stato": "set" if os.environ.get("TIKTOK_ADVERTISER_ID") and os.environ.get("TIKTOK_ACCESS_TOKEN") else "link pronto",
        },
    ]


def load_social_posts() -> pd.DataFrame:
    if not SOCIAL_POSTS_CSV.exists():
        return pd.DataFrame(columns=SOCIAL_POST_FIELDS)
    try:
        frame = pd.read_csv(SOCIAL_POSTS_CSV, dtype=str).fillna("")
    except Exception:
        return pd.DataFrame(columns=SOCIAL_POST_FIELDS)
    for field in SOCIAL_POST_FIELDS:
        if field not in frame.columns:
            frame[field] = ""
    return frame[SOCIAL_POST_FIELDS]


def save_social_posts(frame: pd.DataFrame) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    clean = frame.copy()
    for field in SOCIAL_POST_FIELDS:
        if field not in clean.columns:
            clean[field] = ""
    clean[SOCIAL_POST_FIELDS].to_csv(SOCIAL_POSTS_CSV, index=False, encoding="utf-8-sig")


def append_social_post(row: dict[str, str]) -> None:
    frame = load_social_posts()
    next_id = f"post-{datetime.now():%Y%m%d%H%M%S}-{len(frame) + 1:03d}"
    payload = {field: row.get(field, "") for field in SOCIAL_POST_FIELDS}
    payload["id"] = payload["id"] or next_id
    payload["created_at"] = payload["created_at"] or datetime.now().strftime("%Y-%m-%d %H:%M")
    frame = pd.concat([frame, pd.DataFrame([payload])], ignore_index=True)
    save_social_posts(frame)


def default_social_message(platform: str, collection: str, objective: str) -> str:
    base = (
        f"BKS {collection}: AI-generated all-over print pieces, made to order. "
        "A visual system built for wear, movement and daily use."
    )
    if platform == "TikTok":
        return f"{base} Process, print, fit check. Follow the next drop on bakabo.club."
    if platform == "Instagram":
        return f"{base} Save the collection and explore the new edit on bakabo.club."
    if objective == "Retargeting":
        return f"Still thinking about BKS {collection}? Return to the collection and choose the piece that fits your next city day."
    return f"{base} Explore the collection on bakabo.club."


def generate_social_drafts() -> None:
    drafts = [
        ("Facebook", "Folklore", "Traffic", "Collection post"),
        ("Instagram", "Glyph", "Engagement", "Carousel"),
        ("TikTok", "Marker", "Awareness", "Short video"),
        ("Facebook", "Riviera", "Retargeting", "Catalog post"),
        ("Instagram", "Token", "Traffic", "Reel"),
        ("TikTok", "Pulse", "Creative test", "Short video"),
    ]
    for platform, collection, objective, post_format in drafts:
        append_social_post(
            {
                "platform": platform,
                "phase": "09 Social PM",
                "collection": collection,
                "objective": objective,
                "format": post_format,
                "publish_date": "",
                "status": "draft",
                "message": default_social_message(platform, collection, objective),
                "cta": "Explore collection",
                "url": "https://bakabo.club",
                "utm_campaign": f"bks-{collection.lower()}-{platform.lower()}",
            }
        )


def render_social_post_manager() -> None:
    st.write("Post e messaggi")
    with st.form("social-post-form"):
        col_a, col_b, col_c = st.columns(3)
        platform = col_a.selectbox("Canale", ["Facebook", "Instagram", "TikTok", "Meta Ads"])
        collection = col_b.selectbox("Collection", ["Hours", "Glyph", "Marker", "Riviera", "Pulse", "Token", "Flag", "Folklore", "Catalog"])
        objective = col_c.selectbox("Obiettivo", ["Awareness", "Traffic", "Engagement", "Retargeting", "Creative test"])
        col_d, col_e, col_f = st.columns(3)
        post_format = col_d.selectbox("Formato", ["Collection post", "Carousel", "Reel", "Short video", "Story", "Catalog ad"])
        publish_date = col_e.date_input("Data", value=None)
        status = col_f.selectbox("Stato", ["draft", "ready", "scheduled", "published", "paused"])
        suggested = default_social_message(platform, collection, objective)
        message = st.text_area("Messaggio", value=suggested, height=120)
        col_g, col_h = st.columns(2)
        cta = col_g.text_input("CTA", value="Explore collection")
        url = col_h.text_input("URL", value="https://bakabo.club")
        submitted = st.form_submit_button("Salva post")
        if submitted:
            append_social_post(
                {
                    "platform": platform,
                    "phase": "09 Social PM",
                    "collection": collection,
                    "objective": objective,
                    "format": post_format,
                    "publish_date": publish_date.isoformat() if publish_date else "",
                    "status": status,
                    "message": message,
                    "cta": cta,
                    "url": url,
                    "utm_campaign": f"bks-{collection.lower()}-{platform.lower()}",
                }
            )
            st.success("Post salvato nella queue.")

    if st.button("Genera bozze base Facebook/Instagram/TikTok", use_container_width=True):
        generate_social_drafts()
        st.success("Bozze create.")
        st.rerun()

    posts = load_social_posts()
    if posts.empty:
        st.info("Nessun post in queue.")
        return
    edited = st.data_editor(posts, use_container_width=True, hide_index=True, num_rows="dynamic")
    if st.button("Salva modifiche queue", use_container_width=True):
        save_social_posts(edited)
        st.success("Queue aggiornata.")
    st.download_button(
        "Scarica social_posts_queue.csv",
        data=SOCIAL_POSTS_CSV.read_bytes(),
        file_name="social_posts_queue.csv",
        mime="text/csv",
        use_container_width=True,
    )


def social_plan_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"canale": "Facebook", "ruolo": "Proof, community, retargeting", "contenuti": "Collection drop, policy trust, product proof", "target": "visitatori + pubblico caldo"},
            {"canale": "Instagram", "ruolo": "Visual discovery", "contenuti": "Carousel collezioni, reel prodotto, stories QA", "target": "streetwear, resort, AI-art"},
            {"canale": "TikTok", "ruolo": "Creative testing", "contenuti": "Before/after mockup, process AI, outfit loop", "target": "prospecting creativo"},
            {"canale": "Meta Ads", "ruolo": "Acquisizione + retargeting", "contenuti": "Catalog ads, DPA, UTM per collection", "target": "lookalike + visitatori 7/14/30g"},
        ]
    )


def connector_steps_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"step": "01", "azione": "Inserire META_BUSINESS_ID e META_ACCESS_TOKEN in .env", "stato": "richiede credenziali"},
            {"step": "02", "azione": "Inserire FACEBOOK_PAGE_ID e INSTAGRAM_BUSINESS_ID", "stato": "richiede credenziali"},
            {"step": "03", "azione": "Inserire TIKTOK_ADVERTISER_ID e TIKTOK_ACCESS_TOKEN", "stato": "opzionale"},
            {"step": "04", "azione": "Standardizzare UTM: source, medium, campaign, content", "stato": "da applicare"},
            {"step": "05", "azione": "Collegare feed/catalogo prodotti a Meta Commerce e TikTok Catalog", "stato": "post-import"},
        ]
    )


def render_social_panel() -> None:
    st.subheader("2_Social")
    st.caption("Creazione messaggi, coda post e collegamenti business per Facebook, Instagram, TikTok e Meta Ads.")

    social_cols = st.columns(3)
    for index, (label, url) in enumerate(SOCIAL_LINKS.items()):
        social_cols[index].link_button(label, url, use_container_width=True)

    st.write("Piano canali")
    st.dataframe(social_plan_frame(), use_container_width=True, hide_index=True)

    render_social_post_manager()

    st.write("Collegamenti business")
    st.dataframe(pd.DataFrame(social_account_rows()), use_container_width=True, hide_index=True)
    st.dataframe(connector_steps_frame(), use_container_width=True, hide_index=True)


def render_project_manager() -> None:
    st.subheader("3_Project Manager")
    phase_frame = pd.DataFrame(PROJECT_PHASES)
    status_counts = phase_frame["stato"].value_counts().rename_axis("stato").reset_index(name="fasi")

    cols = st.columns(4)
    cols[0].metric("Fasi totali", len(phase_frame))
    cols[1].metric("Pronte/integrate", int(phase_frame["stato"].isin(["pronto", "integrata", "attivo"]).sum()))
    cols[2].metric("Monitoraggio", int((phase_frame["stato"] == "monitoraggio").sum()))
    cols[3].metric("Da eseguire", int((phase_frame["stato"] == "da eseguire").sum()))

    st.bar_chart(status_counts.set_index("stato"))
    st.dataframe(phase_frame, use_container_width=True, hide_index=True)

    st.write("Controllo operativo")
    st.dataframe(
        phase_frame[["fase", "nome", "comando", "output", "guida", "stato"]],
        use_container_width=True,
        hide_index=True,
    )


def render_management_panel() -> None:
    st.subheader("1_Gestione")
    st.caption("Avvio servizi, scelta asset attivi, monitoraggio live e configurazione generale.")
    management_tabs = st.tabs(["Comandi", "File attivi", "Monitoraggio", "Config"])
    with management_tabs[0]:
        render_command_center()
    with management_tabs[1]:
        render_critical_files()
    with management_tabs[2]:
        render_monitoring()
    with management_tabs[3]:
        render_environment()


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

    if current_theme.exists() and all(path.resolve() != current_theme.resolve() for path in theme_options):
        theme_options.insert(0, current_theme)
    if current_catalog.exists() and all(path.resolve() != current_catalog.resolve() for path in catalog_options):
        catalog_options.insert(0, current_catalog)

    col_theme, col_catalog = st.columns(2)
    selected_theme = current_theme
    selected_catalog = current_catalog

    with col_theme:
        if theme_options:
            selected_theme = st.selectbox(
                "Tema Shopify",
                theme_options,
                index=option_index(theme_options, current_theme),
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
                index=option_index(catalog_options, current_catalog),
                format_func=format_asset_option,
            )
            latest = latest_catalog_csv()
            st.caption(f"Ultimo rilevato: {relative_to_base(latest)}")
        else:
            st.warning("Nessun CSV catalogo trovato.")

    if st.button("Usa selezione come asset attivi", use_container_width=True, disabled=not (theme_options and catalog_options)):
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
                {"nome": label, **file_info(relative)}
                for label, relative in critical_files()
            ]
        ),
        use_container_width=True,
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

    if st.button("Esegui audit live/GTM", use_container_width=True):
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
            use_container_width=True,
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
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def main() -> None:
    st.set_page_config(page_title="BKS Master Streamlit", page_icon="BKS", layout="wide")
    render_overview_page()


if __name__ == "__main__":
    main()
