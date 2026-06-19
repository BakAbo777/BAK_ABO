/* BKS Catalog Engine v2 */
'use strict';

const $ = id => document.getElementById(id);
const q = (sel, ctx = document) => ctx.querySelector(sel);
const qq = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];

// ── Color presets ──────────────────────────────────────────────────
const PRESETS = [
  { c1: '#ffffff', c2: '#e8e8e8' },
  { c1: '#0A0A0A', c2: '#2C2C2C' },
  { c1: '#EFEAE0', c2: '#FAFAF7' },
  { c1: '#C9B79C', c2: '#F5F2EC' },
  { c1: '#1A6840', c2: '#0A0A0A' },
  { c1: '#9B2A1A', c2: '#FAFAF7' },
  { c1: '#2D3A8C', c2: '#E8E8F5' },
  { c1: '#4A3728', c2: '#D6C8BB' },
  { c1: '#F5C842', c2: '#0A0A0A' },
  { c1: '#E8E0F5', c2: '#6A4A9A' },
];

// ── State ──────────────────────────────────────────────────────────
const state = { bgMode: 'bone', c1: '#ffffff', c2: '#e8e8e8' };
let pollTimer = null;

// ── Product card builder ───────────────────────────────────────────
function buildProductCard(p, c1, c2, showBg) {
  const el = document.createElement('div');
  el.className = 'product-card';

  if (showBg) {
    const mode = state.bgMode;
    if (mode === 'bone') el.style.background = '#EFEAE0';
    else if (mode === 'salt') el.style.background = '#FAFAF7';
    else if (mode === 'gradient') el.style.background = `linear-gradient(135deg, ${c1} 0%, ${c2} 100%)`;
    else el.style.background = c1 || '#EFEAE0';
  }

  const col = (p.collection || 'glyph').toLowerCase().trim();
  const colColors = {
    hours:    ['#0A0A0A', '#FAFAF7'],
    glyph:    ['#C9B79C', '#2C2C2C'],
    marker:   ['#1A6840', '#FAFAF7'],
    riviera:  ['#2D3A8C', '#FAFAF7'],
    pulse:    ['#9B2A1A', '#FAFAF7'],
    token:    ['#4A3728', '#EFEAE0'],
    flag:     ['#0A0A0A', '#F5C842'],
    folklore: ['#E8E0F5', '#4A3728'],
  };
  const [bg, fg] = colColors[col] || ['#6A6A6A', '#FAFAF7'];

  const safe = document.createElement('div');
  safe.className = 'pcard-safe';
  el.appendChild(safe);

  if (p.image) {
    const img = document.createElement('img');
    img.className = 'pcard-img';
    img.src = p.image;
    img.alt = p.title || '';
    img.loading = 'lazy';
    img.onerror = () => { img.style.display = 'none'; };
    el.appendChild(img);
  } else {
    const ph = document.createElement('div');
    ph.className = 'pcard-placeholder';
    ph.style.background = bg;
    ph.style.color = fg;
    ph.textContent = (p.title || col).toUpperCase().slice(0, 12);
    el.appendChild(ph);
  }

  if (p.visible !== undefined) {
    const badge = document.createElement('div');
    badge.className = `pcard-badge ${p.visible ? 'live' : 'draft'}`;
    badge.textContent = p.visible ? 'LIVE' : 'DRAFT';
    el.appendChild(badge);
  }

  const dot = document.createElement('div');
  dot.className = 'pcard-dot';
  dot.style.background = bg;
  el.appendChild(dot);

  const lbl = document.createElement('div');
  lbl.className = 'pcard-label';
  lbl.textContent = (p.title || '').toUpperCase().slice(0, 22);
  el.appendChild(lbl);

  return el;
}

