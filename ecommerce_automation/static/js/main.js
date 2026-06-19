async function getJson(url, options) {
  const response = await fetch(url, options);
  const body = await response.json();
  if (!response.ok) {
    throw new Error(body.message || body.error || response.statusText);
  }
  return body;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function mediaUrl(path) {
  return path ? encodeURI(`/media/workspace/${path}`) : "";
}

function connectionState(configured) {
  if (typeof configured === "boolean") {
    return {
      connected: configured,
      status: configured ? "configured" : "missing",
      label: configured ? "Connesso" : "Non connesso",
      details: "",
    };
  }
  const status = configured.status || (configured.configured ? "configured" : "missing");
  const connected = Boolean(configured.configured) && !["offline", "missing", "missing_key", "missing_api_key", "missing_webhook_url", "not_configured", "needs_config", "error", "suspended", "limited", "needs_review"].includes(status);
  const details = Object.entries(configured)
    .filter(([key]) => !["configured", "status"].includes(key))
    .map(([key, value]) => `${key}: ${typeof value === "object" ? JSON.stringify(value) : value}`)
    .join("<br>");
  return {
    connected,
    status,
    label: connected ? "Connesso" : "Non connesso",
    details,
  };
}

function serviceCard(name, configured) {
  const state = connectionState(configured);
  return `
    <div class="status-card connection-card">
      <div class="connection-head">
        <strong>${escapeHtml(name)}</strong>
        <span class="status-dot ${state.connected ? "connected" : "disconnected"}"></span>
      </div>
      <div class="connection-label ${state.connected ? "connected" : "disconnected"}">${state.label}</div>
      <div class="phase-meta">${escapeHtml(state.status)}</div>
      ${state.details ? `<div class="phase-meta">${state.details}</div>` : ""}
    </div>
  `;
}

function phaseCard(phase) {
  const statusClass = `status-${String(phase.status).replaceAll("_", "-")}`;
  const systems = (phase.external_systems || []).join(", ") || "local";
  const progress = phase.progress || 0;
  return `
    <article class="phase-card">
      <strong>${phase.phase_id}. ${phase.name}</strong>
      <p>${phase.objective || phase.message || ""}</p>
      <div class="phase-progress-line"><span>Avanzamento</span><b>${progress}%</b></div>
      <div class="progress"><span style="width:${progress}%"></span></div>
      <div class="phase-meta"><span class="${statusClass}">${phase.status}</span> · ${systems}</div>
      <button class="button" data-run-phase="${phase.phase_id}">Run</button>
      <button class="button secondary" data-agent-message="stato fase ${phase.phase_id}">Info</button>
    </article>
  `;
}

function referenceCard(label, value, detail = "") {
  return `<div class="reference-card"><strong>${escapeHtml(label)}</strong><div class="reference-value">${escapeHtml(value)}</div><div class="phase-meta">${escapeHtml(detail)}</div></div>`;
}

function avatarSummaryCard(label, value, detail = "") {
  return `<div class="reference-card"><strong>${escapeHtml(label)}</strong><div class="reference-value">${escapeHtml(value)}</div><div class="phase-meta">${escapeHtml(detail)}</div></div>`;
}

function boundedPercent(value) {
  const number = Number(value || 0);
  return Math.max(0, Math.min(100, Number.isFinite(number) ? number : 0));
}

function metricBars(rows) {
  if (!rows.length) return "No metrics yet.";
  return rows.map((row) => {
    const percent = boundedPercent(row.percent ?? row.score);
    return `
      <div class="metric-bar-row">
        <div class="metric-bar-head">
          <strong>${escapeHtml(row.label || row.signal || row.name)}</strong>
          <span>${escapeHtml(row.value ?? row.status ?? "")}${row.total ? ` / ${escapeHtml(row.total)}` : ""} · ${percent}%</span>
        </div>
        <div class="metric-bar"><span style="width:${percent}%"></span></div>
        ${row.meaning ? `<div class="phase-meta">${escapeHtml(row.meaning)}</div>` : ""}
      </div>
    `;
  }).join("");
}

function donutCard(label, value, detail = "", status = "ready") {
  const percent = boundedPercent(value);
  return `
    <div class="donut-card">
      <div class="donut" style="--p:${percent}%">
        <span>${percent}%</span>
      </div>
      <div>
        <strong>${escapeHtml(label)}</strong>
        <p><span class="status-${escapeHtml(status)}">${escapeHtml(status)}</span></p>
        <small>${escapeHtml(detail)}</small>
      </div>
    </div>
  `;
}

function progressChart(rows) {
  if (!rows.length) return "No chart data yet.";
  return rows.map((row) => {
    const percent = boundedPercent(row.progress ?? row.percent ?? 0);
    return `
      <div class="chart-bar-row">
        <div class="chart-bar-head">
          <strong>${escapeHtml(row.stage || row.label || row.signal)}</strong>
          <span><span class="status-${escapeHtml(row.status || "ready")}">${escapeHtml(row.status || "ready")}</span> · ${percent}%</span>
        </div>
        <div class="chart-bar"><span style="width:${percent}%"></span></div>
        <small>${escapeHtml(row.signal || row.detail || "")}</small>
      </div>
    `;
  }).join("");
}

function avatarTable(rows) {
  if (!rows.length) return "No avatar rows yet.";
  const head = `
    <div class="table-row table-head">
      <span>Collection</span>
      <span>Preview</span>
      <span>Script</span>
      <span>Image</span>
      <span>Export</span>
      <span>Next</span>
    </div>
  `;
  const body = rows.map((row) => `
    <div class="table-row">
      <span><strong>${escapeHtml(row.collection)}</strong><br><small>${escapeHtml(row.progress)}%</small><div class="mini-progress"><span style="width:${escapeHtml(row.progress)}%"></span></div></span>
      <span>${row.preview_image ? `<img class="avatar-thumb" src="${mediaUrl(row.preview_image)}" alt="${escapeHtml(row.collection)} preview">` : ""}</span>
      <span><span class="status-${escapeHtml(row.script_status)}">${escapeHtml(row.script_status)}</span><br><small>${escapeHtml(row.script_words)} words</small></span>
      <span>${row.selected_image ? "selected" : "needed"}<br><small>${escapeHtml(row.selected_image || row.suggested_image || "")}</small></span>
      <span>${row.export_file ? "ready" : "pending"}<br><small>${escapeHtml(row.export_file || "")}</small></span>
      <span>${escapeHtml(row.next_action)}</span>
    </div>
  `).join("");
  return head + body;
}

function avatarPreviewGrid(rows, videos) {
  const collectionCards = rows.map((row) => `
    <article class="preview-card">
      ${row.preview_image ? `<img class="preview-media" src="${mediaUrl(row.preview_image)}" alt="${escapeHtml(row.collection)}">` : `<div class="preview-placeholder">No preview</div>`}
      <div class="preview-title"><strong>${escapeHtml(row.collection)}</strong><span>${escapeHtml(row.progress)}%</span></div>
      <div class="mini-progress"><span style="width:${escapeHtml(row.progress)}%"></span></div>
      <p>${escapeHtml(row.script_excerpt || row.next_action || "")}</p>
      ${row.export_file ? `<video class="preview-video" src="${mediaUrl(row.export_file)}" controls></video>` : ""}
    </article>
  `).join("");
  const videoCards = (videos || []).slice(0, 2).map((video) => `
    <article class="preview-card">
      <video class="preview-video large" src="${mediaUrl(video.path)}" controls></video>
      <strong>${escapeHtml(video.name)}</strong>
      <p>${escapeHtml(video.size_mb)} MB existing MP4</p>
    </article>
  `).join("");
  return collectionCards + videoCards;
}

async function refreshAvatarProduction() {
  const summaryRoot = document.querySelector("#avatar-summary");
  const tableRoot = document.querySelector("#avatar-table");
  const heygenRoot = document.querySelector("#heygen-steps");
  const apiRoot = document.querySelector("#heygen-api-status");
  const previewRoot = document.querySelector("#avatar-preview-grid");
  if (!summaryRoot && !tableRoot && !heygenRoot && !apiRoot && !previewRoot) return;

  const data = await getJson("/api/avatar-production");
  const summary = data.summary || {};
  const heygen = data.heygen_api || {};
  if (summaryRoot) {
    summaryRoot.innerHTML = [
      avatarSummaryCard("Scripts", `${summary.scripts_ready || 0}/${summary.collections || 0}`, data.script_target || ""),
      avatarSummaryCard("Images", `${summary.images_ready || 0}/${summary.collections || 0}`, "selected 9:16 hero images"),
      avatarSummaryCard("Exports", `${summary.exports_ready || 0}/${summary.collections || 0}`, `${summary.existing_video_files || 0} MP4 in Video_Avatar`),
      avatarSummaryCard("Progress", `${summary.progress || 0}%`, summary.workspace || ""),
    ].join("");
  }
  if (apiRoot) {
    apiRoot.innerHTML = `
      <div class="api-pill ${heygen.configured ? "configured" : "missing"}">
        <strong>HeyGen API</strong>
        <span>${heygen.configured ? "configured" : "missing key"}</span>
        <small>${escapeHtml(heygen.key_env || "HEYGEN_API_KEY")} · <a href="${escapeHtml(heygen.console || "#")}" target="_blank" rel="noreferrer">console</a></small>
      </div>
    `;
  }
  if (previewRoot) {
    previewRoot.innerHTML = avatarPreviewGrid(data.rows || [], data.videos || []);
  }
  if (tableRoot) {
    tableRoot.innerHTML = avatarTable(data.rows || []);
  }
  if (heygenRoot) {
    heygenRoot.innerHTML = (data.heygen_steps || []).map((step) => `<li>${escapeHtml(step)}</li>`).join("");
  }
}

function socialRenderTable(rows) {
  if (!rows.length) return "No social render rows yet.";
  const head = `
    <div class="social-row table-head">
      <span>Collection</span>
      <span>Status</span>
      <span>Format</span>
      <span>Asset</span>
      <span>Target</span>
      <span>Next</span>
    </div>
  `;
  const body = rows.map((row) => `
    <div class="social-row">
      <span><strong>${escapeHtml(row.collection)}</strong><br><small>${escapeHtml(row.progress)}%</small><div class="mini-progress"><span style="width:${escapeHtml(row.progress)}%"></span></div></span>
      <span>${escapeHtml(row.render_status)}<br><small>${escapeHtml(row.make_event)}</small></span>
      <span>${escapeHtml(row.format)}<br><small>${escapeHtml(row.duration)} · ${escapeHtml(row.platforms)}</small></span>
      <span><small>${escapeHtml(row.video_file || row.source_image || row.suggested_image || row.script_path)}</small></span>
      <span>${escapeHtml(row.cta)}<br><small>${escapeHtml(row.target_url)}<br>${escapeHtml(row.utm_campaign)}</small></span>
      <span>${escapeHtml(row.next_action)}</span>
    </div>
  `).join("");
  return head + body;
}

async function refreshSocialRender() {
  const statusRoot = document.querySelector("#social-render-status");
  const tableRoot = document.querySelector("#social-render-table");
  const downloadLink = document.querySelector("#social-render-download");
  if (!statusRoot && !tableRoot && !downloadLink) return;

  const data = await getJson("/api/social-render");
  const heygen = data.heygen_api || {};
  const make = data.make || {};
  const youtube = data.youtube || {};
  const rows = data.rows || [];
  const readyForHeygen = rows.filter((row) => row.render_status === "ready_for_heygen").length;
  const readyForSocial = rows.filter((row) => row.render_status === "ready_for_social").length;

  if (statusRoot) {
    statusRoot.innerHTML = [
      avatarSummaryCard("HeyGen", heygen.configured ? "Connesso" : "Non connesso", heygen.status || ""),
      avatarSummaryCard("Avatar/Voice", heygen.render_profile_ready ? "Pronto" : "Da completare", `${heygen.avatar_env || ""} · ${heygen.voice_env || ""}`),
      avatarSummaryCard("Make", make.configured ? "Connesso" : "Non connesso", make.status || ""),
      avatarSummaryCard("YouTube", youtube.configured ? "Connesso" : "Non connesso", youtube.status || ""),
      avatarSummaryCard("Social ready", `${readyForSocial}/${rows.length}`, `${readyForHeygen} ready for HeyGen`),
    ].join("");
  }
  if (tableRoot) {
    tableRoot.innerHTML = socialRenderTable(rows);
  }
  if (downloadLink && data.sheet) {
    downloadLink.href = mediaUrl(data.sheet);
  }
}

function communicationsTable(rows) {
  if (!rows.length) return "No communication channels yet.";
  const head = `
    <div class="comm-row table-head">
      <span>Channel</span>
      <span>Status</span>
      <span>Purpose</span>
      <span>Env</span>
      <span>Link</span>
      <span>Consent</span>
    </div>
  `;
  const body = rows.map((row) => `
    <div class="comm-row">
      <span><strong>${escapeHtml(row.channel)}</strong></span>
      <span>${escapeHtml(row.status)}</span>
      <span>${escapeHtml(row.purpose)}</span>
      <span><small>${escapeHtml(row.required_env)}</small></span>
      <span>${row.link ? `<a href="${escapeHtml(row.link)}" target="_blank" rel="noreferrer">open</a>` : "pending"}</span>
      <span>${escapeHtml(row.consent)}</span>
    </div>
  `).join("");
  return head + body;
}

async function refreshCommunications() {
  const summaryRoot = document.querySelector("#communications-summary");
  const tableRoot = document.querySelector("#communications-table");
  if (!summaryRoot && !tableRoot) return;
  const data = await getJson("/api/communications");
  const summary = data.summary || {};
  if (summaryRoot) {
    summaryRoot.innerHTML = [
      avatarSummaryCard("Configured", summary.configured || 0, "ready channels"),
      avatarSummaryCard("Missing", summary.missing || 0, "needs credentials"),
      avatarSummaryCard("Planned", summary.planned || 0, "future bot links"),
      avatarSummaryCard("Consent", "Required", "automated customer chat"),
    ].join("");
  }
  if (tableRoot) {
    tableRoot.innerHTML = communicationsTable(data.channels || []);
  }
}

function salesChannelsTable(rows) {
  if (!rows.length) return "No sales channels yet.";
  const head = `
    <div class="sales-row table-head">
      <span>Channel</span>
      <span>Status</span>
      <span>Type</span>
      <span>Priority</span>
      <span>Purpose</span>
      <span>Next</span>
    </div>
  `;
  const body = rows.map((row) => `
    <div class="sales-row">
      <span><strong>${escapeHtml(row.channel)}</strong></span>
      <span><span class="status-${escapeHtml(row.status)}">${escapeHtml(row.status)}</span><br><small>${escapeHtml(row.required)}</small></span>
      <span>${escapeHtml(row.type)}</span>
      <span>${escapeHtml(row.priority)}</span>
      <span>${escapeHtml(row.purpose)}</span>
      <span>${escapeHtml(row.next_action)}</span>
    </div>
  `).join("");
  return head + body;
}

async function refreshSalesChannels() {
  const summaryRoot = document.querySelector("#sales-channels-summary");
  const tableRoot = document.querySelector("#sales-channels-table");
  const downloadLink = document.querySelector("#sales-channels-download");
  if (!summaryRoot && !tableRoot && !downloadLink) return;
  const data = await getJson("/api/sales-channels");
  const summary = data.summary || {};
  if (summaryRoot) {
    summaryRoot.innerHTML = [
      avatarSummaryCard("Active", summary.active || 0, "selling now"),
      avatarSummaryCard("Partial", summary.partial || 0, "needs completion"),
      avatarSummaryCard("Planned", summary.planned || 0, "roadmap"),
      avatarSummaryCard("Missing", summary.missing || 0, "needs config"),
    ].join("");
  }
  if (tableRoot) {
    tableRoot.innerHTML = salesChannelsTable(data.rows || []);
  }
  if (downloadLink && summary.sheet) {
    downloadLink.href = mediaUrl(summary.sheet);
  }
}

async function refreshCatalogSync(live = false) {
  const summaryRoot = document.querySelector("#catalog-sync-summary");
  const chartsRoot = document.querySelector("#catalog-sync-charts");
  const tableRoot = document.querySelector("#catalog-sync-diff-table");
  const downloadLink = document.querySelector("#catalog-sync-download");
  if (!summaryRoot && !chartsRoot && !tableRoot && !downloadLink) return;
  const data = live
    ? await getJson("/api/catalog-live-sync/run", { method: "POST" })
    : await getJson("/api/catalog-live-sync");
  const summary = data.summary || {};
  if (summaryRoot) {
    summaryRoot.innerHTML = [
      avatarSummaryCard("Status", summary.status || "ready_for_live_sync", summary.live ? "live" : "snapshot"),
      avatarSummaryCard("Shopify", summary.shopify_products || 0, "prodotti live"),
      avatarSummaryCard("Printify", summary.printify_products || 0, "prodotti live"),
      avatarSummaryCard("Attention", summary.attention || 0, `${summary.errors || 0} errori`),
    ].join("");
  }
  if (chartsRoot) {
    const total = Number(summary.matched || 0) + Number(summary.attention || 0);
    const matchPercent = total ? Math.round((Number(summary.matched || 0) / total) * 100) : 0;
    const attentionPercent = total ? Math.round((Number(summary.attention || 0) / total) * 100) : 0;
    chartsRoot.innerHTML = [
      donutCard("Matched", matchPercent, `${summary.matched || 0} prodotti`, matchPercent >= 90 ? "pass" : "needs_review"),
      donutCard("Attention", attentionPercent, "mapping/status", attentionPercent ? "needs_review" : "pass"),
    ].join("");
  }
  if (tableRoot) {
    tableRoot.innerHTML = simpleRowsTable(data.diff || [], [
      { key: "status", label: "Status", render: (row) => `<span class="status-${escapeHtml(row.status)}">${escapeHtml(row.status)}</span>` },
      { key: "handle", label: "Handle", render: (row) => `<strong>${escapeHtml(row.handle)}</strong><br><small>${escapeHtml(row.title)}</small>` },
      { key: "shopify_id", label: "Shopify" },
      { key: "printify_id", label: "Printify" },
      { key: "next_action", label: "Next" },
    ], "catalog-row");
  }
  if (downloadLink && summary.diff_sheet) downloadLink.href = mediaUrl(summary.diff_sheet);
}

async function refreshProductNameAudit(live = false) {
  const summaryRoot = document.querySelector("#product-name-audit-summary");
  const chartsRoot = document.querySelector("#product-name-audit-charts");
  const tableRoot = document.querySelector("#product-name-audit-table");
  const downloadLink = document.querySelector("#product-name-audit-download");
  if (!summaryRoot && !chartsRoot && !tableRoot && !downloadLink) return;
  const data = await getJson(`/api/product-name-audit${live ? "?live=1" : ""}`);
  const summary = data.summary || {};
  if (summaryRoot) {
    summaryRoot.innerHTML = [
      avatarSummaryCard("Source", summary.source || "-", "live Shopify or CSV"),
      avatarSummaryCard("Products", summary.products || 0, "checked"),
      avatarSummaryCard("Needs fix", summary.needs_fix || 0, "high priority"),
      avatarSummaryCard("Needs review", summary.needs_review || 0, "manual check"),
    ].join("");
  }
  if (chartsRoot) {
    const total = Number(summary.products || 0);
    const passPercent = total ? Math.round((Number(summary.pass || 0) / total) * 100) : 0;
    const fixPercent = total ? Math.round((Number(summary.needs_fix || 0) / total) * 100) : 0;
    const reviewPercent = total ? Math.round((Number(summary.needs_review || 0) / total) * 100) : 0;
    chartsRoot.innerHTML = [
      donutCard("Names OK", passPercent, `${summary.pass || 0} prodotti`, passPercent >= 90 ? "pass" : "needs_review"),
      donutCard("Fix", fixPercent, `${summary.needs_fix || 0} urgenti`, fixPercent ? "needs_fix" : "pass"),
      donutCard("Review", reviewPercent, `${summary.needs_review || 0} da verificare`, reviewPercent ? "needs_review" : "pass"),
    ].join("");
  }
  if (tableRoot) {
    tableRoot.innerHTML = simpleRowsTable(data.rows || [], [
      { key: "status", label: "Status", render: (row) => `<span class="status-${escapeHtml(row.status)}">${escapeHtml(row.status)}</span><br><small>${escapeHtml(row.issues)}</small>` },
      { key: "handle", label: "Handle", render: (row) => `<strong>${escapeHtml(row.handle)}</strong><br><small>${escapeHtml(row.collection)}</small>` },
      { key: "title", label: "Current title" },
      { key: "suggested_title", label: "Suggested" },
    ], "name-audit-row");
  }
  if (downloadLink && summary.sheet) downloadLink.href = mediaUrl(summary.sheet);
}

function skillRegistryTable(rows) {
  if (!rows.length) return "No skills found yet.";
  const head = `
    <div class="skill-row table-head">
      <span>Skill</span>
      <span>Status</span>
      <span>Phase</span>
      <span>File</span>
      <span>Related</span>
    </div>
  `;
  const body = rows.map((row) => `
    <div class="skill-row">
      <span><strong>${escapeHtml(row.skill)}</strong><br><small>${escapeHtml(row.title)}</small></span>
      <span>${escapeHtml(row.status)}<br><small>${escapeHtml(row.sections)} sections</small></span>
      <span>${escapeHtml(row.phase_hint)}</span>
      <span><small>${escapeHtml(row.file)}</small></span>
      <span><small>${escapeHtml(row.related_skills || "")}</small></span>
    </div>
  `).join("");
  return head + body;
}

async function refreshSkillRegistry() {
  const summaryRoot = document.querySelector("#skill-registry-summary");
  const tableRoot = document.querySelector("#skill-registry-table");
  const downloadLink = document.querySelector("#skill-registry-download");
  if (!summaryRoot && !tableRoot && !downloadLink) return;

  const data = await getJson("/api/skills");
  const summary = data.summary || {};
  if (summaryRoot) {
    summaryRoot.innerHTML = [
      avatarSummaryCard("Active skills", summary.active || 0, "docs/*_SKILL.md"),
      avatarSummaryCard("Missing refs", summary.missing || 0, "referenced but not present"),
      avatarSummaryCard("Registry", "CSV", summary.registry || ""),
      avatarSummaryCard("Index", "MD", summary.index || ""),
    ].join("");
  }
  if (tableRoot) {
    tableRoot.innerHTML = skillRegistryTable(data.rows || []);
  }
  if (downloadLink && summary.registry) {
    downloadLink.href = mediaUrl(summary.registry);
  }
}

function appendAgentMessage(role, text) {
  const log = document.querySelector("#agent-log");
  if (!log) return;
  const node = document.createElement("div");
  node.className = `agent-message ${role}`;
  node.textContent = text;
  log.appendChild(node);
  log.scrollTop = log.scrollHeight;
}

async function sendAgentMessage(message) {
  const clean = String(message || "").trim();
  if (!clean) return;
  appendAgentMessage("user", clean);
  markRealtimeWorking(clean);
  const response = await getJson("/api/agent/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: clean }),
  });
  appendAgentMessage("assistant", response.reply || "");
  await refreshRealtimeControl().catch(() => {});
  await refreshDashboard().catch(() => {});
}

