"""
BKS Pattern Registry Generator
Crea bks_patterns.json — il catalogo ufficiale di tutte le pezze BKS.

Formato ID: BKS-{COLLECTION}-{NNN}
Esempio:    BKS-GLYPH-001, BKS-HOURS-007

Usage: python scripts/generate_pattern_registry.py
Output: output/bks_patterns.json
"""
from __future__ import annotations
import json, re
from pathlib import Path
from datetime import datetime

ROOT       = Path(__file__).parent.parent
BATCH_LOG  = ROOT / "ecommerce_automation" / "design_batch_log.json"
SYNC_LOG   = ROOT / "output" / "mockup_sync_log.json"
OUT_FILE   = ROOT / "output" / "bks_patterns.json"

# Mappa collezione → prefisso ID
COLLECTION_CODES = {
    "flag":     "FLAG",
    "glyph":    "GLYPH",
    "hours":    "HOURS",
    "marker":   "MARKER",
    "origin":   "ORIGIN",
    "pulse":    "PULSE",
    "riviera":  "RIVIERA",
    "token":    "TOKEN",
    "folklore": "ORIGIN",   # alias storico → origin
    "unknown":  "STUDIO",
}

def load_json(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}

def main():
    batch = load_json(BATCH_LOG)
    sync  = load_json(SYNC_LOG)

    # Indice shopify_id per printify_id dal sync log
    shopify_index = {}
    for pid, entry in sync.items():
        if isinstance(entry, dict) and entry.get("shopify_id"):
            shopify_index[pid] = str(entry["shopify_id"])

    # Raggruppa per template (una pezza può avere più prodotti derivati)
    template_map: dict[str, list] = {}
    for pid, entry in batch.items():
        if not isinstance(entry, dict):
            continue
        template = entry.get("result", {}).get("template_used", "")
        if not template:
            template = f"_no_template_{pid[:6]}"
        if template not in template_map:
            template_map[template] = []
        template_map[template].append((pid, entry))

    # Costruisci registry ordinato per collezione
    counters: dict[str, int] = {}
    patterns: dict[str, dict] = {}

    for template, products in sorted(template_map.items()):
        # Prendi il primo prodotto come rappresentante
        pid, entry = products[0]
        col_raw  = (entry.get("collection") or "unknown").lower()
        col_code = COLLECTION_CODES.get(col_raw, "STUDIO")

        counters[col_code] = counters.get(col_code, 0) + 1
        pattern_id = f"BKS-{col_code}-{counters[col_code]:03d}"

        result = entry.get("result", {})
        dims   = result.get("bks_dims", {})
        score  = result.get("bks_score", 0)

        # Tutti i prodotti derivati da questa pezza
        derived_products = []
        for p_id, p_entry in products:
            derived_products.append({
                "printify_id": p_id,
                "shopify_id":  shopify_index.get(p_id, ""),
                "title":       p_entry.get("title", ""),
                "visible":     p_entry.get("visible", False),
            })

        patterns[pattern_id] = {
            "id":           pattern_id,
            "collection":   col_raw,
            "template":     template,
            "quality_score": score,
            "quality_dims": {
                "identity":   dims.get("identity", 0),
                "execution":  dims.get("execution", 0),
                "color":      dims.get("color", 0),
                "invention":  dims.get("invention", 0),
                "commercial": dims.get("commercial", 0),
            },
            "decision":     result.get("bks_decision", ""),
            "feedback":     result.get("bks_feedback", ""),
            "products":     derived_products,
            "created_at":   entry.get("ts", ""),
            "status":       "active" if entry.get("visible") else "draft",
        }

    # Statistiche
    stats = {
        "total":       len(patterns),
        "by_collection": {},
        "score_distribution": {"excellent": 0, "good": 0, "draft": 0},
    }
    for p in patterns.values():
        col = p["collection"]
        stats["by_collection"][col] = stats["by_collection"].get(col, 0) + 1
        s = p["quality_score"]
        if s >= 22:
            stats["score_distribution"]["excellent"] += 1
        elif s >= 20:
            stats["score_distribution"]["good"] += 1
        else:
            stats["score_distribution"]["draft"] += 1

    registry = {
        "_meta": {
            "version":      "1.0",
            "generated_at": datetime.now().isoformat(),
            "description":  "BKS Pattern Registry — catalogo ufficiale delle pezze BKS",
            "id_format":    "BKS-{COLLECTION}-{NNN}",
            "stats":        stats,
        },
        "patterns": patterns,
    }

    OUT_FILE.write_text(json.dumps(registry, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Registry generato: {OUT_FILE}")
    print(f"Totale pezze: {stats['total']}")
    print(f"Per collezione: {stats['by_collection']}")
    print(f"Score distribution: {stats['score_distribution']}")

if __name__ == "__main__":
    main()
