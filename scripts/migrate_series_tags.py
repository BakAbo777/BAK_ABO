"""Migrate legacy series:* tags to new collection:* tags.

Migration map:
  series:brut              → collection:glyph
  series:naif              → collection:origin
  series:neo-dada          → collection:flag
  series:neo-expressionism → collection:marker
  series:arcade            → collection:token
  series:islands           → collection:riviera
  series:hyperrealism      → collection:hours

Run with --dry-run first to preview. Use --execute to apply.
Exports CSV before making any changes.
"""
from __future__ import annotations
import os, sys, csv, time, requests, urllib3, argparse
from pathlib import Path

urllib3.disable_warnings()  # type: ignore
ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ or not os.environ[k]: os.environ[k] = v

DOMAIN  = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN   = os.environ["SHOPIFY_ADMIN_TOKEN"]
VERSION = os.environ.get("SHOPIFY_API_VERSION", "2024-01")
BASE    = f"https://{DOMAIN}/admin/api/{VERSION}"
HDR     = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

# Series → Collection mapping
SERIES_MAP = {
    "series:brut":              "collection:glyph",
    "series:naif":              "collection:origin",
    "series:neo-dada":          "collection:flag",
    "series:neo-expressionism": "collection:marker",
    "series:arcade":            "collection:token",
    "series:islands":           "collection:riviera",
    "series:hyperrealism":      "collection:hours",
}
# Tags to remove without replacement (fully superseded)
REMOVE_ONLY = {"series:optical", "series:brut", "series:naif"}


def get_all_products():
    products, page_info = [], None
    while True:
        params = {"limit": 250, "fields": "id,handle,title,tags"}
        if page_info:
            params = {"limit": 250, "page_info": page_info, "fields": "id,handle,title,tags"}
        r = requests.get(f"{BASE}/products.json", headers=HDR, params=params, timeout=30, verify=False)
        r.raise_for_status()
        data = r.json().get("products", [])
        products.extend(data)
        link = r.headers.get("Link", "")
        if 'rel="next"' not in link:
            break
        for part in link.split(","):
            if 'rel="next"' in part:
                page_info = part.split("page_info=")[1].split(">")[0]
                break
        time.sleep(0.3)
    return products


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true", help="Apply changes (default: dry-run)")
    args = parser.parse_args()
    dry = not args.execute

    print("=== BKS Series Tag Migration ===")
    print(f"Mode: {'DRY RUN' if dry else 'EXECUTE'}\n")

    products = get_all_products()
    print(f"Fetched {len(products)} products\n")

    # Export CSV snapshot before any changes
    csv_path = ROOT / "output" / "pre_migration_tags_snapshot.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["handle", "title", "tags"])
        for p in products:
            w.writerow([p["handle"], p["title"], p.get("tags", "")])
    print(f"CSV snapshot: {csv_path}\n")

    ok = err = skipped = 0
    for p in products:
        tags = [t.strip() for t in p.get("tags", "").split(",") if t.strip()]
        old_tags = set(tags)

        new_tags = []
        changed = False
        for tag in tags:
            tl = tag.lower()
            if tl in SERIES_MAP:
                new_col = SERIES_MAP[tl]
                # Add new collection tag only if not already present
                if new_col not in [t.lower() for t in tags]:
                    new_tags.append(new_col)
                # Keep the old series tag with archive prefix instead of deleting
                new_tags.append("archive:" + tl.replace("series:", ""))
                changed = True
            else:
                new_tags.append(tag)

        if not changed:
            skipped += 1
            continue

        print(f"  {p['handle'][:45]}")
        print(f"    OLD: {', '.join(sorted(old_tags - set(new_tags)))}")
        print(f"    ADD: {', '.join(sorted(set(new_tags) - old_tags))}")

        if not dry:
            tags_str = ", ".join(new_tags)
            r = requests.put(
                f"{BASE}/products/{p['id']}.json",
                headers=HDR,
                json={"product": {"id": p["id"], "tags": tags_str}},
                timeout=20,
                verify=False,
            )
            if r.ok:
                ok += 1
            else:
                print(f"    ERR: {r.status_code} {r.text[:80]}")
                err += 1
            time.sleep(0.4)
        else:
            ok += 1

    print(f"\n=== {ok} products {'would be' if dry else 'were'} updated | {err} errors | {skipped} no series tags ===")
    if dry:
        print("Run with --execute to apply changes.")


if __name__ == "__main__":
    main()
