"""Prepare the cited Harbor records for the public evidence viewer."""
import hashlib
import json
import re
import shutil

from import_agent_runs import CREDENTIAL, REDACTED

# Reviewed pixel bounds on the exact frames, excluding unrelated chart or roster details.
SCREENSHOT_CROPS = {
    "dea4cc1f53d0c2844428fd6b06c4aeedef37cfddf16f793dfcfa9cf19b99b0d8": (309, 489, 1148, 785),
    "ede474c1883b97bdf6300cc0c77b25b6912069827162ee46ec3c4991d7bbd4e6": (284, 545, 1020, 642),
    "cadf6a1eddbd1f9a17afd2f7372f80a977ff1241b777fdade406cbea91eca00f": (284, 328, 1020, 625),
    "f33308c82bf9d75ca67d3c49b2975317a6f9e036697968444f3fd2112e5e98f4": (285, 238, 1020, 624),
    "ac2008454322cc20e0e32260b310084b3a97420d440858d5960150767798e979": (87, 157, 1375, 780),
    "6e12d577345a17feb3b1c47cf39cf43a7677ea47348cc92503da701d56e91545": (548, 105, 787, 159),
    "7566b0709ce4407a51df75f5c5e52bb0d9ed79b98de2ded123f1af63beb78441": (384, 162, 944, 704),
    "03adea99c830c6507eef25448d6e14e58fe497f300e9c75ae2269471d85f0677": (401, 310, 936, 681),
    "c92a337c4e05315d23279cd2be795448ecc405a3b8aa4d7f16256a41665da677": (412, 235, 600, 634),
    "19c85c731c4508c233e78b71a1b5c876fd366a616df1ffa05622399e136a2a90": (421, 306, 686, 558),
    "220b8f0eb2e6902690e595ee4709dbaf442e6830beb1379b341b0ff39c2237ee": (421, 53, 690, 150),
    "f378e8d0312fa4cbb40af032acff5e568c4c153529b20f2a1c9334e59237d1e9": (386, 166, 944, 435),
    "da2b05aeca17dabb22143479ab3f36d518bba12beb1a4679f8d6ead3f7d70654": (510, 0, 1748, 216),
    "ee1dd52ae5f30d96e4c7c3014657c45ed999b25214c8e0d544b3e5ea538e6c43": (473, 106, 1238, 247),
}


def screenshot(record, verifier, folder):
    path = record["data"]
    if not re.fullmatch(r"(?:final-screen|recorded-screenshots/pi_\d+_\d+)\.jpg", path):
        raise ValueError(f"Invalid screenshot path for {record['id']}")
    source = verifier / path
    if folder.parent.name in {"complete-sign-clinical-note", "update-class-gradebook"}:
        crop = SCREENSHOT_CROPS.get(hashlib.sha256(source.read_bytes()).hexdigest())
        if crop is None:
            return {"availability": "This frame needs a public crop."}
        from PIL import Image
        name = source.stem + "-crop.png"
        with Image.open(source) as frame:
            frame.crop(crop).save(folder / name)
        return {"file": name, "cropped": True}
    shutil.copyfile(source, folder / source.name)
    return {"file": source.name}


EMAIL = re.compile(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}")
PRIVATE_VALUE = re.compile(
    r"(://[^/\s:@]+:)[^\s@/]+(@)|(/devtools/page/)[a-f\d]{20,}", re.I
)


def public_text(text, slug, tool=False):
    # Preserve the operation around connection credentials; never export their values.
    text = PRIVATE_VALUE.sub(lambda m: (m[1] + REDACTED + m[2]) if m[1] else m[3] + REDACTED, text)
    if tool:
        lines = text.splitlines(keepends=True)
        for i, line in enumerate(lines):
            # A URI password above was already removed; still check the rest of the line.
            if CREDENTIAL.search(re.sub(r"://[^/\s:]+:\[redacted\]@", "://", line)):
                lines[i] = REDACTED + ("\n" if line.endswith("\n") else "")
        text = "".join(lines)
    if slug == "update-class-gradebook":
        roster = re.findall(r"\b([a-z-]+)\.([a-z-]+)\d*@organize\.school\b", text, re.I)
        roster += re.findall(r"^([a-z-]+)\.([a-z-]+)\d*\t", text, re.I | re.M)
        text = EMAIL.sub(REDACTED, text)
        for first, last in set(roster):
            if (first.lower(), last.lower()) != ("casey", "boehm"):
                text = re.sub(rf"\b(?:{re.escape(first)}|{re.escape(last)})\b", REDACTED, text, flags=re.I)
    if slug == "reconcile-business-bank-account":
        text = re.sub(r'(?i)(\baccount\s+|\bacct#\s*|\bnumber=\\?")(\d{6,})(\d{4})\b', r"\1[redacted]\3", text)
    return text


def public_fields(value, slug):
    if isinstance(value, dict):
        return {k: REDACTED if CREDENTIAL.search(k) else public_fields(v, slug) for k, v in value.items()}
    if isinstance(value, list):
        return [public_fields(v, slug) for v in value]
    return public_text(value, slug, tool=True) if isinstance(value, str) else value


def observation(record, verifier, folder):
    key, source = record["id"], record["source"]
    slug = folder.parent.name
    if source == "recorded_screenshot" or record.get("view") == "screen":
        kind = "screenshots"
        label = f'Screenshot · step {record["pi_step"]}' if "pi_step" in record else "Final screenshot"
    elif source == "trajectory":
        kind = "tools"
        step = re.fullmatch(r"obs_step_(\d+)_p\d+", key)
        if not step:
            raise ValueError(f"Unexpected trajectory citation: {key}")
        label = "Step " + step[1]
    elif source == "live_environment":
        kind = "environment"
        label = record["view"].replace("_", " ").capitalize()
    else:
        raise ValueError(f"Unknown evidence source: {source}")
    if record.get("pages", 1) > 1:
        label += f' · page {record["page"]} of {record["pages"]}'
    item = {"kind": kind, "source": source, "label": label,
            "record_sha256": hashlib.sha256(json.dumps(record, sort_keys=True).encode()).hexdigest()}
    if not record["ok"]:
        item["availability"] = "The inspection was unsuccessful."
    elif kind == "screenshots":
        item.update(screenshot(record, verifier, folder))
    elif kind == "tools" and record.get("pages", 1) == 1:
        step = json.loads(record["data"])
        item["record"] = {k: public_fields(step[k], slug) for k in
                          ("step", "timestamp", "status", "tool_calls", "results") if k in step}
        if step["tool_calls"]:
            item["label"] += " · " + ", ".join(c["function_name"] for c in step["tool_calls"])
    else:
        # Multi-page observations can cut through JSON strings. Keep the actual cited page.
        raw = public_text(record["data"], slug, tool=kind == "tools")
        if record.get("pages", 1) == 1:
            try:
                raw = json.loads(raw)
            except ValueError:
                pass  # Plain-text outputs include tables, CSV and TSV.
        item["record"] = raw
    return item
