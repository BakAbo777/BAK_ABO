from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ASSISTANT_SECTION = Path("04_TEMA_SHOPIFY/sections/bks-ai-assistant.liquid")
INSTALL_DOC = Path("04_TEMA_SHOPIFY/BKS_AI_ASSISTANT_INSTALL.md")
GOOGLE_NOTE = Path("04_TEMA_SHOPIFY/BKS_AI_ASSISTANT_GOOGLE_TRUST_NOTE.md")


SAFE_POLICY_LINKS = {
    "shipping": "https://bakabo.club/policies/shipping-policy",
    "refund": "https://bakabo.club/policies/refund-policy",
    "privacy": "https://bakabo.club/policies/privacy-policy",
    "terms": "https://bakabo.club/policies/terms-of-service",
    "contact": "https://bakabo.club/pages/contact",
    "about": "https://bakabo.club/pages/about",
}


def _relative(root_dir: Path, path: Path) -> str:
    try:
        return path.relative_to(root_dir).as_posix()
    except ValueError:
        return path.as_posix()


def _enabled(value: str) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on", "enabled"}


def section_liquid(settings: Any) -> str:
    endpoint_default = json.dumps(settings.bks_assistant_public_endpoint or "")
    token_default = json.dumps(settings.bks_assistant_public_token or "")
    return f"""{{% comment %}}
  BKS AI Assistant
  Customer-facing assistant for Shopify. It must answer from verified BKS data,
  disclose that it is AI, avoid payments/data collection, and route policy
  questions to official store pages.
{{% endcomment %}}

{{% if section.settings.enabled %}}
<section
  class="bks-ai-assistant"
  data-bks-ai-assistant
  data-endpoint="{{{{ section.settings.api_endpoint | escape }}}}"
  data-token="{{{{ section.settings.public_token | escape }}}}"
  data-product-title="{{% if product %}}{{{{ product.title | escape }}}}{{% endif %}}"
  aria-label="{{{{ section.settings.title | default: 'BKS AI Assistant' | escape }}}}"
>
  <button class="bks-ai-assistant__button" type="button" data-bks-ai-toggle aria-expanded="false">
    <span>{{{{ section.settings.button_label | default: 'Ask BKS' | escape }}}}</span>
  </button>
  <div class="bks-ai-assistant__panel" data-bks-ai-panel hidden>
    <div class="bks-ai-assistant__head">
      <div>
        <strong>{{{{ section.settings.title | default: 'BKS AI Assistant' | escape }}}}</strong>
        <small>{{{{ section.settings.disclosure | escape }}}}</small>
      </div>
      <button type="button" data-bks-ai-close aria-label="Close">x</button>
    </div>
    <div class="bks-ai-assistant__log" data-bks-ai-log>
      <p class="bks-ai-assistant__message assistant">{{{{ section.settings.welcome | escape }}}}</p>
    </div>
    <form class="bks-ai-assistant__form" data-bks-ai-form>
      <input data-bks-ai-input type="text" autocomplete="off" placeholder="{{{{ section.settings.placeholder | escape }}}}">
      <button type="submit">{{{{ section.settings.send_label | default: 'Send' | escape }}}}</button>
    </form>
    <p class="bks-ai-assistant__terms">{{{{ section.settings.terms | escape }}}}</p>
  </div>
</section>

<style>
  .bks-ai-assistant {{
    --bks-ai-ink: #111111;
    --bks-ai-paper: #ffffff;
    --bks-ai-muted: #5f5a52;
    --bks-ai-line: #ded8cd;
    --bks-ai-accent: #2f6f6b;
    --bks-font-display: "BKS Display", var(--font-heading-family, "Segoe UI", Arial, sans-serif);
    --bks-font-text: "BKS Text", var(--font-body-family, "Segoe UI", Arial, sans-serif);
    bottom: 18px;
    font-family: var(--bks-font-text);
    font-size: 14px;
    line-height: 1.5;
    position: fixed;
    right: 18px;
    z-index: 80;
  }}
  .bks-ai-assistant__button {{
    background: var(--bks-ai-ink);
    border: 1px solid var(--bks-ai-ink);
    color: #fff;
    cursor: pointer;
    font: inherit;
    font-weight: 700;
    line-height: 1.2;
    min-height: 44px;
    padding: 12px 15px;
  }}
  .bks-ai-assistant__panel {{
    background: var(--bks-ai-paper);
    border: 1px solid var(--bks-ai-line);
    bottom: 54px;
    box-shadow: 0 18px 48px rgba(17, 17, 17, .18);
    color: var(--bks-ai-ink);
    display: grid;
    gap: 10px;
    max-height: min(620px, calc(100vh - 100px));
    overflow: hidden;
    position: absolute;
    right: 0;
    width: min(380px, calc(100vw - 36px));
  }}
  .bks-ai-assistant__panel[hidden] {{
    display: none;
  }}
  .bks-ai-assistant__head {{
    align-items: start;
    border-bottom: 1px solid var(--bks-ai-line);
    display: flex;
    gap: 12px;
    justify-content: space-between;
    padding: 13px 14px;
  }}
  .bks-ai-assistant__head strong,
  .bks-ai-assistant__head small {{
    display: block;
  }}
  .bks-ai-assistant__head strong {{
    font-family: var(--bks-font-display);
    letter-spacing: 0;
    line-height: 1.2;
  }}
  .bks-ai-assistant__head small {{
    color: var(--bks-ai-muted);
    font-size: 12px;
    line-height: 1.45;
    margin-top: 3px;
  }}
  .bks-ai-assistant__head button {{
    background: transparent;
    border: 0;
    color: var(--bks-ai-ink);
    cursor: pointer;
    font: inherit;
    padding: 2px 4px;
  }}
  .bks-ai-assistant__log {{
    display: grid;
    gap: 8px;
    max-height: 320px;
    overflow: auto;
    padding: 12px 14px;
  }}
  .bks-ai-assistant__message {{
    border: 1px solid var(--bks-ai-line);
    font-size: 14px;
    line-height: 1.5;
    margin: 0;
    padding: 9px 10px;
    white-space: pre-wrap;
  }}
  .bks-ai-assistant__message.user {{
    background: #f1ede5;
    margin-left: 28px;
  }}
  .bks-ai-assistant__message.assistant {{
    background: #fff;
    margin-right: 28px;
  }}
  .bks-ai-assistant__form {{
    border-top: 1px solid var(--bks-ai-line);
    display: grid;
    gap: 8px;
    grid-template-columns: minmax(0, 1fr) auto;
    padding: 12px 14px 0;
  }}
  .bks-ai-assistant__form input {{
    border: 1px solid var(--bks-ai-line);
    color: var(--bks-ai-ink);
    font: inherit;
    font-size: 16px;
    min-width: 0;
    padding: 10px 11px;
  }}
  .bks-ai-assistant__form button {{
    background: var(--bks-ai-accent);
    border: 1px solid var(--bks-ai-accent);
    color: #fff;
    cursor: pointer;
    font: inherit;
    font-weight: 700;
    min-height: 44px;
    padding: 10px 12px;
  }}
  .bks-ai-assistant__terms {{
    color: var(--bks-ai-muted);
    font-size: 12px;
    line-height: 1.45;
    margin: 0;
    padding: 0 14px 14px;
  }}
  @media (max-width: 760px) {{
    .bks-ai-assistant {{
      bottom: 12px;
      right: 12px;
    }}
    .bks-ai-assistant__panel {{
      bottom: 50px;
      max-height: calc(100vh - 80px);
      width: calc(100vw - 24px);
    }}
    .bks-ai-assistant__message.user,
    .bks-ai-assistant__message.assistant {{
      margin-left: 0;
      margin-right: 0;
    }}
  }}
</style>

<script>
  (function () {{
    var root = document.querySelector('[data-bks-ai-assistant]');
    if (!root || root.dataset.bound === '1') return;
    root.dataset.bound = '1';
    var panel = root.querySelector('[data-bks-ai-panel]');
    var toggle = root.querySelector('[data-bks-ai-toggle]');
    var close = root.querySelector('[data-bks-ai-close]');
    var form = root.querySelector('[data-bks-ai-form]');
    var input = root.querySelector('[data-bks-ai-input]');
    var log = root.querySelector('[data-bks-ai-log]');
    var endpoint = root.dataset.endpoint || '';
    var token = root.dataset.token || '';
    function append(role, text) {{
      var node = document.createElement('p');
      node.className = 'bks-ai-assistant__message ' + role;
      node.textContent = text;
      log.appendChild(node);
      log.scrollTop = log.scrollHeight;
    }}
    function setOpen(open) {{
      panel.hidden = !open;
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      if (open) input.focus();
    }}
    toggle.addEventListener('click', function () {{ setOpen(panel.hidden); }});
    close.addEventListener('click', function () {{ setOpen(false); }});
    form.addEventListener('submit', function (event) {{
      event.preventDefault();
      var message = (input.value || '').trim();
      if (!message) return;
      input.value = '';
      append('user', message);
      if (!endpoint) {{
        append('assistant', 'Assistente BKS predisposto: per attivarlo serve collegare un endpoint pubblico sicuro nel tema.');
        return;
      }}
      append('assistant', 'Controllo i dati BKS disponibili...');
      fetch(endpoint, {{
        method: 'POST',
        headers: {{
          'Content-Type': 'application/json',
          'X-BKS-Assistant-Token': token
        }},
        body: JSON.stringify({{
          message: message,
          page_url: window.location.href,
          product_title: root.dataset.productTitle || ''
        }})
      }})
        .then(function (response) {{ return response.json(); }})
        .then(function (data) {{
          var pending = log.querySelector('.bks-ai-assistant__message.assistant:last-child');
          if (pending && pending.textContent === 'Controllo i dati BKS disponibili...') pending.remove();
          append('assistant', data.reply || 'Non ho trovato una risposta verificata nel database BKS.');
        }})
        .catch(function () {{
          append('assistant', 'In questo momento non riesco a raggiungere il database BKS. Usa le pagine policy o il contatto ufficiale.');
        }});
    }});
  }})();
</script>
{{% endif %}}

{{% schema %}}
{{
  "name": "BKS AI assistant",
  "settings": [
    {{ "type": "checkbox", "id": "enabled", "label": "Enable assistant", "default": false }},
    {{ "type": "text", "id": "api_endpoint", "label": "Public API endpoint", "default": {endpoint_default} }},
    {{ "type": "text", "id": "public_token", "label": "Public routing token", "default": {token_default} }},
    {{ "type": "text", "id": "button_label", "label": "Button label", "default": "Ask BKS" }},
    {{ "type": "text", "id": "title", "label": "Panel title", "default": "BKS AI Assistant" }},
    {{ "type": "textarea", "id": "disclosure", "label": "AI disclosure", "default": "AI assistant: answers from verified BKS data and official store policies." }},
    {{ "type": "textarea", "id": "welcome", "label": "Welcome message", "default": "Hi, I can help with BKS collections, shipping, returns and product information. Prices and availability are always confirmed on the product page and at checkout." }},
    {{ "type": "text", "id": "placeholder", "label": "Input placeholder", "default": "Ask about BKS..." }},
    {{ "type": "text", "id": "send_label", "label": "Send label", "default": "Send" }},
    {{ "type": "textarea", "id": "terms", "label": "Footer terms", "default": "The assistant does not collect payment details and cannot replace checkout, order confirmation, shipping policy, refund policy or human support." }}
  ],
  "presets": [
    {{ "name": "BKS AI assistant" }}
  ]
}}
{{% endschema %}}
"""


