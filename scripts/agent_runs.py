"""Render the two recorded Pi trials on each static task page."""
import json
import re
from html import escape
from pathlib import Path

CONDITIONS = {"guided": "With guidance and rubrics", "unguided": "Without guidance or rubrics"}


HARBOR_SCORES = {"full": 1, "partial": 0, "no_credit": 0, "unresolved": 0}
CODEX_SCORES = {"met": 1, "incomplete": 0, "insufficient": 0}


def load_agent_runs(tasks, root, plain_text):
    manifest = json.loads((root / "agent-runs.json").read_text(encoding="utf-8"))
    scores = json.loads((root / "run-scores.json").read_text(encoding="utf-8"))
    if manifest.keys() != {task["slug"] for task in tasks} or scores.keys() != manifest.keys():
        raise ValueError("Agent runs must cover every task")
    for task in tasks:
        slug = task["slug"]
        if manifest[slug].keys() != CONDITIONS.keys():
            raise ValueError(f"Expected both conditions for {slug}")
        task["agent_runs"] = {}
        grading = scores[slug]
        criteria = grading["criteria"]
        if ([r["criterion"] for r in criteria] != [plain_text(r["criterion"]) for r in task["rubrics"]]
                or len({r["id"] for r in criteria}) != len(criteria)):
            raise ValueError(f"Scores do not match the published criteria for {slug}")
        for condition in CONDITIONS:
            run = manifest[slug][condition]
            source = grading["runs"][condition]
            if source["trial"] != run["trial"]:
                raise ValueError(f"Scores refer to a different trial: {slug}/{condition}")
            rubric_scores = []
            for criterion in criteria:
                harbor = criterion[condition]["harbor"]
                codex = criterion[condition]["codex"]
                rubric_scores.append({"id": criterion["id"], "criterion": criterion["criterion"], "harbor_verdict": harbor, "harbor_score": HARBOR_SCORES[harbor],
                                      "codex_finding": codex, "codex_score": CODEX_SCORES[codex]})
            path = Path("assets/agent-runs") / slug / condition
            folder = root / path
            frames = sorted((p.name for p in folder.glob("frame_*.png") if re.fullmatch(r"frame_\d+\.png", p.name)),
                            key=lambda name: int(name[6:-4]))
            if not frames or len(frames) != run["frame_count"] or not (folder / "traj.jsonl").is_file():
                raise ValueError(f"Incomplete agent recording: {folder}")
            task["agent_runs"][condition] = dict(run, asset_path=path.as_posix(), frames=frames,
                                                 rubric_scores=rubric_scores, harbor_source=source["harbor_source"])


def render_scores(task, condition, title):
    scores = task["agent_runs"][condition]["rubric_scores"]
    count = len(scores)
    harbor_full = sum(s["harbor_score"] for s in scores)
    codex_full = sum(s["codex_score"] for s in scores)
    rows = []
    for rubric, score in zip(task["rubrics"], scores):
        number = rubric["number"]
        cells = []
        for value in (score["harbor_score"], score["codex_score"]):
            mark = '<span class="score-check" aria-hidden="true">✓</span> ' if value else ""
            cells.append(f'<td>{mark}<strong>{value}</strong></td>')
        rows.append(f'<tr data-rubric-id="{escape(score["id"])}"><th scope="row">'
                    f'<a href="#rubric-{number}" aria-label="View outcome criterion {number}">{number:02d}</a> '
                    f'{escape(score["criterion"])}</th>{"".join(cells)}</tr>')
    return f'''<div class="run-scores" id="scores-{condition}">
              <h4>Rubric scores</h4>
              <dl class="score-totals">
                <div><dt>Harbor RewardKit + gemini-4-carbon</dt><dd>{harbor_full} / {count}</dd></div>
                <div><dt>Codex + GPT-6.2 Astra</dt><dd>{codex_full} / {count}</dd></div>
              </dl>
              <details class="score-checklist">
                <summary>View all {count} rubric scores</summary>
                <table aria-label="Rubric scores — {escape(title)}">
                  <thead><tr><th scope="col">Outcome criterion</th><th scope="col">Harbor RewardKit<span>gemini-4-carbon</span></th><th scope="col">Codex<span>GPT-6.2 Astra</span></th></tr></thead>
                  <tbody>{"".join(rows)}</tbody>
                </table>
              </details>
            </div>'''


def render_agent_runs(task, prefix):
    articles = []
    for condition, title in CONDITIONS.items():
        run = task["agent_runs"][condition]
        directory = prefix + run["asset_path"] + "/"
        frames = run["frames"]
        first = directory + frames[0]
        mins, seconds = divmod(run["runtime_seconds"], 60)
        hours, minutes = divmod(mins, 60)
        duration = f"{hours}:{minutes:02d}:{seconds:02d}"
        stats = (("Agent", run["agent"] + " agent"), ("Model", run["model"]),
                 ("Runtime (h:mm:ss)", duration), ("Total tokens", f"{run['total_tokens']:,}"))
        metrics = "".join(f"<div><dt>{label}</dt><dd>{escape(value)}</dd></div>" for label, value in stats)
        options = "".join(f'<option value="{directory}{name}">{i} / {len(frames)} · {name}</option>'
                          for i, name in enumerate(frames, 1))
        links = " ".join(f'<a href="{directory}{name}">{name}</a>' for name in frames)
        note = '<p class="source-note">The recorded Pi session ended with a communication error.</p>' if run["agent_error"] else ""
        articles.append(f'''<article class="agent-run" id="run-{condition}" aria-labelledby="heading-{condition}">
            <h3 id="heading-{condition}">{title}</h3>
            <dl class="run-metrics">{metrics}</dl>{note}
            {render_scores(task, condition, title)}
            <figure class="run-frames">
              <figcaption>Trajectory screenshots <span class="section-meta">{len(frames)} frames</span></figcaption>
              <a class="run-image-link" href="{first}" title="Open full-size screenshot">
                <img src="{first}" loading="lazy" decoding="async" alt="{title} — {frames[0]}">
              </a>
              <div class="frame-controls" hidden>
                <button class="button frame-back" type="button">Previous</button>
                <select aria-label="Screenshot for the run {title.lower()}">{options}</select>
                <button class="button frame-forward" type="button">Next</button>
              </div>
              <noscript><details><summary>All screenshots</summary>{links}</details></noscript>
            </figure>
            <div class="run-trajectory">
              <a class="text-link" href="{directory}traj.jsonl" download>Download trajectory (JSONL)</a>
              <span class="section-meta">{run["event_count"]:,} events</span>
            </div>
            <details class="event-viewer" hidden>
              <summary>Browse trajectory events</summary>
              <p class="event-status source-note" role="status"></p>
              <div class="event-controls" hidden>
                <button type="button" class="button event-back">Previous event</button>
                <label>Event <input type="number" min="1" value="1" max="{run['event_count']}" aria-label="Event number for the run {title.lower()}"> of {run['event_count']:,}</label>
                <button type="button" class="button event-forward">Next event</button>
              </div>
              <pre class="event-record" tabindex="0" hidden></pre>
            </details>
          </article>''')
    return f'''<section id="agent-run" class="task-section" aria-labelledby="agent-run-title">
            <div class="section-heading"><h2 id="agent-run-title">Agent run</h2></div>
            <p class="section-description">Runtime covers Pi’s execution. Total tokens are input plus output, including cached input once. Trajectory downloads omit session credentials and redact authentication-related payloads.</p>
            {"".join(articles)}
          </section>'''
