"""Render the headings, nested steps and inline formatting in the tutorial guides."""

import re
from html import escape

from materials import markdown_preview


def inline(text):
    parts = []
    start = 0
    for match in re.finditer(r"`([^`]+)`|\*\*(.+?)\*\*|\*(\S(?:[^*]*?\S)?)\*", text):
        parts.append(escape(text[start:match.start()]))
        code, strong, emphasis = match.groups()
        if code is not None:
            parts.append(f"<code>{escape(code)}</code>")
        else:
            tag = "strong" if strong is not None else "em"
            parts.append(f"<{tag}>{inline(strong or emphasis)}</{tag}>")
        start = match.end()
    parts.append(escape(text[start:]))
    return "".join(parts)


def blocks(text):
    output = []
    lists = []

    def close_list():
        _, tag = lists.pop()
        output.append(f"</li></{tag}>")

    for line in text.splitlines():
        content = line.strip()
        if not content:
            continue
        indent = len(line) - len(line.lstrip())
        item = re.match(r"(-|\d+\.)\s+(.*)", content)
        if item:
            marker, label = item.groups()
            tag = "ul" if marker == "-" else "ol"
            while lists and (lists[-1][0] > indent or (lists[-1][0] == indent and lists[-1][1] != tag)):
                close_list()
            if lists and lists[-1][0] == indent:
                output.append("</li>")
            else:
                start = f' start="{int(marker[:-1])}"' if tag == "ol" and marker != "1." else ""
                output.append(f"<{tag}{start}>")
                lists.append((indent, tag))
            output.append(f"<li>{inline(label)}")
        else:
            while lists and lists[-1][0] >= indent:
                close_list()
            output.append("<hr>" if content == "---" else f"<p>{inline(content)}</p>")
    while lists:
        close_list()
    return "\n".join(output)


def render_guidance(markdown):
    levels = re.findall(r"^(#{1,6})\s+", markdown, re.MULTILINE)
    offset = 3 - min(map(len, levels), default=3)
    return markdown_preview(markdown, inline, blocks, heading_offset=offset)
