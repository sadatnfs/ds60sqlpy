# Day 10 — Solutions: Testing with Pytest

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

The solution is not a typing template. Read the learner contract, predict
the result, then compare decisions and evidence. The central mental model is
**tests as executable contracts and useful failure reports**.

A test is a small executable example of observable behavior. Arrange
the inputs, act once, then assert the output or failure. Tests do not
prove a program has no bugs; they make chosen contracts repeatable and
reveal when later changes violate them.

Good cases cover a normal path, exact boundaries, and invalid input.
Keep each test focused enough that its name and failure identify the
broken behavior. Fixtures own reusable setup and teardown. Parametrized
tests express the same contract across several inputs without hiding
which case failed.

### Vocabulary used in the worked answers

- **test case:** one named example with inputs and expected behavior.
- **assertion:** a claim that must be true for the test to pass.
- **fixture:** reusable setup data or a managed resource supplied to tests.
- **parametrization:** running one test contract with multiple named inputs.
- **regression:** behavior that used to work but was later broken.
- **test isolation:** the property that one test does not depend on another's state or order.

### Reference pattern 1 — Test a pure calculation with plain assertions

Direct equality makes failures explain the two values.

```python
def subtotal(prices: list[float]) -> float:
    return sum(prices)

assert subtotal([2.5, 3.0]) == 5.5
assert subtotal([]) == 0
"two subtotal contracts passed"
```

**Expected observation:** `'two subtotal contracts passed'`. If an assertion fails, execution stops at the violated contract.

### Reference pattern 2 — Represent cases as data

The same behavior can be checked across several boundaries.

```python
def is_valid_percentage(value: float) -> bool:
    return 0 <= value <= 100

cases = [(0, True), (100, True), (-0.1, False), (100.1, False)]
results = [(value, is_valid_percentage(value) == expected)
           for value, expected in cases]
results
```

**Expected observation:** `[(0, True), (100, True), (-0.1, True), (100.1, True)]`. Each tuple reports that its expectation matched.

## Exercise-by-exercise reasoning map

The numbering and learner contracts below match the guide and notebook.
Each entry explains what to reason about, how to inspect the worked code,
an alternative, an edge case, and the evidence required for completion.

### Exercise 1 — reasoning, alternatives, and proof

**Learner contract:** Write pytest tests for `safe_divide(numerator, denominator)` and `validate_email(text)`. **Coverage:** one ordinary result, negative values, zero denominator, one accepted bounded email example, and several rejected near misses. **Constraints:** name each behavior clearly and compare observable return values directly. **Verify:** run the test file from the repository root and confirm all intended cases are collected.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies tests as executable contracts and useful failure reports.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A doctest can suit tiny documentation examples, while pytest is clearer for fixtures, parametrization, exceptions, and larger behavior contracts.

**Edge case:** Empty input, exact bounds, malformed values, repeated calls, and cleanup after an exception reveal weak tests.

**Solution evidence to inspect:** run the test file from the repository root and confirm all intended cases are collected.

### Exercise 2 — reasoning, alternatives, and proof

**Learner contract:** Add negative tests with `pytest.raises` for the narrow exception types documented by both functions. **Constraints:** keep only the expected failing call inside each context manager and match one stable, useful message fragment. **Verify:** temporarily change the expected exception once to observe a meaningful failure, then restore it.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies tests as executable contracts and useful failure reports.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A doctest can suit tiny documentation examples, while pytest is clearer for fixtures, parametrization, exceptions, and larger behavior contracts.

**Edge case:** Empty input, exact bounds, malformed values, repeated calls, and cleanup after an exception reveal weak tests.

**Solution evidence to inspect:** temporarily change the expected exception once to observe a meaningful failure, then restore it.

### Exercise 3 — reasoning, alternatives, and proof

**Learner contract:** **Prediction:** Predict how pytest reports `assert actual == expected` compared with `assert check(actual)` when the values differ. **Progressive hint:** Direct comparisons usually produce more useful assertion introspection. **Verify:** Run both deliberately failing assertions once and compare pytest's messages; record which report exposes actual/expected values directly.

