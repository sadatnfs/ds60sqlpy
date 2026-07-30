# Day 14 — Solutions: Code Quality with Ruff and mypy

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

## Exercise-by-exercise reference

Every numbered learner exercise has a matching entry here. The original
worked examples remain above; the expanded answers below add heavily
commented code, explicit reasoning, and executable checks.

### Exercise 1 — Original lesson practice

**Prompt:** Run all four checks on utilities from earlier days. Predict what each tool will report, then make the smallest behavior-preserving fixes. **Hint:** process one diagnostic at a time from the first file; an early syntax/import issue can cause many downstream messages. Finish with pytest because clean static output does not prove correct behavior.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 2 — Prediction

**Prompt:** Given an unused import, inconsistent spacing, a possible `None` value, and a wrong result, predict which quality tool can detect each.

**Reasoning checkpoint:** No single tool proves all four properties. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 3 — Tracing

**Prompt:** Trace type narrowing for `str | None` through an explicit `is None` branch and state the type in each path.

**Reasoning checkpoint:** A type checker follows control-flow evidence. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 4 — Implementation

**Prompt:** Refactor an untyped file loader into a typed function using `Path`, a context manager, UTF-8, and a validated return shape.

**Reasoning checkpoint:** Boundary validation can replace an unhelpfully broad `Any`. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 5 — Debugging

**Prompt:** Replace an unexplained `# type: ignore` with a real narrowing or a narrow error-code ignore plus justification.

**Reasoning checkpoint:** Do not suppress diagnostics before understanding the contract. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 6 — Edge case and explanation

**Prompt:** Design a local/CI gate order and explain why formatter success should not prevent tests from running during diagnosis.

**Reasoning checkpoint:** Fast static checks give feedback, but each signal remains independent. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

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
