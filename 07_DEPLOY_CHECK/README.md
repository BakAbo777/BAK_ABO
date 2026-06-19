# Fase 07 — Deploy Check

Aggiornato 17 Giugno 2026.

Obiettivo: checklist pre e post deploy per aggiornamenti al tema live.

## Tema attivo

```text
ID: 202392961362
Nome: BKS TM04 MEMBER TIER + SHOPPER 17JUN2026
Sorgente: 04_TEMA_SHOPIFY/_merged_tm04/
```

## Deploy sezioni (uso standard)

```bat
python scripts\deploy_theme_section.py
```

## Deploy tema completo (nuovo draft)

```bat
python scripts\push_draft_theme.py
python scripts\retry_draft_theme.py
```

Poi pubblicare manualmente dal Theme Editor Shopify.

## Checklist pre-deploy

- [ ] File modificati in `_merged_tm04/` testati localmente
- [ ] Schema Liquid valido (no `default: ""`, no `name` > 25 char)
- [ ] Nessun riferimento a sezioni inesistenti nei template `.json`
- [ ] `bks_active_assets.json` aggiornato

## Checklist post-deploy

- [ ] Tema pubblicato visibile su `bakabo.club`
- [ ] Header, footer, collection grid caricano correttamente
- [ ] Member area accessibile da `/pages/bks-members`
- [ ] Shopping Guide accessibile da `/pages/bks-shopping-guide`
- [ ] AI Assistant visibile top-right
- [ ] GTM `GTM-PF5Z85KS` presente nel `<head>` live
- [ ] Nessun `404` su collection e product principali
- [ ] `python tools\audit_live_site.py` — nessun errore critico
- [ ] Merchant Center: richiedere ricontrollo se aggiornato feed/sitemap
- [ ] Fare un ordine test end-to-end

## Assegnazione template pagine

Verificare da Shopify Admin → Pages che ogni pagina custom usi il template corretto:

| Pagina | Template suffix |
| --- | --- |
| BKS Members | `bks-members` |
| BKS AI Assistant | `bks-ai-assistant` |
| BKS Shopping Guide | `bks-shopping-guide` |
| Help FAQ | `help-faq` |
| BKS Custom Request | `bks-custom` |
