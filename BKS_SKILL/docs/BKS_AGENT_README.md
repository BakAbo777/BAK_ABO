# BKS Studio — AI Pricing Agent
## Sistema completo: Shopify + Google Merchant API + Streamlit
### Guida installazione e configurazione · 16 Giugno 2026

---

## Architettura

```
┌─────────────────────────────────────────────────────────┐
│              STREAMLIT DASHBOARD (browser)               │
│    Audit · Correzioni · Google Merchant · Analytics      │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│                 AI PRICING AGENT                         │
│  Tabella costi Printify → Calcolo margini BKS →          │
│  Prezzi ottimali → Aggiornamento simultaneo              │
└──────┬──────────────────────────────┬───────────────────┘
       │                              │
┌──────▼──────┐                ┌──────▼──────────────────┐
│   SHOPIFY   │                │  GOOGLE MERCHANT API v1  │
│  Admin API  │                │  (nuova API — non Content │
│  prezzi     │                │   API che scade 18/08/26) │
└─────────────┘                └─────────────────────────┘
```

---

## Installazione locale

### 1. Requisiti
```bash
pip install -r requirements.txt
```

### 2. Configurazione
```bash
cp .env.template .env
# Compila .env con i tuoi valori (vedi sezioni sotto)
```

### 3. Avvio
```bash
streamlit run bks_agent_dashboard.py
```

Apri il browser su http://localhost:8501

---

## Configurazione Shopify

### Token API
1. **Shopify Admin → Settings → Apps and sales channels**
2. **Develop apps** → Create an app → nome: "BKS Pricing Agent"
3. **Configuration → Admin API access scopes:**
   - `read_products` ✅
   - `write_products` ✅
4. **Install app** → copia l'**Admin API access token** (`shpat_...`)
5. Incolla in `.env` come `SHOPIFY_TOKEN`

### Bloccare Printify dal sovrascrivere i prezzi
**CRITICO** — prima di usare l'agent:
1. Printify → ogni prodotto → **Pricing**
2. Imposta il campo "Retail price" su **vuoto** o **0**
3. Oppure: Printify Settings → **Disable automatic pricing**
4. In questo modo solo l'agent controlla i prezzi su Shopify

---

## Configurazione Google Merchant Center

### Step 1 — Google Cloud Console

1. Vai su **console.cloud.google.com**
2. Crea progetto: "BKS Studio Merchant"
3. **APIs & Services → Enable APIs:**
   - Cerca **"Merchant API"** → Abilita
   - ⚠️ NON abilitare "Content API for Shopping" — viene spenta il 18/08/2026
4. **IAM & Admin → Service Accounts:**
   - Create Service Account → nome: "bks-merchant-agent"
   - Role: **Editor**
   - Crea e scarica la chiave JSON → salva in `I:\BAK ABO\google_service_account.json`

### Step 2 — Google Merchant Center

1. Vai su **merchants.google.com**
2. Crea account business → nome: **BKS Studio**
3. **Verifica il sito bakabo.club:**
   - Settings → Business info → Website
   - Metodo consigliato: tag HTML in theme.liquid
4. **Aggiungi Service Account come utente:**
   - Settings → Account access → Add user
   - Inserisci l'email del Service Account (tipo: `bks-merchant-agent@project.iam.gserviceaccount.com`)
   - Ruolo: **Admin**
5. Copia il **Merchant ID** (numero in alto a destra nel dashboard)
6. Incolla in `.env` come `GOOGLE_MERCHANT_ID`

### Step 3 — Feed prodotti da Shopify

**Metodo A — App nativa Shopify (consigliato per il feed base):**
1. Shopify Admin → Apps → Cerca "Google & YouTube"
2. Installa l'app gratuita → collega il tuo account Google Merchant
3. Il feed si sincronizza automaticamente ogni 24h
4. L'agent aggiorna i prezzi in real-time via API senza aspettare il ciclo feed

**Metodo B — Feed XML manuale:**
- Non necessario se usi l'app Shopify + questo agent

### Step 4 — Free Listings (traffico gratuito)
1. Google Merchant Center → **Growth → Manage programs**
2. **Free listings** → Attiva
3. I tuoi 189 prodotti appaiono gratuitamente su Google Shopping

