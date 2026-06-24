"""Check Printify uploads library for original wonder images."""
import requests, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
env = {}
for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.startswith("#"):
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip()

TOKEN = env["PRINTIFY_API_TOKEN"]
SHOP  = "12030061"
HDR   = {"Authorization": f"Bearer {TOKEN}"}

# List uploads - page 1
r = requests.get("https://api.printify.com/v1/uploads.json",
    params={"limit": 100, "page": 1},
    headers=HDR, verify=False, timeout=30)
data = r.json()
uploads = data.get("data", [])
total = data.get("total", 0)
pages = data.get("last_page", 1)

print(f"Total uploads: {total}, pages: {pages}")
print(f"First page: {len(uploads)} images")

# Show first 10
print("\nSample uploads (most recent 10):")
for u in uploads[:10]:
    fname = u.get("file_name", "")
    uid   = u.get("id", "")
    print(f"  {uid}  {fname}")

# Check if any have 'wonder' in filename
wonder_uploads = [u for u in uploads if "wonder" in u.get("file_name","").lower()]
print(f"\nWonder images in first page: {len(wonder_uploads)}")
for u in wonder_uploads[:5]:
    print(f"  {u['id']}  {u['file_name']}")
