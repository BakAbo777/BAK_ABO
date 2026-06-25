"""Redesign piano keys to front-facing low-angle perspective matching reference photo."""
path = r'I:\BAK ABO\04_TEMA_SHOPIFY\assets\bks-piano-hero.js'
with open(path, 'r', encoding='utf-8') as f:
    src = f.read()

src = src.replace('\r\r\n', '\n').replace('\r\n', '\n').replace('\r', '\n')

# ── 1. buildKeys ──────────────────────────────────────────────────────────────
old_bk = (
    '  function buildKeys() {\n'
    '    keys = [];\n'
    '    const whites = COLS.filter(c => c.white);\n'
    '    const nW  = whites.length;\n'
    '    const fY  = H, bY = H * 0.24;\n'
    '    const fW  = W, bW = W * 0.46;\n'
    '    const sF  = 0, sB = (W - bW) / 2;\n'
    '    const wFW = fW / nW, wBW = bW / nW;\n'
    '    const g   = 1.2;\n'
)

assert old_bk in src, f"buildKeys signature not found"

# Find start of buildKeys
start = src.index(old_bk)
# Find the closing brace of buildKeys (the line "  }" after it)
# We search for the function end: "  }\n\n  function inTrap"
end_marker = '\n\n  function inTrap'
end_pos = src.index(end_marker, start)
close_brace_pos = end_pos  # will insert replacement up to here

old_full_bk = src[start:close_brace_pos + 4]  # include "  }"

new_bk = '''  function buildKeys() {
    keys = [];
    const whites = COLS.filter(c => c.white);
    const nW = whites.length;

    // Front-facing low-angle perspective: camera at key level
    const surTop  = H * 0.30;   // back edge of key surface (meets fallboard)
    const surBot  = H * 0.73;   // front edge of surface / top of key front face
    const faceBot = H * 0.88;   // bottom of key front face
    const bkTop   = H * 0.06;   // top of black keys
    const bkBot   = H * 0.67;   // bottom of black keys

    // Width: back edge narrower (perspective convergence)
    const frontW = W,        frontX0 = 0;
    const backW  = W * 0.82, backX0  = W * 0.09;
    const wFW = frontW / nW;
    const wBW = backW  / nW;
    const g   = 2.2;

    whites.forEach((col, i) => {
      const idx = COLS.indexOf(col);
      keys.push({
        idx, white: true,
        tl:     { x: backX0  + i       * wBW + g, y: surTop  },
        tr:     { x: backX0  + (i + 1) * wBW - g, y: surTop  },
        bl:     { x: frontX0 + i       * wFW + g, y: faceBot },
        br:     { x: frontX0 + (i + 1) * wFW - g, y: faceBot },
        surBot, faceBot,
      });
    });

    // Black keys sit between white keys, sticking up above playing surface
    let wIdx = 0;
    COLS.forEach(col => {
      if (col.white) { wIdx++; return; }
      const idx  = COLS.indexOf(col);
      const pos  = wIdx - 0.5;
      const bkWF = wFW * 0.55, bkWB = wBW * 0.55;
      const bkLF = frontX0 + pos * wFW + (wFW - bkWF) / 2;
      const bkLB = backX0  + pos * wBW + (wBW - bkWB) / 2;
      keys.push({
        idx, white: false,
        tl: { x: bkLB + g,        y: bkTop },
        tr: { x: bkLB + bkWB - g, y: bkTop },
        bl: { x: bkLF + g,        y: bkBot },
        br: { x: bkLF + bkWF - g, y: bkBot },
      });
    });
  }'''

src = src[:start] + new_bk + src[close_brace_pos + 4:]
print("1. buildKeys replaced OK")

# ── 2. drawFallboard — update fbH + add dark piano body below keys ────────────
old_fbh = '    const fbH = H * 0.24;'
new_fbh = (
    '    const fbH    = H * 0.30;\n'
    '    // Dark piano body below keys (faceBot=88% to bottom)\n'
    '    const bodyTop = H * 0.88;\n'
    '    const bodG = ctx.createLinearGradient(0, bodyTop, 0, H);\n'
    "    bodG.addColorStop(0,   '#0e0d0c');\n"
    "    bodG.addColorStop(0.4, '#080706');\n"
    "    bodG.addColorStop(1,   '#050403');\n"
    '    ctx.fillStyle = bodG; ctx.fillRect(0, bodyTop, W, H - bodyTop);'
)

