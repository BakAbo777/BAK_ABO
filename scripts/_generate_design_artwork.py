"""
CLI: genera nuova artwork per un prodotto Printify.
Usa il design template locale (scaricato con _download_design_templates.py)
come base per images.edit, oppure genera da zero.

Uso:
    python scripts/_generate_design_artwork.py \
        --product-id 651f3b7691a9771a560ac91d \
        --collection pulse \
        --handle bks-pulse-hex-sneakers \
        [--design "kinetic hex optical pattern, electric blue on dark navy"] \
        [--template path/to/design.jpg] \
        [--dry-run]

Dopo approvazione:
    python scripts/_update_printify_design.py --product-id ID --image output/...jpg
"""
import argparse, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

env = {}
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    env[k.strip()] = v.strip().strip('"').strip("'")

OPENAI_KEY = env.get("OPENAI_API_KEY", "")
if not OPENAI_KEY:
    print("ERRORE: OPENAI_API_KEY non trovato nel .env")
    sys.exit(1)

from ecommerce_automation.printify_design_generator import (
    generate_design_artwork, find_design_template, DESIGNS_DIR
)

COLLECTIONS = ["hours", "glyph", "marker", "riviera", "pulse", "token", "flag", "folklore"]

parser = argparse.ArgumentParser(description="Genera nuova artwork per prodotto Printify")
parser.add_argument("--product-id",    required=True,  help="Printify product ID")
parser.add_argument("--collection",    required=True,  choices=COLLECTIONS)
parser.add_argument("--handle",        required=True,  help="Product handle (es. bks-pulse-hex-sneakers)")
parser.add_argument("--blueprint-id",  default=None,   help="Printify blueprint ID (es. 1084 per Athletic Shorts)")
parser.add_argument("--position",      default="",     help="Print area position (es. right_leg, front)")
parser.add_argument("--design",        default="",     help="Descrizione design (opzionale)")
parser.add_argument("--template",      default=None,   help="Path template design (auto-discovery se omesso)")
parser.add_argument("--no-template",   action="store_true", help="Genera da zero senza usare template esistente")
parser.add_argument("--dry-run",       action="store_true")
args = parser.parse_args()

# Template resolution avviene dentro generate_design_artwork (local BKS db > wonder_* > none)
template_path = None
if args.no_template:
    template_path = None  # forza generate mode
elif args.template:
    template_path = Path(args.template)
# se né --template né --no-template: auto-discovery dentro generate_design_artwork

print(f"\nBKS Design Artwork Generator")
print(f"  Prodotto   : {args.handle}")
print(f"  Collezione : {args.collection}")
print(f"  Blueprint  : {args.blueprint_id or '(non specificato)'}")
print(f"  Posizione  : {args.position or '(auto)'}")
print(f"  Template   : {template_path.name if template_path else 'auto-discovery'}")
print(f"  Design     : {args.design or '(auto)'}")
print(f"  Dry run    : {args.dry_run}")
print()

result = generate_design_artwork(
    product_id=args.product_id,
    collection=args.collection,
    handle=args.handle,
    openai_api_key=OPENAI_KEY,
    design_description=args.design,
    template_path=template_path,
    blueprint_id=args.blueprint_id,
    position=args.position,
    dry_run=args.dry_run,
)

print(f"\n{'='*60}")
if result["status"] in ("ok", "dry_run"):
    print(f"Stato    : {result['status']}")
    print(f"Modalita : {result.get('mode', '?')}")
    print(f"Output   : {result['path']}")
    if not args.dry_run:
        print(f"\nProssimi passi:")
        print(f"  1. Approva l'artwork generata")
        print(f"  2. Carica su Printify:")
        print(f"     python scripts/_update_printify_design.py --product-id {args.product_id} --image {result['path']}")
else:
    print(f"ERRORE: {result.get('error', '?')}")
    sys.exit(1)
