# Day 14 — Solutions: Code Quality with Ruff and mypy

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

The solution is not a typing template. Read the learner contract, predict
the result, then compare decisions and evidence. The central mental model is
**automated formatting, linting, and static type feedback**.

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

### Reference pattern 1 — Inspect annotations as documentation

Hints are stored but do not enforce runtime arguments by themselves.

```python
from typing import get_type_hints

def total(values: list[float]) -> float:
    return sum(values)

(get_type_hints(total), total([1.5, 2.0]))
```

**Expected observation:** `({'values': list[float], 'return': float}, 3.5)` (representation may vary slightly). A type checker uses the hints before execution.

### Reference pattern 2 — Refactor a long expression into named facts

Formatting cannot choose meaningful names; design still belongs to the author.

```python
prices = [12.0, 8.0]
subtotal = sum(prices)
discount_rate = 0.10
discounted_total = subtotal * (1 - discount_rate)
round(discounted_total, 2)
```

**Expected observation:** `18.0`. A formatter controls whitespace; the names make the calculation explainable.

## Exercise-by-exercise reasoning map

The numbering and learner contracts below match the guide and notebook.
Each entry explains what to reason about, how to inspect the worked code,
an alternative, an edge case, and the evidence required for completion.

### Exercise 1 — reasoning, alternatives, and proof

**Learner contract:** Run Ruff formatting and lint checks on a small intentionally messy Python file. **Evidence:** record at least one formatter change and one lint diagnostic with its rule code. **Constraints:** understand each automatic fix, do not run broad fixes over unrelated repository files, and delete only the scratch file you created. **Verify:** both `ruff format --check` and `ruff check` pass afterward.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies automated formatting, linting, and static type feedback.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Editor-on-save feedback is fast, while command-line checks are reproducible; continuous integration should run the same checked-in configuration.

**Edge case:** Generated files, notebook code, untyped third-party libraries, version drift, and broad suppressions can create misleading results.

**Solution evidence to inspect:** both `ruff format --check` and `ruff check` pass afterward.

### Exercise 2 — reasoning, alternatives, and proof

**Learner contract:** Add useful type hints to a function that accepts records and returns a numeric total, then run mypy on the file. **Introduce:** one wrong caller argument and one wrong return in scratch code so you can read both diagnostics. **Expected behavior:** mypy rejects both; after repair it reports success while runtime tests still pass. **Verify:** Save the two expected mypy diagnostics, repair both defects, and show mypy plus the runtime test command pass.

**Reasoning before code:** Reproduce the bad behavior on the smallest input, state the violated contract, make one repair, and rerun both the failing boundary and a normal case. Keep the diagnosis grounded in automated formatting, linting, and static type feedback.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Editor-on-save feedback is fast, while command-line checks are reproducible; continuous integration should run the same checked-in configuration.

**Edge case:** Generated files, notebook code, untyped third-party libraries, version drift, and broad suppressions can create misleading results.

**Solution evidence to inspect:** Save the two expected mypy diagnostics, repair both defects, and show mypy plus the runtime test command pass.

### Exercise 3 — reasoning, alternatives, and proof

**Learner contract:** **Prediction:** Given an unused import, inconsistent spacing, a possible `None` value, and a wrong result, predict which quality tool can detect each. **Progressive hint:** No single tool proves all four properties. **Verify:** Create a four-row matrix mapping each defect to formatter, linter, type checker, or test; run the tools and record which predictions were confirmed.

**Reasoning before code:** Evaluate the expression or state transition by hand first. Name the input state, the next operation, and the exact evidence that would falsify the prediction while applying automated formatting, linting, and static type feedback.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Editor-on-save feedback is fast, while command-line checks are reproducible; continuous integration should run the same checked-in configuration.

**Edge case:** Generated files, notebook code, untyped third-party libraries, version drift, and broad suppressions can create misleading results.

**Solution evidence to inspect:** Create a four-row matrix mapping each defect to formatter, linter, type checker, or test; run the tools and record which predictions were confirmed.

### Exercise 4 — reasoning, alternatives, and proof

**Learner contract:** **Tracing:** Trace type narrowing for `str | None` through an explicit `is None` branch and state the type in each path. **Progressive hint:** A type checker follows control-flow evidence. **Verify:** Use `reveal_type` or equivalent diagnostics in both branches; confirm the non-None branch narrows to `str` and the absence branch cannot call string methods.

**Reasoning before code:** Create a small trace table with one row per operation or input item. Record the relevant names, labels, shape, or iterator position after each step so the automated formatting, linting, and static type feedback model is visible.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Editor-on-save feedback is fast, while command-line checks are reproducible; continuous integration should run the same checked-in configuration.

**Edge case:** Generated files, notebook code, untyped third-party libraries, version drift, and broad suppressions can create misleading results.

**Solution evidence to inspect:** Use `reveal_type` or equivalent diagnostics in both branches; confirm the non-None branch narrows to `str` and the absence branch cannot call string methods.

### Exercise 5 — reasoning, alternatives, and proof

**Learner contract:** **Implementation:** Refactor an untyped file loader into a typed function using `Path`, a context manager, UTF-8, and a validated return shape. **Progressive hint:** Boundary validation can replace an unhelpfully broad `Any`. **Verify:** Type-check the loader, then test valid UTF-8 input plus missing column, invalid field type, and missing path boundaries.

