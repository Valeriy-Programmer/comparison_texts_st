import difflib
import html as html_module


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
