# Day 04 — Solutions: Loops, Comprehensions, and Generators

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

The solution is not a typing template. Read the learner contract, predict
the result, then compare decisions and evidence. The central mental model is
**iteration, eager collection building, and lazy generators**.

An iterable is a source that can provide values one at a time. A `for`
loop asks for each next value, binds it to a loop name, and runs the
indented body. Direct iteration communicates “use each value”; use
`enumerate` when both position and value matter, and `range` when you
truly need a sequence of integers.

A comprehension eagerly builds a new collection. Read
`[transform(item) for item in source if keep(item)]` from the middle:
take each item from the source, keep matching items, then transform
them. A generator uses `yield` or parentheses to produce values lazily.
It remembers its position, performs work only when consumed, and is
normally exhausted after one pass.

### Vocabulary used in the worked answers

- **iterable:** an object able to provide an iterator, such as a list or range.
- **iterator:** a stateful one-way cursor that provides the next value.
- **iteration:** one pass through successive values.
- **comprehension:** compact syntax that eagerly constructs a collection.
- **generator:** an iterator that computes values lazily.
- **exhaustion:** the state after an iterator has no more values.

### Reference pattern 1 — Translate an append loop one clause at a time

Use the loop as a readable specification before compressing it.

```python
temperatures = [-4, 0, 7, 12]
warm_fahrenheit = []
for celsius in temperatures:
    if celsius > 0:
        warm_fahrenheit.append(celsius * 9 / 5 + 32)

compact = [c * 9 / 5 + 32 for c in temperatures if c > 0]
(warm_fahrenheit, compact, warm_fahrenheit == compact)
```

**Expected observation:** `([44.6, 53.6], [44.6, 53.6], True)`. The two forms implement the same filter and transformation.

### Reference pattern 2 — Observe a generator's saved position

Consumption advances the iterator instead of restarting it.

```python
squares = (number**2 for number in range(4))
first = next(squares)
rest = list(squares)
after_exhaustion = list(squares)
(first, rest, after_exhaustion)
```

**Expected observation:** `(0, [1, 4, 9], [])`. Materializing `rest` consumes everything that remained.

## Exercise-by-exercise reasoning map

The numbering and learner contracts below match the guide and notebook.
Each entry explains what to reason about, how to inspect the worked code,
an alternative, an edge case, and the evidence required for completion.

### Exercise 1 — reasoning, alternatives, and proof

**Learner contract:** Start with `numbers = [-3, -1, 0, 2, 5]`. Write an ordinary loop that appends the **squares of strictly positive values** to `positive_squares`, then write an equivalent list comprehension named `compact_squares`. **Expected result:** both are `[4, 25]`. **Constraints:** do not mutate `numbers`, and keep the filter (`> 0`) distinct from the transformation (`value ** 2`). **Verify:** assert the two results are equal and the input is unchanged.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies iteration, eager collection building, and lazy generators.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Choose a normal loop for side effects or several decisions, a comprehension for one clear collection transformation, and a generator for streaming.

**Edge case:** Empty inputs, a non-positive batch size, a final partial batch, and inclusive versus exclusive endpoints must be explicit.

**Solution evidence to inspect:** assert the two results are equal and the input is unchanged.

### Exercise 2 — reasoning, alternatives, and proof

**Learner contract:** Implement `evens_through(limit)` as a generator that yields even integers from `0` through `limit` **inclusive**. **Inputs to verify:** `-1`, `0`, `1`, `2`, and `7`. **Expected results:** `[]`, `[0]`, `[0]`, `[0, 2]`, and `[0, 2, 4, 6]`. **Constraints:** use `yield`, return no stored list, and document the inclusive endpoint. **Verify:** Assert the exact five expected lists for limits `-1`, `0`, `1`, `2`, and `7`; also confirm `inspect.isgenerator(evens_through(2))` is true.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies iteration, eager collection building, and lazy generators.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Choose a normal loop for side effects or several decisions, a comprehension for one clear collection transformation, and a generator for streaming.

**Edge case:** Empty inputs, a non-positive batch size, a final partial batch, and inclusive versus exclusive endpoints must be explicit.

**Solution evidence to inspect:** Assert the exact five expected lists for limits `-1`, `0`, `1`, `2`, and `7`; also confirm `inspect.isgenerator(evens_through(2))` is true.

### Exercise 3 — reasoning, alternatives, and proof

**Learner contract:** For `items = ['red', 'blue', 'red', 'green', 'blue', 'red']`, build a frequency mapping whose expected value is `{'red': 3, 'blue': 2, 'green': 1}`. **First:** implement an explicit one-pass loop with `dict.get`. **Then:** compare it with `collections.Counter`. **Constraint:** do not repeatedly call `items.count` in production code. **Verify:** assert both mappings agree and explain their time-cost difference.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies iteration, eager collection building, and lazy generators.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Choose a normal loop for side effects or several decisions, a comprehension for one clear collection transformation, and a generator for streaming.

