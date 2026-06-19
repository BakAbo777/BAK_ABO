# BKS SKILL

Skill e strumenti del sistema BKS Catalog Engine.
Fonte di verità per business rules, prezzi, spedizioni e guide operative.

## Struttura

```text
BKS_SKILL/
├── business/
│   └── bakabo-business.json   — regole business, price ladder, margin rules, alert critici
├── tools/
│   └── shipping_sync.py       — sync Printify → analisi spedizioni → report JSON
├── size_guides/
│   ├── man.json               — guide taglie uomo XS-3XL
│   └── woman.json             — guide taglie donna XS-2XL
└── README.md
```

## API Endpoints

| Endpoint | Metodo | Descrizione |
| --- | --- | --- |
| `/api/skill/business` | GET | Regole business, price ladder, alert |
| `/api/skill/margin_check` | GET | Calcola margine: `?retail=&base_cost=&shipping=` |
| `/api/skill/size_guide` | GET | Guide taglie man + woman |
| `/api/skill/list` | GET | Lista tutti i file JSON nelle skill |
| `/api/shipping/report` | GET | Report spedizioni Printify (cache) |
| `/api/shipping/refresh` | POST | Ri-scarica dati spedizioni da Printify |
| `/api/shipping/progress` | GET | Avanzamento sync spedizioni |

## Business Rules (sintesi)

### Margini target

| Tier | % Margine | Azione |
| --- | --- | --- |
| DRAFT | < 40% | Non pubblicare mai |
| Minimo | 40–45% | Pubblicabile solo con motivazione |
| Standard | 55–65% | Obiettivo normale |
| Premium | 65–75% | Goal per hero e limited |

### Formula margine

```text
net_revenue = retail_usd × 0.971 − 0.30   (Shopify Basic)
total_cost  = base_cost_printify + shipping
margin_pct  = (net_revenue − total_cost) / net_revenue × 100
```

### Alert critici attivi

- 🔴 **Cozy Slipper** ($32.20) — SOTTO COSTO. DRAFT immediato → riprezzare min $75
- 🔴 **Athletic Shorts** — shipping $17–32 USD su retail $53 medio. Riprezzare min $70
- 🔴 **Flip Flop EU** — shipping €14.99 su retail €19. Margine EU negativo
- 🟡 **Woven Blanket** ($47.10) — shipping EU $19.99. Riprezzare min $90
- 🟡 **AOP Puffer** — verificare base cost in Printify dashboard

## Come aggiornare

1. Aprire Printify dashboard → ogni blueprint → annotare il **base cost reale**
2. Aggiornare `business/bakabo-business.json` → campo `base_cost_usd` per ogni categoria
3. `POST /api/shipping/refresh` per ricalcolare l'analisi
4. Verificare alert in tab **Spedizioni** del Catalog Engine
5. Portare in DRAFT i prodotti sotto soglia su Shopify

## Auto-aggiornamento

Il Catalog Engine (`catalog_engine.py`) esegue un refresh automatico delle spedizioni
ogni **24 ore** in background. Il report è in `output/bks_shipping_sync.json`.
