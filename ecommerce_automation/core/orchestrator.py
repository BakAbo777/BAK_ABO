from __future__ import annotations

import logging
from dataclasses import asdict
from typing import Any, Callable

from ecommerce_automation.core.logger import BKS_LOG_NAME
from ecommerce_automation.core.run_ledger import RunLedger
from ecommerce_automation.core.state_manager import StateManager

BAKABO_STORE_DOMAIN = "bakabo.club"
BKS_TM04_THEME_ID = "202392961362"

# Phases that publish externally or spend credits — require Roberto approval (approved=True)
APPROVAL_REQUIRED_PHASES = frozenset({"05", "07", "08", "09"})

_log = logging.getLogger(BKS_LOG_NAME)

PhaseRunner = Callable[[dict[str, Any]], dict[str, Any]]


class Orchestrator:
    def __init__(
        self,
        *,
        state: StateManager,
        ledger: RunLedger,
        context_factory: Callable[[], dict[str, Any]],
    ):
        self.state = state
        self.ledger = ledger
        self.context_factory = context_factory

    def phases(self) -> list[dict[str, Any]]:
        return self.state.list_phases()

    def run_phase(
        self,
        phase_id: str,
        runner: PhaseRunner,
        *,
        intent: str = "manual",
        payload: dict[str, Any] | None = None,
        approved: bool = False,
    ) -> dict[str, Any]:
        needs_approval = phase_id in APPROVAL_REQUIRED_PHASES
        if needs_approval and not approved:
            _log.warning("Phase %s publishes externally — approval required.", phase_id)
            return {
                "phase": self.state.get_phase(phase_id),
                "approval_required": True,
                "message": (
                    f"Phase {phase_id} publishes to external systems and requires Roberto approval. "
                    "Call run_phase(..., approved=True) to proceed."
                ),
            }

        current = self.state.get_phase(phase_id)
        if current.get("status") == "running":
            _log.warning("Phase %s already running — skipped.", phase_id)
            return {"phase": current, "skipped": True, "message": "Phase already running."}

        run = self.ledger.start_run(phase_id, intent, payload)
        _log.info("Phase %s started — run_id=%s intent=%s", phase_id, run.run_id, intent)
        self.state.update_phase(
            phase_id,
            status="running",
            progress=5,
            message=f"Run {run.run_id} started.",
            metrics={"run_id": run.run_id, "idempotency_key": run.idempotency_key},
        )
        context = self.context_factory()
        context["run"] = asdict(run)
        try:
            result = runner(context)
            status = result.get("status", "complete")
            metrics = result.get("metrics", {})
            finished = self.ledger.finish_run(run.run_id, status=status, metrics=metrics)
            updated = self.state.update_phase(
                phase_id,
                status=status,
                progress=result.get("progress", 100),
                message=result.get("message", ""),
                external_ref=result.get("external_ref", ""),
                metrics=metrics | {"run_id": run.run_id, "idempotency_key": run.idempotency_key},
            )
            _log.info("Phase %s finished — status=%s run_id=%s", phase_id, status, run.run_id)
            out: dict[str, Any] = {"phase": updated, "run": asdict(finished)}
            if needs_approval:
                out["approval_required"] = False
            return out
        except Exception as exc:  # noqa: BLE001
            _log.error("Phase %s failed — %s: %s run_id=%s", phase_id, type(exc).__name__, exc, run.run_id)
            finished = self.ledger.finish_run(
                run.run_id, status="failed", error=f"{type(exc).__name__}: {exc}"
            )
            updated = self.state.update_phase(
                phase_id,
                status="failed",
                progress=0,
                message=str(exc),
                metrics={
                    "run_id": run.run_id,
                    "idempotency_key": run.idempotency_key,
                    "error": type(exc).__name__,
                },
            )
            return {"phase": updated, "run": asdict(finished), "error": str(exc)}
