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
from reasoning import LABELS, REASONING  # noqa: E402
from teaching import TEACHING  # noqa: E402

BASE = Path(__file__).resolve().parents[1]
SPECS = []
STUDY = "../STUDY-GUIDE.md"
SOURCE_LABELS = {
    "https://go.dev/ref/spec": "The Go Programming Language Specification",
    "https://go.dev/ref/spec#Channel_types": "Go specification: channel types",
    "https://go.dev/ref/mem": "The Go Memory Model",
    "https://go.dev/doc/tutorial/generics": "Go tutorial: getting started with generics",
    "https://go.dev/doc/modules/managing-dependencies": "Go modules: managing dependencies",
    "https://go.dev/doc/install/source#environment": "Go build environment variables",
    "https://go.dev/doc/effective_go#concurrency": "Effective Go: concurrency",
    "https://go.dev/doc/database/execute-transactions": "Go database guide: executing transactions",
    "https://github.com/kubernetes/client-go": "client-go repository",
    "https://github.com/kubernetes/client-go/tree/master/testing": "client-go testing package",
    "https://kubernetes.io/docs/concepts/architecture/controller/": "Kubernetes controllers",
    "https://kubernetes.io/docs/reference/using-api/api-concepts/#resource-versions": "Kubernetes API concepts: resource versions",
    "https://kubernetes.io/docs/reference/using-api/api-concepts/#efficient-detection-of-changes": "Kubernetes API concepts: efficient detection of changes",
    "https://kubernetes.io/docs/reference/access-authn-authz/rbac/": "Kubernetes RBAC authorization",
    "https://kubernetes.io/docs/reference/access-authn-authz/extensible-admission-controllers/": "Kubernetes dynamic admission control",
    "https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/": "Kubernetes labels and selectors",
    "https://kubernetes.io/docs/concepts/overview/working-with-objects/kubernetes-objects/": "Kubernetes objects",
    "https://kubernetes.io/docs/concepts/overview/working-with-objects/finalizers/": "Kubernetes finalizers",
}


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


def source_label(url):
    """A readable name for a primary-source link."""
    if url in SOURCE_LABELS:
        return SOURCE_LABELS[url]
    if url.startswith("https://pkg.go.dev/"):
        path = url.removeprefix("https://pkg.go.dev/").split("#", 1)[0]
        return f"`{path}` package documentation"
    raise ValueError("Add a label for source " + url)


def needed_helper(s, count):
    """The helper source, or nothing when none of the shown cases refers to it."""
    code = "\n".join(c["code"] for c in s["cases"][:count])
    names = re.findall(r"\b(?:func|type|var|const)\s+(?:\([^)]*\)\s*)?(\w+)", s["helper"])
    if any(re.search(r"\b" + re.escape(name) + r"\b", code) for name in names):
        return s["helper"]
    return ""


def program(s, count=6):
    helper = needed_helper(s, count)
    used = helper + "\n" + "\n".join(c["code"] for c in s["cases"][:count])
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
        + (helper + "\n\n" if helper else "")
        + "func main() {\n"
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


def _first_sentence(text):
    return re.split(r"(?<=[.!?])\s+", text.strip(), maxsplit=1)[0]


