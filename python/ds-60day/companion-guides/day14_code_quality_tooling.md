# Day 14 — Code Quality with Ruff, mypy, and pytest

**Level:** Beginner

Formatting, linting, static typing, and tests answer different questions. A
project needs all four signals, and this repository configures them in
`pyproject.toml`.

## Learning objectives

By the end of this lesson, you can:

- distinguish formatting, linting, type checking, and behavioral testing;
- run Ruff's linter and formatter without replacing repository configuration;
- interpret and fix a mypy error by narrowing or correcting a contract;
- make the smallest behavior-preserving fix, then rerun tests.

## Prerequisites

Complete Day 13 (`python-13`), Day 10 testing (`python-10`), and Day 5 type hints
(`python-05`).





<!-- BEGIN HOW TO RUN -->
## How to run this lesson

Work from the repository root. The rendered HTML lesson is a readable
preview; execute the real notebook in VS Code or JupyterLab.

1. Confirm the course environment before changing it:

   ```powershell
   # Windows PowerShell
   $CoursePython = if (Test-Path .\.venv\Scripts\python.exe) {
       (Resolve-Path .\.venv\Scripts\python.exe).Path
   } else {
       (Resolve-Path .\.venv\python.exe).Path
   }
   & $CoursePython scripts\course.py doctor
   ```

   ```bash
   # macOS/Linux
   .venv/bin/python scripts/course.py doctor
   ```

2. Read `python/ds-60day/companion-guides/day14_code_quality_tooling.md`, then open `python/ds-60day/notebooks/day14_code_quality_tooling.ipynb` from the repository
   folder in VS Code or JupyterLab.
3. Select **Python (ds60sqlpy)**. Do not run `%pip` in the notebook. If
   an import is missing, use the doctor and the catalog dependency label
   to repair the shared environment.
4. Restart the kernel and run from the first cell downward. Before every
   example, write a prediction; after it runs, compare the actual value,
   type, shape, or side effect with the stated observation.
5. Attempt each numbered exercise in its own work cell. Use the explicit
   verification as part of the task. Keep `solutions/` closed until you
   have a tested attempt or deliberately ask for help.

**Lesson outcome:** use day 14 — code quality with ruff, mypy, and pytest to practice automated formatting, linting, and static type feedback
and explain the evidence produced by your code.
<!-- END HOW TO RUN -->

<!-- BEGIN BEGINNER DEEP DIVE -->
## Beginner deep dive — build the idea before the syntax

### Start with one mental picture

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

### Vocabulary in plain language

- **formatter:** a tool that rewrites source layout consistently.
- **linter:** a static checker for selected code patterns and style rules.
- **type checker:** a tool that compares annotations and operations without running code.
- **diagnostic:** a tool report tied to a location and rule.
- **configuration:** shared settings controlling tool behavior.
- **suppression:** an explicit request to ignore one diagnostic, ideally with rationale.

### Syntax anatomy

`python -m ruff check path` chooses the repository interpreter, runs the
Ruff module, performs checks, and scopes them to `path`. `ruff format
--check` reports formatting drift without rewriting. A function
annotation such as `def total(values: list[float]) -> float:` gives
mypy a contract to compare with callers and return statements.

### Worked example 1 — Inspect annotations as documentation

Hints are stored but do not enforce runtime arguments by themselves. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
from typing import get_type_hints

def total(values: list[float]) -> float:
    return sum(values)

(get_type_hints(total), total([1.5, 2.0]))
```

**Expected observation**

```text
`({'values': list[float], 'return': float}, 3.5)` (representation may vary slightly). A type checker uses the hints before execution.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### Worked example 2 — Refactor a long expression into named facts

Formatting cannot choose meaningful names; design still belongs to the author. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
prices = [12.0, 8.0]
subtotal = sum(prices)
discount_rate = 0.10
discounted_total = subtotal * (1 - discount_rate)
round(discounted_total, 2)
```

**Expected observation**

```text
`18.0`. A formatter controls whitespace; the names make the calculation explainable.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### A debugging routine for this topic

When the output differs from your prediction, use this order:

1. Read the diagnostic rule and location before using an automatic fix.
2. Run formatter, linter, type checker, and tests separately so the failing contract is clear.
3. Use the repository interpreter to avoid invoking a globally installed tool with different versions.
4. If suppression is necessary, scope it narrowly and explain why the code is safe.

### Practice ramp

Work through the numbered exercises in five modes rather than treating all
of them as blank-code prompts:

1. **Prediction:** state the value, type, shape, rows, or side effect before
   execution.
2. **Guided modification:** change one part of a worked example and explain
   which part of the result must change.
3. **Independent application:** implement the same idea with a new input and
   an explicit contract.
4. **Debugging and edge cases:** reproduce a failure, identify the violated
   assumption, and prove the repair at a boundary.
5. **Retrieval:** close the guide and explain the core model from memory
   before moving on.

**Useful alternative:** Editor-on-save feedback is fast, while command-line checks are reproducible; continuous integration should run the same checked-in configuration.

**Boundary to remember:** Generated files, notebook code, untyped third-party libraries, version drift, and broad suppressions can create misleading results.
<!-- END BEGINNER DEEP DIVE -->

## Vocabulary and mental model

- **Formatter:** rewrites layout consistently.
- **Linter:** detects suspicious constructs, undefined names, import problems,
  and configured style issues.
- **Static type checker:** compares annotated contracts without executing every
  path.
- **Test suite:** executes selected behavior.
- **Quality gate:** a check that must pass before a change is accepted.

Ruff replaces Black and Flake8 in this repository. Do not add conflicting tool
configuration to a lesson project.

## Worked example

