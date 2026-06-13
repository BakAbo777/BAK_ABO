# Fase 03 — Metafields e Metaobjects

Obiettivo: creare/verificare definizioni BKS, metaobject e popolamento prodotti.

Launcher:

```bat
03_START_METAFIELDS_RUNNER.bat
```

Ordine script:

```bat
python tools\create_metafields.py
python tools\create_metaobjects.py
python tools\populate_metafields.py --resume
```

Nota: le definizioni Shopify native in namespace `shopify.*` possono restituire `access_denied`; non blocca i metafield BKS già creati.

## Metaobject `bks_collection`

Campi minimi per la collection hero e la griglia editoriale:

| Campo | Tipo Shopify | Uso nel tema |
|---|---|---|
| `name` | Single line text | Titolo editoriale della collezione |
| `tagline` | Single line text | Descrizione breve nella hero |
| `description` | Multi-line text | Descrizione editoriale principale |
| `series` | Single line text | Registro/serie BKS |
| `color_hex` | Color | Accento cromatico della collection signal |
| `shopify_handle` | Single line text | Collegamento alla collezione Shopify |
| `hero_image` | File reference | Immagine preview sopra il titolo |
| `hero_video` | URL | Video preview/spot sopra il titolo |

Il tema mantiene fallback compatibili ai campi legacy `editorial_description`, `image` e `video`, ma i campi ufficiali BKS sono `hero_image` e `hero_video`.
