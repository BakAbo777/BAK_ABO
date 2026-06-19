from __future__ import annotations

from typing import Any


# Session: 2026-06-17/18 — services rebuild + theme deploy + module BKS upgrade pass
# Session: 2026-06-18 — armocromista pass 1: product pages + responsive.css
# Session: 2026-06-18 — armocromista pass 2: all 8 collections — collection page 47/47 PASS
# Session: 2026-06-18 — output/ alignment (folklore→origin 880 files) + BKS SQLite database (53 tables)
# Session: 2026-06-18 — BKS Algorithm engine + Streamlit Control Center + pages upgrade
# Session: 2026-06-18 — collection templates (collection.json default + bks-origin updated) + hub page + card fix + hearts all pages + mobile patch v2 + 203 Shopify products CSV
# Session: 2026-06-18 v3 — Playwright audit (48 pages) + all 8 BKS collection templates fixed (main-collection-product-grid-bks) + hearts global load + template-product body class + html overflow fix + bks-theme-effects.css deployed
# Session: 2026-06-18 v4 — Card white background global fix (home+product+collection) + MutationObserver hearts (AJAX related-products) + 3 missing Shopify pages created (bks-collections, bks-ai-assistant, bks-custom)
# Session: 2026-06-18 v5 — P0 Liquid pagination fix (bks-member-dashboard) + /collections redirect + mobile variant picker + 365 Onyx color rename + 203 Folklore→Origin (body+alts) + 167 series:*→archive:* migration
# Session: 2026-06-19 v6 — Home index.json + FAQ (JSON-LD) + About pages + Product Hero (auto-accent) + Camerino validation (GDPR) + Header 3px accent bar + Marketing Hub + Analytics page + Shopify pages API + 4 avatar videos uploaded
# Session: 2026-06-19 v7 — Contact page + Policy template + Default product.json (BKS hero all products) + Magazine all 8 collections
# Session: 2026-06-19 v8 — 13 product-type collection templates (sneakers/backpack/puffer-jacket/etc.) + deploy 89 files
# Session: 2026-06-19 v9 — Members area Metal tier alignment + anatomy fix (bks-token-editorial.png → bks-token-puffer.png) + rejected_assets DB
# Session: 2026-06-19 v10 — GDPR cookie banner + Google Shopping XML feed + Cloudflare Worker config
# Session: 2026-06-19 v17 — Pricing fix (swimsuits/slippers/flip flops), 13 prodotti immagini sync Printify, Athletic Shorts rinominati schema BKS
# Session: 2026-06-19 v18 — Catalog naming schema applicato a TUTTE le categorie: 142 prodotti rinominati (Hoodie/Lounge Pants/One-Piece/Puffer/Sneakers/Swim Trunks/Tee/Pullover + Athletic Shorts)
# Session: 2026-06-19 v19 — SESSION_CHANGES compattato, Athletic Shorts $65→$69 (87 varianti), Wishlist standalone page live (bakabo.club/pages/bks-wishlist)
# Session: 2026-06-19 v20 — Cloudflare Worker bks-agent live (KV+secrets+OpenAI), AI assistant endpoint→Worker, try/catch fix
# Session: 2026-06-19 v21 — AI assistant attivo globalmente (enabled:true, endpoint Worker), 6 template/sezioni deploy (members-login, embed, origin, ai-page, members, wishlist)
# Session: 2026-06-19 v22 — Deploy completo 48 file BKS (assets/sections/snippets/templates) + handle emoji fix Pullover Token bks-pullover-token + GSC TXT verificato
BKS_LAST_DEPLOY = "19_06_2026_v22"
BKS_THEME_VERSION = "BKS TM04 19_06_2026 V.22"
BKS_THEME_ID = "202392961362"
BKS_COLLECTIONS = ("Hours", "Glyph", "Marker", "Riviera", "Pulse", "Token", "Flag", "Origin")
SESSION_CHANGES = {
    "V.0  18_06_2026": "TM04 deploy (31 files) + module BKS upgrade pass (trust_gate, SKILL_DOC, Folklore→Origin)",
    "V.1  18_06_2026": "Armocromista pass 1 (product pages, responsive.css) + pass 2 (47/47 collezioni PASS)",
    "V.2  18_06_2026": "output/ align 880 files + SQLite DB 53 tabelle + collection templates + hearts + mobile patch v2",
    "V.3  18_06_2026": "Playwright audit 48/48 PASS + card bg fix + hearts MutationObserver + 3 pagine Shopify",
    "V.4  18_06_2026": "P0 fixes: dashboard paginate, /collections redirect, variant picker, 365 varianti Onyx",
    "V.5  18_06_2026": "203 prodotti Folklore→Origin body+alts + 167 tags series:*→archive:* + GMC metafields 203/203",
    "V.6  19_06_2026": "Home index.json + FAQ JSON-LD + About pages + Product Hero auto-accent + header 3px bar + Marketing/Analytics pages",
    "V.7  19_06_2026": "Contact + Policy template + Default product.json (tutti prodotti BKS hero) + Magazine 8 spread + nav/footer update",
    "V.8  19_06_2026": "13 product-type collection templates + 89 file deploy — copertura sito completa",
    "V.9  19_06_2026": "Members Metal tier unificato + anatomy fix bks-token-puffer.png + rejected_assets DB",
    "V.10 19_06_2026": "GDPR banner + Google Shopping XML feed + Cloudflare Worker config",
    "V.11 19_06_2026": "JSON-LD structured data (Product/WebSite/ItemList/Organization)",
    "V.12 19_06_2026": "BKS Cart Drawer CSS (ink bg, DM Mono, gold CTA)",
    "V.17 19_06_2026": "Pricing fix (swimsuits $55/slippers $55/flip flops $49) + 13 prodotti immagini Printify sync (28 upload)",
    "V.18 19_06_2026": "Catalog naming schema applicato a TUTTE le categorie — 142 prodotti rinominati BKS [Type] — [Collection]",
    "V.19 19_06_2026": "SESSION_CHANGES compattato + Athletic Shorts $65→$69 (87 varianti) + Wishlist standalone page (bakabo.club/pages/bks-wishlist)",
    "V.20 19_06_2026": "Cloudflare Worker bks-agent live (KV 8f6b1e4a, 4 secrets, OpenAI) + AI assistant endpoint→Worker + try/catch graceful 503",
    "V.21 19_06_2026": "AI assistant attivo globalmente (enabled:true) + 6 deploy: members-login, ai-embed, origin template, ai-page, members, wishlist",
    "V.22 19_06_2026": "Deploy completo 48 file BKS custom (11 assets + 25 sections + 6 snippets + 6 templates) + handle emoji fix Pullover Token + GSC TXT OK",
}


