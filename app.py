import streamlit as st
from utils.text import strip_html_tags
from ui.layout import render_text_inputs, render_diff_result

st.set_page_config(page_title="Text Diff Viewer", layout="wide")

# streamlit run app.py

with open("styles/styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("📄 Сравнение текстов")

compare_mode = st.radio(
    "Режим сравнения:",
    ("Только текст (без тегов)", "Исходный текст (вместе с тегами)"),
)

text1, text2 = render_text_inputs()

if st.button("Сравнить"):
    if compare_mode == "Только текст (без тегов)":
        clean1 = strip_html_tags(text1)
        clean2 = strip_html_tags(text2)
    else:
        clean1 = text1
        clean2 = text2

    if clean1.strip() == clean2.strip():
        st.success("✅ Тексты идентичны.")
    else:
        render_diff_result(clean1, clean2)
