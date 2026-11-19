"""Import the selected Harbor trials from the agent runtime comparison CSV, before building the site."""
import argparse
import csv
import json
import re
import shutil
from datetime import datetime
from pathlib import Path

from build import ROOT, SOURCE, parse_tasks
from materials import sha256

TASKS = {
    "word": "finalize-document-tracked-changes", "outlook": "schedule-calendar-events",
    "quickbooks": "reconcile-business-bank-account", "drchrono": "complete-sign-clinical-note",
    "google-classroom": "update-class-gradebook", "spss": "survey-data-frequency-analyses",
    "premiere-pro": "edit-youtube-video", "asana": "plan-website-launch",
    "salesforce": "sales-leads-revenue-dashboards", "autocad": "floor-plan-architectural-details",
}
# Only these task deliverables are intended for public download.
OUTPUT_PATHS = {
    "floor-plan-architectural-details": ("/home/ga/Documents/CAD/example 2.pdf",
                                        "/home/ga/Documents/CAD/floor plan exercise.dwg"),
    "finalize-document-tracked-changes": ("/home/ga/Documents/SOW-Revision 1.docx",),
    "schedule-calendar-events": ("/home/ga/.local/share/outlook-calendar/Calendar.ics",),
    "edit-youtube-video": ("/home/ga/Documents/Justin Edit/Justin Edit.kdenlive",),
    "reconcile-business-bank-account": ("/home/ga/Documents/HECTOR 2024 LLC.kmy",),
}
CREDENTIAL = re.compile(
    r"password|passwd|credential|secret|api[_-]?key|token|authorization|bearer\s|"
    r"basic\s+[a-z0-9+/=]{12,}|cookie|csrf|://[^@/\s]+:[^/\s]+@|"
    r"eyJ[\w-]{5,}\.[\w-]{5,}\.[\w-]{10,}|(?:AKIA|ASIA)[A-Z0-9]{16}|/data/user_data/|"
    r"private.key|-----BEGIN |\b(?:sk-|gh[pousr]_)[\w-]{16,}|AIza[\w-]{32,}", re.I
)
PAYLOADS = ("arguments", "operations", "action", "executed_actions", "tool_result", "error")
REDACTED = "[redacted]"


def export_trajectory(source, dest):
    # One output event for every recorded event, including interrupted trials.
    events = [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines()]
    sessions = [e for e in events if e["event"] == "session"]
    secrets = {v for e in sessions for k, v in e.items() if CREDENTIAL.search(k) and isinstance(v, str) and v}
    sensitive_calls = set()
    for e in events:
        if e.get("tool_call_id"):
            payload = json.dumps([e[k] for k in PAYLOADS if k in e], ensure_ascii=False)
            if CREDENTIAL.search(payload) or any(s in payload for s in secrets):
                sensitive_calls.add(e["tool_call_id"])
    with dest.open("w", encoding="utf-8") as out:
        for e in events:
            if e["event"] == "session":
                e = {k: v for k, v in e.items() if k in (
                    "event", "env_id", "task_id", "platform_family", "resolution", "fps")}
            elif e.get("tool_call_id") in sensitive_calls:
                for k in PAYLOADS:
                    if k in e:
                        e[k] = REDACTED
            line = json.dumps(e, ensure_ascii=False, separators=(",", ":"))
            for secret in secrets:
                line = line.replace(secret, REDACTED)
            out.write(line + "\n")
    return len(events)


def import_outputs(trial, slug, output):
    folder = output / "outputs"
    files = []
    manifest = trial / "artifacts/manifest.json"
    entries = json.loads(manifest.read_text()) if manifest.is_file() else []
    for entry in entries:
        guest = entry["source"]
        if guest not in OUTPUT_PATHS.get(slug, ()) or entry["status"] != "ok" or entry["type"] != "file":
            continue
        expected = Path("artifacts") / guest.lstrip("/")
        source = trial / expected
        if Path(entry["destination"]) != expected or source.resolve() != trial.resolve() / expected or not source.is_file():
            raise ValueError(f"Invalid collected output for {trial.name}: {guest}")
        folder.mkdir(exist_ok=True)
        shutil.copyfile(source, folder / source.name)
        files.append({"name": source.name, "guest_path": guest, "bytes": source.stat().st_size, "sha256": sha256(source)})
    names = {item["name"] for item in files}
    for stale in folder.glob("*"):
        if stale.name not in names:
            stale.unlink()
    return files


def import_runs(selection):
    manifest = {}
    with selection.open(encoding="utf-8", newline="") as stream:
        for row in csv.DictReader(stream):
            slug, condition = TASKS[row["task"]], row["condition"]
            pair = manifest.setdefault(slug, {})
            if condition not in ("guided", "unguided") or condition in pair:
                raise ValueError(f"Invalid run selection for {slug}: {condition}")
            trial = Path(row["trial_result_path"]).parent
            result = json.loads((trial / "result.json").read_text())
            config = json.loads((trial / "config.json").read_text())
            if bool(config.get("extra_instruction_paths")) != (condition == "guided"):
                raise ValueError(f"Guidance condition mismatch: {trial}")
            episode, = (trial / "verifier/gym").glob("episode_*")
            frames = sorted(p for p in episode.glob("frame_*.png") if re.fullmatch(r"frame_\d+\.png", p.name))
            if not frames:
                raise ValueError(f"Missing numbered frames: {episode}")
            output = ROOT / "assets/agent-runs" / slug / condition
            output.mkdir(parents=True, exist_ok=True)
            for p in frames:
                shutil.copyfile(p, output / p.name)
            for stale in output.glob("frame_*.png"):
                if not (episode / stale.name).is_file():
                    stale.unlink()
            count = export_trajectory(episode / "traj.jsonl", output / "traj.jsonl")
            timing, metrics = result["agent_execution"], result["agent_result"]
            start, end = (datetime.fromisoformat(timing[k].replace("Z", "+00:00"))
                          for k in ("started_at", "finished_at"))
            runtime = round((end-start).total_seconds())
            total = metrics["n_input_tokens"] + metrics["n_output_tokens"]
            model = result["agent_info"]["model_info"]["name"]
            if (float(row["agent_runtime_seconds"]) != (end-start).total_seconds()
                    or int(row["total_tokens"]) != total or row["model"] != model):
                raise ValueError(f"Metrics do not match the selection: {trial}")
            pair[condition] = dict(job=trial.parent.name, trial=trial.name, episode=episode.name,
                                   agent="Pi", model=model, runtime_seconds=runtime,
                                   input_tokens=metrics["n_input_tokens"], output_tokens=metrics["n_output_tokens"],
                                   cached_input_tokens=metrics["n_cache_tokens"], total_tokens=total,
                                   frame_count=len(frames), event_count=count, output_files=import_outputs(trial, slug, output),
                                   agent_error=(result.get("exception_info") or {}).get("exception_type") == "PiRpcError")
    expected = {task["slug"] for task in parse_tasks(SOURCE.read_text(encoding="utf-8"))}
    if set(manifest) != expected or any(set(pair) != {"guided", "unguided"} for pair in manifest.values()):
        raise ValueError("Expected a guided and unguided trial for every task")
    (ROOT / "agent-runs.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("selection", type=Path)
    import_runs(cli.parse_args().selection)
