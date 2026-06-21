"""
Fix contact page (id=120387338578):
  - Replace studio@bakabo.club -> crew@bakabo.club
  - Delete stub contatti page (id=173871792466)
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

CONTACT_ID  = 120387338578
CONTATTI_ID = 173871792466

NEW_BODY = """<section class="bks-contact">

  <h1>Contact</h1>
  <p>For order enquiries, returns, or any questions about BKS Studio products, write to us at <a href="mailto:crew@bakabo.club">crew@bakabo.club</a>. We reply within 2 business days.</p>

  <h2>Before you write</h2>
  <p>Most questions about production times, shipping, sizing, and returns are answered in the <a href="/pages/help-faq">Help &amp; FAQ</a>.</p>

  <h2>Studio</h2>
  <p>BKS Studio<br>
  Terni, Italy<br>
  <a href="mailto:crew@bakabo.club">crew@bakabo.club</a></p>

  <h2>EU Representative</h2>
  <p>HONSON VENTURES LIMITED<br>
  Gnaftis House flat 102<br>
  Limassol, Mesa Geitonia, 4003<br>
  Cyprus<br>
  <a href="mailto:gpsr@honsonventures.com">gpsr@honsonventures.com</a></p>

</section>"""

# Update contact page
r = requests.put(
    f"{BASE}/pages/{CONTACT_ID}.json",
    headers=HDR,
    json={"page": {"id": CONTACT_ID, "body_html": NEW_BODY}},
    verify=False, timeout=20
)
if r.ok:
    p = r.json().get("page", {})
    print(f"OK — contact page updated (id={p['id']}, handle='{p['handle']}')")
    print(f"     email: crew@bakabo.club confirmed")
else:
    print(f"ERR updating contact page: {r.status_code} {r.text[:200]}")

# Delete stub contatti page
r2 = requests.delete(f"{BASE}/pages/{CONTATTI_ID}.json", headers=HDR, verify=False, timeout=20)
if r2.status_code in (200, 204):
    print(f"OK — stub 'contatti' page (id={CONTATTI_ID}) deleted")
else:
    print(f"ERR deleting contatti page: {r2.status_code} {r2.text[:100]}")
