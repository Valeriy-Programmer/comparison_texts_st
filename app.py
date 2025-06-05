import streamlit as st
from core.diff_engine import git_style_diff_html
from utils.text import strip_html_tags
from ui.layout import render_text_inputs, render_diff_result

st.set_page_config(page_title="Text Diff Viewer", layout="wide")

with open("styles/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("📄 Сравнение текстов")

text1, text2 = render_text_inputs()

if st.button("Сравнить"):
    clean1 = strip_html_tags(text1)
    clean2 = strip_html_tags(text2)

    if clean1.strip() == clean2.strip():
        st.success("✅ Тексты идентичны.")
    else:
        render_diff_result(clean1, clean2)
