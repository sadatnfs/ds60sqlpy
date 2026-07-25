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

1. Write tests for `safe_divide` and `validate_email`. **Hint:** list the
   contract's normal, boundary, and invalid cases before writing test code.
2. Add a negative test using `pytest.raises`. **Hint:** assert the narrow
   exception type and, when stable, a meaningful part of its message.

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
