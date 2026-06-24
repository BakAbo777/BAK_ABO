"""
Carica i template PNG locali (I:\\BKS database) su Printify uploads API,
poi scrive i riferimenti in Cloudflare KV come:
  key:   template_bp:{blueprint_id}:{position}
  value: { "preview_url": "...", "printify_id": "...", "bp": ..., "position": "...", "px_w": ..., "px_h": ... }

Il Worker usa questi URL come template blank per images.edit.

Uso:
    python scripts/_upload_templates_to_kv.py           # tutti i template
    python scripts/_upload_templates_to_kv.py --bp 1084 # solo un blueprint
    python scripts/_upload_templates_to_kv.py --dry-run
"""
import argparse, base64, json, struct, sys, time
from pathlib import Path

import requests, urllib3
urllib3.disable_warnings()

ROOT = Path(__file__).resolve().parent.parent
env = {}
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    env[k.strip()] = v.strip().strip('"').strip("'")

PRINTIFY_TOKEN = env.get("PRINTIFY_API_TOKEN", "")
PRINTIFY_SHOP  = env.get("PRINTIFY_SHOP_ID", "12030061")
CF_TOKEN       = env.get("CLOUDFLARE_API_TOKEN", "")
CF_ACCOUNT     = "e796d289f744035eee2641e853d8a5af"
KV_NS_ID       = "8f6b1e4accae47949b2960735d270a3a"
BKS_DATABASE   = Path("I:/BKS database")
BP_MAP_PATH    = ROOT / "ecommerce_automation" / "blueprint_templates.json"
OUT_IDS_PATH   = ROOT / "ecommerce_automation" / "template_upload_ids.json"

PRINTIFY_HDR = {"Authorization": f"Bearer {PRINTIFY_TOKEN}"}
CF_HDR       = {"Authorization": f"Bearer {CF_TOKEN}", "Content-Type": "application/json"}


def get_png_size(path: Path):
    try:
        with open(path, "rb") as f:
            f.read(8); f.read(4)
            if f.read(4) == b"IHDR":
                return struct.unpack(">I", f.read(4))[0], struct.unpack(">I", f.read(4))[0]
    except Exception:
        pass
    return None, None


def upload_to_printify(png_path: Path, file_name: str) -> dict | None:
    """Carica PNG su Printify uploads API. Ritorna {id, preview_url, width, height}."""
    data_b64 = base64.b64encode(png_path.read_bytes()).decode()
    r = requests.post(
        f"https://api.printify.com/v1/uploads/images.json",
        headers={**PRINTIFY_HDR, "Content-Type": "application/json"},
        json={"file_name": file_name, "contents": data_b64},
        timeout=120, verify=False,
    )
    if r.ok:
        return r.json()
    print(f"    ERR Printify upload {png_path.name}: {r.status_code} {r.text[:200]}")
    return None


def kv_put(key: str, value: dict) -> bool:
    """Scrive un valore in Cloudflare KV."""
    r = requests.put(
        f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT}/storage/kv/namespaces/{KV_NS_ID}/values/{key}",
        headers={"Authorization": f"Bearer {CF_TOKEN}"},
        data=json.dumps(value),
        timeout=20, verify=False,
    )
    return r.ok


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--bp",      default=None, help="Filtra per blueprint ID (es. 1084)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    bp_map = json.loads(BP_MAP_PATH.read_text(encoding="utf-8"))
    # Carica IDs già uploadati (per non ri-caricare se già fatto)
    if OUT_IDS_PATH.exists():
        uploaded_ids = json.loads(OUT_IDS_PATH.read_text(encoding="utf-8"))
    else:
        uploaded_ids = {}

    print(f"\nBKS Template Upload to Printify + Cloudflare KV")
    print(f"  Dry run: {args.dry_run}\n")

    stats = {"templates": 0, "uploaded": 0, "cached": 0, "kv_ok": 0, "errors": 0}

    for bp_str, entry in bp_map.items():
        if bp_str.startswith("_"): continue
        if args.bp and bp_str != str(args.bp): continue
        if not entry.get("has_png"): continue

        folder = BKS_DATABASE / entry["folder"]
        if not folder.exists():
            print(f"  SKIP bp={bp_str}: folder non trovato ({entry['folder']})")
            continue

        print(f"  bp={bp_str} — {entry['product']}")

        for position, rel_path in entry.get("png_per_area", {}).items():
            png_path = folder / rel_path.replace("/", "\\")
            if not png_path.exists() or png_path.stat().st_size < 5000:
                print(f"    SKIP {position}: file non trovato")
                stats["errors"] += 1
                continue

            stats["templates"] += 1
            kv_key = f"template_bp:{bp_str}:{position}"
            cache_key = f"{bp_str}:{position}"
            sz_kb = png_path.stat().st_size // 1024
            w, h = get_png_size(png_path)

            # Già caricato?
            if cache_key in uploaded_ids:
                existing = uploaded_ids[cache_key]
                print(f"    CACHED {position:20s} {w}x{h}  {sz_kb}KB -> {existing['printify_id']}")
                stats["cached"] += 1
                if not args.dry_run:
                    kv_put(kv_key, existing)
                    stats["kv_ok"] += 1
                continue

            print(f"    Carico {position:20s} {w}x{h}  {sz_kb}KB ... ", end="", flush=True)

            if args.dry_run:
                print("[dry-run]")
                continue

            file_name = f"bks_template_bp{bp_str}_{position}.png"
            result = upload_to_printify(png_path, file_name)
            time.sleep(0.5)

            if result:
                rec = {
                    "printify_id": result.get("id", ""),
                    "preview_url": result.get("preview_url", ""),
                    "bp": int(bp_str) if bp_str.isdigit() else bp_str,
                    "position": position,
                    "px_w": w, "px_h": h,
                }
                uploaded_ids[cache_key] = rec
                OUT_IDS_PATH.write_text(json.dumps(uploaded_ids, indent=2), encoding="utf-8")

                kv_ok = kv_put(kv_key, rec)
                print(f"OK  id={rec['printify_id']}  kv={'OK' if kv_ok else 'FAIL'}")
                stats["uploaded"] += 1
                if kv_ok: stats["kv_ok"] += 1
            else:
                stats["errors"] += 1
            time.sleep(0.3)

    print(f"\n{'='*60}")
    print(f"Template trovati   : {stats['templates']}")
    print(f"Caricati (nuovi)   : {stats['uploaded']}")
    print(f"Cached (esistenti) : {stats['cached']}")
    print(f"KV aggiornati      : {stats['kv_ok']}")
    print(f"Errori             : {stats['errors']}")
    if not args.dry_run:
        print(f"IDs salvati in     : {OUT_IDS_PATH}")

if __name__ == "__main__":
    main()
