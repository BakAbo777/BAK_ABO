/**
 * BKS Multi-Agent Worker — bks-agent.bakabo.workers.dev
 * SORGENTE DI VERITÀ — v21/06/2026 v4
 * Per aggiornare: copia il contenuto nell'editor Cloudflare → Deploy.
 *
 * KV binding richiesto: BKS_AGENT_KV
 * Secrets: OPENAI_API_KEY, SHOPIFY_DOMAIN, SHOPIFY_TOKEN, SHOPIFY_API_VERSION
 *
 * Aggiornamenti 21/06/2026 v4:
 *   - BKS Verse Platform aggiunta: /pages/verse, /pages/verse-hall, API verse.bakabo.club
 *   - verseAgent dedicato (intent "verse"): spiega la piattaforma poesia→oggetto
 *   - Video Canvas Hero ottimizzato (interno — direct video CSS, nessuna canvas)
 *   - Navigazione: /pages/verse e /pages/verse-hall aggiunte
 *   - classifyIntent: nuovo intent "verse" per domande sulla piattaforma poesia
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

SISTEMA BKS (aggiornato 21/06/2026 v4):
- Tema live: BKS TM04 V.22 (id 202392961362)
- Homepage: Video Hero (4 avatar in sequenza) → Piano Hero (8 tasti CDN) → Magazine → Reviews → Trust Strip
- Try-On Camerino virtuale: tier Brass+ → /pages/bks-members → tab Try-On
- Members Area: /pages/bks-members — dashboard tier Metal, wishlist, Try-On, accesso anticipato drop
- Gold Ring: cerchio animato intorno all'icona account, colore per tier (piombo→oro)
- AI Assistant: integrato nel menu di navigazione globale come voce "Ask BKS"
- BKS Verse: piattaforma poesia→oggetto, accessibile da /pages/verse (Brass+). Leaderboard mondiale su /pages/verse-hall. API: verse.bakabo.club
- App attive: Search & Discovery (5 filtri, 19 sinonimi), Flow (9 workflow), Essential Announcer,
  Judge.me Reviews, Messaging (email automation), Selecty
- Contatto: crew@bakabo.club

NAVIGAZIONE MENU:
- Desktop: CATALOG · COLLECTIONS (dropdown 8 collezioni) · ABOUT · … · [IT · EN] · Ask BKS
- Mobile: drawer con tutte le voci + selettore lingua IT/EN + Ask BKS
- Ask BKS è integrato nel menu — il pannello AI si apre direttamente dalla nav
- Selettore lingua IT · EN nel menu: switch tra italiano e inglese (Shopify Markets)

PAGINE CHIAVE DEL SITO:
- /collections/all → catalogo completo (202+ prodotti attivi)
- /collections/bks-hours → BKS Hours (contemplazione urbana)
- /collections/bks-glyph → BKS Glyph (alfabeto visivo BKS)
- /collections/bks-marker → BKS Marker (grafica urbana)
- /collections/bks-riviera → BKS Riviera (resort mediterraneo)
- /collections/bks-pulse → BKS Pulse (collezione ottica)
- /collections/bks-token → BKS Token (arcade/pixel)
- /collections/bks-flag → BKS Flag (pop-collage)
- /collections/bks-origin → BKS Origin (illustrazione naif, 33 prodotti)
- /pages/bks-members → Area Membri: tier dashboard, wishlist, Try-On Camerino
- /pages/verse → BKS Verse: invia un verso, il Giudice AI lo valuta, diventa un capo BKS (Brass+)
- /pages/verse-hall → BKS Verse Hall of Fame: leaderboard mondiale, 21 poeti storici, archivio vincitrici
- /pages/bks-ai-assistant → pagina dedicata BKS AI
- /pages/about-bakabo-1 → about BakAbo / BKS Studio
- /pages/contatti → contatto diretto
- /account → login / area account / livello Metal
- /cart → carrello
- /pages/faq → domande frequenti

LINGUA: Lo store è disponibile in italiano e inglese. Rileva la lingua del messaggio e rispondi nella stessa lingua.
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

// Compact bilingual synonym map — used by catalogAgent + navigationAgent
// Full reference: BKS_SKILL/skills/bakabo-italian-terminology/SKILL.md
var BKS_SYNONYMS = `
PRODUCT SYNONYMS (IT/EN → BKS official name):
- giacca / piumino / giubbotto / puffer / quilted jacket / bubble jacket → Puffer Jacket
- felpa / cappuccio / hoodie / sweatshirt / pullover → Pullover Hoodie
- pantaloncini / shorts / gym shorts / running shorts → Athletic Shorts
- costume intero / costumino / swimsuit / one-piece / bathing suit → Swimwear
- boxer mare / costume uomo / swim trunks / board shorts / surf shorts → Swim Trunks
- vestito / abito / dress / racerback / sporty dress → Racerback Dress
- scarpe / sneaker / kicks / graphic shoes → Sneakers
- borsa viaggio / borsone / duffel / weekender / travel bag → Travel Bag
- zaino / backpack / bookbag / rucksack → Backpack
- pantalone / jogger / sweatpants / lounge pants / track pants → Lounge Pants
- infradito / ciabatte / flip flops / slides / sandals → Flip Flops
- maglietta / maglia / tee / graphic tee → T-Shirt
- k-way / giacca vento / impermeabile / windbreaker / shell jacket → Windbreaker

COLLECTION KEYWORDS (IT/EN → BKS handle):
- ore / tempo / urbano / monochrome / city / grayscale → bks-hours (#c8c4be)
- glifi / simboli / segni / graphic / typographic / abstract marks → bks-glyph (#d4a030)
- pennarello / graffiti / muro / brushstroke / street art / gestural → bks-marker (#c04418)
- riviera / mare / estate / coastal / resort / Mediterranean / teal → bks-riviera (#0ca898)
- pulse / ottico / viola / geometric / optical / kinetic / hypnotic → bks-pulse (#8888cc)
- token / pixel / arcade / retro gaming / 8-bit / sci-fi / digital → bks-token (#9828d8)
- bandiera / rosso / pop / bold color / color block / dada → bks-flag (#c82020)
- origine / folklore / naif / folk art / illustrated / storybook / earthy / green → bks-origin (#489808)

FIT NOTES (US market):
- Puffer jackets and hoodies: intentional oversized fit. If asked "runs big?" → confirm, that's the design.
- Dresses, athletic shorts, swim trunks: slim/standard cut.
- All items are made to order — no stock, no sell-outs. Production: 7–14 days + 3–5 days shipping.
- Returns: 30 days from delivery. Contact: crew@bakabo.club
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
Rispondi SOLO su: prodotti, collezioni, disponibilità, prezzi, caratteristiche, tag, pagine del sito.
Se la domanda riguarda ordini/resi/spedizioni → rispondi SOLO: [ESCALATE:support]
Se riguarda personalizzazioni → rispondi SOLO: [ESCALATE:customization]
Tono: editoriale, essenziale. Rileva la lingua del messaggio e rispondi nella stessa lingua (italiano o inglese). Sii preciso e conciso.

${BKS_BRAND}
${BKS_COLLECTIONS}
${BKS_PRODUCTS}

${BKS_SYNONYMS}
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
Tono: esclusivo, diretto, brand BKS. Rileva la lingua del messaggio e rispondi nella stessa lingua (italiano o inglese).`;
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
Tono: professionale, empatico. Rileva la lingua del messaggio e rispondi nella stessa lingua (italiano o inglese).
Tier cliente: ${customerProfile?.tier ?? "none"}
Per assistenza umana diretta: crew@bakabo.club`;
  const reply   = await callOpenAI(env, system, [...history, { role: "user", content: message }]);
  const escalate= reply.includes("[ESCALATE:human]");
  return { reply: escalate ? null : reply, resolved: !escalate, escalate, sentiment: detectSentiment(message) };
}
__name(supportAgent, "supportAgent");

async function tierAgent({ message, customerProfile, env }) {
  const tier = customerProfile?.tier ?? "none";
  const isEN = /\b(what|my|tier|level|member|unlock|how|badge|status)\b/i.test(message);
  const info = isEN ? {
    none:   "You're not yet a BKS member. Create an account on bakabo.club — your first order unlocks Lead ◎ tier with wishlist access and the exclusive newsletter.",
    lead:   "You're BKS Lead ◎ — welcome to the club. You have wishlist access and the newsletter. Complete 1–2 orders to reach Iron ⬡ and unlock basic AI recommendations.",
    iron:   "You're BKS Iron ⬡ — size history active, basic AI recommendations enabled. Next tier: Brass ◈ (3+ orders) — unlocks the Try-On Fitting Room and 48h early drop access.",
    brass:  "You're BKS Brass ◈ — AI Personal Shopper active, Try-On Fitting Room available at bakabo.club/pages/bks-members, +48h early drop access. Next tier: Silver ◇ (6+ orders).",
    silver: "You're BKS Silver ◇ — curated drops with +24h access, full collection archive, advanced text customisation (+€15). Next tier: Gold ✦ (11+ orders).",
    gold:   "You're BKS Gold ✦ — maximum access: private VIP drops, white-glove curation, co-creation with BKS Studio. You're at the top of the Metal system.",
  } : {
    none:   "Non sei ancora un membro BKS. Crea un account su bakabo.club — al primo acquisto diventi Lead ◎ e accedi alla wishlist e alla newsletter esclusiva.",
    lead:   "Sei BKS Lead ◎ — benvenuto nel club. Hai accesso alla wishlist e alla newsletter. Completa 1–2 ordini per salire a Iron ⬡ e sbloccare le raccomandazioni AI personalizzate.",
    iron:   "Sei BKS Iron ⬡ — storico taglie attivo, raccomandazioni AI di base. Prossimo tier: Brass ◈ (3+ ordini) — sblocchi il Try-On Camerino e l'accesso anticipato ai drop di 48h.",
    brass:  "Sei BKS Brass ◈ — AI Personal Shopper attivo, Try-On Camerino disponibile su bakabo.club/pages/bks-members, accesso anticipato ai drop +48h. Prossimo tier: Silver ◇ (6+ ordini).",
    silver: "Sei BKS Silver ◇ — drop curati con accesso +24h, archivio completo collezioni, personalizzazione testo avanzata (+€15). Prossimo tier: Gold ✦ (11+ ordini).",
    gold:   "Sei BKS Gold ✦ — massimo accesso: drop VIP privati, curation white-glove, co-creazione con BKS Studio. Sei al vertice del sistema Metal.",
  };
  return { reply: info[tier] || info.none, resolved: true, escalate: false, sentiment: "neutral" };
}
__name(tierAgent, "tierAgent");

async function tryonAgent({ message, customerProfile, env }) {
  const tier = customerProfile?.tier ?? "none";
  const eligible = ["brass", "silver", "gold"].includes(tier);
  const isEN = /\b(try.?on|fitting|virtual|room|available|access|where)\b/i.test(message);
  if (!eligible) {
    const needed = isEN
      ? (tier === "none" || tier === "lead"
          ? "The Try-On Fitting Room is unlocked at Brass ◈ tier (3+ orders on bakabo.club)."
          : "Iron ⬡ tier doesn't include Try-On yet. Complete 3 total orders to reach Brass ◈.")
      : (tier === "none" || tier === "lead"
          ? "Il Try-On Camerino si sblocca con il tier Brass ◈ (3+ ordini su bakabo.club)."
          : "Il tier Iron ⬡ non include ancora il Try-On. Completa 3 ordini totali per salire a Brass ◈.");
    return { reply: needed, resolved: true, escalate: false, sentiment: "neutral" };
  }
  const reply = isEN
    ? `The BKS Try-On Fitting Room is available for your ${tier.charAt(0).toUpperCase() + tier.slice(1)} tier.\n\nAccess it at: bakabo.club/pages/bks-members → Try-On tab.\nYou can virtually try on all active BKS catalogue garments. Support: crew@bakabo.club`
    : `Il Try-On Camerino BKS è disponibile per il tuo tier ${tier.charAt(0).toUpperCase() + tier.slice(1)}.\n\nAccedi da: bakabo.club/pages/bks-members → tab Try-On.\nPuoi provare virtualmente tutti i capi attivi del catalogo BKS. Supporto: crew@bakabo.club`;
  return { reply, resolved: true, escalate: false, sentiment: "positive" };
}
__name(tryonAgent, "tryonAgent");

async function navigationAgent({ message, env }) {
  const isEN = /\b(where|find|page|go|link|how|access|navigate|site)\b/i.test(message);
  const system = isEN
    ? `You are the BKS Navigation Agent for bakabo.club.
Help the user find the right page or section of the site.
Key pages: /collections/all (full catalogue), /collections/bks-{hours,glyph,marker,riviera,pulse,token,flag,origin} (8 collections), /pages/bks-members (member area: tier dashboard, wishlist, Try-On), /pages/verse (BKS Verse: submit a poem, AI judge evaluates it, becomes a garment — Brass+ only), /pages/verse-hall (BKS Verse Hall of Fame: world leaderboard, 21 historical poets archive), /pages/bks-ai-assistant (AI assistant), /pages/about-bakabo-1 (about), /pages/contatti (contact), /account (login/account), /cart (cart).
Ask BKS is in the navigation menu — the user is already using it.
Reply concisely with the direct URL and a one-line description. Use English.`
    : `Sei il BKS Navigation Agent per bakabo.club.
Aiuta l'utente a trovare la pagina o sezione giusta del sito.
Pagine chiave: /collections/all (catalogo completo), /collections/bks-{hours,glyph,marker,riviera,pulse,token,flag,origin} (8 collezioni), /pages/bks-members (area membri: tier, wishlist, Try-On), /pages/verse (BKS Verse: invia un verso, il Giudice AI lo valuta, diventa un capo BKS — solo Brass+), /pages/verse-hall (BKS Verse Hall of Fame: leaderboard mondiale, archivio 21 poeti storici), /pages/bks-ai-assistant (AI assistant), /pages/about-bakabo-1 (about), /pages/contatti (contatto), /account (login/account), /cart (carrello).
Ask BKS è nel menu di navigazione — l'utente lo sta già usando.
Rispondi con l'URL diretto e una descrizione in una riga. Usa l'italiano.`;
  const reply = await callOpenAI(env, system, [{ role: "user", content: message }]);
  return { reply, resolved: true, escalate: false, sentiment: "neutral" };
}
__name(navigationAgent, "navigationAgent");

async function verseAgent({ message, customerProfile, env }) {
  const tier     = customerProfile?.tier ?? "none";
  const eligible = ["brass", "silver", "gold"].includes(tier);
  const isEN     = /\b(poem|verse|poetry|judge|submit|write|word|line|art|object|win|leaderboard|hall)\b/i.test(message);

  const INFO_IT = `BKS Verse è la piattaforma di BKS Studio dove la poesia diventa un capo.
Come funziona:
1. Scrivi un verso (80–280 caratteri) su /pages/verse
2. Il Giudice AI — ispirato ai Grandi Poeti della storia — lo valuta su 5 assi: Immagine, Voce, Tensione, BKS, Corpo
3. Se il verso supera la soglia, diventa artwork AI e poi prodotto reale nel catalogo BKS
4. La tua firma compare sul capo come parte dell'edizione
Leaderboard mondiale: /pages/verse-hall — classifica pubblica con i 25 migliori versi di sempre.
Accesso: riservato ai membri Brass ◈ e superiori (3+ ordini su bakabo.club).`;

  const INFO_EN = `BKS Verse is BKS Studio's platform where poetry becomes a garment.
How it works:
1. Write a verse (80–280 characters) at /pages/verse
2. The AI Judge — inspired by the Great Poets of history — evaluates it on 5 axes: Image, Voice, Tension, BKS, Body
3. If the verse passes the threshold, it becomes AI artwork then a real product in the BKS catalogue
4. Your name appears on the garment as part of the edition
World leaderboard: /pages/verse-hall — public ranking of the 25 best verses ever.
Access: reserved for Brass ◈ members and above (3+ orders on bakabo.club).`;

  const gateIT = tier === "none" || tier === "lead" || tier === "iron"
    ? `\n\nPer accedere a BKS Verse devi essere almeno Brass ◈ (3+ ordini). Il tuo tier attuale: ${tier === "none" ? "nessuno" : tier.charAt(0).toUpperCase() + tier.slice(1)}.`
    : "";
  const gateEN = tier === "none" || tier === "lead" || tier === "iron"
    ? `\n\nTo access BKS Verse you need at least Brass ◈ tier (3+ orders). Your current tier: ${tier === "none" ? "none" : tier.charAt(0).toUpperCase() + tier.slice(1)}.`
    : "";

  const reply = isEN ? INFO_EN + gateEN : INFO_IT + gateIT;
  return { reply, resolved: true, escalate: false, sentiment: "positive" };
}
__name(verseAgent, "verseAgent");

// ── evaluator.js ─────────────────────────────────────────────────────────────
var AGENTS    = ["catalog", "custom", "support", "tier", "tryon", "navigation", "verse", "orchestrator"];
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
catalog       → domande su prodotti, collezioni, prezzi, disponibilità, caratteristiche
customization → richieste di personalizzazione, testo su capo, custom order
support       → ordini, spedizioni, resi, rimborsi, problemi tecnici
tier          → domande sul proprio tier/membership BKS, livello Metal, sblocchi
tryon         → richiesta accesso Try-On Camerino, virtual fitting, provare virtualmente
navigation    → dove trovo X, link a pagina, come accedo a Y, dove è la pagina Z
verse         → BKS Verse, poesia, verso, giudice AI, poema, come partecipare, leaderboard poesia, hall of fame
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
    case "verse":         return verseAgent(context);
    case "navigation":    return navigationAgent(context);
    case "greeting": {
      const isEN = /\b(hi|hello|hey|good|help|what can)\b/i.test(context.message);
      const reply = isEN
        ? "Hi! I'm the BKS AI assistant — you'll find me in the navigation menu. I can help with products, collections, your Metal tier, the Try-On Fitting Room, BKS Verse (poetry→garment), customisation, or orders."
        : "Ciao! Sono l'assistente AI di BKS — mi trovi nel menu di navigazione. Posso aiutarti con prodotti, collezioni, il tuo tier Metal, il Try-On Camerino, BKS Verse (poesia→capo), personalizzazioni o ordini.";
      return { reply, resolved: true, escalate: false, sentiment: "neutral" };
    }
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

// ── Try-On helpers ───────────────────────────────────────────────────────────
function base64ToUint8Array(b64) {
  const bin = atob(b64);
  const arr = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) arr[i] = bin.charCodeAt(i);
  return arr;
}
__name(base64ToUint8Array, "base64ToUint8Array");

function uint8ArrayToBase64(bytes) {
  let bin = "";
  for (let i = 0; i < bytes.byteLength; i++) bin += String.fromCharCode(bytes[i]);
  return btoa(bin);
}
__name(uint8ArrayToBase64, "uint8ArrayToBase64");

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

    // ── Social content generation ─────────────────────────────────────────────
    if (request.method === "POST" && url.pathname === "/social") {
      let body;
      try { body = await request.json(); }
      catch { return new Response("Bad JSON", { status: 400, headers: cors }); }

      const { collection = "", product_type = "", platform = "instagram", language = "en", product_title = "" } = body;

      const FORMATS = {
        youtube:   "title (max 70 chars, no emoji), description (3 paragraphs: visual → collection → links), tags (array of 15 strings)",
        instagram: "caption (headline + 2-3 lines editorial + 'bakabo.club — link in bio'), hashtags (array of 25)",
        facebook:  "caption (slightly longer than IG, optional Italian), hashtags (array of 10)",
        pinterest: "title (max 100 chars), description (150-300 chars, natural keyword), hashtags (array of 5)",
        tiktok:    "caption (max 150 chars, punchy), hashtags (array of 8)",
      };

      const system = `You are the BKS Studio Social Content Agent.
Generate ${platform} content for BKS Studio (bakabo.club) — wearable AI art, print on demand.
Output format: ${FORMATS[platform] || FORMATS.instagram}
Language: ${language === "it" ? "Italian" : "English"}
Respond ONLY with valid JSON: { ${platform === "youtube" ? '"title","description","tags"' : '"caption","hashtags"'} }

VOICE RULES (never break):
- No exclamation marks. No urgency. No "luxury", "premium", "limited edition", "drop".
- Tone: observational, editorial, cool. Describe, don't sell.
- CTA: only "bakabo.club" or "link in bio" or "in the catalog".
- Collection name: always full "BKS ${collection.replace("bks-", "").charAt(0).toUpperCase() + collection.replace("bks-", "").slice(1)}", never abbreviated.

${BKS_BRAND}
${BKS_COLLECTIONS}`;

      const userMsg = `Generate ${platform} content for: collection=${collection}, product_type=${product_type}${product_title ? ", product_title=" + product_title : ""}`;

      try {
        const reply = await callOpenAI(env, system, [{ role: "user", content: userMsg }]);
        let parsed;
        try { parsed = JSON.parse(reply); }
        catch { parsed = { raw: reply }; }
        return Response.json({ ...parsed, collection, product_type, platform, language }, { headers: cors });
      } catch (err) {
        return Response.json({ error: "Content generation failed", details: err.message }, { status: 503, headers: cors });
      }
    }

    // ── Try-On endpoint ───────────────────────────────────────────────────────
    if (request.method === "POST" && url.pathname === "/tryon") {
      let body;
      try { body = await request.json(); }
      catch { return new Response("Bad JSON", { status: 400, headers: cors }); }

      const { customer_id = "anonymous", customer_tier = "", person_image_b64, garment_url } = body;

      // Tier gate: Brass+ only
      if (!["brass", "silver", "gold"].includes(customer_tier.toLowerCase())) {
        return Response.json({
          error: "Try-On requires Brass tier or higher (3+ orders on bakabo.club).",
          tier_required: "brass",
        }, { status: 403, headers: cors });
      }

      if (!person_image_b64 || !garment_url) {
        return new Response("Missing person_image_b64 or garment_url", { status: 400, headers: cors });
      }

      try {
        // Fetch garment image from Shopify CDN
        const gRes = await fetch(garment_url, { headers: { "User-Agent": "BKS-TryOn/1.0" } });
        if (!gRes.ok) throw new Error(`Garment fetch failed: ${gRes.status}`);
        const garmentBytes = new Uint8Array(await gRes.arrayBuffer());

        // Decode person image (strip data URI prefix)
        const b64clean = person_image_b64.replace(/^data:image\/[^;]+;base64,/, "");
        const personBytes = base64ToUint8Array(b64clean);

        // Cloudflare Workers AI — p-image-try-on (Pruna AI)
        // Binding: env.AI  (add [ai] binding = "AI" in wrangler.toml — already done)
        const result = await env.AI.run("@pruna-ai/p-image-try-on", {
          person_image:  personBytes,
          garment_image: garmentBytes,
        });

        // Result is Uint8Array (JPEG bytes)
        const resultBytes = result instanceof Uint8Array ? result : new Uint8Array(result);
        const resultB64 = uint8ArrayToBase64(resultBytes);

        // Log usage (no PII stored — only customer_id hash)
        await memory.appendHistory(customer_id, {
          role: "system",
          content: `[tryon] garment=${garment_url.split("/").pop().split("?")[0]}`,
          agent: "tryon",
        });

        return Response.json({
          result_image: `data:image/jpeg;base64,${resultB64}`,
          status: "ok",
        }, { headers: cors });

      } catch (err) {
        console.error("[BKS TryOn] Error:", err.message);
        return Response.json({
          error: "Try-On processing failed. Use 'Send to crew' for manual processing.",
          fallback: "crew",
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
