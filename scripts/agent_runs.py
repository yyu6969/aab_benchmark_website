"""Render instruction-only trials and the earlier two-condition comparison."""
import json
import re
from html import escape
from pathlib import Path
from materials import file_size, file_url

CONDITIONS = {"guided": "With guidance and rubrics", "unguided": "Without guidance or rubrics"}


HARBOR_SCORES = {"full": 1, "partial": 0, "no_credit": 0, "unresolved": 0}
CODEX_SCORES = {"met": 1, "incomplete": 0, "insufficient": 0}


def load_agent_runs(tasks, root, plain_text):
    manifest = json.loads((root / "agent-runs.json").read_text(encoding="utf-8"))
    scores = json.loads((root / "run-scores.json").read_text(encoding="utf-8"))
    if manifest.keys() != {task["slug"] for task in tasks} or scores.keys() != manifest.keys():
        raise ValueError("Agent runs must cover every task")
    instruction_runs = json.loads((root / "instruction-runs.json").read_text(encoding="utf-8"))
    if set(instruction_runs) != {t["slug"] for t in tasks if "id" in t["rubrics"][0]}:
        raise ValueError("Expected one instruction-only run per reviewed task")
    for task in tasks:
        slug = task["slug"]
        if slug in instruction_runs:
            run = instruction_runs[slug]
            graded = run.get("graded_rubrics", task["rubrics"])
            ids = {r["id"] for r in graded}
            if len(ids) != len(graded) or [r["number"] for r in graded] != list(range(1, len(graded) + 1)):
                raise ValueError(f"Invalid criterion order or repeated criterion in trial for {slug}")
            if run["rows"].keys() - ids or (run["status"] == "Graded" and run["rows"].keys() != ids):
                raise ValueError(f"Instruction-only verdicts differ from the rubric for {slug}")
            task["instruction_run"] = run
        if manifest[slug].keys() != CONDITIONS.keys():
            raise ValueError(f"Expected both conditions for {slug}")
        task["agent_runs"] = {}
        grading = scores[slug]
        criteria = grading["criteria"]
        reviewed = "clips" in task["rubrics"][0]
        if len({r["id"] for r in criteria}) != len(criteria) or (
                not reviewed and [r["criterion"] for r in criteria] != [plain_text(r["criterion"]) for r in task["rubrics"]]):
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
            if reviewed:
                task["agent_runs"][condition]["score_basis"] = "earlier_rubric"


