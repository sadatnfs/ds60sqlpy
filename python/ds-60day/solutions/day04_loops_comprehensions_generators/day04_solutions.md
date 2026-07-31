# Day 04 — Solutions: Loops, Comprehensions, and Generators

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

These worked answers demonstrate **iteration, eager collection building, and lazy generators**. Predict each named
result before comparing your attempt with its matching assertions.

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

### How to compare an answer

For this lesson's **iteration, eager collection building, and lazy generators** model, follow the exact values from each learner contract through its function or expression to the assertion that proves the expected behavior; then change one boundary input and make that assertion fail once before accepting the answer.
<!-- END BEGINNER SOLUTION REVIEW -->

## Exercises 1–3 — Worked answers

### Exercise 1 — worked answer

**Learner contract:** Start with `numbers = [-3, -1, 0, 2, 5]`. Write an ordinary loop that appends the **squares of strictly positive values** to `positive_squares`, then write an equivalent list comprehension named `compact_squares`. **Expected result:** both are `[4, 25]`. **Constraints:** do not mutate `numbers`, and keep the filter (`> 0`) distinct from the transformation (`value ** 2`). **Verify:** assert the two results are equal and the input is unchanged.

**Reasoning:** Implement this exact contract as written: Start with `numbers = [-3, -1, 0, 2, 5]`. Write an ordinary loop that appends the squares of strictly positive values to `positive_squares`, then write an equivalent list comprehension named `compact_squares`. Expected result: both are `[4, 25]`. Constraints: do not mutate `numbers`, and keep the filter (`> 0`) distinct from the transformation (`value ** 2`). Keep the prompt's named data and constraints visible in the code, then establish this specific result: assert the two results are equal and the input is unchanged. That connects the answer to iteration, eager collection building, and lazy generators.

```python
numbers = [-3, -1, 0, 2, 5]
positive_squares = []
for value in numbers:
    if value > 0:
        positive_squares.append(value**2)

compact_squares = [value**2 for value in numbers if value > 0]
assert positive_squares == compact_squares == [4, 25]
assert numbers == [-3, -1, 0, 2, 5]
```

The output expression, source, and filter map directly from the loop to
the comprehension.

**Verification evidence:** assert the two results are equal and the input is unchanged.

### Exercise 2 — worked answer

**Learner contract:** Implement `evens_through(limit)` as a generator that yields even integers from `0` through `limit` **inclusive**. **Inputs to verify:** `-1`, `0`, `1`, `2`, and `7`. **Expected results:** `[]`, `[0]`, `[0]`, `[0, 2]`, and `[0, 2, 4, 6]`. **Constraints:** use `yield`, return no stored list, and document the inclusive endpoint. **Verify:** Assert the exact five expected lists for limits `-1`, `0`, `1`, `2`, and `7`; also confirm `inspect.isgenerator(evens_through(2))` is true.

**Reasoning:** Implement this exact contract as written: Implement `evens_through(limit)` as a generator that yields even integers from `0` through `limit` inclusive. Inputs to verify: `-1`, `0`, `1`, `2`, and `7`. Expected results: `[]`, `[0]`, `[0]`, `[0, 2]`, and `[0, 2, 4, 6]`. Constraints: use `yield`, return no stored list, and document the inclusive endpoint. Keep the prompt's named data and constraints visible in the code, then establish this specific result: Assert the exact five expected lists for limits `-1`, `0`, `1`, `2`, and `7`; also confirm `inspect.isgenerator(evens_through(2))` is true. That connects the answer to iteration, eager collection building, and lazy generators.

```python
from collections.abc import Iterator
import inspect


def evens_through(limit: int) -> Iterator[int]:
    """Yield even integers from zero through ``limit``, inclusive."""

    yield from range(0, limit + 1, 2)


expected = {
    -1: [],
    0: [0],
    1: [0],
    2: [0, 2],
    7: [0, 2, 4, 6],
}
assert {limit: list(evens_through(limit)) for limit in expected} == expected
assert inspect.isgenerator(evens_through(2))
```

