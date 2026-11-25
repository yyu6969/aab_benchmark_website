#!/usr/bin/env python3
"""Check source fidelity and links in the generated static website."""

import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from agent_runs import CODEX_SCORES, HARBOR_SCORES, load_agent_runs
from build import OUTPUT, ROOT, SOURCE, load_tutorials, parse_tasks, plain_text
from materials import file_url, load_materials, sha256


def compact(text):
    return " ".join(text.split())


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path = path
        self.links = []
        self.ids = set()
        self.section_ids = []
        self.run_frames = {}
        self.run_condition = None
        self.h1_count = 0
        self.in_table = False
        self.cell = None
        self.row = []
        self.rubrics = []
        self.scores = {}
        self.score_row_id = None
        self.instruction_depth = 0
        self.instruction = []
        self.excerpts = {}
        self.excerpt_triggers = []
        self.excerpt_id = None
        self.excerpt_depth = 0
        self.in_mark = False
        self.materials = []
        self.material = None
        self.feed(path.read_text(encoding="utf-8"))

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = attrs.get("class", "").split()
        if tag == "div" and "source-popover" in classes:
            self.excerpt_id = attrs["id"]
            self.excerpts[self.excerpt_id] = {"marked": [], "context": []}
        if "data-excerpt" in attrs:
            assert tag == "a" and "instruction-source" in classes and attrs["href"] == "#instruction"
            self.excerpt_triggers.append(attrs["data-excerpt"])
        if tag == "div" and (self.excerpt_depth or "excerpt-body" in classes):
            self.excerpt_depth += 1
        if self.excerpt_depth:
            if tag == "mark":
                self.in_mark = True
            if tag in ("p", "li"):
                self.excerpts[self.excerpt_id]["marked"].append(" ")
        if tag == "section" and attrs.get("id"):
            self.section_ids.append(attrs["id"])
        if tag == "article" and "agent-run" in attrs.get("class", "").split():
            self.run_condition = attrs["id"].removeprefix("run-")
            self.run_frames[self.run_condition] = []
            self.scores[self.run_condition] = []
        if tag == "option" and self.run_condition:
            self.run_frames[self.run_condition].append(attrs["value"])
        if attrs.get("id"):
            assert attrs["id"] not in self.ids, f"Duplicate ID in {self.path}: {attrs['id']}"
            self.ids.add(attrs["id"])
        for name in ("href", "src", "poster"):
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
        if tag == "table" and "rubric-table" in classes and "run-results" not in classes:
            self.in_table = True
        if self.run_condition and tag == "tr":
            self.score_row_id = attrs.get("data-rubric-id")
        if (self.in_table or self.score_row_id) and tag == "tr":
            self.row = []
        if (self.in_table or self.score_row_id) and tag in ("td", "th"):
            self.cell = []

    def handle_endtag(self, tag):
        if self.excerpt_depth:
            if tag == "div":
                self.excerpt_depth -= 1
            elif tag == "mark":
                self.in_mark = False
        if tag == "article":
            self.run_condition = None
        if self.instruction_depth and tag == "div":
            self.instruction_depth -= 1
        if tag == "code" and self.material is not None:
            self.materials.append("".join(self.material))
            self.material = None
        if (self.in_table or self.score_row_id) and tag in ("td", "th"):
            self.row.append(compact("".join(self.cell)))
            self.cell = None
        if self.in_table and tag == "tr" and self.row and self.row[0].isdigit():
            self.rubrics.append(self.row)
        if tag == "tr" and self.score_row_id:
            self.scores[self.run_condition].append([self.score_row_id, *self.row])
            self.score_row_id = None
        if tag == "table":
            self.in_table = False

    def handle_data(self, text):
        if self.excerpt_depth:
            key = "marked" if self.in_mark else "context"
            self.excerpts[self.excerpt_id][key].append(text)
        if self.instruction_depth:
            self.instruction.append(text)
        if self.material is not None:
            self.material.append(text)
        if self.cell is not None:
            self.cell.append(text)


