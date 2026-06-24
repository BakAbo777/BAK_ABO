import json
from collections import Counter

with open("ecommerce_automation/design_batch_log.json") as f:
    log = json.load(f)

statuses = Counter(v["status"] for v in log.values())
print(f"Totale nel log: {len(log)}")
for s, c in statuses.most_common():
    print(f"  {s}: {c}")

recent = sorted(log.items(), key=lambda x: x[1].get("ts", ""), reverse=True)[:8]
print("\nUltimi aggiornati:")
for pid, v in recent:
    score = v.get("result", {}).get("bks_score")
    score_str = f"  score={score}" if score else ""
    status = v["status"]
    ts = v["ts"][:19]
    col = v["collection"]
    title = v["title"][:40]
    print(f"  [{status:12s}] {ts}  {col:10s}  {title}{score_str}")
