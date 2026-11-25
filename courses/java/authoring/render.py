import json
import re
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.format_inline_code import canonical_markdown  # noqa: E402

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import variants  # noqa: E402
from outcomes import OUTCOMES  # noqa: E402
from teaching import TEACHING  # noqa: E402

SPECS = {}
STUDY = "../STUDY-GUIDE.md"


def ex(title, prompt, expected, code, why):
    return dict(
        title=title, prompt=prompt, expected=expected, code=textwrap.dedent(code).strip(), why=why
    )


def add(
    n,
    mental,
    anatomy,
    terms,
    exercises,
    helper="",
    imports="import java.util.*;",
    source="https://docs.oracle.com/en/java/javase/21/docs/api/index.html",
    run_notes="",
):
    assert len(exercises) == 6
    SPECS[f"java-{n:03d}"] = dict(
        mental=mental,
        anatomy=anatomy,
        terms=terms,
        exercises=exercises,
        helper=textwrap.dedent(helper).strip(),
        imports=imports,
        source=source,
        run_notes=run_notes,
    )


def program(s, blocks, success=None):
    """Assemble Main.java; ``success`` appends one fixed stdout line after all checks."""
    final = "" if success is None else f'\n        System.out.println("{success}");'
    return (
        s["imports"]
        + "\n\npublic class Main {\n"
        + textwrap.indent(s["helper"], "    ")
        + "\n    public static void main(String[] args) throws Exception {\n"
        + textwrap.indent("\n\n".join(blocks), "        ")
        + final
        + "\n    }\n}\n"
    )


def _message(v):
    """The qualified run's assertion message as a code span, when it is a plain literal."""
    message = v.get("message") if v else None
    if message and len(message) > 1 and message[0] == message[-1] == '"' and "\\" not in message:
        return " with " + variants.code_span("AssertionError: " + message[1:-1])
    return ""


def _failure(v, condition):
    """How the qualified run fails, naming the assertion message when it is a plain literal."""
    return f"fails{_message(v) or ' with an `AssertionError`'} from the assertion on {condition}"


def _occurs(excerpt, code):
    """Whether an edited excerpt already appears verbatim, which would make it ambiguous."""
    return " ".join(excerpt.split()) in " ".join(code.split())


def formatted_codes(s, path):
    """The exercise snippets exactly as the canonical Markdown formatter prints them."""
    document = "".join(f"```java\n{e['code']}\n```\n\n" for e in s["exercises"])
    serialized = document.encode("utf-8", errors="backslashreplace").decode("utf-8")
    text = canonical_markdown(serialized, root=ROOT, path=path)
    shown = re.findall(r"^```java\n(.*?)^```$", text, re.S | re.M)
    if len(shown) != len(s["exercises"]):
        return [e["code"] for e in s["exercises"]]
    return [code.rstrip("\n") for code in shown]


