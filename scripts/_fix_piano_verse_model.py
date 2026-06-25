"""
Add verse + model fields to index.json blocks,
Add #bks-coll-verse CSS to bks-piano-hero.css,
Add #bks-key-model CSS to bks-piano-hero.css,
Update bks-piano-hero.js openCollection() and buildKeys().
"""
import json
from pathlib import Path

ROOT = Path(r'I:\BAK ABO')

# ── 1. index.json — add verse + model_url to each piano block ─────────────────
VERSES = {
    "piano_hours":   "Le ore si pesano\nsenza che nessuno\nle stia contando.",
    "piano_glyph":   "Un alfabeto senza parole —\nsolo forma e vuoto.\nIl segno viene prima.",
    "piano_marker":  "Ogni luogo lascia\nun segno sul corpo\nprima ancora che tu parta.",
    "piano_riviera": "La luce del mezzogiorno\nnon perdona\nné ombra né misura.",
    "piano_pulse":   "Nel ritmo c'è una promessa\nche il tempo\nnon ha ancora tradito.",
    "piano_token":   "Quello che vale\nnon si vede —\nsi porta.",
    "piano_flag":    "Appartenere è involontario\ncome alzare gli occhi\nverso una bandiera.",
    "piano_origin":  "Le radici non cercano luce.\nSanno già\ndove andare.",
}

idx_path = ROOT / '04_TEMA_SHOPIFY/templates/index.json'
idx = json.loads(idx_path.read_text(encoding='utf-8'))

piano = idx['sections']['bks_piano_hero']['blocks']
for block_id, block in piano.items():
    if block_id in VERSES:
        block['settings']['verse']     = VERSES[block_id]
        block['settings']['model_url'] = ""  # placeholder — upload PNGs later

idx_path.write_text(json.dumps(idx, indent=2, ensure_ascii=False), encoding='utf-8')
print("1. index.json — verses added to all 8 collections")

# ── 2. bks-piano-hero.css — add verse + model overlay styles ──────────────────
css_path = ROOT / '04_TEMA_SHOPIFY/assets/bks-piano-hero.css'
css = css_path.read_text(encoding='utf-8').replace('\r\r\n', '\n').replace('\r\n', '\n').replace('\r', '\n')

VERSE_CSS = """
/* ── BKS Verse — poesia per collezione ──────────────────────────────────── */
#bks-coll-verse {
  margin: 8px 0 14px;
  padding: 0 0 0 12px;
  border-left: 2px solid currentColor;
  opacity: 0.75;
  font-family: 'DM Mono', monospace;
  font-size: 11px;
  font-style: italic;
  line-height: 1.7;
  white-space: pre-line;
  letter-spacing: 0.02em;
  color: inherit;
  display: none;
}
#bks-coll-verse:not(:empty) { display: block; }

/* ── 3D Model overlay — modello scontornato sul piano ───────────────────── */
#bks-key-model {
  position: absolute;
  bottom: 12%;
  width: auto;
  max-width: 22%;
  height: 82%;
  pointer-events: none;
  z-index: 8;
  opacity: 0;
  transform: translateY(18px) scale(0.88);
  transition: opacity 0.38s ease, transform 0.38s ease;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  filter: drop-shadow(0 8px 24px rgba(0,0,0,0.55));
}
#bks-key-model.bks-model-active {
  opacity: 1;
  transform: translateY(0) scale(1);
}
#bks-key-model img {
  max-height: 100%;
  max-width: 100%;
  width: auto;
  height: auto;
  object-fit: contain;
  object-position: bottom center;
}
"""

if '#bks-coll-verse' not in css:
    css = css + VERSE_CSS
    css_path.write_text(css, encoding='utf-8')
    print("2. bks-piano-hero.css — verse + model CSS added")
else:
    print("2. bks-piano-hero.css — already has verse CSS, skipped")

# ── 3. bks-piano-hero.js — update openCollection + buildKeys ──────────────────
js_path = ROOT / '04_TEMA_SHOPIFY/assets/bks-piano-hero.js'
js = js_path.read_text(encoding='utf-8').replace('\r\r\n', '\n').replace('\r\n', '\n').replace('\r', '\n')

