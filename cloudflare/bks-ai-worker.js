/**
 * BKS Multi-Agent Worker — bks-agent.bakabo.workers.dev
 * SORGENTE DI VERITÀ — v20/06/2026
 * Per aggiornare: copia il contenuto nell'editor Cloudflare → Deploy.
 *
 * KV binding richiesto: BKS_AGENT_KV
 * Secrets: OPENAI_API_KEY, SHOPIFY_DOMAIN, SHOPIFY_TOKEN, SHOPIFY_API_VERSION
 *
 * Aggiornamenti 20/06/2026:
 *   - Tier Metal: Lead/Iron/Brass/Silver/Gold (da subscriber/drop/archive)
 *   - Agente Try-On Camerino (intent "tryon") — tier Brass+ required
 *   - Personalizzazione: tier Brass/Silver/Gold (era Subscriber/Drop/Archive)
 *   - BKS_BRAND: sistema completo, app 12 configurate, tema TM04 v20/06/2026
 *   - Greeting aggiornato con menzione Try-On + tier Metal
 */

var __defProp = Object.defineProperty;
var __name = (target, value) => __defProp(target, "name", { value, configurable: true });

// ── memory.js ────────────────────────────────────────────────────────────────
var HISTORY_MAX = 40;
var TTL_PROFILE  = 60 * 60 * 24 * 180;
var TTL_HISTORY  = 60 * 60 * 24 * 90;
var TTL_METRICS  = 60 * 60 * 24 * 365;

var BKSMemory = class {
  static { __name(this, "BKSMemory"); }
  constructor(kv) { this.kv = kv; }

  async getProfile(id) {
    return await this.kv.get(`customer:${id}:profile`, "json")
      ?? { tier: "none", preferences: {}, interaction_count: 0, last_seen: null };
  }
  async saveProfile(id, updates) {
    const cur = await this.getProfile(id);
    const p = { ...cur, ...updates, interaction_count: cur.interaction_count + 1, last_seen: new Date().toISOString() };
    await this.kv.put(`customer:${id}:profile`, JSON.stringify(p), { expirationTtl: TTL_PROFILE });
    return p;
  }
  async getHistory(id) {
    return await this.kv.get(`customer:${id}:history`, "json") ?? [];
  }
  async appendHistory(id, turn) {
    const h = await this.getHistory(id);
    h.push({ ...turn, ts: new Date().toISOString() });
    await this.kv.put(`customer:${id}:history`, JSON.stringify(h.slice(-HISTORY_MAX)), { expirationTtl: TTL_HISTORY });
  }
  async getContextMessages(id, n = 10) {
    const h = await this.getHistory(id);
    return h.slice(-n).map(t => ({ role: t.role, content: t.content }));
  }
  async getMetrics(name) {
    return await this.kv.get(`agent:${name}:metrics`, "json")
      ?? { calls: 0, resolved: 0, escalated: 0, positive: 0, negative: 0, total_ms: 0 };
  }
  async recordCall(name, { resolved, escalated, sentiment, ms }) {
    const m = await this.getMetrics(name);
    await this.kv.put(`agent:${name}:metrics`, JSON.stringify({
      calls:     m.calls     + 1,
      resolved:  m.resolved  + (resolved   ? 1 : 0),
      escalated: m.escalated + (escalated  ? 1 : 0),
      positive:  m.positive  + (sentiment === "positive" ? 1 : 0),
      negative:  m.negative  + (sentiment === "negative" ? 1 : 0),
      total_ms:  m.total_ms  + (ms || 0),
    }), { expirationTtl: TTL_METRICS });
  }
  async getCatalog() {
    return await this.kv.get("system:catalog_snapshot", "json") ?? null;
  }
  async saveEvalReport(report) {
    await this.kv.put("system:eval_report", JSON.stringify(report), { expirationTtl: TTL_METRICS });
  }
  async getEvalReport() {
    return await this.kv.get("system:eval_report", "json") ?? null;
  }
};

// ── agents.js ────────────────────────────────────────────────────────────────
var OPENAI_URL = "https://api.openai.com/v1/chat/completions";
var MODEL      = "gpt-4o";

