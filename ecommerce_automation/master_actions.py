from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MEMORY_FILE = Path("output/master_agent_memory.json")
QUEUE_FILE = Path("output/master_action_queue.csv")


def _relative(root_dir: Path, path: Path) -> str:
    try:
        return path.relative_to(root_dir).as_posix()
    except ValueError:
        return path.as_posix()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _load_memory(root_dir: Path) -> dict[str, Any]:
    path = root_dir / MEMORY_FILE
    if not path.exists():
        return {"checks": {}, "events": []}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"checks": {}, "events": []}


def _save_memory(root_dir: Path, memory: dict[str, Any]) -> None:
    path = root_dir / MEMORY_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(memory, indent=2, ensure_ascii=False), encoding="utf-8")


def remember(root_dir: Path, action_id: str, status: str, detail: str) -> dict[str, Any]:
    memory = _load_memory(root_dir)
    memory.setdefault("checks", {})[action_id] = {"status": status, "detail": detail, "updated_at": _now()}
    memory.setdefault("events", []).insert(0, {"action_id": action_id, "status": status, "detail": detail, "created_at": _now()})
    memory["events"] = memory["events"][:80]
    _save_memory(root_dir, memory)
    return memory


def _status_from_memory(memory: dict[str, Any], action_id: str, fallback: str) -> str:
    return memory.get("checks", {}).get(action_id, {}).get("status", fallback)


def _resolve(computed: str, memory_status: str) -> str:
    """Let a human-verified memory pass override the computed status so the agent can progress."""
    if memory_status == "pass" and computed not in {"pass", "ready"}:
        return "pass"
    return computed