def practice(ident, s):
    """Six exercises: two derived from the worked examples, four authored investigations.

    Every Verify line names the exercise's own assertion and, where recorded, a one-token
    edit that qualify_variants.py observed making that assertion fail. Hints are authored
    per lesson in teaching.py; the shared protocol lives in ../STUDY-GUIDE.md.
    """
    span = variants.code_span
    hints = TEACHING[ident]["hints"]
    records = variants.load_records()
    shown_codes = formatted_codes(s, f"courses/java/solutions/{ident}_solutions.md")
    rows = []
    for index, e in enumerate(s["exercises"]):
        shown = shown_codes[index]
        if len(variants.checks(shown)) != len(variants.checks(e["code"])):
            shown = e["code"]
        v = variants.variant(records, ident, index, e["code"], shown)
        spans = variants.checks(shown)
        condition = v["condition"] if v and v.get("condition") else spans[-1][2] if spans else None
        cond = span(condition) if condition else None
        row = {"title": e["title"], "task": e["prompt"], "expected": e["expected"]}
        if v:
            original, edited = span(v["line"]), span(v["broken"])
            fail = _failure(v, cond)
        if index == 0:
            row["title"] = e["title"] + (
                ": predict an edited check" if v and v["in_check"] else ": change one input"
            )
            if v and v["in_check"]:
                row["task"] = (
                    f"Change Example A's assertion to {edited}, predict whether it holds, then run and restore it."
                )
                row["verify"] = (
                    f"Explain why the edited assertion is false for the values that satisfy {cond}."
                )
            elif v:
                row["task"] = (
                    f"Change {original} to {edited} in Example A and predict which assertion fails and why."
                )
                row["verify"] = f"Name the value that makes {cond} false, then restore the line."
            else:
                row["task"] = (
                    "Rebuild Example A from memory and propose one input change that makes "
                    + (f"the assertion on {cond} fail." if cond else "its observation change.")
                )
                row["verify"] = (
                    "Name the value that differs between your rebuild and the changed copy."
                )
            row["expected"] = (
                f"The edited run {fail}."
                if v
                else "The rebuild passes and the changed copy fails as predicted."
            )
        elif index == 1:
            row["title"] = e["title"] + (
                ": diagnose an edited check" if v and v["in_check"] else ": debug a regression"
            )
            if v and v["in_check"]:
                row["task"] = (
                    f"Example B's new assertion was edited to {edited}. Explain why it fails for unchanged state and restore it."
                )
                row["verify"] = (
                    f"Explain why the edited assertion rejects the state that {cond} accepts."
                )
            elif v and _occurs(v["broken"], shown_codes[0] + "\n" + shown):
                row["task"] = (
                    f"A regression changed {original} to {edited} in Example B's new code. Repair it using the failing assertion."
                )
                row["verify"] = f"Explain how the changed token alters the value that {cond} tests."
            elif v:
                row["task"] = (
                    f"A regression in Example B's new code makes one line read {edited}. Repair it using the failing assertion."
                )
                row["verify"] = f"Explain how the changed token alters the value that {cond} tests."
            else:
                row["task"] = (
                    "Add one defect to Example B's new code that "
                    + (f"fails the assertion on {cond}," if cond else "changes its observation,")
                    + " then repair it."
                )
                row["verify"] = (
                    "Name the first statement whose value differs between the failing and repaired runs."
                )
            row["expected"] = (
                f"The unrepaired run {fail}; the repaired line reads {original}."
                if v and not v["in_check"]
                else f"The edited run {fail}; the restored assertion passes."
                if v
                else "The defective copy fails its assertion and the repaired copy passes."
            )
        elif v and not v["in_check"]:
            row["verify"] = (
                f"Control: changing {original} to {edited} must fail the assertion on {cond}"
                + _message(v)
                + "."
            )
        elif v:
            row["verify"] = (
                f"Control: changing {original} to {edited} inside the assertion must make it fail."
            )
        elif cond:
            row["verify"] = (
                f"Name an input that would make {cond} false and the value that changes."
            )
        else:
            row["verify"] = (
                "Compare the observed values with the expected result and name an input that would change them."
            )
        row["hints"] = hints[index]
        rows.append(row)
    return rows


