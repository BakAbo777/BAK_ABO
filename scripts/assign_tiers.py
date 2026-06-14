"""Assign bks-subscriber tag to all real customers without a tier tag.

Skips:
- Accounts with Inbox/chat tags (support contacts, not buyers)
- Accounts already tagged bks-subscriber/bks-drop/bks-archive
- Admin account (bakabofirm@gmail.com)
"""
import os, requests, urllib3, time
from pathlib import Path

urllib3.disable_warnings()
ROOT = Path(__file__).resolve().parent.parent
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    k = k.strip(); v = v.strip().strip('"').strip("'")
    if k not in os.environ or not os.environ[k]: os.environ[k] = v

DOMAIN  = os.environ["SHOPIFY_MYSHOPIFY_DOMAIN"]
TOKEN   = os.environ["SHOPIFY_ADMIN_TOKEN"]
VERSION = os.environ.get("SHOPIFY_API_VERSION", "2025-01")
BASE    = f"https://{DOMAIN}/admin/api/{VERSION}"
HDR     = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

ADMIN_EMAILS = {"bakabofirm@gmail.com", "crew@bakabo.club"}

SKIP_TAGS = {
    "inbox online store chat", "inbox shop chat", "inbox", "shop chat",
}

BKS_TIERS = {"bks-subscriber", "bks-drop", "bks-archive"}


def _get(path, params=None):
    r = requests.get(f"{BASE}{path}", headers=HDR, params=params, timeout=20, verify=False)
    r.raise_for_status()
    return r.json()


def _put(path, data):
    for attempt in range(4):
        r = requests.put(f"{BASE}{path}", headers=HDR, json=data, timeout=20, verify=False)
        if r.status_code == 429:
            time.sleep(2 ** attempt + 1)
            continue
        r.raise_for_status()
        return r.json()


def is_chat_account(tags_str: str) -> bool:
    tags_lower = [t.strip().lower() for t in tags_str.split(",")]
    return any(t in SKIP_TAGS for t in tags_lower)


def has_bks_tier(tags_str: str) -> bool:
    tags_lower = {t.strip().lower() for t in tags_str.split(",")}
    return bool(tags_lower & BKS_TIERS)


def add_tag(existing: str, new_tag: str) -> str:
    tags = [t.strip() for t in existing.split(",") if t.strip()]
    if new_tag not in tags:
        tags.append(new_tag)
    return ", ".join(tags)


def main():
    print("=== BKS Tier Assignment ===\n")

    data = _get("/customers.json", {
        "limit": 250,
        "fields": "id,first_name,last_name,email,orders_count,tags"
    })
    customers = data.get("customers", [])
    print(f"Totale clienti: {len(customers)}\n")

    assigned = []
    skipped  = []

    for c in customers:
        cid    = c["id"]
        name   = f"{c['first_name'] or ''} {c['last_name'] or ''}".strip() or c["email"]
        email  = c["email"]
        tags   = c.get("tags") or ""
        orders = c["orders_count"]

        if email in ADMIN_EMAILS:
            skipped.append((name, email, "admin"))
            continue

        if is_chat_account(tags):
            skipped.append((name, email, "chat"))
            continue

        if has_bks_tier(tags):
            skipped.append((name, email, f"tier gia' assegnato: {tags}"))
            continue

        new_tags = add_tag(tags, "bks-subscriber")
        _put(f"/customers/{cid}.json", {"customer": {"id": cid, "tags": new_tags}})
        assigned.append((name, email, orders))
        print(f"  [OK]  {name} <{email}>  (ordini: {orders})")
        time.sleep(0.35)

    print(f"\n--- Saltati ({len(skipped)}) ---")
    for name, email, reason in skipped:
        print(f"  [SKIP]  {name} <{email}>  — {reason}")

    print(f"\nDone — bks-subscriber assegnato: {len(assigned)}  saltati: {len(skipped)}")


if __name__ == "__main__":
    main()
