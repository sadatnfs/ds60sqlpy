# Day 05 — Solutions: Functions, Docstrings, and Type Hints

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

## Exercise-by-exercise reference

Every numbered learner exercise has a matching entry here. The original
worked examples remain above; the expanded answers below add heavily
commented code, explicit reasoning, and executable checks.

### Exercise 1 — Original lesson practice

**Prompt:** Write an annotated function that computes the mean and population standard deviation of a list of numbers. **Hint:** calculate the mean once, then use each value's squared distance from that mean.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 2 — Original lesson practice

**Prompt:** Add a docstring that states the return shape and empty-input behavior. **Hint:** decide on the contract before coding: return a sentinel or raise a specific exception.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 3 — Original lesson practice

**Prompt:** Reject invalid inputs with `ValueError`. **Hint:** validate the collection and its values near the function boundary; do not catch errors the function cannot repair.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 4 — Prediction

**Prompt:** Predict the result of calling a function with `items=[]` as a default three times when it appends on each call. Explain shared defaults.

**Reasoning checkpoint:** Default objects are created once when `def` executes. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 5 — Tracing

**Prompt:** Trace a local variable that shadows a global of the same name. Which binding changes, and when would `global` be required?

**Reasoning checkpoint:** Assignment makes a name local unless explicitly declared otherwise. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 6 — Implementation

**Prompt:** Implement typed `weighted_mean(values, weights)` with length, empty, and zero-total-weight validation.

**Reasoning checkpoint:** State every invalid condition before calculating. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 7 — Debugging

**Prompt:** Repair a function whose `*items` argument is accidentally passed as one list instead of unpacked individual items.

**Reasoning checkpoint:** Compare `f(values)` with `f(*values)`. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 8 — Edge case and explanation

**Prompt:** Write a docstring for a name-normalization function and test empty, whitespace-only, and Unicode input.

**Reasoning checkpoint:** Document whether empty normalized output is valid or an error. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

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
