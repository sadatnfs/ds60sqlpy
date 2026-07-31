# Day 13 — Solutions: Functional Tools (itertools, functools, map/filter)

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

The solution is not a typing template. Read the learner contract, predict
the result, then compare decisions and evidence. The central mental model is
**functions as values and composable iterable tools**.

Python functions are objects: they can be assigned to names, passed as
arguments, and returned. A higher-order function accepts or returns
another function. This enables small reusable operations, but an
ordinary named function is usually clearer than a dense lambda once
logic needs explanation.

`map` transforms, `filter` selects, `itertools` composes lazy iteration,
and `functools` supplies function adapters and caching. List
comprehensions often read more naturally for one transformation/filter;
lazy tools matter when the input is a stream or too large to materialize.
Avoid `reduce` when a named loop or built-in such as `sum`, `min`, or
`max` states the intent better.

### Vocabulary used in the worked answers

- **first-class function:** a function usable as an ordinary runtime value.
- **higher-order function:** a function that accepts or returns functions.
- **lambda:** a small anonymous single-expression function.
- **lazy iterator:** an iterator that computes values only when requested.
- **accumulator:** the progressively combined value in a fold/reduction.
- **cache:** stored results reused for repeated equivalent calls.

### Reference pattern 1 — Pass a named function into a lazy transformation

Keep the operation testable on its own.

```python
def normalize_name(text: str) -> str:
    return " ".join(text.strip().title().split())

raw_names = ["  ada lovelace", "GRACE   HOPPER  "]
normalized_iter = map(normalize_name, raw_names)
list(normalized_iter)
```

**Expected observation:** `['Ada Lovelace', 'Grace Hopper']`. `map` is lazy; `list` consumes it.

### Reference pattern 2 — Compose lazy filtering and slicing

Generate only as many values as the consumer requests.

```python
from itertools import islice

squares = (number**2 for number in range(100))
even_squares = filter(lambda value: value % 2 == 0, squares)
list(islice(even_squares, 5))
```

**Expected observation:** `[0, 4, 16, 36, 64]`. `islice` stops after five accepted values rather than consuming all 100 squares.

## Exercise-by-exercise reasoning map

The numbering and learner contracts below match the guide and notebook.
Each entry explains what to reason about, how to inspect the worked code,
an alternative, an edge case, and the evidence required for completion.

### Exercise 1 — reasoning, alternatives, and proof

**Learner contract:** Use `itertools.groupby` to group records that are already sorted by a category key. **Inputs:** include the same category in separated positions before sorting. **Expected behavior:** after explicit sorting, each category appears once with all of its records. **Constraint:** explain why `groupby` groups adjacent runs rather than globally collecting unsorted data. **Verify:** Show the unsorted input produces separated runs, then assert the sorted grouping has one entry per category and preserves every record.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies functions as values and composable iterable tools.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use a comprehension for a clear transform/filter, `itertools` for lazy composition, and an explicit loop when stateful branching matters.

**Edge case:** One-shot iterators, infinite inputs, side effects inside transformations, unhashable cache arguments, and empty reductions require care.

**Solution evidence to inspect:** Show the unsorted input produces separated runs, then assert the sorted grouping has one entry per category and preserves every record.

### Exercise 2 — reasoning, alternatives, and proof

**Learner contract:** Use `functools.reduce` to compute a product for `[2, 3, 4]`, giving an explicit identity so empty input returns `1`. **Then:** implement the same result with a named loop and compare readability. **Verify:** both return `24` and both define empty behavior; state why `sum`/`math.prod` is preferable in ordinary production code.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies functions as values and composable iterable tools.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use a comprehension for a clear transform/filter, `itertools` for lazy composition, and an explicit loop when stateful branching matters.

**Edge case:** One-shot iterators, infinite inputs, side effects inside transformations, unhashable cache arguments, and empty reductions require care.

**Solution evidence to inspect:** both return `24` and both define empty behavior; state why `sum`/`math.prod` is preferable in ordinary production code.

### Exercise 3 — reasoning, alternatives, and proof

**Learner contract:** **Prediction:** Predict what remains after calling `next` on a `map` object and then converting it to a list. **Progressive hint:** `map` is a lazy one-shot iterator in Python 3. **Verify:** Assert the first mapped value and exact remaining list, then confirm another pass is empty because the map iterator is exhausted.

