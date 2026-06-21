"""Full audit: sold-out variants + bad titles across ALL products."""
import os, re, time, requests, urllib3
from pathlib import Path

urllib3.disable_warnings()  # type: ignore

ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line:
        continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ:
        os.environ[k] = v

DOMAIN = os.environ.get("SHOPIFY_MYSHOPIFY_DOMAIN", "")
TOKEN  = os.environ.get("SHOPIFY_ADMIN_TOKEN", "") or os.environ.get("SHOPIFY_API_TOKEN", "")
BASE   = f"https://{DOMAIN}/admin/api/2024-04"
HDR    = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
print(f"Shop: {DOMAIN} | Token: {TOKEN[:8]}...")

def get(path, **kw):
    return requests.get(f"{BASE}{path}", headers=HDR, verify=False, timeout=20, **kw)

ITALIAN_WORDS = ["taglia","uomo","donna","prezzo","nuovo","con ","del ","nel ","una ","alla "]
OLD_PATTERNS  = ["folklore"]
EMOJI_RE      = re.compile(r"[^\x00-\x7F]")

sold_out   = []  # {id, title, variant_id, qty, policy}
bad_titles = []  # {id, title, reasons}

# Paginate all products
page_info = None
page_num  = 0
total_scanned = 0

while True:
    page_num += 1
    if page_info:
        url = f"/products.json?limit=50&fields=id,title,status,variants&page_info={page_info}"
    else:
        url = "/products.json?limit=50&fields=id,title,status,variants"

    r = get(url)
    prods = r.json().get("products", [])
    if not prods:
        break

    total_scanned += len(prods)

    for p in prods:
        title   = p.get("title", "")
        title_l = title.lower()
        pid     = p["id"]

        has_emoji   = bool(EMOJI_RE.search(title))
        has_italian = any(w in title_l for w in ITALIAN_WORDS)
        has_old     = any(w in title_l for w in OLD_PATTERNS)

        # Sold-out: any variant with deny + qty <= 0
        for v in p.get("variants", []):
            policy = v.get("inventory_policy", "deny")
            qty    = v.get("inventory_quantity", 0) or 0
            if policy == "deny" and qty <= 0:
                sold_out.append({"id": pid, "title": title[:60], "variant_id": v["id"], "qty": qty})
                break

        if has_emoji or has_italian or has_old:
            reasons = []
            if has_emoji:   reasons.append("emoji")
            if has_italian: reasons.append("IT")
            if has_old:     reasons.append("folklore")
            bad_titles.append({"id": pid, "title": title, "reasons": reasons})

    # Cursor-based pagination via Link header
    link = r.headers.get("Link", "")
    next_match = re.search(r'<[^>]+page_info=([^&>]+)[^>]*>;\s*rel="next"', link)
    if next_match:
        page_info = next_match.group(1)
    else:
        break
    time.sleep(0.3)

total = get("/products/count.json").json().get("count", "?")
print(f"Total products: {total} | Scanned: {total_scanned}")

print(f"\n=== SOLD-OUT (deny+qty<=0): {len(sold_out)} ===")
for s in sold_out[:20]:
    print(f"  [id:{s['id']}] {s['title']}")

print(f"\n=== BAD TITLES: {len(bad_titles)} ===")
by_reason = {}
for b in bad_titles:
    key = "+".join(b["reasons"])
    by_reason.setdefault(key, []).append(b)

for reason, items in sorted(by_reason.items()):
    print(f"\n  [{reason}] ({len(items)} products):")
    for item in items[:10]:
        print(f"    [{item['id']}] {item['title'][:80]}")

# Summary
emoji_count    = sum(1 for b in bad_titles if "emoji" in b["reasons"])
folklore_count = sum(1 for b in bad_titles if "folklore" in b["reasons"])
italian_count  = sum(1 for b in bad_titles if "IT" in b["reasons"])
print(f"\n=== SUMMARY ===")
print(f"  Sold-out blocked: {len(sold_out)}")
print(f"  Titles with emoji: {emoji_count}")
print(f"  Titles with Folklore: {folklore_count}")
print(f"  Titles with Italian: {italian_count}")
