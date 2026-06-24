"""Marca BKS Pulse Blush come no_design (Worker non ha template per questo blueprint)."""
import json
LOG = "ecommerce_automation/design_batch_log.json"
with open(LOG) as f:
    log = json.load(f)

pid = "6661b48041b44b5a8e0b0c89"
if pid in log:
    log[pid]["status"] = "no_design"
    log[pid]["result"] = {"status": "no_design", "body": "Worker: nessun template per questo prodotto"}
    with open(LOG, "w") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)
    print(f"OK: BKS Pulse Blush Windbreaker -> no_design")
else:
    print("PID non trovato nel log")
