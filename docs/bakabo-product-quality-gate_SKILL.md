# BakAbo — Product Quality Gate

`bakabo-product-quality-gate` — Gate obbligatorio pre-pubblicazione. Score 0–25 su 5 dimensioni moda×arte. Minimo 20/25. Nessun prodotto BakAbo viene pubblicato senza superare questo gate.

## Le 5 dimensioni (0–5 ciascuna)

| Dim | Nome | Dominant |
| --- | --- | --- |
| D1 | Blank suitability | Moda |
| D2 | Print×garment dialogue | Moda+Arte |
| D3 | Visual concept strength | Arte |
| D4 | Chromatic integrity | Arte+Moda |
| D5 | Editorial credibility | Moda+Arte |

## Matrice decisionale

| Score | Decisione | Tag |
| --- | --- | --- |
| 22–25 | PUBBLICA — prodotto di riferimento | `bakabo-hero-product` |
| 20–21 | PUBBLICA — prodotto solido | `bakabo-enriched` |
| 17–19 | HOLD — revisione dimensioni specifiche | `bakabo-needs-review` |
| 14–16 | REDESIGN — non è un ritocco, è una ripartenza | `bakabo-needs-redesign` |
| < 14 | RIMUOVI da Printify | `bakabo-ai-failed` |

## Blockers automatici (score = 0 qualunque)
- Immagini stock senza trasformazione
- Print che replica brand esistente
- Blank con tasso resi > 10% nella categoria
- Combinazione cromatica che distrugge la leggibilità

## Posizione nel workflow catalogo
```
Printify sync → quality gate (questo skill) → printify-sync enrichment
→ product-copy → art-critic gallery text → business margin check → publish
```

Related: `bakabo-art-critic`, `bakabo-market-antagonist`, `bakabo-business`, `bakabo-printify-sync`
