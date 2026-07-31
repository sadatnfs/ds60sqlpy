# Day 14 — Solutions: Code Quality with Ruff and mypy

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

## Exercises 1–2 — Worked answers

### Exercise 1 — worked answer

**Learner contract:** Run Ruff formatting and lint checks on a small intentionally messy Python file. **Evidence:** record at least one formatter change and one lint diagnostic with its rule code. **Constraints:** understand each automatic fix, do not run broad fixes over unrelated repository files, and delete only the scratch file you created. **Verify:** both `ruff format --check` and `ruff check` pass afterward.

**Reasoning:** Implement this exact contract as written: Run Ruff formatting and lint checks on a small intentionally messy Python file. Evidence: record at least one formatter change and one lint diagnostic with its rule code. Constraints: understand each automatic fix, do not run broad fixes over unrelated repository files, and delete only the scratch file you created. Keep the prompt's named data and constraints visible in the code, then establish this specific result: both `ruff format --check` and `ruff check` pass afterward. That connects the answer to automated formatting, linting, and static type feedback.

Use a small scratch file and run the repository tools independently:

```text
python -m ruff format --check scratch_quality.py
python -m ruff check scratch_quality.py
python -m mypy scratch_quality.py
python -m pytest path/to/test_scratch_quality.py
```

Ruff formatting owns layout; Ruff checks selected static patterns; mypy
checks annotated type consistency; pytest checks runtime contracts.
Save one diagnostic from each deliberate defect, repair it, then rerun.

**Verification evidence:** both `ruff format --check` and `ruff check` pass afterward.

### Exercise 2 — worked answer

**Learner contract:** Add useful type hints to a function that accepts records and returns a numeric total, then run mypy on the file. **Introduce:** one wrong caller argument and one wrong return in scratch code so you can read both diagnostics. **Expected behavior:** mypy rejects both; after repair it reports success while runtime tests still pass. **Verify:** Save the two expected mypy diagnostics, repair both defects, and show mypy plus the runtime test command pass.

**Reasoning:** Reproduce the exact failure described here before changing code: Add useful type hints to a function that accepts records and returns a numeric total, then run mypy on the file. Introduce: one wrong caller argument and one wrong return in scratch code so you can read both diagnostics. Expected behavior: mypy rejects both; after repair it reports success while runtime tests still pass. Preserve that failing case, repair the violated rule, and rerun the evidence named here: Save the two expected mypy diagnostics, repair both defects, and show mypy plus the runtime test command pass. The diagnosis depends on automated formatting, linting, and static type feedback.

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

**Verification evidence:** Save the two expected mypy diagnostics, repair both defects, and show mypy plus the runtime test command pass.

## Exercises 3–7 — Expanded mastery answers

### Exercise 3 — answer contract

**Learner contract:** **Prediction:** Given an unused import, inconsistent spacing, a possible `None` value, and a wrong result, predict which quality tool can detect each. **Progressive hint:** No single tool proves all four properties. **Verify:** Create a four-row matrix mapping each defect to formatter, linter, type checker, or test; run the tools and record which predictions were confirmed.

**Reasoning:** Predict this named state change before running it: Prediction: Given an unused import, inconsistent spacing, a possible `None` value, and a wrong result, predict which quality tool can detect each. Progressive hint: No single tool proves all four properties. Then compare the prediction with this proof target: Create a four-row matrix mapping each defect to formatter, linter, type checker, or test; run the tools and record which predictions were confirmed. This makes automated formatting, linting, and static type feedback observable instead of relying on intuition.

**Evidence to locate in the grouped implementation:** Create a four-row matrix mapping each defect to formatter, linter, type checker, or test; run the tools and record which predictions were confirmed.

### Exercise 4 — answer contract

**Learner contract:** **Tracing:** Trace type narrowing for `str | None` through an explicit `is None` branch and state the type in each path. **Progressive hint:** A type checker follows control-flow evidence. **Verify:** Capture `reveal_type` or equivalent type-checker output in both branches; assert the non-None branch reports `str` and the absence branch reports an error for a string-method call.