var BKS_BRAND = `
BKS Studio — wearable art, on demand. Venduto su bakabo.club (BakAbo container).
Modello: made-to-order, stampa edge-to-edge AOP (All Over Print). Produzione 7-14 giorni, spedizione 3-5 giorni.
Fornitore principale: Printify. Nessun magazzino fisico — ogni pezzo è prodotto all'ordine.

SISTEMA BKS (aggiornato 20/06/2026):
- Tema live: TM04 v20/06/2026 (id 202392961362) — 20 file deployati, 8 sezioni attive
- Try-On Camerino: disponibile per tier Brass+ alla pagina /pages/bks-members
- Members Area: /pages/bks-members — dashboard tier, wishlist, Try-On, accesso anticipato drop
- AI Assistant embed: attivo su product pages + section dedicata
- App attive: Search & Discovery (5 filtri, 19 sinonimi), Flow (9 workflow), Essential Announcer,
  Selecty (EN/IT), Judge.me Reviews, Messaging (email automation)
- Contatto: crew@bakabo.club
`;

var BKS_COLLECTIONS = `
8 COLLEZIONI EDITORIALI BKS STUDIO (catalogo verificato 2026-06-20):

1. BKS HOURS #c8c4be — Contemplazione urbana, registro iperrealista. AI-art pittura iperrealista: luci città, silenzio interiore, vita quotidiana. Prodotti: puffer, sneakers, swim trunks, travel bag, hoodie, lounge pants, athletic shorts, racerback dress, tee. Tag: collection:hours.

2. BKS GLYPH #d4a030 — DNA grafico del brand. Alfabeto visivo proprietario: simboli astratti, frammenti a mano, geroglifici inventati. Collezione molto ampia. Prodotti: puffer, swim trunks, swimwear, backpack, hoodie, travel bag, lounge pants, windbreaker, racerback dress, sneakers, athletic shorts. Tag: collection:glyph.

3. BKS MARKER #c04418 — Grafica urbana gestuale. Pennello, muro, segno: drip, stroke, color block. Prodotti: puffer, travel bag, swim trunks, racerback dress, lounge pants, hoodie, swimwear, sneakers, athletic shorts, windbreaker, tee. Tag: collection:marker.

4. BKS RIVIERA #0ca898 — Resort mediterraneo permanente. Sale, sole, terracotta, blu profondo. Prodotti: puffer, swimwear, swim trunks, racerback dress, travel bag, sneakers, athletic shorts, windbreaker. Tag: collection:riviera.

5. BKS PULSE #8888cc — Collezione ottica. Ritmo, vibrazione, moto visivo. Ripetizione geometrica, campi cinetici. Prodotti: puffer, racerback dress, swim trunks, swimwear, sneakers, flip flops, travel bag, hoodie, windbreaker, lounge pants, athletic shorts. Tag: collection:pulse.

6. BKS TOKEN #9828d8 — Collezione arcade. Pixel, game, campo digitale. Low-bit visual language, colore elettronico. Prodotti: puffer, sneakers, windbreaker, swim trunks, racerback dress, athletic shorts. Tag: collection:token.

7. BKS FLAG #c82020 — Pop-collage. Campi astratti, colore codificato, blocchi grafici. Energia Dada. Prodotti: puffer, racerback dress, hoodie, sneakers, swim trunks, windbreaker, flip flops, travel bag, lounge pants, athletic shorts. Tag: collection:flag.

8. BKS ORIGIN #489808 — COLLEZIONE PIÙ AMPIA (33 prodotti, serie naif). Mondi immaginari, storie disegnate, memoria inventata. Illustrazione flat, figure organiche. Prodotti: puffer(9), hoodie(5), sneakers(5), swim trunks(3), racerback dress(3), lounge pants(3), windbreaker(2), swimwear, travel bag, athletic shorts. Tag: collection:origin.
`;

var BKS_PRODUCTS = `
TIPI PRODOTTO ATTIVI:
- Sneakers (all-over print, graphic low-top)
- Swim Trunks (quick-dry, edge-to-edge)
- Swimwear / One-Piece Swimsuit
- Puffer Jacket (AOP quilted outerwear)
- Windbreaker (technical shell)
- Athletic Shorts (long cut)
- Lounge Pants
- Pullover Hoodie
- Racerback Dress
- Travel Bag (impermeabile)
- Backpack (multi-compartment)
- Flip Flop
- T-Shirt

POLICY CHIAVE:
- Resi: 30 giorni dalla consegna
- Personalizzazione testo: disponibile per tier Brass/Silver/Gold. Costo +€15.
- Try-On Camerino virtuale: disponibile per tier Brass+ (3+ ordini)
- EU Representative: presente
- Nessun GTIN — made-to-order custom product
- Contatto: crew@bakabo.club
`;

