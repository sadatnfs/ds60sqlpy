from pathlib import Path
import json, textwrap, re
import sys

ROOT = Path(__file__).resolve().parents[3]
SOURCE_ROOT = ROOT
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))
from outcomes import OUTCOMES  # noqa: E402

from scripts.format_inline_code import canonical_markdown  # noqa: E402

SPECS = {}
GUIDES_ONLY = False


def ex(title, prompt, expected, code, why):
    return dict(
        title=title, prompt=prompt, expected=expected, code=textwrap.dedent(code).strip(), why=why
    )


def add(
    id,
    mental,
    anatomy,
    terms,
    exercises,
    source,
    imports="import numpy as np",
    helper="",
    decisions="",
):
    assert len(exercises) == 6, id
    SPECS[id] = dict(
        mental=mental,
        anatomy=anatomy,
        terms=terms,
        exercises=exercises,
        source=source,
        imports=imports,
        helper=textwrap.dedent(helper).strip(),
        decisions=decisions,
    )


def polish(value):
    value = re.sub(r",(?=\S)", ", ", value)
    value = re.sub(r";(?=\S)", "; ", value)
    value = re.sub(
        r"\b(with|of|by|rank|alpha|beta|size|overlap|budget|reserve|lengths|visits|purchases|version|seed|steps|count|value|rate)(?=\d)",
        r"\1 ",
        value,
    )
    value = re.sub(
        r"(?<=\d)(?=records|steps|tokens|bytes|updates|entries|documents|times|characters)",
        " ",
        value,
    )
    return value


def polish_textbook_prose(document):
    def clean(part):
        def number_boundary(match):
            word, number = match.groups()
            if word.lower() in {
                "float",
                "int",
                "uint",
                "complex",
                "sha",
                "utf",
                "bm",
                "nf",
                "smollm",
                "fp",
                "bf",
                "tf",
                "log",
                "expm",
                "conv",
                "batchnorm",
                "layernorm",
                "maxpool",
                "normalfloat",
                "arm",
                "amd",
            }:
                return word + number
            return word + " " + number

        for old, new in {
            "authorized source with stale=False admission": "authorized source with fresh=False",
            "withk100": "with k=100",
            "withk5": "with k=5",
            "withrequires_gradTrue": "with requires_grad=True",
            "onlyparameters": "only parameters",
            "withLoRAHead": "with LoRAHead",
            "under_no_grad": "under no_grad",
            "underno_grad": "under no_grad",
            "itsstate_dict": "its state_dict",
            "usesmodel.eval": "uses model.eval",
            "andtorch.no_grad": "and torch.no_grad",
            "losslog2": "loss log(2)",
            "belowlog2": "below log(2)",
            "atlearningrate.01": "at learning rate 0.01",
            "TakeSGD.2": "Take SGD at 0.2",
            "SGD.5": "SGD at 0.5",
            "SGD.2": "SGD at 0.2",
            "oneSGD": "one SGD",
            "andGPU": "and GPU",
            "atleast": "at least",
            "classicalstandalone": "classical standalone",
            "containsstatus": "contains status",
            "andcitations": "and citations",
            "includesdocument_id": "includes document_id",
            "returnstatusunknown": "return status unknown",
            "statusanswered": "status answered",
            "statusunknown": "status unknown",
            "reasonmissing": "reason missing",
            "returnsFalse": "returns False",
            "returnNone": "return None",
            "recallNone": "recall None",
            "abstentionTrue": "abstention True",
            "correctTrue": "correct True",
            "supportedFalse": "supported False",
            "decisionFalse": "decision False",
            "preferenceTrue": "preference True",
            "source_supportedFalse": "source_supported False",
            "explicitlyFalse": "explicitly False",
            "freshTrue": "fresh True",
            "admissionFalse": "admission False",
            "reasonstale": "reason stale",
            "authorizedTrue": "authorized True",
            "withfreshFalse": "with fresh=False",
            "usedbefore": "used before",
            "exactlyoperation": "exactly operation",
            "andvalue": "and value",
            "aregroup_mean": "are group_mean",
            "haveid": "have id",
            "Rejectbool": "Reject bool",
            "anint": "an int",
            "containinggroup": "containing group",
            "perquery": "per query",
            "pergroup": "per group",
            "anddocuments": "and documents",
            "withpositive": "with positive",
            "oflength": "of length",
            "answerlength": "answer length",
            "samelabels": "same labels",
            "andloss": "and loss",
            "scaled bybeta": "scaled by beta",
            "andbeta": "and beta",
            "Atzero": "At zero",
            "atzero": "at zero",
            "onlineRL": "online RL",
            "orRLHF": "or RLHF",
            "updatesTrue": "updates True",
            "encoderFalse": "encoder False",
            "updateTrue": "update True",
            "trainedFalse": "trained False",
            "online_rlFalse": "online_rl False",
            "65, 536": "65,536",
            "16, 777, 216": "16,777,216",
            "pretrained executionunverified": "this hypothetical learner run remains unverified",
            "pretrained execution unverified": "this hypothetical learner run remains unverified",
            "notNF4": "not NF4",
            "fromNF4": "from NF4",
            "quantizationNF4": "quantization NF4",
            "distribution-awareNF4": "distribution-aware NF4",
            "tofloat32": "to float32",
            "oneuint8": "one uint8",
            "fourint8": "four int8",
            "Reconstructfloat32weights": "Reconstruct float32 weights",
            "plusonefloat32scale": "plus one float32 scale",
            "dequantizedbuffer": "dequantized buffer",
            "a2x2": "a 2-by-2",
            "a4-bit": "a 4-bit",
            "a16-byte": "a 16-byte",
            "a20-entry": "a 20-entry",
            "a90%": "a 90%",
            "arek1": "are k1",
            "querytermq": "query term q",
            "usesidf": "uses idf",
            "multipliesidf": "multiplies idf",
            "bytf": "by tf",
            "ofsize": "of size",
            "bysize": "by size",
            "recordsdocument_id": "records document_id",
        }.items():
            part = part.replace(old, new)
        part = re.sub(r"\b([A-Za-z]{2,})(\d+)", number_boundary, part)
        part = re.sub(
            r"(?<=\d)(?=steps\b|tokens\b|records\b|examples\b|queries\b|bytes\b|updates\b)",
            " ",
            part,
        )
        for old, new in {
            "andassignment_unit": "and assignment_unit",
            "andquestion": "and question",
            "andevidence": "and evidence",
            "ofint": "of int",
            "UseNone": "Use None",
        }.items():
            part = part.replace(old, new)
        return part

    pieces = re.split(r"(```[\s\S]*?```|`[^`\n]*`|\]\([^\n]*?\))", document)
    return "".join(part if part.startswith(("```", "`", "](")) else clean(part) for part in pieces)


