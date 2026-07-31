# Day 03 — Solutions: Control Flow, Truthiness, and Exceptions

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

These worked answers demonstrate **branch selection, loop decisions, and narrow exception boundaries**. Predict each named
result before comparing your attempt with its matching assertions.

Control flow is the route execution takes through a program. An
`if`/`elif`/`else` chain chooses exactly one branch: Python tests from
top to bottom and stops at the first true condition. Put narrow or more
specific rules before broader ones, and validate impossible inputs
before classifying valid ones.

Exceptions separate a normal return path from a failure path. A `try`
block should contain only the operation expected to fail, while
`except` names the failure the current layer can interpret. Catching
every exception hides programming bugs. `else` runs after a successful
`try`; `finally` runs whether success or failure occurred.

### Vocabulary used in the worked answers

- **condition:** an expression evaluated for truthiness.
- **branch:** one possible block selected by a condition.
- **guard clause:** an early check that rejects or handles an invalid case.
- **exception:** an object representing a failure that interrupts normal flow.
- **raise:** to deliberately signal an exception.
- **handler:** an `except` block for a named exception type.

### How to compare an answer

For this lesson's **branch selection, loop decisions, and narrow exception boundaries** model, follow the exact values from each learner contract through its function or expression to the assertion that proves the expected behavior; then change one boundary input and make that assertion fail once before accepting the answer.
<!-- END BEGINNER SOLUTION REVIEW -->

## Exercises 1–3 — Worked answers

### Exercise 1 — worked answer

**Learner contract:** Print FizzBuzz for every integer from 1 through 30 inclusive. **Rules:** multiples of both 3 and 5 print `FizzBuzz`; only 3 prints `Fizz`; only 5 prints `Buzz`; all others print the number. **Constraints:** use one ordered `if`/`elif`/`else` chain. **Verify:** capture the output lines, assert there are exactly 30, and assert positions 3, 5, 15, 16, and 30 equal `Fizz`, `Buzz`, `FizzBuzz`, `16`, and `FizzBuzz`.

**Reasoning:** Implement this exact contract as written: Print FizzBuzz for every integer from 1 through 30 inclusive. Rules: multiples of both 3 and 5 print `FizzBuzz`; only 3 prints `Fizz`; only 5 prints `Buzz`; all others print the number. Constraints: use one ordered `if`/`elif`/`else` chain. Keep the prompt's named data and constraints visible in the code, then establish this specific result: capture the output lines, assert there are exactly 30, and assert positions 3, 5, 15, 16, and 30 equal `Fizz`, `Buzz`, `FizzBuzz`, `16`, and `FizzBuzz`. That connects the answer to branch selection, loop decisions, and narrow exception boundaries.

```python
output = []
for number in range(1, 31):
    if number % 15 == 0:
        output.append("FizzBuzz")
    elif number % 3 == 0:
        output.append("Fizz")
    elif number % 5 == 0:
        output.append("Buzz")
    else:
        output.append(str(number))

assert len(output) == 30
assert [output[index - 1] for index in (3, 5, 15, 16, 30)] == [
    "Fizz", "Buzz", "FizzBuzz", "16", "FizzBuzz"
]
```

The combined rule comes first because an `elif` chain stops at the
first true condition.

**Verification evidence:** capture the output lines, assert there are exactly 30, and assert positions 3, 5, 15, 16, and 30 equal `Fizz`, `Buzz`, `FizzBuzz`, `16`, and `FizzBuzz`.

### Exercise 2 — worked answer

**Learner contract:** Write `parse_age(text)` that returns an integer for valid integer text and returns `None` only when conversion raises `ValueError`. **Constraints:** put only `int(text)` inside `try`; do not use a bare `except`. **Verify:** test `'42'`, `' 7 '`, and `'seven'`, then explain which path uses `else`.

**Reasoning:** Implement this exact contract as written: Write `parse_age(text)` that returns an integer for valid integer text and returns `None` only when conversion raises `ValueError`. Constraints: put only `int(text)` inside `try`; do not use a bare `except`. Keep the prompt's named data and constraints visible in the code, then establish this specific result: test `'42'`, `' 7 '`, and `'seven'`, then explain which path uses `else`. That connects the answer to branch selection, loop decisions, and narrow exception boundaries.

