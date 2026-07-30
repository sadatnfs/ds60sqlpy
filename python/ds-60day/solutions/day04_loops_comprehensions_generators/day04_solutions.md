# Day 04 — Solutions: Loops, Comprehensions, and Generators

Beginner-friendly, line-by-line explanations for each exercise.

Contents
- Exercise 1: Loop → list comprehension
- Exercise 2: Even-number generator up to N
- Exercise 3: Frequency dictionary via comprehension (and Counter)

---

Exercise 1 — Convert a loop that builds a filtered list into a comprehension
Goal: Given a list of numbers, keep the squares of the positive ones.

Loop version (starting point)
```python
nums = [-2, -1, 0, 3, 5]
out = []
for x in nums:                  # 1) iterate each element
    if x > 0:                   # 2) keep only positives
        out.append(x * x)       # 3) append its square
```

Comprehension version
```python
nums = [-2, -1, 0, 3, 5]
out = [x * x for x in nums if x > 0]
```
Line-by-line mapping
- [x * x ...] → what to compute per kept element (the square)
- for x in nums → where elements come from (the input iterable)
- if x > 0 → filter condition; only truthy items are included

Notes
- List comprehensions are concise and often faster than manual loops for simple transforms + filters.
- Prefer readability: if the expression becomes long or uses nested loops, break it back into a normal loop.

---

Exercise 2 — Generator that yields even numbers up to N
Goal: Produce a sequence lazily (one-at-a-time) to avoid building large lists in memory.

```python
def evens_up_to(n: int):
    """Yield even integers from 0 up to and including n.

    Args:
        n: non-negative upper bound

    Yields:
        even integers in ascending order
    """
    if n < 0:                          # 1) guard clause for invalid input
        raise ValueError("n must be >= 0")
    for i in range(0, n + 1, 2):       # 2) start at 0, step by 2
        yield i                        # 3) produce one value at a time

# Demo
list(evens_up_to(10))  # [0, 2, 4, 6, 8, 10]
```
Why a generator?
- Memory-friendly for large n (doesn’t build a full list)
- Composable with other generators or streaming pipelines

Variation: generator expression
```python
evens = (i for i in range(101) if i % 2 == 0)
```

---

Exercise 3 — Build a frequency dict using a comprehension
Goal: Count occurrences of items. We’ll show both a comprehension-based approach and the purpose-built tools.

Comprehension + set baseline
```python
items = list("datascience")
unique = set(items)                                   # unique symbols
freq = {ch: sum(1 for x in items if x == ch) for ch in unique}
freq  # e.g., {'d': 1, 'a': 2, ...}
```
Line-by-line
- unique = set(items) → we only compute one count per unique element
- {ch: ... for ch in unique} → dict comprehension mapping char → count
- sum(1 for x in items if x == ch) → count matches by summing 1s

Better: collections.Counter (clearer and faster)
```python
from collections import Counter
items = list("datascience")
freq = Counter(items)           # Counter({'e': 3, 'a': 2, 's': 2, 'd': 1, 't': 1, 'c': 1, 'i': 1, 'n': 1})
```
Trade-offs
- Comprehension teaches the mechanics but is O(n^2) in worst case
- Counter is the idiomatic O(n) solution and should be preferred in practice

---

## Exercise-by-exercise reference

Every numbered learner exercise has a matching entry here. The original
worked examples remain above; the expanded answers below add heavily
commented code, explicit reasoning, and executable checks.

### Exercise 1 — Original lesson practice

**Prompt:** Replace a loop that appends filtered values with a list comprehension. **Hint:** identify the output expression, the `for` clause, then the filter.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 2 — Original lesson practice

**Prompt:** Write a generator that yields even numbers up to `N`. **Hint:** decide explicitly whether "up to" includes `N`, and test both an even and odd `N`.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 3 — Original lesson practice

**Prompt:** Build a frequency dictionary. **Hint:** a comprehension can count each distinct item, but first consider the repeated-work cost; compare it with `collections.Counter`.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 4 — Prediction

**Prompt:** Create a generator expression, consume one item with `next`, then convert the rest to a list. Predict what remains and why.

**Reasoning checkpoint:** Iterators remember their current position and are usually one-shot. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 5 — Tracing

**Prompt:** Trace `[n * 10 for n in range(6) if n % 2]` one input at a time.

**Reasoning checkpoint:** Evaluate the filter before the output expression. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 6 — Implementation

**Prompt:** Implement `batched(items, size)` yielding lists of at most `size`, including a final partial batch.

**Reasoning checkpoint:** Accumulate, yield when full, then handle leftovers after the loop. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 7 — Debugging

**Prompt:** Explain and repair a loop that removes negative values from the same list it is iterating over.

**Reasoning checkpoint:** Build a new list or iterate over a copy. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 8 — Edge case and explanation

**Prompt:** Define whether an even-number generator 'up to N' includes N and test N values -1, 0, 1, 2, and 3.

**Reasoning checkpoint:** Boundary examples turn ambiguous English into a contract. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

## Expanded mastery lab solutions

Trace iteration boundaries and laziness. Prefer a clear loop when a comprehension would hide state changes or several decisions.

Read the reasoning before the code. Inline comments explain ownership, boundary choices, and why each check exists; assertions turn the stated contract into executable evidence.

### Practices 1–2 — Iteration traces

```python
stream = (n * n for n in range(4))
first = next(stream)        # Consumes 0 ** 2.
remaining = list(stream)    # Continues at 1; it does not restart.
assert first == 0
assert remaining == [1, 4, 9]

# The filter runs first. Only odd n values reach n * 10.
assert [n * 10 for n in range(6) if n % 2] == [10, 30, 50]
```

### Practices 3–5 — Batches, safe filtering, and explicit endpoints

```python
from collections.abc import Iterable, Iterator
from typing import TypeVar

T = TypeVar("T")


def batched(items: Iterable[T], size: int) -> Iterator[list[T]]:
    """Yield non-empty lists with at most ``size`` items."""

    if size <= 0:
        raise ValueError("size must be positive")
    batch: list[T] = []
    for item in items:
        batch.append(item)
        if len(batch) == size:
            yield batch
            batch = []      # New list: already-yielded batches stay unchanged.
    if batch:
        yield batch         # Preserve the final partial batch.


values = [3, -1, -2, 4]
non_negative = [value for value in values if value >= 0]
assert values == [3, -1, -2, 4]   # The input was not mutated mid-iteration.
assert non_negative == [3, 4]


def evens_through(n: int) -> Iterator[int]:
    """Yield even integers from 0 through n, inclusive."""

    yield from range(0, n + 1, 2)


assert list(batched(range(5), 2)) == [[0, 1], [2, 3], [4]]
assert [list(evens_through(n)) for n in (-1, 0, 1, 2, 3)] == [
    [], [0], [0], [0, 2], [0, 2]
]
```
