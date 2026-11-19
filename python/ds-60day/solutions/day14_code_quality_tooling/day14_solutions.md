# Day 14 Solutions: Code Quality with Ruff, mypy, and pytest

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

These worked answers demonstrate **automated formatting, linting, and static type feedback**. Predict each named
result before comparing your attempt with its matching assertions.

Code-quality tools answer different questions. A formatter applies one
consistent layout. A linter detects selected suspicious or inconsistent
patterns. A static type checker compares annotated contracts without
executing the program. Tests still check runtime behavior; no one tool
replaces the others.

Treat tool output as a precise diagnostic: file, line, rule, and
message. Understand a warning before suppressing it, make the smallest
change, then rerun the narrow command. Configuration belongs in
`pyproject.toml` so developers and continuous integration use the same
rules.

### Vocabulary used in the worked answers

- **formatter:** a tool that rewrites source layout consistently.
- **linter:** a static checker for selected code patterns and style rules.
- **type checker:** a tool that compares annotations and operations without running code.
- **diagnostic:** a tool report tied to a location and rule.
- **configuration:** shared settings controlling tool behavior.
- **suppression:** an explicit request to ignore one diagnostic, ideally with rationale.

### How to compare an answer

For this lesson's **automated formatting, linting, and static type feedback** model, follow the exact values from each learner contract through its function or expression to the assertion that proves the expected behavior; then change one boundary input and make that assertion fail once before accepting the answer.
<!-- END BEGINNER SOLUTION REVIEW -->

## Exercises 1-2: Worked answers

### Exercise 1: worked answer

**Learner contract:** Run Ruff formatting and lint checks on a small intentionally messy Python file. **Evidence:** record at least one formatter change and one lint diagnostic with its rule code. **Constraints:** understand each automatic fix, do not run broad fixes over unrelated repository files, and delete only the scratch file you created. **Verify:** use the pad recipe in "Run the quality gates from the classroom pad" with your own messy source; afterwards `ruff format --diff` reports `1 file already formatted` and `ruff check` reports `All checks passed!`.

**Reasoning:** Each tool answers a different question, so run them separately and keep each report: `ruff format --diff` shows layout changes without applying them, and `ruff check` names rule violations with codes such as `F401` for an unused import. Reading the diff before accepting a fix is the point of the exercise; running `--fix` across a repository would make unrelated changes that nobody reviewed. The block below uses the same child-process approach as the guide's pad recipe on a three-line scratch file, and `--isolated` keeps the run independent of any project configuration.

Use a small scratch file and run each tool independently. In the classroom pad,
the helper below writes the source to a temporary folder and runs one tool on
it as a child process; in a prepared contributor checkout, the same checks are
`uv run --no-sync python -m ruff format --diff scratch.py` and
`uv run --no-sync python -m ruff check scratch.py`.

```python
import os
import subprocess
import sys
import tempfile
from pathlib import Path

PLAIN = {key: value for key, value in os.environ.items() if "COLOR" not in key} | {"NO_COLOR": "1"}
MYPY = ["mypy", "--config-file=", f"--cache-dir={os.devnull}"]


def run_tool(arguments: list[str], source: str) -> str:
    """Write source to scratch.py, run one tool on it, and return its report."""
    with tempfile.TemporaryDirectory(prefix="day14-") as folder:
        (Path(folder) / "scratch.py").write_text(source, encoding="utf-8")
        result = subprocess.run(
            [sys.executable, "-m", *arguments, "scratch.py"],
            cwd=folder,
            env=PLAIN,
            capture_output=True,
            text=True,
            timeout=120,
        )
    return (result.stdout + result.stderr).strip()


messy = "import sys\nx=1\nprint( x )\n"
layout = run_tool(["ruff", "format", "--isolated", "--diff"], messy)
lint = run_tool(["ruff", "check", "--isolated", "--output-format=concise"], messy)
print(layout)
print(lint)
assert "+x = 1" in layout and "+print(x)" in layout
assert "F401" in lint
```

Ruff formatting owns layout; Ruff checks selected static patterns; mypy
checks annotated type consistency; pytest checks runtime contracts.
Save one diagnostic from each deliberate defect, repair it, then rerun.

### Exercise 2: worked answer

**Learner contract:** Add useful type hints to a function that accepts records and returns a numeric total, then run mypy on the file. **Introduce:** one wrong caller argument and one wrong return in scratch code so you can read both diagnostics. **Expected behavior:** mypy rejects both; after repair it reports success while runtime tests still pass. **Verify:** Save the two expected mypy diagnostics, repair both defects, and show mypy plus the runtime test command pass.

