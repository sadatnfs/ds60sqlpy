"""Author the offline D3 browser specialization after the original 42 lessons."""

from pathlib import Path
import json
import runpy
import sys

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.format_inline_code import canonical_markdown  # noqa: E402

SPECS = runpy.run_path(str(Path(__file__).with_name("d3_specs.py")))["LESSONS"]


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == ".md":
        text = canonical_markdown(text, root=ROOT, path=path.relative_to(ROOT).as_posix())
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def build():
    plan = json.loads((BASE / "track.json").read_text(encoding="utf-8"))
    manifest = json.loads((BASE / "lessons.json").read_text(encoding="utf-8"))
    plan["lessons"] = [r for r in plan["lessons"] if int(r["id"].split("-")[-1]) <= 42]
    manifest["lessons"] = [r for r in manifest["lessons"] if int(r["id"].split("-")[-1]) <= 42]
    inventory = []
    for n, spec in enumerate(SPECS, 43):
        title, concepts, mental, anatomy, examples, tasks, reference, refs = spec
        key = f"js-{n:03d}"
        prereq = ["js-029", "js-005"] if n == 43 else [f"js-{n - 1:03d}"]
        level = "intermediate" if n <= 54 else "advanced"
        guide = f"courses/javascript-typescript/guides/{key}.md"
        source = f"courses/javascript-typescript/lessons/{key}.js"
        solution = f"courses/javascript-typescript/solutions/{key}_solution.js"
        explanation = f"courses/javascript-typescript/solutions/{key}_solutions.md"
        prerequisites = ", ".join(f"`{p}`" for p in prereq)
        text = f"""# {key}: {title}

## Level and prerequisites

{level.capitalize()}; about 110 minutes plus independent practice. Direct prerequisites: {prerequisites}. This is the D3.js specialization within the JavaScript path. Use the original language and browser lessons whenever syntax or DOM behavior is unfamiliar.

## Learning objectives

{tasks[2][0]} {tasks[-1][0]} Produce a chart whose data transformation, visual encoding and interaction can be explained and checked independently.

## Purpose, vocabulary and mental model

{mental}

## Syntax anatomy and mechanism

{anatomy}

## Browser execution and offline inputs

Use the classroom's JavaScript browser preview. The prepared preview supplies D3 7.9.0 as the global `d3`, an empty `#chart` container and a `#output` text region. It supports top-level `await` through an asynchronous wrapper. These examples do not import modules, fetch datasets, use a CDN or contact an external service. All data is small, synthetic and present in the source. Node has no DOM and is not the execution host for these lessons.

Save your own pad before editing. Run the learner source after implementing its tasks. A completed reference prints `{key} D3 complete` only after its executable checks finish. A thrown Error signals a failed check; `console.assert` alone is not a reliable completion contract. A browser observation proves this source ran in this preview. It is not a trusted backend verifier or a guarantee of statistical correctness, accessibility or mastery.

The visual output belongs inside `#chart`. Use `.text()` or `textContent` for untrusted labels, never HTML interpolation. The preview is recreated for a new run, so long-lived listeners and animations should still be bounded and cleaned up in reusable components. No reference needs cookies, credentials, host files or engine access.

## Worked example / walkthrough
"""
        for i, (heading, body, code, expected) in enumerate(examples, 1):
            text += f"\n### Worked example {i}: {heading}\n\n{body}\n\n```javascript\n{code}\n```\n\n**Expected observation:** {expected}\n"
        text += "\n## Six progressive exercises\n"
        starter = f"// {key}: {title}\n// D3 7.9.0 is supplied as global d3. Render only inside #chart.\n// Answer-free learner artifact. Save your own copy before editing.\n\n"
        answer = f"# {key}: explanatory solutions\n\nCompare after your own attempt or an explicit reveal. The separate .js reference is a complete offline browser program. These explanations discuss the six practice tasks; a visual resemblance alone is not a data or behavior check.\n\n## Mechanism review\n\n{mental}\n\n{anatomy}\n"
        for i, (prompt, expected, reason) in enumerate(tasks, 1):
            text += f"\n### Exercise {i}: {prompt}\n\n**Expected evidence:** {expected}\n\n**Progressive hint:** Inspect the input records, then the derived values, then the DOM or Canvas marks. Compare the first disagreement with the worked example before changing another layer.\n"
            starter += f"// Exercise {i}: {prompt}\n// Expected: {expected}\n\n"
            answer += f"\n## Exercise {i}: {prompt}\n\n{reason}\n\n**Expected:** {expected}\n"
        starter += 'throw new Error("Implement the six D3 practice tasks in your saved pad before claiming completion.");\n'
        text += (
            f"""
## Debugging and common mistakes

Keep three checkpoints separate: the records after parsing, the domain and geometry after transformation, and the visible marks after rendering. A chart can look plausible while silently dropping records or assigning the wrong scale. Inspect counts, IDs, finite coordinates and meaningful expected values before adjusting colors. A missing mark may come from invalid input, a missing selection, an undefined scale result or clipping outside the viewBox.

The controlled failure for this lesson is: {tasks[3][0]} Its distinguishing evidence is {tasks[3][1]} Preserve that failing case when repairing your program. Do not remove an assertion or broaden a scale merely to hide a wrong input. Explain whether a changed value should affect the data, an encoding, a layout or only presentation.

## Accessibility and interpretation

Give the visualization a descriptive title and a short textual summary of the main result. Keep a table or list when exact values matter. Do not encode a critical category only through color; use labels, shapes or position as appropriate. Interactive controls need keyboard operation and clear focus, and motion should respect the user's reduced-motion preference. Automated DOM checks support, but do not replace, a real keyboard and assistive-technology review.

A data scientist must also defend the statistical meaning. State the population, units, aggregation, missing-value policy and uncertainty where relevant. Synthetic points illustrate a mechanism and do not establish a real-world finding. A beautiful visualization should make a valid claim easier to inspect, not make a weak claim appear certain.

## Retrieval and transfer

Close the solution and explain {", ".join(concepts[:3])} using a new small dataset. Reconstruct one example from a blank pad. Predict the effect of one missing value, empty input or reordered record before execution. Retain the source and observation separately from the explanation so a future reader can reproduce the case.

## Primary references

"""
            + "\n".join(f"- [D3 reference {i}]({url})" for i, url in enumerate(refs, 1))
            + f"""

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for {key}: {title}.
Read {guide} and {source}. Direct prerequisites: {prerequisites}.
Explain the data-to-mark mechanism, ask for a prediction, inspect my attempt and give one hint.
Keep courses/javascript-typescript/solutions/ closed until I attempt or request comparison.
Require real browser evidence for DOM interactions and a separate explanation of statistical meaning.
Use only the offline D3 global and inline synthetic inputs; do not fetch packages or data.
Finish with a fresh boundary case, keyboard review and a reconstruction from memory.
```
"""
        )
        prefix = f"""// {key}: complete offline D3 browser reference.
if (typeof d3 !== 'object' || d3.version !== '7.9.0') throw new Error('Prepared D3 7.9.0 is required.');
const host = document.querySelector('#chart');
const output = document.querySelector('#output');
if (!host || !output) throw new Error('Preview chart/output nodes are required.');
host.replaceChildren();
const check = (condition, message) => {{ if (!condition) throw new Error(message); }};
const svg = d3.select(host)
  .append('svg')
  .attr('viewBox', '0 0 640 360')
  .attr('role', 'img')
  .attr('aria-label', {json.dumps(title)})
  .style('width', '100%')
  .style('max-width', '640px');
svg.append('title').text({json.dumps(title)});
"""
        suffix = f"""\noutput.textContent = {json.dumps(key + " D3 complete")};
console.log({json.dumps(key + " D3 complete")});
"""
        write(ROOT / guide, text)
        write(ROOT / source, starter)
        write(ROOT / solution, prefix + reference.strip() + "\n" + suffix)
        write(ROOT / explanation, answer)
        plan["lessons"].append(
            dict(
                id=key,
                title=title,
                level=level,
                minutes=110,
                prerequisites=prereq,
                runtime="javascript-browser",
                concepts=concepts,
                outcome=tasks[-1][0],
                lab=tasks[2][0],
                verification=tasks[-1][1],
            )
        )
        manifest["lessons"].append(
            dict(
                id=key,
                status="authored",
                language="javascript",
                runtime_profile="javascript-browser",
                guide_path=guide,
                source_path=source,
                solution_paths=[solution, explanation],
                verification_id=None,
            )
        )
        inventory.append(
            dict(
                id=key,
                source=source,
                reference=solution,
                marker=f"{key} D3 complete",
                runtime="javascript-browser",
                input="inline synthetic",
                no_network=True,
                expected=tasks[0][1],
            )
        )
    plan["summary"] = (
        "66 lessons in JavaScript and TypeScript, including a dedicated 24-lesson offline D3 visualization sequence. Progress from language foundations through browser behavior, typed applications, statistical graphics and accessible interactive dashboards."
    )
    write(BASE / "track.json", json.dumps(plan, indent=2))
    write(BASE / "lessons.json", json.dumps(manifest, indent=2))
    write(
        BASE / "fixtures/d3-inventory.json",
        json.dumps(
            dict(
                schema_version=1,
                library="D3 7.9.0",
                capability="actual browser preview; no backend verifier claim",
                references=inventory,
            ),
            indent=2,
        ),
    )
    print(
        f"Authored {len(SPECS)} D3 browser lessons; total {len(plan['lessons'])} JavaScript/TypeScript lessons."
    )


if __name__ == "__main__":
    build()
