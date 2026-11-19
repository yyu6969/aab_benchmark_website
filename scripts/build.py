#!/usr/bin/env python3
"""Build the GitHub Pages website from new_10_tasks.md. No dependencies."""

from __future__ import annotations

import html
import json
import re
import shutil
from pathlib import Path

from agent_runs import load_agent_runs, render_agent_runs
from guidance import render_guidance
from materials import build_material_page, download_url, file_size, load_materials

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "docs"
SOURCE = ROOT / "new_10_tasks.md"

# Editorial summaries and navigation labels; task content comes from the source.
METADATA = [
    ("Documents", "Accept approved revisions and release a clean Statement of Work.", "finalize-document-tracked-changes"),
    ("Calendar", "Schedule a study session and a recurring all-day calendar event.", "schedule-calendar-events"),
    ("Accounting", "Reconcile a company ledger against a monthly bank statement.", "reconcile-business-bank-account"),
    ("Clinical documentation", "Complete encounter findings, assessment, and plan, then sign the note.", "complete-sign-clinical-note"),
    ("Education", "Grade student work, return submissions, and update the class gradebook.", "update-class-gradebook"),
    ("Data analysis", "Prepare survey records and compare complete and missing-response frequencies.", "survey-data-frequency-analyses"),
    ("Video editing", "Assemble an editable presenter video with cutaways, graphics, and music.", "edit-youtube-video"),
    ("Project management", "Organize a team, plan a holiday website launch, and manage handoffs.", "plan-website-launch"),
    ("Sales operations", "Manage converted leads and build closed-won revenue reports and dashboards.", "sales-leads-revenue-dashboards"),
    ("CAD & architecture", "Complete a ground-floor drawing and prepare scaled presentation sheets.", "floor-plan-architectural-details"),
]


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def normalize(text: str) -> str:
    """Remove export escaping while retaining the original words and punctuation."""
    text = html.unescape(text).replace("\xa0", " ")
    return re.sub(r"\\([\\`*_{}\[\]()#+\-.!$|])", r"\1", text).strip()


