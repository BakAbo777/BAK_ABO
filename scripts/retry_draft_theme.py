"""Ricarica solo gli asset falliti nel push iniziale del tema draft, in ordine sicuro."""
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

# Ordine: sezioni dipendenti prima, poi i template che le referenziano.
FILES = [
    "sections/bks-dedicated-collection-page.liquid",
    "sections/bks-piano-hero.liquid",
    "sections/footer-group.json",
    "templates/index.json",
    "templates/page.bks-athletic-shorts.json",
    "templates/page.bks-backpack.json",
    "templates/page.bks-flag.json",
    "templates/page.bks-flip-flop.json",
    "templates/page.bks-glyph.json",
    "templates/page.bks-graphic-sneakers.json",
    "templates/page.bks-hours.json",
    "templates/page.bks-lounge-pants.json",
    "templates/page.bks-marker.json",
    "templates/page.bks-men.json",
    "templates/page.bks-one-piece-swimsuit.json",
    "templates/page.bks-piano-hero.json",
    "templates/page.bks-puffer-jacket.json",
    "templates/page.bks-pullover-hoodie.json",
    "templates/page.bks-pulse.json",
    "templates/page.bks-racerback-dress.json",
    "templates/page.bks-riviera.json",
    "templates/page.bks-shoes.json",
    "templates/page.bks-sneakers.json",
    "templates/page.bks-swimwear.json",
    "templates/page.bks-token.json",
    "templates/page.bks-travel-bag.json",
    "templates/page.bks-tribal-signals.json",
    "templates/page.bks-windbreaker.json",
    "templates/page.bks-woman.json",
    "templates/page.json",
]


def upload(dest_key: str) -> bool:
    path = THEME_DIR / dest_key
    content = path.read_bytes()
    is_binary = dest_key.rsplit(".", 1)[-1].lower() in {"png","jpg","jpeg","gif","webp","svg","woff","woff2","ttf","ico","eot"}
    payload = {"asset": {"key": dest_key, **({"attachment": base64.b64encode(content).decode()} if is_binary else {"value": content.decode("utf-8")})}}
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
