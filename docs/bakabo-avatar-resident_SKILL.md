# BakAbo — Avatar Resident

`bakabo-avatar-resident` — Skill residente per la produzione avatar BKS via Claude Code, senza Streamlit. Gestisce scripts 15s, workspace HeyGen, QC checklist, e registra i video completati in catalog_db (asset_type='avatar').

## Workspace

```
output/avatar_production/
├── scripts/    ← BKS_{Collection}_avatar_15s.md (8 file)
├── images/     ← BKS_{Collection}_hero_{DATE}.jpg (9:16)
├── exports/    ← MP4 finali da HeyGen
└── metadata/   ← delivery metadata
```

## Funzioni Python dirette

```python
from ecommerce_automation.avatar_production import ensure_workspace, summary, collection_rows
from ecommerce_automation.catalog_db import upsert_asset
```

## Regole script
- 35–50 parole per 15 secondi
- Voce calma, premium, zero punti esclamativi
- Prima riga: "BKS [Collezione]..."
- Chiusura: CTA (explore / save / follow / test the drop)

## Registrazione video in BKS database
Dopo export HeyGen: `upsert_asset(db, product_handle=..., asset_type='avatar', collection=..., ...)`

Related: `bakabo-master`, `bakabo-market-intelligence`