// ── KV list renderer ───────────────────────────────────────────────
function renderKV(targetId, data) {
  const el = $(targetId);
  if (!el) return;
  const entries = Object.entries(data || {});
  if (!entries.length) {
    el.innerHTML = '<div class="kv-row"><span>Nessun dato</span></div>';
    return;
  }
  const max = Math.max(...entries.map(([, v]) => Number(v) || 0)) || 1;
  el.innerHTML = entries.map(([k, v]) => {
    const pct = Math.round((Number(v) / max) * 100);
    return `<div class="kv-row">
      <span>${k}</span>
      <div style="display:flex;align-items:center;gap:8px;flex-shrink:0;">
        <div style="width:${Math.max(pct * 0.5, 4)}px;height:5px;background:var(--onyx);border-radius:3px;opacity:.2;"></div>
        <b>${v}</b>
      </div>
    </div>`;
  }).join('');
}

// ── Tabs ───────────────────────────────────────────────────────────
function initTabs() {
  qq('.tab').forEach(btn => {
    btn.addEventListener('click', () => {
      qq('.tab').forEach(t => t.classList.remove('active'));
      qq('.tab-panel').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      const panel = $(btn.dataset.tab);
      if (panel) panel.classList.add('active');
      if (btn.dataset.tab === 'backgroundPanel') loadPreview();
      if (btn.dataset.tab === 'curationPanel') loadCuration();
      if (btn.dataset.tab === 'shippingPanel') loadShippingReport();
    });
  });
}

// ── Badge helpers ──────────────────────────────────────────────────
function setBadge(id, label, badgeState) {
  const el = $(id);
  if (!el) return;
  el.className = `badge ${badgeState}`;
  el.textContent = label;
}

// ── CSV files ──────────────────────────────────────────────────────
async function loadCsvFiles() {
  try {
    const res = await fetch('/api/csv_files');
    const d = await res.json();
    if (!d.ok || !d.files?.length) {
      setBadge('csvBadge', 'CSV non trovato', 'err');
      return;
    }

    const active = d.files.find(f => f.active);
    if (active) {
      $('csvName').textContent = active.name;
      $('csvMeta').textContent = `${active.size_mb} MB · ${active.modified}`;
      setBadge('csvBadge', `CSV ${active.size_mb} MB`, 'ok');
    } else {
      setBadge('csvBadge', 'CSV non attivo', 'err');
    }

    const picker = $('csvPicker');
    picker.innerHTML = '';
    d.files.slice(0, 6).forEach(f => {
      const row = document.createElement('div');
      row.className = `csv-option${f.active ? ' active' : ''}`;
      row.innerHTML = `<span class="csv-opt-name">${f.name}</span><span class="csv-opt-meta">${f.size_mb} MB</span>`;
      if (!f.active) {
        row.addEventListener('click', async () => {
          const r = await fetch('/api/set_csv', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ path: f.path }),
          });
          const rd = await r.json();
          if (rd.ok) { loadCsvFiles(); loadSummary(); }
        });
      }
      picker.appendChild(row);
    });
  } catch (e) {
    setBadge('csvBadge', 'Errore CSV', 'err');
  }
}

// ── Summary / Catalogo ─────────────────────────────────────────────
async function loadSummary() {
  try {
    const res = await fetch('/api/summary');
    const d = await res.json();
    if (!d.ok) { $('rowsStat').textContent = 'ERR'; return; }
    $('rowsStat').textContent    = d.rows ?? '-';
    $('handlesStat').textContent = d.handles ?? '-';
    $('imagesStat').textContent  = d.image_rows ?? '-';
    $('rembgStat').textContent   = d.rembg_available ? 'ON' : 'OFF';
    $('missingTitleStat').textContent = d.missing_seo_title ?? '-';
    $('missingDescStat').textContent  = d.missing_seo_description ?? '-';
    $('missingAltStat').textContent   = d.missing_alt ?? '-';
    renderKV('typesList', d.types || {});
    renderKV('vendorsList', d.vendors || {});
  } catch (e) {
    console.warn('summary error', e);
  }
}

