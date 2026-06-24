"""Legge token dal .env, trova chat ID, invia messaggio di test."""
import os, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
env = {}
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    env[k.strip()] = v.strip().strip('"').strip("'")

import requests

TOKEN   = env.get("TELEGRAM_BOT_TOKEN", "").strip()
CHAT_ID = env.get("TELEGRAM_CHAT_ID", "").strip()

if not TOKEN:
    print("ERRORE: TELEGRAM_BOT_TOKEN non configurato nel .env")
    sys.exit(1)

BASE = f"https://api.telegram.org/bot{TOKEN}"

# 1. Trova chat ID se mancante
if not CHAT_ID:
    print("CHAT_ID non trovato — cerco negli aggiornamenti recenti...")
    r = requests.get(f"{BASE}/getUpdates", verify=False, timeout=10)
    updates = r.json().get("result", [])
    if not updates:
        print("Nessun messaggio trovato. Manda un messaggio al bot su Telegram e riprova.")
        sys.exit(1)
    # prendi il chat ID dell'ultimo messaggio
    for upd in reversed(updates):
        msg = upd.get("message") or upd.get("channel_post") or {}
        chat = msg.get("chat", {})
        if chat.get("id"):
            CHAT_ID = str(chat["id"])
            nome = chat.get("first_name", chat.get("title", ""))
            print(f"Chat ID trovato: {CHAT_ID} ({nome})")
            break
    if not CHAT_ID:
        print("Impossibile trovare Chat ID. Assicurati di aver mandato almeno un messaggio al bot.")
        sys.exit(1)

# 2. Invia messaggio
TEXT = (
    "🔔 *BKS Studio* — Sistema attivo\n\n"
    "✅ Streamlit :8501 online\n"
    "✅ AI Worker v6 deployato\n"
    "✅ Tema TM04 V.22 live\n"
    "✅ Camerino v3 deployato\n\n"
    "📍 Tablet: http://192.168.1.103:8501\n"
    "🌐 Store: https://bakabo.club\n\n"
    "_Messaggio inviato da Claude — BKS Sistema Monitor_"
)

r = requests.post(
    f"{BASE}/sendMessage",
    json={"chat_id": CHAT_ID, "text": TEXT, "parse_mode": "Markdown"},
    verify=False, timeout=10,
)

if r.ok:
    print(f"✓ Messaggio inviato a chat {CHAT_ID}")
    # salva chat_id nel .env se mancava
    env_text = (ROOT / ".env").read_text(encoding="utf-8")
    if "TELEGRAM_CHAT_ID=" not in env_text and "TELEGRAM_CHANNEL_ID=" not in env_text:
        with open(ROOT / ".env", "a", encoding="utf-8") as f:
            f.write(f"\nTELEGRAM_CHAT_ID={CHAT_ID}\n")
        print(f"  → TELEGRAM_CHAT_ID={CHAT_ID} aggiunto al .env")
else:
    print(f"ERRORE invio: {r.status_code} {r.text}")
