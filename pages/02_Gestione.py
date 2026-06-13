import streamlit as st

from streamlit_master import render_management_panel


st.set_page_config(page_title="BKS - Gestione", page_icon="BKS", layout="wide")
st.title("Gestione")
render_management_panel()
