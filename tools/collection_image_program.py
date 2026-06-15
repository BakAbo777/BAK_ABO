from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

try:
    from PIL import Image, ImageDraw, ImageFont
except Exception:  # pragma: no cover - optional preview dependency
    Image = None
    ImageDraw = None
    ImageFont = None


BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from bks_assets import active_catalog_csv  # noqa: E402

DEFAULT_CSV = active_catalog_csv() or BASE_DIR / "collezioni_csv" / "collezione_12_06_2026_VERIFIED.csv"
DEFAULT_IMAGE_DIR = BASE_DIR / "output" / "images"
DEFAULT_MODEL_DIR = BASE_DIR / "input" / "models"
DEFAULT_OUT_DIR = BASE_DIR / "output" / "collection_image_program"

EDITORIAL_COLLECTIONS = (
    "folklore",
    "glyph",
    "marker",
    "riviera",
    "pulse",
    "token",
    "flag",
    "hours",
)

TYPE_ALIASES = {
    "all over prints": "puffer-jacket",
    "bags": "backpack",
    "dress": "racerback-dress",
    "duffle": "travel-bag",
    "duffel": "travel-bag",
    "flip flop": "flip-flop",
    "puffer": "puffer-jacket",
    "puffer jacket": "puffer-jacket",
    "pullover hoodie": "pullover-hoodie",
    "shoes": "sneakers",
    "sneaker": "sneakers",
    "sneakers": "sneakers",
    "swim trunks": "swim-trunks",
    "swimwear": "one-piece-swimsuit",
    "travel bag": "travel-bag",
    "windbreaker jacket": "windbreaker",
}

TYPE_LABELS = {
    "backpack": "backpack",
    "flip-flop": "flip flop",
    "lounge-pants": "lounge pants",
    "one-piece-swimsuit": "one-piece swimsuit",
    "puffer-jacket": "puffer jacket",
    "pullover-hoodie": "pullover hoodie",
    "racerback-dress": "racerback dress",
    "sneakers": "low-top canvas sneakers",
    "swim-trunks": "swim trunks",
    "travel-bag": "waterproof travel duffle bag",
    "windbreaker": "windbreaker jacket",
}

STILL_LIFE_TYPE_ORDER = (
    "sneakers",
    "travel-bag",
    "puffer-jacket",
    "windbreaker",
    "backpack",
    "racerback-dress",
    "swim-trunks",
)

ON_MODEL_TYPE_ORDER = (
    "puffer-jacket",
    "windbreaker",
    "pullover-hoodie",
    "racerback-dress",
    "lounge-pants",
    "swim-trunks",
    "one-piece-swimsuit",
    "sneakers",
    "travel-bag",
)

