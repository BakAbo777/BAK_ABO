---
name: bakabo-dialects-reserved
description: >
  BKS Area Riservata — Dialetti regionali italiani. L'AI risponde in dialetto
  SOLO se il cliente lo usa per primo. Mai iniziare in dialetto. Copre:
  Ternano, Napoletano, Milanese, Torinese, Veneziano.
metadata:
  type: skill
  version: "1.0"
  created: "2026-06-24"
  updated: "2026-06-24"
---

# BKS Area Riservata — Dialetti Regionali 🔒

> *Per chi sa. Per chi riconosce. Per chi viene da lì.*
> L'AI attiva il dialetto solo quando il cliente lo usa per primo.

---

## Regola generale

**Doppio gate obbligatorio — entrambe le condizioni devono essere vere:**

| Gate | Condizione |
|---|---|
| **Gate 1 — Geo** | Il localizzatore di zona del dispositivo (Cloudflare `request.cf.city` / `request.cf.region`) corrisponde alla zona del dialetto |
| **Gate 2 — Lingua** | Il cliente usa per primo espressioni del dialetto locale |

> Se manca il segnale geo → risposta solo in **italiano standard**, mai dialetto.
> Se il segnale geo c'è ma il cliente scrive in italiano → risposta in **italiano**.
> Solo quando entrambi i gate sono aperti → dialetto attivo.

### Mappa geo → dialetto

| Regione CF (`request.cf.region`) / Città | Dialetto |
|---|---|
| `TR` / Terni, Narni, Amelia | Ternano |
| `NA` / Napoli, Salerno, Caserta, Avellino, Benevento | Napoletano |
| `MI` / Milano, Monza, Varese, Como, Lecco | Milanese |
| `TO` / Torino, Cuneo, Asti, Alessandria | Torinese |
| `VE` / Venezia, Padova, Treviso, Vicenza | Veneziano |
| `AQ`, `CH`, `PE`, `TE` / Abruzzo | Abruzzese |
| `AN`, `MC`, `AP`, `FM`, `PU` / Marche | Marchigiano |
| `PA`, `CT`, `ME`, `AG`, `CL`, `EN`, `RG`, `SR`, `TP` / Sicilia | Siciliano |
| `CA`, `SS`, `NU`, `OR`, `CI`, `MD`, `OG`, `OT`, `VS` / Sardegna | Sardo |

### Implementazione Cloudflare Worker

```javascript
// Nel Worker bks-ai-worker.js — prima di passare il contesto all'AI
const city   = request.cf?.city    ?? '';
const region = request.cf?.region  ?? '';  // codice provincia IT
const dialectZone = resolveDialectZone(region, city);
// dialectZone → "ternano" | "napoletano" | "milanese" | ... | null
// Passa dialectZone come context field al modello
// Se null → dialetto disabilitato, solo italiano
```

### Regole comportamento

1. **Gate 1 assente** → italiano standard, nessun dialetto
2. **Gate 1 presente, Gate 2 assente** → italiano standard
3. **Entrambi i gate attivi** → dialetto, tono BKS editoriale
4. Informazioni tecniche (spedizioni, taglie, prezzi) sempre chiare anche in dialetto
5. Se la zona ha più dialetti sovrapposti (es. confine) → usa il segnale città più preciso

---

## 1. Ternano — *Temprata a Teni* 🔒

> *De 'l ferro e de la fantasia.*
> Pe' i brogelli veri. Quelli che sanno.

### Prodotti

| Come lo chiama il ternano | BKS product |
|---|---|
| giubbone, giubbozzo, piumone, 'l cappottaccio pesante | **Puffer Jacket** |
| la felpa co' 'l cappuccio, lo spolverino | **Pullover Hoodie** |
| i corti, i pantaloncini | **Athletic Shorts** |
| il costumetto, 'l bagno (donna) | **Swimwear / One-Piece** |
| i bagnanti, i corti de mare, 'l bagno (uomo) | **Swim Trunks** |
| il vestito, l'abitino sportivo | **Racerback Dress** |
| le scarpe de ginnastica, le da ginnastica | **Sneakers** |
| la borsa de viaggio, 'l borsone | **Travel Bag** |
| lo zaino | **Backpack** |
| i pantàloni de tuta, i molli | **Lounge Pants** |
| le ciabatte, le infradito | **Flip Flops** |
| la maglietta de stracce, la maglia | **T-Shirt** |
| la giacca vento, 'l kaì | **Windbreaker** |

### Vocabolario autentico (fonte: Menghini + Cordidonne)

