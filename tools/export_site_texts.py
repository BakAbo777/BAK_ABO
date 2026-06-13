"""Export BKS site text blocks into Shopify-ready files.

The source document stays untouched. This script creates a practical launch
bundle with raw HTML, legally safer reviewed variants, metadata, and an audit.
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "BKS_Testi_Sito_Completi_v1.md"
WEB_SKILL = ROOT / "docs" / "bakabo-web-experience_SKILL.md"
COLOR_SKILL = ROOT / "docs" / "bakabo-armocromia_SKILL.md"
OUT_DIR = ROOT / "output" / "site_texts_v1"


SECTION_FILES = {
    "ABOUT PAGE": "about",
    "SHIPPING POLICY": "shipping_policy",
    "RETURNS & REFUND POLICY": "returns_refund_policy",
    "PRIVACY POLICY": "privacy_policy",
    "TERMS OF SERVICE": "terms_of_service",
    "FAQ / HELP CENTER": "help_faq",
    "CONTACT PAGE": "contact",
}


@dataclass
class PageBlock:
    number: int
    title: str
    shopify: str = ""
    template: str = ""
    seo_title: str = ""
    meta_description: str = ""
    html: str = ""

    @property
    def slug(self) -> str:
        return SECTION_FILES[self.title]


def extract_backtick_value(line: str) -> str:
    match = re.search(r"`([^`]+)`", line)
    if match:
        return match.group(1).strip()
    return line.split(":", 1)[-1].strip().strip("* ")


def extract_metadata_value(line: str) -> str:
    value = re.sub(r"^\*\*[^:]+:\*\*\s*", "", line).strip()
    return value


def parse_source(text: str) -> tuple[list[PageBlock], str, str]:
    lines = text.splitlines()
    pages: list[PageBlock] = []
    homepage_lines: list[str] = []
    collection_lines: list[str] = []

    current: PageBlock | None = None
    in_html = False
    html_lines: list[str] = []
    section_name = ""

    for line in lines:
        section_match = re.match(r"^# (\d+)\. (.+)$", line)
        if section_match:
            if current:
                if html_lines:
                    current.html = "\n".join(html_lines).strip() + "\n"
                pages.append(current)
            number = int(section_match.group(1))
            title = section_match.group(2).strip()
            current = PageBlock(number=number, title=title) if title in SECTION_FILES else None
            in_html = False
            html_lines = []
            section_name = title
            continue

        if section_name.startswith("HOMEPAGE") or re.match(r"^## 8\.", line):
            homepage_lines.append(line)
        if section_name.startswith("COLLECTION PAGES") or line.startswith("| **BKS"):
            collection_lines.append(line)

        if not current:
            continue

        if line.startswith("**Shopify:**"):
            current.shopify = extract_metadata_value(line)
        elif line.startswith("**Template:**"):
            current.template = extract_backtick_value(line)
        elif line.startswith("**SEO Title:**"):
            current.seo_title = extract_backtick_value(line)
        elif line.startswith("**Meta description:**"):
            current.meta_description = extract_backtick_value(line)
        elif line.strip() == "```html":
            in_html = True
            html_lines = []
        elif in_html and line.strip() == "```":
            in_html = False
            current.html = "\n".join(html_lines).strip() + "\n"
        elif in_html:
            html_lines.append(line)

    if current:
        if html_lines and not current.html:
            current.html = "\n".join(html_lines).strip() + "\n"
        pages.append(current)

    for page in pages:
        if page.title == "FAQ / HELP CENTER":
            page.template = "page.help-faq"

    return pages, "\n".join(homepage_lines).strip() + "\n", "\n".join(collection_lines).strip() + "\n"


def reviewed_html(page: PageBlock) -> str:
    html = page.html
    html = html.replace(
        "EU Directive 1999/44/EC",
        "Directive (EU) 2019/771 and applicable national consumer law",
    )
    html = html.replace(
        "under Directive 1999/44/EC",
        "under Directive (EU) 2019/771 and applicable national consumer law",
    )
    return html


def reviewed_meta(meta: str) -> str:
    if "GDPR compliant" in meta:
        return "BKS Studio privacy policy: how we collect, use, protect your data, and explain your privacy rights on bakabo.club."
    replacements = {
        "2-year EU warranty.": "EU legal warranty.",
    }
    for old, new in replacements.items():
        meta = meta.replace(old, new)
    return meta


def reviewed_homepage_copy(text: str) -> str:
    text = text.replace(
        "④  2-Year EU Warranty  Manufacturing defects covered for 2 years under EU Directive 1999/44/EC.",
        "④  EU Legal Warranty   Manufacturing defects covered under Directive (EU) 2019/771 and applicable national consumer law.",
    )
    text = text.replace("Button:      Subscribe", "Button:      Join the archive")
    return text


def seo_status(chars: int) -> str:
    if 120 <= chars <= 160:
        return "ok"
    if 90 <= chars < 120:
        return "usable-short"
    if 1 <= chars < 90:
        return "short"
    if chars > 160:
        return "too-long"
    return "missing"


def write_audit(pages: list[PageBlock], homepage: str, collection_intro: str) -> None:
    rows = []
    for page in pages:
        meta = reviewed_meta(page.meta_description)
        rows.append(
            f"| {page.title} | {page.slug}.html | {len(meta)} | {seo_status(len(meta))} | "
            f"{'yes' if page.html else 'no'} |"
        )

    audit = f"""# BKS Site Texts Export Audit

Generated from: `docs/BKS_Testi_Sito_Completi_v1.md`

