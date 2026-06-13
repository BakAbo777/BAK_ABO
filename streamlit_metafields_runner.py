#!/usr/bin/env python3
"""
BKS Shopify Metafield Runner

Run:
  streamlit run streamlit_metafields_runner.py
"""

from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import requests
import streamlit as st  # type: ignore


BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"
OUTPUT_DIR = BASE_DIR / "output"
DEFAULT_SHOP = "bakabo.myshopify.com"
DEFAULT_API_VERSION = "2025-01"


@dataclass(frozen=True)
class ScriptStep:
    key: str
    title: str
    script: str
    scope_note: str
    log_path: Path
    help_text: str


STEPS: tuple[ScriptStep, ...] = (
    ScriptStep(
        key="metafields",
        title="1. Crea / verifica metafield definitions",
        script="tools/create_metafields.py",
        scope_note="write_products + read_products",
        log_path=OUTPUT_DIR / "metafield_definitions_log.csv",
        help_text="Crea o verifica i campi prodotto essenziali: bks.collection, bks.design, bks.series, bks.drop.",
    ),
    ScriptStep(
        key="metaobjects",
        title="2. Crea / verifica metaobject BKS collection",
        script="tools/create_metaobjects.py",
        scope_note="write_metaobject_definitions + write_metaobjects",
        log_path=OUTPUT_DIR / "metaobjects_log.csv",
        help_text="Crea la definizione metaobject bks_collection e le 8 entry editoriali BKS.",
    ),
    ScriptStep(
        key="populate",
        title="3. Popola metafield prodotti",
        script="tools/populate_metafields.py",
        scope_note="write_products + read_products",
        log_path=OUTPUT_DIR / "populate_metafields_log.csv",
        help_text="Legge BKS_COLLEZIONE_26_v6.csv e aggiorna i metafield sui prodotti Shopify.",
    ),
)


def load_local_env(path: Path = ENV_PATH) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def env_value(*names: str, default: str = "") -> str:
    for name in names:
        value = os.environ.get(name, "").strip()
        if value:
            return value
    return default


def mask_token(token: str) -> str:
    return f"{token[:6]}...{token[-4:]}" if len(token) >= 12 else "<non impostato>"


def configured_myshopify_domain() -> str:
    return env_value("SHOPIFY_MYSHOPIFY_DOMAIN", "SHOP", default=DEFAULT_SHOP)


def admin_domain_for(shop: str) -> tuple[str, str]:
    domain = shop.replace("https://", "").replace("http://", "").strip("/")
    if domain.endswith(".myshopify.com"):
        return domain, ""

    configured = configured_myshopify_domain()
    if configured.endswith(".myshopify.com"):
        return configured, f"`{domain}` e un dominio pubblico. Uso il dominio Admin API `{configured}`."

    return domain, "Per Admin API Shopify usa il dominio `nome-store.myshopify.com`, non il dominio pubblico."


def build_env(shop: str, token: str, api_version: str) -> dict[str, str]:
    admin_shop, _ = admin_domain_for(shop)
    env = os.environ.copy()
    env["SHOP"] = admin_shop
    env["TOKEN"] = token
    env["SHOPIFY_STORE"] = admin_shop
    env["SHOPIFY_MYSHOPIFY_DOMAIN"] = admin_shop
    env["SHOPIFY_TOKEN"] = token
    env["SHOPIFY_ADMIN_TOKEN"] = token
    env["SHOPIFY_API_VERSION"] = api_version
    return env


def run_command(args: list[str], shop: str, token: str, api_version: str, timeout: int = 3600) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=BASE_DIR,
        env=build_env(shop, token, api_version),
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )


def run_pip_install() -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "pip", "install", "requests"],
        cwd=BASE_DIR,
        text=True,
        capture_output=True,
        timeout=900,
        check=False,
    )


def render_result(result: subprocess.CompletedProcess[str]) -> None:
    if result.returncode == 0:
        st.success("Comando completato.")
    else:
        st.error(f"Comando fallito con exit code {result.returncode}.")
    output = "\n".join(part for part in (result.stdout, result.stderr) if part.strip())
    if output:
        if "WinError 10051" in output or "network is unreachable" in output.lower() or "rete non raggiungibile" in output.lower():
            st.warning("La rete e caduta durante la chiamata Shopify. Rilancia lo script 3 con `--resume` oppure usa `Start after handle`.")
        if "404 Client Error" in output or "Not Found for url" in output:
            st.warning("404 Shopify Admin API: controlla che SHOP sia un dominio `*.myshopify.com`, non il dominio pubblico del sito.")
        st.code(output[-10000:], language="text")


