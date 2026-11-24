#!/usr/bin/env python3
"""Publish only the complete JAX course; never execute a learner program."""

from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
import tempfile
from dataclasses import replace
from pathlib import Path
from textwrap import indent

from model import HEADER, Case, Reasoning, Unit

ROOT = Path(__file__).resolve().parents[3]
SOURCE_ROOT = ROOT
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from scripts.format_inline_code import (  # noqa: E402
    Formatter,
    adapter_bytes,
    canonical_markdown,
    invoke,
)

BASE = "courses/jax"


def inline_adapter(source: bytes, language: str, suffix: str, root: Path) -> bytes:
    if language != "python":
        return adapter_bytes(source, language, suffix, root)
    return invoke(
        [
            sys.executable,
            "-m",
            "ruff",
            "format",
            "--no-cache",
            "--config",
            str(root / "pyproject.toml"),
            "--stdin-filename",
            "snippet.py",
            "-",
        ],
        source,
        root,
    )


def units() -> list[Unit]:
    from advanced import UNITS as advanced
    from composition import UNITS as composition
    from foundation import UNITS as foundations
    from reasoning import REASONING
    from records import RECORDS
    from scientific import UNITS as scientific

    result = [*foundations, *composition, *scientific, *advanced]
    result = [
        replace(
            unit,
            reasoning=REASONING.get(unit.number),
            records=RECORDS.get(unit.number, ()),
        )
        for unit in result
    ]
    numbers = [unit.number for unit in result]
    if numbers != list(range(1, len(result) + 1)):
        raise ValueError("JAX units must form one complete, unique ordered route")
    if {unit.level for unit in result} != {"beginner", "intermediate", "advanced"}:
        raise ValueError("Publish the complete route rather than placeholder stages")
    for unit in result:
        if len(unit.practice) != 6 or len({case.title for case in unit.practice}) != 6:
            raise ValueError(f"{unit.id} needs six distinct concrete tasks")
        if any(number >= unit.number for number in unit.prerequisites):
            raise ValueError(f"{unit.id} has a forward prerequisite")
        check_key_terms(unit)
        check_reasoning(unit)
        check_records(unit)
    return result


MIN_SOLUTION_WORDS = 700