assert old_fbh in src, 'fbH not found'
src = src.replace(old_fbh, new_fbh, 1)
print("2. drawFallboard updated OK")

# ── 3. drawBlackKeyShadow — limit shadow length ────────────────────────────────
old_sh = '    const spread = 9, shadowLen = (k.bl.y - k.tl.y) + 28;'
new_sh = '    const spread = 8, shadowLen = Math.min((k.bl.y - k.tl.y) * 0.28 + 16, H * 0.16);'

assert old_sh in src, 'shadow not found'
src = src.replace(old_sh, new_sh, 1)
print("3. drawBlackKeyShadow updated OK")

# ── 4. drawWhiteKey — full replacement ────────────────────────────────────────
wk_start_marker = '  function drawWhiteKey(k, pd, col, active) {\n'
wk_end_marker   = '\n\n  function drawBlackKey'

wk_start = src.index(wk_start_marker)
wk_end   = src.index(wk_end_marker, wk_start)

# The function ends with "  }" right before "\n\n  function drawBlackKey"
# Find last "  }" before wk_end_marker
close = src.rfind('  }', wk_start, wk_end)
old_wk_full = src[wk_start:close + 3]

new_wk = '''  function drawWhiteKey(k, pd, col, active) {
    const dy      = pd * 7;
    const surBot  = k.surBot;
    const faceBot = k.faceBot;
    ctx.save();
    if (active) { ctx.shadowBlur = 32; ctx.shadowColor = col.color + 'aa'; }

    // ── Top playing surface (trapezoid) ──────────────────────────────────────
    ctx.beginPath();
    ctx.moveTo(k.tl.x, k.tl.y + dy * 0.4); ctx.lineTo(k.tr.x, k.tr.y + dy * 0.4);
    ctx.lineTo(k.br.x, surBot + dy);         ctx.lineTo(k.bl.x, surBot + dy);
    ctx.closePath();

    if (active) {
      const gr = ctx.createLinearGradient(0, k.tl.y, 0, surBot);
      gr.addColorStop(0,    '#0e0c0a');
      gr.addColorStop(0.22, col.color + 'ee');
      gr.addColorStop(0.68, col.color + 'bb');
      gr.addColorStop(1,    '#1a1613');
      ctx.fillStyle = gr;
    } else {
      const gr = ctx.createLinearGradient(0, k.tl.y, 0, surBot);
      gr.addColorStop(0,    col.color + '55');
      gr.addColorStop(0.10, col.color + '2a');
      gr.addColorStop(0.28, '#ddd8d0');
      gr.addColorStop(0.72, '#d2cdc5');
      gr.addColorStop(0.94, '#b8b4ac');
      gr.addColorStop(1,    '#8c8880');
      ctx.fillStyle = gr;
    }
    ctx.fill();
    ctx.shadowBlur = 0;

    // Specular left strip
    if (!active) {
      const sw = (k.br.x - k.bl.x) * 0.11;
      const sg = ctx.createLinearGradient(0, k.tl.y, 0, surBot);
      sg.addColorStop(0,    'rgba(255,255,255,0.24)');
      sg.addColorStop(0.20, 'rgba(255,255,255,0.10)');
      sg.addColorStop(1,    'rgba(255,255,255,0.01)');
      ctx.beginPath();
      ctx.moveTo(k.tl.x + 2,      k.tl.y + dy * 0.4 + 5);
      ctx.lineTo(k.tl.x + sw + 2, k.tl.y + dy * 0.4 + 5);
      ctx.lineTo(k.bl.x + sw + 2, surBot + dy);
      ctx.lineTo(k.bl.x + 2,      surBot + dy);
      ctx.closePath();
      ctx.fillStyle = sg; ctx.fill();
    }

    // Color lip at back edge — collection accent
    ctx.beginPath();
    ctx.moveTo(k.tl.x, k.tl.y + dy * 0.4);     ctx.lineTo(k.tr.x, k.tr.y + dy * 0.4);
    ctx.lineTo(k.tr.x, k.tr.y + dy * 0.4 + 8); ctx.lineTo(k.tl.x, k.tl.y + dy * 0.4 + 8);
    ctx.closePath();
    ctx.fillStyle = active ? '#1a1614' : (col.color + 'cc'); ctx.fill();

    // Right shadow edge
    ctx.beginPath();
    ctx.moveTo(k.tr.x, k.tr.y + dy * 0.4); ctx.lineTo(k.br.x, surBot + dy);
    ctx.strokeStyle = 'rgba(0,0,0,0.65)'; ctx.lineWidth = 2.5; ctx.stroke();

    // ── Front face (prominent rectangle) ─────────────────────────────────────
    ctx.beginPath();
    ctx.moveTo(k.bl.x, surBot  + dy); ctx.lineTo(k.br.x, surBot  + dy);
    ctx.lineTo(k.br.x, faceBot + dy); ctx.lineTo(k.bl.x, faceBot + dy);
    ctx.closePath();
    const gf = ctx.createLinearGradient(0, surBot, 0, faceBot);
    if (active) {
      gf.addColorStop(0,    '#1e1a16');
      gf.addColorStop(0.30, '#110e0b');
      gf.addColorStop(1,    '#050403');
    } else {
      gf.addColorStop(0,    '#d0cbc2');
      gf.addColorStop(0.28, '#b8b3ab');
      gf.addColorStop(0.74, '#787470');
      gf.addColorStop(1,    '#131110');
    }
    ctx.fillStyle = gf; ctx.fill();

    // BKS accent stripe at bottom of front face
    if (!active) {
      const sh = Math.min(8, (faceBot - surBot) * 0.07);
      ctx.beginPath();
      ctx.moveTo(k.bl.x, faceBot + dy - sh); ctx.lineTo(k.br.x, faceBot + dy - sh);
      ctx.lineTo(k.br.x, faceBot + dy);      ctx.lineTo(k.bl.x, faceBot + dy);
      ctx.closePath(); ctx.fillStyle = col.color + 'bb'; ctx.fill();
    }

    // Left-to-right sheen on front face
    if (!active) {
      const hg = ctx.createLinearGradient(k.bl.x, 0, k.br.x, 0);
      hg.addColorStop(0,    'rgba(255,255,255,0.17)');
      hg.addColorStop(0.20, 'rgba(255,255,255,0.07)');
      hg.addColorStop(0.65, 'rgba(255,255,255,0.01)');
      hg.addColorStop(1,    'rgba(0,0,0,0.09)');
      ctx.beginPath();
      ctx.moveTo(k.bl.x, surBot  + dy); ctx.lineTo(k.br.x, surBot  + dy);
      ctx.lineTo(k.br.x, faceBot + dy); ctx.lineTo(k.bl.x, faceBot + dy);
      ctx.closePath(); ctx.fillStyle = hg; ctx.fill();
    }

    // Key gap dividers
    ctx.beginPath(); ctx.moveTo(k.bl.x, surBot + dy); ctx.lineTo(k.bl.x, faceBot + dy);
    ctx.strokeStyle = 'rgba(0,0,0,0.48)'; ctx.lineWidth = 2; ctx.stroke();
    ctx.beginPath(); ctx.moveTo(k.br.x, surBot + dy); ctx.lineTo(k.br.x, faceBot + dy);
    ctx.strokeStyle = 'rgba(0,0,0,0.58)'; ctx.lineWidth = 2; ctx.stroke();

    // ── Labels in front face ─────────────────────────────────────────────────
    if (!active) {
      const cx    = (k.bl.x + k.br.x) / 2;
      const areaH = faceBot - surBot;
      const nameY = surBot + dy + areaH * 0.40;
      ctx.textAlign = 'center';
      ctx.font      = '400 16px "Bebas Neue", sans-serif';
      ctx.fillStyle = 'rgba(255,252,245,0.90)';
      ctx.fillText(col.name.toUpperCase(), cx, nameY);
      ctx.font      = '600 7px "DM Mono", monospace';
      ctx.fillStyle = 'rgba(255,252,245,0.52)';
      ctx.letterSpacing = '0.14em';
      ctx.fillText(col.note.toUpperCase(), cx, nameY + areaH * 0.23);
      ctx.letterSpacing = '0em';
    }
    ctx.restore();
  }'''

src = src[:wk_start] + new_wk + src[close + 3:]
print("4. drawWhiteKey replaced OK")

# ── 5. drawBlackKey label position ────────────────────────────────────────────
old_bkl = '      const cx = (k.bl.x + k.br.x) / 2, my = k.bl.y - 14;'
new_bkl = '      const cx = (k.bl.x + k.br.x) / 2, my = k.tl.y + (k.bl.y - k.tl.y) * 0.78;'

assert old_bkl in src, 'black key label not found'
src = src.replace(old_bkl, new_bkl, 1)
print("5. drawBlackKey label updated OK")

with open(path, 'w', encoding='utf-8') as f:
    f.write(src)

print("\nDone — file saved.")