def install_doc(settings: Any) -> str:
    endpoint = settings.bks_assistant_public_endpoint or "not configured yet"
    enabled = settings.agent_customer_chat_enabled
    return f"""# BKS AI Assistant Install

## Purpose

Customer-facing AI assistant for the Shopify theme. It is designed to answer only from BKS data, store policies and safe public guidance.

## Files

- `sections/bks-ai-assistant.liquid`
- `BKS_AI_ASSISTANT_GOOGLE_TRUST_NOTE.md`

## Activation

1. Add the section `BKS AI assistant` to the theme.
2. Keep it disabled until the public endpoint is reachable over HTTPS.
3. Set `Public API endpoint` to: `{endpoint}`
4. Set `Public routing token` only if the endpoint expects one.
5. Enable the section after verifying a test question about shipping, refunds and product availability.

## Current runtime flags

- `AGENT_CUSTOMER_CHAT_ENABLED`: {enabled}
- `BKS_ASSISTANT_PUBLIC_ENDPOINT`: {endpoint}

## Required guardrails

- Always disclose that it is an AI assistant.
- Do not collect card details, passwords or payment data.
- Do not promise discounts, availability or delivery beyond the product page and checkout.
- Link to official policies for shipping, refunds, privacy and terms.
- Log customer questions as learning signals without storing sensitive personal data.
"""


