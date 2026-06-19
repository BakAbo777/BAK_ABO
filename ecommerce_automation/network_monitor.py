from __future__ import annotations

import csv
import json
import socket
import ssl
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib import error, request
from urllib.parse import urlparse


DNS_FILE = Path("output/network_dns_matrix.csv")
EMAIL_FILE = Path("output/network_email_auth_matrix.csv")
ENDPOINT_FILE = Path("output/network_endpoint_matrix.csv")
SUFFIX_FILE = Path("output/network_data_suffix_matrix.csv")
REPORT_FILE = Path("output/network_monitor_report.json")
DOC_FILE = Path("docs/BKS_NETWORK_MONITOR.md")
BAKABO_STORE_DOMAIN = "bakabo.club"


TRACKING_SUFFIXES: tuple[dict[str, str], ...] = (
    {"suffix": "utm_source", "status": "approved", "purpose": "Source attribution for campaigns.", "rule": "Use only for analytics; page canonical stays clean."},
    {"suffix": "utm_medium", "status": "approved", "purpose": "Channel grouping for social/email/paid.", "rule": "Keep values stable and human-readable."},
    {"suffix": "utm_campaign", "status": "approved", "purpose": "Campaign reporting.", "rule": "Name campaigns truthfully; no deceptive offer labels."},
    {"suffix": "utm_content", "status": "approved", "purpose": "Creative or avatar variant testing.", "rule": "Use for A/B learning, not customer-specific promises."},
    {"suffix": "gclid", "status": "allowed_after_ads", "purpose": "Google Ads auto-tagging.", "rule": "Allowed when Ads are approved; do not index parameter URLs."},
    {"suffix": "fbclid", "status": "allowed_after_social", "purpose": "Meta click attribution.", "rule": "Treat as analytics signal; canonical points to the product/collection URL."},
    {"suffix": "ttclid", "status": "allowed_after_social", "purpose": "TikTok click attribution.", "rule": "Use after TikTok connector is approved."},
    {"suffix": "msclkid", "status": "allowed_after_ads", "purpose": "Microsoft Ads attribution.", "rule": "Future paid channel only after trust gate is green."},
    {"suffix": "variant", "status": "shopify_controlled", "purpose": "Shopify variant selection.", "rule": "Must match real purchasable product variants."},
    {"suffix": "ref", "status": "approval_required", "purpose": "Affiliate/referral attribution.", "rule": "Use only with transparent partner terms and no misleading endorsements."},
    {"suffix": "email_open", "status": "consent_required", "purpose": "Open/read signal.", "rule": "Only through a compliant provider and transparent consent mode."},
    {"suffix": "click_id", "status": "consent_required", "purpose": "Email/link click event.", "rule": "Store only what is needed for support/analytics and respect opt-out."},
)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _relative(root_dir: Path, path: Path) -> str:
    try:
        return path.relative_to(root_dir).as_posix()
    except ValueError:
        return path.as_posix()


def _domain_from(value: str) -> str:
    clean = (value or "").strip()
    if not clean:
        return ""
    if "://" not in clean:
        clean = f"https://{clean}"
    host = urlparse(clean).hostname or ""
    return host.lower().strip(".")


def _primary_domain(settings: Any) -> str:
    configured = _domain_from(getattr(settings, "primary_domain", ""))
    if configured:
        return configured
    public_domain = _domain_from(getattr(settings, "shopify_public_domain", ""))
    if public_domain and not public_domain.endswith(".myshopify.com"):
        return public_domain
    email = str(getattr(settings, "official_inbox_email", "") or getattr(settings, "support_email", ""))
    if "@" in email:
        return email.split("@", 1)[1].lower()
    return BAKABO_STORE_DOMAIN


def _selectors(settings: Any) -> list[str]:
    configured = str(getattr(settings, "network_dkim_selectors", "") or "google")
    selectors = [item.strip() for item in configured.split(",") if item.strip()]
    return selectors or ["google"]


def _compact(raw: str, limit: int = 220) -> str:
    text = " ".join((raw or "").split())
    return text[:limit] + ("..." if len(text) > limit else "")


