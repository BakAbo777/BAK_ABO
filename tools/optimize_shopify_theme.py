#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import zipfile
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from bks_assets import active_theme_zip, relative_to_base, save_active_assets  # noqa: E402


BKS_DEFAULT_DESCRIPTION = (
    "BKS Studio by BakAbo: AI-generated all-over print wearables, sneakers, swimwear, "
    "outerwear and accessories, made to order at bakabo.club."
)


def default_output_path(input_path: Path) -> Path:
    stem = input_path.stem
    for suffix in ("_SEO_READY", "_OPTIMIZED"):
        if stem.endswith(suffix):
            stem = stem[: -len(suffix)]
    return input_path.with_name(f"{stem}_SEO_READY.zip")


def patch_layout_theme(content: str) -> tuple[str, list[str]]:
    changes: list[str] = []
    old = """    {% if page_description %}
      <meta name="description" content="{{ page_description | escape }}">
    {% endif %}
    {% render 'meta-tags' %}"""
    new = """    {%- liquid
      assign bks_default_description = 'BKS Studio by BakAbo: AI-generated all-over print wearables, sneakers, swimwear, outerwear and accessories, made to order at bakabo.club.'
      assign bks_meta_description = page_description | default: shop.description | default: bks_default_description
    -%}
    <meta name="description" content="{{ bks_meta_description | strip_html | escape }}">
    {% render 'meta-tags' %}
    <script type="application/ld+json">
      {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "BKS Studio",
        "alternateName": "BakAbo",
        "url": "{{ request.origin }}",
        "brand": {
          "@type": "Brand",
          "name": "BakAbo"
        }
      }
    </script>"""
    if old in content:
        content = content.replace(old, new, 1)
        changes.append("layout meta description fallback + Organization JSON-LD")
    return content, changes


def patch_meta_tags(content: str) -> tuple[str, list[str]]:
    changes: list[str] = []
    old = "  assign og_description = page_description | default: shop.description | default: shop.name"
    new = (
        "  assign bks_default_description = 'BKS Studio by BakAbo: AI-generated all-over print wearables, sneakers, "
        "swimwear, outerwear and accessories, made to order at bakabo.club.'\n"
        "  assign og_description = page_description | default: shop.description | default: bks_default_description"
    )
    if old in content:
        content = content.replace(old, new, 1)
        changes.append("Open Graph/Twitter default description")
    return content, changes


def patch_editorial_matrix(content: str) -> tuple[str, list[str]]:
    changes: list[str] = []
    marker = "BKS TM03 visual balance overrides"
    if marker in content:
        return content, changes
    override = """

  /* BKS TM03 visual balance overrides: lighter imagery, calmer mobile type */
  #shopify-section-{{ section.id }} .bks-editorial-matrix {
    background: #171510;
  }
  #shopify-section-{{ section.id }} .bks-editorial-grid {
    background: rgba(250,250,247,0.14);
  }
  #shopify-section-{{ section.id }} .bks-editorial-card {
    background: #151f1b;
    padding: clamp(14px,2.4vw,20px);
  }
  #shopify-section-{{ section.id }} .bks-editorial-card::before {
    opacity: 0.07;
  }
  #shopify-section-{{ section.id }} .bks-editorial-card:hover::before {
    opacity: 0.16;
  }
  #shopify-section-{{ section.id }} .bks-editorial-card__media::after {
    background: linear-gradient(180deg, rgba(10,10,10,0.04) 0%, rgba(10,10,10,0.34) 100%);
  }
  #shopify-section-{{ section.id }} .bks-editorial-card__media img {
    filter: brightness(1.14) contrast(0.98) saturate(1.02);
    opacity: 0.98;
  }
  #shopify-section-{{ section.id }} .bks-editorial-card h3 {
    font-size: clamp(1.35rem,2.1vw,2.25rem);
    line-height: 0.98;
    letter-spacing: 0;
  }
  #shopify-section-{{ section.id }} .bks-editorial-card p {
    font-size: clamp(0.76rem,1vw,0.84rem);
    line-height: 1.45;
  }
  @media screen and (max-width: 749px) {
    #shopify-section-{{ section.id }} .bks-editorial-matrix__inner {
      width: min(100% - 20px, 560px);
      padding: 40px 0;
    }
    #shopify-section-{{ section.id }} .bks-editorial-grid {
      grid-template-columns: 1fr;
      gap: 10px;
      background: transparent;
    }
    #shopify-section-{{ section.id }} .bks-editorial-card {
      min-height: auto;
      padding: 14px;
      background: #18231f;
    }
    #shopify-section-{{ section.id }} .bks-editorial-card__media {
      min-height: 188px;
      margin: -14px -14px 14px;
    }
    #shopify-section-{{ section.id }} .bks-editorial-card h3 {
      margin-bottom: 8px;
      font-size: clamp(1.24rem,7vw,1.55rem);
      line-height: 0.98;
    }
    #shopify-section-{{ section.id }} .bks-editorial-card p {
      font-size: 0.76rem;
      line-height: 1.42;
      display: -webkit-box;
      -webkit-line-clamp: 4;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }
    #shopify-section-{{ section.id }} .bks-editorial-card__meta {
      margin-top: 12px;
      padding-top: 10px;
      font-size: 0.56rem;
      letter-spacing: 0.08em;
    }
  }
"""
    if "</style>" in content:
        content = content.replace("</style>", f"{override}\n</style>", 1)
        changes.append("editorial matrix brightness + mobile typography")
    return content, changes