`range(0, limit + 1, 2)` makes the inclusive endpoint explicit. When
`limit` is negative, the range is empty, so the generator yields
nothing instead of raising an unrelated error.

**Verification evidence:** Assert the exact five expected lists for limits `-1`, `0`, `1`, `2`, and `7`; also confirm `inspect.isgenerator(evens_through(2))` is true.

### Exercise 3 — worked answer

**Learner contract:** For `items = ['red', 'blue', 'red', 'green', 'blue', 'red']`, build a frequency mapping whose expected value is `{'red': 3, 'blue': 2, 'green': 1}`. **First:** implement an explicit one-pass loop with `dict.get`. **Then:** compare it with `collections.Counter`. **Constraint:** do not repeatedly call `items.count` in production code. **Verify:** assert both mappings agree and explain their time-cost difference.

**Reasoning:** Implement this exact contract as written: For `items = ['red', 'blue', 'red', 'green', 'blue', 'red']`, build a frequency mapping whose expected value is `{'red': 3, 'blue': 2, 'green': 1}`. First: implement an explicit one-pass loop with `dict.get`. Then: compare it with `collections.Counter`. Constraint: do not repeatedly call `items.count` in production code. Keep the prompt's named data and constraints visible in the code, then establish this specific result: assert both mappings agree and explain their time-cost difference. That connects the answer to iteration, eager collection building, and lazy generators.

```python
from collections import Counter

items = ["red", "blue", "red", "green", "blue", "red"]
frequencies: dict[str, int] = {}
for item in items:
    frequencies[item] = frequencies.get(item, 0) + 1

counter_frequencies = dict(Counter(items))
expected = {"red": 3, "blue": 2, "green": 1}
assert frequencies == counter_frequencies == expected
```

The explicit loop and `Counter` are both one-pass approaches; repeated
`items.count(item)` would rescan the list for each distinct value.

**Verification evidence:** assert both mappings agree and explain their time-cost difference.

## Exercises 4–8 — Expanded mastery answers

### Exercise 4 — answer contract

**Learner contract:** **Prediction:** Create a generator expression, consume one item with `next`, then convert the rest to a list. Predict what remains and why. **Progressive hint:** Iterators remember their current position and are usually one-shot. **Verify:** Assert the first consumed square is `0`, the remaining list is `[1, 4, 9]`, and a third pass is empty; explain the saved iterator position.

**Reasoning:** Predict this named state change before running it: Prediction: Create a generator expression, consume one item with `next`, then convert the rest to a list. Predict what remains and why. Progressive hint: Iterators remember their current position and are usually one-shot. Then compare the prediction with this proof target: Assert the first consumed square is `0`, the remaining list is `[1, 4, 9]`, and a third pass is empty; explain the saved iterator position. This makes iteration, eager collection building, and lazy generators observable instead of relying on intuition.

**Evidence to locate in the grouped implementation:** Assert the first consumed square is `0`, the remaining list is `[1, 4, 9]`, and a third pass is empty; explain the saved iterator position.

### Exercise 5 — answer contract

**Learner contract:** **Tracing:** Trace `[n * 10 for n in range(6) if n % 2]` one input at a time. **Progressive hint:** Evaluate the filter before the output expression. **Verify:** Build a six-row trace for inputs `0..5` containing filter result and optional output; confirm the final list is `[10, 30, 50]`.

**Reasoning:** Trace the concrete values in this contract one step at a time: Tracing: Trace `[n * 10 for n in range(6) if n % 2]` one input at a time. Progressive hint: Evaluate the filter before the output expression. Record the named value, shape, label, or iterator position needed to establish: Build a six-row trace for inputs `0..5` containing filter result and optional output; confirm the final list is `[10, 30, 50]`. The trace exposes iteration, eager collection building, and lazy generators directly.

**Evidence to locate in the grouped implementation:** Build a six-row trace for inputs `0..5` containing filter result and optional output; confirm the final list is `[10, 30, 50]`.

### Exercise 6 — answer contract

