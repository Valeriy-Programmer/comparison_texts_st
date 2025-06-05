import streamlit as st
from core.diff_engine import git_style_diff_html


def render_text_inputs():
    col1, col2 = st.columns(2)
    with col1:
        input_text1 = st.text_area("Old", "Привет!\nЭто текст номер один.", height=200)
    with col2:
        input_text2 = st.text_area("New", "Привет!\nЭто текст номер два.", height=200)
    return input_text1, input_text2


def render_diff_result(text1, text2):
    diff_html = git_style_diff_html(text1, text2)
    st.markdown(diff_html, unsafe_allow_html=True)
