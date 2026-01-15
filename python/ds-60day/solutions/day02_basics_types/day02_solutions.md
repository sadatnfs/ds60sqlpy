# Day 02 — Solutions: Variables and Core Types

This solution provides code and commentary for each exercise.

Exercise 1: percent(n, total) -> '37.5%'

Why: Formatting is presentation logic; protect against division by zero; use round or format spec.

```python
def percent(n: float, total: float) -> str:
    if total == 0:
        return '0.0%'
    pct = (n / total) * 100
    return f"{pct:.1f}%"

assert percent(3, 8) == '37.5%'
assert percent(0, 10) == '0.0%'
```

Exercise 2: Slugify '  Data Science  ' to 'data-science'

Why: Normalize whitespace and case before replacement; strings are immutable so each method returns a new string.

```python
s = '  Data Science  '
slug = s.strip().lower().replace(' ', '-')
assert slug == 'data-science'
```

Exercise 3: Read two numbers as strings, convert safely, print sum/product

Why: Defensive parsing—report invalid inputs rather than crashing; f-strings for readable output.

```python
def to_int(s: str) -> int | None:
    try:
        return int(s)
    except ValueError:
        return None

raw_a, raw_b = '12', '7'  # replace with input() in interactive flows
A, B = to_int(raw_a), to_int(raw_b)
if A is None or B is None:
    print('Invalid number input')
else:
    print(f"sum={A + B}")
    print(f"product={A * B}")
```

Stretch: safe_float

```python
import math

def safe_float(s: str, default: float = math.nan) -> float:
    try:
        return float(s)
    except ValueError:
        print(f"bad float input: {s!r}")
        return default
```
