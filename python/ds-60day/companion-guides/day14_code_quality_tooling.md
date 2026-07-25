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

## Exercise and progressive hint

Run all four checks on utilities from earlier days. Predict what each tool will
report, then make the smallest behavior-preserving fixes. **Hint:** process one
diagnostic at a time from the first file; an early syntax/import issue can cause
many downstream messages. Finish with pytest because clean static output does
not prove correct behavior.

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
