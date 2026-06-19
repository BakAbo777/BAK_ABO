/* BKS Member Area — JS: tabs, wishlist, countdown, referral copy */

(function () {
  'use strict';

  /* ── Tab navigation ── */
  function initTabs() {
    const tabs   = document.querySelectorAll('.bks-tab-btn');
    const panels = document.querySelectorAll('.bks-member-panel');
    if (!tabs.length) return;

    function activate(id) {
      tabs.forEach(t => t.classList.toggle('active', t.dataset.tab === id));
      panels.forEach(p => p.classList.toggle('active', p.id === 'bks-panel-' + id));
      try { history.replaceState(null, '', '#' + id); } catch (e) {}
    }

    tabs.forEach(btn => {
      btn.addEventListener('click', () => activate(btn.dataset.tab));
    });

    const hash = (location.hash || '').replace('#', '');
    const valid = [...tabs].map(t => t.dataset.tab);
    activate(valid.includes(hash) ? hash : (valid[0] || 'orders'));
  }

  /* ── Wishlist — localStorage persistence ── */
  const WL_KEY = 'bks_wishlist_v1';

  function wlLoad() {
    try { return JSON.parse(localStorage.getItem(WL_KEY) || '[]'); } catch { return []; }
  }

  function wlSave(list) {
    try { localStorage.setItem(WL_KEY, JSON.stringify(list)); } catch {}
  }

  function wlHas(handle) { return wlLoad().includes(handle); }

  function wlToggle(handle) {
    let list = wlLoad();
    if (list.includes(handle)) {
      list = list.filter(h => h !== handle);
    } else {
      list.push(handle);
    }
    wlSave(list);
    return list.includes(handle);
  }

  /* Sync wishlist visual state on all existing heart buttons (no new listeners) */
  function initHeartButtons() {
    document.querySelectorAll('.bks-heart-btn').forEach(btn => {
      const handle = btn.dataset.handle;
      if (!handle) return;
      btn.classList.toggle('wishlisted', wlHas(handle));
    });
  }

  /* Render wishlist panel from localStorage via AJAX product JSON */
  const BKS_COLLECTIONS = {
    origin:  { label: 'BKS Origin',  color: '#C8B59A' },
    glyph:   { label: 'BKS Glyph',   color: '#9BB5CC' },
    marker:  { label: 'BKS Marker',  color: '#E2A86B' },
    riviera: { label: 'BKS Riviera', color: '#7EB3D4' },
    pulse:   { label: 'BKS Pulse',   color: '#D4A030' },
    token:   { label: 'BKS Token',   color: '#B8C89A' },
    flag:    { label: 'BKS Flag',    color: '#CC9999' },
    hours:   { label: 'BKS Hours',   color: '#A8A8C8' }
  };

  function detectCollection(handle) {
    for (const key of Object.keys(BKS_COLLECTIONS)) {
      if (handle === 'bks-' + key || handle.startsWith('bks-' + key + '-')) return key;
    }
    return null;
  }

  async function renderWishlistPanel() {
    const container = document.getElementById('bks-wishlist-container');
    if (!container) return;

    const handles = wlLoad();

    if (handles.length === 0) {
      container.innerHTML = `
        <div class="bks-wishlist-empty">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
          </svg>
          <p>La tua wishlist è vuota</p>
          <a href="/collections/all" class="bks-btn-ghost">Esplora i prodotti</a>
        </div>`;
      return;
    }

    container.innerHTML = '<div class="bks-wishlist-grid" id="bks-wl-grid"></div>';
    const grid = document.getElementById('bks-wl-grid');

    const shareBtn = document.createElement('button');
    shareBtn.className = 'bks-wishlist-share';
    shareBtn.innerHTML = `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 12v8a2 2 0 002 2h12a2 2 0 002-2v-8M16 6l-4-4-4 4M12 2v13"/></svg> Condividi wishlist`;
    shareBtn.addEventListener('click', shareWishlist);

    for (const handle of handles) {
      try {
        const res  = await fetch('/products/' + handle + '.js');
        const prod = await res.json();
        const img  = prod.featured_image || '';
        const price = prod.price_min ? (prod.price_min / 100).toFixed(2) + ' €' : '';
        const col   = detectCollection(handle);
        const colMeta = col ? BKS_COLLECTIONS[col] : null;

        const card = document.createElement('div');
        card.className = 'bks-wishlist-card';
        if (col) card.dataset.collection = col;

        card.innerHTML = `
          <a href="/products/${handle}" class="bks-wishlist-card-link">
            ${img
              ? `<img class="bks-wishlist-card-img" src="${img}" alt="${prod.title}" loading="lazy">`
              : `<div class="bks-wishlist-card-img-placeholder">BKS</div>`}
            <div class="bks-wishlist-card-info">
              ${colMeta ? `<p class="bks-wishlist-card-cat">${colMeta.label}</p>` : ''}
              <p class="bks-wishlist-card-title">${prod.title}</p>
              <p class="bks-wishlist-card-price">${price}</p>
            </div>
          </a>
          <button class="bks-wishlist-card-remove" data-remove="${handle}">Rimuovi</button>`;

        card.querySelector('[data-remove]').addEventListener('click', () => {
          wlToggle(handle);
          document.querySelectorAll(`.bks-heart-btn[data-handle="${handle}"]`)
            .forEach(b => b.classList.remove('wishlisted'));
          renderWishlistPanel();
        });

        if (col) {
          card.addEventListener('mouseenter', () => setMood(col));
          card.addEventListener('mouseleave', () => setMood(null));
        }

        grid.appendChild(card);
      } catch (e) {}
    }

    container.appendChild(shareBtn);
  }

  function shareWishlist() {
    const handles = wlLoad();
    if (!handles.length) return;
    const url = location.origin + '/account?wl=' + handles.join(',');
    if (navigator.share) {
      navigator.share({ title: 'La mia BKS Wishlist', url }).catch(() => copyText(url));
    } else {
      copyText(url);
    }
  }

  /* Prefill wishlist from URL param ?wl= (shared link) */
  function importSharedWishlist() {
    const params  = new URLSearchParams(location.search);
    const handles = params.get('wl');
    if (!handles) return;
    const current = wlLoad();
    handles.split(',').forEach(h => { if (h && !current.includes(h)) current.push(h); });
    wlSave(current);
  }

  /* ── Referral copy ── */
  function initReferralCopy() {
    const btn   = document.getElementById('bks-referral-copy');
    const input = document.getElementById('bks-referral-url');
    if (!btn || !input) return;
    btn.addEventListener('click', () => {
      copyText(input.value);
      btn.textContent = 'Copiato!';
      btn.classList.add('copied');
      setTimeout(() => { btn.textContent = 'Copia link'; btn.classList.remove('copied'); }, 2000);
    });
  }

  function copyText(text) {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(text).catch(() => fallbackCopy(text));
    } else {
      fallbackCopy(text);
    }
  }

  function fallbackCopy(text) {
    const ta = document.createElement('textarea');
    ta.value = text;
    ta.style.cssText = 'position:fixed;opacity:0';
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
  }

  /* ── Countdown ── */
  function initCountdown() {
    const el = document.getElementById('bks-countdown');
    if (!el) return;
    const target = new Date(el.dataset.target);
    if (isNaN(target)) return;

    function tick() {
      const diff = target - Date.now();
      if (diff <= 0) { el.textContent = 'Drop live'; return; }
      const d = Math.floor(diff / 86400000);
      const h = Math.floor((diff % 86400000) / 3600000);
      const m = Math.floor((diff % 3600000)  / 60000);
      const s = Math.floor((diff % 60000)    / 1000);
      ['d','h','m','s'].forEach((unit, i) => {
        const num = [d,h,m,s][i];
        const span = el.querySelector('.bks-countdown-' + unit);
        if (span) span.textContent = String(num).padStart(2,'0');
      });
    }

    tick();
    setInterval(tick, 1000);
  }

  /* ── Customize form ── */
  const CZ_KEY = 'bks_customize_v1';
  const CZ_TYPE_LABELS = {
    palette: 'Color palette', text: 'Text / Monogram',
    placement: 'Graphic placement', sizing: 'Non-standard sizing',
    composition: 'Composition', full: 'Full custom'
  };

  function czLoad() { try { return JSON.parse(localStorage.getItem(CZ_KEY) || '[]'); } catch { return []; } }
  function czSave(list) { try { localStorage.setItem(CZ_KEY, JSON.stringify(list)); } catch {} }

  function czRenderHistory() {
    const container = document.getElementById('bks-cz-history');
    if (!container) return;
    const reqs = czLoad();
    if (!reqs.length) { container.innerHTML = ''; return; }
    container.innerHTML = `
      <div class="bks-cz-history-block">
        <p class="bks-cz-history-title">Sent requests (${reqs.length})</p>
        ${reqs.map(r => `
          <div class="bks-cz-req-card">
            <span class="bks-cz-req-status">Pending</span>
            <div class="bks-cz-req-info">
              <p class="bks-cz-req-title">${r.type_label} — ${r.collection} / ${r.product}</p>
              <p class="bks-cz-req-meta">${r.date} · Size ${r.size}</p>
            </div>
          </div>`).join('')}
      </div>`;
  }

  function initCustomizeForm() {
    const form      = document.getElementById('bks-cz-form');
    const success   = document.getElementById('bks-cz-success');
    const submitBtn = document.getElementById('bks-cz-submit');
    const newBtn    = document.getElementById('bks-cz-new');
    const descArea  = document.getElementById('bks-cz-desc');
    const descCount = document.getElementById('bks-cz-desc-count');
    if (!form) return;

    czRenderHistory();

    if (descArea && descCount) {
      descArea.addEventListener('input', () => {
        const len = Math.min(descArea.value.length, 500);
        if (descArea.value.length > 500) descArea.value = descArea.value.slice(0, 500);
        descCount.textContent = len;
      });
    }

    form.querySelectorAll('.bks-cz-type-card:not(.bks-cz-type-locked)').forEach(card => {
      card.addEventListener('click', () => {
        const radio = card.querySelector('input[type="radio"]');
        if (radio && !radio.disabled) radio.checked = true;
      });
    });

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const collection = form.querySelector('#bks-cz-collection').value;
      const product    = form.querySelector('#bks-cz-product').value;
      const size       = form.querySelector('#bks-cz-size').value;
      const typeRadio  = form.querySelector('input[name="bks-cz-type"]:checked');
      const desc       = (form.querySelector('#bks-cz-desc').value || '').trim();
      const ref        = (form.querySelector('#bks-cz-ref').value || '').trim();

      if (!collection || !product || !typeRadio || desc.length < 20) {
        alert('Please fill in all required fields (description min. 20 characters).');
        return;
      }

      const typeLabel = CZ_TYPE_LABELS[typeRadio.value] || typeRadio.value;
      const name      = form.dataset.customerName  || '';
      const email     = form.dataset.customerEmail || '';

      const msgBody = [
        'BKS CUSTOMIZATION REQUEST',
        '---',
        `Customer: ${name} <${email}>`,
        `Collection: ${collection}`,
        `Garment: ${product}`,
        `Size: ${size}`,
        `Type: ${typeLabel}`,
        '---',
        'Description:',
        desc,
        ref ? `\nVisual reference: ${ref}` : ''
      ].filter(Boolean).join('\n');

      if (submitBtn) { submitBtn.disabled = true; submitBtn.textContent = 'Sending…'; }

      try {
        const params = new URLSearchParams({
          'form_type':      'contact',
          'utf8':           '✓',
          'contact[name]':  name,
          'contact[email]': email,
          'contact[body]':  msgBody
        });
        const r = await fetch('/contact', {
          method:  'POST',
          headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'Accept': 'application/json' },
          body:    params.toString()
        });
        if (!r.ok) throw new Error('HTTP ' + r.status);

        const reqs = czLoad();
        reqs.unshift({
          date: new Date().toLocaleDateString('en-GB'),
          collection, product, size,
          type: typeRadio.value, type_label: typeLabel, desc
        });
        czSave(reqs.slice(0, 20));

        form.hidden = true;
        if (success) success.hidden = false;
        czRenderHistory();

      } catch {
        if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = 'Send request'; }
        alert('Send error. Please retry or contact us at crew@bakabo.club');
      }
    });

    if (newBtn) {
      newBtn.addEventListener('click', () => {
        form.reset();
        form.hidden = false;
        if (success) success.hidden = true;
        if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = 'Send request'; }
        if (descCount) descCount.textContent = '0';
      });
    }
  }

  /* ── Camerino Virtuale — popola wishlist per bks-tryon.js ── */
  function initCamerino() {
    const container = document.getElementById('bks-camerino-wishlist');
    if (!container) return;

    async function renderCamerinoItems() {
      const handles = wlLoad();
      if (!handles.length) {
        container.innerHTML = '<div style="color:#b8b2a6;font-size:13px;padding:8px 0;">Aggiungi prodotti alla wishlist per usare il camerino.<br><a href="/collections/all" style="display:inline-block;margin-top:10px;font-size:12px;text-decoration:underline;color:#b8b2a6;">Esplora</a></div>';
        return;
      }
      container.innerHTML = '';
      for (const handle of handles) {
        try {
          const res  = await fetch('/products/' + handle + '.js');
          const prod = await res.json();
          const img  = prod.featured_image || '';
          const col  = detectCollection(handle);
          const colMeta = col ? BKS_COLLECTIONS[col] : null;
          const btn  = document.createElement('button');
          btn.className             = 'bks-wishlist__item';
          btn.dataset.productId     = String(prod.id || handle);
          btn.dataset.productHandle = handle;
          btn.dataset.productTitle  = prod.title;
          btn.dataset.productImage  = img;
          if (col) { btn.dataset.collection = col; btn.dataset.mood = colMeta.color; }
          btn.innerHTML = img
            ? `<img class="bks-wishlist__thumb" src="${img}" alt="${prod.title}" loading="lazy"><span>${prod.title}</span>`
            : `<div class="bks-wishlist__thumb" style="background:#333;display:flex;align-items:center;justify-content:center;font-size:10px;color:#888">IMG</div><span>${prod.title}</span>`;
          container.appendChild(btn);
        } catch (e) {}
      }
    }

    renderCamerinoItems();
  }

  /* ── Inject heart buttons into any product card on any page ── */
  function injectHeartButtons() {
    const CARD_SELECTORS = [
      '.grid__item',
      '.product-card-wrapper',
      '.product-recommendations .card-wrapper',
      '.related-products .card-wrapper',
      '[data-product-card]',
      '.featured-collection .card-wrapper',
      '.bks-product-pop',
    ];
    document.querySelectorAll(CARD_SELECTORS.join(',')).forEach(item => {
      if (item.querySelector('.bks-heart-btn')) return;
      const link = item.querySelector('a[href*="/products/"]');
      if (!link) return;
      const match = link.href.match(/\/products\/([^/?#]+)/);
      if (!match) return;
      const handle = match[1];
      const wrapper = item.querySelector('.card__inner') || item.querySelector('.card') || item;
      wrapper.style.position = 'relative';
      const btn = document.createElement('button');
      btn.className = 'bks-heart-btn';
      btn.dataset.handle = handle;
      btn.title = wlHas(handle) ? 'Rimuovi da wishlist' : 'Aggiungi a wishlist';
      btn.setAttribute('aria-label', 'Aggiungi a wishlist');
      if (wlHas(handle)) btn.classList.add('wishlisted');
      btn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" class="bks-heart-icon"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>`;
      btn.addEventListener('click', e => {
        e.preventDefault();
        e.stopPropagation();
        const added = wlToggle(handle);
        btn.classList.toggle('wishlisted', added);
        btn.title = added ? 'Rimuovi da wishlist' : 'Aggiungi a wishlist';
        showWishlistToast(added);
        updateWishlistBadge();
        renderWishlistPanel();
      });
      wrapper.appendChild(btn);
    });
  }

  /* ── Wishlist toast ── */
  function showWishlistToast(added) {
    let toast = document.getElementById('bks-wl-toast');
    if (!toast) {
      toast = document.createElement('div');
      toast.id = 'bks-wl-toast';
      document.body.appendChild(toast);
    }
    clearTimeout(toast._bksTimer);
    toast.className = 'bks-wl-toast' + (added ? ' bks-wl-toast--added' : ' bks-wl-toast--removed');
    toast.innerHTML = added
      ? `<svg width="13" height="13" viewBox="0 0 24 24" fill="#e74c3c" stroke="#e74c3c" stroke-width="1.5"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg> Saved to wishlist &nbsp;<a href="/account#wishlist">View →</a>`
      : `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg> Removed from wishlist`;
    toast.classList.add('bks-wl-toast--visible');
    toast._bksTimer = setTimeout(() => toast.classList.remove('bks-wl-toast--visible'), 2800);
  }

  /* ── Wishlist badge on account icon ── */
  function updateWishlistBadge() {
    const count = wlLoad().length;
    let badge = document.getElementById('bks-wl-badge');
    if (!badge) {
      const accountLink = document.querySelector('a[href*="/account"], .bks-member-halo a');
      if (!accountLink) return;
      const wrap = accountLink.closest('a, .bks-member-halo') || accountLink;
      wrap.style.position = 'relative';
      badge = document.createElement('span');
      badge.id = 'bks-wl-badge';
      badge.className = 'bks-wl-badge';
      wrap.appendChild(badge);
    }
    badge.textContent = count;
    badge.style.display = count > 0 ? '' : 'none';
  }

  /* ── Boot ── */
  function init() {
    importSharedWishlist();
    initTabs();
    injectHeartButtons();
    initHeartButtons();
    renderWishlistPanel();
    updateWishlistBadge();
    initReferralCopy();
    initCountdown();
    initCustomizeForm();
    initCamerino();
    startHeartObserver();
  }

  /* Re-inject hearts when AJAX sections load new product cards */
  function startHeartObserver() {
    let debounce;
    const observer = new MutationObserver(() => {
      clearTimeout(debounce);
      debounce = setTimeout(() => {
        injectHeartButtons();
        initHeartButtons();
      }, 300);
    });
    observer.observe(document.body, { childList: true, subtree: true });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  /* Expose wishlist API for theme use */
  /* ── Mood system — panel assumes the selected collection's colour ── */
  function setMood(colKey) {
    const wrap = document.querySelector('.bks-member-wrap');
    if (!wrap) return;
    const color = colKey && BKS_COLLECTIONS[colKey] ? BKS_COLLECTIONS[colKey].color : null;
    if (color) {
      wrap.style.setProperty('--bks-mood', color);
      wrap.dataset.mood = colKey;
    } else {
      wrap.style.removeProperty('--bks-mood');
      delete wrap.dataset.mood;
    }
  }

  window.BKSMember = { wlToggle, wlHas, wlLoad, renderWishlistPanel, setMood, BKS_COLLECTIONS, detectCollection };
})();
