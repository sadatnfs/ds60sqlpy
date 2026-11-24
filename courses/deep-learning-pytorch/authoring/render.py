from pathlib import Path
import json, textwrap, re
import sys

ROOT = Path(__file__).resolve().parents[3]
SOURCE_ROOT = ROOT
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))
from scripts.format_inline_code import canonical_markdown  # noqa: E402

if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from objectives import OBJECTIVES  # noqa: E402
from verify_text import describe_checks  # noqa: E402

SPECS = {}
AUTHORING = Path(__file__).resolve().parent
# References bound to immutable runtime receipts keep their original six exercises,
# whose first three are also the worked examples. Every other lesson publishes the
# worked examples separately and adds three transfer exercises with new inputs.
FROZEN_REFERENCES = {"torch-005", "torch-012", "torch-014", "torch-015", "torch-016", "torch-030"}
# These guides are byte-bound by curriculum/presentation-parity.json and runtime
# receipts. Their reviewed presentation is reproduced from authoring/frozen_guides/
# until a new presentation binding is recorded for regenerated text.
FROZEN_GUIDES = {"torch-005", "torch-012", "torch-015", "torch-016"}


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
    comparison="",
    interview=(),
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
        comparison=comparison,
        interview=interview,
    )


def verify_line(lesson_id, exercise, reading):
    """Name the exercise's own checks; authored text covers written reasoning cases."""
    from transfer_exercises import AUTHORED_VERIFY

    if "verify" in exercise:
        return exercise["verify"]
    if (lesson_id, exercise["title"]) in AUTHORED_VERIFY:
        return AUTHORED_VERIFY[(lesson_id, exercise["title"])]
    described = None if reading else describe_checks(exercise["code"])
    if described is None:
        raise ValueError(f"{lesson_id}: exercise {exercise['title']!r} needs an authored verify")
    return f"In a fresh process, the exercise checks confirm {described}."


def sentence(text):
    text = text.strip()
    return text if text[-1:] in ".?!" else text + "."


def practice_note(lesson_id):
    if lesson_id in FROZEN_REFERENCES:
        return "Exercises 1-3 repeat the worked examples as guided reconstructions; exercises 4-6 change the fixture or expose a failure."
    return "The worked examples demonstrate the mechanism; exercises 1-3 transfer it to new inputs and exercises 4-6 extend it to failures and boundary cases."