AGENT_PROFILE: dict[str, Any] = {
    "name": "BKS Master Agent",
    "role": "Agente operativo finale per fasi, API, avatar, social render e skill registry.",
    "avatar_candidate": True,
    "voice": "Calma, precisa, premium, operativa.",
    "heygen_avatar_env": "HEYGEN_AVATAR_ID",
    "heygen_voice_env": "HEYGEN_VOICE_ID",
    "channels": "Dashboard;HeyGen;Instagram Reels;TikTok;YouTube Shorts;Homepage",
    "customer_consent_required": True,
    "dialogic_mode": "never improvise; explain; ask approval for risky actions; learn from feedback",
}

AGENT_MODES: tuple[dict[str, str], ...] = (
    {"mode": "Internal operator", "use": "Gestisce fasi, API, file, avanzamento e checklist operative.", "customer_safe": "internal_only"},
    {"mode": "BKS Virtual Creator 360", "use": "Ideazione e coordinamento a 360 gradi: sito, copy, video, offerte, canali, pagamenti e trust Google.", "customer_safe": "supervised"},
    {"mode": "Dialogic copilot", "use": "Dialoga come co-fondatore operativo: propone, spiega, verifica e chiede conferma prima delle azioni rischiose.", "customer_safe": "supervised"},
    {"mode": "Production director", "use": "Dà direttive creative per shooting, spot, avatar, tono e asset.", "customer_safe": "internal_only"},
    {"mode": "Male spot avatar", "use": "Versione uomo per spot, video verticali e spiegazioni prodotto.", "customer_safe": "public_content"},
    {"mode": "Female spot avatar", "use": "Versione donna per spot, video verticali e spiegazioni prodotto.", "customer_safe": "public_content"},
    {"mode": "Customer concierge", "use": "Parla con il cliente solo dopo consenso esplicito e solo per supporto/prodotto.", "customer_safe": "requires_opt_in"},
)


def _phase_line(phase: dict[str, Any]) -> str:
    return f"{phase['phase_id']} {phase['name']}: {phase['status']} ({phase.get('progress', 0)}%)"


def _connection_label(item: dict[str, Any] | bool) -> str:
    if isinstance(item, bool):
        return "Connesso" if item else "Non connesso"
    status = item.get("status", "")
    configured = bool(item.get("configured", False))
    if configured and status not in {"offline", "missing_key", "missing_token", "missing_webhook_url", "missing_oauth", "error", "suspended", "limited", "needs_review", "needs_fix", "needs_config", "manual_pending", "blocked"}:
        return f"Connesso ({status})"
    return f"Non connesso ({status or 'missing'})"


