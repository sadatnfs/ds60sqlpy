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

SPECS = {}


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


def program(s, blocks):
    return (
        s["imports"]
        + "\n\npublic class Main {\n"
        + textwrap.indent(s["helper"], "    ")
        + "\n    public static void main(String[] args) throws Exception {\n"
        + textwrap.indent("\n\n".join(blocks), "        ")
        + "\n    }\n}\n"
    )


def _lower_first(text):
    """Lower-case an ordinary leading word, leaving identifiers such as Optional intact."""
    return text[:1].lower() + text[1:] if text[1:2].islower() else text


def _failure(v, condition):
    """How the qualified run fails, naming the assertion message when it is a plain literal."""
    message = v.get("message") if v else None
    if message and len(message) > 1 and message[0] == message[-1] == '"' and "\\" not in message:
        shown = variants.code_span("AssertionError: " + message[1:-1])
        return f"fails with {shown} from the assertion on {condition}"
    return f"fails with an `AssertionError` from the assertion on {condition}"


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

    Every Verify line and hint names the exercise's own assertion and, where recorded,
    a one-token edit that qualify_variants.py observed making that assertion fail.
    """
    span = variants.code_span
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
        expected = _lower_first(e["expected"])
        if v:
            original, edited = span(v["line"]), span(v["broken"])
            fail = _failure(v, cond)
        example = "Example A" if index == 0 else "Example B"
        if index == 0:
            row["title"] = e["title"] + (
                ": predict an edited check" if v and v["in_check"] else ": change one input"
            )
            if v and v["in_check"]:
                row["task"] = (
                    f"Copy Example A into a scratch `Main.java` and change {original} to {edited} inside its assertion. "
                    "Before running it with `java -ea Main`, predict whether the assertion still holds and explain why; then restore it."
                )
            elif v:
                row["task"] = (
                    f"Copy Example A into a scratch `Main.java` and change {original} to {edited}. "
                    "Before running it with `java -ea Main`, predict which assertion fails and which value it now sees; "
                    "then run it and restore the original line."
                )
            elif cond:
                row["task"] = (
                    f"Close Example A and rebuild it in a fresh `Main.java`, keeping the assertion on {cond}. "
                    "Then propose one input change that would make that assertion fail and explain why before trying it."
                )
            else:
                row["task"] = (
                    "Close Example A and rebuild it in a fresh `Main.java`. Then propose one input change that "
                    "would alter its observation and explain the new result before trying it."
                )
            if v:
                row["expected"] = (
                    f"The changed run {fail}. Restoring the original line brings back the worked observation: {expected}"
                )
                row["verify"] = (
                    "Compare your written prediction with the reported `AssertionError` and its stack-trace line, and "
                    + (
                        f"explain why the edited condition is false for the values that satisfy {cond}."
                        if v["in_check"]
                        else f"name the value that made {cond} false."
                    )
                    + " After restoring the line, the program completes without an `AssertionError` again."
                )
            else:
                row["expected"] = (
                    f"Your rebuild reproduces the worked observation ({expected.rstrip('.')})"
                    + (
                        f", and your proposed change makes the assertion on {cond} fail."
                        if cond
                        else ", and your proposed change alters it as you predicted."
                    )
                )
                row["verify"] = (
                    "Run the rebuild with `java -ea Main` first, then the changed copy, and keep both results. "
                    + (
                        f"Name the value that makes {cond} false in the changed copy."
                        if cond
                        else "Name the value that changed."
                    )
                )
        elif index == 1:
            row["title"] = e["title"] + (
                ": diagnose an edited check" if v and v["in_check"] else ": debug a regression"
            )
            if v and v["in_check"]:
                row["task"] = (
                    f"A careless edit changed the assertion that Example B adds after Example A so that it reads {edited}. "
                    "Run Example B with that line, explain why the edited assertion now fails for the same program state, and restore it."
                )
            elif v and _occurs(v["broken"], shown_codes[0] + "\n" + shown):
                row["task"] = (
                    f"A regression changed {original} to {edited} in the code that Example B adds after Example A. "
                    "Run Example B with that change, use the failing assertion to explain the defect and repair it without changing the assertion."
                )
            elif v:
                row["task"] = (
                    f"A regression changed one token in the code that Example B adds after Example A, so one line now reads {edited}. "
                    "Run Example B with that line, use the failing assertion to locate the defect and repair it without changing the assertion."
                )
            elif cond:
                row["task"] = (
                    f"Introduce one deliberate defect into a copy of Example B that makes the assertion on {cond} fail, "
                    "then explain how the stack trace leads back to the faulty statement."
                )
            else:
                row["task"] = (
                    "Introduce one deliberate defect into the code that Example B adds after Example A and explain "
                    "which observation exposes it, then repair it."
                )
            if v:
                row["expected"] = (
                    f"Before the repair the run {fail}; after it the line reads {original} again and {expected}"
                )
            else:
                row["expected"] = (
                    "The defective copy "
                    + (f"fails the assertion on {cond}" if cond else "changes the observation")
                    + f"; the repaired copy reproduces the worked observation: {expected}"
                )
            row["verify"] = (
                f"Keep the failing and the repaired runs. Explain why the edited assertion rejects the same program state that {cond} accepts."
                if v and v["in_check"]
                else f"Keep the failing and the repaired runs. Explain why the changed token alters the value tested by {cond} for this input."
                if v
                else "Keep the failing and the repaired runs and name the first statement whose value differs between them."
            )
        elif v and not v["in_check"]:
            row["verify"] = (
                f"Keep an assertion equivalent to {cond}. As a control, change {original} to {edited}: the run must "
                + fail.replace("fails with", "fail with", 1)
                + ". Restore the line before continuing."
            )
        elif v:
            row["verify"] = (
                f"Keep an assertion equivalent to {cond}. As a control, change {original} to {edited} inside it: "
                "the run must fail with an `AssertionError`, which shows the assertion can fail. Restore it."
            )
        elif cond:
            row["verify"] = (
                f"Keep an assertion equivalent to {cond} and confirm that `java -ea Main` completes. "
                "Then name an input that would make it fail and explain which value changes."
            )
        else:
            row["verify"] = (
                f"Run with `java -ea Main` and compare the observed values with: {expected} "
                "Then name an input that would change them."
            )
        if index == 0 and v:
            third = f"compute the asserted value with {edited} in place before running"
        elif index == 1 and v:
            third = f"compare {edited} with the same line in {example} and state the claim each version makes"
        elif v and not v["in_check"]:
            third = f"predict the effect of changing {original} to {edited} before running anything"
        elif cond:
            third = f"name one input that would make {cond} false"
        else:
            third = "name one input that would change the observation"
        row["hints"] = (
            f"First restate the expected observation: {expected} "
            + (
                f"Then list the values read by {cond} and trace each one from its declaration"
                if cond
                else "Then trace each value from its declaration to the observation"
            )
            + f". Finally, {third}."
        )
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
        outcome = OUTCOMES[id]
        if (
            outcome.lower().startswith("explain and implement")
            or outcome == s["mental"].split(".")[0] + "."
        ):
            raise ValueError(id + " needs a specific outcome")
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

{outcome} Along the way, explain {", ".join(k.lower() for k, v in s["terms"])} using a concrete program. Trace the normal execution, identify its boundary assumptions and make a failure case observable. Exercises 1 and 2 start from the worked examples; the authored investigations begin with this task: {s["exercises"][2]["prompt"]} The final exercise transfers the mechanism to {s["exercises"][-1]["title"].lower()}.

## Purpose and mental model

{s["mental"]}

## Vocabulary and concepts

{terms}

## How to run this lesson

Open the Docker classroom, choose the prepared Java 21 profile and save a learner pad. The pad is compiled as `Main.java` with `javac --release 21` and executed with `java -ea Main`. Assertions are enabled deliberately. A successful assertion has no output; a failed assertion throws `AssertionError` and the process should fail. Do not remove assertions to obtain a green result.

For a prepared native JDK, copy a worked example into your own `Main.java` under ignored `.learning/expansion/{id}/`. From that directory run the same two commands on PowerShell, macOS or Linux:

```text
javac --release 21 Main.java
java -ea Main
```

The public class name and source filename must agree. Each worked example below is a complete file. Example B includes the setup it needs from Example A, so it can be compiled by itself. The six exercise reference blocks form one complete program in the separate solution. Keep your original prediction, source and diagnostic text together. Most examples use prepared JDK libraries and tiny local fixtures; any additional dependency is specified in the lesson notes below. Any lesson-specific library or additional file is named explicitly; do not download packages from inside a learner program. Resource examples close their owned files, executors or loopback servers.

{s.get("run_notes", "")}

## Syntax anatomy and execution trace

{s["anatomy"]}

## Worked example / walkthrough

{examples}

## Prediction before your attempt

Read the source from the entry point and name each value before executing it. Identify which operations create new values, which mutate existing state and which can fail. Predict the first observable output or assertion result. For a compile-time failure, explain which source rule is violated before discussing runtime state: a program that did not compile never reached its main method. Keep normal, boundary and invalid inputs separate so each check has a clear purpose.

## Exercises

{exercises}

## Common pitfalls and diagnosis

When a check fails, keep the smallest source file that still demonstrates the failure. Read the first relevant compiler diagnostic before editing several lines; later diagnostics can be consequences of the same missing delimiter or wrong type. For a runtime exception, identify the first frame belonging to your code and compare its input with the method contract. For an assertion failure, inspect the actual value and the independent expected value. A passing process exit is weaker than a checked invariant, and a checked invariant applies only under its stated assumptions.

Do not replace a precise exception with a catch-all that returns a plausible default. That can hide an invalid input or an unfinished operation. If an example owns a resource, verify its lifetime on both the success and failure paths. If an operation is concurrent, use ordering primitives to establish the relationship you need; an observed timing coincidence is not a synchronization guarantee. The solution explanations identify the specific alternative that would break each exercise.

## Progressive hints

Read one hint at a time and attempt the exercise again before reading the next. Keep a small table of input, expected value, actual value and exception type. Ask for one hint about the first incorrect assumption before requesting the entire reference implementation.

{hints}

## Self-check and retrieval

Close the solution and explain {", ".join(k for k, v in s["terms"][:3])} in your own words. Reconstruct one example from a blank `Main.java`, then add a new boundary input. Explain why the new case should pass or fail before compiling it. Identify a situation where this technique is appropriate and one where a different data structure, lifetime policy or abstraction would be clearer. This is a reasoning check, not a memorization test for an API spelling.

## Next step

Preserve the saved pad and the six exercise observations. Continue to the next lesson only when you can explain the invariants without reading the answer. Later chapters reuse these contracts in larger programs, so keep a failing counterexample as well as a repaired result. A reference implementation demonstrates one valid design under the stated assumptions; it is not a universal design rule.

## Sources and verification status

[Official Java 21 API or language reference]({s["source"]}), reviewed 2026-10-22. Examples and exercise fixtures are original course material. Use the [validation guide](../../../docs/validation.md) and CI artifacts for the exact revision and platform to inspect actual compile/run results. Authoring, parsing, compilation, execution and learner mastery are separate forms of evidence.

## Ask an AI tutor about this lesson

```text
{prompt}
```
"""
        explanation_text = f"""# {id}: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

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
        explanation_text += """## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.
"""
        for path, text in [
            (guide, guide_text),
            (solution, program(s, code_blocks)),
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
