"""
BKS YouTube OAuth Setup — one-shot credential flow.

Run once to authorize and save YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET,
YOUTUBE_REFRESH_TOKEN to .env, then immediately updates the channel.

Usage:
  python scripts/youtube_oauth_setup.py
  python scripts/youtube_oauth_setup.py --client-id=... --client-secret=...
"""
import os, sys, json, time, socket, webbrowser, threading, urllib.parse, urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")  # type: ignore

ENV_PATH = Path(__file__).parent.parent / ".env"

# ── Load .env ──────────────────────────────────────────────────────────────────
def load_env():
    env = {}
    for raw in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env

# ── Write a single key back to .env (update if exists, else append) ───────────
def set_env_key(key: str, value: str):
    text = ENV_PATH.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    updated = False
    for i, line in enumerate(lines):
        if line.startswith(f"{key}=") or line.startswith(f"{key} ="):
            lines[i] = f"{key}={value}\n"
            updated = True
            break
    if not updated:
        lines.append(f"{key}={value}\n")
    ENV_PATH.write_text("".join(lines), encoding="utf-8")


# ── OAuth constants ────────────────────────────────────────────────────────────
REDIRECT_URI  = "http://localhost:8080/oauth2callback"
SCOPES        = "https://www.googleapis.com/auth/youtube"
AUTH_URL      = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL     = "https://oauth2.googleapis.com/token"
CALLBACK_PORT = 8080

# Shared container for the auth code
_auth_code_container: dict = {}
_server_event = threading.Event()


class _OAuthHandler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass  # suppress server logs

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/oauth2callback":
            self.send_response(404)
            self.end_headers()
            return

        params = dict(urllib.parse.parse_qsl(parsed.query))
        if "code" in params:
            _auth_code_container["code"] = params["code"]
            body = b"""<!DOCTYPE html><html><body style="font-family:monospace;background:#0a0a0a;color:#c8c4be;padding:40px">
<h2>BKS Studio</h2><p>Authorization complete. Return to the terminal.</p>
</body></html>"""
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(body)
        else:
            error = params.get("error", "unknown")
            _auth_code_container["error"] = error
            body = f"<html><body>Error: {error}</body></html>".encode()
            self.send_response(400)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(body)

        _server_event.set()


def _run_server(httpd: HTTPServer):
    httpd.handle_request()  # handle exactly one request then stop


def get_auth_code(client_id: str) -> str:
    params = {
        "client_id":     client_id,
        "redirect_uri":  REDIRECT_URI,
        "response_type": "code",
        "scope":         SCOPES,
        "access_type":   "offline",
        "prompt":        "consent",   # force refresh_token even if previously authorized
    }
    url = AUTH_URL + "?" + urllib.parse.urlencode(params)

    httpd = HTTPServer(("localhost", CALLBACK_PORT), _OAuthHandler)
    t = threading.Thread(target=_run_server, args=(httpd,), daemon=True)
    t.start()

    print(f"\n  → Apertura browser per autorizzazione Google...")
    webbrowser.open(url)
    print(f"  → Se il browser non si apre, vai su:\n  {url}\n")

    _server_event.wait(timeout=300)
    httpd.server_close()

    if "error" in _auth_code_container:
        raise RuntimeError(f"OAuth error: {_auth_code_container['error']}")
    if "code" not in _auth_code_container:
        raise RuntimeError("Timeout — nessuna risposta dal browser entro 5 minuti.")

    return _auth_code_container["code"]


