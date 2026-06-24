import json
with open("ecommerce_automation/design_batch_log.json") as f:
    log = json.load(f)
errors = {pid: v for pid, v in log.items() if v["status"] == "error"}
print(f"Errors: {len(errors)}")
for pid, v in errors.items():
    title = v["title"]
    col = v["collection"]
    result = v.get("result") or {}
    err = v.get("error") or result.get("error") or result.get("message") or str(result)[:120]
    ts = v.get("ts", "")[:19]
    print(f"\n  PID: {pid}")
    print(f"  Title: {title}")
    print(f"  Col: {col}  TS: {ts}")
    print(f"  Keys: {list(v.keys())}")
    print(f"  Error: {err[:150]}")
