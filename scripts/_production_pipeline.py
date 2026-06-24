"""
BKS Production Pipeline — orchestrazione completa.

Esegue in sequenza:
  1. Verifica prodotti approvati (™) su Printify
  2. Genera design con OpenAI → upload → update Printify
  3. Log risultati + statistiche finali

Modalità generazione:
  --local  (default) : Python chiama OpenAI direttamente — nessun timeout CF Worker
  --worker           : Chiama Worker (solo per test/debug — CF timeout 30s spesso causa HTML error)

Uso:
    python scripts/_production_pipeline.py                   # 200 prodotti, 3 paralleli, local mode
    python scripts/_production_pipeline.py --workers 1       # sequenziale (sicuro)
    python scripts/_production_pipeline.py --workers 5       # più veloce
    python scripts/_production_pipeline.py --collection pulse # solo una collezione
    python scripts/_production_pipeline.py --test 5          # prova 5 prodotti
    python scripts/_production_pipeline.py --resume          # continua da dove si era arrivati
    python scripts/_production_pipeline.py --dry-run         # solo prompt, no generazione
    python scripts/_production_pipeline.py --worker          # usa Worker CF (legacy, timeout 30s)
    python scripts/_production_pipeline.py --create-missing  # crea prodotti mancanti per ogni collezione
    python scripts/_production_pipeline.py --create-missing --collection flag --type tee  # crea solo Flag Tee
"""
from __future__ import annotations
import argparse, asyncio, json, sys, time
from datetime import datetime
from pathlib import Path

import urllib3
urllib3.disable_warnings()

try:
    import aiohttp
    ASYNC_OK = True
except ImportError:
    ASYNC_OK = False
    import requests  # fallback sincrono

import requests as rq  # usato per fetch sincrono Printify

ROOT = Path(__file__).resolve().parent.parent
env = {}
for raw in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
    line = raw.strip()
    if not line or line.startswith("#") or "=" not in line: continue
    k, v = line.split("=", 1)
    env[k.strip()] = v.strip().strip('"').strip("'")

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WORKER_URL     = "https://bks-agent.bakabo.workers.dev"
BKS_TOKEN      = env.get("BKS_AI_TOKEN") or env.get("BKS_ASSISTANT_PUBLIC_TOKEN", "")
PRINTIFY_TOKEN = env.get("PRINTIFY_API_TOKEN", "")
SHOP_ID        = env.get("PRINTIFY_SHOP_ID", "12030061")
OPENAI_KEY     = env.get("OPENAI_API_KEY", "")

WORKER_HDR   = {"Authorization": f"Bearer {BKS_TOKEN}", "Content-Type": "application/json"}
PRINTIFY_HDR = {"Authorization": f"Bearer {PRINTIFY_TOKEN}"}
LOG_PATH     = ROOT / "ecommerce_automation" / "design_batch_log.json"

COLLECTIONS   = ["hours", "glyph", "marker", "riviera", "pulse", "token", "flag", "origin"]

# ── Blueprint map — blueprint_id + print_provider_id rilevati dai prodotti esistenti ─
BLUEPRINT_MAP = {
    "tee":          {"blueprint_id": 279,  "print_provider_id": 10},
    "puffer":       {"blueprint_id": 934,  "print_provider_id": 14},
    "hoodie":       {"blueprint_id": 212,  "print_provider_id": 10},
    "lounge_pants": {"blueprint_id": 739,  "print_provider_id": 10},
    "windbreaker":  {"blueprint_id": 1397, "print_provider_id": 10},
    "backpack":     {"blueprint_id": 581,  "print_provider_id": 14},
    "sneakers":     {"blueprint_id": 291,  "print_provider_id": 14},
    "shorts":       {"blueprint_id": 1084, "print_provider_id": 83},
    "one_piece":    {"blueprint_id": 360,  "print_provider_id": 14},
    "swim_trunks":  {"blueprint_id": 589,  "print_provider_id": 83},
    "travel_bag":   {"blueprint_id": 888,  "print_provider_id": 14},
    "beach_towel":  {"blueprint_id": 371,  "print_provider_id": 14},
    "flip_flops":   {"blueprint_id": 587,  "print_provider_id": 1},
    "hawaiian":     {"blueprint_id": 924,  "print_provider_id": 14},
    "pullover":     {"blueprint_id": 439,  "print_provider_id": 14},
}

# Price ladder BKS — prezzi retail (cents) per product type
# Target da business rules: margine 55-65%, price ladder approvato BKS
PRODUCT_PRICE_MAP: dict[str, int] = {
    "tee":          5500,   # $55 — base $19, ship $5.5, margine ~60%
    "puffer":       12900,  # $129 — base $46, ship $11
    "hoodie":       7500,   # $75 — base $28, ship $8
    "lounge_pants": 6500,   # $65 — base $19, ship $8
    "windbreaker":  10900,  # $109 — base $33, ship $10
    "backpack":     8500,   # $85 — base $26, ship $11
    "sneakers":     8900,   # $89 — base $22, ship $11
    "shorts":       6500,   # $65 — base $17, ship $5.5
    "one_piece":    6500,   # $65 — base $21, ship $8
    "swim_trunks":  5500,   # $55 — base $17, ship $8
    "travel_bag":   9900,   # $99 — base $36, ship $11
    "beach_towel":  4500,   # $45 — base ~$18, ship $8
    "flip_flops":   4500,   # $45 — base $13, ship $5.5
    "hawaiian":     7500,   # $75 — base $24, ship $8
    "pullover":     6900,   # $69
}

# Shopify product type label per product_type
PRODUCT_TYPE_LABEL: dict[str, str] = {
    "tee": "T-Shirt", "puffer": "Puffer Jacket", "hoodie": "Hoodie",
    "lounge_pants": "Lounge Pants", "windbreaker": "Windbreaker",
    "backpack": "Backpack", "sneakers": "Sneakers", "shorts": "Athletic Shorts",
    "one_piece": "One-Piece Swimsuit", "swim_trunks": "Swim Trunks",
    "travel_bag": "Travel Bag", "beach_towel": "Beach Towel",
    "flip_flops": "Flip Flops", "hawaiian": "Hawaiian Shirt", "pullover": "Pullover",
}


