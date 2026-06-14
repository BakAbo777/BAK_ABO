/**
 * BKS Specialized Agents
 *
 * Each agent receives: { message, customerProfile, history, catalog, env }
 * Returns: { reply, resolved, escalate, sentiment, intent }
 */

const OPENAI_URL = 'https://api.openai.com/v1/chat/completions';
const MODEL      = 'gpt-4o';

// ── BKS Static Knowledge Base ────────────────────────────────────────────────
// Aggiornato automaticamente via cron + manuale ad ogni variazione di sistema

const BKS_BRAND = `
BKS Studio — wearable art, on demand. Venduto su bakabo.club (BakAbo container).
Modello: made-to-order, stampa edge-to-edge AOP (All Over Print). Produzione 7-14 giorni, spedizione 3-5 giorni.
Fornitore principale: Printify. Nessun magazzino fisico — ogni pezzo è prodotto all'ordine.
`;

const BKS_COLLECTIONS = `
8 COLLEZIONI EDITORIALI BKS STUDIO:

1. BKS HOURS — Contemplazione urbana, registro iperrealista. AI-art in stile pittura iperrealista: luci città, silenzio interiore, vita quotidiana. Colore identitario: ambra #D4A96A. Tag: collection:hours.

2. BKS GLYPH — DNA grafico del brand. Alfabeto visivo proprietario: simboli astratti, frammenti a mano, geroglifici inventati. Non decorazione, ma sistema codificato. Colore: bianco freddo #E8E8E4. Tag: collection:glyph.

3. BKS MARKER — Grafica urbana gestuale. Pennello, muro, segno. Energia street drawing: drip, stroke, color block, segni applicati a mano. Colore: verde organico #7DBF72. Tag: collection:marker.

4. BKS RIVIERA — Resort mediterraneo permanente. Energia costiera: sale, sole, terracotta, blu profondo. Swimwear, camicie, accessori. Colore: azzurro oceano #7EB3D4. Tag: collection:riviera.

5. BKS PULSE — Collezione ottica. Ritmo, vibrazione, moto visivo. Ripetizione geometrica, campi cinetici, griglie modulari. Colore: rosso intenso #E05C5C. Tag: collection:pulse.

6. BKS TOKEN — Collezione arcade. Pixel, game, campo digitale. Low-bit visual language, colore elettronico kaleidoscopico. Ogni pezzo è un oggetto collezionabile. Colore: oro saturno #F0C84A. Tag: collection:token.

7. BKS FLAG — Pop-collage. Campi astratti, colore codificato, blocchi grafici. Composizioni da piani colore, superfici stencil, bandiere inventate. Energia Dada. Colore: viola/magenta #C97AB8. Tag: collection:flag.

8. BKS FOLKLORE — Collezione figurativa. Mondi immaginari, storie disegnate, memoria inventata. Animali da favola, archetipi da giardino, illustrazione flat. Mai preso in prestito. Colore: dune #C9B79C. Tag: collection:folklore.
`;

const BKS_PRODUCTS = `
TIPI PRODOTTO ATTIVI:
- Sneakers (all-over print, graphic low-top)
- Swim Trunks (quick-dry, edge-to-edge)
- One-Piece Swimsuit
- Puffer Jacket (quilted outerwear)
- Windbreaker (technical shell)
- Athletic Shorts (long cut)
- Lounge Pants
- Pullover Hoodie
- Racerback Dress
- Travel Bag (duffel impermeabile)
- Backpack (13L multi-compartment)
- Flip Flop
- Cozy Slipper
- Women's Tee (cut-and-sew)

POLICY CHIAVE:
- Resi: 30 giorni dalla consegna
- Personalizzazione testo: disponibile per tier Subscriber/Drop/Archive. Costo +€15.
- EU Representative: presente
- Nessun GTIN — made-to-order custom product
`;

const BKS_TIERS = `
SISTEMA TIER BKS:
- none: nessun acquisto. Per accedere al tier: completa il primo ordine.
- subscriber: primo acquisto. Accesso anticipato ai drop, wishlist riservata.
- drop: membro attivo. Drop exclusives, MTO tracker, archivio collezioni precedenti.
- archive: massimo accesso. Prompt library, pattern rifiutati, early access assoluto, personalizzazione prioritaria.
`;