// ── Curation ───────────────────────────────────────────────────────
async function loadCuration() {
  try {
    const res = await fetch('/api/curation/stats');
    const d = await res.json();
    if (!d.ok) return;

    $('curProductsStat').textContent = d.products ?? '-';
    $('curYesStat').textContent  = d.keep_counts?.Yes ?? 0;
    $('curNoStat').textContent   = d.keep_counts?.No ?? 0;
    $('curEmptyStat').textContent = d.keep_counts?.Empty ?? 0;

    const tgt = d.target || {};
    const yes  = d.keep_counts?.Yes ?? 0;
    const min  = tgt.min_total || 90;
    const max_ = tgt.max_total || 150;
    const pct  = Math.round((yes / max_) * 100);
    const fill = $('targetFill');
    fill.style.width = `${Math.min(pct, 100)}%`;
    fill.className = yes < min ? 'under' : yes > max_ ? 'over' : '';
    $('targetPct').textContent = `${yes} / ${min}–${max_} (${pct}%)`;
    $('targetSummary').textContent = `${min}–${max_} active totali · ${tgt.min_per_collection || 8}–${tgt.max_per_collection || 22} per collection`;

    renderKV('activeSeriesList', d.active_by_series || {});
    renderKV('activeTypeList',   d.active_by_type || {});
    renderKV('seriesList',       d.series_counts || {});
    renderKV('statusList',       d.status_counts || {});
  } catch (e) {
    console.warn('curation error', e);
  }
}

// ── Printify status ────────────────────────────────────────────────
async function loadPrintifyStatus() {
  const dot  = $('pDot');
  const text = $('pStatusText');
  const hint = $('pEnvHint');
  const err  = $('pError');

  dot.className = 'pconn-dot loading';
  text.textContent = 'Verifica connessione…';
  if (hint) hint.hidden = true;
  if (err) err.hidden = true;
  setBadge('printifyBadge', 'Printify…', 'loading');

  try {
    const res = await fetch('/api/printify/status');
    const d = await res.json();

    if (d.ok && d.status === 'connected') {
      dot.className = 'pconn-dot online';
      text.textContent = `Connesso · ${d.shop_title || d.shop_id} · ${d.shops} shop`;
      setBadge('printifyBadge', 'Printify OK', 'ok');
      qq('.tab[data-tab="printifyPanel"]').forEach(t => { t.textContent = 'Printify ✓'; });
      loadPrintifyPreview(d.shop_id);
    } else {
      dot.className = 'pconn-dot offline';
      const msg = d.error || 'Connessione fallita';
      text.textContent = msg;
      setBadge('printifyBadge', 'Printify ERR', 'err');
      if (!d.configured && hint) hint.hidden = false;
      if (err) { err.hidden = false; err.textContent = msg; }
    }
  } catch (e) {
    dot.className = 'pconn-dot offline';
    text.textContent = 'Errore di rete: ' + e.message;
    setBadge('printifyBadge', 'Printify ERR', 'err');
  }
}

// ── Printify preview ───────────────────────────────────────────────
async function loadPrintifyPreview(shopId) {
  const section = $('pPreviewSection');
  const grid    = $('printifyGrid');
  const shopTag = $('pShopTag');

  section.hidden = false;
  if (shopTag) shopTag.textContent = shopId ? `· Shop ${shopId}` : '';
  grid.innerHTML = Array(6).fill('<div class="product-card skeleton"></div>').join('');

  try {
    const res = await fetch('/api/printify/preview');
    const d = await res.json();
    grid.innerHTML = '';

    if (!d.ok || !d.products?.length) {
      grid.innerHTML = '<div class="log-box" style="grid-column:1/-1;">Nessun prodotto trovato su Printify.</div>';
      return;
    }
    d.products.forEach(p => grid.appendChild(buildProductCard(p, state.c1, state.c2, false)));
  } catch (e) {
    grid.innerHTML = `<div class="log-box" style="grid-column:1/-1;">Errore: ${e.message}</div>`;
  }
}

// ── Background preview ─────────────────────────────────────────────
async function loadPreview() {
  const grid = $('previewGrid');
  const c1 = $('color1')?.value || state.c1;
  const c2 = $('color2')?.value || state.c2;
  try {
    const res = await fetch('/api/preview');
    const d = await res.json();
    grid.innerHTML = '';
    if (!d.ok || !d.products?.length) {
      grid.innerHTML = '<div class="log-box" style="grid-column:1/-1;">Nessun prodotto nel CSV.</div>';
      return;
    }
    d.products.forEach(p => grid.appendChild(buildProductCard(p, c1, c2, true)));
  } catch (e) {
    grid.innerHTML = `<div class="log-box" style="grid-column:1/-1;">Errore: ${e.message}</div>`;
  }
}

