import os
from pathlib import Path

env = {}
for raw in Path("I:/BAK ABO/.env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    env[k.strip()] = v.strip().strip('"').strip("'")

tok = env.get("TELEGRAM_BOT_TOKEN", "")
cid = env.get("TELEGRAM_CHAT_ID", env.get("TELEGRAM_CHANNEL_ID", ""))
usr = env.get("TELEGRAM_BOT_USERNAME", "")

print("BOT_TOKEN presente:", bool(tok), "| lunghezza:", len(tok))
print("CHAT_ID presente:  ", bool(cid), "| valore:", cid if cid else "(vuoto)")
print("USERNAME:          ", usr)