def practice(ident, s, nudges, steps):
    """Six exercises: two derived from the worked examples, four authored investigations.

    Expected and Verify lines are built from the case's own check and the one-token
    edit that qualify_variants.py observed making that check fail. The shared exercise
    contract and hint ladder are explained once in ../STUDY-GUIDE.md. The second hint
    of every exercise, and the third hint of the first two, are authored in teaching.py.
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
        observed = _lower_first(c["expected"])
        if index == 0:
            row["title"] = c["title"] + (
                ": predict an edited check" if v and v["in_check"] else ": change one input"
            )
            if v and v["in_check"]:
                row["task"] = (
                    f"Copy worked example 1, change {original} to {edited} inside its check and predict whether it still passes; then restore it."
                )
                row["expected"] = (
                    f"The edited check panics with {panic} even though {cond} still holds."
                )
            elif v:
                row["task"] = (
                    f"Copy worked example 1, change {original} to {edited} and predict the failure before running; then restore the line."
                )
                row["expected"] = (
                    f"The edited run panics with {panic} because {cond} no longer holds."
                )
            else:
                row["task"] = (
                    f"Copy worked example 1, then propose an input that makes {cond} false."
                )
                row["expected"] = (
                    f"The original input passes ({observed.rstrip('.')}); yours panics with {panic}."
                )
            row["verify"] = (
                f"Restoring {original} makes the check pass again with the worked observation: {observed}"
                if v
                else f"The check fails with message {panic} once {cond} is false; restoring the input makes it pass."
            )
        elif index == 1:
            row["title"] = c["title"] + (
                ": diagnose an edited check" if v and v["in_check"] else ": debug a regression"
            )
            if v and v["in_check"]:
                row["task"] = (
                    f"A careless edit rewrote the check in worked example 2 as {edited}. Explain the failure, then restore it."
                )
            elif v and _occurs(v["broken"], rows[0]["shown"] + "\n" + shown):
                row["task"] = (
                    f"A regression changed {original} to {edited} in worked example 2. Repair it without changing the check."
                )
            elif v:
                row["task"] = (
                    f"A one-token regression in worked example 2 makes a line read {edited}. Repair it without changing the check."
                )
            else:
                row["task"] = (
                    f"Break one line of worked example 2 so {cond} fails, then trace the panic back to it."
                )
            row["expected"] = (
                f"The defective run panics with {panic}; after restoring {original}, {observed}"
                if v
                else f"Your defect panics with {panic}; undoing it restores the worked observation: {observed}"
            )
            row["verify"] = (
                f"The edited check fails with message {panic} for a state that {cond} accepts."
                if v and v["in_check"]
                else f"The failing run shows message {panic}; after the repair {cond} holds again."
            )
        elif v:
            row["verify"] = (
                f"Your solution must keep {cond} true. Control: changing {original} to {edited} panics with message {panic}; revert it."
            )
        else:
            row["verify"] = (
                f"Your solution must keep {cond} true. Control: an input that falsifies it fails with message {panic}; revert it."
            )
        row["hints"] = [
            "Restate the expected observation: " + c["expected"],
            nudges[index],
            steps[index] if index < 2 else _first_sentence(c["explanation"]),
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
        teach = TEACHING[ident]
        notes = REASONING.get(ident)
        if len(teach["hints"]) != len(s["cases"]) or len(teach["steps"]) != 2:
            raise ValueError(ident + " needs six authored hints and two near-answer steps")
        if bool(notes) == ("transfer" in teach):
            raise ValueError(ident + " needs exactly one transfer, in reasoning.py or teaching.py")
        rows = practice(ident, s, teach["hints"], teach["steps"])
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
        if n < len(SPECS):
            next_step = (
                f"Next: go-{n + 1:03d}, {SPECS[n]['title']} ([criteria]({STUDY}#when-to-move-on))."
            )
        else:
            next_step = (
                f"This is the final Go lesson ([completion criteria]({STUDY}#when-to-move-on))."
            )
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

{s["boundary"] + chr(10) + chr(10) if s["boundary"] else ""}Run each worked example as one complete file in your saved pad ([run steps]({STUDY}#run-a-lesson)).

## Worked example / walkthrough

{examples}

## Predict before running

{teach["predict"]}

## Exercises

{exercises}

Work in the answer-free learner source, `{paths["starter"]}` ([exercise contract]({STUDY}#work-an-exercise)).

## Common pitfalls and diagnosis

{teach["pitfall"]}

General compiler, panic and error diagnosis is in the [study guide]({STUDY}#diagnose-a-failure).

## Progressive hints

{hints}

## Self-check and retrieval

{teach["retrieval"]}

The general [retrieval routine]({STUDY}#self-check-and-retrieval) still applies.

## Next step and sources

Source: [{source_label(s["source"])}]({s["source"]}), reviewed 2026-10-23.

{next_step}

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
        answers = f"# {ident}: explained solutions\n\nCompare after an attempt ([using solutions]({STUDY}#use-the-solutions)). `{paths['reference']}` implements all six cases.\n\n## Mechanism\n\n{s['model']}\n\n{s['anatomy']}\n\n"
        if notes and len(notes["cases"]) != len(rows):
            raise ValueError(ident + " reasoning needs one entry per case")
        for i, r in enumerate(rows, 1):
            lead = ""
            if i <= 2:
                lead = f"The unchanged code is worked example {i}:\n\n"
            answers += f"## {i}. {r['title']}\n\n{r['task']}\n\n{lead}```go\n{r['shown']}\n```\n\n**Expected:** {r['expected']}\n\n**Verify:** {r['verify']}\n\n{r['explanation']}\n\n"
            if notes:
                answers += "".join(
                    f"**{label}.** {text}\n\n"
                    for label, text in zip(LABELS, notes["cases"][i - 1], strict=True)
                )
        answers += (
            "## Transfer after comparison\n\n"
            + (notes["transfer"] if notes else teach["transfer"])
            + "\n"
        )
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
