# BKS Master Checklist — Sistema Completo
**Aggiornato:** 2026-06-21 (pipeline editorial cutout)  
**Store:** bakabo.club | Shopify `11628e-2.myshopify.com`  
**Tema live:** id `202392961362` — BKS TM04 20_06_2026

---

## LEGENDA
- ✅ Completato
- 🔄 In progress / parziale
- ❌ Pendente — azione richiesta
- 🔒 Bloccato (dipende da azione Roberto)
- 🤖 Automatico (script pronto, si esegue su trigger)

---

## 1. SHOPIFY STORE — PRODOTTI

| # | Item | Stato | Note / Risoluzione |
|---|---|---|---|
| 1.1 | 202 prodotti in catalogo | ✅ | DB + CSV sincronizzati |
| 1.2 | Schema naming V18 `BKS [Type] — [Collection]` | ✅ | 189/202 rinominati. Stamp Sneakerz = DRAFT (Roberto decide) |
| 1.3 | Tutti i prodotti con immagini | ✅ | 28 immagini uploadate, 0 prodotti senza foto |
| 1.4 | Prezzi corretti (price ladder BKS) | ✅ | 5 alert critici risolti. Puffer $129, Slipper $55, Flip Flop $49, One-Piece $55, Athletic $69 |
| 1.5 | Inventory policy = `continue` su tutti | ✅ | 0 varianti in `deny` con qty=0 |
| 1.6 | 13 prodotti senza tag → taggati | ✅ | Stamp Sneakerz rimane DRAFT |
| 1.7 | Traduzioni italiane prodotti (Printify) | ✅ | 131 title translations eliminate 20-06-2026 |
| 1.8 | Tag `collection:X` coerenti per 8 collezioni | ✅ | Tutti i 202 prodotti taggati |
| 1.9 | Prodotti non taggati (Stamp Sneakerz) | 🔒 | Roberto attiva manualmente da Shopify Admin → Products |
| 1.10 | `write_inventory` scope per sync qty | 🔒 | Aggiungere scope all'API token se necessario. Origin 03 = policy:continue OK |
| 1.11 | Editorial cutout pipeline — scontorno AI prodotti | 🤖 | `scripts/bg_remove_catalog.py` — rembg 2.0.76, onnxruntime. Output: `output/catalog_images/editorial/{handle}/_01_cutout.png` + `_01_white.jpg`. 5 test OK (1200×1200px). Full run in corso 21-06-2026. |

---

## 2. SHOPIFY STORE — COLLEZIONI

| # | Item | Stato | Note / Risoluzione |
|---|---|---|---|
| 2.1 | 8 collezioni BKS live (Hours/Origin/Glyph/Marker/Riviera/Pulse/Token/Flag) | ✅ | Tutte attive con prodotti |
| 2.2 | Collezioni product-type (Sneakers, Backpacks, ecc.) | ✅ | Smart collection per tag |
| 2.3 | Collection templates con hero accent-color | ✅ | 13 templates deployati V.8 |
| 2.4 | Collezioni "Excluded from 9 sales channels" | 🔄 | Product-type collections escluse correttamente. Review se intenzionale |
| 2.5 | `bks-shopping-guide` collection (0 prodotti) | ❌ | Creare/assegnare prodotti o eliminare |

---

## 3. SHOPIFY STORE — PAGINE

| # | Item | Stato | Note / Risoluzione |
|---|---|---|---|
| 3.1 | FAQ (`bks-faq`) | ✅ | Contenuto inglese popolato 20-06-2026 |
| 3.2 | About BakAbo (`about-bakabo-1`) | ✅ | "Two Worlds. One Brand." EN |
| 3.3 | About BKS Studio (`about-bks-studio`) | ✅ | Contenuto EN da `bks-about-bks` |
| 3.4 | Contact (`contact`) | ✅ | `crew@bakabo.club`, EU Rep info |
| 3.5 | Help & FAQ (`help-faq`, `faq-domande-frequenti`) | ✅ | Stesso contenuto EN |
| 3.6 | BKS Shopping Guide | ✅ | Quiz armocromia + Man/Woman guide |
| 3.7 | BKS Members (`bks-members`) | ✅ | Template members area |
| 3.8 | BKS AI Assistant (`bks-ai-assistant`) | ✅ | Template section-driven |
| 3.9 | BKS Collections (`bks-collections`) | ✅ | Template section-driven |
| 3.10 | BKS Custom (`bks-custom`) | ✅ | Template section-driven |
| 3.11 | BKS Wishlist (`bks-wishlist`) | ✅ | Template section-driven |
| 3.12 | BKS Google Shopping Feed | ✅ | XML feed live `/pages/google-shopping-feed` |
| 3.13 | Your Privacy Choices (`data-sharing-opt-out`) | ✅ | Shopify Cloud consent app |
| 3.14 | Pagine duplicate da eliminare | ✅ | Eliminate 20/06/2026 — verificate non referenziate nel menu |
| 3.15 | `BKA About Bak Abo` (bks-about-bakabo) | 🔒 | Titolo anomalo ("BKA"). Verifica se intenzionale o eliminare |

