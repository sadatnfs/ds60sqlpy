# Day 10 Solutions: Testing with pytest

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

These worked answers demonstrate **tests as executable contracts and useful failure reports**. Predict each named
result before comparing your attempt with its matching assertions.

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

### How to compare an answer

For this lesson's **tests as executable contracts and useful failure reports** model, follow the exact values from each learner contract through its function or expression to the assertion that proves the expected behavior; then change one boundary input and make that assertion fail once before accepting the answer.
<!-- END BEGINNER SOLUTION REVIEW -->

## Exercises 1-2: Worked answers

### Exercise 1: worked answer

**Learner contract:** Write pytest tests for `safe_divide(numerator, denominator)` and `validate_email(text)`. **Coverage:** one ordinary result, negative values, zero denominator, one accepted bounded email example, and several rejected near misses. **Constraints:** name each behavior clearly and compare observable return values directly. **Verify:** run the tests with the pad recipe in "Run pytest from the classroom pad" and confirm that the summary counts every case you wrote as passed.

**Reasoning:** Each test names one behavior and checks an observable return value directly, so a failure report says which rule broke. The ordinary and negative divisions confirm that the sign survives, and the zero-denominator test pins the documented `ZeroDivisionError` and its message. The email cases are deliberately small: one accepted address and two near misses, one without `@` and one without a dot in the domain; the pattern checks an email shape, not whether the mailbox exists. Calling the test functions at the end runs their assertions once inside this file; the shared implementation for Exercises 3-4 shows a real pytest run and its report.

```python
import re


def safe_divide(left: float, right: float) -> float:
    if right == 0:
        raise ZeroDivisionError("right operand must be nonzero")
    return left / right


def validate_email(text: str) -> bool:
    if not isinstance(text, str):
        raise TypeError("email text must be a string")
    return re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", text) is not None
```

```python
import pytest


def test_safe_divide_contract() -> None:
    assert safe_divide(9, 3) == 3
    assert safe_divide(-9, 3) == -3


def test_safe_divide_zero_denominator() -> None:
    with pytest.raises(ZeroDivisionError, match="nonzero"):
        safe_divide(9, 0)


@pytest.mark.parametrize(
    ("text", "expected"),
    [("ada@example.com", True), ("missing-at.example.com", False), ("a@b", False)],
)
def test_validate_email(text: str, expected: bool) -> None:
    assert validate_email(text) is expected
```

Outside pytest, calling the test functions runs their assertions once:

```python
test_safe_divide_contract()
test_safe_divide_zero_denominator()
for text, expected in [
    ("ada@example.com", True),
    ("missing-at.example.com", False),
    ("a@b", False),
]:
    test_validate_email(text, expected)
```

### Exercise 2: worked answer

**Learner contract:** Add negative tests with `pytest.raises` for the narrow exception types documented by both functions. **Constraints:** keep only the expected failing call inside each context manager and match one stable, useful message fragment. **Verify:** temporarily change the expected exception once to observe a meaningful failure, then restore it.

**Reasoning:** `pytest.raises(ZeroDivisionError, match="nonzero")` passes only when that exact type is raised and its message matches the pattern, so a different error or a reworded message makes the test fail. Only the call that should fail sits inside the `with` block; if setup code were inside too, an error from the setup could satisfy the test by accident. The `TypeError` test protects the input contract of `validate_email`. Temporarily changing `ZeroDivisionError` to `ValueError` shows pytest reporting the actual exception, which is the evidence that the test can fail for the right reason.

```python
import pytest


def test_safe_divide_rejects_zero() -> None:
    with pytest.raises(ZeroDivisionError, match="nonzero"):
        safe_divide(1, 0)


def test_validate_email_rejects_non_text() -> None:
    with pytest.raises(TypeError, match="must be a string"):
        validate_email(42)  # type: ignore[arg-type]
```

```python
test_safe_divide_rejects_zero()
test_validate_email_rejects_non_text()
```

Each context manager encloses only the call expected to fail. Changing
either exception class temporarily demonstrates that pytest reports the
actual type and stable message before the test is restored.

## Exercises 3-7: Expanded mastery answers

### Exercise 3: answer contract

**Learner contract:** **Prediction:** Predict how pytest reports `assert actual == expected` compared with `assert check(actual)` when the values differ. **Progressive hint:** Direct comparisons usually produce more useful assertion introspection. **Verify:** Run both deliberately failing assertions once and compare pytest's messages; record which report exposes actual/expected values directly.

**Reasoning:** pytest rewrites `assert` statements so that a failing comparison shows its operands: `assert actual == 5` fails with `assert 4 == 5`, naming both the actual and the expected value. A helper that hides the comparison, `assert check(actual)`, can report only `assert False` and `where False = check(4)`: you see the input, not what it should have been. The shared implementation for Exercises 3-4 runs both failing tests with pytest in a child process and asserts both report lines. Prefer direct comparisons in tests, and give helpers a descriptive failure message when you need them.

### Exercise 4: answer contract

**Learner contract:** **Tracing:** Trace fixture setup, test execution, and teardown when the test passes and when it raises. **Progressive hint:** A yielding fixture resumes after `yield` for cleanup in both paths. **Verify:** Append events from setup, test, and teardown for pass and raise cases; assert teardown is the final event in both traces.

**Reasoning:** pytest runs a yielding fixture up to `yield`, passes the yielded value to the test, and resumes after `yield` when the test ends, whether it passed or raised. The trace test in the shared implementation for Exercises 3-4 records `setup`, `pass body`, `teardown`, then `setup`, `raise body`, `teardown`, which proves that cleanup also ran after the failure. That makes the code after `yield` the right place to close files or remove temporary state. Cleanup written at the end of a test body instead would be skipped whenever the test raises.