async function callOpenAI(env, systemPrompt, messages) {
  const r = await fetch(OPENAI_URL, {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${env.OPENAI_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ model: MODEL, temperature: 0.4, messages: [{ role: "system", content: systemPrompt }, ...messages] }),
  });
  if (!r.ok) throw new Error(`OpenAI ${r.status}: ${await r.text()}`);
  const data = await r.json();
  return data.choices[0].message.content.trim();
}
__name(callOpenAI, "callOpenAI");

function detectSentiment(text) {
  const pos = /grazie|perfetto|ottimo|capito|ok|super|bravo/i.test(text);
  const neg = /non capisco|sbagliato|ripeti|errore|problema|non funziona/i.test(text);
  return pos ? "positive" : neg ? "negative" : "neutral";
}
__name(detectSentiment, "detectSentiment");

async function catalogAgent({ message, history, catalog, env, pageUrl, productTitle }) {
  const liveCatalog = catalog
    ? `CATALOGO LIVE (aggiornato ${catalog.updated_at}, ${catalog.product_count} prodotti attivi):\n`
      + catalog.products.slice(0, 30).map(
          p => `- ${p.title} | tipo: ${p.type} | €${p.variants?.[0]?.price ?? "?"} | handle: ${p.handle}`
        ).join("\n")
    : "Snapshot live non disponibile — usa la knowledge base statica sotto.";

  const pageContext = [
    pageUrl      ? `Pagina visitata dal cliente: ${pageUrl}` : "",
    productTitle ? `Prodotto attualmente visualizzato: ${productTitle}` : "",
  ].filter(Boolean).join("\n");

  const system = `Sei il BKS Catalog Agent per bakabo.club — wearable art, on demand.
Rispondi SOLO su: prodotti, collezioni, disponibilità, prezzi, caratteristiche, tag.
Se la domanda riguarda ordini/resi/spedizioni → rispondi SOLO: [ESCALATE:support]
Se riguarda personalizzazioni → rispondi SOLO: [ESCALATE:customization]
Tono: editoriale, essenziale, italiano. Sii preciso e conciso.

${BKS_BRAND}
${BKS_COLLECTIONS}
${BKS_PRODUCTS}

${pageContext ? "CONTESTO PAGINA CLIENTE:\n" + pageContext + "\n" : ""}
${liveCatalog}`;

  const reply = await callOpenAI(env, system, [...history, { role: "user", content: message }]);
  const escalate = reply.startsWith("[ESCALATE:");
  return { reply: escalate ? null : reply, resolved: !escalate, escalate, sentiment: detectSentiment(message) };
}
__name(catalogAgent, "catalogAgent");

async function customAgent({ message, customerProfile, history, catalog, env }) {
  const tier    = customerProfile?.tier ?? "none";
  const allowed = ["brass", "silver", "gold"].includes(tier);
  if (!allowed) {
    const msg = tier === "none"
      ? "La personalizzazione è disponibile per i membri BKS Brass e superiori. Crea un account e completa almeno 3 ordini per sbloccare questo servizio."
      : `La personalizzazione richiede il tier Brass (3+ ordini). Il tuo tier attuale è ${tier.charAt(0).toUpperCase() + tier.slice(1)}. Continua a ordinare per salire di livello!`;
    return { reply: msg, resolved: true, escalate: false, sentiment: "neutral" };
  }
  const system = `Sei il BKS Customization Agent.
Gestisci richieste di personalizzazione prodotti BKS: testo su fronte, retro o manica.
Costo aggiuntivo standard: +€15 per personalizzazione testo.
Flow:
1. Chiedi quale prodotto e colore/taglia
2. Chiedi il testo e la posizione (fronte / retro / manica sinistra / destra)
3. Conferma i dettagli e il costo extra
4. Rispondi SOLO con: [CUSTOM_READY: prodotto=X, testo=Y, posizione=Z, taglia=W] quando tutto è confermato

Tier cliente: ${tier}
Tono: esclusivo, diretto, brand BKS.`;
  const reply = await callOpenAI(env, system, [...history, { role: "user", content: message }]);
  const ready   = reply.startsWith("[CUSTOM_READY:");
  const escalate= reply.startsWith("[ESCALATE:");
  return { reply: ready || escalate ? null : reply, resolved: ready, escalate, customPayload: ready ? reply : null, sentiment: detectSentiment(message) };
}
__name(customAgent, "customAgent");