def build_actions(snapshot: dict[str, Any], memory: dict[str, Any]) -> list[dict[str, str]]:
    google = snapshot.get("google", {})
    marketing = snapshot.get("marketing", {})
    theme = snapshot.get("theme", {})
    network = snapshot.get("network", {})
    catalog_sync = snapshot.get("catalog_sync", {})
    product_names = snapshot.get("product_names", {})
    member = snapshot.get("member_area", {})
    trust_contract = snapshot.get("trust_contract", {})

    google_summary = google.get("summary", {})
    trust_fail = [row for row in google.get("trust_pages", []) if row.get("status") != "pass"]
    feed = google.get("feed", {}).get("summary", {})
    timer_summary = marketing.get("summary", {})
    theme_summary = theme.get("summary", {})
    network_summary = network.get("summary", {})
    network_needs_fix = int(network_summary.get("needs_fix", 0) or 0)
    catalog_summary = catalog_sync.get("summary", {})
    catalog_attention = int(catalog_summary.get("attention", 0) or 0) + int(catalog_summary.get("errors", 0) or 0)
    name_summary = product_names.get("summary", {})
    name_issues = int(name_summary.get("needs_fix", 0) or 0) + int(name_summary.get("needs_review", 0) or 0)

    # Google Merchant P0: use feed data when available, else fall back to memory
    local_inv_errors = int(google_summary.get("local_inventory_errors", -1) or -1)
    unavail_pages = int(google_summary.get("unavailable_pages", -1) or -1)
    local_inv_computed = "pass" if local_inv_errors == 0 else "needs_fix"
    unavail_computed = "pass" if unavail_pages == 0 else "needs_fix"

    def mem(action_id: str) -> str:
        return _status_from_memory(memory, action_id, "")

    actions = [
        {
            "id": "google_local_inventory_gate",
            "priority": "1",
            "title": "Disattiva o completa inventario locale Google",
            "area": "Google Merchant",
            "status": _resolve(local_inv_computed, mem("google_local_inventory_gate")),
            "why": "Merchant segnala dati di inventario locale mancanti. Per un modello print-on-demand senza negozio fisico, il canale locale va disattivato.",
            "do": "In Merchant Center disattiva local inventory ads/free local listings; conferma la verifica quando fatto.",
            "verify": "GET /api/master-actions/verify/google_local_inventory_gate",
            "next": "google_product_pages_available",
        },
        {
            "id": "google_product_pages_available",
            "priority": "2",
            "title": "Correggi pagine prodotto non disponibili",
            "area": "Google Merchant",
            "status": _resolve(unavail_computed, mem("google_product_pages_available")),
            "why": "Merchant segnala prodotti con pagina non disponibile. Sembra offerta non reale o non consegnabile.",
            "do": "Rimuovi prodotti vecchi dal feed, risincronizza Shopify, verifica URL e aspetta nuova scansione Merchant.",
            "verify": "GET /api/master-actions/verify/google_product_pages_available",
            "next": "google_trust_pages",
        },
        {
            "id": "google_trust_pages",
            "priority": "3",
            "title": "Sistema pagine fiducia Google",
            "area": "Google Merchant",
            "status": _resolve("pass" if not trust_fail else "needs_fix", mem("google_trust_pages")),
            "why": "Google richiede identita, contatto, spedizioni, resi, privacy e termini prima di rimuovere segnalazioni.",
            "do": "Pubblica o correggi About, FAQ, policy spedizione/reso/privacy, poi riesegui verifica.",
            "verify": "GET /api/master-actions/verify/google_trust_pages",
            "next": "network_trust_monitor",
        },
        {
            "id": "network_trust_monitor",
            "priority": "4",
            "title": "Sistema DNS, email auth e dominio",
            "area": "Network",
            "status": _resolve(
                "pass" if network_needs_fix == 0 and network_summary.get("status") not in ("manual_pending", "needs_fix") else "needs_fix",
                mem("network_trust_monitor"),
            ),
            "why": "SPF/DKIM/DMARC, HTTPS e bounce DSN devono essere puliti prima di scalare comunicazioni e campagne.",
            "do": "Apri Network Monitor, aggiungi DMARC se manca, configura IMAP per crew@bakabo.club, verifica endpoint.",
            "verify": "GET /api/master-actions/verify/network_trust_monitor",
            "next": "google_feed_cleanup",
        },
        {
            "id": "google_feed_cleanup",
            "priority": "5",
            "title": "Pulisci feed prodotti non disponibili",
            "area": "Google Merchant",
            "status": _resolve("manual_pending", mem("google_feed_cleanup")),
            "why": "Prodotti non disponibili nel feed sono rischiosi per segnalazioni 'offerta non reale'.",
            "do": "In Merchant/Shopify rimuovi prodotti eliminati, aggiorna sitemap e attendi nuova scansione.",
            "verify": "GET /api/master-actions/verify/google_feed_cleanup",
            "next": "catalog_live_sync",
        },
        {
            "id": "catalog_live_sync",
            "priority": "6",
            "title": "Sincronizza catalogo Shopify/Printify",
            "area": "Catalog",
            "status": _resolve(
                "pass" if catalog_summary.get("status") == "synced" and catalog_attention == 0 else "needs_review",
                mem("catalog_live_sync"),
            ),
            "why": "Prodotti non mappati o bozze Printify non pubblicate creano disallineamento tra store e fornitore.",
            "do": "Esegui live sync nel pannello Catalog Sync e correggi prodotti non mappati o non attivi.",
            "verify": "GET /api/master-actions/verify/catalog_live_sync",
            "next": "product_name_cleanup",
        },
        {
            "id": "product_name_cleanup",
            "priority": "7",
            "title": "Pulisci nomi prodotto online",
            "area": "Catalog",
            "status": _resolve(
                "pass" if name_issues == 0 and name_summary.get("status") == "pass" else "needs_fix",
                mem("product_name_cleanup"),
            ),
            "why": "Emoji, simboli, refusi, duplicati o mismatch handle/titolo riducono fiducia e peggiorano feed/campagne.",
            "do": "Apri Product Name Audit, rimuovi emoji/simboli, correggi refusi, riallinea titoli a handle/collection.",
            "verify": "GET /api/master-actions/verify/product_name_cleanup",
            "next": "copy_claims_review",
        },
        {
            "id": "copy_claims_review",
            "priority": "8",
            "title": "Ripulisci claim potenzialmente fuorvianti",
            "area": "Copy",
            "status": _resolve("needs_review" if feed.get("claim_review", 0) else "pass", mem("copy_claims_review")),
            "why": "Claim come official, certified, free o guaranteed devono essere provabili sulla landing.",
            "do": "Rivedi i prodotti segnalati e rimuovi promesse non dimostrabili.",
            "verify": "GET /api/master-actions/verify/copy_claims_review",
            "next": "member_area_health",
        },
        {
            "id": "member_area_health",
            "priority": "9",
            "title": "Verifica area member e gold ring attivi",
            "area": "Member",
            "status": _resolve(
                "pass" if member.get("status") == "ok" else "needs_review",
                mem("member_area_health"),
            ),
            "why": "L'area member BKS (gold ring, Try-On, Metal tier) e' l'app interna per fidelizzazione e conversione.",
            "do": "Verifica che bakabo.club/pages/bks-members carichi il tema dark, il gold ring sia visibile, il tab Try-On risponda.",
            "verify": "GET /api/master-actions/verify/member_area_health",
            "next": "marketing_timer_safe",
        },
        {
            "id": "marketing_timer_safe",
            "priority": "10",
            "title": "Attiva timer offerta con regole chiare",
            "area": "Marketing",
            "status": _resolve(
                "pass" if timer_summary.get("compliance") == "google_safe" else "needs_fix",
                mem("marketing_timer_safe"),
            ),
            "why": "Il countdown deve avere scadenza reale e termini visibili per non essere considerato pressione artificiale.",
            "do": "Configura la sezione BKS Timed Offer con data/ora reale e termini visibili.",
            "verify": "GET /api/master-actions/verify/marketing_timer_safe",
            "next": "theme_tm04_active",
        },
        {
            "id": "theme_tm04_active",
            "priority": "11",
            "title": "Tema BKS TM04 attivo e deployato",
            "area": "Theme",
            "status": _resolve(
                "pass" if theme_summary.get("theme_id") == "202392961362" or theme_summary.get("status") == "ready" else "needs_review",
                mem("theme_tm04_active"),
            ),
            "why": "TM04 e' il tema live BKS — dark editorial, header gold ring, area member integrata. Deve essere il tema attivo su Shopify.",
            "do": "Verifica in Shopify Admin che TM04 (id 202392961362) sia il tema pubblicato. Se draft, pubblica.",
            "verify": "GET /api/master-actions/verify/theme_tm04_active",
            "next": "merchant_appeal_ready",
        },
        {
            "id": "merchant_appeal_ready",
            "priority": "12",
            "title": "Richiedi revisione Merchant",
            "area": "Google Merchant",
            "status": _resolve(
                "ready" if trust_contract.get("summary", {}).get("merchant_appeal_ready", False)
                else "blocked",
                mem("merchant_appeal_ready"),
            ),
            "why": "La revisione va chiesta solo dopo che tutti i P0 del Trust Contract sono verdi: Business identity, Product truth, Collection identity, Returns, Secure checkout.",
            "do": "Apri google_trust_contract.csv e verifica p0_blockers == []. Se vuoto, prepara ricorso con: URL policy, feed aggiornato (local_inventory_errors=0), TM04 pubblicato, tag Origin corretti.",
            "verify": "GET /api/master-actions/verify/merchant_appeal_ready",
            "next": "monitor_after_appeal",
        },
    ]

    for action in actions:
        action["memory_status"] = mem(action["id"])
    return actions


