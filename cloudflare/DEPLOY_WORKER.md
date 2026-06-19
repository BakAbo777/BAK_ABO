# Deploy BKS Agent Worker su Cloudflare

## Metodo rapido — CLI (raccomandato)

Doppio click su `DEPLOY_NOW.bat`. Segue 5 step guidati:

1. Login browser Cloudflare
2. Crea KV namespace → copia ID → aggiornalo in `wrangler.toml`
3. Deploy Worker
4. Configura secrets (OpenAI, Shopify, BKS token)
5. Verifica con `wrangler tail`

Worker live: `https://bks-agent.bakabo.workers.dev`

---

## Metodo manuale — Dashboard

1. `https://dash.cloudflare.com` → Workers & Pages → Create Worker
2. Nome: `bks-agent`
3. Incolla `bks-ai-worker.js` → Deploy
4. KV & Storage → KV → Create namespace `BKS_AGENT_KV`
5. Workers → bks-agent → Settings → Bindings → Add KV → binding: `BKS_AGENT_KV`
6. Settings → Variables → Secrets (aggiungi tutti):
   - `OPENAI_API_KEY`
   - `SHOPIFY_DOMAIN` — es: `11628e-2.myshopify.com`
   - `SHOPIFY_TOKEN`
   - `SHOPIFY_API_VERSION` — `2025-01`
   - `BKS_AI_TOKEN` — token libero (blocca scraping)
7. Settings → Triggers → Cron: `0 10 * * *`

---

## Cosa fa il Worker

**Endpoint `/chat` (POST)** — BKS Multi-Agent AI per clienti bakabo.club.
Classifica il messaggio → route verso catalog / support / customization / tier agent → risposta GPT-4o.

**Cron `0 10 * * *` (12:00 CET)** — catalog refresh Shopify + valutazione performance agenti.
Salva snapshot in KV (`system:catalog_snapshot`), aggiorna metriche, segnala agenti sotto soglia 60.

**Endpoint `/eval` (GET)** — ultimo report valutazione agenti.
**Endpoint `/catalog` (GET)** — snapshot catalogo corrente in KV.
**Endpoint `/memory/{customer_id}` (GET)** — profilo + history cliente.

---

## Connetti al widget Shopify

Dopo il deploy, il widget `bks-ai-assistant-embed.liquid` usa:
`data-endpoint="{{ shop.metafields.bks.ai_endpoint | default: '' }}"`

Shopify Admin → Impostazioni → Metafields → Shop:
- Namespace: `bks` | Chiave: `ai_endpoint`
- Valore: `https://bks-agent.bakabo.workers.dev`

---

## Test

```bash
curl -X POST https://bks-agent.bakabo.workers.dev/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Quanto tempo ci vuole per la spedizione?", "customer_id": "test-1"}'
```

---

## Costo stimato

- Workers Free: 100.000 req/giorno gratuiti
- KV: 100.000 read/giorno gratuiti
- OpenAI GPT-4o: ~€0.002/risposta → 1.000 chat/mese ≈ €2