def audit_zip(path: Path) -> dict[str, object]:
    placeholders = [
        "Talk about your brand",
        "Share information about your brand",
        "Image banner",
        "Button label",
        "Give customers details",
        "Welcome to our store",
    ]
    result: dict[str, object] = {
        "placeholders_in_templates": [],
        "legacy_gtm_files": [],
        "target_gtm_files": [],
        "eu_rep_files": [],
        "json_errors": [],
    }
    with zipfile.ZipFile(path) as archive:
        for name in archive.namelist():
            lower = name.lower()
            if lower.endswith(".json"):
                try:
                    json.loads(archive.read(name).decode("utf-8"))
                except Exception as exc:  # noqa: BLE001
                    result["json_errors"].append({"file": name, "error": str(exc)})  # type: ignore[index]
            if not lower.endswith((".liquid", ".json", ".js", ".css")):
                continue
            try:
                text = archive.read(name).decode("utf-8")
            except UnicodeDecodeError:
                continue
            if name.startswith("templates/") and any(item in text for item in placeholders):
                result["placeholders_in_templates"].append(name)  # type: ignore[index]
            if "GTM-M4ND7QL" in text or "GT-TWMGQB9" in text:
                result["legacy_gtm_files"].append(name)  # type: ignore[index]
            if "GTM-PF5Z85KS" in text:
                result["target_gtm_files"].append(name)  # type: ignore[index]
            if "HONSON VENTURES LIMITED" in text or "gpsr@honsonventures.com" in text:
                result["eu_rep_files"].append(name)  # type: ignore[index]
    return result


def optimize(input_path: Path, output_path: Path, report_path: Path) -> dict[str, object]:
    changes: dict[str, list[str]] = {}
    with zipfile.ZipFile(input_path, "r") as source, zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as dest:
        for info in source.infolist():
            data = source.read(info.filename)
            if info.filename == "layout/theme.liquid":
                text, file_changes = patch_layout_theme(data.decode("utf-8"))
                if file_changes:
                    data = text.encode("utf-8")
                    changes[info.filename] = file_changes
            elif info.filename == "snippets/meta-tags.liquid":
                text, file_changes = patch_meta_tags(data.decode("utf-8"))
                if file_changes:
                    data = text.encode("utf-8")
                    changes[info.filename] = file_changes
            elif info.filename == "sections/bks-editorial-matrix.liquid":
                text, file_changes = patch_editorial_matrix(data.decode("utf-8"))
                if file_changes:
                    data = text.encode("utf-8")
                    changes[info.filename] = file_changes
            dest.writestr(info, data)

    report = {
        "input": relative_to_base(input_path),
        "output": relative_to_base(output_path),
        "changes": changes,
        "audit": audit_zip(output_path),
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Ottimizza lo ZIP tema Shopify BKS con fallback SEO e audit rapido.")
    parser.add_argument("--input", type=Path, default=active_theme_zip())
    parser.add_argument("--output", type=Path)
    parser.add_argument("--report", type=Path)
    parser.add_argument("--set-active", action="store_true", help="Imposta lo ZIP generato come tema attivo.")
    args = parser.parse_args()

    input_path = args.input
    output_path = args.output or default_output_path(input_path)
    report_path = args.report or ROOT / "output" / f"theme_optimization_report_{datetime.now():%Y%m%d_%H%M%S}.json"

    report = optimize(input_path, output_path, report_path)
    if args.set_active:
        save_active_assets(theme_zip=output_path)

    print(f"Output: {relative_to_base(output_path)}")
    print(f"Report: {relative_to_base(report_path)}")
    print(f"Changed files: {len(report['changes'])}")
    audit = report["audit"]
    print(f"Template placeholders: {len(audit['placeholders_in_templates'])}")
    print(f"Legacy GTM files: {len(audit['legacy_gtm_files'])}")
    print(f"JSON errors: {len(audit['json_errors'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
