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
