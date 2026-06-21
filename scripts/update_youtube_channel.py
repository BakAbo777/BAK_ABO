"""
Update YouTube channel: name, description, keywords.
Uses OAuth credentials from .env (refresh_token flow).
Requires: google-auth, google-auth-oauthlib, google-api-python-client
"""
import os, sys, json, requests
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")  # type: ignore

# Load .env
for raw in (Path(__file__).parent.parent / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("=")
        if k.strip() not in os.environ:
            os.environ[k.strip()] = v.strip().strip('"').strip("'")

CLIENT_ID     = os.environ.get("YOUTUBE_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("YOUTUBE_CLIENT_SECRET", "")
REFRESH_TOKEN = os.environ.get("YOUTUBE_REFRESH_TOKEN", "")
CHANNEL_ID    = os.environ.get("YOUTUBE_CHANNEL_ID", "")

if not all([CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN, CHANNEL_ID]):
    print("✗ Credenziali YouTube mancanti in .env")
    sys.exit(1)

# ── Step 1: refresh access token ──────────────────────────────────────────────
def get_access_token():
    r = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id":     CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type":    "refresh_token",
    })
    r.raise_for_status()
    return r.json()["access_token"]

# ── Channel metadata ───────────────────────────────────────────────────────────
CHANNEL_TITLE = "BKS Studio"

CHANNEL_DESCRIPTION = """BKS Studio — AI-Art Atelier.
Eight permanent collections designed with artificial intelligence, printed on demand.
Wearable art. No stock, no expiring seasons.
bakabo.club"""

CHANNEL_KEYWORDS = (
    "BKS Studio, AI art fashion, wearable art, print on demand, AI generated patterns, "
    "fashion design, streetwear, swimwear, puffer jacket, Italian design, bakabo club, "
    "one piece swimsuit, athletic shorts, AI art clothing"
)

def update_channel(token):
    url = "https://www.googleapis.com/youtube/v3/channels"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    # ── Update snippet (title) ─────────────────────────────────────────────────
    body_snippet = {
        "id": CHANNEL_ID,
        "snippet": {
            "title":       CHANNEL_TITLE,
            "description": CHANNEL_DESCRIPTION,
        }
    }
    r1 = requests.put(url, params={"part": "snippet"}, headers=headers, json=body_snippet)
    if r1.status_code == 200:
        print(f"  ✓ snippet aggiornato: title='{CHANNEL_TITLE}'")
    else:
        print(f"  ✗ snippet error {r1.status_code}: {r1.text[:300]}")

    # ── Update brandingSettings (keywords) ────────────────────────────────────
    body_branding = {
        "id": CHANNEL_ID,
        "brandingSettings": {
            "channel": {
                "name":        CHANNEL_TITLE,
                "description": CHANNEL_DESCRIPTION,
                "keywords":    CHANNEL_KEYWORDS,
                "country":     "IT",
            }
        }
    }
    r2 = requests.put(url, params={"part": "brandingSettings"}, headers=headers, json=body_branding)
    if r2.status_code == 200:
        print(f"  ✓ brandingSettings aggiornati (keywords + country)")
    else:
        print(f"  ✗ brandingSettings error {r2.status_code}: {r2.text[:300]}")

    return r1.status_code == 200 and r2.status_code == 200


print("=== BKS YouTube Channel Update ===")
print(f"  Channel ID: {CHANNEL_ID}")
print(f"  Nuovo nome: {CHANNEL_TITLE}")

try:
    token = get_access_token()
    print(f"  ✓ Access token ottenuto")
    ok = update_channel(token)
    if ok:
        print("\n✓ Canale aggiornato. Verifica su: https://studio.youtube.com")
    else:
        print("\n⚠ Aggiornamento parziale — controlla gli errori sopra")
except requests.HTTPError as e:
    print(f"\n✗ Errore HTTP: {e}")
    print("  → Verifica che il refresh_token sia valido e abbia scope youtube")
except Exception as e:
    print(f"\n✗ Errore: {e}")
