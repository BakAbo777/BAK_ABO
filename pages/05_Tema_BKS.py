import streamlit as st

from streamlit_master import inject_bks_theme, render_theme_bks_page
import bks_nav


st.set_page_config(page_title="BKS — Tema", page_icon="◎", layout="wide")
bks_nav.render("tema")
inject_bks_theme()
render_theme_bks_page()
