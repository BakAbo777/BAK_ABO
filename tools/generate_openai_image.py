#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate a BakAbo/BKS image asset with the OpenAI Images API."""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from urllib.request import urlopen

import requests

try:
    import certifi
except ImportError:  # pragma: no cover - optional runtime dependency
    certifi = None

try:
    import urllib3
except ImportError:  # pragma: no cover - requests normally provides urllib3
    urllib3 = None


ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"
OUT_DIR = ROOT / "output" / "openai_images"
API_URL = "https://api.openai.com/v1/images/generations"


def load_local_env(path: Path = ENV_PATH) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def slugify(value: str) -> str:
    clean = "".join(char.lower() if char.isalnum() else "-" for char in value)
    return "-".join(part for part in clean.split("-") if part) or "bks-image"


def read_prompt(args: argparse.Namespace) -> str:
    if args.prompt_file:
        return Path(args.prompt_file).read_text(encoding="utf-8").strip()
    return (args.prompt or "").strip()


def write_image_from_payload(item: dict[str, str], out_path: Path) -> None:
    if item.get("b64_json"):
        out_path.write_bytes(base64.b64decode(item["b64_json"]))
        return
    if item.get("url"):
        with urlopen(item["url"], timeout=60) as response:
            out_path.write_bytes(response.read())
        return
    raise RuntimeError("La risposta OpenAI non contiene b64_json o url.")


def parse_openai_error(response: requests.Response) -> dict[str, str]:
    try:
        payload = response.json()
    except ValueError:
        return {
            "message": response.text[:2000],
            "type": "http_error",
            "code": str(response.status_code),
        }
    error = payload.get("error", payload)
    if not isinstance(error, dict):
        return {"message": str(error), "type": "http_error", "code": str(response.status_code)}
    code = error.get("code") or response.status_code
    return {
        "message": str(error.get("message", "")),
        "type": str(error.get("type", "")),
        "code": str(code),
    }


def write_error_meta(path: Path, args: argparse.Namespace, prompt: str, error: dict[str, str]) -> None:
    path.write_text(
        json.dumps(
            {
                "created_at": datetime.now().isoformat(timespec="seconds"),
                "status": "error",
                "provider": "openai",
                "model": args.model,
                "size": args.size,
                "quality": args.quality,
                "format": args.format,
                "background": args.background,
                "prompt": prompt,
                "error": error,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate one image with OpenAI for BakAbo/BKS.")
    parser.add_argument("--prompt", default="", help="Prompt text. Use --prompt-file for longer prompts.")
    parser.add_argument("--prompt-file", default="", help="Path to a UTF-8 prompt file.")
    parser.add_argument("--name", default="bks-image", help="Output asset name.")
    parser.add_argument("--model", default="gpt-image-1.5", help="OpenAI image model.")
    parser.add_argument("--size", default="1024x1536", help="Image size, e.g. 1024x1024, 1024x1536, 1536x1024.")
    parser.add_argument("--quality", default="medium", choices=["low", "medium", "high", "auto"])
    parser.add_argument("--format", default="png", choices=["png", "webp", "jpeg"])
    parser.add_argument("--background", default="opaque", choices=["auto", "opaque", "transparent"])
    parser.add_argument("--no-verify-ssl", action="store_true", help="Bypass TLS verification for local certificate problems.")
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    return parser.parse_args()


def ssl_verify_setting(no_verify_ssl: bool) -> bool | str:
    if no_verify_ssl:
        if urllib3 is not None:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        return False
    if certifi is not None:
        return certifi.where()
    return True


def main() -> int:
    load_local_env()
    args = parse_args()
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        print("Errore: OPENAI_API_KEY mancante in .env o variabili ambiente.")
        return 1

    prompt = read_prompt(args)
    if not prompt:
        print("Errore: prompt vuoto.")
        return 1

    args.out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stem = f"{slugify(args.name)}_{stamp}"
    image_path = args.out_dir / f"{stem}.{args.format}"
    meta_path = args.out_dir / f"{stem}.json"
    error_path = args.out_dir / f"{stem}.error.json"

    payload: dict[str, object] = {
        "model": args.model,
        "prompt": prompt,
        "size": args.size,
        "quality": args.quality,
        "n": 1,
        "output_format": args.format,
    }
    if args.background != "auto":
        payload["background"] = args.background

    verify = ssl_verify_setting(args.no_verify_ssl)
    try:
        response = requests.post(
            API_URL,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json=payload,
            timeout=180,
            verify=verify,
        )
    except requests.exceptions.SSLError as exc:
        write_error_meta(
            error_path,
            args,
            prompt,
            {
                "message": str(exc),
                "type": "ssl_error",
                "code": "ssl_verification_failed",
            },
        )
        print("Errore SSL verso OpenAI.")
        print("Rimedio consigliato: aggiorna certifi oppure usa temporaneamente --no-verify-ssl dal cruscotto solo su questa macchina.")
        print(str(exc))
        print(f"Log errore: {error_path}")
        return 2
    except requests.exceptions.RequestException as exc:
        write_error_meta(
            error_path,
            args,
            prompt,
            {
                "message": str(exc),
                "type": "network_error",
                "code": "openai_request_failed",
            },
        )
        print("Errore rete verso OpenAI.")
        print(str(exc))
        print(f"Log errore: {error_path}")
        return 3
    try:
        response.raise_for_status()
    except requests.HTTPError:
        error = parse_openai_error(response)
        write_error_meta(error_path, args, prompt, error)
        print(f"Errore OpenAI API: {error.get('code') or response.status_code}")
        if error.get("message"):
            print(error["message"])
        if error.get("code") == "billing_hard_limit_reached":
            print("Limite di fatturazione OpenAI raggiunto: aumenta il limite/budget del progetto o usa una chiave API con credito disponibile.")
        print(f"Log errore: {error_path}")
        return 4

    data = response.json()
    write_image_from_payload(data["data"][0], image_path)
    meta_path.write_text(
        json.dumps(
            {
                "created_at": datetime.now().isoformat(timespec="seconds"),
                "image": str(image_path.resolve()),
                "model": args.model,
                "size": args.size,
                "quality": args.quality,
                "format": args.format,
                "background": args.background,
                "prompt": prompt,
                "response_usage": data.get("usage", {}),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(image_path)
    print(meta_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
