"""Deploy Worker v5 leggendo il token da .env — non espone credenziali in CLI."""
import os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8", errors="replace").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, _, v = line.partition("=")
    k = k.strip(); v = v.strip().strip('"').strip("'")
    os.environ.setdefault(k, v)

token = os.environ.get("CLOUDFLARE_API_TOKEN", "")
if not token:
    print("CLOUDFLARE_API_TOKEN non trovato in .env"); sys.exit(1)

# Usa setup_worker.py già esistente
sys.argv = ["setup_worker.py", "--token", token]
exec(open(ROOT / "cloudflare" / "setup_worker.py").read())
