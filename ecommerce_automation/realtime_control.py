from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


STATUS_FILE = Path("output/realtime_control_status.json")
TIMELINE_FILE = Path("output/realtime_processing_timeline.csv")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _relative(root_dir: Path, path: Path) -> str:
    try:
        return path.relative_to(root_dir).as_posix()
    except ValueError:
        return path.as_posix()


def _load_json(root_dir: Path, relative: str) -> dict[str, Any]:
    path = root_dir / relative
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _load_action_queue(root_dir: Path) -> list[dict[str, str]]:
    path = root_dir / "output" / "master_action_queue.csv"
    if not path.exists():
        return []
    try:
        with path.open("r", newline="", encoding="utf-8-sig") as handle:
            return list(csv.DictReader(handle))
    except OSError:
        return []


def _latest_event(live_events: list[dict[str, Any]], database_events: list[dict[str, Any]]) -> dict[str, str]:
    if live_events:
        event = live_events[0]
        return {
            "type": str(event.get("type", "live.event")),
            "detail": str(event.get("payload", {}))[:180],
        }
    if database_events:
        event = database_events[0]
        payload = event.get("payload", {}) if isinstance(event, dict) else {}
        return {
            "type": str(event.get("event_type", "database.event")),
            "detail": str(payload.get("message") or payload.get("status") or payload)[:180],
        }
    return {"type": "idle", "detail": "Nessun evento recente. Agente pronto."}


def _stage(name: str, status: str, progress: int, signal: str, detail: str) -> dict[str, Any]:
    return {
        "stage": name,
        "status": status,
        "progress": max(0, min(100, progress)),
        "signal": signal,
        "detail": detail,
    }


def _phase_progress(phases: list[dict[str, Any]]) -> int:
    if not phases:
        return 0
    values = [int(phase.get("progress", 0) or 0) for phase in phases]
    return round(sum(values) / len(values))


def payload(settings: Any, phases: list[dict[str, Any]], live_events: list[dict[str, Any]], database_events: list[dict[str, Any]]) -> dict[str, Any]:
    actions = _load_action_queue(settings.root_dir)
    network = _load_json(settings.root_dir, "output/network_monitor_report.json")
    always_on = _load_json(settings.root_dir, "output/always_on_agent_status.json")

    next_action = next((row for row in actions if row.get("status") not in {"pass", "ready"}), actions[0] if actions else {})
    latest = _latest_event(live_events, database_events)
    phase_progress = _phase_progress(phases)
    network_summary = network.get("summary", {}) if isinstance(network, dict) else {}
    network_needs = int(network_summary.get("needs_fix", 0) or 0)
    always_summary = always_on.get("summary", {}) if isinstance(always_on, dict) else {}
    blockers = int(always_summary.get("blockers", 0) or 0)
    action_status = next_action.get("status", "ready")

    stages = [
        _stage(
            "Dialogo",
            "running" if latest["type"] == "agent.chat" else "ready",
            100,
            "AI conversazionale",
            "Una richiesta alla volta: capisco, rispondo, propongo un solo passo.",
        ),
        _stage(
            "Memoria e fasi",
            "running" if any(phase.get("status") == "running" for phase in phases) else "ready",
            phase_progress,
            f"{len(phases)} fasi",
            "Uso lo stato locale e la Knowledge DB prima di chiamare API costose.",
        ),
        _stage(
            "Network e API",
            "needs_fix" if network_needs else ("manual_pending" if not network_summary else "ready"),
            100 - min(network_needs * 20, 80),
            f"{network_needs} blocker",
            "DNS, DMARC, DSN, endpoint e suffissi dati governano consegna e fiducia.",
        ),
        _stage(
            "Trust gate",
            "attention" if blockers else "ready",
            100 - min(blockers * 15, 75),
            f"{blockers} blocker",
            "Google, legal, customer safety e Merchant restano il semaforo prima della crescita.",
        ),
        _stage(
            "Prossima azione",
            action_status,
            100 if action_status in {"pass", "ready"} else 55,
            next_action.get("title", "Agente pronto"),
            next_action.get("do", "Chiedimi la prima cosa da fare."),
        ),
        _stage(
            "Verifica e apprendimento",
            "ready",
            100,
            latest["type"],
            latest["detail"],
        ),
    ]

    progress = round(sum(int(stage["progress"]) for stage in stages) / len(stages)) if stages else 0
    report = {
        "summary": {
            "mode": "realtime_light_control",
            "status": "attention" if any(stage["status"] in {"needs_fix", "attention"} for stage in stages) else "ready",
            "progress": progress,
            "poll_seconds": 8,
            "updated_at": _now(),
            "next_action": next_action.get("title", "Agente pronto"),
            "current_event": latest["type"],
        },
        "stages": stages,
        "latest_event": latest,
        "principle": "Conversational control first; detailed panels only when evidence is needed.",
    }

    status_path = settings.root_dir / STATUS_FILE
    status_path.parent.mkdir(parents=True, exist_ok=True)
    status_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    timeline_path = settings.root_dir / TIMELINE_FILE
    with timeline_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=["stage", "status", "progress", "signal", "detail"])
        writer.writeheader()
        writer.writerows(stages)

    report["summary"]["status_file"] = _relative(settings.root_dir, status_path)
    report["summary"]["timeline"] = _relative(settings.root_dir, timeline_path)
    return report
