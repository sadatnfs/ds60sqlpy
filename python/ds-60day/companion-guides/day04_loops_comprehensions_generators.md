# Day 4 — Loops, Comprehensions, and Generators

**Level:** Beginner

All three tools process iterables. The important choice is whether to perform
an action, build a collection now, or yield values lazily.

## Learning objectives

By the end of this lesson, you can:

- iterate safely with `range`, `enumerate`, and direct iteration;
- translate a simple append loop into a readable comprehension;
- build list, set, and dictionary comprehensions; and
- write and consume a generator without assuming it is a stored list.

## Prerequisites

Complete Day 3 (`python-03`): branches, loops, and exception behavior.

## Vocabulary and mental model

- **Iterable:** an object that can provide values one at a time.
- **Iterator:** the stateful object that tracks the next value.
- **Comprehension:** an expression that eagerly constructs a collection.
- **Generator:** a lazy iterator produced by `yield` or a generator expression.
- **Exhaustion:** once an iterator has no next value, another pass is empty.

Use a loop for side effects or complex branching, a comprehension for one clear
transformation, and a generator when values can be streamed.

## Worked example

```python
readings = [12, -1, 18, 7, 21]
valid_squares = [value**2 for value in readings if value >= 0]


def batches(values: list[int], size: int):
    for start in range(0, len(values), size):
        yield values[start : start + size]


print(list(batches(valid_squares, 2)))
```

The comprehension creates its result immediately. `batches(...)` does no work
until it is iterated.

## Exercises and progressive hints

1. Replace a loop that appends filtered values with a list comprehension.
   **Hint:** identify the output expression, the `for` clause, then the filter.
2. Write a generator that yields even numbers up to `N`. **Hint:** decide
   explicitly whether "up to" includes `N`, and test both an even and odd `N`.
3. Build a frequency dictionary. **Hint:** a comprehension can count each
   distinct item, but first consider the repeated-work cost; compare it with
   `collections.Counter`.

### Additional mastery practice

Trace iteration boundaries and laziness. Prefer a clear loop when a comprehension would hide state changes or several decisions.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

4. **Prediction:** Create a generator expression, consume one item with `next`, then convert the rest to a list. Predict what remains and why.
   **Progressive hint:** Iterators remember their current position and are usually one-shot.
5. **Tracing:** Trace `[n * 10 for n in range(6) if n % 2]` one input at a time.
   **Progressive hint:** Evaluate the filter before the output expression.
6. **Implementation:** Implement `batched(items, size)` yielding lists of at most `size`, including a final partial batch.
   **Progressive hint:** Accumulate, yield when full, then handle leftovers after the loop.
7. **Debugging:** Explain and repair a loop that removes negative values from the same list it is iterating over.
   **Progressive hint:** Build a new list or iterate over a copy.
8. **Edge case and explanation:** Define whether an even-number generator 'up to N' includes N and test N values -1, 0, 1, 2, and 3.
   **Progressive hint:** Boundary examples turn ambiguous English into a contract.

Before opening the reference solution, write one sentence explaining
which contract or mental model each result confirms.


## Self-check

- Why can iterating over the same generator twice produce different results?
- When is a comprehension less readable than an ordinary loop?
- What is the memory difference between a list and generator expression?
- Why is modifying a list while iterating over it risky?

Expected behavior: the transformed list matches the original loop, the
generator is lazy, and frequency counts include every occurrence.

## Common pitfalls and diagnosis

- **A generator prints as `<generator object ...>`:** consume it with `next`,
  iteration, or `list(...)` only when materializing is safe.
- **The second pass is empty:** the iterator was exhausted; create a fresh
  generator.
- **An off-by-one boundary:** inspect the stop value passed to `range`.
- **A dense nested comprehension is hard to debug:** expand it into named loops
  and verify each stage.
- **Frequency counting is unexpectedly slow:** avoid calling `items.count(x)`
  for every item in a large list.

## Continue

- [Open the learner notebook](../notebooks/day04_loops_comprehensions_generators.ipynb)
- [Check the separate solution](../solutions/day04_loops_comprehensions_generators/day04_solutions.md)
- [Next: Day 5 — Functions and type hints](day05_functions_type_hints.md)
