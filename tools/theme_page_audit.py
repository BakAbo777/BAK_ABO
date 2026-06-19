"""BKS Theme Page Audit — Playwright screenshot + visual checks.

Tests all BKS theme pages at mobile/desktop viewports.
Saves screenshots to output/page_audit/{viewport}/{slug}.png
Reports: overflow, console errors, card visibility, image presence.

Run: python tools/theme_page_audit.py [--url https://bakabo.club]
"""
from __future__ import annotations
import asyncio, json, time, argparse
from pathlib import Path
from datetime import datetime, timezone

STORE_URL = "https://bakabo.club"

PAGES = [
    ("home",                "/"),
    ("collections-hub",     "/pages/bks-collections"),
    ("bks-hours",           "/collections/bks-hours"),
    ("bks-glyph",           "/collections/bks-glyph"),
    ("bks-marker",          "/collections/bks-marker"),
    ("bks-riviera",         "/collections/bks-riviera"),
    ("bks-pulse",           "/collections/bks-pulse"),
    ("bks-token",           "/collections/bks-token"),
    ("bks-flag",            "/collections/bks-flag"),
    ("bks-origin",          "/collections/bks-origin"),
    ("product-sneakers",    "/products/bks-abyss-sneakers"),
    ("product-puffer",      "/products/bks-glyph-cross-puffer"),
    ("members",             "/pages/bks-members"),
    ("ai-assistant",        "/pages/bks-ai-assistant"),
    ("custom-request",      "/pages/bks-custom"),
    ("all-products",        "/collections/all"),
]

VIEWPORTS = [
    ("mobile",  {"width": 390, "height": 844}),
    ("tablet",  {"width": 768, "height": 1024}),
    ("desktop", {"width": 1440, "height": 900}),
]

CHECKS = [
    # (label, JS expression that returns a problem string or null)
    ("overflow_x",
     "(()=>{ const diff = document.documentElement.scrollWidth - window.innerWidth; return diff > 8 ? `overflow: ${document.documentElement.scrollWidth}px > ${window.innerWidth}px (+${diff}px)` : null; })()"),
    ("no_images",
     "(()=>{ const imgs=document.querySelectorAll('img[src]:not([loading=\"lazy\"]):not([data-srcset]):not(.motion-reduce)'); const failed=Array.from(imgs).filter(i=>i.src&&!i.src.startsWith('data:')&&(!i.complete||i.naturalWidth===0)); return failed.length ? `${failed.length} broken images` : null; })()"),
    ("console_errors",
     "null"),  # collected separately via page.on('console')
    ("card_visibility",
     "(()=>{ const wrappers=document.querySelectorAll('.card-wrapper'); if(!wrappers.length) return null; const bad=Array.from(wrappers).slice(0,6).filter(c=>{ const bg=getComputedStyle(c).backgroundColor; return bg==='rgba(0, 0, 0, 0)'||bg==='transparent'; }); return bad.length > 0 ? `${bad.length} card-wrapper(s) transparent` : null; })()"),
    ("hearts_present",
     "(()=>{ const grid=document.querySelector('#product-grid, .product-grid, .collection__grid, .grid.product-grid'); if(!grid) return null; const hearts=grid.querySelectorAll('.bks-heart-btn'); return hearts.length > 0 ? null : 'no heart buttons on product cards'; })()"),
]


IGNORE_ERRORS = (
    "shop.app",                    # CSP framing — Shopify-side, harmless
    "account.bakabo.club",         # Customer Accounts v2 cross-origin iframe warnings
    "Unsafe attempt to load URL",  # generic cross-origin iframe security warning from Shopify auth
    "status of 403",               # shop.app/pay/hop 403 — Shop Pay widget, Shopify-side
    "X-Frame-Options",             # deprecated ALLOW-FROM directive — browser compat warning, Shopify server header
)


