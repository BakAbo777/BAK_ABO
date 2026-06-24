"""Genera collage 4x2 con le 8 candidate hero images per review visiva."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(r"I:\BAK ABO\output\catalog_images\hero_candidates")

# Rimuovi file dalla prima scan errata
for f in OUT.glob("*_opt*.jpg"):
    f.unlink()
    print(f"Rimosso: {f.name}")

# File correnti dalla seconda scan
FILES = {
    "bks-hours":   "bks-hours_best_pullover-hoodie.jpg",
    "bks-glyph":   "bks-glyph_best_windbreaker-jacket.jpg",
    "bks-marker":  "bks-marker_best_windbreaker-jacket.jpg",
    "bks-riviera": "bks-riviera_best_windbreaker-jacket.jpg",
    "bks-pulse":   "bks-pulse_best_windbreaker-jacket.jpg",
    "bks-token":   "bks-token_best_windbreaker-jacket.jpg",
    "bks-flag":    "bks-flag_best_windbreaker-jacket.jpg",
    "bks-origin":  "bks-origin_best_windbreaker-jacket.jpg",
}

COLS = list(FILES.keys())
W, H = 300, 300
COLS_N = 4
ROWS = 2
PAD = 8
LABEL_H = 24
FONT_SIZE = 13

canvas_w = COLS_N * (W + PAD) + PAD
canvas_h = ROWS * (H + LABEL_H + PAD) + PAD
canvas = Image.new("RGB", (canvas_w, canvas_h), (18, 16, 14))
draw = ImageDraw.Draw(canvas)

try:
    font = ImageFont.truetype("arial.ttf", FONT_SIZE)
except:
    font = ImageFont.load_default()

for i, col in enumerate(COLS):
    row = i // COLS_N
    c = i % COLS_N
    x = PAD + c * (W + PAD)
    y = PAD + row * (H + LABEL_H + PAD)
    fpath = OUT / FILES[col]
    if fpath.exists():
        img = Image.open(fpath).convert("RGB")
        img.thumbnail((W, H))
        # Center crop
        iw, ih = img.size
        if iw < W or ih < H:
            bg = Image.new("RGB", (W, H), (40, 38, 36))
            bg.paste(img, ((W - iw) // 2, (H - ih) // 2))
            img = bg
        canvas.paste(img, (x, y))
    else:
        draw.rectangle([x, y, x+W, y+H], fill=(50, 48, 46))
        draw.text((x+W//2, y+H//2), "MISSING", fill=(200,100,100), anchor="mm", font=font)

    # Label
    label = col.replace("bks-","").upper()
    draw.text((x + W//2, y + H + 4), label, fill=(200,195,185), anchor="mt", font=font)

out_path = OUT / "_PREVIEW_GRID.jpg"
canvas.save(out_path, "JPEG", quality=90)
print(f"Collage salvato: {out_path}")

import os
os.startfile(str(out_path))
