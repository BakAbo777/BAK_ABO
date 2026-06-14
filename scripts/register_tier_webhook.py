"""Register Shopify orders/paid webhook pointing to the BKS Tier Upgrade Worker.

Run AFTER deploying the Cloudflare Worker and setting TIER_WEBHOOK_URL in .env.

Usage:
  1. Deploy webhook/tier_upgrade_worker.js to Cloudflare
  2. Add to .env:
       TIER_WEBHOOK_URL=https://bks-tier-upgrade.<your-subdomain>.workers.dev
  3. Run: python scripts/register_tier_webhook.py
"""
import os, requests, urllib3, json, hmac, hashlib, secrets
from pathlib import Path

urllib3.disable_warnings()
ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ or not os.environ[k]: os.environ[k] = v

DOMAIN  = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN   = os.environ["SHOPIFY_ADMIN_TOKEN"]
VERSION = os.environ.get("SHOPIFY_API_VERSION", "2025-01")
BASE    = f"https://{DOMAIN}/admin/api/{VERSION}"
HDR     = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

WORKER_URL = os.environ.get("TIER_WEBHOOK_URL", "")


def list_webhooks():
    r = requests.get(f"{BASE}/webhooks.json", headers=HDR, timeout=15, verify=False)
    r.raise_for_status()
    return r.json().get("webhooks", [])


def delete_webhook(wid):
    requests.delete(f"{BASE}/webhooks/{wid}.json", headers=HDR, timeout=10, verify=False)


def create_webhook(address, secret):
    payload = {
        "webhook": {
            "topic":   "orders/paid",
            "address": address,
            "format":  "json",
            "api_version": VERSION,
        }
    }
    r = requests.post(f"{BASE}/webhooks.json", headers=HDR,
                      json=payload, timeout=15, verify=False)
    r.raise_for_status()
    return r.json().get("webhook", {})


def main():
    if not WORKER_URL:
        print("ERRORE: TIER_WEBHOOK_URL non configurato in .env")
        print()
        print("  1. Esegui: cd webhook && npx wrangler deploy")
        print("  2. Copia l'URL del Worker (es. https://bks-tier-upgrade.xxx.workers.dev)")
        print("  3. Aggiungi a .env: TIER_WEBHOOK_URL=https://...")
        print("  4. Riesegui questo script")
        return

    print(f"Worker URL: {WORKER_URL}\n")

    # Remove existing tier webhook if any
    existing = list_webhooks()
    removed  = 0
    for wh in existing:
        if WORKER_URL in wh.get("address", "") or "tier" in wh.get("address", "").lower():
            delete_webhook(wh["id"])
            print(f"  Rimosso vecchio webhook id={wh['id']}")
            removed += 1

    # Generate HMAC secret
    secret = secrets.token_hex(32)

    # Register new webhook
    wh = create_webhook(WORKER_URL, secret)
    print(f"  Webhook registrato: id={wh.get('id')}  topic={wh.get('topic')}")
    print(f"  Address: {wh.get('address')}")
    print()
    print("IMPORTANTE — aggiungi questo secret nelle variabili del Worker su Cloudflare:")
    print(f"  SHOPIFY_HMAC_SECRET = {secret}")
    print()
    print("  Cloudflare Dashboard -> Workers -> bks-tier-upgrade")
    print("  -> Settings -> Variables -> Add variable")


if __name__ == "__main__":
    main()
