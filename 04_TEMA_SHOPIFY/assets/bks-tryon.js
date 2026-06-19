(function () {
  const root = document.querySelector("[data-bks-camerino]");
  if (!root) return;

  const cfg = window.BKS_TRYON || {};
  const apiBase = (cfg.apiBase || "http://127.0.0.1:8010/api").replace(/\/$/, "");

  const state = {
    product: null,
    background: "travertine_golden_hour",
    requestId: null,
    eventSource: null
  };

  const els = {
    backgrounds: root.querySelectorAll("[data-bks-bg]"),
    preview: root.querySelector("[data-bks-preview]"),
    productImg: root.querySelector("[data-bks-preview-product]"),
    finalImg: root.querySelector("[data-bks-preview-final]"),
    status: root.querySelector("[data-bks-status]"),
    progress: root.querySelector("[data-bks-progress]"),
    generate: root.querySelector("[data-bks-generate]"),
    crew: root.querySelector("[data-bks-crew]"),
    steps: root.querySelectorAll("[data-bks-step]")
  };

  function setStep(n) {
    els.steps.forEach((s) => s.classList.toggle("is-active", Number(s.dataset.bksStep) <= n));
  }

  function setStatus(text, progress) {
    if (els.status) els.status.textContent = text;
    if (els.progress) els.progress.style.width = Math.max(1, Math.min(100, progress || 1)) + "%";
  }

  function selectProduct(btn) {
    root.querySelectorAll(".bks-wishlist__item").forEach(b => b.classList.remove("is-selected"));
    btn.classList.add("is-selected");
    state.product = {
      product_id: btn.dataset.productId,
      product_handle: btn.dataset.productHandle || "",
      product_title: btn.dataset.productTitle,
      product_image_url: btn.dataset.productImage || ""
    };
    if (state.product.product_image_url && els.productImg) {
      els.productImg.src = state.product.product_image_url;
    }
    // Mood: shift camerino accent to product's collection colour
    const mood = btn.dataset.mood;
    if (mood) {
      root.style.setProperty("--bks-accent", mood);
      if (window.BKSMember) window.BKSMember.setMood(btn.dataset.collection);
    }
    setStep(1);
    setStatus("Capo selezionato. Scegli uno sfondo editoriale.", 8);
    if (els.generate) els.generate.disabled = false;
  }

  function selectBackground(btn) {
    root.querySelectorAll(".bks-bg-option").forEach(b => b.classList.remove("is-selected"));
    btn.classList.add("is-selected");
    state.background = btn.dataset.bksBg;
    if (els.preview) els.preview.dataset.bg = state.background;
    setStep(2);
    setStatus("Sfondo pronto. Anteprima immediata disponibile.", 15);
  }

  function startEvents(requestId) {
    if (state.eventSource) state.eventSource.close();
    const url = `${apiBase}/tryon/events/${requestId}`;
    state.eventSource = new EventSource(url);

    state.eventSource.onmessage = (ev) => {
      const data = JSON.parse(ev.data);
      setStatus(data.message || "Rendering", data.progress || 1);

      if (data.event_type === "ready") {
        fetch(`${apiBase}/tryon/status/${requestId}`)
          .then(r => r.json())
          .then(status => {
            if (status.render_url && els.finalImg && els.preview) {
              els.finalImg.src = status.render_url + "?t=" + Date.now();
              els.preview.classList.add("has-final");
              setStep(4);
              setStatus("Render pronto. Salvato nel Camerino.", 100);
              if (els.crew) els.crew.disabled = false;
            }
          });
        state.eventSource.close();
      }

      if (data.event_type === "error") {
        setStatus("Render non completato. La preview resta salvata.", 100);
        if (els.crew) els.crew.disabled = false;
        state.eventSource.close();
      }
    };

    state.eventSource.onerror = () => {
      setStatus("Connessione lenta. La preview resta attiva.", 80);
    };
  }

  function generate() {
    if (!state.product) {
      setStatus("Seleziona prima un capo dalla wishlist.", 1);
      return;
    }

    if (els.preview) els.preview.classList.remove("has-final");
    if (els.preview) els.preview.dataset.bg = state.background;
    setStep(3);
    setStatus("Preview immediata attiva. Render AI in corso.", 22);
    if (els.generate) els.generate.disabled = true;
    if (els.crew) els.crew.disabled = true;

    const payload = Object.assign({}, state.product, {
      customer_id: cfg.customerId || "guest",
      customer_email: cfg.customerEmail || "",
      background_code: state.background,
      user_note: ""
    });

    fetch(`${apiBase}/tryon/start`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(payload)
    })
    .then(r => {
      if (!r.ok) throw new Error("Errore API try-on");
      return r.json();
    })
    .then(data => {
      state.requestId = data.request_id;
      startEvents(data.request_id);
    })
    .catch(err => {
      setStatus("API non raggiungibile. Preview locale attiva.", 100);
      if (els.generate) els.generate.disabled = false;
      if (els.crew) els.crew.disabled = false;
      console.warn("[BKS Camerino] API offline:", err.message);
    });
  }

  function requestCrew() {
    if (!state.requestId) return;
    fetch(`${apiBase}/tryon/request-crew/${state.requestId}`, { method: "POST" })
      .then(r => r.json())
      .then(() => setStatus("Richiesta inviata alla crew BKS.", 100))
      .catch(() => setStatus("Richiesta non inviata. Riprova più tardi.", 100));
  }

  // Event delegation — wishlist items are loaded dynamically via bks-member.js
  const wishlistEl = root.querySelector("[data-bks-wishlist]");
  if (wishlistEl) {
    wishlistEl.addEventListener("click", e => {
      const btn = e.target.closest(".bks-wishlist__item");
      if (btn) selectProduct(btn);
    });
  }

  els.backgrounds.forEach(btn => {
    btn.addEventListener("click", () => selectBackground(btn));
  });

  if (els.generate) els.generate.addEventListener("click", generate);
  if (els.crew) els.crew.addEventListener("click", requestCrew);

  setStatus("Scegli un capo dalla wishlist.", 1);
  setStep(0);
})();
