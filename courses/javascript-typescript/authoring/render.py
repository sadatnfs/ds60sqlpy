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
from guidance import GUIDANCE  # noqa: E402

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


IMPORT = re.compile(r"^import\s+(type\s+)?\{([^}]*)\}\s+from\s+(['\"][^'\"]+['\"]);?$")


def used_imports(imports, body):
    """Drop named import specifiers that a standalone worked example never references."""
    kept = []
    for line in imports.splitlines():
        match = IMPORT.match(line.strip())
        if not match:
            kept.append(line)
            continue
        names = [n.strip() for n in match.group(2).split(",") if n.strip()]
        used = [
            n for n in names if re.search(rf"(?<![\w$.]){re.escape(n.split()[-1])}(?![\w$])", body)
        ]
        if used:
            kept.append(
                f"import {match.group(1) or ''}{{ {', '.join(used)} }} from {match.group(3)};"
            )
    return "\n".join(kept)


def program(spec, blocks, reference=True, typed=False):
    signature = ": Promise<{ checks: number; status: string }>" if typed else ""
    imports = (
        spec["imports"]
        if reference
        else used_imports(spec["imports"], spec["helper"] + "\n" + "\n".join(blocks))
    )
    result = imports + "\n\n" + spec["helper"] + "\n\n"
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


def _first_sentence(text):
    """The opening sentence of an example's explanation, used as the rule a check exercises."""
    return re.split(r"(?<=[.!?])\s+(?=[A-Z`(])", text.strip(), maxsplit=1)[0]


def reading_practice(spec):
    """Browser reading lessons: no Node runtime, so practice is phrased as browser observations."""
    rows = []
    for index, e in enumerate(spec["exercises"]):
        expected = _lower_first(e["expected"])
        why_first = _first_sentence(e["why"])
        row = {"title": e["title"], "task": e["prompt"], "expected": e["expected"]}
        if index == 0:
            row["title"] = e["title"] + ": change one input"
            row["task"] = (
                f"{e['prompt']} Then change one attribute, label or handler in your copy and predict the "
                "visible difference before reloading."
            )
            row["expected"] = (
                f"The rebuild reproduces the observation: {expected} The changed copy differs as you predicted."
            )
            row["verify"] = f"Record the browser observation, then explain it: {why_first}"
        elif index == 1:
            row["title"] = e["title"] + ": debug a regression"
            row["task"] = (
                f"{e['prompt']} Then break one selector or attribute in a copy, predict which behavior exposes "
                "it, and repair it."
            )
            row["expected"] = (
                f"The broken copy no longer shows that {expected} The repair restores it."
            )
            row["verify"] = (
                f"Record the first browser observation that differed, then explain the repair: {why_first}"
            )
        else:
            row["verify"] = (
                f"Record the browser observation that shows it, then explain why: {why_first}"
            )
        row["hints"] = (
            f"{why_first} Inspect the elements and listeners involved in the browser's developer tools."
        )
        rows.append(row)
    return rows


def _guard(code, condition):
    """The whole `if (...) check` statement when a check only runs under a guard."""
    head = " ".join(condition.split())[:40]
    for line in code.splitlines():
        text = line.strip()
        if text.startswith("if (") and head in " ".join(text.split()):
            return text.rstrip(";")
    return None


def practice(ident, spec, typed, language, path):
    """Six exercises: two derived from the worked examples, four authored investigations.

    Every Verify line and hint names the exercise's own check and, where recorded, a
    one-token edit that qualify_variants.py observed making that check fail. The shared
    edit-predict-restore routine is explained once in ../STUDY-GUIDE.md.
    """
    span = variants.code_span
    records = variants.load_records()
    shown_codes = formatted_codes(spec, path, language)
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
        why_first = _first_sentence(e["why"])
        row = {"title": e["title"], "task": e["prompt"], "expected": e["expected"]}
        if v:
            original, edited = span(v["line"]), span(v["broken"])
            fail = f"fails with an `AssertionError` at {edited if v['in_check'] else cond}"
        if index == 0:
            row["title"] = e["title"] + (
                ": predict an edited check" if v and v["in_check"] else ": change one input"
            )
            if v and v["in_check"]:
                row["task"] = (
                    f"In a scratch copy of Example A, change {original} to {edited} inside its check. "
                    "Does the check still pass?"
                )
            elif v:
                row["task"] = (
                    f"In a scratch copy of Example A, change {original} to {edited}. Which check fails, "
                    "and what value does it see?"
                )
            else:
                row["task"] = (
                    f"Rebuild Example A from memory, keeping the check {cond}, then propose one input "
                    "change that should make it fail."
                )
            if v:
                row["expected"] = (
                    f"The edited run {fail}. Restoring {original} brings back: {expected}"
                )
                row["verify"] = (
                    f"{why_first} Use that rule to account for the actual and expected values in the "
                    "`AssertionError`."
                )
                row["verify_solution"] = (
                    f"Compare the reported actual and expected values with your prediction, then restore {original}."
                )
            else:
                row["expected"] = (
                    f"The rebuild reproduces: {expected} Your proposed change makes {cond} fail."
                )
                row["verify"] = (
                    f"{why_first} Name the value that makes {cond} fail in your changed copy."
                )
                row["verify_solution"] = (
                    f"Name the value that makes {cond} fail in your changed copy."
                )
        elif index == 1:
            row["title"] = e["title"] + (
                ": diagnose an edited check" if v and v["in_check"] else ": debug a regression"
            )
            if v and v["in_check"]:
                row["task"] = (
                    f"Example B's check was edited to read {edited}. Run it, explain the failure and "
                    "restore the original."
                )
            elif v and _occurs(v["broken"], shown):
                row["task"] = (
                    f"A regression changed {original} to {edited} in Example B. Repair it without "
                    "editing the check."
                )
            elif v:
                row["task"] = (
                    f"A regression made one Example B line read {edited}. Locate and repair it without "
                    "editing the check."
                )
            else:
                row["task"] = (
                    f"Break a copy of Example B so that {cond} fails, then trace the reported values "
                    "back to the faulty line."
                )
            row["expected"] = (
                f"Before the repair the run {fail}. Restoring {original} brings back: {expected}"
                if v
                else f"The broken copy fails {cond}; the repaired copy reproduces: {expected}"
            )
            row["verify"] = (
                f"{why_first} Keep the failing and repaired runs and compare the values each one reports."
            )
            row["verify_solution"] = (
                "Keep the failing and repaired runs and name the first value that differs between them."
            )
        elif v and not v["in_check"]:
            row["verify"] = (
                f"Keep {cond}. Control: changing {original} to {edited} must make that check fail; "
                "then restore it."
            )
        elif v:
            row["verify"] = (
                f"Keep {cond}. Control: editing it to {edited} must make the check fail; then restore it."
            )
        else:
            guard = _guard(shown, condition) if condition else None
            row["verify"] = (
                f"Keep the guarded check {span(guard)}; name an input that passes the guard but fails "
                "the check."
                if guard
                else f"Keep the check {cond}; name an input that would make it fail and the value that changes."
            )
        if index == 0:
            row["hints"] = (
                f"Compute the checked value with {edited} in place before running it."
                if v
                else f"Name one input that would make {cond} fail."
            )
        elif index == 1:
            row["hints"] = (
                f"Compare {edited} with the original line and state the claim each version makes."
                if v
                else "Trace the first value that differs between the failing and repaired runs."
            )
        else:
            row["hints"] = f"{why_first} Trace each value that {cond} reads."
        rows.append(row)
    return rows


