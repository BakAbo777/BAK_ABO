import streamlit as st

from streamlit_master import render_project_manager


st.set_page_config(page_title="BKS - Project Manager", page_icon="BKS", layout="wide")
st.title("Project Manager")
render_project_manager()