---

## 4. SHOPIFY STORE — NAVIGAZIONE

| # | Item | Stato | Note / Risoluzione |
|---|---|---|---|
| 4.1 | Main menu (6 items: Home/Collections/Product Types/BKS Members/About BakAbo/Contact) | ✅ | Labels inglese, URL `/pages/contact` |
| 4.2 | Footer menu (Shipping/Returns/Privacy/Terms/Contact/Track Order) | ✅ | Tutto inglese |
| 4.3 | Footer Support column — hardcoded EN links | ✅ | Non più da `linklists.support` — bypass translation layer |
| 4.4 | Menu `main-menu-copy`, `main-menu-1`, `bks-base-menu`, `bks-menu-base`, `bks-main-menu-base` | ✅ | Eliminati 20-06-2026 via `scripts/_delete_old_menus.py` (GraphQL menuDelete) |
| 4.5 | Redirect `/pages/contatti` → `/pages/contact` | ✅ | Redirect 301 creato 20-06-2026 via `scripts/_add_redirect_contatti.py` (id=1725845176658) |

---

## 5. TEMA TM04 — COMPONENTI

| # | Item | Stato | Note / Risoluzione |
|---|---|---|---|
| 5.1 | Tema live id `202392961362` | ✅ | V.18+ deployato |
| 5.2 | Hero video homepage (Spot 2025.mp4) | ✅ | Shopify CDN, `hero_video_url` setting |
| 5.2b | Piano Hero — 8 tasti × 8 collezioni con artwork CDN | ✅ | `bks_piano_hero` in index.json, URL CDN reali, pushato 20/06 |
| 5.3 | BKS Cart drawer — ink bg, gold CTA | ✅ | V.12 |
| 5.4 | Wishlist hearts sulle card (bug listener duplicati) | ✅ | V.13 fix |
| 5.5 | Wishlist toast + account badge | ✅ | V.14 |
| 5.6 | BKS Weekly Editorial section | ✅ | V.15 — aggiungere via theme editor |
| 5.7 | JSON-LD structured data | ✅ | Product/WebSite/ItemList/Organization |
| 5.8 | GDPR cookie banner | ✅ | Shopify CustomerPrivacy + GTM Consent Mode v2 |
| 5.9 | Gold ring animato su icona account | ✅ | Member Gold Ring — CSS var tier |
| 5.10 | `locales/it.json` sovrascritto con EN | ✅ | Nessun testo Shopify in italiano |
| 5.11 | Selettore lingua rimosso (MutationObserver) | ✅ | Header snippet + CSS aggressivo |
| 5.12 | `bakabo-policy-access.liquid` — inglese | ✅ | "BKS Policies & Support" |
| 5.13 | `bks-policy.liquid` — inglese | ✅ | "Updated: / Back to previous page" |
| 5.14 | `footer.liquid` — Support links hardcoded EN | ✅ | |
| 5.15 | `bks-responsive.css` — mobile variant picker | ✅ | Patch 20-06-2026 |
| 5.16 | BKS Weekly Editorial — configurazione homepage | ✅ | Vol.1 / Issue 6 — Summer 2026 aggiunto a index.json (20/06/2026). Product picker vuoti — Roberto aggiunge 3 prodotti via theme editor |
| 5.17 | Puffer jacket collection template hero | 🔄 | Immagine hero da caricare per collection bks-token |

---

## 6. MEMBERS AREA

| # | Item | Stato | Note / Risoluzione |
|---|---|---|---|
| 6.1 | Metal tier system (Lead/Iron/Brass/Silver/Gold) | ✅ | Via `customer.orders_count` |
| 6.2 | Member dashboard (dashboard/wishlist/try-on/orders) | ✅ | `bks-member-dashboard.liquid` |
| 6.3 | AI Personal Shopper (Brass+) | ✅ | Gate tier + Cloudflare Worker endpoint |
| 6.4 | Try-On Camerino desktop QR | ✅ | Liquid gate Brass+ |
| 6.5 | Wishlist standalone page | ✅ | `/pages/bks-wishlist` |
| 6.6 | Try-On engine locale (porta :8010) | 🔄 | `05_START_TRYON_ENGINE.bat` — verificare stato servizio |
| 6.7 | Shopify Markets IT/EN setup | ❌ | Admin → Settings → Markets → Aggiungi mercato IT e EN separati → attiva traduzione selettiva (solo UI, non prodotti) |
| 6.8 | Email trigger per ogni tier upgrade | ❌ | Template in `Members Skill` — non inviati automaticamente (richiede Shopify Flow o Klaviyo) |

