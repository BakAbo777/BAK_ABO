"""
BKS YouTube — Ottimizzazione video esistenti.
Legge tutti i video del canale, genera titoli/descrizioni/tag ottimizzati
via BKS Worker /social endpoint, aggiorna via YouTube API.

Prerequisiti:
  - YouTube Data API v3 ABILITATA nel progetto Google Cloud
  - YOUTUBE_REFRESH_TOKEN presente in .env (run youtube_oauth_setup.py prima)
  - YOUTUBE_API_KEY, YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, YOUTUBE_CHANNEL_ID in .env

Uso:
  python scripts/youtube_optimize_videos.py           # analisi senza modifiche
  python scripts/youtube_optimize_videos.py --apply   # applica aggiornamenti
  python scripts/youtube_optimize_videos.py --video-id=VIDEO_ID --apply  # singolo video
"""
import os, sys, json, ssl, time, urllib.request, urllib.parse
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")  # type: ignore

ENV_PATH  = Path(__file__).parent.parent / ".env"
WORKER_URL = "https://bks-agent.bakabo.workers.dev/social"

# ── BKS collection map (handle → display name) ────────────────────────────────
COLLECTION_MAP = {
    "hours":   "BKS Hours",
    "glyph":   "BKS Glyph",
    "marker":  "BKS Marker",
    "riviera": "BKS Riviera",
    "pulse":   "BKS Pulse",
    "token":   "BKS Token",
    "flag":    "BKS Flag",
    "origin":  "BKS Origin",
}

# ── Default optimized metadata per collection ─────────────────────────────────
# Used as fallback if Worker is unavailable
DEFAULT_META = {
    "BKS Hours": {
        "description": "BKS Hours — a graphic system built around time, urban geometry, and monochrome silence. Wearable AI art. Made to order.\n\nbakabo.club/collections/bks-hours\n\nEach piece is produced for your order. No stock, no expiring seasons.",
        "tags": ["BKS Studio", "BKS Hours", "AI art fashion", "wearable art", "monochrome", "urban wear", "print on demand", "Italian design", "bakabo"],
    },
    "BKS Glyph": {
        "description": "BKS Glyph — symbols, marks, and visual alphabets woven into garments. Wearable AI art. Made to order.\n\nbakabo.club/collections/bks-glyph\n\nEach piece is produced for your order.",
        "tags": ["BKS Studio", "BKS Glyph", "AI art fashion", "graphic art", "symbol print", "wearable art", "print on demand", "Italian design", "bakabo"],
    },
    "BKS Marker": {
        "description": "BKS Marker — gestural brushstrokes and urban expressionism printed on every surface. Wearable AI art. Made to order.\n\nbakabo.club/collections/bks-marker",
        "tags": ["BKS Studio", "BKS Marker", "AI art fashion", "street art", "graffiti fashion", "wearable art", "print on demand", "Italian design", "bakabo"],
    },
    "BKS Riviera": {
        "description": "BKS Riviera — Mediterranean light, coastal palette, resort geometry. Wearable AI art. Made to order.\n\nbakabo.club/collections/bks-riviera",
        "tags": ["BKS Studio", "BKS Riviera", "AI art fashion", "resort wear", "Mediterranean", "coastal fashion", "wearable art", "print on demand", "Italian design"],
    },
    "BKS Pulse": {
        "description": "BKS Pulse — optical vibration, kinetic geometry, hypnotic patterns. Wearable AI art. Made to order.\n\nbakabo.club/collections/bks-pulse",
        "tags": ["BKS Studio", "BKS Pulse", "AI art fashion", "op art", "optical illusion", "geometric fashion", "wearable art", "print on demand", "Italian design"],
    },
    "BKS Token": {
        "description": "BKS Token — pixel art, arcade aesthetics, and digital iconography on fabric. Wearable AI art. Made to order.\n\nbakabo.club/collections/bks-token",
        "tags": ["BKS Studio", "BKS Token", "AI art fashion", "pixel art", "retro gaming", "digital fashion", "wearable art", "print on demand", "Italian design"],
    },
    "BKS Flag": {
        "description": "BKS Flag — bold color fields, pop art language, graphic blocks as statement. Wearable AI art. Made to order.\n\nbakabo.club/collections/bks-flag",
        "tags": ["BKS Studio", "BKS Flag", "AI art fashion", "pop art", "color block", "bold graphics", "wearable art", "print on demand", "Italian design"],
    },
    "BKS Origin": {
        "description": "BKS Origin — folk narratives, illustrated landscapes, organic marks from collective memory. Wearable AI art. Made to order.\n\nbakabo.club/collections/bks-origin",
        "tags": ["BKS Studio", "BKS Origin", "AI art fashion", "folk art", "illustrated fashion", "naive art", "wearable art", "print on demand", "Italian design"],
    },
}

