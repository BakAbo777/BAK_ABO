"""Riclassifica needs_rework con score >= 20 → updated (nuovo gate)."""
import json

LOG = "ecommerce_automation/design_batch_log.json"
with open(LOG) as f:
    log = json.load(f)

fixed = 0
for pid, v in log.items():
    if v.get("status") == "needs_rework":
        score = v.get("result", {}).get("bks_score")
        if score is not None and score >= 20:
            v["status"] = "updated"
            fixed += 1
            print(f"  FIXED  score={score}  {v['collection']:10s}  {v['title'][:45]}")

with open(LOG, "w") as f:
    json.dump(log, f, indent=2, ensure_ascii=False)

print(f"\nRiclassificati: {fixed} prodotti needs_rework -> updated")