def _nslookup(name: str, record_type: str) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        completed = subprocess.run(
            ["nslookup", f"-type={record_type}", name],
            capture_output=True,
            text=True,
            timeout=8,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "value": f"{type(exc).__name__}: {exc}", "ms": 0}
    elapsed = int((time.perf_counter() - started) * 1000)
    raw = f"{completed.stdout}\n{completed.stderr}".strip()
    lower = raw.lower()
    missing_markers = ("non-existent", "can't find", "cant find", "nxdomain", "nome dns inesistente", "server failed")
    ok = completed.returncode == 0 and not any(marker in lower for marker in missing_markers)
    return {"ok": ok, "value": _compact(raw), "raw": raw, "ms": elapsed}


def _a_lookup(name: str) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        infos = socket.getaddrinfo(name, 443, type=socket.SOCK_STREAM)
    except OSError as exc:
        return {"ok": False, "value": f"{type(exc).__name__}: {exc}", "ms": 0}
    elapsed = int((time.perf_counter() - started) * 1000)
    ips = sorted({info[4][0] for info in infos})
    return {"ok": bool(ips), "value": ", ".join(ips), "raw": "\n".join(ips), "ms": elapsed}


def _dns_check(cache: dict[tuple[str, str], dict[str, Any]], name: str, record_type: str, live: bool) -> dict[str, Any]:
    if not live:
        return {"ok": False, "value": "live check off", "raw": "", "ms": 0}
    key = (name, record_type)
    if key not in cache:
        cache[key] = _a_lookup(name) if record_type == "A" else _nslookup(name, record_type)
    return cache[key]


def dns_rows(settings: Any, live: bool = False) -> list[dict[str, Any]]:
    domain = _primary_domain(settings)
    cache: dict[tuple[str, str], dict[str, Any]] = {}
    rows: list[dict[str, Any]] = []

    def add(check: str, record: str, name: str, status: str, value: str, expected: str, next_action: str, ms: int = 0) -> None:
        rows.append(
            {
                "check": check,
                "record": record,
                "name": name,
                "status": status,
                "value": value,
                "expected": expected,
                "next_action": next_action,
                "ms": ms,
                "live": "yes" if live else "no",
            }
        )

    apex = _dns_check(cache, domain, "A", live)
    if live:
        status = "pass" if "23.227.38.65" in apex.get("value", "") else ("needs_review" if apex["ok"] else "needs_fix")
        value = apex["value"]
    else:
        status = "manual_pending"
        value = "Run live network check"
    add("Apex domain", "A", domain, status, value, "Shopify storefront A record, usually 23.227.38.65", "Keep apex domain pointed to Shopify and avoid duplicate storefronts.", apex.get("ms", 0))

    www_name = f"www.{domain}"
    www = _dns_check(cache, www_name, "CNAME", live)
    if live:
        status = "pass" if ("shops.myshopify.com" in www.get("value", "").lower() or www["ok"]) else "needs_fix"
        value = www["value"]
    else:
        status = "manual_pending"
        value = "Run live network check"
    add("WWW storefront", "CNAME/A", www_name, status, value, "shops.myshopify.com or valid Shopify target", "Keep www and apex consistent; redirect to one canonical domain.", www.get("ms", 0))

    mx = _dns_check(cache, domain, "MX", live)
    if live:
        status = "pass" if mx["ok"] and ("google.com" in mx.get("value", "").lower() or "mail exchanger" in mx.get("value", "").lower()) else "needs_fix"
        value = mx["value"]
    else:
        status = "manual_pending"
        value = "Run live network check"
    add("Mail exchange", "MX", domain, status, value, "Google Workspace MX or chosen official mail provider", "Keep official inbox deliverable for crew@bakabo.club.", mx.get("ms", 0))

    txt = _dns_check(cache, domain, "TXT", live)
    txt_value = txt.get("value", "")
    if live:
        status = "pass" if "v=spf1" in txt_value.lower() else "needs_fix"
        value = txt_value
    else:
        status = "manual_pending"
        value = "Run live network check"
    add("SPF", "TXT", domain, status, value, "v=spf1 including every sender used by BKS", "Add every authorized sender; avoid multiple SPF records.", txt.get("ms", 0))

    dmarc_name = f"_dmarc.{domain}"
    dmarc = _dns_check(cache, dmarc_name, "TXT", live)
    dmarc_value = dmarc.get("value", "")
    if live:
        status = "pass" if "v=dmarc1" in dmarc_value.lower() else "needs_fix"
        value = dmarc_value
    else:
        status = "manual_pending"
        value = "Run live network check"
    add("DMARC", "TXT", dmarc_name, status, value, "v=DMARC1; p=none; rua=mailto:crew@bakabo.club to start", "Create DMARC, monitor reports, then harden policy when clean.", dmarc.get("ms", 0))

    for selector in _selectors(settings):
        dkim_name = f"{selector}._domainkey.{domain}"
        dkim = _dns_check(cache, dkim_name, "TXT", live)
        dkim_value = dkim.get("value", "")
        if live:
            status = "pass" if "v=dkim1" in dkim_value.lower() else ("needs_fix" if selector == "google" else "needs_review")
            value = dkim_value
        else:
            status = "manual_pending"
            value = "Run live network check"
        add(f"DKIM selector {selector}", "TXT", dkim_name, status, value, "v=DKIM1 with 2048-bit key when supported", "Keep DKIM aligned with official sending provider.", dkim.get("ms", 0))

    return rows


