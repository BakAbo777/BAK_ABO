"""Publish BKS Studio policies and pages to Shopify.

Policies (Settings > Policies via shopPolicyUpdate GraphQL):
  - SHIPPING_POLICY
  - REFUND_POLICY
  - PRIVACY_POLICY
  - TERMS_OF_SERVICE

Pages (Online Store > Pages via REST):
  - about
  - help-faq
  - contact
"""
from __future__ import annotations
import os, re, requests, urllib3, json
from pathlib import Path

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
GQL_URL = f"https://{DOMAIN}/admin/api/{VERSION}/graphql.json"
REST_BASE = f"https://{DOMAIN}/admin/api/{VERSION}"
HDRS_GQL  = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
HDRS_REST = {"X-Shopify-Access-Token": TOKEN}

_ssl_warned = False

def _post(url: str, **kwargs) -> requests.Response:
    global _ssl_warned
    try:
        return requests.post(url, **kwargs, timeout=30)
    except requests.exceptions.SSLError:
        if not _ssl_warned:
            urllib3.disable_warnings()
            _ssl_warned = True
        return requests.post(url, **kwargs, timeout=30, verify=False)

def _get(url: str, **kwargs) -> requests.Response:
    try:
        return requests.get(url, **kwargs, timeout=30)
    except requests.exceptions.SSLError:
        urllib3.disable_warnings()
        return requests.get(url, **kwargs, timeout=30, verify=False)

def _put(url: str, **kwargs) -> requests.Response:
    try:
        return requests.put(url, **kwargs, timeout=30)
    except requests.exceptions.SSLError:
        urllib3.disable_warnings()
        return requests.put(url, **kwargs, timeout=30, verify=False)

def gql(query: str, variables: dict) -> dict:
    r = _post(GQL_URL, json={"query": query, "variables": variables}, headers=HDRS_GQL)
    r.raise_for_status()
    return r.json()


# ── Extract HTML blocks from the docs file ─────────────────────────────────

def extract_sections(doc: str) -> dict[str, str]:
    """Return dict of section_name -> html_body extracted from ```html ... ``` blocks."""
    # Split by section headers
    sections_raw = re.split(r"\n# (\d+\. [^\n]+)", doc)
    result = {}
    for i in range(1, len(sections_raw), 2):
        title = sections_raw[i].strip()
        body  = sections_raw[i + 1]
        html_match = re.search(r"```html\s*(.*?)```", body, re.DOTALL)
        if html_match:
            result[title] = html_match.group(1).strip()
    return result


# ── Publish a Shopify policy ────────────────────────────────────────────────

def publish_policy(policy_type: str, body: str) -> str:
    q = """
    mutation($policy: ShopPolicyInput!) {
      shopPolicyUpdate(policy: $policy) {
        shopPolicy { type url }
        userErrors { field message }
      }
    }"""
    data = gql(q, {"policy": {"type": policy_type, "body": body}})
    errs = data.get("data", {}).get("shopPolicyUpdate", {}).get("userErrors", [])
    if errs:
        return f"ERROR {errs}"
    sp = data.get("data", {}).get("shopPolicyUpdate", {}).get("shopPolicy", {})
    return f"OK url={sp.get('url')}"


# ── Create or update a Shopify page ────────────────────────────────────────

def upsert_page(handle: str, title: str, body_html: str,
                seo_title: str = "", seo_desc: str = "") -> str:
    # Check if page exists
    r = _get(f"{REST_BASE}/pages.json", headers=HDRS_REST,
             params={"handle": handle, "fields": "id,handle"})
    pages = r.json().get("pages", [])
    payload = {
        "page": {
            "handle": handle,
            "title": title,
            "body_html": body_html,
            "published": True,
            "metafields": [],
        }
    }
    if seo_title:
        payload["page"]["metafields"].append(
            {"namespace": "global", "key": "title_tag", "value": seo_title, "type": "single_line_text_field"})
    if seo_desc:
        payload["page"]["metafields"].append(
            {"namespace": "global", "key": "description_tag", "value": seo_desc, "type": "single_line_text_field"})

    if pages:
        pid = pages[0]["id"]
        r2 = _put(f"{REST_BASE}/pages/{pid}.json",
                  json=payload, headers={**HDRS_REST, "Content-Type": "application/json"})
        r2.raise_for_status()
        return f"UPDATED id={pid}"
    else:
        r2 = _post(f"{REST_BASE}/pages.json",
                   json=payload, headers={**HDRS_REST, "Content-Type": "application/json"})
        r2.raise_for_status()
        new_id = r2.json().get("page", {}).get("id")
        return f"CREATED id={new_id}"


def main() -> None:
    doc = (ROOT / "docs" / "BKS_Testi_Sito_Completi_v1.md").read_text(encoding="utf-8")
    sections = extract_sections(doc)

    print("=== POLICIES ===")
    policy_map = {
        "2. SHIPPING POLICY":         "SHIPPING_POLICY",
        "3. RETURNS & REFUND POLICY": "REFUND_POLICY",
        "4. PRIVACY POLICY":          "PRIVACY_POLICY",
        "5. TERMS OF SERVICE":        "TERMS_OF_SERVICE",
    }
    for sec_key, policy_type in policy_map.items():
        matched = next((v for k, v in sections.items() if sec_key in k), None)
        if not matched:
            print(f"  SKIP  {policy_type} — section not found")
            continue
        msg = publish_policy(policy_type, matched)
        print(f"  {policy_type}: {msg}")

    print("\n=== PAGES ===")
    pages_cfg = [
        ("1. ABOUT PAGE",    "about",    "About BKS Studio",
         "About BKS Studio — AI-Art Atelier",
         "BKS Studio is a digital atelier producing AI-generated wearable art. Eight editorial collections, made to order. Designed in Italy, printed on demand."),
        ("6. FAQ / HELP CENTER", "help-faq", "Help & FAQ",
         "FAQ — BKS Studio Help Center",
         "Answers to common questions about BKS Studio orders: production times, shipping, returns, sizing, and the AI-art process."),
        ("7. CONTACT PAGE",  "contact",  "Contact",
         "Contact BKS Studio",
         "Contact BKS Studio for order support, returns, or general enquiries. We reply within 2 business days."),
    ]
    for sec_key, handle, title, seo_title, seo_desc in pages_cfg:
        matched = next((v for k, v in sections.items() if sec_key in k), None)
        if not matched:
            print(f"  SKIP  {handle} — section not found")
            continue
        msg = upsert_page(handle, title, matched, seo_title, seo_desc)
        print(f"  {handle}: {msg}")

    print("\nDone.")


if __name__ == "__main__":
    main()
