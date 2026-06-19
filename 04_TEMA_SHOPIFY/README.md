# Fase 04 — Tema Shopify TM04

Obiettivo: mantenere il tema allineato a BakAbo come contenitore e BKS Studio come gruppo creativo.

## Tema live

| Campo | Valore |
| --- | --- |
| Nome | BKS TM04 18_06_2026 V.0 |
| ID | `202392961362` |
| Store | `bakabo.club` |
| Ultimo deploy | 18_06_2026 — 31 file OK |
| Deploy script | `scripts/deploy_theme_section.py` |

## Directory locale

```text
04_TEMA_SHOPIFY/
├── assets/          bks-member.css/js, bks-tryon.css/js, bks-piano-hero.css/js,
│                    bks-commerce-light.css, bks-dynamic-theme.css, bks-dynamic-ux.js
├── sections/        15 sezioni BKS (vedi lista sezioni)
├── snippets/        bakabo-header, bks-ai-assistant-embed, bks-member-tier, orbit-card …
├── templates/       collection.bks-origin, page.bks-members, page.bks-ai-assistant,
│                    page.bks-custom, page.bks-planet-collections-orbit, page.bks-archive
├── layout/          theme.liquid
└── _merged_tm04/    working copy pre-deploy
```

Zip disponibili:

- `BKS_TM04_FULL_LINKS_PAGES_UPDATE_16JUN2026.zip`
- `BKS_TM04_members_tryon_mobile_ux_16JUN2026.zip`

Selezione asset attivi: `output/bks_active_assets.json`

## Sezioni BKS

| Sezione | Scopo |
| --- | --- |
| `bks-piano-hero` | Hero homepage — tasto piano animato, left 40% libero per signal |
| `bks-impact-home` | Blocco impatto brand sulla homepage |
| `bks-trust-strip` | Strip di trust (policy, certificazioni, garanzie) |
| `bks-store-reviews` | Recensioni — sistema reale, niente testimonial finti |
| `bks-collection-signal` | Segnale visivo per identità collezione |
| `bks-planet-collections-orbit` | Griglia orbit tutte e 8 le collezioni |
| `bks-timed-offer` | Offerta a tempo — solo con scadenza reale e codice Shopify configurato |
| `bks-ai-assistant` | Assistente AI nel tema — dichiara AI, rimanda a policy |
| `bks-member-dashboard` | Area member con tier Metal, avatar, try-on gate |
| `bks-member-archive-page` | Archivio ordini/acquisti member |
| `bks-members-login` | Login/registrazione area member |
| `bks-product-editorial-care` | Cura editoriale nella PDP |
| `bks-accessories-panel` | Pannello accessori correlati |
| `bks-custom-request` | Richiesta personalizzazione — contatto via <crew@bakabo.club> |
| `main-collection-product-grid-bks` | Grid collezione — mobile-first, card a colonna singola <749px |

## Collezioni e accent color

| Collezione | Accent |
| --- | --- |
| Hours | `#1a1a2e` |
| Glyph | `#2e1a1a` |
| Marker | `#1a2e1a` |
| Riviera | `#1a2a3e` |
| Pulse | `#2e1a2e` |
| Token | `#2e2a1a` |
| Flag | `#1a1e2e` |
| Origin | `#489808` |

Non esiste la collezione "Folklore" — la collezione è Origin.

## Metal Tier (member area)

| Tier | Ordini | Colore |
| --- | --- | --- |
| Lead | 0 | `#7a7a7a` |
| Iron | 1–2 | `#8a8a8a` |
| Brass | 3–5 | `#c8a96e` |
| Silver | 6–10 | `#b0b0c8` |
| Gold | 11+ | `#d4a030` |

CSS vars in `bks-member.css`: `--tier-lead`, `--tier-iron`, `--tier-brass`, `--tier-silver`, `--tier-gold`.

## Regole editoriali TM04

- Hero banner: **left 40% libero** — spazio segnale editoriale TM04.
- Font: BKS Display per titoli, BKS Text per descrizioni/pannelli, BKS Mono per log/dati.
- Mobile descrizioni: min 14–15px, line-height ariosa, bottoni min 44px, lettera-spacing 0.
- Accent color: uno per asset, mai mescolare accents di collezioni diverse.
- Timer offerta: solo scadenza reale; nessun codice sconto finto; compliance bks-timed-offer.
- AI assistant: dichiara identità AI nel primo messaggio, offre handoff umano, non raccoglie pagamenti.

## Controlli obbligatori pre-deploy

- GTM unico `GTM-PF5Z85KS` presente nel `layout/theme.liquid`.
- `bks.series` non visibile al cliente.
- EU Representative visibile nel footer.
- Policy, FAQ, About e Contact accessibili da ogni pagina.
- Recensioni trattate come sistema reale — niente testimonial finti.
- Contrasto testi sempre leggibile (AA minimo).
- Mobile collection cards: immagini non oscurate, testi proporzionati, card a una colonna sotto 749px.
- Checkout rimane su Shopify nativo — non bypassare per pagamenti o dati personali.
- Theme publish richiede conferma di Roberto.

## Deploy

```bash
python scripts/deploy_theme_section.py
```

Il script carica tutti i file della lista `FILES` sul tema `202392961362` via Shopify Admin API.
Per rinominare il tema usare PUT `/admin/api/{VERSION}/themes/202392961362.json`.