def exchange_code(client_id: str, client_secret: str, code: str) -> dict:
    data = urllib.parse.urlencode({
        "code":          code,
        "client_id":     client_id,
        "client_secret": client_secret,
        "redirect_uri":  REDIRECT_URI,
        "grant_type":    "authorization_code",
    }).encode()
    req = urllib.request.Request(TOKEN_URL, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def get_access_token_from_refresh(client_id, client_secret, refresh_token):
    import urllib.request
    data = urllib.parse.urlencode({
        "client_id":     client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type":    "refresh_token",
    }).encode()
    req = urllib.request.Request(TOKEN_URL, data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())["access_token"]


# ── YouTube channel update (copied from update_youtube_channel.py) ─────────────
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


def update_channel(access_token: str, channel_id: str):
    import urllib.request, json
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type":  "application/json",
    }
    base_url = "https://www.googleapis.com/youtube/v3/channels"

    def api_put(params, body):
        url = base_url + "?" + urllib.parse.urlencode(params)
        data = json.dumps(body).encode()
        req = urllib.request.Request(url, data=data, method="PUT")
        for k, v in headers.items():
            req.add_header(k, v)
        try:
            with urllib.request.urlopen(req) as resp:
                return resp.status, json.loads(resp.read())
        except urllib.error.HTTPError as e:
            return e.code, e.read().decode()[:400]

    # snippet — title + description
    status1, resp1 = api_put(
        {"part": "snippet"},
        {"id": channel_id, "snippet": {"title": CHANNEL_TITLE, "description": CHANNEL_DESCRIPTION}}
    )
    if status1 == 200:
        print(f"  ✓ snippet: title='{CHANNEL_TITLE}'")
    else:
        print(f"  ✗ snippet {status1}: {resp1}")

    # brandingSettings — name + keywords + country
    status2, resp2 = api_put(
        {"part": "brandingSettings"},
        {"id": channel_id, "brandingSettings": {"channel": {
            "name": CHANNEL_TITLE, "description": CHANNEL_DESCRIPTION,
            "keywords": CHANNEL_KEYWORDS, "country": "IT"
        }}}
    )
    if status2 == 200:
        print(f"  ✓ brandingSettings (keywords + country)")
    else:
        print(f"  ✗ brandingSettings {status2}: {resp2}")

    return status1 == 200 and status2 == 200


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    print("=" * 55)
    print("  BKS Studio — YouTube OAuth Setup")
    print("=" * 55)

    # Parse args
    client_id = client_secret = ""
    for arg in sys.argv[1:]:
        if arg.startswith("--client-id="):
            client_id = arg.split("=", 1)[1].strip()
        elif arg.startswith("--client-secret="):
            client_secret = arg.split("=", 1)[1].strip()

    # Load existing .env
    env = load_env()
    channel_id = env.get("YOUTUBE_CHANNEL_ID", "")

    # Use saved credentials if already present (re-run case)
    if not client_id:
        client_id = env.get("YOUTUBE_CLIENT_ID", "")
    if not client_secret:
        client_secret = env.get("YOUTUBE_CLIENT_SECRET", "")

    # If refresh_token already present, skip OAuth and go straight to channel update
    refresh_token = env.get("YOUTUBE_REFRESH_TOKEN", "")
    if refresh_token and client_id and client_secret:
        print(f"\n  ✓ Credenziali già presenti — aggiorno il canale direttamente.\n")
        try:
            token = get_access_token_from_refresh(client_id, client_secret, refresh_token)
            ok = update_channel(token, channel_id)
            if ok:
                print("\n✓ Canale aggiornato → https://studio.youtube.com")
            else:
                print("\n⚠ Aggiornamento parziale — controlla gli errori sopra.")
        except Exception as e:
            print(f"\n✗ Errore: {e}")
        return

    # Need credentials from user
    if not client_id or not client_secret:
        print("""
  Per procedere hai bisogno del CLIENT_ID e CLIENT_SECRET di Google OAuth 2.0.

  Come ottenerli (2 minuti):
  ──────────────────────────────────────────────────────
  1. Vai su: https://console.cloud.google.com/
  2. Seleziona il tuo progetto (o creane uno nuovo: "BKS Studio")
  3. Menu: API e Servizi → Credenziali
  4. Crea credenziale → ID client OAuth 2.0
     - Tipo: Applicazione desktop
     - Nome: BKS YouTube CLI
  5. Copia CLIENT_ID e CLIENT_SECRET
  6. Assicurati che "YouTube Data API v3" sia abilitata:
     API e Servizi → Libreria → cerca "YouTube Data API v3" → Attiva
  ──────────────────────────────────────────────────────
""")

    if not client_id:
        client_id = input("  CLIENT_ID: ").strip()
    if not client_secret:
        client_secret = input("  CLIENT_SECRET: ").strip()

    if not client_id or not client_secret:
        print("✗ CLIENT_ID e CLIENT_SECRET richiesti.")
        sys.exit(1)

    if not channel_id:
        channel_id = input("  CHANNEL_ID (es. UCxxxxxx): ").strip()

    # Check if port 8080 is available
    try:
        s = socket.socket()
        s.bind(("localhost", CALLBACK_PORT))
        s.close()
    except OSError:
        print(f"✗ Porta {CALLBACK_PORT} occupata. Chiudi altri processi e riprova.")
        sys.exit(1)

    print(f"\n  → Avvio OAuth flow...")
    try:
        code = get_auth_code(client_id)
        print(f"  ✓ Authorization code ricevuto.")
    except Exception as e:
        print(f"✗ Errore OAuth: {e}")
        sys.exit(1)

    print(f"  → Scambio codice per token...")
    try:
        tokens = exchange_code(client_id, client_secret, code)
    except Exception as e:
        print(f"✗ Errore token exchange: {e}")
        sys.exit(1)

    access_token  = tokens.get("access_token", "")
    refresh_token = tokens.get("refresh_token", "")

    if not refresh_token:
        print("✗ Nessun refresh_token ricevuto. Riprova con account diverso o revoca prima su:")
        print("  https://myaccount.google.com/permissions")
        sys.exit(1)

    print(f"  ✓ Token ottenuti. Salvo in .env...")

    # Save to .env
    set_env_key("YOUTUBE_CLIENT_ID",     client_id)
    set_env_key("YOUTUBE_CLIENT_SECRET", client_secret)
    set_env_key("YOUTUBE_REFRESH_TOKEN", refresh_token)
    if channel_id:
        set_env_key("YOUTUBE_CHANNEL_ID", channel_id)

    print(f"  ✓ .env aggiornato (YOUTUBE_CLIENT_ID / SECRET / REFRESH_TOKEN)")

    # Immediately update the channel
    print(f"\n  → Aggiornamento canale YouTube...\n")
    if not channel_id:
        print("⚠ CHANNEL_ID mancante — skip channel update. Aggiungi YOUTUBE_CHANNEL_ID in .env e rilancia.")
        return

    try:
        ok = update_channel(access_token, channel_id)
        if ok:
            print("\n✓ Canale aggiornato con successo.")
            print("  Verifica su: https://studio.youtube.com")
        else:
            print("\n⚠ Aggiornamento parziale — vedi errori sopra.")
    except Exception as e:
        print(f"\n✗ Errore update canale: {e}")
        print("  → Il token è salvato. Rilancia per ritentare.")


if __name__ == "__main__":
    main()