async function callOpenAI(env, systemPrompt, messages) {
  const r = await fetch(OPENAI_URL, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${env.OPENAI_API_KEY}`,
      'Content-Type':  'application/json',
    },
    body: JSON.stringify({
      model: MODEL,
      temperature: 0.4,
      messages: [{ role: 'system', content: systemPrompt }, ...messages],
    }),
  });
  if (!r.ok) throw new Error(`OpenAI ${r.status}: ${await r.text()}`);
  const data = await r.json();
  return data.choices[0].message.content.trim();
}

function detectSentiment(text) {
  const pos = /grazie|perfetto|ottimo|capito|ok|super|bravo/i.test(text);
  const neg = /non capisco|sbagliato|ripeti|errore|problema|non funziona/i.test(text);
  return pos ? 'positive' : neg ? 'negative' : 'neutral';
}

// ── Catalog Agent ────────────────────────────────────────────────────────────

export async function catalogAgent({ message, history, catalog, env }) {
  const liveCatalog = catalog
    ? `CATALOGO LIVE (aggiornato ${catalog.updated_at}, ${catalog.product_count} prodotti attivi):\n` +
      catalog.products.slice(0, 30).map(p =>
        `- ${p.title} | tipo: ${p.type} | €${p.variants?.[0]?.price ?? '?'} | handle: ${p.handle}`
      ).join('\n')
    : 'Snapshot live non disponibile — usa la knowledge base statica sotto.';

  const system = `Sei il BKS Catalog Agent per bakabo.club — wearable art, on demand.
Rispondi SOLO su: prodotti, collezioni, disponibilità, prezzi, caratteristiche, tag.
Se la domanda riguarda ordini/resi/spedizioni → rispondi SOLO: [ESCALATE:support]
Se riguarda personalizzazioni → rispondi SOLO: [ESCALATE:customization]
Tono: editoriale, essenziale, italiano. Sii preciso e conciso.

${BKS_BRAND}
${BKS_COLLECTIONS}
${BKS_PRODUCTS}

${liveCatalog}`;

  const reply = await callOpenAI(env, system, [
    ...history,
    { role: 'user', content: message },
  ]);

  const escalate = reply.startsWith('[ESCALATE:');
  return { reply: escalate ? null : reply, resolved: !escalate, escalate, sentiment: detectSentiment(message) };
}

// ── Customization Agent ──────────────────────────────────────────────────────

export async function customAgent({ message, customerProfile, history, catalog, env }) {
  const tier    = customerProfile?.tier ?? 'none';
  const allowed = ['subscriber', 'drop', 'archive'].includes(tier);

  if (!allowed) {
    return {
      reply: 'La personalizzazione prodotti è disponibile per i clienti BKS registrati. Crea un account su bakabo.club per accedere.',
      resolved: true, escalate: false, sentiment: 'neutral',
    };
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

  const reply = await callOpenAI(env, system, [
    ...history,
    { role: 'user', content: message },
  ]);

  const ready    = reply.startsWith('[CUSTOM_READY:');
  const escalate = reply.startsWith('[ESCALATE:');
  return {
    reply:    (ready || escalate) ? null : reply,
    resolved: ready,
    escalate,
    customPayload: ready ? reply : null,
    sentiment: detectSentiment(message),
  };
}

// ── Support Agent ────────────────────────────────────────────────────────────

export async function supportAgent({ message, customerProfile, history, env }) {
  const system = `Sei il BKS Support Agent per bakabo.club.
Gestisci: stato ordini, resi (30 giorni dalla consegna), spedizioni (MTO: 7-14 giorni produzione + 3-5 spedizione), policy.
Se la richiesta richiede accesso all'ordine specifico, chiedi il numero ordine o email.
Se non riesci a risolvere, rispondi SOLO con: [ESCALATE:human]
Tono: professionale, empatico, italiano.
Tier cliente: ${customerProfile?.tier ?? 'none'}`;

  const reply = await callOpenAI(env, system, [
    ...history,
    { role: 'user', content: message },
  ]);

  const escalate = reply.includes('[ESCALATE:human]');
  return { reply: escalate ? null : reply, resolved: !escalate, escalate, sentiment: detectSentiment(message) };
}

// ── Tier Agent ───────────────────────────────────────────────────────────────

export async function tierAgent({ message, customerProfile, env }) {
  const tier = customerProfile?.tier ?? 'none';
  const info = {
    none:       'Non sei ancora un membro BKS. Completa il tuo primo acquisto su bakabo.club per accedere al tier Subscriber e sbloccare accesso anticipato ai drop.',
    subscriber: 'Sei BKS Subscriber — accesso anticipato ai drop, wishlist riservata. Tier successivo: Drop (acquisto ricorrente).',
    drop:       'Sei BKS Drop Member — drop exclusives, MTO tracker in tempo reale e archivio collezioni precedenti. Tier successivo: Archive.',
    archive:    'Sei BKS Archive — massimo accesso: prompt library, pattern rifiutati, early access assoluto, personalizzazione testo prioritaria (+€15 standard).',
  };
  return {
    reply:    info[tier] || info.none,
    resolved: true,
    escalate: false,
    sentiment: 'neutral',
  };
}
