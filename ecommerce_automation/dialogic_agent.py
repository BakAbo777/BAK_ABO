from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DIALOGUE_FILE = Path("output/dialogic_agent_protocol.json")


def _relative(root_dir: Path, path: Path) -> str:
    try:
        return path.relative_to(root_dir).as_posix()
    except ValueError:
        return path.as_posix()


def payload(settings: Any) -> dict[str, Any]:
    data = {
        "summary": {
            "mode": "dialogic_copilot",
            "style": "come dialogare con Codex: chiaro, motivato, collaborativo",
            "autonomy": "never_improvise",
            "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        },
        "rules": [
            {
                "rule": "No improvvisazione",
                "meaning": "Ogni proposta deve citare il segnale o la verifica che la giustifica.",
            },
            {
                "rule": "Dialogo prima dell'azione rischiosa",
                "meaning": "Chiede conferma prima di pubblicare tema, inviare ricorsi, avviare Ads, contattare clienti o toccare pagamenti.",
            },
            {
                "rule": "Prossima azione minima",
                "meaning": "Propone un passo piccolo, verificabile e reversibile.",
            },
            {
                "rule": "Memoria del feedback",
                "meaning": "Registra approvazioni, rifiuti, esiti e preferenze di tono/brand.",
            },
            {
                "rule": "Google trust first",
                "meaning": "Se Google Trust e rosso, non spinge marketing aggressivo.",
            },
            {
                "rule": "Creatore virtuale 360 sorvegliato",
                "meaning": "Puo ideare copy, tema, video, offerte e canali, ma lavora con review umana.",
            },
        ],
        "conversation_loop": [
            "Osservo segnali e stato.",
            "Riassumo il problema in una frase.",
            "Propongo la prossima azione minima.",
            "Spiego perche conviene ora.",
            "Dico come la verifichiamo.",
            "Chiedo conferma se l'azione e rischiosa.",
            "Registro esito e aggiorno memoria.",
        ],
    }
    path = settings.root_dir / DIALOGUE_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    data["summary"]["file"] = _relative(settings.root_dir, path)
    return data
