"""Execute one-token mutants of every Java exercise in the prepared java21 worker.

The renderer turns each exercise into practice text only after this script has
observed that a specific edit makes a specific assertion of that same exercise fail.
Run from the repository root after changing any exercise code:

    python courses/java/authoring/qualify_variants.py

It needs a local Docker engine and the prepared worker image (default
ds60sqlpy-worker-java21:2.1.1, override with JAVA_VARIANT_IMAGE). Programs compile
with the classroom's javac flags and run with assertions enabled, offline and with
no repository mount; they are passed on standard input. For identification only,
each assertion of the mutated exercise is rewritten as a numbered always-on check.
Unchanged exercises keep their records; the script writes only variants.json.
"""

import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import render  # noqa: E402
import specs  # noqa: E402,F401  (registers the lessons)
import variants  # noqa: E402

IMAGE = os.environ.get("JAVA_VARIANT_IMAGE", "ds60sqlpy-worker-java21:2.1.1")
LIMIT = 10

DRIVER = r"""
import concurrent.futures, json, os, re, subprocess, sys, tempfile
jobs = json.load(sys.stdin)
LIB = "/opt/course-libs/h2-2.5.252.jar"

def run(source):
    folder = tempfile.mkdtemp()
    with open(folder + "/Main.java", "w") as handle:
        handle.write(source)
    os.makedirs(folder + "/classes")
    built = subprocess.run(["javac", "-encoding", "UTF-8", "-Xlint:all", "--release", "21", "-cp", LIB,
                            "-d", "classes", "Main.java"], cwd=folder, capture_output=True, text=True,
                           timeout=240)
    if built.returncode:
        return {"outcome": "compile", "detail": built.stderr[-400:]}
    try:
        ran = subprocess.run(["java", "-ea", "-Xmx512m", "-cp", "classes:" + LIB, "Main"], cwd=folder,
                             capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        return {"outcome": "timeout"}
    if ran.returncode == 0:
        return {"outcome": "survived"}
    found = re.search(r"AssertionError: CHECK#(\d+)", ran.stderr)
    if found:
        return {"outcome": "killed", "check": int(found.group(1))}
    return {"outcome": "crash", "detail": ran.stderr[-400:]}

def job(item):
    tried = []
    for candidate in item["candidates"]:
        result = run(candidate["source"])
        result["index"] = candidate["index"]
        tried.append(result)
        if item.get("baseline") or (result["outcome"] == "killed" and result["check"] == item["target"]):
            break
    return item["key"], tried

with concurrent.futures.ThreadPoolExecutor(4) as pool:
    json.dump(dict(pool.map(job, jobs)), sys.stdout)
"""


def numbered(code):
    """Rewrite each assertion of one exercise as a numbered always-on check."""
    items = variants.tokens(code)
    for number, (first, last, condition, _) in reversed(list(enumerate(variants.checks(code)))):
        start, end = items[first][2], items[last][3]
        code = (
            code[:start]
            + f'if (!({condition})) throw new AssertionError("CHECK#{number}");'
            + code[end:]
        )
    return code


def blocks(spec, override=None):
    result = []
    for index, exercise in enumerate(spec["exercises"]):
        code = exercise["code"]
        if override and override[0] == index:
            code = override[1]
        result.append(f"// Exercise {index + 1}: {exercise['title']}\n" + code)
    return result


def main():
    records = variants.load_records()
    jobs, plans = [], {}
    for ident, spec in render.SPECS.items():
        jobs.append(
            {
                "key": ident + "/baseline",
                "baseline": True,
                "candidates": [{"index": -1, "source": render.program(spec, blocks(spec))}],
            }
        )
        for index, exercise in enumerate(spec["exercises"]):
            previous = records.get(ident, {}).get(str(index + 1))
            if previous and previous["sha"] == variants.digest(exercise["code"]):
                continue
            ordered = variants.ordered(exercise["code"], index)[:LIMIT]
            plans[(ident, index)] = ordered
            jobs.append(
                {
                    "key": f"{ident}/{index}",
                    "target": len(variants.checks(exercise["code"])) - 1,
                    "candidates": [
                        {
                            "index": i,
                            "source": render.program(
                                spec,
                                blocks(
                                    spec, (index, numbered(variants.apply(exercise["code"], c)))
                                ),
                            ),
                        }
                        for i, c in enumerate(ordered)
                    ],
                }
            )
    print(f"Running {len(jobs)} jobs in {IMAGE}", file=sys.stderr)
    result = subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "-i",
            "--network",
            "none",
            "--entrypoint",
            "python3",
            IMAGE,
            "-c",
            DRIVER,
        ],
        input=json.dumps(jobs),
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        raise SystemExit(result.stderr[-4000:])
    outcomes = json.loads(result.stdout)
    failed = [
        key
        for key, tried in outcomes.items()
        if key.endswith("/baseline") and tried[0]["outcome"] != "survived"
    ]
    if failed:
        for key in failed:
            print(key, outcomes[key], file=sys.stderr)
        raise SystemExit("Unmodified references must pass before mutants are judged.")
    tally = {}
    for key, tried in outcomes.items():
        if not key.endswith("/baseline"):
            for attempt in tried:
                tally[attempt["outcome"]] = tally.get(attempt["outcome"], 0) + 1
    print("Mutant outcomes:", dict(sorted(tally.items())), file=sys.stderr)
    for (ident, index), ordered in plans.items():
        tried = outcomes[f"{ident}/{index}"]
        code = render.SPECS[ident]["exercises"][index]["code"]
        entry = {"sha": variants.digest(code), "tried": len(tried), "outcome": "exhausted"}
        target = len(variants.checks(code)) - 1
        kills = [t for t in tried if t["outcome"] == "killed"]
        outside = [t for t in kills if not ordered[t["index"]]["inside"]]
        inside = [t for t in kills if ordered[t["index"]]["inside"]]
        best = (
            next((t for t in outside if t["check"] == target), None)
            or (outside[0] if outside else None)
            or next((t for t in inside if t["check"] == target), None)
            or (inside[0] if inside else None)
        )
        if best:
            entry.update(ordered[best["index"]], outcome="killed", check=best["check"])
        records.setdefault(ident, {})[str(index + 1)] = entry
    variants.RECORDS.write_text(
        json.dumps(records, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    killed = sum(
        1 for lesson in records.values() for e in lesson.values() if e["outcome"] == "killed"
    )
    total = sum(len(lesson) for lesson in records.values())
    print(f"Recorded {killed}/{total} exercises with an observed failing mutant.")


if __name__ == "__main__":
    main()
