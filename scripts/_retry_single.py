"""Ritenta singolo prodotto in errore usando call_local_full direttamente."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts._production_pipeline import call_local_full, load_log, save_log
from datetime import datetime

PRODUCTS = [
    {"id": "655d33f7dd7666ffb705bb86", "collection": "hours",  "title": "BKS Hours Atelier™ Backpack",     "visible": False},
    {"id": "6661b48041b44b5a8e0b0c89", "collection": "pulse",  "title": "BKS Pulse Blush™ Windbreaker",    "visible": False},
]

log = load_log()
for prod in PRODUCTS:
    print(f"\nProcesso: {prod['title']}")
    result = call_local_full(prod, dry_run=False)
    status = result.get("status", "error")
    score = result.get("bks_score")
    print(f"  status={status}  score={score}")
    print(f"  body={str(result.get('body', ''))[:120]}")
    log[prod["id"]] = {
        "ts": datetime.now().isoformat(),
        "collection": prod["collection"],
        "title": prod["title"],
        "visible": prod["visible"],
        "status": status,
        "result": result,
    }
    save_log(log)
    print("  Salvato.")

print("\nDone.")