### Exercise 5: answer contract

**Learner contract:** **Implementation:** Write parameterized tests for a slug function covering ordinary text, extra whitespace, punctuation, and empty text. **Progressive hint:** Each parameter row should communicate one behavior. **Verify:** Confirm pytest reports a separate named case for ordinary, whitespace, punctuation, and empty inputs and that all match the written slug contract.

**Reasoning:** Each parameter row is one behavior with its own expected value, so pytest reports four separate cases and a failure names the row that broke. `re.findall(r"[a-z0-9]+", ...)` keeps runs of letters and digits after `casefold()`, which collapses repeated spaces, drops punctuation, and returns `""` for empty input. The punctuation row, `"A&B!"` becoming `"a-b"`, documents a choice: the `&` acts as a separator instead of disappearing. Packing all four cases into one test with several asserts would stop at the first failure and hide the others.

### Exercise 6: answer contract

**Learner contract:** **Debugging:** Repair a test whose `pytest.raises(Exception)` would accept unrelated bugs and whose protected block contains several operations. **Progressive hint:** Assert a narrow exception around one operation. **Verify:** Prove the narrow expected error passes, then trigger an unrelated error and confirm the test fails instead of accepting it.

**Reasoning:** `pytest.raises(Exception)` accepts any error, including a `NameError` from a typo, so the test can pass while the code is broken. The repair names the specific type, `ValueError`, matches a stable message fragment, and wraps only the one call under test, as `test_negative_root_is_rejected` in the shared implementation for Exercises 5-7 shows. To see the difference, replace the call with one that raises `TypeError`: the narrow test now fails, while the broad version would have passed.

### Exercise 7: answer contract

**Learner contract:** **Edge case and explanation:** Test floating-point output and `NaN` correctly. Explain why direct equality is inappropriate for each. **Progressive hint:** Use `pytest.approx` for tolerance and `math.isnan` for NaN. **Verify:** Assert one computed float passes with `pytest.approx`, assert `math.isnan(value)` is true for NaN, and record that `value == value` is false.

**Reasoning:** Floating-point arithmetic rounds, so `0.1 + 0.2` is `0.30000000000000004` and `== 0.3` is false; `pytest.approx` compares within a relative tolerance of one part in a million by default. `NaN` is defined to be unequal to everything, itself included, so `value == value` is `False` and equality can never detect it; `math.isnan` is the correct test. The shared implementation for Exercises 5-7 asserts both. Choose tolerances from the domain: a loose tolerance can hide a real error just as an exact comparison can report a false one.

## Expanded mastery lab solutions

Test observable contracts across normal, boundary, and invalid inputs. A good failure explains which behavior changed.

### Shared implementation for Exercises 3-4: Readable failures and reliable cleanup

Direct value comparisons let pytest display the differing values. A yielding
fixture's code after `yield` behaves like a `finally` cleanup step. The block
below writes a test file with two deliberately failing assertions and a traced
fixture, runs pytest on it in a child process (the Day 10 pad recipe), and
checks the report.

```python
import os
import subprocess
import sys
import tempfile
from pathlib import Path

test_source = """import pytest

EVENTS = []


def check(value):
    return value == 5


def test_direct_comparison():
    actual = 2 + 2
    assert actual == 5


def test_opaque_helper():
    actual = 2 + 2
    assert check(actual)


@pytest.fixture
def resource():
    EVENTS.append("setup")
    yield "resource"
    EVENTS.append("teardown")


def test_fixture_pass(resource):
    EVENTS.append("pass body")


def test_fixture_raise(resource):
    EVENTS.append("raise body")
    raise RuntimeError("deliberate failure")


def test_zz_fixture_trace():
    assert EVENTS == ["setup", "pass body", "teardown", "setup", "raise body", "teardown"]
"""

with tempfile.TemporaryDirectory(prefix="day10-") as folder:
    project = Path(folder)
    (project / "pytest.ini").write_text("[pytest]\n", encoding="utf-8")
    (project / "test_reports.py").write_text(test_source, encoding="utf-8")
    environment = dict(os.environ, PYTEST_DISABLE_PLUGIN_AUTOLOAD="1", PYTHONDONTWRITEBYTECODE="1")
    environment.pop("PYTEST_ADDOPTS", None)
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "--color=no", "-p", "no:cacheprovider"]
        + ["test_reports.py"],
        cwd=project,
        env=environment,
        capture_output=True,
        text=True,
        timeout=60,
    )

report = result.stdout
print(report)
assert "assert 4 == 5" in report  # the direct comparison shows actual and expected
assert "where False = check(4)" in report  # the helper hides the expected value
assert "3 failed, 2 passed" in report  # the trace test passed after the raising test
```

### Shared implementation for Exercises 5-7: Focused tests

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
    return value**0.5


def test_negative_root_is_rejected() -> None:
    # Only the operation under contract is inside the context manager.
    with pytest.raises(ValueError, match="non-negative"):
        positive_root(-1)


def test_float_and_nan_semantics() -> None:
    assert 0.1 + 0.2 == pytest.approx(0.3)
    missing = float("nan")
    assert math.isnan(missing)
    assert missing != missing


for source, expected in [
    ("Data Tools", "data-tools"),
    ("  spaced   words ", "spaced-words"),
    ("A&B!", "a-b"),
    ("", ""),
]:
    test_slugify(source, expected)
test_negative_root_is_rejected()
test_float_and_nan_semantics()
```

`NaN != NaN` by IEEE floating-point design, so equality cannot recognize it.
Tolerance checks should use a scale appropriate to the domain rather than a
randomly large allowance.
