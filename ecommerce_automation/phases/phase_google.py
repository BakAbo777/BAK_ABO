from __future__ import annotations

from typing import Any


def run(context: dict[str, Any]) -> dict[str, Any]:
    root = context["settings"].root_dir
    audit = root / "output" / "live_site_audit" / "live_site_audit.md"
    return {
        "status": "ready" if audit.exists() else "pending",
        "progress": 80 if audit.exists() else 35,
        "message": "Live audit file found." if audit.exists() else "Run tools/audit_live_site.py after deploy.",
        "metrics": {"audit_file": str(audit), "exists": audit.exists()},
    }

