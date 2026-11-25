"""Package the public results of each displayed Harbor trial from its private ZIP snapshot."""
import argparse
import hashlib
import json
import re
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from build import ROOT


def fields(record, names):
    return {key: record[key] for key in names.split() if key in record}


def public_metadata(obj):
    """Remove host-specific locations and secret settings from Harbor metadata."""
    if isinstance(obj, dict):
        return {k: "[redacted]" if re.search(r"password|secret|credential|api_key|access_token|auth_token|private_key", k, re.I)
                else public_metadata(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [public_metadata(v) for v in obj]
    if isinstance(obj, str):
        return re.sub(r"(?:file://)?/(?:data/user_data|home/yingjiey)/[^\s]+", "[local path]", obj)
    return obj


def public_actions(step):
    calls = []
    for call in step.get("tool_calls", []):
        action = fields(call, "tool_call_id function_name")
        args = call.get("arguments", {})
        # Retain numeric arguments, including pointer coordinates, without text entered in the guest.
        action["arguments"] = {k: v for k, v in args.items() if type(v) in (bool, int, float) or
                               (k == "coordinate" and isinstance(v, list) and all(type(n) in (int, float) for n in v))}
        calls.append(action)
    return calls


def public_step(step, reviewed):
    row = fields(step, "step_id timestamp source metrics")
    execution = step.get("extra", {}).get("execution", {})
    if execution:
        row["execution"] = fields(execution, "status started_at finished_at")
        row["execution"]["operations"] = [
            fields(op, "operation started_at finished_at status exit_code") for op in execution.get("operations", [])
        ]
    if step.get("tool_calls"):
        row["tool_calls"] = public_actions(step)
    if step["step_id"] in reviewed:
        row["reviewed_observations"] = reviewed[step["step_id"]]
    return row


def write_public_zip(snapshot, target, run, slug):
    job, trial = run["job"], run["trial"]
    assets = ROOT / "assets/agent-runs" / slug / trial

    def js(data):
        return json.dumps(data, ensure_ascii=False, indent=2) + "\n"

    with ZipFile(snapshot) as src, ZipFile(target, "w", ZIP_DEFLATED, compresslevel=6) as dest:
        names = {i.filename for i in src.infolist() if not i.is_dir()}
        if not names or any(not p.startswith(job + "/") or ".." in Path(p).parts for p in names):
            raise ValueError(f"Unexpected snapshot layout for {job}")
        def save(rel, data):
            dest.writestr(job + "/" + rel, data)
        def read(rel):
            return json.loads(src.read(job + "/" + rel))
        def has(rel):
            return job + "/" + rel in names

        for prefix in ("", trial + "/"):
            for name in ("config.json", "lock.json", "result.json"):
                rel = prefix + name
                if has(rel):
                    metadata = read(rel)
                    # Debug payloads supplied by a solver or raised by a runner can contain credentials.
                    if name == "result.json" and prefix:
                        for key in ("rollout_details", "metadata"):
                            if (metadata.get("agent_result") or {}).get(key):
                                metadata["agent_result"][key] = "[withheld]"
                        if metadata.get("exception_info"):
                            metadata["exception_info"] = fields(metadata["exception_info"], "exception_type")
                    save(rel, js(public_metadata(metadata)))
        for rel in ("job.log", trial + "/trial.log", trial + "/agent/pi_stderr.txt"):
            if has(rel):
                lines = src.read(job + "/" + rel).decode().splitlines(keepends=True)
                safe_lines = {"Collecting main service artifacts",
                              "Agent 'pi-agent' does not declare an options_model; leftover kwargs are ignored"}
                save(rel, "".join(line if line.strip() in safe_lines else "[private log line]\n" for line in lines))

        ag = trial + "/agent/"
        vr = trial + "/verifier/"
        runtime = read(ag + "pi_runtime.json")
        save(ag + "pi_runtime.json", js(fields(runtime, "pi_version node_version image provider model "
                                               "requested_thinking_level tools image_sha256 extension_sha256")))
        reviewed = {}
        observations = []
        for obs_id, original in run["evidence"].items():
            item = dict(original, id=obs_id)
            if f := item.get("file"):
                if f != Path(f).name:
                    raise ValueError(f"Invalid evidence filename: {f}")
                save(vr + "screenshots/" + f, (assets / f).read_bytes())
                item["file"] = "screenshots/" + f
            match = re.fullmatch(r"obs_(?:step_|frame_pi_)(\d+)(?:_p?\d+)", obs_id)
            if match:
                reviewed.setdefault(int(match[1]), []).append(obs_id)
            observations.append(item)
        if has(vr + "live-observations.jsonl"):
            save(vr + "live-observations.jsonl", "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in observations))
            # Keep the complete inspection index, including checks that the verdict did not cite.
            index = [fields(json.loads(line), "id source view page pages ok pi_step")
                     for line in src.read(job + "/" + vr + "live-observations.jsonl").splitlines()]
            save(vr + "observation-index.json", js(index))
        if has(vr + "live-judge.json"):
            judge = read(vr + "live-judge.json")
            for item in judge["items"]:
                row = run["rows"][item["id"]]
                if item["rating"] != row["score"] or item["reason"] != row["reason"]:
                    raise ValueError(f"Website and snapshot verdicts differ for {item['id']}")
            save(vr + "live-judge.json", js(public_metadata(judge)))

        tr = read(ag + "trajectory.json")
        tr["steps"] = [public_step(s, reviewed) for s in tr["steps"]]
        save(ag + "trajectory.json", js(fields(tr, "schema_version session_id trajectory_id agent steps final_metrics")))
        for path in sorted(names):
            if not path.startswith(job + "/" + vr + "gym/"):
                continue
            rel = path[len(job) + 1:]
            if path.endswith("/traj.jsonl"):
                events = [fields(json.loads(line), "event ts idx sequence phase status tool_call_id tool_name "
                                 "observation_id started_at finished_at platform_family resolution fps")
                          for line in src.read(path).splitlines()]
                save(rel, "".join(json.dumps(e, separators=(",", ":")) + "\n" for e in events))
            elif path.endswith("/summary.json"):
                save(rel, js(fields(json.loads(src.read(path)), "env task start_ts end_ts steps")))
        for out in run.get("output_files", []):
            data = (assets / "outputs" / out["name"]).read_bytes()
            if hashlib.sha256(data).hexdigest() != out["sha256"]:
                raise ValueError(f"Output hash mismatch for {out['name']}")
            save(trial + "/artifacts/" + out["guest_path"].lstrip("/"), data)
        save(trial + "/artifacts/manifest.json", js(run.get("output_files", [])))
        save("README.txt", (
            f"Public Harbor run results for {job}\n\n"
            "The job and trial metadata include the recorded usage, timing, and final result when available. "
            "agent/trajectory.json includes every recorded step, action type, numeric action arguments, and reported metrics. "
            "The Gym event index retains every recorded event. verifier/live-judge.json contains the final scores and reasons when a verdict exists. "
            "verifier/live-observations.jsonl contains the reviewed evidence for the verdicts, including tool calls and responses. "
            "The observation index includes all recorded verifier checks. Screenshots and collected deliverables are the public versions from the task page.\n\n"
            "For public distribution, the export omits session credentials, host-specific locations, unreviewed free-text messages, "
            "tool payloads and screenshots, private setup and debug logs, and unpublished guest files. "
            "Some published screenshots are cropped. The original run folder is retained privately.\n"
        ))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshots", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--release-url", required=True, help="GitHub Releases download base URL")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    manifest = ROOT / "instruction-runs.json"
    runs = json.loads(manifest.read_text())
    for slug, run in runs.items():
        name = run["job"] + ".zip"
        output = args.output / name
        snapshot = args.snapshots / name
        if snapshot.resolve() == output.resolve():
            raise ValueError("Use a separate directory for public ZIPs")
        write_public_zip(snapshot, output, run, slug)
        with ZipFile(output) as z:
            if z.testzip() is not None or any(i.flag_bits & 1 for i in z.infolist()):
                raise ValueError(f"Invalid public ZIP: {output}")
        archive = {"url": args.release_url.rstrip("/") + "/" + name, "bytes": output.stat().st_size,
                   "sha256": hashlib.sha256(output.read_bytes()).hexdigest()}
        if run.get("archive", {}).get("snapshot_at"):
            archive["snapshot_at"] = run["archive"]["snapshot_at"]
        run["archive"] = archive
    manifest.write_text(json.dumps(runs, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
