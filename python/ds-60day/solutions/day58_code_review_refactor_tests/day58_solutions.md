# Day 58 — Solutions: Code Review, Refactoring, and Tests

We refactor notebook logic into a module, write unit tests, configure pre‑commit hooks, and add a CI workflow.

Contents
- Exercise 1: Extract functions and add tests
- Exercise 2: Configure pre‑commit
- Exercise 3: GitHub Actions CI for lint+tests

---

Exercise 1 — Extract and test
```python
# src/myproj/fe.py
from __future__ import annotations
from typing import Iterable

def scale_minmax(xs: Iterable[float]) -> list[float]:
    xs = list(xs)
    mn, mx = min(xs), max(xs)
    if mx == mn:  # avoid divide by zero
        return [0.0 for _ in xs]
    return [(x-mn)/(mx-mn) for x in xs]
```

```python
# tests/test_fe.py
import pytest
from myproj.fe import scale_minmax

def test_scale_happy():
    assert scale_minmax([0,5,10]) == [0.0, 0.5, 1.0]

def test_scale_constant():
    assert scale_minmax([3,3,3]) == [0.0,0.0,0.0]
```
Run tests
```powershell
# Windows PowerShell
.\.venv\Scripts\python.exe -m pytest -q
```

```bash
# macOS or Linux
.venv/bin/python -m pytest -q
```

---

Exercise 2 — pre‑commit
```yaml
# .pre-commit-config.yaml
repos:
- repo: local
  hooks:
  - id: ruff-check
    name: Ruff check
    entry: ruff check --fix
    language: system
    types: [python]
  - id: ruff-format
    name: Ruff format
    entry: ruff format
    language: system
    types: [python]
```
Core setup already installs pre-commit. Install the local hook and run it:

```powershell
# Windows PowerShell
.\.venv\Scripts\python.exe -m pre_commit install
.\.venv\Scripts\python.exe -m pre_commit run --all-files
```

```bash
# macOS or Linux
.venv/bin/python -m pre_commit install
.venv/bin/python -m pre_commit run --all-files
```

---

Exercise 3 — CI workflow
```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v6
    - uses: actions/setup-python@v6
      with: { python-version: '3.12' }
    - run: python -m pip install -e ".[quality]"
    - run: ruff check .
    - run: ruff format --check .
    - run: pytest -q
```
Notes
- Keep PRs small and focused; require reviews
- Enforce status checks before merge

---

<!-- BEGIN ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Solution reasoning lens

A strong solution is not merely code that produces one plausible
output. It establishes a chain from input contract to operation to
verification:

1. **characterization test:** locks down important current behavior before extracting or renaming it.
2. **pure core + impure shell:** isolates transformations from I/O so normal, boundary, and failure cases are deterministic.
3. **Ruff + mypy + pytest:** checks formatting/lint, static type contracts, and executable behavior as complementary evidence.
4. **Verification:** Compare the result with an independent invariant, baseline, or failure case before interpreting it.

**Why this approach is appropriate:** Characterization evidence preserves intent while pure seams and precise failures make the improved design testable.

**Useful alternative:** Leave stable code unchanged when risk exceeds benefit; use an adapter/deprecation path when a public contract must evolve.

**Trade-off:** More abstraction can improve reuse and testing but increases indirection; extract around real responsibilities, not hypothetical reuse.

**Edge case to test:** Floating-point/rounding changes, exception type/message changes, ordering, mutation, file encoding, and public type narrowing can be breaking.

**Evidence of correctness:** Run old/new behavior on normal and boundary fixtures, test failure/side effects, check public types and deprecation, and pass formatter/linter/type/tests from a clean process.

When comparing your attempt with the reference, explain which of these
decisions your code made explicitly. If the reference makes a different
choice, compare the contracts and evidence before deciding that one
version is universally better.

<!-- END ADVANCED PYTHON CONCEPT ENRICHMENT -->

## Exercise-by-exercise reasoning map

This map connects every learner prompt to a reasoning path. Read the
explanation before copying code: the goal is to understand the assumptions,
the evidence that validates the result, and the edge cases that can make an
apparently correct implementation fail.

### Reasoning notes for original Exercise 1

**Prompt:** Move at least two notebook functions into a `src/` package and add tests.

