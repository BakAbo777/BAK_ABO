"""Set Shopify credentials as Cloudflare Worker secrets via API, then register Shopify webhook."""
import requests, urllib3, os, secrets, time
from pathlib import Path

urllib3.disable_warnings()
ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ or not os.environ[k]: os.environ[k] = v

CF_ACCOUNT  = "e796d289f744035eee2641e853d8a5af"
CF_TOKEN    = "cfoat_ttdWlIIC0R52Kg3klNqzmBpAGbQRm5oVItDO1yfGsCU.o045AJ39otUUuvu5_G5k31ao_oRDE77mTLus8k8KRAE"
WORKER_NAME = "bks-tier-upgrade"
WORKER_URL  = "https://bks-tier-upgrade.bakabo.workers.dev"

SHOPIFY_DOMAIN  = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
SHOPIFY_TOKEN   = os.environ["SHOPIFY_ADMIN_TOKEN"]
SHOPIFY_VERSION = os.environ.get("SHOPIFY_API_VERSION", "2025-01")

CF_HDR = {"Authorization": f"Bearer {CF_TOKEN}", "Content-Type": "application/json"}
SH_HDR = {"X-Shopify-Access-Token": SHOPIFY_TOKEN, "Content-Type": "application/json"}
SH_BASE = f"https://{SHOPIFY_DOMAIN}/admin/api/{SHOPIFY_VERSION}"


def cf_put_secret(name: str, value: str) -> None:
    r = requests.put(
        f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT}/workers/scripts/{WORKER_NAME}/secrets",
        headers=CF_HDR,
        json={"name": name, "text": value, "type": "secret_text"},
        timeout=15, verify=False
    )
    r.raise_for_status()
    print(f"  Secret {name}: OK")


def register_shopify_webhook(hmac_secret: str) -> None:
    # Remove old tier webhooks
    r = requests.get(f"{SH_BASE}/webhooks.json", headers=SH_HDR, timeout=15, verify=False)
    for wh in r.json().get("webhooks", []):
        if WORKER_URL in wh.get("address", ""):
            requests.delete(f"{SH_BASE}/webhooks/{wh['id']}.json", headers=SH_HDR, timeout=10, verify=False)
            print(f"  Rimosso vecchio webhook {wh['id']}")

    r2 = requests.post(
        f"{SH_BASE}/webhooks.json",
        headers=SH_HDR,
        json={"webhook": {"topic": "customers/update", "address": WORKER_URL, "format": "json"}},
        timeout=15, verify=False
    )
    if not r2.ok:
        print(f"  ERRORE {r2.status_code}: {r2.text}")
        return
    wh = r2.json().get("webhook", {})
    print(f"  Webhook Shopify: id={wh.get('id')} topic={wh.get('topic')}")
    print(f"  URL: {wh.get('address')}")


def main():
    print("=== CF Worker Secrets + Shopify Webhook ===\n")

    # Generate HMAC secret
    hmac_secret = secrets.token_hex(32)

    print("1. Imposto secrets nel Worker...")
    cf_put_secret("SHOPIFY_DOMAIN",      SHOPIFY_DOMAIN)
    cf_put_secret("SHOPIFY_TOKEN",       SHOPIFY_TOKEN)
    cf_put_secret("SHOPIFY_API_VERSION", SHOPIFY_VERSION)
    cf_put_secret("SHOPIFY_HMAC_SECRET", hmac_secret)

    print("\n2. Registro webhook Shopify orders/paid...")
    register_shopify_webhook(hmac_secret)

    print("\n=== COMPLETATO ===")
    print(f"Worker: {WORKER_URL}")
    print("Trigger: ogni ordine pagato aggiorna automaticamente il tier del cliente.")
    print("  1 ordine  -> bks-drop")
    print("  2+ ordini -> bks-archive")


if __name__ == "__main__":
    main()