CURATED_COLLECTION_DIRECTIONS = {
    "new-arrivals": {
        "mode": "still-life",
        "types": ["sneakers", "travel-bag", "puffer-jacket", "windbreaker"],
        "note": "Sneakers + travel-bag + puffer jacket + windbreaker. Massima varieta di categoria in un solo shot; rappresenta l'ampiezza del catalogo 2026 meglio di qualsiasi singolo prodotto. Sfondo bone pulito.",
        "rejected": "new-arrivals/on-model: piu impatto visivo ma meno rappresentativo della varieta.",
    },
    "flag": {
        "mode": "still-life",
        "types": ["sneakers", "travel-bag", "puffer-jacket", "racerback-dress"],
        "note": "Palette netta e codici cromatici leggibili: sneakers giallo/nero, travel-bag a strisce bordeaux, puffer bianco/nero e racerback come elemento hero.",
        "rejected": "flag/on-model: hoodie troppo dominante, non mostra l'identita Flag.",
    },
    "folklore": {
        "mode": "on-model",
        "types": ["puffer-jacket", "pullover-hoodie", "racerback-dress", "swim-trunks"],
        "note": "Il registro naif/invented-world funziona meglio on-model: puffer leopard dorato, hoodie blu con creature, racerback con castello medievale e swim trunks farfalle.",
        "rejected": "folklore/still-life: solo tre prodotti, meno rappresentativo.",
    },
    "glyph": {
        "mode": "still-life",
        "types": ["sneakers", "travel-bag", "puffer-jacket", "backpack"],
        "note": "Sistema segnico perfettamente leggibile: sneakers blu/bianco, travel-bag dorata con glifi, puffer bianco/nero e backpack diamond pattern.",
        "rejected": "glyph/on-model: il green neon dei lounge pants distrae dall'identita brut.",
    },
    "hours": {
        "mode": "still-life",
        "types": ["sneakers", "travel-bag", "puffer-jacket", "backpack"],
        "note": "Still-life piu equilibrata: sneakers blu/turchese con medaglione, travel-bag con volto femminile antico, puffer grigio onde e backpack meccanico.",
        "rejected": "hours/on-model: racerback forte, ma meno bilanciata come collection image.",
    },
    "marker": {
        "mode": "still-life",
        "types": ["sneakers", "travel-bag", "puffer-jacket", "windbreaker"],
        "note": "Neo-expressionism chiaro: sneakers rosso/nero/bianco, travel-bag con volto-leone, puffer arancio/rosso e windbreaker bicolore.",
        "rejected": "marker/on-model: ottimo, ma la windbreaker bicolore e piu leggibile nella still-life.",
    },
    "pulse": {
        "mode": "on-model",
        "types": ["puffer-jacket", "pullover-hoodie", "racerback-dress", "one-piece-swimsuit"],
        "note": "On-model comunica meglio il movimento ottico: puffer multicolor cinetico, hoodie arancio/blu, racerback arcobaleno verticale e one-piece viola.",
        "rejected": "pulse/still-life: travel-bag interessante ma puffer troppo simile alla riviera.",
    },
    "riviera": {
        "mode": "on-model",
        "types": ["puffer-jacket", "racerback-dress", "swim-trunks", "sneakers", "travel-bag"],
        "note": "Palette mediterranea per eccellenza: puffer blu/oro, racerback geometrica blu, swim trunks argyle beige/grigio, sneakers checkerboard e travel-bag verde/bianco.",
        "rejected": "riviera/still-life: pulita ma meno rappresentativa dell'identita islands.",
    },
    "token": {
        "mode": "on-model",
        "types": ["puffer-jacket", "racerback-dress", "swim-trunks", "sneakers"],
        "note": "Registro digitale/arcade chiarissimo: puffer bianco con schizzi di colore, racerback pixel multicolore, swim trunks con oggetti arcade e sneakers verde/ocra.",
        "rejected": "token/still-life: piu pulita, ma on-model comunica meglio l'energia arcade.",
    },
}


@dataclass
class Product:
    handle: str
    title: str
    product_type: str
    collection: str
    macros: tuple[str, ...]
    series: str
    colors: str
    image_src: str
    local_images: list[str]


def slugify(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value or "").strip("-").lower()
    return value or "bks-product"


def tag_value(tags: str, key: str) -> str:
    match = re.search(rf"(?:^|,\s*){re.escape(key)}:([^,\s]+)", tags or "", re.I)
    return match.group(1).strip().lower() if match else ""


def macro_values(tags: str) -> tuple[str, ...]:
    values = re.findall(r"(?:^|,\s*)macro:([^,\s]+)", tags or "", re.I)
    return tuple(dict.fromkeys(v.strip().lower() for v in values if v.strip()))


def normalize_type(row_type: str, tags: str) -> str:
    tagged = tag_value(tags, "type")
    raw = (tagged or row_type or "").strip().lower()
    return TYPE_ALIASES.get(raw, raw.replace(" ", "-"))


def compact_title(title: str) -> str:
    return re.sub(r"\s+", " ", (title or "").replace("Printify", "")).strip()


def image_candidates(image_dir: Path, handle: str, title: str) -> list[str]:
    keys = [slugify(handle), slugify(title)]
    found: list[Path] = []
    for key in keys:
        if not key:
            continue
        found.extend(image_dir.glob(f"{key}*.webp"))
        found.extend(image_dir.glob(f"{key}*.jpg"))
        found.extend(image_dir.glob(f"{key}*.png"))
    unique = []
    seen = set()
    for path in sorted(found):
        resolved = str(path.resolve())
        if resolved not in seen:
            unique.append(resolved)
            seen.add(resolved)
    return unique