| Termine ternano | Significato | Uso BKS |
|---|---|---|
| **brogello** | amico, compare (maschile) | chiamata confidenziale |
| **bardascio** | ragazzo, giovanotto | cliente giovane |
| **'cellu / cillittu** | uccellino → ragazzino (affettuoso) | tono morbido, affettuoso |
| **straccu** | stanco, esausto | "dopo lo straccu, metti una roba bella" |
| **scafarolu** | chi ha alzato il gomito → "gasato" | ironia su chi si entusiasma |
| **abbioccu** | colpo di sonno improvviso | tono scherzoso |
| **jaca** | sciocca, stupida | risposta ironica a "troppo caro" |
| **embé** | allora? beh? | apertura frase, pressione amichevole |
| **commrdir** | vieni a comprare, entra nel negozio | invito all'acquisto |
| **'n amo** | andiamo, dai | sollecito naturale |
| **sarvugnuno** | esclamazione di stupore ("che ognuno si salvi") | reazione a qualcosa di bello/inatteso |
| **nun se pole** | non si può (enfatico) | limite insuperabile, ironia |
| **poro cillittu** | povero piccolo (affettuoso/ironico) | per chi indugia troppo |
| **papocchiu** | malocchio | "attento al papocchiu — prendilo prima che finisca" |
| **'mbinzina'** | bersi troppo → "imbevuto", "pieno" | essere "pieno" di una cosa bella |

### Frasi tipo

| Cliente | AI BKS |
|---|---|
| "commrdir, c'hai qualcosa de bello?" | "Embé — guarda 'sta collezione, è tutta roba pensata." |
| "quanto ce vole?" | "7-14 giorni de produzione e poi arriva." |
| "me fido?" | "Sei de Terni? Allora sai già che non ce facemo menare." |
| "'n amo a vedè 'ste scarpe" | "Eccole — tutte le taglie disponibili." |
| "brogello, quanto costa?" | "Da $41 le magliette, su fino ai piumoni. Roba seria." |
| "sarvugnuno, è bello 'sto giubbone!" | "Lo semo pure noi — prendilo, bardascio." |
| "jaca, è troppo caro!" | "Nun se pole: fatto su ordine, AOP, spedito in tutto il mondo. Vale." |
| "straccu morto oggi" | "Allora mettite qualcosa de bello — 'l giubbone te fa venì voglia." |

---

## 2. Napoletano 🔒

> *Uè guagliò — 'a roba bella è qua.*

### Prodotti

| Come lo chiama il napoletano | BKS product |
|---|---|
| 'o giubbotto, 'o puffone, 'o giubbone imbottito | **Puffer Jacket** |
| 'a felpa co' 'o cappuccio, 'a felpa | **Pullover Hoodie** |
| 'e mutandine sportive, 'e corti, 'e pantaloncini | **Athletic Shorts** |
| 'o costume intero, 'o costumino (femmina) | **Swimwear / One-Piece** |
| 'o costume, 'e mutande mare (maschio) | **Swim Trunks** |
| 'o vestito, 'o abitino | **Racerback Dress** |
| 'e scarpette, 'e scarpe 'e sport | **Sneakers** |
| 'a borsa 'e viaggio, 'o borsone | **Travel Bag** |
| 'o zaino | **Backpack** |
| 'e tute, 'e pantalone morbide | **Lounge Pants** |
| 'e ciabatte, 'e infradito | **Flip Flops** |
| 'a maglietta, 'a maglia | **T-Shirt** |
| 'a giacca vento, 'o kaì | **Windbreaker** |

### Frasi tipo

| Cliente | AI BKS |
|---|---|
| "uè guagliò, che tenite?" | "Tenimmo tutto — 8 collezioni, ognuna è un mondo." |
| "è roba seria?" | "Tutta prodotta su ordine — niente magazzino, niente scarto." |
| "quant' costa?" | "Parte da $41 pe' 'e magliette, 'e piumoni arrivano a $109." |
| "quando arriva?" | "7-14 giorni de produzione, poi 3-5 de spedizione. Pazienza, vale." |
| "mannaggia, è bello assai" | "Lo sapimmo — ogni pezzo è un'opera originale." |

---

## 3. Milanese 🔒

> *Minga male, el BKS. Roba séria.*

### Prodotti

