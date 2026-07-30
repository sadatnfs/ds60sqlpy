# Day 13 — Functional Tools: `itertools` and `functools`

**Level:** Beginner

The standard library can transform iterables lazily and specialize or cache
functions. Use these tools when they make intent clearer than hand-written
state.

## Learning objectives

By the end of this lesson, you can:

- compose lazy iterator operations with `itertools`;
- explain why `itertools.groupby` groups adjacent values;
- cache a pure function with `functools.lru_cache`;
- specialize parameters with `functools.partial`;
- choose between a comprehension, `map`/`filter`, and vectorized data tools.

## Prerequisites

Complete Day 12 (`python-12`), plus generators from Day 4 (`python-04`).

## Vocabulary and mental model

- **Higher-order function:** accepts or returns another function.
- **Lazy:** produces values only as the consumer requests them.
- **Pure function:** result depends only on inputs and has no observable side
  effects; safe candidate for caching.
- **Memoization:** reuse a stored result for repeated arguments.
- **Partial application:** fix some arguments now to create a specialized
  callable.
- **Adjacent grouping:** runs of equal keys, not global aggregation.

## Worked example

```python
from functools import lru_cache
from itertools import chain, islice


@lru_cache(maxsize=128)
def expensive_label(code: int) -> str:
    return f"item-{code:04d}"


pages = [[1, 2], [3, 4], [5]]
first_three = list(islice(chain.from_iterable(pages), 3))
labels = [expensive_label(code) for code in first_three]
```

`chain.from_iterable` flattens lazily. The bounded cache is useful only because
the function is deterministic for a given integer.

## Exercises and progressive hints

1. Group `(key, value)` pairs by key with `itertools.groupby`. **Hint:** inspect
   what happens to keys that reappear later; arrange the input by the same key
   before grouping.
2. Use `partial` to create a specialized function from a more general one.
   **Hint:** identify the argument that stays constant across many calls and
   bind only that argument.

### Additional mastery practice

Use functional tools when they make data flow clearer. Preserve laziness intentionally and keep side effects at explicit boundaries.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

3. **Prediction:** Predict what remains after calling `next` on a `map` object and then converting it to a list.
   **Progressive hint:** `map` is a lazy one-shot iterator in Python 3.
4. **Tracing:** Trace `sorted(records, key=lambda row: (row['team'], -row['score']))` and explain the tuple key.
   **Progressive hint:** Tuple components are compared left to right.
5. **Implementation:** Implement `compose(*functions)` so `compose(f, g)(x)` applies `g` then `f`, and handle no functions as identity.
   **Progressive hint:** Apply the reversed function sequence to the current value.
6. **Debugging:** Repair lambdas created in a loop that all use the final loop value.
   **Progressive hint:** Bind the current value as a default argument or use a factory function.
7. **Edge case and explanation:** Refactor a pipeline that prints inside `map` into pure transforms plus one explicit presentation step.
   **Progressive hint:** Pure stages are easier to test and reuse.

Before opening the reference solution, write one sentence explaining
which contract or mental model each result confirms.


## Self-check

- Why does `groupby` usually require sorted input?
- Why should a function that reads the current time not be cached blindly?
- What is lazy about `map` and `filter` in Python 3?
- When is a list comprehension clearer than a chain of functional calls?

Expected behavior: every key's values are grouped as intended, and the partial
callable behaves like the general function with one argument pre-filled.

## Common pitfalls and diagnosis

- **One key appears in multiple groups:** the input was not ordered by the
  grouping key.
- **A grouped iterator is empty later:** consume each group while iterating the
  outer `groupby`; they share the source iterator.
- **A cache returns stale external data:** cache only pure computations or add
  an explicit invalidation policy.
- **A lambda is difficult to interpret:** replace non-trivial logic with a named
  function.
- **Python-level transforms are slow on arrays:** prefer NumPy/pandas
  vectorization after measuring the relevant workload.

## Continue

- [Open the learner notebook](../notebooks/day13_functional_tools.ipynb)
- [Check the separate solution](../solutions/day13_functional_tools/day13_solutions.md)
- [Next: Day 14 — Ruff, mypy, and pytest](day14_code_quality_tooling.md)
