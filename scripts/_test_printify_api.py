"""Quick test of Printify API endpoints."""
import os, requests, urllib3, json
from pathlib import Path
urllib3.disable_warnings()  # type: ignore

ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ:
        os.environ[k] = v

TOKEN = os.environ.get("PRINTIFY_API_TOKEN", "")
BASE  = "https://api.printify.com/v1"
HDR   = {"Authorization": f"Bearer {TOKEN}", "User-Agent": "BKS/1.0"}
SHOP  = "12030061"

print(f"Token: {TOKEN[:8]}...")

CT_HDR = {**HDR, "Content-Type": "application/json;charset=utf-8"}

tests = [
    ("limit=10  no CT",   {"page": 1, "limit": 10},  HDR),
    ("limit=50  no CT",   {"page": 1, "limit": 50},  HDR),
    ("limit=100 no CT",   {"page": 1, "limit": 100}, HDR),
    ("limit=10  with CT", {"page": 1, "limit": 10},  CT_HDR),
    ("limit=50  with CT", {"page": 1, "limit": 50},  CT_HDR),
    ("limit=100 with CT", {"page": 1, "limit": 100}, CT_HDR),
]

for label, params, headers in tests:
    r = requests.get(f"{BASE}/uploads.json", headers=headers, params=params,
                     timeout=15, verify=False)
    cnt = len(r.json().get("data", [])) if r.ok else "?"
    body = r.text[:120] if not r.ok else ""
    print(f"  {label}: HTTP {r.status_code}  items={cnt}  {body}")
