import streamlit as st

from streamlit_master import inject_bks_theme, render_management_panel


st.set_page_config(page_title="BKS — Gestione", page_icon="◎", layout="wide")
inject_bks_theme()
st.title("Gestione ◎ Servizi & Asset")
render_management_panel()