def load_products(csv_path: Path, image_dir: Path) -> list[Product]:
    products: dict[str, Product] = {}
    with csv_path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            handle = (row.get("Handle") or "").strip()
            if not handle or handle in products:
                continue
            tags = row.get("Tags") or ""
            collection = tag_value(tags, "collection")
            if not collection and "drop:catalog-reset-2026" not in tags:
                continue
            title = compact_title(row.get("Title") or handle)
            product_type = normalize_type(row.get("Type") or "", tags)
            title_lower = title.lower()
            if "swim trunks" in title_lower:
                product_type = "swim-trunks"
            elif "one-piece swimsuit" in title_lower:
                product_type = "one-piece-swimsuit"
            elif "windbreaker" in title_lower:
                product_type = "windbreaker"
            elif "puffer" in title_lower:
                product_type = "puffer-jacket"
            colors = row.get("Color (product.metafields.shopify.color-pattern)") or ""
            products[handle] = Product(
                handle=handle,
                title=title,
                product_type=product_type,
                collection=collection,
                macros=macro_values(tags),
                series=tag_value(tags, "series"),
                colors=colors,
                image_src=(row.get("Image Src") or "").strip(),
                local_images=image_candidates(image_dir, handle, title),
            )
    return list(products.values())


def type_rank(product: Product, order: tuple[str, ...]) -> tuple[int, str]:
    try:
        rank = order.index(product.product_type)
    except ValueError:
        rank = len(order)
    return rank, product.title


def select_products(
    products: Iterable[Product],
    collection: str,
    mode: str,
    limit: int,
) -> list[Product]:
    pool = [
        p for p in products
        if collection == "new-arrivals" or p.collection == collection
    ]
    order = ON_MODEL_TYPE_ORDER if mode == "on-model" else STILL_LIFE_TYPE_ORDER
    selected: list[Product] = []
    used_types: set[str] = set()
    for product in sorted(pool, key=lambda p: type_rank(p, order)):
        if product.product_type in used_types:
            continue
        selected.append(product)
        used_types.add(product.product_type)
        if len(selected) >= limit:
            break
    if len(selected) < limit:
        for product in sorted(pool, key=lambda p: type_rank(p, order)):
            if product.handle in {p.handle for p in selected}:
                continue
            selected.append(product)
            if len(selected) >= limit:
                break
    return selected


def select_products_by_types(
    products: Iterable[Product],
    collection: str,
    wanted_types: list[str],
) -> list[Product]:
    pool = [
        p for p in products
        if collection == "new-arrivals" or p.collection == collection
    ]
    selected: list[Product] = []
    used_handles: set[str] = set()
    for wanted_type in wanted_types:
        candidates = sorted(
            [
                p for p in pool
                if p.product_type == wanted_type and p.handle not in used_handles
            ],
            key=lambda p: (-len(p.local_images), p.title),
        )
        if not candidates:
            continue
        selected.append(candidates[0])
        used_handles.add(candidates[0].handle)
    return selected


def product_phrase(product: Product) -> str:
    label = TYPE_LABELS.get(product.product_type, product.product_type.replace("-", " "))
    texture = product.series.replace("-", " ") if product.series else "AI-generated"
    colors = f", palette {product.colors}" if product.colors else ""
    return f"{label} ({product.title}, {texture} AOP print{colors})"


def list_model_refs(model_dir: Path) -> list[str]:
    if not model_dir.exists():
        return []
    refs: list[str] = []
    for pattern in ("*.jpg", "*.jpeg", "*.png", "*.webp"):
        refs.extend(str(path.resolve()) for path in sorted(model_dir.glob(pattern)))
    return refs


