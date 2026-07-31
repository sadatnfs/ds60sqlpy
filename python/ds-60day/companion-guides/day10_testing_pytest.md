# Day 10 — Testing with pytest

**Level:** Beginner

Tests are executable examples of a contract. A useful test fails for one clear
reason and tells you what behavior changed.

## Learning objectives

By the end of this lesson, you can:

- arrange a test, perform one action, and assert observable behavior;
- use parametrization for multiple cases of one rule;
- assert a specific exception with `pytest.raises`;
- use `tmp_path` for isolated filesystem tests;
- run the repository's test suite through its `.venv` interpreter.

## Prerequisites

Complete Day 9 (`python-09`): importable functions and package structure.





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

2. Read `python/ds-60day/companion-guides/day10_testing_pytest.md`, then open `python/ds-60day/notebooks/day10_testing_pytest.ipynb` from the repository
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

**Lesson outcome:** use day 10 — testing with pytest to practice tests as executable contracts and useful failure reports
and explain the evidence produced by your code.
<!-- END HOW TO RUN -->

<!-- BEGIN BEGINNER DEEP DIVE -->
## Beginner deep dive — build the idea before the syntax

### Start with one mental picture

A test is a small executable example of observable behavior. Arrange
the inputs, act once, then assert the output or failure. Tests do not
prove a program has no bugs; they make chosen contracts repeatable and
reveal when later changes violate them.

Good cases cover a normal path, exact boundaries, and invalid input.
Keep each test focused enough that its name and failure identify the
broken behavior. Fixtures own reusable setup and teardown. Parametrized
tests express the same contract across several inputs without hiding
which case failed.

### Vocabulary in plain language

- **test case:** one named example with inputs and expected behavior.
- **assertion:** a claim that must be true for the test to pass.
- **fixture:** reusable setup data or a managed resource supplied to tests.
- **parametrization:** running one test contract with multiple named inputs.
- **regression:** behavior that used to work but was later broken.
- **test isolation:** the property that one test does not depend on another's state or order.

### Syntax anatomy

In `assert actual == expected`, pytest can display both values and their
difference. `with pytest.raises(ValueError, match="positive"):` states
that the indented call must raise that exact failure and optionally
match a stable message fragment. The test name should state behavior,
such as `test_safe_divide_rejects_zero_denominator`.

### Worked example 1 — Test a pure calculation with plain assertions

Direct equality makes failures explain the two values. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
def subtotal(prices: list[float]) -> float:
    return sum(prices)

assert subtotal([2.5, 3.0]) == 5.5
assert subtotal([]) == 0
"two subtotal contracts passed"
```

**Expected observation**

```text
`'two subtotal contracts passed'`. If an assertion fails, execution stops at the violated contract.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### Worked example 2 — Represent cases as data

The same behavior can be checked across several boundaries. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
def is_valid_percentage(value: float) -> bool:
    return 0 <= value <= 100

cases = [(0, True), (100, True), (-0.1, False), (100.1, False)]
results = [(value, is_valid_percentage(value) == expected)
           for value, expected in cases]
results
```

**Expected observation**

```text
`[(0, True), (100, True), (-0.1, True), (100.1, True)]`. Each tuple reports that its expectation matched.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### A debugging routine for this topic

When the output differs from your prediction, use this order:

1. Read the first failing assertion and reproduce that smallest case before scanning later failures.
2. Assert directly on useful values rather than wrapping them in an opaque helper returning only `True`/`False`.
3. Make fixtures create and clean up only state owned by the test.
4. If a test passes alone but fails in the suite, look for shared mutable state, order dependence, time, or randomness.

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

**Useful alternative:** A doctest can suit tiny documentation examples, while pytest is clearer for fixtures, parametrization, exceptions, and larger behavior contracts.

**Boundary to remember:** Empty input, exact bounds, malformed values, repeated calls, and cleanup after an exception reveal weak tests.
<!-- END BEGINNER DEEP DIVE -->

## Vocabulary and mental model

- **Test case:** one scenario with a defined expected result.
- **Assertion:** a condition that must be true for the test to pass.
- **Fixture:** setup data/resource supplied to a test.
- **Parametrization:** run one test contract against multiple inputs.
- **Regression:** behavior that worked before but later broke.
- **Unit test:** focused test of a small behavior with controlled dependencies.

Tests do not prove the absence of every bug; they preserve selected contracts.

## Worked example

```python
import pytest


def normalize_age(raw: str) -> int:
    age = int(raw)
    if age < 0:
        raise ValueError("age must be non-negative")
    return age


@pytest.mark.parametrize(("raw", "expected"), [("0", 0), ("42", 42)])
def test_normalize_age(raw: str, expected: int) -> None:
    assert normalize_age(raw) == expected


def test_normalize_age_rejects_negative() -> None:
    with pytest.raises(ValueError, match="non-negative"):
        normalize_age("-1")
```

