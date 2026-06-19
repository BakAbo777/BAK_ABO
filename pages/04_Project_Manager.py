import streamlit as st

from streamlit_master import inject_bks_theme, render_project_manager


st.set_page_config(page_title="BKS — Project Manager", page_icon="◎", layout="wide")
inject_bks_theme()
st.title("Project Manager ◎ BKS Studio")
render_project_manager()
