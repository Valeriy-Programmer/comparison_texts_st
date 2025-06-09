import difflib
import html as html_module
from core.html_helpers import highlight_inline_changes, wrap_line


def git_style_diff_html(text1, text2):
    lines1 = text1.splitlines()
    lines2 = text2.splitlines()
    diff = list(
        difflib.unified_diff(lines1, lines2, fromfile="Old", tofile="New", lineterm="")
    )

    table_rows = []
    old_line_no = 0
    new_line_no = 0

    i = 0
    while i < len(diff):
        line = diff[i]

        if line.startswith("---") or line.startswith("+++"):
            table_rows.append(
                wrap_line("", "", "", html_module.escape(line), "line-header")
            )
            i += 1
            continue

        if line.startswith("@@"):
            parts = line.split()
            old_line_no = int(parts[1].split(",")[0][1:]) - 1
            new_line_no = int(parts[2].split(",")[0]) - 1
            table_rows.append(
                wrap_line("", "", "", html_module.escape(line), "line-hunk")
            )
            i += 1
            continue

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
                                        "line-removed",
                                        old_text,
                                    )
                                )
                                table_rows.append(
                                    wrap_line(
                                        "",
                                        new_line_no,
                                        "+",
                                        new_hl,
                                        "line-added",
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
                                        "line-removed",
                                        old_text,
                                    )
                                )
                    for a in range(j1 + max(0, i2 - i1), j2):
                        new_line_no += 1
                        new_text = added_lines[a]
                        table_rows.append(
                            wrap_line(
                                "",
                                new_line_no,
                                "+",
                                html_module.escape(new_text),
                                "line-added",
                                new_text,
                            )
                        )
            continue

        if line.startswith(" "):
            old_line_no += 1
            new_line_no += 1
            table_rows.append(
                wrap_line(
                    old_line_no,
                    new_line_no,
                    " ",
                    html_module.escape(line[1:]),
                    "line-context",
                    line[1:],
                )
            )
            i += 1
            continue

        i += 1

    html_output = (
        "<div class='diff-container'>"
        "<table class='diff-table'>"
        "<tbody>" + "".join(table_rows) + "</tbody></table></div>"
    )

    return html_output
