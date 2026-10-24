"""Durable Docker curriculum authoring. No engine access or downloads."""

from pathlib import Path
import json
import runpy

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
SPECS = runpy.run_path(str(Path(__file__).with_name("chapters.py")))["CHAPTERS"]


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def build():
    rows, records = [], []
    for n, spec in enumerate(SPECS, 1):
        key = f"docker-{n:03d}"
        level = "beginner" if n <= 14 else "intermediate" if n <= 28 else "advanced"
        prereq = [f"docker-{n - 1:03d}"] if n > 1 else []
        title, mental, anatomy, examples, tasks, refs = spec
        terms = mental.split("\n\n")[0]
        rows.append(
            dict(
                id=key,
                title=title,
                level=level,
                minutes=100 if n < 29 else 120,
                prerequisites=prereq,
                runtime="reading",
                concepts=title.split(":")[0].split(", "),
                outcome=tasks[-1][0],
                lab=tasks[2][0],
                verification=tasks[-1][1],
            )
        )
        guide = f"courses/docker/guides/{key}.md"
        source = f"courses/docker/lessons/{key}.md"
        solution = f"courses/docker/solutions/{key}_solutions.md"
        prerequisites = (
            ", ".join(f"`{p}`" for p in prereq)
            or "None; start with the terminal and process explanations here."
        )
        text = f"""# {key}: {title}

## Level and prerequisites

{level.capitalize()}; about {rows[-1]["minutes"]} minutes, with additional time for the optional host experiment. Direct prerequisites: {prerequisites}

## Learning objectives

{tasks[2][0]} {tasks[-1][0]} Explain the difference between a configuration, an observed process and evidence of the application's behavior.

## Purpose, vocabulary and mental model

{mental}

## Anatomy and a trace you can follow

{anatomy}

## How to use this lesson

The classroom displays this guide and saves your worksheet. Its Run button does not control your Docker engine. Docker engine access is powerful host access, so the classroom deliberately receives no engine socket. Work through the supplied examples without starting anything, then use the optional host lab only in your own disposable project. Reading a command, parsing YAML and actually running the project are different forms of evidence.

Use Bash in Linux, macOS Terminal, or Ubuntu under WSL 2 on Windows. The supported engine runs Linux containers. The maintained fixture is `courses/docker/fixtures/compose-lab/`; its README explains copying it into a new ignored learner directory, checking the engine, building locally with visible logs, and using the fixed project name `ds60-docker-study`. The fixture uses port 18080 on host loopback. Stop if that project name or port belongs to unrelated work; choose a new project name consistently in your own copy. Never paste a command against a remote Docker context simply because it is currently selected.

For Dockerfile examples, create a file named `Dockerfile` in a scratch project. YAML snippets describe a fragment unless explicitly called a complete file. Text transcripts are synthetic illustrations, not claims about your machine. Do not substitute a real password, token or private registry into a checked-in example.

## Worked example / walkthrough
"""
        for i, (heading, body, lang, code, expected) in enumerate(examples, 1):
            text += f"\n### Worked example {i}: {heading}\n\n{body}\n\n```{lang}\n{code}\n```\n\n**Expected observation:** {expected}\n"
        text += "\n## Six progressive exercises\n"
        worksheet = f"# {key}: learner worksheet\n\nSave predictions before optional host execution. Keep exact project name, engine identity and timestamps with runtime observations. No exercise runs automatically.\n"
        answer = f"# {key}: explanatory solutions\n\nCompare after your own attempt or an explicit reveal. These are explanations of the supplied teaching fixtures, not fabricated engine results.\n\n## Mechanism review\n\n{mental}\n\n{anatomy}\n"
        for i, (prompt, expected, reason) in enumerate(tasks, 1):
            text += f"\n### Exercise {i}: {prompt}\n\n**Expected evidence:** {expected}\n\n**Hint:** Identify the object and the phase of its lifetime before changing it. Use the relevant worked example, then vary only the condition named in this task.\n"
            worksheet += f"\n## Exercise {i}: {prompt}\n\nMy prediction:\n\nMy evidence:\n\nMy explanation and remaining limitation:\n"
            answer += f"\n## Exercise {i}: {prompt}\n\n{reason}\n\n**Expected:** {expected}\n"
        text += (
            f"""
## Common mistakes and diagnosis

Start with the smallest observation that separates two plausible causes. An image inspection answers questions about the packaged filesystem and configuration; container inspection adds runtime mounts, network attachment and exit status. An application request adds another layer of evidence. A healthy container can still serve the wrong application result. Preserve the original failure and the exact changed field before retrying.

The boundary case in this chapter is: {tasks[3][0]} Use its expected observation, {tasks[3][1]}, to avoid treating a successful command as proof of the wrong claim. Keep source edits in your own copy. Do not make a container privileged, mount the engine socket, disable all checks or delete every volume to make an example succeed.

## Retrieval, transfer and next steps

Close the explanations and draw the path from source files to image to container to the observation relevant here. Reconstruct the second worked example with one different value and predict what changes. Explain which state survives process restart, container recreation and image rebuild. If none of those operations applies to this mechanism, explain why.

Before proceeding, retain six evidence records. For the optional host project, use `docker compose -p ds60-docker-study down` from the fixture copy to stop its containers and remove its ordinary network. This command preserves named volumes. Volume deletion is a separate deliberate reset of that disposable lab after a backup or export, never a general cleanup step. The fixture README describes its exact scoped reset.

## Primary references

"""
            + "\n".join(f"- [Official reference {i}]({url})" for i, url in enumerate(refs, 1))
            + f"""

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for {key}: {title}.
Read {guide} and {source}. Direct prerequisites: {prerequisites}
Ask me to predict the first example, review my worksheet, and give one hint at a time.
Keep courses/docker/solutions/ closed until I attempt or explicitly request comparison.
Distinguish image metadata, container state and actual application evidence.
Do not execute host commands, change Docker contexts or delete volumes on my behalf.
Finish with a fresh transfer case and ask which evidence would falsify my explanation.
```
"""
        )
        answer += "\n## Check your transfer\n\nA useful solution identifies the exact object, the phase when a setting takes effect, the expected normal result and an observation that disproves it. Repeating a command until it succeeds hides the mechanism. Change one variable, keep a failure record, and test the intended behavior again. Source examples here are small enough to inspect; a production system additionally needs ownership, lifecycle, data recovery and operational review. The host exercises are optional and must stay within the learner-created project.\n"
        write(ROOT / guide, text)
        write(ROOT / source, worksheet)
        write(ROOT / solution, answer)
        records.append(
            dict(
                id=key,
                status="authored",
                language="markdown",
                runtime_profile="reading",
                guide_path=guide,
                source_path=source,
                solution_paths=[solution],
                verification_id=None,
            )
        )
    write(
        BASE / "track.json",
        json.dumps(
            dict(
                schema_version=1,
                id="docker",
                title="Docker: images, applications and operating containers",
                summary=f"{len(rows)} detailed lessons from the first container to reproducible builds, Compose, networking, durable data, security, delivery and recovery. Study offline and use clearly scoped optional host labs.",
                lessons=rows,
            ),
            indent=2,
        ),
    )
    write(
        BASE / "lessons.json",
        json.dumps(dict(schema_version=1, track_id="docker", lessons=records), indent=2),
    )
    print(f"Authored {len(rows)} Docker lessons with explicit host-only execution boundaries.")


if __name__ == "__main__":
    build()
