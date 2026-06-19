# BKS Studio — Price Audit Tool
## Guida rapida · 16 Giugno 2026

---

## Installazione

```bash
pip install pandas requests python-dotenv openpyxl
```

---

## Uso base — solo audit (nessuna modifica)

```bash
python3 bks_price_audit.py --csv shopify_products_export.csv
```

**Output:**
- `bks_price_audit_[data].xlsx` — report con semaforo colorato
- `bks_price_corrections_[data].csv` — CSV pronto per import Shopify
- `bks_price_corrections_api_[data].json` — payload JSON per API

---

## Dove prendere il CSV Shopify

**Shopify Admin → Products → Export → All products → Export products**

Scarica il file `.csv` e salvalo nella stessa cartella dello script.

---

## Aggiungere i costi reali Printify

Copia `printify_costs_template.csv`, rinominalo `my_costs.csv`,
e compila `BaseCost` e `ShippingEU` per ogni prodotto:

```
Title,BaseCost,ShippingEU
BKS Hours Drift™ Cozy Slipper,13.50,5.50
BKS Token Block™ Cozy Slipper,14.20,5.50
...
```

Poi esegui:

```bash
python3 bks_price_audit.py --csv shopify_export.csv --costs my_costs.csv
```

Se non fornisci i costi reali, lo script usa i **valori medi per categoria**
dalla tabella della skill `bakabo-business`. Abbastanza precisi per un audit
rapido, ma i costi reali danno risultati esatti.

---

## Applicare le correzioni

### Metodo A — Import CSV (più semplice)

1. Apri `bks_price_corrections_[data].csv`
2. Shopify Admin → Products → Import → carica il file
3. Shopify aggiorna solo i campi presenti nel CSV

### Metodo B — API automatica (più veloce su molti prodotti)

Crea un file `.env` nella stessa cartella:

```
SHOPIFY_STORE=11628e-2
SHOPIFY_TOKEN=shpat_xxxxxxxxxxxxx
```

Esegui prima in dry-run per vedere cosa farebbe:

```bash
python3 bks_price_audit.py --csv shopify_export.csv --dry-run
```

Se tutto ok, esegui l'aggiornamento reale:

```bash
python3 bks_price_audit.py --csv shopify_export.csv --update
```

---

## Come leggere il report

| Semaforo | Significato | Azione |
|---|---|---|
| 🟢 OK | Prezzo e margine corretti | Nessuna |
| 🟡 ALERT | Prezzo fuori range o formato non BKS | Aggiornare |
| 🔴 STOP | Margine sotto 45% — vendere in perdita | Aggiornare subito |
| ⚪ SKIP | Categoria non riconosciuta | Verificare manualmente |

---

## Aggiornare i costi nella tabella

Se i costi Printify cambiano (aggiornamenti provider, nuovo piano Premium),
aggiorna la sezione `COST_TABLE` in `bks_price_audit.py` — ogni voce ha:

```python
"Categoria": {
    "base_avg": X,   # costo produzione medio
    "ship_avg": Y,   # spedizione EU media
    "margin_target": 0.60,  # target margine (60%)
    "price_min": Z,  # prezzo minimo BKS
    "price_target": W,  # prezzo ideale BKS
    "price_max": V,  # prezzo massimo BKS
}
```

---

## Shopify Token — come ottenerlo

**Shopify Admin → Settings → Apps and sales channels →
Develop apps → Create app → Admin API → Configure →
seleziona `write_products` e `read_products` → Install → Access Token**

Copia il token nel `.env` come `SHOPIFY_TOKEN=shpat_...`

---

*Script prodotto da Gaetano per BKS Studio · 16 Giugno 2026*
