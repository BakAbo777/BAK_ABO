import json
with open("ecommerce_automation/design_batch_log.json") as f:
    log = json.load(f)
errors = {pid: v for pid, v in log.items() if v["status"] == "error"}
print(f"Errors: {len(errors)}")
for pid, v in errors.items():
    err = v.get("error", "")[:90]
    title = v["title"][:40]
    col = v["collection"]
    print(f"  {title:40s}  {col:10s}  {err}")
