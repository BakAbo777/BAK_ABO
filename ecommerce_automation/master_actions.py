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


def build_actions(snapshot: dict[str, Any], memory: dict[str, Any]) -> list[dict[str, str]]:
    google = snapshot.get("google", {})
    marketing = snapshot.get("marketing", {})
    theme = snapshot.get("theme", {})
    turbo = snapshot.get("turbobak", {})
    network = snapshot.get("network", {})
    catalog_sync = snapshot.get("catalog_sync", {})
    product_names = snapshot.get("product_names", {})

    google_summary = google.get("summary", {})
    trust_fail = [row for row in google.get("trust_pages", []) if row.get("status") != "pass"]
    feed = google.get("feed", {}).get("summary", {})
    timer_summary = marketing.get("summary", {})
    theme_summary = theme.get("summary", {})
    turbo_exists = turbo.get("exists", False)
    network_summary = network.get("summary", {})
    network_needs_fix = int(network_summary.get("needs_fix", 0) or 0)
    catalog_summary = catalog_sync.get("summary", {})
    catalog_attention = int(catalog_summary.get("attention", 0) or 0) + int(catalog_summary.get("errors", 0) or 0)
    name_summary = product_names.get("summary", {})
    name_issues = int(name_summary.get("needs_fix", 0) or 0) + int(name_summary.get("needs_review", 0) or 0)

    actions = [
        {
            "id": "google_trust_pages",
            "priority": "1",
            "title": "Sistema pagine fiducia Google",
            "area": "Google Merchant",
            "status": "pass" if not trust_fail else "needs_fix",
            "why": "Google segnala rappresentazione ingannevole: prima deve vedere identita, contatto, spedizioni, resi, privacy e termini.",
            "do": "Pubblica o correggi About e FAQ/help, poi riesegui verifica.",
            "verify": "GET /api/master-actions/verify/google_trust_pages",
            "next": "google_feed_cleanup",
        },
        {
            "id": "network_trust_monitor",
            "priority": "2",
            "title": "Sistema DNS, DSN e dominio fiducia",
            "area": "Network",
            "status": "pass" if network_needs_fix == 0 and network_summary.get("status") != "manual_pending" else "needs_fix",
            "why": "Email ufficiali, bounce DSN, SPF/DKIM/DMARC, HTTPS e suffissi tracking devono essere puliti prima di scalare comunicazioni e campagne.",
            "do": "Apri Network Trust Monitor, aggiungi DMARC se manca, configura IMAP/DSN per crew@bakabo.club e verifica endpoint HTTPS.",
            "verify": "GET /api/master-actions/verify/network_trust_monitor",
            "next": "google_feed_cleanup",
        },
        {
            "id": "google_feed_cleanup",
            "priority": "3",
            "title": "Pulisci feed prodotti non disponibili",
            "area": "Google Merchant",
            "status": "manual_pending",
            "why": "Merchant riporta prodotti non disponibili e residui di inventario locale: sono rischiosi per 'offerte non disponibili'.",
            "do": "In Merchant/Shopify rimuovi prodotti eliminati dal feed, aggiorna sitemap e attendi nuova scansione.",
            "verify": "GET /api/master-actions/verify/google_feed_cleanup",
            "next": "copy_claims_review",
        },
        {
            "id": "catalog_live_sync",
            "priority": "4",
            "title": "Sincronizza catalogo Shopify/Printify",
            "area": "Catalog",
            "status": "pass" if catalog_summary.get("status") == "synced" and catalog_attention == 0 else "needs_review",
            "why": "Il Master deve caricare da solo i prodotti live e confrontare aggiornamenti, mapping e stati tra Shopify e Printify.",
            "do": "Esegui Run live sync nella scheda Catalog Sync e correggi prodotti non mappati, bozze Printify o Shopify non attivi.",
            "verify": "GET /api/master-actions/verify/catalog_live_sync",
            "next": "copy_claims_review",
        },
        {
            "id": "copy_claims_review",
            "priority": "5",
            "title": "Ripulisci claim potenzialmente fuorvianti",
            "area": "Copy",
            "status": "needs_review" if feed.get("claim_review", 0) else "pass",
            "why": "Parole come official, certified, free, guaranteed o discount vanno usate solo se provabili sulla landing.",
            "do": "Rivedi i prodotti segnalati e rimuovi promesse non dimostrabili.",
            "verify": "GET /api/master-actions/verify/copy_claims_review",
            "next": "theme_light_trust",
        },
        {
            "id": "product_name_cleanup",
            "priority": "6",
            "title": "Pulisci nomi prodotto online",
            "area": "Catalog",
            "status": "pass" if name_issues == 0 and name_summary.get("status") == "pass" else "needs_fix",
            "why": "Emoji, simboli, refusi, duplicati o mismatch handle/titolo riducono fiducia e possono peggiorare feed/campagne.",
            "do": "Apri Product Name Audit, rimuovi emoji/simboli tipo ™, correggi refusi e riallinea titoli a handle/collection.",
            "verify": "GET /api/master-actions/verify/product_name_cleanup",
            "next": "theme_light_trust",
        },
        {
            "id": "theme_light_trust",
            "priority": "7",
            "title": "Applica tema piu chiaro e rassicurante",
            "area": "Theme",
            "status": "pass" if theme_summary.get("status") == "ready" else "needs_build",
            "why": "Troppe novita e un look troppo scuro riducono fiducia. Procediamo con una patch leggera, reversibile.",
            "do": "Usa lo zip LIGHT_TRUST_TIMER_READY o installa gli asset generati.",
            "verify": "GET /api/master-actions/verify/theme_light_trust",
            "next": "marketing_timer_safe",
        },
        {
            "id": "marketing_timer_safe",
            "priority": "8",
            "title": "Attiva timer offerta con regole chiare",
            "area": "Marketing",
            "status": "pass" if timer_summary.get("compliance") == "google_safe" else "needs_fix",
            "why": "Il countdown puo aiutare, ma deve avere scadenza reale e termini visibili per non sembrare pressione artificiale.",
            "do": "Installa la sezione BKS timed offer e mostra solo condizioni vere.",
            "verify": "GET /api/master-actions/verify/marketing_timer_safe",
            "next": "merchant_appeal_ready",
        },
        {
            "id": "merchant_appeal_ready",
            "priority": "9",
            "title": "Richiedi revisione Merchant",
            "area": "Google Merchant",
            "status": "blocked" if google_summary.get("blockers", 0) else "ready",
            "why": "La revisione va chiesta solo dopo aver corretto sito, feed e messaggi.",
            "do": "Quando i P0 sono verdi, prepara ricorso con prove: URL policy, feed aggiornato, tema chiaro, tag corretti.",
            "verify": "GET /api/master-actions/verify/merchant_appeal_ready",
            "next": "monitor_after_appeal",
        },
        {
            "id": "turbobak_memory",
            "priority": "10",
            "title": "Usa TurboBAK come memoria operativa",
            "area": "Agent",
            "status": "pass" if turbo_exists else "needs_fix",
            "why": "Il Master deve imparare dai controlli e proporre la prossima azione, non solo rispondere.",
            "do": "Mantieni indice TurboBAK e memoria verifiche attivi.",
            "verify": "GET /api/master-actions/verify/turbobak_memory",
            "next": "continuous_learning",
        },
    ]

    for action in actions:
        action["memory_status"] = _status_from_memory(memory, action["id"], "")
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
    return {
        "summary": {
            "total": len(actions),
            "pass": sum(1 for action in actions if action["status"] == "pass"),
            "needs_fix": sum(1 for action in actions if action["status"] in {"needs_fix", "needs_build", "needs_review"}),
            "blocked": sum(1 for action in actions if action["status"] == "blocked"),
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