// ── Mock image background ──────────────────────────────────────────
function updateMockBg() {
  const mock = $('mockImg');
  if (!mock) return;
  const c1 = $('color1')?.value || state.c1;
  const c2 = $('color2')?.value || state.c2;
  const map = {
    bone:      '#EFEAE0',
    salt:      '#FAFAF7',
    gradient:  `linear-gradient(135deg, ${c1} 0%, ${c2} 100%)`,
    hero:      `linear-gradient(180deg, ${c2} 0%, ${c1} 100%)`,
    editorial: `linear-gradient(90deg, ${c1} 0%, ${c2} 100%)`,
    custom:    c1,
  };
  mock.style.background = map[state.bgMode] || '#EFEAE0';
}

// ── Swatches ───────────────────────────────────────────────────────
function initSwatches() {
  const container = $('swatches');
  PRESETS.forEach((p, i) => {
    const sw = document.createElement('div');
    sw.className = `swatch${i === 0 ? ' active' : ''}`;
    sw.title = `${p.c1} / ${p.c2}`;
    sw.style.background = `linear-gradient(135deg, ${p.c1} 50%, ${p.c2} 50%)`;
    sw.addEventListener('click', () => {
      qq('.swatch').forEach(s => s.classList.remove('active'));
      sw.classList.add('active');
      $('color1').value = p.c1;
      $('color2').value = p.c2;
      state.c1 = p.c1;
      state.c2 = p.c2;
      updateMockBg();
    });
    container.appendChild(sw);
  });
}

// ── Background mode buttons ────────────────────────────────────────
function initBgButtons() {
  qq('[data-bg]').forEach(btn => {
    btn.addEventListener('click', () => {
      qq('[data-bg]').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.bgMode = btn.dataset.bg;
      updateMockBg();
    });
  });

  ['color1', 'color2'].forEach(id => {
    const el = $(id);
    if (!el) return;
    el.addEventListener('input', e => {
      if (id === 'color1') state.c1 = e.target.value;
      else state.c2 = e.target.value;
      qq('.swatch').forEach(s => s.classList.remove('active'));
      qq('[data-bg]').forEach(b => b.classList.remove('active'));
      qq('[data-bg="custom"]').forEach(b => b.classList.add('active'));
      state.bgMode = 'custom';
      updateMockBg();
    });
  });
}

// ── Process + progress ─────────────────────────────────────────────
function log(msg) {
  const el = $('processLog');
  if (el) el.textContent = msg;
}

function updateProgress(d) {
  const pct = d.total > 0 ? Math.round((d.progress / d.total) * 100) : 0;
  $('progressBar').style.width = `${pct}%`;
  $('progressLabel').textContent = d.current || 'In corso…';
  $('progressPct').textContent = `${pct}%`;
  log(d.current || '');
  if (d.errors?.length) log('⚠ ' + d.errors[d.errors.length - 1]);
}

function startPolling() {
  if (pollTimer) return;
  $('progressWrap').hidden = false;
  pollTimer = setInterval(async () => {
    try {
      const res = await fetch('/api/progress');
      const d = await res.json();
      updateProgress(d);
      if (!d.active) {
        clearInterval(pollTimer);
        pollTimer = null;
        $('processBtn').disabled = false;
        $('processBtn').textContent = 'Avvia elaborazione';
        if (!d.errors?.length) {
          log('Completato.');
          loadSummary();
          loadCsvFiles();
          showExportPreview();
        }
      }
    } catch (_) { clearInterval(pollTimer); pollTimer = null; }
  }, 900);
}