def build_prompt(collection: str, mode: str, selected: list[Product], model_refs: list[str]) -> str:
    items = "; ".join(product_phrase(p) for p in selected)
    if mode == "on-model":
        model_note = (
            "Use the supplied approved model reference images for face/body consistency. "
            if model_refs
            else "Use editorial anonymous professional models with no celebrity resemblance. "
        )
        return (
            "Collection hero image for BKS Studio / BakAbo Club, vertical 4:5 format "
            "2000x2500px, premium fashion editorial studio scene, two professional models "
            "wearing selected BKS all-over print garments and accessories, full outfit styling, "
            "deep onyx background #0A0A0A, minimal architectural set, cinematic directional "
            "light from the right, restrained COS and Zara Studio visual language, no text, "
            "no logo, realistic fabric texture, elegant posture, high resolution. "
            f"{model_note}"
            f"Collection: {collection}. Wardrobe references: {items}."
        )
    return (
        "Collection hero image for BKS Studio / BakAbo Club, vertical 4:5 format "
        "2000x2500px, editorial product still life on a minimal dark architectural surface, "
        "deep onyx background #0A0A0A, selected BKS all-over print fashion items arranged "
        "as sculptural objects, soft cinematic directional light from the right, long shadows, "
        "no models, no text, no logo, fashion editorial photography inspired by COS and Zara "
        "Studio, ultra realistic, premium restrained aesthetic, high resolution, rich detail "
        f"on fabric textures. Collection: {collection}. Product references: {items}."
    )


