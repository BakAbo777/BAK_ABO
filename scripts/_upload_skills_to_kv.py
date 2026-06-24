"""
Carica tutte le BKS SKILL.md in Cloudflare KV.
Chiave KV: skill:<nome-skill>  (es. skill:bakabo-armocromista)

Il Worker può poi leggerle via:  await memory.kv.get("skill:bakabo-armocromista", "text")

Uso:
    python scripts/_upload_skills_to_kv.py              (tutte le skill)
    python scripts/_upload_skills_to_kv.py --list       (elenca senza caricare)
    python scripts/_upload_skills_to_kv.py --skill bakabo-armocromista
"""
from __future__ import annotations
import argparse, json, sys, time
from pathlib import Path

import requests, urllib3
urllib3.disable_warnings()
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT       = Path(__file__).resolve().parent.parent
SKILL_ROOT = ROOT / "BKS_SKILL"
env = {}
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    env[k.strip()] = v.strip().strip('"').strip("'")

CF_ACCOUNT_ID = env.get("CLOUDFLARE_ACCOUNT_ID", "e796d289f744035eee2641e853d8a5af")
CF_API_TOKEN  = env.get("CLOUDFLARE_API_TOKEN", "")
KV_NS_ID      = "8f6b1e4accae47949b2960735d270a3a"

CF_HDR = {"Authorization": f"Bearer {CF_API_TOKEN}", "Content-Type": "application/json"}
KV_BASE = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/storage/kv/namespaces/{KV_NS_ID}"


def collect_skills() -> list[tuple[str, Path]]:
    """Raccoglie (skill-name, path) per tutte le SKILL.md."""
    skills = []
    for md in sorted(SKILL_ROOT.rglob("SKILL.md")):
        # nome da directory parent (es. bakabo-armocromista)
        name = md.parent.name
        skills.append((name, md))
    # Aggiungi il theme skill
    for md in sorted((SKILL_ROOT / "theme").glob("*.md")):
        name = md.stem  # bks-tm04-theme-skill
        skills.append((name, md))
    return skills


def kv_put(key: str, value: str) -> bool:
    r = requests.put(
        f"{KV_BASE}/values/{requests.utils.quote(key, safe='')}",
        headers={"Authorization": f"Bearer {CF_API_TOKEN}"},
        data=value.encode("utf-8"),
        timeout=30,
        verify=False,
    )
    return r.ok


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--list",  action="store_true")
    parser.add_argument("--skill", default=None, help="Carica solo questa skill")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not CF_API_TOKEN:
        print("ERR: CLOUDFLARE_API_TOKEN mancante nel .env")
        sys.exit(1)

    skills = collect_skills()
    if args.skill:
        skills = [(n, p) for n, p in skills if n == args.skill]

    if args.list:
        for name, path in skills:
            size = path.stat().st_size
            print(f"  {name:50s}  {size:>7,} bytes")
        print(f"\n{len(skills)} skill files trovati")
        return

    print(f"BKS Skills → Cloudflare KV  [{len(skills)} skill]")
    print(f"KV namespace: {KV_NS_ID}")
    print("=" * 65)

    ok, err = 0, 0
    for name, path in skills:
        content = path.read_text(encoding="utf-8")
        kv_key  = f"skill:{name}"
        size    = len(content)

        if args.dry_run:
            print(f"  DRY  {kv_key}  ({size:,} chars)")
            ok += 1
            continue

        success = kv_put(kv_key, content)
        if success:
            ok += 1
            print(f"  OK   {kv_key}  ({size:,} chars)")
        else:
            err += 1
            print(f"  ERR  {kv_key}")
        time.sleep(0.15)

    print(f"\n{'DRY-RUN ' if args.dry_run else ''}Caricati: {ok}  Errori: {err}")
    if ok and not args.dry_run:
        print("Skill disponibili nel Worker via: await memory.kv.get('skill:<name>', 'text')")


if __name__ == "__main__":
    main()