# Keyword per identificare product type da titolo prodotto
# Tipi di prodotto AOP (all-over-print / dye-sublimation): il design copre TUTTA la superficie
# Per questi il prompt deve richiedere pattern seamless, nessun margine, copertura totale.
# Per i non-AOP (panel design): grafica isolata con spazio negativo attorno.
AOP_TYPES = frozenset({
    "tee", "hoodie", "pullover", "lounge_pants", "one_piece",
    "swim_trunks", "shorts", "hawaiian", "windbreaker", "puffer",
})

PRODUCT_TYPE_KEYWORDS = {
    "tee": ["tee", "t-shirt"], "puffer": ["puffer"], "hoodie": ["hoodie"],
    "lounge_pants": ["lounge pants", "lounge"], "windbreaker": ["windbreaker"],
    "backpack": ["backpack"], "sneakers": ["sneakers", "sneaker"],
    "shorts": ["shorts"], "one_piece": ["one-piece", "one piece"],
    "swim_trunks": ["swim trunks", "swim trunk"], "travel_bag": ["travel bag"],
    "beach_towel": ["beach towel"], "flip_flops": ["flip flop", "flip-flop"],
    "hawaiian": ["hawaiian"], "pullover": ["pullover"],
}
TITLE_KEYWORDS = {
    "hours": ["hours"], "glyph": ["glyph"], "marker": ["marker"],
    "riviera": ["riviera"], "pulse": ["pulse"], "token": ["token"],
    "flag": ["flag", "burst"], "origin": ["origin", "folklore"],  # folklore = vecchio nome di origin
}
# "folklore" nel titolo → collezione "origin" (rinomina avvenuta)
COLLECTION_ALIAS = {"folklore": "origin"}

def get_collection(tags, title: str = "") -> str:
    tag_list = tags if isinstance(tags, list) else [t.strip() for t in (tags or "").split(",")]
    for tag in tag_list:
        t = str(tag).strip().lower()
        if t.startswith("collection:"):
            col = t.split(":", 1)[1].strip()
            return COLLECTION_ALIAS.get(col, col)
    tl = title.lower()
    for col, keywords in TITLE_KEYWORDS.items():
        if any(kw in tl for kw in keywords):
            return COLLECTION_ALIAS.get(col, col)
    return "unknown"


def fetch_approved(collection_filter: str | None = None) -> list[dict]:
    products, page = [], 1
    print("Carico prodotti approvati da Printify...")
    while True:
        r = rq.get(
            f"https://api.printify.com/v1/shops/{SHOP_ID}/products.json?limit=20&page={page}",
            headers=PRINTIFY_HDR, verify=False, timeout=30,
        )
        if not r.ok: break
        batch = r.json().get("data", [])
        if not batch: break
        for p in batch:
            if "™" not in p.get("title", ""):
                continue
            col = get_collection(p.get("tags", ""), p.get("title", ""))
            if collection_filter and col != collection_filter:
                continue
            products.append({
                "id": p["id"], "title": p["title"],
                "visible": p.get("visible", False), "collection": col,
            })
        if len(batch) < 20: break
        page += 1
        time.sleep(0.15)
    return products


def load_log() -> dict:
    return json.loads(LOG_PATH.read_text(encoding="utf-8")) if LOG_PATH.exists() else {}

def save_log(log: dict):
    LOG_PATH.write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")


# ── Async worker call ─────────────────────────────────────────────────────────

async def call_worker_async(session, prod: dict, dry_run: bool, semaphore: asyncio.Semaphore) -> tuple[dict, dict]:
    col = prod["collection"] if prod["collection"] in COLLECTIONS else "glyph"
    payload = {"product_id": prod["id"], "collection": col, "dry_run": dry_run}
    async with semaphore:
        for attempt in range(3):
            try:
                if attempt > 0:
                    await asyncio.sleep(15 * attempt)  # backoff: 15s, 30s
                async with session.post(
                    f"{WORKER_URL}/design-generate",
                    headers=WORKER_HDR,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=180),
                    ssl=False,
                ) as resp:
                    text = await resp.text()
                    if resp.ok and not text.strip().startswith("<"):
                        try: return prod, json.loads(text)
                        except: pass
                    if text.strip().startswith("<") and attempt < 2:
                        continue  # Cloudflare HTML error page — retry
                    return prod, {"status": "error", "http": resp.status, "body": text[:200]}
            except Exception as e:
                if attempt < 2: continue
                return prod, {"status": "error", "body": str(e)[:200]}
        return prod, {"status": "error", "body": "max retries"}


def call_worker_sync(prod: dict, dry_run: bool) -> dict:
    col = prod["collection"] if prod["collection"] in COLLECTIONS else "glyph"
    payload = {"product_id": prod["id"], "collection": col, "dry_run": dry_run}
    try:
        r = rq.post(f"{WORKER_URL}/design-generate", headers=WORKER_HDR,
                    json=payload, timeout=180, verify=False)
        if r.ok and not r.text.strip().startswith("<"):
            return r.json()
        return {"status": "error", "http": r.status_code, "body": r.text[:300]}
    except Exception as e:
        return {"status": "error", "body": str(e)[:200]}


# ── Motore locale — bypassa Worker per evitare CF timeout (30s) ──────────────
# Chiama Worker solo per dry_run (prompt + template info), poi fa tutto in Python.

PRINTIFY_BASE = "https://api.printify.com/v1"
LOGO_IDS_L    = {"6a217ca23d24179e1f1eaf5f", "660d81c6209c2958d2f0bb75"}
LOGO_NAMES_L  = ["logo","log9","log0","sd0","sd1","barra","logo-base","logo_hoodie","logo z0"]
SKIP_POS_L    = {"inside_label","label","neck_label","inside label","label_inside","inside-label"}

