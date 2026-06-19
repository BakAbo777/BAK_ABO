from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


BAKABO_STORE_DOMAIN = "bakabo.club"
BKS_TM04_THEME_ID = "202392961362"
BAKABO_CREW_EMAIL = "crew@bakabo.club"

TOOLSET_CSV = Path("output/openai_alliance_matrix.csv")
SKILL_DOC = Path("BKS_SKILL/skills/bakabo-openai-alliance/SKILL.md")
PROTOCOL_DOC = Path("docs/bakabo-openai-alliance_SKILL.md")  # legacy


CAPABILITIES: tuple[dict[str, str], ...] = (
    {
        "capability": "ChatGPT Project",
        "area": "Strategic workspace",
        "use": "Founder-level project room for BKS memory, prompts, decisions and cross-tool coordination.",
        "env": "OPENAI_CHATGPT_PROJECT_URL",
        "agent_rule": "Use as an allied workspace; do not expose private project URLs in public repo files.",
        "trust_gate": "trust_foundation",
    },
    {
        "capability": "OpenAI API",
        "area": "Agent reasoning",
        "use": "Draft, classify, summarize, plan, write product/social copy and operate the Master assistant.",
        "env": "OPENAI_API_KEY;OPENAI_PROJECT_ID",
        "agent_rule": "Use project-scoped credentials when available; keep high-risk actions behind approval.",
        "trust_gate": "trust_foundation",
    },
    {
        "capability": "Knowledge / Vector Memory",
        "area": "BKS database",
        "use": "Ground customer assistant, official inbox replies, policy answers and product knowledge.",
        "env": "OPENAI_VECTOR_STORE_ID",
        "agent_rule": "Answer from stored BKS evidence; if evidence is missing, say so and route to human review.",
        "trust_gate": "trust_foundation",
    },
    {
        "capability": "Realtime Voice",
        "area": "Conversational interface",
        "use": "Future low-latency voice layer for the Master or customer assistant.",
        "env": "OPENAI_REALTIME_ENABLED",
        "agent_rule": "Enable only after consent, logging and customer safety rules are ready.",
        "trust_gate": "campaign_layer",
    },
    {
        "capability": "Images / Creative Prompts",
        "area": "Visual production",
        "use": "Generate or improve prompts for product shots, collection hero images and campaign visuals.",
        "env": "OPENAI_API_KEY",
        "agent_rule": "Never invent finished product photography; label AI drafts and verify against real product data.",
        "trust_gate": "collection_identity",
    },
    {
        "capability": "Safety / Transparency",
        "area": "Trust gate",
        "use": "Check copy for misleading claims, unsupported urgency and policy-sensitive language.",
        "env": "OPENAI_API_KEY",
        "agent_rule": "Use as a preflight assistant, not as legal approval or Google appeal authority.",
        "trust_gate": "trust_foundation",
    },
)


WORKFLOWS: tuple[dict[str, str], ...] = (
    {
        "workflow": "Master Next Action",
        "sequence": "Read dashboard snapshot -> detect blockers -> propose one action -> verify result -> write memory.",
        "output": "Operational recommendation such as: fix DMARC first, remove emoji titles, verify Merchant trust page.",
        "trust_gate": "trust_foundation",
    },
    {
        "workflow": "Customer Assistant",
        "sequence": "Read BKS knowledge -> answer with disclosure -> cite policy/source link -> hand off on risk.",
        "output": "Safe multilingual support reply inside Shopify theme.",
        "trust_gate": "conversion_support",
    },
    {
        "workflow": "Creative Production",
        "sequence": "Collection brief -> script/copy/prompt -> Canva/HyperFrames/HeyGen handoff -> review metadata.",
        "output": "Avatar scripts, social captions, design briefs and motion storyboards.",
        "trust_gate": "collection_identity",
    },
    {
        "workflow": "Official Inbox",
        "sequence": "Classify incoming email -> draft reply -> check legal/payment/privacy risk -> request approval.",
        "output": "crew@bakabo.club customer/support response draft.",
        "trust_gate": "trust_foundation",
    },
)


GUARDRAILS: tuple[str, ...] = (
    "OpenAI aligns to the BKS project; BKS does not reshape itself around OpenAI defaults.",
    "BKS identity, product data, series/collection system, legal duties and Google trust rules are the source of truth.",
    "OpenAI is an allied reasoning layer, not an unattended business owner.",
    "The Master must answer from BKS data, local database, verified APIs and policy documents.",
    "High-risk actions require approval: customer messages, legal claims, payments, ads, public publishing and Google appeals.",
    "Private ChatGPT Project links belong in `.env`, not tracked source files.",
    "Use OpenAI to prepare clear options; the interface should keep the user in one flow.",
    "Record decisions and outcomes so the agent learns from verified results, not guesses.",
)


def _relative(root_dir: Path, path: Path) -> str:
    try:
        return path.relative_to(root_dir).as_posix()
    except ValueError:
        return path.as_posix()


