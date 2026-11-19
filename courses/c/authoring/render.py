"""Render the C learning route from original, case-based teaching specifications."""

import json
import os
import re
import shlex
import subprocess
import sys
import textwrap
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.format_inline_code import canonical_markdown  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import variants  # noqa: E402
from outcomes import MINUTES, OUTCOMES  # noqa: E402

SPECS = []


def case(title, task, expected, code, why):
    return dict(
        title=title, task=task, expected=expected, code=textwrap.dedent(code).strip(), why=why
    )


def add(
    title,
    model,
    anatomy,
    terms,
    cases,
    helper="",
    headers="",
    source="https://www.gnu.org/software/libc/manual/html_node/index.html",
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
            helper=textwrap.dedent(helper).strip(),
            headers=headers,
            source=source,
            boundary=boundary,
        )
    )


def format_c(source):
    command = shlex.split(os.environ.get("C_LESSON_FORMATTER", "clang-format"))
    result = subprocess.run(
        command + ["--style=LLVM"], input=source, text=True, capture_output=True, check=False
    )
    if result.returncode:
        raise ValueError("C source formatting failed: " + result.stderr)
    return result.stdout


def snippet(source):
    return format_c(source).strip()


def program(s, count=6, worked=False):
    helper = (
        re.sub(r"(?m)^static ", "", format_c(s["helper"]))
        if worked and s["helper"]
        else s["helper"]
    )
    headers = sorted(
        set(
            "assert.h stdbool.h stddef.h stdint.h stdio.h stdlib.h string.h limits.h".split()
            + s["headers"].split()
        )
    )
    body = "\n\n".join(
        "/* " + c["title"] + " */\n{\n" + textwrap.indent(c["code"], "    ") + "\n}"
        for c in s["cases"][:count]
    )
    return format_c(
        "\n".join("#include <" + h + ">" for h in headers)
        + """\n\nstatic void lesson_check(bool condition, const char *file, int line) {\n    if (!condition) { fprintf(stderr, "Check failed at %s:%d\\n", file, line); abort(); }\n}\n#define CHECK(condition) lesson_check((condition), __FILE__, __LINE__)\n\n"""
        + helper
        + "\n\nint main(void) {\n"
        + textwrap.indent(body, "    ")
        + '\n    puts("'
        + ("All lesson checks passed." if count == 6 else "Worked example checks passed.")
        + '");\n    return 0;\n}\n'
    )


def _lower_first(text):
    """Lower-case an ordinary leading word, leaving identifiers such as NULL intact."""
    return text[:1].lower() + text[1:] if text[1:2].islower() else text


def _occurs(excerpt, code):
    """Whether an edited excerpt already appears verbatim, which would make it ambiguous."""
    return " ".join(excerpt.split()) in " ".join(code.split())