def log_summary(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"log": path.name, "status": "non ancora creato", "righe": 0}
    try:
        frame = pd.read_csv(path)
    except Exception as exc:
        return {"log": path.name, "status": f"non leggibile: {exc}", "righe": 0}
    summary: dict[str, Any] = {"log": path.name, "status": "presente", "righe": len(frame)}
    if "status" in frame.columns:
        counts = frame["status"].fillna("").astype(str).value_counts().to_dict()
        summary.update({f"status_{key}": value for key, value in counts.items()})
    return summary


def test_shopify_connection(shop: str, token: str, api_version: str) -> tuple[bool, str]:
    domain, warning = admin_domain_for(shop)
    url = f"https://{domain}/admin/api/{api_version}/shop.json"
    try:
        response = requests.get(
            url,
            headers={"X-Shopify-Access-Token": token, "Content-Type": "application/json"},
            timeout=30,
        )
        if response.status_code == 200:
            name = response.json().get("shop", {}).get("name", domain)
            prefix = f"{warning}\n" if warning else ""
            return True, f"{prefix}Connessione riuscita: {name}"
        return False, f"{warning}\nHTTP {response.status_code}: {response.text[:500]}".strip()
    except Exception as exc:
        return False, f"{warning}\n{exc}".strip()


def command_examples(shop: str) -> tuple[str, str]:
    windows = f"""pip install requests

set SHOP={shop}
set TOKEN=<shopify-admin-token>

python tools\\create_metafields.py
python tools\\create_metaobjects.py
python tools\\populate_metafields.py"""
    unix = f"""pip install requests

SHOP={shop} TOKEN=<shopify-admin-token> python3 tools/create_metafields.py
SHOP={shop} TOKEN=<shopify-admin-token> python3 tools/create_metaobjects.py
SHOP={shop} TOKEN=<shopify-admin-token> python3 tools/populate_metafields.py"""
    return windows, unix


def render_scope_checklist() -> None:
    st.markdown("#### Scope richiesti nell'app Shopify")
    scope_rows = [
        {"Scope": "write_products", "Motivo": "Script 1 + 3: definizioni/metafield prodotto"},
        {"Scope": "read_products", "Motivo": "Script 3: lettura prodotti per handle"},
        {"Scope": "write_metaobject_definitions", "Motivo": "Script 2: definizione bks_collection"},
        {"Scope": "write_metaobjects", "Motivo": "Script 2: entry metaobject editoriali"},
    ]
    st.dataframe(pd.DataFrame(scope_rows), use_container_width=True, hide_index=True)
    st.caption("Shopify Admin -> Settings -> Apps -> Develop apps -> Create app -> Configure Admin API scopes.")


def render_step(step: ScriptStep, shop: str, token: str, api_version: str, verify_ssl: bool) -> None:
    with st.container(border=True):
        st.markdown(f"#### {step.title}")
        st.write(step.help_text)
        st.caption(f"Scope: {step.scope_note}")
        args = [step.script]
        if not verify_ssl:
            args.append("--no-verify-ssl")
        if step.key == "populate":
            limit = st.number_input("Limite test prodotti", min_value=0, max_value=190, value=5, step=1)
            resume = st.checkbox("Riprendi da log esistente", value=True, help="Salta handle gia presenti nel log come updated/skipped/missing.")
            start_after = st.text_input(
                "Start after handle",
                value="",
                placeholder="folklore-shoal-windbreaker",
                help="Utile dopo una caduta rete: riparte dal prodotto successivo a questo handle.",
            ).strip()
            test_args = [step.script]
            if not verify_ssl:
                test_args.append("--no-verify-ssl")
            if resume:
                test_args.append("--resume")
            if start_after:
                test_args.extend(["--start-after", start_after])
            if limit:
                test_args.extend(["--limit", str(limit)])
            args = [step.script]
            if not verify_ssl:
                args.append("--no-verify-ssl")
            if resume:
                args.append("--resume")
            if start_after:
                args.extend(["--start-after", start_after])
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("Test populate", key=f"{step.key}_test", use_container_width=True, disabled=not bool(shop and token)):
                    render_result(run_command(test_args, shop, token, api_version))
            with col_b:
                confirm = st.checkbox("Confermo populate completo", key="confirm_populate")
                if st.button("Popola tutti", key=f"{step.key}_full", use_container_width=True, disabled=not confirm or not bool(shop and token)):
                    render_result(run_command(args, shop, token, api_version))
        else:
            if st.button(f"Esegui {step.script}", key=step.key, use_container_width=True, disabled=not bool(shop and token)):
                render_result(run_command(args, shop, token, api_version))