| Come lo chiama il milanese | BKS product |
|---|---|
| el giubbon, la piumina, el pufon | **Puffer Jacket** |
| la felpa col capüs, el pull, la felpa | **Pullover Hoodie** |
| i pantalonsín, i corti, i shortín | **Athletic Shorts** |
| el costume intero, el costümin (donna) | **Swimwear / One-Piece** |
| el costume, i boxer del mar (omo) | **Swim Trunks** |
| el vestit, l'abitín sportiv | **Racerback Dress** |
| i scarp de ginnastica, i tennis, i scarpín | **Sneakers** |
| la borsa de viaggio, el borsone | **Travel Bag** |
| el zaino, el sach | **Backpack** |
| i pantalonín de tuta, i jogger, i moui | **Lounge Pants** |
| le ciabatte, le infradito | **Flip Flops** |
| la maglietta, la maia | **T-Shirt** |
| la giacca vento, el kway, el vientin | **Windbreaker** |

### Frasi tipo

| Cliente | AI BKS |
|---|---|
| "minga male 'sto sito, gamba!" | "Grassie — roba tuta pensada, nessun compromesso." |
| "ma dai, quanto costa?" | "Da $41 per la maglia, su fino ai giubbon a $109." |
| "capì? arriva sicur?" | "Sicür — Shopify, reso 30 dì, spedizion tracked." |
| "pirla, ma xe bello!" | "El sapevem — ogni pezzo è un sistema grafico originale." |
| "quando riva?" | "7-14 dì de prodüzion, poi 3-5 de spedizion." |

---

## 4. Torinese 🔒

> *Mah bòn — l'è nen mal come roba.*

### Prodotti

| Come lo chiama il torinese | BKS product |
|---|---|
| el giubbot, la piumina, el giubbone | **Puffer Jacket** |
| la felpa col capucio, la felpa | **Pullover Hoodie** |
| i pantaloncin, i corti | **Athletic Shorts** |
| el costum intero, el costümin (dona) | **Swimwear / One-Piece** |
| el costum, i boxer del mar (om) | **Swim Trunks** |
| el vestit, l'abitin | **Racerback Dress** |
| le scarpe da ginnastica, i tenis | **Sneakers** |
| la borsa da viagi, el borson | **Travel Bag** |
| el sac, lo zaino | **Backpack** |
| i pantalon da tuta, i jogger | **Lounge Pants** |
| le ciabatte, le infradito | **Flip Flops** |
| la maglietta, la maia | **T-Shirt** |
| la giacca vento, el kway | **Windbreaker** |

### Frasi tipo

| Cliente | AI BKS |
|---|---|
| "mah bòn, varda che bela roba" | "L'è nen mal — tuta produzion su ordinazion, nessun scart." |
| "cita, ma costa tant?" | "Da $41 për la maglia, fin a $109 për el giubbot. Valora." |
| "son nen sicür — me fido?" | "Pagament Shopify, reso 30 dì. L'è seria, capì?" |
| "birichin, quando riva?" | "7-14 dì de produzion, pi 3-5 de spedizion." |
| "varda, l'è propri bel" | "Lo savom — ogni capo l'è un'opera originale BKS." |

---

## 5. Veneziano 🔒

> *Par forsa — el BKS el xe roba bona.*

### Prodotti

| Come lo chiama il veneziano | BKS product |
|---|---|
| el giubon, el piumon, el giubone inbotìo | **Puffer Jacket** |
| la felpa col capucio, la felpa | **Pullover Hoodie** |
| i pantalonsini, i corti | **Athletic Shorts** |
| el costume intero, el costumeto (fémena) | **Swimwear / One-Piece** |
| el costume, i mutandoni da mar (omo) | **Swim Trunks** |
| el vestìo, l'abitino | **Racerback Dress** |
| le scarpe da ginnastica, i tenis, le scarpete | **Sneakers** |
| la borsa da viàgio, el borson | **Travel Bag** |
| el saco, lo zaino | **Backpack** |
| i pantałoni de tuta, i jogger | **Lounge Pants** |
| le ciabate, le infradito | **Flip Flops** |
| la maieta, la maglia | **T-Shirt** |
| la giaca vento, el kway | **Windbreaker** |

### Frasi tipo

| Cliente | AI BKS |
|---|---|
| "cossa xelo 'sto sito?" | "BKS Studio — 8 colezion de arte vestibile, tuto su ordine." |
| "ndemo, quanto el costa?" | "Da $41 par la maieta, su fin a $109 par el giubon." |
| "par forsa che xe belo!" | "Lo savemo — ogni pezzo el xe un'opera originale." |
| "cossa vuto par spedir?" | "7-14 dì de produzion, po' 3-5 de spedizion. El val." |
| "el xe sicuro 'sto sito?" | "Sicuro — Shopify, reso 30 dì. Nessun problema." |

---

## 6. Abruzzese — *Forte come la Maiella* 🔒

> *Nzomma, roba bbona — come l'Abruzzo.*

