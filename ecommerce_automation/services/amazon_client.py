from __future__ import annotations

from dataclasses import dataclass


@dataclass
class AmazonClient:
    client_id: str = ""

    @property
    def configured(self) -> bool:
        return bool(self.client_id)

    def health(self) -> dict[str, str]:
        return {"status": "configured" if self.configured else "not_configured"}

