# Day 05 — Solutions: Functions, Docstrings, and Type Hints

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

These worked answers demonstrate **function contracts, parameters, return values, scope, and type hints**. Predict each named
result before comparing your attempt with its matching assertions.

A function gives a name to a reusable behavior. Its contract says which
inputs are accepted, what it returns, which failures it raises, and
whether it changes anything outside itself. Parameters are names in the
definition; arguments are actual values supplied by a caller.

A call creates a local scope. Names assigned there normally disappear
when the call returns. A `return` sends one value to the caller and
stops that call. Type hints document intended types and support static
tools, but Python does not enforce them automatically at runtime.
Defaults are evaluated once when `def` runs, so mutable defaults should
normally be replaced by `None` plus a fresh object inside the function.

### Vocabulary used in the worked answers

- **function:** a named reusable block that can accept inputs and return a value.
- **parameter:** a name declared in a function signature.
- **argument:** a value supplied for a parameter during a call.
- **return value:** the object sent back to the caller.
- **scope:** the region in which a name can be resolved.
- **type hint:** machine-readable documentation of an intended type.

### How to compare an answer

For this lesson's **function contracts, parameters, return values, scope, and type hints** model, follow the exact values from each learner contract through its function or expression to the assertion that proves the expected behavior; then change one boundary input and make that assertion fail once before accepting the answer.
<!-- END BEGINNER SOLUTION REVIEW -->

## Exercises 1–3 — Worked answers

### Exercise 1 — worked answer

**Learner contract:** Implement `describe(values: list[float]) -> tuple[float, float]` returning the arithmetic mean and **population** standard deviation. **Input:** `[2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0]`. **Expected result:** `(5.0, 2.0)`. **Constraints:** compute the mean once, use squared distances, and do not import a statistics helper that performs the whole task. **Verify:** Use `math.isclose` to confirm mean `5.0` and population standard deviation `2.0`, then show empty input follows the documented failure path.

**Reasoning:** Implement this exact contract as written: Implement `describe(values: list[float]) -> tuple[float, float]` returning the arithmetic mean and population standard deviation. Input: `[2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0]`. Expected result: `(5.0, 2.0)`. Constraints: compute the mean once, use squared distances, and do not import a statistics helper that performs the whole task. Keep the prompt's named data and constraints visible in the code, then establish this specific result: Use `math.isclose` to confirm mean `5.0` and population standard deviation `2.0`, then show empty input follows the documented failure path. That connects the answer to function contracts, parameters, return values, scope, and type hints.

```python
import math


def describe(values: list[float]) -> tuple[float, float]:
    """Return mean and population standard deviation.

    Raises:
        ValueError: If values is empty or contains a non-finite value.
    """

    if not values:
        raise ValueError("values must not be empty")
    if not all(math.isfinite(value) for value in values):
        raise ValueError("values must be finite")
    mean = sum(values) / len(values)
    variance = sum((value - mean) ** 2 for value in values) / len(values)
    return mean, math.sqrt(variance)


result = describe([2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0])
assert result == (5.0, 2.0)
```

**Verification evidence:** Use `math.isclose` to confirm mean `5.0` and population standard deviation `2.0`, then show empty input follows the documented failure path.

### Exercise 2 — worked answer

**Learner contract:** Add a docstring to `describe` that states accepted input, the two tuple fields in order, and the empty-input policy. **Constraint:** choose and document one explicit behavior—this lesson's reference raises `ValueError`. **Verify:** capture `help(describe)` output and assert it names the accepted input, mean, population standard deviation, tuple order, and empty-input `ValueError` without reading the body.

**Reasoning:** Implement this exact contract as written: Add a docstring to `describe` that states accepted input, the two tuple fields in order, and the empty-input policy. Constraint: choose and document one explicit behavior—this lesson's reference raises `ValueError`. Keep the prompt's named data and constraints visible in the code, then establish this specific result: capture `help(describe)` output and assert it names the accepted input, mean, population standard deviation, tuple order, and empty-input `ValueError` without reading the body. That connects the answer to function contracts, parameters, return values, scope, and type hints.

The docstring belongs directly below the signature and names tuple
order plus failure behavior. The Exercise 1 implementation already
includes the complete docstring.