# Override posizioni logo per blueprint dove il prototipo è errato o va completamente ridisegnato.
# Struttura: blueprint_id → {position_keyword → {logo_id → {x, y, scale, angle}}}
# Per sneakers (bp=291): logo piccolo solo sul tallone (y=0.85), non copertura totale body_outside.
BLUEPRINT_LOGO_OVERRIDE: dict[int, dict[str, dict]] = {
    # sneakers (bp=291): logo BKS piccolo sul tallone, non su tutta la superficie body_outside/inside
    291: {
        "body_outside": {
            "660d81c6209c2958d2f0bb75": {"x": 0.5,  "y": 0.85, "scale": 0.12, "angle": 0},
            "6a217ca23d24179e1f1eaf5f": {"x": 0.5,  "y": 0.85, "scale": 0.12, "angle": 0},
        },
        "body_inside": {
            "660d81c6209c2958d2f0bb75": {"x": 0.5,  "y": 0.50, "scale": 0.18, "angle": 0},
            "6a217ca23d24179e1f1eaf5f": {"x": 0.5,  "y": 0.50, "scale": 0.18, "angle": 0},
        },
    },
    # travel bag (bp=888): logo 660d81c6209c era a scale=1.0 front+back (copre tutto il pannello)
    # Fix: piccolo branding in alto (front) e in basso (back)
    888: {
        "front": {
            "660d81c6209c2958d2f0bb75": {"x": 0.5,  "y": 0.06, "scale": 0.14, "angle": 0},
            "6a217ca23d24179e1f1eaf5f": {"x": 0.5,  "y": 0.06, "scale": 0.14, "angle": 0},
        },
        "back": {
            "660d81c6209c2958d2f0bb75": {"x": 0.5,  "y": 0.88, "scale": 0.12, "angle": 0},
            "6a217ca23d24179e1f1eaf5f": {"x": 0.5,  "y": 0.88, "scale": 0.12, "angle": 0},
        },
        "left_side": {
            "660d81c6209c2958d2f0bb75": {"x": 0.5,  "y": 0.88, "scale": 0.12, "angle": 0},
            "6a217ca23d24179e1f1eaf5f": {"x": 0.5,  "y": 0.88, "scale": 0.12, "angle": 0},
        },
        "right_side": {
            "660d81c6209c2958d2f0bb75": {"x": 0.5,  "y": 0.88, "scale": 0.12, "angle": 0},
            "6a217ca23d24179e1f1eaf5f": {"x": 0.5,  "y": 0.88, "scale": 0.12, "angle": 0},
        },
    },
}

def _is_logo(img: dict) -> bool:
    return img.get("id") in LOGO_IDS_L or any(p in (img.get("name","")).lower() for p in LOGO_NAMES_L)

def _is_skip(ph: dict) -> bool:
    return ph.get("position","").lower().replace(" ","_") in SKIP_POS_L


# Cache prototipi per blueprint — evita chiamate API ridondanti nel batch
_PROTOTYPE_CACHE: dict[int, dict] = {}


def _get_prototype(blueprint_id: int | None, exclude_id: str = "") -> dict | None:
    """
    Restituisce il primo prodotto approvato (™) con il dato blueprint_id.
    Usato per replicare le posizioni esatte del logo (x/y/scale/angle) sui prodotti elaborati.
    Risultato in cache per blueprint — una sola chiamata API per tipo nel batch.
    """
    if not blueprint_id:
        return None
    if blueprint_id in _PROTOTYPE_CACHE:
        return _PROTOTYPE_CACHE[blueprint_id]

    hdr = {"Authorization": f"Bearer {PRINTIFY_TOKEN}"}
    for pg in range(1, 15):
        r = rq.get(
            f"{PRINTIFY_BASE}/shops/{SHOP_ID}/products.json?limit=20&page={pg}",
            headers=hdr, verify=False, timeout=30,
        )
        if not r.ok:
            break
        batch = r.json().get("data", [])
        for p in batch:
            if (p.get("blueprint_id") == blueprint_id
                    and "™" in p.get("title", "")
                    and p.get("id") != exclude_id):
                r2 = rq.get(
                    f"{PRINTIFY_BASE}/shops/{SHOP_ID}/products/{p['id']}.json",
                    headers=hdr, verify=False, timeout=20,
                )
                if r2.ok:
                    proto = r2.json()
                    _PROTOTYPE_CACHE[blueprint_id] = proto
                    return proto
        if len(batch) < 20:
            break
    return None


def get_product_type(title: str) -> str | None:
    """Identifica product type da titolo (es. 'Tee' → 'tee')."""
    tl = title.lower()
    for pt, kws in PRODUCT_TYPE_KEYWORDS.items():
        if any(kw in tl for kw in kws):
            return pt
    return None


def _build_bks_description(col: str, product_type: str, title: str,
                            col_cap: str, pt_label: str, price_fmt: str) -> str:
    """Genera descrizione BKS 5-blocchi per scheda prodotto."""
    collection_hooks = {
        "hours":   "Each piece carries the weight of passing time — geometric marks that accumulate into meaning.",
        "glyph":   "Symbols rewritten by AI into forms that never existed before. Language as surface.",
        "marker":  "Bold brushwork captured before it dries. The gesture is the design.",
        "riviera": "Mediterranean light distilled into pattern — salt, sun, and the geometry of leisure.",
        "pulse":   "The rhythm of the city encoded in fabric. Motion made permanent.",
        "token":   "Digital artifacts printed on organic form. The pixel meets the fiber.",
        "flag":    "Graphic identity as declaration. Every wear is a stance.",
        "origin":  "Art from the archive — expressive roots, contemporary surface.",
    }
    hook = collection_hooks.get(col, f"AI-generated artwork from the BKS {col_cap} collection.")

    return (
        f"<p><strong>{hook}</strong></p>"
        f"<p>This {pt_label} carries an original AI-generated graphic from the <em>BKS {col_cap}</em> collection — "
        f"designed in Italy by BKS Studio, made on demand worldwide.</p>"
        f"<p><strong>Design</strong> — Each surface is unique: generated by AI, approved by the BKS quality gate (21/25 minimum score), "
        f"then applied directly to the garment with no mass-production run.</p>"
        f"<p><strong>Production</strong> — Made after purchase. No overstock. Ships in 5–10 business days. "
        f"Fulfillment via global print-on-demand network.</p>"
        f"<p><strong>Wear it</strong> — {price_fmt} · Designed in Italy · Made on demand · "
        f"<a href='https://bakabo.club'>bakabo.club</a></p>"
    )


