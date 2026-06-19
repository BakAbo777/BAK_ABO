"""BKS Algorithm — multi-factor scoring and priority engine for BakAbo operations."""
from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"
CATALOG_DIR = BASE_DIR / "collezioni_csv"
FACTORY_MANIFEST = BASE_DIR / "BAKABO_IMAGE_FACTORY_v1.1" / "output" / "cutout_manifest.csv"

COLLECTIONS = ("hours", "glyph", "marker", "riviera", "pulse", "token", "flag", "origin")
COLLECTION_ACCENTS = {
    "hours":   "#c8c4be",
    "glyph":   "#d4a030",
    "marker":  "#c04418",
    "riviera": "#0ca898",
    "pulse":   "#8888cc",
    "token":   "#9828d8",
    "flag":    "#c82020",
    "origin":  "#489808",
}

TIER_LABELS = {
    "P0": "CRITICAL",
    "P1": "FIX",
    "P2": "REFINE",
    "P3": "READY",
}

WEIGHTS = {"seo": 0.30, "images": 0.25, "data": 0.20, "collection": 0.15, "brand": 0.10}


@dataclass
class ProductScore:
    handle: str
    title: str
    collection: str
    total: float
    seo: float
    images: float
    data: float
    collection_score: float
    brand: float
    tier: str
    issues: list[str] = field(default_factory=list)
    published: bool = False

    @property
    def tier_label(self) -> str:
        return TIER_LABELS.get(self.tier, self.tier)

    @property
    def accent(self) -> str:
        return COLLECTION_ACCENTS.get(self.collection, "#666666")


@dataclass
class CollectionHealth:
    handle: str
    accent: str
    product_count: int
    avg_score: float
    ready_count: int
    critical_count: int
    status: str