## Run tests

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

macOS/Linux:

```bash
.venv/bin/python -m pytest
```

## Exercises and progressive hints

Each item is a complete mini-contract. Before writing code, copy its input,
expected behavior, constraints, and verification into your work cell. A
result is not complete merely because it “looks right”; run the stated
assertion or inspection and explain what it proves.

1. Write pytest tests for `safe_divide(numerator, denominator)` and `validate_email(text)`. **Coverage:** one ordinary result, negative values, zero denominator, one accepted bounded email example, and several rejected near misses. **Constraints:** name each behavior clearly and compare observable return values directly.
   **Verify:** run the test file from the repository root and confirm all intended cases are collected.

2. Add negative tests with `pytest.raises` for the narrow exception types documented by both functions. **Constraints:** keep only the expected failing call inside each context manager and match one stable, useful message fragment.
   **Verify:** temporarily change the expected exception once to observe a meaningful failure, then restore it.

### Additional mastery practice

Test observable contracts across normal, boundary, and invalid inputs. A good failure explains which behavior changed.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

3. **Prediction:** Predict how pytest reports `assert actual == expected` compared with `assert check(actual)` when the values differ.
   **Progressive hint:** Direct comparisons usually produce more useful assertion introspection.
   **Verify:** Run both deliberately failing assertions once and compare pytest's messages; record which report exposes actual/expected values directly.
4. **Tracing:** Trace fixture setup, test execution, and teardown when the test passes and when it raises.
   **Progressive hint:** A yielding fixture resumes after `yield` for cleanup in both paths.
   **Verify:** Append events from setup, test, and teardown for pass and raise cases; assert teardown is the final event in both traces.
5. **Implementation:** Write parameterized tests for a slug function covering ordinary text, extra whitespace, punctuation, and empty text.
   **Progressive hint:** Each parameter row should communicate one behavior.
   **Verify:** Confirm pytest reports a separate named case for ordinary, whitespace, punctuation, and empty inputs and that all match the written slug contract.
6. **Debugging:** Repair a test whose `pytest.raises(Exception)` would accept unrelated bugs and whose protected block contains several operations.
   **Progressive hint:** Assert a narrow exception around one operation.
   **Verify:** Prove the narrow expected error passes, then trigger an unrelated error and confirm the test fails instead of accepting it.
7. **Edge case and explanation:** Test floating-point output and `NaN` correctly. Explain why direct equality is inappropriate for each.
   **Progressive hint:** Use `pytest.approx` for tolerance and `math.isnan` for NaN.
   **Verify:** Use `pytest.approx` for one computed float and `math.isnan` for NaN; demonstrate why `nan == nan` is false.

Before opening the reference solution, write one sentence explaining
which contract or mental model each result confirms.

## Self-check

- Why should test names describe behavior rather than implementation steps?
- When does parametrization improve a test, and when does it hide distinct
  scenarios?
- What makes `tmp_path` safer than writing into the repository?
- What is the difference between a failing assertion and an unexpected error?

Expected behavior: pytest discovers the tests, normal cases pass, and the
negative test fails if the function stops enforcing its contract.

## Common pitfalls and diagnosis

- **"collected 0 items":** use `test_*.py` filenames and `test_*` function names.
- **An import fails only under pytest:** run from the repository root and use
  package imports rather than changing `sys.path` in tests.
- **A test passes when run alone but fails in the suite:** it probably shares
  mutable state, environment variables, files, or test order.
- **Float equality is brittle:** use `pytest.approx` for approximate results.
- **The test duplicates implementation logic:** assert input/output behavior,
  not every internal step.

## Continue

- [Open the learner notebook](../notebooks/day10_testing_pytest.ipynb)
- [Check the separate solution](../solutions/day10_testing_pytest/day10_solutions.md)
- [Next: Day 11 — Debugging, logging, and profiling](day11_debug_logging_profiling.md)

## Ask Codex about this lesson

Codex coaching is optional; the guide and notebook above contain the full
lesson. If you want a patient tutor, copy this prompt from the repository
root:

```text
Use $guide-ds60sqlpy-learning to tutor me through `python-10`
(Day 10 — Testing with pytest). I am a complete beginner. Emphasize tests as executable contracts and useful failure reports.
Read `python/ds-60day/companion-guides/day10_testing_pytest.md` and use the learner notebook
`python/ds-60day/notebooks/day10_testing_pytest.ipynb`. Do not open or quote anything under `solutions/` unless
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
