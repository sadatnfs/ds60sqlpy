# Day 05 — Solutions: Functions, Docstrings, and Type Hints

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

The solution is not a typing template. Read the learner contract, predict
the result, then compare decisions and evidence. The central mental model is
**function contracts, parameters, return values, scope, and type hints**.

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

### Reference pattern 1 — Make validation part of the contract

Reject an invalid domain before doing the calculation.

```python
def mean(values: list[float]) -> float:
    """Return the arithmetic mean of a non-empty list."""
    if not values:
        raise ValueError("values must not be empty")
    return sum(values) / len(values)

mean([2.0, 4.0, 9.0])
```

**Expected observation:** `5.0`. Empty input follows a deliberate exception path instead of dividing by zero accidentally.

### Reference pattern 2 — Use keyword-only parameters to make calls readable

A signature can prevent ambiguous positional calls.

```python
def discounted(price: float, *, rate: float = 0.0) -> float:
    if not 0 <= rate <= 1:
        raise ValueError("rate must be between 0 and 1")
    return price * (1 - rate)

discounted(80.0, rate=0.25)
```

**Expected observation:** `60.0`. The call labels `rate`, making `0.25` hard to confuse with another quantity.

## Exercise-by-exercise reasoning map

The numbering and learner contracts below match the guide and notebook.
Each entry explains what to reason about, how to inspect the worked code,
an alternative, an edge case, and the evidence required for completion.

### Exercise 1 — reasoning, alternatives, and proof

**Learner contract:** Implement `describe(values: list[float]) -> tuple[float, float]` returning the arithmetic mean and **population** standard deviation. **Input:** `[2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0]`. **Expected result:** `(5.0, 2.0)`. **Constraints:** compute the mean once, use squared distances, and do not import a statistics helper that performs the whole task. **Verify:** Use `math.isclose` to confirm mean `5.0` and population standard deviation `2.0`, then show empty input follows the documented failure path.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies function contracts, parameters, return values, scope, and type hints.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A tuple can return several related values; a dataclass becomes clearer when those values need durable names and behavior.

**Edge case:** Empty input, mismatched lengths, zero total weight, invalid numeric ranges, and Unicode/whitespace normalization need written policy.

**Solution evidence to inspect:** Use `math.isclose` to confirm mean `5.0` and population standard deviation `2.0`, then show empty input follows the documented failure path.

### Exercise 2 — reasoning, alternatives, and proof

**Learner contract:** Add a docstring to `describe` that states accepted input, the two tuple fields in order, and the empty-input policy. **Constraint:** choose and document one explicit behavior—this lesson's reference raises `ValueError`. **Verify:** `help(describe)` communicates the contract without reading the body.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies function contracts, parameters, return values, scope, and type hints.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A tuple can return several related values; a dataclass becomes clearer when those values need durable names and behavior.

**Edge case:** Empty input, mismatched lengths, zero total weight, invalid numeric ranges, and Unicode/whitespace normalization need written policy.

**Solution evidence to inspect:** `help(describe)` communicates the contract without reading the body.

### Exercise 3 — reasoning, alternatives, and proof

**Learner contract:** Validate `describe` near its boundary: reject an empty list and any non-finite value such as `float('nan')` with a useful `ValueError`. **Verify:** show the normal result and use two separate `try`/`except ValueError` checks for the invalid cases; do not catch errors inside the function that it cannot repair.

**Reasoning before code:** Reproduce the bad behavior on the smallest input, state the violated contract, make one repair, and rerun both the failing boundary and a normal case. Keep the diagnosis grounded in function contracts, parameters, return values, scope, and type hints.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A tuple can return several related values; a dataclass becomes clearer when those values need durable names and behavior.

**Edge case:** Empty input, mismatched lengths, zero total weight, invalid numeric ranges, and Unicode/whitespace normalization need written policy.

**Solution evidence to inspect:** show the normal result and use two separate `try`/`except ValueError` checks for the invalid cases; do not catch errors inside the function that it cannot repair.