def write_all(only=None, markdown_only=False):
    from transfer_exercises import TRANSFER

    for track in ["deep-learning-pytorch"]:
        base = ROOT / "courses" / track
        plan = json.loads((base / "track.json").read_text(encoding="utf-8"))
        inventory = json.loads((base / "lessons.json").read_text(encoding="utf-8"))
        existing = {x["id"] for x in inventory["lessons"]}
        for p in plan["lessons"]:
            id = p["id"]
            if id not in SPECS or (only is not None and id not in only):
                continue
            s = SPECS[id]
            p["outcome"], p["lab"], p["verification"] = OBJECTIVES[id]
            p["concepts"] = [k for k, v in s["terms"]]
            reading = p["runtime"] == "reading"
            if id in FROZEN_REFERENCES:
                worked, exercises = s["exercises"][:3], s["exercises"]
                reference_order = list(range(6))
            else:
                worked = s["exercises"][:3]
                exercises = TRANSFER[id] + s["exercises"][3:]
                # Exercises 4-6 continue the worked fixture state exactly as before;
                # the transfer exercises build their own fixtures and run afterward.
                reference_order = [3, 4, 5, 0, 1, 2]
            assert len(exercises) == 6, id
            ext = "md" if reading else "py"
            prefix = f"courses/{track}"
            guide = f"{prefix}/guides/{id}.md"
            learner = f"{prefix}/lessons/{id}.{ext}"
            solution = f"{prefix}/solutions/{id}_solution.py"
            explanation = f"{prefix}/solutions/{id}_solutions.md"
            prereq = ", ".join(f"`{q}`" for q in p["prerequisites"])
            terms = "\n\n".join(f"**{k}:** {v}" for k, v in s["terms"])
            exercise_text = "\n\n".join(
                f"{n}. **{e['title']}.** {e['prompt']}\n   **Expected:** {e['expected']}\n   **Verify:** {verify_line(id, e, reading)}"
                for n, e in enumerate(exercises, 1)
            )
            examples = "\n\n".join(
                f"### Example {chr(65 + n)}: {e['title']}\n\n{e['why']}\n\n```{'text' if reading else 'python'}\n{(s['imports'] + chr(10) + s['helper'] + chr(10)) if not reading and n == 0 else ''}{e['code']}\n```\n\n**Expected:** {e['expected']}"
                for n, e in enumerate(worked)
            )
            runtime = (
                "Use the reading worksheet. Write a reasoned response for each case; no execution or model download is required."
                if reading
                else f"Start or resume the Docker classroom with `./classroom` from the repository root. On Windows, run that command in WSL 2. In the shared home, choose the **{plan['title']}** subject and select `{id}`. Use its `{p['runtime']}` worker and wait for readiness before choosing **Run**; the [classroom instructions](../../../docs/one-command-classroom.md) explain how to prepare a missing profile. The worker supplies the declared packages and starts a fresh Python process, so no host Python or framework installation is needed. Save your current attempt before replacing the pad with a complete worked example. Keep the example sequence specified below together. Inputs are small local fixtures, with no package installation, dataset or model download, or online service call. For an optional contributor workflow on Linux, macOS or Windows through WSL 2, deliberately prepare an interpreter with the same declared dependencies, then invoke that interpreter on an owned copy of `{learner}` under `.learning/expansion/{id}/`. The general contributor uv environment does not imply that TensorFlow or PyTorch is installed. The Docker profile is the default execution route."
            )
            study_guidance = (
                "Read the three worked cases in order and write the assumptions, intermediate reasoning and conclusion for each one. These are text cases, not programs to execute. Compare your written interpretation with the stated expected observations, then answer the six exercises in your saved worksheet. A correct argument must state its evidence boundary; source presence does not establish a model run."
                if reading
                else "Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the explicit tolerance in each assertion. Several analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone is not a universal numerical-error bound. Finite differences, reductions and conditioning can require different justified tolerances. Integer counts, identities and boolean decisions should be exact."
            )
            code_anatomy = s["anatomy"]
            prompt = f"""Use the checked-in $guide-ds60sqlpy-learning skill for {id}, {p["title"]}.
Read {guide} and {learner}. Direct prerequisites: {prereq}.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep {prefix}/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions."""
            paired = p["paired_lesson_id"]
            interview_text = "\n\n".join(
                "**" + question + "**\n\n" + answer for question, answer in s["interview"]
            )
            diagnosis = s.get(
                "diagnosis",
                "When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.",
            )
            w = [e["title"] for e in worked]
            x = [e["title"] for e in exercises]
            term_list = ", ".join(k for k, v in s["terms"][:3])
            prediction = f"Derive Example A again with its **Expected** line covered: {w[0]}. Predict exercise 6, {x[5]}, from its prompt alone: {sentence(exercises[5]['prompt'])} Then explain why this finish condition holds: {p['verification']} Keep each prediction beside the observed value."
            hints = f"Hint 1: Example B ({w[1]}) alters one assumption of Example A ({w[0]}). Hint 2: exercise 4, {x[3]}, should end at {sentence(exercises[3]['expected'])} Work backward from it. Hint 3: exercise 5, {x[4]}, changes one input; predict which value moves first."
            self_check = f"Close the worked examples and rebuild Example C, {w[2]}, from its inputs alone. Predict whether exercise 3, {x[2]}, survives one changed input. Then explain {term_list} in terms of that fixture; say which claims the code guarantees and which need new observations."
            next_step = f"If Example A ({w[0]}) cannot be rebuilt without help, revisit {prereq} first. Otherwise keep your exercise 2 attempt, {x[1]}, as a regression case alongside a fresh transfer input, then continue along the course plan."
            if "capstone" in p["title"].lower():
                next_step += " In a capstone, a failed acceptance condition is a valid no-go decision; state what evidence would reopen it."
            document = f"""# {id}: {p["title"]}

## Level and prerequisites

{p["level"].capitalize()}; approximately {p["minutes"]} minutes. Direct prerequisites: {prereq}. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

{p["outcome"]}

Central investigation: {p["lab"]}

Finish condition: {p["verification"]}

{practice_note(id)} A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

{s["mental"]}

## Design decisions and when to use this method

{s.get("decisions", "")}

## Paired TensorFlow comparison

Compare [{paired}](../../deep-learning-tensorflow/guides/{paired}.md) after deriving the shared numerical contract.

{s["comparison"]}

## Vocabulary and concepts

{terms}

## How to run this lesson

{runtime}

{study_guidance}

## Syntax anatomy and reasoning sequence

{code_anatomy}

{s.get("deep_dive", "")}

## Worked example / walkthrough

{examples}

## Prediction before your attempt

{prediction}

## Exercises

{exercise_text}

## Common pitfalls and diagnosis

{diagnosis}

## Progressive hints

{hints}

## Self-check and retrieval

{self_check}

## Next step

{next_step}

## Sources and verification status

API and mechanism reference: [{s["source"][0]}]({s["source"][1]}), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. See [validation](../../../docs/validation.md) for execution gates. Check CI artifacts for the exact revision and platform to determine which runtime checks actually ran; authored content alone does not establish runtime execution.

## Interview reasoning with worked answers

{interview_text}

{s.get("appendix", "")}

## Ask an AI tutor about this lesson

```text
{prompt}
```
"""
            explanation_doc = f"""# {id}: explanatory solutions

Open these answers only after attempting {p["title"]} yourself. They reuse the guide's literal inputs, starting from Example A, {w[0]}, so a discrepancy points at one step. The executable companion runs the assertions; this page explains why each one tests {term_list}. After a pass, choose a new input for exercise 6, {x[5]}, without looking.

## Mechanism review

{s["mental"]}

{terms}

## Reading the implementation

{s["anatomy"]}

{s.get("deep_dive", "")}

"""
            blocks = []
            if id not in FROZEN_REFERENCES:
                blocks = [
                    f"    # Worked example {chr(65 + n)}: {e['title']}\n"
                    + textwrap.indent(e["code"], "    ")
                    for n, e in enumerate(worked)
                ]
            exercise_blocks = {}
            for n, e in enumerate(exercises, 1):
                explanation_doc += f"""## Exercise {n}: {e["title"]}

The question is: {e["prompt"]}

{e["why"]}

```{"text" if reading else "python"}
{e["code"]}
```

**Expected:** {e["expected"]}

**Verify:** {verify_line(id, e, reading)}

"""
                exercise_blocks[n - 1] = f"    # Exercise {n}: {e['title']}\n" + textwrap.indent(
                    e["code"], "    "
                )
            blocks.extend(exercise_blocks[index] for index in reference_order)
            explanation_doc += f"## Review after comparison\n\nRepeat exercise 4, {x[3]}, with one changed fixture value and predict the difference before running it. Keep your failing attempt at exercise 5, {x[4]}, beside the repaired result. A missing framework is not a failing assertion. These solutions use only local fixtures.\n"
            if id in FROZEN_GUIDES:
                (ROOT / guide).write_bytes(
                    (AUTHORING / "frozen_guides" / f"{id}.md.snapshot").read_bytes()
                )
            else:
                (ROOT / guide).write_text(
                    canonical_markdown(document, root=SOURCE_ROOT, path=guide),
                    encoding="utf-8",
                    newline="\n",
                )
            (ROOT / explanation).write_text(
                canonical_markdown(explanation_doc, root=SOURCE_ROOT, path=explanation),
                encoding="utf-8",
                newline="\n",
            )
            if markdown_only:
                continue
            if reading:
                (ROOT / learner).write_text(
                    f"# {id}: {p['title']}\n\nRead the guide, record a prediction, then answer the six cases without opening solutions.\n\n## Exercises\n\n"
                    + exercise_text
                    + "\n",
                    encoding="utf-8",
                    newline="\n",
                )
            else:
                source = f'"""{id}: {p["title"]}.\n\nAnswer-free learner worksheet. See the companion guide for worked examples.\nCopy to .learning before editing. Six independent attempts belong below.\n"""\n\n'
                for n, e in enumerate(exercises, 1):
                    source += (
                        f"# Exercise {n}: {e['title']}\n"
                        + "\n".join("# " + x for x in textwrap.wrap(e["prompt"], 88))
                        + "\n# Expected: "
                        + e["expected"]
                        + "\n\n"
                    )
                source += 'if __name__ == "__main__":\n    print("Read the guide and implement the six exercises in your saved copy.")\n'
                (ROOT / learner).write_text(source, encoding="utf-8", newline="\n")
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
                (ROOT / solution).write_text(code, encoding="utf-8", newline="\n")
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
        if markdown_only:
            continue
        inventory["lessons"].sort(key=lambda x: x["id"])
        (base / "lessons.json").write_text(
            json.dumps(inventory, indent=2) + "\n", encoding="utf-8", newline="\n"
        )
        (base / "track.json").write_text(
            json.dumps(plan, indent=2) + "\n", encoding="utf-8", newline="\n"
        )
    print("Authored", len(SPECS), "lesson bundles")