```python
def display_total(total: float | None) -> str:
    if total is None:
        return "not available"
    return f"${total:.2f}"
```

The explicit branch narrows `float | None` to `float` before formatting. This is
both a type-checker proof and useful runtime behavior.

## Run the quality gates

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m ruff format --check .
.\.venv\Scripts\python.exe -m mypy .
.\.venv\Scripts\python.exe -m pytest
```

macOS/Linux:

```bash
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
.venv/bin/python -m mypy .
.venv/bin/python -m pytest
```

## Exercises and progressive hints

Each item is a complete mini-contract. Before writing code, copy its input,
expected behavior, constraints, and verification into your work cell. A
result is not complete merely because it “looks right”; run the stated
assertion or inspection and explain what it proves.

1. Run Ruff formatting and lint checks on a small intentionally messy Python file. **Evidence:** record at least one formatter change and one lint diagnostic with its rule code. **Constraints:** understand each automatic fix, do not run broad fixes over unrelated repository files, and delete only the scratch file you created.
   **Verify:** both `ruff format --check` and `ruff check` pass afterward.

2. Add useful type hints to a function that accepts records and returns a numeric total, then run mypy on the file. **Introduce:** one wrong caller argument and one wrong return in scratch code so you can read both diagnostics.
   **Expected behavior:** mypy rejects both; after repair it reports success while runtime tests still pass.
   **Verify:** Save the two expected mypy diagnostics, repair both defects, and show mypy plus the runtime test command pass.

### Additional mastery practice

Use formatter, linter, type checker, and tests as complementary evidence. Read and fix one diagnostic at a time, then review behavior.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

3. **Prediction:** Given an unused import, inconsistent spacing, a possible `None` value, and a wrong result, predict which quality tool can detect each.
   **Progressive hint:** No single tool proves all four properties.
   **Verify:** Create a four-row matrix mapping each defect to formatter, linter, type checker, or test; run the tools and record which predictions were confirmed.
4. **Tracing:** Trace type narrowing for `str | None` through an explicit `is None` branch and state the type in each path.
   **Progressive hint:** A type checker follows control-flow evidence.
   **Verify:** Use `reveal_type` or equivalent diagnostics in both branches; confirm the non-None branch narrows to `str` and the absence branch cannot call string methods.
5. **Implementation:** Refactor an untyped file loader into a typed function using `Path`, a context manager, UTF-8, and a validated return shape.
   **Progressive hint:** Boundary validation can replace an unhelpfully broad `Any`.
   **Verify:** Type-check the loader, then test valid UTF-8 input plus missing column, invalid field type, and missing path boundaries.
6. **Debugging:** Replace an unexplained `# type: ignore` with a real narrowing or a narrow error-code ignore plus justification.
   **Progressive hint:** Do not suppress diagnostics before understanding the contract.
   **Verify:** Show the original diagnostic, replace suppression with narrowing where possible, and confirm any remaining ignore names one error code and rationale.
7. **Edge case and explanation:** Design a local/CI gate order and explain why formatter success should not prevent tests from running during diagnosis.
   **Progressive hint:** Fast static checks give feedback, but each signal remains independent.
   **Verify:** Run each gate independently on a deliberately broken scratch file and record its signal; confirm one early failure does not erase later diagnostic evidence.

Before opening the reference solution, write one sentence explaining
which contract or mental model each result confirms.

## Self-check

- Which tool changes layout, and which command checks without changing files?
- Why can mypy pass code that still raises at runtime?
- Why can pytest pass code containing an untested undefined path?
- Where should repository-wide tool settings live?

Expected behavior: all four commands exit successfully without adding Black,
Flake8, or tool-specific cache files to Git.

## Common pitfalls and diagnosis

- **Running a globally installed tool:** invoke it with the `.venv` interpreter
  so version and dependencies match the course.
- **Blindly using `# type: ignore`:** understand and fix the contract; if an
  ignore is essential, include the narrow error code and reason.
- **Formatter changes seem enormous:** run from the intended project path and
  honor `pyproject.toml` exclusions.
- **A lint autofix changes behavior:** review the diff and rerun tests.
- **Caches appear:** `.ruff_cache`, `.mypy_cache`, and `.pytest_cache` are
  disposable and already ignored.

## Continue

- [Open the learner notebook](../notebooks/day14_code_quality_tooling.ipynb)
- [Check the separate solution](../solutions/day14_code_quality_tooling/day14_solutions.md)
- [Next: Day 15 — CLI data tool project](day15_cli_project.md)

## Ask Codex about this lesson

Codex coaching is optional; the guide and notebook above contain the full
lesson. If you want a patient tutor, copy this prompt from the repository
root:

```text
Use $guide-ds60sqlpy-learning to tutor me through `python-14`
(Day 14 — Code Quality with Ruff, mypy, and pytest). I am a complete beginner. Emphasize automated formatting, linting, and static type feedback.
Read `python/ds-60day/companion-guides/day14_code_quality_tooling.md` and use the learner notebook
`python/ds-60day/notebooks/day14_code_quality_tooling.ipynb`. Do not open or quote anything under `solutions/` unless
I explicitly ask after making an honest attempt. Use these visible phases:
Explain, Predict, Attempt, Hint, Evidence, and Retrieval. First explain one
concept in plain language, then ask me to predict a small example and wait
for my attempt. Give only one progressive hint at a time. Help me run or
inspect my actual notebook evidence, adapt commands to my operating system,
and do not treat the rendered HTML preview as executable. Finish with 2-3
retrieval questions and one next step. Done when I can explain the mental
model without the guide, complete one independent exercise, and show the
prompt's verification evidence from my notebook.
```