**Reasoning:** Trace the concrete values in this contract one step at a time: Tracing: Trace type narrowing for `str | None` through an explicit `is None` branch and state the type in each path. Progressive hint: A type checker follows control-flow evidence. Record the named value, shape, label, or iterator position needed to establish: Capture `reveal_type` or equivalent type-checker output in both branches; assert the non-None branch reports `str` and the absence branch reports an error for a string-method call. The trace exposes automated formatting, linting, and static type feedback directly.

**Evidence to locate in the grouped implementation:** Capture `reveal_type` or equivalent type-checker output in both branches; assert the non-None branch reports `str` and the absence branch reports an error for a string-method call.

### Exercise 5 — answer contract

**Learner contract:** **Implementation:** Refactor an untyped file loader into a typed function using `Path`, a context manager, UTF-8, and a validated return shape. **Progressive hint:** Boundary validation can replace an unhelpfully broad `Any`. **Verify:** Type-check the loader, then test valid UTF-8 input plus missing column, invalid field type, and missing path boundaries.

**Reasoning:** Make this boundary unambiguous in code: Implementation: Refactor an untyped file loader into a typed function using `Path`, a context manager, UTF-8, and a validated return shape. Progressive hint: Boundary validation can replace an unhelpfully broad `Any`. Values below, at, and above the named boundary must produce the evidence Type-check the loader, then test valid UTF-8 input plus missing column, invalid field type, and missing path boundaries. Those cases show how automated formatting, linting, and static type feedback behaves at its edge.

**Evidence to locate in the grouped implementation:** Type-check the loader, then test valid UTF-8 input plus missing column, invalid field type, and missing path boundaries.

### Exercise 6 — answer contract

**Learner contract:** **Debugging:** Replace an unexplained `# type: ignore` with a real narrowing or a narrow error-code ignore plus justification. **Progressive hint:** Do not suppress diagnostics before understanding the contract. **Verify:** Show the original diagnostic, replace suppression with narrowing where possible, and confirm any remaining ignore names one error code and rationale.

**Reasoning:** Reproduce the exact failure described here before changing code: Debugging: Replace an unexplained `# type: ignore` with a real narrowing or a narrow error-code ignore plus justification. Progressive hint: Do not suppress diagnostics before understanding the contract. Preserve that failing case, repair the violated rule, and rerun the evidence named here: Show the original diagnostic, replace suppression with narrowing where possible, and confirm any remaining ignore names one error code and rationale. The diagnosis depends on automated formatting, linting, and static type feedback.

**Evidence to locate in the grouped implementation:** Show the original diagnostic, replace suppression with narrowing where possible, and confirm any remaining ignore names one error code and rationale.

### Exercise 7 — answer contract

**Learner contract:** **Edge case and explanation:** Design a local/CI gate order and explain why formatter success should not prevent tests from running during diagnosis. **Progressive hint:** Fast static checks give feedback, but each signal remains independent. **Verify:** Run each gate independently on a deliberately broken scratch file and record its signal; confirm one early failure does not erase later diagnostic evidence.

**Reasoning:** Make this boundary unambiguous in code: Edge case and explanation: Design a local/CI gate order and explain why formatter success should not prevent tests from running during diagnosis. Progressive hint: Fast static checks give feedback, but each signal remains independent. Values below, at, and above the named boundary must produce the evidence Run each gate independently on a deliberately broken scratch file and record its signal; confirm one early failure does not erase later diagnostic evidence. Those cases show how automated formatting, linting, and static type feedback behaves at its edge.

**Evidence to locate in the grouped implementation:** Run each gate independently on a deliberately broken scratch file and record its signal; confirm one early failure does not erase later diagnostic evidence.

## Expanded mastery lab solutions

Use formatter, linter, type checker, and tests as complementary evidence. Read and fix one diagnostic at a time, then review behavior.

### Shared implementation for Exercises 3–4 — Match evidence to the question

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

### Shared implementation for Exercises 5–7 — Validate boundaries instead of silencing them

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
