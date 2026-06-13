from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


SKIP_DIRS = {".venv", "__pycache__", ".git", ".qodo"}
PATTERN_FILE = Path("output/turbobak_reuse_patterns.csv")


def _relative(base: Path, path: Path) -> str:
    try:
        return path.relative_to(base).as_posix()
    except ValueError:
        return path.as_posix()


def _safe_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _iter_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    result: list[Path] = []
    for path in root.rglob("*"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.is_file():
            result.append(path)
    return result


def _page_title(path: Path) -> str:
    name = path.parent.name
    return name.replace("_", " ").replace("-", " ")


def index(settings: Any) -> dict[str, Any]:
    root = Path(settings.turbobak_path)
    files = _iter_files(root)
    workers = sorted((root / "workers").glob("*.py")) if (root / "workers").exists() else []
    pages = sorted((root / "pages").glob("*")) if (root / "pages").exists() else []
    data_files = [path for path in files if "\\data\\" in str(path) or "/data/" in path.as_posix()]
    log_files = [path for path in files if path.suffix.lower() in {".log", ".txt"} and ("log" in path.name.lower() or "logs" in path.as_posix().lower())]
    telegram_config = _safe_json(root / "EXTERNAL" / "Telegram_data" / "telegram_config.json")
    telegram = telegram_config.get("telegram", {}) if isinstance(telegram_config, dict) else {}

    existing_names = {path.name.lower(): path for path in workers}
    text_index = " ".join(path.as_posix().lower() for path in files)

    capabilities = [
        {
            "capability": "Priority engine",
            "source": "workers + dashboards",
            "use": "Rank next actions and verify prerequisites before moving phase.",
            "status": "ready" if workers else "missing_workers",
        },
        {
            "capability": "Telegram signal pattern",
            "source": "workers/telegram_bot.py",
            "use": "Reuse notification and opt-in discipline for BKS customer bots.",
            "status": "ready" if (root / "workers" / "telegram_bot.py").exists() else "missing_worker",
        },
        {
            "capability": "Performance dashboards",
            "source": "pages/19_Analisi_performance",
            "use": "Keep analytics charts compact and decision-oriented.",
            "status": "ready" if any("19_Analisi_performance" in path.as_posix() for path in pages) else "missing_page",
        },
        {
            "capability": "Historical logs",
            "source": "logs + 5_logs_Operazioni",
            "use": "Let the Master learn from checks, outcomes and repeat blockers.",
            "status": "ready" if log_files else "missing_logs",
        },
    ]
    reuse_patterns = [
        {
            "pattern": "Worker chain with startup log",
            "source": "run_all.ps1",
            "use_for_master": "Run routine steps in sequence: refresh, validate, signal, alert, dashboard.",
            "status": "ready" if (root / "run_all.ps1").exists() else "missing_source",
            "agent_rule": "Log every step and keep failures non-destructive.",
        },
        {
            "pattern": "Structure health check",
            "source": "check_structure.py",
            "use_for_master": "Check required folders, workers, data files, duplicate paths and running processes.",
            "status": "ready" if (root / "check_structure.py").exists() else "missing_source",
            "agent_rule": "Before automation, verify paths and prerequisites.",
        },
        {
            "pattern": "Telegram alert loop",
            "source": "workers/telegram_bot.py",
            "use_for_master": "Notify owner when Google, email, campaign, cost or customer risk crosses threshold.",
            "status": "ready" if "telegram_bot.py" in existing_names else "missing_source",
            "agent_rule": "Send alerts only for important state changes.",
        },
        {
            "pattern": "Signal threshold engine",
            "source": "workers/indicator_updater.py",
            "use_for_master": "Convert metrics into thresholds: trust red, cost high, inbox urgent, campaign ready.",
            "status": "ready" if "indicator_updater.py" in existing_names else "missing_source",
            "agent_rule": "Every recommendation needs a measurable signal and threshold.",
        },
        {
            "pattern": "Forecast / scenario simulator",
            "source": "workers/monte_carlo_forecast.py",
            "use_for_master": "Estimate campaign outcome/risk ranges before budget or API-heavy operations.",
            "status": "ready" if "monte_carlo_forecast.py" in existing_names else "missing_source",
            "agent_rule": "Use lightweight forecast before paid ads, render batches or large email campaigns.",
        },
        {
            "pattern": "Operation log and fee awareness",
            "source": "pages/5_logs_Operazioni",
            "use_for_master": "Track API cost, ad spend, render credits, email sends and supplier costs.",
            "status": "ready" if "5_logs_operazioni" in text_index else "needs_review",
            "agent_rule": "Cost is a first-class signal before action.",
        },
        {
            "pattern": "Google Drive backup habit",
            "source": "pages + EXTERNAL/Google_Drive",
            "use_for_master": "Mirror key reports and memory to Drive when enabled.",
            "status": "ready" if "google_drive" in text_index else "needs_review",
            "agent_rule": "Drive is backup/mirror, not the only source of truth.",
        },
        {
            "pattern": "AI history / decision archive",
            "source": "pages/6_Storico_Segnali_AI",
            "use_for_master": "Save decisions, outcomes and next suggestions to Knowledge DB.",
            "status": "ready" if "6_storico_segnali_ai" in text_index else "needs_review",
            "agent_rule": "Learning means storing decisions and comparing outcomes.",
        },
    ]

    return {
        "root": str(root),
        "exists": root.exists(),
        "github_repo": settings.turbobak_github_repo,
        "summary": {
            "files": len(files),
            "workers": len(workers),
            "pages": sum(1 for page in pages if page.is_dir()),
            "data_files": len(data_files),
            "log_files": len(log_files),
            "telegram_enabled": bool(telegram.get("enabled")),
        },
        "workers": [
            {"name": path.name, "path": _relative(root, path), "size": path.stat().st_size}
            for path in workers
        ],
        "pages": [
            {"name": page.name, "title": _page_title(page), "path": _relative(root, page)}
            for page in pages
            if page.is_dir()
        ],
        "capabilities": capabilities,
        "reuse_patterns": reuse_patterns,
    }


def write_index(settings: Any) -> dict[str, Any]:
    data = index(settings)
    path = settings.root_dir / "output" / "turbobak_engine_index.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = data["capabilities"] + [
        {
            "capability": f"worker:{row['name']}",
            "source": row["path"],
            "use": "Available local worker pattern.",
            "status": "ready",
        }
        for row in data["workers"]
    ]
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=["capability", "source", "use", "status"])
        writer.writeheader()
        writer.writerows(rows)
    pattern_path = settings.root_dir / PATTERN_FILE
    pattern_path.parent.mkdir(parents=True, exist_ok=True)
    with pattern_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=["pattern", "source", "use_for_master", "status", "agent_rule"])
        writer.writeheader()
        writer.writerows(data["reuse_patterns"])
    data["summary"]["index"] = path.relative_to(settings.root_dir).as_posix()
    data["summary"]["patterns"] = pattern_path.relative_to(settings.root_dir).as_posix()
    data["summary"]["reuse_patterns"] = len(data["reuse_patterns"])
    return data


def payload(settings: Any) -> dict[str, Any]:
    return write_index(settings)
