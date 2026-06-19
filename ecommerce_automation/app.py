from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import socket
import re
from flask import Flask, abort, jsonify, render_template, request, send_file

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ecommerce_automation.config import settings
from ecommerce_automation.core.agent_knowledge import AgentKnowledgeStore
from ecommerce_automation.core.external_references import ExternalReferenceStore
from ecommerce_automation.core.logger import configure_logging
from ecommerce_automation.core.orchestrator import Orchestrator
from ecommerce_automation.core.run_ledger import RunLedger
from ecommerce_automation.core.state_manager import StateManager
from ecommerce_automation.core.websocket_handler import RealtimeHub
from ecommerce_automation.phases import get_runner
from ecommerce_automation.services.amazon_client import AmazonClient
from ecommerce_automation.services.make_webhook_handler import MakeWebhookHandler
from ecommerce_automation.services.openai_service import OpenAIService
from ecommerce_automation.services.printify_client import PrintifyClient
from ecommerce_automation.services.shopify_client import ShopifyClient
from ecommerce_automation.avatar_production import ensure_workspace, payload as avatar_payload
from ecommerce_automation.api_orchestrator import write_matrix as api_orchestration_matrix
from ecommerce_automation.agent_os import payload as agent_os_payload
from ecommerce_automation.agent_routine import payload as agent_routine_payload
from ecommerce_automation.always_on_agent import payload as always_on_payload
from ecommerce_automation.canva_connectors import payload as canva_connectors_payload
from ecommerce_automation.catalog_db import payload as catalog_db_payload
from ecommerce_automation.catalog_live_sync import payload as catalog_live_sync_payload
from ecommerce_automation.communications import payload as communications_payload
from ecommerce_automation.daily_web_update import payload as daily_web_update_payload, run as run_daily_web_update
from ecommerce_automation.dialogic_agent import payload as dialogic_agent_payload
from ecommerce_automation.google_merchant_monitor import payload as google_merchant_payload
from ecommerce_automation.google_trust_contract import payload as google_trust_payload
from ecommerce_automation.growth_crm import payload as growth_crm_payload
from ecommerce_automation.hyperframes_connectors import payload as hyperframes_connectors_payload
from ecommerce_automation.marketing_offers import payload as marketing_offer_payload
from ecommerce_automation.marketing_logic_scout import payload as marketing_logic_payload
from ecommerce_automation.market_sense import payload as market_sense_payload
from ecommerce_automation.master_actions import payload as master_actions_payload, verify as verify_master_action
from ecommerce_automation.master_agent import AGENT_MODES, AGENT_PROFILE, reply as agent_reply
from ecommerce_automation.member_tryon import handle_submission as member_tryon_submit, payload as member_tryon_payload
from ecommerce_automation.network_monitor import payload as network_monitor_payload
from ecommerce_automation.legal_guardrails import payload as legal_guardrails_payload
from ecommerce_automation.official_inbox import payload as official_inbox_payload
from ecommerce_automation.openai_alliance import payload as openai_alliance_payload
from ecommerce_automation.payments import payload as payments_payload
from ecommerce_automation.photo_studio import payload as photo_studio_payload
from ecommerce_automation.product_name_audit import payload as product_name_audit_payload
from ecommerce_automation.realtime_control import payload as realtime_control_payload
from ecommerce_automation.sales_channels import payload as sales_channels_payload
from ecommerce_automation.skill_registry import payload as skills_payload
from ecommerce_automation.social_campaigns import payload as social_campaigns_payload
from ecommerce_automation.theme_ai_assistant import customer_reply as theme_customer_reply
from ecommerce_automation.theme_ai_assistant import payload as theme_ai_assistant_payload
from ecommerce_automation.theme_optimizer import payload as theme_optimizer_payload
from ecommerce_automation.turbobak_engine import payload as turbobak_payload
from ecommerce_automation.weekly_goals import payload as weekly_goals_payload
from bks_assets import active_catalog_csv


def build_services() -> dict[str, Any]:
    return {
        "amazon": AmazonClient(
            seller_id=settings.amazon_seller_id,
            sp_api_client_id=settings.amazon_sp_api_client_id,
            merch_email=settings.amazon_merch_email,
            merch_tier=settings.amazon_merch_tier,
        ),
        "make": MakeWebhookHandler(settings.make_webhook_url, settings.make_webhook_secret),
        "openai": OpenAIService(
            api_key=settings.openai_api_key,
            project_id=settings.openai_project_id,
            organization_id=settings.openai_organization_id,
            chatgpt_project_url=settings.openai_chatgpt_project_url,
            vector_store_id=settings.openai_vector_store_id,
            default_model=settings.openai_default_model,
        ),
        "printify": PrintifyClient(settings.printify_api_token, settings.printify_shop_id),
        "shopify": ShopifyClient(settings.shopify_store, settings.shopify_admin_token, settings.shopify_api_version),
    }