---

## 7. AI INTERNA

| # | Item | Stato | Note / Risoluzione |
|---|---|---|---|
| 7.1 | Cloudflare Worker `bks-agent` live | ✅ | `bks-agent.bakabo.workers.dev` — `/chat` 200 OK |
| 7.2 | Worker `bks-ai` live | ✅ | Prompt con 8 collezioni, colori, prodotti |
| 7.3 | Worker `bks-tier-upgrade` live | ✅ | |
| 7.4 | Theme AI Assistant system prompt | ✅ | Aggiornato con catalogo reale 20-06-2026 |
| 7.5 | Cron refresh 12:00 CET | 🔒 | `bks-agent-refresh` Worker cron — verificare KV secrets in Cloudflare Dashboard |
| 7.6 | KV `BKS_AGENT_KV` + 4 secrets | ✅ | OpenAI/Shopify secrets impostati via CF API |
| 7.7 | Streamlit Master Agent (porta :8501) | ✅ | `streamlit_master.py` — 7 pagine |
| 7.8 | Ecommerce Automation Agent | ✅ | `ecommerce_automation/master_agent.py` |

---

## 8. GOOGLE / SEO / MARKETING

| # | Item | Stato | Note / Risoluzione |
|---|---|---|---|
| 8.1 | JSON-LD structured data su sito | ✅ | Product/WebSite/ItemList/Organization |
| 8.2 | Google Shopping feed XML live | ✅ | `/pages/google-shopping-feed` |
| 8.3 | Shopify App API GMC (2.370+ prodotti) | ✅ | Google & YouTube sales channel attivo |
| 8.4 | Google Search Console — verifica dominio | ✅ | DNS TXT già presente in Cloudflare. Entrambi gli account verificati come Proprietario (bakabofirm@gmail.com + crew@bakabo.club) |
| 8.5 | Google Merchant Center — stato feed | ✅ | Account ATTIVO (nessuna sospensione). Feed Wixpa Google Shopping re-submitted 20-06-2026. 35.1K prodotti "Numero limitato" → attesa re-index 24-48h |
| 8.6 | Pixel Facebook & Instagram | ✅ | Connected — Optimized data |
| 8.7 | Pixel Google & YouTube | ✅ | Connected — Optimized data |
| 8.8 | Pinterest — "Action needed" | 🔒 | Entrambi account sospesi (crew@bakabo.club + bakabofirm@gmail.com). Username: `bakabofirm`. Appeal inviato 20-06-2026. In attesa risposta Pinterest (24-48h) |
| 8.9 | TikTok — "Action needed" + Pixel disconnesso | 🔒 | Admin → TikTok → risolvere. Pixel TikTok: Disconnected |
| 8.10 | Meta descrizioni pagine prodotto | 🔄 | CSV ha SEO fields. Verificare tutte le 202 schede via Search Console |

---

## 9. TECHNICAL INFRASTRUCTURE

| # | Item | Stato | Note / Risoluzione |
|---|---|---|---|
| 9.1 | SQLite DB (`bks_catalog.db`) — 1471 righe | ✅ | Tabelle: catalog_meta, rows, assets, rejected_assets |
| 9.2 | CSV Shopify-ready (`collezione 12_06_2026...csv`) | ✅ | Export derivato dal DB — fonte di verità = DB |
| 9.3 | Cloudflare Worker deploy pipeline | ✅ | `cloudflare/wrangler.toml` + `DEPLOY_NOW.bat` |
| 9.4 | `00_START_BKS_MASTER.bat` — 3 servizi | ✅ | Streamlit :8501, Tryon :8010, Master :8600 |
| 9.5 | Image Factory (`BAKABO_IMAGE_FACTORY_v1.1/`) | 🔄 | Avviabile da Streamlit page 07. Pipeline Printify → upload Shopify completata per 13 prodotti |
| 9.9 | Editorial Cutout Pipeline | 🤖 | `scripts/bg_remove_catalog.py --collection bks-X` — rimuove sfondo mockup Printify per uso magazine. Full run 21-06-2026. Args: `--collection`, `--limit`, `--force`, `--dry-run` |
| 9.6 | Sync media library (`I:\BKS database`) | ✅ | 14.421 file indicizzati, script `sync_bks_database.py` |
| 9.7 | API scope `write_inventory` | 🔒 | Non aggiunto — serve per sync qty programmatico. Aggiungere se necessario |
| 9.8 | Printify → Shopify sync automatico qty | 🔄 | Printify app sincronizza — Origin 03 qty=0 ma policy=continue (no SOLD OUT) |