### Exercise 4 — reasoning, alternatives, and proof

**Learner contract:** **Prediction:** Predict the result of calling a function with `items=[]` as a default three times when it appends on each call. Explain shared defaults. **Progressive hint:** Default objects are created once when `def` executes. **Verify:** Call the faulty function three times and record cumulative state, then assert the `None`-sentinel repair returns independent one-item lists on every call.

**Reasoning before code:** Evaluate the expression or state transition by hand first. Name the input state, the next operation, and the exact evidence that would falsify the prediction while applying function contracts, parameters, return values, scope, and type hints.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A tuple can return several related values; a dataclass becomes clearer when those values need durable names and behavior.

**Edge case:** Empty input, mismatched lengths, zero total weight, invalid numeric ranges, and Unicode/whitespace normalization need written policy.

**Solution evidence to inspect:** Call the faulty function three times and record cumulative state, then assert the `None`-sentinel repair returns independent one-item lists on every call.

### Exercise 5 — reasoning, alternatives, and proof

**Learner contract:** **Tracing:** Trace a local variable that shadows a global of the same name. Which binding changes, and when would `global` be required? **Progressive hint:** Assignment makes a name local unless explicitly declared otherwise. **Verify:** Record local/global values before, during, and after the call; confirm ordinary local assignment leaves the global unchanged.

**Reasoning before code:** Create a small trace table with one row per operation or input item. Record the relevant names, labels, shape, or iterator position after each step so the function contracts, parameters, return values, scope, and type hints model is visible.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A tuple can return several related values; a dataclass becomes clearer when those values need durable names and behavior.

**Edge case:** Empty input, mismatched lengths, zero total weight, invalid numeric ranges, and Unicode/whitespace normalization need written policy.

**Solution evidence to inspect:** Record local/global values before, during, and after the call; confirm ordinary local assignment leaves the global unchanged.

### Exercise 6 — reasoning, alternatives, and proof

**Learner contract:** **Implementation:** Implement typed `weighted_mean(values, weights)` with length, empty, and zero-total-weight validation. **Progressive hint:** State every invalid condition before calculating. **Verify:** Assert a known weighted mean and separately assert empty, length-mismatch, and zero-total-weight inputs raise the documented errors.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies function contracts, parameters, return values, scope, and type hints.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A tuple can return several related values; a dataclass becomes clearer when those values need durable names and behavior.

**Edge case:** Empty input, mismatched lengths, zero total weight, invalid numeric ranges, and Unicode/whitespace normalization need written policy.

**Solution evidence to inspect:** Assert a known weighted mean and separately assert empty, length-mismatch, and zero-total-weight inputs raise the documented errors.

### Exercise 7 — reasoning, alternatives, and proof

**Learner contract:** **Debugging:** Repair a function whose `*items` argument is accidentally passed as one list instead of unpacked individual items. **Progressive hint:** Compare `f(values)` with `f(*values)`. **Verify:** Capture arguments received by `f(values)` and `f(*values)`; assert the repaired call presents individual items rather than one nested list.

**Reasoning before code:** Reproduce the bad behavior on the smallest input, state the violated contract, make one repair, and rerun both the failing boundary and a normal case. Keep the diagnosis grounded in function contracts, parameters, return values, scope, and type hints.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A tuple can return several related values; a dataclass becomes clearer when those values need durable names and behavior.

**Edge case:** Empty input, mismatched lengths, zero total weight, invalid numeric ranges, and Unicode/whitespace normalization need written policy.

**Solution evidence to inspect:** Capture arguments received by `f(values)` and `f(*values)`; assert the repaired call presents individual items rather than one nested list.

### Exercise 8 — reasoning, alternatives, and proof

**Learner contract:** **Edge case and explanation:** Write a docstring for a name-normalization function and test empty, whitespace-only, and Unicode input. **Progressive hint:** Document whether empty normalized output is valid or an error. **Verify:** Test ordinary, empty, whitespace-only, and Unicode names against the docstring's stated contract; every behavior must match the documentation.

