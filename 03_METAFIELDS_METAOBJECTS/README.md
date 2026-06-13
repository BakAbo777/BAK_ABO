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
