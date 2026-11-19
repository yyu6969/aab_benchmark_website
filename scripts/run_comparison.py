"""Compare the two published trials per task against the source video's measured duration."""
import csv
import hashlib
import io
from html import escape
from pathlib import Path

from agent_runs import CONDITIONS

CHARTS = {
    "tokens": "Total tokens",
    "runtime": "Agent runtime",
    "score": "Rubric score",
}


def comparison_rows(tasks):
    rows = []
    for task in sorted(tasks, key=lambda t: t["tutorial"]["duration_seconds"]):
        for condition in CONDITIONS:
            run = task["agent_runs"][condition]
            scores = run["rubric_scores"]
            rows.append(dict(
                task=task["tutorial"]["original_software"], condition=condition,
                video_seconds=task["tutorial"]["duration_seconds"],
                total_tokens=run["total_tokens"], agent_seconds=run["runtime_seconds"],
                criteria=len(scores), harbor_points=sum(s["harbor_score"] for s in scores),
                codex_points=sum(s["codex_score"] for s in scores),
                agent_error=run["agent_error"], trial=run["trial"], slug=task["slug"],
            ))
    return rows


def csv_text(rows):
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=rows[0], lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def render_comparison(tasks, root, output):
    rows = comparison_rows(tasks)
    data = csv_text(rows)
    (output / "data/run-comparison.csv").write_text(data, encoding="utf-8")
    digest = hashlib.sha256(data.encode()).hexdigest()
    figures = []
    for key, title in CHARTS.items():
        path = Path("assets/run-comparison") / f"{key}.svg"
        if digest not in (root / path).read_text(encoding="utf-8"):
            raise ValueError("Plot data changed. Regenerate with python scripts/plot_run_comparison.py")
        figures.append(f'<figure id="{key}" class="comparison-figure"><figcaption><h2 class="sr-only">{title}</h2>'
                       f'<a class="text-link" href="../{path}">Open full-size plot</a>'
                       f'<a class="text-link" href="../{path}" download>Download SVG</a></figcaption>'
                       f'<object type="image/svg+xml" data="../{path}" aria-label="{title} by tutorial duration">'
                       f'<img src="../{path}" alt="{title} by tutorial duration. Exact values are in the table below.">'
                       f'</object></figure>')
    table = []
    for row in rows:
        mins, secs = divmod(round(row["video_seconds"]), 60)
        run_mins, run_secs = divmod(row["agent_seconds"], 60)
        link = f'../tasks/{row["slug"]}/index.html#run-{row["condition"]}'
        interrupted = " (interrupted)" if row["agent_error"] else ""
        table.append(f'<tr><th scope="row"><a href="{link}">{escape(row["task"])}</a></th>'
                     f'<td>{mins}:{secs:02d}</td><td>{row["condition"].capitalize()}{interrupted}</td>'
                     f'<td>{row["total_tokens"]:,}</td><td>{run_mins}:{run_secs:02d}</td>'
                     f'<td>{row["harbor_points"]} / {row["criteria"]}</td>'
                     f'<td>{row["codex_points"]} / {row["criteria"]}</td></tr>')
    errors = sum(row["agent_error"] for row in rows)
    return f'''<main class="container comparison-page" id="main" tabindex="-1">
      <a class="text-link" href="../index.html">Back to tasks</a>
      <h1>Run comparisons</h1>
      <p>Each task has one Pi run with guidance and rubrics and one without. Lines connect distinct tasks in order of tutorial video duration.</p>
      <p>Tokens include input and output, counting cached input once. Runtime covers Pi’s execution. Scores show the percentage of criteria earning 1 under each grader’s binary scoring rule.</p>
      <a class="text-link" href="../data/run-comparison.csv" download>Download plot data (CSV)</a>
      {''.join(figures)}
      <details class="comparison-values"><summary>View exact values by task</summary>
        <p>{errors} recorded runs ended with a communication error. Their observed runtime, tokens, and rubric scores are included.</p>
        <div class="comparison-scroll" tabindex="0" role="region" aria-label="Run comparison data">
          <table><thead><tr><th scope="col">Task</th><th scope="col">Video (min:sec)</th>
          <th scope="col">Run</th><th scope="col">Tokens</th><th scope="col">Runtime (min:sec)</th>
          <th scope="col">Harbor points</th><th scope="col">Codex points</th></tr></thead>
          <tbody>{''.join(table)}</tbody></table>
        </div>
      </details>
    </main>'''
