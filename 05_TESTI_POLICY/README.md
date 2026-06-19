# Fase 05 — Testi e Policy

Aggiornato 17 Giugno 2026.

Obiettivo: testi legali e pagine istituzionali pubblicati e aggiornati su bakabo.club.

## Script

```bat
python scripts\publish_policies.py
python tools\export_site_texts.py
```

File referenziato da `ecommerce_automation/legal_guardrails.py`:

```text
05_TESTI_POLICY/BKS_LEGAL_GUARDRAILS.md  (via docs/ symlink)
```

## Priorità policy

1. Shipping policy
2. Returns / Refund policy
3. Privacy policy
4. Terms of service
5. About
6. FAQ → live su `bakabo.club/pages/help-faq` (template `page.help-faq`, in inglese)
7. Contact → `crew@bakabo.club`

## Stato 17/06/2026

- Help FAQ: live in inglese, 16 domande in 8 categorie (Orders, Sizing, Care, Returns, BKS Membership, Try-On Camerino, Collections, Shipping)
- Lingua sito: inglese unico — tutti i testi nuovi in inglese

## Output testi

```text
output/site_texts_v1/
```

Usare i file `_reviewed.html` come versione approvata.
