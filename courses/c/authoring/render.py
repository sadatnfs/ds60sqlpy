"""Render the C learning route from original, case-based teaching specifications."""

import json
import os
import re
import shlex
import subprocess
import textwrap
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
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
        exercises = "\n\n".join(
            f"### Exercise {i}: {c['title']}\n\n{c['task']}\n\n**Expected:** {c['expected']}\n\n**Verify:** Preserve an independent assertion for this result. Explain the valid input range, object lifetime and bounds required by every access.\n\n**Progressive hints:** First identify the relevant invariant. Then trace the smallest input satisfying the stated case. Finally isolate the expression that would distinguish your implementation from a plausible wrong one."
            for i, c in enumerate(s["cases"], 1)
        )
        guide = f"""# {ident}: {s["title"]}

## Level and prerequisites

{level.capitalize()}, approximately {90 if number <= 14 else 120} minutes plus a later retrieval session. Direct prerequisites: {", ".join("`" + p + "`" for p in prereqs) or "None. Begin with the difference between source text, a compiler and a running process."}

## Learning objectives

Explain {", ".join(name.lower() for name, meaning in s["terms"])}. Implement the six investigations with explicit checks, identify a plausible defect and defend a fresh boundary case before execution. Completing a reference is not evidence of independent mastery.

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

[Primary language, library or platform reference]({s["source"]}), reviewed 2026-10-23. Teaching explanations and synthetic fixtures are original. Source review, successful compilation, executed checks, sanitizer results and Linux Docker receipts are different evidence layers. Runtime qualification is recorded by the repository validation tools.

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
        for i, c in enumerate(s["cases"], 1):
            answers += f"## Exercise {i}: {c['title']}\n\n{c['task']}\n\n```c\n{snippet(c['code'])}\n```\n\n**Expected:** {c['expected']}\n\n{c['why']}\n\n"
        answers += "## After comparison\n\nReturn to your own source and add a fresh distinguishing input. Explain why every access remains within a live object and why every owned resource is released. A valid expected failure belongs in the test contract; undefined behavior does not. Retain compiler diagnostics and any sanitizer evidence separately from ordinary output. A working fixture demonstrates its stated assumptions, not universal safety for arbitrary inputs.\n"
        starter = (
            "#include <stdio.h>\n\nint main(void) {\n"
            + "".join(
                "    /* Exercise "
                + str(i)
                + ": "
                + c["title"]
                + "\n       "
                + c["task"]
                + "\n       Expected: "
                + c["expected"]
                + " */\n\n"
                for i, c in enumerate(s["cases"], 1)
            )
            + '    puts("Implement the six investigations in your saved pad.");\n    return 0;\n}\n'
        )
        for key, content in [
            ("guide", guide),
            ("starter", format_c(starter)),
            ("reference", program(s)),
            ("answers", answers),
        ]:
            target = BASE.parent.parent / paths[key]
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8", newline="\n")
        plan["lessons"].append(
            dict(
                id=ident,
                title=s["title"],
                level=level,
                minutes=90 if number <= 14 else 120,
                prerequisites=prereqs,
                runtime="c17",
                concepts=[name for name, meaning in s["terms"]],
                outcome="Explain and implement " + s["title"].lower() + ".",
                lab=s["cases"][0]["task"],
                verification=s["cases"][0]["expected"] + " " + s["cases"][-1]["expected"],
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
    print(f"Rendered {len(SPECS)} complete C lesson bundles.")
