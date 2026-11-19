"""Execute one-token mutants of every runnable JS/TS exercise in the prepared workers.

The renderer turns exercises 1-2 into practice derived from the worked examples, and
writes every Verify line, only after this script has observed that a specific edit
makes an assertion of that same exercise fail. Run from the repository root after
changing any exercise code:

    python courses/javascript-typescript/authoring/qualify_variants.py

It needs a local Docker engine and the prepared worker images (defaults
ds60sqlpy-worker-javascript-node:1.4.1 and ds60sqlpy-worker-typescript-node:1.4.1,
override with JS_VARIANT_IMAGE and TS_VARIANT_IMAGE). Programs run offline with the
classroom's Node flags; TypeScript is compiled first with the classroom's tsc flags.
For identification only, a marker call records which assertion of the mutated
exercise ran last. Browser reading lessons have no Node runtime and are skipped.
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
import variants  # noqa: E402

for module in ("specs", "intermediate", "typed", "typed_advanced", "browser", "advanced"):
    __import__(module)
__import__("applications")

IMAGES = {
    "js": os.environ.get("JS_VARIANT_IMAGE", "ds60sqlpy-worker-javascript-node:1.4.1"),
    "ts": os.environ.get("TS_VARIANT_IMAGE", "ds60sqlpy-worker-typescript-node:1.4.1"),
}
LIMIT = 10
MARKER = {
    "js": (
        "function __at(k) { globalThis.__CHECK = k; }\n"
        'process.on("exit", (code) => { if (code !== 0 && globalThis.__CHECK !== undefined) '
        "process.stderr.write(`\\nCHECK#${globalThis.__CHECK}\\n`); });\n"
    ),
    "ts": (
        "function __at(k: number): void { (globalThis as any).__CHECK = k; }\n"
        'process.on("exit", (code: number) => { if (code !== 0 && (globalThis as any).__CHECK !== undefined) '
        "process.stderr.write(`\\nCHECK#${(globalThis as any).__CHECK}\\n`); });\n"
    ),
}

DRIVER = r"""
import concurrent.futures, json, os, re, subprocess, sys, tempfile
jobs = json.load(sys.stdin)
NODE = ["node", "--unhandled-rejections=strict", "--max-old-space-size=256"]
TSC = ["node", "/opt/typescript/node_modules/typescript/bin/tsc", "--target", "ES2022", "--module",
       "NodeNext", "--moduleResolution", "NodeNext", "--strict", "--noEmitOnError", "--skipLibCheck",
       "--types", "node", "--typeRoots", "/opt/typescript/node_modules/@types", "--outDir", "compiled",
       "main.mts"]

def run(source, kind):
    folder = tempfile.mkdtemp()
    if kind == "ts":
        with open(folder + "/main.mts", "w") as handle:
            handle.write(source)
        os.makedirs(folder + "/compiled")
        built = subprocess.run(TSC, cwd=folder, capture_output=True, text=True, timeout=120)
        if built.returncode:
            return {"outcome": "compile", "detail": (built.stdout + built.stderr)[-400:]}
        target = "compiled/main.mjs"
    else:
        with open(folder + "/main.mjs", "w") as handle:
            handle.write(source)
        target = "main.mjs"
    try:
        ran = subprocess.run(NODE + [target], cwd=folder, capture_output=True, text=True, timeout=30)
    except subprocess.TimeoutExpired:
        return {"outcome": "timeout"}
    if ran.returncode == 0:
        return {"outcome": "survived"}
    found = re.findall(r"CHECK#(-?\d+)", ran.stderr)
    if found and int(found[-1]) >= 0 and ("ERR_ASSERTION" in ran.stderr or "AssertionError" in ran.stderr):
        return {"outcome": "killed", "check": int(found[-1])}
    return {"outcome": "crash", "detail": ran.stderr[-400:]}

def job(item):
    tried = []
    for candidate in item["candidates"]:
        result = run(candidate["source"], item["kind"])
        result["index"] = candidate["index"]
        tried.append(result)
        if item.get("baseline") or (result["outcome"] == "killed" and result["check"] == item["target"]):
            break
    return item["key"], tried

with concurrent.futures.ThreadPoolExecutor(4) as pool:
    json.dump(dict(pool.map(job, jobs)), sys.stdout)
"""


def numbered(code):
    """Mark each assertion of one exercise so the last one reached can be identified."""
    items = variants.tokens(code)
    significant = [i for i, item in enumerate(items) if item[0] not in {"space", "comment"}]
    for number, (first, last, _, _) in reversed(list(enumerate(variants.checks(code)))):
        start, end = items[first][2], items[last][3]
        position = significant.index(first)
        head = first
        if position and items[significant[position - 1]][1] == "await":
            position -= 1
            head = significant[position]
        previous = items[significant[position - 1]][1] if position else ";"
        if previous in {";", "{", "}"}:
            at = items[head][2]
            code = code[:at] + f"__at({number}); " + code[at:]
        else:
            code = code[:start] + f"(__at({number}), " + code[start:end] + ")" + code[end:]
    return code + "\n__at(-1);"


def kind_of(ident):
    runtime = PLAN[ident]["runtime"]
    return {"javascript-node": "js", "typescript-node": "ts"}.get(runtime)


PLAN = {
    row["id"]: row
    for row in json.loads((HERE.parent / "track.json").read_text(encoding="utf-8"))["lessons"]
}


def source(spec, kind, codes):
    instrumented = dict(spec, imports=spec["imports"] + "\n" + MARKER[kind])
    return render.program(instrumented, codes, True, kind == "ts")


def main():
    records = variants.load_records()
    jobs, plans = [], {}
    for ident, spec in render.SPECS.items():
        kind = kind_of(ident)
        if kind is None:
            continue
        codes = [exercise["code"] for exercise in spec["exercises"]]
        jobs.append(
            {
                "key": ident + "/baseline",
                "kind": kind,
                "baseline": True,
                "candidates": [{"index": -1, "source": source(spec, kind, codes)}],
            }
        )
        for index, exercise in enumerate(spec["exercises"]):
            previous = records.get(ident, {}).get(str(index + 1))
            if previous and previous["sha"] == variants.digest(exercise["code"]):
                continue
            ordered = variants.ordered(exercise["code"], index)[:LIMIT]
            plans[(ident, index)] = ordered
            candidates = []
            for i, candidate in enumerate(ordered):
                mutated = list(codes)
                mutated[index] = numbered(variants.apply(exercise["code"], candidate))
                candidates.append({"index": i, "source": source(spec, kind, mutated)})
            jobs.append(
                {
                    "key": f"{ident}/{index}",
                    "kind": kind,
                    "target": len(variants.checks(exercise["code"])) - 1,
                    "candidates": candidates,
                }
            )
    outcomes = {}
    for kind, image in IMAGES.items():
        batch = [job for job in jobs if job["kind"] == kind]
        print(f"Running {len(batch)} jobs in {image}", file=sys.stderr)
        result = subprocess.run(
            ["docker", "run", "--rm", "-i", "--network", "none", "--entrypoint", "python3", image]
            + ["-c", DRIVER],
            input=json.dumps(batch),
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode:
            raise SystemExit(result.stderr[-4000:])
        outcomes.update(json.loads(result.stdout))
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
        1
        for lesson in records.values()
        for entry in lesson.values()
        if entry["outcome"] == "killed"
    )
    total = sum(len(lesson) for lesson in records.values())
    print(f"Recorded {killed}/{total} exercises with an observed failing mutant.")


if __name__ == "__main__":
    main()