def fix_product_sheet(product_id: str, col: str, product_type: str) -> dict:
    """
    Aggiorna scheda prodotto esistente: prezzi BKS, tags, descrizione 5 blocchi, visible=False.
    Usato per correggere prodotti creati prima dell'introduzione dello standard scheda.
    """
    ph = {"Authorization": f"Bearer {PRINTIFY_TOKEN}", "Content-Type": "application/json"}

    # Carica prodotto attuale
    r = rq.get(f"{PRINTIFY_BASE}/shops/{SHOP_ID}/products/{product_id}.json",
               headers=ph, verify=False, timeout=30)
    if not r.ok:
        return {"status": "error", "body": f"Prodotto non trovato: {r.status_code}"}

    prod = r.json()
    title    = prod.get("title", "")
    col_cap  = col.capitalize()
    pt_label = PRODUCT_TYPE_LABEL.get(product_type, product_type.replace("_", " ").title())
    base_price = PRODUCT_PRICE_MAP.get(product_type, 5500)
    price_fmt  = f"${base_price // 100}"
    LARGE_SIZE_KEYWORDS = {"2xl", "xxl", "3xl", "xxxl", "4xl", "5xl"}

    # Aggiorna variants con BKS price ladder
    updated_variants = []
    for v in prod.get("variants", []):
        size_raw  = str(v.get("title", "")).lower()
        surcharge = 500 if any(k in size_raw for k in LARGE_SIZE_KEYWORDS) else 0
        updated_variants.append({
            "id":         v["id"],
            "price":      base_price + surcharge,
            "is_enabled": v.get("is_enabled", True),
        })

    tags = [
        f"collection:{col}",
        f"bakabo-{product_type.replace('_', '-')}",
        "made-on-demand",
        "bakabo-approved",
        "designed-in-italy",
        "ai-generated",
        f"bks-{col_cap.lower()}",
    ]

    description = _build_bks_description(col, product_type, title, col_cap, pt_label, price_fmt)

    patch = {
        "description": description,
        "tags":        tags,
        "variants":    updated_variants,
        "visible":     False,
    }

    r_upd = rq.put(f"{PRINTIFY_BASE}/shops/{SHOP_ID}/products/{product_id}.json",
                   headers=ph, json=patch, verify=False, timeout=30)
    if not r_upd.ok:
        return {"status": "error", "body": f"Update fallito: {r_upd.text[:300]}"}

    return {
        "status":     "fixed",
        "product_id": product_id,
        "title":      title,
        "price":      base_price,
        "tags":       tags,
    }


def create_product_on_printify(col: str, product_type: str, design_id: str, title: str,
                                description: str = "") -> dict:
    """
    Crea un nuovo prodotto su Printify clonando la struttura da uno esistente (stesso blueprint).
    Regola: se il prodotto non esiste → crea da zero.
    """
    bp_info = BLUEPRINT_MAP.get(product_type)
    if not bp_info:
        return {"status": "error", "body": f"Product type '{product_type}' non in BLUEPRINT_MAP"}

    bp_id   = bp_info["blueprint_id"]
    prov_id = bp_info["print_provider_id"]
    ph      = {"Authorization": f"Bearer {PRINTIFY_TOKEN}", "Content-Type": "application/json"}

    # 1. Trova un prodotto esistente con lo stesso blueprint — scansiona TUTTE le pagine
    clone_source = None
    for pg in range(1, 15):  # max 14 pagine × 20 = 280 prodotti
        r_pg = rq.get(
            f"{PRINTIFY_BASE}/shops/{SHOP_ID}/products.json?limit=20&page={pg}",
            headers={"Authorization": f"Bearer {PRINTIFY_TOKEN}"}, verify=False, timeout=30,
        )
        if not r_pg.ok: break
        batch_pg = r_pg.json().get("data", [])
        if not batch_pg: break
        for p in batch_pg:
            if p.get("blueprint_id") == bp_id and p.get("print_provider_id") == prov_id:
                # Carica il prodotto completo (include print_areas con placeholder)
                r_full = rq.get(
                    f"{PRINTIFY_BASE}/shops/{SHOP_ID}/products/{p['id']}.json",
                    headers={"Authorization": f"Bearer {PRINTIFY_TOKEN}"}, verify=False, timeout=30,
                )
                if r_full.ok:
                    clone_source = r_full.json()
                break
        if clone_source or len(batch_pg) < 20: break
        time.sleep(0.1)

    if not clone_source:
        return {"status": "error", "body": f"Nessun prodotto con blueprint {bp_id}/prov {prov_id} da clonare"}

    # 2. Costruisci variants con BKS price ladder
    base_price = PRODUCT_PRICE_MAP.get(product_type, 5500)
    LARGE_SIZE_KEYWORDS = {"2xl", "xxl", "3xl", "xxxl", "4xl", "5xl"}

    clone_variants = []
    for v in clone_source.get("variants", []):
        if not v.get("is_enabled", True):
            continue
        # Size surcharge: +$5 per taglie extra-large
        size_raw = str(v.get("title", "")).lower()
        surcharge = 500 if any(k in size_raw for k in LARGE_SIZE_KEYWORDS) else 0
        clone_variants.append({
            "id":         v["id"],
            "price":      base_price + surcharge,
            "is_enabled": True,
        })

    # 3. Costruisci print_areas con il nuovo design + posizionamento sezione aurea φ=1.618
    clone_areas = []
    for area in clone_source.get("print_areas", []):
        new_placeholders = []
        for ph_item in area.get("placeholders", []):
            pos = ph_item.get("position", "")
            if pos.lower().replace(" ", "_") in SKIP_POS_L:
                new_placeholders.append(ph_item)
                continue
            new_imgs = []
            for img in ph_item.get("images", []):
                if _is_logo(img):
                    new_imgs.append(img)
                else:
                    new_imgs.append({**img, "id": design_id})
            if new_imgs:
                new_placeholders.append({**ph_item, "images": new_imgs})
        if new_placeholders:
            clone_areas.append({**area, "placeholders": new_placeholders})

    # 4. Scheda prodotto BKS — 5 blocchi
    col_cap  = col.capitalize()
    pt_label = PRODUCT_TYPE_LABEL.get(product_type, product_type.replace("_", " ").title())
    price_fmt = f"${base_price // 100}"

    if not description:
        description = _build_bks_description(col, product_type, title, col_cap, pt_label, price_fmt)

    # 5. Tags BKS standard
    tags = [
        f"collection:{col}",
        f"bakabo-{product_type.replace('_', '-')}",
        "made-on-demand",
        "bakabo-approved",
        "designed-in-italy",
        "ai-generated",
        f"bks-{col_cap.lower()}",
    ]

    body = {
        "title":              title,
        "description":        description,
        "blueprint_id":       bp_id,
        "print_provider_id":  prov_id,
        "variants":           clone_variants,
        "print_areas":        clone_areas,
        "tags":               tags,
        "visible":            False,  # Draft — attende revisione pre-publish gate
    }

    r_create = rq.post(
        f"{PRINTIFY_BASE}/shops/{SHOP_ID}/products.json",
        headers=ph, json=body, verify=False, timeout=60,
    )
    if not r_create.ok:
        return {"status": "error", "body": f"Printify create fallito: {r_create.text[:300]}"}

    new_prod = r_create.json()
    return {
        "status":       "created",
        "product_id":   new_prod.get("id"),
        "title":        new_prod.get("title"),
        "blueprint_id": bp_id,
        "collection":   col,
        "product_type": product_type,
        "price":        base_price,
        "tags":         tags,
    }


