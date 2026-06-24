"""Fetch all Printify uploads and save wonder image catalog.
Paginates /v1/uploads.json and extracts wonder_*.jpg images with their IDs.
"""
import requests, json, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
env = {}
for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.startswith("#"):
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip()

TOKEN = env["PRINTIFY_API_TOKEN"]
HDR   = {"Authorization": f"Bearer {TOKEN}"}

all_uploads = []
page = 1
total_pages = 1

print("Fetching Printify uploads...")
while page <= total_pages:
    r = requests.get("https://api.printify.com/v1/uploads.json",
        params={"limit": 100, "page": page},
        headers=HDR, verify=False, timeout=30)
    if not r.ok:
        print(f"  Error page {page}: {r.status_code}")
        break
    data = r.json()
    batch = data.get("data", [])
    all_uploads.extend(batch)
    total_pages = data.get("last_page", 1)
    print(f"  Page {page}/{total_pages}  +{len(batch)} uploads  total so far: {len(all_uploads)}")
    page += 1
    time.sleep(0.3)

print(f"\nTotal uploads: {len(all_uploads)}")

# Filter wonder images
wonder_uploads = [u for u in all_uploads if "wonder" in u.get("file_name","").lower()]
print(f"Wonder images: {len(wonder_uploads)}")

# Save catalog
out = {
    "total": len(all_uploads),
    "wonder_count": len(wonder_uploads),
    "wonders": [{"id": u["id"], "file_name": u["file_name"]} for u in wonder_uploads],
    "all": [{"id": u["id"], "file_name": u["file_name"]} for u in all_uploads],
}
out_path = ROOT / "output" / "printify_uploads_catalog.json"
out_path.write_text(json.dumps(out, indent=2))
print(f"Saved to {out_path}")
