# Day 13 Solutions: Functional Tools: itertools and functools

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

These worked answers demonstrate **functions as values and composable iterable tools**. Predict each named
result before comparing your attempt with its matching assertions.

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

### How to compare an answer

For this lesson's **functions as values and composable iterable tools** model, follow the exact values from each learner contract through its function or expression to the assertion that proves the expected behavior; then change one boundary input and make that assertion fail once before accepting the answer.
<!-- END BEGINNER SOLUTION REVIEW -->

## Exercises 1-2: Worked answers

### Exercise 1: worked answer

**Learner contract:** Use `itertools.groupby` to group records that are already sorted by a category key. **Inputs:** include the same category in separated positions before sorting. **Expected behavior:** after explicit sorting, each category appears once with all of its records. **Constraint:** explain why `groupby` groups adjacent runs rather than globally collecting unsorted data. **Verify:** Show the unsorted input produces separated runs, then assert the sorted grouping has one entry per category and preserves every record.

**Reasoning:** `itertools.groupby` starts a new group every time the key changes, so it gathers equal keys only when they are next to each other. On the unsorted pairs it would produce groups `b`, `a`, and `b` again, and a dictionary built from those groups would keep only the last `b` group. Sorting with the same key function first makes equal keys adjacent, which is why the sort is part of the contract. Each group's `rows` is a one-shot iterator tied to the `groupby` object, so it must be consumed, here into a list, before moving to the next group.

```python
from itertools import groupby
from operator import itemgetter

pairs = [("b", 2), ("a", 1), ("b", 3)]
ordered = sorted(pairs, key=itemgetter(0))
grouped = {key: [value for _, value in rows] for key, rows in groupby(ordered, key=itemgetter(0))}
assert grouped == {"a": [1], "b": [2, 3]}
```

Sorting is part of the contract because `groupby` collects adjacent
runs rather than searching the entire iterable.

### Exercise 2: worked answer

**Learner contract:** Use `functools.reduce` to compute a product for `[2, 3, 4]`, giving an explicit identity so empty input returns `1`. **Then:** implement the same result with a named loop and compare readability. **Verify:** both return `24` and both define empty behavior; state why `sum`/`math.prod` is preferable in ordinary production code.

**Reasoning:** `reduce(mul, values, 1)` folds the list from the left, `((1 * 2) * 3) * 4`, giving 24. The third argument is the identity value: it is the starting point and also the answer for an empty list; without it, `reduce(mul, [])` raises `TypeError`. The loop version shows the same two decisions as `result = 1` and the update line. In ordinary code, `math.prod(values)` states the intent directly and also returns 1 for an empty list, so `reduce` is best kept for combinations that no built-in already names.

```python
from functools import reduce
from operator import mul


def product(values: list[int]) -> int:
    return reduce(mul, values, 1)


def loop_product(values: list[int]) -> int:
    result = 1
    for value in values:
        result *= value
    return result


assert product([2, 3, 4]) == loop_product([2, 3, 4]) == 24
assert product([]) == loop_product([]) == 1
```

`math.prod(values)` is the clearest production alternative; the
explicit reduction here makes identity behavior visible.

## Exercises 3-7: Expanded mastery answers

### Exercise 3: answer contract

**Learner contract:** **Prediction:** Predict what remains after calling `next` on a `map` object and then converting it to a list. **Progressive hint:** `map` is a lazy one-shot iterator in Python 3. **Verify:** Assert the first mapped value and exact remaining list, then confirm another pass is empty because the map iterator is exhausted.

**Reasoning:** In Python 3, `map` returns a lazy iterator that computes each value only when asked and remembers its position. `next(doubled)` produces 2 for the first input, so `list(doubled)` continues with the remaining inputs and returns `[4, 6]`, and a further `list(doubled)` returns `[]`. The common surprise is code that calls `list(m)` once to inspect the values and then loops over `m` again, finding nothing. The shared implementation for Exercises 3-4 asserts the first value and the remainder; convert to a list once when you need the values more than once.

### Exercise 4: answer contract

**Learner contract:** **Tracing:** Trace `sorted(records, key=lambda row: (row['team'], -row['score']))` and explain the tuple key. **Progressive hint:** Tuple components are compared left to right. **Verify:** Compute each tuple key beside its record and assert final order groups team ascending and score descending within team.