async function showExportPreview() {
  try {
    const res = await fetch('/api/preview');
    const d = await res.json();
    if (!d.ok || !d.products?.length) return;
    const bar  = $('exportPreviewBar');
    const list = $('exportPreviewList');
    if (!bar || !list) return;
    bar.hidden = false;
    list.innerHTML = d.products.slice(0, 8).map(p =>
      `<div class="epr-row"><strong>${p.title || p.handle}</strong><span>${p.collection || '—'} · €${p.price || '—'}</span></div>`
    ).join('');
    $('exportStatusText').textContent = `${d.products.length} prodotti nel catalogo attivo.`;
  } catch (_) { /* ignore */ }
}

// ── Shipping panel ─────────────────────────────────────────────────
let shipPollTimer = null;

async function loadShippingReport() {
  const dot  = $('shipDot');
  const text = $('shipStatusText');
  dot.className = 'pconn-dot loading';
  text.textContent = 'Caricamento report…';

  try {
    const res = await fetch('/api/shipping/report');
    const d = await res.json();
    if (!d.ok) {
      dot.className = 'pconn-dot offline';
      text.textContent = 'Report non disponibile — clicca "Sync Printify"';
      return;
    }
    renderShippingReport(d);
  } catch (e) {
    dot.className = 'pconn-dot offline';
    text.textContent = 'Errore: ' + e.message;
  }
}