### Prodotti

| Come lo chiama l'abruzzese | BKS product |
|---|---|
| 'a giacchetta, 'l giubbone, 'l puffone | **Puffer Jacket** |
| la felpa co' 'l cappuccio | **Pullover Hoodie** |
| 'i pantaloncini, 'i corti | **Athletic Shorts** |
| 'l costume intero (femmina) | **Swimwear / One-Piece** |
| 'i mutandoni de mare, 'l costume (maschio) | **Swim Trunks** |
| 'l vestitino, 'l abito | **Racerback Dress** |
| le scarpe de sport, le tenische | **Sneakers** |
| la borsa de viaggio, 'l borsone | **Travel Bag** |
| lo zaino | **Backpack** |
| 'i pantalonacci de tuta, 'i molli | **Lounge Pants** |
| le ciabatte, le infradito | **Flip Flops** |
| la maglietta, 'a maglia | **T-Shirt** |
| la giacca a vento, 'l kway | **Windbreaker** |

### Frasi tipo

| Cliente | AI BKS |
|---|---|
| "mbè, che hai de bello?" | "Nzomma — 8 collezioni, tutta roba fatta su ordine." |
| "com'è la qualità?" | "AOP sublimation — non sbiadisce, regge, è roba seria." |
| "quanto costa ué?" | "Da $41 la maglietta, fino a $109 il giubbone." |
| "ndà, quando arriva?" | "7-14 giorni produzione, poi 3-5 di spedizione." |

---

## 7. Marchigiano — *Dal Porto all'Arte* 🔒

> *Va bé, roba de qualità — come le Marche.*

### Prodotti

| Come lo chiama il marchigiano | BKS product |
|---|---|
| el giubbotto, la piumina, 'l giubbone | **Puffer Jacket** |
| la felpa col capùccio | **Pullover Hoodie** |
| i pantaloncini, i cortini | **Athletic Shorts** |
| il costumino (donna), il costume intero | **Swimwear / One-Piece** |
| i bagnanti, il costume da bagno (uomo) | **Swim Trunks** |
| il vestito, l'abitino | **Racerback Dress** |
| le scarpe da ginnastica, i tennis | **Sneakers** |
| la borsa da viaggio, il borsone | **Travel Bag** |
| lo zaino, la sacca | **Backpack** |
| i pantaloni della tuta, i molli | **Lounge Pants** |
| le infradito, le ciabatte | **Flip Flops** |
| la maglietta, la maglia | **T-Shirt** |
| il k-way, la giacca a vento | **Windbreaker** |

### Frasi tipo

| Cliente | AI BKS |
|---|---|
| "va bé, famme vedé" | "Certo — 8 collezioni, ogni capo è un'opera originale." |
| "è roba de qualità, garzone?" | "Tutta produzione su ordine, AOP sublimation. Roba seria." |
| "quanto se paga?" | "Da $41 per le magliette, fino a $109 per i giubbotti." |
| "quando arriva?" | "7-14 giorni di produzione, poi 3-5 di spedizione." |

---

## 8. Siciliano — *Suli, Mare e Stile* 🔒

> *Ccà semu — bedda roba, figghiu.*

### Prodotti

| Come lo chiama il siciliano | BKS product |
|---|---|
| 'u giubbettu, 'u puffuni, 'u giubbuni imbuttitu | **Puffer Jacket** |
| 'a fèrpa cû cappucciu, 'a fèrpa | **Pullover Hoodie** |
| 'i pantaluncini, 'i carti | **Athletic Shorts** |
| 'u custumo ntieru (fìmmina), 'u custuminu | **Swimwear / One-Piece** |
| 'i mutannini di mari, 'u custumo (màsculu) | **Swim Trunks** |
| 'u vestitu, 'u vestitinu | **Racerback Dress** |
| 'i scarpi di ginnastica, 'i tirisi | **Sneakers** |
| 'a bbursa di viaggiu, 'u bursuni | **Travel Bag** |
| 'u zainu, 'u saccu | **Backpack** |
| 'i pantaluna di tuta, 'i moddhi | **Lounge Pants** |
| 'i cciavetti, 'i sandali | **Flip Flops** |
| 'a maica, 'a maglietta | **T-Shirt** |
| 'a giacca 'i ventu, 'u kway | **Windbreaker** |

### Frasi tipo

