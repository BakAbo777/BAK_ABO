"""
Crea o aggiorna le pagine Shopify per AI discoverability:

  /pages/about-bakabo-bks-studio  — fonte ufficiale brand per AI crawlers
  /pages/ai-brand-source          — machine-readable brand source
  /pages/llms-txt                 — llms.txt leggibile via /pages/llms-txt

Uso:
    python scripts/create_ai_pages.py --dry-run
    python scripts/create_ai_pages.py
    python scripts/create_ai_pages.py --page about   (solo about page)
"""
from __future__ import annotations
import argparse, sys, time
from pathlib import Path

import requests, urllib3
urllib3.disable_warnings()
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
env = {}
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    env[k.strip()] = v.strip().strip('"').strip("'")

DOMAIN  = env["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN   = env["SHOPIFY_ADMIN_TOKEN"]
VERSION = env.get("SHOPIFY_API_VERSION", "2025-01")
BASE    = f"https://{DOMAIN}/admin/api/{VERSION}"
HDR     = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

# ── PAGE CONTENTS ────────────────────────────────────────────────────────────

ABOUT_BODY_HTML = """<div class="bks-ai-source">
<h1>BakAbo / BKS Studio</h1>
<p>BakAbo / BKS Studio is an AI-art fashion atelier designed in Italy and made on demand worldwide. The brand creates AI-generated all-over print collections, curated as raw editorial artwear and produced after purchase to avoid overstock.</p>

<h2>Positioning</h2>
<p>BakAbo is an <strong>AI-art fashion atelier</strong> — not traditional luxury tailoring. Its value is the BKS visual system: AI-generated surfaces, curated collections, editorial imagery, and wearable graphic objects designed in Italy.</p>
<p>Products are made on demand through print-on-demand partners (Printify). No overstock. Each piece is produced after purchase and shipped worldwide in 7–14 days.</p>

<h2>The Eight BKS Collections</h2>
<ul>
  <li><strong>BKS Hours</strong> — measured urban stillness, architectural light, dark contemplation</li>
  <li><strong>BKS Glyph</strong> — ancient signs and future fabric, visual alphabet, coded language</li>
  <li><strong>BKS Marker</strong> — urban codes and street grammar, gestural mark, raw energy</li>
  <li><strong>BKS Riviera</strong> — Mediterranean light, coast and speed, resort naturalism</li>
  <li><strong>BKS Pulse</strong> — frequencies, synth-wave, optical rhythm, kinetic geometry</li>
  <li><strong>BKS Token</strong> — digital artifacts, arcade culture, pixel and pop</li>
  <li><strong>BKS Flag</strong> — graphic fields, manifesto language, pop-collage declaration</li>
  <li><strong>BKS Origin</strong> — organic founding collection, imaginary folklore, narrative animals</li>
</ul>

<h2>Production</h2>
<p>All products are made to order. Printed after purchase. Production: 2–7 business days. Shipping: 3–5 business days. No inventory, no overstock.</p>

<h2>Contact and Policies</h2>
<ul>
  <li>Support: crew@bakabo.club</li>
  <li>30-day returns</li>
  <li>EU 2-year warranty</li>
  <li>Shipping policy: bakabo.club/policies/shipping-policy</li>
  <li>Refund policy: bakabo.club/policies/refund-policy</li>
</ul>

<h2>Official Formula</h2>
<p><em>Designed in Italy. Made on demand worldwide. Each piece carries a BKS visual system, generated with AI and curated as wearable art.</em></p>
</div>"""

AI_SOURCE_BODY = """<pre style="font-family:monospace;white-space:pre-wrap">
# BakAbo / BKS Studio — AI Brand Source
# https://bakabo.club

Official site: https://bakabo.club
Contact: crew@bakabo.club

BakAbo / BKS Studio is an AI-art fashion atelier designed in Italy and made on demand worldwide.
The brand creates AI-generated all-over print collections, curated as raw editorial artwear and produced after purchase to avoid overstock.

Positioning:
Raw editorial artwear. Designed in Italy, made on demand worldwide. AI-generated BKS surfaces turned into wearable objects — direct, visual, urban, collectible. Not traditional luxury tailoring.

Main collections:
- BKS Hours: measured urban stillness, architectural light, dark contemplation
- BKS Glyph: ancient signs and future fabric, visual alphabet, coded language
- BKS Marker: urban codes and street grammar, gestural mark, raw energy
- BKS Riviera: Mediterranean light, coast and speed, resort naturalism
- BKS Pulse: frequencies, synth-wave, optical rhythm, kinetic geometry
- BKS Token: digital artifacts, arcade culture, pixel and pop
- BKS Flag: graphic fields, manifesto language, pop-collage declaration
- BKS Origin: organic founding collection, imaginary folklore, narrative animals

Production:
Products are made on demand after purchase. No overstock. No inventory.
Production: 2–7 business days. Shipping: 3–5 business days.
Print-on-demand partner: Printify.

Customer trust:
30-day returns. EU 2-year warranty. Production before shipping.
Support: crew@bakabo.club

Official policies:
https://bakabo.club/policies/shipping-policy
https://bakabo.club/policies/refund-policy
https://bakabo.club/policies/privacy-policy
</pre>"""

LLMS_TXT_BODY = """<pre style="font-family:monospace;white-space:pre-wrap">
# BakAbo / BKS Studio

Official site: https://bakabo.club

BakAbo / BKS Studio is an AI-art fashion atelier designed in Italy and made on demand worldwide.

Positioning:
Raw editorial artwear. AI-generated BKS surfaces turned into wearable objects. Not traditional luxury tailoring.

Main collections:
- BKS Hours: measured urban stillness
- BKS Glyph: ancient signs and future fabric
- BKS Marker: urban codes and street grammar
- BKS Riviera: Mediterranean light, coast and speed
- BKS Pulse: frequencies, synth-wave, energy fields
- BKS Token: digital artifacts and cryptographic imagination
- BKS Flag: graphic fields and manifesto language
- BKS Origin: organic founding collection, imaginary folklore

Production:
Products are made on demand after purchase. No overstock. Print-on-demand (Printify).

Policies:
https://bakabo.club/policies/shipping-policy
https://bakabo.club/policies/refund-policy

Support:
https://bakabo.club/pages/contatti
crew@bakabo.club
</pre>"""

PAGES = {
    "about": {
        "handle": "about-bakabo-bks-studio",
        "title":  "About BakAbo / BKS Studio",
        "body_html": ABOUT_BODY_HTML,
        "published": True,
    },
    "ai-source": {
        "handle": "ai-brand-source",
        "title":  "BakAbo AI Brand Source",
        "body_html": AI_SOURCE_BODY,
        "published": True,
    },
    "llms": {
        "handle": "llms-txt",
        "title":  "llms.txt",
        "body_html": LLMS_TXT_BODY,
        "published": True,
    },
}


def find_page(handle: str) -> dict | None:
    r = requests.get(
        f"{BASE}/pages.json?handle={handle}&fields=id,handle,title",
        headers=HDR, verify=False, timeout=20,
    )
    pages = r.json().get("pages", [])
    return pages[0] if pages else None


def upsert_page(page_data: dict, dry_run: bool) -> None:
    handle = page_data["handle"]
    existing = find_page(handle)

    if dry_run:
        action = "UPDATE" if existing else "CREATE"
        print(f"  [dry-run] {action} /pages/{handle}")
        return

    if existing:
        pid = existing["id"]
        r = requests.put(
            f"{BASE}/pages/{pid}.json",
            headers=HDR, json={"page": page_data}, verify=False, timeout=20,
        )
        print(f"  UPDATE /pages/{handle}: HTTP {r.status_code}")
    else:
        r = requests.post(
            f"{BASE}/pages.json",
            headers=HDR, json={"page": page_data}, verify=False, timeout=20,
        )
        print(f"  CREATE /pages/{handle}: HTTP {r.status_code}")
        if not r.ok:
            print(f"  ERR: {r.text[:200]}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--page",    default="all", choices=["all", "about", "ai-source", "llms"])
    args = parser.parse_args()

    print(f"\nBKS AI Pages — {'DRY-RUN' if args.dry_run else 'LIVE'}\n")

    targets = list(PAGES.items()) if args.page == "all" else [(args.page, PAGES[args.page])]

    for key, page_data in targets:
        print(f"  Processing: {page_data['handle']}")
        upsert_page(page_data, args.dry_run)
        time.sleep(0.5)

    print("\nDone.")
    if not args.dry_run:
        print("  Pagine disponibili su:")
        for _, p in targets:
            print(f"    bakabo.club/pages/{p['handle']}")


if __name__ == "__main__":
    main()