def _words(text: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", text))


def check_reasoning(unit: Unit) -> None:
    """Require the four-part explained-reference reasoning for every unit."""
    reasoning = unit.reasoning
    if not isinstance(reasoning, Reasoning):
        raise ValueError(f"{unit.id} needs solution reasoning in reasoning.py")
    for name in ("approach", "correctness", "verification"):
        if _words(getattr(reasoning, name)) < 35:
            raise ValueError(f"{unit.id} reasoning {name} needs at least 35 words")
    if len(reasoning.pitfalls) != 6 or any(_words(text) < 18 for text in reasoning.pitfalls):
        raise ValueError(f"{unit.id} needs six wrong-approach notes of at least 18 words")
    if len(set(reasoning.pitfalls)) != 6:
        raise ValueError(f"{unit.id} wrong-approach notes must be distinct")
    texts = (reasoning.approach, reasoning.correctness, reasoning.verification, *reasoning.pitfalls)
    if any(dash in text for text in texts for dash in ("\u2013", "\u2014")):
        raise ValueError(f"{unit.id} reasoning contains an en or em dash")


def check_records(unit: Unit) -> None:
    """Reading units carry one fenced evidence-record sketch per worked example."""
    if unit.runtime != "reading":
        if unit.records:
            raise ValueError(f"{unit.id} runs code; evidence records are for reading units")
        return
    if len(unit.records) != len(unit.worked):
        raise ValueError(f"{unit.id} needs one evidence record per worked example")
    for record in unit.records:
        lines = record.strip().splitlines()
        if len(lines) < 5 or "```" in record:
            raise ValueError(f"{unit.id} evidence records need five or more unfenced lines")
        if any(dash in record for dash in ("\u2013", "\u2014")):
            raise ValueError(f"{unit.id} evidence record contains an en or em dash")


def check_key_terms(unit: Unit) -> None:
    """Require three to five distinct, defined, lesson-specific vocabulary entries."""
    names = [term.lower() for term, _ in unit.key_terms]
    if not 3 <= len(names) <= 5 or len(set(names)) != len(names):
        raise ValueError(f"{unit.id} needs three to five distinct key terms")
    for term, definition in unit.key_terms:
        if not term.strip() or any(mark in term for mark in ("*", ":", "\n")):
            raise ValueError(f"{unit.id} has an invalid key term name {term!r}")
        if len(definition.split()) < 6 or not definition.endswith("."):
            raise ValueError(f"{unit.id} key term {term!r} needs a one-sentence definition")
        if any(dash in term + definition for dash in ("\u2013", "\u2014")):
            raise ValueError(f"{unit.id} key term {term!r} contains an en or em dash")


def _bound_names(node: ast.stmt) -> set[str]:
    """Names a top-level setup statement binds."""
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return {node.name}
    if isinstance(node, (ast.Import, ast.ImportFrom)):
        return {(alias.asname or alias.name).split(".")[0] for alias in node.names}
    targets = []
    if isinstance(node, ast.Assign):
        targets = node.targets
    elif isinstance(node, (ast.AnnAssign, ast.AugAssign)):
        targets = [node.target]
    return {
        name.id
        for target in targets
        for name in ast.walk(target)
        if isinstance(name, ast.Name) and isinstance(name.ctx, ast.Store)
    }


def _used_names(source: str) -> set[str]:
    return {node.id for node in ast.walk(ast.parse(source)) if isinstance(node, ast.Name)}


def used_setup(setup: str, codes: list[str]) -> str:
    """Keep only setup statements that the selected cases need, in their original order.

    Statements that bind no name (for example a configuration call) are always kept.
    """
    if not setup.strip():
        return ""
    tree = ast.parse(setup)
    lines = setup.splitlines()
    statements = [(node, _bound_names(node)) for node in tree.body]
    keep = [not bound for _, bound in statements]
    required = set().union(*(_used_names(code) for code in codes))
    for index, (node, _) in enumerate(statements):
        if keep[index]:
            required |= {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}
    setup_bound = set().union(*(bound for _, bound in statements))

    def registers_on_kept(node: ast.stmt) -> bool:
        # A decorator such as @function.defjvp registers a rule on a kept setup object.
        kept_bound = set().union(*(b for (_, b), k in zip(statements, keep, strict=True) if k))
        roots = {
            name.id
            for decorator in getattr(node, "decorator_list", [])
            for name in ast.walk(decorator)
            if isinstance(name, ast.Name)
        }
        return bool(roots & setup_bound & kept_bound)

    changed = True
    while changed:
        changed = False
        for index, (node, bound) in enumerate(statements):
            if not keep[index] and (bound & required or registers_on_kept(node)):
                keep[index] = changed = True
                required |= {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}

    def span(index: int) -> tuple[int, int]:
        node = statements[index][0]
        decorators = getattr(node, "decorator_list", [])
        return min([node.lineno, *(item.lineno for item in decorators)]) - 1, node.end_lineno

    output: list[str] = []
    previous = None
    for index, kept in enumerate(keep):
        if not kept:
            continue
        first, last = span(index)
        if previous is not None and index == previous + 1:
            # Adjacent statements keep the original blank lines and comments between them.
            output += lines[span(previous)[1] : last]
        else:
            while first > 0 and lines[first - 1].lstrip().startswith("#"):
                first -= 1
            output += ["", ""] if output else []
            output += lines[first:last]
        previous = index
    return "\n".join(output)


def program(unit: Unit, cases: tuple[Case, ...]) -> str:
    setup_lines = unit.setup.strip().splitlines()
    extra_imports = [line for line in setup_lines if line.startswith(("import ", "from "))]
    setup = "\n".join(line for line in setup_lines if line not in extra_imports).strip()
    codes = [item.code for item in cases]
    setup = used_setup(setup, codes)
    used = set().union(*(_used_names(code) for code in [*codes, setup or "pass"]))
    extra_imports = [line for line in extra_imports if _bound_names(ast.parse(line).body[0]) & used]
    header = HEADER.replace(
        "# Choose precision", "\n".join(extra_imports) + "\n\n# Choose precision"
    )
    if "math" not in used:
        header = header.replace("import math\n", "", 1)
    if "jnp" not in used:
        header = header.replace("import jax.numpy as jnp\n", "", 1)
    if "close" not in used:
        start = header.index("\n\ndef close(")
        header = header[:start] + "\n"
        if "np" not in used:
            header = header.replace("import numpy as np\n", "", 1)
    body = []
    for index, item in enumerate(cases, 1):
        body.append(f"# Case {index}: {item.title}\n{item.code}")
    noun = "case" if len(cases) == 1 else "cases"
    body.append(f'print("{unit.id}: {len(cases)} asserted {noun} passed")')
    return (
        header
        + setup
        + "\n\n\ndef main():\n"
        + indent("\n\n".join(body), "    ")
        + '\n\n\nif __name__ == "__main__":\n    main()\n'
    )


# Calls that construct or compare literals; naming them would not help a learner.
ROUTINE_CALLS = {
    "AssertionError",
    "Path",
    "abs",
    "all",
    "any",
    "bool",
    "close",
    "compare",
    "dict",
    "enumerate",
    "float",
    "int",
    "isinstance",
    "jnp.array",
    "jnp.asarray",
    "len",
    "list",
    "max",
    "min",
    "np.allclose",
    "np.array",
    "np.asarray",
    "np.isclose",
    "np.testing.assert_allclose",
    "print",
    "range",
    "repr",
    "round",
    "set",
    "sorted",
    "str",
    "sum",
    "tuple",
    "type",
    "zip",
}


def _call_name(func: ast.expr) -> str | None:
    parts = []
    node = func
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        name = ".".join([node.id, *reversed(parts)])
        if node.id in {"jax", "jnp", "lax", "np", "math", "tempfile"} or not parts:
            return name
        return "." + parts[0]
    if isinstance(func, ast.Attribute):
        inner = func.value
        if isinstance(inner, ast.Subscript) and isinstance(inner.value, ast.Attribute):
            return f".{inner.value.attr}[...].{func.attr}"
        return "." + func.attr
    return None


def _quoted_list(items: list[str]) -> str:
    quoted = [f"`{item}`" for item in items]
    return quoted[0] if len(quoted) == 1 else ", ".join(quoted[:-1]) + " and " + quoted[-1]


def second_hint(item: Case) -> str:
    """A second, more specific hint derived from the exercise's own reference code."""
    tree = ast.parse(item.code)
    nodes = sorted(
        (node for node in ast.walk(tree) if hasattr(node, "lineno")),
        key=lambda node: (node.lineno, node.col_offset),
    )
    calls: list[str] = []
    errors: list[str] = []
    checks = 0
    # Names the reference binds itself (for example a compiled function) are not hints.
    local = {
        node.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store)
    }
    for node in nodes:
        if isinstance(node, ast.Call):
            name = _call_name(node.func)
            if name in {"close", "compare"}:
                checks += 1
            elif name and name not in ROUTINE_CALLS | local and name not in calls:
                calls.append(name)
        elif isinstance(node, ast.Assert):
            checks += 1
        elif isinstance(node, ast.ExceptHandler) and isinstance(
            node.type, (ast.Name, ast.Attribute)
        ):
            error = _call_name(node.type) or ""
            if error and error not in errors:
                errors.append(error)
    parts = []
    if calls:
        parts.append(f"The reference solution calls {_quoted_list(calls[:5])}")
    else:
        parts.append(
            "The reference solution needs no new function: it combines arrays from the setup "
            "with arithmetic, indexing or broadcasting"
        )
    if errors:
        parts.append(
            f"and treats {_quoted_list(errors)} as the passing outcome, failing if the call returns"
        )
    elif checks:
        noun = "assertion" if checks == 1 else "assertions"
        parts.append(f"and then makes {checks} {noun} against the expected observation")
    return " ".join(parts) + "."


