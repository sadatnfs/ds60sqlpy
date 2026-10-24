from pathlib import Path
import json, textwrap
import yaml

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / "courses/kubernetes"
PLAN = json.loads((ROOT / "docs/expansion/plans/kubernetes.json").read_text())["lessons"]


def fixture(name):
    return list(yaml.safe_load_all((BASE / "fixtures" / name).read_text()))


def hello(service=False):
    docs = list(yaml.safe_load_all((BASE / "lessons/k8s-008.yaml").read_text()))
    return docs if service else docs[:1]


def author(
    n,
    overview,
    sections,
    examples,
    tasks,
    manifests,
    check_code,
    *,
    browser=False,
    capability="owned-namespace observation",
    refs=(),
):
    key = f"k8s-{n:03d}"
    plan = next(p for p in PLAN if p["id"] == key)
    assert len(tasks) == 6 and len(examples) >= 2
    prereq = ", ".join(f"`{p}`" for p in plan["prerequisites"]) or "None"
    guide = f"courses/kubernetes/guides/{key}.md"
    source = (
        f"courses/kubernetes/lessons/{key}.yaml"
        if browser
        else f"courses/kubernetes/lessons/{key}.md"
    )
    lines = [
        f"# {key}: {plan['title']}",
        "## Level and prerequisites",
        f"{plan['level'].capitalize()}; about {plan['minutes']} minutes plus review. Direct prerequisites: {prereq}. The chapter separates desired configuration, API acceptance, controller observation and application evidence.",
        "## Learning objectives",
        plan["outcome"],
        "## Vocabulary and concepts",
        overview,
    ]
    for heading, body in sections[:-1]:
        lines += ["## " + heading, body]
    lines += ["## Worked example / walkthrough"]
    for i, (title, body, expected) in enumerate(examples, 1):
        lines += [f"### Worked example {i}: {title}", body, f"**Expected:** {expected}"]
    if browser:
        run = f"This lesson supplies an allowlisted `k8s-kind` source. Use `{source}` in the prepared module pad and inspect the current fixture-0.2 qualification receipt before Run. The app binds the owned namespace, creates fixed resources, observes its bounded checks and performs UID-aware cleanup. A one-shot Run does not execute the separate stateful host exercises or automatically grade explanations. [The run/host-lab guide](../host-labs.md) explains the precise boundary and POSIX/PowerShell targeting."
    else:
        run = f"The app artifact is a reading worksheet, `{source}`. The current browser adapter does not provide the full **{capability}** operation. Use the synthetic fixture and offline check first. Live work follows [the scoped host-lab guide](../host-labs.md) only when the named capability and owned target have been provisioned. A worksheet or static check is never a cluster execution receipt."
    lines += [
        "## Run and bounded evidence",
        run,
        f"The [manifest example](../solutions/{key}_solution.{'yaml' if browser else 'json'}) is separate from the learner artifact. The [offline reference check](../solutions/{key}_checks.py) evaluates explicitly synthetic facts and makes no API calls. Run it locally with `python courses/kubernetes/solutions/{key}_checks.py` after comparing your attempt. The [case ledger](../fixtures/{key}-cases.json) is immutable teaching input.",
        "## Exercises",
    ]
    for i, (title, prompt, expected, hints, answer) in enumerate(tasks, 1):
        lines += [
            f"### Exercise {i}: {title}",
            prompt,
            f"**Expected result/shape:** {expected}",
            f"**Verify:** Retain the named field values, identities, counts, diagnostic or written comparison: {expected}",
            f"**Progressive hints:** {hints}",
        ]
    lines += [
        "## Self-check",
        f"Explain the mechanism behind the first example, then distinguish it from this boundary case: {examples[1][2]} State which observations are synthetic and which, if any, were read from your owned runtime.",
        "## Common pitfalls",
        sections[-1][1],
        "## Retrieval and transfer",
        f"Close the answer and reconstruct the reasoning for Exercise6, {tasks[-1][0]}. Name the exact source and observed identity you would require before claiming the changed case succeeded.",
        "## Next step",
        f"Continue to `k8s-{n + 1:03d}` after preserving the six evidence records."
        if n < 42
        else "Review the complete release, incident and recovery packet with a second learner. Preserve separate content, runtime and application/data acceptance claims.",
        "## Primary references",
    ]
    lines += ["- " + ref for ref in refs]
    lines += [
        "## Ask an AI tutor about this lesson",
        f"```text\nUse $guide-ds60sqlpy-learning for {key}.\nRead {guide} and {source}. Direct prerequisites: {prereq}.\nExplain the mechanism, ask me to predict, let me attempt, give one hint, inspect evidence, then ask for retrieval.\nKeep courses/kubernetes/solutions/ closed until I attempt or explicitly ask for comparison.\nDistinguish source, synthetic fixtures, API acceptance, observed controllers, application/data results and cleanup.\nUse only an explicit owned lease and the stated capability; never select an ambient cluster or install a controller for me.\n```",
    ]
    guide_text = "\n\n".join(lines) + "\n"
    prompts = "\n".join(
        f"# Exercise {i}: {title}. {prompt} Expected: {expected}"
        for i, (title, prompt, expected, _, _) in enumerate(tasks, 1)
    )
    if browser:
        learner = yaml.safe_dump_all(manifests, sort_keys=False) + "\n" + prompts + "\n"
        manifest_path = f"courses/kubernetes/solutions/{key}_solution.yaml"
        manifest_text = yaml.safe_dump_all(manifests, sort_keys=False)
        language = "yaml"
        profile = "k8s-kind"
    else:
        learner = f"# {key} learner evidence worksheet\n\nUse the guide and synthetic case ledger. A prediction or copied fixture is not a live runtime observation.\n"
        for i, (title, prompt, expected, _, _) in enumerate(tasks, 1):
            learner += f"\n## Exercise {i}: {title}\n\n{prompt}\n\nExpected: {expected}\n\nMy prediction:\n\nMy evidence and interpretation:\n"
        manifest_path = f"courses/kubernetes/solutions/{key}_solution.json"
        manifest_text = (
            json.dumps({"apiVersion": "v1", "kind": "List", "items": manifests}, indent=2) + "\n"
        )
        language = "markdown"
        profile = "reading"
    code = textwrap.dedent(check_code).strip() + "\n"
    assert 'if __name__ == "__main__":' in code
    explanation = f"# {key}: Explanatory solutions\n\nThese answers explain the stated synthetic and scoped runtime contracts. Static checks do not prove cluster acceptance.\n\n## Mechanism\n\n{overview}\n"
    for i, (title, prompt, expected, hints, answer) in enumerate(tasks, 1):
        explanation += f"\n## Exercise {i}: {title}\n\n{answer}\n\n**Expected:** {expected}\n"
    explanation += "\n## Boundary and troubleshooting review\n\n" + sections[-1][1] + "\n"
    ledger = (
        json.dumps(
            {
                "lesson_id": key,
                "provenance": "synthetic teaching cases, not runtime observations",
                "capability": capability,
                "browser_source": browser,
                "cases": [
                    {"exercise": i, "task": prompt, "expected": expected}
                    for i, (_, prompt, expected, _, _) in enumerate(tasks, 1)
                ],
            },
            indent=2,
        )
        + "\n"
    )
    paths = {
        guide: guide_text,
        source: learner,
        manifest_path: manifest_text,
        f"courses/kubernetes/solutions/{key}_checks.py": code,
        f"courses/kubernetes/solutions/{key}_solutions.md": explanation,
        f"courses/kubernetes/fixtures/{key}-cases.json": ledger,
    }
    for relative, text in paths.items():
        assert "\u2014" not in text
        p = ROOT / relative
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    manifest = BASE / "lessons.json"
    data = json.loads(manifest.read_text())
    entry = {
        "id": key,
        "status": "authored",
        "language": language,
        "runtime_profile": profile,
        "guide_path": guide,
        "source_path": source,
        "solution_paths": [
            manifest_path,
            f"courses/kubernetes/solutions/{key}_checks.py",
            f"courses/kubernetes/solutions/{key}_solutions.md",
        ],
        "verification_id": None,
    }
    data["lessons"] = [x for x in data["lessons"] if x["id"] != key] + [entry]
    data["lessons"].sort(key=lambda x: x["id"])
    manifest.write_text(json.dumps(data, indent=2) + "\n")