**Edge case:** Empty inputs, a non-positive batch size, a final partial batch, and inclusive versus exclusive endpoints must be explicit.

**Solution evidence to inspect:** assert both mappings agree and explain their time-cost difference.

### Exercise 4 — reasoning, alternatives, and proof

**Learner contract:** **Prediction:** Create a generator expression, consume one item with `next`, then convert the rest to a list. Predict what remains and why. **Progressive hint:** Iterators remember their current position and are usually one-shot. **Verify:** Assert the first consumed square is `0`, the remaining list is `[1, 4, 9]`, and a third pass is empty; explain the saved iterator position.

**Reasoning before code:** Evaluate the expression or state transition by hand first. Name the input state, the next operation, and the exact evidence that would falsify the prediction while applying iteration, eager collection building, and lazy generators.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Choose a normal loop for side effects or several decisions, a comprehension for one clear collection transformation, and a generator for streaming.

**Edge case:** Empty inputs, a non-positive batch size, a final partial batch, and inclusive versus exclusive endpoints must be explicit.

**Solution evidence to inspect:** Assert the first consumed square is `0`, the remaining list is `[1, 4, 9]`, and a third pass is empty; explain the saved iterator position.

### Exercise 5 — reasoning, alternatives, and proof

**Learner contract:** **Tracing:** Trace `[n * 10 for n in range(6) if n % 2]` one input at a time. **Progressive hint:** Evaluate the filter before the output expression. **Verify:** Build a six-row trace for inputs `0..5` containing filter result and optional output; confirm the final list is `[10, 30, 50]`.

**Reasoning before code:** Create a small trace table with one row per operation or input item. Record the relevant names, labels, shape, or iterator position after each step so the iteration, eager collection building, and lazy generators model is visible.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Choose a normal loop for side effects or several decisions, a comprehension for one clear collection transformation, and a generator for streaming.

**Edge case:** Empty inputs, a non-positive batch size, a final partial batch, and inclusive versus exclusive endpoints must be explicit.

**Solution evidence to inspect:** Build a six-row trace for inputs `0..5` containing filter result and optional output; confirm the final list is `[10, 30, 50]`.

### Exercise 6 — reasoning, alternatives, and proof

**Learner contract:** **Implementation:** Implement `batched(items, size)` yielding lists of at most `size`, including a final partial batch. **Progressive hint:** Accumulate, yield when full, then handle leftovers after the loop. **Verify:** Assert `list(batched(range(5), 2)) == [[0, 1], [2, 3], [4]]`, empty input yields no batches, and size `0` raises.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies iteration, eager collection building, and lazy generators.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Choose a normal loop for side effects or several decisions, a comprehension for one clear collection transformation, and a generator for streaming.

**Edge case:** Empty inputs, a non-positive batch size, a final partial batch, and inclusive versus exclusive endpoints must be explicit.

**Solution evidence to inspect:** Assert `list(batched(range(5), 2)) == [[0, 1], [2, 3], [4]]`, empty input yields no batches, and size `0` raises.

### Exercise 7 — reasoning, alternatives, and proof

**Learner contract:** **Debugging:** Explain and repair a loop that removes negative values from the same list it is iterating over. **Progressive hint:** Build a new list or iterate over a copy. **Verify:** Keep the original failing list as evidence, then assert the repaired result removes every negative without skipping adjacent negatives or mutating the source unexpectedly.

**Reasoning before code:** Reproduce the bad behavior on the smallest input, state the violated contract, make one repair, and rerun both the failing boundary and a normal case. Keep the diagnosis grounded in iteration, eager collection building, and lazy generators.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Choose a normal loop for side effects or several decisions, a comprehension for one clear collection transformation, and a generator for streaming.

**Edge case:** Empty inputs, a non-positive batch size, a final partial batch, and inclusive versus exclusive endpoints must be explicit.

**Solution evidence to inspect:** Keep the original failing list as evidence, then assert the repaired result removes every negative without skipping adjacent negatives or mutating the source unexpectedly.

### Exercise 8 — reasoning, alternatives, and proof

**Learner contract:** **Edge case and explanation:** Define whether an even-number generator 'up to N' includes N and test N values -1, 0, 1, 2, and 3. **Progressive hint:** Boundary examples turn ambiguous English into a contract. **Verify:** Assert exact output for `N` values `-1, 0, 1, 2, 3`; identify which tests prove the endpoint is inclusive and how negative input behaves.

**Reasoning before code:** Turn the ambiguous boundary into an explicit contract before coding. Test values immediately below, at, and above the boundary and explain how the result follows from iteration, eager collection building, and lazy generators.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** Choose a normal loop for side effects or several decisions, a comprehension for one clear collection transformation, and a generator for streaming.

**Edge case:** Empty inputs, a non-positive batch size, a final partial batch, and inclusive versus exclusive endpoints must be explicit.

**Solution evidence to inspect:** Assert exact output for `N` values `-1, 0, 1, 2, 3`; identify which tests prove the endpoint is inclusive and how negative input behaves.
<!-- END BEGINNER SOLUTION REVIEW -->

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
