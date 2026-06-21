"""
Fill and fix empty/Italian stub pages using existing English source content.

Changes:
  bks-faq              <- help-faq content (email: crew@)
  faq-domande-frequenti<- help-faq content (email: crew@)
  about-bakabo-1       <- about-bakabo content  [IN MENU — priority]
  bks-about-bakabo     <- about-bakabo content
  about-bks-studio     <- bks-about-bks content
"""
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
HDR    = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
BASE   = f"https://{DOMAIN}/admin/api/2025-01"

def fetch_body(pid):
    r = requests.get(f"{BASE}/pages/{pid}.json", headers=HDR, verify=False, timeout=20)
    return r.json().get("page", {}).get("body_html", "") or ""

def update_page(pid, title, body, tmpl=None):
    payload = {"page": {"id": pid, "title": title, "body_html": body}}
    if tmpl is not None:
        payload["page"]["template_suffix"] = tmpl
    r = requests.put(f"{BASE}/pages/{pid}.json", headers=HDR,
                     json=payload, verify=False, timeout=20)
    if r.ok:
        p = r.json().get("page", {})
        print(f"  OK  [{pid}] '{p['title']}' handle={p['handle']} ({len(body)} chars)")
    else:
        print(f"  ERR [{pid}]: {r.status_code} {r.text[:120]}")

# ── Fetch source bodies ──────────────────────────────────────────────────────
print("Fetching source content...")
faq_body    = fetch_body(173590151506)  # help-faq (5355 chars, English)
about_body  = fetch_body(171938808146)  # about-bakabo (English, "Two Worlds")
studio_body = fetch_body(173590118738)  # bks-about-bks (English, "BKS Studio")

# Fix email in FAQ
faq_body = faq_body.replace("studio@bakabo.club", "crew@bakabo.club")

print(f"  faq_body:    {len(faq_body)} chars")
print(f"  about_body:  {len(about_body)} chars")
print(f"  studio_body: {len(studio_body)} chars")

# ── Apply updates ────────────────────────────────────────────────────────────
print("\nUpdating pages...")

# FAQ pages
update_page(173871366482, "FAQ",                   faq_body)   # bks-faq (empty)
update_page(173871530322, "Help & FAQ",             faq_body)   # faq-domande-frequenti (Italian stub)

# About BakAbo pages
update_page(173871563090, "About BakAbo",           about_body) # about-bakabo-1 (IN MENU, Italian stub)
update_page(173871399250, "About BakAbo",           about_body) # bks-about-bakabo (empty)

# About BKS Studio
update_page(173871595858, "About BKS Studio",       studio_body) # about-bks-studio (Italian stub)

print("\nDone.")