async function supportAgent({ message, customerProfile, history, env }) {
  const system = `Sei il BKS Support Agent per bakabo.club.
Gestisci: stato ordini, resi (30 giorni dalla consegna), spedizioni (MTO: 7-14 giorni produzione + 3-5 spedizione), policy.
Se la richiesta richiede accesso all'ordine specifico, chiedi il numero ordine o email.
Se non riesci a risolvere, rispondi SOLO con: [ESCALATE:human]
Tono: professionale, empatico, italiano.
Tier cliente: ${customerProfile?.tier ?? "none"}
Per assistenza umana diretta: crew@bakabo.club`;
  const reply   = await callOpenAI(env, system, [...history, { role: "user", content: message }]);
  const escalate= reply.includes("[ESCALATE:human]");
  return { reply: escalate ? null : reply, resolved: !escalate, escalate, sentiment: detectSentiment(message) };
}
__name(supportAgent, "supportAgent");

async function tierAgent({ message, customerProfile, env }) {
  const tier = customerProfile?.tier ?? "none";
  const info = {
    none:   "Non sei ancora un membro BKS. Crea un account su bakabo.club — al primo acquisto diventi Lead ◎ e accedi alla wishlist e alla newsletter esclusiva.",
    lead:   "Sei BKS Lead ◎ — benvenuto nel club. Hai accesso alla wishlist e alla newsletter. Completa 1-2 ordini per salire a Iron ⬡ e sbloccare le raccomandazioni AI personalizzate.",
    iron:   "Sei BKS Iron ⬡ — storico taglie attivo, raccomandazioni AI di base. Prossimo tier: Brass ◈ (3+ ordini) — sblocchi il Try-On Camerino e l'accesso anticipato ai drop di 48h.",
    brass:  "Sei BKS Brass ◈ — AI Personal Shopper attivo, Try-On Camerino disponibile (/pages/bks-members), accesso anticipato ai drop +48h. Prossimo tier: Silver ◇ (6+ ordini).",
    silver: "Sei BKS Silver ◇ — drop curati con accesso +24h, archivio completo collezioni, personalizzazione testo avanzata (+€15). Prossimo tier: Gold ✦ (11+ ordini).",
    gold:   "Sei BKS Gold ✦ — massimo accesso: drop VIP privati, curation white-glove, co-creazione con BKS Studio. Sei al vertice del sistema Metal.",
  };
  return { reply: info[tier] || info.none, resolved: true, escalate: false, sentiment: "neutral" };
}
__name(tierAgent, "tierAgent");

async function tryonAgent({ message, customerProfile, env }) {
  const tier = customerProfile?.tier ?? "none";
  const eligible = ["brass", "silver", "gold"].includes(tier);
  if (!eligible) {
    const needed = tier === "none" || tier === "lead"
      ? "Sblocca il Try-On Camerino completando 3 ordini su bakabo.club (tier Brass ◈)."
      : "Tier Iron ⬡ non include ancora il Try-On. Completa 3 ordini totali per salire a Brass ◈ e accedere.";
    return { reply: needed, resolved: true, escalate: false, sentiment: "neutral" };
  }
  return {
    reply: `Il Try-On Camerino BKS è disponibile per il tuo tier ${tier.charAt(0).toUpperCase() + tier.slice(1)} ✦\n\nAccedi da: bakabo.club/pages/bks-members → tab Try-On.\nPuoi provare virtualmente tutti i capi attivi del catalogo BKS. Se hai bisogno di supporto: crew@bakabo.club`,
    resolved: true, escalate: false, sentiment: "positive",
  };
}
__name(tryonAgent, "tryonAgent");

// ── evaluator.js ─────────────────────────────────────────────────────────────
var AGENTS    = ["catalog", "custom", "support", "tier", "tryon", "orchestrator"];
var THRESHOLD = 60;

function clamp(v, min, max) { return Math.min(Math.max(v, min), max); }
__name(clamp, "clamp");