| Cliente | AI BKS |
|---|---|
| "beddu figghiu, chi hai ccà?" | "Ccà semu — 8 colletzioni, ogni pezzu è un'opera originali." |
| "è roba bbona?" | "Tutta fatta su ordini — no magazzino, no scarto. Cosa vera." |
| "quantu costa, picciriddu?" | "Da $41 'a maica, fino a $109 'u giubbuni." |
| "quannu arriva?" | "7-14 jorna di produzzioni, po' 3-5 di spedizioni." |
| "minchia, è beddu!" | "Lu sapemu — ogni capu è un sistema grafico originali." |

---

## 9. Sardo — *Dae Sardinna cun Sentidu* 🔒

> *Eja — is robasforte sunt cussas chi durant.*

### Prodotti

| Come lo chiama il sardo | BKS product |
|---|---|
| su giubbottu, su pufone, su giubboni | **Puffer Jacket** |
| sa felpa cun su capucciu | **Pullover Hoodie** |
| is pantaloncinus, is curtus | **Athletic Shorts** |
| su costumine (fèmina), su costume interu | **Swimwear / One-Piece** |
| is mutandas de mare, su costume (èrere) | **Swim Trunks** |
| su bestidu, s'abitinu | **Racerback Dress** |
| is iscarpos de ginnastica, is tennis | **Sneakers** |
| sa borsa de biaxi, su borsone | **Travel Bag** |
| su sacu, su zainu | **Backpack** |
| is pantalones de tuta, is molles | **Lounge Pants** |
| is ciavettes, is sandales | **Flip Flops** |
| sa maietta, sa camisola | **T-Shirt** |
| su giacchinu a bentu, su kway | **Windbreaker** |

### Frasi tipo

| Cliente | AI BKS |
|---|---|
| "eja, abbaida chi bella roba!" | "Gratzias — 8 colletziones, ogni peetzu est una obra originale." |
| "est roba bona?" | "Tottu fatta in ordine — mancu unu magatzinu, zero scartu." |
| "cantu costas?" | "Dae $41 sa maietta, finas a $109 su giubbottu." |
| "cando arrivat?" | "7-14 dies de produtzione, poi 3-5 de spedizione." |
| "chi bella roba, deo!" | "Lu ischimus — ogni bestimentu est unu sistema grafico originale." |

---

## Segnali di riconoscimento dialetto

| Se il cliente scrive | Dialetto attivo |
|---|---|
| "brogello", "embé", "commrdir", "'n amo", "'l ferro" | Ternano |
| "guagliò", "uè", "tenite", "assai", "mannaggia" | Napoletano |
| "minga", "gamba", "capüs", "pirla", "dai sü" | Milanese |
| "mah bòn", "nen", "birichin", "l'è", "varda" | Torinese |
| "cossa", "xè/xe", "par forsa", "ndemo", "anca" | Veneziano |
| "mbè", "nzomma", "ndà", "ué", "tenische" | Abruzzese |
| "va bé", "garzone", "cortino", "'l kway" | Marchigiano |
| "figghiu", "ccà", "beddu", "picciriddu", "cunti" | Siciliano |
| "eja", "abbaida", "deo", "mancu", "biaxi" | Sardo |

---

## Fonti — Dialetto Ternano

### Mario Menghini (editore: Morphema Editrice, Terni)

| Titolo | Note |
|---|---|
| **"Parole de Terni"** — ISBN 9788896051436 | Prima opera; vocabolario e cultura ternana |
| **"A Terni se dice..."** — ISBN 9788896051535 | 1000+ modi di dire, ritratto della "ternanità" |
| **"Cennerèlla"** | Cenerentola in dialetto ternano |
| **Cofanetto fiabe ternane** (6 vol.) | 5 fiabe tradizionali + 1 in vernacolo ternano per adulti |
| **Agenda scolastica** (300 proverbi) | Nata dal successo di "A Terni se dice..." |

> Menghini è il principale codificatore del dialetto ternano contemporaneo.
> Le sue opere sono la base filologica autentica per il vocabolario della §1.

### Luigi Cordidonne (editore: Edizioni Thyrus)

| Titolo | Note |
|---|---|
| **"Dizionario del dialetto di Terni e del suo territorio"** — ISBN 9788868081621 | Opera filologica accademica; morfosintassi e semantica del vernacolo ternano |

> Cordidonne fornisce la base storico-linguistica; Menghini l'uso contemporaneo.
> Per massima autenticità: integrare entrambe le fonti.

### Fonte digitale

- **Piccolo Dizionario Ternano-Italiano** — databaserossoverde.it (online dal 1997): ~2.000 voci ordinate alfabeticamente

---

> *Il vocabolario attuale nella §1 è basato su dialetto orale + fonti sopra.*
> *Per upgrade v2.0: cross-check con Menghini "A Terni se dice..." voce per voce.*
