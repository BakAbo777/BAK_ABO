from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# OpenAI is p0 — trust_foundation — phase 04: copy, prompts, product descriptions, agent reasoning
OPENAI_TRUST_GATE = "trust_foundation"
OPENAI_PRIORITY = "p0"
OPENAI_PHASE = "04 AI content / images"

# Recommended model if OPENAI_DEFAULT_MODEL env is not set
OPENAI_DEFAULT_MODEL = "gpt-4o-mini"

# BKS use cases covered by this integration
BKS_USE_CASES = (
    "Catalog enrichment: SEO titles, product descriptions, tag inference.",
    "Avatar scripts: 15s collection scripts for HeyGen production.",
    "AI assistant: bks-ai-assistant theme section responses.",
    "Safety preflight: content review before Merchant submission.",
    "Agent reasoning: BKS Master Agent copy drafts and skill dispatch.",
)


@dataclass
class OpenAIService:
    api_key: str = ""
    project_id: str = ""
    organization_id: str = ""
    chatgpt_project_url: str = ""
    vector_store_id: str = ""
    default_model: str = ""
    _client: Any = field(default=None, repr=False, compare=False)

    @property
    def configured(self) -> bool:
        return bool(self.api_key)

    @property
    def project_configured(self) -> bool:
        return bool(self.project_id or self.chatgpt_project_url)

    @property
    def knowledge_configured(self) -> bool:
        return bool(self.vector_store_id)

    def _effective_model(self) -> str:
        return self.default_model or OPENAI_DEFAULT_MODEL

    def api_status(self) -> dict[str, Any]:
        if not self.api_key:
            return {"status": "missing_api_key", "env": "OPENAI_API_KEY"}
        return {
            "status": "configured",
            "model": self._effective_model(),
            "has_org": bool(self.organization_id),
        }

    def project_status(self) -> dict[str, Any]:
        if self.project_id:
            return {"status": "project_ready", "source": "OPENAI_PROJECT_ID"}
        if self.chatgpt_project_url:
            return {"status": "project_ready", "source": "OPENAI_CHATGPT_PROJECT_URL"}
        return {
            "status": "env_pending",
            "note": "Set OPENAI_PROJECT_ID or OPENAI_CHATGPT_PROJECT_URL for strategic BKS workspace.",
        }

    def knowledge_status(self) -> dict[str, Any]:
        if not self.vector_store_id:
            return {
                "status": "not_configured",
                "note": "Set OPENAI_VECTOR_STORE_ID to enable grounded BKS memory (customer assistant, inbox replies).",
            }
        return {"status": "configured", "vector_store_id_present": True}

    def health_snapshot(self) -> dict[str, Any]:
        return {
            "configured": self.configured,
            "status": "configured" if self.configured else "missing_api_key",
            "priority": OPENAI_PRIORITY,
            "trust_gate": OPENAI_TRUST_GATE,
            "phase": OPENAI_PHASE,
            "api": self.api_status(),
            "project": self.project_status(),
            "knowledge_memory": self.knowledge_status(),
            "use_cases": len(BKS_USE_CASES),
        }

    def health(self) -> dict[str, Any]:
        return self.health_snapshot()
