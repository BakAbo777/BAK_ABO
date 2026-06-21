"""Upload BKS member area files to the active Shopify theme via Assets API."""
from __future__ import annotations
import os, requests, urllib3, time, json
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
BASE    = f"https://{DOMAIN}/admin/api/{VERSION}"
HDR     = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
urllib3.disable_warnings()  # type: ignore

THEME_DIR = ROOT / "04_TEMA_SHOPIFY"

FILES = [
    ("assets/bks-member.css",                   "assets/bks-member.css"),
    ("assets/bks-member.js",                    "assets/bks-member.js"),
    ("snippets/bks-member-tier.liquid",         "snippets/bks-member-tier.liquid"),
    ("snippets/bks-member-tracker.liquid",      "snippets/bks-member-tracker.liquid"),
    ("snippets/bks-member-archive.liquid",      "snippets/bks-member-archive.liquid"),
    ("sections/bks-member-dashboard.liquid",    "sections/bks-member-dashboard.liquid"),
    ("sections/bks-member-archive-page.liquid", "sections/bks-member-archive-page.liquid"),
    ("templates/customers/account.bks-member.json", "templates/customers/account.bks-member.json"),
    ("templates/page.bks-archive.json",         "templates/page.bks-archive.json"),
]


def _req(method: str, path: str, **kwargs) -> dict:
    url = f"{BASE}{path}"
    for attempt in range(4):
        r = getattr(requests, method)(url, headers=HDR, timeout=30, verify=False, **kwargs)
        if r.status_code == 429:
            wait = 2 ** attempt + 2
            print(f"    rate limited — attendo {wait}s")
            time.sleep(wait)
            continue
        r.raise_for_status()
        return r.json()
    r.raise_for_status()


def get_active_theme_id() -> str:
    data = _req("get", "/themes.json")
    for theme in data.get("themes", []):
        if theme.get("role") == "main":
            return str(theme["id"])
    raise RuntimeError("Nessun tema attivo trovato")


def upload_asset(theme_id: str, key: str, content: str) -> None:
    _req("put", f"/themes/{theme_id}/assets.json",
         json={"asset": {"key": key, "value": content}})


def main() -> None:
    print("=== BKS Member Area — Deploy ===\n")

    theme_id = get_active_theme_id()
    print(f"Tema attivo: id={theme_id}\n")

    ok = 0
    err = 0
    for local_rel, theme_key in FILES:
        local_path = THEME_DIR / local_rel
        if not local_path.exists():
            print(f"  [MISS]  {theme_key}")
            err += 1
            continue
        content = local_path.read_text(encoding="utf-8")
        try:
            upload_asset(theme_id, theme_key, content)
            print(f"  [OK]    {theme_key}")
            ok += 1
        except Exception as e:
            print(f"  [ERR]   {theme_key}: {e}")
            err += 1
        time.sleep(0.4)

    print(f"\nDone — OK: {ok}  Errori: {err}")
    if ok == len(FILES):
        print("\nTutti i file caricati. Attiva il template:")
        print("  Shopify Admin → Customers → seleziona un cliente → Edit → Template: bks-member")
        print("  Oppure rinomina account.bks-member.json → account.json nel tema.")


if __name__ == "__main__":
    main()
