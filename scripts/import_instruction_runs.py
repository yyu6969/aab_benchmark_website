"""Import one instruction-only Harbor trial per reviewed task; latest retry wins."""
import argparse
import hashlib
import json
import re
import shutil
from datetime import datetime
from pathlib import Path

from build import ROOT, SOURCE, parse_tasks
from import_agent_runs import TASKS, import_outputs


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def action_records(trajectory):
    for step in trajectory["steps"]:
        for call in step.get("tool_calls", []):
            action = {"step": step["step_id"], "tool": call["function_name"],
                      "status": step.get("extra", {}).get("execution", {}).get("status")}
            args = call.get("arguments", {})
            for key in ("coordinate", "pixels"):
                if key in args:
                    action[key] = args[key]
            yield action


def observation(record, verifier, folder, actions, previous):
    key = record["id"]
    if not record["ok"]:
        return {"label": "Inspection unavailable"}
    source = record["source"]
    if source == "recorded_screenshot" or record.get("view") == "screen":
        label = f'Screenshot · step {record["pi_step"]}' if "pi_step" in record else "Final screenshot"
        item = {"label": label}
        path = record["data"]
        if not re.fullmatch(r"(?:final-screen|recorded-screenshots/pi_\d+_\d+)\.jpg", path):
            raise ValueError(f"Unexpected screenshot path for {key}")
        # Selected clinical and classroom frames can include unrelated chart or roster details.
        if folder.parent.name not in {"complete-sign-clinical-note", "update-class-gradebook"}:
            shutil.copyfile(verifier / path, folder / Path(path).name)
            item["file"] = Path(path).name
    elif source == "trajectory":
        step = json.loads(record["data"])["step"]
        action = actions.get(step)
        item = {"label": f"Step {step} · " + (action["tool"] if action else "trajectory")}
        if action:
            item["action"] = action
    elif source == "live_environment":
        name = record["view"].replace("_", " ").capitalize()
        page = f' · page {record["page"]}' if record.get("pages", 1) > 1 else ""
        item = {"label": name + page}
    else:
        raise ValueError(f"Unknown evidence source {source}")
    item["source"] = source
    # Retain editorial transcriptions only for the exact same observation.
    digest = hashlib.sha256(json.dumps(record, sort_keys=True).encode()).hexdigest()
    item["record_sha256"] = digest
    if previous.get("record_sha256") == digest and previous.get("note"):
        item["note"] = previous["note"]
    return item


def import_trial(trial, task, previous):
    config = read(trial / "config.json")
    if config.get("extra_instruction_paths") or config.get("agent", {}).get("kwargs", {}).get("extra_instruction_paths"):
        raise ValueError(f"Expected instruction-only trial: {trial.name}")
    package = Path(config["task"]["path"])
    instruction = package.joinpath("instruction.md").read_bytes()
    checklist = read(package / "environment/verifier/checklist.json")["items"]
    expected = {row["id"]: row["criterion"] for row in task["rubrics"]}
    if expected != {item["id"]: item["criterion"] for item in checklist}:
        raise ValueError(f"Published criterion differs from the trial package: {task['slug']}")
    rt = read(trial / "agent/pi_runtime.json")
    result = read(trial / "result.json") if (trial / "result.json").exists() else {}
    verifier = trial / "verifier"
    judge = read(verifier / "live-judge.json") if (verifier / "live-judge.json").exists() else {}
    instruction_hash = hashlib.sha256(instruction).hexdigest()
    if judge and judge["instruction_sha256"] != instruction_hash:
        raise ValueError(f"Judge instruction differs from the trial package: {trial}")
    items = judge.get("items", [])
    if len({i["id"] for i in items}) != len(items) or not {i["id"] for i in items} <= expected.keys():
        raise ValueError(f"Unknown or duplicate verdict: {trial.name}")
    if judge.get("decided") and len(items) != len(expected):
        raise ValueError(f"Incomplete final judge report: {trial.name}")
    run = {"job": trial.parent.name, "trial": trial.name, "model": rt["model"], "thinking": rt["requested_thinking_level"],
           "instruction_sha256": instruction_hash, "judge_model": judge.get("model"), "judge_effort": judge.get("reasoning_effort"),
           "status": "Graded" if judge.get("decided") else "No final verdict",
           "rows": {}, "evidence": {}}
    for item in items:
        score = item["rating"]
        if score is not None and (type(score) is not int or score not in (0, 1)):
            raise ValueError(f"Invalid binary rating: {item['id']}")
        run["rows"][item["id"]] = {"score": score, "reason": item.get("reason") or "",
                                   "observations": list(dict.fromkeys(item.get("observations", [])))}
    folder = ROOT / "assets/agent-runs" / task["slug"] / trial.name
    folder.mkdir(parents=True, exist_ok=True)
    if previous.get("trial") != trial.name:
        previous = {}
    if result:
        runtime = result["agent_execution"]
        if runtime.get("finished_at") and runtime.get("started_at"):
            start, end = [datetime.fromisoformat(runtime[k].replace("Z", "+00:00")) for k in ("started_at", "finished_at")]
            run["runtime_seconds"] = round((end - start).total_seconds())
        usage = result.get("agent_result") or {}
        if usage.get("n_input_tokens") is not None and usage.get("n_output_tokens") is not None:
            run["total_tokens"] = usage["n_input_tokens"] + usage["n_output_tokens"]
        run["output_files"] = import_outputs(trial, task["slug"], folder)
    trajectory = trial / "agent/trajectory.json"
    actions = {}
    if trajectory.exists() and (result or judge):
        actions = {a["step"]: a for a in action_records(read(trajectory))}
        with (folder / "actions.jsonl").open("w", encoding="utf-8") as stream:
            for a in actions.values():
                stream.write(json.dumps(a, ensure_ascii=False) + "\n")
        run["action_count"] = len(actions)
    needed = {k for item in run["rows"].values() for k in item["observations"]}
    if needed:
        with (verifier / "live-observations.jsonl").open() as stream:
            for line in stream:
                record = json.loads(line)
                key = record["id"]
                if key in needed:
                    run["evidence"][key] = observation(record, verifier, folder, actions, previous.get("evidence", {}).get(key, {}))
        if run["evidence"].keys() != needed:
            raise ValueError(f"Missing cited observations for {trial.name}: {needed - run['evidence'].keys()}")
    return run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jobs_dir", type=Path)
    args = parser.parse_args()
    source = ROOT / "instruction-runs.json"
    previous = read(source) if source.exists() else {}
    runs = {}
    tasks = {t["slug"]: t for t in parse_tasks(SOURCE.read_text())}
    for name, slug in TASKS.items():
        if "id" not in tasks[slug]["rubrics"][0]:
            continue
        jobs = sorted(args.jobs_dir.glob(f"{name}_pi_*"))
        if not jobs:
            raise ValueError(f"No trial found for {slug}")
        config, = jobs[-1].glob("*/config.json")
        runs[slug] = import_trial(config.parent, tasks[slug], previous.get(slug, {}))
    source.write_text(json.dumps(runs, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
