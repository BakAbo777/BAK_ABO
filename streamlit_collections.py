#!/usr/bin/env python3
"""
BKS CRUSCOTTO COLLEZIONI

Run:
  streamlit run streamlit_collections.py
"""

from __future__ import annotations

import csv
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

import pandas as pd
import requests
import streamlit as st  # type: ignore
import urllib3

try:
    import certifi
except ImportError:
    certifi = None

from bks_assets import active_catalog_csv, relative_to_base
from bks_collection_specs import ( # type: ignore
    ALL_COLLECTIONS,
    LEGACY_COLLECTION_METAFIELDS,
    MANAGED_HANDLES,
    MISSING_COLLECTION_HANDLES,
    TEMPLATE_EXCLUDED_HANDLES,
    CollectionSpec,
    collection_to_payload,
    specs_for_missing_batch,
)


BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
DEFAULT_API_VERSION = "2025-01"
LIVE_CSV = active_catalog_csv()
IMAGE_PROGRAM_DIR = BASE_DIR / "output" / "collection_image_program"
OPENAI_PROMPT_DIR = BASE_DIR / "output" / "openai_image_prompts"
OPENAI_IMAGE_DIR = BASE_DIR / "output" / "openai_images"
LIVE_AUDIT_DIR = BASE_DIR / "output" / "live_site_audit"
LIVE_PAGES_CSV = LIVE_AUDIT_DIR / "live_pages.csv"
COLLECTION_PLAN_CSV = BASE_DIR / "output" / "bks_collection_plan_v20.csv"
TEMPLATE_ASSIGNMENT_CSV = BASE_DIR / "output" / "bks_collection_template_assignment_v20.csv"
TEMPLATE_EXCLUSIONS_CSV = BASE_DIR / "output" / "bks_collection_template_exclusions_v20.csv"
LEGACY_AUDIT_CSV = BASE_DIR / "output" / "bks_collection_legacy_metafields_audit_v20.csv"
IMAGE_PROMPTS_MD = BASE_DIR / "output" / "bks_collection_image_prompts_v20.md"

PHASE1_REPORT = BASE_DIR / "output" / "series_tag_fix_report.csv"
METAFIELDS_LOG = BASE_DIR / "output" / "metafield_definitions_log.csv"
METAOBJECTS_LOG = BASE_DIR / "output" / "metaobjects_log.csv"
POPULATE_LOG = BASE_DIR / "output" / "populate_metafields_log.csv"

MERCHANT_CENTER = {
    "account": "bakabo.club",
    "account_id": "5295165689",
    "local_inventory_missing": 68300,
    "product_page_unavailable": 8390,
    "note": "Molte segnalazioni sono tracce di prodotti eliminati dalla collezione ma non ancora reindicizzati da Google.",
}

