from pathlib import Path
import json, textwrap

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "courses/nlp"
PLAN = json.loads((BASE / "track.json").read_text())["lessons"]


def author(n, overview, sections, examples, exercises, learner, solution, interviews, refs):
    item = PLAN[n - 1]
    key = item["id"]
    assert len(exercises) == 6
    guide = f"courses/nlp/guides/{key}.md"
    source = f"courses/nlp/learners/{key}.py"
    prereq = ", ".join("`" + p + "`" for p in item["prerequisites"])
    lines = [
        f"# {key}: {item['title']}",
        "## Level and prerequisites",
        f"{item['level'].capitalize()}; about {item['minutes']} minutes plus discussion. Direct prerequisites: {prereq}. Read the preceding guide if its notation or information boundaries are unfamiliar.",
        "## Purpose and mental model",
        overview,
    ]
    for title, body in sections:
        lines += ["## " + title, body]
    lines += ["## Worked examples"]
    for i, (title, body) in enumerate(examples, 1):
        lines += [f"### Worked example {i}: {title}", body]
    lines += [
        "## Run and inspect",
        f"Open the NLP module with the prepared `python-core` profile and save `{source}` in your learner pad. The learner file contains fixtures and incomplete work, not the official implementation. No download, model service or external corpus is required. The checked-in [fixture ledger](../fixtures/{key}-cases.json) records the exercise contract. When using a prepared native environment, run `python {source}` from the repository root. A process exit does not automatically grade the exercises. Keep [solutions](../solutions/{key}_solutions.md) closed until an attempt or explicit comparison.",
        "## Exercises",
    ]
    for i, (title, task, expected, hints, answer) in enumerate(exercises, 1):
        lines += [
            f"### Exercise {i}: {title}",
            task,
            f"**Expected:** {expected}",
            f"**Verify:** {expected} Retain the actual values or failure evidence and explain the relevant input boundary.",
            f"**Hints:** {hints}",
        ]
    lines += ["## Interview reasoning"]
    lines += interviews
    lines += [
        "## Retrieval and continuation",
        f"Without the source, explain which mechanism produces the first worked result, which counterexample exposes its limitation, and which claim the tiny fixture cannot establish. Continue to `nlp-{n + 1:03d}`."
        if n < 24
        else "Explain the end-to-end evidence chain to a reviewer. Continue into the applied LLM route when generation or adaptation is justified by the measured failure cases.",
        "## Primary references",
    ]
    lines += ["- " + r for r in refs]
    lines += [
        "## Ask an AI tutor about this lesson",
        f"```text\nUse $guide-ds60sqlpy-learning for {key}.\nRead {guide} and {source}.\nDirect prerequisites: {prereq}.\nExplain the mechanism and notation, ask me to predict, let me attempt, give one hint, inspect evidence, then ask for retrieval.\nKeep courses/nlp/solutions/ closed until I attempt or explicitly request comparison.\nCheck numerical, span or task-level outputs and a counterexample; do not equate a toy mechanism with pretrained-model quality.\nDo not download corpora or models or send text to an external service.\n```",
    ]
    guide_text = "\n\n".join(lines) + "\n"
    learner = textwrap.dedent(learner).strip() + "\n"
    solution = textwrap.dedent(solution).strip() + "\n"
    assert 'if __name__ == "__main__":' in learner and 'if __name__ == "__main__":' in solution
    prompts = "\n".join(
        f"# Exercise {i}: {title}. {task} Expected: {expected}"
        for i, (title, task, expected, hints, answer) in enumerate(exercises, 1)
    )
    learner += "\n" + prompts + "\n"
    answer_text = f"# {key}: Explanatory solutions\n\nThe executable reference checks the declared fixtures. It is separate from the learner scaffold and does not certify general task quality.\n\n"
    for i, (title, task, expected, hints, answer) in enumerate(exercises, 1):
        answer_text += f"## Exercise {i}: {title}\n\n{answer}\n\n**Expected:** {expected}\n\n"
    answer_text += "## Transfer and limits\n\n" + overview + "\n"
    fixture = (
        json.dumps(
            {
                "lesson_id": key,
                "cases": [
                    {"exercise": i, "task": task, "expected": expected}
                    for i, (_, task, expected, _, _) in enumerate(exercises, 1)
                ],
            },
            indent=2,
        )
        + "\n"
    )
    for relative, text in [
        (guide, guide_text),
        (source, learner),
        (f"courses/nlp/solutions/{key}_solution.py", solution),
        (f"courses/nlp/solutions/{key}_solutions.md", answer_text),
        (f"courses/nlp/fixtures/{key}-cases.json", fixture),
    ]:
        assert "\u2014" not in text
        path = ROOT / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    manifest = BASE / "lessons.json"
    data = json.loads(manifest.read_text())
    record = {
        "id": key,
        "status": "authored",
        "language": "python",
        "runtime_profile": "python-core",
        "guide_path": guide,
        "source_path": source,
        "solution_paths": [
            f"courses/nlp/solutions/{key}_solution.py",
            f"courses/nlp/solutions/{key}_solutions.md",
        ],
        "verification_id": None,
    }
    data["lessons"] = [x for x in data["lessons"] if x["id"] != key] + [record]
    data["lessons"].sort(key=lambda x: x["id"])
    manifest.write_text(json.dumps(data, indent=2) + "\n")
