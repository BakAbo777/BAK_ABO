# Fase 03 — Metafields e Metaobjects

Aggiornato 17 Giugno 2026.

Obiettivo: definizioni metafield BKS, metaobject `bks_collection`, popolamento prodotti.

## Script (launcher rimosso)

```bat
python tools\create_metafields.py
python tools\create_metaobjects.py
python tools\populate_metafields.py --resume
```

Nota: namespace `shopify.*` può restituire `access_denied` — non blocca i metafield BKS.

## Output

```text
output/metafield_definitions_log.csv
output/metaobjects_log.csv
output/populate_metafields_log.csv
```

## Metaobject `bks_collection`

| Campo | Tipo Shopify | Uso nel tema |
| --- | --- | --- |
| `name` | Single line text | Titolo editoriale collezione |
| `tagline` | Single line text | Descrizione breve nella hero |
| `description` | Multi-line text | Descrizione editoriale principale |
| `series` | Single line text | Registro interno BKS |
| `color_hex` | Color | Accento collection signal CSS |
| `shopify_handle` | Single line text | Collegamento alla collection Shopify |
| `hero_image` | File reference | Immagine hero sopra il titolo |
| `hero_video` | URL | Video preview (CDN Shopify URL) |

Campi ufficiali: `hero_image` e `hero_video`. Il tema mantiene fallback a `editorial_description`, `image`, `video` per compatibilità legacy.

## Metafield pagine custom

| Namespace | Key | Tipo | Pagine |
| --- | --- | --- | --- |
| `custom` | `special_abilities_text` | `list.single_line_text_field` | Tutte le pagine BKS |
| `custom` | `visual_strength` | `single_line_text_field` | — |
| `custom` | `hero_use` | `single_line_text_field` | — |
| `custom` | `design_code` | `single_line_text_field` | — |
| `custom` | `product_mood` | `single_line_text_field` | — |
| `global` | `title_tag` | `string` | SEO title |
| `global` | `description_tag` | `string` | SEO description |
