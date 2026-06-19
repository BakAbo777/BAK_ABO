/**
 * bks-piano-hero.js — BKS Studio Piano Hero Section
 * Version 1.0 — Giugno 2026
 *
 * Sistema completo:
 *  - Pianoforte prospettico canvas 2D
 *  - Audio: file MP3 reali (Suno) con fallback Web Audio API
 *  - Pannello collezione: manichino + armocromia + info
 *  - Accessibilità: keyboard nav, ARIA live region
 */

(function () {
  'use strict';

  // ── Config ──────────────────────────────────────────────────────────────
  const dataEl = document.getElementById('bks-piano-data');
  if (!dataEl) return;
  const DATA = JSON.parse(dataEl.textContent);
  const COLS = DATA.collections;

  // ── DOM refs ─────────────────────────────────────────────────────────────
  const cv        = document.getElementById('bks-piano-canvas');
  const ctx        = cv.getContext('2d');
  const screen     = document.getElementById('bks-coll-screen');
  const backBtn    = document.getElementById('bks-back-btn');
  const hint       = document.getElementById('bks-hint');
  const musicInd   = document.getElementById('bks-music-ind');
  const volWrap    = document.getElementById('bks-vol-wrap');
  const modelBg    = document.getElementById('bks-model-bg');
  const mqBodyFill = document.getElementById('bks-mq-body-fill');
  const legL       = document.getElementById('bks-leg-l');
  const legR       = document.getElementById('bks-leg-r');
  const armSeason  = document.getElementById('bks-arm-season');
  const armDesc    = document.getElementById('bks-arm-desc');
  const collName   = document.getElementById('bks-coll-name');
  const collNote   = document.getElementById('bks-coll-note');
  const collQuote  = document.getElementById('bks-coll-quote');
  const collPills  = document.getElementById('bks-coll-pills');
  const collCta    = document.getElementById('bks-coll-cta');

  // ── State ────────────────────────────────────────────────────────────────
  let W, H, keys = [], activeKey = -1;
  const KS = COLS.map(() => ({ anim: 0, pressed: false }));
  let ripples = [];

  // ── Audio ─────────────────────────────────────────────────────────────────
  let ac = null, masterG = null, revG = null, fadeG = null, loopT = null;
  let currentAudio = null;
  let masterVolume = 0.75;

  function getAC() {
    if (!ac) {
      ac = new (window.AudioContext || window.webkitAudioContext)();
      masterG = ac.createGain();
      masterG.gain.value = masterVolume;
      // Reverb via feedback delay
      const dly = ac.createDelay(3.0); dly.delayTime.value = 0.44;
      const fb = ac.createGain(); fb.gain.value = 0.36;
      const lpf = ac.createBiquadFilter(); lpf.type = 'lowpass'; lpf.frequency.value = 1500;
      dly.connect(lpf); lpf.connect(fb); fb.connect(dly); dly.connect(masterG);
      revG = dly;
      masterG.connect(ac.destination);
    }
    return ac;
  }

  function midiFreq(midi) { return 440 * Math.pow(2, (midi - 69) / 12); }
  function rootMidi(col) {
    const map = { 'Do': 60, 'Re♭': 61, 'Re': 62, 'Mi♭': 63, 'Mi': 64, 'Fa': 65, 'Sol♭': 66, 'Sol': 67 };
    return map[col.note] || 60;
  }

  function stopAudio() {
    if (loopT) { clearTimeout(loopT); loopT = null; }
    if (fadeG && ac) { fadeG.gain.setTargetAtTime(0, ac.currentTime, 0.6); }
    if (currentAudio) {
      currentAudio.pause();
      currentAudio.currentTime = 0;
      currentAudio = null;
    }
    if (musicInd) musicInd.classList.remove('bks-on');
    if (volWrap) volWrap.classList.remove('bks-visible');
  }

  function playRealAudio(col) {
    const idx = col.audio_index;
    const el = document.getElementById('bks-audio-' + idx);
    if (!el || (!el.querySelector('source[src]') && !el.src)) return false;
    // Fade out previous
    if (currentAudio && currentAudio !== el) {
      currentAudio.pause();
      currentAudio.currentTime = 0;
    }
    el.volume = 0;
    el.play().then(() => {
      // Fade in
      let v = 0;
      const fade = setInterval(() => {
        v = Math.min(v + 0.04, masterVolume);
        el.volume = v;
        if (v >= masterVolume) clearInterval(fade);
      }, 60);
    }).catch(() => {});
    currentAudio = el;
    return true;
  }

  function playWebAudioNote(col, semi) {
    if (semi === null) return;
    const a = getAC();
    const o = a.createOscillator(), g = a.createGain();
    o.connect(g); g.connect(revG); g.connect(fadeG);
    o.type = 'sine';
    o.frequency.value = midiFreq(rootMidi(col) + semi);
    const t = a.currentTime, decay = col.decay || 4;
    g.gain.setValueAtTime(0, t);
    g.gain.linearRampToValueAtTime(0.18, t + 0.018);
    g.gain.exponentialRampToValueAtTime(0.001, t + decay);
    o.start(t); o.stop(t + decay + 0.3);
    addRipple(col.color);
  }

  function startWebAudioLoop(col) {
    const a = getAC();
    fadeG = a.createGain();
    fadeG.gain.setValueAtTime(0, a.currentTime);
    fadeG.gain.linearRampToValueAtTime(1, a.currentTime + 1.2);
    fadeG.connect(masterG);
    const beatMs = 60000 / (col.bpm || 36);
    let step = 0;
    const pattern = col.pattern || [0, null, null, null, 7, null, null, null];
    function tick() {
      if (activeKey < 0 || COLS[activeKey] !== col) return;
      const s = pattern[step % pattern.length];
      if (s !== null) playWebAudioNote(col, s);
      step++;
      loopT = setTimeout(tick, beatMs);
    }
    // Strike root
    playWebAudioNote(col, 0);
    setTimeout(tick, (60000 / (col.bpm || 36)) * 0.5);
  }

  function startAudio(col) {
    stopAudio();
    const usedReal = playRealAudio(col);
    if (!usedReal && DATA.use_webaudio_fallback) {
      startWebAudioLoop(col);
    }
    if (musicInd) {
      musicInd.classList.add('bks-on');
      musicInd.querySelectorAll('span').forEach(s => s.style.background = col.color + '99');
    }
    if (volWrap) volWrap.classList.add('bks-visible');
  }

  // ── Ripples ───────────────────────────────────────────────────────────────
  function addRipple(color) {
    if (activeKey < 0) return;
    const k = keys.find(k => k.idx === activeKey);
    if (!k) return;
    ripples.push({
      x: (k.bl.x + k.br.x) / 2,
      y: (k.tl.y + k.bl.y) / 2,
      r: 0, color, a: 0.28
    });
  }

  function drawRipples() {
    ripples = ripples.filter(r => r.a > 0.01);
    ripples.forEach(r => {
      r.r += 1.3; r.a *= 0.95;
      ctx.save();
      ctx.beginPath(); ctx.arc(r.x, r.y, r.r, 0, Math.PI * 2);
      ctx.strokeStyle = r.color; ctx.globalAlpha = r.a; ctx.lineWidth = 1;
      ctx.stroke(); ctx.restore();
    });
  }

  // ── Piano geometry ─────────────────────────────────────────────────────
  function buildKeys() {
    keys = [];
    const whites = COLS.filter(c => c.white);
    const nW = whites.length;
    const fY = H, bY = H * 0.06;
    const fW = W, bW = W * 0.46;
    const sF = 0, sB = (W - bW) / 2;
    const wFW = fW / nW, wBW = bW / nW;
    const g = 1.2;

    whites.forEach((c, i) => {
      const idx = COLS.indexOf(c);
      const fl = sF + i * wFW, fr = fl + wFW;
      const bl = sB + i * wBW, br = bl + wBW;
      keys.push({
        idx, white: true,
        tl: { x: bl + g, y: bY }, tr: { x: br - g, y: bY },
        br: { x: fr - g, y: fY }, bl: { x: fl + g, y: fY }
      });
    });

    // Black keys — music-correct positions
    const blackDefs = [];
    let wIdx = 0;
    COLS.forEach((c, i) => {
      if (c.white) { wIdx++; return; }
      // Position between previous white and next white
      blackDefs.push({ col: c, pos: (wIdx - 0.32) });
    });

    const bEndY = bY + (fY - bY) * 0.50;
    blackDefs.forEach(({ col, pos }) => {
      const idx = COLS.indexOf(col);
      const fl = sF + pos * wFW, fr = fl + wFW * 0.52;
      const bl = sB + pos * wBW, br = bl + wBW * 0.52;
      keys.push({
        idx, white: false,
        tl: { x: bl + g, y: bY }, tr: { x: br - g, y: bY },
        br: { x: fr - g, y: bEndY }, bl: { x: fl + g, y: bEndY }
      });
    });
  }

  function inTrap(px, py, k) {
    const minY = Math.min(k.tl.y, k.tr.y), maxY = Math.max(k.bl.y, k.br.y);
    if (py < minY || py > maxY) return false;
    const t = (py - minY) / (maxY - minY || 1);
    return px >= k.tl.x + (k.bl.x - k.tl.x) * t && px <= k.tr.x + (k.br.x - k.tr.x) * t;
  }

  function getKeyAt(mx, my) {
    for (const k of keys.filter(k => !k.white)) if (inTrap(mx, my, k)) return k;
    for (const k of keys.filter(k =>  k.white)) if (inTrap(mx, my, k)) return k;
    return null;
  }

  // ── Draw ──────────────────────────────────────────────────────────────────
  function drawWhiteKey(k, pd, col, active) {
    const dy = pd * 20;
    ctx.save();
    ctx.beginPath();
    ctx.moveTo(k.tl.x, k.tl.y + dy * 0.2); ctx.lineTo(k.tr.x, k.tr.y + dy * 0.2);
    ctx.lineTo(k.br.x, k.br.y + dy);        ctx.lineTo(k.bl.x, k.bl.y + dy);
    ctx.closePath();

    if (active) {
      const gr = ctx.createLinearGradient(0, k.tl.y, 0, k.bl.y);
      gr.addColorStop(0, '#111');
      gr.addColorStop(0.3, col.color + 'cc');
      gr.addColorStop(0.7, col.color + 'aa');
      gr.addColorStop(1, '#060402');
      ctx.fillStyle = gr;
    } else {
      const gr = ctx.createLinearGradient(0, k.tl.y, 0, k.bl.y);
      gr.addColorStop(0, '#b5b0a6'); gr.addColorStop(0.08, '#e5dfd1');
      gr.addColorStop(0.55, '#dddace'); gr.addColorStop(0.9, '#c0bcb4'); gr.addColorStop(1, '#969290');
      ctx.fillStyle = gr;
    }
    ctx.fill();

    // Lip
    ctx.beginPath();
    ctx.moveTo(k.tl.x, k.tl.y + dy * 0.2); ctx.lineTo(k.tr.x, k.tr.y + dy * 0.2);
    ctx.lineTo(k.tr.x, k.tr.y + dy * 0.2 + 8); ctx.lineTo(k.tl.x, k.tl.y + dy * 0.2 + 8);
    ctx.closePath();
    ctx.fillStyle = active ? '#181614' : '#787470'; ctx.fill();

    // Bottom thickness
    if (k.bl.y + dy < H + 30) {
      ctx.beginPath();
      ctx.moveTo(k.bl.x, k.bl.y + dy); ctx.lineTo(k.br.x, k.br.y + dy);
      ctx.lineTo(k.br.x, k.br.y + dy + 22); ctx.lineTo(k.bl.x, k.bl.y + dy + 22);
      ctx.closePath();
      const gf = ctx.createLinearGradient(0, k.bl.y + dy, 0, k.bl.y + dy + 22);
      gf.addColorStop(0, active ? '#141210' : '#aca8a0'); gf.addColorStop(1, 'rgba(0,0,0,0.9)');
      ctx.fillStyle = gf; ctx.fill();
    }

    // Specular
    const sw = (k.br.x - k.bl.x) * 0.10;
    ctx.beginPath();
    ctx.moveTo(k.tl.x + 3, k.tl.y + dy * 0.2 + 8); ctx.lineTo(k.tl.x + 3 + sw, k.tr.y + dy * 0.2 + 8);
    ctx.lineTo(k.bl.x + sw + 3, k.bl.y + dy); ctx.lineTo(k.bl.x + 3, k.bl.y + dy);
    ctx.closePath();
    const sg = ctx.createLinearGradient(0, k.tl.y, 0, k.bl.y);
    sg.addColorStop(0, 'rgba(255,255,255,0.18)'); sg.addColorStop(1, 'rgba(255,255,255,0.02)');
    ctx.fillStyle = sg; ctx.fill();

    // Right shadow
    ctx.beginPath(); ctx.moveTo(k.tr.x, k.tr.y + dy * 0.2); ctx.lineTo(k.br.x, k.br.y + dy);
    ctx.strokeStyle = 'rgba(0,0,0,0.52)'; ctx.lineWidth = 2; ctx.stroke();

    // Text
    if (!active) {
      const cx = (k.bl.x + k.br.x) / 2;
      const my = (k.tl.y + k.bl.y) / 2 + 28;
      ctx.textAlign = 'center';
      ctx.font = '500 11px system-ui, sans-serif';
      ctx.fillStyle = 'rgba(36,32,26,0.60)';
      ctx.fillText(col.name.toUpperCase(), cx, my);
      ctx.font = '400 9px system-ui, sans-serif';
      ctx.fillStyle = 'rgba(36,32,26,0.35)';
      ctx.fillText(col.note, cx, my + 15);
    }
    ctx.restore();
  }

  function drawBlackKey(k, pd, col, active) {
    const dy = pd * 13;
    ctx.save();
    ctx.beginPath();
    ctx.moveTo(k.tl.x, k.tl.y + dy * 0.2); ctx.lineTo(k.tr.x, k.tr.y + dy * 0.2);
    ctx.lineTo(k.br.x, k.br.y + dy);        ctx.lineTo(k.bl.x, k.bl.y + dy);
    ctx.closePath();

    if (active) {
      const gr = ctx.createLinearGradient(0, k.tl.y, 0, k.bl.y);
      gr.addColorStop(0, '#0e0c0a'); gr.addColorStop(0.4, col.color + 'aa'); gr.addColorStop(1, '#040302');
      ctx.fillStyle = gr;
    } else {
      const gr = ctx.createLinearGradient(0, k.tl.y, 0, k.bl.y);
      gr.addColorStop(0, '#2c2824'); gr.addColorStop(0.2, '#1a1614');
      gr.addColorStop(0.8, '#0c0a08'); gr.addColorStop(1, '#040302');
      ctx.fillStyle = gr;
    }
    ctx.fill();

    // Top edge
    ctx.beginPath();
    ctx.moveTo(k.tl.x, k.tl.y + dy * 0.2); ctx.lineTo(k.tr.x, k.tr.y + dy * 0.2);
    ctx.strokeStyle = active ? col.color + '66' : 'rgba(255,255,255,0.22)';
    ctx.lineWidth = 1.8; ctx.stroke();

    // Bottom
    ctx.beginPath();
    ctx.moveTo(k.bl.x, k.bl.y + dy); ctx.lineTo(k.br.x, k.br.y + dy);
    ctx.lineTo(k.br.x, k.br.y + dy + 10); ctx.lineTo(k.bl.x, k.bl.y + dy + 10);
    ctx.closePath(); ctx.fillStyle = '#030201'; ctx.fill();

    // Gloss strip
    const gw = (k.tr.x - k.tl.x) * 0.28;
    const gg = ctx.createLinearGradient(k.tl.x, 0, k.tl.x + gw, 0);
    gg.addColorStop(0, 'rgba(255,255,255,0)');
    gg.addColorStop(0.5, 'rgba(255,255,255,0.10)');
    gg.addColorStop(1, 'rgba(255,255,255,0)');
    ctx.beginPath();
    ctx.moveTo(k.tl.x, k.tl.y + dy * 0.2 + 2); ctx.lineTo(k.tl.x + gw, k.tr.y + dy * 0.2 + 2);
    ctx.lineTo(k.bl.x + gw * 0.8, k.bl.y + dy - 2); ctx.lineTo(k.bl.x, k.bl.y + dy - 2);
    ctx.closePath(); ctx.fillStyle = gg; ctx.fill();

    if (!active) {
      const cx = (k.bl.x + k.br.x) / 2, my = (k.tl.y + k.bl.y) / 2 + 7;
      ctx.textAlign = 'center';
      ctx.font = '500 8px system-ui, sans-serif'; ctx.fillStyle = 'rgba(255,255,255,0.26)';
      ctx.fillText(col.name.toUpperCase(), cx, my);
      ctx.font = '400 7px system-ui, sans-serif'; ctx.fillStyle = 'rgba(255,255,255,0.15)';
      ctx.fillText(col.note, cx, my + 11);
    }
    ctx.restore();
  }

  function drawScene() {
    // Fallboard
    const wg = ctx.createLinearGradient(0, 0, 0, H * 0.08);
    wg.addColorStop(0, '#070502'); wg.addColorStop(0.5, '#110d06'); wg.addColorStop(1, '#070502');
    ctx.fillStyle = wg; ctx.fillRect(0, 0, W, H);

    // Brand label
    ctx.save(); ctx.textAlign = 'center';
    ctx.font = '400 9px system-ui, sans-serif';
    ctx.fillStyle = 'rgba(255,240,200,0.08)';
    ctx.fillText(DATA.fallboard_label || 'BAK | ABO', W / 2, H * 0.055);
    ctx.restore();

    // Keys
    keys.filter(k =>  k.white).forEach(k => drawWhiteKey(k, KS[k.idx].anim, COLS[k.idx], activeKey === k.idx));
    keys.filter(k => !k.white).forEach(k => drawBlackKey(k, KS[k.idx].anim, COLS[k.idx], activeKey === k.idx));

    drawRipples();

    // Vignette
    const vg = ctx.createRadialGradient(W / 2, H * 0.5, H * 0.06, W / 2, H * 0.5, W * 0.65);
    vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,0,0.58)');
    ctx.fillStyle = vg; ctx.fillRect(0, 0, W, H);
  }

  function animate() {
    COLS.forEach((_, i) => {
      const t = KS[i].pressed ? 1 : 0;
      KS[i].anim += (t - KS[i].anim) * 0.11;
    });
    ctx.clearRect(0, 0, W, H);
    drawScene();
    requestAnimationFrame(animate);
  }

  // ── Collection UI ─────────────────────────────────────────────────────────
  function openCollection(idx) {
    const col = COLS[idx];
    modelBg.style.background = col.gradient || 'rgba(0,0,0,0.8)';
    mqBodyFill.style.background = col.color;
    legL.style.background = col.color;
    legR.style.background = col.color;
    armSeason.textContent = col.arm_season || '';
    armDesc.textContent = col.arm_desc || '';
    collName.textContent = col.name;
    collName.style.color = col.color;
    collNote.textContent = col.note + ' · ' + Math.round(col.freq) + ' Hz · Minimal ambient';
    collQuote.textContent = col.quote || '';
    collPills.innerHTML = (col.products || '')
      .split(',').map(p => p.trim()).filter(Boolean)
      .map(p => `<span class="bks-prod-pill">${p}</span>`).join('');
    collCta.href = col.url || '#';

    screen.classList.add('bks-show');
    hint.classList.add('bks-hidden');
    backBtn.classList.add('bks-visible');
  }

  function closeCollection() {
    screen.classList.remove('bks-show');
    if (activeKey >= 0) KS[activeKey].pressed = false;
    activeKey = -1;
    stopAudio();
    hint.classList.remove('bks-hidden');
    backBtn.classList.remove('bks-visible');
  }

  // ── Interaction ───────────────────────────────────────────────────────────
  function handleClick(mx, my) {
    if (screen.classList.contains('bks-show')) return;
    const k = getKeyAt(mx, my);
    if (!k) return;
    if (activeKey >= 0) KS[activeKey].pressed = false;
    activeKey = k.idx;
    KS[k.idx].pressed = true;
    startAudio(COLS[k.idx]);
    setTimeout(() => openCollection(k.idx), 380);
  }

  cv.addEventListener('click', e => {
    const r = cv.getBoundingClientRect();
    handleClick((e.clientX - r.left) * (W / r.width), (e.clientY - r.top) * (H / r.height));
  });

  cv.addEventListener('touchstart', e => {
    e.preventDefault();
    const r = cv.getBoundingClientRect(), t = e.touches[0];
    handleClick((t.clientX - r.left) * (W / r.width), (t.clientY - r.top) * (H / r.height));
  }, { passive: false });

  cv.addEventListener('mousemove', e => {
    if (screen.classList.contains('bks-show')) return;
    const r = cv.getBoundingClientRect();
    cv.style.cursor = getKeyAt(
      (e.clientX - r.left) * (W / r.width),
      (e.clientY - r.top) * (H / r.height)
    ) ? 'pointer' : 'default';
  });

  // Keyboard navigation
  cv.setAttribute('tabindex', '0');
  cv.addEventListener('keydown', e => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      if (activeKey >= 0 && !screen.classList.contains('bks-show')) {
        openCollection(activeKey);
      }
    }
    if (e.key === 'Escape') closeCollection();
    if (e.key === 'ArrowRight') {
      const next = (activeKey + 1) % COLS.length;
      if (activeKey >= 0) KS[activeKey].pressed = false;
      activeKey = next;
      KS[next].pressed = true;
    }
    if (e.key === 'ArrowLeft') {
      const prev = (activeKey - 1 + COLS.length) % COLS.length;
      if (activeKey >= 0) KS[activeKey].pressed = false;
      activeKey = prev;
      KS[prev].pressed = true;
    }
  });

  // ── Resize ────────────────────────────────────────────────────────────────
  function resize() {
    const r = cv.parentElement.getBoundingClientRect();
    W = cv.width  = Math.round(r.width);
    H = cv.height = Math.round(r.height);
    buildKeys();
  }

  // ── Public API ────────────────────────────────────────────────────────────
  window.BKSPiano = {
    closeCollection,
    setVolume: function (v) {
      masterVolume = v;
      if (masterG) masterG.gain.setTargetAtTime(v, ac.currentTime, 0.1);
      if (currentAudio) currentAudio.volume = v;
    }
  };

  // ── Init ──────────────────────────────────────────────────────────────────
  resize();
  animate();
  window.addEventListener('resize', resize);

})();
