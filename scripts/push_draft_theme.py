"""Crea un nuovo tema Shopify (role=unpublished) e carica tutti i file di _merged_tm04."""
from __future__ import annotations
import os, sys, requests, urllib3, time, base64
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
VERSION = os.environ.get("SHOPIFY_API_VERSION", "2025-01")
BASE    = f"https://{DOMAIN}/admin/api/{VERSION}"
HDR     = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

THEME_DIR = ROOT / "04_TEMA_SHOPIFY" / "_merged_tm04"
THEME_NAME = "BKS TM04 FULL LINKS UPDATE 16JUN2026 (draft)"
TOP_DIRS = ["assets", "blocks", "config", "layout", "locales", "sections", "snippets", "templates"]
BINARY_EXT = {"png","jpg","jpeg","gif","webp","svg","woff","woff2","ttf","ico","eot"}


def create_theme() -> dict:
    r = requests.post(
        f"{BASE}/themes.json", headers=HDR, timeout=30, verify=False,
        json={"theme": {"name": THEME_NAME, "role": "unpublished"}},
    )
    r.raise_for_status()
    return r.json()["theme"]


def collect_files() -> list[Path]:
    files = []
    for d in TOP_DIRS:
        base = THEME_DIR / d
        if base.exists():
            files.extend(p for p in base.rglob("*") if p.is_file())
    return files


def upload(theme_id: str, path: Path, dest_key: str) -> bool:
    content = path.read_bytes()
    is_binary = dest_key.rsplit(".", 1)[-1].lower() in BINARY_EXT
    payload = {
        "asset": {
            "key": dest_key,
            **({"attachment": base64.b64encode(content).decode()} if is_binary
               else {"value": content.decode("utf-8")}),
        }
    }
    for attempt in range(5):
        r = requests.put(
            f"{BASE}/themes/{theme_id}/assets.json",
            headers=HDR, json=payload, timeout=60, verify=False,
        )
        if r.status_code == 429:
            wait = float(r.headers.get("Retry-After", 2 ** attempt + 1))
            time.sleep(wait)
            continue
        if r.ok:
            return True
        print(f"  ERR   {dest_key}  [{r.status_code}] {r.text[:160]}")
        return False
    print(f"  ERR   {dest_key}  rate-limit retries exhausted")
    return False


def main():
    print("=== Creazione nuovo tema draft (unpublished) ===")
    theme = create_theme()
    theme_id = theme["id"]
    print(f"Tema creato: id={theme_id}  name={theme['name']}\n")

    files = collect_files()
    print(f"File da caricare: {len(files)}\n")

    ok = err = 0
    for i, path in enumerate(files, 1):
        dest_key = path.relative_to(THEME_DIR).as_posix()
        if upload(theme_id, path, dest_key):
            ok += 1
        else:
            err += 1
        if i % 25 == 0 or i == len(files):
            print(f"  [{i}/{len(files)}] ok={ok} err={err}")
        time.sleep(0.55)

    print(f"\n=== Completato: {ok} OK | {err} ERRORI ===")
    print(f"Theme ID: {theme_id}")
    print(f"Editor:   https://{DOMAIN}/admin/themes/{theme_id}/editor")
    print(f"Preview:  https://{os.environ.get('PRIMARY_DOMAIN', DOMAIN)}/?preview_theme_id={theme_id}")


if __name__ == "__main__":
    main()
