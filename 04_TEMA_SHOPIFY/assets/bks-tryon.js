/* BKS Try-On Engine v1 — canvas overlay, drag+resize, mobile pinch-zoom */
(function () {
  'use strict';

  var canvas, ctx, statusEl;
  var userPhoto = null;
  var garmentImg = null;
  var garmentState = { x: 0, y: 0, w: 0, h: 0, aspect: 1 };
  var drag = { active: false, startX: 0, startY: 0, originX: 0, originY: 0 };
  var resizing = false;
  var pinch = { active: false, dist: 0, w0: 0, h0: 0 };

  function init() {
    canvas = document.getElementById('bks-tryon-canvas');
    statusEl = document.querySelector('[data-bks-status]');
    if (!canvas) return;
    ctx = canvas.getContext('2d');

    // Garment selected from wishlist via custom event
    document.addEventListener('bks:tryon:garment', function (e) {
      loadGarment(e.detail.imageUrl, e.detail.title);
    });

    // Garment selected via data-tryon-select click
    document.addEventListener('click', function (e) {
      var item = e.target.closest('[data-tryon-select]');
      if (!item) return;
      var url = item.dataset.tryonImage;
      var title = item.dataset.tryonTitle || 'garment';
      if (url) loadGarment(url, title);
    });

    // Download button
    document.addEventListener('click', function (e) {
      if (e.target.closest('[data-bks-tryon-download]')) {
        window.bksTryOnDownload();
      }
    });

    canvas.addEventListener('mousedown',  onDragStart);
    window.addEventListener('mousemove',  onDragMove);
    window.addEventListener('mouseup',    onDragEnd);
    canvas.addEventListener('touchstart', onTouchStart, { passive: false });
    canvas.addEventListener('touchmove',  onTouchMove,  { passive: false });
    canvas.addEventListener('touchend',   onTouchEnd);
  }

  function setStatus(msg) {
    if (statusEl) statusEl.textContent = msg;
  }

  // Called when user uploads a valid photo (from dashboard JS)
  window.bksTryOnSetPhoto = function (imgEl) {
    userPhoto = imgEl;
    resizeCanvas();
    drawAll();
    setStatus(garmentImg ? 'Drag the garment to position it.' : 'Choose a garment from your wishlist.');
    var dlBtn = document.querySelector('[data-bks-tryon-download]');
    if (dlBtn) dlBtn.style.display = 'inline-flex';
  };

  function resizeCanvas() {
    if (!userPhoto || !canvas) return;
    var container = canvas.parentElement;
    var maxW = container ? container.clientWidth : 480;
    var maxH = Math.min(maxW * 1.5, window.innerHeight * 0.7);
    var ratio = userPhoto.naturalWidth / userPhoto.naturalHeight;
    var w = maxW;
    var h = w / ratio;
    if (h > maxH) { h = maxH; w = h * ratio; }
    canvas.width  = Math.round(w);
    canvas.height = Math.round(h);
    canvas.style.width  = Math.round(w) + 'px';
    canvas.style.height = Math.round(h) + 'px';
  }

  function loadGarment(url, title) {
    setStatus('Loading ' + title + '...');
    var img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = function () {
      garmentImg = img;
      garmentState.aspect = img.naturalWidth / img.naturalHeight;
      // Default: 55% canvas width, centered, upper-body zone
      garmentState.w = Math.round(canvas.width * 0.55);
      garmentState.h = Math.round(garmentState.w / garmentState.aspect);
      garmentState.x = Math.round((canvas.width  - garmentState.w) / 2);
      garmentState.y = Math.round(canvas.height  * 0.18);
      drawAll();
      setStatus('Drag to position  |  Pinch or corner handle to resize');
      // highlight selected item
      document.querySelectorAll('[data-tryon-select]').forEach(function (el) {
        el.classList.toggle('is-selected', el.dataset.tryonImage === url);
      });
    };
    img.onerror = function () {
      setStatus('Could not load garment image. Try another item.');
    };
    img.src = url;
  }

  function drawAll() {
    if (!ctx || !canvas) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (userPhoto) {
      ctx.drawImage(userPhoto, 0, 0, canvas.width, canvas.height);
    } else {
      ctx.fillStyle = '#efeae0';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
    }

    if (!garmentImg) return;

    // Garment with reduced opacity while dragging
    ctx.save();
    ctx.globalAlpha = drag.active ? 0.72 : 0.92;
    ctx.drawImage(garmentImg, garmentState.x, garmentState.y, garmentState.w, garmentState.h);
    ctx.restore();

    // Selection border
    ctx.save();
    ctx.strokeStyle = 'rgba(201,183,156,0.85)';
    ctx.lineWidth = 1.5;
    ctx.setLineDash([5, 4]);
    ctx.strokeRect(garmentState.x, garmentState.y, garmentState.w, garmentState.h);
    ctx.restore();

    // Resize handle bottom-right
    var hx = garmentState.x + garmentState.w - 10;
    var hy = garmentState.y + garmentState.h - 10;
    ctx.fillStyle = '#c9b79c';
    ctx.fillRect(hx, hy, 18, 18);
    ctx.fillStyle = '#0a0a0a';
    ctx.font = 'bold 10px sans-serif';
    ctx.fillText('+', hx + 5, hy + 13);
  }

  function canvasXY(e) {
    var rect = canvas.getBoundingClientRect();
    var scaleX = canvas.width  / rect.width;
    var scaleY = canvas.height / rect.height;
    return {
      x: (e.clientX - rect.left) * scaleX,
      y: (e.clientY - rect.top)  * scaleY,
    };
  }

  function inHandle(cx, cy) {
    var hx = garmentState.x + garmentState.w - 10;
    var hy = garmentState.y + garmentState.h - 10;
    return cx >= hx && cx <= hx + 22 && cy >= hy && cy <= hy + 22;
  }

  function inGarment(cx, cy) {
    return cx >= garmentState.x && cx <= garmentState.x + garmentState.w
        && cy >= garmentState.y && cy <= garmentState.y + garmentState.h;
  }

  function onDragStart(e) {
    if (!garmentImg) return;
    var p = canvasXY(e);
    if (inHandle(p.x, p.y)) {
      resizing = true;
    } else if (inGarment(p.x, p.y)) {
      drag.active = true;
      drag.startX = p.x; drag.startY = p.y;
      drag.originX = garmentState.x; drag.originY = garmentState.y;
    }
  }

  function onDragMove(e) {
    if (!garmentImg) return;
    if (drag.active) {
      var p = canvasXY(e);
      garmentState.x = drag.originX + (p.x - drag.startX);
      garmentState.y = drag.originY + (p.y - drag.startY);
      drawAll();
    } else if (resizing) {
      var p2 = canvasXY(e);
      var newW = Math.max(60, p2.x - garmentState.x + 10);
      garmentState.w = newW;
      garmentState.h = Math.round(newW / garmentState.aspect);
      drawAll();
    }
  }

  function onDragEnd() {
    drag.active = false;
    resizing = false;
    drawAll();
  }

  function touchDist(t) {
    var dx = t[0].clientX - t[1].clientX;
    var dy = t[0].clientY - t[1].clientY;
    return Math.sqrt(dx * dx + dy * dy);
  }

  function onTouchStart(e) {
    if (!garmentImg) return;
    e.preventDefault();
    if (e.touches.length === 2) {
      pinch.active = true;
      pinch.dist   = touchDist(e.touches);
      pinch.w0     = garmentState.w;
      pinch.h0     = garmentState.h;
      drag.active  = false;
    } else if (e.touches.length === 1) {
      var t = e.touches[0];
      var p = canvasXY({ clientX: t.clientX, clientY: t.clientY });
      if (inHandle(p.x, p.y)) {
        resizing = true;
      } else if (inGarment(p.x, p.y)) {
        drag.active  = true;
        drag.startX  = p.x; drag.startY  = p.y;
        drag.originX = garmentState.x; drag.originY = garmentState.y;
      }
    }
  }

  function onTouchMove(e) {
    if (!garmentImg) return;
    e.preventDefault();
    if (pinch.active && e.touches.length === 2) {
      var d = touchDist(e.touches);
      var scale = d / pinch.dist;
      garmentState.w = Math.max(60, Math.round(pinch.w0 * scale));
      garmentState.h = Math.round(garmentState.w / garmentState.aspect);
      drawAll();
    } else if (drag.active && e.touches.length === 1) {
      var t = e.touches[0];
      var p = canvasXY({ clientX: t.clientX, clientY: t.clientY });
      garmentState.x = drag.originX + (p.x - drag.startX);
      garmentState.y = drag.originY + (p.y - drag.startY);
      drawAll();
    } else if (resizing && e.touches.length === 1) {
      var t2 = e.touches[0];
      var p2 = canvasXY({ clientX: t2.clientX, clientY: t2.clientY });
      var newW = Math.max(60, p2.x - garmentState.x + 10);
      garmentState.w = newW;
      garmentState.h = Math.round(newW / garmentState.aspect);
      drawAll();
    }
  }

  function onTouchEnd() {
    drag.active = false;
    resizing    = false;
    pinch.active = false;
    drawAll();
  }

  window.bksTryOnDownload = function () {
    if (!canvas || !userPhoto) return;
    var dataUrl = canvas.toDataURL('image/jpeg', 0.92);
    // iOS Safari: <a download> is ignored — open image in new tab so user can long-press → Save to Photos
    var isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
    if (isIOS) {
      var w = window.open();
      if (w) {
        w.document.write('<img src="' + dataUrl + '" style="max-width:100%;display:block;margin:auto"><p style="text-align:center;font-family:sans-serif;color:#888;font-size:13px">Tap and hold → Save to Photos</p>');
        w.document.close();
      }
      return;
    }
    var link = document.createElement('a');
    link.download = 'bks-tryon.jpg';
    link.href = dataUrl;
    link.click();
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