SOURCE_LABELS = {
    "https://dom.spec.whatwg.org/": "DOM Standard",
    "https://html.spec.whatwg.org/multipage/webstorage.html": "HTML Standard: Web storage",
    "https://www.w3.org/TR/CSP3/": "Content Security Policy Level 3",
}


def _source_label(url):
    """A short link label naming the reference document."""
    if url in SOURCE_LABELS:
        return SOURCE_LABELS[url]
    stem = url.rstrip("/").rsplit("/", 1)[-1].removesuffix(".html").replace("_", " ")
    if "tc39.es" in url:
        return "ECMAScript specification"
    if "typescriptlang.org" in url:
        return f"TypeScript handbook: {stem.replace('-', ' ')}"
    return f"Node.js {stem} documentation"


def _modules(imports):
    """Inline list of the module specifiers a lesson imports."""
    names = dict.fromkeys(re.findall(r"from ['\"]([^'\"]+)['\"]", imports))
    return ", ".join(f"`{name}`" for name in names)


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
        guidance = GUIDANCE[identity]
        if reading:
            run = "Open the checked-in browser fixture described below ([browser lessons](../STUDY-GUIDE.md#browser-reading-lessons))."
        elif typed:
            run = f"Compile `main.mts`, then run `compiled/main.mjs` ([setup](../STUDY-GUIDE.md#running-typescript-lessons)).\n\nModules used: {_modules(spec['imports'])}."
        else:
            run = f"Run `node main.mjs` ([setup](../STUDY-GUIDE.md#running-node-lessons)).\n\nModules used: {_modules(spec['imports'])}."
        objectives = ", ".join(_lower_first(e["title"]) for e in spec["exercises"][:-1])
        objectives += ", and " + _lower_first(spec["exercises"][-1]["title"])
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

{outcome}

By the end you can {objectives}.

## Purpose and mental model

{spec["mental"]}

## Vocabulary and concepts

{terms}

## How to run this lesson

{run}

Save your copy under `.learning/expansion/{identity}/` ([saved copies](../STUDY-GUIDE.md#saved-copies-and-the-success-receipt)).

{spec["notes"]}

## Syntax anatomy and execution trace

{spec["anatomy"]}

## Worked example / walkthrough

{chr(10).join(examples)}

## Prediction before your attempt

{guidance["predict"]} ([Predicting before you run](../STUDY-GUIDE.md#predicting-before-you-run).)

## Exercises

{tasks}

## Common pitfalls and diagnosis

{guidance["pitfall"]} ([Diagnosing a failure](../STUDY-GUIDE.md#diagnosing-a-failure).)

## Progressive hints

Reveal one hint at a time ([using the hints](../STUDY-GUIDE.md#using-the-hints)).

{hints}

## Self-check and retrieval

{guidance["retrieve"]} ([Retrieval practice](../STUDY-GUIDE.md#retrieval-practice).)

## Sources and verification status

Reference: [{_source_label(spec["source"])}]({spec["source"]}).

Fixtures are original; see [sources and validation](../STUDY-GUIDE.md#sources-and-validation).

## Ask an AI tutor about this lesson

```text
{prompt}
```
"""
        answer = f"""# {identity}: explanatory solutions

Open these after your own attempt; each exercise runs in its own scope in the reference.

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

**Verify:** {r.get("verify_solution", r["verify"])}

"""
        answer += f"""## After comparison

{guidance["transfer"]} ([After comparing](../STUDY-GUIDE.md#after-comparing-with-the-solution).)
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
