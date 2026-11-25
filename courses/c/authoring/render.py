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
from transfer import PITFALLS, TRANSFER  # noqa: E402

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


C_WORDS = {
    "bool",
    "char",
    "const",
    "double",
    "enum",
    "false",
    "float",
    "int",
    "long",
    "short",
    "signed",
    "sizeof",
    "struct",
    "true",
    "union",
    "unsigned",
    "void",
}


def _trace(condition):
    """The first hint: which values the CHECK reads, named from its own condition."""
    text = re.sub(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'', " ", condition)
    text = re.sub(r"\b(?:enum|struct|union)\s+\w+", " ", text)
    names = [
        name
        for name in re.findall(r"(?<![\w.>])([A-Za-z_]\w*)\b(?!\s*\()", text)
        if name not in C_WORDS and not name.isupper() and not name.endswith("_t")
    ]
    names = list(dict.fromkeys(names))
    calls = list(dict.fromkeys(re.findall(r"(?<![\w.>])([A-Za-z_]\w*)\s*\(", text)))
    calls = [name for name in calls if name not in C_WORDS and name != "CHECK"]
    if names and len(names) <= 2:
        return f"First trace {_join('`' + n + '`' for n in names)} from initialization."
    if calls and not names and all(n.isupper() for n in calls[:2]):
        return f"First expand {_join('`' + n + '`' for n in calls[:2])} by hand."
    if calls and not names:
        verb = "returns" if len(calls) == 1 else "return"
        return f"First work out what {_join('`' + n + '`' for n in calls[:2])} {verb} here."
    if not names:
        return f"First evaluate {variants.code_span(condition)} by hand."
    return f"First trace each value in {variants.code_span(condition)} from initialization."


def _first_sentence(text):
    return re.split(r"(?<=\.)\s+(?=[A-Z])", text.strip())[0]


def practice(ident, s):
    """Six exercises: two derived from the worked examples, four authored investigations.

    Every Verify line names the case's own CHECK and a one-token edit that
    qualify_variants.py observed making that CHECK fail without any sanitizer report.
    The shared method (hint order, control edits, repairing the line rather than the
    CHECK) lives once in courses/c/STUDY-GUIDE.md, so each line here states only
    this case's edit, condition and observation. Hints name the values to trace and,
    for the authored investigations, the fact the case's reasoning rests on.
    """
    span = variants.code_span
    records = variants.load_records()
    rows = []
    for index, c in enumerate(s["cases"]):
        shown = snippet(c["code"])
        v = variants.variant(records, ident, index, c["code"], shown)
        spans = variants.checks(shown) or variants.checks(c["code"])
        cond = span(v["condition"] if v and v.get("condition") else spans[-1][2])
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
        obs = row["obs"]
        original = edited = None
        if v:
            original, edited = span(v["line"]), span(v["broken"])
        trace = _trace(v["condition"] if v and v.get("condition") else spans[-1][2])
        if index == 0:
            row["title"] = c["title"] + (
                ": predict an edited check" if v and v["in_check"] else ": change one input"
            )
            if v and v["in_check"]:
                row["task"] = (
                    f"In worked example 1, change {original} to {edited}. Predict whether the CHECK still holds and why, then run and restore."
                )
                row["expected"] = f"`Check failed`: {edited} is false, although {obs}."
                row["verify"] = (
                    f"Explain which claim {edited} makes that the state fails; restoring {original} passes again."
                )
            elif v:
                row["task"] = (
                    f"In worked example 1, change {original} to {edited}. Predict which value the CHECK on {cond} sees, then run and restore."
                )
                row["expected"] = f"`Check failed` at {cond}; restoring {original} passes again."
                row["verify"] = (
                    f"Name the value that made {cond} false, where worked example 1 showed that {obs}."
                )
            else:
                row["task"] = (
                    f"Rebuild worked example 1 in a fresh pad keeping the CHECK on {cond}; propose a defined input that makes it fail."
                )
                row["expected"] = (
                    f"Your rebuild passes ({obs}), and your proposed input makes {cond} fail."
                )
                row["verify"] = (
                    f"Name the value that made {cond} false, and keep the change defined."
                )
            then = (
                f"Then compute what the CHECK sees with {edited} in place."
                if v
                else f"Then name a defined input that makes {cond} false."
            )
        elif index == 1:
            row["title"] = c["title"] + (
                ": diagnose an edited check" if v and v["in_check"] else ": debug a regression"
            )
            if v and v["in_check"]:
                row["task"] = (
                    f"Worked example 2's CHECK now reads {edited}. Explain why it fails although {obs}, then restore it."
                )
                row["expected"] = (
                    f"`Check failed` until the CHECK reads {original} again, though {obs}."
                )
                row["verify"] = (
                    f"Explain why {edited} rejects a state that {cond} accepts, using your failing and repaired runs."
                )
            elif v:
                row["task"] = (
                    f"In worked example 2, {original} now reads {edited}. Repair it so that {obs} again."
                    if _occurs(v["broken"], rows[0]["shown"] + "\n" + shown)
                    else f"Worked example 2 now has a line reading {edited}. Repair it so that {obs} again."
                )
                row["expected"] = f"`Check failed` at {cond} until the line reads {original} again."
                row["verify"] = (
                    f"Explain how {edited} changes the value {cond} tests, using your failing and repaired runs."
                )
            else:
                row["task"] = (
                    f"Introduce one defined defect into worked example 2 that fails the CHECK on {cond}; trace it back, then repair it."
                )
                row["expected"] = (
                    f"The defective copy fails at {cond}; the repaired copy shows that {obs}."
                )
                row["verify"] = (
                    f"Explain how your defect changes the value {cond} tests, using your failing and repaired runs."
                )
            then = (
                f"Then compare {edited} with worked example 2's original line."
                if v
                else f"Then name a defined input that makes {cond} false."
            )
        else:
            if v and not v["in_check"]:
                row["verify"] = (
                    f"Keep a CHECK equivalent to {cond}. Control edit: changing {original} to {edited} must fail it; then restore it."
                )
            elif v:
                row["verify"] = (
                    f"Keep a CHECK equivalent to {cond}. Control edit: {edited} must fail; then restore it."
                )
            else:
                row["verify"] = (
                    f"Keep a CHECK equivalent to {cond} and name a defined input that would make it fail."
                )
            then = "Then recall: " + _first_sentence(c["why"])
        row["hints"] = f"{trace} {then}"
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