def render(unit: Unit) -> dict[str, str]:
    key = unit.id
    prefix = f"{BASE}/"
    prerequisites = (
        ", ".join(f"`jax-{n:03d}`" for n in unit.prerequisites) or "No prior JAX knowledge."
    )
    sections = [
        f"# {key}: {unit.title}\n\n## Starting point and outcome\n\n"
        f"{unit.level.title()}. Direct prerequisites: {prerequisites}\n\n{unit.outcome}\n",
        "## Mechanism and purpose\n\n" + unit.narrative.strip(),
        "## Key terms\n\n"
        + "\n".join(f"- **{term}:** {definition}" for term, definition in unit.key_terms),
        "## Derivation and shape contract\n\n" + unit.derivation.strip(),
    ]
    if unit.runtime == "reading":
        sections.append(
            "## Reading and evidence boundary\n\nThis unit uses written traces and a separate "
            "explanation. It does not start a device, process group, server or cluster. "
            "Any external execution needs the explicit preparation and evidence described below."
        )
    else:
        first, second = unit.worked
        sections.append(
            "## Run this investigation\n\n"
            f"Open `{key}` under the **JAX** subject in `/classroom` with its prepared `jax-cpu` "
            f"profile. Worked example 1, *{first.title}*, and worked example 2, *{second.title}*, "
            "are complete programs that include only the setup they use and each print "
            f"`{key}: 1 asserted case passed`. The learner file `{prefix}lessons/{key}.py` leaves "
            f"the six exercises, from *{unit.practice[0].title}* to *{unit.practice[-1].title}*, "
            f"for you to implement; the complete reference prints `{key}: 8 asserted cases "
            "passed`. Every program enables 64-bit arithmetic before creating arrays, a course "
            "choice since JAX defaults to 32 bit, and every Run is a fresh Python process, so "
            "save source and notes before replacing an attempt. A passing assertion supports "
            "its stated contract only, not statistical validity, mastery or accelerator "
            "performance."
        )
    sections.append("## Worked investigations")
    for number, item in enumerate(unit.worked, 1):
        sections.append(
            f"### Worked example {number}: {item.title}\n\n{item.task}\n\n"
            f"{item.explanation}\n\n**Expected:** {item.expected}\n\n"
            + (
                f"```python\n{program(unit, (item,))}```"
                if unit.runtime != "reading"
                else f"{item.code}\n\n**Evidence record sketch:**\n\n"
                f"```text\n{unit.records[number - 1].strip()}\n```"
            )
        )
    sections.append("## Exercises")
    for number, item in enumerate(unit.practice, 1):
        sections.append(
            f"### Exercise {number}: {item.title}\n\n{item.task}\n\n"
            f"**Expected:** {item.expected}\n\n**Verify:** {item.explanation}\n\n"
            + (
                f"**Hint:** {item.hint}"
                if unit.runtime == "reading"
                else f"**Hint 1:** {item.hint}\n\n**Hint 2:** {second_hint(item)}"
            )
        )
    sections.extend(
        [
            "## Diagnosis and boundaries\n\n" + unit.diagnosis,
            "## Transfer and review\n\n" + unit.transfer,
            "## Primary references\n\n"
            + "\n".join(f"- [{title}]({url})" for title, url in unit.sources),
            "## Ask an AI tutor about this lesson\n\n"
            f"Use the checked-in $guide-ds60sqlpy-learning skill for `{key}` ({unit.title}), "
            f"focusing on {', '.join(unit.concepts)}. Start with my own prediction and source "
            f"for one exercise, such as *{unit.practice[2].title}*. Ask me to explain one "
            "intermediate shape, derivative or state transition, then give a progressive hint "
            "for the first incorrect assumption. Distinguish authored examples, my actual saved "
            "run output and any hardware or population claim requiring additional evidence.",
        ]
    )
    reasoning = unit.reasoning
    assert reasoning is not None
    explanation = [
        f"# {key}: explained reference\n\n" + unit.derivation,
        "## Solution approach\n\n"
        + reasoning.approach
        + "\n\n**Why it is correct here:** "
        + reasoning.correctness,
    ]
    for number, item in enumerate(unit.practice, 1):
        explanation.append(
            f"## Exercise {number}: {item.title}\n\n{item.explanation}\n\n"
            f"**Expected:** {item.expected}\n\n"
            + (f"```python\n{item.code}\n```" if unit.runtime != "reading" else item.code)
            + f"\n\n**Plausible wrong approach:** {reasoning.pitfalls[number - 1]}"
        )
    explanation.append("## How to verify\n\n" + reasoning.verification)
    explanation.append("## Scope of this evidence\n\n" + unit.diagnosis + "\n\n" + unit.transfer)
    solution_text = "\n\n".join(explanation) + "\n"
    if _words(solution_text) < MIN_SOLUTION_WORDS:
        raise ValueError(
            f"{key} explained reference has {_words(solution_text)} words; "
            f"needs at least {MIN_SOLUTION_WORDS}"
        )
    result = {
        f"{prefix}guides/{key}.md": "\n\n".join(sections) + "\n",
        f"{prefix}solutions/{key}_solutions.md": solution_text,
    }
    if unit.runtime == "reading":
        result[f"{prefix}lessons/{key}.md"] = (
            f"# {key}: reasoning worksheet\n\n"
            + "\n\n".join(
                f"## Exercise {i}: {item.title}\n\n{item.task}\n\nRecord your evidence and limits."
                for i, item in enumerate(unit.practice, 1)
            )
            + "\n"
        )
    else:
        result[f"{prefix}solutions/{key}_solution.py"] = program(unit, unit.worked + unit.practice)
        stubs = []
        for number, item in enumerate(unit.practice, 1):
            stubs.append(
                f"# Exercise {number}: {item.title}\n"
                f"# {item.task}\n"
                f"def exercise_{number}():\n"
                f"    raise NotImplementedError({item.title!r})\n"
            )
        result[f"{prefix}lessons/{key}.py"] = (
            HEADER
            + "\n\n".join(stubs)
            + '\n\nif __name__ == "__main__":\n'
            + "".join(f"    exercise_{number}()\n" for number in range(1, 7))
        )
    return result