def practice(ident, s):
    """Six exercises: two derived from the worked examples, four authored investigations.

    Every Verify line and hint names the case's own CHECK and a one-token edit that
    qualify_variants.py observed making that CHECK fail without any sanitizer report.
    """
    span = variants.code_span
    records = variants.load_records()
    rows = []
    for index, c in enumerate(s["cases"]):
        shown = snippet(c["code"])
        v = variants.variant(records, ident, index, c["code"], shown)
        spans = variants.checks(shown) or variants.checks(c["code"])
        cond = span(v["condition"] if v and v.get("condition") else spans[-1][2])
        stop = f"stops with `Check failed` at the CHECK on {cond}"
        row = dict(
            title=c["title"],
            task=c["task"],
            expected=c["expected"],
            why=c["why"],
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
                    f"Copy worked example 1 into a scratch pad and change {original} to {edited} inside its CHECK. Before running, predict whether the CHECK still holds and explain why; then restore it."
                )
            elif v:
                row["task"] = (
                    f"Copy worked example 1 into a scratch pad and change {original} to {edited}. Before running, predict which CHECK fails and which value it now sees; then run it and restore the original line."
                )
            else:
                row["task"] = (
                    f"Close worked example 1 and rebuild it in a fresh pad, keeping the CHECK on {cond}. Then propose one defined input change that would make that CHECK fail and explain why before trying it."
                )
            row["expected"] = (
                f"The changed run {stop}. Restoring the original line brings back the worked observation: {_lower_first(c['expected'])}"
                if v
                else f"Your rebuild passes with the original input ({_lower_first(c['expected'])}), and your proposed change makes the CHECK on {cond} fail."
            )
            row["verify"] = (
                f"Compare your written prediction with the failing CHECK and name the value that made {cond} false. The edit is defined behavior: it was run under AddressSanitizer and UndefinedBehaviorSanitizer without a report. After restoring the input, the program prints its success line again."
            )
        elif index == 1:
            row["title"] = c["title"] + (
                ": diagnose an edited check" if v and v["in_check"] else ": debug a regression"
            )
            if v and v["in_check"]:
                row["task"] = (
                    f"A careless edit changed the CHECK in worked example 2 so that it reads {edited}. Run worked example 2 with that line, explain why the edited CHECK now fails for the same program state, and restore it."
                )
            elif v and _occurs(v["broken"], rows[0]["shown"] + "\n" + shown):
                row["task"] = (
                    f"A regression changed {original} to {edited} in worked example 2. Run worked example 2 with that change, use the failing CHECK to explain the defect and repair it without changing the CHECK."
                )
            elif v:
                row["task"] = (
                    f"A regression changed one token in worked example 2, so one line now reads {edited}. Run worked example 2 with that line, use the failing CHECK to locate the defect and repair it without changing the CHECK."
                )
            else:
                row["task"] = (
                    f"Introduce one defined, deliberate defect into a copy of worked example 2 that makes the CHECK on {cond} fail, then explain how the reported line leads back to the faulty statement."
                )
            row["expected"] = (
                f"Before the repair the run {stop}; after it the line reads {original} again and {_lower_first(c['expected'])}"
                if v
                else f"The defective copy {stop}; the repaired copy reproduces the worked observation: {_lower_first(c['expected'])}"
            )
            row["verify"] = (
                f"Keep the failing and the repaired runs. Explain why the edited CHECK rejects the same program state that {cond} accepts."
                if v and v["in_check"]
                else f"Keep the failing and the repaired runs. Explain why the changed token alters the value tested by {cond} for this input."
            )
        elif v and not v["in_check"]:
            row["verify"] = (
                f"Keep a CHECK equivalent to {cond}. As a control, change {original} to {edited}: the run must stop with `Check failed` at that CHECK, with no sanitizer report. Restore the line before continuing."
            )
        elif v:
            row["verify"] = (
                f"Keep a CHECK equivalent to {cond}. As a control, change {original} to {edited} inside it: the run must stop with `Check failed`, which shows the CHECK can fail. Restore it."
            )
        else:
            row["verify"] = (
                f"Keep a CHECK equivalent to {cond} and confirm the success line. Then name a defined input that would make it fail, without executing any out-of-range access."
            )
        if index == 0 and v:
            third = f"compute the checked value with {edited} in place before running"
        elif index == 1 and v:
            third = f"compare {edited} with the same line in worked example 2 and state the claim each version makes"
        elif v and not v["in_check"]:
            third = f"predict the effect of changing {original} to {edited} before running anything"
        else:
            third = f"name one defined input that would make {cond} false"
        row["hints"] = (
            f"First restate the expected observation: {_lower_first(c['expected'])} "
            f"Then list the values read by {cond} and trace each one from its initialization"
            + (", including the bounds of every array it touches" if "[" in c["code"] else "")
            + f". Finally, {third}."
        )
        rows.append(row)
    return rows


