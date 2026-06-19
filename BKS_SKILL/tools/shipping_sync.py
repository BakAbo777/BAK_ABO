"""
BKS Shipping Sync Tool
Sincronizza prezzi spedizione Printify → analisi margini → report coerenza Shopify/Google.
"""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

BASE_DIR = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = BASE_DIR / "output"
CACHE_FILE = OUTPUT_DIR / "bks_shipping_sync.json"
ENV_FILE   = BASE_DIR / ".env"

PRINTIFY_BASE = "https://api.printify.com/v1"
SHOP_ID_DEFAULT = "12030061"

# Country → region mapping for display
COUNTRY_REGION: dict[str, str] = {
    "IT": "EU", "DE": "EU", "FR": "EU", "ES": "EU", "NL": "EU", "BE": "EU",
    "AT": "EU", "PL": "EU", "SE": "EU", "DK": "EU", "FI": "EU", "PT": "EU",
    "GR": "EU", "IE": "EU", "CZ": "EU", "RO": "EU", "HU": "EU", "SK": "EU",
    "BG": "EU", "HR": "EU", "LT": "EU", "LV": "EU", "EE": "EU", "SI": "EU",
    "CY": "EU", "MT": "EU", "LU": "EU",
    "GB": "UK", "CH": "CH", "NO": "EU_EXT", "IS": "EU_EXT",
    "US": "US", "CA": "CA", "AU": "AU", "NZ": "AU",
    "JP": "ASIA", "KR": "ASIA", "SG": "ASIA", "HK": "ASIA",
    "AE": "ME", "SA": "ME", "QA": "ME",
    "BR": "LATAM", "MX": "LATAM", "AR": "LATAM",
    "CN": "CN",
    "REST_OF_THE_WORLD": "ROW",
}

KEY_MARKETS = ["IT", "DE", "FR", "ES", "GB", "US", "CA", "AU", "NL", "SE", "CH", "JP", "AE"]

PRODUCT_TYPE_NAMES: dict[str, str] = {
    "934_14":  "Puffer Jacket (AOP)",
    "1391_14": "Women Puffer Jacket",
    "739_10":  "Lounge Pants",
    "360_14":  "One-Piece Swimsuit",
    "1084_83": "Athletic Long Shorts",
    "1095_90": "Cozy Slippers",
    "587_1":   "Flip Flops",
    "888_14":  "Travel Bag / Duffle",
    "291_14":  "Sneakers",
    "372_10":  "Duffel Bag",
    "279_10":  "Women Cut&Sew Tee",
    "589_83":  "Swim Trunks",
    "1397_10": "Windbreaker Jacket",
    "924_14":  "Hawaiian Shirt",
    "1626_99": "Woven Blanket",
    "450_10":  "Pullover Hoodie",
    "413_10":  "Backpack",
    "276_10":  "Racerback Dress",
    "1006_10": "Beach Towel",
}


def _load_env() -> None:
    if not ENV_FILE.exists():
        return
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def _get(token: str, path: str, timeout: int = 25) -> Any:
    headers = {"Authorization": f"Bearer {token}", "User-Agent": "BKS-ShippingSync/1.0"}
    try:
        r = requests.get(f"{PRINTIFY_BASE}{path}", headers=headers, timeout=timeout, verify=True)
    except requests.exceptions.SSLError:
        r = requests.get(f"{PRINTIFY_BASE}{path}", headers=headers, timeout=timeout, verify=False)
    if not r.ok:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:200]}")
    return r.json()


def _resolve_shop(token: str) -> str:
    saved = os.environ.get("PRINTIFY_SHOP_ID", "").strip()
    shops = _get(token, "/shops.json", timeout=15)
    if not isinstance(shops, list):
        raise RuntimeError("shops.json returned unexpected format")
    valid = {str(s["id"]) for s in shops}
    if saved and saved in valid:
        return saved
    import re
    pref_raw = os.environ.get("PRINTIFY_SHOP_TITLE", "bakabo.club")
    pref_words = [w for w in re.split(r"[\s,]+", pref_raw.lower()) if len(w) > 3]
    for s in shops:
        hay = (str(s.get("title", "")) + " " + str(s.get("sales_channel", ""))).lower()
        if any(w in hay for w in pref_words):
            return str(s["id"])
    for s in shops:
        if str(s.get("sales_channel", "")) in ("shopify", "etsy"):
            return str(s["id"])
    return str(shops[0]["id"])


