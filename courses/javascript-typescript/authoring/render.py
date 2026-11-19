from pathlib import Path
import json
import re
import sys
import textwrap

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
    number,
    mental,
    anatomy,
    terms,
    exercises,
    helper="",
    imports="import { strict as assert } from 'node:assert';",
    source="https://nodejs.org/docs/latest-v24.x/api/",
    notes="",
):
    assert len(exercises) == 6
    SPECS[f"js-{number:03d}"] = dict(
        mental=mental,
        anatomy=anatomy,
        terms=terms,
        exercises=exercises,
        helper=textwrap.dedent(helper).strip(),
        imports=imports,
        source=source,
        notes=notes,
    )


def program(spec, blocks, reference=True, typed=False):
    signature = ": Promise<{ checks: number; status: string }>" if typed else ""
    result = spec["imports"] + "\n\n" + spec["helper"] + "\n\n"
    result += "export async function verify()" + signature + " {\n"
    for i, block in enumerate(blocks, 1):
        label = (
            f"Exercise {i}: {spec['exercises'][i - 1]['title']}" if reference else "Worked example"
        )
        result += f"  // {label}\n  {{\n" + textwrap.indent(block, "    ") + "\n  }\n\n"
    result += f'  return {{ checks: {len(blocks)}, status: "passed" }};\n}}\n'
    return result + "\nconsole.log(JSON.stringify(await verify()));\n"


def _lower_first(text):
    """Lower-case an ordinary leading word, leaving identifiers such as NaN intact."""
    return text[:1].lower() + text[1:] if text[1:2].islower() else text


def _occurs(excerpt, code):
    """Whether an edited excerpt already appears verbatim, which would make it ambiguous."""
    return " ".join(excerpt.split()) in " ".join(code.split())


def formatted_codes(spec, path, language):
    """The exercise snippets exactly as the canonical Markdown formatter prints them."""
    document = "".join(f"```{language}\n{e['code']}\n```\n\n" for e in spec["exercises"])
    text = canonical_markdown(document, root=ROOT, path=path)
    shown = re.findall(rf"^```{language}\n(.*?)^```$", text, re.S | re.M)
    if len(shown) != len(spec["exercises"]):
        return [e["code"] for e in spec["exercises"]]
    return [code.rstrip("\n") for code in shown]


def reading_practice(spec):
    """Browser reading lessons: no Node runtime, so practice is phrased as browser observations."""
    rows = []
    for index, e in enumerate(spec["exercises"]):
        expected = _lower_first(e["expected"])
        row = {"title": e["title"], "task": e["prompt"], "expected": e["expected"]}
        if index == 0:
            row["title"] = e["title"] + ": change one input"
            row["task"] = (
                "Rebuild Example A in your copy of the lesson's browser fixture without looking at it. Then change one "
                "attribute, label or handler and write down the visible, focus or announcement change you expect "
                "before reloading."
            )
            row["expected"] = (
                f"Your rebuild reproduces the worked observation ({expected.rstrip('.')}), and the changed copy shows the "
                "difference you predicted."
            )
            row["verify"] = (
                "Record the browser observation before and after your change, including where focus lands and any "
                "live-region text, and explain which line caused the difference."
            )
        elif index == 1:
            row["title"] = e["title"] + ": debug a regression"
            row["task"] = (
                "Introduce one deliberate defect into a copy of Example B, such as a wrong selector, a missing attribute or a handler on the wrong element. Predict which browser behavior will expose it, confirm that prediction, then repair it."
            )
            row["expected"] = (
                f"The defective copy no longer shows: {expected} The repaired copy shows it again."
            )
            row["verify"] = (
                "Keep notes on the failing and the repaired behavior and name the first browser observation that "
                "differed between them."
            )
        else:
            row["verify"] = (
                f"In the browser fixture, record the observation that shows: {expected} Then change one input and "
                "record what changes, keeping keyboard and pointer results separate."
            )
        row["hints"] = (
            f"First restate the expected observation: {expected} Then inspect the elements, attributes and listeners "
            "involved in the browser's developer tools. Finally, change one thing at a time and reload before changing "
            "another."
        )
        rows.append(row)
    return rows