def heygen_health() -> dict[str, Any]:
    key_ready = bool(settings.heygen_api_key)
    render_profile_ready = key_ready and bool(settings.heygen_avatar_id) and bool(settings.heygen_voice_id)
    return {
        "configured": key_ready,
        "render_profile_ready": render_profile_ready,
        "status": "render_ready" if render_profile_ready else ("key_ready" if key_ready else "missing_key"),
        "key_env": "HEYGEN_API_KEY",
        "avatar_env": "HEYGEN_AVATAR_ID",
        "voice_env": "HEYGEN_VOICE_ID",
        "avatar_id_set": bool(settings.heygen_avatar_id),
        "voice_id_set": bool(settings.heygen_voice_id),
        "console": "https://app.heygen.com/developers/api",
    }


def youtube_health() -> dict[str, Any]:
    required = {
        "YOUTUBE_CHANNEL_ID": bool(settings.youtube_channel_id),
        "YOUTUBE_CLIENT_ID": bool(settings.youtube_client_id),
        "YOUTUBE_CLIENT_SECRET": bool(settings.youtube_client_secret),
        "YOUTUBE_REFRESH_TOKEN": bool(settings.youtube_refresh_token),
    }
    configured = all(required.values())
    return {
        "configured": configured,
        "status": "configured" if configured else "missing_oauth",
        "required": required,
        "format": "YouTube Shorts 9:16",
    }


