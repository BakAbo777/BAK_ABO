"""Marca come 'excluded' i prodotti con error=reset_for_redesign_v14."""
import json

LOG = "ecommerce_automation/design_batch_log.json"
with open(LOG) as f:
    log = json.load(f)

fixed = 0
for pid, v in log.items():
    result = v.get("result") or {}
    body = result.get("body", "")
    if body == "reset_for_redesign_v14":
        v["status"] = "excluded"
        fixed += 1
        print(f"  EXCLUDED  {v['title'][:50]}")

with open(LOG, "w") as f:
    json.dump(log, f, indent=2, ensure_ascii=False)

print(f"\nEsclusi: {fixed} prodotti reset_for_redesign")
