from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

BAKABO_STORE_DOMAIN = "bakabo.club"

# Amazon is phase 08 — gated at campaign_layer (p2) after Google trust P0 is green
AMAZON_TRUST_GATE = "campaign_layer"
AMAZON_PRIORITY = "p2"

# Merch on Demand tier ladder: Standard → Professional → Pro
MERCH_TIERS = ("Standard", "Professional", "Pro")


@dataclass
class AmazonClient:
    seller_id: str = ""
    sp_api_client_id: str = ""
    merch_email: str = ""
    merch_tier: str = "Standard"
    _session: Any = field(default=None, repr=False, compare=False)

    @property
    def marketplace_configured(self) -> bool:
        """SP-API requires both seller_id and client_id for marketplace operations."""
        return bool(self.seller_id and self.sp_api_client_id)

    @property
    def merch_configured(self) -> bool:
        """Merch on Demand requires an approved email account."""
        return bool(self.merch_email)

    @property
    def configured(self) -> bool:
        return self.marketplace_configured or self.merch_configured

    def merch_status(self) -> dict[str, Any]:
        if not self.merch_configured:
            return {
                "status": "not_configured",
                "note": "Set AMAZON_MERCH_EMAIL to activate Merch on Demand. Apply at merch.amazon.com.",
            }
        tier = self.merch_tier if self.merch_tier in MERCH_TIERS else "Standard"
        tier_index = MERCH_TIERS.index(tier)
        return {
            "status": "configured",
            "email": self.merch_email,
            "tier": tier,
            "tier_level": tier_index + 1,
            "tier_max": len(MERCH_TIERS),
            "note": f"Merch on Demand active at tier {tier_index + 1}/{len(MERCH_TIERS)} ({tier}). Tier upgrades unlock higher royalties and expanded product types.",
        }

    def marketplace_status(self) -> dict[str, Any]:
        if not self.seller_id:
            return {
                "status": "not_configured",
                "note": "Set AMAZON_SELLER_ID. Seller Central account required before SP-API access.",
            }
        if not self.sp_api_client_id:
            return {
                "status": "partial",
                "seller_id_present": True,
                "note": "Set AMAZON_SP_API_CLIENT_ID. Register an SP-API app in Seller Central Developer Console.",
            }
        return {
            "status": "configured",
            "seller_id_present": True,
            "client_id_present": True,
            "note": "SP-API client configured. Listing and order APIs available once trust gate is reached.",
        }

    def health_snapshot(self) -> dict[str, Any]:
        merch = self.merch_status()
        marketplace = self.marketplace_status()

        if self.marketplace_configured and self.merch_configured:
            status = "configured"
        elif self.configured:
            status = "partial"
        else:
            status = "not_configured"

        return {
            "configured": self.configured,
            "status": status,
            "priority": AMAZON_PRIORITY,
            "trust_gate": AMAZON_TRUST_GATE,
            "phase": "08 Amazon",
            "merch_on_demand": merch,
            "marketplace": marketplace,
            "note": (
                f"Amazon is a phase-08 channel (trust_gate: {AMAZON_TRUST_GATE}). "
                f"Activate only after Google trust P0 is fully resolved for {BAKABO_STORE_DOMAIN}."
            ),
        }