def local_port_open(port: int, host: str = "127.0.0.1") -> bool:
    try:
        with socket.create_connection((host, port), timeout=1.0):
            return True
    except OSError:
        return False


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.secret_key
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
    logger = configure_logging(settings.package_dir / "logs")
    state = StateManager(settings.database_path)
    ledger = RunLedger(settings.database_path)
    knowledge = AgentKnowledgeStore(settings.database_path)
    references = ExternalReferenceStore(settings.database_path)
    realtime = RealtimeHub()

    def context() -> dict[str, Any]:
        return {
            "settings": settings,
            "services": build_services(),
            "state": state,
            "ledger": ledger,
            "knowledge": knowledge,
            "references": references,
            "realtime": realtime,
        }

    orchestrator = Orchestrator(state=state, ledger=ledger, context_factory=context)

    def services_snapshot() -> dict[str, Any]:
        services = build_services()
        return {
            "make": services["make"].health_snapshot(),
            "openai": services["openai"].health(),
            "openai_project": {
                "configured": bool(settings.openai_project_id or settings.openai_chatgpt_project_url),
                "status": "project_ready" if settings.openai_project_id or settings.openai_chatgpt_project_url else "env_pending",
            },
            "canva": {
                "configured": bool(settings.canva_api_key),
                "status": "configured" if settings.canva_api_key else "connector_available",
            },
            "hyperframes": {
                "configured": bool(settings.hyperframes_api_key or settings.hyperframes_project_id),
                "status": "configured" if settings.hyperframes_api_key or settings.hyperframes_project_id else "connector_available",
            },
            "heygen": heygen_health(),
            "youtube": youtube_health(),
            "meta": {
                "configured": bool(settings.meta_access_token and (settings.instagram_business_id or settings.facebook_page_id)),
                "status": "configured" if settings.meta_access_token and (settings.instagram_business_id or settings.facebook_page_id) else "missing_meta",
            },
            "telegram": {
                "configured": bool(settings.telegram_bot_token and (settings.telegram_bot_username or settings.telegram_bot_url)),
                "status": "configured" if settings.telegram_bot_token and (settings.telegram_bot_username or settings.telegram_bot_url) else "missing_bot",
            },
            "email": {
                "configured": bool(settings.support_email and settings.smtp_host),
                "status": "configured" if settings.support_email and settings.smtp_host else "missing_smtp",
            },
            "google_merchant": {
                "configured": bool(settings.google_merchant_id),
                "status": settings.google_merchant_status if settings.google_merchant_id else "missing_merchant_id",
                "reason": settings.google_merchant_reason,
            },
            "tiktok_shop": {
                "configured": bool(settings.tiktok_shop_id),
                "status": "configured" if settings.tiktok_shop_id else "missing_shop_id",
            },
            "pinterest": {
                "configured": bool(settings.pinterest_business_id),
                "status": "configured" if settings.pinterest_business_id else "missing_business_id",
            },
            "etsy": {
                "configured": bool(settings.etsy_shop_id),
                "status": "configured" if settings.etsy_shop_id else "missing_shop_id",
            },
            "ebay": {
                "configured": bool(settings.ebay_seller_id),
                "status": "configured" if settings.ebay_seller_id else "missing_seller_id",
            },
            "image_factory": {
                "configured": settings.image_factory_dir.exists(),
                "status": "online" if local_port_open(8503) else "offline",
                "url": settings.image_factory_url,
            },
            "amazon": services["amazon"].health(),
            "printify": {
                "configured": services["printify"].configured,
                "status": "configured" if services["printify"].configured else "missing_token",
            },
            "shopify": services["shopify"].health_snapshot(live=False),
        }

    @app.after_request
    def add_no_cache_headers(response):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    @app.get("/")
    def dashboard():
        return render_template("dashboard.html", app_name=settings.app_name)

    @app.get("/phase/<phase_id>")
    def phase_detail(phase_id: str):
        return render_template("phase_detail.html", phase_id=phase_id, app_name=settings.app_name)

    @app.get("/api/health")
    def api_health():
        services = build_services()
        return jsonify(
            {
                "app": settings.app_name,
                "database": str(settings.database_path),
                "services": {
                "make": services["make"].configured,
                "openai": services["openai"].configured,
                "heygen": bool(settings.heygen_api_key),
                "youtube": youtube_health()["configured"],
                "image_factory": local_port_open(8503),
                "printify": services["printify"].configured,
                "shopify": services["shopify"].configured,
                "amazon": services["amazon"].configured,
                },
            }
        )

    @app.get("/api/services/health")
    def api_services_health():
        live = request.args.get("live") == "1"
        services = build_services()
        def safe_snapshot(name: str, callback):
            try:
                return callback()
            except Exception as exc:  # noqa: BLE001
                logger.warning("Service health failed for %s: %s", name, exc)
                return {"configured": True, "status": "error", "error": f"{type(exc).__name__}: {exc}"}

        snapshots: dict[str, Any] = {
            "make": services["make"].health_snapshot(),
            "openai": services["openai"].health(),
            "openai_project": {
                "configured": bool(settings.openai_project_id or settings.openai_chatgpt_project_url),
                "status": "project_ready" if settings.openai_project_id or settings.openai_chatgpt_project_url else "env_pending",
            },
            "canva": {
                "configured": bool(settings.canva_api_key),
                "status": "configured" if settings.canva_api_key else "connector_available",
            },
            "hyperframes": {
                "configured": bool(settings.hyperframes_api_key or settings.hyperframes_project_id),
                "status": "configured" if settings.hyperframes_api_key or settings.hyperframes_project_id else "connector_available",
            },
            "heygen": heygen_health(),
            "youtube": youtube_health(),
            "image_factory": {
                "configured": settings.image_factory_dir.exists(),
                "status": "online" if local_port_open(8503) else "offline",
                "url": settings.image_factory_url,
            },
            "amazon": services["amazon"].health(),
        }
        snapshots["shopify"] = safe_snapshot("shopify", lambda: services["shopify"].health_snapshot(live=live))
        if services["printify"].configured and live:
            snapshots["printify"] = safe_snapshot("printify", lambda: services["printify"].health_snapshot(settings.printify_shop_title))
        else:
            snapshots["printify"] = {
                "configured": services["printify"].configured,
                "status": "configured" if services["printify"].configured else "missing_token",
            }
        return jsonify({"live": live, "services": snapshots})

    @app.post("/api/agent/chat")
    def api_agent_chat():
        payload = request.get_json(silent=True) or {}
        message = str(payload.get("message", "")).strip()
        run_match = re.search(r"(?:run|avvia|esegui|aggiorna)\s+(?:fase\s*)?(\d{1,2})", message.lower())
        if run_match:
            phase_id = run_match.group(1).zfill(2)
            try:
                runner = get_runner(phase_id)
                result = orchestrator.run_phase(phase_id, runner, intent="agent", payload={"message": message})
                realtime.publish("phase.updated", result["phase"])
                state.record_event("agent.chat", phase_id=phase_id, payload={"message": message, "action": "run_phase"})
                return jsonify(
                    {
                        "reply": f"Fase {phase_id} eseguita. Stato: {result['phase']['status']}. {result['phase'].get('message', '')}",
                        "actions": ["open_phases"],
                        "result": result,
                    }
                )
            except KeyError:
                return jsonify({"reply": f"Non trovo la fase {phase_id}.", "actions": ["open_phases"]}), 404

        avatar_data = avatar_payload(settings.root_dir)
        google_data = google_merchant_payload(settings)
        marketing_data = marketing_offer_payload(settings)
        theme_data = theme_optimizer_payload(settings)
        turbobak_data = turbobak_payload(settings)
        agent_os_data = agent_os_payload(settings)
        openai_alliance_data = openai_alliance_payload(settings)
        canva_data = canva_connectors_payload(settings)
        hyperframes_data = hyperframes_connectors_payload(settings)
        payments_data = payments_payload(settings)
        network_data = network_monitor_payload(settings)
        catalog_sync_data = catalog_live_sync_payload(settings, build_services(), references, live=False)
        catalog_db_data = catalog_db_payload(settings)
        member_tryon_data = member_tryon_payload(settings)
        product_names_data = product_name_audit_payload(settings)
        official_inbox_data = official_inbox_payload(settings)
        theme_assistant_data = theme_ai_assistant_payload(settings)
        trust_data = google_trust_payload(
            settings,
            {
                "google": google_data,
                "marketing": marketing_data,
                "payments": payments_data,
                "official_inbox": official_inbox_data,
                "network": network_data,
            },
        )
        legal_data = legal_guardrails_payload(
            settings,
            {
                "google": google_data,
                "trust": trust_data,
                "payments": payments_data,
                "official_inbox": official_inbox_data,
                "network": network_data,
            },
        )
        social_campaigns_data = social_campaigns_payload(
            settings,
            {"google": google_data, "trust": trust_data, "marketing": marketing_data},
        )
        growth_crm_data = growth_crm_payload(
            settings,
            {"google": google_data, "trust": trust_data, "official_inbox": official_inbox_data},
        )
        photo_studio_data = photo_studio_payload(
            settings,
            {"google": google_data, "theme": theme_data, "trust": trust_data, "growth_crm": growth_crm_data},
        )
        marketing_logic_data = marketing_logic_payload(
            settings,
            {
                "google": google_data,
                "marketing": marketing_data,
                "payments": payments_data,
                "trust": trust_data,
                "avatar": avatar_data,
                "social_campaigns": social_campaigns_data,
                "legal_guardrails": legal_data,
                "theme_assistant": theme_assistant_data,
                "openai_alliance": openai_alliance_data,
                "canva": canva_data,
                "hyperframes": hyperframes_data,
            },
        )
        market_data = market_sense_payload(
            settings,
            {
                "google": google_data,
                "marketing": marketing_data,
                "theme": theme_data,
                "turbobak": turbobak_data,
                "sales_channels": sales_channels_payload(settings),
                "avatar": avatar_data,
                "agent_os": agent_os_data,
                "openai_alliance": openai_alliance_data,
                "canva": canva_data,
                "hyperframes": hyperframes_data,
                "payments": payments_data,
                "network": network_data,
                "catalog_sync": catalog_sync_data,
                "product_names": product_names_data,
                "trust": trust_data,
                "marketing_logic": marketing_logic_data,
                "official_inbox": official_inbox_data,
                "social_campaigns": social_campaigns_data,
                "legal_guardrails": legal_data,
                "growth_crm": growth_crm_data,
                "photo_studio": photo_studio_data,
                "theme_assistant": theme_assistant_data,
                "openai_alliance": openai_alliance_data,
                "canva": canva_data,
                "hyperframes": hyperframes_data,
            },
        )
        actions_data = master_actions_payload(
            settings,
            {
                "google": google_data,
                "marketing": marketing_data,
                "theme": theme_data,
                "turbobak": turbobak_data,
                "market": market_data,
                "trust": trust_data,
                "network": network_data,
                "catalog_sync": catalog_sync_data,
                "product_names": product_names_data,
                "official_inbox": official_inbox_data,
                "social_campaigns": social_campaigns_data,
                "legal_guardrails": legal_data,
                "growth_crm": growth_crm_data,
                "photo_studio": photo_studio_data,
                "theme_assistant": theme_assistant_data,
                "openai_alliance": openai_alliance_data,
                "canva": canva_data,
                "hyperframes": hyperframes_data,
            },
        )
        weekly_data = weekly_goals_payload(
            settings,
            {
                "google": google_data,
                "marketing": marketing_data,
                "theme": theme_data,
                "market": market_data,
                "actions": actions_data,
                "network": network_data,
                "growth_crm": growth_crm_data,
                "catalog_sync": catalog_sync_data,
                "product_names": product_names_data,
            },
        )
        snapshot = {
            "phases": state.list_phases(),
            "services": services_snapshot(),
            "avatar": avatar_data,
            "social": {"rows": avatar_data["social_render"], "sheet": avatar_data["social_render_sheet"]},
            "skills": skills_payload(settings.root_dir),
            "communications": communications_payload(settings),
            "sales_channels": sales_channels_payload(settings),
            "google": google_data,
            "marketing": marketing_data,
            "theme": theme_data,
            "turbobak": turbobak_data,
            "agent_os": agent_os_data,
            "openai_alliance": openai_alliance_data,
            "canva": canva_data,
            "hyperframes": hyperframes_data,
            "payments": payments_data,
            "network": network_data,
            "catalog_sync": catalog_sync_data,
            "catalog": catalog_db_data,
            "member_tryon": member_tryon_data,
            "product_names": product_names_data,
            "official_inbox": official_inbox_data,
            "social_campaigns": social_campaigns_data,
            "legal_guardrails": legal_data,
            "growth_crm": growth_crm_data,
            "photo_studio": photo_studio_data,
            "theme_assistant": theme_assistant_data,
            "trust": trust_data,
            "marketing_logic": marketing_logic_data,
            "market": market_data,
            "actions": actions_data,
            "weekly": weekly_data,
            "daily": daily_web_update_payload(
                settings,
                {
                    "actions": actions_data,
                    "market": market_data,
                    "weekly": weekly_data,
                    "network": network_data,
                    "catalog_sync": catalog_sync_data,
                },
            ),
        }
        snapshot["routine"] = agent_routine_payload(settings, snapshot)
        snapshot["always_on"] = always_on_payload(settings, snapshot)
        snapshot["dialogic"] = dialogic_agent_payload(settings)
        knowledge.seed_from_snapshot(snapshot)
        answer = agent_reply(message, snapshot)
        knowledge.add(
            area="chat",
            title=message[:120] or "agent chat",
            status="answered",
            evidence=answer.get("reply", "")[:1000],
            source="dashboard_agent",
            payload={"message": message, "answer": answer},
        )
        state.record_event("agent.chat", payload={"message": message, "actions": answer.get("actions", [])})
        return jsonify(answer)

    @app.get("/api/agent/profile")
    def api_agent_profile():
        profile = dict(AGENT_PROFILE)
        profile["heygen_key_ready"] = bool(settings.heygen_api_key)
        profile["heygen_avatar_ready"] = bool(settings.heygen_avatar_id)
        profile["heygen_voice_ready"] = bool(settings.heygen_voice_id)
        profile["status"] = "avatar_ready" if profile["heygen_avatar_ready"] and profile["heygen_voice_ready"] else "avatar_profile_pending"
        profile["modes"] = list(AGENT_MODES)
        return jsonify(profile)

    @app.get("/api/orchestration")
    def api_orchestration():
        return jsonify(api_orchestration_matrix(settings.root_dir, services_snapshot()))

    @app.get("/api/communications")
    def api_communications():
        return jsonify(communications_payload(settings))

    @app.get("/api/sales-channels")
    def api_sales_channels():
        return jsonify(sales_channels_payload(settings))

    @app.get("/api/google-merchant")
    def api_google_merchant():
        return jsonify(google_merchant_payload(settings))

    @app.get("/api/marketing-offers")
    def api_marketing_offers():
        return jsonify(marketing_offer_payload(settings))

    @app.get("/api/marketing-logic")
    def api_marketing_logic():
        return jsonify(action_snapshot()["marketing_logic"])

    @app.get("/api/theme-ai-assistant")
    def api_theme_ai_assistant():
        return jsonify(action_snapshot()["theme_assistant"])

    @app.get("/api/network-monitor")
    def api_network_monitor():
        return jsonify(network_monitor_payload(settings, live=request.args.get("live") == "1"))

    @app.get("/api/catalog-live-sync")
    def api_catalog_live_sync():
        return jsonify(catalog_live_sync_payload(settings, build_services(), references, live=request.args.get("live") == "1"))

    @app.get("/api/product-name-audit")
    def api_product_name_audit():
        return jsonify(product_name_audit_payload(settings, live=request.args.get("live") == "1"))

    @app.post("/api/catalog-live-sync/run")
    def api_catalog_live_sync_run():
        result = catalog_live_sync_payload(settings, build_services(), references, live=True)
        summary = result.get("summary", {})
        knowledge.add(
            area="catalog_sync",
            title="Shopify/Printify live catalog sync",
            status=summary.get("status", ""),
            evidence=json.dumps(summary, ensure_ascii=False, sort_keys=True)[:1000],
            source="catalog_live_sync",
            payload=summary,
        )
        state.record_event("catalog_live_sync.run", payload=summary)
        realtime.publish("catalog_live_sync.run", summary)
        return jsonify(result)

    @app.post("/api/customer-assistant")
    def api_customer_assistant():
        token = request.headers.get("X-BKS-Assistant-Token", "")
        if settings.bks_assistant_public_token and token != settings.bks_assistant_public_token:
            return jsonify({"error": "unauthorized"}), 401
        payload = request.get_json(silent=True) or {}
        message      = str(payload.get("message", "")).strip()
        page_url     = str(payload.get("page_url", ""))
        product_title= str(payload.get("product_title", ""))
        rows = knowledge.latest(limit=25)
        answer = theme_customer_reply(message, rows, settings, page_url=page_url, product_title=product_title)
        knowledge.add(
            area="customer_assistant",
            title=message[:120] or "customer assistant",
            status="answered",
            evidence=answer.get("reply", "")[:1000],
            source="theme_ai_assistant",
            payload={
                "message": message,
                "page_url": payload.get("page_url", ""),
                "product_title": payload.get("product_title", ""),
                "answer": answer,
            },
        )
        state.record_event("customer_assistant.chat", payload={"message": message[:120], "safe": answer.get("safe")})
        return jsonify(answer)

    @app.post("/apps/bks-tryon")
    def api_member_tryon_submit():
        photo = request.files.get("photo")
        form = {
            "item": request.form.get("item", ""),
            "cart": request.form.get("cart", ""),
            "customer_id": request.form.get("customer_id", ""),
            "customer_email": request.form.get("customer_email", ""),
            "source": request.form.get("source", ""),
        }
        result, status_code = member_tryon_submit(photo, form)
        state.record_event("member_tryon.submit", payload={"status": result.get("status") or result.get("error", ""), "request_id": result.get("request_id", "")})
        realtime.publish("member_tryon.submit", {"request_id": result.get("request_id", ""), "status": result.get("status", "")})
        return jsonify(result), status_code

    @app.get("/api/member-tryon")
    def api_member_tryon_status():
        return jsonify(member_tryon_payload(settings))

    @app.get("/api/theme-optimizer")
    def api_theme_optimizer():
        return jsonify(theme_optimizer_payload(settings))

    @app.get("/api/turbobak")
    def api_turbobak():
        return jsonify(turbobak_payload(settings))

    @app.get("/api/agent-os")
    def api_agent_os():
        return jsonify(agent_os_payload(settings))

    @app.get("/api/openai-alliance")
    def api_openai_alliance():
        return jsonify(openai_alliance_payload(settings))

    @app.get("/api/canva-connectors")
    def api_canva_connectors():
        return jsonify(canva_connectors_payload(settings))

    @app.get("/api/hyperframes-connectors")
    def api_hyperframes_connectors():
        return jsonify(hyperframes_connectors_payload(settings))

    @app.get("/api/agent-routine")
    def api_agent_routine():
        return jsonify(action_snapshot()["routine"])

    @app.get("/api/payments")
    def api_payments():
        return jsonify(payments_payload(settings))

    @app.get("/api/official-inbox")
    def api_official_inbox():
        return jsonify(official_inbox_payload(settings))

    @app.get("/api/social-campaigns")
    def api_social_campaigns():
        return jsonify(action_snapshot()["social_campaigns"])

    @app.get("/api/legal-guardrails")
    def api_legal_guardrails():
        return jsonify(action_snapshot()["legal_guardrails"])

    @app.get("/api/photo-studio")
    def api_photo_studio():
        return jsonify(action_snapshot()["photo_studio"])

    @app.get("/api/growth-crm")
    def api_growth_crm():
        return jsonify(action_snapshot()["growth_crm"])

    @app.get("/api/google-trust")
    def api_google_trust():
        return jsonify(action_snapshot()["trust"])

    @app.get("/api/always-on")
    def api_always_on():
        return jsonify(action_snapshot()["always_on"])

    @app.get("/api/dialogic-agent")
    def api_dialogic_agent():
        return jsonify(action_snapshot()["dialogic"])

    @app.get("/api/knowledge")
    def api_knowledge():
        query = request.args.get("q", "").strip()
        limit = int(request.args.get("limit", 80 if not query else 30))
        if query:
            rows = knowledge.search(query, limit=limit)
        else:
            rows = knowledge.latest(limit=limit, area=request.args.get("area", ""))
        return jsonify({"rows": rows})

    def action_snapshot() -> dict[str, Any]:
        avatar_data = avatar_payload(settings.root_dir)
        snapshot = {
            "google": google_merchant_payload(settings),
            "marketing": marketing_offer_payload(settings),
            "theme": theme_optimizer_payload(settings),
            "turbobak": turbobak_payload(settings),
            "agent_os": agent_os_payload(settings),
            "openai_alliance": openai_alliance_payload(settings),
            "canva": canva_connectors_payload(settings),
            "hyperframes": hyperframes_connectors_payload(settings),
            "payments": payments_payload(settings),
            "network": network_monitor_payload(settings),
            "catalog_sync": catalog_live_sync_payload(settings, build_services(), references, live=False),
            "catalog": catalog_db_payload(settings),
            "member_tryon": member_tryon_payload(settings),
            "product_names": product_name_audit_payload(settings),
            "official_inbox": official_inbox_payload(settings),
            "sales_channels": sales_channels_payload(settings),
            "avatar": avatar_data,
        }
        snapshot["trust"] = google_trust_payload(settings, snapshot)
        snapshot["theme_assistant"] = theme_ai_assistant_payload(settings)
        snapshot["legal_guardrails"] = legal_guardrails_payload(settings, snapshot)
        snapshot["social_campaigns"] = social_campaigns_payload(settings, snapshot)
        snapshot["growth_crm"] = growth_crm_payload(settings, snapshot)
        snapshot["photo_studio"] = photo_studio_payload(settings, snapshot)
        snapshot["marketing_logic"] = marketing_logic_payload(settings, snapshot)
        snapshot["market"] = market_sense_payload(settings, snapshot)
        snapshot["actions"] = master_actions_payload(settings, snapshot)
        snapshot["weekly"] = weekly_goals_payload(settings, snapshot)
        snapshot["daily"] = daily_web_update_payload(settings, snapshot)
        snapshot["routine"] = agent_routine_payload(settings, snapshot)
        snapshot["always_on"] = always_on_payload(settings, snapshot)
        snapshot["dialogic"] = dialogic_agent_payload(settings)
        return snapshot

    @app.get("/api/master-actions")
    def api_master_actions():
        return jsonify(master_actions_payload(settings, action_snapshot()))

    @app.get("/api/market-sense")
    def api_market_sense():
        return jsonify(action_snapshot()["market"])

    @app.get("/api/weekly-goals")
    def api_weekly_goals():
        return jsonify(action_snapshot()["weekly"])

    @app.get("/api/daily-web-update")
    def api_daily_web_update():
        return jsonify(action_snapshot()["daily"])

    @app.get("/api/realtime-control")
    def api_realtime_control():
        return jsonify(realtime_control_payload(settings, state.list_phases(), realtime.latest(), state.recent_events()))

    @app.post("/api/daily-web-update/run")
    def api_run_daily_web_update():
        snapshot = action_snapshot()
        result = run_daily_web_update(settings, snapshot, live=request.args.get("live") == "1")
        knowledge.add(
            area="daily",
            title="Daily web update",
            status=result.get("summary", {}).get("mode", ""),
            evidence=result.get("summary", {}).get("next_action", ""),
            source="daily_web_update",
            payload=result.get("summary", {}),
        )
        state.record_event("daily_web_update.run", payload=result.get("summary", {}))
        return jsonify(result)

    @app.post("/api/master-actions/verify/<action_id>")
    def api_verify_master_action(action_id: str):
        result = verify_master_action(settings, action_id, action_snapshot())
        knowledge.add(
            area="verification",
            title=action_id,
            status=result.get("status", ""),
            evidence=result.get("detail", ""),
            source="master_action",
            payload=result,
        )
        state.record_event("master_action.verify", payload={"action_id": action_id, "status": result.get("status")})
        return jsonify(result), 200 if result.get("status") != "unknown_action" else 404

    @app.get("/api/phases")
    def api_phases():
        return jsonify({"phases": state.list_phases()})

    @app.get("/api/phases/<phase_id>")
    def api_phase(phase_id: str):
        try:
            return jsonify(state.get_phase(phase_id))
        except KeyError:
            return jsonify({"error": "unknown_phase"}), 404

    @app.post("/api/phases/<phase_id>/run")
    def api_run_phase(phase_id: str):
        try:
            runner = get_runner(phase_id)
            payload = request.get_json(silent=True) or {}
            result = orchestrator.run_phase(phase_id, runner, intent=payload.get("intent", "manual"), payload=payload)
            realtime.publish("phase.updated", result["phase"])
            status_code = 500 if "error" in result else 200
            return jsonify(result), status_code
        except KeyError:
            return jsonify({"error": "unknown_phase"}), 404

    @app.post("/api/make/inbound")
    def api_make_inbound():
        payload = request.get_json(silent=True) or {}
        services = build_services()
        normalized = services["make"].normalize_inbound(payload)
        state.record_event("make.inbound", payload=normalized)
        realtime.publish("make.inbound", normalized)
        return jsonify({"ok": True, "received": normalized})

    @app.post("/api/make/outbound/test")
    def api_make_outbound_test():
        services = build_services()
        payload = {"source": "ecamp", "message": "Webhook test"}
        try:
            response = services["make"].send_event("ecamp.test", payload)
        except Exception as exc:  # noqa: BLE001
            return jsonify({"ok": False, "error": str(exc)}), 500
        state.record_event("make.outbound", payload={"event": "ecamp.test", "response": response})
        return jsonify({"ok": True, "response": response})

    @app.get("/api/events")
    def api_events():
        return jsonify({"database_events": state.recent_events(), "live_events": realtime.latest()})

    @app.get("/api/runs")
    def api_runs():
        limit = int(request.args.get("limit", 50))
        return jsonify({"runs": ledger.list_runs(limit=limit)})

    @app.get("/api/references/summary")
    def api_references_summary():
        return jsonify(references.summary())

    @app.get("/api/references")
    def api_references():
        return jsonify(
            {
                "references": references.list_references(
                    limit=int(request.args.get("limit", 50)),
                    offset=int(request.args.get("offset", 0)),
                    search=request.args.get("search", ""),
                )
            }
        )

    @app.post("/api/references/sync-catalog")
    def api_references_sync_catalog():
        result = references.seed_from_catalog(active_catalog_csv())
        state.record_event("references.catalog_synced", payload=result)
        realtime.publish("references.catalog_synced", result)
        return jsonify(result)

    @app.get("/api/avatar-production")
    def api_avatar_production():
        data = avatar_payload(settings.root_dir)
        data["heygen_api"] = heygen_health()
        return jsonify(data)

    @app.post("/api/avatar-production/bootstrap")
    def api_avatar_production_bootstrap():
        result = ensure_workspace(settings.root_dir)
        state.record_event("avatar.bootstrap", phase_id="09", payload=result["summary"])
        realtime.publish("avatar.bootstrap", result["summary"])
        return jsonify(result)

    @app.get("/api/social-render")
    def api_social_render():
        data = avatar_payload(settings.root_dir)
        return jsonify(
            {
                "rows": data["social_render"],
                "sheet": data["social_render_sheet"],
                "summary": data["summary"],
                "heygen_api": heygen_health(),
                "youtube": youtube_health(),
                "make": build_services()["make"].health_snapshot(),
            }
        )

    @app.get("/api/skills")
    def api_skills():
        return jsonify(skills_payload(settings.root_dir))

    @app.get("/media/workspace/<path:relative_path>")
    def media_workspace(relative_path: str):
        root = settings.root_dir.resolve()
        target = (root / relative_path).resolve()
        allowed_suffixes = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".mp4", ".csv", ".md", ".json", ".zip", ".liquid", ".css"}
        if root not in target.parents and target != root:
            abort(404)
        if not target.exists() or not target.is_file() or target.suffix.lower() not in allowed_suffixes:
            abort(404)
        return send_file(target)

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8600, debug=False)
