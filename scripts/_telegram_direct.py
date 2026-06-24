"""Invia messaggio Telegram leggendo token dal .env."""
import sys, requests
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
env = {}
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    env[k.strip()] = v.strip().strip('"').strip("'")

TOKEN   = env.get("TELEGRAM_BOT_TOKEN", "").strip()
CHAT_ID = env.get("TELEGRAM_CHAT_ID", "5706392906").strip()
BASE    = f"https://api.telegram.org/bot{TOKEN}"

if not TOKEN:
    print("ERRORE: TELEGRAM_BOT_TOKEN non trovato nel .env")
    sys.exit(1)

TEXT = (
    "BKS Studio - Sistema attivo\n\n"
    "Tema TM04 V.22 live\n"
    "AI Worker v6 deployato\n"
    "Camerino v3 live\n"
    "Streamlit :8501 online\n\n"
    "Tablet: http://192.168.1.103:8501\n"
    "Store: https://bakabo.club\n\n"
    "Messaggio inviato da Claude - BKS Sistema Monitor"
)

r = requests.post(
    f"{BASE}/sendMessage",
    json={"chat_id": CHAT_ID, "text": TEXT},
    verify=False, timeout=10,
)

if r.ok:
    print("Messaggio inviato OK - Chat ID:", CHAT_ID)
else:
    print("Errore:", r.status_code, r.text[:200])