# ── Load .env ──────────────────────────────────────────────────────────────────
def load_env():
    env = {}
    for raw in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env

env = load_env()
API_KEY       = env.get("YOUTUBE_API_KEY", "")
CLIENT_ID     = env.get("YOUTUBE_CLIENT_ID", "")
CLIENT_SECRET = env.get("YOUTUBE_CLIENT_SECRET", "")
REFRESH_TOKEN = env.get("YOUTUBE_REFRESH_TOKEN", "")
CHANNEL_ID    = env.get("YOUTUBE_CHANNEL_ID", "")

CTX = ssl._create_unverified_context()

def api_get(url):
    with urllib.request.urlopen(url, context=CTX) as r:
        return json.loads(r.read())

def api_put(url, token, body, params=None):
    full_url = url + ("?" + urllib.parse.urlencode(params) if params else "")
    data     = json.dumps(body).encode()
    req      = urllib.request.Request(full_url, data=data, method="PUT")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, context=CTX) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:400]

def get_access_token():
    data = urllib.parse.urlencode({
        "client_id": CLIENT_ID, "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN, "grant_type": "refresh_token",
    }).encode()
    req = urllib.request.Request("https://oauth2.googleapis.com/token", data=data, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    with urllib.request.urlopen(req, context=CTX) as r:
        return json.loads(r.read())["access_token"]

# ── Detect collection from title ───────────────────────────────────────────────
def detect_collection(title: str) -> str | None:
    title_l = title.lower()
    for keyword, name in COLLECTION_MAP.items():
        if keyword in title_l or name.lower() in title_l:
            return name
    # Fallback: BKS keyword
    for keyword, name in COLLECTION_MAP.items():
        if keyword[:3] in title_l:
            return name
    return None

# ── Generate optimized metadata via Worker ─────────────────────────────────────
def generate_meta_worker(collection: str) -> dict | None:
    handle = "bks-" + collection.lower().replace("bks ", "").strip()
    payload = json.dumps({
        "collection": handle,
        "product_type": "puffer-jacket",
        "platform": "youtube",
        "language": "en"
    }).encode()
    req = urllib.request.Request(WORKER_URL, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, context=CTX, timeout=10) as r:
            return json.loads(r.read())
    except Exception:
        return None

# ── Build optimized title (BKS format: "[Collection] — BKS Studio") ────────────
def build_title(original: str, collection: str) -> str:
    # Keep original if already in BKS format
    if "BKS Studio" in original and "—" in original:
        return original
    if collection:
        coll_name = collection.replace("BKS ", "")
        return f"{coll_name} — BKS Studio"
    # Generic fallback
    return f"BKS Studio — Wearable AI Art"

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    apply_mode  = "--apply"   in sys.argv
    target_id   = next((a.split("=")[1] for a in sys.argv if a.startswith("--video-id=")), None)

    print("=" * 60)
    print("  BKS YouTube — Video Optimizer")
    print(f"  Mode: {'APPLY CHANGES' if apply_mode else 'DRY RUN (add --apply to save)'}")
    print("=" * 60)

    if not API_KEY or not CHANNEL_ID:
        print("✗ YOUTUBE_API_KEY o YOUTUBE_CHANNEL_ID mancanti in .env")
        sys.exit(1)

    if apply_mode and not all([CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN]):
        print("✗ OAuth credentials mancanti. Esegui prima: python scripts/youtube_oauth_setup.py")
        sys.exit(1)

    # 1. Get uploads playlist
    try:
        ch_data = api_get(
            f"https://www.googleapis.com/youtube/v3/channels"
            f"?part=contentDetails,snippet,statistics&id={CHANNEL_ID}&key={API_KEY}"
        )
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        if "disabled" in body or "not been used" in body:
            print("\n✗ YouTube Data API v3 non abilitata.")
            print("  → Vai su: https://console.developers.google.com/apis/api/youtube.googleapis.com/overview?project=132804158456")
            print("  → Clicca 'ABILITA', attendi 2 minuti, rilancia.")
        else:
            print(f"✗ API error {e.code}: {body[:300]}")
        sys.exit(1)

    ch      = ch_data["items"][0]
    uploads = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    print(f"\n  Canale: {ch['snippet']['title']}")
    print(f"  Video:  {ch['statistics'].get('videoCount','?')} | Views: {ch['statistics'].get('viewCount','?')}")

    # 2. Get video list
    pl_data = api_get(
        f"https://www.googleapis.com/youtube/v3/playlistItems"
        f"?part=snippet&playlistId={uploads}&maxResults=50&key={API_KEY}"
    )
    items = pl_data["items"]
    if target_id:
        items = [v for v in items if v["snippet"]["resourceId"]["videoId"] == target_id]

    vid_ids = ",".join([v["snippet"]["resourceId"]["videoId"] for v in items])
    details = api_get(
        f"https://www.googleapis.com/youtube/v3/videos"
        f"?part=snippet,statistics,contentDetails,status&id={vid_ids}&key={API_KEY}"
    )
    videos = details["items"]

    # 3. Access token (only if apply mode)
    access_token = None
    if apply_mode:
        print("\n  → Ottengo access token...")
        access_token = get_access_token()
        print("  ✓ Token OK")

    # 4. Process each video
    print(f"\n{'─'*60}")
    updated = 0
    for v in videos:
        vid_id  = v["id"]
        snippet = v["snippet"]
        stats   = v.get("statistics", {})
        status  = v.get("status", {})

        orig_title = snippet["title"]
        orig_desc  = snippet.get("description", "")
        orig_tags  = snippet.get("tags", [])
        pub_date   = snippet["publishedAt"][:10]
        views      = stats.get("viewCount", "0")
        priv       = status.get("privacyStatus", "?")

        collection = detect_collection(orig_title)
        new_title  = build_title(orig_title, collection)

        # Generate or use default metadata
        worker_meta = generate_meta_worker(collection) if collection else None
        if worker_meta and "description" in worker_meta:
            new_desc = worker_meta["description"]
            new_tags = worker_meta.get("tags", DEFAULT_META.get(collection, {}).get("tags", orig_tags))
        elif collection and collection in DEFAULT_META:
            new_desc = DEFAULT_META[collection]["description"]
            new_tags = DEFAULT_META[collection]["tags"]
        else:
            new_desc = f"BKS Studio — Wearable AI art. Made to order.\nbakabo.club\n\n{orig_desc[:200]}".strip()
            new_tags = ["BKS Studio", "AI art fashion", "wearable art", "print on demand", "Italian design", "bakabo"]

        # Always add channel standard tags
        standard_tags = ["BKS Studio", "bakabo", "AI art fashion", "wearable art", "print on demand"]
        for t in standard_tags:
            if t not in new_tags:
                new_tags.append(t)

        changed_title = new_title != orig_title
        changed_desc  = new_desc[:200] != orig_desc[:200]
        changed_tags  = set(new_tags) != set(orig_tags)

        print(f"\n  Video: {vid_id}")
        print(f"  Titolo orig:   {orig_title[:55]}")
        if changed_title:
            print(f"  Titolo nuovo:  {new_title}")
        print(f"  Collezione:    {collection or '(non rilevata)'}")
        print(f"  Views: {views} | Privacy: {priv} | Data: {pub_date}")
        if changed_tags:
            print(f"  Tag nuovi:     {', '.join(new_tags[:6])}...")
        if not changed_title and not changed_desc and not changed_tags:
            print(f"  → Nessuna modifica necessaria.")
            continue

        if apply_mode:
            new_snippet = {
                "id": vid_id,
                "snippet": {
                    "title":       new_title,
                    "description": new_desc,
                    "tags":        new_tags,
                    "categoryId":  snippet.get("categoryId", "26"),  # 26 = How-to & Style
                    "defaultLanguage": "en",
                }
            }
            code, resp = api_put(
                "https://www.googleapis.com/youtube/v3/videos",
                access_token, new_snippet, {"part": "snippet"}
            )
            if code == 200:
                print(f"  ✓ AGGIORNATO")
                updated += 1
            else:
                print(f"  ✗ Errore {code}: {resp[:200]}")
            time.sleep(0.5)

    print(f"\n{'─'*60}")
    if apply_mode:
        print(f"✓ Completato: {updated}/{len(videos)} video aggiornati.")
    else:
        print(f"Analisi completata ({len(videos)} video). Aggiungi --apply per salvare le modifiche.")
    print()


if __name__ == "__main__":
    main()