SPACING_WORDS = (
    "is|are|to|from|of|a|by|with|mean|coverage|gives|becomes|equals|about|approximately|"
    "accuracy|has|in|at|and|or|reports|produces|yields|rate|margin|score|loss"
)


def space_prose(document):
    """Separate words glued to numbers, lists and shapes in Markdown prose only."""

    def clean(part):
        for old, new in {
            "compareW@x forx[": "compare W@x for x [",
            "“test,false,internal traffic”": "`test,false,internal traffic`",
            "by sortedID": "by sorted ID",
            "authorizedanswercitesprivate": "authorized answer cites private",
            "raisesRuntimeError": "raises `RuntimeError`",
            "4-bitCPU": "4-bit CPU",
            "groupAmean 2": "group A mean 2",
            "errorA-errorB": "error A minus error B",
            "adapterParameters": "adapter parameters",
            "Documentb receives": "Document b receives",
            "whilea receives": "while a receives",
            "candidatesa, b": "candidates a, b",
            "score ofb as": "score of b as",
            "For tf1, 2, 10": "For tf values 1, 2 and 10",
            "columns account_type,eligible": "columns `account_type`, `eligible`",
            "inputs=sequence[:-1] and targets=sequence[1:]": "`inputs=sequence[:-1]` and `targets=sequence[1:]`",
        }.items():
            part = part.replace(old, new)
        part = re.sub(
            r"Assignq ?1, q2 to ?family ?F and ?q ?3 to ?G",
            "Assign q1 and q2 to family F and q3 to G",
            part,
        )
        part = re.sub(
            r"\b(for|and)(comet_period|restricted_threshold|score_matrix)\b", r"\1 `\2`", part
        )
        part = re.sub(
            r"\b(to)?(family|favors|update|dequantized)([A-Z])\b",
            lambda m: (m.group(1) + " " if m.group(1) else "") + m.group(2) + " " + m.group(3),
            part,
        )
        part = re.sub(r"\b(coverage|is|are|of|at)\.(\d)", r"\1 0.\2", part)
        part = re.sub(
            rf"\b({SPACING_WORDS})(?=[-+]?\d+(?:\.\d+)?(?![A-Za-z\d]))",
            r"\1 ",
            part,
        )
        part = re.sub(r"\b([a-z]{2,})\[(-?\d+), ?(-?\d+)\)", r"\1 \\([\2, \3)\\)", part)
        part = re.sub(
            r"\b([A-Za-z]{2,}) ?(\[[-+\d.,/ \[\]eNa]*(?:\d|NaN)\]+)",
            lambda m: m.group(1) + " `" + re.sub(r",(?=\S)", ", ", m.group(2)) + "`",
            part,
        )
        part = re.sub(r"\b([a-z]{2,}) ?\[([a-z](?:, ?[a-z])+)\]", r"\1 `[\2]`", part)
        part = re.sub(r"\b(is|are)\((?=-?\d)", r"\1 (", part)
        part = re.sub(r"\bshape\((\d+(?:, ?\d+)*)\)", r"shape `(\1)`", part)
        part = re.sub(r"\b([A-Za-z]{3,}):(\d)", r"\1: \2", part)
        part = re.sub(r"\b([a-z]{3,}),(?=[a-z]{3,}\b)", r"\1, ", part)
        return part.replace("`test, false, internal traffic`", "`test,false,internal traffic`")

    pieces = re.split(
        r"(```[\s\S]*?```|`[^`\n]*`|\]\([^\n]*?\)|\\\([\s\S]*?\\\)|\\\[[\s\S]*?\\\])", document
    )
    return "".join(
        part if part.startswith(("```", "`", "](", "\\(", "\\[")) else clean(part)
        for part in pieces
    )


