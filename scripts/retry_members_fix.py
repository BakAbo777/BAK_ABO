"""Ricarica i 7 template page.bks-* con il fix 'members' mancante da order."""
from __future__ import annotations
import os, requests, urllib3, time, base64
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
THEME_DIR = ROOT / "04_TEMA_SHOPIFY" / "_merged_tm04"
THEME_ID = "202392961362"

FILES = [
    "templates/page.bks-hours.json",
    "templates/page.bks-flag.json",
    "templates/page.bks-glyph.json",
    "templates/page.bks-marker.json",
    "templates/page.bks-pulse.json",
    "templates/page.bks-riviera.json",
    "templates/page.bks-token.json",
]


def upload(dest_key: str) -> bool:
    path = THEME_DIR / dest_key
    content = path.read_bytes()
    payload = {"asset": {"key": dest_key, "value": content.decode("utf-8")}}
    for attempt in range(5):
        r = requests.put(f"{BASE}/themes/{THEME_ID}/assets.json", headers=HDR, json=payload, timeout=60, verify=False)
        if r.status_code == 429:
            time.sleep(float(r.headers.get("Retry-After", 2 ** attempt + 1)))
            continue
        if r.ok:
            print(f"  OK    {dest_key}")
            return True
        print(f"  ERR   {dest_key}  [{r.status_code}] {r.text[:200]}")
        return False
    print(f"  ERR   {dest_key}  rate-limit retries exhausted")
    return False


def main():
    ok = err = 0
    for f in FILES:
        if upload(f):
            ok += 1
        else:
            err += 1
        time.sleep(0.55)
    print(f"\n=== Retry completato: {ok} OK | {err} ERRORI ===")


if __name__ == "__main__":
    main()
