const PRESETS = [
  { label: 'Bone', c1: '#EFEAE0', c2: '#FAFAF7', mode: 'bone' },
  { label: 'Salt', c1: '#FAFAF7', c2: '#EFEAE0', mode: 'salt' },
  { label: 'Shadow', c1: '#242833', c2: '#0A0A0A', mode: 'editorial' },
  { label: 'Onyx', c1: '#0A0A0A', c2: '#242833', mode: 'solid' },
  { label: 'Ink', c1: '#0F2240', c2: '#242833', mode: 'solid' },
  { label: 'Gradient W', c1: '#ffffff', c2: '#e8e8e8', mode: 'gradient' },
  { label: 'Gradient Sand', c1: '#fff8ec', c2: '#d6c1a1', mode: 'gradient' },
  { label: 'Editorial', c1: '#0A0A0A', c2: '#C9B79C', mode: 'editorial' },
  { label: 'Transparent', c1: 'transparent', c2: '#e8e8e8', mode: 'solid' },
];

let currentMode = 'bone';
let selectedPreset = PRESETS[0];

const $ = (id) => document.getElementById(id);

function setStatus(text) {
  $('systemStatus').textContent = text;
}

function listRows(target, data) {
  const el = $(target);
  el.innerHTML = '';
  if (!data || Object.keys(data).length === 0) {
    el.innerHTML = '<div class="list-row"><span>No data</span><b>-</b></div>';
    return;
  }
  Object.entries(data).forEach(([key, value]) => {
    const row = document.createElement('div');
    row.className = 'list-row';
    row.innerHTML = `<span>${key}</span><b>${value}</b>`;
    el.appendChild(row);
  });
}

function updateSummary(data) {
  $('rowsStat').textContent = data.rows ?? '-';
  $('handlesStat').textContent = data.handles ?? '-';
  $('imagesStat').textContent = data.image_rows ?? '-';
  $('rembgStat').textContent = data.rembg_available ? 'ON' : 'Fallback';
  $('missingTitleStat').textContent = data.missing_seo_title ?? '-';
  $('missingDescStat').textContent = data.missing_seo_description ?? data.missing_seo_desc ?? '-';
  $('missingAltStat').textContent = data.missing_alt ?? '-';
  listRows('typesList', data.types || {});
  listRows('vendorsList', data.vendors || {});
}

function updateTargetMeter(yes, target) {
  const min = target?.min_total ?? 90;
  const max = target?.max_total ?? 150;
  const pct = Math.max(0, Math.min(100, Math.round((yes / max) * 100)));
  $('targetMeterFill').style.width = `${pct}%`;
  $('targetMeterFill').classList.toggle('under', yes < min);
  $('targetMeterFill').classList.toggle('over', yes > max);
  $('targetSummary').textContent = `${yes} active selezionati. Target: ${min}-${max} totali, ${target?.min_per_collection ?? 8}-${target?.max_per_collection ?? 22} per collection.`;
}

function updateCurationStats(data) {
  const keep = data.keep_counts || {};
  const yes = keep.Yes ?? 0;
  const no = keep.No ?? 0;
  const skip = keep.Skip ?? 0;
  const empty = keep.Empty ?? 0;
  $('curProductsStat').textContent = data.products ?? '-';
  $('curYesStat').textContent = yes;
  $('curNoStat').textContent = no;
  $('curEmptyStat').textContent = empty + skip;
  listRows('activeSeriesList', data.active_by_series || {});
  listRows('activeTypeList', data.active_by_type || {});
  listRows('seriesList', data.series_counts || {});
  listRows('statusList', data.status_counts || {});
  updateTargetMeter(yes, data.target || {});

  const missing = [];
  if (!data.columns?.keep) missing.push('Keep');
  if (!data.columns?.series) missing.push('Series/Collection');
  $('curationStatus').textContent = missing.length
    ? `Colonne mancanti nel CSV: ${missing.join(', ')}. I conteggi sono parziali: aggiungi queste colonne al workboard per il bilanciamento finale.`
    : `Curation pronta. Keep letto da "${data.columns.keep}", collection letta da "${data.columns.series}".`;
}

async function loadCurationStats() {
  try {
    const res = await fetch('/api/curation/stats');
    const data = await res.json();
    if (!data.ok) throw new Error(data.error || 'Curation stats error');
    updateCurationStats(data);
  } catch (err) {
    $('curationStatus').textContent = err.message;
  }
}

async function loadSummary() {
  try {
    const res = await fetch('/api/summary');
    const data = await res.json();
    if (!data.ok) throw new Error(data.error || 'Summary error');
    updateSummary(data);
    await loadCurationStats();
    setStatus('CSV loaded');
  } catch (err) {
    $('processStatus').textContent = err.message;
    setStatus('CSV missing');
  }
}

function initTabs() {
  document.querySelectorAll('.tab').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      $(btn.dataset.tab).classList.add('active');
    });
  });
}

function initModes() {
  document.querySelectorAll('.seg-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.seg-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentMode = btn.dataset.bgMode;
      selectedPreset.mode = currentMode;
      updateMock();
    });
  });
}