**Reasoning before code:** Turn the ambiguous boundary into an explicit contract before coding. Test values immediately below, at, and above the boundary and explain how the result follows from automated formatting, linting, and static type feedback.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Editor-on-save feedback is fast, while command-line checks are reproducible; continuous integration should run the same checked-in configuration.

**Edge case:** Generated files, notebook code, untyped third-party libraries, version drift, and broad suppressions can create misleading results.

**Solution evidence to inspect:** Type-check the loader, then test valid UTF-8 input plus missing column, invalid field type, and missing path boundaries.

### Exercise 6 — reasoning, alternatives, and proof

**Learner contract:** **Debugging:** Replace an unexplained `# type: ignore` with a real narrowing or a narrow error-code ignore plus justification. **Progressive hint:** Do not suppress diagnostics before understanding the contract. **Verify:** Show the original diagnostic, replace suppression with narrowing where possible, and confirm any remaining ignore names one error code and rationale.

**Reasoning before code:** Reproduce the bad behavior on the smallest input, state the violated contract, make one repair, and rerun both the failing boundary and a normal case. Keep the diagnosis grounded in automated formatting, linting, and static type feedback.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Editor-on-save feedback is fast, while command-line checks are reproducible; continuous integration should run the same checked-in configuration.

**Edge case:** Generated files, notebook code, untyped third-party libraries, version drift, and broad suppressions can create misleading results.

**Solution evidence to inspect:** Show the original diagnostic, replace suppression with narrowing where possible, and confirm any remaining ignore names one error code and rationale.

### Exercise 7 — reasoning, alternatives, and proof

**Learner contract:** **Edge case and explanation:** Design a local/CI gate order and explain why formatter success should not prevent tests from running during diagnosis. **Progressive hint:** Fast static checks give feedback, but each signal remains independent. **Verify:** Run each gate independently on a deliberately broken scratch file and record its signal; confirm one early failure does not erase later diagnostic evidence.

**Reasoning before code:** Turn the ambiguous boundary into an explicit contract before coding. Test values immediately below, at, and above the boundary and explain how the result follows from automated formatting, linting, and static type feedback.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Editor-on-save feedback is fast, while command-line checks are reproducible; continuous integration should run the same checked-in configuration.

**Edge case:** Generated files, notebook code, untyped third-party libraries, version drift, and broad suppressions can create misleading results.

**Solution evidence to inspect:** Run each gate independently on a deliberately broken scratch file and record its signal; confirm one early failure does not erase later diagnostic evidence.
<!-- END BEGINNER SOLUTION REVIEW -->

This solution configures the repository’s actual quality tools and explains
what each signal can—and cannot—prove.

Contents
- Exercise: Apply Ruff and mypy to your utilities, then run tests

---

Sample `pyproject.toml`
```toml
[tool.ruff]
target-version = "py311"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B"]

[tool.mypy]
python_version = "3.11"
strict = true
```

Commands
```text
python -m ruff check .          # lint and import checks
python -m ruff format --check . # verify formatting without changing files
python -m mypy .                # static type checking
python -m pytest                # behavioral checks
```

Typical fixes

- Ruff: remove unused imports, fix undefined names, simplify suspicious code,
  and sort imports.
- mypy: annotate public boundaries, handle `None`, and narrow values before use.
- pytest: repair behavior or the test contract after understanding the failure.

Example: before/after
```python
# BEFORE
import json

def load(path):
    f = open(path)
    return json.load(f)

# AFTER
import json
from pathlib import Path
from typing import Any

def load(path: str | Path) -> Any:
    p = Path(path)
    with p.open(encoding="utf-8") as f:
        return json.load(f)
```
Why better

- Imports and accepted path types are explicit.
- The context manager closes the file if decoding fails.
- The encoding does not depend on the operating-system default.

`Any` is honest for arbitrary JSON but deliberately gives up downstream type
checking. A production boundary could validate the decoded value and return a
more precise type.

CI tip

Run the same lock, lint, format, type, and test commands locally and in
continuous integration. A clean formatter or type checker does not replace
tests; the tools catch different classes of defects.

---

## Expanded mastery lab solutions

Use formatter, linter, type checker, and tests as complementary evidence. Read and fix one diagnostic at a time, then review behavior.

Read the reasoning before the code. Inline comments explain ownership, boundary choices, and why each check exists; assertions turn the stated contract into executable evidence.

### Practices 1–2 — Match evidence to the question

- Ruff reports unused imports and configured lint rules.
- Ruff format checks layout.
- mypy can report use of a possible `None`.
- pytest can expose the wrong result only when a test exercises it.

```python
def display(value: str | None) -> str:
    if value is None:
        return "missing"      # Here value is None.
    return value.upper()      # Here mypy narrows value to str.
```

### Practices 3–5 — Validate boundaries instead of silencing them

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
    if not all(isinstance(key, str) and isinstance(value, str)
               for key, value in decoded.items()):
        raise ValueError("expected string keys and string values")
    return decoded
```

A useful gate order is lock/environment check, Ruff lint, Ruff format check,
mypy, then pytest. During debugging, run the narrow failing command directly;
in CI, configure independent steps or always inspect every gate so a formatter
failure does not hide a behavioral failure.