def render():
    plan = dict(
        schema_version=1,
        id="c",
        title="C: memory, systems and reliable native programs",
        summary="A complete C17 route from first compilation through pointers, resource ownership, data structures, parsing, concurrency and maintainable systems projects. Safe counterexamples and checked programs make the language rules concrete.",
        lessons=[],
    )
    inventory = dict(schema_version=1, track_id="c", lessons=[])
    for number, s in enumerate(SPECS, 1):
        ident = f"c-{number:03d}"
        level = "beginner" if number <= 14 else "intermediate" if number <= 28 else "advanced"
        prereqs = [f"c-{number - 1:03d}"] if number > 1 else []
        paths = {
            k: f"courses/c/{folder}/{ident}{suffix}"
            for k, folder, suffix in [
                ("guide", "guides", ".md"),
                ("starter", "lessons", ".c"),
                ("reference", "solutions", "_solution.c"),
                ("answers", "solutions", "_solutions.md"),
            ]
        }
        vocabulary = "\n".join(f"- **{name}:** {meaning}" for name, meaning in s["terms"])
        examples = "\n\n".join(
            f"### Worked example {i + 1}: {c['title']}\n\n{c['task']}\n\n```c\n{program(s, i + 1, worked=True)}\n```\n\n**Observe:** {c['expected']}\n\n{c['why']}"
            for i, c in enumerate(s["cases"][:2])
        )
        rows = practice(ident, s)
        exercises = "\n\n".join(
            f"### Exercise {i}: {r['title']}\n\n{r['task']}\n\n**Expected:** {r['expected']}\n\n**Verify:** {r['verify']}\n\n**Progressive hints:** {r['hints']}"
            for i, r in enumerate(rows, 1)
        )
        minutes = MINUTES.get(ident, 90 if number <= 14 else 120)
        outcome = OUTCOMES[ident]
        if outcome.lower().startswith("explain and implement"):
            raise ValueError(ident + " needs a specific outcome")
        guide = f"""# {ident}: {s["title"]}

## Level and prerequisites

{level.capitalize()}, approximately {minutes} minutes plus a later retrieval session. Direct prerequisites: {", ".join("`" + p + "`" for p in prereqs) or "None. Begin with the difference between source text, a compiler and a running process."}

## Learning objectives

{outcome} Along the way, explain {", ".join(name.lower() for name, meaning in s["terms"])}. Implement the six investigations with explicit checks, identify a plausible defect and defend a fresh boundary case before execution. Completing a reference is not evidence of independent mastery.

## Purpose and mental model

{s["model"]}

## Vocabulary and concepts

{vocabulary}

## Syntax anatomy and execution trace

{s["anatomy"]}

## How to run this lesson

Open the unified Docker classroom, choose C and save your own learner pad. The prepared Linux worker stages one `main.c`, compiles it as C17 with warnings and pthread support, and executes the result under bounded time and output. No host compiler is required. Windows uses WSL 2 and the same Linux containers.

The complete reference has `int main(void)` and the required standard headers. Its `CHECK` helper is always active and evaluates its condition once. A false check terminates with a nonzero result; a passing check produces no output. Unlike the standard `assert` macro, this helper is not removed by `NDEBUG`. Required operations and input validation must never depend on optional assertions. The explanatory solution snippets belong inside main unless they declare a helper; supporting declarations go above main. `CHECK(expression)` is the always-on teaching check supplied by the complete reference. The separate reference assembles all six cases into one complete file.

For an independently prepared Linux contributor environment, copy your own file to an ignored working directory and run:

```sh
cc -std=c17 -Wall -Wextra -Wpedantic -pthread main.c -lm -o lesson
./lesson
```

The pad does not accept arbitrary compiler flags, interactive input, a project archive, host files or external package installation. Files created by a reference are owned temporary fixtures, not saved learner progress. Multi-file builds and sanitizers are explicitly prepared contributor workflows when discussed below.

{s["boundary"]}

Each worked example below is a complete C file. Copy one whole block into your saved pad. Example 2 includes the first case as well as the second, so its setup is complete. Supporting helper definitions are included. The separate reference adds the other four investigations.

## Worked example / walkthrough

{examples}

## Prediction before execution

Trace each object from initialization through its last valid use. Write down the size of every array, the capacity of every output buffer and the ownership of any allocated storage. Distinguish a compiler diagnostic from a valid runtime rejection and from undefined behavior. Never execute an out-of-bounds access, dangling-pointer read or data race simply to discover what value it happens to print.

## Exercises

{exercises}

## Common pitfalls and diagnosis

Begin with the first relevant compiler warning or error. A declaration mismatch can cause many later diagnostics, so fix one cause at a time. If a check fails, compare actual and expected values and identify the earliest state transition that differs from the intended invariant. A program that compiles can still contain undefined behavior. A program that ran once without crashing can still access invalid memory.

For every pointer, identify its target object, bounds, alignment, lifetime and whether mutation is permitted. For every library call, inspect its return value before using output. For every owned resource, identify one release on each completed path. The worked examples and solutions explain the lesson-specific counterexamples; keep those distinctions rather than replacing a rejected input with a plausible default.

## Self-check and retrieval

Close the reference and explain {s["terms"][0][0].lower()} using a tiny concrete trace. Reconstruct one normal case and one boundary case from a blank source file. State the assumptions that make every expression defined. Then change the data or ownership pattern and predict the result. Explain which observation would prove your interpretation wrong.

## Next step and sources

Save the source and its actual diagnostics with your learning notes. Move onward when you can explain all six outcomes and repair a changed case without copying an answer. Larger projects reuse these contracts; an unexplained pointer or unchecked size calculation becomes more dangerous when hidden behind an API.

[Primary language, library or platform reference]({s["source"]}), reviewed 2026-10-23. Teaching explanations and synthetic fixtures are original.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for {ident}: {s["title"]}.
Read {paths["guide"]} and my saved attempt based on {paths["starter"]}.
Ask me to predict {s["cases"][0]["expected"]} and justify every memory access.
Give one hint about my first incorrect assumption; request actual compiler or runtime evidence.
Keep {paths["reference"]} and {paths["answers"]} closed until I request a reveal or comparison.
Distinguish C17 guarantees from POSIX or compiler-specific behavior.
Finish with a fresh case about {s["terms"][-1][0].lower()}.
```
"""
        answers = f"# {ident}: explained solutions\n\nCompare after an attempt or explicit reveal. The complete executable reference implements all six checks in one main.c.\n\n## Mechanism and assumptions\n\n{s['model']}\n\n{s['anatomy']}\n\n"
        for i, r in enumerate(rows, 1):
            lead = f"The unchanged code is worked example {i}:\n\n" if i <= 2 else ""
            answers += f"## Exercise {i}: {r['title']}\n\n{r['task']}\n\n{lead}```c\n{r['shown']}\n```\n\n**Expected:** {r['expected']}\n\n{r['why']}\n\n"
        answers += "## After comparison\n\nReturn to your own source and add a fresh distinguishing input. Explain why every access remains within a live object and why every owned resource is released. A valid expected failure belongs in the test contract; undefined behavior does not. Retain compiler diagnostics and any sanitizer evidence separately from ordinary output. A working fixture demonstrates its stated assumptions, not universal safety for arbitrary inputs.\n"
        starter = (
            "#include <stdio.h>\n\nint main(void) {\n"
            + "".join(
                "    /* Exercise "
                + str(i)
                + ": "
                + r["title"]
                + "\n       "
                + r["task"].replace("*/", "* /")
                + "\n       Expected: "
                + r["expected"].replace("*/", "* /")
                + " */\n\n"
                for i, r in enumerate(rows, 1)
            )
            + '    puts("Implement the six investigations in your saved pad.");\n    return 0;\n}\n'
        )
        for key, content in [
            ("guide", guide),
            ("starter", format_c(starter)),
            ("reference", program(s)),
            ("answers", answers),
        ]:
            if key in {"guide", "answers"}:
                content = canonical_markdown(content, root=ROOT, path=paths[key])
            target = BASE.parent.parent / paths[key]
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8", newline="\n")
        plan["lessons"].append(
            dict(
                id=ident,
                title=s["title"],
                level=level,
                minutes=minutes,
                prerequisites=prereqs,
                runtime="c17",
                concepts=[name for name, meaning in s["terms"]],
                outcome=outcome,
                lab=s["cases"][2]["task"],
                verification=s["cases"][2]["expected"],
            )
        )
        inventory["lessons"].append(
            dict(
                id=ident,
                status="authored",
                language="c",
                runtime_profile="c17",
                guide_path=paths["guide"],
                source_path=paths["starter"],
                solution_paths=[paths["reference"], paths["answers"]],
                verification_id=None,
            )
        )
    for name, value in [("track.json", plan), ("lessons.json", inventory)]:
        (BASE / name).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")
    missing = set(OUTCOMES) ^ {item["id"] for item in plan["lessons"]}
    if missing:
        raise ValueError("outcomes.py and the lesson list differ: " + ", ".join(sorted(missing)))
    print(f"Rendered {len(SPECS)} complete C lesson bundles.")