**Reasoning before code:** Evaluate the expression or state transition by hand first. Name the input state, the next operation, and the exact evidence that would falsify the prediction while applying functions as values and composable iterable tools.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use a comprehension for a clear transform/filter, `itertools` for lazy composition, and an explicit loop when stateful branching matters.

**Edge case:** One-shot iterators, infinite inputs, side effects inside transformations, unhashable cache arguments, and empty reductions require care.

**Solution evidence to inspect:** Assert the first mapped value and exact remaining list, then confirm another pass is empty because the map iterator is exhausted.

### Exercise 4 — reasoning, alternatives, and proof

**Learner contract:** **Tracing:** Trace `sorted(records, key=lambda row: (row['team'], -row['score']))` and explain the tuple key. **Progressive hint:** Tuple components are compared left to right. **Verify:** Compute each tuple key beside its record and assert final order groups team ascending and score descending within team.

**Reasoning before code:** Create a small trace table with one row per operation or input item. Record the relevant names, labels, shape, or iterator position after each step so the functions as values and composable iterable tools model is visible.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use a comprehension for a clear transform/filter, `itertools` for lazy composition, and an explicit loop when stateful branching matters.

**Edge case:** One-shot iterators, infinite inputs, side effects inside transformations, unhashable cache arguments, and empty reductions require care.

**Solution evidence to inspect:** Compute each tuple key beside its record and assert final order groups team ascending and score descending within team.

### Exercise 5 — reasoning, alternatives, and proof

**Learner contract:** **Implementation:** Implement `compose(*functions)` so `compose(f, g)(x)` applies `g` then `f`, and handle no functions as identity. **Progressive hint:** Apply the reversed function sequence to the current value. **Verify:** Assert composition order with noncommutative functions and assert `compose()(value)` returns the original value unchanged.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies functions as values and composable iterable tools.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use a comprehension for a clear transform/filter, `itertools` for lazy composition, and an explicit loop when stateful branching matters.

**Edge case:** One-shot iterators, infinite inputs, side effects inside transformations, unhashable cache arguments, and empty reductions require care.

**Solution evidence to inspect:** Assert composition order with noncommutative functions and assert `compose()(value)` returns the original value unchanged.

### Exercise 6 — reasoning, alternatives, and proof

**Learner contract:** **Debugging:** Repair lambdas created in a loop that all use the final loop value. **Progressive hint:** Bind the current value as a default argument or use a factory function. **Verify:** Call every produced function and show the faulty results share the final loop value; assert the factory/default-binding repair preserves each intended value.

**Reasoning before code:** Reproduce the bad behavior on the smallest input, state the violated contract, make one repair, and rerun both the failing boundary and a normal case. Keep the diagnosis grounded in functions as values and composable iterable tools.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use a comprehension for a clear transform/filter, `itertools` for lazy composition, and an explicit loop when stateful branching matters.

**Edge case:** One-shot iterators, infinite inputs, side effects inside transformations, unhashable cache arguments, and empty reductions require care.

**Solution evidence to inspect:** Call every produced function and show the faulty results share the final loop value; assert the factory/default-binding repair preserves each intended value.

### Exercise 7 — reasoning, alternatives, and proof

**Learner contract:** **Edge case and explanation:** Refactor a pipeline that prints inside `map` into pure transforms plus one explicit presentation step. **Progressive hint:** Pure stages are easier to test and reuse. **Verify:** Assert transformed values are identical before/after refactoring and capture presentation output only in the final explicit step.

**Reasoning before code:** Turn the ambiguous boundary into an explicit contract before coding. Test values immediately below, at, and above the boundary and explain how the result follows from functions as values and composable iterable tools.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Use a comprehension for a clear transform/filter, `itertools` for lazy composition, and an explicit loop when stateful branching matters.

**Edge case:** One-shot iterators, infinite inputs, side effects inside transformations, unhashable cache arguments, and empty reductions require care.

**Solution evidence to inspect:** Assert transformed values are identical before/after refactoring and capture presentation output only in the final explicit step.
<!-- END BEGINNER SOLUTION REVIEW -->

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
