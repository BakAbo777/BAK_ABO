/**
 * BKS Tier Upgrade — Cloudflare Worker
 *
 * Receives Shopify `orders/paid` webhook → upgrades customer tier tag.
 *
 * Tier logic:
 *   orders_count == 1  → remove bks-subscriber, add bks-drop
 *   orders_count >= 2  → remove bks-subscriber + bks-drop, add bks-archive
 *
 * Env vars (Cloudflare dashboard → Worker → Settings → Variables):
 *   SHOPIFY_DOMAIN      = 11628e-2.myshopify.com
 *   SHOPIFY_TOKEN       = shpat_...
 *   SHOPIFY_API_VERSION = 2025-01
 *   SHOPIFY_HMAC_SECRET = (webhook secret from Shopify)
 */

const BKS_TIERS = ['bks-subscriber', 'bks-drop', 'bks-archive'];

async function verifyHmac(request, secret) {
  const hmacHeader = request.headers.get('X-Shopify-Hmac-Sha256');
  if (!hmacHeader || !secret) return true; // skip in dev
  const body = await request.clone().arrayBuffer();
  const key  = await crypto.subtle.importKey(
    'raw', new TextEncoder().encode(secret),
    { name: 'HMAC', hash: 'SHA-256' }, false, ['sign']
  );
  const sig    = await crypto.subtle.sign('HMAC', key, body);
  const b64    = btoa(String.fromCharCode(...new Uint8Array(sig)));
  return b64 === hmacHeader;
}

async function getCustomer(env, customerId) {
  const url = `https://${env.SHOPIFY_DOMAIN}/admin/api/${env.SHOPIFY_API_VERSION}/customers/${customerId}.json?fields=id,orders_count,tags`;
  const r   = await fetch(url, { headers: { 'X-Shopify-Access-Token': env.SHOPIFY_TOKEN } });
  if (!r.ok) return null;
  return (await r.json()).customer;
}

async function updateCustomerTags(env, customerId, tags) {
  const url = `https://${env.SHOPIFY_DOMAIN}/admin/api/${env.SHOPIFY_API_VERSION}/customers/${customerId}.json`;
  const r   = await fetch(url, {
    method: 'PUT',
    headers: {
      'X-Shopify-Access-Token': env.SHOPIFY_TOKEN,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ customer: { id: customerId, tags } }),
  });
  return r.ok;
}

function computeNewTags(existingTagsStr, ordersCount) {
  const tags = existingTagsStr
    .split(',')
    .map(t => t.trim())
    .filter(t => t && !BKS_TIERS.includes(t));

  if (ordersCount >= 2) {
    tags.push('bks-archive');
  } else if (ordersCount === 1) {
    tags.push('bks-drop');
  } else {
    tags.push('bks-subscriber');
  }

  return tags.join(', ');
}

export default {
  async fetch(request, env) {
    if (request.method !== 'POST') {
      return new Response('BKS Tier Webhook OK', { status: 200 });
    }

    // HMAC verification
    const valid = await verifyHmac(request, env.SHOPIFY_HMAC_SECRET);
    if (!valid) {
      return new Response('Unauthorized', { status: 401 });
    }

    // customers/update sends full customer object directly
    let customer;
    try {
      customer = await request.json();
    } catch {
      return new Response('Bad JSON', { status: 400 });
    }

    const customerId  = customer?.id;
    const ordersCount = customer?.orders_count ?? 0;
    const oldTags     = customer?.tags || '';

    if (!customerId) {
      return new Response('No customer id', { status: 200 });
    }

    // Only act when orders_count is 1 or 2 (tier transition points)
    if (ordersCount < 1) {
      return new Response('No orders yet — skip', { status: 200 });
    }

    const newTags = computeNewTags(oldTags, ordersCount);

    if (newTags === oldTags) {
      return new Response('No change', { status: 200 });
    }

    const updated = await updateCustomerTags(env, customerId, newTags);
    const msg     = updated
      ? `Tier upgraded: customer ${customerId} orders=${ordersCount} tags="${newTags}"`
      : `Failed to update customer ${customerId}`;

    console.log(msg);
    return new Response(msg, { status: 200 });
  },
};
