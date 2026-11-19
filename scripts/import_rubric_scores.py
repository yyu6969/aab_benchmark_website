"""Build the public score manifest from a saved Codex review and its matching Harbor trials."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

from build import ROOT


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def carbon_verdicts(archive, task, trial, checklist_hash, ids):
    replays = archive / "quality_evaluation" / task / "rewardkit_replays" / trial.parent.name
    # Timestamped production replays take precedence over the in-trial verifier.
    candidates = sorted(replays.glob("production_adapter_*/verifier.json"), reverse=True)
    candidates.append(trial / "verifier/verifier.json")
    trajectory_hash = sha256(trial / "agent/trajectory.json")
    for path in candidates:
        if not path.is_file():
            continue
        result = read_json(path)
        if (result.get("mode"), result.get("model")) != ("rewardkit", "gemini-4-carbon"):
            continue
        if path.parent != trial / "verifier":
            replay = read_json(path.parent / "run.json")
            if Path(replay["trial"]) != trial:
                raise ValueError(f"Replay points to another trial: {path}")
        if (result["trajectory_sha256"], result["checklist_sha256"]) != (trajectory_hash, checklist_hash):
            raise ValueError(f"Evidence or checklist hash mismatch: {path}")
        items = result["verdicts"]["items"]
        verdicts = {item["id"]: item["verdict"] for item in items}
        if len(items) != len(ids) or set(verdicts) != ids:
            raise ValueError(f"Rubric ID mismatch: {path}")
        return path.parent.name, verdicts
    raise ValueError(f"No matching Carbon verdicts for {trial.name}")


def import_scores(archive, review):
    recordings = read_json(ROOT / "agent-runs.json")
    bindings = read_json(review / "run_bindings.json")
    with (review / "rubric_scores.csv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    manual = {(r["job"], r["condition"], r["rubric_id"]): r for r in rows}
    if len(manual) != len(rows):
        raise ValueError("Duplicate Codex score")
    scores = {}
    for slug, pair in recordings.items():
        task = pair["guided"]["job"].split("_pi_")[0]
        by_id = {}
        runs = {}
        for condition, run in pair.items():
            binding = bindings[f"{task}/{condition}"]
            trial = Path(binding["trial"])
            episode = trial / "verifier/gym" / run["episode"] / "traj.jsonl"
            if (trial.name, trial.parent.name, str(episode)) != (run["trial"], run["job"], binding["trajectory"]):
                raise ValueError(f"Manual review uses a different run: {slug}/{condition}")
            if sha256(episode) != binding["trajectory_sha256"]:
                raise ValueError(f"Manual review trajectory changed: {episode}")
            checklist = Path(binding["checklist"])
            checklist_hash = sha256(checklist)
            if checklist_hash != binding["checklist_sha256"]:
                raise ValueError(f"Manual review checklist changed: {checklist}")
            items = read_json(checklist)["items"]
            ids = {item["id"] for item in items}
            if len(ids) != len(items) or (by_id and ids != by_id.keys()):
                raise ValueError(f"Checklist differs between conditions: {slug}")
            source, verdicts = carbon_verdicts(archive, task, trial, checklist_hash, ids)
            runs[condition] = {"trial": run["trial"], "harbor_source": source}
            for item in items:
                rubric_id = item["id"]
                row = manual.pop((run["job"], condition, rubric_id))
                target = by_id.setdefault(rubric_id, {"id": rubric_id, "criterion": item["criterion"]})
                if row["task"] != task or row["criterion"] != item["criterion"] or target["criterion"] != item["criterion"]:
                    raise ValueError(f"Criterion mismatch for {rubric_id}")
                if (row["finding"], row["score"]) not in {("met", "1"), ("incomplete", "0"), ("insufficient", "0")}:
                    raise ValueError(f"Invalid Codex finding for {rubric_id}")
                target[condition] = {"harbor": verdicts[rubric_id], "codex": row["finding"]}
        scores[slug] = {"runs": runs, "criteria": list(by_id.values())}
    if manual:
        raise ValueError("Manual review contains scores outside the selected runs")
    return scores


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("review", type=Path)
    args = parser.parse_args()
    scores = import_scores(args.archive, args.review)
    (ROOT / "run-scores.json").write_text(json.dumps(scores, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
