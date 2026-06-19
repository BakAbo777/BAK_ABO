/**
 * BKS Agent Refresh — Cloudflare Worker
 *
 * Cron: daily at 10:00 UTC (12:00 CET / 12:00 CEST)
 *
 * Pulls current product catalog + collections from Shopify and stores
 * a lightweight snapshot in Cloudflare KV for the BKS AI agent to consume.
 *
 * KV bindings (set in wrangler.toml):
 *   BKS_AGENT_KV — namespace for agent data
 *
 * Env vars (Worker secrets):
 *   SHOPIFY_DOMAIN      = 11628e-2.myshopify.com
 *   SHOPIFY_TOKEN       = shpat_...
 *   SHOPIFY_API_VERSION = 2025-01
 */

const MAX_PRODUCTS    = 250;
const MAX_COLLECTIONS = 50;

async function fetchShopify(env, path) {
  const url = `https://${env.SHOPIFY_DOMAIN}/admin/api/${env.SHOPIFY_API_VERSION}${path}`;
  const r   = await fetch(url, {
    headers: { 'X-Shopify-Access-Token': env.SHOPIFY_TOKEN },
  });
  if (!r.ok) throw new Error(`Shopify ${path} → ${r.status}`);
  return r.json();
}

async function buildCatalogSnapshot(env) {
  const [prodData, customCollData, smartCollData] = await Promise.all([
    fetchShopify(env, `/products.json?limit=${MAX_PRODUCTS}&fields=id,title,handle,status,variants,tags,product_type`),
    fetchShopify(env, `/custom_collections.json?limit=${MAX_COLLECTIONS}&fields=id,title,handle`),
    fetchShopify(env, `/smart_collections.json?limit=${MAX_COLLECTIONS}&fields=id,title,handle`),
  ]);

  const products = (prodData.products || []).filter(p => p.status === 'active').map(p => ({
    id:    p.id,
    title: p.title,
    handle: p.handle,
    type:  p.product_type,
    tags:  p.tags,
    variants: (p.variants || []).map(v => ({
      id:    v.id,
      title: v.title,
      price: v.price,
      sku:   v.sku,
      stock: v.inventory_quantity,
    })),
  }));

  const seen = new Set();
  const collections = [
    ...(customCollData.custom_collections || []),
    ...(smartCollData.smart_collections   || []),
  ]
    .filter(c => { if (seen.has(c.handle)) return false; seen.add(c.handle); return true; })
    .map(c => ({ id: c.id, title: c.title, handle: c.handle }));

  return {
    updated_at:    new Date().toISOString(),
    product_count: products.length,
    products,
    collections,
  };
}

export default {
  // HTTP handler — manual trigger via GET /refresh
  async fetch(request, env) {
    if (request.method === 'GET') {
      try {
        const snapshot = await buildCatalogSnapshot(env);
        await env.BKS_AGENT_KV.put('system:catalog_snapshot', JSON.stringify(snapshot), {
          expirationTtl: 90000, // ~25h, refreshed daily
        });
        return new Response(
          `OK — ${snapshot.product_count} prodotti aggiornati alle ${snapshot.updated_at}`,
          { status: 200 }
        );
      } catch (e) {
        return new Response(`Errore: ${e.message}`, { status: 500 });
      }
    }
    return new Response('BKS Agent Refresh Worker', { status: 200 });
  },

  // Cron handler — runs at 10:00 UTC every day
  async scheduled(event, env, ctx) {
    ctx.waitUntil((async () => {
      try {
        const snapshot = await buildCatalogSnapshot(env);
        await env.BKS_AGENT_KV.put('system:catalog_snapshot', JSON.stringify(snapshot), {
          expirationTtl: 90000,
        });
        console.log(`[BKS Agent Refresh] OK — ${snapshot.product_count} prodotti @ ${snapshot.updated_at}`);
      } catch (e) {
        console.error(`[BKS Agent Refresh] ERRORE: ${e.message}`);
      }
    })());
  },
};