def practice(ident, spec, typed, language, path):
    """Six exercises: two derived from the worked examples, four authored investigations.

    Every Verify line and hint names the exercise's own check and, where recorded, a
    one-token edit that qualify_variants.py observed making that check fail.
    """
    span = variants.code_span
    records = variants.load_records()
    shown_codes = formatted_codes(spec, path, language)
    pad = "`main.mts`" if typed else "`main.mjs`"
    receipt = '`{"checks":1,"status":"passed"}`'
    rows = []
    for index, e in enumerate(spec["exercises"]):
        shown = shown_codes[index]
        if len(variants.checks(shown)) != len(variants.checks(e["code"])):
            shown = e["code"]
        v = variants.variant(records, ident, index, e["code"], shown)
        spans = variants.checks(shown)
        condition = v["condition"] if v and v.get("condition") else spans[-1][2] if spans else None
        cond = span(condition) if condition else None
        expected = _lower_first(e["expected"])
        row = {"title": e["title"], "task": e["prompt"], "expected": e["expected"]}
        if v:
            original, edited = span(v["line"]), span(v["broken"])
            fail = f"fails with an `AssertionError` at the check {cond}"
        if index == 0:
            row["title"] = e["title"] + (
                ": predict an edited check" if v and v["in_check"] else ": change one input"
            )
            if v and v["in_check"]:
                row["task"] = (
                    f"Copy Example A into a scratch {pad} and change {original} to {edited} inside its check. "
                    "Before running it, predict whether the check still passes and explain why; then restore it."
                )
            elif v:
                row["task"] = (
                    f"Copy Example A into a scratch {pad} and change {original} to {edited}. Before running it, "
                    "predict which check fails and which value it now sees; then run it and restore the original line."
                )
            else:
                row["task"] = (
                    f"Close Example A and rebuild it in a fresh {pad}, keeping the check {cond}. Then propose one "
                    "input change that would make that check fail and explain why before trying it."
                )
            if v:
                row["expected"] = (
                    f"The changed run {fail}. Restoring the original line brings back the worked observation: {expected}"
                )
                row["verify"] = (
                    "Compare your written prediction with the reported `AssertionError`, including its actual and "
                    "expected values, and "
                    + (
                        f"explain why the edited check rejects the values that {cond} accepts."
                        if v["in_check"]
                        else f"name the value that made {cond} fail."
                    )
                    + f" After restoring the line, the program prints its {receipt} receipt again."
                )
            else:
                row["expected"] = (
                    f"Your rebuild reproduces the worked observation ({expected.rstrip('.')}), and your proposed "
                    f"change makes the check {cond} fail."
                )
                row["verify"] = (
                    f"Run the rebuild first and confirm the {receipt} receipt, then the changed copy. Name the value "
                    f"that makes {cond} fail in the changed copy."
                )
        elif index == 1:
            row["title"] = e["title"] + (
                ": diagnose an edited check" if v and v["in_check"] else ": debug a regression"
            )
            if v and v["in_check"]:
                row["task"] = (
                    f"A careless edit changed a check in Example B so that it reads {edited}. Run Example B with that "
                    "line, explain why the edited check now fails for the same program state, and restore it."
                )
            elif v and _occurs(v["broken"], shown):
                row["task"] = (
                    f"A regression changed {original} to {edited} in Example B. Run Example B with that change, use the "
                    "failing check to explain the defect and repair it without changing the check."
                )
            elif v:
                row["task"] = (
                    f"A regression changed one token in Example B, so one line now reads {edited}. Run Example B with "
                    "that line, use the failing check to locate the defect and repair it without changing the check."
                )
            else:
                row["task"] = (
                    f"Introduce one deliberate defect into a copy of Example B that makes the check {cond} fail, then "
                    "explain how the reported actual and expected values lead back to the faulty line."
                )
            row["expected"] = (
                f"Before the repair the run {fail}; after it the line reads {original} again and {expected}"
                if v
                else f"The defective copy fails the check {cond}; the repaired copy reproduces the worked observation: {expected}"
            )
            row["verify"] = (
                f"Keep the failing and the repaired runs. Explain why the edited check rejects the same program state that {cond} accepts."
                if v and v["in_check"]
                else f"Keep the failing and the repaired runs. Explain why the changed token alters the value tested by {cond} for this input."
                if v
                else "Keep the failing and the repaired runs and name the first value that differs between them."
            )
        elif v and not v["in_check"]:
            row["verify"] = (
                f"Keep a check equivalent to {cond}. As a control, change {original} to {edited}: the run must fail "
                "with an `AssertionError` at that check. Restore the line before continuing."
            )
        elif v:
            row["verify"] = (
                f"Keep a check equivalent to {cond}. As a control, change {original} to {edited} inside it: the run "
                "must fail with an `AssertionError`, which shows the check can fail. Restore it."
            )
        else:
            row["verify"] = (
                f"Keep a check equivalent to {cond} and confirm that the reference still passes. Then name an input "
                "that would make it fail and explain which value changes."
            )
        if index == 0 and v:
            third = f"compute the checked value with {edited} in place before running"
        elif index == 1 and v:
            third = f"compare {edited} with the same line in Example B and state the claim each version makes"
        elif v and not v["in_check"]:
            third = f"predict the effect of changing {original} to {edited} before running anything"
        else:
            third = f"name one input that would make {cond} fail"
        row["hints"] = (
            f"First restate the expected observation: {expected} Then list the values read by {cond} and trace each "
            f"one from its declaration. Finally, {third}."
        )
        rows.append(row)
    return rows