def _find_active_csv() -> Path | None:
    csvs = sorted(CATALOG_DIR.glob("*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
    for p in csvs:
        if p.stat().st_size > 1000:
            return p
    return None


def _parse_catalog(csv_path: Path) -> list[dict]:
    products: dict[str, dict] = {}
    with open(csv_path, encoding="utf-8-sig", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            handle = (row.get("Handle") or "").strip()
            if not handle:
                continue
            if handle not in products:
                products[handle] = {**row, "_variant_count": 1}
            else:
                products[handle]["_variant_count"] = products[handle].get("_variant_count", 1) + 1
                price = (row.get("Variant Price") or row.get("Price") or "").strip()
                if price and not products[handle].get("Variant Price"):
                    products[handle]["Variant Price"] = price
    return list(products.values())


def _load_factory_manifest() -> set[str]:
    processed: set[str] = set()
    if not FACTORY_MANIFEST.exists():
        return processed
    with open(FACTORY_MANIFEST, encoding="utf-8-sig", errors="replace") as f:
        reader = csv.DictReader(f)
        for row in reader:
            h = (row.get("handle") or row.get("slug") or "").strip()
            if h:
                processed.add(h)
    return processed


def _score_seo(p: dict) -> tuple[float, list[str]]:
    issues = []
    score = 0.0
    title = (p.get("Title") or "").strip()
    body = (p.get("Body (HTML)") or "").strip()
    tags = (p.get("Tags") or "").strip()

    # Title: 0-35
    if title:
        tlen = len(title)
        if 40 <= tlen <= 70:
            score += 35
        elif 25 <= tlen < 40:
            score += 25
            issues.append("title short")
        elif tlen > 70:
            score += 20
            issues.append("title too long")
        else:
            score += 10
            issues.append("title very short")
    else:
        issues.append("missing title")

    # Body: 0-40
    body_clean = re.sub(r"<[^>]+>", "", body)
    blen = len(body_clean)
    if blen >= 300:
        score += 40
    elif blen >= 150:
        score += 30
        issues.append("description brief")
    elif blen >= 50:
        score += 15
        issues.append("description thin")
    else:
        issues.append("missing description")

    # Tags: 0-25
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    tcount = len(tag_list)
    if tcount >= 8:
        score += 25
    elif tcount >= 5:
        score += 18
    elif tcount >= 3:
        score += 10
        issues.append("few tags")
    else:
        issues.append("tags missing")

    return min(score, 100.0), issues


def _score_images(p: dict, processed_handles: set[str]) -> tuple[float, list[str]]:
    issues = []
    score = 0.0
    handle = (p.get("Handle") or "").strip()
    image_src = (p.get("Image Src") or "").strip()
    alt = (p.get("Image Alt Text") or "").strip()

    if image_src:
        score += 40
    else:
        issues.append("no Shopify image")

    if handle in processed_handles:
        score += 45
    else:
        issues.append("no image factory output")

    if alt:
        score += 15
    else:
        issues.append("no image alt text")

    return min(score, 100.0), issues


def _score_data(p: dict) -> tuple[float, list[str]]:
    issues = []
    score = 0.0

    if (p.get("Vendor") or "").strip():
        score += 20
    else:
        issues.append("missing vendor")

    if (p.get("Type") or p.get("Product Category") or "").strip():
        score += 25
    else:
        issues.append("missing type")

    price = (p.get("Variant Price") or p.get("Price") or "").strip()
    try:
        pval = float(price.replace(",", "."))
        if pval > 0:
            score += 30
        else:
            issues.append("price is zero")
    except (ValueError, AttributeError):
        issues.append("missing price")

    vc = int(p.get("_variant_count", 1))
    if vc >= 2:
        score += 25
    else:
        issues.append("single variant")

    return min(score, 100.0), issues


def _score_collection(p: dict) -> tuple[float, str, list[str]]:
    tags = (p.get("Tags") or "").lower()
    for coll in COLLECTIONS:
        if f"collection:{coll}" in tags:
            return 100.0, coll, []
    return 0.0, "", ["no BKS collection tag"]


def _score_brand(p: dict) -> tuple[float, list[str]]:
    issues = []
    score = 0.0
    title = (p.get("Title") or "").strip()
    vendor = (p.get("Vendor") or "").strip().lower()

    if title.upper().startswith("BKS"):
        score += 60
    else:
        issues.append("title missing BKS prefix")

    if any(v in vendor for v in ("bakabo", "bks", "bak abo")):
        score += 40
    else:
        issues.append("vendor not BKS/BakAbo")

    return min(score, 100.0), issues


def _tier(total: float) -> str:
    if total >= 75:
        return "P3"
    if total >= 55:
        return "P2"
    if total >= 35:
        return "P1"
    return "P0"


class BKSAlgorithm:
    def __init__(self, csv_path: Path | None = None):
        self._csv_path = csv_path or _find_active_csv()
        self._products: list[dict] = []
        self._processed: set[str] = set()
        self._scores: list[ProductScore] | None = None
        self._loaded_at: str = ""

    def _ensure_loaded(self) -> None:
        if self._products:
            return
        if self._csv_path and self._csv_path.exists():
            self._products = _parse_catalog(self._csv_path)
        self._processed = _load_factory_manifest()
        self._loaded_at = datetime.now(timezone.utc).isoformat(timespec="seconds")

    def score_product(self, p: dict) -> ProductScore:
        self._ensure_loaded()
        seo, seo_issues = _score_seo(p)
        images, img_issues = _score_images(p, self._processed)
        data, data_issues = _score_data(p)
        coll_score, coll_handle, coll_issues = _score_collection(p)
        brand, brand_issues = _score_brand(p)

        total = (
            seo * WEIGHTS["seo"]
            + images * WEIGHTS["images"]
            + data * WEIGHTS["data"]
            + coll_score * WEIGHTS["collection"]
            + brand * WEIGHTS["brand"]
        )
        all_issues = seo_issues + img_issues + data_issues + coll_issues + brand_issues
        published = (p.get("Published") or "").strip().lower() in ("true", "yes", "1")

        return ProductScore(
            handle=(p.get("Handle") or "").strip(),
            title=(p.get("Title") or "").strip(),
            collection=coll_handle,
            total=round(total, 1),
            seo=round(seo, 1),
            images=round(images, 1),
            data=round(data, 1),
            collection_score=round(coll_score, 1),
            brand=round(brand, 1),
            tier=_tier(total),
            issues=all_issues,
            published=published,
        )

    def score_all(self, force: bool = False) -> list[ProductScore]:
        self._ensure_loaded()
        if self._scores is not None and not force:
            return self._scores
        self._scores = [self.score_product(p) for p in self._products]
        return self._scores

    def priority_queue(self, limit: int = 30) -> list[ProductScore]:
        scores = self.score_all()
        return sorted(scores, key=lambda s: s.total)[:limit]

    def ready_for_gate(self) -> list[ProductScore]:
        return [s for s in self.score_all() if s.tier == "P3"]

    def collection_health(self) -> list[CollectionHealth]:
        scores = self.score_all()
        buckets: dict[str, list[ProductScore]] = {c: [] for c in COLLECTIONS}
        unassigned: list[ProductScore] = []
        for s in scores:
            if s.collection in buckets:
                buckets[s.collection].append(s)
            else:
                unassigned.append(s)

        result = []
        for coll in COLLECTIONS:
            items = buckets[coll]
            avg = round(sum(s.total for s in items) / len(items), 1) if items else 0.0
            ready = sum(1 for s in items if s.tier == "P3")
            critical = sum(1 for s in items if s.tier == "P0")
            if not items:
                status = "empty"
            elif avg >= 70:
                status = "ok"
            elif avg >= 45:
                status = "warn"
            else:
                status = "critical"
            result.append(CollectionHealth(
                handle=coll,
                accent=COLLECTION_ACCENTS[coll],
                product_count=len(items),
                avg_score=avg,
                ready_count=ready,
                critical_count=critical,
                status=status,
            ))
        return result

    def summary(self) -> dict:
        scores = self.score_all()
        total = len(scores)
        if not total:
            return {"total": 0, "avg_score": 0, "ready": 0, "critical": 0, "warn": 0, "unassigned": 0}
        avg = round(sum(s.total for s in scores) / total, 1)
        tiers = {t: sum(1 for s in scores if s.tier == t) for t in ("P0", "P1", "P2", "P3")}
        unassigned = sum(1 for s in scores if not s.collection)
        return {
            "total": total,
            "avg_score": avg,
            "ready": tiers["P3"],
            "refine": tiers["P2"],
            "fix": tiers["P1"],
            "critical": tiers["P0"],
            "unassigned": unassigned,
            "csv_path": str(self._csv_path) if self._csv_path else "",
            "loaded_at": self._loaded_at,
        }

    def gate_check(self, handle: str) -> dict:
        scores = self.score_all()
        match = next((s for s in scores if s.handle == handle), None)
        if not match:
            return {"handle": handle, "pass": False, "reason": "product not found"}

        checks = {
            "seo >= 60": match.seo >= 60,
            "images >= 40": match.images >= 40,
            "data >= 60": match.data >= 60,
            "collection assigned": bool(match.collection),
            "brand compliance": match.brand >= 60,
            "score >= 75": match.total >= 75,
        }
        passed = all(checks.values())
        failed = [k for k, v in checks.items() if not v]
        return {
            "handle": handle,
            "title": match.title,
            "collection": match.collection,
            "total_score": match.total,
            "pass": passed,
            "checks": checks,
            "failed": failed,
            "issues": match.issues,
        }

    def to_rows(self) -> list[dict]:
        return [
            {
                "handle": s.handle,
                "title": s.title,
                "collection": s.collection,
                "score": s.total,
                "seo": s.seo,
                "images": s.images,
                "data": s.data,
                "tier": s.tier,
                "published": s.published,
                "issues": "; ".join(s.issues[:3]),
            }
            for s in self.score_all()
        ]

    def export_csv(self, path: Path | None = None) -> Path:
        out = path or (OUTPUT_DIR / "bks_algorithm_scores.csv")
        rows = self.to_rows()
        if not rows:
            return out
        with open(out, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        return out


# Singleton
bks_algorithm = BKSAlgorithm()
