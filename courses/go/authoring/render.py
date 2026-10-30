"""Render complete Go teaching bundles from the original specifications."""

import json
import re
import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.format_inline_code import canonical_markdown  # noqa: E402

BASE = Path(__file__).resolve().parents[1]
SPECS = []


def case(title, task, expected, code, explanation):
    return dict(
        title=title,
        task=task,
        expected=expected,
        code=textwrap.dedent(code).strip(),
        explanation=explanation,
    )


def add(
    title,
    model,
    anatomy,
    terms,
    cases,
    imports="",
    helper="",
    source="https://go.dev/ref/spec",
    boundary="",
):
    assert len(cases) == 6
    SPECS.append(
        dict(
            title=title,
            model=model,
            anatomy=anatomy,
            terms=terms,
            cases=cases,
            imports=imports,
            helper=textwrap.dedent(helper).strip(),
            source=source,
            boundary=boundary,
        )
    )


def format_go(source):
    result = subprocess.run(["gofmt"], input=source, text=True, capture_output=True, check=False)
    if result.returncode:
        raise ValueError("Invalid generated Go source: " + result.stderr)
    return result.stdout


def format_snippet(source):
    wrapped = format_go("package main\n\nfunc main() {\n" + source + "\n}\n")
    return textwrap.dedent(wrapped.split("func main() {\n", 1)[1].rsplit("\n}", 1)[0]).strip()


def program(s, count=6):
    used = s["helper"] + "\n" + "\n".join(c["code"] for c in s["cases"][:count])
    imports = sorted(
        set(
            ["fmt"]
            + [
                name
                for name in s["imports"].split()
                if re.search(r"\b" + re.escape(name.rsplit("/", 1)[-1]) + r"\s*\.", used)
            ]
        )
    )
    body = "\n\n".join(
        "// " + c["title"] + "\n{\n" + textwrap.indent(c["code"], "    ") + "\n}"
        for c in s["cases"][:count]
    )
    return format_go(
        "package main\n\nimport (\n"
        + "".join('    "' + v + '"\n' for v in imports)
        + ")\n\nfunc check(ok bool, message string) { if !ok { panic(message) } }\n\n"
        + s["helper"]
        + "\n\nfunc main() {\n"
        + textwrap.indent(body, "    ")
        + '\n    fmt.Println("'
        + ("All lesson checks passed." if count == 6 else "Worked example checks passed.")
        + '")\n}\n'
    )


