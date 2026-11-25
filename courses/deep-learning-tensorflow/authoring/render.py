from pathlib import Path
import json, textwrap, re
import sys

ROOT = Path(__file__).resolve().parents[3]
SOURCE_ROOT = ROOT
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))
from scripts.format_inline_code import canonical_markdown  # noqa: E402
from verify_text import describe_checks  # noqa: E402

SPECS = {}
STUDY_GUIDE = "../STUDY-GUIDE.md"
DEFAULT_DIAGNOSIS = "When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result."


def ex(title, prompt, expected, code, why, verify=None):
    item = dict(
        title=title, prompt=prompt, expected=expected, code=textwrap.dedent(code).strip(), why=why
    )
    if verify:
        item["verify"] = verify
    return item


COUNT_WORDS = {1: "the", 2: "both", 3: "all three", 4: "all four"}


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


def practice_plan(spec, transfer):
    """Return worked examples, practice exercises and the reference block order."""
    if "worked_examples" in spec:
        return spec["worked_examples"], spec["exercises"], list(range(6)), None
    worked = spec["exercises"][:2]
    if transfer is None:
        note = "Exercises 1 and 2 repeat the worked examples as guided reconstructions; exercises 3-6 change the fixture or expose a failure."
        return worked, spec["exercises"], list(range(6)), note
    assert len(transfer) == 2
    note = "The worked examples demonstrate the mechanism; exercises 1 and 2 transfer it to new inputs and exercises 3-6 extend it to failures and boundary cases."
    # Exercises 3-6 continue the worked fixture state exactly as before, so the
    # reference runs the worked code first and the transfer exercises last.
    return worked, transfer + spec["exercises"][2:], [2, 3, 4, 5, 0, 1], note


def add(id, mental, anatomy, terms, exercises, source, imports="import numpy as np", helper=""):
    assert len(exercises) == 6, id
    SPECS[id] = dict(
        mental=mental,
        anatomy=anatomy,
        terms=terms,
        exercises=exercises,
        source=source,
        imports=imports,
        helper=textwrap.dedent(helper).strip(),
    )


def sentence(text):
    text = text.strip()
    return text if text[-1:] in ".?!" else text + "."


