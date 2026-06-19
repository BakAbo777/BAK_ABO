# bakabo-social-marketplace-hub

Skill for the unified Social & Marketplace Hub (`pages/03_Social.py`, Streamlit, porta 8501): Facebook, Instagram, Pinterest, Amazon Merch on Demand, Telegram bot, TikTok — gestiti da un'unica interfaccia con tracciamento GA4 su ogni link.

## Platforms

- **Facebook / Instagram (Meta)** — post/reel/story queue, UTM automatico, Meta Commerce per catalogo prodotti. Env: `META_BUSINESS_ID`, `META_ACCESS_TOKEN`, `FACEBOOK_PAGE_ID`, `INSTAGRAM_BUSINESS_ID`.
- **Pinterest** — 9 board mappate sulle collezioni BKS (hours, glyph, marker, riviera, pulse, token, flag, folklore + All Drops), check lunghezza titolo (<=60) e descrizione (150-160) per Rich Pin SEO. Env: `PINTEREST_ACCESS_TOKEN`.
- **Amazon Merch on Demand** — non Seller Central. Upload design via merch.amazon.com, tracker ASIN/marketplace/tier/royalty in `output/social/amazon_merch_designs.csv`. Tier progression: Standard (10 slot) -> Premium (25) -> Pro (100+). Specifiche file: PNG 4500x5400px 300DPI sfondo trasparente. Env: `AMAZON_MERCH_EMAIL`, `AMAZON_MERCH_TIER`.
- **Telegram** — bot diretto via REST (`api.telegram.org/bot{token}/...`), invio messaggi con template (drop/restock/promo/behind-the-scenes), storico in `output/social/telegram_history.json`. Env: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `TELEGRAM_CHANNEL_ID` (opzionale).
- **TikTok** — content calendar, queue post condivisa con Meta. Env: `TIKTOK_ADVERTISER_ID`, `TIKTOK_ACCESS_TOKEN`.

## Output persistenti

- `output/social/social_posts_queue.csv` — coda post Meta/TikTok
- `output/social/amazon_merch_designs.csv` — tracker design Amazon Merch
- `output/social/pinterest_pins_queue.csv` — coda pin Pinterest
- `output/social/telegram_history.json` — storico messaggi bot (ultimi 50)

## UTM standard BKS

Ogni link esterno passa da `build_utm(url, source, medium, campaign, content)`: source = piattaforma, medium = social/referral/paid_social, campaign = collezione BKS, content = formato post. Tracciato su GA4 property `bakabo-9a8c5` (`483501489`) e GTM `GTM-PF5Z85KS`.

## Autonomy

L'agente puo preparare bozze, queue, board structure e UTM su tutte le piattaforme. Pubblicazione effettiva (invio Telegram, post Meta/TikTok, submit design Amazon Merch) richiede sempre conferma esplicita dell'operatore. Nessuna automazione cliente senza opt-in.

## Direttive Google (ogni post)

- UTM tracciato su ogni link verso bakabo.club
- Alt text su ogni immagine
- Headline <=60 char (Facebook/Pinterest), descrizione 150-160 char (Pinterest Rich Pin)
- Nessun contenuto YMYL senza fonte verificata
- E-E-A-T: autenticita brand, niente sconti/certificazioni inventate
- Merchant Center come source of truth per prezzo e disponibilita

## Related skills

Si appoggia a `bakabo-social-campaigns` per lingue e protocollo di approvazione multilingua.