def artifacts() -> dict[str, str]:
    result: dict[str, str] = {}
    plan, authored = [], []
    for unit in units():
        result.update(render(unit))
        plan.append(
            {
                "id": unit.id,
                "title": unit.title,
                "level": unit.level,
                "minutes": 100 if unit.level == "beginner" else 140,
                "prerequisites": [f"jax-{n:03d}" for n in unit.prerequisites],
                "runtime": unit.runtime,
                "concepts": list(unit.concepts),
                "outcome": unit.outcome,
                "lab": unit.worked[0].task,
                "verification": unit.worked[0].expected,
            }
        )
        reading = unit.runtime == "reading"
        authored.append(
            {
                "id": unit.id,
                "status": "authored",
                "language": "markdown" if reading else "python",
                "runtime_profile": unit.runtime,
                "guide_path": f"{BASE}/guides/{unit.id}.md",
                "source_path": f"{BASE}/lessons/{unit.id}.{'md' if reading else 'py'}",
                "solution_paths": ([] if reading else [f"{BASE}/solutions/{unit.id}_solution.py"])
                + [f"{BASE}/solutions/{unit.id}_solutions.md"],
                "verification_id": None,
            }
        )
    result[f"{BASE}/track.json"] = (
        json.dumps(
            {
                "schema_version": 1,
                "id": "jax",
                "title": "JAX: numerical functions to independent scientific work",
                "summary": "An offline CPU route through functional state, transformations, differentiation, training, scientific computing and measured systems tradeoffs, with explicit optional hardware boundaries.",
                "lessons": plan,
            },
            indent=2,
        )
        + "\n"
    )
    result[f"{BASE}/lessons.json"] = (
        json.dumps({"schema_version": 1, "track_id": "jax", "lessons": authored}, indent=2) + "\n"
    )
    # Match the repository's pinned Python formatter without importing any
    # learner program or requiring JAX in the authoring environment.
    with tempfile.TemporaryDirectory(prefix="jax-source-format-") as temporary:
        staging = Path(temporary)
        paths = []
        for relative, text in result.items():
            if relative.endswith(".py"):
                path = staging / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(text, encoding="utf-8", newline="\n")
                paths.append(str(path))
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ruff",
                "format",
                "--no-cache",
                "--config",
                str(ROOT / "pyproject.toml"),
                *paths,
            ],
            capture_output=True,
            text=True,
            check=False,
            timeout=60,
        )
        if completed.returncode:
            raise ValueError("JAX source formatting failed: " + completed.stdout + completed.stderr)
        for relative in result:
            if relative.endswith(".py"):
                result[relative] = (staging / relative).read_text(encoding="utf-8")
    formatter = Formatter(SOURCE_ROOT, adapter=inline_adapter)
    for relative, text in result.items():
        if relative.endswith(".md"):
            result[relative] = canonical_markdown(
                text, root=SOURCE_ROOT, path=relative, formatter=formatter
            )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    different = []
    for relative, text in artifacts().items():
        path = ROOT / relative
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                different.append(relative)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8", newline="\n")
    if different:
        print("JAX artifacts differ:\n" + "\n".join(different))
        return 1
    print("JAX content checked" if args.check else "JAX content generated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