def _env_value(settings: Any, name: str) -> str:
    aliases = {
        "OPENAI_CHATGPT_PROJECT_URL": "openai_chatgpt_project_url",
        "OPENAI_API_KEY": "openai_api_key",
        "OPENAI_PROJECT_ID": "openai_project_id",
        "OPENAI_VECTOR_STORE_ID": "openai_vector_store_id",
        "OPENAI_REALTIME_ENABLED": "openai_realtime_enabled",
    }
    return str(getattr(settings, aliases.get(name, name.lower()), "") or "")


def _status(settings: Any, env_string: str) -> str:
    envs = [item.strip() for item in env_string.split(";") if item.strip()]
    if not envs:
        return "planned"
    present = sum(1 for env in envs if _env_value(settings, env))
    if present == len(envs):
        return "ready"
    if present:
        return "partial"
    if "OPENAI_API_KEY" in envs:
        return "missing"
    return "planned"


def rows(settings: Any) -> list[dict[str, str]]:
    result: list[dict[str, str]] = []
    for row in CAPABILITIES:
        envs = [item.strip() for item in row["env"].split(";") if item.strip()]
        configured = sum(1 for env in envs if _env_value(settings, env))
        result.append(
            {
                **row,
                "status": _status(settings, row["env"]),
                "configured": f"{configured}/{len(envs)}",
                "autonomy": "preflight_only" if row["area"] == "Trust gate" else "draft_only",
                "trust_gate": row.get("trust_gate", "trust_foundation"),
            }
        )
    return result


def write_sheet(settings: Any, data: list[dict[str, str]]) -> str:
    path = settings.root_dir / TOOLSET_CSV
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["capability", "area", "status", "configured", "autonomy", "trust_gate", "env", "use", "agent_rule"]
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([{key: row.get(key, "") for key in fieldnames} for row in data])
    return _relative(settings.root_dir, path)


def write_protocol(settings: Any) -> str:
    skill_path = settings.root_dir / SKILL_DOC
    skill_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "---",
        "name: bakabo-openai-alliance",
        "description: OpenAI alliance operating skill for BakAbo/BKS. Use when structuring OpenAI, ChatGPT Projects, OpenAI API, knowledge memory, realtime voice, image/copy generation, safety preflight, customer assistant, or agent workflows inside the BKS Master.",
        "metadata:",
        "  type: skill",
        "  trust_gate: trust_foundation",
        f"  store: {BAKABO_STORE_DOMAIN}",
        "---",
        "",
        "# BakAbo / BKS OpenAI Alliance",
        "",
        "## Operating Rule",
        "",
        "Use OpenAI as the allied intelligence layer of the BKS Master. OpenAI must adapt to BKS identity, data, phases, approvals and tone. It reasons, drafts, summarizes and checks; it does not publish, spend, message customers or make legal/payment decisions without approval.",
        "",
        "## Capabilities",
        "",
    ]
    for capability in CAPABILITIES:
        lines.extend(
            [
                f"### {capability['capability']}",
                f"- Area: {capability['area']}",
                f"- Trust gate: `{capability['trust_gate']}`",
                f"- Use: {capability['use']}",
                f"- Env: `{capability['env']}`",
                f"- Agent rule: {capability['agent_rule']}",
                "",
            ]
        )
    lines.extend(["## Workflows", ""])
    for workflow in WORKFLOWS:
        lines.extend(
            [
                f"### {workflow['workflow']}",
                f"- Trust gate: `{workflow['trust_gate']}`",
                f"- Sequence: {workflow['sequence']}",
                f"- Output: {workflow['output']}",
                "",
            ]
        )
    lines.extend(["## Guardrails", ""])
    lines.extend(f"- {item}" for item in GUARDRAILS)
    lines.append("")
    content = "\n".join(lines)
    skill_path.write_text(content, encoding="utf-8")
    # legacy copy
    legacy_path = settings.root_dir / PROTOCOL_DOC
    legacy_path.parent.mkdir(parents=True, exist_ok=True)
    legacy_path.write_text(content, encoding="utf-8")
    return _relative(settings.root_dir, skill_path)


def payload(settings: Any) -> dict[str, Any]:
    data = rows(settings)
    sheet = write_sheet(settings, data)
    protocol = write_protocol(settings)
    project_ready = bool(str(getattr(settings, "openai_chatgpt_project_url", "") or "").strip())
    return {
        "summary": {
            "status": "ready" if any(row["status"] == "ready" for row in data) else "planned",
            "capabilities": len(data),
            "ready": sum(1 for row in data if row["status"] == "ready"),
            "partial": sum(1 for row in data if row["status"] == "partial"),
            "project_link": "configured" if project_ready else "env_pending",
            "default_model": getattr(settings, "openai_default_model", "") or "project_default",
            "sheet": sheet,
            "skill": protocol,
            "trust_gate": "trust_foundation",
        },
        "capabilities": data,
        "workflows": list(WORKFLOWS),
        "guardrails": list(GUARDRAILS),
    }
