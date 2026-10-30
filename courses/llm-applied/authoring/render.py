from pathlib import Path
import json, textwrap, re
import sys

ROOT = Path(__file__).resolve().parents[3]
SOURCE_ROOT = ROOT
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))
from scripts.format_inline_code import canonical_markdown  # noqa: E402

SPECS = {}
GUIDES_ONLY = False
DEFAULT_DIAGNOSIS = "When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result."


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
            p["outcome"] = s["mental"].split(".")[0] + "."
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
            terms = "\n\n".join(f"**{k}:** {v}" for k, v in s["terms"])
            exercise_text = "\n\n".join(
                f"{n}. **{e['title']}.** {e['prompt']}\n   **Expected:** {e['expected']}\n   **Verify:** Save the {('reasoning table' if reading else 'assertion results')} for exercise {n}, including {e['expected']}"
                for n, e in enumerate(s["exercises"], 1)
            )
            examples = "\n\n".join(
                f"### Example {chr(65 + n)}: {e['title']}\n\n{e['why']}\n\n```{'text' if reading else 'python'}\n{(s['imports'] + chr(10) + s['helper'] + chr(10)) if not reading and n == 0 else ''}{e['code']}\n```\n\n**Expected:** {e['expected']}"
                for n, e in enumerate(s["exercises"][:3])
            )
            runtime = (
                "Use the reading worksheet. Write a reasoned response for each case; no execution or model download is required."
                if reading
                else f"Use a prepared `{p['runtime']}` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/{id}/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. Use the Docker classroom as the default route and select the declared `{p['runtime']}` profile. For a separately prepared native environment, invoke its explicitly selected interpreter on `{learner}` from the repository root. The general repository `.venv` is not assumed to include the heavy model dependencies."
            )
            study_guidance = (
                "Read the three worked cases in order and write the assumptions, intermediate reasoning and conclusion for each one. These are text cases, not programs to execute. Compare your written interpretation with the stated expected observations, then answer the six exercises in your saved worksheet. A correct argument must state its evidence boundary; source presence does not establish a model run. The optional pretrained recipe is a separate, deliberately prepared execution path with its own artifacts and receipts. Reading this chapter does not run or qualify that recipe."
                if reading
                else "Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Distinguish a retrieval or extraction baseline from an actual trained language model; each example names what it implements. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the tolerance stated in each assertion. Many analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone does not determine a universal error bound. Integer counts, identities and boolean decisions should be exact."
            )
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

{p["level"].capitalize()}; approximately {p["minutes"]} minutes. Direct prerequisites: {prereq}. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

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

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: {p["verification"]} Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

{exercise_text}

## Common pitfalls and diagnosis

{s.get("diagnosis", DEFAULT_DIAGNOSIS)}

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Revisit the worked examples, then close them. Explain {", ".join(k for k, v in s["terms"][:3])} using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite {prereq} if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [{s["source"][0]}]({s["source"][1]}), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. See [validation](../../../docs/validation.md) for execution gates. Check CI artifacts for the exact revision and platform to determine which runtime checks actually ran; authored content alone does not establish runtime execution.

{s.get("appendix", "")}

## Ask an AI tutor about this lesson

```text
{prompt}
```
"""
            explanation_doc = f"""# {id}: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

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
            explanation_doc += "## Review after comparison\n\nRepeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.\n"
            (ROOT / guide).write_text(
                canonical_markdown(polish_textbook_prose(document), root=SOURCE_ROOT, path=guide)
            )
            if guides_only:
                continue
            (ROOT / explanation).write_text(
                canonical_markdown(explanation_doc, root=SOURCE_ROOT, path=explanation)
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
