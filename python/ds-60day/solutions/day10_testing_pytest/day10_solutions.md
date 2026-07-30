# Day 10 — Solutions: Testing with Pytest

We write tests for `safe_divide` and `validate_email` (from earlier days) and include a negative test using `pytest.raises`.

Contents
- Exercise 1: Install pytest; write tests for `safe_divide` and `validate_email`
- Exercise 2: Negative test expecting exceptions

---

Prereq functions (from Day 3; include here for context/tests)
```python
def safe_divide(a: float, b: float) -> float:
    if b == 0:
        raise ZeroDivisionError('b must not be 0')
    return a / b

class InvalidEmailError(ValueError):
    pass

def validate_email(email: str) -> None:
    if '@' not in email:
        raise InvalidEmailError('Missing @ in email')
```

Install pytest (in your venv)
```
pip install pytest
```

Project layout
```
project/
  src/
    mymod.py              # optional location for your functions
  tests/
    test_core.py
```

tests/test_core.py
```python
import pytest

from mymod import safe_divide, validate_email, InvalidEmailError

@pytest.mark.parametrize('a,b,exp', [
    (10, 2, 5.0),
    (3, 2, 1.5),
    (-6, 3, -2.0),
])
def test_safe_divide_happy(a, b, exp):
    assert safe_divide(a, b) == exp

def test_safe_divide_raises():
    with pytest.raises(ZeroDivisionError):
        safe_divide(1, 0)

def test_validate_email_ok():
    validate_email('user@example.com')  # no exception

def test_validate_email_bad():
    with pytest.raises(InvalidEmailError):
        validate_email('not-an-email')
```

Run tests
```
pytest -q
```
Notes
- Use parametrize to cover multiple cases succinctly.
- Use `with pytest.raises(...)` to assert the exact exception type.
- Keep business logic and tests separate; import the functions under test.

---

## Exercise-by-exercise reference

Every numbered learner exercise has a matching entry here. The original
worked examples remain above; the expanded answers below add heavily
commented code, explicit reasoning, and executable checks.

### Exercise 1 — Original lesson practice

**Prompt:** Write tests for `safe_divide` and `validate_email`. **Hint:** list the contract's normal, boundary, and invalid cases before writing test code.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 2 — Original lesson practice

**Prompt:** Add a negative test using `pytest.raises`. **Hint:** assert the narrow exception type and, when stable, a meaningful part of its message.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 3 — Prediction

**Prompt:** Predict how pytest reports `assert actual == expected` compared with `assert check(actual)` when the values differ.

**Reasoning checkpoint:** Direct comparisons usually produce more useful assertion introspection. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 4 — Tracing

**Prompt:** Trace fixture setup, test execution, and teardown when the test passes and when it raises.

**Reasoning checkpoint:** A yielding fixture resumes after `yield` for cleanup in both paths. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 5 — Implementation

**Prompt:** Write parameterized tests for a slug function covering ordinary text, extra whitespace, punctuation, and empty text.

**Reasoning checkpoint:** Each parameter row should communicate one behavior. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 6 — Debugging

**Prompt:** Repair a test whose `pytest.raises(Exception)` would accept unrelated bugs and whose protected block contains several operations.

**Reasoning checkpoint:** Assert a narrow exception around one operation. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 7 — Edge case and explanation

**Prompt:** Test floating-point output and `NaN` correctly. Explain why direct equality is inappropriate for each.

**Reasoning checkpoint:** Use `pytest.approx` for tolerance and `math.isnan` for NaN. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

## Expanded mastery lab solutions

Test observable contracts across normal, boundary, and invalid inputs. A good failure explains which behavior changed.

Read the reasoning before the code. Inline comments explain ownership, boundary choices, and why each check exists; assertions turn the stated contract into executable evidence.

### Practices 1–2 — Readable failures and reliable cleanup

Direct value comparisons let pytest display the differing values. A yielding
fixture's code after `yield` behaves like a `finally` cleanup step.

### Practices 3–5 — Focused tests

```python
import math
import re

import pytest


def slugify(text: str) -> str:
    return "-".join(re.findall(r"[a-z0-9]+", text.casefold()))


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("Data Tools", "data-tools"),
        ("  spaced   words ", "spaced-words"),
        ("A&B!", "a-b"),
        ("", ""),
    ],
)
def test_slugify(source: str, expected: str) -> None:
    assert slugify(source) == expected


def positive_root(value: float) -> float:
    if value < 0:
        raise ValueError("value must be non-negative")
    return value ** 0.5


def test_negative_root_is_rejected() -> None:
    # Only the operation under contract is inside the context manager.
    with pytest.raises(ValueError, match="non-negative"):
        positive_root(-1)


def test_float_and_nan_semantics() -> None:
    assert 0.1 + 0.2 == pytest.approx(0.3)
    missing = float("nan")
    assert math.isnan(missing)
```

`NaN != NaN` by IEEE floating-point design, so equality cannot recognize it.
Tolerance checks should use a scale appropriate to the domain rather than a
randomly large allowance.
