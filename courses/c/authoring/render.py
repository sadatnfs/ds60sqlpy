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
from reasoning import LABELS, REASONING  # noqa: E402

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
    # Outside a function body clang-format reads `a && b` as an rvalue-reference declarator
    # and prints `a &&b`; C has no such declarator, so restore the operator spacing.
    return re.sub(r"(?<=[\w)\]]) &&(?=[\w(!])", " && ", format_c(source).strip())


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


def _clause(text):
    """The first sentence of an observation or task as a lower-case clause without its period."""
    return _lower_first(re.split(r"\.\s+(?=[A-Z])", text.strip())[0]).rstrip(".")


def _join(items):
    items = list(items)
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


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
            cond=cond,
            obs=_clause(c["expected"]),
            named=_case(c["title"]),
        )
        obs, named = _clause(c["expected"]), _case(c["title"])
        original = edited = None
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
                    f"Copy worked example 1, {named}, into a scratch pad and change {original} to {edited}. Before running, predict which CHECK fails and which value it sees in place of the worked result ({obs}); then run it and restore the original line."
                )
            else:
                row["task"] = (
                    f"Close worked example 1 and rebuild it in a fresh pad, keeping the CHECK on {cond}. Then propose one defined input change that would make that CHECK fail and explain why before trying it."
                )
            row["expected"] = (
                f"With {edited} the run {stop}, because {named} no longer shows that {obs}. Restoring {original} brings that observation back."
                if v
                else f"Your rebuild passes with the original input ({_lower_first(c['expected'])}), and your proposed change makes the CHECK on {cond} fail."
            )
            row["verify"] = (
                f"Name the value that made {cond} false, where your prediction for {named} said {obs}. "
                + (
                    f"Sanitizers report nothing for this {named} edit, so it is defined; restoring {original} passes again."
                    if v
                    else f"Keep the {named} change defined (no out-of-range or uninitialized read); undoing it passes again."
                )
            )
        elif index == 1:
            row["title"] = c["title"] + (
                ": diagnose an edited check" if v and v["in_check"] else ": debug a regression"
            )
            if v and v["in_check"]:
                row["task"] = (
                    f"A careless edit changed the CHECK in worked example 2, {named}, so that it reads {edited}. Run the example with that line, explain why the edited CHECK now fails even though the program state still means {obs}, and restore it."
                )
            elif v and _occurs(v["broken"], rows[0]["shown"] + "\n" + shown):
                row["task"] = (
                    f"A regression changed {original} to {edited} in worked example 2, {named}. Run the example with that change, use the failing CHECK to explain why {obs} no longer holds and repair it without changing the CHECK."
                )
            elif v:
                row["task"] = (
                    f"A regression changed one token in worked example 2, {named}, so one line now reads {edited}. Run the example with that line, use the failing CHECK to find why {obs} no longer holds and repair the line without changing the CHECK."
                )
            else:
                row["task"] = (
                    f"Introduce one defined, deliberate defect into a copy of worked example 2, {named}, that makes the CHECK on {cond} fail, then explain how the reported line leads back to the statement that should make {obs}."
                )
            row["expected"] = (
                f"Before the repair the run {stop}. Once the line reads {original} again, {named} again shows that {obs}."
                if v
                else f"The defective copy {stop}; the repaired copy reproduces the worked observation: {_lower_first(c['expected'])}"
            )
            row["verify"] = (
                f"Keep the failing and the repaired runs of {named}. Explain why the edited CHECK rejects the same state that {cond} accepts, where {obs}."
                if v and v["in_check"]
                else f"Keep the failing and the repaired runs of {named}. Explain why the changed token alters the value tested by {cond}, so the run can no longer show that {obs}."
            )
        elif v and not v["in_check"]:
            row["verify"] = (
                f"To confirm that {obs}, keep a CHECK equivalent to {cond} after you {_clause(c['task'])}. As a control for {named}, change {original} to {edited}: the run must stop with `Check failed` at that CHECK, with no sanitizer report. Restore the line before continuing."
            )
        elif v:
            row["verify"] = (
                f"To confirm that {obs}, keep a CHECK equivalent to {cond} after you {_clause(c['task'])}. As a control for {named}, change {original} to {edited} inside it: the run must stop with `Check failed`, which shows the CHECK can fail. Restore it."
            )
        else:
            row["verify"] = (
                f"To confirm that {obs}, keep a CHECK equivalent to {cond} after you {_clause(c['task'])}, and confirm the success line. Then name a defined input that would make it fail for {named}, without executing any out-of-range access."
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


ARRAY = re.compile(
    r"\b(?:unsigned\s+|const\s+)*(?:char|int|long|short|double|float|size_t|bool|u?int\d+_t|struct\s+\w+)"
    r"\s+\**(\w+)\s*\[\s*([^\]]*?)\s*\]"
)
NOT_FUNCTIONS = {"if", "for", "while", "switch", "sizeof", "return", "do"}


def _arrays(code):
    return list(dict.fromkeys(f"`{name}[{size}]`" for name, size in ARRAY.findall(code)))


def _helpers(helper):
    names = re.findall(r"\b(\w+)\s*\((?:[^;{}()]|\([^()]*\))*\)\s*\{", helper)
    return list(dict.fromkeys(f"`{n}`" for n in names if n not in NOT_FUNCTIONS))


def _case(title):
    return f'the "{_lower_first(title)}" case'


def _capital(text):
    return text[:1].upper() + text[1:]


def lesson_prose(ident, s, rows, following):
    """Guide paragraphs that name this lesson's own cases, checks, storage and helpers."""
    n = [r["named"] for r in rows]
    terms = [_lower_first(name) for name, meaning in s["terms"]]
    helpers = _helpers(s["helper"])
    arrays = _arrays(s["cases"][0]["code"] + "\n" + s["cases"][1]["code"])
    extra = [h for h in s["headers"].split()]
    where = " or ".join(helpers[:3]) if helpers else "the case code inside `main`"
    first, second = rows[0], rows[1]
    title = _lower_first(s["title"])
    t0 = terms[0]
    classroom = (
        f"Open the unified Docker classroom, choose C and save a pad for {ident}, {title}."
        f" The Linux worker compiles your `main.c` as C17 with warnings and pthread support, then runs {n[0]}, {n[1]} and the other {ident} cases"
        f" under bounded time and output. You need no host compiler to study {t0}, and Windows uses WSL 2."
    )
    pad = (
        f"For {n[2]} and every other {ident} case the pad takes no extra compiler flags, interactive input, archives, host files or packages."
        f" Files the {ident} reference creates are owned temporary fixtures, not saved progress;"
        f" multi-file builds and sanitizer runs of the {t0} code are contributor workflows."
    )
    reference = (
        f"The {ident} reference has `int main(void)`"
        + (f", {_join('`<' + h + '>`' for h in extra)}" if extra else "")
        + (f" and {_join(helpers)} above main" if helpers else " and runs every case inside main")
        + f". Its always-on `CHECK` evaluates once; a false CHECK on {first['cond']} in {n[0]} exits nonzero, while a pass prints nothing."
        f" Unlike `assert`, `NDEBUG` cannot remove it, so {t0} validation never depends on optional assertions."
        f" Solution snippets for {n[2]} and the rest belong inside main unless they declare a helper; one reference file assembles all six."
    )
    examples = (
        f"Worked example 1 ({n[0]}) and worked example 2 ({n[1]}) are complete C files to copy whole into your pad."
        f" Example 2 first repeats {n[0]}"
        + (f" and includes {_join(helpers)}" if helpers else "")
        + f"; the reference adds {n[2]}, {n[3]}, {n[4]} and {n[5]}."
    )
    prediction = (
        f"Predict worked example 1: when you {_clause(s['cases'][0]['task'])}, the CHECK on {first['cond']} should see that {first['obs']}."
        f" For {n[1]}, predict that {second['obs']}."
        + (
            f" Write down the declared size of {_join(arrays)} before indexing it."
            if arrays
            else f" Trace each object {n[0]} and {n[1]} read from initialization to last use."
        )
        + f" Separate a compiler diagnostic, a valid {t0} rejection and undefined behavior; never run an out-of-bounds access, dangling read or data race in {ident} to see what it prints."
    )
    pitfalls = (
        f"Fix diagnostics in {n[0]} and {n[1]} one cause at a time, starting with the first warning for {title}; a declaration mismatch in {where} cascades."
        f" If the CHECK on {second['cond']} in {n[1]} fails, compare the actual value with the claim that {second['obs']} and find the earliest departing transition."
        f" A clean compile, or a run of {n[2]} that did not crash, does not rule out undefined behavior."
        f"\n\nIn {n[3]} and {n[4]}, give every pointer and index a target, bounds, alignment, lifetime and mutability under the {_join(terms)} rules."
        f" Check each library result before use and release each owned resource once per path."
        f" {_capital(n[5])} transfers the mechanism; keep its distinction from {n[0]} instead of replacing a rejected input with a plausible default."
    )
    selfcheck = (
        f"Close the reference and explain {t0} with a tiny trace of {n[2]}."
        f" Rebuild {n[0]} and {n[3]} from a blank file, stating what makes each expression defined."
        f" Change the data or ownership in {n[4]} and predict the result, then name the observation that would refute your account of {_join(terms)}."
    )
    if following:
        onward = (
            f"Move on to {following[0]}, {_lower_first(following[1])}, once you can explain {n[0]} through {n[5]} and repair Exercise 2 without an answer."
            f" Later lessons hide {_join(terms)} behind APIs, where an unexplained pointer or unchecked size grows more dangerous."
        )
    else:
        onward = (
            f"This is the last C lesson: finish when you can explain {n[0]} through {n[5]} and repair Exercise 2 without an answer."
            f" Carry {_join(terms)} into your own APIs, where an unexplained pointer or unchecked size grows more dangerous."
        )
    nextstep = f"Save your {ident} source and diagnostics with your notes. {onward}"
    transfer = (
        f"Add a fresh distinguishing input for {n[5]} to your own {ident} source."
        f" Explain why every access in {where} stays within a live object and each owned resource is released."
        f" An expected {t0} failure belongs in the test contract; undefined behavior does not."
        f" Keep diagnostics and sanitizer evidence for {n[1]} apart from ordinary output: the fixture proves its stated {_join(terms)} assumptions, not universal safety."
    )
    return dict(
        reference=reference,
        examples=examples,
        prediction=prediction,
        pitfalls=pitfalls,
        selfcheck=selfcheck,
        nextstep=nextstep,
        transfer=transfer,
        terms=terms,
        classroom=classroom,
        pad=pad,
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
        rows = practice(ident, s)
        following = (f"c-{number + 1:03d}", SPECS[number]["title"]) if number < len(SPECS) else None
        prose = lesson_prose(ident, s, rows, following)
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

{outcome} Along the way, explain {_join(prose["terms"])}. Implement the six investigations, from {rows[0]["named"]} to {rows[5]["named"]}, with explicit checks, identify a plausible defect and defend a fresh boundary case before execution. Completing a reference is not evidence of independent mastery.

## Purpose and mental model

{s["model"]}

## Vocabulary and concepts

{vocabulary}

## Syntax anatomy and execution trace

{s["anatomy"]}

## How to run this lesson

{prose["classroom"]}

{prose["reference"]}

For an independently prepared Linux contributor environment, copy your own file to an ignored working directory and run:

```sh
cc -std=c17 -Wall -Wextra -Wpedantic -pthread main.c -lm -o lesson
./lesson
```

{prose["pad"]}

{s["boundary"]}

{prose["examples"]}

## Worked example / walkthrough

{examples}

## Prediction before execution

{prose["prediction"]}

## Exercises

{exercises}

## Common pitfalls and diagnosis

{prose["pitfalls"]}

## Self-check and retrieval

{prose["selfcheck"]}

## Next step and sources

{prose["nextstep"]}

[Primary reference for {_lower_first(s["title"])}]({s["source"]}), reviewed 2026-10-23. Teaching explanations and synthetic fixtures are original.

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for {ident}: {s["title"]}.
Read {paths["guide"]} and my saved attempt based on {paths["starter"]}.
Ask me to predict what worked example 1, {rows[0]["named"]}, shows (expected: {rows[0]["obs"]}) and justify every memory access.
Give one hint about my first incorrect assumption; request actual compiler or runtime evidence.
Keep {paths["reference"]} and {paths["answers"]} closed until I request a reveal or comparison.
Distinguish C17 guarantees from POSIX or compiler-specific behavior.
Finish with a fresh case about {prose["terms"][-1]}.
```
"""
        answers = f"# {ident}: explained solutions\n\nCompare after an attempt or explicit reveal. The complete executable reference, `{ident}_solution.c`, implements all six cases, from {rows[0]['named']} to {rows[5]['named']}, in one `main.c`.\n\n## Mechanism and assumptions\n\n{s['model']}\n\n{s['anatomy']}\n\n"
        notes = REASONING.get(ident)
        if notes and len(notes["cases"]) != len(rows):
            raise ValueError(ident + " reasoning needs one entry per case")
        for i, r in enumerate(rows, 1):
            lead = f"The unchanged code is worked example {i}:\n\n" if i <= 2 else ""
            answers += f"## Exercise {i}: {r['title']}\n\n{r['task']}\n\n{lead}```c\n{r['shown']}\n```\n\n**Expected:** {r['expected']}\n\n{r['why']}\n\n"
            if notes:
                answers += "".join(
                    f"**{label}.** {text}\n\n"
                    for label, text in zip(LABELS, notes["cases"][i - 1], strict=True)
                )
        answers += (
            "## After comparison\n\n" + (notes["transfer"] if notes else prose["transfer"]) + "\n"
        )
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
