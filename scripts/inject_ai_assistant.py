"""Inietta {% section 'bks-ai-assistant' %} in layout/theme.liquid prima di </body>."""
from __future__ import annotations
import os, sys, requests, urllib3, base64, json
from pathlib import Path

urllib3.disable_warnings()  # type: ignore
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

INJECT  = "\n  {%- section 'bks-ai-assistant' -%}\n"
MARKER  = "bks-ai-assistant"
TARGET  = "layout/theme.liquid"


def get_active_theme_id() -> str:
    r = requests.get(f"{BASE}/themes.json", headers=HDR, timeout=15, verify=False)
    r.raise_for_status()
    for t in r.json().get("themes", []):
        if t.get("role") == "main":
            return str(t["id"])
    raise RuntimeError("Nessun tema attivo trovato")


def main():
    theme_id = get_active_theme_id()
    print(f"Tema attivo: {theme_id}")

    # Scarica theme.liquid
    r = requests.get(
        f"{BASE}/themes/{theme_id}/assets.json",
        headers=HDR, params={"asset[key]": TARGET}, timeout=30, verify=False
    )
    r.raise_for_status()
    content = r.json()["asset"]["value"]

    if MARKER in content:
        print("✓ bks-ai-assistant già presente in theme.liquid — niente da fare.")
        print("\nSe non lo vedi nel sito, verifica che 'Enable assistant' sia attivo")
        print("nel Theme editor → BKS AI assistant → Enable assistant ✓")
        return

    # Inserisci prima di </body>
    if "</body>" not in content:
        print("ERRORE: tag </body> non trovato in theme.liquid")
        sys.exit(1)

    new_content = content.replace("</body>", INJECT + "</body>", 1)

    # Salva copia locale
    local_path = ROOT / "04_TEMA_SHOPIFY" / "layout" / "theme.liquid"
    local_path.parent.mkdir(parents=True, exist_ok=True)
    local_path.write_text(new_content, encoding="utf-8")
    print(f"Salvato in locale: {local_path}")

    # Push su Shopify
    payload = {"asset": {"key": TARGET, "value": new_content}}
    r2 = requests.put(
        f"{BASE}/themes/{theme_id}/assets.json",
        headers=HDR, json=payload, timeout=60, verify=False
    )
    if r2.ok:
        print("✓ theme.liquid aggiornato su Shopify")
        print("\nORA: vai nel Theme editor → BKS AI assistant → spunta 'Enable assistant'")
    else:
        print(f"ERRORE upload: [{r2.status_code}] {r2.text[:200]}")
        sys.exit(1)


if __name__ == "__main__":
    main()