**How to reason about it:** Extract deterministic transformation/model-building functions first and add tiny offline tests before changing behavior. Keep notebooks as reader-facing orchestration, not the only home of reusable logic.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** For task `Move at least two notebook functions into a src/ package and add tests`, state one precise claim, the evidence supporting it, the governing assumption, and a counterexample or limitation; then report row/feature shapes, seed/splitter, train-versus-validation evidence, and the metric used without consulting final-test labels.








### Reasoning notes for original Exercise 2

**Prompt:** Add type hints and docstrings, then run mypy.

**How to reason about it:** Type public boundaries and document inputs, outputs, assumptions, and failures. Run mypy on the real package; broad Any or unexplained ignores erase the value of the contract.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** For task `Add type hints and docstrings, then run mypy`, reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case; then state one precise claim, the evidence supporting it, the governing assumption, and a counterexample or limitation.








### Reasoning notes for original Exercise 3

**Prompt:** Write a short maintainer guide in the project root.

**How to reason about it:** A maintainer guide should cover setup, architecture, tests, formatting, data contracts, artifacts, security, and acceptance gates with Windows and POSIX commands where they differ.

Use the worked reference earlier in this file, then change one boundary
condition and rerun the stated checks. A copied output is not evidence
unless you can explain why that output follows from the inputs.

**Verify:** For task `Write a short maintainer guide in the project root`, state one precise claim, the evidence supporting it, the governing assumption, and a counterexample or limitation; then record the exact command/input, terminal result or returned value, and repeat the critical check from a clean process or fresh state.








### Exercise 4 — Characterization testing

**Prompt:** Before refactoring a legacy notebook function, capture current behavior for normal, boundary, and known-bug inputs. Mark which behavior is a contract and which bug will intentionally change.

**Reasoning before implementation:** Characterization tests prevent accidental drift; an intentional fix needs a new expected result and a documented reason.

Freeze representative fixtures and outputs before moving code. Include error
types/messages only to the degree they are part of the public contract. Then
refactor in small steps while the unchanged tests stay green.

For the known bug, first add a failing regression test that describes desired
behavior, then implement the fix. Do not quietly update all snapshots to accept
whatever the refactor produced.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** For task `Before refactoring a legacy notebook function, capture current behavior for normal, boundary,...`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case.








### Exercise 5 — Risk-based review

**Prompt:** Review a data-loading-to-prediction change using a checklist for security, data loss, leakage, schema compatibility, performance, error handling, and cross-platform paths.

**Reasoning before implementation:** Trace inputs to side effects and downstream consumers. Prioritize high-impact boundaries over cosmetic preferences.

Ask for evidence: tests, before/after contract, bounded benchmark, secret scan,
and fresh-environment command. Verify that unrelated dirty files are not mixed
into the change and that generated artifacts were regenerated from their
source.

Categorize comments by correctness/risk, maintainability, and optional style so
the author can act on the most important issues first.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** For task `Review a data-loading-to-prediction change using a checklist for security, data loss, leakage...`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then use identical data, split, metric, and budget for both sides; record a side-by-side result and isolate the condition that changed.








### Exercise 6 — Compatibility change

**Prompt:** Rename a public function parameter without breaking callers. Implement a deprecation path, tests for old/new usage, and a removal plan.

**Reasoning before implementation:** Accept the old keyword temporarily, reject ambiguous double use, emit a targeted DeprecationWarning, and update docs/call sites.

Compatibility is a time-bounded contract. The warning should name the new
parameter and intended removal version, use an appropriate stack level, and
avoid firing for unrelated code paths. Tests should assert both semantics and
warning behavior.

Search all repository references and update maintained examples. Remove the
alias only in a declared breaking release or after the documented migration
window.

**Why this matters:** The result should survive a fresh-kernel rerun and
a deliberately chosen boundary case. If it does not, revisit the
assumption or data boundary rather than hiding the failure.

**Verify:** For task `Rename a public function parameter without breaking callers. Implement a deprecation path, te...`, assert the return type/shape/value for the stated valid input and assert the named boundary or invalid input raises/returns exactly the documented behavior; then reproduce the failure first, capture its smallest observable symptom, apply one scoped fix, and rerun the failing plus normal case.
