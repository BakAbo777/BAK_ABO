# Pulizia Cartella

## Regola

La pulizia è conservativa: non si cancella materiale utile, si archivia in `99_ARCHIVIO/`.

## File attivi in root

- `01_START_CATALOG_ENGINE.bat`
- `02_START_COLLECTIONS_DASHBOARD.bat`
- `03_START_METAFIELDS_RUNNER.bat`
- `app.py`
- `streamlit_collections.py`
- `streamlit_metafields_runner.py`
- `bks_collection_specs.py`
- `BKS_COLLEZIONE_26_v6.csv`
- `requirements.txt`
- `.env`

## Cartelle attive da lasciare

- `tools/`
- `docs/`
- `input/`
- `output/`
- `static/`
- `templates/`
- `theme_work/`
- `.codex_work/`
  - tema operativo: `.codex_work/BKS_V20_collections_theme/BKS_V19_work/`

## Archivio

- CSV catalogo vecchi: `99_ARCHIVIO/csv_catalogo/`
- Audit tema storici: `99_ARCHIVIO/audit_tema_legacy/`
- Zip tema storici: `output/99_ARCHIVIO/theme_zip_legacy/`
- Export collection V19: `output/99_ARCHIVIO/collection_plan_v19/`
- Launcher legacy: `99_ARCHIVIO/launcher_legacy/`
- Vecchio `theme_work`: `99_ARCHIVIO/theme_work_legacy/`
- Vecchia `.venv` non usata: `99_ARCHIVIO/venv_legacy_partial/`

Manifest dettagliato:

```text
99_ARCHIVIO/MANIFEST_PULIZIA_2026-06-09.md
```
