"""Ritenta BKS Pulse Blush Windbreaker con debug Worker dry_run."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts._production_pipeline import call_worker_sync, call_local_full, load_log, save_log
from datetime import datetime

prod = {"id": "6661b48041b44b5a8e0b0c89", "collection": "pulse", "title": "BKS Pulse Blush™ Windbreaker", "visible": False}

# Debug step 1: Worker dry_run raw
print("=== Worker dry_run RAW ===")
dry = call_worker_sync(prod, dry_run=True)
print(json.dumps(dry, indent=2, ensure_ascii=False)[:500])

if dry.get("status") == "dry_run":
    print("\nDry_run OK — eseguo full pipeline...")
    result = call_local_full(prod, dry_run=False)
    status = result.get("status", "error")
    score  = result.get("bks_score")
    print(f"Risultato: status={status}  score={score}")
    log = load_log()
    log[prod["id"]] = {
        "ts": datetime.now().isoformat(),
        "collection": prod["collection"],
        "title": prod["title"],
        "visible": prod["visible"],
        "status": status,
        "result": result,
    }
    save_log(log)
    print("Salvato.")
else:
    print(f"\nDry_run FALLITO. Stato: {dry.get('status')}  HTTP: {dry.get('http')}")

# Marca Hours Atelier come deleted_in_printify
log = load_log()
if "655d33f7dd7666ffb705bb86" in log:
    log["655d33f7dd7666ffb705bb86"]["status"] = "excluded"
    log["655d33f7dd7666ffb705bb86"]["result"]["body"] = "deleted_in_printify_404"
    save_log(log)
    print("\nHours Atelier marcato come excluded (deleted_in_printify).")