def lesson_prose(ident, s, rows, following):
    """Guide paragraphs that name this lesson's own cases, checks, storage and helpers."""
    n = [r["named"] for r in rows]
    terms = [_lower_first(name) for name, meaning in s["terms"]]
    helpers = _helpers(s["helper"])
    arrays = _arrays(s["cases"][0]["code"] + "\n" + s["cases"][1]["code"])
    extra = [h for h in s["headers"].split()]
    first, second = rows[0], rows[1]
    t0 = terms[0]
    headers = _join("`<" + h + ">`" for h in extra) if extra else ""
    if helpers and extra:
        layout = f"Beyond the standard headers, this reference includes {headers} and defines {_join(helpers)} above `main`."
    elif extra:
        layout = f"Beyond the standard headers, this reference includes {headers}; every case runs inside `main`."
    elif helpers:
        layout = f"This reference defines {_join(helpers)} above `main`; every case runs in its own block inside `main`."
    else:
        layout = "This reference has no helper functions; every case runs in its own block inside `main`."
    prediction = (
        f"Predict worked example 1: when you {_clause(s['cases'][0]['task'])}, the CHECK on {first['cond']} should see that {first['obs']}."
        f" For {n[1]}, predict that {second['obs']}."
        + (
            f" Write down the declared size of {_join(arrays)} before indexing it."
            if arrays
            else ""
        )
    )
    pitfalls = (
        PITFALLS[ident]
        + "\n\nGeneral diagnosis order and the pointer checklist: [Diagnose failures](../STUDY-GUIDE.md#diagnose-failures)."
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
    nextstep = onward
    return dict(
        layout=layout,
        prediction=prediction,
        pitfalls=pitfalls,
        selfcheck=selfcheck,
        nextstep=nextstep,
        terms=terms,
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
        how_to_run = "\n\n".join(
            part
            for part in (
                prose["layout"],
                "Classroom steps and the always-on `CHECK`: [Run a C lesson](../STUDY-GUIDE.md#run-a-c-lesson).",
                s["boundary"].strip(),
            )
            if part
        )
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

{how_to_run}

## Worked example / walkthrough

{examples}

## Prediction before execution

{prose["prediction"]}

## Exercises

How the hints, control edits and regressions below work: [Work an exercise](../STUDY-GUIDE.md#work-an-exercise).

{exercises}

## Common pitfalls and diagnosis

{prose["pitfalls"]}

## Self-check and retrieval

{prose["selfcheck"]}

## Next step and sources

{prose["nextstep"]}

[Primary reference for {_lower_first(s["title"])}]({s["source"]}), reviewed 2026-10-23.

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
        answers = f"# {ident}: explained solutions\n\n`{ident}_solution.c` assembles {rows[0]['named']} through {rows[5]['named']} in one `main.c`.\n\nCompare only after an attempt: [Compare and transfer](../STUDY-GUIDE.md#compare-and-transfer).\n\n## Mechanism and assumptions\n\n{s['model']}\n\n{s['anatomy']}\n\n"
        notes = REASONING.get(ident)
        if notes and len(notes["cases"]) != len(rows):
            raise ValueError(ident + " reasoning needs one entry per case")
        for i, r in enumerate(rows, 1):
            lead = f"The unchanged code is worked example {i}:\n\n" if i <= 2 else ""
            contract = "" if notes else f"**Verify:** {r['verify']}\n\n"
            answers += f"## Exercise {i}: {r['title']}\n\n{r['task']}\n\n{lead}```c\n{r['shown']}\n```\n\n**Expected:** {r['expected']}\n\n{contract}{r['why']}\n\n"
            if notes:
                answers += "".join(
                    f"**{label}.** {text}\n\n"
                    for label, text in zip(LABELS, notes["cases"][i - 1], strict=True)
                )
        answers += (
            "## After comparison\n\n" + (notes["transfer"] if notes else TRANSFER[ident]) + "\n"
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
