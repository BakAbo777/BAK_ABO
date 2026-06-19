import streamlit as st

from streamlit_master import inject_bks_theme, render_management_panel
import bks_nav


st.set_page_config(page_title="BKS — Gestione", page_icon="◎", layout="wide")
bks_nav.render("gestione")
inject_bks_theme()
st.title("Gestione ◎ Servizi & Asset")
render_management_panel()
