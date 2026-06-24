import requests, urllib3, json, sys
urllib3.disable_warnings()
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
env = {}
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    env[k.strip()] = v.strip().strip('"').strip("'")

BKS_TOKEN = env.get("BKS_AI_TOKEN") or env.get("BKS_ASSISTANT_PUBLIC_TOKEN", "")

r = requests.post(
    "https://bks-agent.bakabo.workers.dev/design-generate",
    headers={"Authorization": f"Bearer {BKS_TOKEN}", "Content-Type": "application/json"},
    json={"product_id": "651f3b7691a9771a560ac91d", "collection": "pulse", "dry_run": True},
    verify=False, timeout=30,
)
d = r.json()
print("Status    :", d.get("status"))
print("Title     :", d.get("title", "?"))
print("Blueprint :", d.get("blueprint_id"))
print("Material  :", d.get("material_context") or "(nessuno)")
print("Decision  :", json.dumps(d.get("decision", {}), indent=2))
print()
prompt = d.get("artwork_prompt", "")
print(f"Prompt ({len(prompt)} chars):")
print(prompt[:700])