def _row_status(rows: list[dict[str, Any]], check: str) -> str:
    row = next((item for item in rows if item.get("check") == check), {})
    return str(row.get("status", "manual_pending"))


def _smtp_tls_status(settings: Any, live: bool) -> tuple[str, str]:
    host = str(getattr(settings, "smtp_host", "") or "")
    port_text = str(getattr(settings, "smtp_port", "") or "")
    if not host:
        return "needs_config", "Set SMTP_HOST/SMTP_USER or keep outgoing email in approved provider."
    if not live:
        return "manual_pending", f"{host}:{port_text or '465/587'} configured; run live check."
    port = int(port_text or "465")
    started = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=6) as sock:
            if port == 465:
                context = ssl.create_default_context()
                with context.wrap_socket(sock, server_hostname=host):
                    pass
            elif port == 587:
                import smtplib  # noqa: PLC0415
                with smtplib.SMTP(host, port, timeout=6) as smtp:
                    smtp.ehlo()
                    smtp.starttls(context=ssl.create_default_context())
        elapsed = int((time.perf_counter() - started) * 1000)
        return "pass", f"{host}:{port} TLS verified in {elapsed} ms"
    except OSError as exc:
        return "needs_fix", f"{host}:{port} failed: {type(exc).__name__}: {exc}"


def email_signal_rows(settings: Any, dns: list[dict[str, Any]], live: bool = False) -> list[dict[str, str]]:
    spf = _row_status(dns, "SPF")
    dkim = _row_status(dns, "DKIM selector google")
    dmarc = _row_status(dns, "DMARC")
    mx = _row_status(dns, "Mail exchange")
    smtp_status, smtp_detail = _smtp_tls_status(settings, live)
    imap_ready = bool(
        getattr(settings, "official_inbox_imap_host", "")
        and getattr(settings, "official_inbox_imap_user", "")
        and getattr(settings, "official_inbox_imap_password", "")
    )
    unsubscribe_url = str(getattr(settings, "official_email_unsubscribe_url", "") or "")
    unsubscribe_status = "pass" if "unsubscribe" in unsubscribe_url.lower() else "manual_pending"
    return [
        {"signal": "SPF alignment", "status": "pass" if spf == "pass" else spf, "evidence": spf, "next_action": "All official senders must be included in the single SPF record."},
        {"signal": "DKIM signing", "status": "pass" if dkim == "pass" else dkim, "evidence": dkim, "next_action": "Use the active provider selector, preferably 2048-bit DKIM."},
        {"signal": "DMARC policy/reporting", "status": "pass" if dmarc == "pass" else "needs_fix", "evidence": dmarc, "next_action": "Add DMARC with aggregate reports before scaling email."},
        {"signal": "MX receive path", "status": "pass" if mx == "pass" else mx, "evidence": mx, "next_action": "Keep crew@bakabo.club reachable for official communications."},
        {"signal": "SMTP TLS", "status": smtp_status, "evidence": smtp_detail, "next_action": "Use TLS for outgoing messages; send through a provider with authentication."},
        {"signal": "DSN/bounce capture", "status": "pass" if imap_ready else "needs_config", "evidence": "IMAP configured" if imap_ready else "IMAP credentials missing", "next_action": "Read delivery-status notifications and bounces into Knowledge DB."},
        {"signal": "List-Unsubscribe", "status": unsubscribe_status, "evidence": unsubscribe_url or "missing", "next_action": "Marketing mail needs visible unsubscribe and one-click headers before scale."},
        {"signal": "Spam/reputation monitoring", "status": "manual_pending", "evidence": "Google Postmaster Tools check required", "next_action": "Monitor spam rate, bounces and domain reputation before increasing volume."},
    ]


