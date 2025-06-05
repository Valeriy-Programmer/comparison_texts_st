import streamlit as st
import difflib
from bs4 import BeautifulSoup
import html as html_module


def strip_html_tags(html_text):
    """Возвращает только текст без HTML-тегов."""
    return BeautifulSoup(html_text, "html.parser").get_text()


def highlight_inline_changes(old_line, new_line):
    """Подсвечивает различия между двумя строками."""
    sequence_matcher = difflib.SequenceMatcher(None, old_line, new_line)
    highlighted_old = []
    highlighted_new = []

    for tag, i1, i2, j1, j2 in sequence_matcher.get_opcodes():
        if tag == "replace" or tag == "delete":
            highlighted_old.append(
                f"<span style='background-color:#ffbaba'>{html_module.escape(old_line[i1:i2])}</span>"
            )
        else:
            highlighted_old.append(html_module.escape(old_line[i1:i2]))

        if tag == "replace" or tag == "insert":
            highlighted_new.append(
                f"<span style='background-color:#b2ffb2'>{html_module.escape(new_line[j1:j2])}</span>"
            )
        else:
            highlighted_new.append(html_module.escape(new_line[j1:j2]))

    return "".join(highlighted_old), "".join(highlighted_new)


def git_style_diff_html(text1, text2):
    lines1 = text1.splitlines()
    lines2 = text2.splitlines()
    diff = list(
        difflib.unified_diff(lines1, lines2, fromfile="Old", tofile="New", lineterm="")
    )

    table_rows = []
    old_line_no = 0
    new_line_no = 0

    def wrap_line(old_lineno, new_lineno, action, content, bg_color, raw_text=None):
        if raw_text is None:
            raw_text = content

        escaped_text = html_module.escape(raw_text).replace("'", "\\'")
        show_button = action in ("+", "-")
        button_html = (
            f"<button onclick=\"navigator.clipboard.writeText('{escaped_text}');"
            " this.innerText='✔'; setTimeout(()=>this.innerText='📋',1000);\""
            " style='background:transparent; border:none; cursor:pointer; font-size:14px;'>📋</button>"
            if show_button
            else ""
        )

        return (
            f"<tr style='background-color:{bg_color};'>"
            f"<td style='border:1px solid {bg_color}; width:40px; text-align:right; color:#555'>{old_lineno or ''}</td>"
            f"<td style='border:1px solid {bg_color}; width:40px; text-align:right; color:#555'>{new_lineno or ''}</td>"
            f"<td style='border:1px solid {bg_color}; width:40px; text-align:center;'>{action}</td>"
            f"<td style='border:1px solid {bg_color}; white-space:pre-wrap; word-break:break-word;'>{content}</td>"
            f"<td style='border:1px solid {bg_color}; width:40px; text-align:center;'>"
            f"<div style='display:flex; justify-content:center; align-items:center; height:100%;'>{button_html}</div>"
            f"</td>"
            f"</tr>"
        )

    i = 0
    while i < len(diff):
        line = diff[i]

        # Метаданные файлов
        if line.startswith("---") or line.startswith("+++"):
            table_rows.append(wrap_line("", "", "", html_module.escape(line), "#eee"))
            i += 1
            continue

        # Хедер блока изменений
        if line.startswith("@@"):
            parts = line.split()
            old_line_no = int(parts[1].split(",")[0][1:]) - 1
            new_line_no = int(parts[2].split(",")[0]) - 1
            table_rows.append(wrap_line("", "", "", html_module.escape(line), "#eef"))
            i += 1
            continue

        # Блоки изменений
        if line.startswith("-") or line.startswith("+"):
            removed_lines = []
            added_lines = []

            while i < len(diff) and diff[i].startswith(("-", "+")):
                if diff[i].startswith("-"):
                    removed_lines.append(diff[i][1:])
                else:
                    added_lines.append(diff[i][1:])
                i += 1

            if removed_lines or added_lines:
                sm = difflib.SequenceMatcher(None, removed_lines, added_lines)
                for tag, i1, i2, j1, j2 in sm.get_opcodes():
                    # Старые строки
                    for r in range(i1, i2):
                        old_line_no += 1
                        old_text = removed_lines[r]
                        if tag in ("replace", "delete"):
                            if tag == "replace" and r - i1 < (j2 - j1):
                                new_text = added_lines[j1 + (r - i1)]
                                new_line_no += 1
                                old_hl, new_hl = highlight_inline_changes(
                                    old_text, new_text
                                )
                                table_rows.append(
                                    wrap_line(
                                        old_line_no,
                                        "",
                                        "-",
                                        old_hl,
                                        "#ffdddd",
                                        old_text,
                                    )
                                )
                                table_rows.append(
                                    wrap_line(
                                        "",
                                        new_line_no,
                                        "+",
                                        new_hl,
                                        "#ddffdd",
                                        new_text,
                                    )
                                )
                            else:
                                table_rows.append(
                                    wrap_line(
                                        old_line_no,
                                        "",
                                        "-",
                                        html_module.escape(old_text),
                                        "#ffdddd",
                                        old_text,
                                    )
                                )
                    # Новые строки
                    for a in range(j1 + max(0, i2 - i1), j2):
                        new_line_no += 1
                        new_text = added_lines[a]
                        table_rows.append(
                            wrap_line(
                                "",
                                new_line_no,
                                "+",
                                html_module.escape(new_text),
                                "#ddffdd",
                                new_text,
                            )
                        )
            continue

        # Общие строки
        if line.startswith(" "):
            old_line_no += 1
            new_line_no += 1
            table_rows.append(
                wrap_line(
                    old_line_no,
                    new_line_no,
                    " ",
                    html_module.escape(line[1:]),
                    "white",
                    line[1:],
                )
            )
            i += 1
            continue

        # Строка не распознана — просто пропускаем
        i += 1

    html_output = (
        "<div style='overflow-x:auto;'>"
        "<table style='border-collapse:collapse; width:100%; table-layout:fixed; font-family:monospace;'>"
        "<tbody>" + "".join(table_rows) + "</tbody></table></div>"
    )
    return html_output


# ---------------------- Streamlit UI ----------------------

st.set_page_config(page_title="Text Diff Viewer", layout="wide")
st.title("📄 Сравнение текстов")

col1, col2 = st.columns(2)
with col1:
    input_text1 = st.text_area("Old", "Привет!\nЭто текст номер один.", height=200)
with col2:
    input_text2 = st.text_area("New", "Привет!\nЭто текст номер два.", height=200)

if st.button("Сравнить"):
    plain_text1 = strip_html_tags(input_text1)
    plain_text2 = strip_html_tags(input_text2)

    if plain_text1.strip() == plain_text2.strip():
        st.success("✅ Тексты идентичны.")
    else:
        diff_html = git_style_diff_html(plain_text1, plain_text2)
        st.markdown(diff_html, unsafe_allow_html=True)