def call_local_full(prod: dict, dry_run: bool) -> dict:
    """Genera design localmente: Worker dry_run → OpenAI Python SDK → Printify."""
    import base64, io

    if not OPENAI_KEY:
        return {"status": "error", "body": "OPENAI_API_KEY mancante in .env"}
    if not PRINTIFY_TOKEN:
        return {"status": "error", "body": "PRINTIFY_API_TOKEN mancante in .env"}

    prod_id = prod["id"]
    col     = prod["collection"] if prod["collection"] in COLLECTIONS else "glyph"
    ph      = {"Authorization": f"Bearer {PRINTIFY_TOKEN}", "Content-Type": "application/json"}

    # 1. Dry-run al Worker per ottenere prompt + template info (richiesta veloce <5s)
    dry = call_worker_sync(prod, dry_run=True)
    if dry.get("status") == "no_design":
        return {"status": "no_design", "body": "Worker: nessun template per questo prodotto"}
    if dry.get("status") != "dry_run":
        return {"status": "error", "body": f"Worker dry_run fallito: {dry.get('body','?')[:150]}"}

    if dry_run:
        return dry

    artwork_prompt = dry.get("artwork_prompt", "")
    mode           = dry.get("decision", {}).get("mode", "generate")
    design_ids     = dry.get("design_ids", [])

    # Inietta regola sezione aurea nel prompt — composizione φ=1.618
    artwork_prompt += (
        " Composition rule (mandatory): apply golden ratio φ=1.618. "
        "Place the main graphic element at the upper golden point (38.2% from top). "
        "61.8% dominant area / 38.2% negative space. "
        "Color harmony: 60% dominant / 30% secondary / 10% accent. "
        "Never perfectly centered. Raw editorial BKS style, not generic mockup."
    )

    # Inietta direttiva stampa: AOP (pezza intera) vs panel (grafica modulare)
    pt = get_product_type(prod.get("title", ""))
    if pt in AOP_TYPES:
        artwork_prompt += (
            " PRINT TYPE — All-Over Print (AOP): the design must cover the ENTIRE surface "
            "with NO empty space, NO borders, NO margins. "
            "Pattern must be seamless and tile-ready OR fill canvas edge to edge. "
            "No isolated single graphic — the surface IS the artwork."
        )
    else:
        artwork_prompt += (
            " PRINT TYPE — Panel/placement graphic: one focused design element "
            "with clean edges and sufficient negative space around it for precise garment placement. "
            "Not a repeating pattern. One strong composition occupying 50-70% of canvas."
        )

    # 2. Se mode=edit, scarica template da Printify
    template_bytes: bytes | None = None
    template_name  = (dry.get("decision") or {}).get("template", {}) or {}
    tpl_fname      = template_name.get("name", "template.jpg") if isinstance(template_name, dict) else "template.jpg"

    if mode == "edit" and design_ids:
        for did in design_ids:
            u_r = rq.get(f"{PRINTIFY_BASE}/uploads/{did}.json", headers=ph, verify=False, timeout=20)
            if not u_r.ok:
                continue
            tpl_url = u_r.json().get("preview_url")
            if not tpl_url:
                continue
            t_r = rq.get(tpl_url, timeout=40, verify=False)
            if t_r.ok:
                template_bytes = t_r.content
                break
        if not template_bytes:
            mode = "generate"  # fallback se template non scaricabile

    # 3. Chiama OpenAI gpt-image-1
    import httpx
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_KEY, http_client=httpx.Client(verify=False))
    try:
        if mode == "edit" and template_bytes:
            resp = client.images.edit(
                model="gpt-image-1",
                image=("template.jpg", io.BytesIO(template_bytes), "image/jpeg"),
                prompt=artwork_prompt,
                n=1,
                size="1024x1024",
            )
        else:
            resp = client.images.generate(
                model="gpt-image-1",
                prompt=artwork_prompt,
                n=1,
                size="1024x1024",
                quality="medium",
                output_format="jpeg",
            )
        img_b64 = resp.data[0].b64_json
    except Exception as e:
        return {"status": "error", "body": f"OpenAI fallito: {str(e)[:200]}"}

    if not img_b64:
        return {"status": "error", "body": "OpenAI: nessuna immagine nel response"}

    # 3.5 Post-processing — schiarimento automatico se troppo scuro per la collezione
    # Soglie luminosità media (0-255): valori bassi = scuro. Hours/Token permettono il buio.
    _BRIGHT_THRESH = {
        "hours": 58, "token": 62, "origin": 68,
        "glyph": 74, "marker": 78, "pulse": 85,
        "riviera": 90, "flag": 90,
    }
    try:
        from PIL import Image, ImageEnhance
        _thresh = _BRIGHT_THRESH.get(col, 83)
        _raw    = base64.b64decode(img_b64)
        _pil    = Image.open(io.BytesIO(_raw)).convert("RGB")
        _gray   = _pil.convert("L")
        _avg_b  = sum(_gray.tobytes()) / (_gray.width * _gray.height)
        if _avg_b < _thresh:
            _boost = min(1.35, (_thresh + 12) / max(_avg_b, 1))
            _pil   = ImageEnhance.Brightness(_pil).enhance(_boost)
            _buf   = io.BytesIO()
            _pil.save(_buf, format="JPEG", quality=92)
            img_b64  = base64.b64encode(_buf.getvalue()).decode()
            file_ext = "jpg"
            print(f"  BRIGHTEN  col={col} avg={_avg_b:.0f}/{_thresh} boost={_boost:.2f}x")
    except ImportError:
        pass  # Pillow non installato — salta
    except Exception:
        pass  # Non blocca il flusso

    # 4. Upload su Printify
    file_ext    = "jpg" if mode == "generate" else "png"
    upload_body = json.dumps({
        "file_name": f"bks_{col}_{prod_id[-6:]}_{int(time.time()*1000)}.{file_ext}",
        "contents":  img_b64,
    })
    up_r = rq.post(f"{PRINTIFY_BASE}/uploads/images.json",
                   data=upload_body, headers=ph, verify=False, timeout=60)
    if not up_r.ok:
        return {"status": "error", "body": f"Upload Printify fallito: {up_r.text[:200]}"}

    new_img_id = up_r.json().get("id", "")
    if not new_img_id:
        return {"status": "error", "body": "Upload OK ma nessun ID ricevuto"}

    # 5. Ricarica print_areas + replica posizione logo dal prototipo dello stesso tipo
    prod_r = rq.get(f"{PRINTIFY_BASE}/shops/{SHOP_ID}/products/{prod_id}.json",
                    headers=ph, verify=False, timeout=20)
    if not prod_r.ok:
        return {"status": "error", "body": f"Ricarica prodotto fallita: {prod_r.status_code}", "new_image_id": new_img_id}

    prod_data    = prod_r.json()
    blueprint_id = prod_data.get("blueprint_id")
    print_areas  = prod_data.get("print_areas", [])

    # Mappa (position, logo_id) → coordinate esatte dal prototipo
    proto_logo_pos: dict[tuple, dict] = {}
    proto = _get_prototype(blueprint_id, exclude_id=prod_id)
    if proto:
        for p_area in proto.get("print_areas", []):
            for p_ph in p_area.get("placeholders", []):
                p_pos = p_ph.get("position", "")
                for p_img in p_ph.get("images", []):
                    if _is_logo(p_img):
                        proto_logo_pos[(p_pos, p_img.get("id", ""))] = {
                            "x": p_img.get("x"), "y": p_img.get("y"),
                            "scale": p_img.get("scale"), "angle": p_img.get("angle"),
                        }

    bp_override   = BLUEPRINT_LOGO_OVERRIDE.get(blueprint_id, {})
    design_id_set = set(design_ids)
    # Aree panel (non-sleeve) per puffer (bp=934): back/front con scale~1 — deduplicare a 1 artwork
    PUFFER_PANEL_POSITIONS = {"back", "front", "collar"}
    replaced = 0
    for area in print_areas:
        for placeholder in area.get("placeholders", []):
            if not _is_skip(placeholder):
                pos = placeholder.get("position", "")
                for img in placeholder.get("images", []):
                    if _is_logo(img):
                        logo_id = img.get("id", "")
                        # 1. Controlla override specifico per blueprint (es. sneakers)
                        pos_key = next((k for k in bp_override if k in pos.lower()), None)
                        if pos_key and logo_id in bp_override[pos_key]:
                            img.update(bp_override[pos_key][logo_id])
                        # 2. Altrimenti replica dal prototipo
                        elif (pos, logo_id) in proto_logo_pos:
                            img.update(proto_logo_pos[(pos, logo_id)])
                    elif img.get("id") in design_id_set:
                        img["id"] = new_img_id
                        replaced += 1
                # Puffer bp=934: deduplica aree panel (back/front) — lascia solo 1 artwork image
                if blueprint_id == 934 and pos.lower() in PUFFER_PANEL_POSITIONS:
                    imgs = placeholder.get("images", [])
                    artwork = [im for im in imgs if not _is_logo(im)]
                    logos   = [im for im in imgs if _is_logo(im)]
                    if len(artwork) > 1:
                        placeholder["images"] = [artwork[0]] + logos

    clean_areas = [
        {**a, "placeholders": [p for p in a.get("placeholders", []) if p.get("images")]}
        for a in print_areas
        if any(p.get("images") for p in a.get("placeholders", []))
    ]

    # 6. Update prodotto su Printify
    upd_r = rq.put(f"{PRINTIFY_BASE}/shops/{SHOP_ID}/products/{prod_id}.json",
                   headers=ph, json={"print_areas": clean_areas}, verify=False, timeout=30)
    if not upd_r.ok:
        return {"status": "error", "body": f"Update prodotto fallito: {upd_r.text[:200]}", "new_image_id": new_img_id}

    # 7. Valutazione automatica — Worker /design-evaluate (gpt-4o vision)
    eval_score    = None
    eval_decision = None
    eval_feedback = None
    eval_dims     = None
    try:
        # Ottieni preview URL dell'immagine appena caricata
        preview_r = rq.get(f"{PRINTIFY_BASE}/uploads/{new_img_id}.json", headers=ph, verify=False, timeout=20)
        if preview_r.ok:
            preview_url = preview_r.json().get("preview_url")
            if preview_url:
                ev_r = rq.post(f"{WORKER_URL}/design-evaluate",
                               headers=WORKER_HDR,
                               json={"image_url": preview_url, "collection": col, "product_title": prod.get("title", "")},
                               verify=False, timeout=60)
                if ev_r.ok and not ev_r.text.strip().startswith("<"):
                    ev = ev_r.json()
                    eval_score    = ev.get("score")
                    eval_decision = ev.get("decision")
                    eval_feedback = ev.get("feedback")
                    eval_dims     = ev.get("dimensions")
    except Exception:
        pass  # Valutazione opzionale — non blocca il flusso

    result = {
        "status": "updated",
        "new_image_id": new_img_id,
        "areas_replaced": replaced,
        "template_used": tpl_fname,
    }
    if eval_score is not None:
        result["bks_score"]    = eval_score
        result["bks_decision"] = eval_decision
        result["bks_feedback"] = eval_feedback
        result["bks_dims"]     = eval_dims
        if eval_score < 20:
            result["status"] = "needs_rework"
    return result