ANALYTICS_SNAPSHOT = {
    "property": "bakabo-9a8c5",
    "property_id": "483501489",
    "active_users": 89,
    "sessions": 97,
    "views": 200,
    "events": 453,
    "gtm_container": "GTM-PF5Z85KS",
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


def get_env_value(*names: str, default: str = "") -> str:
    for name in names:
        value = os.environ.get(name, "").strip()
        if value:
            return value
    return default


def mask_token(token: str) -> str:
    return f"{token[:6]}...{token[-4:]}" if len(token) >= 12 else "<missing>"


def run_command(args: list[str], store_domain: str, token: str, api_version: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    if store_domain:
        env["SHOPIFY_MYSHOPIFY_DOMAIN"] = store_domain
        env["SHOPIFY_STORE"] = store_domain
    if token:
        env["SHOPIFY_ADMIN_TOKEN"] = token
        env["SHOPIFY_TOKEN"] = token
    if api_version:
        env["SHOPIFY_API_VERSION"] = api_version
    return subprocess.run(
        [sys.executable, *args],
        cwd=BASE_DIR,
        env=env,
        text=True,
        capture_output=True,
        timeout=3600,
        check=False,
    )


def render_command_result(result: subprocess.CompletedProcess[str]) -> None:
    if result.returncode == 0:
        st.success("Comando completato.")
    else:
        st.error(f"Comando fallito con exit code {result.returncode}.")
    output = "\n".join(part for part in [result.stdout, result.stderr] if part.strip())
    if output:
        st.code(output[-7000:], language="text")
        if "billing_hard_limit_reached" in output:
            st.warning(
                "OpenAI ha raggiunto il limite di fatturazione del progetto. "
                "Il prompt e' salvato: aumenta il budget/hard limit OpenAI oppure usa una chiave con credito disponibile."
            )
        if "ssl_verification_failed" in output or "Errore SSL verso OpenAI" in output:
            st.info("Problema certificato locale: puoi usare temporaneamente Bypass SSL OpenAI dal pannello immagini.")


def collections_dataframe(collections: tuple[CollectionSpec, ...], live: dict[str, dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for spec in collections:
        item = live.get(spec.handle, {})
        live_template_suffix = item.get("template_suffix")
        live_template = f"collection.{live_template_suffix}" if live_template_suffix else "collection"
        live_title = item.get("metafields_global_title_tag", "") or ""
        live_description = item.get("metafields_global_description_tag", "") or ""
        
        rows.append(
            {
                "sync": spec.handle not in TEMPLATE_EXCLUDED_HANDLES,
                "group": spec.group,
                "title": spec.title,
                "handle": spec.handle,
                "live_status": "presente" if item else "manca",
                "live_products": item.get("products_count", ""),
                "live_id": item.get("id", ""),
                "missing_batch_16": spec.handle in MISSING_COLLECTION_HANDLES,
                "template": spec.effective_template,
                "template_scope": spec.template_scope,
                "live_template": live_template if item else "",
                "seo_chars": spec.seo_description_chars,
                "seo_live": "ok" if item and live_title == spec.seo_title and live_description == spec.seo_description else ("manca" if not item else "da aggiornare"),
                "rule": spec.rule_label,
            }
        )
    return pd.DataFrame(rows)


def read_csv_summary(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {"exists": False, "rows": 0, "products": 0, "published": 0, "active": 0}
    
    products: set[str] = set()
    rows = published = active = 0
    
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as fh:
            first_line = fh.readline()
            if not first_line:
                return {"exists": True, "rows": 0, "products": 0, "published": 0, "active": 0}
            
            fh.seek(0)
            reader = csv.DictReader(fh)
            
            if not reader.fieldnames:
                return {"exists": True, "rows": 0, "products": 0, "published": 0, "active": 0}

            for row in reader:
                if row is None: continue
                rows += 1
                handle = (row.get("Handle") or "").strip()
                if handle:
                    products.add(handle)
                
                pub_val = str(row.get("Published", "")).strip().lower()
                if pub_val in {"true", "1", "yes"}:
                    published += 1
                
                status_val = str(row.get("Status", "")).strip().lower()
                if status_val == "active":
                    active += 1
    except Exception as e:
        return {"exists": True, "rows": rows, "products": len(products), "published": published, "active": active, "error": str(e)}

    return {"exists": True, "rows": rows, "products": len(products), "published": published, "active": active}


def log_counts(path: Path) -> dict[str, int]:
    if not path.exists():
        return {}
    
    try:
        frame = pd.read_csv(path, on_bad_lines='skip', engine='python')
    except Exception:
        return {"error_reading_file": 1}

    if frame.empty:
        return {"empty_file": 1}

    if "status" not in frame.columns:
        return {"rows": len(frame)}
    
    try:
        counts = frame["status"].fillna("unknown").value_counts()
        return {str(key): int(value) for key, value in counts.items()}
    except Exception:
        return {"count_error": 1}


def strip_html(value: str) -> str:
    return " ".join(re.sub(r"<[^>]+>", " ", value or "").split())


def safe_file_stem(value: str, fallback: str = "bks-asset") -> str:
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]+', "-", value or "")
    cleaned = re.sub(r"\s+", "-", cleaned.strip())
    cleaned = re.sub(r"-{2,}", "-", cleaned).strip(" .-_").lower()
    stem = cleaned or fallback
    reserved = {
        "con", "prn", "aux", "nul",
        "com1", "com2", "com3", "com4", "com5", "com6", "com7", "com8", "com9",
        "lpt1", "lpt2", "lpt3", "lpt4", "lpt5", "lpt6", "lpt7", "lpt8", "lpt9",
    }
    if stem in reserved:
        stem = f"{stem}-asset"
    return stem[:120]


def prompt_file_candidates(handle: str) -> list[Path]:
    return [
        IMAGE_PROGRAM_DIR / "curated" / "prompts" / f"{handle}.txt",
        IMAGE_PROGRAM_DIR / "prompts" / f"{handle}_still-life.txt",
        IMAGE_PROGRAM_DIR / "prompts" / f"{handle}_on-model.txt",
        OPENAI_PROMPT_DIR / f"{handle}.txt",
    ]


def base_image_prompt(spec: CollectionSpec, mode: str) -> str:
    mode_copy = {
        "Collection hero 4:5": "vertical 4:5 Shopify collection hero cover",
        "Product cutout transparent": "single product cutout on transparent background",
        "Editorial banner": "wide editorial banner for a Shopify section",
        "Social square": "square social preview image",
    }[mode]
    background = "transparent background" if mode == "Product cutout transparent" else "clean neutral studio background"
    return "\n".join(
        [
            f"{mode_copy} for BakAbo, the storefront container, featuring BKS Studio.",
            f"Collection: {spec.title} ({spec.handle}).",
            f"Concept: {strip_html(spec.body_html)}",
            "Visual direction: AI-art wearable design, product visibility first, strong color, high contrast, no fake review text, no pricing, no discount badge.",
            "Composition: clear product silhouettes, enough negative space for Shopify cropping, no unreadable typography, no copied logo, no watermark.",
            f"Background: {background}.",
            "Output should feel modern, editorial, accessible, and consistent with the BakAbo/BKS visual system.",
        ]
    )


def load_default_prompt(spec: CollectionSpec, mode: str) -> str:
    for path in prompt_file_candidates(spec.handle):
        if path.exists():
            return path.read_text(encoding="utf-8").strip()
    return base_image_prompt(spec, mode)


def read_live_pages() -> pd.DataFrame:
    if not LIVE_PAGES_CSV.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(LIVE_PAGES_CSV)
    except Exception:
        return pd.DataFrame()


def render_phase_map() -> None:
    phases = pd.DataFrame(
        [
            {"fase": "01 Asset attivi", "obiettivo": "Scegli tema e CSV aggiornati", "comando": "Master > 1_Gestione", "stato": "pronto"},
            {"fase": "02 Catalogo", "obiettivo": "SEO, tag canonici, dati prodotto puliti", "comando": "01_START_CATALOG_ENGINE.bat", "stato": "pronto"},
            {"fase": "03 Collezioni", "obiettivo": "25 collection, template, SEO", "comando": "02_START_COLLECTIONS_DASHBOARD.bat", "stato": "operativa"},
            {"fase": "04 Metafields", "obiettivo": "bks.collection/design/drop + metaobject", "comando": "03_START_METAFIELDS_RUNNER.bat", "stato": "operativa"},
            {"fase": "05 Tema Shopify", "obiettivo": "ZIP pronto, card mobile proporzionate, SEO fallback", "comando": "tools/optimize_shopify_theme.py", "stato": "pronto"},
            {"fase": "06 Testi e policy", "obiettivo": "About, FAQ, Contact, Shipping, policy footer", "comando": "05_TESTI_POLICY", "stato": "verifica"},
            {"fase": "07 Image Factory", "obiettivo": "Mockup, shooting, QA, export immagini", "comando": "04_START_IMAGE_FACTORY.bat", "stato": "integrata"},
            {"fase": "08 Analytics", "obiettivo": "GA4/GTM, Merchant Center, marketing efficiency", "comando": "tab Analytics", "stato": "monitoraggio"},
            {"fase": "09 Social PM", "obiettivo": "Post, messaggi, Facebook, Instagram, TikTok", "comando": "Master > 2_Social", "stato": "attivo"},
            {"fase": "10 Deploy", "obiettivo": "Upload tema, import CSV, audit, publish", "comando": "07_DEPLOY_CHECK", "stato": "da eseguire"},
        ]
    )
    st.dataframe(phases, use_container_width=True, hide_index=True)


class ShopifyAdmin:
    def __init__(self, store_domain: str, token: str, api_version: str, verify_ssl: bool = True) -> None:
        domain = store_domain.replace("https://", "").replace("http://", "").strip("/")
        self.base_url = f"https://{domain}/admin/api/{api_version}"
        self.headers = {"X-Shopify-Access-Token": token, "Content-Type": "application/json"}
        self.verify: bool | str = certifi.where() if verify_ssl and certifi else verify_ssl
        if not verify_ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        response = requests.request(
            method,
            f"{self.base_url}{path}",
            headers=self.headers,
            verify=self.verify,
            timeout=45,
            **kwargs,
        )
        response.raise_for_status()
        return response

    def get_shop_name(self) -> str:
        return self.request("GET", "/shop.json").json().get("shop", {}).get("name", "Shopify")

    def get_products_count(self) -> int | None:
        try:
            return int(self.request("GET", "/products/count.json").json().get("count", 0))
        except Exception:
            return None

    def list_smart_collections(self) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        page_info = ""
        while True:
            params = {
                "limit": 250,
                "fields": (
                    "id,title,handle,body_html,rules,disjunctive,published,updated_at,"
                    "template_suffix,metafields_global_title_tag,metafields_global_description_tag"
                ),
            }
            if page_info:
                params = {"limit": 250, "page_info": page_info}
            response = self.request("GET", "/smart_collections.json", params=params)
            out.extend(response.json().get("smart_collections", []))
            page_info = next_page_info(response.headers.get("Link", ""))
            if not page_info:
                break
        return out

    def get_collection_products_count(self, collection_id: int | str) -> int | None:
        try:
            data = self.request("GET", f"/collections/{collection_id}/products/count.json").json()
            return int(data.get("count", 0))
        except Exception:
            return None

    def live_managed_collections(self) -> dict[str, dict[str, Any]]:
        live: dict[str, dict[str, Any]] = {}
        for item in self.list_smart_collections():
            handle = item.get("handle", "")
            if handle in MANAGED_HANDLES:
                item["products_count"] = self.get_collection_products_count(item["id"])
                live[handle] = item
        return live

    def create_smart_collection(self, spec: CollectionSpec) -> dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/smart_collections.json",
            headers=self.headers,
            json=collection_to_payload(spec),
            verify=self.verify,
            timeout=45,
        )
        if response.status_code == 422:
            raise ValueError(response.json().get("errors", response.text))
        response.raise_for_status()
        return response.json()["smart_collection"]

    def update_smart_collection(self, collection_id: int | str, spec: CollectionSpec) -> dict[str, Any]:
        payload = collection_to_payload(spec)
        payload["smart_collection"]["id"] = collection_id
        response = self.request("PUT", f"/smart_collections/{collection_id}.json", json=payload)
        return response.json()["smart_collection"]

    def delete_smart_collection(self, collection_id: int | str) -> None:
        self.request("DELETE", f"/smart_collections/{collection_id}.json")


def next_page_info(link_header: str) -> str:
    for part in link_header.split(","):
        if 'rel="next"' not in part:
            continue
        match = re.search(r"[?&]page_info=([^&>]+)", part)
        if match:
            return match.group(1)
    return ""


def sync_collections(client: ShopifyAdmin, specs: list[CollectionSpec], mode: str, sleep_seconds: float) -> pd.DataFrame:
    live = client.live_managed_collections()
    rows = []
    progress = st.progress(0)
    for index, spec in enumerate(specs, start=1):
        existing = live.get(spec.handle)
        try:
            if existing and mode == "create_missing":
                status = "skipped"
                message = "Presente"
                collection_id = existing.get("id")
            elif existing:
                updated = client.update_smart_collection(existing["id"], spec)
                status = "updated"
                message = "Aggiornata"
                collection_id = updated.get("id")
            else:
                created = client.create_smart_collection(spec)
                status = "created"
                message = "Creata"
                collection_id = created.get("id")
        except Exception as exc:
            status = "error"
            message = str(exc)
            collection_id = existing.get("id") if existing else ""
        rows.append({"status": status, "title": spec.title, "handle": spec.handle, "id": collection_id, "message": message})
        progress.progress(index / len(specs))
        time.sleep(sleep_seconds)
    return pd.DataFrame(rows)


def delete_managed_collections(client: ShopifyAdmin, live: dict[str, dict[str, Any]], handles: set[str], sleep_seconds: float) -> pd.DataFrame:
    rows = []
    selected = [item for handle, item in live.items() if handle in handles]
    progress = st.progress(0)
    for index, item in enumerate(selected, start=1):
        try:
            client.delete_smart_collection(item["id"])
            rows.append({"status": "deleted", "title": item.get("title"), "handle": item.get("handle"), "id": item.get("id")})
        except Exception as exc:
            rows.append({"status": "error", "title": item.get("title"), "handle": item.get("handle"), "id": item.get("id"), "message": str(exc)})
        progress.progress(index / max(len(selected), 1))
        time.sleep(sleep_seconds)
    return pd.DataFrame(rows)


def render_status_overview(client: ShopifyAdmin | None, connected: bool) -> dict[str, dict[str, Any]]:
    csv_summary = read_csv_summary(LIVE_CSV)
    live: dict[str, dict[str, Any]] = {}
    products_count = None

    if connected and client:
        with st.spinner("Leggo dati reali da Shopify..."):
            products_count = client.get_products_count()
            live = client.live_managed_collections()

    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.metric("Prodotti Shopify", products_count if products_count is not None else "n/d")
    col_b.metric("Prodotti CSV locale", csv_summary["products"] if csv_summary["exists"] else "assente")
    col_c.metric("Collection gestite live", len(live) if connected else "n/d")
    col_d.metric("Collection previste", len(ALL_COLLECTIONS))
    return live


def render_reload_tab(store_domain: str, token: str, api_version: str, verify_ssl: bool) -> None:
    st.subheader("Reset e ricarica catalogo")
    st.write("Sequenza consigliata: valida CSV pulito, importa prodotti da Shopify Admin, poi sincronizza collection e metafield.")

    summary = read_csv_summary(LIVE_CSV)
    st.dataframe(pd.DataFrame([summary]), use_container_width=True, hide_index=True)

    ssl_arg = [] if verify_ssl else ["--no-verify-ssl"]
    col_1, col_2, col_3 = st.columns(3)
    with col_1:
        if st.button("Completa SEO/tag CSV", use_container_width=True):
            render_command_result(
                run_command(
                    ["tools/enrich_shopify_catalog.py", "--input", str(LIVE_CSV), "--set-active"],
                    store_domain,
                    token,
                    api_version,
                )
            )
    with col_2:
        if st.button("Crea/Verifica metafield", use_container_width=True, disabled=not bool(store_domain and token)):
            render_command_result(run_command(["tools/create_metafields.py", *ssl_arg], store_domain, token, api_version))
    with col_3:
        if st.button("Crea/Verifica metaobject", use_container_width=True, disabled=not bool(store_domain and token)):
            render_command_result(run_command(["tools/create_metaobjects.py", *ssl_arg], store_domain, token, api_version))

    with st.expander("Dopo import prodotti: popola metafield prodotto"):
        st.write("Da usare solo dopo aver ricaricato o verificato i prodotti in Shopify.")
        test_col, full_col = st.columns(2)
        with test_col:
            if st.button("Test 5 prodotti", use_container_width=True, disabled=not bool(store_domain and token)):
                render_command_result(run_command(["tools/populate_metafields.py", "--csv", str(LIVE_CSV), *ssl_arg, "--limit", "5"], store_domain, token, api_version))
        with full_col:
            allow_full = st.checkbox("Confermo batch completo metafield")
            if st.button("Popola tutti", use_container_width=True, disabled=not allow_full or not bool(store_domain and token)):
                render_command_result(run_command(["tools/populate_metafields.py", "--csv", str(LIVE_CSV), *ssl_arg], store_domain, token, api_version))

    st.info(f"CSV import prodotti: {relative_to_base(LIVE_CSV)}")


def render_plan_tab(store_domain: str, token: str, api_version: str) -> None:
    st.subheader("Piano collection V20")
    st.write("Vista operativa: 16 collection mancanti, 8 template editoriali, SEO, esclusioni e audit metafield legacy.")

    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.metric("Collection piano", len(ALL_COLLECTIONS))
    col_b.metric("Batch da creare", len(specs_for_missing_batch()))
    col_c.metric("Template editoriali", len([spec for spec in ALL_COLLECTIONS if spec.template_scope == "bks-editorial-template"]))
    col_d.metric("Escluse template", len(TEMPLATE_EXCLUDED_HANDLES))

    if st.button("Rigenera export piano V20", use_container_width=True):
        render_command_result(run_command(["tools/export_collection_plan.py"], store_domain, token, api_version))

    rows = [
        ("Piano completo CSV", COLLECTION_PLAN_CSV),
        ("Template assignment", TEMPLATE_ASSIGNMENT_CSV),
        ("Template exclusions", TEMPLATE_EXCLUSIONS_CSV),
        ("Audit metafield legacy", LEGACY_AUDIT_CSV),
        ("Prompt immagini", IMAGE_PROMPTS_MD),
    ]
    
    display_rows = []
    for label, path in rows:
        display_rows.append({"file": label, "path": str(path), "exists": path.exists()})
        
    st.dataframe(
        pd.DataFrame(display_rows),
        use_container_width=True,
        hide_index=True,
    )

    if COLLECTION_PLAN_CSV.exists():
        try:
            st.write("Collection plan")
            st.dataframe(pd.read_csv(COLLECTION_PLAN_CSV), use_container_width=True, hide_index=True)
        except Exception:
            st.warning("Impossibile leggere Collection Plan CSV.")

    if TEMPLATE_EXCLUSIONS_CSV.exists():
        try:
            st.write("Collection escluse dai template BKS")
            st.dataframe(pd.read_csv(TEMPLATE_EXCLUSIONS_CSV), use_container_width=True, hide_index=True)
        except Exception:
            st.warning("Impossibile leggere Template Exclusions CSV.")

    st.write("Audit metafield legacy da eliminare in Shopify Admin")
    st.dataframe(pd.DataFrame(LEGACY_COLLECTION_METAFIELDS), use_container_width=True, hide_index=True)


def render_collection_tab(client: ShopifyAdmin | None, live: dict[str, dict[str, Any]], sleep_seconds: float) -> None:
    st.subheader("Collection live e sync")
    st.caption(
        "Fonte V20: 25 collection operative. Il batch da 16 include solo tipo prodotto + Swimwear/Outerwear; "
        "New Arrivals resta su Default collection ed è deselezionata per evitare sync accidentali."
    )
    groups = st.multiselect(
        "Gruppi",
        ["Editoriali", "Tipo prodotto", "Navigazione"],
        default=["Editoriali", "Tipo prodotto", "Navigazione"],
    )
    filtered = tuple(spec for spec in ALL_COLLECTIONS if spec.group in groups)
    table_df = collections_dataframe(filtered, live)
    edited = st.data_editor(
        table_df,
        hide_index=True,
        use_container_width=True,
        disabled=[
            "group",
            "title",
            "handle",
            "live_status",
            "live_products",
            "live_id",
            "missing_batch_16",
            "template",
            "template_scope",
            "live_template",
            "seo_chars",
            "seo_live",
            "rule",
        ],
        column_config={"sync": st.column_config.CheckboxColumn("Sync", default=True)},
    )
    selected_handles = set(edited.loc[edited["sync"], "handle"].tolist())
    selected = [spec for spec in filtered if spec.handle in selected_handles]
    missing_batch = [spec for spec in specs_for_missing_batch() if spec.handle in selected_handles]

    preview = st.selectbox("Payload preview", [spec.handle for spec in filtered], format_func=lambda h: next(s.title for s in filtered if s.handle == h))
    st.json(collection_to_payload(next(spec for spec in filtered if spec.handle == preview)))

    col_1, col_2, col_3 = st.columns(3)
    with col_1:
        if st.button(f"Crea solo batch 16 ({len(missing_batch)})", type="primary", use_container_width=True, disabled=client is None):
            if client is not None:
                st.dataframe(sync_collections(client, missing_batch, "create_missing", sleep_seconds), use_container_width=True, hide_index=True)
    with col_2:
        if st.button(f"Crea mancanti selezionate ({len(selected)})", use_container_width=True, disabled=client is None):
            if client is not None:
                st.dataframe(sync_collections(client, selected, "create_missing", sleep_seconds), use_container_width=True, hide_index=True)
    with col_3:
        allow_update = st.checkbox("Aggiorna anche collection esistenti")
        if st.button(f"Sync completo ({len(selected)})", use_container_width=True, disabled=client is None or not allow_update):
            if client is not None:
                st.dataframe(sync_collections(client, selected, "upsert", sleep_seconds), use_container_width=True, hide_index=True)


def render_reset_tab(client: ShopifyAdmin | None, live: dict[str, dict[str, Any]], sleep_seconds: float) -> None:
    st.subheader("Reset collection gestite")
    st.warning("Questa sezione elimina solo le smart collection gestite dal cruscotto. Non elimina prodotti.")
    if not live:
        st.info("Nessuna collection gestita trovata live, oppure connessione non attiva.")
        return
    frame = pd.DataFrame(
        [{"delete": False, "title": v.get("title"), "handle": k, "id": v.get("id"), "products": v.get("products_count")} for k, v in sorted(live.items())]
    )
    edited = st.data_editor(
        frame,
        hide_index=True,
        use_container_width=True,
        disabled=["title", "handle", "id", "products"],
        column_config={"delete": st.column_config.CheckboxColumn("Elimina", default=False)},
    )
    handles = set(edited.loc[edited["delete"], "handle"].tolist())
    confirmation = st.text_input("Scrivi RESET BKS COLLECTIONS per abilitare l'eliminazione")
    if st.button(f"Elimina collection selezionate ({len(handles)})", type="primary", disabled=client is None or confirmation != "RESET BKS COLLECTIONS" or not handles):
        if client is not None:
            st.dataframe(delete_managed_collections(client, live, handles, sleep_seconds), use_container_width=True, hide_index=True)


def render_images_tab(store_domain: str, token: str, api_version: str) -> None:
    st.subheader("Progettazione immagini AI")
    st.caption("Brief collection, prompt base modificabile e generazione OpenAI opzionale. Usare immagini trasparenti per prodotti/cutout.")

    if st.button("Rigenera brief immagini collection", use_container_width=True):
        render_command_result(run_command(["tools/collection_image_program.py", "--mode", "all"], store_domain, token, api_version))

    curated = IMAGE_PROGRAM_DIR / "curated" / "curated_collection_image_plan.json"
    if curated.exists():
        try:
            plan = json.loads(curated.read_text(encoding="utf-8"))
            st.dataframe(
                pd.DataFrame(
                    [
                        {
                            "collection": item.get("collection"),
                            "mode": item.get("mode"),
                            "prompt_file": item.get("prompt_file"),
                            "products": len(item.get("products", [])),
                        }
                        for item in plan
                    ]
                ),
                use_container_width=True,
                hide_index=True,
            )
        except Exception:
            st.info("Brief curatoriale presente, ma non leggibile come JSON.")

    spec_by_label = {f"{spec.title} / {spec.handle}": spec for spec in ALL_COLLECTIONS}
    label = st.selectbox("Asset da progettare", list(spec_by_label.keys()))
    spec = spec_by_label[label]
    mode = st.selectbox(
        "Tipo immagine",
        ["Collection hero 4:5", "Product cutout transparent", "Editorial banner", "Social square"],
    )
    default_prompt = load_default_prompt(spec, mode)
    prompt = st.text_area("Prompt modificabile", value=default_prompt, height=260)

    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        model = st.selectbox("OpenAI model", ["gpt-image-1.5", "gpt-image-1", "gpt-image-1-mini"], index=0)
    with col_b:
        size = st.selectbox("Formato", ["1024x1536", "1024x1024", "1536x1024"], index=0)
    with col_c:
        quality = st.selectbox("Qualità", ["medium", "low", "high", "auto"], index=0)
    with col_d:
        background_default = 2 if mode == "Product cutout transparent" else 1
        background = st.selectbox("Sfondo", ["auto", "opaque", "transparent"], index=background_default)
    if mode == "Product cutout transparent" or background == "transparent":
        st.info("Per prodotti e cutout mantieni sfondo trasparente: migliora uniformita' su collection, banner e schede prodotto.")

    default_asset_name = safe_file_stem(f"{spec.handle}-{mode}")
    asset_name = st.text_input("Nome asset", value=default_asset_name)
    asset_stem = safe_file_stem(asset_name, default_asset_name)
    if asset_stem != asset_name:
        st.caption(f"Nome file normalizzato: `{asset_stem}`")
    OPENAI_PROMPT_DIR.mkdir(parents=True, exist_ok=True)
    prompt_path = OPENAI_PROMPT_DIR / f"{asset_stem}.txt"

    col_save, col_generate = st.columns(2)
    with col_save:
        if st.button("Salva prompt", use_container_width=True):
            prompt_path.write_text(prompt.strip() + "\n", encoding="utf-8")
            st.success(f"Prompt salvato: {prompt_path}")
    with col_generate:
        openai_key = get_env_value("OPENAI_API_KEY")
        confirm_cost = st.checkbox("Confermo generazione immagine OpenAI")
        bypass_openai_ssl = st.checkbox("Bypass SSL OpenAI", help="Usare solo se Python locale rifiuta il certificato OpenAI.")
        st.caption("Il prompt viene sempre salvato prima della generazione. Se compare billing_hard_limit_reached, il blocco e' sul budget OpenAI, non sul codice.")
        if st.button("Genera immagine", type="primary", use_container_width=True, disabled=not openai_key or not confirm_cost):
            prompt_path.write_text(prompt.strip() + "\n", encoding="utf-8")
            openai_args = [
                "tools/generate_openai_image.py",
                "--prompt-file",
                str(prompt_path),
                "--name",
                asset_stem,
                "--model",
                model,
                "--size",
                size,
                "--quality",
                quality,
                "--background",
                background,
                "--format",
                "png",
            ]
            if bypass_openai_ssl:
                openai_args.append("--no-verify-ssl")
            result = run_command(
                openai_args,
                store_domain,
                token,
                api_version,
            )
            render_command_result(result)
        if not openai_key:
            st.warning("OPENAI_API_KEY non presente: puoi salvare e rifinire i prompt, ma non generare da qui.")

    recent = sorted(OPENAI_IMAGE_DIR.glob("*.png"), key=lambda path: path.stat().st_mtime, reverse=True)[:6]
    if recent:
        st.write("Ultime immagini generate")
        cols = st.columns(min(len(recent), 3))
        for index, image_path in enumerate(recent):
            with cols[index % len(cols)]:
                st.image(str(image_path), caption=image_path.name, use_container_width=True)


def render_analytics_tab(store_domain: str, token: str, api_version: str) -> None:
    st.subheader("Analytics, Merchant Center e marketing efficiency")
    st.caption("Cruscotto per leggere salute del progetto, feed, tracciamento e target dei prossimi batch.")

    csv_summary = read_csv_summary(LIVE_CSV)
    merchant_total = MERCHANT_CENTER["local_inventory_missing"] + MERCHANT_CENTER["product_page_unavailable"] + 1
    tracking_score = 100 if ANALYTICS_SNAPSHOT["gtm_container"] else 0
    catalog_score = 100 if csv_summary.get("active", 0) else 0
    merchant_score = max(0, round(100 - (MERCHANT_CENTER["product_page_unavailable"] / max(merchant_total, 1) * 100)))
    efficiency_score = round((tracking_score * 0.35) + (catalog_score * 0.35) + (merchant_score * 0.30))

    kpi_cols = st.columns(5)
    kpi_cols[0].metric("Efficiency score", f"{efficiency_score}/100")
    kpi_cols[1].metric("Utenti attivi 7g", ANALYTICS_SNAPSHOT["active_users"])
    kpi_cols[2].metric("Sessioni 7g", ANALYTICS_SNAPSHOT["sessions"])
    kpi_cols[3].metric("Prodotti attivi CSV", csv_summary.get("active", "n/d"))
    kpi_cols[4].metric("GTM target", ANALYTICS_SNAPSHOT["gtm_container"])

    kpi_tab, forecast_tab, merchant_tab, audit_tab = st.tabs(["KPI", "Target futuri", "Merchant", "Audit"])

    with kpi_tab:
        dates = pd.date_range(end=pd.Timestamp.today().normalize(), periods=7)
        sessions = ANALYTICS_SNAPSHOT["sessions"]
        users = ANALYTICS_SNAPSHOT["active_users"]
        views = ANALYTICS_SNAPSHOT["views"]
        trend = pd.DataFrame(
            {
                "data": dates,
                "utenti": [max(1, round(users * factor)) for factor in [0.09, 0.11, 0.10, 0.13, 0.15, 0.19, 0.23]],
                "sessioni": [max(1, round(sessions * factor)) for factor in [0.08, 0.10, 0.12, 0.13, 0.14, 0.19, 0.24]],
                "view": [max(1, round(views * factor)) for factor in [0.07, 0.10, 0.12, 0.14, 0.15, 0.19, 0.23]],
            }
        ).set_index("data")
        st.line_chart(trend)

        source_mix = pd.DataFrame(
            [
                {"canale": "Organic / SEO", "peso": 42, "azione": "Collection SEO + sitemap pulita"},
                {"canale": "Google Shopping", "peso": 28, "azione": "Feed con custom label e prodotti attivi"},
                {"canale": "Social prospecting", "peso": 20, "azione": "Creative test per collezione"},
                {"canale": "Retargeting / Email", "peso": 10, "azione": "Carrelli, view content, micro-lista"},
            ]
        )
        st.bar_chart(source_mix.set_index("canale")["peso"])
        st.dataframe(source_mix, use_container_width=True, hide_index=True)

    with forecast_tab:
        st.write("Scenario 30 giorni")
        control_cols = st.columns(3)
        target_sessions = control_cols[0].number_input("Sessioni target", min_value=100, max_value=200000, value=2500, step=100)
        conversion_rate = control_cols[1].slider("Conversion rate", 0.1, 8.0, 1.2, 0.1) / 100
        average_order = control_cols[2].number_input("AOV medio EUR", min_value=20.0, max_value=500.0, value=72.0, step=1.0)

        control_cols_2 = st.columns(3)
        gross_margin = control_cols_2[0].slider("Margine lordo", 10, 85, 42, 1) / 100
        ad_budget = control_cols_2[1].number_input("Budget ads EUR", min_value=0.0, max_value=100000.0, value=750.0, step=50.0)
        cpc = control_cols_2[2].number_input("CPC atteso EUR", min_value=0.05, max_value=10.0, value=0.45, step=0.05)

        expected_orders = target_sessions * conversion_rate
        expected_revenue = expected_orders * average_order
        gross_profit = expected_revenue * gross_margin
        paid_clicks = ad_budget / cpc if cpc else 0
        paid_orders = paid_clicks * conversion_rate
        paid_revenue = paid_orders * average_order
        cpa = ad_budget / paid_orders if paid_orders else 0
        roas = paid_revenue / ad_budget if ad_budget else 0
        net_after_ads = gross_profit - ad_budget
        break_even_roas = 1 / gross_margin if gross_margin else 0

        result_cols = st.columns(5)
        result_cols[0].metric("Ordini attesi", f"{expected_orders:.1f}")
        result_cols[1].metric("Ricavi attesi", f"EUR {expected_revenue:,.0f}".replace(",", "."))
        result_cols[2].metric("CPA paid", f"EUR {cpa:,.2f}".replace(",", "."))
        result_cols[3].metric("ROAS paid", f"{roas:.2f}x", delta=f"BE {break_even_roas:.2f}x")
        result_cols[4].metric("Utile dopo ads", f"EUR {net_after_ads:,.0f}".replace(",", "."))

        funnel = pd.DataFrame(
            [
                {"step": "Sessioni", "volume": target_sessions},
                {"step": "Product views", "volume": round(target_sessions * 0.62)},
                {"step": "Add to cart", "volume": round(expected_orders * 2.8)},
                {"step": "Checkout", "volume": round(expected_orders * 1.45)},
                {"step": "Ordini", "volume": round(expected_orders, 1)},
            ]
        )
        st.bar_chart(funnel.set_index("step"))

        target_table = pd.DataFrame(
            [
                {"target": "Sneakers / streetwear", "priorita": "Alta", "KPI": "CTR collection + add_to_cart", "test": "Hero visual + Google Shopping label sneakers"},
                {"target": "Outerwear", "priorita": "Alta", "KPI": "View content + AOV", "test": "Puffer/Windbreaker editorial cards"},
                {"target": "Swimwear resort", "priorita": "Media", "KPI": "CTR stagionale + CVR", "test": "Riviera/Token summer creative"},
                {"target": "Bags / travel", "priorita": "Media", "KPI": "ROAS + bundle rate", "test": "Travel bag + backpack pairing"},
                {"target": "Retargeting caldo", "priorita": "Alta", "KPI": "CPA < margine per ordine", "test": "View product 7/14 giorni"},
            ]
        )
        st.dataframe(target_table, use_container_width=True, hide_index=True)

    with merchant_tab:
        issue_cols = st.columns(3)
        issue_cols[0].metric("Merchant account", MERCHANT_CENTER["account_id"])
        issue_cols[1].metric("Inventario locale mancante", f"{MERCHANT_CENTER['local_inventory_missing']:,}".replace(",", "."))
        issue_cols[2].metric("Pagine prodotto non disponibili", f"{MERCHANT_CENTER['product_page_unavailable']:,}".replace(",", "."))
        st.info(MERCHANT_CENTER["note"])
        merchant_frame = pd.DataFrame(
            [
                {"problema": "Dati inventario locale mancanti", "prodotti": MERCHANT_CENTER["local_inventory_missing"], "impatto": "Feed noise", "azione": "Disattiva local inventory se non usato"},
                {"problema": "Pagina prodotto non disponibile", "prodotti": MERCHANT_CENTER["product_page_unavailable"], "impatto": "Shopping / SEO residuo", "azione": "Aggiorna feed, sitemap e richiedi ricontrollo"},
                {"problema": "Taglia mancante", "prodotti": 1, "impatto": "Disapprovazione puntuale", "azione": "Controlla variante size sui prodotti attivi"},
            ]
        )
        st.bar_chart(merchant_frame.set_index("problema")["prodotti"])
        st.dataframe(merchant_frame, use_container_width=True, hide_index=True)

    with audit_tab:
        controls = pd.DataFrame(
            [
                {"area": "GA4", "controllo": "purchase, add_to_cart, view_item", "target": "Eventi con value/currency", "stato": "da verificare live"},
                {"area": "GTM", "controllo": "Un solo container", "target": ANALYTICS_SNAPSHOT["gtm_container"], "stato": "tema pronto"},
                {"area": "UTM", "controllo": "source / medium / campaign / content", "target": "Naming per collezione e creative", "stato": "standardizzare"},
                {"area": "Feed", "controllo": "custom_label_0/1", "target": "no-gtin + tipo prodotto", "stato": "CSV aggiornato"},
                {"area": "SEO", "controllo": "Title <= 70, Description <= 160", "target": "0 mancanti", "stato": "CSV aggiornato"},
                {"area": "Sitemap", "controllo": "Solo URL attivi", "target": "No prodotti legacy", "stato": "post-publish"},
            ]
        )
        st.dataframe(controls, use_container_width=True, hide_index=True)

        if st.button("Esegui audit pubblico link/GTM", use_container_width=True):
            render_command_result(run_command(["tools/audit_live_site.py"], store_domain, token, api_version))

        live_pages = read_live_pages()
        if live_pages.empty:
            st.warning("Audit live non ancora disponibile. Esegui il controllo dopo aver caricato/pubblicato il tema.")
        else:
            status_frame = live_pages.copy()
            status_frame["ok"] = status_frame["status"].apply(lambda value: "ok" if int(value) in range(200, 400) else "errore")
            st.write("Risultato ultimo audit live")
            st.dataframe(
                status_frame[["url", "status", "title", "expected_gtm", "legacy_gtm", "welcome_placeholder", "error"]],
                use_container_width=True,
                hide_index=True,
            )
            status_counts = status_frame["ok"].value_counts().rename_axis("stato").reset_index(name="pagine")
            st.bar_chart(status_counts.set_index("stato"))


def render_logs_tab() -> None:
    st.subheader("Log operativi")
    rows = []
    log_files = [
        ("Piano collection V20", COLLECTION_PLAN_CSV),
        ("Template assignment V20", TEMPLATE_ASSIGNMENT_CSV),
        ("Template exclusions V20", TEMPLATE_EXCLUSIONS_CSV),
        ("Audit metafield collection V20", LEGACY_AUDIT_CSV),
        ("Prompt immagini V20", IMAGE_PROMPTS_MD),
        ("Fix CSV", PHASE1_REPORT),
        ("Metafields", METAFIELDS_LOG),
        ("Metaobjects", METAOBJECTS_LOG),
        ("Populate metafields", POPULATE_LOG),
    ]
    
    for label, path in log_files:
        counts = log_counts(path)
        counts_str = json.dumps(counts) if counts else "-"
        
        rows.append({
            "fase": label, 
            "path": str(path), 
            "exists": path.exists(), 
            "counts": counts_str
        })
        
    df_logs = pd.DataFrame(rows)
    st.dataframe(df_logs, use_container_width=True, hide_index=True)


def main() -> None:
    load_local_env()
    st.set_page_config(page_title="BKS Automation Console", page_icon="BKS", layout="wide")
    st.title("BKS AUTOMATION CONSOLE")
    st.caption("Automazione Shopify, progettazione immagini, monitoraggio Analytics e controllo Merchant Center in un unico flusso.")

    default_store = get_env_value("SHOPIFY_MYSHOPIFY_DOMAIN", "SHOPIFY_STORE", "SHOP")
    default_token = get_env_value("SHOPIFY_ADMIN_TOKEN", "SHOPIFY_TOKEN", "TOKEN")
    default_api_version = get_env_value("SHOPIFY_API_VERSION", default=DEFAULT_API_VERSION)

    with st.sidebar:
        st.header("Shopify Admin API")
        store_domain = st.text_input("Store domain", value=default_store)
        api_version = st.text_input("API version", value=default_api_version)
        token = st.text_input("Admin access token", value=default_token, type="password")
        verify_ssl = st.checkbox("Verifica certificato SSL", value=False)
        sleep_seconds = st.slider("Delay richieste", 0.1, 2.0, 0.4, 0.1)
        st.caption(f"Token: {mask_token(token)}")
        if not verify_ssl:
            st.caption("SSL verification disattivata.")

    client = None
    connected = bool(store_domain and token)
    if connected:
        client = ShopifyAdmin(store_domain, token, api_version, verify_ssl=verify_ssl)

    live = render_status_overview(client, connected)
    with st.expander("Mappa fasi operative", expanded=True):
        render_phase_map()
    st.divider()

    tabs = st.tabs(["01 Asset/CSV", "03 Piano", "03 Collection", "04 Reset", "07 Immagini AI", "08 Analytics", "10 Log"])
    with tabs[0]:
        render_reload_tab(store_domain, token, api_version, verify_ssl)
    with tabs[1]:
        render_plan_tab(store_domain, token, api_version)
    with tabs[2]:
        render_collection_tab(client, live, sleep_seconds)
    with tabs[3]:
        render_reset_tab(client, live, sleep_seconds)
    with tabs[4]:
        render_images_tab(store_domain, token, api_version)
    with tabs[5]:
        render_analytics_tab(store_domain, token, api_version)
    with tabs[6]:
        render_logs_tab()


if __name__ == "__main__":
    main()