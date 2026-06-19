// BKS dynamic collection/menu UX — generated 16JUN2026
(function () {
  'use strict';

  function safeJson(id) {
    var el = document.getElementById(id);
    if (!el) return null;
    try { return JSON.parse(el.textContent || '{}'); }
    catch (e) { return null; }
  }

  function contrastColor(hex) {
    if (!hex || hex.charAt(0) !== '#') return '#0A0A0A';
    var h = hex.replace('#','');
    if (h.length === 3) h = h.split('').map(function(c){ return c + c; }).join('');
    var r = parseInt(h.slice(0,2),16), g = parseInt(h.slice(2,4),16), b = parseInt(h.slice(4,6),16);
    var yiq = ((r * 299) + (g * 587) + (b * 114)) / 1000;
    return yiq >= 150 ? '#0A0A0A' : '#FAFAF7';
  }

  function applyContext(ctx) {
    if (!ctx) return;
    var root = document.documentElement;
    var accent = ctx.accent || '#C9B79C';
    var fg = ctx.foreground || contrastColor(accent);
    var hasCollection = ctx.hasCollectionContext === true || /bks-/.test(ctx.contextHandle || '');

    root.style.setProperty('--bks-active-accent', accent);
    root.style.setProperty('--bks-active-foreground', fg);
    // Header stays white — only the 3px accent bar changes color per collection
    root.style.setProperty('--bks-header-background', '#ffffff');
    root.style.setProperty('--bks-header-foreground', '#0A0A0A');
    root.style.setProperty('--bks-header-accent-bar', hasCollection ? accent : 'transparent');
    root.setAttribute('data-bks-context-handle', ctx.contextHandle || '');
    root.setAttribute('data-bks-page-type', ctx.pageType || '');
    root.setAttribute('data-bks-collection-context', hasCollection ? 'true' : 'false');

    var header = document.getElementById('bks-global-header');
    if (header) {
      header.setAttribute('data-bks-context', ctx.pageType || 'site');
      header.setAttribute('data-bks-context-handle', ctx.contextHandle || '');
      header.setAttribute('data-bks-tinted', hasCollection ? 'true' : 'false');
    }
  }

  function setupBack(ctx) {
    var btn = document.querySelector('[data-bks-back]');
    if (!btn) return;
    var fallback = (ctx && (ctx.parentUrl || ctx.collectionUrl)) || '/collections/all';
    btn.setAttribute('href', fallback);
    btn.addEventListener('click', function (event) {
      var ref = document.referrer;
      var sameHost = false;
      try { sameHost = ref && new URL(ref).hostname === window.location.hostname; } catch (e) {}
      if (sameHost && window.history.length > 1) {
        event.preventDefault();
        window.history.back();
      }
    });
  }

  function hideLocalizationAfterDetection() {
    // Kill ALL localization UI — single-market IT store, no selector needed anywhere
    var selectors = [
      'localization-form',
      'country-localization',
      'language-localization',
      '.localization-form',
      '.shopify-localization-form',
      'form[action*="/localization"]',
      '[data-localization-form]',
      '.disclosure.localization-selector'
    ];
    var forms = document.querySelectorAll(selectors.join(','));
    forms.forEach(function (el) {
      el.setAttribute('data-bks-locale-hidden', 'true');
      el.style.setProperty('display', 'none', 'important');
    });
    document.documentElement.setAttribute('data-bks-locale-detected', 'true');
  }

  function stylePreFooterSection() {
    // Find the section immediately before the footer and make it dark
    var footer = document.querySelector('footer.footer');
    if (!footer) return;
    var footerSection = footer.closest('.shopify-section');
    if (!footerSection) return;
    var prev = footerSection.previousElementSibling;
    if (prev && prev.classList.contains('shopify-section')) {
      prev.classList.add('bks-pre-footer');
    }
  }

  function boot() {
    var ctx = safeJson('bks-ai-context');
    applyContext(ctx);
    setupBack(ctx);
    hideLocalizationAfterDetection();
    stylePreFooterSection();
    window.BKS_AI_CONTEXT = ctx || {};
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