```python
def parse_age(text: str) -> int | None:
    try:
        value = int(text)
    except ValueError:
        return None
    else:
        return value


assert parse_age("42") == 42
assert parse_age(" 7 ") == 7
assert parse_age("seven") is None
```

Only conversion is protected; a later programming defect is not
mislabeled as invalid user input.

**Verification evidence:** test `'42'`, `' 7 '`, and `'seven'`, then explain which path uses `else`.

### Exercise 3 — worked answer

**Learner contract:** Define `NegativeMeasurementError` as a subclass of `ValueError`, then write `validate_measurement(value)` that returns non-negative values unchanged and raises your exception for `-0.1`. **Verify:** show one normal return and catch the exact custom type in a small demonstration; do not catch it inside the validator.

**Reasoning:** Implement this exact contract as written: Define `NegativeMeasurementError` as a subclass of `ValueError`, then write `validate_measurement(value)` that returns non-negative values unchanged and raises your exception for `-0.1`. Keep the prompt's named data and constraints visible in the code, then establish this specific result: show one normal return and catch the exact custom type in a small demonstration; do not catch it inside the validator. That connects the answer to branch selection, loop decisions, and narrow exception boundaries.

```python
class NegativeMeasurementError(ValueError):
    """Raised when a measurement is below zero."""


def validate_measurement(value: float) -> float:
    if value < 0:
        raise NegativeMeasurementError("measurement must be non-negative")
    return value


assert validate_measurement(0.0) == 0.0
try:
    validate_measurement(-0.1)
except NegativeMeasurementError as error:
    assert "non-negative" in str(error)
else:
    raise AssertionError("negative input should fail")
```

**Verification evidence:** show one normal return and catch the exact custom type in a small demonstration; do not catch it inside the validator.

## Exercises 4–8 — Expanded mastery answers

### Exercise 4 — answer contract

**Learner contract:** **Prediction:** Predict which branch handles 0, 9, and 12 when checks are ordered as `x % 2 == 0`, `x % 3 == 0`, then both. Explain the bug. **Progressive hint:** Only the first true branch runs; test the most specific rule first. **Verify:** Record the branch selected for `0`, `9`, and `12` before/after reordering; confirm the repaired `12` reaches the combined rule.

**Reasoning:** Predict this named state change before running it: Prediction: Predict which branch handles 0, 9, and 12 when checks are ordered as `x % 2 == 0`, `x % 3 == 0`, then both. Explain the bug. Progressive hint: Only the first true branch runs; test the most specific rule first. Then compare the prediction with this proof target: Record the branch selected for `0`, `9`, and `12` before/after reordering; confirm the repaired `12` reaches the combined rule. This makes branch selection, loop decisions, and narrow exception boundaries observable instead of relying on intuition.

**Evidence to locate in the grouped implementation:** Record the branch selected for `0`, `9`, and `12` before/after reordering; confirm the repaired `12` reaches the combined rule.

### Exercise 5 — answer contract

**Learner contract:** **Tracing:** Trace `try/except/else/finally` for a successful integer parse and for invalid text. Which clauses run in each path? **Progressive hint:** `else` follows success; `finally` runs in both cases. **Verify:** Use a four-column trace for `try`, `except`, `else`, and `finally` on valid/invalid text; each clause's executed flag must match the language rules.

**Reasoning:** Trace the concrete values in this contract one step at a time: Tracing: Trace `try/except/else/finally` for a successful integer parse and for invalid text. Which clauses run in each path? Progressive hint: `else` follows success; `finally` runs in both cases. Record the named value, shape, label, or iterator position needed to establish: Use a four-column trace for `try`, `except`, `else`, and `finally` on valid/invalid text; each clause's executed flag must match the language rules. The trace exposes branch selection, loop decisions, and narrow exception boundaries directly.

**Evidence to locate in the grouped implementation:** Use a four-column trace for `try`, `except`, `else`, and `finally` on valid/invalid text; each clause's executed flag must match the language rules.

### Exercise 6 — answer contract

**Learner contract:** **Implementation:** Implement `classify_score(score)` returning fail/pass/distinction and reject scores outside 0–100 with `ValueError`. **Progressive hint:** Validate the domain before choosing a result branch. **Verify:** Assert representative scores return `fail`, `pass`, and `distinction`, then assert `-1` and `101` each raise `ValueError`.

