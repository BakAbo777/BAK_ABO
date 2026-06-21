"""Create Shopify URL redirects for renamed/removed paths."""
import os, requests, urllib3
from pathlib import Path

urllib3.disable_warnings()  # type: ignore
ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, _, v = line.partition("="); k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ: os.environ[k] = v

DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ.get("SHOPIFY_ADMIN_TOKEN", "")
BASE   = f"https://{DOMAIN}/admin/api/2025-01"
HDR    = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

REDIRECTS = [
    ("/collections/bks-folklore", "/collections/bks-origin"),
    ("/collections/outerwear",    "/collections/puffer-jacket"),
]

for path, target in REDIRECTS:
    # Check if already exists
    r = requests.get(f"{BASE}/redirects.json?path={path}", headers=HDR, verify=False, timeout=15)
    existing = r.json().get("redirects", [])
    if existing:
        print(f"  EXISTS  {path} -> {existing[0]['target']}")
        continue
    r2 = requests.post(f"{BASE}/redirects.json",
        headers=HDR,
        json={"redirect": {"path": path, "target": target}},
        verify=False, timeout=15)
    if r2.ok:
        rid = r2.json()["redirect"]["id"]
        print(f"  OK [{rid}]  {path} -> {target}")
    else:
        print(f"  ERR  {path}: {r2.status_code} {r2.text[:80]}")