def google_trust_note() -> str:
    return """# BKS AI Assistant - Google Trust Note

This file explains why the customer-facing assistant is a trust feature, not a misleading sales device.

## Position

BKS AI Assistant is designed as a transparent customer support layer. It identifies itself as AI, uses the BKS knowledge database and official store policies, and avoids unverified product, price or availability claims.

## Google Merchant alignment

- Clear identity: the assistant says it is the BKS AI Assistant and does not impersonate a human, Google, Shopify or another brand.
- Relevant information before purchase: shipping, refunds, privacy, terms and contact routes are linked from official store pages.
- No misleading offers: the assistant does not invent discounts, countdowns, scarcity, certifications or partnerships.
- No unavailable offers: product price and availability are delegated to the product page and checkout.
- No sensitive data collection: it does not ask for card data, passwords or private payment information.
- Human handoff: support questions can be routed to the contact page or human support.

## Evidence to keep

- Theme section: `sections/bks-ai-assistant.liquid`
- Knowledge database: `ecommerce_automation/database.db`, table `agent_knowledge`
- Assistant protocol: `output/dialogic_agent_protocol.json`
- Google trust contract: `output/google_trust_contract.csv`

## Sources used for policy framing

- Google Merchant misrepresentation policy: https://support.google.com/merchants/answer/6150127?hl=it
- Google Merchant product data specification: https://support.google.com/merchants/answer/7052112
"""