**Reasoning:** Annotating `records` as an iterable of `Record` and the result as `float` gives mypy a contract to check at every call site. The two deliberate defects produce two different diagnostics: a caller passing `"2.5"` for `amount` is reported as an incompatible TypedDict item, and returning `str(...)` is reported as an incompatible return value. Neither defect stops the program from starting, which is exactly why a static check helps: it finds both before any test runs. After the repair, mypy reports success and the runtime assertion still proves the arithmetic.

```python
from collections.abc import Iterable
from typing import TypedDict


class Record(TypedDict):
    amount: float


def total_amount(records: Iterable[Record]) -> float:
    return sum(record["amount"] for record in records)


assert total_amount([{"amount": 2.5}, {"amount": 1.5}]) == 4.0
```

Mypy rejects `{"amount": "2.5"}` and a string return before runtime;
the assertion still proves the valid runtime calculation.

```python
broken = """from collections.abc import Iterable
from typing import TypedDict


class Record(TypedDict):
    amount: float


def total_amount(records: Iterable[Record]) -> float:
    return str(sum(record["amount"] for record in records))


total_amount([{"amount": "2.5"}])
"""
report = run_tool(MYPY, broken)
print(report)
assert "[return-value]" in report and "[typeddict-item]" in report
```

## Exercises 3-7: Expanded mastery answers

### Exercise 3: answer contract

**Learner contract:** **Prediction:** Given an unused import, inconsistent spacing, a possible `None` value, and a wrong result, predict which quality tool can detect each. **Progressive hint:** No single tool proves all four properties. **Verify:** Create a four-row matrix mapping each defect to formatter, linter, type checker, or test; run the tools and record which predictions were confirmed.

**Reasoning:** No single tool covers all four defects. Ruff's linter reports the unused import, Ruff's formatter reports the inconsistent spacing, mypy reports a method call on a value that may be `None`, and only a test with a known expected value catches the wrong result, because the other tools never run the code. The shared implementation for Exercises 3-4 runs all three static tools on one file containing the four defects and then calls the function to expose the wrong total. Treating a clean lint and type check as proof of correct behavior is the trap this exercise targets.

### Exercise 4: answer contract

**Learner contract:** **Tracing:** Trace type narrowing for `str | None` through an explicit `is None` branch and state the type in each path. **Progressive hint:** A type checker follows control-flow evidence. **Verify:** Capture `reveal_type` or equivalent type-checker output in both branches; assert the non-None branch reports `str` and the absence branch reports an error for a string-method call.

**Reasoning:** mypy follows control flow: inside `if value is None:` it knows `value` is `None`, and after that branch returns it knows `value` must be `str`. `reveal_type` asks mypy to print its inferred type at that point; the shared implementation for Exercises 3-4 runs mypy on such a file and asserts `Revealed type is "None"` in the first branch and `Revealed type is "str"` after it. Calling `value.upper()` before the check fails with `Item "None" of "str | None" has no attribute "upper"`. Remove `reveal_type` calls after use; at runtime the name exists only when imported from `typing`.

### Exercise 5: answer contract

**Learner contract:** **Implementation:** Refactor an untyped file loader into a typed function using `Path`, a context manager, UTF-8, and a validated return shape. **Progressive hint:** Boundary validation can replace an unhelpfully broad `Any`. **Verify:** Type-check the loader, then test valid UTF-8 input plus missing column, invalid field type, and missing path boundaries.

**Reasoning:** `json.load` returns `Any`, so the function validates the decoded value before claiming the precise type `dict[str, str]`: it must be a JSON object, and every key and value must be a string. That runtime check is what makes the return annotation true, unlike a `cast`, which only silences mypy. Opening with `Path(path).open(encoding="utf-8")` inside `with` closes the file on every exit and avoids the platform's default encoding. The added checks cover a valid file, a JSON list, a non-string value, and a missing path, which raises `FileNotFoundError` unchanged.

### Exercise 6: answer contract

**Learner contract:** **Debugging:** Replace an unexplained `# type: ignore` with a real narrowing or a narrow error-code ignore plus justification. **Progressive hint:** Do not suppress diagnostics before understanding the contract. **Verify:** Show the original diagnostic, replace suppression with narrowing where possible, and confirm any remaining ignore names one error code and rationale.