function markRealtimeWorking(message) {
  const summaryRoot = document.querySelector("#realtime-summary");
  const chartsRoot = document.querySelector("#realtime-charts");
  const stagesRoot = document.querySelector("#realtime-stages");
  if (summaryRoot) {
    summaryRoot.innerHTML = [
      avatarSummaryCard("Mode", "processing", message),
      avatarSummaryCard("Status", "running", "sto raccogliendo dati"),
      avatarSummaryCard("Progress", "35%", "ciclo agente"),
      avatarSummaryCard("Poll", "live", "verifica in corso"),
    ].join("");
  }
  if (chartsRoot) {
    chartsRoot.innerHTML = [
      donutCard("Agent loop", 35, "Elaborazione richiesta", "running"),
      `<div class="chart-panel">${progressChart([
        { stage: "Dialogo", status: "running", progress: 100, signal: "richiesta ricevuta" },
        { stage: "Memoria e fasi", status: "running", progress: 45, signal: "raccolta contesto" },
        { stage: "Network e API", status: "manual_pending", progress: 20, signal: "se serve verifico" },
        { stage: "Prossima azione", status: "pending", progress: 10, signal: "selezione in corso" },
      ])}</div>`,
    ].join("");
  }
  if (stagesRoot) {
    stagesRoot.innerHTML = "Sto elaborando la richiesta e preparando la prossima azione.";
  }
}

