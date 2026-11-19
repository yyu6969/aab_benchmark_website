# AAB Benchmark task website

A static website for the 10 tasks in `new_10_tasks.md`, inspired by the typography and task-page structure of [TimelineBench](https://timelinebench.tensortest.com/tasks/klug-brand-story).

The site includes a searchable task catalog, 10 permanent task pages, complete instructions, all 183 outcome criteria with sources, and 15 openable support materials. It also includes light and dark themes, copy controls, Markdown and JSON downloads, responsive layouts, and print styles.

Support materials have dedicated preview pages and original-file downloads. PDFs open in the browser, Word documents have text previews that show tracked insertions and deletions, the style guide is rendered as Markdown, and audio and video have native playback controls. DWG files download for opening in a compatible CAD application.

Small originals and full-length 540p MP4 and WebM video previews are included in `assets/materials/` and copied into the published site. Original video files use the repository's `support-materials-v1` GitHub release to accommodate GitHub's file-size limits. `support-materials.json` maps all 15 original task paths to their pages and files, with original file sizes and SHA-256 checksums. Do not substitute a compressed preview for an original task input.

## Publish on GitHub Pages

Each task page includes its tutorial recording, measured duration, original software, and open-source benchmark application. The player streams the original MP4 from the repository’s `tutorial-videos-v1` release. Task slugs in `tutorial-videos.json` map the recordings and software to their pages.

Expand **Reference guidance** beneath a video to read its walkthrough or download the Markdown. The public copies of the ten `reference_guidance.md` files are in `assets/tutorial-guidance/`, named by task slug. The Salesforce guide redacts the account-recovery answer.

1. Push the project to a GitHub repository on `main` or `master`.
2. In **Settings → Pages → Build and deployment**, select **GitHub Actions** as the source.
3. Open **Actions → Deploy task website to GitHub Pages** and run the workflow, or push a commit to trigger it.

The workflow builds and validates the site, then publishes `docs/`. The site works at both `https://USERNAME.github.io/REPOSITORY/` and a custom domain because all internal URLs are relative.

You can also publish the checked-in `docs/` folder using **Deploy from a branch**, selecting your branch and `/docs`. In that case, disable the included Actions workflow to avoid two deployment methods, and run the build locally before committing content updates.

## Edit and preview

Python 3.9 or newer is sufficient. No package installation or frontend build tools are required.

```sh
# After editing the source Markdown or the assets:
python3 scripts/build.py
python3 scripts/check.py

# Serve the website locally:
python3 -m http.server 8000 --directory docs
```

Open `http://localhost:8000`. Individual pages can also be opened directly from `docs/`; search and theme controls work without a server.

## Agent runs

Each task page compares the selected guided and unguided Harbor trials. The screenshot control opens every numbered Gym episode frame in chronological order. The JSONL download keeps the recorded event sequence. It omits private session connection details and redacts authentication-related payloads across linked tool events. The benchmark archive retains the originals.

Runtime covers the Pi agent execution interval. Total tokens sum reported input and output across calls and include cached input once. The selection includes the newer unguided AutoCAD run and the graded unguided Asana run. A communication error is indicated for the three affected guided trials.

The selected trials are pinned in `agent-runs.json`. Their files live in `assets/agent-runs/`, so building or serving the site does not require the benchmark machine. To refresh the selection from the archive, run `python3 scripts/import_agent_runs.py /path/to/agent_runtime_tokens.csv` and then the normal build and check commands.

An **Output files** subsection links the deliverables Harbor collected for that specific trial. The importer selects the approved guest paths from its artifact manifest and records a SHA-256 hash for each download. Runs without collected deliverables omit the subsection.
The Google Classroom gradebook is excluded from the public downloads.

Each run includes a criterion-by-criterion comparison of Harbor RewardKit with `gemini-4-carbon` and the independent Codex review with GPT-6.2 Astra. Harbor full credit maps to 1. Partial, no-credit and unresolved verdicts each map to 0. Codex reports binary scores and distinguishes incomplete work from insufficient evidence. The totals count criteria with full credit in each recorded run.

The checked-in `run-scores.json` binds the scores to the selected trials and rubric IDs. To refresh it, run `python3 scripts/import_rubric_scores.py /path/to/aab_benchmark_archive /path/to/manual_review` before the normal build. The importer uses the latest matching production Carbon replay when available, checks trajectory and checklist hashes, and publishes only the verdicts and criterion text.

The catalog links to three downloadable plots comparing the selected runs by tutorial duration. After changing the run or video data, regenerate the SVGs with `python scripts/plot_run_comparison.py` in a Matplotlib environment, then build as usual. The build checks the figures against the downloadable CSV and serves the checked-in plots without a plotting dependency.

## Files

| Path | Purpose |
| --- | --- |
| `new_10_tasks.md` | Source of truth for task titles, instructions, rubrics, and material paths |
| `scripts/build.py` | Dependency-free site generator; edit summaries, categories, or slugs here |
| `assets/` | Original site styles, browser scripts, icon, and self-hosted fonts |
| `assets/materials/` | Original small support files and browser-compatible video previews |
| `support-materials.json` | Support-file mapping, original checksums, preview paths, and original-video release links |
| `docs/` | Generated website ready to publish |
| `docs/data/` | Original source, individual task Markdown, and structured JSON downloads |
| `.github/workflows/pages.yml` | GitHub Pages build and deployment |

The generator normalizes Markdown export escaping and whitespace for display, while preserving task wording, file paths, and all rubric rows. The original source is included unchanged as a download. There are no analytics, accounts, or backend services. Original-video download links point to GitHub Releases.

Geist fonts are distributed under the SIL Open Font License; see `assets/fonts/LICENSE`.