---

## 10. CONTENT — PAGINE DA COMPLETARE/PUBBLICARE

| # | Item | Stato | Note / Risoluzione |
|---|---|---|---|
| 10.1 | BKS Shopping Guide — contenuto live | ✅ | Quiz + guide già deployate |
| 10.2 | BKS Weekly Editorial — configurazione | ✅ | Vol.1/Issue 6 live — product picker vuoti (Roberto aggiunge via editor) |
| 10.3 | `bundles` page — "Hidden" | 🔄 | Bundle builder app (MW Bundle Builder) — attivare o eliminare |
| 10.4 | `mix-and-match` page — "Hidden" | 🔄 | Verificare se la funzionalità è attiva e decidere |
| 10.5 | `bks-google-feed` page — empty body | ✅ | Body vuoto è corretto — usa template Liquid che genera l'XML |
| 10.6 | About BakAbo — immagine hero (`bakabo-970...jpg`) | ✅ | Immagine già nel CDN Shopify |
| 10.7 | Help & FAQ — email aggiornata | ✅ | `crew@bakabo.club` in tutti i posti |

---

## 11. CLEANUP — ELEMENTI DA ELIMINARE

| # | Item | Stato | Risoluzione |
|---|---|---|---|
| 11.1 | Menu obsoleti (5 menu con dead links) | ✅ | Eliminati 20-06-2026 via GraphQL menuDelete — vedi 4.4 |
| 11.2 | Pagine duplicate About | ✅ | Eliminate 20/06/2026: `about-bakabo` (171938808146) e `bks-about-bks` (173590118738) — menu usa about-bakabo-1 e about-bks-studio |
| 11.3 | `FAQ — Domande Frequenti` handle `faq-domande-frequenti` | 🔄 | Ora ha contenuto EN. Valutare redirect → `help-faq` o mantenerla |
| 11.4 | Tema precedente id `202388308306` | ✅ | Non trovato — già eliminato in precedenza |
| 11.5 | Temi bozza non più usati | 🔄 | 14 temi unpublished rilevati. Attenzione: NON eliminare "AVADA Assets - DO NOT REMOVE". Roberto decide quali bozze rimuovere. |

---

## 12. PRIORITÀ ASSOLUTA — TODO IMMEDIATO

```
URGENTE — Blocca visibilità Google:
  [x] 8.4  DNS TXT Google Search Console — ✅ verificato
  [x] 8.5  GMC Wixpa feed re-submitted — ✅ 20-06-2026 (attesa re-index 24-48h)

ALTA — Esperienza utente:
  [x] 4.4  5 menu obsoleti eliminati — ✅ 20-06-2026
  [x] 4.5  Redirect /pages/contatti → /pages/contact — ✅ 20-06-2026
  [x] 5.16 BKS Weekly Editorial homepage — ✅ Vol.1/Issue 6 live 20/06/2026
  [x] 1.11 Editorial cutout pipeline — ✅ rembg 2.0.76, full run 21-06-2026

MEDIA — Completamento:
  [ ] 6.7  Shopify Markets IT/EN
  [ ] 8.8  Pinterest reconnect — 🔒 appeal inviato, in attesa
  [ ] 8.9  TikTok reconnect
  [x] 11.2 Cleanup pagine duplicate (about-bakabo, bks-about-bks) — ✅ 20/06/2026
  [ ] 10.3 Decidere su Bundles page (attivare o rimuovere)

BASSA — Fine tuning:
  [ ] 1.9  Pubblicare Stamp Sneakerz (Roberto decide)
  [ ] 6.8  Email trigger tier upgrade (Flow/Klaviyo)
  [ ] 7.5  Verificare cron Cloudflare 12:00 CET
```

---

## HOW TO USE THIS CHECKLIST

Questo file è la fonte di verità operativa del progetto BKS.  
**Aggiornare dopo ogni sessione di lavoro** — aggiungere ✅ e spostare item in COMPLETATI.

Per ogni ❌ o 🔒 il campo "Risoluzione" contiene i passi esatti da seguire.  
Riferimento skill correlate: `bakabo-commercial-strategy`, `bakabo-members`, `bakabo-photo-studio`, `bakabo-fashion-editorial`, `bakabo-collection-guide`.