**Reasoning:** A bare `# type: ignore` silences every error on its line, including future, unrelated ones. The first choice is to remove the cause by narrowing the type with an `isinstance` check or an explicit `None` branch, as the loader does before returning. When an ignore is genuinely needed, for example around an untyped third-party call, name the error code (`# type: ignore[arg-type]`) and add a short reason so the suppression stays narrow and reviewable. Running mypy with `--warn-unused-ignores` reports ignores that no longer suppress anything.

### Exercise 7: answer contract

**Learner contract:** **Edge case and explanation:** Design a local/CI gate order and explain why formatter success should not prevent tests from running during diagnosis. **Progressive hint:** Fast static checks give feedback, but each signal remains independent. **Verify:** Run each gate independently on a deliberately broken scratch file and record its signal; confirm one early failure does not erase later diagnostic evidence.

**Reasoning:** A sensible local and CI order runs the fast static checks first (environment check, Ruff lint, Ruff format check, mypy) and the slower tests last, but each gate is an independent signal. During diagnosis, a formatting failure says nothing about behavior, so stopping at the first failure can hide a failing test that matters more. CI should run the gates as separate steps or report every failure, and locally you can rerun the one failing command directly. The four-defect file in the shared implementation for Exercises 3-4 shows each tool reporting only its own kind of problem.

## Expanded mastery lab solutions

Use formatter, linter, type checker, and tests as complementary evidence. Read and fix one diagnostic at a time, then review behavior.

### Shared implementation for Exercises 3-4: Match evidence to the question

- Ruff reports unused imports and configured lint rules.
- Ruff format checks layout.
- mypy can report use of a possible `None`.
- pytest can expose the wrong result only when a test exercises it.

```python
def display(value: str | None) -> str:
    if value is None:
        return "missing"  # Here value is None.
    return value.upper()  # Here mypy narrows value to str.
```

The block below runs the three static tools on one file containing all four
defects, then calls the function to expose the wrong result, and finally asks
mypy to reveal the narrowed types:

```python
four_defects = """import os


def total(values: list[float]) -> float:
    return sum(values)  +  1


def label(value: str | None) -> str:
    return value.upper()
"""
print(run_tool(["ruff", "format", "--isolated", "--diff"], four_defects))
print(run_tool(["ruff", "check", "--isolated", "--output-format=concise"], four_defects))
print(run_tool(MYPY, four_defects))
namespace: dict[str, object] = {}
exec(four_defects, namespace)
print("total([1.0, 2.0]) =", namespace["total"]([1.0, 2.0]), "but the contract says 3.0")

narrowing = """def display(value: str | None) -> str:
    if value is None:
        reveal_type(value)
        return "missing"
    reveal_type(value)
    return value.upper()
"""
revealed = run_tool(MYPY, narrowing)
print(revealed)
assert 'Revealed type is "None"' in revealed and 'Revealed type is "str"' in revealed
```

### Shared implementation for Exercises 5-7: Validate boundaries instead of silencing them

```python
from __future__ import annotations

import json
from pathlib import Path


def load_string_map(path: str | Path) -> dict[str, str]:
    """Load a JSON object whose keys and values are strings."""

    resolved = Path(path)
    with resolved.open(encoding="utf-8") as handle:
        decoded = json.load(handle)

    # Runtime validation earns a precise return type.
    if not isinstance(decoded, dict):
        raise ValueError("expected a JSON object")
    if not all(isinstance(key, str) and isinstance(value, str) for key, value in decoded.items()):
        raise ValueError("expected string keys and string values")
    return decoded


with tempfile.TemporaryDirectory() as folder:
    good = Path(folder) / "good.json"
    good.write_text('{"city": "Zürich"}', encoding="utf-8")
    assert load_string_map(good) == {"city": "Zürich"}
    for name, text in (("list.json", "[1, 2]"), ("number.json", '{"count": 3}')):
        bad = Path(folder) / name
        bad.write_text(text, encoding="utf-8")
        try:
            load_string_map(bad)
        except ValueError:
            pass
        else:
            raise AssertionError(f"{name} should be rejected")
    try:
        load_string_map(Path(folder) / "missing.json")
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("a missing path should raise FileNotFoundError")
```

A useful gate order is lock/environment check, Ruff lint, Ruff format check,
mypy, then pytest. During debugging, run the narrow failing command directly;
in CI, configure independent steps or always inspect every gate so a formatter
failure does not hide a behavioral failure.