def inline(text: str) -> str:
    # Tokenize code and links before escaping. Do not interpret filename underscores.
    tokens = re.split(r"(`[^`]+`|\[[^\]]+\]\((?:mailto:|https?://)[^)]+\))", text)
    parts = []
    for token in tokens:
        if token.startswith("`") and token.endswith("`"):
            parts.append(f"<code>{esc(token[1:-1])}</code>")
        elif re.fullmatch(r"\[[^\]]+\]\((?:mailto:|https?://)[^)]+\)", token):
            label, url = re.fullmatch(r"\[([^\]]+)\]\(([^)]+)\)", token).groups()
            parts.append(f'<a href="{esc(url)}">{esc(label)}</a>')
        else:
            parts.append(re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", esc(token)))
    return "".join(parts)


def plain_text(text: str) -> str:
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    return text.replace("**", "").replace("`", "")


def prose(text: str) -> str:
    blocks, paragraph, items = [], [], []

    def flush_paragraph():
        if paragraph:
            blocks.append("<p>" + " ".join(inline(line) for line in paragraph) + "</p>")
            paragraph.clear()

    def flush_items():
        if items:
            blocks.append("<ul>" + "".join(f"<li>{inline(item)}</li>" for item in items) + "</ul>")
            items.clear()

    for line in text.splitlines():
        line = line.strip()
        if not line:
            flush_paragraph()
            flush_items()
        elif line.startswith("- "):
            flush_paragraph()
            items.append(line[2:])
        else:
            flush_items()
            paragraph.append(line)
    flush_paragraph()
    flush_items()
    return "\n".join(blocks)


def parse_tasks(source: str) -> list[dict]:
    starts = list(re.finditer(r"^## \*\*(\d+)\\\. (.*?)\*\*\s*$", source, re.MULTILINE))
    if len(starts) != 10:
        raise ValueError(f"Expected 10 tasks; found {len(starts)}")
    tasks = []
    for i, start in enumerate(starts):
        raw = source[start.start():starts[i + 1].start() if i + 1 < len(starts) else len(source)]
        text = normalize(raw)
        sections = re.split(r"^### \*\*(.*?)\*\*[^\n]*\n", text, flags=re.MULTILINE)
        section_map = {sections[n].strip().lower(): sections[n + 1].strip() for n in range(1, len(sections), 2)}
        instruction = section_map["task instruction"]
        support = section_map["support materials"]
        materials = [line.strip().strip("`") for line in support.splitlines() if line.strip() and line.strip() != "None"]
        rubrics = []
        for line in section_map["outcome rubric"].splitlines():
            if re.match(r"^\|\s*\d+\s*\|", line):
                cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
                if len(cells) != 3:
                    raise ValueError(f"Invalid rubric row: {line}")
                rubrics.append({"number": int(cells[0]), "criterion": cells[1], "source": cells[2]})
        if not instruction or not rubrics:
            raise ValueError(f"Missing content for task {i + 1}")
        if [r["number"] for r in rubrics] != list(range(1, len(rubrics) + 1)):
            raise ValueError(f"Rubric numbering is not sequential for task {i + 1}")
        category, summary, slug = METADATA[i]
        tasks.append({"id": int(start.group(1)), "title": normalize(start.group(2)),
                      "category": category, "summary": summary, "slug": slug,
                      "instruction": instruction, "materials": materials, "rubrics": rubrics,
                      "markdown": text.removesuffix("---").strip() + "\n"})
    if [task["id"] for task in tasks] != list(range(1, 11)):
        raise ValueError("Expected task IDs 1 through 10")
    return tasks


ICONS = {
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1.5 1.5m11 11L19 19M5 19l1.5-1.5m11-11L19 5"/>',
    "moon": '<path d="M20.9 13A9 9 0 0 1 11 3.1 9 9 0 1 0 20.9 13Z"/>',
    "copy": '<rect x="8" y="8" width="12" height="13" rx="1"/><path d="M16 8V3H3v13h5"/>',
    "download": '<path d="M12 3v12m-4-4 4 4 4-4M4 17v4h16v-4"/>',
    "search": '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 4 4"/>',
    "file": '<path d="M14 2H5v20h14V7zM14 2v6h5M8 12h8M8 16h8"/>',
}


def icon(name: str, cls: str = "") -> str:
    return f'<svg class="icon {cls}" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>'


def page(title: str, description: str, content: str, prefix: str = "./", home: bool = False) -> str:
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light dark">
  <meta name="description" content="{esc(description)}">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:type" content="website">
  <title>{esc(title)}</title>
  <link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml">
  <link rel="preload" href="{prefix}assets/fonts/geist-mono-latin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="{prefix}assets/styles.css">
  <script src="{prefix}assets/theme.js"></script>
  <script src="{prefix}assets/app.js" defer></script>
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>
  <header class="site-header">
    <nav class="header-inner" aria-label="Main navigation">
      <a class="wordmark" href="{prefix}index.html" aria-label="AAB Benchmark home"><span class="brand-mark" aria-hidden="true"><i></i><i></i><i></i></span>AAB<span class="wordmark-tail"> BENCHMARK</span></a>
      <div class="header-links">
        <a class="nav-link active" href="{prefix}index.html#tasks" {'aria-current="page"' if home else ''}>Tasks <span class="nav-count">10</span></a>
        <a class="nav-link about-link" href="{prefix}index.html#about">About</a>
        <a class="nav-link source-link" href="{prefix}data/new_10_tasks.md" download>Source</a>
        <span class="nav-divider" aria-hidden="true"></span>
        <button class="icon-button theme-toggle" type="button" aria-label="Switch to dark theme" title="Switch theme" hidden>{icon("sun", "sun-icon")}{icon("moon", "moon-icon")}</button>
      </div>
    </nav>
  </header>
  {content}
  <footer class="site-footer"><div class="footer-inner">
    <div><a class="footer-brand" href="{prefix}index.html">AAB BENCHMARK</a><p>Ten tasks. Real workflows. Explicit outcomes.</p></div>
    <nav aria-label="Footer navigation"><a href="{prefix}index.html#tasks">Browse tasks</a><a href="{prefix}data/tasks.json" download>Download JSON</a><a href="{prefix}data/new_10_tasks.md" download>Source Markdown</a></nav>
  </div></footer>
  <div class="toast" role="status" aria-live="polite"></div>
</body>
</html>
'''


def stats(tasks: list[dict]) -> str:
    values = [(len(tasks), "Tasks"), (sum(len(t["rubrics"]) for t in tasks), "Outcome criteria"),
              (len({t["category"] for t in tasks}), "Work domains"),
              (sum(len(t["materials"]) for t in tasks), "Support materials")]
    return '<dl class="collection-stats">' + "".join(f'<div><dt>{label}</dt><dd>{value:02d}</dd></div>' for value, label in values) + '</dl>'


def build_catalog(tasks: list[dict]) -> str:
    rows = []
    for task in tasks:
        search = plain_text(" ".join([task["title"], task["category"], task["instruction"], *task["materials"],
                                      *[r["criterion"] + " " + r["source"] for r in task["rubrics"]]]))
        rows.append(f'''<li class="task-row" data-category="{esc(task['category'])}" data-search="{esc(search.lower())}">
          <a class="task-card" href="./tasks/{task['slug']}/index.html">
            <span class="task-id">TASK {task['id']:02d}</span>
            <div class="task-card-body"><span class="category-label">{esc(task['category'])}</span><h3>{esc(task['title'])}</h3><p>{esc(task['summary'])}</p></div>
            <div class="task-card-meta"><span><strong>{len(task['rubrics'])}</strong> criteria</span><span>{len(task['materials'])} support {'file' if len(task['materials']) == 1 else 'files'}</span><span class="view-task">View task</span></div>
          </a>
        </li>''')
    options = "".join(f'<option value="{esc(t["category"])}">{esc(t["category"])}</option>' for t in tasks)
    content = f'''<main id="main" class="container catalog-page" tabindex="-1">
      <section class="catalog-hero" aria-labelledby="catalog-title">
        <p class="eyebrow"><span class="accent-line" aria-hidden="true"></span> THE TASK COLLECTION</p>
        <div class="hero-grid"><h1 id="catalog-title">Real work.<br><span>Ten tasks.</span></h1><div class="hero-description"><p>A collection of practical tasks across everyday professional workflows.</p><p>Explore the instructions, inspect every outcome criterion, and find the materials behind each task.</p><a class="text-link" href="./data/new_10_tasks.md" download>{icon('download')} Download the collection</a></div></div>
        {stats(tasks)}
      </section>
      <section id="tasks" class="task-collection" aria-labelledby="tasks-heading">
        <div class="section-heading"><h2 id="tasks-heading">Explore tasks</h2><span class="section-meta" id="result-count" role="status" aria-live="polite">10 tasks</span></div>
        <form class="catalog-controls" role="search" hidden>
          <div class="search-field">{icon('search')}<label class="sr-only" for="task-search">Search task titles, instructions, rubrics, and materials</label><input type="search" id="task-search" placeholder="Search tasks, instructions, or rubrics…" autocomplete="off"><kbd aria-hidden="true">/</kbd></div>
          <div class="filter-field"><label class="sr-only" for="category-filter">Filter by work domain</label><select id="category-filter"><option value="">All domains</option>{options}</select></div>
        </form>
        <ol class="task-list">{''.join(rows)}</ol>
        <div class="empty-state" hidden><h3>No matching tasks</h3><p>Try another keyword or work domain.</p><button type="button" class="button reset-filters">Clear filters</button></div>
      </section>
      <section id="about" class="about-section" aria-labelledby="about-heading"><div class="section-heading"><h2 id="about-heading">About this collection</h2><span class="section-meta">From brief to outcome</span></div>
        <div class="about-grid"><p>Each task presents a professional scenario with a concrete goal. Its outcome rubric records the individual criteria used to assess the completed work.</p><div><h3>What's included</h3><p>The complete task instructions, all original rubric criteria and their sources, and the support materials listed in the source document. Open files from each task page to preview documents, play media, or download the originals.</p><a class="text-link" href="./data/tasks.json" download>{icon('download')} Download structured task data</a></div></div>
      </section>
    </main>'''
    return page("Tasks | AAB Benchmark", "Explore 10 professional tasks with complete instructions, 183 outcome criteria, and support-material references.", content, home=True)


def load_tutorials(tasks: list[dict]) -> None:
    videos = json.loads((ROOT / "tutorial-videos.json").read_text(encoding="utf-8"))
    if set(videos) != {task["slug"] for task in tasks}:
        raise ValueError("Expected one tutorial video for each task slug")
    for task in tasks:
        task["tutorial"] = videos[task["slug"]]
        task["tutorial"]["guidance_path"] = f"assets/tutorial-guidance/{task['slug']}.md"


def tutorial_player(task: dict) -> str:
    video = task["tutorial"]
    minutes, seconds = divmod(int(video["duration_seconds"]), 60)
    hours, minutes = divmod(minutes, 60)
    duration = f"{hours}:{minutes:02}:{seconds:02}" if hours else f"{minutes}:{seconds:02}"
    title = esc(video["title"])
    url = esc(video["url"])
    guidance = (ROOT / video["guidance_path"]).read_text(encoding="utf-8")
    return f'''<div class="tutorial-block">
      <figure class="tutorial">
        <video controls playsinline preload="none" poster="../../assets/tutorial-posters/{esc(task['slug'])}.jpg" aria-labelledby="tutorial-title">
          <source src="{url}" type="video/mp4">
        </video>
        <figcaption>
          <h2 id="tutorial-title">{title}</h2>
          <dl>
            <div><dt>Video duration</dt><dd><time datetime="PT{video['duration_seconds']}S">{duration}</time></dd></div>
            <div><dt>Original software</dt><dd>{esc(video['original_software'])}</dd></div>
            <div><dt>Open-source software</dt><dd>{esc(video['open_source_software'])}</dd></div>
          </dl>
          <a class="text-link" href="{url}" download>{icon("download")} Download video</a>
        </figcaption>
      </figure>
      <details class="tutorial-guidance" id="reference-guidance">
        <summary>Reference guidance</summary>
        <div class="guidance-body prose">
          <a class="text-link" href="../../{esc(video['guidance_path'])}" download>{icon("download")} Download guidance (.md)</a>
          {render_guidance(guidance)}
        </div>
      </details>
    </div>'''


def build_task(task: dict, tasks: list[dict]) -> str:
    prefix = "../../"
    rows = []
    sources = {material["name"]: material for material in task["material_files"]}
    for rubric in task["rubrics"]:
        source = inline(rubric["source"])
        if rubric["source"] in sources:
            source = f'<a class="rubric-material-link" href="{esc(prefix + sources[rubric["source"]]["page"])}">{source}</a>'
        rows.append(f'<tr id="rubric-{rubric["number"]}"><th scope="row"><a href="#rubric-{rubric["number"]}" aria-label="Criterion {rubric["number"]} permalink">{rubric["number"]:02d}</a></th><td>{inline(rubric["criterion"])}</td><td class="rubric-source">{source}</td></tr>')
    materials = []
    for material in task["material_files"]:
        path = material["path"]
        name = Path(path).name
        extension = Path(path).suffix[1:].upper() or "FILE"
        preview = esc(prefix + material["page"])
        download = esc(download_url(material, prefix))
        materials.append(f'''<li class="material-row">{icon('file')}<div><div class="material-title"><a class="material-name" href="{preview}">{esc(name)}</a><span class="file-type">{esc(extension)}</span><span class="material-size">{file_size(material['bytes'])}</span></div><code class="material-path">{esc(path)}</code><div class="material-actions"><a href="{preview}" aria-label="Open {esc(name)}">Open</a><a href="{download}" download aria-label="Download {esc(name)}">Download original</a></div></div><button type="button" class="icon-button copy-button" data-copy="{esc(path)}" aria-label="Copy path for {esc(name)}" title="Copy file path" hidden>{icon('copy')}</button></li>''')
    materials_html = ('<p class="section-description">Open a file to preview it or download the original. The paths below identify where each file belongs in the task environment.</p><ul class="material-list">' + "".join(materials) + '</ul>') if materials else '<div class="no-materials"><span class="empty-symbol" aria-hidden="true">—</span><div><strong>No support materials</strong><p>This task does not list any support materials.</p></div></div>'
    prev_task = tasks[task["id"] - 2] if task["id"] > 1 else None
    next_task = tasks[task["id"]] if task["id"] < len(tasks) else None
    pagination = []
    for other, direction in [(prev_task, "Previous task"), (next_task, "Next task")]:
        if other:
            pagination.append(f'<a class="pagination-link" href="../{other["slug"]}/index.html"><span>{direction} · {other["id"]:02d}</span><strong>{esc(other["title"])}</strong></a>')
        else:
            pagination.append('<a class="pagination-link" href="../../index.html#tasks"><span>Task collection</span><strong>Browse all 10 tasks</strong></a>')
    task_links = []
    for other in tasks:
        current = 'aria-current="page"' if other["id"] == task["id"] else ""
        task_links.append(f'<li><a href="../{other["slug"]}/index.html" {current}><span>{other["id"]:02d}</span>{esc(other["title"])}</a></li>')
    content = f'''<main id="main" class="container detail-page" tabindex="-1">
      <header class="task-hero">
        <nav class="breadcrumbs" aria-label="Breadcrumb"><ol><li><a href="../../index.html#tasks">Tasks</a></li><li>{esc(task['category'])}</li><li aria-current="page">Task {task['id']:02d}</li></ol></nav>
        <p class="eyebrow"><span class="accent-line" aria-hidden="true"></span> TASK {task['id']:02d} / 10</p>
        <h1>{esc(task['title'])}</h1>
        {tutorial_player(task)}
        <p class="task-summary">{esc(task['summary'])}</p>
        <div class="task-badges"><span class="badge category-badge">{esc(task['category'])}</span><a class="badge" href="#rubrics">{len(task['rubrics'])} outcome criteria</a><a class="badge" href="#support-materials">{len(task['materials'])} support {'file' if len(task['materials']) == 1 else 'files'}</a></div>
      </header>
      <div class="detail-layout">
        <div class="task-content">
          <section id="instruction" class="task-section" aria-labelledby="instruction-title">
            <div class="section-heading"><h2 id="instruction-title">Task instruction</h2><button type="button" class="text-button copy-button" data-copy="{esc(plain_text(task['instruction']))}" hidden>{icon('copy')} Copy instruction</button></div>
            <div class="instruction-panel prose">{prose(task['instruction'])}</div><p class="source-note">Task instruction from the source collection. Formatting has been normalized for reading.</p>
          </section>
          <section id="rubrics" class="task-section" aria-labelledby="rubrics-title">
            <div class="section-heading"><h2 id="rubrics-title">Outcome rubric</h2><span class="section-meta">{len(task['rubrics'])} criteria</span></div>
            <p class="section-description">The expected outcomes for this task, with the source for each criterion.</p>
            <div class="rubric-table-wrapper" role="region" aria-label="Outcome rubric table" tabindex="0"><table class="rubric-table"><caption class="sr-only">Outcome rubric for {esc(task['title'])}</caption><thead><tr><th scope="col">#</th><th scope="col">Outcome criterion</th><th scope="col">Source</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>
          </section>
          <section id="support-materials" class="task-section" aria-labelledby="materials-title">
            <div class="section-heading"><h2 id="materials-title">Support materials</h2><span class="section-meta">{len(task['materials'])} {'file' if len(task['materials']) == 1 else 'files'}</span></div>{materials_html}
          </section>
          {render_agent_runs(task, prefix)}
          <nav class="task-pagination" aria-label="Task navigation">{''.join(pagination)}</nav>
        </div>
        <aside class="task-sidebar" aria-label="Task page navigation"><div class="sidebar-sticky"><nav class="section-nav" aria-label="On this page"><h2>On this page</h2><a href="#instruction" class="current" aria-current="location">Task instruction</a><a href="#rubrics">Outcome rubric <span>{len(task['rubrics'])}</span></a><a href="#support-materials">Support materials <span>{len(task['materials'])}</span></a><a href="#agent-run">Agent run</a></nav><a class="button download-task" href="../../data/{task['slug']}.md" download>{icon('download')} Download task</a><details class="browse-tasks" open><summary>In this collection</summary><ol>{''.join(task_links)}</ol></details></div></aside>
      </div>
    </main>'''
    return page(f"{task['title']} | AAB Benchmark", task["summary"], content, prefix)


def build() -> list[dict]:
    tasks = parse_tasks(SOURCE.read_text(encoding="utf-8"))
    load_materials(tasks, ROOT)
    load_tutorials(tasks)
    load_agent_runs(tasks, ROOT)
    OUTPUT.mkdir(exist_ok=True)
    (OUTPUT / "data").mkdir(exist_ok=True)
    shutil.copytree(ROOT / "assets", OUTPUT / "assets", dirs_exist_ok=True)
    shutil.copyfile(SOURCE, OUTPUT / "data" / "new_10_tasks.md")
    shutil.copyfile(ROOT / "support-materials.json", OUTPUT / "data" / "support-materials.json")
    (OUTPUT / ".nojekyll").write_text("", encoding="utf-8")
    (OUTPUT / "index.html").write_text(build_catalog(tasks), encoding="utf-8")
    for task in tasks:
        directory = OUTPUT / "tasks" / task["slug"]
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "index.html").write_text(build_task(task, tasks), encoding="utf-8")
        (OUTPUT / "data" / f"{task['slug']}.md").write_text(task["markdown"], encoding="utf-8")
        for material in task["material_files"]:
            destination = OUTPUT / material["page"]
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(build_material_page(material, task, ROOT, page, inline, prose), encoding="utf-8")
    public_tasks = [{k: v for k, v in task.items() if k != "markdown"} for task in tasks]
    (OUTPUT / "data" / "tasks.json").write_text(json.dumps(public_tasks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Built {len(tasks)} tasks, {sum(len(t['rubrics']) for t in tasks)} rubric criteria, "
          f"and {sum(len(t['materials']) for t in tasks)} support-material references into docs/.")
    return tasks


if __name__ == "__main__":
    build()
