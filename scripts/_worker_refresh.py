"""Trigger Worker pattern sync and verify health."""
import os, requests, urllib3
from pathlib import Path
urllib3.disable_warnings()

ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ: os.environ[k] = v

tok = os.environ.get("BKS_ASSISTANT_PUBLIC_TOKEN", "")
HDR = {"Authorization": f"Bearer {tok}"}
BASE = "https://bks-agent.bakabo.workers.dev"

r1 = requests.post(f"{BASE}/admin/patterns/sync", headers=HDR, verify=False, timeout=20)
print(f"sync:   {r1.status_code}  {r1.text[:120]}")

r2 = requests.get(f"{BASE}/health", headers=HDR, verify=False, timeout=10)
print(f"health: {r2.status_code}  {r2.text[:200]}")
