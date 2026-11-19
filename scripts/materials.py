"""Build portable support-file previews from the published material manifest."""

import base64
import hashlib
import html
import json
import posixpath
import re
import zipfile
from pathlib import Path
from urllib.parse import quote
import xml.etree.ElementTree as ET


def escape(value):
    return html.escape(str(value), quote=True)


def file_size(value):
    for unit in ("B", "KB", "MB", "GB"):
        if value < 1024 or unit == "GB":
            return f"{value:,.0f} {unit}" if unit == "B" else f"{value:,.1f} {unit}"
        value /= 1024


def file_url(path):
    return quote(path, safe="/")


def download_url(material, prefix=""):
    return material.get("download_url") or prefix + file_url(material["file_path"])


def load_materials(tasks, root):
    manifest = json.loads((root / "support-materials.json").read_text(encoding="utf-8"))
    entries = {(item["task_id"], item["path"]): item for item in manifest["files"]}
    expected = {(task["id"], path) for task in tasks for path in task["materials"]}
    if len(entries) != len(manifest["files"]) or set(entries) != expected:
        raise ValueError("Support-material manifest must match every source material exactly once")
    for task in tasks:
        task["material_files"] = [entries[(task["id"], path)] for path in task["materials"]]
        for material in task["material_files"]:
            if material["task_slug"] != task["slug"]:
                raise ValueError("Support-material task slug does not match")
            for key in ("file_path", "preview_path", "webm_path", "page"):
                if key in material:
                    path = Path(material[key])
                    if path.is_absolute() or ".." in path.parts:
                        raise ValueError(f"Invalid material path: {path}")
    return manifest


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def docx_preview(path):
    """Render document text, tables, inline images, and tracked revisions safely."""
    w = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    rel = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
    a = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
    with zipfile.ZipFile(path) as archive:
        document = ET.fromstring(archive.read("word/document.xml"))
        relationships = {}
        if "word/_rels/document.xml.rels" in archive.namelist():
            for item in ET.fromstring(archive.read("word/_rels/document.xml.rels")):
                if item.attrib.get("TargetMode") != "External":
                    relationships[item.attrib["Id"]] = posixpath.normpath("word/" + item.attrib["Target"])

        def render(element):
            tag = element.tag.removeprefix(w)
            if tag in ("t", "delText"):
                return escape(element.text or "")
            if tag in ("pPr", "rPr", "tblPr", "trPr", "tcPr", "tblGrid", "sectPr"):
                return ""
            if tag == "tab":
                return "&emsp;"
            if tag in ("br", "cr"):
                return "<br>"
            if tag == "drawing":
                images = []
                for blip in element.iter(a + "blip"):
                    name = relationships.get(blip.attrib.get(rel + "embed"))
                    if name and name in archive.namelist() and Path(name).suffix.lower() in (".png", ".jpg", ".jpeg"):
                        mime = "image/png" if name.endswith(".png") else "image/jpeg"
                        data = base64.b64encode(archive.read(name)).decode("ascii")
                        images.append(f'<img class="document-image" src="data:{mime};base64,{data}" alt="Document illustration">')
                return "".join(images)
            children = "".join(render(child) for child in element)
            if tag == "p":
                style = element.find(w + "pPr/" + w + "pStyle")
                value = style.attrib.get(w + "val", "") if style is not None else ""
                heading = re.fullmatch(r"Heading([1-6])", value, flags=re.IGNORECASE)
                level = min(int(heading.group(1)) + 1, 6) if heading else None
                return f"<h{level}>{children}</h{level}>" if level else f"<p>{children or '<br>'}</p>"
            if tag == "r":
                props = element.find(w + "rPr")
                if props is not None:
                    for name, markup in (("b", "strong"), ("i", "em"), ("u", "u")):
                        prop = props.find(w + name)
                        if prop is not None and prop.attrib.get(w + "val") not in ("0", "false", "none"):
                            children = f"<{markup}>{children}</{markup}>"
                return children
            if tag in ("ins", "del"):
                return f'<{tag} class="revision-{tag}">{children}</{tag}>'
            if tag == "tbl":
                return f'<div class="document-table-wrapper"><table>{children}</table></div>'
            if tag == "tr":
                return f"<tr>{children}</tr>"
            if tag == "tc":
                span = element.find(w + "tcPr/" + w + "gridSpan")
                colspan = f' colspan="{int(span.attrib[w + "val"])}"' if span is not None else ""
                return f"<td{colspan}>{children}</td>"
            return children

        body = render(document.find(w + "body"))
        revisions = bool(list(document.iter(w + "ins")) or list(document.iter(w + "del")))
        return body, revisions