def authored_outcome(id):
    """Return the lesson's authored outcome after the shared observable-verb check."""
    from scripts.build_coverage_matrix import outcome_issue

    outcome = OUTCOMES[id]
    issue = outcome_issue(outcome)
    assert issue is None, f"{id} outcome {issue}"
    return outcome


def write_outcomes():
    """Update only plan outcomes, preserving every other track.json value."""
    path = ROOT / "courses" / "llm-applied" / "track.json"
    plan = json.loads(path.read_text())
    ids = [p["id"] for p in plan["lessons"]]
    assert sorted(ids) == sorted(OUTCOMES), "outcomes.py must cover every planned lesson"
    for p in plan["lessons"]:
        p["outcome"] = authored_outcome(p["id"])
    path.write_text(json.dumps(plan, indent=2) + "\n")
    print("Updated", len(ids), "plan outcomes")


def sentence(text):
    """Return a fragment as a sentence with a capital initial and a final period."""
    text = text.strip()
    if not text:
        return text
    if re.fullmatch(r"[a-z]+[,;:]?", text.split()[0]):
        text = text[0].upper() + text[1:]
    return text if text.endswith((".", "?", "!")) else text + "."


def lesson_prose(id, p, s, plan, reading, learner, solution):
    """Build the guide and explanation paragraphs from this lesson's own fixtures."""
    titles = {x["id"]: x["title"] for x in plan["lessons"]}
    order = [x["id"] for x in plan["lessons"]]
    ex = s["exercises"]
    a, b, c, last = ex[0], ex[1], ex[2], ex[-1]
    t = [k for k, v in s["terms"]]
    topic = p["title"].removeprefix("Capstone: ")
    topic = topic[0].lower() + topic[1:]
    finish = sentence(a["expected"]) + " " + sentence(last["expected"])
    blob = s["imports"] + s["helper"] + "".join(e["code"] for e in ex)
    if "torch" in blob:
        stack = "PyTorch" + (" and NumPy" if "np." in blob else "")
    elif "np." in blob:
        stack = "NumPy"
    else:
        stack = "the Python standard library"
    prereqs = p["prerequisites"]
    named = [f"`{q}` ({titles.get(q, q)})" for q in prereqs]
    named = ", ".join(named[:-1]) + " and " + named[-1] if len(named) > 1 else "".join(named)
    later = order[order.index(id) + 1 :]
    capstone = not later
    out = {}
    out["level"] = f"{p['level'].capitalize()}; approximately {p['minutes']} minutes. " + (
        "Direct prerequisites: "
        + named
        + f". They introduce the notation this lesson needs for {t[0].lower()} and {t[1].lower()}."
        if prereqs
        else f"No prerequisite lesson; {t[0].lower()} and {t[1].lower()} are defined below."
    )
    if reading:
        out["runtime"] = (
            f"Use the reading worksheet `{learner}`. *{a['title']}*, *{b['title']}* and "
            f"*{c['title']}* are text cases; no execution or model download is required."
        )
    else:
        out["runtime"] = (
            f"Run `{learner}` in the declared `{p['runtime']}` profile. *{a['title']}*, "
            f"*{b['title']}* and *{c['title']}* need only {stack} and literal fixtures.\n\n"
            f"Copy it to `.learning/expansion/{id}/` or the saved pad before editing; "
            "nothing is installed or downloaded."
        )
    if reading:
        out["study"] = (
            f"Read *{a['title']}*, *{b['title']}* and *{c['title']}* in order, writing the assumptions and "
            f"conclusion for each. Compare them with the stated observations, beginning with "
            f"{sentence(a['expected'])} Then answer the six cases, ending with *{last['title']}*. "
            "These are text cases, not programs to execute. The optional pretrained recipe is a "
            "separate, deliberately prepared execution path; reading this chapter does not run or "
            "qualify it."
        )
    else:
        out["study"] = (
            f"Run Examples A to C in one scratch file: *{b['title']}* and "
            f"*{c['title']}* reuse the helper and fixture introduced in "
            f"*{a['title']}*. Before running Example A, write its intermediate "
            f"quantities by hand and predict the result. It should give: {sentence(a['expected'])} "
            f"Example B should give: {sentence(b['expected'])} Example C should give: "
            f"{sentence(c['expected'])} Use the tolerance in each assertion; counts, "
            "identities and decisions must match exactly."
        )
    out["prediction"] = (
        f"Before reading the code for *{b['title']}*, predict its result from the prompt alone: "
        f"{sentence(b['prompt'])} Write the guess beside the stated outcome ({b['expected'].rstrip('.')}). "
        f"Then predict how the decisive case, *{last['title']}*, should end: "
        f"{sentence(last['prompt'])} For {topic}, the finish condition is: {finish}"
    )
    out["hints"] = (
        f"Hint 1: restate {t[0].lower()} and {t[1].lower()} for the fixture in "
        f"*{a['title']}*. Hint 2: change one literal in *{b['title']}* and note which "
        f"intermediate value moves. Hint 3: compare your fourth exercise, *{ex[3]['title']}*, "
        f"with its stated result ({ex[3]['expected'].rstrip('.')}). If *{last['title']}* "
        "accepts an input it should reject, look for the missing check rather than widening a tolerance."
    )
    out["self"] = (
        f"Close the examples and explain {', '.join(x.lower() for x in t[:2])} and {t[2].lower()} using "
        f"*{a['title']}*. Recompute its result ({a['expected'].rstrip('.')}) from the inputs. "
        f"Change one input in *{c['title']}* and predict whether "
        f"the stated result ({c['expected'].rstrip('.')}) still holds. Say which part of {topic} the code "
        "guarantees and which part would need new observations."
    )
    back = "revisit " + named if prereqs else "reread the vocabulary section"
    out["next"] = f"If *{a['title']}* cannot be reconstructed without the solution, {back}. " + (
        f"Otherwise keep the six observations from {topic} and continue to "
        f"`{later[0]}` ({titles[later[0]]})."
        if not capstone
        else f"As the capstone, a failed *{last['title']}* check is a valid no-go "
        "decision; state which evidence would reopen it."
    )
    out["sources"] = (
        f"Reference for {t[0].lower()}: [{s['source'][0]}]({s['source'][1]}), reviewed {s['source'][2] if len(s['source']) > 2 else '2026-10-22'}. "
        f"The fixtures for *{a['title']}*, *{b['title']}* and "
        f"*{c['title']}* and the six exercises are original course material.\n\n"
        "Execution gates are described in [validation](../../../docs/validation.md); "
        "CI artifacts show which checks ran for each revision."
    )
    out["diagnosis"] = (
        f"When a result in {topic} disagrees, find the first intermediate value that departs "
        "from the explanation, checking shapes and identities before aggregates. "
        f"*{last['title']}* is the decisive failure case and should end with: "
        f"{sentence(last['expected'])} If your version accepts that input, a validation step is "
        f"missing; do not edit the expected text. *{ex[4]['title']}* should give: "
        f"{sentence(ex[4]['expected'])} If the {stack} runtime is unavailable, record the code as "
        "unverified."
    )
    out["intro"] = (
        f"Open these answers for {topic} only after attempting *{a['title']}* through "
        f"*{last['title']}*. A discrepancy in *{b['title']}* can be traced to one "
        "step because the inputs match the guide. "
        + (
            f"`{solution}` runs the assertions; this page explains why they test "
            f"{t[0].lower()} and {t[1].lower()}."
            if not reading
            else f"This page explains why each answer tests {t[0].lower()} and {t[1].lower()}."
        )
    )
    out["review"] = (
        f"Change one literal in *{c['title']}* and predict how the result changes before "
        f"checking it; the unchanged inputs give: {c['expected'].rstrip('.')}. Keep the original "
        f"*{last['title']}* failure beside the repaired result; a missing {stack} runtime "
        "is not a failing assertion. No solution downloads data, calls an online model or "
        "changes a database."
    )
    out["transfer"] = [
        f"This repeats Example {chr(65 + n)}; reproduce it closed-book, then change one literal "
        f"and predict the new result before running it."
        for n in range(3)
    ]
    return out


