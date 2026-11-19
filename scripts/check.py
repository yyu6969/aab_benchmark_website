#!/usr/bin/env python3
"""Check source fidelity and links in the generated static website."""

import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from build import OUTPUT, ROOT, SOURCE, parse_tasks, plain_text
from materials import load_materials, sha256


def compact(text):
    return " ".join(text.split())


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.links = []
        self.ids = set()
        self.h1_count = 0
        self.in_table = False
        self.cell = None
        self.row = []
        self.rubrics = []
        self.instruction_depth = 0
        self.instruction = []
        self.materials = []
        self.material = None
        self.feed(path.read_text(encoding="utf-8"))

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            assert attrs["id"] not in self.ids, f"Duplicate ID in {self.path}: {attrs['id']}"
            self.ids.add(attrs["id"])
        for name in ("href", "src"):
            if attrs.get(name):
                self.links.append(attrs[name])
        if tag == "h1":
            self.h1_count += 1
        if tag == "div" and "instruction-panel" in attrs.get("class", "").split():
            self.instruction_depth = 1
        elif self.instruction_depth and tag == "div":
            self.instruction_depth += 1
        if self.instruction_depth and tag in ("p", "li", "br"):
            self.instruction.append(" ")
        if tag == "code" and "material-path" in attrs.get("class", "").split():
            self.material = []
        if tag == "table" and "rubric-table" in attrs.get("class", "").split():
            self.in_table = True
        if self.in_table and tag == "tr":
            self.row = []
        if self.in_table and tag in ("td", "th"):
            self.cell = []

    def handle_endtag(self, tag):
        if self.instruction_depth and tag == "div":
            self.instruction_depth -= 1
        if tag == "code" and self.material is not None:
            self.materials.append("".join(self.material))
            self.material = None
        if self.in_table and tag in ("td", "th"):
            self.row.append(compact("".join(self.cell)))
            self.cell = None
        if self.in_table and tag == "tr" and self.row and self.row[0].isdigit():
            self.rubrics.append(self.row)
        if tag == "table":
            self.in_table = False

    def handle_data(self, text):
        if self.instruction_depth:
            self.instruction.append(text)
        if self.material is not None:
            self.material.append(text)
        if self.cell is not None:
            self.cell.append(text)


def check():
    tasks = parse_tasks(SOURCE.read_text(encoding="utf-8"))
    manifest = load_materials(tasks, ROOT)
    assert (OUTPUT / "data/new_10_tasks.md").read_bytes() == SOURCE.read_bytes(), "Source download differs"
    exported = json.loads((OUTPUT / "data/tasks.json").read_text(encoding="utf-8"))
    assert exported == [{k: v for k, v in task.items() if k != "markdown"} for task in tasks], "JSON differs from source"
    pages = {path.resolve(): Page(path) for path in OUTPUT.rglob("*.html")}
    expected_pages = 11 + len(manifest["files"])
    assert len(pages) == expected_pages, f"Expected {expected_pages} HTML pages, found {len(pages)}"
    checked_links = 0
    for path, page in pages.items():
        assert page.h1_count == 1, f"Expected one H1 in {path}"
        for link in page.links:
            url = urlsplit(link)
            if url.scheme or url.netloc:
                continue
            assert not url.path.startswith("/"), f"Root-relative URL breaks project Pages: {link}"
            target = (path.parent / unquote(url.path)).resolve() if url.path else path
            if target.is_dir():
                target /= "index.html"
            assert target.is_relative_to(OUTPUT.resolve()), f"URL leaves site: {link}"
            assert target.is_file(), f"Broken link from {path}: {link}"
            if url.fragment and target in pages:
                assert unquote(url.fragment) in pages[target].ids, f"Missing fragment {link} in {path}"
            checked_links += 1
    for task in tasks:
        path = (OUTPUT / "tasks" / task["slug"] / "index.html").resolve()
        page = pages[path]
        expected = [[f"{r['number']:02d}", compact(plain_text(r["criterion"])), compact(plain_text(r["source"]))] for r in task["rubrics"]]
        assert page.rubrics == expected, f"Rubric content changed in task {task['id']}"
        instruction = re.sub(r"(?m)^\s*-\s+", "", plain_text(task["instruction"]))
        assert compact("".join(page.instruction)) == compact(instruction), f"Instruction changed in task {task['id']}"
        assert page.materials == task["materials"], f"Material paths changed in task {task['id']}"
        assert (OUTPUT / "data" / f"{task['slug']}.md").read_text(encoding="utf-8") == task["markdown"]
    for css in (OUTPUT / "assets").glob("*.css"):
        for ref in re.findall(r"url\(['\"]?([^)'\"]+)", css.read_text(encoding="utf-8")):
            assert (css.parent / ref).is_file(), f"Missing CSS asset {ref}"
    for material in manifest["files"]:
        if "file_path" in material:
            source = ROOT / material["file_path"]
            published = OUTPUT / material["file_path"]
            assert source.stat().st_size == material["bytes"], f"Incorrect original file size: {source}"
            assert sha256(source) == material["sha256"], f"Original support file changed: {source}"
            assert sha256(published) == material["sha256"], f"Published support file changed: {published}"
        for key in ("preview_path", "webm_path"):
            if key in material:
                preview = ROOT / material[key]
                assert preview.is_file() and preview.stat().st_size > 1000, f"Missing video preview: {preview}"
                assert sha256(preview) == sha256(OUTPUT / material[key]), "Video preview copy differs"
        assert (OUTPUT / material["page"]).is_file(), "Missing material preview page"
    assert (ROOT / "assets/fonts/LICENSE").is_file(), "Missing font license"
    print(f"Passed: {expected_pages} pages, {checked_links} local links, 10 complete instructions, "
          f"{sum(len(t['rubrics']) for t in tasks)} exact rubric rows, "
          f"{sum(len(t['materials']) for t in tasks)} material paths, Markdown and JSON downloads.")


if __name__ == "__main__":
    check()
