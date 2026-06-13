import streamlit as st

from streamlit_master import render_social_panel


st.set_page_config(page_title="BKS - Social", page_icon="BKS", layout="wide")
st.title("Social")
render_social_panel()
