# Day 4 Solutions: Loops, Comprehensions, and Generators

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

## Exercises 1-3: Worked answers

### Exercise 1: worked answer

**Learner contract:** Start with `numbers = [-3, -1, 0, 2, 5]`. Write an ordinary loop that appends the **squares of strictly positive values** to `positive_squares`, then write an equivalent list comprehension named `compact_squares`. **Expected result:** both are `[4, 25]`. **Constraints:** do not mutate `numbers`, and keep the filter (`> 0`) distinct from the transformation (`value ** 2`). **Verify:** assert the two results are equal and the input is unchanged.

**Reasoning:** Filter and transformation answer separate questions: `value > 0` decides which items survive, and `value ** 2` decides what each survivor becomes. Zero is the boundary: `0 > 0` is false, so it is excluded, which is why the result is `[4, 25]` and not `[0, 4, 25]`. A common wrong answer squares first and then filters the squares (`value ** 2 > 0`), which keeps the negative numbers because their squares are positive. Neither version touches `numbers`; the loop appends to a new list and the comprehension builds one.

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

### Exercise 2: worked answer

**Learner contract:** Implement `evens_through(limit)` as a generator that yields even integers from `0` through `limit` **inclusive**. **Inputs to verify:** `-1`, `0`, `1`, `2`, and `7`. **Expected results:** `[]`, `[0]`, `[0]`, `[0, 2]`, and `[0, 2, 4, 6]`. **Constraints:** use `yield`, return no stored list, and document the inclusive endpoint. **Verify:** Assert the exact five expected lists for limits `-1`, `0`, `1`, `2`, and `7`; also confirm `inspect.isgenerator(evens_through(2))` is true.

**Reasoning:** `range(0, limit + 1, 2)` encodes "through `limit`" directly: `range` stops before its end, so the `+ 1` is what includes 0 for `limit = 0` and 2 for `limit = 2`, while 7 stays out for `limit = 7` because it is odd. A negative limit produces an empty range, so the generator yields nothing instead of raising. Because the body contains `yield`, calling the function returns a generator object without running the body, which is what `inspect.isgenerator` checks. Forgetting the `+ 1` still passes the `-1`, `1`, and `7` cases but fails `0` and `2`, which is why both boundaries are in the test list.

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

### Exercise 3: worked answer

**Learner contract:** For `items = ['red', 'blue', 'red', 'green', 'blue', 'red']`, build a frequency mapping whose expected value is `{'red': 3, 'blue': 2, 'green': 1}`. **First:** implement an explicit one-pass loop with `dict.get`. **Then:** compare it with `collections.Counter`. **Constraint:** do not repeatedly call `items.count` in production code. **Verify:** assert both mappings agree and explain their time-cost difference.

**Reasoning:** One pass with `frequencies.get(item, 0) + 1` visits each item once, so the cost grows with the length of the list. Calling `items.count(item)` for each distinct value rescans the whole list every time, which becomes quadratic when many values are distinct. `Counter` performs the same single pass and adds conveniences such as `most_common`. The two mappings compare equal because dictionary equality ignores insertion order; if you need a particular display order, sort explicitly.

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

## Exercises 4-8: Expanded mastery answers

### Exercise 4: answer contract

**Learner contract:** **Prediction:** Create a generator expression, consume one item with `next`, then convert the rest to a list. Predict what remains and why. **Progressive hint:** Iterators remember their current position and are usually one-shot. **Verify:** Assert the first consumed square is `0`, the remaining list is `[1, 4, 9]`, and a third pass is empty; explain the saved iterator position.

**Reasoning:** A generator expression produces values lazily and remembers its position. `next(stream)` consumes the first square, 0, so `list(stream)` continues from 1 and returns `[1, 4, 9]`; it does not restart. A third pass gets `[]` because the generator is exhausted and cannot rewind. The usual wrong prediction is `[0, 1, 4, 9]`, which treats the generator like a list that can be read again. The shared implementation for Exercises 4-5 below asserts these values; to iterate twice, store the values in a list or create a new generator.

### Exercise 5: answer contract

**Learner contract:** **Tracing:** Trace `[n * 10 for n in range(6) if n % 2]` one input at a time. **Progressive hint:** Evaluate the filter before the output expression. **Verify:** Build a six-row trace for inputs `0..5` containing filter result and optional output; confirm the final list is `[10, 30, 50]`.

