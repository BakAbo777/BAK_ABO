"""Push mobile fixes: header lang selector removed + impact-home spacing."""
import os, requests
from dotenv import load_dotenv
load_dotenv()

DOMAIN  = os.getenv("SHOPIFY_MYSHOPIFY_DOMAIN")
TOKEN   = os.getenv("SHOPIFY_ADMIN_TOKEN")
THEME   = "202392961362"
BASE    = f"https://{DOMAIN}/admin/api/2024-01/themes/{THEME}/assets.json"
HEADERS = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

files = [
    ("snippets/bakabo-header.liquid",        "I:/BAK ABO/04_TEMA_SHOPIFY/snippets/bakabo-header.liquid"),
    ("sections/bks-impact-home.liquid",      "I:/BAK ABO/04_TEMA_SHOPIFY/sections/bks-impact-home.liquid"),
]

for key, path in files:
    content = open(path, encoding="utf-8").read()
    r = requests.put(BASE, json={"asset": {"key": key, "value": content}},
                     headers=HEADERS, verify=False, timeout=30)
    status = "OK" if r.status_code == 200 else f"ERRORE {r.status_code}"
    print(f"  {status}  {key}")
