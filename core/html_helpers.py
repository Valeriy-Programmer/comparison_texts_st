import difflib
import html as html_module


def wrap_line(old_lineno, new_lineno, action, content, css_class, raw_text=None):
    if raw_text is None:
        raw_text = content

    escaped_text = html_module.escape(raw_text).replace("'", "\\'")
    show_button = action in ("+", "-")
    button_html = (
        f"<button onclick=\"navigator.clipboard.writeText('{escaped_text}');"
        " this.innerText='✔'; setTimeout(()=>this.innerText='📋',1000);\""
        " class='copy-btn'></button>"
        if show_button
        else ""
    )

    return (
        f"<tr class='{css_class}'>"
        f"<td class='line-no'>{old_lineno or ''}</td>"
        f"<td class='line-no'>{new_lineno or ''}</td>"
        f"<td class='action'>{action}</td>"
        f"<td class='code'>{content}</td>"
        f"<td class='copy'>{button_html}</td>"
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
