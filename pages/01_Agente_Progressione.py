import streamlit as st

from streamlit_master import build_master_snapshot, render_agent_console, render_master_actions, render_progression_panel


st.set_page_config(page_title="BKS - Agente", page_icon="BKS", layout="wide")
st.title("Agente e Progressione")
st.caption("Q&A ampia, avanzamento visibile e prima azione consigliata.")

snapshot = build_master_snapshot()
render_progression_panel(snapshot)
render_agent_console(snapshot)
render_master_actions(snapshot)