# 3a. buildKeys — add cxPct + surBotPct to each key for model positioning
old_push_white = (
    "      keys.push({\n"
    "        idx, white: true,\n"
    "        tl:     { x: backX0  + i       * wBW + g, y: surTop  },\n"
    "        tr:     { x: backX0  + (i + 1) * wBW - g, y: surTop  },\n"
    "        bl:     { x: frontX0 + i       * wFW + g, y: faceBot },\n"
    "        br:     { x: frontX0 + (i + 1) * wFW - g, y: faceBot },\n"
    "        surBot, faceBot,\n"
    "      });\n"
)
new_push_white = (
    "      const cxPct = (frontX0 + (i + 0.5) * wFW) / W;\n"
    "      keys.push({\n"
    "        idx, white: true,\n"
    "        tl:     { x: backX0  + i       * wBW + g, y: surTop  },\n"
    "        tr:     { x: backX0  + (i + 1) * wBW - g, y: surTop  },\n"
    "        bl:     { x: frontX0 + i       * wFW + g, y: faceBot },\n"
    "        br:     { x: frontX0 + (i + 1) * wFW - g, y: faceBot },\n"
    "        surBot, faceBot, cxPct, surBotPct: surBot / H,\n"
    "      });\n"
)
assert old_push_white in js, "white key push not found"
js = js.replace(old_push_white, new_push_white, 1)
print("3a. buildKeys — added cxPct + surBotPct to white keys")

# 3b. Add cxPct+surBotPct to black keys too
old_push_black = (
    "      keys.push({\n"
    "        idx, white: false,\n"
    "        tl: { x: bkLB + g,        y: bkTop },\n"
    "        tr: { x: bkLB + bkWB - g, y: bkTop },\n"
    "        bl: { x: bkLF + g,        y: bkBot },\n"
    "        br: { x: bkLF + bkWF - g, y: bkBot },\n"
    "      });\n"
)
new_push_black = (
    "      const bkCxPct = (bkLF + bkWF / 2) / W;\n"
    "      keys.push({\n"
    "        idx, white: false,\n"
    "        tl: { x: bkLB + g,        y: bkTop },\n"
    "        tr: { x: bkLB + bkWB - g, y: bkTop },\n"
    "        bl: { x: bkLF + g,        y: bkBot },\n"
    "        br: { x: bkLF + bkWF - g, y: bkBot },\n"
    "        surBot: bkBot, faceBot: bkBot, cxPct: bkCxPct, surBotPct: bkBot / H,\n"
    "      });\n"
)
assert old_push_black in js, "black key push not found"
js = js.replace(old_push_black, new_push_black, 1)
print("3b. buildKeys — added cxPct + surBotPct to black keys")

# 3c. openCollection — add verse display + model positioning
old_open_end = (
    "    screen.classList.add('bks-show');\n"
    "    hint.classList.add('bks-hidden');\n"
    "    backBtn.classList.add('bks-visible');\n"
    "  }"
)
new_open_end = (
    "    screen.classList.add('bks-show');\n"
    "    hint.classList.add('bks-hidden');\n"
    "    backBtn.classList.add('bks-visible');\n"
    "\n"
    "    // BKS Verse — show collection poem\n"
    "    const verseEl = document.getElementById('bks-coll-verse');\n"
    "    if (verseEl) verseEl.textContent = col.verse || '';\n"
    "\n"
    "    // 3D model overlay — positioned at the active key on canvas\n"
    "    const modelEl  = document.getElementById('bks-key-model');\n"
    "    const modelImg = document.getElementById('bks-key-model-img');\n"
    "    if (modelEl && col.model_url) {\n"
    "      const k = keys.find(kk => kk.idx === idx);\n"
    "      if (k) {\n"
    "        if (modelImg) { modelImg.src = col.model_url; modelImg.alt = col.name; }\n"
    "        modelEl.style.left = (k.cxPct * 100) + '%';\n"
    "        modelEl.style.transform = 'translateX(-50%) translateY(18px) scale(0.88)';\n"
    "        modelEl.style.bottom = ((1 - k.surBotPct) * 100) + '%';\n"
    "        requestAnimationFrame(() => modelEl.classList.add('bks-model-active'));\n"
    "      }\n"
    "    } else if (modelEl) {\n"
    "      modelEl.classList.remove('bks-model-active');\n"
    "    }\n"
    "  }"
)
assert old_open_end in js, "openCollection end not found"
js = js.replace(old_open_end, new_open_end, 1)
print("3c. openCollection — verse + model overlay added")

# 3d. closeCollection — hide model overlay
old_close_end = (
    "    hint.classList.remove('bks-hidden');\n"
    "    backBtn.classList.remove('bks-visible');\n"
    "    if (collCta) collCta.style.color = '';\n"
    "  }"
)
new_close_end = (
    "    hint.classList.remove('bks-hidden');\n"
    "    backBtn.classList.remove('bks-visible');\n"
    "    if (collCta) collCta.style.color = '';\n"
    "    const mEl = document.getElementById('bks-key-model');\n"
    "    if (mEl) mEl.classList.remove('bks-model-active');\n"
    "  }"
)
assert old_close_end in js, "closeCollection end not found"
js = js.replace(old_close_end, new_close_end, 1)
print("3d. closeCollection — model overlay hidden")

js_path.write_text(js, encoding='utf-8')
print("\nAll JS changes saved.")

print("\nDone. Now push to Shopify.")