async def audit_page(page, slug: str, url: str, viewport_name: str, out_dir: Path):
    console_errs: list[str] = []

    def _on_console(m):
        if m.type == "error" and not any(k in m.text for k in IGNORE_ERRORS):
            console_errs.append(m.text)

    page.on("console", _on_console)

    try:
        resp = await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        status = resp.status if resp else 0
    except Exception as e:
        return {"slug": slug, "viewport": viewport_name, "url": url, "status": "TIMEOUT", "error": str(e)}

    # Scroll to trigger lazy-loaded images, then wait for network
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    await asyncio.sleep(0.8)
    await page.evaluate("window.scrollTo(0, 0)")
    try:
        await page.wait_for_load_state("networkidle", timeout=10000)
    except Exception:
        pass
    await asyncio.sleep(0.5)

    # Screenshot
    img_path = out_dir / f"{viewport_name}_{slug}.png"
    await page.screenshot(path=str(img_path), full_page=True)

    # Run checks
    results = {"slug": slug, "viewport": viewport_name, "url": url, "status": status, "checks": {}}
    for label, js in CHECKS:
        if label == "console_errors":
            if console_errs:
                unique = list(dict.fromkeys(console_errs))  # dedupe while preserving order
                results["checks"][label] = f"{len(console_errs)} errors"
                results["console_error_msgs"] = unique[:10]
            continue
        try:
            problem = await page.evaluate(js)
            if problem:
                results["checks"][label] = problem
        except Exception as e:
            results["checks"][label] = f"check failed: {e}"

    results["screenshot"] = str(img_path)
    results["ok"] = not results["checks"]
    return results


async def main_async(store_url: str):
    from playwright.async_api import async_playwright

    out_dir = Path("output/page_audit")
    out_dir.mkdir(parents=True, exist_ok=True)

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "store": store_url,
        "pages": [],
        "summary": {"ok": 0, "fail": 0, "total": 0}
    }

    EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

    async with async_playwright() as p:
        import os as _os
        for launch_kwargs in [
            {"channel": "msedge",  "headless": True},
            {"channel": "chrome",  "headless": True},
            {"executable_path": EDGE_PATH, "headless": True} if _os.path.exists(EDGE_PATH) else {},
            {"headless": True},  # fallback: requires playwright chromium download
        ]:
            if not launch_kwargs:
                continue
            try:
                browser = await p.chromium.launch(**launch_kwargs)
                print(f"Browser launched: {launch_kwargs.get('channel', launch_kwargs.get('executable_path', 'default'))}")
                break
            except Exception as ex:
                print(f"Launch failed ({launch_kwargs.get('channel', 'exec')}): {ex}")
        else:
            raise RuntimeError("No browser could be launched. Install Chromium with: python -m playwright install chromium")

        for vp_name, vp_size in VIEWPORTS:
            print(f"\n=== Viewport: {vp_name} ({vp_size['width']}x{vp_size['height']}) ===")

            for slug, path in PAGES:
                url = store_url.rstrip("/") + path
                print(f"  {slug} ... ", end="", flush=True)
                context = await browser.new_context(viewport=vp_size)
                page = await context.new_page()
                result = await audit_page(page, slug, url, vp_name, out_dir)
                await context.close()
                report["pages"].append(result)
                report["summary"]["total"] += 1
                if result.get("ok"):
                    report["summary"]["ok"] += 1
                    print("OK")
                else:
                    report["summary"]["fail"] += 1
                    issues = list(result.get("checks", {}).values())
                    print(f"FAIL: {'; '.join(issues)}")

        await browser.close()

    report_path = Path("output/page_audit_report.json")
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    csv_path = Path("output/page_audit_failures.csv")
    import csv as _csv
    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        w = _csv.DictWriter(f, fieldnames=["slug", "viewport", "url", "status", "issues", "screenshot"])
        w.writeheader()
        for pg in report["pages"]:
            if not pg.get("ok"):
                w.writerow({
                    "slug":       pg["slug"],
                    "viewport":   pg["viewport"],
                    "url":        pg["url"],
                    "status":     pg.get("status", ""),
                    "issues":     "; ".join(pg.get("checks", {}).values()),
                    "screenshot": pg.get("screenshot", ""),
                })

    total = report["summary"]["total"]
    ok    = report["summary"]["ok"]
    fail  = report["summary"]["fail"]
    print(f"\n=== AUDIT COMPLETE: {ok}/{total} OK  |  {fail} FAILURES ===")
    print(f"Report: {report_path}")
    print(f"Failures CSV: {csv_path}")
    print(f"Screenshots: {out_dir}/")
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=STORE_URL)
    args = parser.parse_args()
    asyncio.run(main_async(args.url))


if __name__ == "__main__":
    main()
