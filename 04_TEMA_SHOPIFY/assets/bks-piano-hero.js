/**
 * bks-piano-hero.js — BKS Studio Piano Hero Section
 * Version 2.0 — June 2026
 *
 * Dual rendering modes:
 *   cinema    — dark #0A0A0A background, glow on press, cinematic ambient
 *   editorial — newspaper/paper aesthetic, keys emerge from page on press
 *
 * Page colour adaptation: reads --bks-active-accent CSS variable (injected
 * per collection by bks-dynamic-ux.js) to tint accent elements automatically.
 */

(function () {
  'use strict';

  // ── Config ──────────────────────────────────────────────────────────────────
  const dataEl = document.getElementById('bks-piano-data');
  if (!dataEl) return;
  const DATA       = JSON.parse(dataEl.textContent);
  const COLS       = DATA.collections;
  const PAPER_MODE = DATA.style_mode === 'editorial';

  // ── DOM refs ─────────────────────────────────────────────────────────────────
  const cv         = document.getElementById('bks-piano-canvas');
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
  const pianoEl    = cv ? cv.closest('.bks-piano-hero') : null;

  // ── State ────────────────────────────────────────────────────────────────────
  let W, H, keys = [], activeKey = -1;
  const KS     = COLS.map(() => ({ anim: 0, pressed: false }));
  let ripples  = [];
  let pageAccent = '';

  function getPageAccent() {
    return getComputedStyle(document.documentElement)
      .getPropertyValue('--bks-active-accent').trim() || '';
  }

  // ── Audio ─────────────────────────────────────────────────────────────────────
  let ac = null, masterG = null, revG = null, fadeG = null, loopT = null;
  let currentAudio = null;
  let masterVolume = 0.75;

  function getAC() {
    if (!ac) {
      ac = new (window.AudioContext || window.webkitAudioContext)();
      masterG = ac.createGain();
      masterG.gain.value = masterVolume;
      // Warm reverb: feedback delay with lowpass
      const dly = ac.createDelay(3.0); dly.delayTime.value = 0.55;
      const fb  = ac.createGain();     fb.gain.value = 0.18;
      const lpf = ac.createBiquadFilter(); lpf.type = 'lowpass'; lpf.frequency.value = 900;
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
    if (volWrap)  volWrap.classList.remove('bks-visible');
  }

  function playRealAudio(col) {
    const idx = col.audio_index;
    const el  = document.getElementById('bks-audio-' + idx);
    if (!el || (!el.querySelector('source[src]') && !el.src)) return false;
    if (currentAudio && currentAudio !== el) {
      currentAudio.pause(); currentAudio.currentTime = 0;
    }
    el.volume = 0;
    el.play().then(() => {
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
    const a     = getAC();
    const freq  = midiFreq(rootMidi(col) + semi);
    const decay = (col.decay || 4) + 2;
    const t     = a.currentTime;

    // Per-note warmth filter
    const filt = a.createBiquadFilter();
    filt.type = 'lowpass'; filt.frequency.value = 1400; filt.Q.value = 0.5;
    filt.connect(revG); filt.connect(fadeG);

    // Primary — clean sine
    const o1 = a.createOscillator(), g1 = a.createGain();
    o1.type = 'sine'; o1.frequency.value = freq;
    o1.connect(g1); g1.connect(filt);
    g1.gain.setValueAtTime(0, t);
    g1.gain.linearRampToValueAtTime(0.16, t + 0.10);
    g1.gain.exponentialRampToValueAtTime(0.001, t + decay);
    o1.start(t); o1.stop(t + decay + 0.5);

    // Detuned companion — chorus warmth
    const o2 = a.createOscillator(), g2 = a.createGain();
    o2.type = 'sine'; o2.frequency.value = freq * 1.0038;
    o2.connect(g2); g2.connect(filt);
    g2.gain.setValueAtTime(0, t);
    g2.gain.linearRampToValueAtTime(0.07, t + 0.14);
    g2.gain.exponentialRampToValueAtTime(0.001, t + decay);
    o2.start(t); o2.stop(t + decay + 0.5);

    // Sub-octave breath — body without mud
    const o3 = a.createOscillator(), g3 = a.createGain();
    o3.type = 'sine'; o3.frequency.value = freq * 0.5;
    o3.connect(g3); g3.connect(filt);
    g3.gain.setValueAtTime(0, t);
    g3.gain.linearRampToValueAtTime(0.04, t + 0.18);
    g3.gain.exponentialRampToValueAtTime(0.001, t + decay * 0.7);
    o3.start(t); o3.stop(t + decay + 0.5);

    addRipple(col.color);
  }

  function startWebAudioLoop(col) {
    const a = getAC();
    fadeG = a.createGain();
    fadeG.gain.setValueAtTime(0, a.currentTime);
    fadeG.gain.linearRampToValueAtTime(1, a.currentTime + 1.2);
    fadeG.connect(masterG);
    const beatMs  = 60000 / (col.bpm || 36);
    let step      = 0;
    const pattern = col.pattern || [0, null, null, null, 7, null, null, null];
    function tick() {
      if (activeKey < 0 || COLS[activeKey] !== col) return;
      const s = pattern[step % pattern.length];
      if (s !== null) playWebAudioNote(col, s);
      step++;
      loopT = setTimeout(tick, beatMs);
    }
    playWebAudioNote(col, 0);
    setTimeout(tick, beatMs * 0.5);
  }

  function startAudio(col) {
    stopAudio();
    const usedReal = playRealAudio(col);
    if (!usedReal && DATA.use_webaudio_fallback) startWebAudioLoop(col);
    if (musicInd) {
      musicInd.classList.add('bks-on');
      musicInd.querySelectorAll('span').forEach(s => s.style.background = col.color + '99');
    }
    if (volWrap) volWrap.classList.add('bks-visible');
  }

  // ── Ripples ───────────────────────────────────────────────────────────────────
  function addRipple(color) {
    if (activeKey < 0) return;
    const k = keys.find(k => k.idx === activeKey);
    if (!k) return;
    ripples.push({ x: (k.bl.x + k.br.x) / 2, y: (k.tl.y + k.bl.y) / 2, r: 0, color, a: 0.28 });
  }

  // Cinema ripples — bloom ring
  function drawRipples() {
    ripples = ripples.filter(r => r.a > 0.008);
    ripples.forEach(r => {
      r.r += 1.8; r.a *= 0.93;
      ctx.save();
      ctx.beginPath(); ctx.arc(r.x, r.y, r.r, 0, Math.PI * 2);
      ctx.strokeStyle = r.color; ctx.globalAlpha = r.a; ctx.lineWidth = 1.2;
      ctx.stroke();
      if (r.r < 40) {
        const rg = ctx.createRadialGradient(r.x, r.y, 0, r.x, r.y, r.r * 0.5);
        rg.addColorStop(0, r.color + '30'); rg.addColorStop(1, r.color + '00');
        ctx.beginPath(); ctx.arc(r.x, r.y, r.r * 0.5, 0, Math.PI * 2);
        ctx.fillStyle = rg; ctx.globalAlpha = r.a * 0.7; ctx.fill();
      }
      ctx.restore();
    });
  }

  // Paper ripples — ink splash
  function drawRipplesPaper() {
    ripples = ripples.filter(r => r.a > 0.008);
    ripples.forEach(r => {
      r.r += 1.2; r.a *= 0.90;
      ctx.save();
      ctx.beginPath(); ctx.arc(r.x, r.y, r.r, 0, Math.PI * 2);
      ctx.strokeStyle = r.color; ctx.globalAlpha = r.a * 0.55;
      ctx.lineWidth = 0.8; ctx.stroke();
      ctx.restore();
    });
  }

  // ── Piano geometry ────────────────────────────────────────────────────────────
  function buildKeys() {
    keys = [];
    const whites = COLS.filter(c => c.white);
    const nW  = whites.length;
    const fY  = H, bY = H * 0.06;
    const fW  = W, bW = W * 0.46;
    const sF  = 0, sB = (W - bW) / 2;
    const wFW = fW / nW, wBW = bW / nW;
    const g   = 1.2;

    whites.forEach((c, i) => {
      const idx = COLS.indexOf(c);
      const fl  = sF + i * wFW, fr = fl + wFW;
      const bl  = sB + i * wBW, br = bl + wBW;
      keys.push({
        idx, white: true,
        tl: { x: bl + g, y: bY }, tr: { x: br - g, y: bY },
        br: { x: fr - g, y: fY }, bl: { x: fl + g, y: fY },
      });
    });

    let wIdx = 0;
    COLS.forEach((c) => {
      if (c.white) { wIdx++; return; }
      const idx = COLS.indexOf(c);
      const pos = wIdx - 0.32;
      const fl  = sF + pos * wFW, fr = fl + wFW * 0.52;
      const bl  = sB + pos * wBW, br = bl + wBW * 0.52;
      const bEndY = bY + (fY - bY) * 0.50;
      keys.push({
        idx, white: false,
        tl: { x: bl + g, y: bY }, tr: { x: br - g, y: bY },
        br: { x: fr - g, y: bEndY }, bl: { x: fl + g, y: bEndY },
      });
    });
  }

  function inTrap(px, py, k) {
    const minY = Math.min(k.tl.y, k.tr.y), maxY = Math.max(k.bl.y, k.br.y);
    if (py < minY || py > maxY) return false;
    const t = (py - minY) / (maxY - minY || 1);
    return px >= k.tl.x + (k.bl.x - k.tl.x) * t &&
           px <= k.tr.x + (k.br.x - k.tr.x) * t;
  }

  function getKeyAt(mx, my) {
    for (const k of keys.filter(k => !k.white)) if (inTrap(mx, my, k)) return k;
    for (const k of keys.filter(k =>  k.white)) if (inTrap(mx, my, k)) return k;
    return null;
  }

  // ════════════════════════════════════════════════════════════════════════
  // CINEMA MODE — dark luxury rendering
  // ════════════════════════════════════════════════════════════════════════

  function drawFallboard() {
    // Background — BakAbo brand dark
    ctx.fillStyle = '#0A0A0A';
    ctx.fillRect(0, 0, W, H);

    // Active key accent wash over full canvas
    if (activeKey >= 0) {
      const ac = COLS[activeKey];
      const wash = ctx.createRadialGradient(W / 2, H, 0, W / 2, H * 0.5, W * 0.7);
      wash.addColorStop(0,   ac.color + '14');
      wash.addColorStop(0.5, ac.color + '08');
      wash.addColorStop(1,   'rgba(0,0,0,0)');
      ctx.fillStyle = wash; ctx.fillRect(0, 0, W, H);
    }

    const fbH = H * 0.10;

    // Lacquered body
    const bg = ctx.createLinearGradient(0, 0, 0, fbH);
    bg.addColorStop(0,    '#111110');
    bg.addColorStop(0.42, '#1c1816');
    bg.addColorStop(0.80, '#0f0e0d');
    bg.addColorStop(1,    '#0A0A0A');
    ctx.fillStyle = bg; ctx.fillRect(0, 0, W, fbH);

    // Wood grain — faint
    ctx.save();
    for (let i = 0; i < 24; i++) {
      const y = (i / 24) * (fbH * 0.90) + fbH * 0.05;
      const amp = 1.2 + Math.sin(i * 1.1) * 0.9;
      ctx.beginPath(); ctx.moveTo(0, y);
      for (let x = 0; x <= W; x += 48)
        ctx.lineTo(x, y + Math.sin((x / W) * Math.PI * 3 + i * 0.38) * amp);
      ctx.strokeStyle = i % 4 === 0 ? 'rgba(190,140,55,0.026)' : 'rgba(190,140,55,0.013)';
      ctx.lineWidth = 0.7; ctx.stroke();
    }
    ctx.restore();

    // Sheen
    ctx.save();
    const sh = ctx.createLinearGradient(W * 0.08, 0, W * 0.92, 0);
    sh.addColorStop(0,    'rgba(255,240,200,0)');
    sh.addColorStop(0.30, 'rgba(255,240,200,0.028)');
    sh.addColorStop(0.50, 'rgba(255,240,200,0.09)');
    sh.addColorStop(0.70, 'rgba(255,240,200,0.028)');
    sh.addColorStop(1,    'rgba(255,240,200,0)');
    ctx.fillStyle = sh; ctx.fillRect(W * 0.08, fbH * 0.20, W * 0.84, fbH * 0.40);
    ctx.restore();

    // Gold trim
    ctx.save();
    const trim = ctx.createLinearGradient(0, 0, W, 0);
    trim.addColorStop(0,    'rgba(190,150,65,0)');
    trim.addColorStop(0.12, 'rgba(190,150,65,0.28)');
    trim.addColorStop(0.50, 'rgba(210,170,75,0.38)');
    trim.addColorStop(0.88, 'rgba(190,150,65,0.28)');
    trim.addColorStop(1,    'rgba(190,150,65,0)');
    ctx.fillStyle = trim; ctx.fillRect(0, fbH - 2.5, W, 2.5);
    ctx.restore();

    // Brand label
    ctx.save(); ctx.textAlign = 'center';
    ctx.font = '300 9px "DM Mono", monospace, system-ui';
    ctx.fillStyle = 'rgba(255,240,200,0.14)';
    ctx.fillText(DATA.fallboard_label || 'BAK | ABO', W / 2, fbH * 0.60);
    ctx.restore();

    // Shadow cascade from fallboard
    ctx.save();
    const csc = ctx.createLinearGradient(0, fbH, 0, fbH + H * 0.09);
    csc.addColorStop(0,    'rgba(0,0,0,0.60)');
    csc.addColorStop(0.45, 'rgba(0,0,0,0.20)');
    csc.addColorStop(1,    'rgba(0,0,0,0)');
    ctx.fillStyle = csc; ctx.fillRect(0, fbH, W, H * 0.09);
    ctx.restore();
  }

  function drawBlackKeyShadow(k) {
    const pd = KS[k.idx].anim, dy = pd * 13;
    const spread = 9, shadowLen = (k.bl.y - k.tl.y) + 28;
    ctx.save();
    ctx.beginPath();
    ctx.moveTo(k.tl.x - spread,       k.tl.y + dy * 0.2);
    ctx.lineTo(k.tr.x + spread,       k.tr.y + dy * 0.2);
    ctx.lineTo(k.br.x + spread * 1.8, k.tl.y + shadowLen);
    ctx.lineTo(k.bl.x - spread * 1.8, k.tl.y + shadowLen);
    ctx.closePath();
    const sg = ctx.createLinearGradient(0, k.tl.y, 0, k.tl.y + shadowLen);
    sg.addColorStop(0,    'rgba(0,0,0,0.46)');
    sg.addColorStop(0.50, 'rgba(0,0,0,0.18)');
    sg.addColorStop(1,    'rgba(0,0,0,0)');
    ctx.fillStyle = sg; ctx.fill(); ctx.restore();
  }

  function drawWhiteKey(k, pd, col, active) {
    const dy = pd * 20, faceH = 38;
    ctx.save();
    if (active) { ctx.shadowBlur = 28; ctx.shadowColor = col.color; }

    ctx.beginPath();
    ctx.moveTo(k.tl.x, k.tl.y + dy * 0.2); ctx.lineTo(k.tr.x, k.tr.y + dy * 0.2);
    ctx.lineTo(k.br.x, k.br.y + dy);        ctx.lineTo(k.bl.x, k.bl.y + dy);
    ctx.closePath();

    if (active) {
      const gr = ctx.createLinearGradient(0, k.tl.y, 0, k.bl.y);
      gr.addColorStop(0,    '#0e0c0a');
      gr.addColorStop(0.25, col.color + 'ee');
      gr.addColorStop(0.65, col.color + 'bb');
      gr.addColorStop(1,    '#0A0A0A');
      ctx.fillStyle = gr;
    } else {
      const gr = ctx.createLinearGradient(0, k.tl.y, 0, k.bl.y);
      gr.addColorStop(0,    '#a0998e'); gr.addColorStop(0.06, '#e8e2d4');
      gr.addColorStop(0.50, '#e0dace'); gr.addColorStop(0.88, '#c8c4bc');
      gr.addColorStop(1,    '#9a9690');
      ctx.fillStyle = gr;
    }
    ctx.fill();
    ctx.shadowBlur = 0;

    // Specular left strip
    if (!active) {
      const sw = (k.br.x - k.bl.x) * 0.12;
      const sg = ctx.createLinearGradient(0, k.tl.y, 0, k.bl.y);
      sg.addColorStop(0,    'rgba(255,255,255,0.22)');
      sg.addColorStop(0.18, 'rgba(255,255,255,0.10)');
      sg.addColorStop(1,    'rgba(255,255,255,0.01)');
      ctx.beginPath();
      ctx.moveTo(k.tl.x + 2, k.tl.y + dy * 0.2 + 8);
      ctx.lineTo(k.tl.x + 2 + sw, k.tr.y + dy * 0.2 + 8);
      ctx.lineTo(k.bl.x + sw + 2, k.bl.y + dy);
      ctx.lineTo(k.bl.x + 2, k.bl.y + dy);
      ctx.closePath();
      ctx.fillStyle = sg; ctx.fill();
    }

    // Lip
    ctx.beginPath();
    ctx.moveTo(k.tl.x, k.tl.y + dy * 0.2);      ctx.lineTo(k.tr.x, k.tr.y + dy * 0.2);
    ctx.lineTo(k.tr.x, k.tr.y + dy * 0.2 + 9);  ctx.lineTo(k.tl.x, k.tl.y + dy * 0.2 + 9);
    ctx.closePath();
    ctx.fillStyle = active ? '#1a1614' : '#706a62'; ctx.fill();

    // Front vertical face
    if (k.bl.y + dy < H + faceH + 10) {
      ctx.beginPath();
      ctx.moveTo(k.bl.x, k.bl.y + dy); ctx.lineTo(k.br.x, k.br.y + dy);
      ctx.lineTo(k.br.x, k.br.y + dy + faceH); ctx.lineTo(k.bl.x, k.bl.y + dy + faceH);
      ctx.closePath();
      const gf = ctx.createLinearGradient(0, k.bl.y + dy, 0, k.bl.y + dy + faceH);
      if (active) {
        gf.addColorStop(0, '#1e1a16'); gf.addColorStop(0.35, '#110e0b'); gf.addColorStop(1, '#050403');
      } else {
        gf.addColorStop(0, '#ccc7bf'); gf.addColorStop(0.28, '#b8b3ab');
        gf.addColorStop(0.72, '#8a8680'); gf.addColorStop(1, '#1a1814');
      }
      ctx.fillStyle = gf; ctx.fill();
      if (!active) {
        const hg = ctx.createLinearGradient(k.bl.x, 0, k.br.x, 0);
        hg.addColorStop(0, 'rgba(255,255,255,0.14)'); hg.addColorStop(0.22, 'rgba(255,255,255,0.07)');
        hg.addColorStop(0.60, 'rgba(255,255,255,0.01)'); hg.addColorStop(1, 'rgba(0,0,0,0.10)');
        ctx.beginPath();
        ctx.moveTo(k.bl.x, k.bl.y + dy); ctx.lineTo(k.br.x, k.br.y + dy);
        ctx.lineTo(k.br.x, k.br.y + dy + faceH); ctx.lineTo(k.bl.x, k.bl.y + dy + faceH);
        ctx.closePath(); ctx.fillStyle = hg; ctx.fill();
      }
    }

    // Right shadow
    ctx.beginPath();
    ctx.moveTo(k.tr.x, k.tr.y + dy * 0.2); ctx.lineTo(k.br.x, k.br.y + dy);
    ctx.strokeStyle = 'rgba(0,0,0,0.60)'; ctx.lineWidth = 2.5; ctx.stroke();

    // Labels
    if (!active) {
      const cx = (k.bl.x + k.br.x) / 2, my = (k.tl.y + k.bl.y) / 2 + 28;
      ctx.textAlign = 'center';
      ctx.font = '500 11px system-ui, sans-serif'; ctx.fillStyle = 'rgba(36,32,26,0.58)';
      ctx.fillText(col.name.toUpperCase(), cx, my);
      ctx.font = '400 9px system-ui, sans-serif'; ctx.fillStyle = 'rgba(36,32,26,0.32)';
      ctx.fillText(col.note, cx, my + 15);
    }
    ctx.restore();
  }

  function drawBlackKey(k, pd, col, active) {
    const dy = pd * 13;
    ctx.save();
    if (active) { ctx.shadowBlur = 22; ctx.shadowColor = col.color; }

    ctx.beginPath();
    ctx.moveTo(k.tl.x, k.tl.y + dy * 0.2); ctx.lineTo(k.tr.x, k.tr.y + dy * 0.2);
    ctx.lineTo(k.br.x, k.br.y + dy);        ctx.lineTo(k.bl.x, k.bl.y + dy);
    ctx.closePath();

    if (active) {
      const gr = ctx.createLinearGradient(0, k.tl.y, 0, k.bl.y);
      gr.addColorStop(0,    '#0e0c0a');
      gr.addColorStop(0.30, col.color + 'cc');
      gr.addColorStop(0.70, col.color + '88');
      gr.addColorStop(1,    '#040302');
      ctx.fillStyle = gr;
    } else {
      const gr = ctx.createLinearGradient(0, k.tl.y, 0, k.bl.y);
      gr.addColorStop(0,    '#2e2a26'); gr.addColorStop(0.15, '#1c1814');
      gr.addColorStop(0.75, '#0c0a08'); gr.addColorStop(1,    '#040302');
      ctx.fillStyle = gr;
    }
    ctx.fill();
    ctx.shadowBlur = 0;

    ctx.beginPath(); ctx.moveTo(k.tl.x, k.tl.y + dy * 0.2); ctx.lineTo(k.bl.x, k.bl.y + dy);
    ctx.strokeStyle = 'rgba(255,255,255,0.07)'; ctx.lineWidth = 1; ctx.stroke();
    ctx.beginPath(); ctx.moveTo(k.tr.x, k.tr.y + dy * 0.2); ctx.lineTo(k.br.x, k.br.y + dy);
    ctx.strokeStyle = 'rgba(0,0,0,0.55)'; ctx.lineWidth = 1.2; ctx.stroke();

    ctx.beginPath(); ctx.moveTo(k.tl.x, k.tl.y + dy * 0.2); ctx.lineTo(k.tr.x, k.tr.y + dy * 0.2);
    ctx.strokeStyle = active ? col.color + '55' : 'rgba(255,255,255,0.26)';
    ctx.lineWidth = 1.8; ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(k.bl.x, k.bl.y + dy); ctx.lineTo(k.br.x, k.br.y + dy);
    ctx.lineTo(k.br.x, k.br.y + dy + 12); ctx.lineTo(k.bl.x, k.bl.y + dy + 12);
    ctx.closePath(); ctx.fillStyle = '#030201'; ctx.fill();

    // Gloss strip
    const kW  = k.tr.x - k.tl.x, gw = kW * 0.30, gx0 = k.tl.x + kW * 0.12;
    const gg  = ctx.createLinearGradient(gx0, 0, gx0 + gw, 0);
    gg.addColorStop(0, 'rgba(255,255,255,0)'); gg.addColorStop(0.38, 'rgba(255,255,255,0.17)');
    gg.addColorStop(0.62, 'rgba(255,255,255,0.17)'); gg.addColorStop(1, 'rgba(255,255,255,0)');
    ctx.beginPath();
    ctx.moveTo(gx0, k.tl.y + dy * 0.2 + 2); ctx.lineTo(gx0 + gw, k.tr.y + dy * 0.2 + 2);
    ctx.lineTo(k.bl.x + gw * 0.72, k.bl.y + dy - 3); ctx.lineTo(k.bl.x, k.bl.y + dy - 3);
    ctx.closePath(); ctx.fillStyle = gg; ctx.fill();

    if (!active) {
      const cx = (k.bl.x + k.br.x) / 2, my = (k.tl.y + k.bl.y) / 2 + 7;
      ctx.textAlign = 'center';
      ctx.font = '500 8px system-ui, sans-serif'; ctx.fillStyle = 'rgba(255,255,255,0.30)';
      ctx.fillText(col.name.toUpperCase(), cx, my);
      ctx.font = '400 7px system-ui, sans-serif'; ctx.fillStyle = 'rgba(255,255,255,0.16)';
      ctx.fillText(col.note, cx, my + 11);
    }
    ctx.restore();
  }

  // ════════════════════════════════════════════════════════════════════════
  // EDITORIAL / NEWSPAPER MODE — keys emerge from page
  // ════════════════════════════════════════════════════════════════════════

  function drawPaperBackground() {
    // Paper base — aged editorial paper
    const bg = ctx.createLinearGradient(0, 0, W, H);
    bg.addColorStop(0,   '#f7f3ea');
    bg.addColorStop(0.5, '#fafaf7');
    bg.addColorStop(1,   '#f4f0e6');
    ctx.fillStyle = bg; ctx.fillRect(0, 0, W, H);

    // Newsprint texture — very faint horizontal lines
    ctx.save();
    for (let y = 0; y < H; y += 7) {
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y);
      ctx.strokeStyle = 'rgba(80,60,30,0.016)'; ctx.lineWidth = 0.5; ctx.stroke();
    }
    ctx.restore();

    // Masthead / newspaper header area
    const mastH = H * 0.09;
    ctx.save();

    // Top rule
    ctx.beginPath(); ctx.moveTo(W * 0.04, mastH * 0.28); ctx.lineTo(W * 0.96, mastH * 0.28);
    ctx.strokeStyle = 'rgba(20,14,6,0.22)'; ctx.lineWidth = 2; ctx.stroke();

    // Masthead text
    ctx.textAlign = 'center';
    ctx.font = '400 9px "DM Mono", monospace, system-ui';
    ctx.fillStyle = 'rgba(20,14,6,0.45)';
    ctx.fillText((DATA.fallboard_label || 'BAK | ABO').toUpperCase() + '  —  WEARABLE ART', W / 2, mastH * 0.60);

    // Bottom rule — accent color if active key
    const accent = pageAccent || (activeKey >= 0 ? COLS[activeKey].color : 'rgba(20,14,6,0.12)');
    ctx.beginPath(); ctx.moveTo(W * 0.04, mastH * 0.88); ctx.lineTo(W * 0.96, mastH * 0.88);
    ctx.strokeStyle = activeKey >= 0 ? accent : 'rgba(20,14,6,0.12)';
    ctx.lineWidth = activeKey >= 0 ? 1.5 : 0.5; ctx.stroke();

    ctx.restore();
  }

  function drawWhiteKeyPaper(k, pd, col, active) {
    const lift   = pd * 16;
    const accent = pageAccent || col.color;

    // Drop shadow (drawn before key body)
    if (lift > 0.05) {
      const sd = lift * 0.38 + 2;
      ctx.save();
      ctx.beginPath();
      ctx.moveTo(k.tl.x + sd,       k.tl.y + sd * 0.25);
      ctx.lineTo(k.tr.x + sd,       k.tr.y + sd * 0.25);
      ctx.lineTo(k.br.x + sd * 1.2, k.br.y - lift + sd);
      ctx.lineTo(k.bl.x + sd * 1.2, k.bl.y - lift + sd);
      ctx.closePath();
      const sg = ctx.createLinearGradient(0, k.tl.y, 0, k.bl.y);
      sg.addColorStop(0, 'rgba(0,0,0,0.14)'); sg.addColorStop(0.6, 'rgba(0,0,0,0.06)');
      sg.addColorStop(1, 'rgba(0,0,0,0.01)');
      ctx.fillStyle = sg; ctx.fill();
      ctx.restore();
    }

    const expand = lift * 0.4;
    ctx.save();
    ctx.beginPath();
    ctx.moveTo(k.tl.x - expand, k.tl.y);
    ctx.lineTo(k.tr.x + expand, k.tr.y);
    ctx.lineTo(k.br.x + expand, k.br.y - lift);
    ctx.lineTo(k.bl.x - expand, k.bl.y - lift);
    ctx.closePath();

    // Key surface
    if (active) {
      const gr = ctx.createLinearGradient(0, k.tl.y, 0, k.bl.y);
      gr.addColorStop(0,   '#ffffff');
      gr.addColorStop(0.4, '#fafaf7');
      gr.addColorStop(1,   '#f2ede0');
      ctx.fillStyle = gr;
    } else {
      const gr = ctx.createLinearGradient(0, k.tl.y, 0, k.bl.y);
      gr.addColorStop(0,   '#eee8d8');
      gr.addColorStop(0.15,'#f2ede2');
      gr.addColorStop(0.80,'#ede8da');
      gr.addColorStop(1,   '#e5e0d0');
      ctx.fillStyle = gr;
    }
    ctx.fill();

    // Accent wash on active
    if (active) {
      ctx.beginPath();
      ctx.moveTo(k.tl.x - expand, k.tl.y); ctx.lineTo(k.tr.x + expand, k.tr.y);
      ctx.lineTo(k.br.x + expand, k.br.y - lift); ctx.lineTo(k.bl.x - expand, k.bl.y - lift);
      ctx.closePath();
      const aw = ctx.createLinearGradient(0, k.tl.y, 0, k.bl.y);
      aw.addColorStop(0, accent + '28'); aw.addColorStop(0.5, accent + '18');
      aw.addColorStop(1, accent + '08');
      ctx.fillStyle = aw; ctx.fill();
    }

    // Ink border
    ctx.beginPath();
    ctx.moveTo(k.tl.x - expand, k.tl.y); ctx.lineTo(k.tr.x + expand, k.tr.y);
    ctx.lineTo(k.br.x + expand, k.br.y - lift); ctx.lineTo(k.bl.x - expand, k.bl.y - lift);
    ctx.closePath();
    ctx.strokeStyle = active ? accent + 'cc' : 'rgba(20,14,6,0.42)';
    ctx.lineWidth   = active ? 1.5 : 1.0; ctx.stroke();

    // Collection name — ink printed
    const cx = (k.bl.x + k.br.x) / 2;
    const my = (k.tl.y + k.bl.y) / 2 + (active ? 16 : 20);
    ctx.textAlign = 'center';
    if (active) {
      ctx.font = '600 11px "DM Mono", monospace, system-ui'; ctx.fillStyle = accent;
      ctx.fillText(col.name.toUpperCase(), cx, my);
    } else {
      ctx.font = '500 10px "DM Mono", monospace, system-ui'; ctx.fillStyle = 'rgba(20,14,6,0.52)';
      ctx.fillText(col.name.toUpperCase(), cx, my);
      ctx.font = '400 8px "DM Mono", monospace, system-ui'; ctx.fillStyle = 'rgba(20,14,6,0.28)';
      ctx.fillText(col.note, cx, my + 14);
    }
    ctx.restore();
  }

  function drawBlackKeyPaper(k, pd, col, active) {
    const lift   = pd * 12;
    const accent = pageAccent || col.color;

    // Drop shadow
    if (lift > 0.05) {
      const sd = lift * 0.35 + 1.5;
      ctx.save();
      ctx.beginPath();
      ctx.moveTo(k.tl.x + sd, k.tl.y + sd * 0.25);
      ctx.lineTo(k.tr.x + sd, k.tr.y + sd * 0.25);
      ctx.lineTo(k.br.x + sd, k.br.y - lift + sd);
      ctx.lineTo(k.bl.x + sd, k.bl.y - lift + sd);
      ctx.closePath();
      ctx.fillStyle = 'rgba(0,0,0,0.18)'; ctx.fill(); ctx.restore();
    }

    const expand = lift * 0.3;
    ctx.save();
    ctx.beginPath();
    ctx.moveTo(k.tl.x - expand, k.tl.y);
    ctx.lineTo(k.tr.x + expand, k.tr.y);
    ctx.lineTo(k.br.x + expand, k.br.y - lift);
    ctx.lineTo(k.bl.x - expand, k.bl.y - lift);
    ctx.closePath();

    if (active) {
      const gr = ctx.createLinearGradient(0, k.tl.y, 0, k.bl.y);
      gr.addColorStop(0, accent); gr.addColorStop(0.5, accent + 'dd'); gr.addColorStop(1, '#1a1410');
      ctx.fillStyle = gr;
    } else {
      const gr = ctx.createLinearGradient(0, k.tl.y, 0, k.bl.y);
      gr.addColorStop(0, '#2a2420'); gr.addColorStop(0.3, '#1a1410'); gr.addColorStop(1, '#0e0c0a');
      ctx.fillStyle = gr;
    }
    ctx.fill();

    ctx.beginPath();
    ctx.moveTo(k.tl.x - expand, k.tl.y); ctx.lineTo(k.tr.x + expand, k.tr.y);
    ctx.lineTo(k.br.x + expand, k.br.y - lift); ctx.lineTo(k.bl.x - expand, k.bl.y - lift);
    ctx.closePath();
    ctx.strokeStyle = active ? 'rgba(255,255,255,0.45)' : 'rgba(255,255,255,0.12)';
    ctx.lineWidth = 0.8; ctx.stroke();

    if (!active) {
      const cx = (k.bl.x + k.br.x) / 2, my = (k.tl.y + k.bl.y) / 2 + 5;
      ctx.textAlign = 'center';
      ctx.font = '500 7px "DM Mono", monospace, system-ui'; ctx.fillStyle = 'rgba(255,255,255,0.38)';
      ctx.fillText(col.name.toUpperCase(), cx, my);
    }
    ctx.restore();
  }

  // ── Draw — combined scene ─────────────────────────────────────────────────────
  function drawScene() {
    if (PAPER_MODE) {
      pageAccent = getPageAccent();
      drawPaperBackground();
      keys.filter(k =>  k.white).forEach(k => drawWhiteKeyPaper(k, KS[k.idx].anim, COLS[k.idx], activeKey === k.idx));
      keys.filter(k => !k.white).forEach(k => drawBlackKeyPaper(k, KS[k.idx].anim, COLS[k.idx], activeKey === k.idx));
      drawRipplesPaper();
    } else {
      drawFallboard();
      keys.filter(k =>  k.white).forEach(k => drawWhiteKey(k, KS[k.idx].anim, COLS[k.idx], activeKey === k.idx));
      keys.filter(k => !k.white).forEach(k => drawBlackKeyShadow(k));
      keys.filter(k => !k.white).forEach(k => drawBlackKey(k, KS[k.idx].anim, COLS[k.idx], activeKey === k.idx));
      drawRipples();
      const vg = ctx.createRadialGradient(W / 2, H * 0.5, H * 0.06, W / 2, H * 0.5, W * 0.65);
      vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(0,0,0,0.58)');
      ctx.fillStyle = vg; ctx.fillRect(0, 0, W, H);
    }
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

  // ── Collection UI ─────────────────────────────────────────────────────────────
  function openCollection(idx) {
    const col = COLS[idx];

    // Paper mode: add .bks-paper to container for CSS panel inversion
    if (PAPER_MODE && pianoEl) pianoEl.classList.add('bks-paper');

    // Expose collection identity as CSS variables for editorial typography
    if (pianoEl) {
      pianoEl.style.setProperty('--bks-coll-initial', '"' + col.name[0].toUpperCase() + '"');
      pianoEl.style.setProperty('--bks-coll-accent', col.color);
    }

    // Model panel background — Canva artwork or gradient fallback
    if (col.image_url) {
      modelBg.style.backgroundImage    = 'url(' + col.image_url + ')';
      modelBg.style.backgroundSize     = 'cover';
      modelBg.style.backgroundPosition = 'center';
      modelBg.style.background         = '';
    } else {
      modelBg.style.backgroundImage = 'none';
      modelBg.style.background      = col.gradient || 'rgba(0,0,0,0.8)';
    }

    mqBodyFill.style.background = col.color;
    if (legL) legL.style.background = col.color;
    if (legR) legR.style.background = col.color;
    armSeason.textContent = col.arm_season || '';
    armDesc.textContent   = col.arm_desc   || '';
    collName.textContent  = col.name;
    collName.style.color  = PAPER_MODE ? '' : col.color;
    collNote.textContent  = col.note + ' · ' + Math.round(col.freq) + ' Hz · Minimal ambient';
    collQuote.textContent = col.quote || '';
    collPills.innerHTML   = (col.products || '')
      .split(',').map(p => p.trim()).filter(Boolean)
      .map(p => `<span class="bks-prod-pill" role="listitem">${p}</span>`).join('');
    if (collCta) {
      collCta.href = col.url || '#';
      if (PAPER_MODE) collCta.style.color = col.color;
    }

    screen.classList.add('bks-show');
    hint.classList.add('bks-hidden');
    backBtn.classList.add('bks-visible');
  }

  function closeCollection() {
    if (pianoEl) {
      pianoEl.classList.remove('bks-paper');
      pianoEl.style.removeProperty('--bks-coll-initial');
      pianoEl.style.removeProperty('--bks-coll-accent');
    }
    screen.classList.remove('bks-show');
    if (activeKey >= 0) KS[activeKey].pressed = false;
    activeKey = -1;
    stopAudio();
    hint.classList.remove('bks-hidden');
    backBtn.classList.remove('bks-visible');
    if (collCta) collCta.style.color = '';
  }

  // ── Interaction ───────────────────────────────────────────────────────────────
  function handleClick(mx, my) {
    if (screen.classList.contains('bks-show')) return;
    const k = getKeyAt(mx, my);
    if (!k) return;
    if (activeKey >= 0) KS[activeKey].pressed = false;
    activeKey = k.idx; KS[k.idx].pressed = true;
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
      (e.clientY - r.top)  * (H / r.height)
    ) ? 'pointer' : 'default';
  });

  cv.addEventListener('keydown', e => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      if (activeKey >= 0 && !screen.classList.contains('bks-show')) openCollection(activeKey);
    }
    if (e.key === 'Escape') closeCollection();
    if (e.key === 'ArrowRight') {
      const next = (activeKey + 1) % COLS.length;
      if (activeKey >= 0) KS[activeKey].pressed = false;
      activeKey = next; KS[next].pressed = true;
    }
    if (e.key === 'ArrowLeft') {
      const prev = (activeKey - 1 + COLS.length) % COLS.length;
      if (activeKey >= 0) KS[activeKey].pressed = false;
      activeKey = prev; KS[prev].pressed = true;
    }
  });

  // ── Resize ────────────────────────────────────────────────────────────────────
  function resize() {
    const r = cv.parentElement.getBoundingClientRect();
    W = cv.width  = Math.round(r.width);
    H = cv.height = Math.round(r.height);
    buildKeys();
  }

  // ── Public API ────────────────────────────────────────────────────────────────
  window.BKSPiano = {
    closeCollection,
    setVolume: function (v) {
      masterVolume = v;
      if (masterG && ac) masterG.gain.setTargetAtTime(v, ac.currentTime, 0.1);
      if (currentAudio)  currentAudio.volume = v;
    },
  };

  // ── Init ──────────────────────────────────────────────────────────────────────
  resize();
  animate();
  window.addEventListener('resize', resize);

})();