def markdown_preview(text, inline, prose):
    sections, paragraph = [], []

    def flush():
        if paragraph:
            sections.append(prose("\n".join(paragraph)))
            paragraph.clear()

    for line in text.splitlines():
        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading:
            flush()
            level = min(len(heading.group(1)) + 1, 6)
            sections.append(f"<h{level}>{inline(heading.group(2))}</h{level}>")
        else:
            paragraph.append(line)
    flush()
    return "\n".join(sections)


def build_material_page(material, task, root, page, inline, prose):
    prefix = "../../"
    name = escape(material["name"])
    original = escape(download_url(material, prefix))
    kind = material["kind"]
    open_original = ""
    if kind == "pdf":
        source = prefix + file_url(material["file_path"])
        preview = f'<iframe class="pdf-preview" src="{escape(source)}" title="{name}"></iframe>'
        open_original = f'<a class="button" href="{escape(source)}" target="_blank" rel="noopener">Open PDF</a>'
        note = "Original PDF. Use Open PDF if your browser does not display the embedded preview."
    elif kind == "video":
        source = prefix + file_url(material["preview_path"])
        fallback = f'<source src="{escape(prefix + file_url(material["webm_path"]))}" type="video/webm">' if material.get("webm_path") else ""
        preview = f'<video class="video-preview" controls playsinline preload="metadata"><source src="{escape(source)}" type="video/mp4">{fallback}Your browser cannot play this preview. Use Download original to open the source file.</video>'
        open_original = f'<a class="button" href="{escape(source)}" download>Download preview</a>'
        note = "Full-length 540p preview for browser playback. Download original for the unmodified source footage."
    elif kind == "audio":
        source = prefix + file_url(material["file_path"])
        preview = f'<div class="audio-preview"><span class="audio-caption">{name}</span><audio controls preload="metadata"><source src="{escape(source)}" type="audio/mpeg">Your browser cannot play this audio. Download the original track to listen.</audio></div>'
        note = "Original audio track."
    elif kind == "document":
        document, revisions = docx_preview(root / material["file_path"])
        legend = '<p class="revision-legend"><ins>Inserted text</ins><del>Deleted text</del></p>' if revisions else ""
        preview = f'{legend}<article class="document-preview prose" aria-label="Document text preview">{document}</article>'
        note = "Document text preview. Download the original DOCX for its exact page layout and editing features."
        if revisions:
            note += " Tracked insertions and deletions are shown below."
    elif kind == "markdown":
        document = markdown_preview((root / material["file_path"]).read_text(encoding="utf-8"), inline, prose)
        preview = f'<article class="document-preview prose" aria-label="Markdown preview">{document}</article>'
        note = "Rendered from the original Markdown support material."
    elif kind == "cad":
        reference = next(item for item in task["material_files"] if item["kind"] == "pdf")
        preview = f'<div class="cad-preview"><span class="cad-file-type">DWG</span><h2>Open this drawing in a CAD application</h2><p>Download the original DWG file and open it in an application that supports DWG. A browser preview is available for the separate design reference.</p><div class="material-toolbar"><a class="button primary-button" href="{original}" download>Download DWG</a><a class="button" href="{escape(prefix + reference["page"])}">View design reference PDF</a></div></div>'
        note = "Original editable CAD drawing. DWG files require a compatible CAD application."
    else:
        raise ValueError(f"Unsupported material type: {kind}")
    siblings = "".join(f'<li><a href="{escape(prefix + item["page"])}" {"aria-current=page" if item == material else ""}>{escape(item["name"])}</a></li>' for item in task["material_files"])
    content = f'''<main id="main" class="container material-page" tabindex="-1">
      <nav class="breadcrumbs" aria-label="Breadcrumb"><ol><li><a href="../../index.html#tasks">Tasks</a></li><li><a href="../../tasks/{task['slug']}/index.html#support-materials">Task {task['id']:02d} · Support materials</a></li><li aria-current="page">{name}</li></ol></nav>
      <header class="material-hero"><p class="eyebrow"><span class="accent-line" aria-hidden="true"></span> SUPPORT MATERIAL</p><h1>{name}</h1><p class="material-detail">{escape(material['name'].rsplit('.', 1)[-1].upper())} · {file_size(material['bytes'])} original file</p><code class="material-original-path">{escape(material['path'])}</code><div class="material-toolbar"><a class="button primary-button" href="{original}" download>Download original</a>{open_original}<a class="button" href="../../tasks/{task['slug']}/index.html#support-materials">Back to task</a></div></header>
      <p class="material-preview-note">{note}</p><div class="material-preview">{preview}</div>
      <section class="related-materials" aria-labelledby="related-title"><div class="section-heading"><h2 id="related-title">Materials for this task</h2><span class="section-meta">{len(task['material_files'])} {'file' if len(task['material_files']) == 1 else 'files'}</span></div><ul>{siblings}</ul></section>
    </main>'''
    return page(f"{material['name']} | AAB Benchmark", f"Open the support material {material['name']} for {task['title']}.", content, prefix)