def _cost_for_country(profiles: list[dict], country: str) -> dict[str, float] | None:
    """Return first/additional shipping cost in USD for a given country code."""
    direct_match = None
    row_match = None
    for prof in profiles:
        countries = prof.get("countries", [])
        f = prof.get("first_item", {}).get("cost", 0) / 100
        a = prof.get("additional_items", {}).get("cost", 0) / 100
        if country in countries:
            direct_match = {"first": f, "additional": a, "source": "explicit"}
        if "REST_OF_THE_WORLD" in countries:
            row_match = {"first": f, "additional": a, "source": "REST_OF_THE_WORLD"}
    return direct_match or row_match


def build_report(token: str | None = None, progress_cb=None) -> dict[str, Any]:
    """Full shipping sync — fetches Printify and builds the report."""
    _load_env()
    token = token or os.environ.get("PRINTIFY_API_TOKEN", "").strip()
    if not token:
        raise RuntimeError("PRINTIFY_API_TOKEN non configurato")

    if progress_cb:
        progress_cb("Connessione Printify…", 0)
    shop_id = _resolve_shop(token)

    # ── Fetch all products ──────────────────────────────────────────
    if progress_cb:
        progress_cb("Download catalogo prodotti…", 10)
    all_products: list[dict] = []
    page = 1
    while True:
        data = _get(token, f"/shops/{shop_id}/products.json?page={page}&limit=20", timeout=30)
        batch = data.get("data", [])
        all_products.extend(batch)
        if page >= data.get("last_page", 1):
            break
        page += 1
        time.sleep(0.08)

    # ── Group by blueprint+provider ─────────────────────────────────
    combos: dict[str, dict[str, Any]] = {}
    for p in all_products:
        bp = str(p.get("blueprint_id", ""))
        pp = str(p.get("print_provider_id", ""))
        key = f"{bp}_{pp}"
        if key not in combos:
            combos[key] = {
                "key": key,
                "blueprint_id": int(bp),
                "print_provider_id": int(pp),
                "name": PRODUCT_TYPE_NAMES.get(key, f"BP:{bp} PP:{pp}"),
                "products": [],
                "retail_prices": [],
            }
        combos[key]["products"].append(p.get("title", ""))
        for v in p.get("variants", []):
            if v.get("is_enabled") and v.get("price"):
                combos[key]["retail_prices"].append(v["price"])

    # ── Fetch shipping for each combo ───────────────────────────────
    total = len(combos)
    for idx, (key, combo) in enumerate(combos.items()):
        if progress_cb:
            pct = 20 + int((idx / total) * 60)
            progress_cb(f"Spedizioni {combo['name']}…", pct)
        bp = combo["blueprint_id"]
        pp = combo["print_provider_id"]
        try:
            ship = _get(token, f"/catalog/blueprints/{bp}/print_providers/{pp}/shipping.json", timeout=20)
            combo["handling_days"] = ship.get("handling_time", {}).get("value", 10)
            combo["profiles"] = ship.get("profiles", [])
        except Exception as e:
            combo["shipping_error"] = str(e)
            combo["handling_days"] = 10
            combo["profiles"] = []
        time.sleep(0.12)

    # ── Build analysis ──────────────────────────────────────────────
    if progress_cb:
        progress_cb("Analisi margini e copertura…", 85)

    by_type: list[dict[str, Any]] = []
    alerts_global: list[dict] = []

    for key, combo in sorted(combos.items(), key=lambda x: -len(x[1]["products"])):
        prices = combo.get("retail_prices", [])
        retail_min = min(prices) / 100 if prices else 0
        retail_max = max(prices) / 100 if prices else 0
        retail_avg = (sum(prices) / len(prices)) / 100 if prices else 0

        profiles = combo.get("profiles", [])
        markets: list[dict] = []
        alerts: list[str] = []

        for market in KEY_MARKETS:
            shipping = _cost_for_country(profiles, market)
            region = COUNTRY_REGION.get(market, "?")
            if shipping:
                margin_min = retail_min - shipping["first"] if retail_min else None
                margin_avg = retail_avg - shipping["first"] if retail_avg else None
                markets.append({
                    "country": market,
                    "region": region,
                    "ship_first": shipping["first"],
                    "ship_add": shipping["additional"],
                    "ship_source": shipping["source"],
                    "margin_min": round(margin_min, 2) if margin_min is not None else None,
                    "margin_avg": round(margin_avg, 2) if margin_avg is not None else None,
                })
                # Alert: shipping > 25% of retail
                if retail_avg > 0 and shipping["first"] > retail_avg * 0.25:
                    alerts.append(f"⚠ {market}: spedizione ${shipping['first']:.2f} = {shipping['first']/retail_avg*100:.0f}% del prezzo medio")
            else:
                markets.append({"country": market, "region": region, "ship_first": None, "covered": False})
                alerts.append(f"✗ {market}: paese NON coperto")

        if alerts:
            alerts_global.extend([{"type": combo["name"], "msg": a} for a in alerts])

        by_type.append({
            "key": key,
            "name": combo["name"],
            "product_count": len(combo["products"]),
            "handling_days": combo.get("handling_days", 10),
            "retail_min": round(retail_min, 2),
            "retail_max": round(retail_max, 2),
            "retail_avg": round(retail_avg, 2),
            "markets": markets,
            "alerts": alerts,
            "sample_products": combo["products"][:3],
        })

    # ── Key market coverage summary ─────────────────────────────────
    country_coverage: dict[str, dict] = {}
    for country in KEY_MARKETS:
        covered_by = [t["name"] for t in by_type if any(m["country"] == country and m.get("ship_first") is not None for m in t["markets"])]
        shipping_range = []
        for t in by_type:
            for m in t["markets"]:
                if m["country"] == country and m.get("ship_first") is not None:
                    shipping_range.append(m["ship_first"])
        country_coverage[country] = {
            "region": COUNTRY_REGION.get(country, "?"),
            "covered_by_types": len(covered_by),
            "ship_min": min(shipping_range) if shipping_range else None,
            "ship_max": max(shipping_range) if shipping_range else None,
        }

    report = {
        "generated_at": datetime.now().isoformat(),
        "shop_id": shop_id,
        "total_products": len(all_products),
        "total_types": len(by_type),
        "key_markets_summary": country_coverage,
        "by_type": by_type,
        "alerts": alerts_global,
        "sync_targets": {
            "printify": {"status": "source_of_truth", "last_sync": datetime.now().isoformat()},
            "shopify": {"note": "Importare profili spedizione dal report. Zones: EU €8-15, US $6-20, ROW $10-25"},
            "google_merchant": {"note": "Feed shipping: usare i valori ship_first per ogni paese come costo flat"},
            "youtube_shopping": {"note": "Connesso a Google Merchant Center — aggiornamento automatico dal feed"},
        },
        "recommendations": _build_recommendations(by_type, country_coverage),
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    if progress_cb:
        progress_cb("Completato", 100)
    return report


def _build_recommendations(by_type: list, country_coverage: dict) -> list[dict]:
    recs = []

    # Check IT coverage (home market)
    it = country_coverage.get("IT", {})
    if it.get("ship_min") is not None:
        recs.append({
            "priority": "HIGH",
            "market": "IT",
            "msg": f"Italia: spedizioni ${it['ship_min']:.2f}—${it['ship_max']:.2f} USD. Considerare spedizione gratuita sopra €80.",
        })

    # High shipping alert
    for t in by_type:
        for m in t["markets"]:
            if m.get("ship_first") and m.get("margin_avg") is not None and m["margin_avg"] < 15:
                recs.append({
                    "priority": "MEDIUM",
                    "market": m["country"],
                    "msg": f"{t['name']} → {m['country']}: margine basso ${m['margin_avg']:.2f} dopo spedizione ${m['ship_first']:.2f}",
                })

    # Discount suggestion: free shipping threshold
    for t in by_type:
        if t["retail_avg"] > 80:
            recs.append({
                "priority": "LOW",
                "market": "ALL",
                "msg": f"{t['name']}: prezzo medio ${t['retail_avg']:.2f} — candidato per promozione 'free shipping' in EU/US",
            })

    return recs[:20]


if __name__ == "__main__":
    print("BKS Shipping Sync — avvio…")
    _load_env()
    token = os.environ.get("PRINTIFY_API_TOKEN", "")
    if not token:
        print("ERROR: PRINTIFY_API_TOKEN non trovato nel .env")
        sys.exit(1)

    def cb(msg: str, pct: int) -> None:
        print(f"  [{pct:3d}%] {msg}")

    report = build_report(token, progress_cb=cb)
    print(f"\nReport salvato in: {CACHE_FILE}")
    print(f"Prodotti: {report['total_products']} | Tipi: {report['total_types']}")
    print(f"Alert totali: {len(report['alerts'])}")
    print(f"Raccomandazioni: {len(report['recommendations'])}")
    print()
    print("=== MERCATI CHIAVE ===")
    for country, info in report["key_markets_summary"].items():
        ship = f"${info['ship_min']:.2f}—${info['ship_max']:.2f}" if info["ship_min"] is not None else "NON COPERTO"
        print(f"  {country} ({info['region']}): {ship} USD · {info['covered_by_types']} tipi prodotto")
