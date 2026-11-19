"""Execute one-token mutants of every Go case in the prepared worker image.

The renderer turns each case into practice text only after this script has observed
that a specific edit makes a specific check of that same case fail. Run from the
repository root after changing any case code:

    python courses/go/authoring/qualify_variants.py

It needs a local Docker engine and the prepared worker image (default
ds60sqlpy-worker-go:1.4.0, override with GO_VARIANT_IMAGE). Programs are compiled
with the classroom's fixed import configuration and run offline with no repository
mount; they are passed on standard input. Unchanged
cases keep their existing records. The script writes only authoring/variants.json.
"""

import copy
import json
import os
import subprocess
import sys
from importlib import import_module
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import render  # noqa: E402
import variants  # noqa: E402

IMAGE = os.environ.get("GO_VARIANT_IMAGE", "ds60sqlpy-worker-go:1.4.0")
LIMIT = 14
NUMBERED = 'func checkAt(id int, ok bool, message string) { if !ok { panic(fmt.Sprintf("CHECK#%d %s", id, message)) } }'

DRIVER = r"""
import concurrent.futures, json, re, subprocess, sys, tempfile
jobs = json.load(sys.stdin)

def run(source):
    folder = tempfile.mkdtemp()
    with open(folder + "/main.go", "w") as handle:
        handle.write(source)
    config = "/opt/course-go/importcfg"
    for command in (["go", "tool", "compile", "-importcfg", config, "-p", "main", "-o", "main.a", "main.go"],
                    ["go", "tool", "link", "-importcfg", config, "-o", "lesson", "main.a"]):
        built = subprocess.run(command, cwd=folder, capture_output=True, text=True, timeout=180)
        if built.returncode:
            return {"outcome": "compile", "detail": built.stderr[-400:]}
    try:
        ran = subprocess.run(["./lesson"], cwd=folder, capture_output=True, text=True, timeout=15)
    except subprocess.TimeoutExpired:
        return {"outcome": "timeout"}
    if ran.returncode == 0:
        return {"outcome": "survived"}
    found = re.search(r"panic: CHECK#(\d+) ", ran.stderr)
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
    """Name each check of one case so a failure identifies exactly which one fired."""
    items = variants.tokens(code)
    spans = [first for first, _, _, _ in variants.checks(code)]
    for number, first in reversed(list(enumerate(spans))):
        _, _, start, end = items[first]
        opening = items[first + 1]
        code = code[:start] + f"checkAt({number}, " + code[opening[3] :]
    return code


def mutant(spec, case_index, code):
    changed = copy.deepcopy(spec)
    changed["cases"][case_index]["code"] = numbered(code)
    changed["helper"] = (spec["helper"] + "\n\n" + NUMBERED).strip()
    return render.program(changed)


def main():
    render.format_go = lambda source: source
    for section in ("foundations", "composition", "systems"):
        import_module(section)
    records = variants.load_records()
    jobs, plans = [], {}
    for number, spec in enumerate(render.SPECS, 1):
        ident = f"go-{number:03d}"
        jobs.append(
            dict(
                key=ident + "/baseline",
                baseline=True,
                candidates=[dict(index=-1, source=render.program(spec))],
            )
        )
        for case_index, case in enumerate(spec["cases"]):
            previous = records.get(ident, {}).get(str(case_index + 1))
            if previous and previous["sha"] == variants.digest(case["code"]):
                continue
            ordered = variants.ordered(case["code"], case_index)[:LIMIT]
            plans[(ident, case_index)] = ordered
            jobs.append(
                dict(
                    key=f"{ident}/{case_index}",
                    target=len(variants.checks(case["code"])) - 1,
                    candidates=[
                        dict(
                            index=i,
                            source=mutant(spec, case_index, variants.apply(case["code"], c)),
                        )
                        for i, c in enumerate(ordered)
                    ],
                )
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
    for (ident, case_index), ordered in plans.items():
        tried = outcomes[f"{ident}/{case_index}"]
        code = render.SPECS[int(ident[3:]) - 1]["cases"][case_index]["code"]
        entry = dict(sha=variants.digest(code), tried=len(tried), outcome="exhausted")
        target = len(variants.checks(code)) - 1
        kills = [t for t in tried if t["outcome"] == "killed"]
        outside = [t for t in kills if not ordered[t["index"]]["inside"]]
        # Prefer a real input or logic change over editing a check, then the case's
        # main (last) claim over a precondition or cleanup check.
        inside = [t for t in kills if ordered[t["index"]]["inside"]]
        best = (
            next((t for t in outside if t["check"] == target), None)
            or (outside[0] if outside else None)
            or next((t for t in inside if t["check"] == target), None)
            or (inside[0] if inside else None)
        )
        if best:
            entry.update(ordered[best["index"]], outcome="killed", check=best["check"])
        records.setdefault(ident, {})[str(case_index + 1)] = entry
    variants.RECORDS.write_text(
        json.dumps(records, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    killed = sum(
        1 for lesson in records.values() for e in lesson.values() if e["outcome"] == "killed"
    )
    total = sum(len(lesson) for lesson in records.values())
    print(f"Recorded {killed}/{total} cases with an observed failing mutant.")


if __name__ == "__main__":
    main()