def make_contact_sheet(selected: list[Product], out_path: Path, title: str) -> None:
    if Image is None or ImageDraw is None:
        return
    thumbs = []
    for product in selected:
        if not product.local_images:
            continue
        try:
            img = Image.open(product.local_images[0]).convert("RGB")
        except Exception:
            continue
        img.thumbnail((320, 360))
        thumbs.append((product, img.copy()))
    if not thumbs:
        return
    width = 360 * len(thumbs)
    height = 470
    sheet = Image.new("RGB", (width, height), "#0A0A0A")
    draw = ImageDraw.Draw(sheet)
    for idx, (product, img) in enumerate(thumbs):
        x = idx * 360 + 20
        y = 58
        sheet.paste(img, (x + (320 - img.width) // 2, y))
        draw.text((x, 20), title[:42], fill="#F5F1E8")
        label = f"{product.title[:38]}\n{product.product_type}"
        draw.text((x, 405), label, fill="#F5F1E8")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out_path, quality=92)


def write_curated_program(products: list[Product], out_dir: Path, model_refs: list[str]) -> None:
    curated_dir = out_dir / "curated"
    prompts_dir = curated_dir / "prompts"
    previews_dir = curated_dir / "contact_sheets"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    previews_dir.mkdir(parents=True, exist_ok=True)

    briefs = []
    for collection, direction in CURATED_COLLECTION_DIRECTIONS.items():
        mode = direction["mode"]
        wanted_types = direction["types"]
        selected = select_products_by_types(products, collection, wanted_types)
        prompt = build_prompt(collection, mode, selected, model_refs)
        prompt = f"{prompt}\n\nCuratorial direction: {direction['note']}"
        slug = f"{collection}-{mode}"
        prompt_path = prompts_dir / f"{slug}.txt"
        contact_sheet = previews_dir / f"{slug}.jpg"
        prompt_path.write_text(prompt, encoding="utf-8")
        make_contact_sheet(selected, contact_sheet, f"{collection} / {mode}")
        briefs.append(
            {
                "collection": collection,
                "selected_mode": mode,
                "selected_path": f"{collection}/{mode}",
                "ratio": "4:5",
                "size_px": [2000, 2500],
                "wanted_types": wanted_types,
                "curatorial_note": direction["note"],
                "rejected_alternative": direction["rejected"],
                "prompt_file": str(prompt_path.resolve()),
                "contact_sheet": str(contact_sheet.resolve()) if contact_sheet.exists() else "",
                "model_references": model_refs if mode == "on-model" else [],
                "selected_products": [
                    {
                        "handle": p.handle,
                        "title": p.title,
                        "type": p.product_type,
                        "collection": p.collection,
                        "macros": list(p.macros),
                        "image_src": p.image_src,
                        "local_images": p.local_images[:4],
                    }
                    for p in selected
                ],
                "prompt": prompt,
            }
        )

    (curated_dir / "curated_collection_image_plan.json").write_text(
        json.dumps(briefs, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (curated_dir / "README.txt").write_text(
        "BKS curated collection image plan\n\n"
        "Questo piano riflette le scelte editoriali approvate: una sola modalita per "
        "collection, con alternativa scartata e motivazione curatoriale.\n",
        encoding="utf-8",
    )


def write_program(products: list[Product], out_dir: Path, modes: list[str], model_refs: list[str]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    collections = ["new-arrivals", *EDITORIAL_COLLECTIONS]
    briefs = []
    prompts_dir = out_dir / "prompts"
    previews_dir = out_dir / "contact_sheets"
    prompts_dir.mkdir(exist_ok=True)
    previews_dir.mkdir(exist_ok=True)

    for collection in collections:
        for mode in modes:
            limit = 4 if mode == "still-life" else 5
            selected = select_products(products, collection, mode, limit)
            prompt = build_prompt(collection, mode, selected, model_refs)
            slug = f"{collection}-{mode}"
            (prompts_dir / f"{slug}.txt").write_text(prompt, encoding="utf-8")
            contact_sheet = previews_dir / f"{slug}.jpg"
            make_contact_sheet(selected, contact_sheet, f"{collection} / {mode}")
            briefs.append(
                {
                    "collection": collection,
                    "mode": mode,
                    "ratio": "4:5",
                    "size_px": [2000, 2500],
                    "prompt_file": str((prompts_dir / f"{slug}.txt").resolve()),
                    "contact_sheet": str(contact_sheet.resolve()) if contact_sheet.exists() else "",
                    "model_references": model_refs if mode == "on-model" else [],
                    "selected_products": [
                        {
                            "handle": p.handle,
                            "title": p.title,
                            "type": p.product_type,
                            "collection": p.collection,
                            "macros": list(p.macros),
                            "image_src": p.image_src,
                            "local_images": p.local_images[:4],
                        }
                        for p in selected
                    ],
                    "prompt": prompt,
                }
            )

    inventory_path = out_dir / "asset_inventory.csv"
    with inventory_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["handle", "title", "type", "collection", "macros", "series", "image_count", "image_src"])
        for p in products:
            writer.writerow([p.handle, p.title, p.product_type, p.collection, ";".join(p.macros), p.series, len(p.local_images), p.image_src])

    (out_dir / "collection_image_briefs.json").write_text(
        json.dumps(briefs, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (out_dir / "README.txt").write_text(
        "BKS collection image program\n\n"
        "1. asset_inventory.csv = products detected from the Shopify CSV and local image archive.\n"
        "2. collection_image_briefs.json = generation-ready briefs with selected products and references.\n"
        "3. prompts/*.txt = prompts for each collection/mode.\n"
        "4. contact_sheets/*.jpg = visual QA sheets for the selected reference products.\n\n"
        "Put approved model/modelle reference images in input/models to include them in on-model briefs.\n"
        "Use still-life prompts for Shopify collection heroes. Use on-model prompts only with a generator "
        "or virtual try-on flow that accepts product reference images and model reference images.\n",
        encoding="utf-8",
    )
    write_curated_program(products, out_dir, model_refs)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build BKS Studio collection image briefs from catalog assets.")
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--image-dir", type=Path, default=DEFAULT_IMAGE_DIR)
    parser.add_argument("--model-dir", type=Path, default=DEFAULT_MODEL_DIR)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--mode", choices=["still-life", "on-model", "all"], default="all")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    modes = ["still-life", "on-model"] if args.mode == "all" else [args.mode]
    products = load_products(args.csv, args.image_dir)
    model_refs = list_model_refs(args.model_dir)
    write_program(products, args.out, modes, model_refs)
    print(f"Products indexed: {len(products)}")
    print(f"Model references indexed: {len(model_refs)}")
    print(f"Output: {args.out.resolve()}")


if __name__ == "__main__":
    main()