**Reasoning before code:** Turn the ambiguous boundary into an explicit contract before coding. Test values immediately below, at, and above the boundary and explain how the result follows from function contracts, parameters, return values, scope, and type hints.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** A tuple can return several related values; a dataclass becomes clearer when those values need durable names and behavior.

**Edge case:** Empty input, mismatched lengths, zero total weight, invalid numeric ranges, and Unicode/whitespace normalization need written policy.

**Solution evidence to inspect:** Test ordinary, empty, whitespace-only, and Unicode names against the docstring's stated contract; every behavior must match the documentation.
<!-- END BEGINNER SOLUTION REVIEW -->

We implement a robust function that computes mean and standard deviation with clear types, docstring, and validation.

Contents
- Exercise 1: mean/std with type hints
- Exercise 2: Add docstring and edge cases
- Exercise 3: Validate inputs and raise ValueError

---

Exercise 1+2 — mean and std with type hints and docstring
```python
from typing import Sequence, Tuple
import math

def mean_std(xs: Sequence[float], *, ddof: int = 0) -> Tuple[float, float]:
    """
    Compute the arithmetic mean and standard deviation of a sequence of numbers.

    Args:
        xs: sequence of numeric values (e.g., list[float]); may be any iterable that supports len() and indexing
        ddof: delta degrees of freedom (0 for population std, 1 for sample std)

    Returns:
        (mean, std) as floats.

    Raises:
        ValueError: if xs is empty, contains non-numbers, or ddof is invalid.
    """
    # Validate ddof first
    if ddof < 0:
        raise ValueError(f"ddof must be >= 0, got {ddof}")

    n = len(xs)                         # may raise TypeError if xs has no length
    if n == 0:
        raise ValueError("xs must be non-empty")
    if ddof >= n:
        raise ValueError(f"ddof ({ddof}) must be < len(xs) ({n})")

    # Convert to floats and validate elements
    vals: list[float] = []
    for i, x in enumerate(xs):
        try:
            vals.append(float(x))       # coerce ints to float; reject non-numeric
        except (TypeError, ValueError):
            raise ValueError(f"xs[{i}] is not a number: {x!r}") from None

    mu = sum(vals) / n
    var = sum((v - mu) ** 2 for v in vals) / (n - ddof)
    sigma = math.sqrt(var)
    return mu, sigma

# Quick checks
m, s = mean_std([1, 2, 3])
assert round(m, 3) == 2.000 and round(s, 3) == round(math.sqrt(2/3), 3)
assert mean_std([1, 2, 3], ddof=1)[0] == 2.0
```
Line-by-line highlights
- ddof lets you choose population (0) vs sample (1) std; we validate `ddof < len(xs)`.
- We coerce items to float, catching non-numeric input early with helpful indices.
- Variance uses the standard formula; `math.sqrt` computes std.

---

Exercise 3 — Input validation examples
Bad inputs and expected errors:
```python
try:
    mean_std([], ddof=0)
except ValueError as e:
    print(e)  # xs must be non-empty

try:
    mean_std([1, 'x', 3])
except ValueError as e:
    print(e)  # xs[1] is not a number: 'x'

try:
    mean_std([1, 2], ddof=2)
except ValueError as e:
    print(e)  # ddof (2) must be < len(xs) (2)
```
Notes
- Good error messages tell a user (or your future self) exactly what to fix.
- For large data, consider `statistics` module or NumPy for performance.

---

## Expanded mastery lab solutions

Design functions from their contracts: accepted inputs, return value, failure behavior, side effects, and boundary cases.

Read the reasoning before the code. Inline comments explain ownership, boundary choices, and why each check exists; assertions turn the stated contract into executable evidence.

### Practice 1 — Mutable defaults

A list default is shared across calls. Use `None` as a sentinel and create a new
list inside the function when the caller supplied no collection.

### Practices 2–5 — Contracts make functions predictable

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