def _http_status(url: str, live: bool) -> dict[str, Any]:
    if not live:
        return {"status": "manual_pending", "http_status": "", "ms": 0, "detail": "Run live network check"}
    started = time.perf_counter()
    try:
        req = request.Request(url, method="HEAD", headers={"User-Agent": "BKS-Master-Network-Monitor/1.0"})
        with request.urlopen(req, timeout=8) as response:  # noqa: S310 - fixed configured URLs.
            elapsed = int((time.perf_counter() - started) * 1000)
            status_code = int(response.status)
            return {"status": "pass" if 200 <= status_code < 400 else "needs_fix", "http_status": status_code, "ms": elapsed, "detail": response.url}
    except error.HTTPError as exc:
        if exc.code == 405:
            return _http_get_status(url, started)
        elapsed = int((time.perf_counter() - started) * 1000)
        return {"status": "needs_fix", "http_status": exc.code, "ms": elapsed, "detail": str(exc)}
    except (OSError, error.URLError) as exc:
        elapsed = int((time.perf_counter() - started) * 1000)
        return {"status": "needs_fix", "http_status": "", "ms": elapsed, "detail": f"{type(exc).__name__}: {exc}"}


def _http_get_status(url: str, started: float) -> dict[str, Any]:
    try:
        req = request.Request(url, method="GET", headers={"User-Agent": "BKS-Master-Network-Monitor/1.0"})
        with request.urlopen(req, timeout=8) as response:  # noqa: S310 - fixed configured URLs.
            elapsed = int((time.perf_counter() - started) * 1000)
            status_code = int(response.status)
            return {"status": "pass" if 200 <= status_code < 400 else "needs_fix", "http_status": status_code, "ms": elapsed, "detail": response.url}
    except (OSError, error.URLError, error.HTTPError) as exc:
        elapsed = int((time.perf_counter() - started) * 1000)
        code = getattr(exc, "code", "")
        return {"status": "needs_fix", "http_status": code, "ms": elapsed, "detail": f"{type(exc).__name__}: {exc}"}


def endpoint_rows(settings: Any, live: bool = False) -> list[dict[str, Any]]:
    domain = _primary_domain(settings)
    urls = [
        ("Storefront apex", f"https://{domain}", "Customer storefront should resolve over HTTPS."),
        ("Storefront www", f"https://www.{domain}", "WWW path should redirect or resolve consistently."),
        ("Contact page", f"https://{domain}/pages/contact", "Human support and Merchant trust."),
        ("Refund policy", f"https://{domain}/policies/refund-policy", "Returns and refund proof."),
        ("Sitemap", f"https://{domain}/sitemap.xml", "Canonical discovery for Google."),
    ]
    if getattr(settings, "bks_assistant_public_endpoint", ""):
        urls.append(("BKS AI assistant endpoint", settings.bks_assistant_public_endpoint, "Public endpoint for Shopify assistant widget."))
    if getattr(settings, "image_factory_url", ""):
        urls.append(("Local Image Factory", settings.image_factory_url, "Local creative network dependency."))

    rows: list[dict[str, Any]] = []
    for name, url, purpose in urls:
        result = _http_status(url, live)
        rows.append(
            {
                "endpoint": name,
                "url": url,
                "status": result["status"],
                "http_status": result["http_status"],
                "ms": result["ms"],
                "purpose": purpose,
                "detail": result["detail"],
            }
        )
    return rows


def suffix_rows() -> list[dict[str, str]]:
    return [dict(row) for row in TRACKING_SUFFIXES]


