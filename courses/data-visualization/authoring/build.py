"""Assemble the paired Plotly practice route from durable source and guides."""

import ast
import json
import re
import subprocess
import sys
import textwrap
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parents[1]

UNITS = json.loads((BASE / "authoring" / "units.json").read_text(encoding="utf-8"))
REASONING = json.loads((BASE / "authoring" / "reasoning.json").read_text(encoding="utf-8"))
REASONING_LABELS = {
    "approach": "Approach",
    "correct": "Why it is correct",
    "wrong": "A plausible wrong approach",
    "verify": "How to verify",
}


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def format_python(text, name):
    """Apply the repository's Ruff import order and formatting to generated Python."""
    config = str(ROOT / "pyproject.toml")
    for command in (
        ["check", "--select", "I", "--fix", "--config", config, "--stdin-filename", name, "-"],
        ["format", "--config", config, "--stdin-filename", name, "-"],
    ):
        text = subprocess.run(
            [sys.executable, "-m", "ruff", *command],
            input=text,
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    return text


def js_literal(value, indent=0, prefix="", suffix=""):
    """Write a JSON-compatible fixture the way the repository's Prettier settings do."""

    def flat(item):
        if isinstance(item, list):
            return "[" + ", ".join(flat(x) for x in item) + "]"
        if isinstance(item, dict):
            pairs = ", ".join(
                (k if re.fullmatch(r"[A-Za-z_$][\w$]*", k) else json.dumps(k)) + ": " + flat(v)
                for k, v in item.items()
            )
            return "{ " + pairs + " }" if pairs else "{}"
        return json.dumps(item)

    pad = " " * indent
    one_line = pad + prefix + flat(value) + suffix
    if len(one_line) <= 100 or not isinstance(value, (list, dict)):
        return one_line
    if isinstance(value, list):
        inner = [js_literal(item, indent + 2, "", ",") for item in value]
        return pad + prefix + "[\n" + "\n".join(inner) + "\n" + pad + "]" + suffix
    inner = [
        js_literal(
            v,
            indent + 2,
            (k if re.fullmatch(r"[A-Za-z_$][\w$]*", k) else json.dumps(k)) + ": ",
            ",",
        )
        for k, v in value.items()
    ]
    return pad + prefix + "{\n" + "\n".join(inner) + "\n" + pad + "}" + suffix


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


ANATOMY_START = "<!-- plotly-anatomy:start -->"
ANATOMY_END = "<!-- plotly-anatomy:end -->"
OPENERS, CLOSERS = "([{", ")]}"


def python_figure_lines(number):
    """Return the exact figure-construction statements of one durable Python case."""
    text = (BASE / "authoring" / "python_cases.py").read_text()
    function = next(
        node
        for node in ast.parse(text).body
        if isinstance(node, ast.FunctionDef) and node.name == f"case_{number:02d}"
    )

    def touches_figure(statement):
        targets = statement.targets if isinstance(statement, ast.Assign) else []
        if any(isinstance(t, ast.Name) and t.id == "fig" for t in targets):
            return True
        call = statement.value if isinstance(statement, ast.Expr) else None
        return (
            isinstance(call, ast.Call)
            and isinstance(call.func, ast.Attribute)
            and isinstance(call.func.value, ast.Name)
            and call.func.value.id == "fig"
        )

    chosen = [statement for statement in function.body if touches_figure(statement)]
    lines = text.splitlines()[chosen[0].lineno - 1 : chosen[-1].end_lineno]
    return textwrap.dedent("\n".join(lines))


def balanced_block(lines, first):
    """Collect lines from first until JavaScript brackets outside strings balance."""
    depth, quote, collected = 0, None, []
    for line in lines[first:]:
        collected.append(line)
        escaped = False
        for character in line:
            if quote:
                if escaped:
                    escaped = False
                elif character == "\\":
                    escaped = True
                elif character == quote:
                    quote = None
            elif character in "\"'`":
                quote = character
            elif character in OPENERS:
                depth += 1
            elif character in CLOSERS:
                depth -= 1
        if depth <= 0:
            return collected
    raise ValueError("Unbalanced JavaScript excerpt")


def javascript_figure_lines(number):
    """Return the trace and layout declarations of one durable browser case."""
    text = (BASE / "authoring" / "browser_cases.js").read_text()
    start = text.index(f"\n  {number}() {{\n")
    end = text.index("\n  },\n", start)
    lines = text[start:end].splitlines()
    data = next(
        i
        for i, line in enumerate(lines)
        if line.startswith(("      data: [", "    const data = ", "    const data=["))
    )
    layout = next(i for i, line in enumerate(lines) if line.startswith("      layout: {"))
    return "\n".join(
        textwrap.dedent("\n".join(balanced_block(lines, first))) for first in (data, layout)
    )


def anatomy(number):
    return (
        f"{ANATOMY_START}\n"
        f"Python, from `case_{number:02d}` in the subject's durable Plotly source:\n\n"
        f"```python\n{python_figure_lines(number)}\n```\n\n"
        f"JavaScript, from browser specification {number}, which `renderCase` passes to "
        "`Plotly.newPlot` with the shared caption and table:\n\n"
        f"```javascript\n{javascript_figure_lines(number)}\n```\n"
        f"{ANATOMY_END}"
    )


def lab_text(guide):
    text = guide.read_text(encoding="utf-8")
    worked = re.search(r"^## Worked case: (.+)$", text, flags=re.M).group(1).strip()
    first, *_, last = exercise_titles(text)
    return (
        f"Rebuild the worked case ({worked}) from the inline fixture, then complete the six "
        f"exercises from {first.lower()} to {last.lower()}, checking each expected value "
        "in the figure and its table."
    )


def exercise_titles(text):
    titles = re.findall(r"^\d\. \*\*(.+?)\.\*\*", text, flags=re.M)
    assert len(titles) == 6, titles
    return titles


def key_terms(text, key):
    """Require 3 to 5 distinct, defined Key terms bullets in each directly authored guide."""
    section = re.search(r"^#{2,3} Key terms\n\n((?:- .+\n)+)", text, flags=re.M)
    assert section, f"{key}: missing Key terms section"
    terms = re.findall(r"^- \*\*(.+?):\*\* (.+)$", section.group(1), flags=re.M)
    names = [name for name, _ in terms]
    assert 3 <= len(terms) <= 5, (key, names)
    assert len(set(names)) == len(names), (key, names)
    for name, definition in terms:
        assert len(definition.split()) >= 6 and definition.endswith("."), (key, name)
        assert not re.search("[\u2013\u2014]", name + definition), (key, name)
    return names


def reasoning_text(key):
    """Render the four-part solution reasoning authored in reasoning.json."""
    entry = REASONING.get(key)
    assert isinstance(entry, dict), f"{key}: missing solution reasoning"
    assert set(entry) == set(REASONING_LABELS), (key, sorted(entry))
    parts = []
    for field, label in REASONING_LABELS.items():
        body = entry[field].strip()
        assert len(body.split()) >= 20, (key, field)
        assert not re.search("[\u2013\u2014]", body), (key, field)
        parts.append(f"**{label}.** {body}")
    return "\n\n".join(parts)


def build():
    assert set(REASONING) == {f"viz-{n:03d}" for n in range(1, len(UNITS) + 1)}, sorted(REASONING)
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
                "lab": lab_text(BASE / "guides" / f"{key}.md"),
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
        write(ROOT / python_reference, format_python(standalone_python(number), f"{key}.py"))
        write(
            ROOT / js_reference,
            browser + f'\nawait renderCase(specifications[{number}](), "{key} Plotly complete");\n',
        )
        tasks = exercise_titles((BASE / "guides" / f"{key}.md").read_text(encoding="utf-8"))
        python_todos = "\n".join(
            f"    # TODO {index}: {task}." for index, task in enumerate(tasks, 1)
        )
        javascript_todos = "\n".join(
            f"// TODO {index}: {task}." for index, task in enumerate(tasks, 1)
        )
        write(
            ROOT / python_source,
            format_python(
                f'''"""{key}: learner source. Read the guide and keep your own saved draft."""

import plotly.graph_objects as go

FIXTURE = {fixture!r}


def build_figure():
    """Derive traces, axis titles and units from FIXTURE as the guide describes."""
    fig = go.Figure()
{python_todos}
    # Add traces with fig.add_trace(go.Bar(...)) or fig.add_trace(go.Scatter(...)).
    fig.update_layout(title="Describe the measured quantity and its units")
    return fig


def main():
    figure = build_figure()
    print("Fixture records:", FIXTURE)
    print("Traces so far:", len(figure.data))
    # When the figure and its table are complete, display it with figure.show().


if __name__ == "__main__":
    main()
''',
                f"{key}.py",
            ),
        )
        write(
            ROOT / js_source,
            f"""// {key}: learner source for the prepared browser Plotly variant.
// window.Plotly, #chart and #output are supplied. No imports or fetches.
{js_literal(fixture, prefix="const fixture = ", suffix=";")}
console.table(fixture);
// Derive your traces, caption and native source table from fixture.
{javascript_todos}
const traces = [];
const layout = {{ title: {{ text: "Describe the measured quantity and its units" }} }};
if (typeof Plotly !== "undefined" && traces.length > 0) {{
  Plotly.newPlot(document.getElementById("chart"), traces, layout);
}}
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
        solution += f"\n## Solution reasoning\n\n{reasoning_text(key)}\n"
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
        key_terms(text, key)
        heading, body = text.split("\n", 1)
        text = f"# {key}: {title}\n" + body
        if ANATOMY_START in text:
            before, rest = text.split(ANATOMY_START, 1)
            text = before + anatomy(number) + rest.split(ANATOMY_END, 1)[1]
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