```python
assert describe.__doc__ is not None
assert "population standard deviation" in describe.__doc__
assert "ValueError" in describe.__doc__
```

**Verification evidence:** capture `help(describe)` output and assert it names the accepted input, mean, population standard deviation, tuple order, and empty-input `ValueError` without reading the body.

### Exercise 3 — worked answer

**Learner contract:** Validate `describe` near its boundary: reject an empty list and any non-finite value such as `float('nan')` with a useful `ValueError`. **Verify:** show the normal result and use two separate `try`/`except ValueError` checks for the invalid cases; do not catch errors inside the function that it cannot repair.

**Reasoning:** Reproduce the exact failure described here before changing code: Validate `describe` near its boundary: reject an empty list and any non-finite value such as `float('nan')` with a useful `ValueError`. Preserve that failing case, repair the violated rule, and rerun the evidence named here: show the normal result and use two separate `try`/`except ValueError` checks for the invalid cases; do not catch errors inside the function that it cannot repair. The diagnosis depends on function contracts, parameters, return values, scope, and type hints.

```python
for invalid in ([], [1.0, float("nan")]):
    try:
        describe(invalid)
    except ValueError:
        pass
    else:
        raise AssertionError(f"expected ValueError for {invalid!r}")
```

Validation occurs before arithmetic so the error states the real
contract instead of surfacing a later divide-by-zero or NaN.

**Verification evidence:** show the normal result and use two separate `try`/`except ValueError` checks for the invalid cases; do not catch errors inside the function that it cannot repair.

## Exercises 4–8 — Expanded mastery answers

### Exercise 4 — answer contract

**Learner contract:** **Prediction:** Predict the result of calling a function with `items=[]` as a default three times when it appends on each call. Explain shared defaults. **Progressive hint:** Default objects are created once when `def` executes. **Verify:** Call the faulty function three times and record cumulative state, then assert the `None`-sentinel repair returns independent one-item lists on every call.

**Reasoning:** Predict this named state change before running it: Prediction: Predict the result of calling a function with `items=[]` as a default three times when it appends on each call. Explain shared defaults. Progressive hint: Default objects are created once when `def` executes. Then compare the prediction with this proof target: Call the faulty function three times and record cumulative state, then assert the `None`-sentinel repair returns independent one-item lists on every call. This makes function contracts, parameters, return values, scope, and type hints observable instead of relying on intuition.

**Evidence to locate in the grouped implementation:** Call the faulty function three times and record cumulative state, then assert the `None`-sentinel repair returns independent one-item lists on every call.

### Exercise 5 — answer contract

**Learner contract:** **Tracing:** Trace a local variable that shadows a global of the same name. Which binding changes, and when would `global` be required? **Progressive hint:** Assignment makes a name local unless explicitly declared otherwise. **Verify:** Record local/global values before, during, and after the call; confirm ordinary local assignment leaves the global unchanged.

**Reasoning:** Trace the concrete values in this contract one step at a time: Tracing: Trace a local variable that shadows a global of the same name. Which binding changes, and when would `global` be required? Progressive hint: Assignment makes a name local unless explicitly declared otherwise. Record the named value, shape, label, or iterator position needed to establish: Record local/global values before, during, and after the call; confirm ordinary local assignment leaves the global unchanged. The trace exposes function contracts, parameters, return values, scope, and type hints directly.

**Evidence to locate in the grouped implementation:** Record local/global values before, during, and after the call; confirm ordinary local assignment leaves the global unchanged.

### Exercise 6 — answer contract

**Learner contract:** **Implementation:** Implement typed `weighted_mean(values, weights)` with length, empty, and zero-total-weight validation. **Progressive hint:** State every invalid condition before calculating. **Verify:** Assert a known weighted mean and separately assert empty, length-mismatch, and zero-total-weight inputs raise the documented errors.

**Reasoning:** Implement this exact contract as written: Implementation: Implement typed `weighted_mean(values, weights)` with length, empty, and zero-total-weight validation. Progressive hint: State every invalid condition before calculating. Keep the prompt's named data and constraints visible in the code, then establish this specific result: Assert a known weighted mean and separately assert empty, length-mismatch, and zero-total-weight inputs raise the documented errors. That connects the answer to function contracts, parameters, return values, scope, and type hints.