def _write_csv(root_dir: Path, path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> str:
    full_path = root_dir / path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    with full_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([{key: row.get(key, "") for key in fieldnames} for row in rows])
    return _relative(root_dir, full_path)


def _write_doc(settings: Any, summary: dict[str, Any]) -> str:
    domain = _primary_domain(settings)
    doc = f"""# BKS Network Monitor

Updated: {summary.get("checked_at", "")}

## What The Agent Watches

- DNS storefront: apex, www, MX, SPF, DKIM, DMARC.
- DSN/email delivery: bounce capture, TLS sending, unsubscribe readiness, reputation checks.
- HTTPS endpoints: storefront, policies, contact, sitemap, assistant endpoint.
- Data suffixes: UTM, click IDs and consent-sensitive email/read signals.

## Current Priority

1. Add or verify DMARC for `{domain}`:
   `v=DMARC1; p=none; rua=mailto:crew@bakabo.club; adkim=s; aspf=s`
2. Keep SPF as a single record containing every sender used by BKS.
3. Keep DKIM active for the real sending provider.
4. Configure IMAP for `crew@bakabo.club` so DSN/bounces can enter the Knowledge DB.
5. Keep UTM/click suffixes for analytics only; canonical URLs must stay clean.

## Rules

- The agent can monitor DNS/network status without approval.
- DNS changes, email sending scale, paid ads and customer outreach require human approval.
- Tracking is never a substitute for truth: prices, offers, stock, delivery and policies must match the storefront.
"""
    path = settings.root_dir / DOC_FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(doc, encoding="utf-8")
    return _relative(settings.root_dir, path)


def payload(settings: Any, live: bool = False) -> dict[str, Any]:
    dns = dns_rows(settings, live=live)
    email = email_signal_rows(settings, dns, live=live)
    endpoints = endpoint_rows(settings, live=live)
    suffixes = suffix_rows()

    dns_sheet = _write_csv(settings.root_dir, DNS_FILE, dns, ["check", "record", "name", "status", "value", "expected", "next_action", "ms", "live"])
    email_sheet = _write_csv(settings.root_dir, EMAIL_FILE, email, ["signal", "status", "evidence", "next_action"])
    endpoint_sheet = _write_csv(settings.root_dir, ENDPOINT_FILE, endpoints, ["endpoint", "url", "status", "http_status", "ms", "purpose", "detail"])
    suffix_sheet = _write_csv(settings.root_dir, SUFFIX_FILE, suffixes, ["suffix", "status", "purpose", "rule"])

    attention_statuses = {"needs_fix", "needs_config", "needs_review", "manual_pending"}
    blockers = {"needs_fix", "needs_config"}
    summary = {
        "status": "needs_fix" if any(row["status"] in blockers for row in [*dns, *email, *endpoints]) else ("manual_pending" if not live else "pass"),
        "domain": _primary_domain(settings),
        "live": live,
        "checked_at": _now(),
        "dns_pass": sum(1 for row in dns if row["status"] == "pass"),
        "dns_attention": sum(1 for row in dns if row["status"] in attention_statuses),
        "email_pass": sum(1 for row in email if row["status"] == "pass"),
        "email_attention": sum(1 for row in email if row["status"] in attention_statuses),
        "endpoints_pass": sum(1 for row in endpoints if row["status"] == "pass"),
        "endpoints_attention": sum(1 for row in endpoints if row["status"] in attention_statuses),
        "needs_fix": sum(1 for row in [*dns, *email, *endpoints] if row["status"] in blockers),
        "suffix_rules": len(suffixes),
        "dns_sheet": dns_sheet,
        "email_sheet": email_sheet,
        "endpoint_sheet": endpoint_sheet,
        "suffix_sheet": suffix_sheet,
    }
    summary["doc"] = _write_doc(settings, summary)

    report = {
        "summary": summary,
        "dns": dns,
        "email": email,
        "endpoints": endpoints,
        "suffixes": suffixes,
        "sources": [
            "https://support.google.com/mail/answer/81126",
            "https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls",
        ],
    }
    report_path = settings.root_dir / REPORT_FILE
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    report["summary"]["report"] = _relative(settings.root_dir, report_path)
    return report
