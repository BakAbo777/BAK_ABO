"""
BKS YouTube — OAuth token via copia-incolla (no HTTP server).
Apre il browser, tu autorizzi, copi il codice dalla URL di redirect, incolli qui.
"""
import os, sys, json, ssl, webbrowser, urllib.parse, urllib.request
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")  # type: ignore

ENV_PATH = Path(__file__).parent.parent / ".env"

CLIENT_ID     = "132804158456-ugoaa4trkkff9chdbsgjjnfqr6gdiaog.apps.googleusercontent.com"
CLIENT_SECRET = "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"
REDIRECT_URI  = "urn:ietf:wg:oauth:2.0:oob"   # out-of-band: Google mostra il codice direttamente
SCOPE         = "https://www.googleapis.com/auth/youtube"

def set_env_key(key, value):
    text  = ENV_PATH.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    found = False
    for i, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[i] = f"{key}={value}\n"
            found = True
            break
    if not found:
        lines.append(f"{key}={value}\n")
    ENV_PATH.write_text("".join(lines), encoding="utf-8")
    print(f"  ✓ .env aggiornato: {key}")

auth_url = (
    "https://accounts.google.com/o/oauth2/v2/auth?"
    + urllib.parse.urlencode({
        "client_id":     CLIENT_ID,
        "redirect_uri":  REDIRECT_URI,
        "response_type": "code",
        "scope":         SCOPE,
        "access_type":   "offline",
        "prompt":        "consent",
    })
)

print("\n=== BKS YouTube — Token Setup ===")
print("\n→ Apertura browser per autorizzazione...")
webbrowser.open(auth_url)
print("\nSe il browser non si apre, vai manualmente su:")
print(auth_url[:100] + "...")
print("\nDopo aver autorizzato, Google mostra un CODICE nella pagina.")
print("Copia il codice e incollalo qui sotto.\n")

code = input("  Codice di autorizzazione: ").strip()

if not code:
    print("✗ Nessun codice inserito.")
    sys.exit(1)

# Exchange code for tokens
ctx  = ssl._create_unverified_context()
data = urllib.parse.urlencode({
    "code":          code,
    "client_id":     CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "redirect_uri":  REDIRECT_URI,
    "grant_type":    "authorization_code",
}).encode()

req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data, method="POST")
req.add_header("Content-Type", "application/x-www-form-urlencoded")

try:
    with urllib.request.urlopen(req, context=ctx) as r:
        tokens = json.loads(r.read())
except urllib.error.HTTPError as e:
    print(f"✗ Errore token: {e.read().decode()}")
    sys.exit(1)

refresh_token = tokens.get("refresh_token", "")
access_token  = tokens.get("access_token", "")

if not refresh_token:
    print("✗ Nessun refresh_token ricevuto.")
    sys.exit(1)

print(f"\n  ✓ Refresh token ottenuto.")

# Save to .env
set_env_key("YOUTUBE_CLIENT_ID",     CLIENT_ID)
set_env_key("YOUTUBE_CLIENT_SECRET", CLIENT_SECRET)
set_env_key("YOUTUBE_REFRESH_TOKEN", refresh_token)

# Update channel immediately
CHANNEL_ID = ""
for raw in ENV_PATH.read_text(encoding="utf-8").splitlines():
    if raw.startswith("YOUTUBE_CHANNEL_ID="):
        CHANNEL_ID = raw.split("=",1)[1].strip()

if not CHANNEL_ID:
    print("⚠ CHANNEL_ID non trovato in .env — skip update canale.")
    sys.exit(0)

print(f"\n→ Aggiornamento canale YouTube ({CHANNEL_ID})...")

def api_put(url, token, body, part):
    full = url + f"?part={part}"
    req2 = urllib.request.Request(full, data=json.dumps(body).encode(), method="PUT")
    req2.add_header("Authorization", f"Bearer {token}")
    req2.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req2, context=ctx) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:300]

TITLE = "BKS Studio"
DESC  = "BKS Studio — AI-Art Atelier.\nEight permanent collections designed with artificial intelligence, printed on demand.\nWearable art. No stock, no expiring seasons.\nbakabo.club"

s1, _ = api_put("https://www.googleapis.com/youtube/v3/channels", access_token,
    {"id": CHANNEL_ID, "snippet": {"title": TITLE, "description": DESC}}, "snippet")
print(f"  {'✓' if s1==200 else '✗'} snippet (title): {s1}")

s2, _ = api_put("https://www.googleapis.com/youtube/v3/channels", access_token,
    {"id": CHANNEL_ID, "brandingSettings": {"channel": {
        "name": TITLE, "description": DESC,
        "keywords": "BKS Studio, AI art fashion, wearable art, print on demand, AI generated patterns, fashion design, streetwear, swimwear, puffer jacket, Italian design, bakabo",
        "country": "IT"
    }}}, "brandingSettings")
print(f"  {'✓' if s2==200 else '✗'} brandingSettings: {s2}")

if s1 == 200 and s2 == 200:
    print("\n✓ Canale rinominato 'BKS Studio'. Verifica: https://studio.youtube.com")
else:
    print("\n⚠ Aggiornamento parziale — controlla errori sopra.")
