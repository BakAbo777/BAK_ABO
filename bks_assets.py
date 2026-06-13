from __future__ import annotations

import json
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
THEME_DIR = BASE_DIR / "04_TEMA_SHOPIFY"
CATALOG_DIR = BASE_DIR / "collezioni_csv"
IMAGE_FACTORY_DIR = BASE_DIR / "BAKABO_IMAGE_FACTORY_v1.1"
ACTIVE_ASSETS_PATH = OUTPUT_DIR / "bks_active_assets.json"


def _resolve_path(value: str | Path | None) -> Path | None:
    if not value:
        return None
    path = Path(value)
    if not path.is_absolute():
        path = BASE_DIR / path
    return path


def relative_to_base(path: str | Path | None) -> str:
    resolved = _resolve_path(path)
    if resolved is None:
        return ""
    try:
        return str(resolved.resolve().relative_to(BASE_DIR.resolve()))
    except ValueError:
        return str(resolved)


def _load_config() -> dict[str, Any]:
    if not ACTIVE_ASSETS_PATH.exists():
        return {}
    try:
        data = json.loads(ACTIVE_ASSETS_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def discover_theme_zips() -> list[Path]:
    if not THEME_DIR.exists():
        return []
    return sorted(THEME_DIR.glob("*.zip"), key=lambda item: item.stat().st_mtime, reverse=True)


def discover_catalog_csvs() -> list[Path]:
    files: list[Path] = []
    if CATALOG_DIR.exists():
        files.extend(CATALOG_DIR.glob("*.csv"))
    files.extend(BASE_DIR.glob("BKS_COLLEZIONE_*.csv"))
    unique = {item.resolve(): item for item in files if item.exists()}
    return sorted(unique.values(), key=lambda item: item.stat().st_mtime, reverse=True)


def latest_theme_zip() -> Path:
    files = discover_theme_zips()
    return files[0] if files else THEME_DIR / "BKS_TM03_clean_12JUN2026.zip"


def latest_catalog_csv() -> Path:
    files = discover_catalog_csvs()
    return files[0] if files else CATALOG_DIR / "collezione 12_06_2026.csv"


def active_theme_zip() -> Path:
    configured = _resolve_path(_load_config().get("theme_zip"))
    if configured and configured.exists():
        return configured
    return latest_theme_zip()


def active_catalog_csv() -> Path:
    configured = _resolve_path(_load_config().get("catalog_csv"))
    if configured and configured.exists():
        return configured
    return latest_catalog_csv()


def active_image_factory_dir() -> Path:
    configured = _resolve_path(_load_config().get("image_factory_dir"))
    if configured and configured.exists():
        return configured
    return IMAGE_FACTORY_DIR


def load_active_assets() -> dict[str, str]:
    return {
        "theme_zip": relative_to_base(active_theme_zip()),
        "catalog_csv": relative_to_base(active_catalog_csv()),
        "image_factory_dir": relative_to_base(active_image_factory_dir()),
    }


def save_active_assets(
    *,
    theme_zip: str | Path | None = None,
    catalog_csv: str | Path | None = None,
    image_factory_dir: str | Path | None = None,
) -> dict[str, str]:
    current = load_active_assets()
    if theme_zip is not None:
        current["theme_zip"] = relative_to_base(theme_zip)
    if catalog_csv is not None:
        current["catalog_csv"] = relative_to_base(catalog_csv)
    if image_factory_dir is not None:
        current["image_factory_dir"] = relative_to_base(image_factory_dir)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ACTIVE_ASSETS_PATH.write_text(json.dumps(current, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return current