function scoreAgent(m) {
  if (!m.calls) return { score: null, issue: "no_data" };
  const resolution    = m.resolved / m.calls;
  const satisfaction  = clamp((m.positive - m.negative) / m.calls, -1, 1);
  const avgMs         = m.calls ? m.total_ms / m.calls : 0;
  const speed         = 1 - clamp(avgMs / 5000, 0, 1);
  const escalationPen = m.escalated / m.calls;
  const score = Math.round((resolution * 0.4 + (satisfaction + 1) / 2 * 0.3 + speed * 0.2 - escalationPen * 0.1) * 100);
  const issues = [];
  if (resolution < 0.6)        issues.push(`bassa risoluzione (${(resolution * 100).toFixed(0)}%)`);
  if (m.negative > m.positive)  issues.push("sentiment negativo prevalente");
  if (avgMs > 4000)             issues.push(`risposta lenta (avg ${avgMs.toFixed(0)}ms)`);
  if (escalationPen > 0.3)      issues.push(`alto tasso escalation (${(escalationPen * 100).toFixed(0)}%)`);
  return { score, issues, resolution, satisfaction, speed, calls: m.calls };
}
__name(scoreAgent, "scoreAgent");

async function runEvaluation(memory) {
  const report = { date: new Date().toISOString(), agents: [], overall: 0, flags: [] };
  let scoredCount = 0, totalScore = 0;
  for (const name of AGENTS) {
    const metrics        = await memory.getMetrics(name);
    const { score, issues, ...stats } = scoreAgent(metrics);
    report.agents.push({ name, score, issues: issues ?? [], ...stats, raw: metrics });
    if (score !== null) {
      scoredCount++;
      totalScore += score;
      if (score < THRESHOLD) report.flags.push({ agent: name, score, issues });
    }
  }
  report.overall = scoredCount ? Math.round(totalScore / scoredCount) : null;
  await memory.saveEvalReport(report);
  return report;
}
__name(runEvaluation, "runEvaluation");

// ── orchestrator.js ──────────────────────────────────────────────────────────
var OPENAI_URL2 = "https://api.openai.com/v1/chat/completions";

async function classifyIntent(env, message) {
  const r = await fetch(OPENAI_URL2, {
    method: "POST",
    headers: { "Authorization": `Bearer ${env.OPENAI_API_KEY}`, "Content-Type": "application/json" },
    body: JSON.stringify({
      model: "gpt-4o-mini",
      temperature: 0,
      messages: [{
        role: "system",
        content: `Classifica il messaggio in UNO di questi intent (rispondi SOLO con il nome):
catalog       → domande su prodotti, collezioni, prezzi, disponibilità, Try-On
customization → richieste di personalizzazione, testo su capo, custom order
support       → ordini, spedizioni, resi, rimborsi, problemi tecnici
tier          → domande sul proprio tier/membership BKS, livello Metal, sblocchi
tryon         → richiesta accesso Try-On Camerino, virtual fitting
greeting      → saluti generici senza richiesta specifica`,
      }, { role: "user", content: message }],
    }),
  });
  const data = await r.json();
  return (data.choices?.[0]?.message?.content ?? "support").trim().toLowerCase();
}
__name(classifyIntent, "classifyIntent");

async function route(intent, context) {
  switch (intent) {
    case "catalog":       return catalogAgent(context);
    case "customization": return customAgent(context);
    case "tier":          return tierAgent(context);
    case "tryon":         return tryonAgent(context);
    case "greeting":      return { reply: "Ciao! Sono l'assistente BKS. Posso aiutarti con prodotti, collezioni, il tuo tier Metal, il Try-On Camerino, personalizzazioni o ordini.", resolved: true, escalate: false, sentiment: "neutral" };
    default:              return supportAgent(context);
  }
}
__name(route, "route");

async function refreshCatalog(env, memory) {
  const url = `https://${env.SHOPIFY_DOMAIN}/admin/api/${env.SHOPIFY_API_VERSION}/products.json?limit=250&fields=id,title,handle,status,variants,tags,product_type`;
  const r = await fetch(url, { headers: { "X-Shopify-Access-Token": env.SHOPIFY_TOKEN } });
  if (!r.ok) return;
  const { products } = await r.json();
  const snapshot = {
    updated_at:    new Date().toISOString(),
    product_count: products.length,
    products: products.filter(p => p.status === "active").map(p => ({
      id:       p.id,
      title:    p.title,
      handle:   p.handle,
      type:     p.product_type,
      tags:     p.tags,
      variants: (p.variants || []).map(v => ({ id: v.id, title: v.title, price: v.price, sku: v.sku })),
    })),
  };
  await memory.kv.put("system:catalog_snapshot", JSON.stringify(snapshot), { expirationTtl: 90000 });
  return snapshot;
}
__name(refreshCatalog, "refreshCatalog");