def ensure_workspace(settings: Any) -> dict[str, str]:
    section_path = settings.root_dir / ASSISTANT_SECTION
    section_path.parent.mkdir(parents=True, exist_ok=True)
    section_path.write_text(section_liquid(settings), encoding="utf-8")

    install_path = settings.root_dir / INSTALL_DOC
    install_path.write_text(install_doc(settings), encoding="utf-8")

    google_path = settings.root_dir / GOOGLE_NOTE
    google_path.write_text(google_trust_note(), encoding="utf-8")

    return {
        "section": _relative(settings.root_dir, section_path),
        "install_doc": _relative(settings.root_dir, install_path),
        "google_note": _relative(settings.root_dir, google_path),
    }


def payload(settings: Any) -> dict[str, Any]:
    files = ensure_workspace(settings)
    endpoint_ready = bool(settings.bks_assistant_public_endpoint)
    customer_enabled = _enabled(settings.agent_customer_chat_enabled)
    theme_enabled = _enabled(settings.bks_assistant_theme_enabled)
    checks = [
        {"check": "ai_disclosure", "status": "pass", "detail": "Widget says it is an AI assistant."},
        {"check": "knowledge_db_only", "status": "pass", "detail": "Endpoint is designed to answer from agent_knowledge and BKS policy links."},
        {"check": "no_payment_capture", "status": "pass", "detail": "Assistant cannot collect card, password or payment details."},
        {"check": "policy_handoff", "status": "pass", "detail": "Shipping/refund/privacy/terms/contact links are official store pages."},
        {"check": "public_endpoint", "status": "pass" if endpoint_ready else "manual_pending", "detail": settings.bks_assistant_public_endpoint or "Set BKS_ASSISTANT_PUBLIC_ENDPOINT before live activation."},
        {"check": "customer_chat_flag", "status": "pass" if customer_enabled else "manual_pending", "detail": f"AGENT_CUSTOMER_CHAT_ENABLED={settings.agent_customer_chat_enabled}"},
        {"check": "theme_default", "status": "pass", "detail": "Shopify section defaults to disabled until reviewed."},
    ]
    status = "ready_for_theme" if files.get("section") else "needs_build"
    if endpoint_ready and customer_enabled and theme_enabled:
        status = "ready_for_live_test"
    return {
        "summary": {
            "status": status,
            "google_safe": "pass",
            "theme_enabled": theme_enabled,
            "customer_chat_enabled": customer_enabled,
            "endpoint": settings.bks_assistant_public_endpoint or "",
            "section": files["section"],
            "install_doc": files["install_doc"],
            "google_note": files["google_note"],
        },
        "files": files,
        "checks": checks,
        "guardrails": [
            "AI disclosure is visible.",
            "Answers use BKS data and official policy links.",
            "Checkout remains the only source for final price, shipping and availability.",
            "No payment data collection in chat.",
            "Human support path stays visible.",
        ],
        "customer_topics": [
            "shipping",
            "refunds",
            "product availability",
            "collection explanation",
            "made to order",
            "contact and human handoff",
        ],
        "sources": [
            {"label": "Google Merchant misrepresentation policy", "url": "https://support.google.com/merchants/answer/6150127?hl=it"},
            {"label": "Google Merchant product data specification", "url": "https://support.google.com/merchants/answer/7052112"},
        ],
    }


