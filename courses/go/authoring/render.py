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

sys.path.insert(0, str(Path(__file__).resolve().parent))
import variants  # noqa: E402
from outcomes import MINUTES, OUTCOMES  # noqa: E402

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


def _lower_first(text):
    """Lower-case an ordinary leading word, leaving identifiers such as JSON intact."""
    return text[:1].lower() + text[1:] if text[1:2].islower() else text


def _message(value):
    if value and len(value) >= 2 and value[0] == value[-1] == '"':
        return value[1:-1].replace('\\"', '"').replace("\\\\", "\\")
    return value


def _occurs(excerpt, code):
    """Whether an edited excerpt already appears verbatim, which would make it ambiguous."""
    return " ".join(excerpt.split()) in " ".join(code.split())


def practice(ident, s):
    """Six exercises: two derived from the worked examples, four authored investigations.

    Every Verify line and hint is built from the case's own check and the one-token
    edit that qualify_variants.py observed making that check fail.
    """
    span = variants.code_span
    records = variants.load_records()
    rows = []
    for index, c in enumerate(s["cases"]):
        shown = format_snippet(c["code"])
        v = variants.variant(records, ident, index, c["code"], shown)
        spans = variants.checks(shown) or variants.checks(c["code"])
        cond = span(v["condition"] if v and v.get("condition") else spans[-1][2])
        message = _message(v["message"] if v else spans[-1][3]) or "the check"
        panic = span(message)
        row = dict(
            title=c["title"],
            task=c["task"],
            expected=c["expected"],
            code=c["code"],
            explanation=c["explanation"],
            variant=v,
            shown=shown,
        )
        if v:
            original, edited = span(v["line"]), span(v["broken"])
        if index == 0:
            row["title"] = c["title"] + (
                ": predict an edited check" if v and v["in_check"] else ": change one input"
            )
            if v and v["in_check"]:
                row["task"] = (
                    f"Copy worked example 1 into a scratch pad and change {original} to {edited} inside its check. Before running, predict whether the check still passes and explain why; then restore it."
                )
            elif v:
                row["task"] = (
                    f"Copy worked example 1 into a scratch pad and change {original} to {edited}. Before running, predict which check fails and which value it now sees; then run it and restore the original line."
                )
            else:
                row["task"] = (
                    f"Close worked example 1 and rebuild it in a fresh pad, keeping its check {cond}. Then propose one input change that would make that check fail and explain why before trying it."
                )
            row["expected"] = (
                f"The changed run panics with {panic} because "
                + ("the edited check" if v["in_check"] else cond)
                + f" no longer holds. Restoring the original line brings back the worked observation: {_lower_first(c['expected'])}"
                if v
                else f"Your rebuild passes with the original input ({_lower_first(c['expected'])}), and your proposed change makes the check panic with {panic}."
            )
            row["verify"] = (
                f"Compare your written prediction with the panic message {panic} and name the value that made {cond} false. After restoring the input, the program must print its success line again."
            )
        elif index == 1:
            row["title"] = c["title"] + (
                ": diagnose an edited check" if v and v["in_check"] else ": debug a regression"
            )
            if v and v["in_check"]:
                row["task"] = (
                    f"A careless edit changed the check in worked example 2 so that it reads {edited}. Run worked example 2 with that line, explain why the edited check now fails for the same program state, and restore it."
                )
            elif v and _occurs(v["broken"], rows[0]["shown"] + "\n" + shown):
                row["task"] = (
                    f"A regression changed {original} to {edited} in worked example 2. Run worked example 2 with that change, use the failure to explain the defect and repair it without changing the check."
                )
            elif v:
                row["task"] = (
                    f"A regression changed one token in worked example 2, so one line now reads {edited}. Run worked example 2 with that line, use the failure to locate the defect and repair it without changing the check."
                )
            else:
                row["task"] = (
                    f"Introduce one deliberate defect into a copy of worked example 2 that makes {cond} fail, then explain how the panic message leads back to the faulty line."
                )
            row["expected"] = (
                f"Before the repair the program panics with {panic}; after it the line reads {original} again and {_lower_first(c['expected'])}"
                if v
                else f"The defective copy panics with {panic}; the repaired copy reproduces the worked observation: {_lower_first(c['expected'])}"
            )
            row["verify"] = (
                f"Keep the failing and the repaired runs. Explain why the edited check rejects the same program state that {cond} accepts."
                if v and v["in_check"]
                else f"Keep the failing and the repaired runs. Explain why the changed token alters the value tested by {cond} for this input."
            )
        elif v and not v["in_check"]:
            row["verify"] = (
                f"Keep a check equivalent to {cond}. As a control, change {original} to {edited}: the run must panic with {panic}. Restore the line before continuing."
            )
        elif v:
            row["verify"] = (
                f"Keep a check equivalent to {cond}. As a control, change {original} to {edited} inside that check: it must panic with {panic}, which shows the check can fail. Restore it."
            )
        else:
            row["verify"] = (
                f"Keep a check equivalent to {cond} and confirm the success line. Then name an input that would make it fail and the panic message ({panic}) you would expect."
            )
        third = (
            f"Predict the effect of changing {original} to {edited} before running anything. If the prediction is hard, trace that line again with the original input."
            if v and not v["in_check"]
            else f"Name one input that would make {cond} false. A check that no input can falsify is not evidence."
        )
        if index == 0 and v:
            third = f"Compute the checked value with {edited} in place before running, then compare it with the value {cond} expects."
        elif index == 1 and v:
            third = f"Compare {edited} with the same line in worked example 2 and state the claim each version makes."
        row["hints"] = [
            "Restate the expected observation: "
            + (c["expected"] if index < 2 else row["expected"]),
            f"The check {cond} decides this case. List the values it reads and trace each one back to the input before changing code.",
            third,
        ]
        rows.append(row)
    return rows


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
        rows = practice(ident, s)
        exercises = "\n\n".join(
            f"### Exercise {i}: {r['title']}\n\n{r['task']}\n\n**Expected:** {r['expected']}\n\n**Verify:** {r['verify']}"
            for i, r in enumerate(rows, 1)
        )
        hints = "\n\n".join(
            f"### Hint for investigation {i}: {r['title']}\n\n"
            + "\n".join(f"{n}. {hint}" for n, hint in enumerate(r["hints"], 1))
            for i, r in enumerate(rows, 1)
        )
        minutes = MINUTES.get(ident, 90 if n <= 16 else 120)
        outcome = OUTCOMES[ident]
        if outcome.lower().startswith("explain and implement"):
            raise ValueError(ident + " needs a specific outcome")
        guide = f"""# {ident}: {s["title"]}

## Level and prerequisites

{level.capitalize()}. Allow about {minutes} minutes, then revisit the transfer case later. Prerequisites: {", ".join(prereqs) or "No previous Go knowledge. Read source as plain text and distinguish editing from executing."}

## Learning objectives

{outcome} Along the way, explain {", ".join(a.lower() for a, b in s["terms"])}; implement the six investigations below; and defend the expected result of a changed input before running it.

## Why this mechanism matters

{s["model"]}

## Vocabulary and concepts

{terms}

## Syntax anatomy and reasoning

{s["anatomy"]}

## Run this lesson

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

[Primary language or library documentation]({s["source"]}), reviewed 2026-10-23. The teaching explanations and synthetic fixtures are original. Continue with the next lesson when you can explain the six observations and diagnose a changed case without copying its answer.

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
        for i, r in enumerate(rows, 1):
            lead = ""
            if i <= 2:
                lead = f"The unchanged code is worked example {i}:\n\n"
            answers += f"## {i}. {r['title']}\n\n{r['task']}\n\n{lead}```go\n{r['shown']}\n```\n\n**Expected:** {r['expected']}\n\n{r['explanation']}\n\n"
        answers += "## Transfer after comparison\n\nReturn to your own pad and reproduce one check with a new input. Explain why the check rejects a plausible wrong implementation. Keep the distinction between a pure model, an in-process fake, and a real external system visible in your notes.\n"
        starter = (
            'package main\n\nimport "fmt"\n\nfunc main() {\n'
            + "".join(
                "    // Exercise "
                + str(i)
                + ": "
                + r["title"]
                + ": "
                + r["task"]
                + "\n    // Expected: "
                + r["expected"]
                + "\n\n"
                for i, r in enumerate(rows, 1)
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
                minutes=minutes,
                prerequisites=prereqs,
                runtime="go",
                concepts=[a for a, b in s["terms"]],
                outcome=outcome,
                lab=s["cases"][2]["task"],
                verification=s["cases"][2]["expected"],
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
    missing = set(OUTCOMES) ^ {item["id"] for item in plan["lessons"]}
    if missing:
        raise ValueError("outcomes.py and the lesson list differ: " + ", ".join(sorted(missing)))
    print(f"Rendered {len(SPECS)} complete Go lesson bundles.")
