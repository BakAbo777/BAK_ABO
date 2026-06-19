"""Quick targeted check on key pages — verifies deploy fixes and prints actual console errors."""
import asyncio, json
from playwright.async_api import async_playwright

PAGES = [
    ("bks-hours",        "/collections/bks-hours"),
    ("product-sneakers", "/products/bks-abyss-sneakers"),
    ("home",             "/"),
]
STORE = "https://bakabo.club"
VIEWPORT = {"width": 390, "height": 844}


async def check(page, slug, path):
    errors = []
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    await page.goto(STORE + path, wait_until="domcontentloaded", timeout=30000)
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    await asyncio.sleep(1.5)
    await page.evaluate("window.scrollTo(0, 0)")
    try:
        await page.wait_for_load_state("networkidle", timeout=10000)
    except Exception:
        pass
    await asyncio.sleep(2)  # allow JS (heart injection, etc.) to complete

    overflow = await page.evaluate(
        "(()=>{ const d=document.documentElement.scrollWidth - window.innerWidth; return d > 8 ? d : 0; })()"
    )
    broken = await page.evaluate(
        "(()=>{ return Array.from(document.querySelectorAll('img[src]')).filter(i=>!i.complete||i.naturalWidth===0).length; })()"
    )
    transparent = await page.evaluate(
        "(()=>{ const c=document.querySelectorAll('.card-wrapper'); if(!c.length) return false; return Array.from(c).slice(0,4).some(x=>getComputedStyle(x).backgroundColor==='rgba(0, 0, 0, 0)'); })()"
    )
    hearts = await page.evaluate(
        "(()=>{ const g=document.querySelector('#product-grid,.product-grid,.collection__grid,.grid__item'); const total=document.querySelectorAll('.bks-heart-btn').length; return total + ' hearts on page | grid=' + (g?'found':'none'); })()"
    )
    print(f"\n--- {slug} ({path}) ---")
    print(f"  overflow: {overflow}px | broken images: {broken} | transparent cards: {transparent} | hearts: {hearts}")
    if errors:
        print(f"  console errors ({len(errors)}):")
        for e in list(dict.fromkeys(errors))[:5]:
            print(f"    {e[:120]}")


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel="msedge", headless=True)
        for slug, path in PAGES:
            ctx = await browser.new_context(viewport=VIEWPORT)
            page = await ctx.new_page()
            await check(page, slug, path)
            await ctx.close()
        await browser.close()


asyncio.run(main())