def main() -> None:
    load_local_env()
    st.set_page_config(page_title="BKS 03 - Metafields Runner", page_icon="BKS", layout="wide")

    st.title("BKS 03 - METAFIELDS RUNNER")
    st.caption("Interfaccia locale per installare/verificare requests e lanciare i tre script Shopify in sequenza controllata.")

    with st.sidebar:
        st.header("Connessione")
        shop = st.text_input(
            "SHOP",
            value=env_value("SHOPIFY_MYSHOPIFY_DOMAIN", "SHOP", "SHOPIFY_STORE", default=DEFAULT_SHOP),
        )
        admin_shop, shop_warning = admin_domain_for(shop)
        if shop_warning:
            st.warning(shop_warning)
        st.caption(f"Admin API domain: `{admin_shop}`")
        token = st.text_input(
            "TOKEN",
            value=env_value("TOKEN", "SHOPIFY_TOKEN", "SHOPIFY_ADMIN_TOKEN"),
            type="password",
            help="Il token viene passato solo ai processi avviati da questa sessione.",
        )
        api_version = st.text_input("API version", value=env_value("SHOPIFY_API_VERSION", default=DEFAULT_API_VERSION))
        verify_ssl = st.checkbox("Verifica SSL", value=True)
        st.caption(f"Token: {mask_token(token)}")

        if st.button("Test connessione Shopify", use_container_width=True, disabled=not bool(shop and token)):
            ok, message = test_shopify_connection(shop, token, api_version)
            if ok:
                st.success(message)
            else:
                st.error(message)

    tab_run, tab_sequence, tab_requirements, tab_logs, tab_commands = st.tabs(
        ["Esecuzione", "Sequenza completa", "Requisiti token", "Log", "Comandi"]
    )

    with tab_run:
        col_req, col_status = st.columns([1, 2])
        with col_req:
            st.markdown("#### Dipendenza")
            st.write("Verifica/installazione del pacchetto richiesto dagli script.")
            if st.button("pip install requests", use_container_width=True):
                render_result(run_pip_install())
        with col_status:
            st.markdown("#### Stato")
            st.write(f"Shop: `{shop}`")
            st.write(f"Admin API: `{admin_shop}`")
            st.write(f"API: `{api_version}`")
            st.write(f"Python: `{sys.executable}`")

        for step in STEPS:
            render_step(step, shop, token, api_version, verify_ssl)

    with tab_sequence:
        st.markdown("#### Esecuzione consigliata")
        st.write("Ordine: metafield definitions, metaobject definitions, test populate, populate completo.")
        test_limit = st.number_input("Limite test prima del batch completo", min_value=1, max_value=190, value=5, step=1)
        run_full = st.checkbox("Dopo il test, esegui anche populate completo")
        confirm_sequence = st.text_input("Scrivi RUN BKS per avviare la sequenza")
        if st.button("Avvia sequenza", type="primary", use_container_width=True, disabled=confirm_sequence != "RUN BKS" or not bool(shop and token)):
            commands = [
                ["tools/create_metafields.py"],
                ["tools/create_metaobjects.py"],
                ["tools/populate_metafields.py", "--resume", "--limit", str(test_limit)],
            ]
            if run_full:
                commands.append(["tools/populate_metafields.py", "--resume"])
            for command in commands:
                if not verify_ssl:
                    command.append("--no-verify-ssl")
                st.markdown(f"**Eseguo:** `python {' '.join(command)}`")
                result = run_command(command, shop, token, api_version)
                render_result(result)
                if result.returncode != 0:
                    st.stop()

    with tab_requirements:
        render_scope_checklist()
        st.warning("Non incollare mai un token reale in chat o in documenti condivisi. Inseriscilo solo nel campo password dell'interfaccia o nelle variabili ambiente locali.")

    with tab_logs:
        st.markdown("#### Log generati")
        st.dataframe(pd.DataFrame([log_summary(step.log_path) for step in STEPS]), use_container_width=True, hide_index=True)
        selected = st.selectbox("Apri log", [step.log_path for step in STEPS], format_func=lambda path: path.name)
        if selected.exists():
            st.dataframe(pd.read_csv(selected), use_container_width=True)
        else:
            st.info("Log non ancora generato.")

    with tab_commands:
        windows, unix = command_examples(admin_shop or DEFAULT_SHOP)
        st.markdown("#### Windows")
        st.code(windows, language="bat")
        st.markdown("#### Mac / Linux")
        st.code(unix, language="bash")


if __name__ == "__main__":
    main()
