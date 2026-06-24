"""
Armocromista — abbina prodotti a collezioni per colore dominante.
Analizza ogni source image, estrae palette dominante,
trova la combinazione migliore: 8 collezioni x 8 prodotti diversi.
"""
from pathlib import Path
from PIL import Image
import numpy as np

SOURCE_DIR = Path("I:/BAK ABO/BAKABO_IMAGE_FACTORY_v1.1/output/source")

# Palette collezioni (bg + accent)
COLLECTIONS = {
    "hours":   {"bg": (26, 26, 26),     "accent": (201, 183, 156), "mood": "dark-warm"},
    "glyph":   {"bg": (10, 10, 10),     "accent": (201, 183, 156), "mood": "dark-cold"},
    "marker":  {"bg": (245, 240, 232),  "accent": (10, 10, 10),    "mood": "light-neutral"},
    "riviera": {"bg": (232, 220, 200),  "accent": (42, 139, 133),  "mood": "warm-teal"},
    "pulse":   {"bg": (14, 20, 32),     "accent": (201, 183, 156), "mood": "dark-navy"},
    "token":   {"bg": (8, 8, 16),       "accent": (201, 183, 156), "mood": "darkest"},
    "flag":    {"bg": (250, 250, 247),  "accent": (10, 10, 10),    "mood": "pure-pop"},
    "folklore":{"bg": (237, 229, 208),  "accent": (42, 139, 133),  "mood": "warm-organic"},
}

def dominant_colors(img_path: Path, n: int = 5) -> np.ndarray:
    """Estrae n colori dominanti via k-means semplificato (quantize)."""
    img = Image.open(img_path).convert("RGB").resize((150, 150))
    arr = np.array(img).reshape(-1, 3).astype(float)
    # rimuovi sfondo (pixel molto chiari o molto scuri al bordo)
    mask = (arr.sum(axis=1) > 30) & (arr.sum(axis=1) < 700)
    arr = arr[mask]
    if len(arr) < 10:
        return arr[:n]
    # cluster semplice: dividi in n bucket per luminosità
    lum = arr.mean(axis=1)
    indices = np.argsort(lum)
    buckets = np.array_split(indices, n)
    centers = np.array([arr[b].mean(axis=0) for b in buckets if len(b)])
    return centers

def color_distance(c1, c2) -> float:
    return float(np.sqrt(sum((a - b) ** 2 for a, b in zip(c1, c2))))

def product_affinity(img_path: Path, col_name: str) -> float:
    """Score: quanto il prodotto è affine alla collezione (più basso = meglio)."""
    palette = COLLECTIONS[col_name]
    try:
        dom = dominant_colors(img_path)
    except Exception:
        return 9999.0
    # distanza media dai colori dominanti del prodotto verso bg+accent
    bg_dists = [color_distance(c, palette["bg"]) for c in dom]
    ac_dists = [color_distance(c, palette["accent"]) for c in dom]
    # peso: avvicinarsi all'accent vale più che avvicinarsi al bg
    score = min(bg_dists) * 0.4 + min(ac_dists) * 0.6
    return score

def product_type_from_name(name: str) -> str:
    name = name.lower()
    if "sneaker" in name or "loafer" in name or "slipper" in name or "flip" in name: return "shoes"
    if "puffer" in name or "jacket" in name or "windbreaker" in name: return "jacket"
    if "dress" in name: return "dress"
    if "pants" in name or "lounge" in name: return "pants"
    if "hoodie" in name or "sweat" in name: return "hoodie"
    if "tee" in name or "t-shirt" in name or "shirt" in name: return "shirt"
    if "bag" in name or "backpack" in name or "duffel" in name: return "bag"
    if "swimsuit" in name or "one-piece" in name: return "swimwear"
    if "trunk" in name or "short" in name: return "shorts"
    return "other"

# Carica tutte le source image (escludi mockup numerati)
sources = [f for f in SOURCE_DIR.glob("*_source.*") if f.suffix in {".jpg", ".png", ".webp"}]
print(f"Analisi {len(sources)} prodotti vs 8 collezioni...\n")

# Calcola score per ogni prodotto x collezione
scores = {}
for img in sources:
    pname = img.stem.replace("_source", "")
    ptype = product_type_from_name(pname)
    col_scores = {}
    for col in COLLECTIONS:
        col_scores[col] = product_affinity(img, col)
    scores[pname] = {"type": ptype, "path": img, "scores": col_scores}

# Selezione greedy: per ogni collezione, il prodotto col score più basso
# che non sia già stato usato e che abbia tipo diverso dagli altri già scelti
COLLECTION_ORDER = ["folklore", "riviera", "marker", "flag", "hours", "glyph", "pulse", "token"]
selected = {}
used_products = set()
used_types = set()

for col in COLLECTION_ORDER:
    candidates = sorted(
        [(pname, data["scores"][col], data["type"], data["path"])
         for pname, data in scores.items()
         if pname not in used_products],
        key=lambda x: x[1]
    )
    # Preferisci tipo non ancora usato
    chosen = None
    for pname, score, ptype, path in candidates:
        if ptype not in used_types:
            chosen = (pname, score, ptype, path)
            break
    if not chosen:
        chosen = candidates[0]

    pname, score, ptype, path = chosen
    selected[col] = {"product": pname, "type": ptype, "score": round(score, 1), "path": path}
    used_products.add(pname)
    used_types.add(ptype)

print("=" * 70)
print(f"{'COLLEZIONE':<12} {'TIPO':<12} {'SCORE':>6}  PRODOTTO")
print("=" * 70)
for col in COLLECTION_ORDER:
    s = selected[col]
    print(f"{col.upper():<12} {s['type']:<12} {s['score']:>6.1f}  {s['product']}")

print("\nFile source selezionati:")
for col in COLLECTION_ORDER:
    s = selected[col]
    print(f"  {col}: {s['path'].name}")