def render():
    plan = dict(
        schema_version=1,
        id="go",
        title="Go: practical programs, concurrency and Kubernetes controllers",
        summary="A complete Go learning path from your first compiled program to tested services and Kubernetes controller design. Small offline programs make language rules observable; prepared project chapters explain real integration boundaries.",
        lessons=[],
    )
    manifest = dict(schema_version=1, track_id="go", lessons=[])
    for n, s in enumerate(SPECS, 1):
        ident = f"go-{n:03d}"
        level = "beginner" if n <= 16 else "intermediate" if n <= 32 else "advanced"
        paths = {
            k: f"courses/go/{folder}/{ident}{suffix}"
            for k, folder, suffix in [
                ("guide", "guides", ".md"),
                ("starter", "lessons", ".go"),
                ("reference", "solutions", "_solution.go"),
                ("answers", "solutions", "_solutions.md"),
            ]
        }
        prereqs = [f"go-{n - 1:03d}"] if n > 1 else []
        terms = "\n".join(f"- **{a}:** {b}" for a, b in s["terms"])
        examples = "\n\n".join(
            f"### Worked example {i + 1}: {c['title']}\n\n{c['task']}\n\n```go\n{program(s, i + 1)}\n```\n\n**Observe:** {c['expected']}\n\n{c['explanation']}"
            for i, c in enumerate(s["cases"][:2])
        )
        exercises = "\n\n".join(
            f"### Exercise {i}: {c['title']}\n\n{c['task']}\n\n**Expected:** {c['expected']}\n\n**Verify:** Retain the input and assert the stated result. Change one relevant boundary and explain why the same check should pass or fail."
            for i, c in enumerate(s["cases"], 1)
        )
        hints = "\n\n".join(
            f"### Hint for investigation {i}: {c['title']}\n\n1. Restate the expected observation: {c['expected']}\n2. Identify the input and the state boundary relevant to {c['title'].lower()}. Trace that boundary before changing code.\n3. Reduce the experiment to one assertion and compare it with the corresponding worked-example mechanism. Keep the smallest distinguishing input."
            for i, c in enumerate(s["cases"], 1)
        )
        guide = f"""# {ident}: {s["title"]}

## Level and prerequisites

{level.capitalize()}. Allow about {90 if n <= 16 else 120} minutes, then revisit the transfer case later. Prerequisites: {", ".join(prereqs) or "No previous Go knowledge. Read source as plain text and distinguish editing from executing."}

## Learning objectives

By the end, explain {", ".join(a.lower() for a, b in s["terms"])}; implement the six investigations below; and defend the expected result of a changed input before running it. A passing reference is evidence about that program, not a certification of your independent understanding.

## Why this mechanism matters

{s["model"]}

## Vocabulary and concepts

{terms}

## Syntax anatomy and reasoning

{s["anatomy"]}

## Classroom execution contract

Choose Go in the unified Docker classroom. Save your own pad before experimenting. The prepared worker stages it as `main.go`, compiles it, and executes the resulting program with bounded time and output. The pad is one source file. It does not supply interactive input, arbitrary command-line arguments, package installation, Kubernetes credentials or a host Docker socket. Every ordinary reference here uses the standard library, synthetic local data and explicit checks. A failed `check` panics and produces a nonzero process result; do not remove it to make the run appear successful.

The explanatory solution snippets belong inside `func main()` unless they declare a helper. `check` is a tiny teaching helper that panics when a condition is false. The separate reference supplies required imports and helpers and implements all six cases. Use that complete source only after an attempt or an explicit reveal. For an independently prepared Go project, the equivalent local build is `go build -o lesson main.go`, followed by `./lesson`; use Linux or WSL 2 for that optional workflow. Compiling proves syntax and type consistency, while the executed checks establish the stated example contracts.

{s["boundary"]}

Each worked example below is a complete Go file. Copy one whole block into your saved pad and run it. Example 2 includes the first case as well as the second, so its setup is complete. Its supporting declarations may be reused in later investigations. The separate reference implements all six cases.

## Worked example / walkthrough

{examples}

## Predict before running

For each example, write the input values, the state that can change, and the expected observation. Explain which result would disprove your current interpretation. For concurrency, predict a guaranteed relationship rather than an arbitrary scheduling order. For an error case, identify whether it is rejected at compilation or returned during execution.

## Exercises

{exercises}

Implement these in the answer-free learner source. Keep one independent check per claim. A task can require tracing, construction, a changed input or a deliberate safe failure. Do not run a data race, corrupt memory or contact a shared cluster merely to demonstrate why it would be wrong.

## Common pitfalls and diagnosis

Read a compiler error from the first location in your source, then fix one cause at a time. Unused imports and variables are errors in Go; add an import when its use exists, rather than copying a large unused import list. A panic from `check` identifies a violated example contract. Compare the actual value with the expected value and inspect the state transition that produced it. A returned `error` is a value that the caller must handle; an ignored error can make later output look plausible while the original operation failed.

The lesson-specific explanations in the two examples identify the important counterexamples. Extend that reasoning to every investigation: explain why a plausible alternative would fail, and preserve a tiny input that distinguishes it. Treat empty data, missing values and cancellation as domain cases with explicit policies. In concurrent work, replace sleeps used as synchronization with channels, mutexes or an explicit ownership protocol.

## Progressive hints

{hints}

## Self-check and retrieval

Close the reference. Rebuild one normal case and one boundary case from a blank pad. Explain the role of {s["terms"][0][0].lower()} without using its name in the definition. Then change the domain while keeping the same invariant. Record the new input, your prediction and the observed output. If your program passes only because its input is hard-coded, explain which part would need a reusable function in a larger project.

## Next step and sources

[Primary language or library documentation]({s["source"]}), reviewed 2026-10-23. The teaching explanations and synthetic fixtures are original. This source supports the API contract; it does not verify the classroom worker. Runtime receipts are recorded separately by the repository validation tools. Continue with the next lesson when you can explain the six observations and diagnose a changed case without copying its answer.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for {ident}: {s["title"]}.
Read {paths["guide"]} and my saved attempt based on {paths["starter"]}.
Ask me to predict {s["cases"][0]["expected"]} and explain the mechanism.
Give one progressive hint about my first incorrect assumption.
Keep {paths["reference"]} and {paths["answers"]} closed until I request a reveal or comparison.
Check compiler or runtime evidence, distinguish local models from real integrations,
and finish with a fresh boundary case about {s["terms"][-1][0].lower()}.
```
"""
        answers = f"# {ident}: explained solutions\n\nThese are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.\n\n## Mechanism\n\n{s['model']}\n\n{s['anatomy']}\n\n"
        for i, c in enumerate(s["cases"], 1):
            answers += f"## {i}. {c['title']}\n\n{c['task']}\n\n```go\n{format_snippet(c['code'])}\n```\n\n**Expected:** {c['expected']}\n\n{c['explanation']}\n\n"
        answers += "## Transfer after comparison\n\nReturn to your own pad and reproduce one check with a new input. Explain why the check rejects a plausible wrong implementation. Keep the distinction between a pure model, an in-process fake, and a real external system visible in your notes.\n"
        starter = (
            'package main\n\nimport "fmt"\n\nfunc main() {\n'
            + "".join(
                "    // Exercise "
                + str(i)
                + ": "
                + c["title"]
                + ": "
                + c["task"]
                + "\n    // Expected: "
                + c["expected"]
                + "\n\n"
                for i, c in enumerate(s["cases"], 1)
            )
            + '    fmt.Println("Implement the six investigations in your saved pad.")\n}\n'
        )
        for key, content in [
            ("guide", guide),
            ("starter", format_go(starter)),
            ("reference", program(s)),
            ("answers", answers),
        ]:
            p = BASE.parent.parent / paths[key]
            p.parent.mkdir(parents=True, exist_ok=True)
            if key in {"guide", "answers"}:
                content = canonical_markdown(content, root=ROOT, path=paths[key])
            p.write_text(content, encoding="utf-8", newline="\n")
        plan["lessons"].append(
            dict(
                id=ident,
                title=s["title"],
                level=level,
                minutes=90 if n <= 16 else 120,
                prerequisites=prereqs,
                runtime="go",
                concepts=[a for a, b in s["terms"]],
                outcome="Explain and implement " + s["title"].lower() + ".",
                lab=s["cases"][0]["task"],
                verification=s["cases"][0]["expected"] + " " + s["cases"][-1]["expected"],
            )
        )
        manifest["lessons"].append(
            dict(
                id=ident,
                status="authored",
                language="go",
                runtime_profile="go",
                guide_path=paths["guide"],
                source_path=paths["starter"],
                solution_paths=[paths["reference"], paths["answers"]],
                verification_id=None,
            )
        )
    for filename, value in [("track.json", plan), ("lessons.json", manifest)]:
        (BASE / filename).write_text(
            json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n"
        )
    print(f"Rendered {len(SPECS)} complete Go lesson bundles.")
