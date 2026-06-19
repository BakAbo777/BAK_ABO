"""BKS Studio — Shared sidebar navigation with live progress indicators."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import streamlit as st

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

_PAGES = [
    ("◎", "BKS Algorithm",     "BKS_Algorithm"),
    ("◈", "Agente",             "Agente_Progressione"),
    ("⊡", "Gestione",           "Gestione"),
    ("◉", "Social",             "Social"),
    ("◫", "Project Manager",    "Project_Manager"),
    ("◧", "Tema BKS",           "Tema_BKS"),
    ("▦", "Catalogo",           "Catalogo"),
    ("◐", "Image Factory",      "Image_Factory"),
    ("◑", "Camerino",           "Camerino"),
    ("◒", "Google Merchant",    "Google_Merchant"),
    ("◕", "Marketing",          "Marketing"),
    ("◔", "Analytics",          "Analytics"),
]

_COLL_ACCENTS = {
    "bks-hours":   "#c8c4be",
    "bks-glyph":   "#9b7cba",
    "bks-marker":  "#e03c2d",
    "bks-riviera": "#3daed6",
    "bks-pulse":   "#e87c2b",
    "bks-token":   "#4cae8c",
    "bks-flag":    "#d4a017",
    "bks-origin":  "#6aab48",
}


@st.cache_data(ttl=90, show_spinner=False)
def _load_data() -> dict[str, Any]:
    try:
        from ecommerce_automation.bks_algorithm import BKSAlgorithm
        algo = BKSAlgorithm()
        s = algo.summary()
        health = algo.collection_health()
        return {
            "ok": True,
            "total": s.get("total", 0),
            "ready": s.get("ready", 0),
            "fix": s.get("fix", 0),
            "critical": s.get("critical", 0),
            "avg_score": round(s.get("avg_score", 0), 1),
            "health": [
                {
                    "handle": h.handle,
                    "status": h.status,
                    "accent": _COLL_ACCENTS.get(h.handle, "#888"),
                    "avg_score": h.avg_score,
                    "product_count": h.product_count,
                }
                for h in health
            ],
        }
    except Exception:
        return {"ok": False, "total": 0, "ready": 0, "fix": 0, "critical": 0, "avg_score": 0, "health": []}


def render(active_page: str = "") -> None:
    """Inject BKS sidebar: header + live progress indicators."""
    with st.sidebar:
        # ── Wordmark ─────────────────────────────────────────────────────────
        st.markdown(
            """
            <div style="
                padding: 10px 0 10px;
                border-bottom: 1px solid #c9b79c44;
                margin-bottom: 14px;
                text-align: left;
            ">
              <span style="
                font-size: 0.78rem;
                letter-spacing: .26em;
                font-weight: 700;
                color: #b8a165;
                text-transform: uppercase;
              ">BKS STUDIO</span>
              <span style="
                display: block;
                font-size: 0.58rem;
                letter-spacing: .12em;
                color: #999;
                margin-top: 1px;
              ">bakabo.club</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── Progress indicators ───────────────────────────────────────────────
        data = _load_data()

        if data["ok"] and data["total"] > 0:
            total = data["total"]
            ready = data["ready"]
            critical = data["critical"]
            fix = data["fix"]
            score = data["avg_score"]

            # Catalog progress bar
            ready_pct = ready / total if total else 0
            score_color = (
                "#2f9e44" if score >= 80 else
                "#e67700" if score >= 60 else
                "#c92a2a"
            )

            st.markdown(
                '<p style="font-size:0.58rem;letter-spacing:.14em;color:#888;'
                'text-transform:uppercase;margin:0 0 4px;">Catalog</p>',
                unsafe_allow_html=True,
            )
            st.progress(ready_pct)
            st.markdown(
                f'<p style="font-size:0.65rem;color:#555;margin:-6px 0 2px;">'
                f'{ready}/{total} ready &nbsp;·&nbsp; '
                f'<span style="color:{score_color};font-weight:600;">◎ {score}</span>'
                f'</p>',
                unsafe_allow_html=True,
            )

            # P0 critical alert
            if critical > 0:
                st.markdown(
                    f'<div style="font-size:0.62rem;color:#c92a2a;'
                    f'background:#fff0f0;border-left:3px solid #c92a2a;'
                    f'padding:3px 7px;border-radius:2px;margin:6px 0 4px;">'
                    f'⚠ {critical} critical &nbsp;·&nbsp; {fix} to fix'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            # Collection health dots
            if data["health"]:
                st.markdown(
                    '<p style="font-size:0.58rem;letter-spacing:.14em;color:#888;'
                    'text-transform:uppercase;margin:10px 0 5px;">Collections</p>',
                    unsafe_allow_html=True,
                )
                _status_icon = {"ok": "●", "warn": "◐", "critical": "!", "empty": "○"}
                _status_color = {"ok": "#2f9e44", "warn": "#e67700", "critical": "#c92a2a", "empty": "#bbb"}

                rows = []
                for h in data["health"]:
                    icon = _status_icon.get(h["status"], "·")
                    col = _status_color.get(h["status"], "#999")
                    short = h["handle"].replace("bks-", "").upper()[:3]
                    rows.append(
                        f'<span title="{h["handle"]} — {h["avg_score"]} · {h["product_count"]} prod" '
                        f'style="color:{col};font-size:0.65rem;margin-right:5px;cursor:default;">'
                        f'{icon} {short}</span>'
                    )

                # Two rows of 4
                st.markdown(
                    '<div style="line-height:1.8;">'
                    + "".join(rows[:4]) + "<br>"
                    + "".join(rows[4:])
                    + "</div>",
                    unsafe_allow_html=True,
                )

        st.markdown(
            '<hr style="border:none;border-top:1px solid #c9b79c33;margin:14px 0 6px;">',
            unsafe_allow_html=True,
        )
