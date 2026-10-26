"""Assemble the paired Plotly practice route from durable source and guides."""

import ast
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]

UNITS = json.loads((BASE / "authoring" / "units.json").read_text(encoding="utf-8"))


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def standalone_python(number):
    text = (BASE / "authoring" / "python_cases.py").read_text()
    tree = ast.parse(text)
    functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
    name = f"case_{number:02d}"
    required = {name}
    while True:
        before = required.copy()
        for function in before:
            required |= {
                node.id
                for node in ast.walk(functions[function])
                if isinstance(node, ast.Name) and node.id in functions
            }
        if required == before:
            break
    names = {
        node.id
        for function in required
        for node in ast.walk(functions[function])
        if isinstance(node, ast.Name)
    }
    imports = []
    for node in tree.body:
        if not isinstance(node, (ast.Import, ast.ImportFrom)):
            continue
        aliases = [
            alias for alias in node.names if (alias.asname or alias.name.split(".")[0]) in names
        ]
        if aliases:
            selected = (
                ast.Import(names=aliases)
                if isinstance(node, ast.Import)
                else ast.ImportFrom(module=node.module, names=aliases, level=node.level)
            )
            imports.append(ast.unparse(selected))
    parts = [f'"""viz-{number:03d}: complete offline Plotly reference."""', "\n".join(imports)]
    parts += [
        ast.get_source_segment(text, node)
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and node.name in required
    ]
    parts += [
        (
            f"def main():\n    figure = {name}()\n"
            '    figure.show(config={"responsive": True, "displaylogo": False})\n'
            f'    print("viz-{number:03d} Plotly complete")'
        ),
        'if __name__ == "__main__":\n    main()',
    ]
    return "\n\n\n".join(parts)


def build():
    plan, admission, inventory = [], [], []
    browser = (BASE / "authoring" / "browser_cases.js").read_text()
    for number, (title, level, prerequisites, concepts, outcome, fixture, answers) in enumerate(
        UNITS, 1
    ):
        key = f"viz-{number:03d}"
        prefix = "courses/data-visualization"
        guide = f"{prefix}/guides/{key}.md"
        python_source, js_source = f"{prefix}/lessons/{key}.py", f"{prefix}/lessons/{key}.js"
        python_reference, js_reference = (
            f"{prefix}/references/{key}.py",
            f"{prefix}/references/{key}.js",
        )
        explanation = f"{prefix}/solutions/{key}_solutions.md"
        plan.append(
            {
                "id": key,
                "title": title,
                "level": level,
                "minutes": 90,
                "prerequisites": prerequisites,
                "runtime": "python-core",
                "concepts": concepts,
                "outcome": outcome,
                "lab": (
                    f"Use the supplied fixture to complete the six {title.lower()} tasks "
                    "and compare the numerical and visual evidence."
                ),
                "verification": (
                    "Check the named values and failure case in the guide; "
                    f"the reference prints {key} Plotly complete after creating its figure."
                ),
            }
        )
        admission.append(
            {
                "id": key,
                "status": "authored",
                "language": "python",
                "runtime_profile": "python-core",
                "guide_path": guide,
                "source_path": python_source,
                "solution_paths": [python_reference, explanation],
                "verification_id": None,
                "variants": [
                    {
                        "id": "javascript",
                        "title": "JavaScript (browser)",
                        "language": "javascript",
                        "runtime_profile": "javascript-browser",
                        "source_path": js_source,
                        "solution_paths": [js_reference, explanation],
                        "verification_id": None,
                    }
                ],
            }
        )
        write(ROOT / python_reference, standalone_python(number))
        write(
            ROOT / js_reference,
            browser + f'\nawait renderCase(specifications[{number}](), "{key} Plotly complete");\n',
        )
        write(
            ROOT / python_source,
            f'''"""{key}: learner source. Read the guide and keep your own saved draft."""

import plotly.graph_objects as go

FIXTURE = {fixture!r}


def main():
    # Derive the chart and accessible table from FIXTURE.
    # Follow the six tasks in the guide; the worked reference is separate.
    print("Prepared Plotly figure type:", go.Figure.__name__)
    print("Fixture loaded; derive the figure and its checks from the guide tasks.")


if __name__ == "__main__":
    main()
''',
        )
        write(
            ROOT / js_source,
            f"""// {key}: learner source for the prepared browser Plotly variant.
// window.Plotly, #chart and #output are supplied. No imports or fetches.
const fixture = {json.dumps(fixture)};
console.table(fixture);
// Derive your traces, caption and native source table from fixture.
// Complete the six guide tasks in your own saved source.
console.log("Fixture loaded; derive the figure and its checks from the guide tasks.");
""",
        )
        solution = (
            f"# {key}: explanatory solutions\n\n"
            "Compare with your attempt when you choose to reveal the reference. "
            "These answers explain the six tasks in the guide. "
            "The complete Python and browser references use the same scientific fixture.\n"
        )
        for index, answer in enumerate(answers, 1):
            solution += f"\n## Exercise {index}\n\n{answer}\n"
        solution += (
            "\n## Complete references and evidence\n\n"
            f"[Python reference](../references/{key}.py) and "
            f"[JavaScript reference](../references/{key}.js) are complete programs "
            "for their declared hosts. Python figure construction and browser rendering "
            "are separate observations. Test numerical values, real interaction, table access, "
            "narrow layouts and source persistence separately. "
            "No completion marker certifies scientific validity or learner mastery.\n"
        )
        write(ROOT / explanation, solution)
        path = ROOT / guide
        text = path.read_text()
        marker = "## Ask an AI tutor about this lesson"
        if marker in text:
            text = text.split(marker, 1)[0].rstrip() + "\n"
        text += f"""\n{marker}

```text
Use the repository's .agents/skills/guide-ds60sqlpy-learning/SKILL.md to tutor me on {key}: {title}.
Read courses/data-visualization/guides/{key}.md and my chosen Python or JavaScript
learner source under courses/data-visualization/lessons/.
Focus on {", ".join(concepts)} and the exact numerical/visual evidence in this guide.
Explain one mechanism, ask for a prediction, then review my attempt with progressive hints.
Do not read the separate references or solutions until I ask or explicitly authorize comparison.
Keep my saved source and observations. Use only the prepared offline classroom;
no fetches, package installs, accounts or servers.
Completion means I can explain the calculation, diagnose the stated failure case
and transfer the encoding to another fixture, not merely copy a picture.
```
"""
        write(path, text)
        inventory.append(
            {
                "id": key,
                "python_reference": python_reference,
                "javascript_reference": js_reference,
                "marker": f"{key} Plotly complete",
                "expected_table_rows": [3, 4, 3, 8, 3, 8, 3, 3][number - 1],
            }
        )
    write(
        BASE / "track.json",
        json.dumps(
            {
                "schema_version": 1,
                "id": "data-visualization",
                "title": "Scientific visualization with Plotly: Python and JavaScript",
                "summary": (
                    "Eight paired lessons on data encodings, distributions, "
                    "uncertainty, interactive inspection, forecasting, model "
                    "comparisons, bounded rendering and accessible figure evidence."
                ),
                "lessons": plan,
            },
            indent=2,
        ),
    )
    write(
        BASE / "lessons.json",
        json.dumps(
            {"schema_version": 1, "track_id": "data-visualization", "lessons": admission}, indent=2
        ),
    )
    write(BASE / "fixtures" / "plotly-inventory.json", json.dumps(inventory, indent=2))


if __name__ == "__main__":
    build()
