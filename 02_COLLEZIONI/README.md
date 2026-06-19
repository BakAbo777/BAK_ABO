# Fase 02 — Collezioni

Aggiornato 17 Giugno 2026.

Obiettivo: mantenere le 26 collection BKS (8 editorial + 18 product type) allineate a template, SEO e prompt immagini.

## Stato attuale

Tutte le collection sono live e raggiungibili (`200`). Nessuna collection da creare ex novo.

## Script diretti (launcher rimosso)

```bat
python tools\create_collections.py --dry-run
python tools\create_collections.py --upsert
python tools\export_collection_plan.py
```

## Template assignment

Template già assegnati e verificati su tutti i 29 template `collection.*.json`.
Script deploy: `scripts/push_collection_templates.py`

## Output

```text
output/bks_collection_payloads_v20.json
output/bks_collection_plan_v20.csv
```

## 8 Collezioni editorial

| Handle | Nome | Accento |
| --- | --- | --- |
| `bks-hours` | BKS Hours | `#c8c4be` |
| `bks-glyph` | BKS Glyph | `#d4a030` |
| `bks-marker` | BKS Marker | `#c04418` |
| `bks-riviera` | BKS Riviera | `#0ca898` |
| `bks-pulse` | BKS Pulse | `#8888cc` |
| `bks-token` | BKS Token | `#9828d8` |
| `bks-flag` | BKS Flag | `#c82020` |
| `bks-origin` | BKS Origin | `#489808` |

Nota: `bks-origin` è il rename di `bks-folklore` (completato 16/06/2026).

## Prompt immagini collection

```bat
python tools\generate_openai_image.py --prompt-file output\openai_image_prompts\bks-hours.txt --name bks-hours-hero --size 1024x1536 --quality medium
```