def write_all(only=None, guides_only=False, markdown_only=False):
    from transfer_exercises import TRANSFER

    for track in ["deep-learning-tensorflow", "llm-theory"]:
        base = ROOT / "courses" / track
        plan = json.loads((ROOT / "docs/expansion/plans" / f"{track}.json").read_text())
        inventory = json.loads((base / "lessons.json").read_text())
        existing = {x["id"] for x in inventory["lessons"]}
        for p in plan["lessons"]:
            id = p["id"]
            if id not in SPECS or (only is not None and id not in only):
                continue
            s = SPECS[id]
            tf_track = track == "deep-learning-tensorflow"
            reading = p["runtime"] == "reading"
            worked, exercises, reference_order, practice_note = practice_plan(s, TRANSFER.get(id))
            if tf_track and practice_note:
                practice_note = (
                    f"Exercises 1 and 2 use new inputs; 3-6 add failures ([exercise plan]({STUDY_GUIDE}#exercise-plan))."
                    if id in TRANSFER
                    else f"Exercises 1 and 2 rebuild the worked examples; 3-6 change the fixture ([exercise plan]({STUDY_GUIDE}#exercise-plan))."
                )
            separate_worked = "worked_examples" in s or id in TRANSFER
            count = COUNT_WORDS[len(worked)]
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
                f"### Example {chr(65 + n)}: {e['title']}\n\n{e['why']}\n\n```{'text' if reading else 'python'}\n{(e.get('preamble', s['imports'] + chr(10) + s['helper']) + chr(10)) if not reading else ''}{e['code'] if reading or 'worked_examples' in s else chr(10).join(item['code'] for item in worked[: n + 1])}\n```\n\n**Expected:** {e['expected']}"
                for n, e in enumerate(worked)
            )
            runtime = (
                "Use the reading worksheet. Write a reasoned response for each case; no execution or model download is required."
                if reading
                else f"Use the `{p['runtime']}` worker; each example block is a complete program ([shared routine]({STUDY_GUIDE}#launch-a-lesson))."
                if tf_track
                else f"Start or resume the Docker classroom with `./classroom` from the repository root. On Windows, run that command in WSL 2. In the shared home, choose the **{plan['title']}** subject and select `{id}`. Use its `{p['runtime']}` worker and wait for readiness before choosing **Run**; the [classroom instructions](../../../docs/one-command-classroom.md) explain how to prepare a missing profile. The worker supplies the declared packages and starts a fresh Python process, so no host Python or framework installation is needed. Save your current attempt before replacing the pad with a complete worked example. Keep the example sequence specified below together. Inputs are small local fixtures, with no package installation, dataset or model download, or online service call. For an optional contributor workflow on Linux, macOS or Windows through WSL 2, deliberately prepare an interpreter with the same declared dependencies, then invoke that interpreter on an owned copy of `{learner}` under `.learning/expansion/{id}/`. The general contributor uv environment does not imply that TensorFlow or PyTorch is installed. The Docker profile is the default execution route."
            )
            study_method = (
                f"Read {count} worked reasoning cases. Derive the intermediate quantities and units on paper, then compare the assumptions and conclusions. Text blocks here are evidence tables or written arguments, not programs. Keep unknown evidence distinct from a failed condition and explain what observation would settle it."
                if reading
                else f"Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. {'Examples B and C change assumptions' if len(worked) == 3 else 'Example B changes an assumption'} that matters to this mechanism. Compare {'the' if len(worked) == 3 else 'both'} observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. For float64 arithmetic use an absolute tolerance of 1e-12 unless an exercise gives another bound. TensorFlow and PyTorch float32 comparisons use 1e-6. Integer counts, identities and boolean decisions should be exact."
            )
            code_anatomy = s["anatomy"]
            run_section = runtime if tf_track else f"{runtime}\n\n{study_method}"
            level_text = f"{p['level'].capitalize()}; approximately {p['minutes']} minutes. Direct prerequisites: {prereq}."
            objectives = f"{p['outcome']} The central investigation is concrete: {p['lab']} The finish condition is {p['verification']}"
            if not tf_track:
                level_text += " The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar."
                objectives += " A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition."
            prompt = f"""Use the checked-in $guide-ds60sqlpy-learning skill for {id}, {p["title"]}.
Read {guide} and {learner}. Direct prerequisites: {prereq}.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep {prefix}/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions."""
            w = [e["title"] for e in worked]
            x = [e["title"] for e in exercises]
            term_list = ", ".join(k for k, v in s["terms"][:3])
            prediction = (
                f"Cover the **Expected** line of Example A, {w[0]}, and derive it from the fixture: name the input unit, the intermediate state and the final quantity. Read exercise 6, {x[5]}, and predict its outcome before any code runs: {sentence(exercises[5]['prompt'])} Then restate this finish condition in your own words: {p['verification']} Keep each prediction next to the value you later observe."
                if tf_track
                else f"For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: {p['verification']} Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation."
            )
            hints = (
                f"Hint 1: Example {chr(64 + len(w))}, {w[-1]}, changes one assumption of Example A, {w[0]}; name it. Hint 2: exercise 4, {x[3]}, should reach {sentence(exercises[3]['expected'])} Trace backward from that value. Hint 3: exercise 5, {x[4]}, alters one input; say which intermediate moves first. If a step still disagrees, ask for the first wrong step, not a replacement implementation."
                if tf_track
                else "First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson."
            )
            self_check = (
                f"Close the guide and rebuild Example {chr(64 + len(w))}, {w[-1]}, from its inputs alone. Predict whether exercise 3, {x[2]}, still passes after one changed input. Explain {term_list} using that fixture, then separate what the code guarantees from what would need new observations about unseen data."
                if tf_track
                else f"Close {count} worked examples. Explain {term_list} using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model."
            )
            next_step = (
                f"If Example A, {w[0]}, cannot be rebuilt without help, revisit {prereq} first. Otherwise keep your exercise 2 attempt, {x[1]}, as a regression case beside a fresh transfer input, then continue along the course plan."
                if tf_track
                else f"Revisit the direct prerequisite {prereq} if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it."
            )
            sources = (
                f"API and mechanism reference: [{s['source'][0]}]({s['source'][1]}), reviewed 2026-10-22 ([verification status]({STUDY_GUIDE}#verification-status))."
                if tf_track
                else f"API and mechanism reference: [{s['source'][0]}]({s['source'][1]}), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. See [validation](../../../docs/validation.md) for execution gates. Check CI artifacts for the exact revision and platform to determine which runtime checks actually ran; authored content alone does not establish runtime execution."
            )
            if tf_track and "capstone" in p["title"].lower():
                next_step += " In a capstone, a failed acceptance condition is a valid no-go decision; state what evidence would reopen it."
            document = f"""# {id}: {p["title"]}

## Level and prerequisites

{level_text}

## Learning objectives

{objectives}

## Purpose and mental model

{s["mental"]}

## Vocabulary and concepts

{terms}

## How to run this lesson

{run_section}

## Syntax anatomy and reasoning sequence

{code_anatomy}

{s.get("mechanism_notes", "")}

## Worked example / walkthrough

{examples}

## Prediction before your attempt

{prediction}

## Exercises

{practice_note or ("The worked examples demonstrate the mechanism; the exercises below change inputs, expose failures and add boundary cases." if separate_worked else "")}

{exercise_text}

## Common pitfalls and diagnosis

{s.get("diagnosis", DEFAULT_DIAGNOSIS)}

## Progressive hints

{hints}

## Self-check and retrieval

{self_check}

## Next step

{next_step}

## Sources and verification status

{sources}

## Ask an AI tutor about this lesson

```text
{prompt}
```
"""
            solutions_intro = (
                f"Open these answers after an attempt; they reuse the guide's inputs ([comparison steps]({STUDY_GUIDE}#after-the-solutions))."
                if tf_track
                else "Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer."
            )
            explanation_doc = f"""# {id}: explanatory solutions

{solutions_intro}

## Mechanism review

{s["mental"]}

{terms}

## Reading the implementation

{s["anatomy"]}

"""
            blocks = []
            if id in TRANSFER:
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
            if not tf_track:
                explanation_doc += "## Review after comparison\n\nRepeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.\n"
            (ROOT / guide).write_text(canonical_markdown(document, root=SOURCE_ROOT, path=guide))
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
                for n, e in enumerate(exercises, 1):
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
        if markdown_only:
            continue
        inventory["lessons"].sort(key=lambda x: x["id"])
        (base / "lessons.json").write_text(json.dumps(inventory, indent=2) + "\n")
    print("Authored", len(SPECS), "lesson bundles")
