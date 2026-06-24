---
name: bakabo-system-connections
description: >
  Mappa completa di tutti i collegamenti del sistema BKS — servizi locali, cloud, tablet, SSH,
  Google/Analytics, cassaforte credenziali, posta Gmail. Pagina monitor: pages/11_Sistema_BKS.py
  Trigger: "come accedo", "quale porta", "tablet", "server finlandese", "Hetzner", "google merchant",
  "analytics", "GTM", "GA4", "cassaforte", "credenziali", "gmail", "posta", "link rapido", "come entro".
metadata:
  type: skill
  version: "3.0"
  created: "2026-06-22"
  updated: "2026-06-24"
---

# SKILL — BKS SYSTEM CONNECTIONS

## Servizi locali (PC Roberto — I:\BAK ABO)

| Servizio | Porta | URL locale | URL tablet |
|---|---|---|---|
| BKS Studio (Streamlit) | 8501 | http://localhost:8501 | http://192.168.1.103:8501 |
| Try-On AI Engine | 8010 | http://127.0.0.1:8010 | (solo locale) |

**Avvio:** `00_START_BKS_MASTER.bat` → menu [1] Studio [2] Try-On [A] Tutto  
**Config Streamlit:** `.streamlit/config.toml` — `address = "0.0.0.0"` (tablet abilitato)  
**Firewall:** regola "BKS Streamlit 8501" in Windows Defender  
**Versione Streamlit:** 1.58.0 (ultima disponibile, verificato 24/06/2026)

## Server Hetzner Helsinki — BKS Verse

| Risorsa | Valore |
|---|---|
| IP | 95.217.232.186 |
| FastAPI :8001 | http://95.217.232.186:8001 |
| Admin :8099 | solo SSH tunnel: `ssh -L 8099:localhost:8099 root@95.217.232.186` |
| Dominio | https://verse.bakabo.club |
| Source locale | I:\BAKABO SYSTEM\ |
| Deploy | scripts/deploy_shopify.py |

## Cloudflare Workers

| Worker | URL | Funzione |
|---|---|---|
| bks-agent (v16) | https://bks-agent.bakabo.workers.dev/chat | AI Assistant + /social + /origins + KV+AI bindings |
| bks-agent (health) | https://bks-agent.bakabo.workers.dev/health | Health check — kv:true, ai:true |
| bks-account-redirect | account.bakabo.club/* | Redirect → /pages/bks-members |
| bks-agent-refresh | bks-agent-refresh.bakabo.workers.dev | Cron 12:00 CET agent refresh |

**Nota deploy Worker:** Cloudflare REST API (non wrangler — VPN blocca TLS).  
Script: `cloudflare/bks-ai-worker.js` — deploy via PowerShell multipart/form-data.  
Bindings: KV `BKS_AGENT_KV` (ID `8f6b1e4accae47949b2960735d270a3a`) + Workers AI `AI`.

## Shopify — link admin

| Risorsa | URL |
|---|---|
| Store live | https://bakabo.club |
| Admin | https://admin.shopify.com/store/11628e-2 |
| Theme Editor | https://11628e-2.myshopify.com/admin/themes/202392961362/editor |
| Member Area | https://bakabo.club/pages/bks-members |
| AI Assistant | https://bakabo.club/pages/bks-ai-assistant |

**Tema:** TM04 V.22 · ID `202392961362` · Token System 3-layer live (20 file CSS, 24/06/2026)

## Servizi esterni

| Servizio | URL / note |
|---|---|
| Printify | https://printify.com/app — shop ID 12030061 |
| Google Merchant | GMC ID 5295165689 — 35.1K prodotti, limited_quantity issue |
| Cloudflare | account e796d289f744035eee2641e853d8a5af |
| Pinterest | bakabofirm sospeso — appeal inviato |

## Accesso da tablet — procedura

1. PC acceso con Streamlit attivo (BAT avviato)
2. Tablet e PC sulla stessa rete Wi-Fi (subnet 192.168.1.x)
3. Browser tablet → `http://192.168.1.103:8501`
4. Se non raggiunge: verifica regola Firewall Windows porta 8501

## Monitor sistema

Pannello live: `pages/11_Sistema_BKS.py` — ping automatico ogni 25s su tutti i servizi.  
KPI visibili: prodotti (202), collezioni (8), tema (V.22), worker (v16), servizi live, % sistema.