// ── CORS ─────────────────────────────────────────────────────────────────────
const ALLOWED_ORIGINS = ["https://bakabo.club", "https://www.bakabo.club"];

function corsHeaders(origin) {
  const allowed = ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0];
  return {
    "Access-Control-Allow-Origin":  allowed,
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, X-BKS-Assistant-Token",
    "Access-Control-Max-Age":       "86400",
  };
}

// ── Main export ───────────────────────────────────────────────────────────────
var orchestrator_default = {
  async fetch(request, env) {
    const memory = new BKSMemory(env.BKS_AGENT_KV);
    const url    = new URL(request.url);
    const origin = request.headers.get("Origin") || "";
    const cors   = corsHeaders(origin);

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: cors });
    }

    // ── Read endpoints ────────────────────────────────────────────────────────
    if (request.method === "GET" && url.pathname === "/eval") {
      const report = await memory.getEvalReport();
      return Response.json(report ?? { message: "Nessun report disponibile" }, { headers: cors });
    }
    if (request.method === "GET" && url.pathname === "/catalog") {
      const cat = await memory.getCatalog();
      return Response.json(cat ?? { message: "Catalog non disponibile" }, { headers: cors });
    }
    if (request.method === "GET" && url.pathname.startsWith("/memory/")) {
      const id      = url.pathname.split("/")[2];
      const profile = await memory.getProfile(id);
      const history = await memory.getHistory(id);
      return Response.json({ profile, turns: history.length, last: history.at(-1) ?? null }, { headers: cors });
    }

    // ── Chat endpoint ─────────────────────────────────────────────────────────
    if (request.method === "POST" && url.pathname === "/chat") {
      let body;
      try { body = await request.json(); }
      catch { return new Response("Bad JSON", { status: 400, headers: cors }); }

      const { message, customer_id = "anonymous", customer_tier, page_url = "", product_title = "" } = body;
      if (!message) return new Response("Missing message", { status: 400, headers: cors });

      try {
      const t0 = Date.now();
      const [profile, history, catalog] = await Promise.all([
        memory.getProfile(customer_id),
        memory.getContextMessages(customer_id, 10),
        memory.getCatalog(),
      ]);
      if (customer_tier) profile.tier = customer_tier;

      const intent = await classifyIntent(env, message);
      const result = await route(intent, {
        message,
        customerProfile: profile,
        history,
        catalog,
        env,
        pageUrl:      page_url,
        productTitle: product_title,
      });
      const ms = Date.now() - t0;

      await Promise.all([
        memory.appendHistory(customer_id, { role: "user",      content: message }),
        memory.appendHistory(customer_id, { role: "assistant", content: result.reply ?? "[escalated]", agent: intent }),
        memory.saveProfile(customer_id, { tier: profile.tier }),
        memory.recordCall(intent, { resolved: result.resolved, escalated: result.escalate, sentiment: result.sentiment, ms }),
      ]);

      return Response.json({
        reply:          result.reply ?? "Richiesta inoltrata a un operatore BKS. Contattaci a crew@bakabo.club.",
        intent,
        resolved:       result.resolved,
        escalate:       result.escalate,
        custom_payload: result.customPayload ?? null,
        ms,
      }, { headers: cors });
      } catch (err) {
        console.error("[BKS Chat] Error:", err.message);
        return Response.json({
          reply: "Servizio temporaneamente non disponibile. Contattaci a crew@bakabo.club.",
          error: err.message,
        }, { status: 503, headers: cors });
      }
    }

    return new Response("BKS Multi-Agent v2.0 — /chat per le domande", { status: 200, headers: cors });
  },

  // Cron: ogni giorno alle 12:00 CET (0 10 * * *) — refresh catalogo + valutazione
  async scheduled(event, env, ctx) {
    const memory = new BKSMemory(env.BKS_AGENT_KV);
    ctx.waitUntil((async () => {
      const [snapshot, report] = await Promise.all([
        refreshCatalog(env, memory),
        runEvaluation(memory),
      ]);
      console.log(`[BKS Cron] Catalog: ${snapshot?.product_count ?? "ERR"} prodotti | Score: ${report.overall ?? "N/A"}`);
      if (report.flags?.length) {
        console.warn(`[BKS Cron] Agenti sotto soglia: ${report.flags.map(f => f.agent).join(", ")}`);
      }
    })());
  },
};

export { orchestrator_default as default };
