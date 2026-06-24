"""
Aggiorna il tono pubblicitario BakAbo in Cloudflare KV.
Il Worker legge style:bakabo:ad_voice per ogni prompt generativo.
Aggiorna questo KV key periodicamente per riflettere le tendenze attuali.

Uso:
    python scripts/_update_ad_voice.py
    python scripts/_update_ad_voice.py --dry-run
    python scripts/_update_ad_voice.py --year 2027 --tone "new wave minimalism, raw texture, anti-drop era"
"""
import json, sys, argparse
from datetime import datetime
from pathlib import Path

import requests, urllib3
urllib3.disable_warnings()

ROOT = Path(__file__).resolve().parent.parent
env = {}
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    env[k.strip()] = v.strip().strip('"').strip("'")

CF_ACCOUNT = "e796d289f744035eee2641e853d8a5af"
CF_TOKEN   = env.get("CLOUDFLARE_API_TOKEN", "")
KV_NS_ID   = "8f6b1e4accae47949b2960735d270a3a"

parser = argparse.ArgumentParser()
parser.add_argument("--dry-run", action="store_true")
parser.add_argument("--year",    default=str(datetime.now().year))
parser.add_argument("--tone",    default="")
args = parser.parse_args()

# ── Vocabolario pubblicitario 2026 (aggiorna ogni stagione) ─────────────────
AD_VOICE_2026 = {
    "year": args.year,
    "tone": args.tone or (
        "raw editorial artwear — designed in Italy, made on demand worldwide. "
        "Direct, visual, urban, slightly poetic, never fake-luxury. "
        "The product is made on demand via print-on-demand, but the value is the BKS visual system: "
        "AI-generated surfaces, curated collections, editorial imagery, wearable graphic objects."
    ),
    "vocabulary": [
        "wearable art",
        "designed in Italy",
        "made on demand",
        "art on fabric",
        "wearable graphic object",
        "BKS visual system",
        "printed for you",
        "no overstock",
        "AI-generated visual collection",
    ],
    "anti_words": [
        "luxury craftsmanship", "Italian-made garment", "premium materials",
        "limited edition", "handmade", "artisan", "finest quality",
        "bespoke tailoring", "haute couture", "exclusive",
    ],
    "direction": (
        "Position BakAbo as AI-art fashion atelier, not traditional luxury tailoring. "
        "Never inflate the base product — always elevate through curation, image, collection, "
        "and commercial clarity. The client buys a piece inside a visual universe, not a printed shirt."
    ),
    "visual_register": (
        "editorial, direct, urban — product as graphic object, "
        "system visible, collection DNA dominant, "
        "light and space communicate value (not product description alone)"
    ),
    "positioning": "AI-art fashion atelier: più alto del POD generico, più artistico dello streetwear, più accessibile del luxury classico.",
    "updated_at": datetime.now().isoformat(),
}

print("\nBKS Ad Voice Update")
print(f"  Anno    : {AD_VOICE_2026['year']}")
print(f"  Tone    : {AD_VOICE_2026['tone'][:80]}...")
print(f"  Mode    : {'DRY-RUN' if args.dry_run else 'LIVE'}\n")

if args.dry_run:
    print("  [dry-run] KV PUT style:bakabo:ad_voice")
    print(json.dumps(AD_VOICE_2026, indent=2, ensure_ascii=False))
    sys.exit(0)

r = requests.put(
    f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT}/storage/kv/namespaces/{KV_NS_ID}/values/style:bakabo:ad_voice",
    headers={"Authorization": f"Bearer {CF_TOKEN}"},
    data=json.dumps(AD_VOICE_2026, ensure_ascii=False),
    timeout=20, verify=False,
)
if r.ok:
    print("  KV PUT style:bakabo:ad_voice: OK")
    print(f"  Tone aggiornato: {AD_VOICE_2026['tone'][:100]}")
else:
    print(f"  ERRORE: {r.status_code} {r.text[:200]}")
    sys.exit(1)

print("\nDone. Il Worker usera questo tono alla prossima generazione.")
