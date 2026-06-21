"""Fetch content of key pages for audit."""
import os, requests, urllib3, sys
urllib3.disable_warnings()  # type: ignore
sys.stdout.reconfigure(encoding="utf-8")  # type: ignore
from pathlib import Path
for raw in Path("I:/BAK ABO/.env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if line and not line.startswith("#") and "=" in line:
        k, _, v = line.partition("=")
        if k.strip() not in os.environ:
            os.environ[k.strip()] = v.strip().strip('"').strip("'")
DOMAIN = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN  = os.environ.get("SHOPIFY_ADMIN_TOKEN", "")
HDR    = {"X-Shopify-Access-Token": TOKEN}
BASE   = f"https://{DOMAIN}/admin/api/2025-01"

# Pages to check: id -> label
TO_CHECK = {
    173590151506: "Help & FAQ (help-faq)",
    173871595858: "About BKS Studio IT (about-bks-studio)",
    173590118738: "About BKS Studio EN (bks-about-bks)",
    171938808146: "About BakAbo (about-bakabo)",
    173871563090: "About BakAbo OK (about-bakabo-1)",
    173871366482: "FAQ empty (bks-faq)",
    173871399250: "BKA About Bak Abo empty (bks-about-bakabo)",
    173871530322: "FAQ Domande Frequenti IT (faq-domande-frequenti)",
}

for pid, label in TO_CHECK.items():
    r = requests.get(f"{BASE}/pages/{pid}.json", headers=HDR, verify=False, timeout=20)
    p = r.json().get("page", {})
    body = (p.get("body_html") or "").strip()
    print(f"\n{'='*60}")
    print(f"[{label}]  id={pid}  handle={p.get('handle')}")
    print(f"BODY ({len(body)} chars): {body[:300]}")
