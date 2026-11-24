"""Render human-review excerpts from the original tutorial recordings."""
import argparse
import json
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
CONTEXT_SECONDS = 2


def clip_file(slug, clip):
    if "segment_id" in clip:
        name = f"segment-{clip['segment_id']}.webm"
    else:
        segments = clip["source_segment_ids"]
        if not segments or segments != sorted(set(segments)) or any(type(i) is not int or i < 0 for i in segments):
            raise ValueError(f"Invalid source segment IDs for {slug}: {segments}")
        start_ms, end_ms = (round(clip[key] * 1000) for key in ("start_sec", "end_sec"))
        name = f"range-{start_ms}-{end_ms}.webm"
    expected = Path("assets/rubric-clips") / slug / name
    if clip["file"] != expected.as_posix():
        raise ValueError(f"Unexpected clip path: {clip['file']}")
    return expected


def playback_interval(clip, duration):
    start, end = clip["start_sec"], clip["end_sec"]
    if not 0 <= start < end <= duration:
        raise ValueError(f"Evidence outside the tutorial: {start}–{end} of {duration}")
    return max(0, start - CONTEXT_SECONDS), min(duration, end + CONTEXT_SECONDS)


def render(job):
    source, target, start, end = job
    target.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=target.parent) as temp:
        output = Path(temp) / target.name
        subprocess.run([
            "ffmpeg", "-nostdin", "-loglevel", "error", "-threads", "1",
            "-ss", str(start), "-i", str(source), "-t", str(round(end - start, 6)),
            "-map", "0:v:0", "-map", "0:a:0?", "-map_metadata", "-1",
            "-vf", "scale='min(1280,iw)':-2", "-c:v", "libvpx-vp9",
            "-deadline", "realtime", "-cpu-used", "7", "-threads", "2", "-crf", "31",
            "-b:v", "0", "-pix_fmt", "yuv420p", "-c:a", "libopus", "-b:a", "56k", str(output),
        ], check=True)
        probe = json.loads(subprocess.check_output([
            "ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_name",
            "-of", "json", str(output),
        ]))
        # Allow frame and audio-packet rounding at the two cut points.
        if (abs(float(probe["format"]["duration"]) - (end - start)) > 0.13
                or not any(s["codec_name"] == "vp9" for s in probe["streams"])):
            raise ValueError(f"Invalid rendered clip: {target}")
        os.replace(output, target)


def render_all(tutorial_dir):
    tutorials = json.loads((ROOT / "tutorial-videos.json").read_text())
    rubrics = json.loads((ROOT / "rubric-evidence.json").read_text())
    jobs = {}
    for slug, items in rubrics.items():
        tutorial = tutorials[slug]
        source = tutorial_dir / (tutorial["title"] + ".mp4")
        if not source.is_file():
            raise FileNotFoundError(source)
        for item in items:
            for clip in item["clips"]:
                target = ROOT / clip_file(slug, clip)
                start, end = playback_interval(clip, tutorial["duration_seconds"])
                job = (source, target, start, end)
                if jobs.setdefault(target, job) != job:
                    raise ValueError(f"Conflicting times for {target}")
    with ThreadPoolExecutor(max_workers=2) as pool:
        for count, _ in enumerate(pool.map(render, jobs.values()), 1):
            if count % 25 == 0 or count == len(jobs):
                print(f"Rendered and checked {count}/{len(jobs)} excerpts", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("tutorial_dir", type=Path, help="Directory of original MP4s named by tutorial title")
    render_all(parser.parse_args().tutorial_dir)
