"""
CLI: dopo approvazione design → genera AI shots via OpenAI.
Camera libera (0m-infinito), set virtuale illimitato, luci cinema BakAbo.
Uso:
    python scripts/_generate_drone_shots.py \
        --handle bks-pulse-hex-sneakers \
        --collection pulse \
        --type sneakers \
        --title "BKS Pulse Hex Sneakers" \
        [--design "dark navy hex optical grid"] \
        [--slots hero_shot editorial_scene] \
        [--dry-run]
"""
import argparse, json, os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

env = {}
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    env[k.strip()] = v.strip().strip('"').strip("'")

OPENAI_KEY = env.get("OPENAI_API_KEY", "")
if not OPENAI_KEY:
    print("ERRORE: OPENAI_API_KEY non trovato nel .env")
    sys.exit(1)

from ecommerce_automation.drone_shot_generator import generate_drone_shots, SLOT_SPECS

parser = argparse.ArgumentParser(description="Genera drone shots via OpenAI")
parser.add_argument("--handle",     required=True, help="Handle prodotto (es. bks-pulse-hex-sneakers)")
parser.add_argument("--collection", required=True, choices=["hours","glyph","marker","riviera","pulse","token","flag","folklore"])
parser.add_argument("--type",       required=True, help="Tipo prodotto (es. sneakers, puffer-jacket)")
parser.add_argument("--title",      required=True, help="Titolo prodotto completo")
parser.add_argument("--design",     default="",   help="Descrizione breve del design/pezza")
parser.add_argument("--slots",      nargs="+",    choices=list(SLOT_SPECS.keys()), default=None)
parser.add_argument("--dry-run",    action="store_true")
args = parser.parse_args()

print(f"\nBKS Drone Shot Generator")
print(f"  Prodotto   : {args.title}")
print(f"  Collezione : {args.collection}")
print(f"  Tipo       : {args.type}")
print(f"  Slot       : {args.slots or list(SLOT_SPECS.keys())}")
print(f"  Dry run    : {args.dry_run}")
if args.design:
    print(f"  Design     : {args.design}")
print()

results = generate_drone_shots(
    product_title   = args.title,
    product_type    = args.type,
    collection      = args.collection,
    handle          = args.handle,
    openai_api_key  = OPENAI_KEY,
    design_description = args.design,
    slots           = args.slots,
    dry_run         = args.dry_run,
)

print(f"\n{'='*60}")
ok    = sum(1 for r in results if r["status"] in ("ok","dry_run"))
errs  = sum(1 for r in results if r["status"] == "error")
print(f"Generati: {ok}  Errori: {errs}")

out_dir = Path(results[0]["path"]).parent if results else Path(".")
print(f"Output: {out_dir}")

if not args.dry_run and ok > 0:
    print("\nProssimi passi:")
    print("  1. Verifica immagini in", out_dir)
    print("  2. Approva -> push a Shopify come product images")
    print("  3. Oppure usa come design_url per /printify-update")
