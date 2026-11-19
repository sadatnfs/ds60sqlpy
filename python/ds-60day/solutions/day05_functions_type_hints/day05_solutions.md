# Day 5 Solutions: Functions, Docstrings, and Type Hints

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

## Exercises 1-3: Worked answers

### Exercise 1: worked answer

**Learner contract:** Implement `describe(values: list[float]) -> tuple[float, float]` returning the arithmetic mean and **population** standard deviation. **Input:** `[2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0]`. **Expected result:** `(5.0, 2.0)`. **Constraints:** compute the mean once, use squared distances, and do not import a statistics helper that performs the whole task. **Verify:** Use `math.isclose` to confirm mean `5.0` and population standard deviation `2.0`, then show empty input follows the documented failure path.

**Reasoning:** The mean is computed once and reused for every squared distance, which is clearer and cheaper than recomputing it inside the sum. Population standard deviation divides the summed squared distances (32) by `n` (8), giving variance 4.0 and standard deviation 2.0; dividing by `n - 1`, the sample formula used by `statistics.stdev`, gives about 2.14 and is the most likely wrong answer. Validation comes first, so empty input raises a clear `ValueError` instead of a `ZeroDivisionError`. The exact `== (5.0, 2.0)` comparison is safe here because every intermediate value is exactly representable; use `math.isclose` for general inputs.

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

### Exercise 2: worked answer

**Learner contract:** Add a docstring to `describe` that states accepted input, the two tuple fields in order, and the empty-input policy. **Constraint:** choose and document one explicit behavior, this lesson's reference raises `ValueError`. **Verify:** capture `help(describe)` output and assert it names the accepted input, mean, population standard deviation, tuple order, and empty-input `ValueError` without reading the body.

**Reasoning:** A docstring is the contract a caller reads with `help(describe)`, so it must answer what the code alone does not show: which input is accepted, what the two tuple positions mean, and what happens for empty input. Naming "population standard deviation" matters because it distinguishes the `n` divisor from the sample `n - 1` divisor. The assertions check the docstring text, a lightweight guard against someone changing the behavior without updating the documentation. A vague docstring such as "computes stats" would pass a non-empty check but fail every specific one.

The docstring belongs directly below the signature and names tuple
order plus failure behavior. The Exercise 1 implementation already
includes the complete docstring.

```python
assert describe.__doc__ is not None
assert "population standard deviation" in describe.__doc__
assert "ValueError" in describe.__doc__
```

### Exercise 3: worked answer

**Learner contract:** Validate `describe` near its boundary: reject an empty list and any non-finite value such as `float('nan')` with a useful `ValueError`. **Verify:** show the normal result and use two separate `try`/`except ValueError` checks for the invalid cases; do not catch errors inside the function that it cannot repair.

**Reasoning:** Validation belongs at the function's boundary, before any arithmetic: an empty list would otherwise fail later with a `ZeroDivisionError` from the mean, and a `nan` would quietly turn every result into `nan`. `math.isfinite` rejects `nan` and both infinities in one test. Each invalid input is checked in its own `try` block so that one passing case cannot hide the other, and the `else` branch fails loudly if no exception arrives. The function does not catch these errors itself, because it cannot repair them; the caller decides what to do.

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

## Exercises 4-8: Expanded mastery answers

### Exercise 4: answer contract

**Learner contract:** **Prediction:** Predict the result of calling a function with `items=[]` as a default three times when it appends on each call. Explain shared defaults. **Progressive hint:** Default objects are created once when `def` executes. **Verify:** Call the faulty function three times and record cumulative state, then assert the `None`-sentinel repair returns independent one-item lists on every call.

**Reasoning:** Default values are evaluated once, when `def` runs, so `items=[]` creates one list that every call without an `items` argument shares. Appending on each call therefore returns `[1]`, then `[1, 2]`, then `[1, 2, 3]` from calls that look independent, and all three results are the same list object. The repair uses `None` as a sentinel and creates a new list inside the function; the shared implementation for Exercise 4 below runs the faulty and repaired versions side by side. Copying a caller-supplied list with `list(items)` also avoids mutating the caller's data.

### Exercise 5: answer contract

**Learner contract:** **Tracing:** Trace a local variable that shadows a global of the same name. Which binding changes, and when would `global` be required? **Progressive hint:** Assignment makes a name local unless explicitly declared otherwise. **Verify:** Record local/global values before, during, and after the call; confirm ordinary local assignment leaves the global unchanged.