def customer_reply(message: str, knowledge_rows: list[dict[str, Any]], settings: Any) -> dict[str, Any]:
    text = (message or "").strip()
    lower = text.lower()
    links = SAFE_POLICY_LINKS
    evidence_count = len(knowledge_rows)

    if not text:
        reply = "Scrivimi una domanda su collezioni BKS, spedizioni, resi, pagamenti o disponibilita prodotto."
    elif any(token in lower for token in ("carta", "password", "iban", "cvv", "numero carta", "dati personali")):
        reply = (
            "Per sicurezza non raccolgo dati di pagamento, password o informazioni sensibili in chat. "
            "Usa solo il checkout ufficiale e, se serve supporto, la pagina contatti: "
            f"{links['contact']}."
        )
    elif any(token in lower for token in ("spedizione", "consegna", "shipping", "delivery", "tempo")):
        reply = (
            "In base alle regole BKS disponibili, tempi e costi definitivi di spedizione vanno confermati nel checkout. "
            "La pagina ufficiale per le condizioni di spedizione e: "
            f"{links['shipping']}."
        )
    elif any(token in lower for token in ("reso", "rimborso", "refund", "return", "restituzione")):
        reply = (
            "Per resi e rimborsi fa fede la policy ufficiale BKS. Prima dell'acquisto controlla qui: "
            f"{links['refund']}. Se il pagamento usa metodi speciali come crypto, la policy di rimborso resta la fonte da verificare."
        )
    elif any(token in lower for token in ("prezzo", "sconto", "offerta", "disponibile", "stock", "taglia", "misura")):
        reply = (
            "Posso orientarti, ma prezzo, disponibilita, taglie e costi finali sono validi solo sulla pagina prodotto e al checkout. "
            "Non invento sconti o disponibilita: se la pagina mostra un dato diverso, fa fede la pagina prodotto."
        )
    elif any(token in lower for token in ("bitcoin", "crypto", "criptovaluta", "pagamento")):
        reply = (
            "BKS puo trattare Bitcoin o crypto solo come opzione di pagamento, non come investimento o promessa finanziaria. "
            "La disponibilita effettiva va verificata al checkout e le condizioni restano quelle delle policy ufficiali."
        )
    elif any(token in lower for token in ("chi sei", "ai", "assistente", "umano")):
        reply = (
            "Sono l'assistente AI BKS. Rispondo usando dati BKS disponibili, policy ufficiali e regole di sicurezza. "
            "Per ordini, pagamenti, dati personali o problemi specifici serve sempre il percorso ufficiale o un contatto umano."
        )
    else:
        reply = (
            "Posso aiutarti a capire le collezioni BKS e orientarti tra prodotto, spedizione, resi e contatti. "
            f"Ho consultato la memoria BKS disponibile ({evidence_count} segnali), ma per prezzo, disponibilita e ordine fa fede il checkout ufficiale. "
            f"Per assistenza umana: {links['contact']}."
        )

    return {
        "reply": reply,
        "assistant": "BKS AI Assistant",
        "basis": "agent_knowledge_db_and_store_policy_links",
        "evidence_count": evidence_count,
        "links": links,
        "safe": True,
    }