**Reasoning:** Read the comprehension as: for each `n` in `range(6)`, test `n % 2`, and only when that is truthy compute `n * 10`. For 0, 2, and 4 the remainder is 0, which is falsy, so nothing is produced; for 1, 3, and 5 the remainder is 1 and the outputs are 10, 30, and 50. Writing the six-row trace shows that the output expression never runs for filtered-out inputs, which matters when that expression is expensive or could fail. The final assertion in the shared implementation for Exercises 4-5 checks `[10, 30, 50]`.

### Exercise 6: answer contract

**Learner contract:** **Implementation:** Implement `batched(items, size)` yielding lists of at most `size`, including a final partial batch. **Progressive hint:** Accumulate, yield when full, then handle leftovers after the loop. **Verify:** Assert `list(batched(range(5), 2)) == [[0, 1], [2, 3], [4]]`, empty input yields no batches, and size `0` raises.

**Reasoning:** `batched` accumulates items and yields the list whenever it reaches `size`, then starts a new list; creating a new list instead of clearing the old one keeps already-yielded batches unchanged for the caller. After the loop, a non-empty leftover is yielded as the final partial batch, the step most often forgotten: without it, pairs from `range(5)` lose the 4. Validating `size <= 0` first matters because a zero size would never fill a batch. The shared implementation for Exercises 6-8 tests the normal case, empty input, and the zero-size error; Python 3.12 also provides `itertools.batched`, which yields tuples.

### Exercise 7: answer contract

**Learner contract:** **Debugging:** Explain and repair a loop that removes negative values from the same list it is iterating over. **Progressive hint:** Build a new list or iterate over a copy. **Verify:** Keep the original failing list as evidence, then assert the repaired result removes every negative without skipping adjacent negatives or mutating the source unexpectedly.

**Reasoning:** Removing items from a list while a `for` loop walks it shifts every later item one position left, so the loop skips the element right after each removal. With `[3, -1, -2, 4]`, removing `-1` moves `-2` into a position the loop has already passed, so `-2` survives. Building a new list with a comprehension avoids the problem and leaves the source unchanged, which the shared implementation for Exercises 6-8 asserts. Iterating over a copy (`for value in values[:]`) also works when in-place removal is genuinely required.

### Exercise 8: answer contract

**Learner contract:** **Edge case and explanation:** Define whether an even-number generator 'up to N' includes N and test N values -1, 0, 1, 2, and 3. **Progressive hint:** Boundary examples turn ambiguous English into a contract. **Verify:** Assert exact output for `N` values `-1, 0, 1, 2, 3`; identify which tests prove the endpoint is inclusive and how negative input behaves.

**Reasoning:** "Up to N" is ambiguous English, so tests fix the contract: `N = 2` returning `[0, 2]` proves the endpoint is inclusive, and `N = 3` returning `[0, 2]` shows that an odd endpoint simply has no even value at the top. `N = 0` returning `[0]` and `N = -1` returning `[]` define the low edge: zero is even and included, and a negative limit yields nothing instead of raising. The shared implementation for Exercises 6-8 asserts all five cases. Writing the expected lists before the code is what turns the ambiguity into a decision.

## Expanded mastery lab solutions

Trace iteration boundaries and laziness. Prefer a clear loop when a comprehension would hide state changes or several decisions.

### Shared implementation for Exercises 4-5: Iteration traces

```python
stream = (n * n for n in range(4))
first = next(stream)  # Consumes 0 ** 2.
remaining = list(stream)  # Continues at 1; it does not restart.
assert first == 0
assert remaining == [1, 4, 9]

# The filter runs first. Only odd n values reach n * 10.
assert [n * 10 for n in range(6) if n % 2] == [10, 30, 50]
```

### Shared implementation for Exercises 6-8: Batches, safe filtering, and explicit endpoints

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
            batch = []  # New list: already-yielded batches stay unchanged.
    if batch:
        yield batch  # Preserve the final partial batch.


values = [3, -1, -2, 4]
non_negative = [value for value in values if value >= 0]
assert values == [3, -1, -2, 4]  # The input was not mutated mid-iteration.
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
assert [list(evens_through(n)) for n in (-1, 0, 1, 2, 3)] == [[], [0], [0], [0, 2], [0, 2]]
```