**Reasoning:** Tuples compare element by element from the left, so the key `(row["team"], -row["score"])` sorts by team first and uses the score only to break ties within a team. Negating the score makes the scores descend while the teams still ascend: the two `A` rows have keys `("A", -9)` and `("A", -7)`, so 9 comes before 7, and `("B", -8)` comes last. The shared implementation for Exercises 3-4 asserts the scores `[9, 7, 8]`. Negation works only for numbers; for descending text, sort twice, relying on the stability of Python's sort.

### Exercise 5: answer contract

**Learner contract:** **Implementation:** Implement `compose(*functions)` so `compose(f, g)(x)` applies `g` then `f`, and handle no functions as identity. **Progressive hint:** Apply the reversed function sequence to the current value. **Verify:** Assert composition order with noncommutative functions and assert `compose()(value)` returns the original value unchanged.

**Reasoning:** Composition applies functions right to left, as in mathematical notation: `compose(f, g)(x)` is `f(g(x))`, so the implementation walks the function list in reverse. `str.upper` and `str.strip` cannot reveal a wrong order, because both orders give `"DATA"`; a non-commutative pair can, so the shared implementation for Exercises 5-7 asserts that `compose(add_one, double)(3)` is 7 while the reverse order gives 8. With no functions the loop does nothing and the input comes back unchanged, which makes `compose()` the identity, a useful neutral element when pipelines are built dynamically.

### Exercise 6: answer contract

**Learner contract:** **Debugging:** Repair lambdas created in a loop that all use the final loop value. **Progressive hint:** Bind the current value as a default argument or use a factory function. **Verify:** Call every produced function and show the faulty results share the final loop value; assert the factory/default-binding repair preserves each intended value.

**Reasoning:** Each lambda looks up `factor` when it is called, not when it is created, and by then the loop has finished with `factor` equal to 2; that is why every function in the faulty list returns 20 for the input 10. Binding the current value as a default argument, `lambda value, factor=factor: ...`, evaluates it at creation time, so the repaired functions return 0, 10, and 20. A small factory function such as `def make(factor): return lambda value: value * factor` achieves the same with a clearer signature. The shared implementation for Exercises 5-7 asserts both the faulty and the repaired results.

### Exercise 7: answer contract

**Learner contract:** **Edge case and explanation:** Refactor a pipeline that prints inside `map` into pure transforms plus one explicit presentation step. **Progressive hint:** Pure stages are easier to test and reuse. **Verify:** Assert transformed values are identical before/after refactoring and capture presentation output only in the final explicit step.

**Reasoning:** Printing inside `map` hides a side effect in what looks like a pure transformation: the output appears only when the iterator is consumed, possibly never, and the transformation cannot be tested without capturing printed text. Splitting the work into a pure step that normalizes each value and one explicit presentation step that joins and prints makes the transformed values directly comparable before and after the refactor. In the shared implementation for Exercises 5-7, `normalized` is a plain list that can be asserted, and only `rendered` is meant for display.

## Expanded mastery lab solutions

Use functional tools when they make data flow clearer. Preserve laziness intentionally and keep side effects at explicit boundaries.

### Shared implementation for Exercises 3-4: Lazy iterators and tuple ordering

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

### Shared implementation for Exercises 5-7: Composition, binding, and pure stages

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


def add_one(value: int) -> int:
    return value + 1


def double(value: int) -> int:
    return value * 2


assert compose(add_one, double)(3) == 7  # double first, then add one
assert compose(double, add_one)(3) == 8

# The faulty version looks factor up later, after the loop has finished.
faulty = [lambda value: value * factor for factor in range(3)]
assert [function(10) for function in faulty] == [20, 20, 20]

# Bind each loop value now, rather than looking it up later.
multipliers = [lambda value, factor=factor: value * factor for factor in range(3)]
assert [function(10) for function in multipliers] == [0, 10, 20]

normalize = lambda text: text.strip().casefold()
normalized = list(map(normalize, [" A ", " B "]))  # Pure transformation.
rendered = ", ".join(normalized)  # Presentation boundary.
assert rendered == "a, b"
```
