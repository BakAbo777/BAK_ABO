from __future__ import annotations

from dataclasses import asdict
from typing import Any, Callable

from ecommerce_automation.core.run_ledger import RunLedger
from ecommerce_automation.core.state_manager import StateManager


PhaseRunner = Callable[[dict[str, Any]], dict[str, Any]]


class Orchestrator:
    def __init__(self, *, state: StateManager, ledger: RunLedger, context_factory: Callable[[], dict[str, Any]]):
        self.state = state
        self.ledger = ledger
        self.context_factory = context_factory

    def run_phase(self, phase_id: str, runner: PhaseRunner, *, intent: str = "manual", payload: dict[str, Any] | None = None) -> dict[str, Any]:
        run = self.ledger.start_run(phase_id, intent, payload)
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
            return {"phase": updated, "run": asdict(finished)}
        except Exception as exc:  # noqa: BLE001
            finished = self.ledger.finish_run(run.run_id, status="failed", error=f"{type(exc).__name__}: {exc}")
            updated = self.state.update_phase(
                phase_id,
                status="failed",
                progress=0,
                message=str(exc),
                metrics={"run_id": run.run_id, "idempotency_key": run.idempotency_key, "error": type(exc).__name__},
            )
            return {"phase": updated, "run": asdict(finished), "error": str(exc)}

