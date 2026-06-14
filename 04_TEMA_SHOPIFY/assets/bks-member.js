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

  /* Heart buttons on product cards */
  function initHeartButtons() {
    document.querySelectorAll('.bks-heart-btn').forEach(btn => {
      const handle = btn.dataset.handle;
      if (!handle) return;
      if (wlHas(handle)) btn.classList.add('wishlisted');
      btn.addEventListener('click', e => {
        e.preventDefault();
        e.stopPropagation();
        const added = wlToggle(handle);
        btn.classList.toggle('wishlisted', added);
        btn.title = added ? 'Rimuovi da wishlist' : 'Aggiungi a wishlist';
        renderWishlistPanel();
      });
    });
  }

  /* Render wishlist panel from localStorage via AJAX product JSON */
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
        const card = document.createElement('div');
        card.className = 'bks-wishlist-card';
        card.innerHTML = `
          <a href="/products/${handle}" style="display:block;text-decoration:none;color:inherit;">
            ${img
              ? `<img class="bks-wishlist-card-img" src="${img}" alt="${prod.title}" loading="lazy">`
              : `<div class="bks-wishlist-card-img-placeholder">BKS</div>`}
            <div class="bks-wishlist-card-info">
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

  /* ── Boot ── */
  function init() {
    importSharedWishlist();
    initTabs();
    initHeartButtons();
    renderWishlistPanel();
    initReferralCopy();
    initCountdown();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  /* Expose wishlist API for theme use */
  window.BKSMember = { wlToggle, wlHas, wlLoad, renderWishlistPanel };
})();
