"""Regenerate the three shareable Matplotlib figures after the pinned trial data change."""
import hashlib
from xml.dom import minidom

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator, MultipleLocator

from agent_runs import CONDITIONS, load_agent_runs
from build import ROOT, SOURCE, load_tutorials, parse_tasks, plain_text
from run_comparison import CHARTS, comparison_rows, csv_text


def label_markers(path, tooltips):
    svg = minidom.parse(str(path))
    for series in svg.getElementsByTagName("g"):
        labels = tooltips.get(series.getAttribute("id"))
        if labels is None:
            continue
        markers = series.getElementsByTagName("use")
        if len(markers) != len(labels):
            raise ValueError(f"Unexpected marker count in {path}")
        for marker, label in zip(markers, labels):
            group = svg.createElement("g")
            title = svg.createElement("title")
            title.appendChild(svg.createTextNode(label))
            marker.parentNode.replaceChild(group, marker)
            group.appendChild(title)
            group.appendChild(marker)
    path.write_text("\n".join(line.rstrip() for line in svg.toxml().splitlines()) + "\n", encoding="utf-8")


def plot_runs(tasks):
    rows = comparison_rows(tasks)
    digest = hashlib.sha256(csv_text(rows).encode()).hexdigest()
    folder = ROOT / "assets/run-comparison"
    folder.mkdir(exist_ok=True)
    plt.rcParams.update({"font.size": 11, "svg.fonttype": "none", "svg.hashsalt": "aab-comparison",
                         "axes.spines.top": False, "axes.spines.right": False,
                         "axes.edgecolor": "#9ca3af", "text.color": "#24232b",
                         "axes.labelcolor": "#393844", "xtick.color": "#514f5e", "ytick.color": "#514f5e"})
    panels = {
        "tokens": [("Total tokens (millions)", lambda r: r["total_tokens"] / 1e6)],
        "runtime": [("Agent runtime (minutes)", lambda r: r["agent_seconds"] / 60)],
        "score": [(label, lambda r, field=field: 100 * r[field] / r["criteria"])
                  for label, field in (("Harbor RewardKit + gemini-4-carbon", "harbor_points"),
                                       ("Codex + GPT-6.2 Astra", "codex_points"))],
    }
    styles = {
        "guided": dict(color="#6139b4", marker="o", markersize=5.5, linestyle="-", zorder=3),
        "unguided": dict(color="#a7450d", marker="s", markersize=9, markerfacecolor="none",
                         markeredgewidth=1.5, linestyle="--", zorder=2),
    }
    last = max(r["video_seconds"] for r in rows) / 60
    for key, panel in panels.items():
        score = key == "score"
        fig, axes = plt.subplots(len(panel), 1, figsize=(8.6, 7.2 if score else 4.5), sharex=True, squeeze=False)
        fig.subplots_adjust(left=.115, right=.965, bottom=.11 if score else .16,
                            top=.81 if score else .77, hspace=.56)
        fig.suptitle(f"{CHARTS[key]} by tutorial duration", x=.115, y=.975, ha="left",
                     fontsize=17, fontweight="bold")
        tooltips = {}
        for index, (ax, (label, measure)) in enumerate(zip(axes.flat, panel)):
            for condition, legend in CONDITIONS.items():
                points = [r for r in rows if r["condition"] == condition]
                series_id = f"{key}-{index}-{condition}"
                ax.plot([r["video_seconds"] / 60 for r in points], [measure(r) for r in points],
                        gid=series_id, label=legend, linewidth=1.8, **styles[condition])
                unit = {"tokens": "M tokens", "runtime": " min", "score": "%"}[key]
                tooltips[series_id] = [f'{r["task"]} · {legend} · video {r["video_seconds"] / 60:.2f} min'
                                       f' · {measure(r):.2f}{unit}' for r in points]
            ax.set_xlim(0, last * 1.045)
            ax.set_axisbelow(True)
            ax.grid(axis="y", color="#e2e3e8", linewidth=.8)
            ax.xaxis.set_major_locator(MaxNLocator(nbins=8, steps=[1, 2, 5, 10]))
            if score:
                ax.set_title(label, loc="left", pad=8, fontsize=12)
                ax.set_ylabel("Criteria earning 1 (%)")
                ax.set_ylim(-4, 106)
                ax.yaxis.set_major_locator(MultipleLocator(25))
            else:
                ax.set_ylabel(label)
                ax.set_ylim(bottom=0)
        axes[-1, 0].set_xlabel("Tutorial video duration (minutes)", labelpad=8)
        handles, labels = axes[0, 0].get_legend_handles_labels()
        fig.legend(handles, labels, loc="upper left", bbox_to_anchor=(.108, .923 if score else .89),
                   ncol=2, frameon=False, borderaxespad=0, fontsize=10, handlelength=2.8)
        fig.savefig(folder / f"{key}.svg", metadata={"Date": None, "Title": f"{CHARTS[key]} by tutorial duration",
                                                    "Source": digest})
        label_markers(folder / f"{key}.svg", tooltips)
        plt.close(fig)


if __name__ == "__main__":
    tasks = parse_tasks(SOURCE.read_text(encoding="utf-8"))
    load_tutorials(tasks)
    load_agent_runs(tasks, ROOT, plain_text)
    plot_runs(tasks)