def write_all():
    base = ROOT / "courses/java"
    plan = json.loads((base / "track.json").read_text())
    inventory = json.loads((base / "lessons.json").read_text())
    existing = {e["id"] for e in inventory["lessons"]}
    for p in plan["lessons"]:
        id = p["id"]
        if id not in SPECS:
            continue
        s = SPECS[id]
        guide = f"courses/java/guides/{id}.md"
        learner = f"courses/java/lessons/{id}.java"
        solution = f"courses/java/solutions/{id}_solution.java"
        explanation = f"courses/java/solutions/{id}_solutions.md"
        prereq = (
            ", ".join("`" + v + "`" for v in p["prerequisites"])
            or "None. This lesson starts from a plain text source file."
        )
        terms = "\n\n".join(f"**{k}:** {v}" for k, v in s["terms"])
        rows = practice(id, s)
        exercises = "\n\n".join(
            f"{i}. **{r['title']}.** {r['task']}\n   **Expected:** {r['expected']}\n   **Verify:** {r['verify']}"
            for i, r in enumerate(rows, 1)
        )
        hints = "\n".join(f"- **Exercise {i}:** {r['hints']}" for i, r in enumerate(rows, 1))
        t = TEACHING[id]
        outcome = OUTCOMES[id]
        if (
            outcome.lower().startswith("explain and implement")
            or outcome == s["mental"].split(".")[0] + "."
        ):
            raise ValueError(id + " needs a specific outcome")
        objectives = "\n".join(f"- {e['title']}." for e in s["exercises"])
        position = [q["id"] for q in plan["lessons"]].index(id)
        following = plan["lessons"][position + 1] if position + 1 < len(plan["lessons"]) else None
        next_step = (
            f"Continue with `{following['id']}`: {following['title']}."
            if following
            else "This is the last Java lesson; revisit any lesson whose contracts you cannot yet explain."
        )
        examples = "\n\n".join(
            f"### Example {chr(65 + i)}: {e['title']}\n\n{e['why']}\n\n```java\n{program(s, [x['code'] for x in s['exercises'][: i + 1]])}\n```\n\n**Expected:** {e['expected']}"
            for i, e in enumerate(s["exercises"][:2])
        )
        prompt = f"""Use $guide-ds60sqlpy-learning for {id}: {p["title"]}.
Read {guide} and {learner}. Direct prerequisites: {prereq}.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java 21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution."""
        guide_text = f"""# {id}: {p["title"]}

## Level and prerequisites

{p["level"].capitalize()}, approximately {p["minutes"]} minutes. Direct prerequisites: {prereq}

## Learning objectives

{outcome}

The six exercises practice these steps:

{objectives}

## Purpose and mental model

{s["mental"]}

## Vocabulary and concepts

{terms}

## How to run this lesson

{t["run"]}

Classroom and native JDK steps, the exercise controls and the hint routine are in the [Java study guide]({STUDY}).

{s.get("run_notes", "")}

## Syntax anatomy and execution trace

{s["anatomy"]}

## Worked example / walkthrough

{examples}

## Prediction before your attempt

{t["predict"]}

## Exercises

{exercises}

## Common pitfalls and diagnosis

{t["pitfalls"]}

General compiler, runtime and assertion triage: [diagnose a failure]({STUDY}#diagnose-a-failure).

## Progressive hints

Read one rung at a time, as described in [using hints]({STUDY}#use-hints-one-at-a-time).

{hints}

## Self-check and retrieval

{t["retrieval"]}

## Next step

{next_step} Keep your six observations; see [moving on]({STUDY}#move-to-the-next-lesson).

## Sources and verification status

[Official Java 21 API or language reference]({s["source"]}), reviewed 2026-10-22. Evidence levels: [sources and evidence]({STUDY}#sources-and-evidence).

## Ask an AI tutor about this lesson

```text
{prompt}
```
"""
        explanation_text = f"""# {id}: explanatory solutions

Open this after an attempt; see [using the solutions]({STUDY}#use-the-solutions).

## Mechanism review

{s["mental"]}

{terms}

## Reading the reference

{s["anatomy"]}

"""
        code_blocks = []
        for i, (e, r) in enumerate(zip(s["exercises"], rows, strict=True), 1):
            lead = (
                f"The unchanged code is the part that Example {chr(64 + i)} adds:\n\n"
                if i <= 2
                else ""
            )
            explanation_text += f"""## Exercise {i}: {r["title"]}

Task: {r["task"]}

{e["why"]}

{lead}```java
{e["code"]}
```

**Expected:** {r["expected"]}

**Verify:** {r["verify"]}

"""
            code_blocks.append(f"// Exercise {i}: {e['title']}\n" + e["code"])
        explanation_text += f"""## After comparing the answer

{t["after"]}

Run the complete reference with `java -ea Main` first; the [review routine]({STUDY}#use-the-solutions) covers the rest.
"""
        for path, text in [
            (guide, guide_text),
            (solution, program(s, code_blocks, s.get("success"))),
            (explanation, explanation_text),
        ]:
            if path.endswith(".md"):
                # Match the existing output encoding before guarding Java literals.
                # Python surrogate units were already written as Java escapes.
                serialized = text.encode("utf-8", errors="backslashreplace").decode("utf-8")
                text = canonical_markdown(serialized, root=ROOT, path=path)
            target = ROOT / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding="utf-8", errors="backslashreplace")
        comments = []
        for i, r in enumerate(rows, 1):
            comments.append(
                f"// Exercise {i}: {r['title']}\n"
                + "\n".join("// " + line for line in textwrap.wrap(r["task"], 90))
                + "".join(
                    "\n// " + line for line in textwrap.wrap("Expected: " + r["expected"], 90)
                )
            )
        (ROOT / learner).parent.mkdir(parents=True, exist_ok=True)
        (ROOT / learner).write_text(
            """// Answer-free learner worksheet. Save your own Main.java before editing.
public class Main {
    public static void main(String[] args) throws Exception {
"""
            + textwrap.indent("\n\n".join(comments), "        ")
            + '\n        System.out.println("Implement and check the six exercises in your saved copy.");\n    }\n}\n'
        )
        if id not in existing:
            inventory["lessons"].append(
                dict(
                    id=id,
                    status="authored",
                    language="java",
                    runtime_profile="java21",
                    guide_path=guide,
                    source_path=learner,
                    solution_paths=[solution, explanation],
                    verification_id=None,
                )
            )
        p["outcome"] = outcome
        p["lab"] = s["exercises"][2]["prompt"]
        p["verification"] = s["exercises"][2]["expected"]
    missing = set(OUTCOMES) ^ {p["id"] for p in plan["lessons"] if p["id"] in SPECS}
    if missing:
        raise ValueError("outcomes.py and the lesson list differ: " + ", ".join(sorted(missing)))
    inventory["lessons"].sort(key=lambda e: e["id"])
    (base / "lessons.json").write_text(json.dumps(inventory, indent=2) + "\n")
    (base / "track.json").write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n")
    print("Authored Java lessons:", len(SPECS))
