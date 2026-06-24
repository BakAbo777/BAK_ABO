"""
CLI: sostituisce il design di un prodotto Printify con una nuova immagine AI.
Mantiene intatto il logo BKS e tutte le posizioni/scale.

Uso:
    python scripts/_update_printify_design.py \
        --product-id 6a2544f48ca667581803f49b \
        --image path/to/new_design.png \
        [--dry-run]
"""
import argparse, json, os, sys
from pathlib import Path
import urllib3; urllib3.disable_warnings()

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Carica .env
env = {}
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    env[k.strip()] = v.strip().strip('"').strip("'")
    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

from ecommerce_automation.services.printify_client import PrintifyClient
from ecommerce_automation.printify_design_updater import update_product_design

TOKEN   = env.get("PRINTIFY_API_TOKEN", "")
SHOP_ID = env.get("PRINTIFY_SHOP_ID", "12030061")

if not TOKEN:
    print("ERRORE: PRINTIFY_API_TOKEN non trovato nel .env")
    sys.exit(1)

parser = argparse.ArgumentParser(description="Aggiorna design Printify (logo preservato)")
parser.add_argument("--product-id", required=True, help="ID prodotto Printify")
parser.add_argument("--image",      required=True, help="Path immagine nuova (PNG/JPG)")
parser.add_argument("--shop-id",    default=SHOP_ID)
parser.add_argument("--dry-run",    action="store_true", help="Simula senza modificare")
args = parser.parse_args()

img_path = Path(args.image)
if not img_path.exists():
    print(f"ERRORE: immagine non trovata: {img_path}")
    sys.exit(1)

client = PrintifyClient(token=TOKEN, shop_id=args.shop_id)

print(f"Prodotto : {args.product_id}")
print(f"Immagine : {img_path.name}  ({img_path.stat().st_size // 1024}KB)")
print(f"Dry run  : {args.dry_run}")
print()

result = update_product_design(
    shop_id    = args.shop_id,
    product_id = args.product_id,
    new_image_path = img_path,
    client     = client,
    dry_run    = args.dry_run,
)

print(json.dumps(result, indent=2, ensure_ascii=False))

if result.get("status") in ("updated", "dry_run_ok"):
    print(f"\nOK — {result['areas_modified']} layer aggiornati, logo preservato.")
else:
    print(f"\nERRORE: {result.get('status')} — {result.get('error','')}")
    sys.exit(1)
