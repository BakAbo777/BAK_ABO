from __future__ import annotations

from typing import Any


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

    if "nomi prodotti" in lower or "nome prodotto" in lower or "titoli prodotti" in lower or "titolo prodotto" in lower or "sbgliati" in lower or "sbagliati" in lower:
        summary = product_names.get("summary", {})
        return {
            "reply": (
                f"Product Name Audit: sorgente {summary.get('source', 'active_csv')}, {summary.get('products', 0)} prodotti controllati, "
                f"{summary.get('needs_fix', 0)} da correggere e {summary.get('needs_review', 0)} da verificare. "
                "Priorita: correggere titoli mancanti/refusi/draft word e poi controllare mismatch handle-titolo prima di feed Google o campagne."
            ),
            "actions": ["open_product_name_audit", "open_catalog_sync"],
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

    if "google" in lower or "merchant" in lower or "fuorviant" in lower or "sospes" in lower or "analytics" in lower or "gtm" in lower or "ga4" in lower or "tag" in lower:
        summary = google.get("summary", {})
        tag_summary = google.get("tag_summary", {})
        return {
            "reply": (
                f"Google Merchant: stato {summary.get('status', 'unknown')}, motivo {summary.get('reason', 'unknown')}, "
                f"P0 blocker {summary.get('blockers', 0)}. "
                f"GTM {tag_summary.get('expected_gtm_percent', 0)}%, GA4 {tag_summary.get('ga4_percent', 0)}%. "
                "Per rappresentazione ingannevole la priorita e: pagine fiducia, feed prodotti disponibili, claim sobri, poi ricorso."
            ),
            "actions": ["open_google", "open_master_actions"],
        }

    if "mercato" in lower or "market" in lower or "adatta" in lower or "evoluzione" in lower:
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

    if "timer" in lower or "offerta" in lower or "marketing" in lower or "countdown" in lower:
        summary = marketing.get("summary", {})
        return {
            "reply": (
                f"Timer marketing: stato {summary.get('status', 'draft')}, compliance {summary.get('compliance', 'unknown')}. "
                "Lo uso solo con scadenza reale, termini visibili e nessuna promessa di sconto se il codice Shopify non e configurato."
            ),
            "actions": ["open_marketing", "open_theme"],
        }

    if "tema" in lower or "theme" in lower or "scuro" in lower or "tenebroso" in lower:
        summary = theme.get("summary", {})
        return {
            "reply": (
                f"Tema: patch {summary.get('status', 'unknown')} per {summary.get('goal', 'lighter_commerce_trust_theme')}. "
                f"Zip pronto: {summary.get('output_zip', 'non ancora generato')}. Procediamo con cambi piccoli: leggibilita, trust strip, timer sobrio."
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

    if "foto" in lower or "fotografia" in lower or "cataloghi" in lower or "recension" in lower or "photo" in lower:
        summary = snapshot.get("photo_studio", {}).get("summary", {})
        return {
            "reply": (
                f"Photo Studio: {summary.get('shot_types', 0)} tipi scatto, {summary.get('p0', 0)} P0, "
                f"{summary.get('ready', 0)} pronti da pianificare. "
                "Progressione tema: fiducia/prodotto reale, identita collezione, supporto conversione, poi campagne. Le recensioni si chiedono solo dopo esperienza reale e senza feedback finti."
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
                "Salva nuove skill come docs/nome_SKILL.md e poi chiedimi di aggiornare la fase 10."
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

    return {
        "reply": (
            "Sono l'Agente Master BKS. Posso leggere stato fasi, connessioni, Avatar Production, Social Render e Skill Registry. "
            "Comandi utili: `stato fasi`, `connessioni`, `stato avatar`, `stato social`, `skill`, `run fase 09`, `run fase 10`."
        ),
        "actions": ["open_phases", "open_avatar", "open_social_render"],
    }