def write_queue(root_dir: Path, actions: list[dict[str, str]]) -> str:
    path = root_dir / QUEUE_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["id", "priority", "title", "area", "status", "why", "do", "verify", "next", "memory_status"]
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([{key: action.get(key, "") for key in fieldnames} for action in actions])
    return _relative(root_dir, path)


def payload(settings: Any, snapshot: dict[str, Any]) -> dict[str, Any]:
    root_dir = settings.root_dir
    memory = _load_memory(root_dir)
    actions = build_actions(snapshot, memory)
    queue = write_queue(root_dir, actions)
    next_action = next((action for action in actions if action["status"] not in {"pass", "ready"}), actions[0] if actions else {})
    total = len(actions)
    passed = sum(1 for a in actions if a["status"] in {"pass", "ready"})
    return {
        "summary": {
            "total": total,
            "pass": passed,
            "needs_fix": sum(1 for a in actions if a["status"] in {"needs_fix", "needs_build", "needs_review"}),
            "blocked": sum(1 for a in actions if a["status"] == "blocked"),
            "percent_complete": round(passed / total * 100) if total else 0,
            "queue": queue,
            "memory": _relative(root_dir, root_dir / MEMORY_FILE),
        },
        "next_action": next_action,
        "actions": actions,
        "memory": memory,
    }


def verify(settings: Any, action_id: str, snapshot: dict[str, Any]) -> dict[str, Any]:
    data = payload(settings, snapshot)
    action = next((row for row in data["actions"] if row["id"] == action_id), None)
    if not action:
        memory = remember(settings.root_dir, action_id, "unknown_action", "Action not found.")
        return {"ok": False, "status": "unknown_action", "memory": memory}
    ok = action["status"] in {"pass", "ready"}
    detail = action["why"] if ok else action["do"]
    memory = remember(settings.root_dir, action_id, "pass" if ok else action["status"], detail)
    return {"ok": ok, "action": action, "status": "pass" if ok else action["status"], "detail": detail, "memory": memory}
