/**
 * BKS Multi-Agent Orchestrator — Cloudflare Worker
 *
 * Endpoints:
 *   POST /chat          → customer message → routed agent response
 *   GET  /eval          → latest performance report
 *   GET  /memory/:id    → customer profile + history summary
 *   GET  /catalog       → current catalog snapshot
 *
 * KV bindings (wrangler.toml):
 *   BKS_AGENT_KV
 *
 * Secrets:
 *   OPENAI_API_KEY, SHOPIFY_DOMAIN, SHOPIFY_TOKEN, SHOPIFY_API_VERSION
 *
 * Cron: "0 10 * * *" → daily evaluation + catalog refresh
 */

import { BKSMemory }                                   from './memory.js';
import { catalogAgent, customAgent, supportAgent, tierAgent } from './agents.js';
import { runEvaluation }                               from './evaluator.js';

const OPENAI_URL = 'https://api.openai.com/v1/chat/completions';

// ── Intent classifier ────────────────────────────────────────────────────────

async function classifyIntent(env, message) {
  const r = await fetch(OPENAI_URL, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${env.OPENAI_API_KEY}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model: 'gpt-4o-mini',
      temperature: 0,
      messages: [{
        role: 'system',
        content: `Classifica il messaggio in UNO di questi intent (rispondi SOLO con il nome):
catalog      → domande su prodotti, collezioni, prezzi, disponibilità
customization → richieste di personalizzazione, testo su capo, custom order
support      → ordini, spedizioni, resi, rimborsi, problemi
tier         → domande sul proprio tier/membership BKS
greeting     → saluti generici senza richiesta specifica`,
      }, { role: 'user', content: message }],
    }),
  });
  const data = await r.json();
  return (data.choices?.[0]?.message?.content ?? 'support').trim().toLowerCase();
}

// ── Router ───────────────────────────────────────────────────────────────────

async function route(intent, context) {
  switch (intent) {
    case 'catalog':       return catalogAgent(context);
    case 'customization': return customAgent(context);
    case 'tier':          return tierAgent(context);
    case 'greeting':      return { reply: 'Ciao! Come posso aiutarti? Puoi chiedermi info su prodotti, personalizzazioni, ordini o il tuo tier BKS.', resolved: true, escalate: false, sentiment: 'neutral' };
    default:              return supportAgent(context);
  }
}

// ── Catalog refresh (reuses agent_refresh_worker logic) ──────────────────────

async function refreshCatalog(env, memory) {
  const url = `https://${env.SHOPIFY_DOMAIN}/admin/api/${env.SHOPIFY_API_VERSION}/products.json?limit=250&fields=id,title,handle,status,variants,tags,product_type`;
  const r   = await fetch(url, { headers: { 'X-Shopify-Access-Token': env.SHOPIFY_TOKEN } });
  if (!r.ok) return;
  const { products } = await r.json();
  const snapshot = {
    updated_at:    new Date().toISOString(),
    product_count: products.length,
    products:      products.filter(p => p.status === 'active').map(p => ({
      id: p.id, title: p.title, handle: p.handle, type: p.product_type,
      tags: p.tags,
      variants: (p.variants || []).map(v => ({ id: v.id, title: v.title, price: v.price, sku: v.sku })),
    })),
  };
  await memory.kv.put('system:catalog_snapshot', JSON.stringify(snapshot), { expirationTtl: 90000 });
  return snapshot;
}

// ── Main handler ─────────────────────────────────────────────────────────────

export default {
  async fetch(request, env) {
    const memory = new BKSMemory(env.BKS_AGENT_KV);
    const url    = new URL(request.url);

    // GET /eval
    if (request.method === 'GET' && url.pathname === '/eval') {
      const report = await memory.getEvalReport();
      return Response.json(report ?? { message: 'Nessun report disponibile' });
    }

    // GET /catalog
    if (request.method === 'GET' && url.pathname === '/catalog') {
      const cat = await memory.getCatalog();
      return Response.json(cat ?? { message: 'Catalog non disponibile' });
    }

    // GET /memory/:id
    if (request.method === 'GET' && url.pathname.startsWith('/memory/')) {
      const id      = url.pathname.split('/')[2];
      const profile = await memory.getProfile(id);
      const history = await memory.getHistory(id);
      return Response.json({ profile, turns: history.length, last: history.at(-1) ?? null });
    }

    // POST /chat
    if (request.method === 'POST' && url.pathname === '/chat') {
      let body;
      try { body = await request.json(); } catch { return new Response('Bad JSON', { status: 400 }); }

      const { message, customer_id = 'anonymous', customer_tier } = body;
      if (!message) return new Response('Missing message', { status: 400 });

      const t0 = Date.now();

      const [profile, history, catalog] = await Promise.all([
        memory.getProfile(customer_id),
        memory.getContextMessages(customer_id, 10),
        memory.getCatalog(),
      ]);

      if (customer_tier) profile.tier = customer_tier;

      const intent = await classifyIntent(env, message);
      const result = await route(intent, { message, customerProfile: profile, history, catalog, env });

      const ms = Date.now() - t0;

      await Promise.all([
        memory.appendHistory(customer_id, { role: 'user',      content: message }),
        memory.appendHistory(customer_id, { role: 'assistant', content: result.reply ?? '[escalated]', agent: intent }),
        memory.saveProfile(customer_id, { tier: profile.tier }),
        memory.recordCall(intent, { resolved: result.resolved, escalated: result.escalate, sentiment: result.sentiment, ms }),
      ]);

      return Response.json({
        reply:          result.reply ?? 'Richiesta inoltrata a un operatore BKS.',
        intent,
        resolved:       result.resolved,
        escalate:       result.escalate,
        custom_payload: result.customPayload ?? null,
        ms,
      });
    }

    return new Response('BKS Multi-Agent v1.0', { status: 200 });
  },

  // Cron: daily 12:00 CET — catalog refresh + performance evaluation
  async scheduled(event, env, ctx) {
    const memory = new BKSMemory(env.BKS_AGENT_KV);
    ctx.waitUntil((async () => {
      const [snapshot, report] = await Promise.all([
        refreshCatalog(env, memory),
        runEvaluation(memory),
      ]);
      console.log(`[BKS Cron] Catalog: ${snapshot?.product_count ?? 'ERR'} prodotti | Score: ${report.overall ?? 'N/A'}`);
      if (report.flags?.length) {
        console.warn(`[BKS Cron] Agenti sotto soglia: ${report.flags.map(f => f.agent).join(', ')}`);
      }
    })());
  },
};
