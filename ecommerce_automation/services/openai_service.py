from __future__ import annotations

from dataclasses import dataclass


@dataclass
class OpenAIService:
    api_key: str

    @property
    def configured(self) -> bool:
        return bool(self.api_key)

    def health(self) -> dict[str, str]:
        return {"status": "configured" if self.configured else "missing_api_key"}

