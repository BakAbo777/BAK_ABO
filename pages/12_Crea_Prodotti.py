"""BKS — Product Creation Panel
Gestione del processo iniziale: matrice collezione × tipo, crea mancanti, rework queue.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import bks_nav
from streamlit_master import inject_bks_theme

st.set_page_config(page_title="BKS Crea Prodotti", page_icon="⊕", layout="wide")
bks_nav.render("crea")
inject_bks_theme()

# ── Constants ────────────────────────────────────────────────────────────────
COLLECTIONS = ["hours", "glyph", "marker", "riviera", "pulse", "token", "flag", "origin"]

DESIRED: dict[str, list[str]] = {
    "hours":   ["tee", "puffer", "lounge_pants", "windbreaker", "travel_bag"],
    "glyph":   ["tee", "puffer", "backpack", "sneakers", "travel_bag"],
    "marker":  ["tee", "hoodie", "windbreaker", "backpack", "shorts"],
    "riviera": ["tee", "swim_trunks", "beach_towel", "flip_flops", "hawaiian", "travel_bag"],
    "pulse":   ["tee", "hoodie", "windbreaker", "sneakers", "backpack"],
    "token":   ["tee", "backpack", "sneakers", "windbreaker", "travel_bag"],
    "flag":    ["tee", "hoodie", "beach_towel", "shorts", "windbreaker"],
    "origin":  ["tee", "lounge_pants", "beach_towel", "windbreaker", "travel_bag"],
}

ALL_TYPES = sorted({pt for pts in DESIRED.values() for pt in pts})

BLUEPRINT_TYPES = [
    "tee", "puffer", "hoodie", "lounge_pants", "windbreaker",
    "backpack", "sneakers", "shorts", "one_piece", "swim_trunks",
    "travel_bag", "beach_towel", "flip_flops", "hawaiian", "pullover",
]

# Title suffix → type key (after ™ in title)
TYPE_SUFFIX: dict[str, str] = {
    "Tee": "tee",
    "T-Shirt": "tee",
    "Women's Tee": "tee",
    "Puffer": "puffer",
    "Puffer Jacket": "puffer",
    "Hoodie": "hoodie",
    "Pullover Hoodie": "hoodie",
    "Lounge Pants": "lounge_pants",
    "Windbreaker": "windbreaker",
    "Windbreaker Jacket": "windbreaker",
    "Backpack": "backpack",
    "Sneakers": "sneakers",
    "Shorts": "shorts",
    "Athletic Long Shorts": "shorts",
    "Athletic Shorts": "shorts",
    "Swim Trunks": "swim_trunks",
    "Travel Bag": "travel_bag",
    "Beach Towel": "beach_towel",
    "Flip Flops": "flip_flops",
    "Flip-Flops": "flip_flops",
    "Hawaiian": "hawaiian",
    "Hawaiian Shirt": "hawaiian",
    "Pullover": "pullover",
    "One Piece": "one_piece",
    "One-Piece Swimsuit": "one_piece",
}

LOG_PATH = BASE_DIR / "ecommerce_automation" / "design_batch_log.json"
REWORK_LOG = BASE_DIR / "output" / "pipeline_retry_rework.log"
PID_FILE = BASE_DIR / "output" / "pipeline_rework.pid"
PIPELINE = BASE_DIR / "scripts" / "_production_pipeline.py"


# ── Helpers ──────────────────────────────────────────────────────────────────
@st.cache_data(ttl=15, show_spinner=False)
def load_log() -> dict:
    if LOG_PATH.exists():
        return json.loads(LOG_PATH.read_text("utf-8"))
    return {}


def extract_type(title: str) -> str | None:
    """Extract product type key from title like 'BKS Hours Clock™ Lounge Pants'."""
    if "™" not in title:
        return None
    suffix = title.split("™", 1)[1].strip()
    # Try longest match first
    for label in sorted(TYPE_SUFFIX, key=len, reverse=True):
        if suffix.lower().startswith(label.lower()):
            return TYPE_SUFFIX[label]
    return None


def build_matrix(log: dict) -> dict[tuple[str, str], str]:
    """Return {(collection, type): status} for all log entries."""
    matrix: dict[tuple[str, str], str] = {}
    for v in log.values():
        if not isinstance(v, dict):
            continue
        col = v.get("collection", "")
        title = v.get("title", "")
        ptype = extract_type(title)
        if col and ptype:
            matrix[(col, ptype)] = v.get("status", "?")
    return matrix


def pid_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False


def get_rework_pid() -> int | None:
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
            return pid if pid_running(pid) else None
        except Exception:
            return None
    return None


def status_badge(status: str) -> str:
    badges = {
        "updated":          "🟢",
        "restored_phase1":  "🟢",
        "needs_rework":     "🟡",
        "dry_run":          "🟡",
        "excluded":         "⚫",
        "no_design":        "⚫",
        "missing":          "🔴",
    }
    return badges.get(status, "⚪")


# ── Page header ──────────────────────────────────────────────────────────────
st.title("⊕ Crea Prodotti")
st.caption("Matrice collezione × tipo — processo iniziale creazione oggetti BKS")

tab_status, tab_matrix, tab_create, tab_rework = st.tabs([
    "Status", "Matrice", "Crea Mancanti", "Rework Queue"
])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1: STATUS
# ─────────────────────────────────────────────────────────────────────────────
with tab_status:
    log = load_log()
    counts = Counter(
        v.get("status", "?")
        for v in log.values()
        if isinstance(v, dict)
    )
    matrix = build_matrix(log)

    # Count missing (in DESIRED but not in matrix)
    missing_pairs = [
        (col, pt)
        for col, pts in DESIRED.items()
        for pt in pts
        if (col, pt) not in matrix
    ]
    total_desired = sum(len(pts) for pts in DESIRED.values())

    st.subheader("Pipeline Log — Stato corrente")

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("✅ Updated", counts.get("updated", 0) + counts.get("restored_phase1", 0))
    c2.metric("🟡 Needs Rework", counts.get("needs_rework", 0))
    c3.metric("🟡 Dry Run", counts.get("dry_run", 0))
    c4.metric("🔴 Mancanti", len(missing_pairs), help=f"Su {total_desired} prodotti nel DESIRED matrix")
    c5.metric("⚫ Excluded", counts.get("excluded", 0) + counts.get("no_design", 0))
    c6.metric("📦 Totale log", len(log))

    st.divider()

    # Score distribution for updated products
    scores = [
        v.get("result", {}).get("bks_score", 0)
        for v in log.values()
        if isinstance(v, dict) and v.get("status") == "updated"
        and isinstance(v.get("result", {}).get("bks_score"), (int, float))
    ]

    if scores:
        st.subheader("Score Distribution (updated products)")
        buckets = {"≥23": 0, "21-22": 0, "20": 0, "<20": 0}
        for s in scores:
            if s >= 23:
                buckets["≥23"] += 1
            elif s >= 21:
                buckets["21-22"] += 1
            elif s >= 20:
                buckets["20"] += 1
            else:
                buckets["<20"] += 1

        bc1, bc2, bc3, bc4 = st.columns(4)
        bc1.metric("Score ≥ 23 (top)", buckets["≥23"])
        bc2.metric("Score 21-22 (ok)", buckets["21-22"])
        bc3.metric("Score 20 (borderline)", buckets["20"])
        bc4.metric("Score < 20 (rework)", buckets["<20"])

    st.divider()

    # Missing pairs list
    if missing_pairs:
        st.subheader(f"🔴 {len(missing_pairs)} prodotti mancanti nel DESIRED matrix")
        col_a, col_b = st.columns(2)
        half = len(missing_pairs) // 2 + len(missing_pairs) % 2
        with col_a:
            for col, pt in missing_pairs[:half]:
                st.markdown(f"- **{col}** / {pt}")
        with col_b:
            for col, pt in missing_pairs[half:]:
                st.markdown(f"- **{col}** / {pt}")
    else:
        st.success("Tutti i prodotti del DESIRED matrix sono presenti nel log.")

    if st.button("Aggiorna dati", key="refresh_status"):
        st.cache_data.clear()
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# TAB 2: MATRICE
# ─────────────────────────────────────────────────────────────────────────────
with tab_matrix:
    log = load_log()
    matrix = build_matrix(log)

    st.subheader("Matrice Prodotti — Collezione × Tipo")
    st.caption("🟢 updated/restored  🟡 needs_rework/dry_run  🔴 mancante  ⚫ excluded")

    # Build all_types that appear in DESIRED
    desired_types = sorted({pt for pts in DESIRED.values() for pt in pts})

    # Header row
    header_cols = st.columns([1.4] + [1] * len(COLLECTIONS))
    header_cols[0].markdown("**Tipo**")
    for i, col in enumerate(COLLECTIONS):
        header_cols[i + 1].markdown(f"**{col.upper()}**")

    st.markdown(
        "<hr style='margin:4px 0 8px;border-color:#c9b79c44'>",
        unsafe_allow_html=True,
    )

    for pt in desired_types:
        row_cols = st.columns([1.4] + [1] * len(COLLECTIONS))
        row_cols[0].markdown(f"`{pt}`")
        for i, col in enumerate(COLLECTIONS):
            if pt not in DESIRED.get(col, []):
                row_cols[i + 1].markdown("—")
            else:
                status = matrix.get((col, pt), "missing")
                badge = status_badge(status)
                short = {
                    "updated": "ok",
                    "restored_phase1": "ok",
                    "needs_rework": "rework",
                    "dry_run": "dry",
                    "excluded": "excl",
                    "no_design": "none",
                    "missing": "manca",
                }.get(status, status[:4])
                row_cols[i + 1].markdown(f"{badge} {short}")

    if st.button("Aggiorna matrice", key="refresh_matrix"):
        st.cache_data.clear()
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# TAB 3: CREA MANCANTI
# ─────────────────────────────────────────────────────────────────────────────
with tab_create:
    st.subheader("Crea Prodotti Mancanti")
    st.info(
        "Questa operazione **crea i prodotti Printify** (struttura + prezzi) "
        "per le coppie (collezione, tipo) non ancora presenti. "
        "Non genera immagini — usa il pipeline rework per quello."
    )

    col_filter, type_filter = st.columns(2)
    with col_filter:
        coll_choice = st.selectbox(
            "Collezione",
            ["Tutte"] + COLLECTIONS,
            key="create_coll",
        )
    with type_filter:
        type_choice = st.selectbox(
            "Tipo prodotto",
            ["Tutti"] + ALL_TYPES,
            key="create_type",
        )

    # Preview which products would be created
    log = load_log()
    matrix = build_matrix(log)

    filter_col = None if coll_choice == "Tutte" else coll_choice
    filter_type = None if type_choice == "Tutti" else type_choice

    preview = [
        (col, pt)
        for col, pts in DESIRED.items()
        for pt in pts
        if (filter_col is None or col == filter_col)
        and (filter_type is None or pt == filter_type)
        and (col, pt) not in matrix
    ]

    if preview:
        st.markdown(f"**{len(preview)} prodotti da creare:**")
        for col, pt in preview:
            st.markdown(f"  🔴 {col} / {pt}")
    else:
        st.success("Nessun prodotto mancante per i filtri selezionati.")

    if preview:
        st.divider()
        if st.button(
            f"⊕ Crea {len(preview)} prodotti",
            type="primary",
            key="btn_create_missing",
        ):
            cmd = [sys.executable, str(PIPELINE), "--create-missing"]
            if filter_col:
                cmd += ["--collection", filter_col]
            if filter_type:
                cmd += ["--type", filter_type]

            with st.spinner(f"Creando {len(preview)} prodotti..."):
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=str(BASE_DIR),
                    encoding="utf-8",
                    errors="replace",
                )

            if result.returncode == 0:
                st.success("Creazione completata.")
            else:
                st.error(f"Errore (exit {result.returncode})")

            output = (result.stdout or "") + (result.stderr or "")
            if output.strip():
                st.code(output[-4000:], language="text")

            st.cache_data.clear()
            st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# TAB 4: REWORK QUEUE
# ─────────────────────────────────────────────────────────────────────────────
with tab_rework:
    log = load_log()

    rework_entries = [
        {
            "id": pid,
            "title": v.get("title", pid)[:50],
            "collection": v.get("collection", "?"),
            "status": v.get("status", "?"),
            "score": v.get("result", {}).get("bks_score", "—"),
            "reason": v.get("result", {}).get("body", v.get("result", {}).get("bks_feedback", ""))[:60],
        }
        for pid, v in log.items()
        if isinstance(v, dict) and v.get("status") in ("needs_rework", "dry_run")
    ]

    st.subheader(f"Rework Queue — {len(rework_entries)} prodotti")

    active_pid = get_rework_pid()

    if active_pid:
        st.warning(f"Pipeline rework attiva (PID {active_pid})")
        if st.button("Aggiorna log", key="btn_refresh_log"):
            st.rerun()
    else:
        col_run, col_force = st.columns([2, 2])
        with col_run:
            if st.button(
                f"▶ Avvia Rework ({len(rework_entries)} prodotti)",
                type="primary",
                key="btn_rework",
                disabled=len(rework_entries) == 0,
            ):
                (BASE_DIR / "output").mkdir(exist_ok=True)
                log_f = open(str(REWORK_LOG), "w", encoding="utf-8", errors="replace")
                proc = subprocess.Popen(
                    [sys.executable, "-u", str(PIPELINE), "--retry-rework"],
                    stdout=log_f,
                    stderr=subprocess.STDOUT,
                    cwd=str(BASE_DIR),
                )
                PID_FILE.write_text(str(proc.pid))
                st.success(f"Pipeline avviata in background (PID {proc.pid})")
                st.rerun()

        with col_force:
            st.caption("Vuoi rigenerare anche i prodotti già approvati?")
            if st.button("⚠ Forza Rigenerazione Totale", key="btn_force", type="secondary"):
                st.session_state["confirm_force"] = True

            if st.session_state.get("confirm_force"):
                st.error("ATTENZIONE: sovrascriverà tutti i 137 prodotti approvati!")
                if st.button("Conferma --force", key="btn_force_confirm", type="primary"):
                    (BASE_DIR / "output").mkdir(exist_ok=True)
                    log_f = open(str(REWORK_LOG), "w", encoding="utf-8", errors="replace")
                    proc = subprocess.Popen(
                        [sys.executable, "-u", str(PIPELINE), "--force"],
                        stdout=log_f,
                        stderr=subprocess.STDOUT,
                        cwd=str(BASE_DIR),
                    )
                    PID_FILE.write_text(str(proc.pid))
                    st.session_state["confirm_force"] = False
                    st.success(f"Force pipeline avviata (PID {proc.pid})")
                    st.rerun()

    # Table of rework products
    if rework_entries:
        st.divider()
        import pandas as pd
        df = pd.DataFrame(rework_entries)[["collection", "title", "status", "score", "reason"]]
        df.columns = ["Collezione", "Titolo", "Status", "Score", "Motivo"]
        st.dataframe(df, use_container_width=True, hide_index=True)

    # Live log viewer
    st.divider()
    st.subheader("Pipeline Log")

    if REWORK_LOG.exists():
        log_text = REWORK_LOG.read_text(encoding="utf-8", errors="replace")
        if log_text.strip():
            lines = log_text.splitlines()
            last_lines = "\n".join(lines[-60:])
            st.code(last_lines, language="text")
            st.caption(f"{REWORK_LOG} — {len(lines)} righe totali")
        else:
            st.caption("Log file vuoto.")
    else:
        st.caption("Nessun log disponibile. Avvia il rework per generarlo.")

    if active_pid:
        st.caption("Auto-refresh: clicca 'Aggiorna log' per vedere gli ultimi aggiornamenti.")