async function refreshAgentProfile() {
  const root = document.querySelector("#agent-profile");
  const modesRoot = document.querySelector("#agent-modes");
  if (!root && !modesRoot) return;
  const profile = await getJson("/api/agent/profile");
  if (root) {
    root.innerHTML = `
    <div class="api-pill ${profile.status === "avatar_ready" ? "configured" : "missing"}">
      <strong>${escapeHtml(profile.name)}</strong>
      <span>${escapeHtml(profile.status)}</span>
      <small>${escapeHtml(profile.voice)} · ${escapeHtml(profile.channels)}</small>
    </div>
  `;
  }
  if (modesRoot) {
    modesRoot.innerHTML = (profile.modes || []).map((mode) => `
      <div class="mode-card">
        <strong>${escapeHtml(mode.mode)}</strong>
        <p>${escapeHtml(mode.use)}</p>
        <span>${escapeHtml(mode.customer_safe)}</span>
      </div>
    `).join("");
  }
}

async function refreshRealtimeControl() {
  const summaryRoot = document.querySelector("#realtime-summary");
  const chartsRoot = document.querySelector("#realtime-charts");
  const stagesRoot = document.querySelector("#realtime-stages");
  const updatedRoot = document.querySelector("#realtime-updated");
  if (!summaryRoot && !chartsRoot && !stagesRoot && !updatedRoot) return;
  const data = await getJson("/api/realtime-control");
  const summary = data.summary || {};
  const stages = data.stages || [];
  if (summaryRoot) {
    summaryRoot.innerHTML = [
      avatarSummaryCard("Mode", summary.mode || "realtime", summary.current_event || ""),
      avatarSummaryCard("Status", summary.status || "ready", summary.next_action || ""),
      avatarSummaryCard("Progress", `${summary.progress || 0}%`, "ciclo agente"),
      avatarSummaryCard("Poll", `${summary.poll_seconds || 8}s`, "live leggero"),
    ].join("");
  }
  if (chartsRoot) {
    chartsRoot.innerHTML = [
      donutCard("Agent loop", summary.progress || 0, summary.next_action || "Agente pronto", summary.status || "ready"),
      `<div class="chart-panel">${progressChart(stages)}</div>`,
    ].join("");
  }
  if (stagesRoot) {
    stagesRoot.innerHTML = simpleRowsTable(stages, [
      { key: "stage", label: "Stage", render: (row) => `<strong>${escapeHtml(row.stage)}</strong><br><small>${escapeHtml(row.signal)}</small>` },
      { key: "status", label: "Status", render: (row) => `<span class="status-${escapeHtml(row.status)}">${escapeHtml(row.status)}</span><br><small>${escapeHtml(row.progress)}%</small>` },
      { key: "detail", label: "Detail" },
    ], "realtime-row");
  }
  if (updatedRoot) {
    updatedRoot.textContent = `Aggiornato ${summary.updated_at || ""}`;
  }
}

function masterActionsTable(rows) {
  if (!rows.length) return "No master actions yet.";
  const head = `
    <div class="action-row table-head">
      <span>Priority</span>
      <span>Action</span>
      <span>Status</span>
      <span>Why</span>
      <span>Do</span>
      <span>Verify</span>
    </div>
  `;
  const body = rows.map((row) => `
    <div class="action-row">
      <span>${escapeHtml(row.priority)}</span>
      <span><strong>${escapeHtml(row.title)}</strong><br><small>${escapeHtml(row.area)}</small></span>
      <span><span class="status-${escapeHtml(row.status)}">${escapeHtml(row.status)}</span><br><small>${escapeHtml(row.memory_status || "")}</small></span>
      <span>${escapeHtml(row.why)}</span>
      <span>${escapeHtml(row.do)}</span>
      <span><button class="button secondary small" data-verify-action="${escapeHtml(row.id)}">Verifica</button></span>
    </div>
  `).join("");
  return head + body;
}

async function refreshMasterActions() {
  const nextRoot = document.querySelector("#master-next-action");
  const summaryRoot = document.querySelector("#master-actions-summary");
  const tableRoot = document.querySelector("#master-actions-table");
  const downloadLink = document.querySelector("#master-actions-download");
  if (!nextRoot && !summaryRoot && !tableRoot && !downloadLink) return;
  const data = await getJson("/api/master-actions");
  const summary = data.summary || {};
  const next = data.next_action || {};
  if (nextRoot) {
    nextRoot.innerHTML = `
      <strong>Prima cosa: ${escapeHtml(next.title || "Verifica Google Merchant")}</strong>
      <p>${escapeHtml(next.why || "")}</p>
      <div class="phase-meta">${escapeHtml(next.do || "")}</div>
    `;
  }
  if (summaryRoot) {
    summaryRoot.innerHTML = [
      avatarSummaryCard("Pass", summary.pass || 0, "azioni verdi"),
      avatarSummaryCard("Needs fix", summary.needs_fix || 0, "da lavorare"),
      avatarSummaryCard("Blocked", summary.blocked || 0, "non procedere"),
      avatarSummaryCard("Memory", "ON", summary.memory || ""),
    ].join("");
  }
  if (tableRoot) {
    tableRoot.innerHTML = masterActionsTable(data.actions || []);
  }
  if (downloadLink && summary.queue) {
    downloadLink.href = mediaUrl(summary.queue);
  }
}

function weeklyGoalsTable(rows) {
  if (!rows.length) return "No weekly goals yet.";
  const head = `
    <div class="weekly-row table-head">
      <span>Area</span>
      <span>Status</span>
      <span>Minimum</span>
      <span>Target</span>
      <span>Evidence</span>
    </div>
  `;
  const body = rows.map((row) => `
    <div class="weekly-row">
      <span><strong>${escapeHtml(row.area)}</strong><br><small>${escapeHtml(row.week)}</small></span>
      <span><span class="status-${escapeHtml(row.status)}">${escapeHtml(row.status)}</span></span>
      <span>${escapeHtml(row.minimum)}</span>
      <span>${escapeHtml(row.target)}</span>
      <span>${escapeHtml(row.evidence)}</span>
    </div>
  `).join("");
  return head + body;
}

async function refreshWeeklyGoals() {
  const summaryRoot = document.querySelector("#weekly-goals-summary");
  const tableRoot = document.querySelector("#weekly-goals-table");
  const downloadLink = document.querySelector("#weekly-goals-download");
  if (!summaryRoot && !tableRoot && !downloadLink) return;
  const data = await getJson("/api/weekly-goals");
  const summary = data.summary || {};
  if (summaryRoot) {
    summaryRoot.innerHTML = [
      avatarSummaryCard("Week", summary.week || "-", "minimum checks"),
      avatarSummaryCard("Pass", summary.pass || 0, `${summary.total || 0} total`),
      avatarSummaryCard("Attention", summary.needs_attention || 0, "da verificare"),
      avatarSummaryCard("Routine", "ON", summary.sheet || ""),
    ].join("");
  }
  if (tableRoot) {
    tableRoot.innerHTML = weeklyGoalsTable(data.rows || []);
  }
  if (downloadLink && summary.sheet) {
    downloadLink.href = mediaUrl(summary.sheet);
  }
}

function dailySourcesTable(rows) {
  if (!rows.length) return "No daily sources yet.";
  const head = `
    <div class="daily-row table-head">
      <span>Source</span>
      <span>Status</span>
      <span>HTTP</span>
      <span>Purpose</span>
      <span>URL</span>
    </div>
  `;
  const body = rows.map((row) => `
    <div class="daily-row">
      <span><strong>${escapeHtml(row.name)}</strong><br><small>${escapeHtml(row.kind)}</small></span>
      <span><span class="status-${escapeHtml(row.status)}">${escapeHtml(row.status)}</span><br><small>${escapeHtml(row.error || `${row.ms || ""} ms`)}</small></span>
      <span>${escapeHtml(row.http_status || "-")}</span>
      <span>${escapeHtml(row.purpose)}</span>
      <span><small>${escapeHtml(row.url)}</small></span>
    </div>
  `).join("");
  return head + body;
}

async function refreshDailyWebUpdate() {
  const summaryRoot = document.querySelector("#daily-web-update-summary");
  const nextRoot = document.querySelector("#daily-web-update-next");
  const tableRoot = document.querySelector("#daily-web-update-table");
  const downloadLink = document.querySelector("#daily-web-update-download");
  if (!summaryRoot && !nextRoot && !tableRoot && !downloadLink) return;
  const data = await getJson("/api/daily-web-update");
  const summary = data.summary || {};
  const next = data.next_action || {};
  if (summaryRoot) {
    summaryRoot.innerHTML = [
      avatarSummaryCard("Mode", summary.mode || "local_snapshot", summary.checked_at || ""),
      avatarSummaryCard("Pass", summary.pass || 0, `${summary.sources || 0} sources`),
      avatarSummaryCard("Needs fix", summary.needs_fix || 0, "live checks"),
      avatarSummaryCard("Errors", summary.errors || 0, "network/tool"),
    ].join("");
  }
  if (nextRoot) {
    nextRoot.innerHTML = `
      <strong>Prossima azione daily: ${escapeHtml(next.title || summary.next_action || "Verifica Google Merchant")}</strong>
      <p>${escapeHtml(next.why || "Usa la coda Azioni Master per decidere il passo successivo.")}</p>
      <div class="phase-meta">${escapeHtml(next.do || "")}</div>
    `;
  }
  if (tableRoot) {
    tableRoot.innerHTML = dailySourcesTable(data.sources || []);
  }
  if (downloadLink && summary.sheet) {
    downloadLink.href = mediaUrl(summary.sheet);
  }
}

function simpleRowsTable(rows, columns, className) {
  if (!rows.length) return "No rows yet.";
  const head = `
    <div class="${className} table-head">
      ${columns.map((column) => `<span>${escapeHtml(column.label)}</span>`).join("")}
    </div>
  `;
  const body = rows.map((row) => `
    <div class="${className}">
      ${columns.map((column) => `<span>${column.render ? column.render(row) : escapeHtml(row[column.key] ?? "")}</span>`).join("")}
    </div>
  `).join("");
  return head + body;
}