function renderShippingReport(d) {
  const dot  = $('shipDot');
  const text = $('shipStatusText');
  const upd  = $('shipUpdated');

  dot.className = 'pconn-dot online';
  text.textContent = `Sync Printify · ${d.total_products} prodotti · ${d.total_types} tipi`;
  if (upd) upd.textContent = d.generated_at ? `Aggiornato: ${d.generated_at.slice(0,16).replace('T',' ')}` : '';

  $('shipStats').hidden  = false;
  $('shipProducts').textContent = d.total_products || '-';
  $('shipTypes').textContent    = d.total_types || '-';
  $('shipAlerts').textContent   = (d.alerts || []).length;
  const mkts = Object.values(d.key_markets_summary || {});
  $('shipMarkets').textContent  = mkts.filter(m => m.covered_by_types > 0).length + '/' + mkts.length;

  // Key markets table
  const tbody = $('shipMarketsBody');
  if (tbody && d.key_markets_summary) {
    tbody.innerHTML = '';
    Object.entries(d.key_markets_summary).forEach(([country, info]) => {
      const covered = info.ship_min !== null;
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>${country}</td>
        <td>${info.region}</td>
        <td style="text-align:right">${covered ? '$' + info.ship_min.toFixed(2) : '—'}</td>
        <td style="text-align:right">${covered ? '$' + info.ship_max.toFixed(2) : '—'}</td>
        <td style="text-align:right;${covered ? '' : 'color:var(--warning);font-weight:700'}">${info.covered_by_types || (covered ? '?' : '✗')}</td>
      `;
      tbody.appendChild(tr);
    });
    $('shipMarketsCard').hidden = false;
  }

  // Per-type cards
  const typesList = $('shipTypesList');
  if (typesList && d.by_type) {
    typesList.innerHTML = '';
    d.by_type.forEach(t => {
      const card = document.createElement('div');
      card.className = 'ship-type-card';
      const itMarket = t.markets?.find(m => m.country === 'IT');
      const usMarket = t.markets?.find(m => m.country === 'US');
      const deMarket = t.markets?.find(m => m.country === 'DE');

      const chips = (t.markets || []).filter(m => m.ship_first !== null && m.ship_first !== undefined).slice(0, 6).map(m => {
        const cls = m.region === 'EU' || m.region === 'UK' || m.region === 'CH' ? 'eu' : m.region === 'US' || m.region === 'CA' ? 'us' : '';
        return `<span class="ship-country-chip ${cls}">${m.country} $${m.ship_first?.toFixed(2)}</span>`;
      }).join('');

      const alerts = (t.alerts || []).slice(0, 3).map(a =>
        `<div class="ship-alert-row">${a}</div>`
      ).join('');

      card.innerHTML = `
        <div class="ship-type-header">
          <div>
            <h4>${t.name}</h4>
            <span style="font-size:11px;color:var(--soft);">${t.product_count} prodotti · Handling: ${t.handling_days} gg</span>
          </div>
          <div class="ship-type-meta">
            <span class="ship-meta-pill">Retail $${t.retail_min?.toFixed(0)}–$${t.retail_max?.toFixed(0)}</span>
            <span class="ship-meta-pill">IT $${itMarket?.ship_first?.toFixed(2) ?? '?'}</span>
            <span class="ship-meta-pill">US $${usMarket?.ship_first?.toFixed(2) ?? '?'}</span>
            <span class="ship-meta-pill">DE $${deMarket?.ship_first?.toFixed(2) ?? '?'}</span>
          </div>
        </div>
        <div class="ship-markets-mini">${chips}</div>
        ${alerts ? `<div class="ship-alerts-mini">${alerts}</div>` : ''}
      `;
      typesList.appendChild(card);
    });
    $('shipTypesSection').hidden = false;
  }

  // Recommendations
  if (d.recommendations?.length) {
    const recsList = $('shipRecsList');
    recsList.innerHTML = d.recommendations.map(r =>
      `<div class="rec-row"><span class="rec-priority ${r.priority}">${r.priority}</span><span>${r.msg}</span></div>`
    ).join('');
    $('shipRecsCard').hidden = false;
  }
}

function startShipPolling() {
  if (shipPollTimer) return;
  $('shipProgress').hidden = false;
  shipPollTimer = setInterval(async () => {
    try {
      const res = await fetch('/api/shipping/progress');
      const d = await res.json();
      $('shipProgress').textContent = `[${d.pct}%] ${d.msg}`;
      if (!d.active) {
        clearInterval(shipPollTimer); shipPollTimer = null;
        $('shipProgress').hidden = true;
        if (d.error) {
          $('shipDot').className = 'pconn-dot offline';
          $('shipStatusText').textContent = 'Errore: ' + d.error;
        } else {
          loadShippingReport();
        }
      }
    } catch (_) { clearInterval(shipPollTimer); shipPollTimer = null; }
  }, 1200);
}

// ── Init ───────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initTabs();
  initSwatches();
  initBgButtons();
  updateMockBg();

  $('csvRefreshBtn')?.addEventListener('click', loadCsvFiles);
  $('pRefreshBtn')?.addEventListener('click', loadPrintifyStatus);

  $('shipRefreshBtn')?.addEventListener('click', async () => {
    const btn = $('shipRefreshBtn');
    btn.disabled = true;
    btn.textContent = 'Sync…';
    $('shipDot').className = 'pconn-dot loading';
    $('shipStatusText').textContent = 'Avvio sync Printify…';
    try {
      const res = await fetch('/api/shipping/refresh', { method: 'POST' });
      const d = await res.json();
      if (d.ok) {
        startShipPolling();
      } else {
        $('shipStatusText').textContent = 'Errore: ' + (d.error || 'sconosciuto');
        $('shipDot').className = 'pconn-dot offline';
      }
    } catch (e) {
      $('shipStatusText').textContent = 'Errore: ' + e.message;
      $('shipDot').className = 'pconn-dot offline';
    } finally {
      btn.disabled = false;
      btn.textContent = 'Sync Printify';
    }
  });

  $('processBtn')?.addEventListener('click', async () => {
    const btn = $('processBtn');
    btn.disabled = true;
    btn.textContent = 'Avvio…';
    log('Avvio elaborazione…');
    try {
      const res = await fetch('/api/process', { method: 'POST' });
      const d = await res.json();
      if (d.ok) {
        btn.textContent = 'Elaborazione in corso…';
        startPolling();
      } else {
        log('Errore: ' + (d.error || 'sconosciuto'));
        btn.disabled = false;
        btn.textContent = 'Avvia elaborazione';
      }
    } catch (e) {
      log('Errore: ' + e.message);
      btn.disabled = false;
      btn.textContent = 'Avvia elaborazione';
    }
  });

  fetch('/api/progress').then(r => r.json()).then(d => {
    if (d.active) {
      $('processBtn').disabled = true;
      $('processBtn').textContent = 'Elaborazione in corso…';
      $('progressWrap').hidden = false;
      startPolling();
    }
  }).catch(() => {});

  loadCsvFiles();
  loadSummary();
  loadPrintifyStatus();
  showExportPreview();

  // ── Immagini Printify ──────────────────────────────────────────────
  let imgState = { page: 1, lastPage: 1, selected: new Set(), polling: null };

  function imgDot(state) { // 'loading' | 'ok' | 'error'
    const dot = $('imgDot');
    if (!dot) return;
    dot.className = `pconn-dot ${state}`;
  }

  function buildImgCard(p) {
    const div = document.createElement('div');
    div.className = 'img-card' + (p.downloaded ? ' downloaded' : '');
    div.dataset.id = p.printify_id;
    div.dataset.handle = p.handle;
    div.dataset.url = p.image || '';

    const chk = document.createElement('input');
    chk.type = 'checkbox';
    chk.className = 'img-card-chk';
    chk.checked = imgState.selected.has(p.printify_id);
    chk.addEventListener('change', e => {
      e.stopPropagation();
      if (chk.checked) imgState.selected.add(p.printify_id);
      else imgState.selected.delete(p.printify_id);
      div.classList.toggle('selected', chk.checked);
      updateImgDownloadBtn();
    });
    div.appendChild(chk);

    if (p.image) {
      const img = document.createElement('img');
      img.className = 'img-thumb';
      img.src = p.image;
      img.alt = p.title;
      img.loading = 'lazy';
      div.appendChild(img);
    } else {
      const ph = document.createElement('div');
      ph.className = 'img-thumb-placeholder';
      ph.textContent = (p.collection || 'BKS')[0].toUpperCase();
      div.appendChild(ph);
    }

    const body = document.createElement('div');
    body.className = 'img-card-body';
    body.innerHTML = `<div class="img-card-title">${p.title}</div>
      <div class="img-card-meta">${p.price ? '€' + p.price : ''}</div>
      <span class="img-card-badge ${p.visible ? 'live' : 'draft'}">${p.visible ? 'Live' : 'Draft'}</span>`;
    div.appendChild(body);

    div.addEventListener('click', e => {
      if (e.target === chk) return;
      chk.checked = !chk.checked;
      if (chk.checked) imgState.selected.add(p.printify_id);
      else imgState.selected.delete(p.printify_id);
      div.classList.toggle('selected', chk.checked);
      updateImgDownloadBtn();
    });

    if (chk.checked) div.classList.add('selected');
    return div;
  }

  function updateImgDownloadBtn() {
    const btn = $('imgDownloadBtn');
    if (!btn) return;
    const n = imgState.selected.size;
    btn.disabled = n === 0 || !!imgState.polling;
    btn.textContent = n ? `Scarica selezionati (${n})` : 'Scarica selezionati';
  }

  async function loadPrintifyImages(page) {
    imgDot('loading');
    $('imgStatusText').textContent = 'Caricamento prodotti…';
    const visible = $('imgVisible')?.value || 'all';
    const collection = $('imgCollection')?.value || '';
    const q_val = $('imgSearch')?.value || '';
    const params = new URLSearchParams({ page, limit: 24, visible });
    if (collection) params.set('collection', collection);
    if (q_val) params.set('q', q_val);
    try {
      const res = await fetch('/api/printify/images?' + params);
      const d = await res.json();
      if (!d.ok) throw new Error(d.error || 'Errore API');
      imgState.page = d.page;
      imgState.lastPage = d.last_page;

      const grid = $('imgGrid');
      grid.innerHTML = '';
      if (!d.products.length) {
        grid.innerHTML = '<div class="muted" style="grid-column:1/-1;padding:24px;text-align:center;">Nessun prodotto trovato.</div>';
      } else {
        d.products.forEach(p => grid.appendChild(buildImgCard(p)));
      }

      // pagination
      const pg = $('imgPagination');
      pg.hidden = d.last_page <= 1;
      $('imgPageInfo').textContent = `Pagina ${d.page} di ${d.last_page} — ${d.total} prodotti`;
      $('imgPrevBtn').disabled = d.page <= 1;
      $('imgNextBtn').disabled = d.page >= d.last_page;

      // local count badge
      if (d.local_count !== undefined)
        $('imgLocalCount').textContent = `${d.local_count} immagini scaricate localmente`;

      imgDot('ok');
      $('imgStatusText').textContent = `${d.products.length} prodotti caricati`;
      updateImgDownloadBtn();
    } catch(e) {
      imgDot('error');
      $('imgStatusText').textContent = 'Errore: ' + e.message;
    }
  }

  function imgPollProgress() {
    if (imgState.polling) return;
    imgState.polling = setInterval(async () => {
      try {
        const d = await fetch('/api/printify/images/progress').then(r => r.json());
        const pct = d.total ? Math.round(d.done / d.total * 100) : 0;
        $('imgProgressBar').style.width = pct + '%';
        $('imgProgressPct').textContent = pct + '%';
        $('imgProgressCurrent').textContent = d.current || '';
        $('imgProgressLabel').textContent = `Download: ${d.done}/${d.total}`;
        if (d.errors && d.errors.length) {
          $('imgProgressErrors').hidden = false;
          $('imgProgressErrors').textContent = d.errors.join('\n');
        }
        if (!d.active) {
          clearInterval(imgState.polling);
          imgState.polling = null;
          $('imgProgressLabel').textContent = d.current || 'Download completato';
          $('imgDownloadBtn').disabled = false;
          $('imgDownloadBtn').textContent = 'Scarica selezionati';
          setTimeout(() => loadPrintifyImages(imgState.page), 800);
        }
      } catch(e) { /* keep polling */ }
    }, 1500);
  }

  $('imgRefreshBtn')?.addEventListener('click', () => {
    imgState.selected.clear();
    loadPrintifyImages(1);
  });
  $('imgPrevBtn')?.addEventListener('click', () => loadPrintifyImages(imgState.page - 1));
  $('imgNextBtn')?.addEventListener('click', () => loadPrintifyImages(imgState.page + 1));

  $('imgSelectAll')?.addEventListener('change', e => {
    qq('.img-card').forEach(card => {
      const chk = card.querySelector('.img-card-chk');
      if (!chk) return;
      chk.checked = e.target.checked;
      if (e.target.checked) imgState.selected.add(card.dataset.id);
      else imgState.selected.delete(card.dataset.id);
      card.classList.toggle('selected', e.target.checked);
    });
    updateImgDownloadBtn();
  });

  let imgSearchTimer = null;
  $('imgSearch')?.addEventListener('input', () => {
    clearTimeout(imgSearchTimer);
    imgSearchTimer = setTimeout(() => loadPrintifyImages(1), 400);
  });
  $('imgVisible')?.addEventListener('change', () => loadPrintifyImages(1));
  $('imgCollection')?.addEventListener('change', () => loadPrintifyImages(1));

  $('imgDownloadBtn')?.addEventListener('click', async () => {
    if (!imgState.selected.size) return;
    const cards = qq('.img-card');
    const items = [];
    cards.forEach(card => {
      if (imgState.selected.has(card.dataset.id)) {
        const url = card.dataset.url || '';
        const ext = url.split('.').pop().split('?')[0].toLowerCase();
        items.push({ handle: card.dataset.handle, url, ext: ['jpg','jpeg','png','webp'].includes(ext) ? ext : 'jpg' });
      }
    });
    if (!items.length) return;
    $('imgProgressWrap').hidden = false;
    $('imgProgressBar').style.width = '0%';
    $('imgProgressPct').textContent = '0%';
    $('imgProgressLabel').textContent = `Avvio download ${items.length} immagini…`;
    $('imgProgressErrors').hidden = true;
    $('imgDownloadBtn').disabled = true;
    try {
      await fetch('/api/printify/images/download', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ items }),
      });
      imgPollProgress();
    } catch(e) {
      $('imgProgressLabel').textContent = 'Errore avvio: ' + e.message;
      $('imgDownloadBtn').disabled = false;
    }
  });

  // Carica immagini quando si apre la tab
  document.querySelectorAll('.tab[data-tab="imagesPanel"]').forEach(btn => {
    btn.addEventListener('click', () => {
      if ($('imgGrid').children.length === 0) loadPrintifyImages(1);
    });
  });
});
