# Day 10 — Solutions: Testing with Pytest

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

## Exercises 1–2 — Worked answers

### Exercise 1 — worked answer

**Learner contract:** Write pytest tests for `safe_divide(numerator, denominator)` and `validate_email(text)`. **Coverage:** one ordinary result, negative values, zero denominator, one accepted bounded email example, and several rejected near misses. **Constraints:** name each behavior clearly and compare observable return values directly. **Verify:** run the test file from the repository root and confirm all intended cases are collected.

**Reasoning:** Implement this exact contract as written: Write pytest tests for `safe_divide(numerator, denominator)` and `validate_email(text)`. Coverage: one ordinary result, negative values, zero denominator, one accepted bounded email example, and several rejected near misses. Constraints: name each behavior clearly and compare observable return values directly. Keep the prompt's named data and constraints visible in the code, then establish this specific result: run the test file from the repository root and confirm all intended cases are collected. That connects the answer to tests as executable contracts and useful failure reports.

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

**Verification evidence:** run the test file from the repository root and confirm all intended cases are collected.

### Exercise 2 — worked answer

**Learner contract:** Add negative tests with `pytest.raises` for the narrow exception types documented by both functions. **Constraints:** keep only the expected failing call inside each context manager and match one stable, useful message fragment. **Verify:** temporarily change the expected exception once to observe a meaningful failure, then restore it.

**Reasoning:** Implement this exact contract as written: Add negative tests with `pytest.raises` for the narrow exception types documented by both functions. Constraints: keep only the expected failing call inside each context manager and match one stable, useful message fragment. Keep the prompt's named data and constraints visible in the code, then establish this specific result: temporarily change the expected exception once to observe a meaningful failure, then restore it. That connects the answer to tests as executable contracts and useful failure reports.

```python
import pytest


def test_safe_divide_rejects_zero() -> None:
    with pytest.raises(ZeroDivisionError, match="nonzero"):
        safe_divide(1, 0)


def test_validate_email_rejects_non_text() -> None:
    with pytest.raises(TypeError, match="must be a string"):
        validate_email(42)  # type: ignore[arg-type]
```

Each context manager encloses only the call expected to fail. Changing
either exception class temporarily demonstrates that pytest reports the
actual type and stable message before the test is restored.

**Verification evidence:** temporarily change the expected exception once to observe a meaningful failure, then restore it.

## Exercises 3–7 — Expanded mastery answers

### Exercise 3 — answer contract

**Learner contract:** **Prediction:** Predict how pytest reports `assert actual == expected` compared with `assert check(actual)` when the values differ. **Progressive hint:** Direct comparisons usually produce more useful assertion introspection. **Verify:** Run both deliberately failing assertions once and compare pytest's messages; record which report exposes actual/expected values directly.

**Reasoning:** Predict this named state change before running it: Prediction: Predict how pytest reports `assert actual == expected` compared with `assert check(actual)` when the values differ. Progressive hint: Direct comparisons usually produce more useful assertion introspection. Then compare the prediction with this proof target: Run both deliberately failing assertions once and compare pytest's messages; record which report exposes actual/expected values directly. This makes tests as executable contracts and useful failure reports observable instead of relying on intuition.

**Evidence to locate in the grouped implementation:** Run both deliberately failing assertions once and compare pytest's messages; record which report exposes actual/expected values directly.

### Exercise 4 — answer contract

**Learner contract:** **Tracing:** Trace fixture setup, test execution, and teardown when the test passes and when it raises. **Progressive hint:** A yielding fixture resumes after `yield` for cleanup in both paths. **Verify:** Append events from setup, test, and teardown for pass and raise cases; assert teardown is the final event in both traces.

**Reasoning:** Trace the concrete values in this contract one step at a time: Tracing: Trace fixture setup, test execution, and teardown when the test passes and when it raises. Progressive hint: A yielding fixture resumes after `yield` for cleanup in both paths. Record the named value, shape, label, or iterator position needed to establish: Append events from setup, test, and teardown for pass and raise cases; assert teardown is the final event in both traces. The trace exposes tests as executable contracts and useful failure reports directly.

**Evidence to locate in the grouped implementation:** Append events from setup, test, and teardown for pass and raise cases; assert teardown is the final event in both traces.

### Exercise 5 — answer contract

**Learner contract:** **Implementation:** Write parameterized tests for a slug function covering ordinary text, extra whitespace, punctuation, and empty text. **Progressive hint:** Each parameter row should communicate one behavior. **Verify:** Confirm pytest reports a separate named case for ordinary, whitespace, punctuation, and empty inputs and that all match the written slug contract.

**Reasoning:** Implement this exact contract as written: Implementation: Write parameterized tests for a slug function covering ordinary text, extra whitespace, punctuation, and empty text. Progressive hint: Each parameter row should communicate one behavior. Keep the prompt's named data and constraints visible in the code, then establish this specific result: Confirm pytest reports a separate named case for ordinary, whitespace, punctuation, and empty inputs and that all match the written slug contract. That connects the answer to tests as executable contracts and useful failure reports.

**Evidence to locate in the grouped implementation:** Confirm pytest reports a separate named case for ordinary, whitespace, punctuation, and empty inputs and that all match the written slug contract.

### Exercise 6 — answer contract

**Learner contract:** **Debugging:** Repair a test whose `pytest.raises(Exception)` would accept unrelated bugs and whose protected block contains several operations. **Progressive hint:** Assert a narrow exception around one operation. **Verify:** Prove the narrow expected error passes, then trigger an unrelated error and confirm the test fails instead of accepting it.

**Reasoning:** Reproduce the exact failure described here before changing code: Debugging: Repair a test whose `pytest.raises(Exception)` would accept unrelated bugs and whose protected block contains several operations. Progressive hint: Assert a narrow exception around one operation. Preserve that failing case, repair the violated rule, and rerun the evidence named here: Prove the narrow expected error passes, then trigger an unrelated error and confirm the test fails instead of accepting it. The diagnosis depends on tests as executable contracts and useful failure reports.

**Evidence to locate in the grouped implementation:** Prove the narrow expected error passes, then trigger an unrelated error and confirm the test fails instead of accepting it.

### Exercise 7 — answer contract

**Learner contract:** **Edge case and explanation:** Test floating-point output and `NaN` correctly. Explain why direct equality is inappropriate for each. **Progressive hint:** Use `pytest.approx` for tolerance and `math.isnan` for NaN. **Verify:** Assert one computed float passes with `pytest.approx`, assert `math.isnan(value)` is true for NaN, and record that `value == value` is false.

**Reasoning:** Make this boundary unambiguous in code: Edge case and explanation: Test floating-point output and `NaN` correctly. Explain why direct equality is inappropriate for each. Progressive hint: Use `pytest.approx` for tolerance and `math.isnan` for NaN. Values below, at, and above the named boundary must produce the evidence Assert one computed float passes with `pytest.approx`, assert `math.isnan(value)` is true for NaN, and record that `value == value` is false. Those cases show how tests as executable contracts and useful failure reports behaves at its edge.

**Evidence to locate in the grouped implementation:** Assert one computed float passes with `pytest.approx`, assert `math.isnan(value)` is true for NaN, and record that `value == value` is false.

## Expanded mastery lab solutions

Test observable contracts across normal, boundary, and invalid inputs. A good failure explains which behavior changed.

### Shared implementation for Exercises 3–4 — Readable failures and reliable cleanup

Direct value comparisons let pytest display the differing values. A yielding
fixture's code after `yield` behaves like a `finally` cleanup step.

### Shared implementation for Exercises 5–7 — Focused tests

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