def check():
    tasks = parse_tasks(SOURCE.read_text(encoding="utf-8"))
    manifest = load_materials(tasks, ROOT)
    load_tutorials(tasks)
    load_agent_runs(tasks, ROOT, plain_text)
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
        boxes = [f"source-{r['number']}" for r in task["rubrics"] if any(s["name"] == "instruction.md" for s in r.get("sources", []))]
        assert page.excerpt_triggers == boxes and set(page.excerpts) == set(boxes)
        for row, rubric in zip(expected, task["rubrics"]):
            if "sources" in rubric:
                row[2] = " ".join(src["name"] for src in rubric["sources"])
                for src in rubric["sources"]:
                    if src["name"] == "instruction.md":
                        excerpt = page.excerpts[f"source-{rubric['number']}"]
                        quote = re.sub(r"(?m)^\s*- ", "", plain_text(src["highlight"]))
                        assert compact("".join(excerpt["marked"])) == compact(quote)
                        if src["highlight"] != task["instruction"]:
                            assert compact("".join(excerpt["context"])).strip("… ")
            if "clips" in rubric:
                row.append(" ".join(c["label"] for c in rubric["clips"]))
                for clip in rubric["clips"]:
                    duration = task["tutorial"]["duration_seconds"]
                    assert 0 <= clip["playback_start_sec"] <= clip["start_sec"] < clip["end_sec"] <= clip["playback_end_sec"] <= duration
                    assert clip["playback_start_sec"] == max(0, clip["start_sec"] - 2)
                    assert clip["playback_end_sec"] == min(duration, clip["end_sec"] + 2)
                    assert f"../../{clip['file']}?context=2" in page.links
        assert page.rubrics == expected, f"Rubric content changed in task {task['id']}"
        instruction = re.sub(r"(?m)^\s*-\s+", "", plain_text(task["instruction"]))
        assert compact("".join(page.instruction)) == compact(instruction), f"Instruction changed in task {task['id']}"
        assert page.materials == task["materials"], f"Material paths changed in task {task['id']}"
        guide = task["tutorial"]["guidance_path"]
        assert "reference-guidance" in page.ids and f"../../{guide}" in page.links
        assert sha256(OUTPUT / guide) == sha256(ROOT / guide), f"Guidance download differs: {guide}"
        assert (OUTPUT / "data" / f"{task['slug']}.md").read_text(encoding="utf-8") == task["markdown"]
        ordered = page.section_ids
        assert ordered.index("agent-run") == ordered.index("support-materials") + 1
        assert "#agent-run" in page.links
        if "instruction_run" in task:
            run = task["instruction_run"]
            actual = page.scores["instruction-only"]
            assert len(actual) == len(task["rubrics"])
            for rubric, cells in zip(task["rubrics"], actual):
                item = run["rows"].get(rubric["id"], {})
                rating = item.get("score")
                assert rating is None or type(rating) is int and rating in (0, 1)
                assert len(cells) == 6 and cells[:4] == [rubric["id"], f"{rubric['number']:02}",
                    compact(plain_text(rubric["criterion"])), "null" if rating is None else str(rating)]
                assert cells[4] and cells[5]
                for ref in item.get("observations", []):
                    evidence = run["evidence"][ref]
                    assert evidence["label"] in cells[5]
                    if evidence.get("note"):
                        assert compact(evidence["note"]) in cells[5]
                    if evidence.get("file"):
                        assert f"../../assets/agent-runs/{task['slug']}/{run['trial']}/{evidence['file']}" in page.links
        for condition, run in task["agent_runs"].items():
            assert f"run-{condition}" in page.ids
            expected_scores = []
            for number, score in enumerate(run["rubric_scores"], 1):
                cells = []
                for value in (HARBOR_SCORES[score["harbor_verdict"]], CODEX_SCORES[score["codex_finding"]]):
                    cells.append({1: "✓ 1", 0: "0"}[value])
                expected_scores.append([score["id"], f"{number:02d} {score['criterion']}", *cells])
            assert page.scores[condition] == expected_scores, f"Score checklist mismatch: {task['slug']}/{condition}"
            folder = Path(run["asset_path"])
            outputs = run["output_files"]
            assert (f"outputs-{condition}" in page.ids) == bool(outputs)
            expected_files = {item["name"] for item in outputs}
            for root in (ROOT, OUTPUT):
                assert {p.name for p in (root / folder / "outputs").glob("*")} == expected_files
            for item in outputs:
                path = folder / "outputs" / item["name"]
                assert f"../../{file_url(path.as_posix())}" in page.links
                assert (OUTPUT / path).stat().st_size == item["bytes"]
                assert sha256(OUTPUT / path) == sha256(ROOT / path) == item["sha256"]
            assert run["total_tokens"] == run["input_tokens"] + run["output_tokens"]
            assert 0 <= run["cached_input_tokens"] <= run["input_tokens"] and run["runtime_seconds"] > 0
            assert page.run_frames[condition] == [f"../../{folder}/{name}" for name in run["frames"]]
            for name in [*run["frames"], "traj.jsonl"]:
                assert sha256(ROOT / folder / name) == sha256(OUTPUT / folder / name)
            assert f"../../{folder}/traj.jsonl" in page.links
            with (OUTPUT / folder / "traj.jsonl").open(encoding="utf-8") as stream:
                assert sum(1 for line in stream if json.loads(line)["event"]) == run["event_count"]
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