def render_scores(task, condition, title):
    scores = task["agent_runs"][condition]["rubric_scores"]
    count = len(scores)
    harbor_full = sum(s["harbor_score"] for s in scores)
    codex_full = sum(s["codex_score"] for s in scores)
    rows = []
    historical = "clips" in task["rubrics"][0]
    heading = "Rubric scores · earlier rubric" if historical else "Rubric scores"
    for number, score in enumerate(scores, 1):
        cells = []
        for value in (score["harbor_score"], score["codex_score"]):
            mark = '<span class="score-check" aria-hidden="true">✓</span> ' if value else ""
            cells.append(f'<td>{mark}<strong>{value}</strong></td>')
        reference = (f'{number:02d}' if historical else
                     f'<a href="#rubric-{number}" aria-label="View outcome criterion {number}">{number:02d}</a>')
        rows.append(f'<tr data-rubric-id="{escape(score["id"])}"><th scope="row">'
                    f'{reference} '
                    f'{escape(score["criterion"])}</th>{"".join(cells)}</tr>')
    return f'''<div class="run-scores" id="scores-{condition}">
              <h4>{heading}</h4>
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


def render_outputs(files, directory, condition):
    if not files:
        return ""
    items = []
    for item in files:
        name = escape(item["name"])
        href = directory + "outputs/" + file_url(item["name"])
        preview = f' <a href="{href}" aria-label="View {name}">View PDF</a>' if item["name"].lower().endswith(".pdf") else ""
        items.append(f'<li><a href="{href}" download aria-label="Download {name}">{name}</a>'
                     f'<span class="section-meta">{file_size(item["bytes"])}</span>{preview}</li>')
    return (f'<section class="run-outputs" id="outputs-{condition}" aria-labelledby="outputs-title-{condition}">'
            f'<h4 id="outputs-title-{condition}">Output files</h4><ul>{"".join(items)}</ul></section>')


def render_agent_runs(task, prefix, inline):
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
            {render_scores(task, condition, title)}{render_outputs(run["output_files"], directory, condition)}
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
    history = "".join(articles)
    intro = '<p class="section-description">Runtime covers Pi’s execution. Total tokens are input plus output, including cached input once. Trajectory downloads omit session credentials and redact authentication-related payloads.</p>'
    if "instruction_run" in task:
        content = render_instruction_run(task, prefix, inline)
        content += f'<details class="earlier-runs"><summary>Earlier guided and unguided runs</summary>{intro}{history}</details>'
    else:
        content = intro + "\n            " + history
    return f'''<section id="agent-run" class="task-section" aria-labelledby="agent-run-title">
            <div class="section-heading"><h2 id="agent-run-title">Agent run</h2></div>
            {content}
          </section>'''


EVIDENCE_TYPES = {"screenshots": "Screenshots", "tools": "Tool calls and results",
                  "environment": "Live environment records", "analysis": "Verification evidence"}


def evidence_links(ids, evidence, number):
    links = []
    for kind, title in EVIDENCE_TYPES.items():
        refs = [ref for ref in ids if evidence[ref]["kind"] == kind]
        if refs:
            links.append(f'<li><button type="button" class="evidence-link" aria-haspopup="dialog" '
                         f'data-evidence-ids="{escape(" ".join(refs))}" data-criterion="{number}" '
                         f'data-kind="{kind}">{title} ({len(refs)})</button></li>')
    return '<ul class="run-citations">' + "".join(links) + '</ul>'


def evidence_code(value):
    text = value if isinstance(value, str) else json.dumps(value, indent=2, ensure_ascii=False)
    # Character references preserve the recorded line endings in HTML as well as in the popup.
    encoded = escape(text).replace("\r", "&#13;").replace("\n", "&#10;")
    return '<pre tabindex="0"><code>' + encoded + '</code></pre>'


def evidence_template(ref, item, directory):
    label = escape(item["label"])
    blocks = []
    if item.get("inspection"):
        check = item["inspection"]
        args = json.dumps(check["view"])
        if check["page"] != 1:
            args += f', page={check["page"]}'
        blocks.append('<p class="inspection-call">Verifier check <code>inspect_view(' + escape(args) + ')</code></p>')
    if item.get("explanation"):
        explanation = item["explanation"]
        blocks.append('<dl class="record-explanation"><dt>Purpose</dt><dd>' + escape(explanation["purpose"])
                      + '</dd><dt>Observed result</dt><dd>' + escape(explanation["result"]) + '</dd></dl>')
        if example := explanation.get("example"):
            blocks.append('<details class="inspection-example"><summary>' + escape(example["title"])
                          + '</summary><p>' + escape(example["instruction"]) + '</p>' + evidence_code(example["code"])
                          + '<h5>Example output</h5>' + evidence_code(example["output"]) + '</details>')
    if item.get("availability"):
        blocks.append('<p>' + escape(item["availability"]) + '</p>')
    elif item.get("file"):
        src = directory + file_url(item["file"])
        if item.get("cropped"):
            label += " · cropped"
        blocks.append(f'<a href="{src}" aria-label="Open {label} at full size"><img src="{src}" alt="{label}"></a>')
    elif item["kind"] == "tools" and isinstance(item["record"], dict) and "tool_calls" in item["record"]:
        step = item["record"]
        blocks.append('<p class="evidence-meta">' + escape(" · ".join(filter(None, [step.get("timestamp"), step.get("status")]))) + '</p>')
        for call in step["tool_calls"]:
            blocks.append('<h5>Tool call · ' + escape(call["function_name"]) + '</h5>')
            args = call["arguments"]
            if isinstance(args, dict) and isinstance(args.get("command"), str):
                blocks.append(evidence_code(args["command"]))
                options = {k: v for k, v in args.items() if k != "command"}
                if options:
                    blocks.append(evidence_code(options))
            else:
                blocks.append(evidence_code(args))
            blocks.append('<p class="evidence-meta">' + escape(call["tool_call_id"]) + '</p>')
        for result in step["results"]:
            blocks.append('<h5>Tool result</h5>' + evidence_code(result.get("text", result)))
            if "call_id" in result:
                blocks.append('<p class="evidence-meta">' + escape(result["call_id"]) + '</p>')
    else:
        title = {"environment": "Original inspection result", "analysis": "Analysis result", "tools": "Original tool record"}[item["kind"]]
        blocks.append(f'<h5>{title}</h5>')
        blocks.append(evidence_code(item["record"]))
    return (f'<template id="evidence-{escape(ref)}"><section class="evidence-record"><h4>{label}</h4>'
            f'<p class="evidence-meta">{escape(ref)}</p>{"".join(blocks)}</section></template>')


def evidence_viewer(evidence, directory):
    if not evidence:
        return ""
    templates = "".join(evidence_template(ref, item, directory) for ref, item in evidence.items())
    return (templates + '<dialog class="run-evidence" aria-labelledby="evidence-heading">'
            '<div class="clip-toolbar"><h3 id="evidence-heading">Evidence</h3><form method="dialog">'
            '<button class="button" autofocus>Close</button></form></div><div class="evidence-body"></div></dialog>')


def render_instruction_run(task, prefix, inline):
    run = task["instruction_run"]
    directory = prefix + f'assets/agent-runs/{task["slug"]}/{run["trial"]}/'
    summary = [("Solver", "Pi · " + run["model"] + " · " + run["thinking"])]
    if run.get("judge_model"):
        summary.append(("Verifier", "Codex · " + run["judge_model"] + " · " + run["judge_effort"]))
    if "runtime_seconds" in run:
        mins, sec = divmod(run["runtime_seconds"], 60)
        hours, mins = divmod(mins, 60)
        summary.append(("Runtime", f"{hours}:{mins:02}:{sec:02}"))
    if "total_tokens" in run:
        summary.append(("Total tokens", f"{run['total_tokens']:,}"))
    metrics = "".join(f"<div><dt>{key}</dt><dd>{escape(value)}</dd></div>" for key, value in summary)
    rows = []
    historical = "graded_rubrics" in run
    for rubric in run.get("graded_rubrics", task["rubrics"]):
        key, number = rubric["id"], rubric["number"]
        record = run["rows"].get(key, {})
        score = record.get("score")
        evidence = run["evidence"]
        ids = [ref for ref in record.get("observations", [])
               if key not in evidence[ref].get("hidden_for_criteria", [])]
        reason = record.get("reason", "")
        # Keep the original verdict text in the JSON download. Render named references for readers.
        reason = re.sub(r'(?<=\.)\s+obs_\w+(?:,\s*obs_\w+)*\.$', '', reason)
        reason = re.sub(r'\bobs_\w+\b', lambda m: evidence.get(m[0], {}).get("label", m[0]), reason)
        if not reason:
            reason = "Awaiting a verifier verdict." if not record else "No reason recorded."
        refs = evidence_links(ids, evidence, number) if ids else (
            "No evidence cited yet." if not record else "No evidence cited.")
        value = "null" if score is None else str(score)
        carried = ' <small>(Original verdict retained.)</small>' if record.get("origin") == "carried_forward" else ""
        reference = f'{number:02}' if historical else f'<a href="#rubric-{number}">{number:02}</a>'
        rows.append(f'<tr data-rubric-id="{escape(key)}"><th scope="row">{reference}</th>'
                    f'<td>{inline(rubric["criterion"])}</td><td data-label="Score"><strong>{value}</strong></td>'
                    f'<td data-label="Reason">{escape(reason)}{carried}</td><td data-label="Evidence">{refs}</td></tr>')
    scored = [r["score"] for r in run["rows"].values() if r["score"] is not None]
    total = len(rows)
    status = (f'{sum(scored)} / {total}' if len(scored) == total else
              f'{len(scored)} / {total} criteria scored · null = no score recorded')
    archive_link = ""
    review_info = ""
    review = run.get("reverification")
    if review:
        status = f"{sum(scored)} / {total}"
        if len(scored) < total:
            status += f" · {total - len(scored)} unresolved"
        reviewed = f"Codex regraded {review['changed']} criteria using evidence saved from this run."
        if review["carried"]:
            reviewed += f" {review['carried']} unchanged criteria retain their original verdicts."
        review_info = (f'<p>{reviewed} Live environment records were captured before the original guest shut down.</p>'
                       f'<p><a class="text-link" href="{directory}{file_url(review["results"])}" download>Download revised verification (ZIP)</a></p>')
        if review.get("preview"):
            review_info += (f'<p><a class="text-link" href="{directory}{file_url(review["preview"])}">'
                            'Watch the review render of the saved project</a></p>')
    if archive := run.get("archive"):
        captured = archive.get("snapshot_at")
        label = "Download public run snapshot" if captured else "Download public run results"
        if review:
            label = "Download original run snapshot" if captured else "Download original run results"
        note = f"<br>Snapshot taken {escape(captured)}." if captured else ""
        archive_link = (f'<p><a class="text-link" href="{escape(archive["url"], quote=True)}">'
                        f'{label} (ZIP · {file_size(archive["bytes"])})</a>{note}</p>')
    heading = "Task instruction · earlier rubric" if historical else "Task instruction"
    return (f'<article class="agent-run instruction-run" id="run-instruction-only"><details><summary>{heading}</summary>'
            f'<dl class="run-metrics">{metrics}</dl>{archive_link}{review_info}<h4>{status}</h4>'
            '<div class="rubric-table-wrapper" role="region" aria-label="Agent run scores" tabindex="0">'
            '<table class="rubric-table run-results"><caption class="sr-only">Task instruction run results</caption>'
            '<thead><tr><th scope="col">#</th><th scope="col">Outcome criterion</th><th scope="col">Score</th>'
            '<th scope="col">Reason</th><th scope="col">Evidence</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table></div>'
            f'{render_outputs(run.get("output_files", []), directory, "instruction-only")}</details></article>'
            + evidence_viewer(run["evidence"], directory))
