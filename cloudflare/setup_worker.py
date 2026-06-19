"""
BKS Cloudflare Worker Setup
============================
Questo script:
  1. Crea il KV namespace BKS_AGENT_KV
  2. Imposta i 4 secrets del Worker (letti da .env)
  3. Aggiorna wrangler.toml con il KV namespace ID reale
  4. Fa il deploy del Worker con il binding KV attivo

Eseguire una sola volta dopo aver creato un Cloudflare API Token con permessi:
  - Account > Workers Scripts > Edit
  - Account > Workers KV Storage > Edit

Come creare il token:
  1. Vai su https://dash.cloudflare.com/profile/api-tokens
  2. "Create Token" > "Edit Cloudflare Workers" template
  3. Copia il token e incollalo qui sotto oppure impostalo nella variabile d'ambiente:
     set CLOUDFLARE_API_TOKEN=il_tuo_token

Usage:
  python cloudflare/setup_worker.py --token TUO_CF_API_TOKEN
  oppure
  set CLOUDFLARE_API_TOKEN=il_tuo_token && python cloudflare/setup_worker.py
"""

import os
import sys
import json
import argparse
import warnings
import requests
warnings.filterwarnings("ignore", message="Unverified HTTPS request")

# ── Costanti Worker ──────────────────────────────────────────────────────────
ACCOUNT_ID  = "e796d289f744035eee2641e853d8a5af"
SCRIPT_NAME = "bks-agent"
KV_NAME     = "BKS_AGENT_KV"
ENV_PATH    = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
TOML_PATH   = os.path.join(os.path.dirname(__file__), "wrangler.toml")
JS_PATH     = os.path.join(os.path.dirname(__file__), "bks-ai-worker.js")


def load_env(path):
    env = {}
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def cf_headers(token):
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def step_create_kv(token):
    print("\n[1/4] Creazione KV namespace BKS_AGENT_KV...")
    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/storage/kv/namespaces"
    r = requests.post(url, headers=cf_headers(token), json={"title": KV_NAME}, verify=False)
    data = r.json()
    if not data.get("success"):
        errors = data.get("errors", [])
        # Already exists?
        if any("already exists" in str(e) for e in errors):
            print("  KV namespace esiste già — recupero ID...")
            r2 = requests.get(url, headers=cf_headers(token), verify=False)
            namespaces = r2.json().get("result", [])
            for ns in namespaces:
                if ns.get("title") == KV_NAME:
                    kv_id = ns["id"]
                    print(f"  KV ID trovato: {kv_id}")
                    return kv_id
        print(f"  ERRORE: {errors}")
        sys.exit(1)
    kv_id = data["result"]["id"]
    print(f"  KV namespace creato: {kv_id}")
    return kv_id


def step_set_secrets(token, env_vars):
    print("\n[2/4] Impostazione secrets Worker...")
    secrets = {
        "OPENAI_API_KEY":      env_vars.get("OPENAI_API_KEY", ""),
        "SHOPIFY_DOMAIN":      env_vars.get("SHOPIFY_MYSHOPIFY_DOMAIN", ""),
        "SHOPIFY_TOKEN":       env_vars.get("SHOPIFY_ADMIN_TOKEN", ""),
        "SHOPIFY_API_VERSION": env_vars.get("SHOPIFY_API_VERSION", "2025-01"),
    }
    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/workers/scripts/{SCRIPT_NAME}/secrets"
    ok, err = 0, 0
    for name, value in secrets.items():
        if not value:
            print(f"  SKIP {name} — valore mancante in .env")
            continue
        r = requests.put(url, headers=cf_headers(token),
                         json={"name": name, "text": value, "type": "secret_text"}, verify=False)
        data = r.json()
        if data.get("success"):
            print(f"  OK {name}")
            ok += 1
        else:
            print(f"  ERR {name}: {data.get('errors')}")
            err += 1
    print(f"  Secrets: {ok} impostati, {err} errori")
    return err == 0


def step_update_toml(kv_id):
    print("\n[3/4] Aggiornamento wrangler.toml con KV ID reale...")
    with open(TOML_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    if "SOSTITUIRE_CON_ID_KV" in content:
        content = content.replace("SOSTITUIRE_CON_ID_KV", kv_id)
        with open(TOML_PATH, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  wrangler.toml aggiornato: id = \"{kv_id}\"")
    else:
        print("  wrangler.toml già aggiornato (o placeholder non trovato)")


def step_deploy_worker(token, kv_id):
    print("\n[4/4] Deploy Worker con KV binding...")
    with open(JS_PATH, "r", encoding="utf-8") as f:
        script_content = f.read()

    metadata = {
        "main_module": "bks-ai-worker.js",
        "bindings": [
            {
                "type": "kv_namespace",
                "name": "BKS_AGENT_KV",
                "namespace_id": kv_id
            }
        ],
        "compatibility_date": "2025-01-01",
        "compatibility_flags": ["nodejs_compat"],
    }

    import io
    files = {
        "metadata": ("metadata.json", json.dumps(metadata), "application/json"),
        "bks-ai-worker.js": ("bks-ai-worker.js", script_content, "application/javascript+module"),
    }

    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/workers/scripts/{SCRIPT_NAME}"
    r = requests.put(url, headers=headers, files=files, verify=False)
    data = r.json()
    if data.get("success"):
        print(f"  Worker deployato: {SCRIPT_NAME}")
        print(f"  URL: https://bks-agent.bakabo.workers.dev")
        return True
    else:
        print(f"  ERRORE deploy: {data.get('errors')}")
        print(f"  (Il worker e' gia' live — solo il KV binding e' nuovo)")
        return False


def main():
    parser = argparse.ArgumentParser(description="BKS Cloudflare Worker Setup")
    parser.add_argument("--token", help="Cloudflare API Token")
    args = parser.parse_args()

    token = args.token or os.environ.get("CLOUDFLARE_API_TOKEN", "").strip()
    if not token:
        print("ERRORE: CF API Token mancante.")
        print("  Opzione 1: python cloudflare/setup_worker.py --token TUO_TOKEN")
        print("  Opzione 2: set CLOUDFLARE_API_TOKEN=TUO_TOKEN")
        print()
        print("Come ottenerlo:")
        print("  1. https://dash.cloudflare.com/profile/api-tokens")
        print("  2. 'Create Token' > 'Edit Cloudflare Workers'")
        print("  3. Copia il token e riesegui questo script")
        sys.exit(1)

    print("BKS Cloudflare Worker Setup")
    print(f"Account: {ACCOUNT_ID}")
    print(f"Worker:  {SCRIPT_NAME}")
    print(f".env:    {ENV_PATH}")

    env_vars = load_env(ENV_PATH)
    print(f"  SHOPIFY_DOMAIN:  {env_vars.get('SHOPIFY_MYSHOPIFY_DOMAIN','?')}")
    print(f"  OPENAI_API_KEY:  {'OK (trovata)' if env_vars.get('OPENAI_API_KEY') else 'MANCANTE'}")

    kv_id = step_create_kv(token)
    step_set_secrets(token, env_vars)
    step_update_toml(kv_id)
    step_deploy_worker(token, kv_id)

    print("\n=== SETUP COMPLETATO ===")
    print(f"Worker live: https://bks-agent.bakabo.workers.dev")
    print(f"KV namespace ID: {kv_id}")
    print()
    print("Verifica invocations su Cloudflare dashboard:")
    print(f"  https://dash.cloudflare.com/{ACCOUNT_ID}/workers/services/view/{SCRIPT_NAME}")


if __name__ == "__main__":
    main()
