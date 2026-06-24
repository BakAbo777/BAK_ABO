"""Riporta prodotti dry_run (senza score reale) → needs_rework per retry-rework."""
import json

LOG = "ecommerce_automation/design_batch_log.json"
with open(LOG) as f:
    log = json.load(f)

fixed = 0
for pid, v in log.items():
    if v.get("status") == "dry_run":
        v["status"] = "needs_rework"
        # Rimuove risultato dry_run (nessun score reale)
        v["result"] = {"status": "needs_rework", "body": "reverted_from_dry_run"}
        fixed += 1
        print(f"  REVERT  {v['collection']:10s}  {v['title'][:45]}")

with open(LOG, "w") as f:
    json.dump(log, f, indent=2, ensure_ascii=False)

print(f"\nRipristinati: {fixed} prodotti dry_run -> needs_rework")
