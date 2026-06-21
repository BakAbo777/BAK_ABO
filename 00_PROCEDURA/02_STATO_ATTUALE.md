# Stato Attuale — BKS Studio / bakabo.club

Aggiornato: 2026-06-20

## Domini Shopify

| Dominio | Stato |
| --- | --- |
| `bakabo.club` | Primary, Connected |
| `11628e-2.myshopify.com` | Connected |
| `bakabo.myshopify.com` | Connected |
| `www.bakabo.club` | Connected |
| `account.bakabo.club` | Customer Account Primary, Connected |

## Tema live

| Campo | Valore |
| --- | --- |
| ID | `202392961362` |
| Nome | BKS TM04 20_06_2026 V.22 |
| Ruolo | main (pubblicato) |
| Sorgente locale | `04_TEMA_SHOPIFY/_merged_tm04/` |
| Script deploy | `scripts/deploy_theme_section.py` |
| GTM | `GTM-PF5Z85KS` (live nel tema) |
| Lingua | Inglese unico (`locales/it.json` sovrascritto) |

## Stato sito live (20 Giugno 2026)

- Tutte le 8 collezioni editorial rispondono `200`
- Tutte le 18 collection product type attive e raggiungibili
- GTM `GTM-PF5Z85KS` live e attivo
- Area member live con metal tier system (Lead/Iron/Brass/Silver/Gold)
- Try-On Camerino accessibile da mobile (Brass+)
- BKS Shopping Guide live: `bakabo.club/pages/bks-shopping-guide`
- Help FAQ live in inglese: `bakabo.club/pages/help-faq`
- Selettore lingua rimosso (MutationObserver attivo nell'header)
- AI Assistant live globalmente: `bakabo.club/pages/bks-ai-assistant`
- Cloudflare Worker AI: `bks-agent.bakabo.workers.dev`
- Wishlist standalone: `bakabo.club/pages/bks-wishlist`
- Homepage (20/06): Video Hero → Weekly Editorial Vol.1/Issue 6 → Piano Hero (8 tasti) → Magazine → Reviews → Trust
- Pagine duplicate eliminate: `about-bakabo`, `bks-about-bks`
- Gold Ring animato: icona account header + avatar dashboard

## Catalogo

| Campo | Valore |
| --- | --- |
| CSV attivo | `collezioni_csv/collezione 12_06_2026_SHOPIFY_IMPORT_READY_SEO_TAGS_READY.csv` |
| DB SQLite | `collezioni_csv/bks_catalog.db` |
| Prodotti live | 202 (8 collezioni × product type) |
| Fonte di verità | DB SQLite — CSV è export derivato |

## Analytics / Tag Manager

| Elemento | Valore |
| --- | --- |
| Account Analytics | `Roberto Picchioni architetto` |
| Account ID | `252970033` |
| Property | `bakabo-9a8c5` — ID `483501489` |
| GTM Container | `GTM-PF5Z85KS` — `www.bakabo.club` |

## Google Merchant Center

| Elemento | Valore |
| --- | --- |
| Account | `bakabo.club` |
| Merchant Center ID | `5295165689` |

Stato: feed e sitemap da riverificare dopo i deploy di giugno. Richiedere nuovo controllo sito da Merchant Center. Vedi task pendenti in `project_bks_pending.md`.

## 8 Collezioni permanenti (stato 20/06)

| Collezione | Handle | Colore | Stato |
| --- | --- | --- | --- |
| BKS Hours | `bks-hours` | `#c8c4be` | Live |
| BKS Glyph | `bks-glyph` | `#d4a030` | Live |
| BKS Marker | `bks-marker` | `#c04418` | Live |
| BKS Riviera | `bks-riviera` | `#0ca898` | Live |
| BKS Pulse | `bks-pulse` | `#8888cc` | Live |
| BKS Token | `bks-token` | `#9828d8` | Live |
| BKS Flag | `bks-flag` | `#c82020` | Live |
| BKS Origin | `bks-origin` | `#489808` | Live (ex Folklore, rinominato 16/06) |

## Member Area — Metal Tier System

| Tier | Simbolo | Acquisti | Accesso chiave |
| --- | --- | --- | --- |
| Lead | ◎ | 0 | Wishlist, newsletter |
| Iron | ⬡ | 1–2 | Size history, raccomandazioni base |
| Brass | ◈ | 3–5 | AI Personal Shopper, Try-On Camerino |
| Silver | ◇ | 6–10 | Drop anticipati +24h, Archive completo |
| Gold | ✦ | 11+ | VIP private drops, white-glove curation |

Tier rilevato automaticamente da `customer.orders_count` — nessun tag manuale.
Skill: `BKS_SKILL/members/bks-member-marketing.json`

## Pagine live custom

| Pagina | Handle | Template |
| --- | --- | --- |
| Member Area | `bks-members` | `page.bks-members` |
| AI Assistant | `bks-ai-assistant` | `page.bks-ai-assistant` |
| Shopping Guide | `bks-shopping-guide` | `page.bks-shopping-guide` |
| Help FAQ | `help-faq` | `page.help-faq` |
| Custom Request | `bks-custom` | `page.bks-custom` |
| Wishlist | `bks-wishlist` | `page.bks-wishlist` |
| Members Login | `bks-members-login` | `page.bks-members-login` |

## OpenAI Immagini

```bat
python tools\generate_openai_image.py --prompt-file output\openai_image_prompts\bks-hours.txt --name bks-hours-hero --size 1024x1536 --quality medium
```

Output: `output/openai_images/`
Prompt salvati: `output/openai_image_prompts/`

## Skill AI attive

```text
BKS_SKILL/skills/          15 skill di dominio
BKS_SKILL/members/         bks-member-marketing.json (metal tier, personal shopper)
BKS_SKILL/business/        bakabo-business.json
BKS_SKILL/size_guides/     man.json, woman.json
BKS_SKILL/theme/           bks-tm04-theme-skill.md
docs/                      skill referenziate dall'agente Python
ecommerce_automation/      theme_ai_assistant.py (system prompt AI)
```