def write_all(only=None, guides_only=False, markdown_only=False):
    for track in ["llm-applied"]:
        base = ROOT / "courses" / track
        plan = json.loads((base / "track.json").read_text())
        inventory = json.loads((base / "lessons.json").read_text())
        existing = {x["id"] for x in inventory["lessons"]}
        for p in plan["lessons"]:
            id = p["id"]
            if id not in SPECS or (only is not None and id not in only):
                continue
            s = SPECS[id]
            for field in ["mental", "anatomy", "decisions"]:
                s[field] = polish(s[field])
            for exercise in s["exercises"]:
                for field in ["prompt", "expected", "why"]:
                    exercise[field] = polish(exercise[field])
            p["outcome"] = authored_outcome(id)
            p["lab"] = s["exercises"][0]["prompt"]
            p["verification"] = s["exercises"][0]["expected"] + " " + s["exercises"][-1]["expected"]
            p["concepts"] = [k for k, v in s["terms"]]
            reading = p["runtime"] == "reading"
            ext = "md" if reading else "py"
            prefix = f"courses/{track}"
            guide = f"{prefix}/guides/{id}.md"
            learner = f"{prefix}/lessons/{id}.{ext}"
            solution = f"{prefix}/solutions/{id}_solution.py"
            explanation = f"{prefix}/solutions/{id}_solutions.md"
            prereq = ", ".join(f"`{q}`" for q in p["prerequisites"])
            prose = lesson_prose(id, p, s, plan, reading, learner, solution)
            terms = "\n\n".join(f"**{k}:** {v}" for k, v in s["terms"])
            exercise_text = "\n\n".join(
                f"{n}. **{e['title']}.** {e['prompt']}\n   **Expected:** {e['expected']}\n   **Verify:** Save the {('reasoning table' if reading else 'assertion results')} for exercise {n}, including {e['expected']}"
                + (f"\n   **Transfer:** {prose['transfer'][n - 1]}" if n <= 3 else "")
                for n, e in enumerate(s["exercises"], 1)
            )
            examples = "\n\n".join(
                f"### Example {chr(65 + n)}: {e['title']}\n\n{e['why']}\n\n```{'text' if reading else 'python'}\n{(s['imports'] + chr(10) + s['helper'] + chr(10)) if not reading and n == 0 else ''}{e['code']}\n```\n\n**Expected:** {e['expected']}"
                for n, e in enumerate(s["exercises"][:3])
            )
            runtime = prose["runtime"]
            study_guidance = prose["study"]
            code_anatomy = s["anatomy"]
            purpose = s.get("textbook_mental", s["mental"])
            overview = s.get(
                "textbook_overview",
                p["outcome"]
                + " The central investigation is concrete: "
                + p["lab"]
                + " The finish condition is "
                + p["verification"]
                + " A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.",
            )
            prompt = f"""Use the checked-in $guide-ds60sqlpy-learning skill for {id}, {p["title"]}.
Read {guide} and {learner}. Direct prerequisites: {prereq}.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep {prefix}/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions."""
            document = f"""# {id}: {p["title"]}

## Level and prerequisites

{prose["level"]}

## Learning objectives

{overview}

## Purpose and mental model

{purpose}

{s.get("textbook_chapter", "")}

## Design decisions and when to use this method

{s.get("decisions", "")}

## Vocabulary and concepts

{terms}

## How to run this lesson

{runtime}

{study_guidance}

## Syntax anatomy and reasoning sequence

{code_anatomy}

## Worked example / walkthrough

{examples}

## Prediction before your attempt

{prose["prediction"]}

## Exercises

{exercise_text}

## Common pitfalls and diagnosis

{s.get("diagnosis", prose["diagnosis"])}

## Progressive hints

{prose["hints"]}

## Self-check and retrieval

{prose["self"]}

## Next step

{prose["next"]}

## Sources and verification status

{prose["sources"]}

{s.get("appendix", "")}

## Ask an AI tutor about this lesson

```text
{prompt}
```
"""
            explanation_doc = f"""# {id}: explanatory solutions

{prose["intro"]}

## Mechanism review

{s["mental"]}

{terms}

## Reading the implementation

{s["anatomy"]}

"""
            blocks = []
            for n, e in enumerate(s["exercises"], 1):
                explanation_doc += f"""## Exercise {n}: {e["title"]}

The question is: {e["prompt"]}

{e["why"]}

```{"text" if reading else "python"}
{e["code"]}
```

**Expected:** {e["expected"]}

**Verify:** Compare the computed values or written argument with {e["expected"]}

"""
                blocks.append(
                    f"    # Exercise {n}: {e['title']}\n" + textwrap.indent(e["code"], "    ")
                )
            explanation_doc += "## Review after comparison\n\n" + prose["review"] + "\n"
            (ROOT / guide).write_text(
                canonical_markdown(
                    space_prose(polish_textbook_prose(document)), root=SOURCE_ROOT, path=guide
                )
            )
            if guides_only:
                continue
            (ROOT / explanation).write_text(
                canonical_markdown(
                    space_prose(polish_textbook_prose(explanation_doc)),
                    root=SOURCE_ROOT,
                    path=explanation,
                )
            )
            if markdown_only:
                continue
            if reading:
                (ROOT / learner).write_text(
                    f"# {id}: {p['title']}\n\nRead the guide, record a prediction, then answer the six cases without opening solutions.\n\n## Exercises\n\n"
                    + exercise_text
                    + "\n"
                )
            else:
                source = f'"""{id}: {p["title"]}.\n\nAnswer-free learner worksheet. See the companion guide for worked examples.\nCopy to .learning before editing. Six independent attempts belong below.\n"""\n\n'
                for n, e in enumerate(s["exercises"], 1):
                    source += (
                        f"# Exercise {n}: {e['title']}\n"
                        + "\n".join("# " + x for x in textwrap.wrap(e["prompt"], 88))
                        + "\n# Expected: "
                        + e["expected"]
                        + "\n\n"
                    )
                source += 'if __name__ == "__main__":\n    print("Read the guide and implement the six exercises in your saved copy.")\n'
                (ROOT / learner).write_text(source)
                code = (
                    '"""'
                    + id
                    + ': bounded local reference checks. No network or persistent data writes."""\n\n'
                    + s["imports"]
                    + "\n\n"
                    + s["helper"]
                    + "\n\n\ndef verify():\n"
                    + "\n\n".join(blocks)
                    + '\n    return {"checks": 6, "status": "passed"}\n\n\nif __name__ == "__main__":\n    print(verify())\n'
                )
                (ROOT / solution).write_text(code)
            if id not in existing:
                inventory["lessons"].append(
                    dict(
                        id=id,
                        status="authored",
                        language="markdown" if reading else "python",
                        runtime_profile=p["runtime"],
                        guide_path=guide,
                        source_path=learner,
                        solution_paths=[explanation] if reading else [solution, explanation],
                        verification_id=None,
                    )
                )
        if guides_only or markdown_only:
            continue
        inventory["lessons"].sort(key=lambda x: x["id"])
        (base / "lessons.json").write_text(json.dumps(inventory, indent=2) + "\n")
        (base / "track.json").write_text(json.dumps(plan, indent=2) + "\n")
    print("Rendered", len(SPECS), "guides" if guides_only else "lesson bundles")
