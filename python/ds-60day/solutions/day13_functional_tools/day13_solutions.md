# Day 13 — Solutions: Functional Tools (itertools, functools, map/filter)

We implement grouping with itertools.groupby and create specialized functions with functools.partial.

Contents
- Exercise 1: Group pairs by key with itertools.groupby
- Exercise 2: Use partial to specialize a function

---

Exercise 1 — Group by key
Note: itertools.groupby requires data to be sorted by the same key.

```python
import itertools as it
from operator import itemgetter
from typing import Iterable, Tuple, Hashable, List

Pair = Tuple[Hashable, int]

def group_pairs(pairs: Iterable[Pair]) -> dict[Hashable, list[int]]:
    # 1) sort by key so groupby can group consecutive items
    pairs_sorted = sorted(pairs, key=itemgetter(0))
    out: dict[Hashable, list[int]] = {}
    # 2) groupby yields (key, iterator-over-group)
    for k, group in it.groupby(pairs_sorted, key=itemgetter(0)):
        vals = [v for _, v in group]         # 3) extract second element
        out[k] = vals
    return out

# Demo
pairs = [("b",2),("a",1),("a",3),("b",4)]
assert group_pairs(pairs) == {"a":[1,3], "b":[2,4]}
```
Line-by-line
- sorted by itemgetter(0) aligns with groupby’s key
- group is an iterator over consecutive items with the same key

Alternative: collections.defaultdict (often simpler and order-preserving per input).

---

Exercise 2 — partial to specialize
Given a generic power function, make square and cube variants.

```python
from functools import partial

def power(base: float, exp: float) -> float:
    return base ** exp

square = partial(power, exp=2)
cube   = partial(power, exp=3)

assert square(5) == 25
assert cube(2) == 8
```
Notes
- partial binds some parameters, returning a new callable with fewer arguments.
- Combine with map for pipelines, but prefer comprehensions for clarity when possible.

---

## Exercise-by-exercise reference

Every numbered learner exercise has a matching entry here. The original
worked examples remain above; the expanded answers below add heavily
commented code, explicit reasoning, and executable checks.

### Exercise 1 — Original lesson practice

**Prompt:** Group `(key, value)` pairs by key with `itertools.groupby`. **Hint:** inspect what happens to keys that reappear later; arrange the input by the same key before grouping.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 2 — Original lesson practice

**Prompt:** Use `partial` to create a specialized function from a more general one. **Hint:** identify the argument that stays constant across many calls and bind only that argument.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 3 — Prediction

**Prompt:** Predict what remains after calling `next` on a `map` object and then converting it to a list.

**Reasoning checkpoint:** `map` is a lazy one-shot iterator in Python 3. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 4 — Tracing

**Prompt:** Trace `sorted(records, key=lambda row: (row['team'], -row['score']))` and explain the tuple key.

**Reasoning checkpoint:** Tuple components are compared left to right. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 5 — Implementation

**Prompt:** Implement `compose(*functions)` so `compose(f, g)(x)` applies `g` then `f`, and handle no functions as identity.

**Reasoning checkpoint:** Apply the reversed function sequence to the current value. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 6 — Debugging

**Prompt:** Repair lambdas created in a loop that all use the final loop value.

**Reasoning checkpoint:** Bind the current value as a default argument or use a factory function. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 7 — Edge case and explanation

**Prompt:** Refactor a pipeline that prints inside `map` into pure transforms plus one explicit presentation step.

**Reasoning checkpoint:** Pure stages are easier to test and reuse. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

## Expanded mastery lab solutions

Use functional tools when they make data flow clearer. Preserve laziness intentionally and keep side effects at explicit boundaries.

Read the reasoning before the code. Inline comments explain ownership, boundary choices, and why each check exists; assertions turn the stated contract into executable evidence.

### Practices 1–2 — Lazy iterators and tuple ordering

```python
doubled = map(lambda value: value * 2, [1, 2, 3])
assert next(doubled) == 2
assert list(doubled) == [4, 6]

records = [
    {"team": "B", "score": 8},
    {"team": "A", "score": 7},
    {"team": "A", "score": 9},
]
ordered = sorted(records, key=lambda row: (row["team"], -row["score"]))
assert [row["score"] for row in ordered] == [9, 7, 8]
```

### Practices 3–5 — Composition, binding, and pure stages

```python
from collections.abc import Callable
from typing import Any


def compose(*functions: Callable[[Any], Any]) -> Callable[[Any], Any]:
    """Compose right-to-left; no functions produce the identity operation."""

    def composed(value: Any) -> Any:
        current = value
        for function in reversed(functions):
            current = function(current)
        return current

    return composed


pipeline = compose(str.upper, str.strip)
assert pipeline("  data ") == "DATA"
assert compose()(42) == 42

# Bind each loop value now, rather than looking it up later.
multipliers = [lambda value, factor=factor: value * factor for factor in range(3)]
assert [function(10) for function in multipliers] == [0, 10, 20]

normalize = lambda text: text.strip().casefold()
normalized = list(map(normalize, [" A ", " B "]))  # Pure transformation.
rendered = ", ".join(normalized)                    # Presentation boundary.
assert rendered == "a, b"
```