async function refreshAlwaysOn() {
  const summaryRoot = document.querySelector("#always-on-summary");
  const loopsRoot = document.querySelector("#always-on-loops");
  const driveRoot = document.querySelector("#always-on-drive");
  const downloadLink = document.querySelector("#always-on-download");
  if (!summaryRoot && !loopsRoot && !driveRoot && !downloadLink) return;
  const data = await getJson("/api/always-on");
  const summary = data.summary || {};
  if (summaryRoot) {
    summaryRoot.innerHTML = [
      avatarSummaryCard("Status", summary.status || "watching", summary.mode || ""),
      avatarSummaryCard("Autonomy", summary.autonomy || "supervised", "approval gates active"),
      avatarSummaryCard("Blockers", summary.blockers || 0, "Google/actions"),
      avatarSummaryCard("Drive ready", summary.drive_ready || 0, summary.drive_manifest || ""),
    ].join("");
  }
  if (loopsRoot) {
    loopsRoot.innerHTML = simpleRowsTable(data.loops || [], [
      { key: "loop", label: "Loop", render: (row) => `<strong>${escapeHtml(row.loop)}</strong><br><small>${escapeHtml(row.cadence)}</small>` },
      { key: "status", label: "Status" },
      { key: "approval", label: "Approval" },
    ], "always-row");
  }
  if (driveRoot) {
    driveRoot.innerHTML = simpleRowsTable(data.drive || [], [
      { key: "artifact", label: "Artifact", render: (row) => `<strong>${escapeHtml(row.artifact)}</strong><br><small>${escapeHtml(row.path)}</small>` },
      { key: "exists", label: "Exists" },
      { key: "drive_status", label: "Drive" },
    ], "drive-row");
  }
  if (downloadLink && summary.drive_manifest) {
    downloadLink.href = mediaUrl(summary.drive_manifest);
  }
}

async function refreshAgentOS() {
  const summaryRoot = document.querySelector("#agent-os-summary");
  const layersRoot = document.querySelector("#agent-os-layers");
  const tableRoot = document.querySelector("#agent-os-table");
  const downloadLink = document.querySelector("#agent-os-download");
  if (!summaryRoot && !layersRoot && !tableRoot && !downloadLink) return;
  const data = await getJson("/api/agent-os");
  const summary = data.summary || {};
  if (summaryRoot) {
    summaryRoot.innerHTML = [
      avatarSummaryCard("Ready", summary.ready || 0, `${summary.total || 0} connectors`),
      avatarSummaryCard("Partial", summary.partial || 0, "complete credentials"),
      avatarSummaryCard("Blocked", summary.blocked || 0, "compliance gate"),
      avatarSummaryCard("Autonomy", summary.autonomy || "supervised", "approval required for risk"),
    ].join("");
  }
  if (layersRoot) {
    layersRoot.innerHTML = (data.layers || []).map((layer) => `
      <div class="mode-card">
        <strong>${escapeHtml(layer.layer)}</strong>
        <p>${escapeHtml(layer.purpose)}</p>
      </div>
    `).join("");
  }
  if (tableRoot) {
    tableRoot.innerHTML = simpleRowsTable(data.connectors || [], [
      { key: "name", label: "Connector", render: (row) => `<strong>${escapeHtml(row.name)}</strong><br><small>${escapeHtml(row.domain)}</small>` },
      { key: "status", label: "Status", render: (row) => `<span class="status-${escapeHtml(row.status)}">${escapeHtml(row.status)}</span><br><small>${escapeHtml(row.configured)}/${escapeHtml(row.total_env)}</small>` },
      { key: "autonomy", label: "Autonomy" },
      { key: "risk", label: "Risk" },
      { key: "purpose", label: "Purpose" },
      { key: "next_action", label: "Next" },
    ], "connector-row");
  }
  if (downloadLink && summary.sheet) {
    downloadLink.href = mediaUrl(summary.sheet);
  }
}

