import json
log = json.loads(open("ecommerce_automation/design_batch_log.json").read())
rw = [(pid, v) for pid, v in log.items() if v["status"] == "needs_rework"]
print(f"needs_rework totali: {len(rw)}")
puffers = [(pid, v) for pid, v in rw if "puffer" in v["title"].lower()]
print(f"Puffer in needs_rework: {len(puffers)}")
for pid, v in puffers:
    score = v.get("result", {}).get("bks_score", "?")
    title = v["title"]
    col   = v["collection"]
    print(f"  score={score}  {col:10s}  {title}")

print()
# Mostra tutti puffer nel log (anche updated)
all_puffers = [(pid, v) for pid, v in log.items() if "puffer" in v["title"].lower()]
print(f"Tutti i Puffer nel log: {len(all_puffers)}")
for pid, v in all_puffers:
    score  = v.get("result", {}).get("bks_score", "?")
    status = v["status"]
    title  = v["title"]
    col    = v["collection"]
    print(f"  [{status:12s}]  score={score}  {col:10s}  {title}")