def print_result(i: int, total: int, prod: dict, result: dict):
    pid, col = prod["id"], prod["collection"]
    pub   = "PUB" if prod["visible"] else "DRF"
    title = prod["title"][:45].encode("ascii", "replace").decode()
    status = result.get("status", "error")
    print(f"\n[{i:>3}/{total}] [{pub}] {col:10s} | {title}")
    if status == "dry_run":
        plen = len(result.get("artwork_prompt", ""))
        print(f"  DRY  prompt={plen}ch  mode={result.get('decision',{}).get('mode','?')}")
    elif status == "updated":
        new_id  = result.get("new_image_id", "")[:12]
        rep     = result.get("areas_replaced", 0)
        tpl     = result.get("template_used") or "none"
        print(f"  OK   image={new_id}  areas={rep}  tpl={tpl}")
    elif status == "no_design":
        print(f"  SKIP nessun design area")
    else:
        err = (result.get("body") or result.get("error", "?"))[:100]
        print(f"  ERR  {err}")


async def run_async(products: list[dict], dry_run: bool, max_workers: int, log: dict):
    connector = aiohttp.TCPConnector(ssl=False, limit=max_workers)
    semaphore = asyncio.Semaphore(max_workers)
    stats = {"ok": 0, "dry_run": 0, "no_design": 0, "error": 0}
    total = len(products)

    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [call_worker_async(session, prod, dry_run, semaphore) for prod in products]
        for i, coro in enumerate(asyncio.as_completed(tasks), 1):
            prod, result = await coro
            status = result.get("status", "error")
            print_result(i, total, prod, result)
            stats[{"updated":"ok","dry_run":"dry_run","no_design":"no_design"}.get(status,"error")] += 1
            log[prod["id"]] = {
                "ts": datetime.now().isoformat(), "collection": prod["collection"],
                "title": prod["title"], "visible": prod["visible"],
                "status": status, "result": result,
            }
            save_log(log)
    return stats


