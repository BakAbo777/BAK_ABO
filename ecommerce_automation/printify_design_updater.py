"""
BKS — Printify Design Updater
Sostituisce l'immagine design (pezza/artwork) di un prodotto Printify
mantenendo intatto il logo BKS e tutte le posizioni/scale/angoli.

Uso:
    from ecommerce_automation.printify_design_updater import update_product_design
    result = update_product_design(
        shop_id="12030061",
        product_id="6a2544f48ca667581803f49b",
        new_image_path=Path("output/generated/bks-hours-brocade-new.png"),
        client=printify_client,
    )
"""
from __future__ import annotations

import copy
import re
from collections import Counter
from pathlib import Path
from typing import Any

# ID e nomi logo BKS — non modificare mai
BKS_LOGO_IDS = {
    "6a217ca23d24179e1f1eaf5f",  # bks.png (shorts/apparel)
    "660d81c6209c2958d2f0bb75",  # LG 002.png (sneakers)
}
BKS_LOGO_NAMES = {
    "bks.png", "bks_logo.png", "bks-logo.png",
    "lg 002.png", "lg002.png", "lg_002.png",  # sneaker logo
}
# Pattern nomi logo: file che iniziano con "LG " o "BKS" senza "wonder_"
BKS_LOGO_PATTERNS = re.compile(r"^(lg\s*\d+|bks[\s_-]*(logo|label|tag)).*\.(png|svg)$", re.IGNORECASE)


def _is_logo(img: dict[str, Any]) -> bool:
    """Ritorna True se l'immagine è un elemento logo/branding BKS — da preservare."""
    img_id   = str(img.get("id", ""))
    img_name = str(img.get("name", "")).lower().strip()
    if img_id in BKS_LOGO_IDS:
        return True
    if img_name in BKS_LOGO_NAMES:
        return True
    if BKS_LOGO_PATTERNS.match(img_name):
        return True
    return False


def _find_design_image_ids(print_areas: list[dict]) -> set[str]:
    """
    Trova gli ID delle immagini design (non-logo) presenti nei print_areas.
    Il design principale è quello più frequente tra i placeholder.
    """
    counter: Counter = Counter()
    for area in print_areas:
        for ph in area.get("placeholders", []):
            for img in ph.get("images", []):
                if not _is_logo(img):
                    counter[img["id"]] += 1
    # Tutti gli id non-logo (potrebbe esserci più di uno)
    return set(counter.keys())


def _replace_design_in_areas(
    print_areas: list[dict],
    old_ids: set[str],
    new_id: str,
) -> list[dict]:
    """
    Clona print_areas sostituendo ogni immagine con id in old_ids
    con new_id, preservando x/y/scale/angle/layer.
    Il logo non viene mai toccato.
    """
    updated = copy.deepcopy(print_areas)
    for area in updated:
        for ph in area.get("placeholders", []):
            for img in ph.get("images", []):
                if _is_logo(img):
                    continue
                if img.get("id") in old_ids:
                    img["id"] = new_id
    return updated


def update_product_design(
    shop_id: str,
    product_id: str,
    new_image_path: Path,
    client: Any,
    dry_run: bool = False,
) -> dict[str, Any]:
    """
    Pipeline completa:
    1. Legge il prodotto da Printify
    2. Identifica le immagini design (non-logo)
    3. Carica la nuova immagine su Printify
    4. Sostituisce i layer design nei print_areas
    5. Aggiorna il prodotto (salvo dry_run)

    Ritorna dict con: product_id, old_design_ids, new_image_id,
                      areas_modified, dry_run, status
    """
    # 1. Fetch prodotto
    product = client.get_product(shop_id, product_id)
    title   = product.get("title", product_id)
    areas   = product.get("print_areas", [])

    # 2. Trova ID design da sostituire
    old_ids = _find_design_image_ids(areas)
    if not old_ids:
        return {"status": "no_design_found", "product_id": product_id, "title": title}

    # 3. Upload nuova immagine
    img_bytes  = new_image_path.read_bytes()
    file_name  = new_image_path.name
    if not dry_run:
        upload_result = client.upload_image_from_bytes(file_name, img_bytes)
        new_image_id  = upload_result.get("id", "")
        if not new_image_id:
            return {"status": "upload_failed", "error": str(upload_result)}
    else:
        new_image_id = "DRY-RUN-ID"

    # 4. Costruisce nuove print_areas
    new_areas = _replace_design_in_areas(areas, old_ids, new_image_id)

    # Conta modifiche
    count_replaced = sum(
        1
        for area in new_areas
        for ph in area.get("placeholders", [])
        for img in ph.get("images", [])
        if img.get("id") == new_image_id
    )

    # 5. Aggiorna prodotto
    if not dry_run:
        client.update_product(shop_id, product_id, {"print_areas": new_areas})
        status = "updated"
    else:
        status = "dry_run_ok"

    return {
        "status":          status,
        "product_id":      product_id,
        "title":           title,
        "old_design_ids":  list(old_ids),
        "new_image_id":    new_image_id,
        "new_image_file":  file_name,
        "areas_modified":  count_replaced,
        "dry_run":         dry_run,
    }