def reply(message: str, snapshot: dict[str, Any]) -> dict[str, Any]:
    lower = message.lower().strip()
    phases = snapshot.get("phases", [])
    services = snapshot.get("services", {})
    avatar = snapshot.get("avatar", {})
    social = snapshot.get("social", {})
    skills = snapshot.get("skills", {})
    communications = snapshot.get("communications", {})
    sales_channels = snapshot.get("sales_channels", {})
    google = snapshot.get("google", {})
    marketing = snapshot.get("marketing", {})
    theme = snapshot.get("theme", {})
    turbobak = snapshot.get("turbobak", {})
    market = snapshot.get("market", {})
    actions = snapshot.get("actions", {})
    weekly = snapshot.get("weekly", {})
    daily = snapshot.get("daily", {})
    agent_os = snapshot.get("agent_os", {})
    payments = snapshot.get("payments", {})
    trust = snapshot.get("trust", {})
    always_on = snapshot.get("always_on", {})
    marketing_logic = snapshot.get("marketing_logic", {})
    official_inbox = snapshot.get("official_inbox", {})
    social_campaigns = snapshot.get("social_campaigns", {})
    legal_guardrails = snapshot.get("legal_guardrails", {})
    theme_assistant = snapshot.get("theme_assistant", {})
    network = snapshot.get("network", {})
    growth_crm = snapshot.get("growth_crm", {})
    catalog_sync = snapshot.get("catalog_sync", {})
    product_names = snapshot.get("product_names", {})
    openai_alliance = snapshot.get("openai_alliance", {})
    canva = snapshot.get("canva", {})
    hyperframes = snapshot.get("hyperframes", {})

    if not lower:
        return {"reply": "Scrivimi una richiesta operativa: stato, connessioni, avatar, social, skill, oppure run fase 09.", "actions": []}

    if "non deve improvvisare" in lower or "improvvisare" in lower or "dialogare" in lower or "dialogo" in lower or "come io con te" in lower:
        return {
            "reply": (
                "Ricevuto: lavoro in modalita Dialogic Copilot. Non improvviso: parto dai dati, propongo la prossima azione minima, "
                "spiego perche, dico come verificarla e chiedo conferma prima di pubblicare, inviare ricorsi, attivare Ads, toccare pagamenti o parlare con clienti."
            ),
            "actions": ["open_agent", "open_master_actions"],
        }

    if "pieno controllo" in lower or "ai conversazionale" in lower or "controllo del sistema" in lower or "ai conversazionale" in lower:
        next_action = actions.get("next_action", {})
        return {
            "reply": (
                "Confermo: l'interfaccia deve restare conversazionale. Io tengo il controllo operativo leggendo fasi, API, Google, network, posta, tema, social, pagamenti e memoria; "
                "tu mi chiedi cosa fare, io propongo un solo passo, preparo i file o le verifiche e poi registro l'esito. "
                f"Prossimo passo ora: {next_action.get('title', 'verifica Google Merchant')}."
            ),
            "actions": ["open_agent", "open_master_actions"],
        }

    if "real time" in lower or "realtime" in lower or "progressione" in lower or "grafici" in lower or "elaborazione" in lower:
        return {
            "reply": (
                "Modalita real-time attiva: mostro la progressione dell'agente in sei step, con grafici leggeri: dialogo, memoria/fasi, network/API, trust gate, prossima azione, verifica/apprendimento. "
                "Non ricarico tutto in continuo: aggiorno il controllo live ogni pochi secondi e uso le schede dettagliate solo come prova."
            ),
            "actions": ["open_realtime_control", "open_master_actions"],
        }

    if "prossima" in lower or "prima cosa" in lower or "cosa facciamo" in lower or "priorit" in lower:
        next_action = actions.get("next_action", {})
        return {
            "reply": (
                f"Prima cosa: {next_action.get('title', 'verifica Google Merchant')}.\n"
                f"Perche: {next_action.get('why', 'dobbiamo togliere i blocchi prima di scalare')}.\n"
                f"Azione: {next_action.get('do', 'apri la scheda Azioni Master e verifica il primo blocco')}."
            ),
            "actions": ["open_master_actions"],
        }

    if "settimana" in lower or "settiman" in lower or "obiettivi" in lower:
        summary = weekly.get("summary", {})
        return {
            "reply": (
                f"Obiettivi minimi {summary.get('week', '')}: {summary.get('pass', 0)}/{summary.get('total', 0)} passati, "
                f"{summary.get('needs_attention', 0)} da controllare. La routine resta: Merchant, tag/analytics, feed, timer, tema, mercato e memoria agente."
            ),
            "actions": ["open_weekly_goals", "open_master_actions"],
        }

    catalog_intent = "csv" in lower or "catalogo" in lower or ("shopify" in lower and "printify" in lower) or "aggiornamenti prodotti" in lower

    if "giornal" in lower or "daily" in lower or "rete" in lower or ("aggiornament" in lower and not catalog_intent):
        summary = daily.get("summary", {})
        next_action = daily.get("next_action", {})
        return {
            "reply": (
                f"Daily Web Update: modalita {summary.get('mode', 'local_snapshot')}, "
                f"{summary.get('pass', 0)} pass, {summary.get('needs_fix', 0)} da correggere, "
                f"{summary.get('errors', 0)} errori rete. "
                f"Prossima azione: {next_action.get('title', summary.get('next_action', 'verifica Google Merchant'))}."
            ),
            "actions": ["open_daily_update", "open_master_actions"],
        }

    if "sempre attivo" in lower or "always" in lower or "monitorare" in lower or "monitor" in lower or "drive" in lower:
        summary = always_on.get("summary", {})
        return {
            "reply": (
                f"Always-On Agent: stato {summary.get('status', 'watching')}, autonomia {summary.get('autonomy', 'supervised')}, "
                f"blocker {summary.get('blockers', 0)}, Drive ready {summary.get('drive_ready', 0)} artifact. "
                "Monitoro sempre; preparo correzioni e report; chiedo approvazione per pubblicare, inviare ricorsi, Ads, pagamenti e messaggi cliente."
            ),
            "actions": ["open_always_on", "open_master_actions"],
        }

    if "dns" in lower or "dsn" in lower or "network" in lower or "suffiss" in lower or "trasmissione dati" in lower or "bounce" in lower or "dmarc" in lower or "dkim" in lower or "spf" in lower:
        summary = network.get("summary", {})
        return {
            "reply": (
                f"Network Trust Monitor: dominio {summary.get('domain', 'bakabo.club')}, stato {summary.get('status', 'manual_pending')}. "
                f"DNS: {summary.get('dns_pass', 0)} pass / {summary.get('dns_attention', 0)} attention. "
                f"Email/DSN: {summary.get('email_pass', 0)} pass / {summary.get('email_attention', 0)} attention. "
                f"Endpoint: {summary.get('endpoints_pass', 0)} pass / {summary.get('endpoints_attention', 0)} attention. "
                "Priorita: DMARC, DSN/bounce su crew@bakabo.club, TLS SMTP e suffissi UTM/click usati solo per analytics con canoniche pulite."
            ),
            "actions": ["open_network_monitor", "open_google_trust"],
        }

    if catalog_intent:
        summary = catalog_sync.get("summary", {})
        return {
            "reply": (
                f"Catalog Live Sync: stato {summary.get('status', 'ready_for_live_sync')}. "
                f"Shopify {summary.get('shopify_products', 0)} prodotti, Printify {summary.get('printify_products', 0)}, "
                f"match {summary.get('matched', 0)}, attention {summary.get('attention', 0)}, errori {summary.get('errors', 0)}. "
                "Quando premi Run live sync scarico direttamente da Shopify/Printify, genero i CSV, aggiorno il ledger e segnalo prodotti nuovi, non mappati o con stato diverso."
            ),
            "actions": ["open_catalog_sync", "open_references"],
        }

    if "nomi prodotti" in lower or "nome prodotto" in lower or "titoli prodotti" in lower or "titolo prodotto" in lower or "sbgliati" in lower or "sbagliati" in lower or "schema nome" in lower or "naming" in lower:
        summary = product_names.get("summary", {})
        return {
            "reply": (
                "Schema titoli BKS (da skill bakabo-brand, formula unica):\n"
                "  BKS [Product Type] — [Collection]\n"
                "  Se piu prodotti stesso tipo+collezione: BKS [Product Type] — [Collection] 01 / 02\n\n"
                "Esempi corretti: BKS Athletic Shorts — Riviera 01, BKS Sneakers — Pulse, BKS Swim Trunks — Riviera\n"
                "Errori da evitare: BKS Pulse™ Urban Luxury Sneakers (tm, aggettivi), SerenityBlend (BKS)🍀 (emoji, nome AI casuale)\n\n"
                "Categoria Athletic Shorts — rinominati 2026-06-19 (11 prodotti):\n"
                "  Flag, Hours, Origin, Pulse, Token → singoli (no numero)\n"
                "  Glyph 01/02, Marker 01/02, Riviera 01/02 → doppi (numerati)\n\n"
                f"Product Name Audit: {summary.get('products', 0)} prodotti controllati, "
                f"{summary.get('needs_fix', 0)} da correggere. "
                "Schema applicato su TUTTE le categorie 2026-06-19 v18 — 142 prodotti rinominati:\n"
                "  Athletic Shorts (11), Hoodie (16), Lounge Pants (14), One-Piece (18),\n"
                "  Puffer (29), Sneakers (22), Swim Trunks (25), Tee (6), Pullover (1)\n"
                "Catalogo nominalmente allineato. Rimane: Stamp Sneakerz (DRAFT, emoji — Roberto decide)."
            ),
            "actions": ["open_product_name_audit", "open_catalog_sync"],
        }

    if any(t in lower for t in ("contrasto", "contrast", "leggibil", "visibil", "testo nero", "pagina nera", "buio", "scuro", "armocro", "colori")):
        return {
            "reply": (
                "Armocromista pass 1+2 completo (18_06_2026). "
                "REGOLA BASE: accent BKS sono DECORATIVI (bordi, glow, chip bg) — testo sempre #0A0A0A su chiaro, #FAFAF7 su scuro. "
                "PASS 1 — product pages: "
                "bks-product-system kicker #5a5450 + bordo-accent (era color-mix invisibile per Hours); "
                "bks-product-meta 3 fix su amber bg (#1e1a14/#2a2218); "
                "bks-responsive.css: mobile patch + section tokens + cindex + member + footer + timed-offer + tier badge. "
                "PASS 2 — tutte le 8 collezioni: "
                "bks-collection-signal chip/typo-label -> color-mix(60%,#FAFAF7) per Token/Marker/Flag (3.4-3.8->6.5-7.4:1 su dark); "
                "kicker/label border -> color-mix(60%,#0A0A0A) per Hours/Glyph (1.7->4.3:1); "
                "main-collection-product-grid: Origin+backpack foreground #FAFAF7->#0A0A0A (verde bg 3.5->5.4:1); "
                "made-to-order stamp 74->85% (3.4->5.2:1). "
                "AUDIT FINALE pagina collezione: 47/47 PASS (4.3-18.9:1). "
                "Bug critico risolto: tutti 15 product template erano BKS Folklore/bks-folklore -> BKS Origin/bks-origin."
            ),
            "actions": ["open_theme", "open_master_actions"],
        }

    if "font" in lower or "tipografia" in lower or ("mobile" in lower and "descriz" in lower) or "bks e la serie" in lower or "non stravolgere" in lower:
        return {
            "reply": (
                "Standard BKS impostato in modo conservativo: BKS Display per titoli, BKS Text per descrizioni e pannelli, BKS Mono per log e dati. "
                "Su mobile le descrizioni restano almeno 14-15px con line-height ariosa, i bottoni almeno 44px, spaziatura lettere a zero. "
                "Naming: BKS + serie/collezione rimane il riferimento, senza riordinare aggressivamente i titoli prodotto."
            ),
            "actions": ["open_theme", "open_skills"],
        }

    if "fiducia" in lower or "trust" in lower or "esigenza google" in lower:
        summary = trust.get("summary", {})
        return {
            "reply": (
                f"Google Trust Contract: {summary.get('pass', 0)}/{summary.get('total', 0)} bisogni passati, "
                f"{summary.get('needs_fix', 0)} da correggere, {summary.get('manual_pending', 0)} da verificare manualmente. "
                "Prima di crescere con Ads, timer, Bitcoin, social o automazioni cliente, dobbiamo provare identita, prodotto reale, prezzi chiari, shipping, resi, checkout sicuro, tag e supporto."
            ),
            "actions": ["open_google_trust", "open_master_actions"],
        }

    if "google" in lower or "merchant" in lower or "fuorviant" in lower or "sospes" in lower or "gtm" in lower or "ga4" in lower or "google analytics" in lower or "tag" in lower:
        summary = google.get("summary", {})
        tag_summary = google.get("tag_summary", {})
        feed_summary = google.get("feed", {}).get("summary", {})
        return {
            "reply": (
                f"Google Merchant: stato {summary.get('status', 'unknown')}, motivo {summary.get('reason', 'unknown')}, "
                f"P0 blocker {summary.get('blockers', 0)}. "
                f"GTM {tag_summary.get('expected_gtm_percent', 0)}%, GA4 {tag_summary.get('ga4_percent', 0)}%. "
                f"Attributi prodotto da sistemare: {feed_summary.get('attribute_issues', 0)}; paesi da configurare: {feed_summary.get('country_needs_config', 0)}. "
                f"Prima azione: {summary.get('first_action', 'disattiva o completa inventario locale')}. "
                "Poi pagine prodotto disponibili, size/color/gender/age, spedizioni/resi per paese, trust pages e ricorso."
            ),
            "actions": ["open_google", "open_master_actions"],
        }

    if "mercato" in lower or "market sense" in lower or "adatta" in lower or "evoluzione" in lower:
        summary = market.get("summary", {})
        recommendations = market.get("recommendations", [])
        first = recommendations[0] if recommendations else {}
        return {
            "reply": (
                f"Market Sense: punteggio {summary.get('market_sense', 0)} in modalita {summary.get('mode', 'conservative_adaptation')}. "
                f"Suggerimento: {first.get('recommendation', 'adattare il sito con cambi piccoli e verificati')}. "
                f"Cambio sito: {first.get('site_change', 'prima fiducia e chiarezza, poi campagne')}."
            ),
            "actions": ["open_market_sense", "open_master_actions"],
        }

    if "performant" in lower or "logic" in lower or "logiche" in lower or "benchmark" in lower:
        summary = marketing_logic.get("summary", {})
        rows = marketing_logic.get("rows", [])
        top = rows[:3]
        lines = [
            f"Marketing Logic Scout: {summary.get('playbooks', 0)} playbook, migliore ora: {summary.get('best_logic', '')}.",
            "Classifica iniziale:",
        ]
        lines.extend(
            f"- {row.get('logic')}: {row.get('readiness')} / score {row.get('quality_fit_score')} / {row.get('first_action')}"
            for row in top
        )
        lines.append("Le applichiamo in modo progressivo: prima trust, poi creator/video, poi Pinterest/timer.")
        return {"reply": "\n".join(lines), "actions": ["open_marketing_logic", "open_theme"]}

    if "allena" in lower or "train" in lower or "aggiornato" in lower or "cosa sai" in lower or "cosa hai imparato" in lower:
        return {
            "reply": (
                f"Agente aggiornato — sessione {BKS_LAST_DEPLOY}. Nuove conoscenze:\n"
                "- Home page finalmente live (index.json): video canvas 4 avatar + magazine editoriale\n"
                "- FAQ con JSON-LD (Google FAQ rich results attivi)\n"
                "- About BakAbo + About BKS Studio live su Shopify\n"
                "- Product Hero: auto-rileva accent dalla collezione, prodotto fluttua su sfondo colorato\n"
                "- Header: barra 3px accent per collezione (non cambia il bg, solo il bordo inferiore)\n"
                "- Camerino: validazione foto (600x900min, verticale, 12MB), GDPR consent attivo\n"
                "- Marketing Hub (pagina 09): crea offerte Shopify, sconti tier, UTM builder, trigger email\n"
                "- Analytics (pagina 10): revenue chart, top prodotti, ordini live da Shopify API\n"
                "- 4 video avatar caricati su Shopify Files (CDN in admin > Content > Files)\n"
                "- 3 pagine Shopify create via API (FAQ/About BakAbo/About BKS Studio)\n"
                f"Deployato: {BKS_THEME_VERSION} — 70 file OK"
            ),
            "actions": ["open_theme", "open_master_actions"],
        }

    if "home" in lower or "canvas" in lower or "video canvas" in lower or "index" in lower or "pagina principale" in lower:
        return {
            "reply": (
                f"Home page BKS — live con template index.json ({BKS_LAST_DEPLOY}). "
                "Struttura: bks-home-video-canvas (4 video avatar in sequenza, crossfade, grain, nessun audio) -> "
                "bks-home-magazine (copertina Bebas Neue + 8 spread editoriali Hours/Origin/Glyph/Marker/Riviera/Pulse/Token/Flag + pull quote) -> "
                "bks-store-reviews -> bks-trust-strip. "
                "Magazine ora include tutti e 8 i spread (v7 — era 4 in v6). "
                "I 4 video avatar sono stati caricati su Shopify Files; copia gli URL CDN in Theme Editor > BKS Video Canvas Hero > Video 1/2/3/4."
            ),
            "actions": ["open_theme", "open_master_actions"],
        }

    if "faq" in lower or "domande frequenti" in lower or "domande" in lower or "assistenza" in lower:
        return {
            "reply": (
                "FAQ live su bakabo.club/pages/faq-domande-frequenti (template page.bks-faq). "
                "9 domande pre-caricate, 7 categorie (Prodotti/Ordini/Spedizioni/Resi/Members/Try-On/Pagamenti), filtro pills. "
                "JSON-LD FAQPage schema attivo = Google mostra le risposte direttamente nei risultati di ricerca (rich results). "
                "Aggiungi/modifica domande dal Theme Editor > BKS FAQ > blocchi Domanda & Risposta."
            ),
            "actions": ["open_theme", "open_google"],
        }

    if "contatt" in lower or "contact" in lower or "scrivici" in lower or "crew@" in lower or "parliamoci" in lower:
        return {
            "reply": (
                "Contact page live: bakabo.club/pages/contatti (template page.bks-contact, id 173871792466). "
                "Layout bicolonna: sinistra — crew@bakabo.club + IG/YT + link a Custom Request/FAQ/About; "
                "destra — form nativo Shopify (nome/email/argomento dropdown 7 categorie/messaggio). "
                "Form submission invia email al proprietario store. Personalizza titolo/lead in Theme Editor > BKS Contact."
            ),
            "actions": ["open_theme", "open_master_actions"],
        }

    if "privacy" in lower or "termini" in lower or "reso" in lower or "resi" in lower or "spedizione" in lower or "spedizioni" in lower or "normativa" in lower or "policy" in lower or "legal" in lower or "cookie" in lower or "gdpr" in lower:
        return {
            "reply": (
                "Policy pages — template BKS attivo: templates/policy.liquid -> sezione bks-policy.liquid. "
                "Le policy native Shopify (Settings > Legal > Privacy/Terms/Refund/Shipping) ora usano il template BKS styled "
                "(BKS typography: Bebas Neue header, DM Sans body, accent bar 8 collezioni, data aggiornamento). "
                "URL Shopify: bakabo.club/policies/privacy-policy, /policies/terms-of-service, "
                "/policies/refund-policy, /policies/shipping-policy. "
                "Contenuto: modifica in Shopify admin > Settings > Policies."
            ),
            "actions": ["open_master_actions"],
        }

    if "about" in lower or "chi siamo" in lower or "bakabo storia" in lower or "bks studio" in lower:
        return {
            "reply": (
                "Pagine About live: "
                "bakabo.club/pages/about-bakabo-1 (template page.bks-about-bakabo) — brand story, NFT origins, print-on-demand. "
                "bakabo.club/pages/about-bks-studio (template page.bks-about-bks) — studio, processo AI-art, dalla generazione alla stampa. "
                "Entrambe usano bks-about.liquid: hero con immagine (blend luminosity su accent), pull quote, colonne testo, statistiche. "
                "Carica immagini hero in Theme Editor > BKS About > Hero image."
            ),
            "actions": ["open_theme", "open_master_actions"],
        }

    if "hero prodotto" in lower or "product hero" in lower or "pagina prodotto" in lower or "prodotto" in lower:
        return {
            "reply": (
                f"Product Hero live ({BKS_LAST_DEPLOY}): bks-product-hero.liquid. "
                "Auto-rileva il colore accent dalla collezione BKS tramite product.collections (nessuna configurazione manuale necessaria). "
                "L'immagine prodotto fluttua sul fondo colorato con drop-shadow — sfondo bianco appare 'ritagliato' sul colore della collezione. "
                "Template product.json (DEFAULT): ora TUTTI i prodotti hanno il BKS hero senza assegnazione manuale. "
                "Template product.bks.json: disponibile come alternativa esplicita. "
                "Struttura: bks-product-hero + main-product + bks-product-editorial-care + bks-accessories-panel."
            ),
            "actions": ["open_theme", "open_master_actions"],
        }

    if "analytics" in lower or "dati" in lower or "vendite" in lower or "revenue" in lower or "ordini" in lower:
        return {
            "reply": (
                "Analytics Dashboard (pages/10_Analytics.py — Streamlit porta 8501): "
                "revenue giornaliera (line chart), top prodotti (bar chart + tabella), ordini per stato, "
                "catalog summary per tipo prodotto. Dati live da Shopify Admin API. "
                "Periodi: 7/30/90 giorni. Bottone Aggiorna per refresh cache. "
                "Link diretti: Shopify Analytics, Google Analytics, Google Merchant Center."
            ),
            "actions": ["open_analytics", "open_google"],
        }

    if "timer" in lower or "offerta" in lower or "sconto" in lower or "coupon" in lower or "marketing" in lower or "countdown" in lower:
        summary = marketing.get("summary", {})
        return {
            "reply": (
                "Marketing Hub attivo (pages/09_Marketing.py — Streamlit porta 8501). "
                "Funzioni: Active Offers (regole sconto Shopify), Create Offer (nuova regola + codice via API), "
                "Member Discounts (tier Lead 0% / Iron 5% / Brass 10% / Silver 15% / Gold 20%), "
                "UTM Builder (link tracciati per GA4), Email Triggers (checklist flow welcome/tier/drop/cart). "
                f"Timer/timed-offer: stato {summary.get('status', 'draft')}, compliance {summary.get('compliance', 'unknown')}. "
                "Uso solo con scadenza reale e codice Shopify configurato."
            ),
            "actions": ["open_marketing", "open_theme"],
        }

    if "sneakers" in lower or "backpack" in lower or "puffer" in lower or "windbreaker" in lower or "hoodie" in lower or "swim" in lower or "lounge" in lower or "athletic" in lower or "flip" in lower or "tipo prodotto" in lower or "product type" in lower:
        return {
            "reply": (
                f"Product-type collections live ({BKS_LAST_DEPLOY}): 13 template dedicati con BKS hero e accent color per categoria. "
                "Sneakers #1a1a1a / Puffer Jacket #1c2d3a / Windbreaker #1e3a2c / Pullover Hoodie #2a2a2a / "
                "Swim Trunks+Swimwear #0d4d5a / Flip-Flop #8a5c10 / Athletic Shorts #1a1a1a / Lounge Pants #3d2010 / "
                "Backpack+Travel Bag #2a1e14 / One-Piece Swimsuit #c04418 / Racerback Dress #7820a8. "
                "Ogni template ha tagline editoriale + bks-cindex (8 BKS collections) in fondo. "
                "template_suffix già impostato su tutte 13 smart_collections — /collections/{handle} usa automaticamente il template BKS."
            ),
            "actions": ["open_theme", "open_master_actions"],
        }

    if "tema" in lower or "theme" in lower or "scuro" in lower or "tenebroso" in lower or "deploy" in lower or "versione" in lower or "18_06" in lower or "19_06" in lower:
        summary = theme.get("summary", {})
        return {
            "reply": (
                f"Tema live: {BKS_THEME_VERSION} (ID {BKS_THEME_ID}). "
                f"Ultimo deploy: {BKS_LAST_DEPLOY} — 89 file OK (sections/assets/snippets/templates/layout). "
                f"Stato interno: {summary.get('status', 'tm04_live')}. "
                "Struttura completa: Home + 8 BKS collezioni editoriali + 13 product-type collections + Product (default tutti) + FAQ + About x2 + Members + Hub + AI + Custom + Planet + Contact + Policy. "
                "Script deploy: python scripts/deploy_theme_section.py"
            ),
            "actions": ["open_theme", "open_master_actions"],
        }

    if "impara" in lower or "memoria" in lower or "turbobak" in lower or "engine" in lower:
        summary = turbobak.get("summary", {})
        patterns = turbobak.get("reuse_patterns", [])[:4]
        pattern_text = "; ".join(row.get("pattern", "") for row in patterns) or "worker chain, alert, storico"
        return {
            "reply": (
                f"TurboBAK Engine: {summary.get('workers', 0)} worker, {summary.get('pages', 0)} pagine, "
                f"{summary.get('log_files', 0)} log indicizzati, {summary.get('reuse_patterns', 0)} pattern riusabili. "
                f"Sto importando queste logiche: {pattern_text}. Il Master salva gli esiti delle verifiche e usa la memoria per scegliere la prossima azione."
            ),
            "actions": ["open_turbobak", "open_master_actions"],
        }

    if "routine" in lower or "automatizz" in lower or "costi" in lower or "cost guard" in lower or "api cosc" in lower:
        routine = snapshot.get("routine", {})
        summary = routine.get("summary", {})
        next_step = routine.get("next_step", {})
        return {
            "reply": (
                f"Routine agente: {summary.get('steps', 0)} step, {summary.get('ready', 0)} pronti, "
                f"{summary.get('attention', 0)} da attenzionare. "
                f"Prossimo step: {next_step.get('step', summary.get('next_step', 'Check Google trust gate'))}. "
                "Uso prima dati locali, poi API leggere, poi chiedo approvazione per crediti, render, pubblicazioni, email campagne e budget Ads."
            ),
            "actions": ["open_routine", "open_master_actions"],
        }

    if "adamo" in lower or "eva" in lower or "modelli" in lower or "mondo" in lower or "temperatur" in lower or "contesto" in lower:
        summary = snapshot.get("photo_studio", {}).get("summary", {})
        return {
            "reply": (
                f"Adamo/Eva nuova era: sistema pronto con {summary.get('world_contexts', 0)} contesti mercato. "
                "Non sono celebrita e non fingono appartenenze: sono una coppia adulta, internazionale, adattata al mercato solo quando Analytics, lingua, shipping, resi e Merchant sono coerenti. "
                "Usano prodotti reali in azioni quotidiane plausibili, con clima locale e tono culturale sobrio. "
                "Per mercati non configurati o ad alto rischio, l'agente propone di sospendere il target invece di forzare traduzioni o immagini."
            ),
            "actions": ["open_photo_studio", "open_market_sense"],
        }

    if "foto" in lower or "fotografia" in lower or "cataloghi" in lower or "recension" in lower or "photo" in lower or "size guide" in lower or "curation" in lower:
        summary = snapshot.get("photo_studio", {}).get("summary", {})
        return {
            "reply": (
                f"Photo Studio: {summary.get('shot_types', 0)} tipi scatto, {summary.get('p0', 0)} P0, "
                f"{summary.get('ready', 0)} pronti da pianificare. "
                "Progressione tema: fiducia/prodotto reale, size guide e curation su ogni PDP, identita collezione, supporto conversione, poi campagne. Le recensioni si chiedono solo dopo esperienza reale e senza feedback finti."
            ),
            "actions": ["open_photo_studio", "open_theme"],
        }

    if "crm" in lower or "member" in lower or "area clienti" in lower or "wishlist" in lower or "loyalty" in lower or "welcome flow" in lower or "pdp" in lower:
        summary = growth_crm.get("summary", {})
        return {
            "reply": (
                f"Growth CRM: {summary.get('segments', 0)} segmenti, {summary.get('ready', 0)} elementi pronti, "
                f"{summary.get('attention', 0)} da controllare. "
                f"Priorita: {summary.get('primary_action', 'Fix PDP clarity and draft welcome flow before heavier CRM')}. "
                "Regola: niente over-engineering, niente urgenza finta; prima PDP chiara, immagini vere, welcome flow sobrio e member area via Shopify."
            ),
            "actions": ["open_growth_crm", "open_photo_studio"],
        }

    if "agent os" in lower or "connettori" in lower or "connessioni future" in lower or "architettura" in lower:
        summary = agent_os.get("summary", {})
        return {
            "reply": (
                f"Agent OS: {summary.get('ready', 0)} connettori ready, {summary.get('partial', 0)} parziali, "
                f"{summary.get('blocked', 0)} bloccati, {summary.get('planned', 0)} pianificati. "
                "Architettura: percezione, memoria, planner, registry connettori, approval gate, executor e osservabilita."
            ),
            "actions": ["open_agent_os", "open_api"],
        }

    if "open ai" in lower or "openai" in lower or "chatgpt" in lower or "alleata" in lower or "allinea" in lower:
        summary = openai_alliance.get("summary", {})
        return {
            "reply": (
                "OpenAI si allinea al progetto BKS, non il contrario. "
                "BKS resta la fonte: identita, serie/collezioni, catalogo, policy, Google trust, tono e approvazioni. "
                f"OpenAI Alliance: {summary.get('ready', 0)} capacita ready, {summary.get('partial', 0)} parziali, "
                f"Project {summary.get('project_link', 'env_pending')}, modello {summary.get('default_model', 'project_default')}. "
                "Uso OpenAI per ragionare, riassumere, scrivere bozze, controllare rischi e preparare output; non per cambiare direzione al brand. "
                "Canva e HyperFrames restano strumenti a valle: impaginano e animano cio che BKS ha gia deciso."
            ),
            "actions": ["open_openai_alliance", "open_agent_os"],
        }

    if "canva" in lower or "brand kit" in lower or "brand template" in lower or "autofill" in lower or "search designs" in lower:
        summary = canva.get("summary", {})
        return {
            "reply": (
                f"Canva Connector Agent: stato {summary.get('status', 'connector_available')}, "
                f"{summary.get('groups', 0)} gruppi strumenti, {summary.get('workflows', 0)} workflow. "
                "Sequenza corretta: Brand Kit o template BKS, dataset/autofill se ripetibile, generazione candidata se serve, review, resize, export. "
                "Salvataggi ufficiali, template pubblicati ed export campagna richiedono approvazione."
            ),
            "actions": ["open_canva_connectors", "open_social_campaigns"],
        }

    if "hyperframes" in lower or "motion" in lower or "explainer" in lower or "video html" in lower or "animated" in lower:
        summary = hyperframes.get("summary", {})
        return {
            "reply": (
                f"HyperFrames: stato {summary.get('status', 'connector_available')}, "
                f"{summary.get('tools', 0)} strumenti, formato default {summary.get('default_format', '1080x1920')}. "
                "Lo uso per trasformare storyboard HTML approvati in slide animate, explainer e motion graphics. "
                "HeyGen parla, HyperFrames visualizza; render solo dopo review e con metadata."
            ),
            "actions": ["open_hyperframes_connectors", "open_social_render"],
        }

    if "assistente" in lower and ("tema" in lower or "cliente" in lower or "fruitore" in lower or "shopify" in lower):
        summary = theme_assistant.get("summary", {})
        return {
            "reply": (
                f"Assistente AI nel tema: stato {summary.get('status', 'ready_for_theme')}, Google-safe {summary.get('google_safe', 'pass')}. "
                "Il widget e installabile ma disabilitato di default: risponde da Knowledge DB BKS, dichiara che e AI, non raccoglie pagamenti e rimanda a policy/checkout per prezzo, disponibilita, resi e spedizione."
            ),
            "actions": ["open_theme_assistant", "open_google_trust"],
        }

    if "bitcoin" in lower or "crypto" in lower or "pagament" in lower or "payment" in lower:
        summary = payments.get("summary", {})
        return {
            "reply": (
                f"Pagamenti: Bitcoin {summary.get('bitcoin', 'unknown')}, provider {summary.get('provider', '')}. "
                "Lo tratto come competenza bakabo-bitcoin-payments: asso moderno per vendite internazionali, ma solo come opzione checkout chiara. "
                "Mai come investimento, sconto garantito o promessa finanziaria."
            ),
            "actions": ["open_payments", "open_agent_os"],
        }

    if any(token in lower for token in ("connession", "conness", "api", "youtube", "heygen")):
        lines = ["Connessioni principali:"]
        for name in ("heygen", "youtube", "make", "openai", "shopify", "printify", "google_merchant", "image_factory"):
            if name in services:
                lines.append(f"- {name}: {_connection_label(services[name])}")
        return {"reply": "\n".join(lines), "actions": ["live_health", "social_render"]}

    if "cliente" in lower or "customer" in lower or "consenso" in lower:
        return {
            "reply": (
                "Modalita Customer Concierge: possibile, ma solo con opt-in esplicito del cliente. "
                "L'agente puo rispondere su prodotto, taglie, tempi, policy e stato generale; non deve raccogliere pagamenti, password o dati sensibili fuori dai flussi autorizzati."
            ),
            "actions": ["open_agent", "open_api"],
        }

    if "posta" in lower or "crew@" in lower or "crew@bakabo.club" in lower or "email ufficial" in lower or "mail ufficial" in lower:
        summary = official_inbox.get("summary", {})
        return {
            "reply": (
                f"Official Inbox: {summary.get('official_email', 'crew@bakabo.club')} in modalita {summary.get('status', 'ready_for_drafts')}. "
                f"{summary.get('configured', 0)} blocchi configurati, {summary.get('needs_attention', 0)} da completare. "
                "L'agente classifica messaggi, prepara bozze multilingua, registra segnali in Knowledge DB e chiede review per reclami, privacy, pagamenti, legal e marketing."
            ),
            "actions": ["open_official_inbox", "open_knowledge_db"],
        }

    if "garanz" in lower or "legisl" in lower or "legale" in lower or "fornitor" in lower or "produttor" in lower or "supplier" in lower:
        summary = legal_guardrails.get("summary", {})
        return {
            "reply": (
                f"Legal Guardrails: cliente {summary.get('customer_pass', 0)} pass / {summary.get('customer_needs', 0)} da verificare; "
                f"fornitori attivi {summary.get('supplier_active', 0)} con review contrattuale. "
                "Regola: i diritti del cliente restano centrali; sicurezza prodotto, privacy, pagamenti, reclami e rapporti produttori/fornitori richiedono prova e revisione umana."
            ),
            "actions": ["open_legal_guardrails", "open_official_inbox"],
        }

    if any(token in lower for token in ("pinterest", "amazon merch", "merch on demand", "social hub", "marketplace hub", "telegram bot", "bot telegram", "pin board")):
        sales = sales_channels.get("rows", []) if isinstance(sales_channels, dict) else []
        pin_status = next((row.get("status") for row in sales if row.get("status_key") == "pinterest" or row.get("channel") == "Pinterest Catalog"), "unknown")
        amzn_status = next((row.get("status") for row in sales if row.get("channel") == "Amazon Merch on Demand"), "unknown")
        tg_status = next((row.get("status") for row in sales if row.get("channel") == "Telegram Bot"), "unknown")
        return {
            "reply": (
                "Social & Marketplace Hub (pagina 03, Streamlit porta 8501): Facebook, Instagram, Pinterest, Amazon Merch on Demand, Telegram bot e TikTok gestiti da un'unica interfaccia. "
                f"Pinterest: {pin_status} — 9 board mappate sulle collezioni BKS, check titolo<=60 e descrizione 150-160 char per Rich Pin SEO. "
                f"Amazon: {amzn_status} — e Merch on Demand (non Seller Central): carico design via merch.amazon.com, traccio ASIN/tier/royalty in output/social/amazon_merch_designs.csv. "
                f"Telegram: {tg_status} — bot diretto con invio messaggi, template drop/restock/promo e storico in output/social/telegram_history.json. "
                "Ogni link passa da build_utm() per GA4 (bakabo-9a8c5/483501489) e GTM (GTM-PF5Z85KS). Pubblicazione effettiva richiede sempre conferma."
            ),
            "actions": ["open_social_hub", "open_sales_channels"],
        }

    if "messaggi" in lower or "email" in lower or "instagram" in lower or "telegram" in lower or "bot" in lower:
        summary = communications.get("summary", {})
        return {
            "reply": (
                f"Communications: {summary.get('configured', 0)} canali configurati, "
                f"{summary.get('missing', 0)} mancanti, {summary.get('planned', 0)} pianificati. "
                "Email, Instagram DM e Telegram Bot richiedono consenso esplicito prima delle automazioni cliente."
            ),
            "actions": ["open_communications"],
        }

    if "campagne" in lower or "multiling" in lower or "lingue" in lower or "tutte le lingue" in lower or "social autonome" in lower:
        summary = social_campaigns.get("summary", {})
        return {
            "reply": (
                f"Social Campaigns: {summary.get('channels', 0)} canali, {summary.get('languages', 0)} lingue, "
                f"{summary.get('ready', 0)} pronti a draft, {summary.get('partial', 0)} parziali. "
                "L'agente puo preparare campagne multilingua su social, email e community; pubblicazione/ad spend restano supervisionati finche trust, consenso e API non sono verdi."
            ),
            "actions": ["open_social_campaigns", "open_marketing_logic"],
        }

    if "canali" in lower or "vendita" in lower or "marketplace" in lower or "shop" in lower:
        summary = sales_channels.get("summary", {})
        return {
            "reply": (
                f"Canali di vendita: {summary.get('active', 0)} attivi, "
                f"{summary.get('partial', 0)} parziali, {summary.get('planned', 0)} pianificati, "
                f"{summary.get('missing', 0)} da configurare. Shopify resta primario; Meta/Instagram, Google Merchant e YouTube Shopping sono i prossimi canali ad alto impatto."
            ),
            "actions": ["open_sales_channels"],
        }

    if "spot" in lower or "uomo" in lower or "donna" in lower or "direttive" in lower:
        return {
            "reply": (
                "Modalita Production Director: posso preparare direttive per spot uomo, spot donna o avatar neutro. "
                "Input minimo: collection, pubblico, canale, durata, CTA e immagine hero. Output: script, scaletta, visual direction e dati Social Render."
            ),
            "actions": ["open_avatar", "open_social_render"],
        }

    if "skill" in lower or "claude" in lower or "cloude" in lower:
        summary = skills.get("summary", {})
        return {
            "reply": (
                f"Skill registry: {summary.get('active', 0)} skill attive, "
                f"{summary.get('missing', 0)} referenze mancanti. "
                "Salva nuove skill in BKS_SKILL/skills/<nome>/SKILL.md e poi chiedimi di aggiornare la fase 10."
            ),
            "actions": ["run fase 10", "open_skills"],
        }

    if "social" in lower or "render" in lower or "youtube" in lower:
        rows = social.get("rows", [])
        ready_social = sum(1 for row in rows if row.get("render_status") == "ready_for_social")
        ready_heygen = sum(1 for row in rows if row.get("render_status") == "ready_for_heygen")
        return {
            "reply": (
                f"Scheda Social Render: {len(rows)} collection, {ready_social} pronte alla pubblicazione, "
                f"{ready_heygen} pronte per HeyGen. Canali inclusi: Instagram Reels, TikTok, YouTube Shorts, Homepage, Email."
            ),
            "actions": ["open_social_render", "run fase 09"],
        }

    if "avatar" in lower or "heygen" in lower:
        summary = avatar.get("summary", {})
        return {
            "reply": (
                f"Avatar Production: script {summary.get('scripts_ready', 0)}/{summary.get('collections', 0)}, "
                f"immagini selezionate {summary.get('images_ready', 0)}/{summary.get('collections', 0)}, "
                f"export {summary.get('exports_ready', 0)}/{summary.get('collections', 0)}. "
                "Il prossimo passo operativo e selezionare/croppare le immagini 9:16."
            ),
            "actions": ["open_avatar", "run fase 09"],
        }

    if "fase" in lower or "stato" in lower or "avanzamento" in lower:
        lines = ["Stato fasi operative:"]
        lines.extend(f"- {_phase_line(phase)}" for phase in phases)
        return {"reply": "\n".join(lines), "actions": ["open_phases"]}

    if "origin" in lower or "folklore" in lower or "collezioni" in lower or "collezione" in lower:
        return {
            "reply": (
                f"BKS ha 8 collezioni: {', '.join(BKS_COLLECTIONS)}. "
                "Non esiste 'Folklore' — la collezione e Origin. "
                "Ogni collezione ha il proprio accent color (vedi COLLECTION_ACCENTS in avatar_production.py). "
                "Origin: toni naturali, materiali onesti, stampe made-to-order. Accent #489808."
            ),
            "actions": ["open_avatar", "open_social_render"],
        }

    if any(t in lower for t in ("database", "bks_db", "sqlite", "archivio", "tabelle", "query")):
        try:
            from ecommerce_automation.bks_db import bks_db
            tables = bks_db.list_tables()
            cat = {r["table_name"]: r["row_count"] for r in bks_db.catalog()}
            top = sorted(cat.items(), key=lambda x: -x[1])[:5]
            top_str = ", ".join(f"{t}({r})" for t, r in top)
        except Exception as e:
            tables, top_str = [], str(e)
        return {
            "reply": (
                f"BKS Database: {len(tables)} tabelle SQLite in output/bks_database.sqlite. "
                f"Tabelle piu popolate: {top_str}. "
                "Accesso via: from ecommerce_automation.bks_db import bks_db; bks_db.query('SELECT ...'); "
                "bks_db.rebuild() per aggiornare da CSV/JSON sorgente. "
                "L'archivio output/99_ARCHIVIO contiene log, report stale e run batch archiviati."
            ),
            "actions": ["open_bks_db"],
        }

    if any(t in lower for t in ("algoritmo", "algorithm", "score", "priorità", "priority", "scoring", "gate", "tier", "p0", "p1", "p2", "p3", "control center")):
        try:
            from ecommerce_automation.bks_algorithm import BKSAlgorithm
            algo = BKSAlgorithm()
            s = algo.summary()
            health = algo.collection_health()
            critical_colls = [h.handle for h in health if h.status in ("critical", "empty")]
        except Exception as e:
            s, critical_colls = {"total": 0}, []
        return {
            "reply": (
                f"BKS Algorithm: {s.get('total',0)} prodotti analizzati — "
                f"score medio {s.get('avg_score',0)}, "
                f"P3 ready: {s.get('ready',0)}, P0 critical: {s.get('critical',0)}. "
                f"Collezioni da curare: {', '.join(critical_colls) if critical_colls else 'nessuna'}. "
                "Pannello: pages/00_BKS_Algorithm.py — scoring, coda priorità, gate pubblicazione. "
                "API: from ecommerce_automation.bks_algorithm import bks_algorithm; bks_algorithm.priority_queue()"
            ),
            "actions": ["open_algorithm", "open_bks_db"],
        }

    if "session" in lower or "aggiornamento" in lower or "cosa e cambiato" in lower or "novita" in lower:
        return {
            "reply": (
                f"Changelog BKS TM04 — ultima versione: {BKS_LAST_DEPLOY}\n"
                + "\n".join(f"- {v}: {desc}" for v, desc in SESSION_CHANGES.items())
            ),
            "actions": ["open_skills", "open_theme"],
        }

    return {
        "reply": (
            "Sono l'Agente Master BKS. Posso leggere stato fasi, connessioni, Avatar Production, Social Render e Skill Registry. "
            "Comandi utili: `stato fasi`, `connessioni`, `stato avatar`, `stato social`, `skill`, `run fase 09`, `run fase 10`."
        ),
        "actions": ["open_phases", "open_avatar", "open_social_render"],
    }