## Output

| Page | HTML file | Reviewed meta chars | SEO status | HTML found |
|---|---:|---:|---|---|
{chr(10).join(rows)}

## Reviewed Changes Applied In `_reviewed.html`

- Replaced legacy warranty reference `Directive 1999/44/EC` with `Directive (EU) 2019/771 and applicable national consumer law`.
- Reworded the privacy meta description away from the broad claim `GDPR compliant`.
- Replaced homepage newsletter CTA `Subscribe` with `Join the archive`, matching the BakAbo web experience rule.
- Preserved 30-day returns language because it is more generous than the EU minimum, but it must match the real Shopify return workflow.

## Shopify Placement

- `about.html` -> Shopify Page handle `about`, template `page.about`.
- `help_faq.html` -> Shopify Page handle `help-faq`, template `page.help-faq`.
- `contact.html` -> Shopify Page handle `contact`, template `page.contact`.
- `shipping_policy.html`, `returns_refund_policy.html`, `privacy_policy.html`, `terms_of_service.html` -> Shopify Settings -> Policies.

## Theme Notes

- The default `page.json` in the theme contains a legacy collection-list block. Use the dedicated page templates added to the V20 theme for About, FAQ and policy-style pages.
- MAN/WOMAN should remain secondary navigation/filter logic only. BKS/BakAbo collection identity must dominate homepage and collection pages.
- Product media should be exported/uploaded as PNG or WebP with alpha whenever possible. Theme media wrappers should stay visually neutral so product silhouettes remain consistent.
- Reviews/social proof must use real verified review data only. Until there are enough verified reviews, use trust/service commitments instead of testimonial blocks.

## Color And Contrast Rules

- BakAbo is the container: neutral architectural base, strong readability, product/collection color as accent.
- BKS is the creative studio signal: visible in copy and collection identity, without overpowering BakAbo as the storefront container.
- For BKS visuals, the product must remain the protagonist. Background, model palette and accent color support the pattern rather than competing with it.
- Keep text on collection accent bars at high contrast. Avoid low-contrast accent-on-white or dark-on-dark combinations.
- Homepage/banner palette rule: use a maximum of two background colors plus one accent.
- Collection cards should not all share one background color, but they must still read as one coherent BakAbo/BKS system.
- Armocromia source: `docs/bakabo-armocromia_SKILL.md`. Any previous temporary armocromia note is superseded.

## Source Checks

- EU sale-of-goods legal warranty framework: Directive (EU) 2019/771, which repealed Directive 1999/44/EC.
- EU withdrawal/consumer rights framework: Directive 2011/83/EU.
- Shopify policies should be entered in Settings -> Policies so checkout/footer policy links resolve correctly.

Reference URLs:

- https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32019L0771
- https://commission.europa.eu/law/law-topic/consumer-protection-law/consumer-contract-law/consumer-rights-directive_en
- https://help.shopify.com/en/manual/checkout-settings/refund-privacy-tos

## Counts

- Page HTML blocks: {len(pages)}
- Homepage copy chars: {len(homepage)}
- Collection intro chars: {len(collection_intro)}
"""
    (OUT_DIR / "site_texts_audit.md").write_text(audit, encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    source = SOURCE.read_text(encoding="utf-8")
    pages, homepage, collection_intro = parse_source(source)

    if len(pages) != len(SECTION_FILES):
        found = ", ".join(page.title for page in pages)
        raise SystemExit(f"Expected {len(SECTION_FILES)} page blocks, found {len(pages)}: {found}")

    for page in pages:
        (OUT_DIR / f"{page.slug}.html").write_text(page.html, encoding="utf-8")
        (OUT_DIR / f"{page.slug}_reviewed.html").write_text(reviewed_html(page), encoding="utf-8")

    (OUT_DIR / "homepage_copy.md").write_text(homepage, encoding="utf-8")
    (OUT_DIR / "homepage_copy_reviewed.md").write_text(reviewed_homepage_copy(homepage), encoding="utf-8")
    (OUT_DIR / "collection_intro_copy.md").write_text(collection_intro, encoding="utf-8")

    with (OUT_DIR / "site_texts_metadata.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "page",
                "shopify_location",
                "template",
                "seo_title",
                "meta_description",
                "meta_chars",
                "reviewed_meta_description",
                "reviewed_meta_chars",
                "seo_status",
                "html_file",
                "reviewed_html_file",
            ],
        )
        writer.writeheader()
        for page in pages:
            reviewed = reviewed_meta(page.meta_description)
            writer.writerow(
                {
                    "page": page.title,
                    "shopify_location": page.shopify,
                    "template": page.template,
                    "seo_title": page.seo_title,
                    "meta_description": page.meta_description,
                    "meta_chars": len(page.meta_description),
                    "reviewed_meta_description": reviewed,
                    "reviewed_meta_chars": len(reviewed),
                    "seo_status": seo_status(len(reviewed)),
                    "html_file": f"{page.slug}.html",
                    "reviewed_html_file": f"{page.slug}_reviewed.html",
                }
            )

    write_audit(pages, homepage, collection_intro)

    skill_refs = [
        ("bakabo-web-experience_SKILL.md", WEB_SKILL.exists()),
        ("bakabo-armocromia_SKILL.md", COLOR_SKILL.exists()),
    ]
    print(f"Exported {len(pages)} page blocks to {OUT_DIR}")
    for name, exists in skill_refs:
        print(f"{'found' if exists else 'missing'} {name}")


if __name__ == "__main__":
    main()