def run_sync(products: list[dict], dry_run: bool, pause: float, log: dict, use_worker: bool = False) -> dict:
    stats = {"ok": 0, "dry_run": 0, "no_design": 0, "error": 0}
    for i, prod in enumerate(products, 1):
        result = call_worker_sync(prod, dry_run) if use_worker else call_local_full(prod, dry_run)
        status = result.get("status", "error")
        print_result(i, len(products), prod, result)
        stats[{"updated":"ok","dry_run":"dry_run","no_design":"no_design"}.get(status,"error")] += 1
        log[prod["id"]] = {
            "ts": datetime.now().isoformat(), "collection": prod["collection"],
            "title": prod["title"], "visible": prod["visible"],
            "status": status, "result": result,
        }
        save_log(log)
        time.sleep(pause)
    return stats


def _run_create_missing(collection_filter: str | None, type_filter: str | None):
    """
    Regola: se prodotto non esiste per una collezione/tipo → crea su Printify.
    Genera design con OpenAI, carica su Printify, crea prodotto.
    """
    print("BKS Create Missing Products")
    ph = {"Authorization": f"Bearer {PRINTIFY_TOKEN}", "Content-Type": "application/json"}

    # 1. Mappa esistente usando fetch_approved (funziona su tutti i 200 prodotti)
    all_prods_list = fetch_approved(None)
    existing: dict[tuple, str] = {}
    col_bp_map: dict[str, dict] = {}  # col → {blueprint_id, print_provider_id, product_id}
    for p in all_prods_list:
        col = p["collection"]
        pt  = get_product_type(p["title"])
        if col and pt and (col, pt) not in existing:
            existing[(col, pt)] = p["id"]

    # Carica blueprint info da Printify per prodotti campione (full product data)
    print(f"  {len(existing)} (col,type) pair trovati tra {len(all_prods_list)} prodotti ™")

    # 2. Desired matrix: ogni collezione × product types prioritari
    DESIRED: dict[str, list[str]] = {
        "hours":   ["tee","puffer","lounge_pants","windbreaker","travel_bag"],
        "glyph":   ["tee","puffer","backpack","sneakers","travel_bag"],
        "marker":  ["tee","hoodie","windbreaker","backpack","shorts"],
        "riviera": ["tee","swim_trunks","beach_towel","flip_flops","hawaiian","travel_bag"],
        "pulse":   ["tee","hoodie","windbreaker","sneakers","backpack"],
        "token":   ["tee","backpack","sneakers","windbreaker","travel_bag"],
        "flag":    ["tee","hoodie","beach_towel","shorts","windbreaker"],
        "origin":  ["tee","lounge_pants","beach_towel","windbreaker","travel_bag"],
    }

    cols = [collection_filter] if collection_filter else COLLECTIONS
    to_create = []
    for col in cols:
        for pt in DESIRED.get(col, []):
            if type_filter and pt != type_filter:
                continue
            if (col, pt) not in existing:
                to_create.append((col, pt))

    if not to_create:
        print("  Nessun prodotto mancante trovato.")
        return

    print(f"  {len(to_create)} prodotti mancanti da creare:")
    for col, pt in to_create:
        print(f"    - {col} / {pt}")
    print("=" * 65)

    # Mappa collection → prodotto_id reale (per dry_run prompt)
    col_sample_id: dict[str, str] = {}
    all_prods = fetch_approved(None)
    for p in all_prods:
        c = p["collection"]
        if c not in col_sample_id:
            col_sample_id[c] = p["id"]

    ok_count = 0
    for i, (col, pt) in enumerate(to_create, 1):
        col_cap  = col.capitalize()
        pt_label = pt.replace("_", " ").title()
        title    = f"BKS {col_cap} {pt_label}™"
        print(f"\n[{i:>3}/{len(to_create)}] {col:8} / {pt:15} → {title}")

        # a. Ottieni prompt da Worker usando un prodotto reale della stessa collezione
        sample_id = col_sample_id.get(col)
        if not sample_id:
            print(f"  ERR  Nessun prodotto campione per collezione {col}")
            continue
        sample_prod = {"id": sample_id, "collection": col, "title": title, "visible": False}
        dry = call_worker_sync(sample_prod, dry_run=True)
        if dry.get("status") != "dry_run":
            print(f"  ERR  Worker dry_run: {dry.get('body','?')[:100]}")
            continue

        artwork_prompt = dry.get("artwork_prompt", "")

        # b. Genera immagine con OpenAI (generate da zero — nessun template)
        import httpx
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_KEY, http_client=httpx.Client(verify=False))
        try:
            resp = client.images.generate(
                model="gpt-image-1", prompt=artwork_prompt,
                n=1, size="1024x1024", quality="medium", output_format="jpeg",
            )
            img_b64 = resp.data[0].b64_json
        except Exception as e:
            print(f"  ERR  OpenAI: {str(e)[:100]}")
            continue

        # c. Upload su Printify
        upload_body = json.dumps({
            "file_name": f"bks_{col}_{pt}_{int(time.time()*1000)}.jpg",
            "contents":  img_b64,
        })
        up_r = rq.post(f"{PRINTIFY_BASE}/uploads/images.json",
                       data=upload_body, headers=ph, verify=False, timeout=60)
        if not up_r.ok:
            print(f"  ERR  Upload: {up_r.text[:150]}")
            continue
        new_img_id = up_r.json().get("id", "")

        # d. Crea prodotto su Printify
        result = create_product_on_printify(col, pt, new_img_id, title)
        if result.get("status") == "created":
            print(f"  OK   product_id={result['product_id']}  title={result['title']}")
            ok_count += 1
        else:
            print(f"  ERR  {result.get('body','?')[:150]}")

        time.sleep(2)

    print(f"\n{'='*65}")
    print(f"Creati: {ok_count}/{len(to_create)}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run",    action="store_true")
    parser.add_argument("--resume",     action="store_true")
    parser.add_argument("--test",       type=int, default=0)
    parser.add_argument("--collection", default=None)
    parser.add_argument("--workers",    type=int, default=3, help="Paralleli (default 3, max 5)")
    parser.add_argument("--pause",      type=float, default=3.0, help="Pausa sec tra chiamate (sync)")
    parser.add_argument("--worker",         action="store_true", help="Usa Worker CF invece del motore locale (legacy, può dare timeout)")
    parser.add_argument("--create-missing", action="store_true", help="Crea prodotti mancanti per ogni collezione")
    parser.add_argument("--type",           default=None, help="Product type per --create-missing (es. tee, hoodie)")
    parser.add_argument("--fix-product",    default=None, metavar="PRODUCT_ID", help="Aggiorna scheda prodotto esistente (prezzi, tags, desc, draft)")
    parser.add_argument("--retry-rework",   action="store_true", help="Ri-genera solo i prodotti needs_rework (score < 20)")
    parser.add_argument("--force",           action="store_true", help="PERICOLOSO: ri-processa anche prodotti già updated/approvati")
    args = parser.parse_args()

    # ── Modalità --fix-product ─────────────────────────────────────────────────
    if args.fix_product:
        if not args.collection or not args.type:
            print("ERR: --fix-product richiede --collection e --type")
            return
        result = fix_product_sheet(args.fix_product, args.collection, args.type)
        if result["status"] == "fixed":
            print(f"OK   product={result['product_id']}  title={result['title']}  price=${result['price']//100}  tags={result['tags']}")
        else:
            print(f"ERR  {result['body']}")
        return

    # ── Modalità --create-missing ──────────────────────────────────────────────
    if args.create_missing:
        _run_create_missing(args.collection, args.type)
        return

    products = fetch_approved(args.collection)
    print(f"  Trovati {len(products)} prodotti approvati (™)")

    log = load_log()

    # ── SAFETY GATE (default) ─────────────────────────────────────────────────
    # Per default skip tutti i prodotti già updated (approvati). Richiede --force
    # per sovrascrivere prodotti già processati con successo.
    if args.force:
        print("  [!] --force attivo: ri-processo TUTTI i prodotti inclusi quelli già approvati")
    elif args.retry_rework:
        before = len(products)
        products = [p for p in products if log.get(p["id"], {}).get("status") in ("needs_rework", "dry_run")]
        print(f"  Retry-rework: {len(products)} needs_rework/dry_run da ri-generare (su {before} totali)")
    else:
        # Default sicuro: salta updated + excluded + no_design, processa solo nuovi + needs_rework + error
        before = len(products)
        SAFE_SKIP = {"updated", "excluded", "no_design"}
        products = [p for p in products if log.get(p["id"], {}).get("status") not in SAFE_SKIP]
        skipped = before - len(products)
        rework_n = sum(1 for p in products if log.get(p["id"], {}).get("status") == "needs_rework")
        new_n = sum(1 for p in products if p["id"] not in log)
        print(f"  Safe mode: {skipped} già approvati saltati | {new_n} nuovi + {rework_n} rework = {len(products)} da processare")
        print(f"  (usa --force per ri-processare tutti, --retry-rework per solo rework)")

    if args.resume:
        before = len(products)
        products = [p for p in products if p["id"] not in log or log[p["id"]].get("status") == "error"]
        print(f"  Resume: {before - len(products)} già OK, {len(products)} da processare")

    if args.test:
        products = products[:args.test]
        print(f"  TEST MODE: {args.test} prodotti")

    if not products:
        print("Nessun prodotto da processare.")
        return

    use_worker = args.worker
    use_async  = ASYNC_OK and args.workers > 1 and not args.dry_run and use_worker
    mode_str   = f"[ASYNC ×{args.workers}]" if use_async else "[SYNC]"
    mode_dry   = "[DRY-RUN]" if args.dry_run else "[LIVE]"
    mode_eng   = "[WORKER-CF]" if use_worker else "[LOCAL-PYTHON]"

    print(f"\nBKS Production Pipeline {mode_dry} {mode_str} {mode_eng} — {len(products)} prodotti")
    eta_min = len(products) * (45 if use_async else 60) // (args.workers if use_async else 1) // 60
    print(f"ETA stimata: ~{eta_min} minuti")
    print("=" * 65)

    start = datetime.now()

    if use_async:
        stats = asyncio.run(run_async(products, args.dry_run, min(args.workers, 5), log))
    else:
        stats = run_sync(products, args.dry_run, args.pause, log, use_worker=use_worker)

    elapsed = (datetime.now() - start).seconds
    print(f"\n{'='*65}")
    print(f"Completati   : {stats['ok']}")
    print(f"Dry run      : {stats['dry_run']}")
    print(f"Saltati      : {stats['no_design']}")
    print(f"Errori       : {stats['error']}")
    print(f"Tempo         : {elapsed//60}m {elapsed%60}s")
    print(f"Log           : {LOG_PATH}")


if __name__ == "__main__":
    main()