**Reasoning before code:** Evaluate the expression or state transition by hand first. Name the input state, the next operation, and the exact evidence that would falsify the prediction while applying tests as executable contracts and useful failure reports.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A doctest can suit tiny documentation examples, while pytest is clearer for fixtures, parametrization, exceptions, and larger behavior contracts.

**Edge case:** Empty input, exact bounds, malformed values, repeated calls, and cleanup after an exception reveal weak tests.

**Solution evidence to inspect:** Run both deliberately failing assertions once and compare pytest's messages; record which report exposes actual/expected values directly.

### Exercise 4 — reasoning, alternatives, and proof

**Learner contract:** **Tracing:** Trace fixture setup, test execution, and teardown when the test passes and when it raises. **Progressive hint:** A yielding fixture resumes after `yield` for cleanup in both paths. **Verify:** Append events from setup, test, and teardown for pass and raise cases; assert teardown is the final event in both traces.

**Reasoning before code:** Create a small trace table with one row per operation or input item. Record the relevant names, labels, shape, or iterator position after each step so the tests as executable contracts and useful failure reports model is visible.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A doctest can suit tiny documentation examples, while pytest is clearer for fixtures, parametrization, exceptions, and larger behavior contracts.

**Edge case:** Empty input, exact bounds, malformed values, repeated calls, and cleanup after an exception reveal weak tests.

**Solution evidence to inspect:** Append events from setup, test, and teardown for pass and raise cases; assert teardown is the final event in both traces.

### Exercise 5 — reasoning, alternatives, and proof

**Learner contract:** **Implementation:** Write parameterized tests for a slug function covering ordinary text, extra whitespace, punctuation, and empty text. **Progressive hint:** Each parameter row should communicate one behavior. **Verify:** Confirm pytest reports a separate named case for ordinary, whitespace, punctuation, and empty inputs and that all match the written slug contract.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies tests as executable contracts and useful failure reports.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A doctest can suit tiny documentation examples, while pytest is clearer for fixtures, parametrization, exceptions, and larger behavior contracts.

**Edge case:** Empty input, exact bounds, malformed values, repeated calls, and cleanup after an exception reveal weak tests.

**Solution evidence to inspect:** Confirm pytest reports a separate named case for ordinary, whitespace, punctuation, and empty inputs and that all match the written slug contract.

### Exercise 6 — reasoning, alternatives, and proof

**Learner contract:** **Debugging:** Repair a test whose `pytest.raises(Exception)` would accept unrelated bugs and whose protected block contains several operations. **Progressive hint:** Assert a narrow exception around one operation. **Verify:** Prove the narrow expected error passes, then trigger an unrelated error and confirm the test fails instead of accepting it.

**Reasoning before code:** Reproduce the bad behavior on the smallest input, state the violated contract, make one repair, and rerun both the failing boundary and a normal case. Keep the diagnosis grounded in tests as executable contracts and useful failure reports.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A doctest can suit tiny documentation examples, while pytest is clearer for fixtures, parametrization, exceptions, and larger behavior contracts.

**Edge case:** Empty input, exact bounds, malformed values, repeated calls, and cleanup after an exception reveal weak tests.

**Solution evidence to inspect:** Prove the narrow expected error passes, then trigger an unrelated error and confirm the test fails instead of accepting it.

### Exercise 7 — reasoning, alternatives, and proof

**Learner contract:** **Edge case and explanation:** Test floating-point output and `NaN` correctly. Explain why direct equality is inappropriate for each. **Progressive hint:** Use `pytest.approx` for tolerance and `math.isnan` for NaN. **Verify:** Use `pytest.approx` for one computed float and `math.isnan` for NaN; demonstrate why `nan == nan` is false.

**Reasoning before code:** Turn the ambiguous boundary into an explicit contract before coding. Test values immediately below, at, and above the boundary and explain how the result follows from tests as executable contracts and useful failure reports.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A doctest can suit tiny documentation examples, while pytest is clearer for fixtures, parametrization, exceptions, and larger behavior contracts.

**Edge case:** Empty input, exact bounds, malformed values, repeated calls, and cleanup after an exception reveal weak tests.

**Solution evidence to inspect:** Use `pytest.approx` for one computed float and `math.isnan` for NaN; demonstrate why `nan == nan` is false.
<!-- END BEGINNER SOLUTION REVIEW -->

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