### Step 5 — Performance Max (campagne a pagamento — opzionale)
Quando hai budget pubblicitario:
1. Google Ads → Nuova campagna → **Performance Max**
2. Collega l'account Merchant Center
3. Carica: logo BKS, 3-5 immagini prodotto editoriali, titoli e descrizioni
4. Google gestisce automaticamente Search + Shopping + YouTube + Display
5. Budget minimo suggerito: €10/gg per i primi 30 giorni (fase apprendimento)

---

## Deploy online su Streamlit Cloud

### Opzione A — Streamlit Community Cloud (gratuito)

1. Carica il progetto su **GitHub** (repository privato):
   ```
   bks_agent_dashboard.py
   requirements.txt
   ```
   ⚠️ NON caricare il file `.env` su GitHub — usa i Secrets di Streamlit

2. Vai su **share.streamlit.io** → Sign in with GitHub

3. **New app** → seleziona il repository → file: `bks_agent_dashboard.py`

4. **Advanced settings → Secrets:**
   ```toml
   SHOPIFY_STORE = "11628e-2"
   SHOPIFY_TOKEN = "shpat_xxx"
   GOOGLE_MERCHANT_ID = "1234567890"
   ANTHROPIC_API_KEY = "sk-ant-xxx"
   ```
   Per il Service Account JSON, incolla il contenuto del file JSON come secret:
   ```toml
   GOOGLE_SERVICE_ACCOUNT_JSON = '''
   {
     "type": "service_account",
     "project_id": "...",
     ...
   }
   '''
   ```

5. **Deploy** → la dashboard è online in 2-3 minuti su un URL tipo:
   `https://bks-pricing-agent.streamlit.app`

### Opzione B — Server VPS (per uso intensivo)

```bash
# Su VPS Ubuntu/Debian
pip install -r requirements.txt
screen -S bks-agent
streamlit run bks_agent_dashboard.py --server.port 8501 --server.address 0.0.0.0
# Ctrl+A D per detach
```

Aggiungi nginx come reverse proxy per HTTPS.

---

## Opportunità che non stavi sfruttando

### 1. Free Listings Google Shopping
Zero costo — i tuoi 189 prodotti appaiono nei risultati Google Shopping.
Con metafield GPC già compilati sei avvantaggiato rispetto al 90% dei POD.

### 2. Google Merchant Promotions
Puoi caricare promozioni (es. "Drop launch -15% per 48h") direttamente
nel feed — appaiono come badge "In promozione" nei risultati Shopping.

### 3. Dynamic Remarketing
Google può mostrare i tuoi prodotti esatti agli utenti che hanno già
visitato bakabo.club — non altri prodotti simili, i tuoi.
Richiede: pixel Google Ads sul sito + feed connesso.

### 4. Google Merchant Reviews
Se raccogli recensioni via Judge.me puoi abilitare il programma
Google Customer Reviews — le stelle appaiono negli annunci.

### 5. Merchant API — Product Enrichment automatico
La nuova Merchant API v1 permette di aggiornare non solo i prezzi
ma anche titoli, descrizioni, immagini in bulk via script Python.
Utile quando vuoi ottimizzare i titoli per SEO su Google Shopping
senza modificare le schede Shopify.

### 6. Price Competitiveness Report
Google Merchant Center mostra quanto i tuoi prezzi sono competitivi
rispetto ad altri merchant che vendono prodotti simili.
Dati disponibili in Merchant Center → Growth → Price competitiveness.

---

## Flusso operativo consigliato

```
Settimana 1:
  [x] Revoca vecchia API key OpenAI
  [x] Genera nuova API key OpenAI
  [x] Configura Shopify Token
  [x] Blocca Printify dal sovrascrivere i prezzi
  [x] Esegui primo audit prezzi → correggi 🔴 STOP

Settimana 2:
  [ ] Crea account Google Cloud + Service Account
  [ ] Crea account Google Merchant Center
  [ ] Verifica bakabo.club
  [ ] Installa app Google & YouTube su Shopify
  [ ] Attiva Free Listings

Settimana 3:
  [ ] Deploy dashboard su Streamlit Cloud
  [ ] Primo audit integrato Shopify + Google
  [ ] Correggi eventuali disapprovazioni Google

Mensile:
  [ ] Audit prezzi automatico via dashboard
  [ ] Review Price Competitiveness Report Google
  [ ] Aggiorna costi Printify se cambiati
```

---

*Prodotto da Gaetano per BKS Studio · 16 Giugno 2026*