**Learner contract:** **Implementation:** Implement `batched(items, size)` yielding lists of at most `size`, including a final partial batch. **Progressive hint:** Accumulate, yield when full, then handle leftovers after the loop. **Verify:** Assert `list(batched(range(5), 2)) == [[0, 1], [2, 3], [4]]`, empty input yields no batches, and size `0` raises.

**Reasoning:** Implement this exact contract as written: Implementation: Implement `batched(items, size)` yielding lists of at most `size`, including a final partial batch. Progressive hint: Accumulate, yield when full, then handle leftovers after the loop. Keep the prompt's named data and constraints visible in the code, then establish this specific result: Assert `list(batched(range(5), 2)) == [[0, 1], [2, 3], [4]]`, empty input yields no batches, and size `0` raises. That connects the answer to iteration, eager collection building, and lazy generators.

**Evidence to locate in the grouped implementation:** Assert `list(batched(range(5), 2)) == [[0, 1], [2, 3], [4]]`, empty input yields no batches, and size `0` raises.

### Exercise 7 — answer contract

**Learner contract:** **Debugging:** Explain and repair a loop that removes negative values from the same list it is iterating over. **Progressive hint:** Build a new list or iterate over a copy. **Verify:** Keep the original failing list as evidence, then assert the repaired result removes every negative without skipping adjacent negatives or mutating the source unexpectedly.

**Reasoning:** Reproduce the exact failure described here before changing code: Debugging: Explain and repair a loop that removes negative values from the same list it is iterating over. Progressive hint: Build a new list or iterate over a copy. Preserve that failing case, repair the violated rule, and rerun the evidence named here: Keep the original failing list as evidence, then assert the repaired result removes every negative without skipping adjacent negatives or mutating the source unexpectedly. The diagnosis depends on iteration, eager collection building, and lazy generators.

**Evidence to locate in the grouped implementation:** Keep the original failing list as evidence, then assert the repaired result removes every negative without skipping adjacent negatives or mutating the source unexpectedly.

### Exercise 8 — answer contract

**Learner contract:** **Edge case and explanation:** Define whether an even-number generator 'up to N' includes N and test N values -1, 0, 1, 2, and 3. **Progressive hint:** Boundary examples turn ambiguous English into a contract. **Verify:** Assert exact output for `N` values `-1, 0, 1, 2, 3`; identify which tests prove the endpoint is inclusive and how negative input behaves.

**Reasoning:** Make this boundary unambiguous in code: Edge case and explanation: Define whether an even-number generator 'up to N' includes N and test N values -1, 0, 1, 2, and 3. Progressive hint: Boundary examples turn ambiguous English into a contract. Values below, at, and above the named boundary must produce the evidence Assert exact output for `N` values `-1, 0, 1, 2, 3`; identify which tests prove the endpoint is inclusive and how negative input behaves. Those cases show how iteration, eager collection building, and lazy generators behaves at its edge.

**Evidence to locate in the grouped implementation:** Assert exact output for `N` values `-1, 0, 1, 2, 3`; identify which tests prove the endpoint is inclusive and how negative input behaves.

## Expanded mastery lab solutions

Trace iteration boundaries and laziness. Prefer a clear loop when a comprehension would hide state changes or several decisions.

### Shared implementation for Exercises 4–5 — Iteration traces

```python
stream = (n * n for n in range(4))
first = next(stream)        # Consumes 0 ** 2.
remaining = list(stream)    # Continues at 1; it does not restart.
assert first == 0
assert remaining == [1, 4, 9]

# The filter runs first. Only odd n values reach n * 10.
assert [n * 10 for n in range(6) if n % 2] == [10, 30, 50]
```

### Shared implementation for Exercises 6–8 — Batches, safe filtering, and explicit endpoints

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
assert list(batched([], 2)) == []
try:
    list(batched(range(3), 0))
except ValueError as error:
    assert "size must be positive" in str(error)
else:
    raise AssertionError("zero batch size should raise")
assert [list(evens_through(n)) for n in (-1, 0, 1, 2, 3)] == [
    [], [0], [0], [0, 2], [0, 2]
]
```
