# Stato Attuale

Aggiornato: 2026-06-09

## Domini Shopify

Da screenshot Shopify Admin:

| Dominio | Stato |
|---|---|
| `bakabo.club` | Primary, Connected |
| `11628e-2.myshopify.com` | Connected |
| `bakabo.myshopify.com` | Connected |
| `www.bakabo.club` | Connected |
| `account.bakabo.club` | Customer Account Primary, Connected |

## Analytics / Tag Manager

Da screenshot Google:

| Elemento | Valore |
|---|---|
| Account Analytics | `Roberto Picchioni architetto` |
| Account ID | `252970033` |
| Proprietà selezionata | `bakabo-9a8c5` |
| Property ID visibile | `483501489` |
| Container GTM | `www.bakabo.club` |
| Container ID | `GTM-PF5Z85KS` |
| Tipo container | Web |

Snapshot Analytics visibile:

| Metrica | Valore |
|---|---:|
| Utenti attivi ultimi 7 giorni | 89 |
| Sessioni ultimi 7 giorni | 97 |
| Visualizzazioni ultimi 7 giorni | 200 |
| Conteggio eventi ultimi 7 giorni | 453 |

## Google Merchant Center

Da screenshot Merchant Center Next:

| Elemento | Valore |
|---|---|
| Account | `bakabo.club` |
| Merchant Center ID | `5295165689` |
| Dati inventario locale mancanti | 68,3K prodotti, 95,1% |
| Pagina prodotto non disponibile | 8,39K prodotti, 11,7% |
| Esempio aggiuntivo | `Taglia mancante` su un prodotto campione |

Interpretazione: molte segnalazioni sono tracce di prodotti eliminati dalla collezione ma non ancora reindicizzati da Google. Dopo publish pulito, controllare feed/sitemap e richiedere nuovo controllo del sito da Merchant Center.

## Nota Live Sito

Il crawl pubblico del 2026-06-09 mostra che il live pubblicato non è ancora allineato al tema locale V20:

- Home e collection editoriali rispondono `200`.
- GTM live ancora `GTM-M4ND7QL`; il tema locale pronto usa `GTM-PF5Z85KS`.
- Le collection prodotto/navigazione nuove (`swimwear`, `outerwear`, `sneakers`, `puffer-jacket`, `windbreaker`, `backpack`) sono ancora `404` live.
- Alcune pagine/policy hanno restituito `429 Verifying your connection` durante il crawl automatico; verificare da browser dopo publish.

Il tema locale V20 è stato aggiornato, ma va caricato/pubblicato per sostituire il live.

## Tema Locale Corrente

```text
output/BKS_V20_TEXTS_COLOR_READY.zip
```

Contiene:

- `GTM-PF5Z85KS` come GTM unico nel tema.
- Google Fonts Bebas Neue, DM Sans, DM Mono.
- token CSS BKS estesi.
- EU Representative nel footer.
- rimozione `bks.series` dalla UI cliente.
- template pagina puliti per About, FAQ, policy.
- media wrappers transparent-friendly.

## OpenAI Immagini

Il cruscotto `02_START_COLLECTIONS_DASHBOARD.bat` include il tab `05 Immagini AI`:

- prompt base per ogni collection;
- prompt modificabile;
- salvataggio in `output/openai_image_prompts/`;
- generazione opzionale con `OPENAI_API_KEY`;
- output in `output/openai_images/`.

## Sorgenti Skill

- `docs/bakabo-web-experience_SKILL.md`
- `docs/bakabo-armocromia_SKILL.md`
- `docs/BKS_V20_AUDIT.md`