def write_all():
    base = ROOT / "courses/javascript-typescript"
    plan = json.loads((base / "track.json").read_text())
    manifest = json.loads((base / "lessons.json").read_text())
    existing = {e["id"] for e in manifest["lessons"]}
    for folder in ("guides", "lessons", "solutions", "fixtures", "authoring"):
        (base / folder).mkdir(exist_ok=True)
    for row in plan["lessons"]:
        identity = row["id"]
        if identity not in SPECS:
            continue
        spec = SPECS[identity]
        reading = row["runtime"] == "reading"
        typed = row["runtime"] == "typescript-node"
        suffix = "md" if reading else "mts" if typed else "mjs"
        language = "markdown" if reading else "typescript" if typed else "javascript"
        guide = f"courses/javascript-typescript/guides/{identity}.md"
        learner = f"courses/javascript-typescript/lessons/{identity}.{suffix}"
        solution = f"courses/javascript-typescript/solutions/{identity}_solution.{suffix}"
        explanation = f"courses/javascript-typescript/solutions/{identity}_solutions.md"
        prerequisites = (
            ", ".join("`" + p + "`" for p in row["prerequisites"])
            or "None. This lesson starts from the language and host distinction."
        )
        terms = "\n\n".join(f"**{name}:** {meaning}" for name, meaning in spec["terms"])
        rows = (
            reading_practice(spec)
            if reading
            else practice(identity, spec, typed, language, explanation)
        )
        tasks = "\n\n".join(
            f"{i}. **{r['title']}.** {r['task']}\n   **Expected:** {r['expected']}\n   **Verify:** {r['verify']}"
            for i, r in enumerate(rows, 1)
        )
        hints = "\n".join(f"- **Exercise {i}:** {r['hints']}" for i, r in enumerate(rows, 1))
        outcome = OUTCOMES[identity]
        if (
            outcome.lower().startswith("explain and implement")
            or outcome == spec["mental"].split(".")[0] + "."
        ):
            raise ValueError(identity + " needs a specific outcome")
        examples = []
        for i, e in enumerate(spec["exercises"][:2]):
            code = e["code"] if reading else program(spec, [e["code"]], False, typed)
            examples.append(
                f"### Example {chr(65 + i)}: {e['title']}\n\n{e['why']}\n\n```{'html' if reading else language}\n{code}\n```\n\n**Expected:** {e['expected']}"
            )
        if reading:
            run = "This is a browser reading and practice lesson. Node has no document or window. Use the separate checked-in browser fixture described below and record its visible interaction, focus and state changes. The manifest deliberately supplies no Node execution claim for these DOM examples."
        elif typed:
            run = "Use the prepared TypeScript 5.9.3 profile. The classroom saves main.mts, checks strict NodeNext resolution with noEmitOnError and an ES2022 target, then runs compiled/main.mjs on Node 24.22.3. Node typings 24.10.0 are prepared. Compilation and execution are separate stages. Types are erased and do not validate external JSON. No npm installation belongs inside the lesson."
        else:
            run = "Use the prepared Node 24.22.3 profile. The classroom saves an ES module as main.mjs and executes it with Node. Only built-in Node or ECMAScript APIs are used. For a prepared native environment, node main.mjs is the same command on PowerShell and POSIX. Browser APIs have separate host requirements."
        prompt = f"""Use $guide-ds60sqlpy-learning for {identity}: {row["title"]}.
Read {guide} and {learner}. Direct prerequisites: {prerequisites}.
Explain the mechanism, ask me to predict a value or failure, review my own attempt,
give one hint, request compile/runtime/browser evidence, and ask a fresh retrieval question.
Keep courses/javascript-typescript/solutions/ closed until I request comparison or show an attempt.
Done when I can explain the state and host contracts, pass all six exercise checks,
diagnose a controlled failure, and solve a new boundary case without copying the answer."""
        document = f"""# {identity}: {row["title"]}

## Level and prerequisites

{row["level"].capitalize()}, approximately {row["minutes"]} minutes. Direct prerequisites: {prerequisites}

## Learning objectives

{outcome} Along the way, explain {", ".join(name.lower() for name, _ in spec["terms"])} with a concrete program. Trace how the values change, identify the assumptions, and make a boundary or invalid case observable. Exercises 1 and 2 start from the worked examples; the authored investigations begin with this task: {spec["exercises"][2]["prompt"]} The final task tests {spec["exercises"][-1]["title"].lower()}.

## Purpose and mental model

{spec["mental"]}

## Vocabulary and concepts

{terms}

## How to run this lesson

{run}

Save your own learner copy under ignored `.learning/expansion/{identity}/` or use a saved classroom pad. Record predictions before execution. Each worked program includes its helper definitions. The reference puts the six exercises in separate scopes, so a task cannot silently rely on a variable from a previous task. A successful assertion is silent; the final JSON receipt reports how many exercise blocks completed. A failing assertion must produce a failed process, not a generic success message.

{spec["notes"]}

## Syntax anatomy and execution trace

{spec["anatomy"]}

## Worked example / walkthrough

{chr(10).join(examples)}

## Prediction before your attempt

Trace the entry point and identify the values that exist before each operation. Distinguish a value from a reference to an object, a returned Promise from its eventual result, and a compile-time type from a runtime check. Write down the first observation that would disprove your explanation. A useful prediction includes an expected value or failure category, not merely a claim that the program should work.

For a loop, write the state before and after one iteration. For a callback, identify the caller and the arguments it supplies. For an asynchronous operation, identify who starts it, who awaits it, and who owns cleanup. These small traces make failures local: you can compare the first incorrect state instead of guessing from a much later symptom.

## Exercises

{tasks}

## Common pitfalls and diagnosis

Keep the smallest fixture that distinguishes the intended behavior from a tempting alternative. Read the assertion message and inspect the input, return value and state at that point. Do not remove a failing check just to reach the success receipt. Preserve the original failure, repair the responsible assumption, then check the normal path and the negative case again.

If a host API is absent, confirm the actual host and version before changing the algorithm. A successful parse does not prove that an API exists. Compiler success does not prove that external data satisfies a type. A browser interaction requires browser evidence. For resource-owning examples, inspect cleanup after failure as carefully as the happy path. The separate explanations discuss the specific mistaken inference in each exercise.

## Progressive hints

Read one hint at a time and attempt the exercise again before reading the next. If a discrepancy involves scheduling, replace unrelated work with a small trace array and await the exact completion you intend to observe. Ask for one hint about the first incorrect assumption before opening the reference.

{hints}

## Self-check and retrieval

Close the solution and explain {", ".join(name for name, _ in spec["terms"][:3])} using the fixture. Reconstruct one example from a blank saved copy. Change a boundary input and predict the new result before running it. Explain the assumptions under which the mechanism is useful and a situation in which its cost or host requirements make another design preferable. A copied program is useful rehearsal; a fresh case demonstrates transfer.

## Sources and verification status

[Official language or host reference]({spec["source"]}). Fixtures and exercises are original course material. The [validation guide](../../../docs/validation.md) describes how the references are run. No default lesson installs dependencies, downloads a model or contacts a shared service.

## Ask an AI tutor about this lesson

```text
{prompt}
```
"""
        answer = f"""# {identity}: explanatory solutions

Use these answers after an attempt or an explicit reveal. The reference uses the same literal fixtures as the guide and keeps the exercises in separate scopes. A successful run checks these examples; explaining a changed input is a separate learning goal.

## Mechanism review

{spec["mental"]}

{terms}

## Reading the implementation

{spec["anatomy"]}

"""
        for i, (e, r) in enumerate(zip(spec["exercises"], rows, strict=True), 1):
            lead = (
                f"The unchanged code is the exercise block of Example {chr(64 + i)}:\n\n"
                if i <= 2
                else ""
            )
            answer += f"""## Exercise {i}: {r["title"]}

Task: {r["task"]}

{e["why"]}

{lead}```{"html" if reading else language}
{e["code"]}
```

**Expected:** {r["expected"]}

**Verify:** {r["verify"]}

"""
        answer += """## After comparison

Return to your saved implementation and repeat a case with different values. Keep compiler diagnostics, process output and browser observations separate. Do not suppress a failing assertion or use a type assertion to declare an unvalidated value safe. Resource-owning examples must finish cleanup even when work fails. Describe each result with its actual host and fixture scope rather than as production acceptance.
"""
        document = canonical_markdown(document, root=ROOT, path=guide)
        answer = canonical_markdown(answer, root=ROOT, path=explanation)
        (ROOT / guide).write_text(document)
        (ROOT / explanation).write_text(answer)
        if reading:
            (ROOT / learner).write_text(
                f"# {identity}: {row['title']}\n\nUse the browser fixture and record predictions before inspecting solutions.\n\n## Exercises\n\n"
                + tasks
                + "\n"
            )
        else:
            (ROOT / solution).write_text(
                program(spec, [e["code"] for e in spec["exercises"]], True, typed)
            )
            comments = []
            for i, r in enumerate(rows, 1):
                comments.append(
                    f"// Exercise {i}: {r['title']}\n"
                    + "\n".join("// " + line for line in textwrap.wrap(r["task"], 90))
                    + "".join(
                        "\n// " + line for line in textwrap.wrap("Expected: " + r["expected"], 90)
                    )
                )
            (ROOT / learner).write_text(
                "// Answer-free learner source. Save your own copy before editing.\n"
                + ("\nexport {};\n" if typed else "")
                + "\n\n".join(comments)
                + '\n\nconsole.log("Implement the six exercises in your saved copy.");\n'
            )
        if identity not in existing:
            manifest["lessons"].append(
                dict(
                    id=identity,
                    status="authored",
                    language=language,
                    runtime_profile=row["runtime"],
                    guide_path=guide,
                    source_path=learner,
                    solution_paths=[explanation] if reading else [solution, explanation],
                    verification_id=None,
                )
            )
        row["outcome"] = outcome
        row["lab"] = spec["exercises"][2]["prompt"]
        row["verification"] = spec["exercises"][2]["expected"]
        row["concepts"] = [name for name, _ in spec["terms"]]
    manifest["lessons"].sort(key=lambda e: e["id"])
    (base / "lessons.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (base / "track.json").write_text(json.dumps(plan, indent=2) + "\n")
    print("Authored JS/TS lessons:", len(SPECS))
