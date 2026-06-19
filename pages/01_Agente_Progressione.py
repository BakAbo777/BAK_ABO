import streamlit as st

from streamlit_master import (
    build_master_snapshot,
    inject_bks_theme,
    render_agent_console,
    render_agent_routine,
    render_master_actions,
    render_progression_panel,
)
import bks_nav


st.set_page_config(page_title="BKS — Agente", page_icon="◎", layout="wide")
bks_nav.render("agente")
inject_bks_theme()
st.title("Agente ◎ Progressione")
st.caption("Routine operativa, Q&A, avanzamento fasi, prossima azione.")

snapshot = build_master_snapshot()

tabs = st.tabs(["Routine", "Progressione", "Q&A", "Azioni"])
with tabs[0]:
    render_agent_routine(snapshot)
with tabs[1]:
    render_progression_panel(snapshot)
with tabs[2]:
    render_agent_console(snapshot)
with tabs[3]:
    render_master_actions(snapshot)