async function refreshOpenAIAlliance() {
  const summaryRoot = document.querySelector("#openai-alliance-summary");
  const tableRoot = document.querySelector("#openai-alliance-table");
  const guardsRoot = document.querySelector("#openai-alliance-guards");
  const downloadLink = document.querySelector("#openai-alliance-download");
  if (!summaryRoot && !tableRoot && !guardsRoot && !downloadLink) return;
  const data = await getJson("/api/openai-alliance");
  const summary = data.summary || {};
  if (summaryRoot) {
    summaryRoot.innerHTML = [
      avatarSummaryCard("Status", summary.status || "planned", "aligned to BKS"),
      avatarSummaryCard("Ready", summary.ready || 0, `${summary.capabilities || 0} capabilities`),
      avatarSummaryCard("Project", summary.project_link || "env_pending", "ChatGPT Project"),
      avatarSummaryCard("Model", summary.default_model || "project_default", "BKS decides"),
    ].join("");
  }
  if (tableRoot) {
    tableRoot.innerHTML = simpleRowsTable(data.capabilities || [], [
      { key: "capability", label: "Capability", render: (row) => `<strong>${escapeHtml(row.capability)}</strong><br><small>${escapeHtml(row.area)}</small>` },
      { key: "status", label: "Status", render: (row) => `<span class="status-${escapeHtml(row.status)}">${escapeHtml(row.status)}</span><br><small>${escapeHtml(row.configured)}</small>` },
      { key: "autonomy", label: "Autonomy" },
      { key: "use", label: "Use" },
      { key: "agent_rule", label: "BKS rule" },
    ], "openai-row");
  }
  if (guardsRoot) {
    guardsRoot.innerHTML = (data.guardrails || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("");
  }
  if (downloadLink && summary.sheet) {
    downloadLink.href = mediaUrl(summary.sheet);
  }
}

async function refreshCanvaConnectors() {
  const summaryRoot = document.querySelector("#canva-connectors-summary");
  const tableRoot = document.querySelector("#canva-connectors-table");
  const workflowsRoot = document.querySelector("#canva-workflows");
  const downloadLink = document.querySelector("#canva-connectors-download");
  if (!summaryRoot && !tableRoot && !workflowsRoot && !downloadLink) return;
  const data = await getJson("/api/canva-connectors");
  const summary = data.summary || {};
  if (summaryRoot) {
    summaryRoot.innerHTML = [
      avatarSummaryCard("Status", summary.status || "connector_available", "Canva connector"),
      avatarSummaryCard("Tool groups", summary.groups || 0, "read/write/review"),
      avatarSummaryCard("Workflows", summary.workflows || 0, "social + catalog"),
      avatarSummaryCard("Autonomy", "Draft", summary.autonomy || "supervised"),
    ].join("");
  }
  if (tableRoot) {
    tableRoot.innerHTML = simpleRowsTable(data.tool_groups || [], [
      { key: "group", label: "Group", render: (row) => `<strong>${escapeHtml(row.group)}</strong><br><small>${escapeHtml(row.autonomy)} · ${escapeHtml(row.risk)}</small>` },
      { key: "status", label: "Status", render: (row) => `<span class="status-${escapeHtml(row.status)}">${escapeHtml(row.status)}</span>` },
      { key: "tools", label: "Tools" },
      { key: "use", label: "Use" },
      { key: "agent_rule", label: "Rule" },
    ], "canva-row");
  }
  if (workflowsRoot) {
    workflowsRoot.innerHTML = (data.workflows || []).map((workflow) => `
      <div class="mode-card">
        <strong>${escapeHtml(workflow.workflow)}</strong>
        <p>${escapeHtml(workflow.sequence)}</p>
        <span>${escapeHtml(workflow.output)}</span>
      </div>
    `).join("");
  }
  if (downloadLink && summary.sheet) {
    downloadLink.href = mediaUrl(summary.sheet);
  }
}

async function refreshHyperFramesConnectors() {
  const summaryRoot = document.querySelector("#hyperframes-connectors-summary");
  const tableRoot = document.querySelector("#hyperframes-connectors-table");
  const workflowsRoot = document.querySelector("#hyperframes-workflows");
  const downloadLink = document.querySelector("#hyperframes-connectors-download");
  if (!summaryRoot && !tableRoot && !workflowsRoot && !downloadLink) return;
  const data = await getJson("/api/hyperframes-connectors");
  const summary = data.summary || {};
  if (summaryRoot) {
    summaryRoot.innerHTML = [
      avatarSummaryCard("Status", summary.status || "connector_available", "HTML to video"),
      avatarSummaryCard("Tools", summary.tools || 0, "compose/render/status"),
      avatarSummaryCard("Format", summary.default_format || "1080x1920", "default"),
      avatarSummaryCard("Autonomy", "Render draft", summary.autonomy || "approval"),
    ].join("");
  }
  if (tableRoot) {
    tableRoot.innerHTML = simpleRowsTable(data.tools || [], [
      { key: "tool", label: "Tool", render: (row) => `<strong>${escapeHtml(row.tool)}</strong><br><small>${escapeHtml(row.mode)}</small>` },
      { key: "status", label: "Status", render: (row) => `<span class="status-${escapeHtml(row.status)}">${escapeHtml(row.status)}</span>` },
      { key: "risk", label: "Risk" },
      { key: "use", label: "Use" },
      { key: "agent_rule", label: "Rule" },
    ], "hyperframes-row");
  }
  if (workflowsRoot) {
    workflowsRoot.innerHTML = (data.workflows || []).map((workflow) => `
      <div class="mode-card">
        <strong>${escapeHtml(workflow.workflow)}</strong>
        <p>${escapeHtml(workflow.sequence)}</p>
        <span>${escapeHtml(workflow.output)}</span>
      </div>
    `).join("");
  }
  if (downloadLink && summary.sheet) {
    downloadLink.href = mediaUrl(summary.sheet);
  }
}

async function refreshGoogleTrust() {
  const summaryRoot = document.querySelector("#google-trust-summary");
  const tableRoot = document.querySelector("#google-trust-table");
  const downloadLink = document.querySelector("#google-trust-download");
  if (!summaryRoot && !tableRoot && !downloadLink) return;
  const data = await getJson("/api/google-trust");
  const summary = data.summary || {};
  if (summaryRoot) {
    summaryRoot.innerHTML = [
      avatarSummaryCard("Pass", summary.pass || 0, `${summary.total || 0} needs`),
      avatarSummaryCard("Needs fix", summary.needs_fix || 0, "before growth"),
      avatarSummaryCard("Manual", summary.manual_pending || 0, "checkout/GMC"),
      avatarSummaryCard("Gate", "Google", "central trust authority"),
    ].join("");
  }
  if (tableRoot) {
    tableRoot.innerHTML = simpleRowsTable(data.rows || [], [
      { key: "need", label: "Need", render: (row) => `<strong>${escapeHtml(row.need)}</strong><br><small>${escapeHtml(row.current_evidence)}</small>` },
      { key: "status", label: "Status", render: (row) => `<span class="status-${escapeHtml(row.status)}">${escapeHtml(row.status)}</span>` },
      { key: "google_question", label: "Google asks" },
      { key: "evidence", label: "Evidence" },
      { key: "agent_rule", label: "Agent rule" },
    ], "trust-contract-row");
  }
  if (downloadLink && summary.sheet) {
    downloadLink.href = mediaUrl(summary.sheet);
  }
}

async function refreshPayments() {
  const summaryRoot = document.querySelector("#payments-summary");
  const tableRoot = document.querySelector("#payments-table");
  const downloadLink = document.querySelector("#payments-download");
  if (!summaryRoot && !tableRoot && !downloadLink) return;
  const data = await getJson("/api/payments");
  const summary = data.summary || {};
  if (summaryRoot) {
    summaryRoot.innerHTML = [
      avatarSummaryCard("Active", summary.active || 0, "visible/configured"),
      avatarSummaryCard("Bitcoin", summary.bitcoin || "planned", summary.provider || ""),
      avatarSummaryCard("Planned", summary.planned || 0, "future methods"),
      avatarSummaryCard("Skill", data.agent_skill || "payments", "agent competence"),
    ].join("");
  }
  if (tableRoot) {
    tableRoot.innerHTML = simpleRowsTable(data.rows || [], [
      { key: "method", label: "Method", render: (row) => `<strong>${escapeHtml(row.method)}</strong><br><small>${escapeHtml(row.provider)}</small>` },
      { key: "status", label: "Status", render: (row) => `<span class="status-${escapeHtml(row.status)}">${escapeHtml(row.status)}</span>` },
      { key: "customer_message", label: "Customer message" },
      { key: "risk", label: "Risk" },
      { key: "verification", label: "Verify" },
    ], "payment-row");
  }
  if (downloadLink && summary.sheet) {
    downloadLink.href = mediaUrl(summary.sheet);
  }
}

async function refreshMarketingLogic() {
  const summaryRoot = document.querySelector("#marketing-logic-summary");
  const tableRoot = document.querySelector("#marketing-logic-table");
  const downloadLink = document.querySelector("#marketing-logic-download");
  if (!summaryRoot && !tableRoot && !downloadLink) return;
  const data = await getJson("/api/marketing-logic");
  const summary = data.summary || {};
  if (summaryRoot) {
    summaryRoot.innerHTML = [
      avatarSummaryCard("Best", summary.best_logic || "-", "top playbook"),
      avatarSummaryCard("Do now", summary.do_now || 0, "apply first"),
      avatarSummaryCard("Prepare", summary.prepare_only || 0, "after trust"),
      avatarSummaryCard("Playbooks", summary.playbooks || 0, "market logic"),
    ].join("");
  }
  if (tableRoot) {
    tableRoot.innerHTML = simpleRowsTable(data.rows || [], [
      { key: "logic", label: "Logic", render: (row) => `<strong>${escapeHtml(row.logic)}</strong><br><small>${escapeHtml(row.source)}</small>` },
      { key: "readiness", label: "Ready", render: (row) => `<span class="status-${escapeHtml(row.readiness)}">${escapeHtml(row.readiness)}</span><br><small>${escapeHtml(row.quality_fit_score)}</small>` },
      { key: "best_for_bks", label: "BKS use" },
      { key: "product_quality_need", label: "Quality need" },
      { key: "first_action", label: "First action" },
    ], "marketing-logic-row");
  }
  if (downloadLink && summary.sheet) {
    downloadLink.href = mediaUrl(summary.sheet);
  }
}

async function refreshKnowledgeDB() {
  const summaryRoot = document.querySelector("#knowledge-db-summary");
  const tableRoot = document.querySelector("#knowledge-db-table");
  if (!summaryRoot && !tableRoot) return;
  const data = await getJson("/api/knowledge?limit=40");
  const rows = data.rows || [];
  const areas = new Set(rows.map((row) => row.area));
  if (summaryRoot) {
    summaryRoot.innerHTML = [
      avatarSummaryCard("Entries", rows.length, "latest rows"),
      avatarSummaryCard("Areas", areas.size, "indexed domains"),
      avatarSummaryCard("Database", "SQLite", "agent_knowledge"),
      avatarSummaryCard("Mode", "Evidence", "answers from stored data"),
    ].join("");
  }
  if (tableRoot) {
    tableRoot.innerHTML = simpleRowsTable(rows, [
      { key: "area", label: "Area", render: (row) => `<strong>${escapeHtml(row.area)}</strong><br><small>#${escapeHtml(row.id)}</small>` },
      { key: "title", label: "Title" },
      { key: "status", label: "Status", render: (row) => `<span class="status-${escapeHtml(row.status)}">${escapeHtml(row.status)}</span>` },
      { key: "evidence", label: "Evidence" },
      { key: "created_at", label: "Created" },
    ], "knowledge-row");
  }
}

async function refreshAgentRoutine() {
  const summaryRoot = document.querySelector("#agent-routine-summary");
  const nextRoot = document.querySelector("#agent-routine-next");
  const tableRoot = document.querySelector("#agent-routine-table");
  const costRoot = document.querySelector("#api-cost-guard-table");
  const routineLink = document.querySelector("#agent-routine-download");
  const costLink = document.querySelector("#api-cost-guard-download");
  if (!summaryRoot && !nextRoot && !tableRoot && !costRoot && !routineLink && !costLink) return;
  const data = await getJson("/api/agent-routine");
  const summary = data.summary || {};
  const next = data.next_step || {};
  if (summaryRoot) {
    summaryRoot.innerHTML = [
      avatarSummaryCard("Steps", summary.steps || 0, "routine totale"),
      avatarSummaryCard("Ready", summary.ready || 0, "automatizzabili"),
      avatarSummaryCard("Attention", summary.attention || 0, "da controllare"),
      avatarSummaryCard("Next", summary.next_step || "-", "azione suggerita"),
    ].join("");
  }
  if (nextRoot) {
    nextRoot.innerHTML = `
      <strong>Prossimo step: ${escapeHtml(next.step || summary.next_step || "-")}</strong>
      <p>${escapeHtml(next.output || "Aggiorna il sistema, suggerisci una azione e verifica l'esito.")}</p>
      <div class="phase-meta">${escapeHtml(next.cost_level || "")} · ${escapeHtml(next.approval || "")}</div>
    `;
  }
  if (tableRoot) {
    tableRoot.innerHTML = simpleRowsTable(data.rows || [], [
      { key: "priority", label: "#" },
      { key: "step", label: "Step", render: (row) => `<strong>${escapeHtml(row.step)}</strong><br><small>${escapeHtml(row.inputs)}</small>` },
      { key: "status", label: "Status", render: (row) => `<span class="status-${escapeHtml(row.status)}">${escapeHtml(row.status)}</span>` },
      { key: "cadence", label: "Cadence" },
      { key: "cost_level", label: "Cost" },
      { key: "approval", label: "Approval" },
    ], "routine-row");
  }
  if (costRoot) {
    costRoot.innerHTML = simpleRowsTable(data.cost_guards || [], [
      { key: "api", label: "API", render: (row) => `<strong>${escapeHtml(row.api)}</strong><br><small>${escapeHtml(row.cost)}</small>` },
      { key: "rule", label: "Rule" },
      { key: "approval", label: "Approval" },
    ], "cost-row");
  }
  if (routineLink && summary.routine_sheet) routineLink.href = mediaUrl(summary.routine_sheet);
  if (costLink && summary.cost_sheet) costLink.href = mediaUrl(summary.cost_sheet);
}

async function refreshThemeAIAssistant() {
  const summaryRoot = document.querySelector("#theme-ai-assistant-summary");
  const tableRoot = document.querySelector("#theme-ai-assistant-table");
  const downloadLink = document.querySelector("#theme-ai-assistant-download");
  if (!summaryRoot && !tableRoot && !downloadLink) return;
  const data = await getJson("/api/theme-ai-assistant");
  const summary = data.summary || {};
  if (summaryRoot) {
    summaryRoot.innerHTML = [
      avatarSummaryCard("Status", summary.status || "-", "Shopify widget"),
      avatarSummaryCard("Google-safe", summary.google_safe || "-", "trust note"),
      avatarSummaryCard("Theme enabled", summary.theme_enabled ? "yes" : "no", "disabled by default"),
      avatarSummaryCard("Customer chat", summary.customer_chat_enabled ? "yes" : "no", "approval gate"),
    ].join("");
  }
  if (tableRoot) {
    tableRoot.innerHTML = simpleRowsTable(data.checks || [], [
      { key: "check", label: "Check", render: (row) => `<strong>${escapeHtml(row.check)}</strong>` },
      { key: "status", label: "Status", render: (row) => `<span class="status-${escapeHtml(row.status)}">${escapeHtml(row.status)}</span>` },
      { key: "detail", label: "Detail" },
    ], "assistant-row");
  }
  if (downloadLink && summary.google_note) downloadLink.href = mediaUrl(summary.google_note);
}

async function refreshNetworkMonitor(live = false) {
  const summaryRoot = document.querySelector("#network-monitor-summary");
  const chartsRoot = document.querySelector("#network-monitor-charts");
  const dnsRoot = document.querySelector("#network-dns-table");
  const emailRoot = document.querySelector("#network-email-table");
  const endpointRoot = document.querySelector("#network-endpoint-table");
  const suffixRoot = document.querySelector("#network-suffix-table");
  const downloadLink = document.querySelector("#network-monitor-download");
  if (!summaryRoot && !chartsRoot && !dnsRoot && !emailRoot && !endpointRoot && !suffixRoot && !downloadLink) return;
  const data = await getJson(`/api/network-monitor${live ? "?live=1" : ""}`);
  const summary = data.summary || {};
  if (summaryRoot) {
    summaryRoot.innerHTML = [
      avatarSummaryCard("Domain", summary.domain || "bakabo.club", summary.live ? "live check" : "snapshot"),
      avatarSummaryCard("DNS", `${summary.dns_pass || 0} pass`, `${summary.dns_attention || 0} attention`),
      avatarSummaryCard("Email/DSN", `${summary.email_pass || 0} pass`, `${summary.email_attention || 0} attention`),
      avatarSummaryCard("Endpoints", `${summary.endpoints_pass || 0} pass`, `${summary.endpoints_attention || 0} attention`),
    ].join("");
  }
  if (chartsRoot) {
    const dnsTotal = Number(summary.dns_pass || 0) + Number(summary.dns_attention || 0);
    const emailTotal = Number(summary.email_pass || 0) + Number(summary.email_attention || 0);
    const endpointTotal = Number(summary.endpoints_pass || 0) + Number(summary.endpoints_attention || 0);
    const dnsPercent = dnsTotal ? Math.round((Number(summary.dns_pass || 0) / dnsTotal) * 100) : 0;
    const emailPercent = emailTotal ? Math.round((Number(summary.email_pass || 0) / emailTotal) * 100) : 0;
    const endpointPercent = endpointTotal ? Math.round((Number(summary.endpoints_pass || 0) / endpointTotal) * 100) : 0;
    chartsRoot.innerHTML = [
      donutCard("DNS", dnsPercent, `${summary.dns_attention || 0} attention`, dnsPercent >= 90 ? "pass" : "needs_review"),
      donutCard("Email/DSN", emailPercent, `${summary.email_attention || 0} attention`, emailPercent >= 90 ? "pass" : "needs_fix"),
      donutCard("Endpoint", endpointPercent, `${summary.endpoints_attention || 0} attention`, endpointPercent >= 90 ? "pass" : "needs_review"),
    ].join("");
  }
  if (dnsRoot) {
    dnsRoot.innerHTML = simpleRowsTable(data.dns || [], [
      { key: "check", label: "Check", render: (row) => `<strong>${escapeHtml(row.check)}</strong><br><small>${escapeHtml(row.name)}</small>` },
      { key: "status", label: "Status", render: (row) => `<span class="status-${escapeHtml(row.status)}">${escapeHtml(row.status)}</span><br><small>${escapeHtml(row.ms || "")} ms</small>` },
      { key: "value", label: "Value" },
      { key: "next_action", label: "Next" },
    ], "network-row");
  }
  if (emailRoot) {
    emailRoot.innerHTML = simpleRowsTable(data.email || [], [
      { key: "signal", label: "Signal", render: (row) => `<strong>${escapeHtml(row.signal)}</strong><br><small>${escapeHtml(row.evidence)}</small>` },
      { key: "status", label: "Status", render: (row) => `<span class="status-${escapeHtml(row.status)}">${escapeHtml(row.status)}</span>` },
      { key: "next_action", label: "Next" },
    ], "email-signal-row");
  }
  if (endpointRoot) {
    endpointRoot.innerHTML = simpleRowsTable(data.endpoints || [], [
      { key: "endpoint", label: "Endpoint", render: (row) => `<strong>${escapeHtml(row.endpoint)}</strong><br><small>${escapeHtml(row.url)}</small>` },
      { key: "status", label: "Status", render: (row) => `<span class="status-${escapeHtml(row.status)}">${escapeHtml(row.status)}</span><br><small>${escapeHtml(row.http_status || "")} ${escapeHtml(row.ms || "")} ms</small>` },
      { key: "purpose", label: "Purpose" },
    ], "endpoint-row");
  }
  if (suffixRoot) {
    suffixRoot.innerHTML = simpleRowsTable(data.suffixes || [], [
      { key: "suffix", label: "Suffix", render: (row) => `<strong>${escapeHtml(row.suffix)}</strong><br><small>${escapeHtml(row.status)}</small>` },
      { key: "purpose", label: "Purpose" },
      { key: "rule", label: "Rule" },
    ], "suffix-row");
  }
  if (downloadLink && summary.report) downloadLink.href = mediaUrl(summary.report);
}

async function refreshOfficialInbox() {
  const summaryRoot = document.querySelector("#official-inbox-summary");
  const statusRoot = document.querySelector("#official-inbox-status-table");
  const categoryRoot = document.querySelector("#official-inbox-category-table");
  const transparencyRoot = document.querySelector("#official-inbox-transparency-table");
  const downloadLink = document.querySelector("#official-inbox-download");
  if (!summaryRoot && !statusRoot && !categoryRoot && !transparencyRoot && !downloadLink) return;
  const data = await getJson("/api/official-inbox");
  const summary = data.summary || {};
  if (summaryRoot) {
    summaryRoot.innerHTML = [
      avatarSummaryCard("Email", summary.official_email || "crew@bakabo.club", summary.status || ""),
      avatarSummaryCard("Configured", summary.configured || 0, "blocks ready"),
      avatarSummaryCard("Attention", summary.needs_attention || 0, "needs setup"),
      avatarSummaryCard("Tracking", summary.tracking_mode || "transparent", "consent-aware"),
    ].join("");
  }
  if (statusRoot) {
    statusRoot.innerHTML = simpleRowsTable(data.status_rows || [], [
      { key: "area", label: "Area", render: (row) => `<strong>${escapeHtml(row.area)}</strong><br><small>${escapeHtml(row.value)}</small>` },
      { key: "status", label: "Status", render: (row) => `<span class="status-${escapeHtml(row.status)}">${escapeHtml(row.status)}</span>` },
      { key: "next_action", label: "Next" },
    ], "inbox-row");
  }
  if (categoryRoot) {
    categoryRoot.innerHTML = simpleRowsTable(data.categories || [], [
      { key: "category", label: "Category", render: (row) => `<strong>${escapeHtml(row.category)}</strong><br><small>${escapeHtml(row.sla)}</small>` },
      { key: "approval", label: "Approval" },
      { key: "agent_action", label: "Agent action" },
    ], "inbox-row");
  }
  if (transparencyRoot) {
    transparencyRoot.innerHTML = simpleRowsTable(data.transparency || [], [
      { key: "rule", label: "Rule", render: (row) => `<strong>${escapeHtml(row.rule)}</strong><br><small>${escapeHtml(row.source)}</small>` },
      { key: "meaning", label: "Meaning" },
    ], "transparency-row");
  }
  if (downloadLink && summary.sheet) downloadLink.href = mediaUrl(summary.sheet);
}

async function refreshSocialCampaigns() {
  const summaryRoot = document.querySelector("#social-campaigns-summary");
  const tableRoot = document.querySelector("#social-campaigns-table");
  const languageRoot = document.querySelector("#social-languages-table");
  const downloadLink = document.querySelector("#social-campaigns-download");
  if (!summaryRoot && !tableRoot && !languageRoot && !downloadLink) return;
  const data = await getJson("/api/social-campaigns");
  const summary = data.summary || {};
  if (summaryRoot) {
    summaryRoot.innerHTML = [
      avatarSummaryCard("Channels", summary.channels || 0, "social + owned"),
      avatarSummaryCard("Ready", summary.ready || 0, "draft-ready"),
      avatarSummaryCard("Languages", summary.languages || 0, "multilingual"),
      avatarSummaryCard("Autonomy", "Supervised", summary.autonomy || ""),
    ].join("");
  }
  if (tableRoot) {
    tableRoot.innerHTML = simpleRowsTable(data.channels || [], [
      { key: "channel", label: "Channel", render: (row) => `<strong>${escapeHtml(row.channel)}</strong><br><small>${escapeHtml(row.type)}</small>` },
      { key: "status", label: "Status", render: (row) => `<span class="status-${escapeHtml(row.status)}">${escapeHtml(row.status)}</span><br><small>${escapeHtml(row.configured)}</small>` },
      { key: "asset", label: "Asset" },
      { key: "autonomy", label: "Autonomy" },
      { key: "next_action", label: "Next" },
    ], "campaign-row");
  }
  if (languageRoot) {
    languageRoot.innerHTML = simpleRowsTable(data.languages || [], [
      { key: "code", label: "Lang", render: (row) => `<strong>${escapeHtml(row.code)}</strong><br><small>${escapeHtml(row.label)}</small>` },
      { key: "role", label: "Role" },
      { key: "tone", label: "Tone" },
    ], "language-row");
  }
  if (downloadLink && summary.sheet) downloadLink.href = mediaUrl(summary.sheet);
}

async function refreshLegalGuardrails() {
  const summaryRoot = document.querySelector("#legal-guardrails-summary");
  const customerRoot = document.querySelector("#legal-guardrails-table");
  const supplierRoot = document.querySelector("#supplier-contract-table");
  const legalLink = document.querySelector("#legal-guardrails-download");
  const supplierLink = document.querySelector("#supplier-contract-download");
  if (!summaryRoot && !customerRoot && !supplierRoot && !legalLink && !supplierLink) return;
  const data = await getJson("/api/legal-guardrails");
  const summary = data.summary || {};
  if (summaryRoot) {
    summaryRoot.innerHTML = [
      avatarSummaryCard("Customer pass", summary.customer_pass || 0, "legal guards"),
      avatarSummaryCard("Customer needs", summary.customer_needs || 0, "review"),
      avatarSummaryCard("Suppliers", summary.supplier_active || 0, "active/connected"),
      avatarSummaryCard("Status", summary.status || "attention", "guardrails"),
    ].join("");
  }
  if (customerRoot) {
    customerRoot.innerHTML = simpleRowsTable(data.customer || [], [
      { key: "area", label: "Area", render: (row) => `<strong>${escapeHtml(row.area)}</strong><br><small>${escapeHtml(row.source)}</small>` },
      { key: "status", label: "Status", render: (row) => `<span class="status-${escapeHtml(row.status)}">${escapeHtml(row.status)}</span>` },
      { key: "requirement", label: "Requirement" },
      { key: "agent_rule", label: "Agent rule" },
    ], "legal-row");
  }
  if (supplierRoot) {
    supplierRoot.innerHTML = simpleRowsTable(data.suppliers || [], [
      { key: "supplier", label: "Supplier", render: (row) => `<strong>${escapeHtml(row.supplier)}</strong><br><small>${escapeHtml(row.relationship)}</small>` },
      { key: "status", label: "Status", render: (row) => `<span class="status-${escapeHtml(row.status)}">${escapeHtml(row.status)}</span><br><small>${escapeHtml(row.risk)}</small>` },
      { key: "minimum_terms", label: "Minimum terms" },
      { key: "agent_rule", label: "Agent rule" },
    ], "supplier-row");
  }
  if (legalLink && summary.legal_sheet) legalLink.href = mediaUrl(summary.legal_sheet);
  if (supplierLink && summary.supplier_sheet) supplierLink.href = mediaUrl(summary.supplier_sheet);
}

async function refreshPhotoStudio() {
  const summaryRoot = document.querySelector("#photo-studio-summary");
  const chartsRoot = document.querySelector("#photo-studio-charts");
  const tableRoot = document.querySelector("#photo-studio-table");
  const progressionRoot = document.querySelector("#theme-progression-table");
  const worldRoot = document.querySelector("#world-model-context-table");
  const reviewRoot = document.querySelector("#review-guard-table");
  const photoLink = document.querySelector("#photo-studio-download");
  const progressionLink = document.querySelector("#theme-progression-download");
  if (!summaryRoot && !chartsRoot && !tableRoot && !progressionRoot && !worldRoot && !reviewRoot && !photoLink && !progressionLink) return;
  const data = await getJson("/api/photo-studio");
  const summary = data.summary || {};
  if (summaryRoot) {
    summaryRoot.innerHTML = [
      avatarSummaryCard("Shot types", summary.shot_types || 0, "catalogo foto"),
      avatarSummaryCard("P0", summary.p0 || 0, "product truth"),
      avatarSummaryCard("Ready", summary.ready || 0, "ready to plan"),
      avatarSummaryCard("World contexts", summary.world_contexts || 0, "Adam/Eve system"),
      avatarSummaryCard("Reviews", summary.review_guards || 0, "guardrails"),
    ].join("");
  }
  if (chartsRoot) {
    const shotTypes = Number(summary.shot_types || 0);
    const readyPercent = shotTypes ? Math.round((Number(summary.ready || 0) / shotTypes) * 100) : 0;
    const p0Percent = shotTypes ? Math.round((Number(summary.p0 || 0) / shotTypes) * 100) : 0;
    chartsRoot.innerHTML = [
      donutCard("Photo readiness", readyPercent, "based on Shopify product data", readyPercent ? "ready_to_plan" : "waiting_for_shopify_products"),
      donutCard("P0 visual set", p0Percent, "front, editorial, detail, hero", "ready_to_plan"),
      `<div class="chart-panel">${progressChart([
        { stage: "Mockup truth", status: "pass", progress: 100, signal: "no invented patterns" },
        { stage: "PDP clarity", status: "needs_review", progress: 55, signal: "5+ images per PDP target" },
        { stage: "Reviews", status: "planned", progress: 35, signal: "after delivery only" },
      ])}</div>`,
    ].join("");
  }
  if (tableRoot) {
    tableRoot.innerHTML = simpleRowsTable(data.shots || [], [
      { key: "shot", label: "Shot", render: (row) => `<strong>${escapeHtml(row.shot)}</strong><br><small>${escapeHtml(row.format)}</small>` },
      { key: "priority", label: "Priority" },
      { key: "status", label: "Status", render: (row) => `<span class="status-${escapeHtml(row.status)}">${escapeHtml(row.status)}</span>` },
      { key: "purpose", label: "Purpose" },
      { key: "requirements", label: "Requirements" },
    ], "photo-row");
  }
  if (progressionRoot) {
    progressionRoot.innerHTML = simpleRowsTable(data.theme_stages || [], [
      { key: "stage", label: "Stage", render: (row) => `<strong>${escapeHtml(row.stage)}</strong><br><small>${escapeHtml(row.when)}</small>` },
      { key: "theme_use", label: "Theme use" },
      { key: "image_need", label: "Image need" },
    ], "theme-stage-row");
  }
  if (worldRoot) {
    worldRoot.innerHTML = simpleRowsTable(data.world_contexts || [], [
      { key: "market", label: "Market", render: (row) => `<strong>${escapeHtml(row.market)}</strong><br><small>${escapeHtml(row.language)}</small>` },
      { key: "model_direction", label: "Model direction" },
      { key: "weather_logic", label: "Weather logic" },
      { key: "guardrail", label: "Guardrail" },
    ], "world-model-row");
  }
  if (reviewRoot) {
    reviewRoot.innerHTML = simpleRowsTable(data.review_guards || [], [
      { key: "guard", label: "Review guard", render: (row) => `<strong>${escapeHtml(row.guard)}</strong>` },
      { key: "meaning", label: "Meaning" },
      { key: "agent_rule", label: "Agent rule" },
    ], "review-row");
  }
  if (photoLink && summary.sheet) photoLink.href = mediaUrl(summary.sheet);
  if (progressionLink && summary.progression) progressionLink.href = mediaUrl(summary.progression);
}

async function refreshGrowthCRM() {
  const summaryRoot = document.querySelector("#growth-crm-summary");
  const chartsRoot = document.querySelector("#growth-crm-charts");
  const segmentsRoot = document.querySelector("#growth-crm-segments-table");
  const diagnosticsRoot = document.querySelector("#growth-crm-diagnostics-table");
  const downloadLink = document.querySelector("#growth-crm-download");
  if (!summaryRoot && !chartsRoot && !segmentsRoot && !diagnosticsRoot && !downloadLink) return;
  const data = await getJson("/api/growth-crm");
  const summary = data.summary || {};
  if (summaryRoot) {
    summaryRoot.innerHTML = [
      avatarSummaryCard("Segments", summary.segments || 0, "real customer base"),
      avatarSummaryCard("Ready", summary.ready || 0, "draft/manual"),
      avatarSummaryCard("Attention", summary.attention || 0, "PDP/compliance"),
      avatarSummaryCard("Primary", "PDP first", summary.primary_action || ""),
    ].join("");
  }
  if (chartsRoot) {
    const total = Number(summary.ready || 0) + Number(summary.attention || 0);
    const readyPercent = total ? Math.round((Number(summary.ready || 0) / total) * 100) : 0;
    const attentionPercent = total ? Math.round((Number(summary.attention || 0) / total) * 100) : 0;
    chartsRoot.innerHTML = [
      donutCard("CRM ready", readyPercent, "ready/manual steps", "ready"),
      donutCard("Needs attention", attentionPercent, "PDP, legal, approval", attentionPercent ? "needs_review" : "pass"),
    ].join("");
  }
  if (segmentsRoot) {
    segmentsRoot.innerHTML = simpleRowsTable(data.segments || [], [
      { key: "segment", label: "Segment", render: (row) => `<strong>${escapeHtml(row.segment)}</strong><br><small>${escapeHtml(row.tag)} · ${escapeHtml(row.current_size)}</small>` },
      { key: "status", label: "Status", render: (row) => `<span class="status-${escapeHtml(row.status)}">${escapeHtml(row.status)}</span><br><small>${escapeHtml(row.priority)}</small>` },
      { key: "action", label: "Action" },
      { key: "automation", label: "Automation" },
    ], "crm-row");
  }
  if (diagnosticsRoot) {
    diagnosticsRoot.innerHTML = simpleRowsTable(data.diagnostics || [], [
      { key: "check", label: "Check", render: (row) => `<strong>${escapeHtml(row.check)}</strong><br><small>${escapeHtml(row.target)}</small>` },
      { key: "status", label: "Status", render: (row) => `<span class="status-${escapeHtml(row.status)}">${escapeHtml(row.status)}</span>` },
      { key: "why", label: "Why" },
    ], "crm-row");
  }
  if (downloadLink && summary.sheet) downloadLink.href = mediaUrl(summary.sheet);
}

function apiOrchestrationTable(rows) {
  if (!rows.length) return "No API rows yet.";
  const head = `
    <div class="api-row table-head">
      <span>API</span>
      <span>Status</span>
      <span>Phase</span>
      <span>Purpose</span>
      <span>Env</span>
    </div>
  `;
  const body = rows.map((row) => `
    <div class="api-row">
      <span><strong>${escapeHtml(row.api)}</strong></span>
      <span><span class="status-${escapeHtml(row.status)}">${escapeHtml(row.status)}</span><br><small>${escapeHtml(row.service_status || "")}</small></span>
      <span>${escapeHtml(row.phase)}</span>
      <span>${escapeHtml(row.purpose)}</span>
      <span><small>${escapeHtml(row.required_env)}</small></span>
    </div>
  `).join("");
  return head + body;
}

async function refreshApiOrchestration() {
  const summaryRoot = document.querySelector("#api-orchestration-summary");
  const tableRoot = document.querySelector("#api-orchestration-table");
  const downloadLink = document.querySelector("#api-orchestration-download");
  if (!summaryRoot && !tableRoot && !downloadLink) return;

  const data = await getJson("/api/orchestration");
  const summary = data.summary || {};
  if (summaryRoot) {
    summaryRoot.innerHTML = [
      avatarSummaryCard("Ready", summary.ready || 0, "usable now"),
      avatarSummaryCard("Partial", summary.partial || 0, "configured but incomplete"),
      avatarSummaryCard("Missing", summary.missing || 0, "needs credentials/setup"),
      avatarSummaryCard("Matrix", "CSV", summary.matrix || ""),
    ].join("");
  }
  if (tableRoot) {
    tableRoot.innerHTML = apiOrchestrationTable(data.rows || []);
  }
  if (downloadLink && summary.matrix) {
    downloadLink.href = mediaUrl(summary.matrix);
  }
}

function trustPagesTable(rows) {
  if (!rows.length) return "No trust checks yet.";
  const head = `
    <div class="trust-row table-head">
      <span>Check</span>
      <span>Status</span>
      <span>URL</span>
      <span>Next</span>
    </div>
  `;
  const body = rows.map((row) => `
    <div class="trust-row">
      <span><strong>${escapeHtml(row.check)}</strong><br><small>${escapeHtml(row.purpose)}</small></span>
      <span><span class="status-${escapeHtml(row.status)}">${escapeHtml(row.status)}</span><br><small>${escapeHtml(row.http_status)}</small></span>
      <span><small>${escapeHtml(row.url)}</small></span>
      <span>${escapeHtml(row.next_action)}</span>
    </div>
  `).join("");
  return head + body;
}

function tagIssuesTable(rows) {
  if (!rows.length) return "No tag issues. Good.";
  const head = `
    <div class="tag-row table-head">
      <span>Status</span>
      <span>Issue</span>
      <span>GTM</span>
      <span>GA4</span>
      <span>URL</span>
    </div>
  `;
  const body = rows.slice(0, 18).map((row) => `
    <div class="tag-row">
      <span>${escapeHtml(row.status)}</span>
      <span>${escapeHtml(row.issue)}</span>
      <span>${escapeHtml(row.gtm_ids || "-")}</span>
      <span>${escapeHtml(row.ga_ids || "-")}</span>
      <span><small>${escapeHtml(row.url)}</small></span>
    </div>
  `).join("");
  return head + body;
}

async function refreshGoogleMerchant() {
  const summaryRoot = document.querySelector("#google-merchant-summary");
  const chartsRoot = document.querySelector("#google-merchant-charts");
  const trustRoot = document.querySelector("#google-trust-pages-table");
  const tagRoot = document.querySelector("#google-tag-table");
  const issuesRoot = document.querySelector("#google-merchant-issues-table");
  const actionsRoot = document.querySelector("#google-merchant-actions-table");
  const attributesRoot = document.querySelector("#google-product-attributes-table");
  const countryRoot = document.querySelector("#google-country-policy-table");
  const downloadLink = document.querySelector("#google-merchant-download");
  if (!summaryRoot && !chartsRoot && !trustRoot && !tagRoot && !issuesRoot && !actionsRoot && !attributesRoot && !countryRoot && !downloadLink) return;
  const data = await getJson("/api/google-merchant");
  const summary = data.summary || {};
  const tag = data.tag_summary || {};
  const feedSummary = data.feed?.summary || {};
  if (summaryRoot) {
    summaryRoot.innerHTML = [
      avatarSummaryCard("Merchant", summary.status || "unknown", `ID ${summary.merchant_id || ""}`),
      avatarSummaryCard("Reason", summary.reason || "unknown", "policy issue"),
      avatarSummaryCard("P0 blockers", summary.blockers || 0, "before appeal"),
      avatarSummaryCard("First action", summary.first_action || "Local inventory", "Merchant recovery queue"),
      avatarSummaryCard("Attrs", feedSummary.attribute_issues || 0, "size/color/gender/age"),
      avatarSummaryCard("Countries", feedSummary.country_needs_config || 0, "needs config"),
      avatarSummaryCard("GTM / GA4", `${tag.expected_gtm_percent || 0}% / ${tag.ga4_percent || 0}%`, tag.gtm_target || ""),
    ].join("");
  }
  if (chartsRoot) {
    chartsRoot.innerHTML = metricBars(data.charts || []);
  }
  if (trustRoot) {
    trustRoot.innerHTML = trustPagesTable(data.trust_pages || []);
  }
  if (tagRoot) {
    tagRoot.innerHTML = tagIssuesTable(data.tag_issues || []);
  }
  if (issuesRoot) {
    issuesRoot.innerHTML = simpleRowsTable(data.merchant_issues || [], [
      { key: "merchant_label", label: "Issue", render: (row) => `<strong>${escapeHtml(row.merchant_label)}</strong><br><small>${escapeHtml(row.issue)}</small>` },
      { key: "status", label: "Status", render: (row) => `<span class="status-${escapeHtml(row.status)}">${escapeHtml(row.status)}</span>` },
      { key: "impact", label: "Impact" },
      { key: "first_action", label: "First action" },
    ], "merchant-issue-row");
  }
  if (actionsRoot) {
    actionsRoot.innerHTML = simpleRowsTable(data.actions || [], [
      { key: "priority", label: "P" },
      { key: "area", label: "Area", render: (row) => `<strong>${escapeHtml(row.area)}</strong><br><small>${escapeHtml(row.action)}</small>` },
      { key: "status", label: "Status", render: (row) => `<span class="status-${escapeHtml(row.status)}">${escapeHtml(row.status)}</span>` },
      { key: "detail", label: "Detail" },
    ], "merchant-action-row");
  }
  if (attributesRoot) {
    attributesRoot.innerHTML = simpleRowsTable((data.feed?.attribute_rows || []).slice(0, 30), [
      { key: "handle", label: "Product", render: (row) => `<strong>${escapeHtml(row.handle)}</strong><br><small>${escapeHtml(row.title)}</small>` },
      { key: "detail", label: "Missing" },
      { key: "size", label: "Size" },
      { key: "color", label: "Color" },
      { key: "gender", label: "Gender" },
      { key: "age_group", label: "Age" },
    ], "merchant-attribute-row");
  }
  if (countryRoot) {
    countryRoot.innerHTML = simpleRowsTable(data.country_policy || [], [
      { key: "country", label: "Country", render: (row) => `<strong>${escapeHtml(row.country)}</strong><br><small>${escapeHtml(row.code)}</small>` },
      { key: "status", label: "Status", render: (row) => `<span class="status-${escapeHtml(row.status)}">${escapeHtml(row.status)}</span>` },
      { key: "included_products", label: "Included" },
      { key: "priced_products", label: "Priced" },
      { key: "next_action", label: "Next" },
    ], "merchant-country-row");
  }
  if (downloadLink && summary.matrix) {
    downloadLink.href = mediaUrl(summary.matrix);
  }
}

function marketRecommendationsTable(rows) {
  if (!rows.length) return "No recommendations yet.";
  const head = `
    <div class="market-row table-head">
      <span>Priority</span>
      <span>Recommendation</span>
      <span>Change</span>
      <span>Verification</span>
    </div>
  `;
  const body = rows.map((row) => `
    <div class="market-row">
      <span>${escapeHtml(row.priority)}</span>
      <span><strong>${escapeHtml(row.recommendation)}</strong><br><small>${escapeHtml(row.change_type)}</small></span>
      <span>${escapeHtml(row.site_change)}</span>
      <span>${escapeHtml(row.verification)}</span>
    </div>
  `).join("");
  return head + body;
}

async function refreshMarketSense() {
  const summaryRoot = document.querySelector("#market-sense-summary");
  const signalsRoot = document.querySelector("#market-sense-signals");
  const tableRoot = document.querySelector("#market-sense-table");
  const downloadLink = document.querySelector("#market-sense-download");
  if (!summaryRoot && !signalsRoot && !tableRoot && !downloadLink) return;
  const data = await getJson("/api/market-sense");
  const summary = data.summary || {};
  if (summaryRoot) {
    summaryRoot.innerHTML = [
      avatarSummaryCard("Market sense", summary.market_sense || 0, summary.mode || ""),
      avatarSummaryCard("Signals", summary.signals || 0, "local + connected"),
      avatarSummaryCard("Recs", summary.recommendations || 0, "site adaptations"),
      avatarSummaryCard("Mode", "Conservative", "small verified changes"),
    ].join("");
  }
  if (signalsRoot) {
    signalsRoot.innerHTML = metricBars(data.signals || []);
  }
  if (tableRoot) {
    tableRoot.innerHTML = marketRecommendationsTable(data.recommendations || []);
  }
  if (downloadLink && summary.sheet) {
    downloadLink.href = mediaUrl(summary.sheet);
  }
}

function offerChecksTable(rows) {
  if (!rows.length) return "No offer checks yet.";
  const head = `
    <div class="offer-row table-head">
      <span>Check</span>
      <span>Status</span>
      <span>Detail</span>
    </div>
  `;
  const body = rows.map((row) => `
    <div class="offer-row">
      <span><strong>${escapeHtml(row.check)}</strong></span>
      <span><span class="status-${escapeHtml(row.status)}">${escapeHtml(row.status)}</span></span>
      <span>${escapeHtml(row.detail)}</span>
    </div>
  `).join("");
  return head + body;
}

async function refreshMarketingOffers() {
  const summaryRoot = document.querySelector("#marketing-offers-summary");
  const tableRoot = document.querySelector("#marketing-offers-table");
  if (!summaryRoot && !tableRoot) return;
  const data = await getJson("/api/marketing-offers");
  const summary = data.summary || {};
  const offer = data.offer || {};
  if (summaryRoot) {
    summaryRoot.innerHTML = [
      avatarSummaryCard("Offer", summary.status || "draft", offer.name || ""),
      avatarSummaryCard("Compliance", summary.compliance || "unknown", "Google-safe timer"),
      avatarSummaryCard("Ends", offer.ends_at || "-", "real deadline"),
      avatarSummaryCard("Discount", summary.discount_code || "not_configured", "no fake claim"),
    ].join("");
  }
  if (tableRoot) {
    tableRoot.innerHTML = offerChecksTable(data.checks || []);
  }
}

function themeChecksTable(rows) {
  if (!rows.length) return "No theme checks yet.";
  const head = `
    <div class="theme-row table-head">
      <span>Check</span>
      <span>Status</span>
      <span>Detail</span>
    </div>
  `;
  const body = rows.map((row) => `
    <div class="theme-row">
      <span><strong>${escapeHtml(row.check)}</strong></span>
      <span><span class="status-${escapeHtml(row.status)}">${escapeHtml(row.status)}</span></span>
      <span>${escapeHtml(row.detail)}</span>
    </div>
  `).join("");
  return head + body;
}

async function refreshThemeOptimizer() {
  const summaryRoot = document.querySelector("#theme-optimizer-summary");
  const tableRoot = document.querySelector("#theme-optimizer-table");
  const downloadLink = document.querySelector("#theme-optimizer-download");
  if (!summaryRoot && !tableRoot && !downloadLink) return;
  const data = await getJson("/api/theme-optimizer");
  const summary = data.summary || {};
  const files = data.files || {};
  if (summaryRoot) {
    summaryRoot.innerHTML = [
      avatarSummaryCard("Patch", summary.status || "unknown", summary.goal || ""),
      avatarSummaryCard("Output", summary.output_zip ? "Ready" : "Missing", summary.output_zip || ""),
      avatarSummaryCard("CSS", files.css ? "Ready" : "Missing", files.css || ""),
      avatarSummaryCard("Sections", "Hero BKS + Effects + Trust + Timer + Grid", `${files.impact_home || ""} ${files.theme_effects || ""} ${files.trust_section || ""} ${files.timed_offer || ""} ${files.planet_collections_orbit || ""} ${files.product_editorial_care || ""} ${files.collection_signal || ""} ${files.collection_grid_bks || ""}`),
    ].join("");
  }
  if (tableRoot) {
    tableRoot.innerHTML = themeChecksTable(data.checks || []);
  }
  if (downloadLink && summary.output_zip) {
    downloadLink.href = mediaUrl(summary.output_zip);
  }
}

async function refreshDashboard() {
  const statusRoot = document.querySelector("#service-status");
  const phaseRoot = document.querySelector("#phase-grid");
  const eventRoot = document.querySelector("#event-log");
  const runRoot = document.querySelector("#run-ledger");
  const referencesRoot = document.querySelector("#references-summary");

  if (statusRoot) {
    const health = await getJson("/api/services/health");
    statusRoot.innerHTML = Object.entries(health.services)
      .map(([name, configured]) => serviceCard(name, configured))
      .join("");
  }

  if (phaseRoot) {
    const data = await getJson("/api/phases");
    phaseRoot.innerHTML = data.phases.map(phaseCard).join("");
  }

  if (eventRoot) {
    const data = await getJson("/api/events");
    eventRoot.innerHTML = data.database_events.slice(0, 10).map((event) => `
      <div class="event-row">
        <span>${event.created_at}</span>
        <span>${event.phase_id || "-"}</span>
        <span>${event.event_type}</span>
        <span>${event.payload?.status || ""}</span>
        <span>${event.payload?.message || ""}</span>
      </div>
    `).join("") || "No events yet.";
  }

  if (runRoot) {
    const data = await getJson("/api/runs?limit=12");
    runRoot.innerHTML = data.runs.length
      ? data.runs.map((run) => `
          <div class="ledger-row">
            <span>#${run.run_id}</span>
            <span>${run.phase_id}</span>
            <span>${run.intent}</span>
            <span>${run.status}</span>
            <span>${run.started_at}</span>
          </div>
        `).join("")
      : "No runs yet.";
  }

  if (referencesRoot) {
    const refs = await getJson("/api/references/summary");
    referencesRoot.innerHTML = [
      referenceCard("Catalog products", refs.total_products, "unique handles tracked"),
      referenceCard("Printify mapped", refs.mapped_printify, `${refs.missing_printify} missing`),
      referenceCard("Shopify mapped", refs.mapped_shopify, `${refs.missing_shopify} missing`),
      referenceCard("Publish states", Object.keys(refs.publish_statuses || {}).length, JSON.stringify(refs.publish_statuses || {})),
    ].join("");
  }

  await refreshAvatarProduction();
  await refreshSocialRender();
  await refreshSalesChannels();
  await refreshCatalogSync();
  await refreshProductNameAudit();
  await refreshCommunications();
  await refreshSkillRegistry();
  await refreshApiOrchestration();
  await refreshGoogleMerchant();
  await refreshMarketSense();
  await refreshMarketingOffers();
  await refreshThemeOptimizer();
  await refreshMasterActions();
  await refreshRealtimeControl();
  await refreshWeeklyGoals();
  await refreshDailyWebUpdate();
  await refreshAlwaysOn();
  await refreshKnowledgeDB();
  await refreshAgentRoutine();
  await refreshThemeAIAssistant();
  await refreshAgentOS();
  await refreshOpenAIAlliance();
  await refreshCanvaConnectors();
  await refreshHyperFramesConnectors();
  await refreshGoogleTrust();
  await refreshNetworkMonitor();
  await refreshLegalGuardrails();
  await refreshPayments();
  await refreshMarketingLogic();
  await refreshSocialCampaigns();
  await refreshPhotoStudio();
  await refreshGrowthCRM();
  await refreshOfficialInbox();
  await refreshAgentProfile();
}

async function refreshPhaseDetail() {
  const root = document.querySelector("#phase-detail");
  if (!root) return;
  const phase = await getJson(`/api/phases/${root.dataset.phaseId}`);
  root.textContent = JSON.stringify(phase, null, 2);
}

async function runPhase(phaseId) {
  const result = await getJson(`/api/phases/${phaseId}/run`, { method: "POST" });
  await refreshDashboard().catch(() => {});
  await refreshPhaseDetail().catch(() => {});
  return result;
}

document.addEventListener("click", async (event) => {
  const runButton = event.target.closest("[data-run-phase]");
  if (runButton) {
    runButton.disabled = true;
    try {
      await runPhase(runButton.dataset.runPhase);
    } catch (error) {
      alert(error.message);
    } finally {
      runButton.disabled = false;
    }
  }

  if (event.target.closest("#refresh-button")) {
    refreshDashboard().catch((error) => alert(error.message));
  }

  if (event.target.closest("#live-health-button")) {
    const statusRoot = document.querySelector("#service-status");
    statusRoot.innerHTML = "Checking live services...";
    getJson("/api/services/health?live=1")
      .then((health) => {
        statusRoot.innerHTML = Object.entries(health.services)
          .map(([name, configured]) => serviceCard(name, configured))
          .join("");
      })
      .catch((error) => alert(error.message));
  }

  if (event.target.closest("#network-monitor-live")) {
    const button = event.target.closest("#network-monitor-live");
    button.disabled = true;
    try {
      await refreshNetworkMonitor(true);
    } catch (error) {
      alert(error.message);
    } finally {
      button.disabled = false;
    }
  }

  if (event.target.closest("#catalog-sync-run")) {
    const button = event.target.closest("#catalog-sync-run");
    button.disabled = true;
    try {
      await refreshCatalogSync(true);
      await refreshDashboard();
    } catch (error) {
      alert(error.message);
    } finally {
      button.disabled = false;
    }
  }

  if (event.target.closest("#product-name-audit-live")) {
    const button = event.target.closest("#product-name-audit-live");
    button.disabled = true;
    try {
      await refreshProductNameAudit(true);
    } catch (error) {
      alert(error.message);
    } finally {
      button.disabled = false;
    }
  }

  if (event.target.closest("#sync-references-button")) {
    const referencesRoot = document.querySelector("#references-summary");
    referencesRoot.innerHTML = "Syncing catalog references...";
    getJson("/api/references/sync-catalog", { method: "POST" })
      .then(() => refreshDashboard())
      .catch((error) => alert(error.message));
  }

  if (event.target.closest("#bootstrap-avatar-button")) {
    const summaryRoot = document.querySelector("#avatar-summary");
    if (summaryRoot) summaryRoot.innerHTML = "Preparing avatar workspace...";
    getJson("/api/avatar-production/bootstrap", { method: "POST" })
      .then(() => refreshDashboard())
      .catch((error) => alert(error.message));
  }

  const verifyButton = event.target.closest("[data-verify-action]");
  if (verifyButton) {
    verifyButton.disabled = true;
    try {
      const result = await getJson(`/api/master-actions/verify/${verifyButton.dataset.verifyAction}`, { method: "POST" });
      appendAgentMessage("assistant", `Verifica ${verifyButton.dataset.verifyAction}: ${result.status}. ${result.detail || ""}`);
      await refreshDashboard();
    } catch (error) {
      alert(error.message);
    } finally {
      verifyButton.disabled = false;
    }
  }

  if (event.target.closest("#daily-web-update-run")) {
    const summaryRoot = document.querySelector("#daily-web-update-summary");
    if (summaryRoot) summaryRoot.innerHTML = "Running daily local snapshot...";
    getJson("/api/daily-web-update/run", { method: "POST" })
      .then(() => refreshDashboard())
      .catch((error) => alert(error.message));
  }

  if (event.target.closest("#daily-web-update-live")) {
    const summaryRoot = document.querySelector("#daily-web-update-summary");
    if (summaryRoot) summaryRoot.innerHTML = "Checking live web sources...";
    getJson("/api/daily-web-update/run?live=1", { method: "POST" })
      .then(() => refreshDashboard())
      .catch((error) => alert(error.message));
  }

  const agentButton = event.target.closest("[data-agent-message]");
  if (agentButton) {
    sendAgentMessage(agentButton.dataset.agentMessage).catch((error) => appendAgentMessage("assistant", error.message));
  }
});

document.addEventListener("submit", async (event) => {
  const form = event.target.closest("#agent-form");
  if (!form) return;
  event.preventDefault();
  const input = document.querySelector("#agent-input");
  const value = input.value;
  input.value = "";
  sendAgentMessage(value).catch((error) => appendAgentMessage("assistant", error.message));
});

refreshDashboard().catch(() => {});
refreshPhaseDetail().catch(() => {});

setInterval(() => {
  refreshRealtimeControl().catch(() => {});
}, 8000);
