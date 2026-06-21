"""Pusha bks-collection-signal.liquid (max_blocks 16) poi riprova i template falliti."""
import os, json, time, requests, urllib3, sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore
urllib3.disable_warnings()  # type: ignore

ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ or not os.environ[k]: os.environ[k] = v

DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ["SHOPIFY_ADMIN_TOKEN"]
VER    = os.environ.get("SHOPIFY_API_VERSION", "2025-01")
THEME  = "202392961362"
BASE   = f"https://{DOMAIN}/admin/api/{VER}"
HDR    = {"X-Shopify-Access-Token": TOKEN}
MERGED = ROOT / "04_TEMA_SHOPIFY" / "_merged_tm04"

def push(key, body):
    r = requests.put(f"{BASE}/themes/{THEME}/assets.json",
        json={"asset": {"key": key, "value": body}},
        headers=HDR, timeout=20, verify=False)
    return r

# Step 1: push section
print("=== Push bks-collection-signal.liquid ===")
sec_path = MERGED / "sections" / "bks-collection-signal.liquid"
r = push("sections/bks-collection-signal.liquid", sec_path.read_text(encoding="utf-8"))
print(f"  HTTP {r.status_code}")
if r.status_code not in (200, 201):
    print(f"  ERRORE: {r.text[:200]}")
    raise SystemExit(1)
print("  OK\n")
time.sleep(1)

# Step 2: riprova template falliti (quelli con >6 blocks)
FAILED = [
    "collection.bks-flag.json",
    "collection.bks-glyph.json",
    "collection.bks-hours.json",
    "collection.bks-origin.json",
    "collection.bks-pulse.json",
    "collection.bks-riviera.json",
    "collection.bks-token.json",
]

print("=== Retry template falliti ===")
ok = err = 0
for fname in FAILED:
    key  = f"templates/{fname}"
    body = (MERGED / "templates" / fname).read_text(encoding="utf-8")
    r    = push(key, body)
    if r.status_code in (200, 201):
        print(f"  PUSH {key}")
        ok += 1
    else:
        errs = r.json().get("errors", r.text[:120])
        print(f"  ERR  {key}  HTTP {r.status_code}  {errs}")
        err += 1
    time.sleep(0.4)

print(f"\nFine: {ok} pushati, {err} errori")
