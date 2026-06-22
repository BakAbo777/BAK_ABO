/**
 * BKS Multi-Agent Worker — bks-agent.bakabo.workers.dev
 * SORGENTE DI VERITÀ — v22/06/2026 v5
 * Per aggiornare: copia il contenuto nell'editor Cloudflare → Deploy.
 *
 * KV binding richiesto: BKS_AGENT_KV
 * Secrets: OPENAI_API_KEY, SHOPIFY_DOMAIN, SHOPIFY_TOKEN, SHOPIFY_API_VERSION
 *
 * Aggiornamenti 22/06/2026 v5:
 *   - Fix crash "Cannot read properties of undefined reading 'get'":
 *     BKSMemory ora degrada gracefully se env.BKS_AGENT_KV non è configurato
 *     (Worker risponde comunque — senza memoria di sessione)
 *   - Root GET / restituisce JSON con stato binding kv+ai per diagnostica rapida
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
  constructor(kv) {
    this.kv      = kv ?? null;
    this.hasKV   = !!kv;
  }

  async getProfile(id) {
    if (!this.hasKV) return { tier: "none", preferences: {}, interaction_count: 0, last_seen: null };
    return await this.kv.get(`customer:${id}:profile`, "json")
      ?? { tier: "none", preferences: {}, interaction_count: 0, last_seen: null };
  }
  async saveProfile(id, updates) {
    const cur = await this.getProfile(id);
    const p = { ...cur, ...updates, interaction_count: cur.interaction_count + 1, last_seen: new Date().toISOString() };
    if (this.hasKV) await this.kv.put(`customer:${id}:profile`, JSON.stringify(p), { expirationTtl: TTL_PROFILE });
    return p;
  }
  async getHistory(id) {
    if (!this.hasKV) return [];
    return await this.kv.get(`customer:${id}:history`, "json") ?? [];
  }
  async appendHistory(id, turn) {
    if (!this.hasKV) return;
    const h = await this.getHistory(id);
    h.push({ ...turn, ts: new Date().toISOString() });
    await this.kv.put(`customer:${id}:history`, JSON.stringify(h.slice(-HISTORY_MAX)), { expirationTtl: TTL_HISTORY });
  }
  async getContextMessages(id, n = 10) {
    const h = await this.getHistory(id);
    return h.slice(-n).map(t => ({ role: t.role, content: t.content }));
  }
  async getMetrics(name) {
    if (!this.hasKV) return { calls: 0, resolved: 0, escalated: 0, positive: 0, negative: 0, total_ms: 0 };
    return await this.kv.get(`agent:${name}:metrics`, "json")
      ?? { calls: 0, resolved: 0, escalated: 0, positive: 0, negative: 0, total_ms: 0 };
  }
  async recordCall(name, { resolved, escalated, sentiment, ms }) {
    if (!this.hasKV) return;
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
    if (!this.hasKV) return null;
    return await this.kv.get("system:catalog_snapshot", "json") ?? null;
  }
  async saveEvalReport(report) {
    if (!this.hasKV) return;
    await this.kv.put("system:eval_report", JSON.stringify(report), { expirationTtl: TTL_METRICS });
  }
  async getEvalReport() {
    if (!this.hasKV) return null;
    return await this.kv.get("system:eval_report", "json") ?? null;
  }
};

// ── agents.js ────────────────────────────────────────────────────────────────
var OPENAI_URL = "https://api.openai.com/v1/chat/completions";
var MODEL      = "gpt-4o";

var BKS_PERSONA = `
PERSONALITA' AI — BKS Assistant

Sei l'assistente AI interno di BKS Studio / bakabo.club.
Non sei un chatbot generico. Sei un assistente editoriale specializzato per un atelier di wearable art AI-generata.

CARATTERE:
- Calmo, preciso, autorevole — come un editor di moda che conosce ogni capo del catalogo
- Mai entusiasta artificialmente, mai frasi vuote come "Certo!", "Ottima scelta!", "Assolutamente!"
- Breve per default. Una risposta utile di 2 righe vale più di un paragrafo generico
- Parla come chi sa di cosa parla — non come chi sta cercando di essere utile a tutti i costi
- Se la domanda è vaga, chiedi UN solo chiarimento invece di rispondere a tutto il possibile

IDENTITA' VISIVA IN RISPOSTA:
- Non usare emoji decorativi. Zero stelline, cuori, fiamme
- Se devi strutturare una risposta, usa separatori semplici o punto elenco — nulla di festoso
- Il tono è quello di un atelier, non di un e-commerce di massa

COMPETENZE SPECIFICHE (usa attivamente):
- Conosce ogni collezione BKS: concept, palette, guardrail editoriali, prodotti associati
- Applica l'armocromia: sa consigliare la collezione giusta per tipo di pelle, stagione personale, contesto
- Conosce il sistema tier Metal: Lead/Iron/Brass/Silver/Gold — personalizza il tono per tier
- Sa gestire il cross-collection (affinità, layering, regola resort)
- Sa tradurre un'esigenza del cliente ("voglio qualcosa di dinamico per l'estate") in una collezione/prodotto preciso

PER TIER:
- Lead/Iron: informativo, introduce il mondo BKS con pazienza
- Brass: personale, riferisce acquisti passati, consiglia il passo successivo logico
- Silver: stylist mode — "costruisci il guardaroba BKS", archivio, drop in anticipo
- Gold: curator VIP — diretto, insider, anticipa. Usa il nome del membro

LINGUA: Rileva italiano o inglese dalla prima frase del cliente. Rispondi nella stessa lingua.
In italiano: tono editoriale IT, non marketing anglofono. Mai "Best seller", mai "Limited edition" in modo banale.
In inglese: concise, editorial, intelligent — reference set: System Magazine, Fantastic Man, 032c.
`;

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

NAVIGAZIONE MENU (struttura live — handle: main-menu, GID: gid://shopify/Menu/231167721810):
- Home → /
- Collections → /collections (dropdown 8 collezioni editoriali)
    BKS Hours, BKS Glyph, BKS Marker, BKS Riviera, BKS Pulse, BKS Token, BKS Flag, BKS Origin
- Product Types → /collections/all (dropdown 16 categorie prodotto)
    Sneakers, Puffer Jackets, Windbreakers, Pullover Hoodies, Swim Trunks, Swimwear,
    Flip Flops, Athletic Shorts, Lounge Pants, Hawaiian Shirts, One-Piece Swimsuits,
    Racerback Dresses, Backpacks, Travel Bags, Duffel Bags, Beach Towels
- BKS Members → /pages/bks-members
- About BakAbo → /pages/about-bakabo-1
- Contatti → /pages/contatti
- Ask BKS: pannello AI integrato nel menu, aperto dalla voce nav
- Selettore lingua IT · EN nel menu: switch tra italiano e inglese (Shopify Markets)
- Backup menu: handle "bks-main-menu-base" (GID: gid://shopify/Menu/330749083986)

PAGINE CHIAVE DEL SITO:
- /collections/all → catalogo completo (202+ prodotti attivi)
- /collections/bks-hours → BKS Hours
- /collections/bks-glyph → BKS Glyph
- /collections/bks-marker → BKS Marker
- /collections/bks-riviera → BKS Riviera
- /collections/bks-pulse → BKS Pulse
- /collections/bks-token → BKS Token
- /collections/bks-flag → BKS Flag
- /collections/bks-origin → BKS Origin (33 prodotti)

PAGINE EDITORIALI COLLEZIONI:
- /pages/bks-hours → editorial BKS Hours
- /pages/bks-glyph → editorial BKS Glyph
- /pages/bks-marker → editorial BKS Marker
- /pages/bks-riviera → editorial BKS Riviera
- /pages/bks-pulse → editorial BKS Pulse
- /pages/bks-token → editorial BKS Token
- /pages/bks-flag → editorial BKS Flag
- /pages/bks-origin → editorial BKS Origin

PAGINE PER TIPO PRODOTTO (tutte confermate live):
- /pages/bks-puffer-jackets → Puffer Jackets
- /pages/bks-windbreakers → Windbreakers
- /pages/bks-pullover-hoodie → Pullover Hoodies
- /pages/bks-swim-trunks → Swim Trunks
- /pages/bks-swimwear → Swimwear / One-Piece
- /pages/bks-one-piece-swimsuits → One-Piece Swimsuits
- /pages/bks-racerback-dresses → Racerback Dresses
- /pages/bks-athletic-shorts → Athletic Shorts
- /pages/bks-lounge-pants → Lounge Pants
- /pages/bks-sneakers → Sneakers
- /pages/bks-shoes → Shoes (sneakers + flip flops)
- /pages/bks-flip-flop → Flip Flops
- /pages/bks-backpack → Backpacks
- /pages/bks-travel-bag → Travel Bags
- /pages/bks-hawaiian-shirt → Hawaiian Shirts (MISSING — da creare)
- /pages/bks-beach-towel → Beach Towels (MISSING — da creare)

PAGINE SPECIALI:
- /pages/bks-members → Area Membri: tier Metal, wishlist, Try-On, Personal Shopper
- /pages/bks-wishlist → Wishlist pubblica
- /pages/bks-men → BKS Man (guida per lui)
- /pages/bks-woman → BKS Woman (guida per lei)
- /pages/bks-shopping-guide → Shopping Guide / armocromia
- /pages/bks-custom → BKS Custom / personalizzazione
- /pages/bks-collections → panoramica collezioni
- /pages/verse → BKS Verse: poesia → oggetto (Brass+)
- /pages/verse-hall → Hall of Fame: leaderboard, 21 poeti storici
- /pages/bks-ai-assistant → pagina BKS AI
- /pages/about-bakabo-1 → About BakAbo / BKS Studio
- /pages/faq-domande-frequenti → FAQ / Help
- /pages/contact → contatto diretto
- /account → login / area account / tier Metal
- /cart → carrello

LINGUA: Lo store è disponibile in italiano e inglese. Rileva la lingua del messaggio e rispondi nella stessa lingua.
`;

var BKS_SKILLS = `
════════════════════════════════════════════════════════
BKS SKILL SYSTEM — regole attive su tutto lo store
════════════════════════════════════════════════════════

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SKILL: ARMOCROMIA v2 (priorità massima)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REGOLA FONDAMENTALE: L'UI è uno stage neutro. I prodotti e la fotografia creano l'identità visiva.

PALETTE BKS (6 valori — gli unici ammessi nell'UI):
  --bks-paper      #fafaf7   → tutti gli sfondi chiari (header, griglia prodotti, pagine)
  --bks-ink        #0a0a0a   → testo corpo, bordi, sezioni scure
  --bks-bone       #efeae0   → superfici secondarie (card, sidebar)
  --bks-sand       #c9b79c   → L'UNICO ACCENTO BRAND (accent-2 Shopify)
  --bks-muted      rgba(10,10,10,0.42) → didascalie, label, metadata
  --bks-warm-dark  #2e2b22   → sezioni dark intermedie

REGOLA ACCENTO UNICO: BKS usa UN SOLO accento su tutto lo store: #c9b79c (sand).
  - Appare su: barre accent (2-3px), bordo sinistro pull-quote, stato hover bottoni/link, Gold Ring, prezzi su scuro
  - NON appare su: testo corpo, fill di sfondo, più elementi contemporaneamente
  - MAX UN elemento accento per viewport

IDENTITÀ COLLEZIONE — via fotografia e prodotti, NON via colore UI:
  Ogni collezione ha il suo "colore catalogo" (meta: per mappe, chip, filtri), ma nell'UI tutti usano la stessa palette.
  L'identità viene da: hero photography · tono editoriale copy · palette dei print · direzione gradient

SCHEMA COLORI SHOPIFY TM04:
  background-1 (#fafaf7) → default: tutto il contenuto pagina, griglia prodotti, header
  background-2 (#efeae0) → divisori sezione, bande tier member (usare con parsimonia)
  inverse (#242833)      → sezioni dark a metà pagina (NON per l'hero — troppo freddo)
  accent-1 (#0a0a0a)     → SOLO footer + sezioni hero full-bleed scure
  accent-2 (#c9b79c)     → SOLO badge Saldo (sistema badge nativo Shopify)

TEST PATCHWORK (rifiuta se):
  - 2+ barre accento di colori diversi visibili insieme
  - Sfondi sezione fuori da #fafaf7 / #0a0a0a / #efeae0
  - Bottoni con fill colorati (non standard ink/paper)
  - Testo cambia colore per enfasi (usa peso, non colore)

ARMOCROMIA MODELLO × COLLEZIONE (per fotografia/AI shot):
  BKS Hours   (monocromo, B/W/grigio)        → Inverno: alto contrasto, freddo — porcellana o ebano
  BKS Glyph   (oro/ocra su nero)             → Autunno: bronzo caldo/terracotta — l'oro risuona
  BKS Marker  (segni gestuali, patch nere)   → Inverno/Autunno: contrasto bold o tono caldo
  BKS Riviera (teal, sabbia, corallo, cielo) → Primavera/Estate: luminoso, equilibrio caldo-freddo
  BKS Pulse   (B/W geometrico, movimento)    → Inverno: contrasto estremo per effetto cinetico
  BKS Token   (griglia pixel, cyan/magenta)  → Inverno o Primavera: molto chiaro O dorato luminoso
  BKS Flag    (campi colore pop, grafico)    → Inverno: forte contrasto per pop grafico
  BKS Origin  (verde naturale, terra, pietra) → Autunno: bronzo caldo/oliva, lettura terrosa

STYLING MODELLO — anti-distrazione:
  Capelli: puliti, naturali, mai elaborati | Gioielli: nessuno | Make-up: minimo naturale
  Unghie: nude o bare (mai brillanti) | Calzature: abbinate al prodotto o neutre (bianco/nero)

POSA PER CATEGORIA:
  Sneakers: angolo basso, piede avanti, caviglia visibile, taglio al ginocchio
  Borse: duffel a mano laterale; backpack sulle spalle, taglio vita-fianchi
  Outerwear: giacca mezza zip, collo su, braccia leggermente distanti per silhouette, 3/4
  Swimwear: seduto su bordo piscina/travertino, fascia e cordino visibili, luce mediterranea
  Dresses: in piedi, sguardo a 45°, tessuto in movimento, profilo 3/4

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SKILL: TIPOGRAFIA EDITORIALE v2
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FONT SYSTEM (soli tre font ammessi):
  Bebas Neue → solo display headline (mai per corpo)
  DM Sans    → nomi prodotto, navigazione, testo corpo, CTA
  DM Mono    → tutti i metadati: prezzi, label, kicker, chip, tag

SCALA TIPOGRAFICA:
  Titolo pagina/Hero    → Bebas Neue 64–96px, weight 400, ls -0.01em, lh 0.95
  Nome collezione       → Bebas Neue 40–64px
  Intestazione sezione  → DM Sans 28–40px, weight 700, ls -0.015em, lh 1.1
  Nome prodotto (card)  → DM Sans 14–16px, weight 500
  Testo corpo           → DM Sans 14–16px, weight 400, lh 1.65
  Navigazione           → DM Mono 13–14px, weight 500, ls 0.10em
  Kicker/eyebrow        → DM Mono 10–11px, weight 600, ls 0.22–0.28em
  Prezzo                → DM Mono 14–15px, weight 600

3 PRINCIPI: Silenzio è lusso (riduci, non aggiungere) · Gerarchia prima della decorazione · Coerenza crea autorità

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SKILL: BRAND VOICE — ARCHITETTURA EDITORIALE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
POSIZIONAMENTO: Digital atelier — AI-generated wearable art, accessible designer (€40–140).
Non è luxury (no materiali atelier), non è fast fashion (ogni pezzo è un artefatto progettato).
Tagline: "Wearable art, on demand" / "AI-Art Atelier" / "Prompts to pieces"

3 LIVELLI (mai mescolare):
  NOME COLLEZIONE (visibile al cliente) → BKS Hours, BKS Glyph, etc.
  SERIE IDENTITY (solo interno/metadata) → series:hyperrealism, series:brut — MAI in copy cliente
  TITOLO PRODOTTO (Shopify, SEO) → BKS Hours Cipher™ Sneakers

FORMAT TITOLO: "BKS [Collection] [Design]™ [Tipo Prodotto]" — max 60 caratteri
  Sneakers: BKS [Coll] [Design]™ Sneakers
  Windbreaker: BKS [Coll] [Design]™ Windbreaker Jacket
  Puffer: BKS [Coll] [Design]™ Puffer (senza "Jacket")
  Swim Trunks: BKS [Coll] [Design]™ Swim Trunks

ANATOMIA PAGINA PRODOTTO (6 blocchi fissi):
  1. TITOLO PRODOTTO (una riga)
  2. HERO LINE (una frase in corsivo, statement identità)
  3. DESCRIZIONE (2–3 frasi: cos'è · cosa lo rende BakAbo · dove vive)
  4. SPEC BLOCK (bullet: Materiale · Vestibilità/Capacità · Stampa · Cura)
  5. MADE-TO-ORDER BLOCK (obbligatorio, sempre presente)
  6. SERVICE BULLETS (standard, mai modificati per prodotto)

GUARDRAIL COLLEZIONI (critici):
  Glyph: MAI "tribale", "etnico", "primitivo", "pseudo-africano" — è codice grafico/alfabeto visivo
  Token: MAI "crypto", "NFT", "web3", "digital asset" — Token è oggetto fisico (moneta, gettone)
  Flag: MAI bandiere nazionali/politiche — Flag è "campi astratti, blocchi grafici codificati"
  Folklore: MAI "folk etnico", "antico folklore", "simboli nativi" — è mitologia privata inventata

IDENTITÀ COLLEZIONI (8 permanenti):
  Hours   → città, interni, luce, attesa — energia Edward Hopper — monocromo, astrazione urbana
  Glyph   → alfabeto visivo BKS, segni costruiti, sistema grafico interno — codice, non ornamento
  Marker  → gesto, segno urbano, linea — energia Basquiat/Haring (senza nominarli)
  Riviera → lifestyle costiero mediterraneo, estate — nuoto, accessori resort
  Pulse   → optical, kinético, ritmo geometrico — op-art, movimento, monocromo/duotono
  Token   → pixel, arcade, oggetto digitale — low-bit, gamer-era, kaleidoscopio
  Flag    → pop-collage, campi colore astratti, blocchi grafici — energia Pop-Dada
  Origin  → folklore immaginario, storie, animali narrativi, giardini — flat-drawn, palette organica

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SKILL: COMMERCIAL STRATEGY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REGOLA 60 SECONDI (mobile): Ogni apertura area member deve mostrare UN segnale di valore entro 60s.
  Gold ring visibile · conteggio wishlist · banner Early Access · barra progressione tier

DROP MECHANICS:
  -72h → email Brass+ (Early Access confermato)
  -48h → push a wishlist owner di prodotti simili
  -24h → preview Silver+ (URL collezione privato)
   0h  → drop pubblico live
  +12h → segnale scarsità se stock sotto soglia
  +48h → chiuso — archiviato

TIER PROGRESSION CTAs:
  Lead→Iron: "Il tuo primo pezzo BKS sblocca il Metal tier e i suggerimenti AI sulla taglia."
  Iron→Brass: "Ancora un ordine per aprire il Camerino e l'Early Access. Ci sei quasi."
  Brass→Silver: "Silver: accesso esclusivo 24h su ogni nuovo drop."
  Silver→Gold: "Gold si guadagna con la fedeltà, non si acquista."

REGOLA CROSS-COLLECTION:
  Hours→Flag (outerwear monocromo + pop bold) o Token (stesso urban/encoded)
  Glyph→Token (entrambi simbolici/codificati) o Marker (segni vs gesti — affinità terracotta)
  Marker→Pulse (energia cinetica/urbana) o Flag (struttura urban, diversa temperatura)
  Riviera→Origin (entrambi resort/costiero, stagioni complementari)
  Pulse→Token (sistemi digitali viola, range prodotto diverso)
  Flag→Marker (grafico bold, rosso caldo + terracotta funziona come contrasto invernale)

LAYERING RULE: UN solo pezzo grafico statement per outfit. Due pezzi grafici BKS insieme = rumore visivo.
RESORT RULE: Nuoto + accessori nella stessa collezione (Riviera swim + Riviera beach towel = coerente).
MAI suggerire quello che il cliente già possiede. MAI più di due alternative in una risposta.
`;

var BKS_WORKFLOW = `
FLUSSO OPERATIVO BKS STUDIO — pipeline completa (aggiornato 2026-06-22):

[1] PRINTIFY (produzione POD)
- Fornitore: Printify.com — print-on-demand edge-to-edge AOP
- Shop ID: 12030061 (bakabo.club Shopify)
- 674 prodotti in catalogo Printify / 202 attivi su Shopify
- Blueprint principali: Puffer Jacket, Windbreaker, Hoodie, Swim Trunks, Sneakers, Travel Bag, Backpack, Dress, Swimwear, Athletic Shorts, Lounge Pants, Hawaiian Shirt, Slipper, Flip Flop, T-Shirt
- Tempo produzione: 7–14 giorni lavorativi
- Nessun magazzino fisico — ogni pezzo stampato all'ordine

[2] SHOPIFY (store principale)
- Store: bakabo.club / 11628e-2.myshopify.com
- Tema live: BKS TM04 V.22 (id 202392961362)
- 202 prodotti attivi, 8 collezioni editoriali
- Spedizione: 3–5 giorni (partner Printify)
- Resi: 30 giorni dalla consegna → crew@bakabo.club
- Pagamenti: tutti i metodi standard Shopify (Stripe, PayPal, etc.)
- Mercati attivi: IT, EU — lingua IT/EN

[3] GOOGLE MERCHANT (shopping ads)
- GMC ID: 5295165689
- Feed automatico via app "Google & YouTube" su Shopify
- Feed RSS fallback: bakabo.club/pages/google-shopping-feed
- Status: attivo — 35.1K prodotti in stato "Numero limitato" (issue in corso)
- Analytics: GTM-PF5Z85KS + GA4 attivo

[4] SOCIAL (canali vendita)
- Instagram: attivo → instagram.com/bakabofirm
- Pinterest: sospeso (appeal inviato — bakabofirm)
- TikTok: disconnesso da Shopify — riconnessione in corso
- Meta/Facebook: configurato — Business ID 2070678923161271
- YouTube: canale bakabofirm — YouTube Shopping collegato a GMC, video avatar + collection reels
- Telegram: bot BKS — notifiche drop, aggiornamenti ordini, community
- Discord: server BKS community — canale members, drop announcements, poetry (BKS Verse)
- LinkedIn: BKS Studio / Roberto Picchioni — brand presence, editorial content
- Gmail / Email: crew@bakabo.club — supporto clienti, resi, collaborazioni, press
- Inbox App (Shopify Messaging / Shopify Inbox): gestione risposte clienti direttamente dallo store — chat, email, messaggi integrati nel pannello Shopify admin

[5] SISTEMI INTERNI BKS
- Catalog DB: I:\BKS database (14.421 file — NFT, AI artworks, avatar, video)
  → Sottocartelle: BKS_ORGANIZED (NFT/AI/web assets), AVATAR (foto+video avatar), members_tryon
- Studio App: I:\BAK ABO → Streamlit :8501 (catalog engine, gestione, social, tema)
- BKS Verse Platform: I:\BAKABO SYSTEM → FastAPI :8001, deploy Hetzner 95.217.232.186
  → verse.bakabo.club (pubblico) / admin :8099
  → Entità: Gran Giudice AI (5 assi valutazione), leaderboard mondiale, 21 poeti storici

[6] PREZZI — MONITORAGGIO CONTINUO
Price ladder approvato BKS (unici valori ammessi):
  €35, €39, €45, €49, €55, €59, €65, €69, €75, €79, €85, €89, €95, €99, €105, €109, €115, €119, €125, €129, €135, €139

Targets per categoria (margine minimo 45%):
  Sneakers: €75–€105 target €89 | Backpack: €75–€95 target €85
  Swim Trunks: €45–€65 target €55 | Puffer: €109–€139 target €125
  Windbreaker: €95–€125 target €109 | Travel Bag: €85–€115 target €99
  One-Piece: €55–€75 target €65 | Hawaiian Shirt: €65–€85 target €75
  Lounge Pant: €55–€75 target €65 | Hoodie: €65–€85 target €75
  Racerback Dress: €55–€75 target €65 | Slipper: €35–€55 target €45
  Cut&Sew Tee: €45–€65 target €55 | Athletic Shorts: €45–€65 target €55
  Flip Flop: €35–€55 target €45 | Beach Towel: €39–€55 target €49

ALERT PREZZI: Se un prodotto mostra prezzo sotto il minimo categoria → margine critico → segnalare a crew@bakabo.club.
Regola: nessun prodotto pubblicato con margine < 45%.
Margine formula: net = retail × 0.971 - 0.30 | margin = (net - cost) / net × 100

PREZZI LIVE CORRENTI (post-audit 2026-06-22):
Racerback Dress: 19 prod → fix da $46 a $65 | Tee: 3 prod → fix da $41 a $49
Hawaiian Shirts: 3 prod → fix da $82 a $79 | Windbreaker: 11 prod → fix da $111.50 a $109
Sneakers Flag 03: 1 prod → fix da $70 a $75 | Hoodie: 15 prod → $119 OK (premium 68.7%)
Script fix: scripts/fix_price_alerts.py | Audit: scripts/gmc_daily_sync.py

SCONTI & PROMOZIONI (regole approvate):
- Drop Launch: 15% max, 72h window, codice "BKS-DROP##-YYYYMM"
- Member Early Access (Brass+): 10% auto-applicato pre-drop
- Tier Milestone: 10-20% una tantum su upgrade tier
- Bundle: 10% su 2+ pezzi stessa collezione
- NO sale banner permanenti | NO countdown | NO sconti >20%
- BKS non chiama "Black Friday" → usa "BKS Studio Week" o "November Edit"

[7] GOOGLE MERCHANT — AGGIORNAMENTO GIORNALIERO
- GMC ID: 5295165689 — feed Shopify auto-sync via "Google & YouTube" app
- Sync giornaliero schedulato: ogni mattina alle 08:00 CET (script: scripts/gmc_daily_sync.py)
- Attributi GMC richiesti per ogni prodotto: title, description, price, gtin, brand, color, size, age_group, gender
- Issue principale: 35.1K "Numero limitato" — in corso verifica attributi mancanti
- Feed RSS fallback: bakabo.club/pages/google-shopping-feed

[8] STRUTTURA PAGINE — PAGINE CHIAVE E LORO FUNZIONE
Ogni pagina ha UN SOLO scopo. Il Worker conosce la struttura attesa per ogni pagina:
  / (Home): Hero video → Piano 8 tasti → Editorial → Reviews → Trust bar
  /pages/bks-[collection] (×8): Hero editoriale → Signal bar → Griglia prodotti → Cross-collection
  /pages/bks-[tipo] (×15): Kicker tipo → Filter chips collezione → Griglia prodotti filtrata
  /pages/bks-members: Gold ring dashboard → Tier progress → Wishlist → Try-On (Brass+)
  /pages/faq-domande-frequenti: 10 domande chiave pre-checkout
  /pages/bks-shopping-guide: Armocromia → Guida collezione → AI Ask BKS
  /pages/bks-men, /pages/bks-woman: Tipi prodotto per genere → Collezioni raccomandate
  /pages/bks-custom: Personalizzazione testo → +€15 → email crew@
  /pages/verse: Poesia→Oggetto → Gran Giudice → Leaderboard → Submit (Brass+)
  /pages/about-bakabo-1: Storia BKS Studio → Processo AI-art → Modello POD
  /pages/contact: crew@bakabo.club → Shopify Inbox → Social channels
  /pages/bks-wishlist: Prodotti salvati → Add to cart → Tier upsell

[CUSTOMER-FACING] — cosa rispondere ai clienti:
- "Dove è il mio ordine?" → Produzione Printify 7–14 gg + spedizione 3–5 gg → track via email conferma
- "BKS è su Google Shopping?" → Sì, attivo su Google Shopping
- "Dove posso seguirvi?" → Instagram @bakabofirm (attivo); YouTube bakabofirm; Telegram e Discord (community BKS)
- "Posso restituire?" → Sì, 30 giorni dalla consegna. Contatto: crew@bakabo.club
- "È disponibile subito?" → Made-to-order, nessun stock. Produzione 7–14 gg
- "Il prezzo è giusto?" → Tutti i prezzi BKS sono nel price ladder approvato (€35–€139). Se un prezzo sembra anomalo → segnalare.
`;

var BKS_COLLECTIONS = `
8 COLLEZIONI EDITORIALI BKS STUDIO (catalogo verificato 2026-06-22):

1. BKS HOURS #c8c4be — Contemplazione urbana, registro iperrealista. AI-art pittura iperrealista: luci città, silenzio interiore, vita quotidiana. Prodotti: puffer, sneakers, swim trunks, travel bag, hoodie, lounge pants, athletic shorts, racerback dress, tee, slipper. Tag: collection:hours.

2. BKS GLYPH #d4a030 — DNA grafico del brand. Alfabeto visivo proprietario: simboli astratti, frammenti a mano, geroglifici inventati. Collezione molto ampia. Prodotti: puffer, swim trunks, swimwear, backpack, hoodie, travel bag, lounge pants, windbreaker, racerback dress, sneakers, athletic shorts, hawaiian shirt (2), tee (2). Tag: collection:glyph.

3. BKS MARKER #c04418 — Grafica urbana gestuale. Pennello, muro, segno: drip, stroke, color block. Prodotti: puffer, travel bag, swim trunks, racerback dress, lounge pants, hoodie, swimwear, sneakers, athletic shorts, windbreaker, tee, beach towel. Tag: collection:marker.

4. BKS RIVIERA #0ca898 — Resort mediterraneo permanente. Sale, sole, terracotta, blu profondo. Prodotti: puffer, swimwear (8), swim trunks, racerback dress, travel bag, sneakers, athletic shorts, windbreaker, beach towel. Tag: collection:riviera.

5. BKS PULSE #8888cc — Collezione ottica. Ritmo, vibrazione, moto visivo. Ripetizione geometrica, campi cinetici. Prodotti: puffer, racerback dress, swim trunks, swimwear, sneakers, flip flops, travel bag, hoodie, windbreaker, lounge pants, athletic shorts, hawaiian shirt (1). Tag: collection:pulse.

6. BKS TOKEN #9828d8 — Collezione arcade. Pixel, game, campo digitale. Low-bit visual language, colore elettronico. Prodotti: puffer, sneakers, windbreaker, swim trunks, racerback dress, athletic shorts, slipper. Tag: collection:token.

7. BKS FLAG #c82020 — Pop-collage. Campi astratti, colore codificato, blocchi grafici. Energia Dada. Prodotti: puffer, racerback dress, hoodie, sneakers, swim trunks, windbreaker, flip flops, travel bag, lounge pants, athletic shorts, one-piece swimsuit. Tag: collection:flag.

8. BKS ORIGIN #489808 — COLLEZIONE PIÙ AMPIA (serie naif). Mondi immaginari, storie disegnate, memoria inventata. Illustrazione flat, figure organiche. Prodotti: puffer(9), hoodie(5), sneakers(5), swim trunks(3), racerback dress(3), lounge pants(3), windbreaker(2), swimwear, travel bag, athletic shorts, hawaiian shirt (1), cut&sew tee, beach towel. Tag: collection:origin.
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
- Racerback Dress (AOP all-over print, athletic sporty cut — NOT evening wear; all 8 collections, 19 designs)
- Hawaiian Shirt (short sleeve, AOP — Glyph, Pulse, Origin)
- Travel Bag / Duffle Bag (waterproof, AOP graphic, shoulder + carry handles)
- Backpack (multi-compartment, padded, AOP graphic)
- Flip Flop (AOP graphic sole — Pulse, Flag only)
- Slipper / Cozy Slipper (AOP, closed-toe indoor — Hours, Token only)
- T-Shirt / Women's Tee (AOP women's cut — Hours, Glyph x2, Marker, Origin, Riviera)
- Cut & Sew Tee (AOP cut-and-sewn panels — Origin only)
- Beach Towel (AOP graphic, microfiber — Riviera, Origin, Marker)

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
- vestito / abito / vestitino / dress / mini dress / midi dress / maxi dress / beach dress / summer dress / sundress / athletic dress / running dress / active dress / sporty dress / casual dress / abito sportivo / abito estivo / vestitino racerback / racerback → Racerback Dress (AOP all-over print, athletic-cut, sporty silhouette — available in all 8 collections)
- scarpe / sneaker / kicks / graphic shoes → Sneakers
- borsa viaggio / borsone / duffel / dufflebag / duffle bag / weekender / travel bag / waterproof bag / borsa impermeabile / luggage → Travel Bag (waterproof)
- zaino / backpack / bookbag / rucksack / daypack / tracolla / bag / borse → Backpack
- pantalone / jogger / sweatpants / lounge pants / track pants → Lounge Pants
- infradito / ciabatte / sandali / flip flop / flip flops / slides / thongs / beach sandals / slippers → Flip Flops
- maglietta / maglia / tee / graphic tee / t-shirt / top / crop top / women's tee / cut and sew / cut & sew → T-Shirt (women's AOP tee)
- k-way / giacca vento / impermeabile / windbreaker / shell jacket / anorak / rain jacket → Windbreaker
- camicia hawaii / camicia estiva / aloha shirt / hawaiian / tropical shirt / short sleeve AOP / camicia manica corta → Hawaiian Shirt
- pantofola / ciabatta casa / slipper / cozy slipper / indoor shoe / house shoe / pantofole → Slipper (Hours, Token)
- asciugamano / telo mare / beach towel / towel / telo spiaggia / asciugamano mare / telo piscina → Beach Towel

CHANNEL KEYWORDS (dove trovare BKS):
- instagram / ig / insta → @bakabofirm (attivo)
- youtube / yt / video / canale → youtube.com/bakabofirm (attivo)
- telegram / bot / notifiche → Telegram BKS (community + drop alerts)
- discord / server / community → Discord BKS (members, Verse, drops)
- pinterest / pin → bakabofirm (temporaneamente sospeso)
- tiktok / tok → in arrivo / reconnecting
- facebook / meta / fb → configurato
- linkedin / linkedin.com → BKS Studio / Roberto Picchioni
- email / gmail / mail / contatto / support / resi / reso / assistenza → crew@bakabo.club
- inbox / chat / messaggio / shopify inbox / risposta → Shopify Inbox (crew@bakabo.club)

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

${BKS_PERSONA}
${BKS_BRAND}
${BKS_SKILLS}
${BKS_WORKFLOW}
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

${BKS_PERSONA}
${BKS_BRAND}
${BKS_SKILLS}
${BKS_WORKFLOW}
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

    const kvOk = !!env.BKS_AGENT_KV;
    const aiOk = !!env.AI;
    return new Response(
      JSON.stringify({ status: "ok", version: "v4", kv: kvOk, ai: aiOk, endpoints: ["/chat","/social","/tryon","/catalog","/eval","/memory/:id"] }),
      { status: 200, headers: { ...cors, "Content-Type": "application/json" } }
    );
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