**Reasoning:** Assigning to `label` inside `local_label` creates a local name that exists only during the call, so the module-level `label` keeps the value `"global"` before, during, and after the call. Python decides this when it compiles the function: any assignment in the body makes the name local for the whole function, which is why reading `label` before assigning it there raises `UnboundLocalError`. `global label` would be needed only if the function had to rebind the module-level name, which is rarely the right design; returning a value is clearer. The shared implementation for Exercises 5-8 asserts both values.

### Exercise 6: answer contract

**Learner contract:** **Implementation:** Implement typed `weighted_mean(values, weights)` with length, empty, and zero-total-weight validation. **Progressive hint:** State every invalid condition before calculating. **Verify:** Assert a known weighted mean and separately assert empty, length-mismatch, and zero-total-weight inputs raise the documented errors.

**Reasoning:** Each invalid condition is checked before any arithmetic and gets its own message: empty values, a length mismatch, and weights that sum to zero (which would divide by zero). For `[10, 20]` with weights `[1, 3]`, the weighted sum is 70 and the total weight 4, so the mean is 17.5. The length check matters because `zip` silently stops at the shorter input: `zip([1, 2, 3], [1, 1])` drops the 3 without any error. Since Python 3.10, `zip(values, weights, strict=True)` raises instead.

### Exercise 7: answer contract

**Learner contract:** **Debugging:** Repair a function whose `*items` argument is accidentally passed as one list instead of unpacked individual items. **Progressive hint:** Compare `f(values)` with `f(*values)`. **Verify:** Capture arguments received by `f(values)` and `f(*values)`; assert the repaired call presents individual items rather than one nested list.

**Reasoning:** `join_words(*items)` collects every positional argument into the tuple `items`. Calling `join_words(words)` passes one argument, the whole list, so `items` becomes `(["clear", "contract"],)` and `" ".join` fails with `TypeError` because its only element is a list, not a string. Calling `join_words(*words)` unpacks the list so each word arrives as its own argument, which the shared implementation for Exercises 5-8 asserts with `"clear contract"`. Printing `items` inside the function is the quickest way to see which shape arrived.

### Exercise 8: answer contract

**Learner contract:** **Edge case and explanation:** Write a docstring for a name-normalization function and test empty, whitespace-only, and Unicode input. **Progressive hint:** Document whether empty normalized output is valid or an error. **Verify:** Test ordinary, empty, whitespace-only, and Unicode names against the docstring's stated contract; every behavior must match the documentation.

**Reasoning:** The docstring states the policy: whitespace is trimmed and collapsed, and a name with no visible characters is an error rather than an empty string. `" ".join(text.split())` handles leading, trailing, and repeated whitespace in one step, and non-ASCII names such as `Zoë` pass through unchanged because nothing filters to ASCII. Raising for blank input keeps an empty name from looking valid later. The shared implementation for Exercises 5-8 tests the ordinary, Unicode, empty, and whitespace-only cases.

## Expanded mastery lab solutions

Design functions from their contracts: accepted inputs, return value, failure behavior, side effects, and boundary cases.

### Shared implementation for Exercise 4: Mutable defaults

A list default is shared across calls. Use `None` as a sentinel and create a new
list inside the function when the caller supplied no collection.

```python
def collect_faulty(value: int, items: list[int] = []) -> list[int]:  # noqa: B006
    items.append(value)
    return items


first = collect_faulty(1)
second = collect_faulty(2)
third = collect_faulty(3)
assert first is second is third  # one default list shared by every call
assert third == [1, 2, 3]


def collect_fixed(value: int, items: list[int] | None = None) -> list[int]:
    result = [] if items is None else list(items)
    result.append(value)
    return result


assert [collect_fixed(1), collect_fixed(2), collect_fixed(3)] == [[1], [2], [3]]
```

### Shared implementation for Exercises 5-8: Contracts make functions predictable

```python
from collections.abc import Sequence


def collect(value: int, items: list[int] | None = None) -> list[int]:
    """Return a list containing prior supplied items plus ``value``."""

    result = [] if items is None else list(items)  # Also avoids mutating caller data.
    result.append(value)
    return result


label = "global"


def local_label() -> str:
    label = "local"  # This is a distinct local binding.
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
for blank in ("", "   "):
    try:
        normalize_name(blank)
    except ValueError:
        pass
    else:
        raise AssertionError(f"blank name {blank!r} should raise")
```
