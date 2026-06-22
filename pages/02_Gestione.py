"""BKS — Management Hub
Pannello centrale: system health, price audit, skills status, GMC sync, alerts.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import bks_nav
from streamlit_master import inject_bks_theme, render_management_panel

st.set_page_config(page_title="BKS Gestione", page_icon="◎", layout="wide")
bks_nav.render("gestione")
inject_bks_theme()

st.title("BKS Management Hub ◎")
st.caption(f"Sistema BKS Studio — {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# ── Tabs principali ──────────────────────────────────────────────────────────
tab_overview, tab_prices, tab_skills, tab_pages, tab_system = st.tabs([
    "Overview", "Price Audit", "Skills", "Pages", "System"
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1: OVERVIEW — status rapido
# ─────────────────────────────────────────────────────────────────────────────
with tab_overview:
    st.subheader("System Overview")
    render_management_panel()

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2: PRICE AUDIT — gmc_daily_sync report
# ─────────────────────────────────────────────────────────────────────────────
with tab_prices:
    st.subheader("Price Audit — GMC Daily Sync")

    SYNC_REPORT = BASE_DIR / "output" / "gmc_sync_report.json"

    col_run, col_fix = st.columns([2, 2])
    with col_run:
        if st.button("Run Price Audit Now", type="primary"):
            with st.spinner("Scanning 202 active products..."):
                result = subprocess.run(
                    [sys.executable, str(BASE_DIR / "scripts" / "gmc_daily_sync.py")],
                    capture_output=True, text=True, cwd=str(BASE_DIR)
                )
                if result.returncode == 0:
                    st.success("Audit complete")
                else:
                    st.error(f"Error: {result.stderr[:300]}")
                st.rerun()

    with col_fix:
        if st.button("Apply Price Fixes", type="secondary"):
            with st.spinner("Applying approved ladder corrections..."):
                result = subprocess.run(
                    [sys.executable, str(BASE_DIR / "scripts" / "fix_price_alerts.py")],
                    capture_output=True, text=True, cwd=str(BASE_DIR)
                )
                if result.returncode == 0:
                    st.success("Price fixes applied")
                    st.code(result.stdout[-500:])
                else:
                    st.error(result.stderr[:300])

    if SYNC_REPORT.exists():
        report = json.loads(SYNC_REPORT.read_text(encoding="utf-8"))
        ts = report.get("timestamp", "?")
        total = report.get("total_active", 0)
        ok = report.get("ok", 0)
        alerts = report.get("alerts", 0)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Last sync", ts[:10] if ts != "?" else "Never")
        c2.metric("Active products", total)
        c3.metric("OK prices", ok, delta=None)
        c4.metric("Price alerts", alerts, delta=None,
                  delta_color="inverse" if alerts > 0 else "normal")

        price_alerts = report.get("price_alerts", [])
        if price_alerts:
            st.warning(f"{len(price_alerts)} products with off-ladder prices")
            import pandas as pd
            df = pd.DataFrame(price_alerts)[["title", "product_type", "price", "issue"]]
            df.columns = ["Product", "Type", "Price ($)", "Issue"]
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.success("All prices on approved ladder.")

        # Price ladder reference
        with st.expander("Approved Price Ladder"):
            st.code("35  39  45  49  55  59  65  69  75  79\n85  89  95  99 105 109 115 119 125 129 135 139")
            st.caption("No product published outside this ladder without explicit justification.")
    else:
        st.info("No audit report found. Run audit first.")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 3: SKILLS — overview tutte le skill installate
# ─────────────────────────────────────────────────────────────────────────────
with tab_skills:
    st.subheader("BKS Skill System")

    SKILLS_DIR = BASE_DIR / "BKS_SKILL" / "skills"
    skills = sorted(SKILLS_DIR.glob("*/SKILL.md")) if SKILLS_DIR.exists() else []

    st.caption(f"{len(skills)} skills installed in BKS_SKILL/skills/")

    # Key skills injected in Worker
    worker_skills = {
        "bakabo-armocromia": ("ARMOCROMIA v2", "Worker BKS_SKILLS", "active"),
        "bakabo-editorial-typographer": ("TYPOGRAPHY v2", "Worker BKS_SKILLS", "active"),
        "bakabo-brand": ("BRAND VOICE", "Worker BKS_SKILLS", "active"),
        "bakabo-commercial-strategy": ("COMMERCIAL STRATEGY", "Worker BKS_SKILLS", "active"),
        "bakabo-members": ("MEMBERS METAL TIER", "Worker BKS_SKILLS", "active"),
        "bakabo-collection-guide": ("COLLECTION GUIDE", "Worker catalog/nav agent", "active"),
        "bakabo-ui-components": ("UI COMPONENTS", "theme+Worker", "new"),
        "bakabo-customer-care": ("CUSTOMER CARE", "Worker persona", "new"),
        "bakabo-page-by-page": ("PAGE-BY-PAGE SPEC", "Worker BKS_WORKFLOW", "new"),
        "bakabo-pricing": ("PRICING", "Worker BKS_WORKFLOW + gmc_daily_sync", "new"),
        "bakabo-promotions": ("PROMOTIONS", "Worker BKS_WORKFLOW + 09_Marketing", "new"),
    }

    cols = st.columns(3)
    for i, (skill_id, (name, location, status)) in enumerate(worker_skills.items()):
        badge = "🟢" if status == "active" else "🔵"
        cols[i % 3].markdown(
            f"**{badge} {name}**  \n`{skill_id}`  \n_{location}_"
        )

    st.divider()
    st.caption("All installed skills:")

    skill_names = [s.parent.name for s in skills]
    active_in_worker = set(worker_skills.keys())
    other_skills = [s for s in skill_names if s not in active_in_worker]

    with st.expander(f"All {len(other_skills)} other skills (not yet in Worker)"):
        for s in sorted(other_skills):
            st.text(f"  {s}")

# ─────────────────────────────────────────────────────────────────────────────
# TAB 4: PAGES — 43 pagine Shopify
# ─────────────────────────────────────────────────────────────────────────────
with tab_pages:
    st.subheader("Shopify Pages — 43 live")

    pages_spec = {
        "Home": ("/", "Video Hero → Piano 8 → Editorial → Reviews → Trust bar"),
        "BKS Hours editorial": ("/pages/bks-hours", "Hero 2-col → Signal bar → Product grid → Cross-collection"),
        "BKS Glyph editorial": ("/pages/bks-glyph", "Hero 2-col → Signal bar → Product grid"),
        "BKS Marker editorial": ("/pages/bks-marker", "Hero 2-col → Signal bar → Product grid"),
        "BKS Riviera editorial": ("/pages/bks-riviera", "Hero 2-col → Signal bar → Product grid"),
        "BKS Pulse editorial": ("/pages/bks-pulse", "Hero 2-col → Signal bar → Product grid"),
        "BKS Token editorial": ("/pages/bks-token", "Hero 2-col → Signal bar → Product grid"),
        "BKS Flag editorial": ("/pages/bks-flag", "Hero 2-col → Signal bar → Product grid"),
        "BKS Origin editorial": ("/pages/bks-origin", "Hero 2-col → Signal bar → Product grid"),
        "BKS Members": ("/pages/bks-members", "Gold Ring → Tier → Wishlist → Try-On"),
        "BKS Wishlist": ("/pages/bks-wishlist", "Saved items → Add to cart"),
        "BKS Man": ("/pages/bks-men", "Product types for him → Collections"),
        "BKS Woman": ("/pages/bks-woman", "Product types for her → Collections"),
        "Shopping Guide": ("/pages/bks-shopping-guide", "Armocromia → Collection selector → Ask BKS"),
        "BKS Custom": ("/pages/bks-custom", "Personalizzazione +€15 → crew@"),
        "FAQ": ("/pages/faq-domande-frequenti", "10 pre-checkout questions"),
        "BKS Verse": ("/pages/verse", "Poesia→Oggetto → Gran Giudice → Submit"),
        "Verse Hall of Fame": ("/pages/verse-hall", "Leaderboard → 21 poeti storici"),
        "About BakAbo": ("/pages/about-bakabo-1", "Studio → AI process → POD model"),
        "Contact": ("/pages/contact", "crew@ → Inbox → Social"),
        "Puffer Jackets": ("/pages/bks-puffer-jackets", "Product type grid"),
        "Windbreakers": ("/pages/bks-windbreakers", "Product type grid"),
        "Hoodies": ("/pages/bks-pullover-hoodie", "Product type grid"),
        "Swim Trunks": ("/pages/bks-swim-trunks", "Product type grid"),
        "Swimwear": ("/pages/bks-swimwear", "Product type grid"),
        "One-Piece": ("/pages/bks-one-piece-swimsuits", "Product type grid"),
        "Racerback Dresses": ("/pages/bks-racerback-dresses", "Product type grid"),
        "Athletic Shorts": ("/pages/bks-athletic-shorts", "Product type grid"),
        "Lounge Pants": ("/pages/bks-lounge-pants", "Product type grid"),
        "Sneakers": ("/pages/bks-sneakers", "Product type grid"),
        "Shoes": ("/pages/bks-shoes", "Sneakers + flip flops"),
        "Flip Flops": ("/pages/bks-flip-flop", "Product type grid"),
        "Backpacks": ("/pages/bks-backpack", "Product type grid"),
        "Travel Bags": ("/pages/bks-travel-bag", "Product type grid"),
        "Hawaiian Shirts": ("/pages/bks-hawaiian-shirt", "MISSING — to create"),
        "Beach Towels": ("/pages/bks-beach-towel", "MISSING — to create"),
        "AI Assistant": ("/pages/bks-ai-assistant", "Ask BKS interface"),
        "Collections Hub": ("/pages/bks-collections", "Overview all 8 collections"),
    }

    import pandas as pd
    rows = []
    for name, (url, spec) in pages_spec.items():
        status = "⚠ MISSING" if "MISSING" in spec else "✅ Live"
        rows.append({"Page": name, "URL": url, "Structure": spec, "Status": status})

    df = pd.DataFrame(rows)
    missing = df[df["Status"].str.contains("MISSING")]
    if not missing.empty:
        st.warning(f"{len(missing)} pages to create: {', '.join(missing['Page'].tolist())}")

    st.dataframe(
        df.style.apply(
            lambda col: ["background: #fff3cd" if "MISSING" in v else "" for v in col],
            subset=["Status"]
        ),
        use_container_width=True, hide_index=True
    )

# ─────────────────────────────────────────────────────────────────────────────
# TAB 5: SYSTEM — full management panel
# ─────────────────────────────────────────────────────────────────────────────
with tab_system:
    st.subheader("System Management")

    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Deploy Worker"):
            with st.spinner("Deploying Cloudflare Worker..."):
                r = subprocess.run(
                    [sys.executable, str(BASE_DIR / "cloudflare" / "_deploy_v5.py")],
                    capture_output=True, text=True, cwd=str(BASE_DIR)
                )
                if r.returncode == 0:
                    st.success("Worker deployed")
                else:
                    st.error(r.stderr[:300])

    with c2:
        if st.button("Run GMC Sync"):
            with st.spinner("Syncing with Google Merchant..."):
                r = subprocess.run(
                    [sys.executable, str(BASE_DIR / "scripts" / "gmc_daily_sync.py")],
                    capture_output=True, text=True, cwd=str(BASE_DIR)
                )
                if r.returncode == 0:
                    st.success("GMC sync complete")
                    st.code(r.stdout[-300:])
                else:
                    st.error(r.stderr[:300])

    with c3:
        if st.button("Pull Live Theme"):
            with st.spinner("Pulling live theme files..."):
                r = subprocess.run(
                    [sys.executable, str(BASE_DIR / "scripts" / "_pull_live_members.py")],
                    capture_output=True, text=True, cwd=str(BASE_DIR)
                )
                if r.returncode == 0:
                    st.success("Live files pulled")
                else:
                    st.error(r.stderr[:300])

    st.divider()
    st.caption("Full system panel:")
    # Inline existing management panel (command center + monitoring only)
    from streamlit_master import render_command_center, render_monitoring
    mgmt_tabs = st.tabs(["Commands", "Monitoring"])
    with mgmt_tabs[0]:
        render_command_center()
    with mgmt_tabs[1]:
        render_monitoring()