function initSwatches() {
  const box = $('swatches');
  PRESETS.forEach((preset, index) => {
    const sw = document.createElement('button');
    sw.className = 'swatch' + (index === 0 ? ' active' : '');
    sw.title = preset.label;
    if (preset.c1 === 'transparent') {
      sw.style.background = 'repeating-conic-gradient(#ccc 0% 25%, #eee 0% 50%) 0 0 / 12px 12px';
    } else if (preset.mode === 'gradient') {
      sw.style.background = `linear-gradient(135deg, ${preset.c1}, ${preset.c2})`;
    } else {
      sw.style.background = preset.c1;
    }
    sw.addEventListener('click', () => {
      document.querySelectorAll('.swatch').forEach(s => s.classList.remove('active'));
      sw.classList.add('active');
      selectedPreset = { ...preset };
      currentMode = preset.mode;
      $('color1').value = preset.c1 === 'transparent' ? '#ffffff' : preset.c1;
      $('color2').value = preset.c2;
      document.querySelectorAll('.seg-btn').forEach(b => b.classList.toggle('active', b.dataset.bgMode === currentMode));
      updateMock();
    });
    box.appendChild(sw);
  });
}

function updateMock() {
  const c1 = selectedPreset.c1 === 'transparent' ? '#ffffff' : $('color1').value;
  const c2 = $('color2').value;
  if (selectedPreset.c1 === 'transparent') {
    $('mockImage').style.background = 'repeating-conic-gradient(#ccc 0% 25%, #eee 0% 50%) 0 0 / 22px 22px';
    return;
  }
  $('mockImage').style.background = currentMode === 'gradient' || currentMode === 'editorial'
    ? `linear-gradient(135deg, ${c1}, ${c2})`
    : c1;
}

$('color1').addEventListener('input', () => { selectedPreset.c1 = $('color1').value; updateMock(); });
$('color2').addEventListener('input', () => { selectedPreset.c2 = $('color2').value; updateMock(); });

$('chooseCsvBtn').addEventListener('click', () => $('csvInput').click());
$('uploadBox').addEventListener('click', (e) => {
  if (e.target.id !== 'chooseCsvBtn') $('csvInput').click();
});

$('csvInput').addEventListener('change', async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  const fd = new FormData();
  fd.append('csv', file);
  $('processStatus').textContent = 'Uploading CSV...';
  setStatus('Uploading');
  try {
    const res = await fetch('/api/upload', { method: 'POST', body: fd });
    const data = await res.json();
    if (!data.ok) throw new Error(data.error || 'Upload error');
    updateSummary(data);
    await loadCurationStats();
    $('processStatus').textContent = `CSV uploaded: ${file.name}\nRows: ${data.rows}\nProducts: ${data.handles}`;
    setStatus('CSV uploaded');
  } catch (err) {
    $('processStatus').textContent = err.message;
    setStatus('Upload error');
  }
});

$('processBtn').addEventListener('click', async () => {
  const color1 = selectedPreset.c1 === 'transparent' ? 'transparent' : $('color1').value;
  const payload = {
    bg_style: currentMode,
    color1,
    color2: $('color2').value,
    autofill: $('autofill').checked,
    max_images: Number($('maxImages').value || 0),
    timeout: 45,
  };
  $('processBtn').disabled = true;
  $('progressWrap').hidden = false;
  setProgress(0, 'Avvio elaborazione');
  $('processStatus').textContent = 'Processing catalog...\nThis can take time when many product images are processed.';
  setStatus('Processing');
  try {
    const res = await fetch('/api/process', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (!data.ok) throw new Error(data.error || 'Processing error');
    $('processStatus').textContent = data.message || 'Processing started.';
    pollProgress();
  } catch (err) {
    $('processStatus').textContent = err.message;
    setStatus('Error');
    $('processBtn').disabled = false;
  }
});

function setProgress(pct, label) {
  $('progressBar').style.width = `${pct}%`;
  $('progressPct').textContent = `${pct}%`;
  $('progressLabel').textContent = label;
}

async function pollProgress() {
  const timer = setInterval(async () => {
    try {
      const res = await fetch('/api/progress');
      const data = await res.json();
      const total = Number(data.total || 0);
      const current = Number(data.progress || 0);
      const pct = total > 0 ? Math.min(100, Math.round((current / total) * 100)) : 0;
      setProgress(pct, data.current || (data.active ? 'Elaborazione...' : 'Completato'));

      const errors = Array.isArray(data.errors) && data.errors.length
        ? `\nErrors:\n${data.errors.slice(-8).join('\n')}`
        : '';
      $('processStatus').textContent = `Processed ${current}/${total}.${errors}`;

      if (!data.active) {
        clearInterval(timer);
        setProgress(total > 0 ? 100 : pct, 'Completato');
        $('processStatus').textContent = `Completed.\nProcessed ${current}/${total}.${errors}\n\nScarica i file dal tab Export.`;
        $('processBtn').disabled = false;
        setStatus('Completed');
        await loadSummary();
      }
    } catch (err) {
      clearInterval(timer);
      $('processStatus').textContent = err.message;
      $('processBtn').disabled = false;
      setStatus('Error');
    }
  }, 1000);
}

document.addEventListener('dragover', (event) => event.preventDefault());
document.addEventListener('drop', async (event) => {
  event.preventDefault();
  const file = event.dataTransfer?.files?.[0];
  if (!file) return;
  const fd = new FormData();
  fd.append('csv', file);
  $('processStatus').textContent = 'Uploading CSV...';
  setStatus('Uploading');
  try {
    const res = await fetch('/api/upload', { method: 'POST', body: fd });
    const data = await res.json();
    if (!data.ok) throw new Error(data.error || 'Upload error');
    updateSummary(data);
    await loadCurationStats();
    $('processStatus').textContent = `CSV uploaded: ${file.name}\nRows: ${data.rows}\nProducts: ${data.handles}`;
    setStatus('CSV uploaded');
  } catch (err) {
    $('processStatus').textContent = err.message;
    setStatus('Upload error');
  }
});

initTabs();
initModes();
initSwatches();
updateMock();
loadSummary();
loadCurationStats();
