"""Replace 'Folklore' → 'Origin' in product body_html and image alt texts.

Run: python scripts/fix_folklore_rename.py [--dry-run]
Default is execute mode. Use --dry-run to preview without changes.
"""
from __future__ import annotations
import os, sys, time, requests, urllib3, argparse
from pathlib import Path

urllib3.disable_warnings()  # type: ignore
ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ or not os.environ[k]:
        os.environ[k] = v

DOMAIN  = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN   = os.environ["SHOPIFY_ADMIN_TOKEN"]
VERSION = os.environ.get("SHOPIFY_API_VERSION", "2024-01")
BASE    = f"https://{DOMAIN}/admin/api/{VERSION}"
HDR     = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

REPLACEMENTS = [
    ("BKS Folklore Collection", "BKS Origin Collection"),
    ("BKS Folklore collection", "BKS Origin collection"),
    ("BKS Folklore", "BKS Origin"),
    ("Folklore Collection", "Origin Collection"),
    ("Folklore collection", "Origin collection"),
    ("Folklore Sneakers", "Origin Sneakers"),
    ("Folklore Puffer", "Origin Puffer"),
    ("Folklore Windbreaker", "Origin Windbreaker"),
    ("Folklore Flip Flop", "Origin Flip Flop"),
    ("Folklore Lounge", "Origin Lounge"),
    ("Folklore Hoodie", "Origin Hoodie"),
    ("Folklore Swim", "Origin Swim"),
    ("Folklore Dress", "Origin Dress"),
    ("Folklore Bag", "Origin Bag"),
    ("Folklore Jacket", "Origin Jacket"),
    ("Collection Folklore", "Collection Origin"),
    ("collection folklore", "collection origin"),
]


def apply_replacements(text: str) -> tuple[str, bool]:
    if not text:
        return text, False
    new_text = text
    for old, new in REPLACEMENTS:
        new_text = new_text.replace(old, new)
    return new_text, new_text != text


def get_all_products():
    products, page_info = [], None
    while True:
        params = {"limit": 250, "fields": "id,handle,title,body_html,images,tags"}
        if page_info:
            params = {"limit": 250, "page_info": page_info,
                      "fields": "id,handle,title,body_html,images,tags"}
        r = requests.get(f"{BASE}/products.json", headers=HDR, params=params,
                         timeout=30, verify=False)
        r.raise_for_status()
        products.extend(r.json().get("products", []))
        link = r.headers.get("Link", "")
        if 'rel="next"' not in link:
            break
        for part in link.split(","):
            if 'rel="next"' in part:
                page_info = part.split("page_info=")[1].split(">")[0]
                break
        time.sleep(0.3)
    return products


def out(msg: str):
    sys.stdout.buffer.write((msg + "\n").encode("utf-8", errors="replace"))
    sys.stdout.flush()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    dry = args.dry_run

    out(f"=== BKS Folklore → Origin Fix ({'DRY RUN' if dry else 'EXECUTE'}) ===\n")

    products = get_all_products()
    out(f"Fetched {len(products)} products\n")

    ok = err = skipped = 0
    for p in products:
        pid = p["id"]
        body = p.get("body_html") or ""
        images = p.get("images") or []

        new_body, body_changed = apply_replacements(body)
        img_updates = []
        for img in images:
            alt = img.get("alt") or ""
            new_alt, alt_changed = apply_replacements(alt)
            if alt_changed:
                img_updates.append({"id": img["id"], "alt": new_alt, "_old": alt})

        if not body_changed and not img_updates:
            skipped += 1
            continue

        out(f"  {p['handle'][:50]}")
        if body_changed:
            out("    BODY updated")
        for img in img_updates:
            out(f"    IMG {img['id']}: {img['_old'][:55]} → {img['alt'][:55]}")

        if dry:
            ok += 1
            continue

        # Update body_html
        if body_changed:
            r = requests.put(
                f"{BASE}/products/{pid}.json",
                headers=HDR,
                json={"product": {"id": pid, "body_html": new_body}},
                timeout=20,
                verify=False,
            )
            if not r.ok:
                out(f"    ERR body: {r.status_code} {r.text[:80]}")
                err += 1
            else:
                out("    body OK")
            time.sleep(0.4)

        # Update image alt texts individually
        for img in img_updates:
            r = requests.put(
                f"{BASE}/products/{pid}/images/{img['id']}.json",
                headers=HDR,
                json={"image": {"id": img["id"], "alt": img["alt"]}},
                timeout=20,
                verify=False,
            )
            if not r.ok:
                out(f"    ERR img {img['id']}: {r.status_code} {r.text[:80]}")
                err += 1
            else:
                out(f"    img {img['id']} OK")
            time.sleep(0.3)

        ok += 1

    out(f"\n=== {ok} products {'would be' if dry else 'were'} updated"
        f" | {err} errors | {skipped} unchanged ===")
    if dry:
        out("Run without --dry-run to apply.")


if __name__ == "__main__":
    main()