**Reasoning:** Implement this exact contract as written: Implementation: Implement `classify_score(score)` returning fail/pass/distinction and reject scores outside 0–100 with `ValueError`. Progressive hint: Validate the domain before choosing a result branch. Keep the prompt's named data and constraints visible in the code, then establish this specific result: Assert representative scores return `fail`, `pass`, and `distinction`, then assert `-1` and `101` each raise `ValueError`. That connects the answer to branch selection, loop decisions, and narrow exception boundaries.

**Evidence to locate in the grouped implementation:** Assert representative scores return `fail`, `pass`, and `distinction`, then assert `-1` and `101` each raise `ValueError`.

### Exercise 7 — answer contract

**Learner contract:** **Debugging:** Replace a bare `except:` around parsing and calculation with the narrowest useful handler, while allowing programming errors to surface. **Progressive hint:** Keep only the conversion inside the protected block. **Verify:** Show invalid integer text is handled while a deliberate unrelated `TypeError` still reaches the test; keep only conversion inside `try`.

**Reasoning:** Reproduce the exact failure described here before changing code: Debugging: Replace a bare `except:` around parsing and calculation with the narrowest useful handler, while allowing programming errors to surface. Progressive hint: Keep only the conversion inside the protected block. Preserve that failing case, repair the violated rule, and rerun the evidence named here: Show invalid integer text is handled while a deliberate unrelated `TypeError` still reaches the test; keep only conversion inside `try`. The diagnosis depends on branch selection, loop decisions, and narrow exception boundaries.

**Evidence to locate in the grouped implementation:** Show invalid integer text is handled while a deliberate unrelated `TypeError` still reaches the test; keep only conversion inside `try`.

### Exercise 8 — answer contract

**Learner contract:** **Edge case and explanation:** Design `safe_ratio(numerator, denominator)` for a zero denominator. Choose between raising, returning `None`, or a default and justify it. **Progressive hint:** A reusable library function usually should not invent a numeric result. **Verify:** Test a nonzero ratio and a zero denominator; assert the chosen zero policy exactly and explain why no fabricated numeric answer leaks through.

**Reasoning:** Make this boundary unambiguous in code: Edge case and explanation: Design `safe_ratio(numerator, denominator)` for a zero denominator. Choose between raising, returning `None`, or a default and justify it. Progressive hint: A reusable library function usually should not invent a numeric result. Values below, at, and above the named boundary must produce the evidence Test a nonzero ratio and a zero denominator; assert the chosen zero policy exactly and explain why no fabricated numeric answer leaks through. Those cases show how branch selection, loop decisions, and narrow exception boundaries behaves at its edge.

**Evidence to locate in the grouped implementation:** Test a nonzero ratio and a zero denominator; assert the chosen zero policy exactly and explain why no fabricated numeric answer leaks through.

## Expanded mastery lab solutions

Make branch order and exception boundaries deliberate. Catch only the failure that the current layer can interpret or repair.

### Shared implementation for Exercises 4–5 — Branch and exception traces

The combined-divisibility check must come first; otherwise values such as 12
are consumed by the even branch. On successful parsing, `else` and `finally`
run. On `ValueError`, `except` and `finally` run.

### Shared implementation for Exercises 6–8 — Explicit contracts

```python
def classify_score(score: float) -> str:
    """Classify a score whose valid domain is the closed interval 0..100."""

    if not 0 <= score <= 100:
        raise ValueError("score must be between 0 and 100")
    if score >= 80:
        return "distinction"
    if score >= 60:
        return "pass"
    return "fail"


assert classify_score(80) == "distinction"  # Boundary belongs to upper band.
assert classify_score(59.9) == "fail"


def parse_count(text: str) -> int | None:
    """Return None only when text is not a valid integer."""

    try:
        # Keep the try block narrow: later calculations may reveal real bugs.
        value = int(text)
    except ValueError:
        return None
    else:
        return value


def safe_ratio(numerator: float, denominator: float) -> float:
    """Return a ratio, rejecting an undefined zero-denominator operation."""

    if denominator == 0:
        raise ZeroDivisionError("denominator must be non-zero")
    return numerator / denominator


assert parse_count("12") == 12
assert parse_count("twelve") is None
assert safe_ratio(3, 4) == 0.75
```

Raising in `safe_ratio` preserves the fact that the result is undefined. A
calling application can translate that exception into `None` or a user message
if its own contract calls for one.