**Evidence to locate in the grouped implementation:** Assert a known weighted mean and separately assert empty, length-mismatch, and zero-total-weight inputs raise the documented errors.

### Exercise 7 — answer contract

**Learner contract:** **Debugging:** Repair a function whose `*items` argument is accidentally passed as one list instead of unpacked individual items. **Progressive hint:** Compare `f(values)` with `f(*values)`. **Verify:** Capture arguments received by `f(values)` and `f(*values)`; assert the repaired call presents individual items rather than one nested list.

**Reasoning:** Reproduce the exact failure described here before changing code: Debugging: Repair a function whose `*items` argument is accidentally passed as one list instead of unpacked individual items. Progressive hint: Compare `f(values)` with `f(*values)`. Preserve that failing case, repair the violated rule, and rerun the evidence named here: Capture arguments received by `f(values)` and `f(*values)`; assert the repaired call presents individual items rather than one nested list. The diagnosis depends on function contracts, parameters, return values, scope, and type hints.

**Evidence to locate in the grouped implementation:** Capture arguments received by `f(values)` and `f(*values)`; assert the repaired call presents individual items rather than one nested list.

### Exercise 8 — answer contract

**Learner contract:** **Edge case and explanation:** Write a docstring for a name-normalization function and test empty, whitespace-only, and Unicode input. **Progressive hint:** Document whether empty normalized output is valid or an error. **Verify:** Test ordinary, empty, whitespace-only, and Unicode names against the docstring's stated contract; every behavior must match the documentation.

**Reasoning:** Make this boundary unambiguous in code: Edge case and explanation: Write a docstring for a name-normalization function and test empty, whitespace-only, and Unicode input. Progressive hint: Document whether empty normalized output is valid or an error. Values below, at, and above the named boundary must produce the evidence Test ordinary, empty, whitespace-only, and Unicode names against the docstring's stated contract; every behavior must match the documentation. Those cases show how function contracts, parameters, return values, scope, and type hints behaves at its edge.

**Evidence to locate in the grouped implementation:** Test ordinary, empty, whitespace-only, and Unicode names against the docstring's stated contract; every behavior must match the documentation.

## Expanded mastery lab solutions

Design functions from their contracts: accepted inputs, return value, failure behavior, side effects, and boundary cases.

### Shared implementation for Exercise 4 — Mutable defaults

A list default is shared across calls. Use `None` as a sentinel and create a new
list inside the function when the caller supplied no collection.

### Shared implementation for Exercises 5–8 — Contracts make functions predictable

```python
from collections.abc import Sequence


def collect(value: int, items: list[int] | None = None) -> list[int]:
    """Return a list containing prior supplied items plus ``value``."""

    result = [] if items is None else list(items)  # Also avoids mutating caller data.
    result.append(value)
    return result


label = "global"


def local_label() -> str:
    label = "local"          # This is a distinct local binding.
    return label


def weighted_mean(values: Sequence[float], weights: Sequence[float]) -> float:
    """Return the weighted mean after validating the parallel sequences."""

    if not values:
        raise ValueError("values must not be empty")
    if len(values) != len(weights):
        raise ValueError("values and weights must have equal length")
    total_weight = sum(weights)
    if total_weight == 0:
        raise ValueError("weights must not sum to zero")
    numerator = sum(value * weight for value, weight in zip(values, weights))
    return numerator / total_weight


def join_words(*items: str) -> str:
    return " ".join(items)


def normalize_name(text: str) -> str:
    """Trim and collapse whitespace; reject a name with no visible characters."""

    normalized = " ".join(text.split())
    if not normalized:
        raise ValueError("name must not be blank")
    return normalized


assert collect(1) == [1] and collect(2) == [2]
assert local_label() == "local" and label == "global"
assert weighted_mean([10, 20], [1, 3]) == 17.5
words = ["clear", "contract"]
assert join_words(*words) == "clear contract"
assert normalize_name("  Ada   Lovelace ") == "Ada Lovelace"
assert normalize_name("  Zoë  ") == "Zoë"
```
