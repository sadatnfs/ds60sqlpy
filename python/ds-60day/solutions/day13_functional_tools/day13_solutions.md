# Day 13 — Solutions: Functional Tools (itertools, functools, map/filter)

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

## Exercises 1–2 — Worked answers

### Exercise 1 — worked answer

**Learner contract:** Use `itertools.groupby` to group records that are already sorted by a category key. **Inputs:** include the same category in separated positions before sorting. **Expected behavior:** after explicit sorting, each category appears once with all of its records. **Constraint:** explain why `groupby` groups adjacent runs rather than globally collecting unsorted data. **Verify:** Show the unsorted input produces separated runs, then assert the sorted grouping has one entry per category and preserves every record.

**Reasoning:** Implement this exact contract as written: Use `itertools.groupby` to group records that are already sorted by a category key. Inputs: include the same category in separated positions before sorting. Expected behavior: after explicit sorting, each category appears once with all of its records. Constraint: explain why `groupby` groups adjacent runs rather than globally collecting unsorted data. Keep the prompt's named data and constraints visible in the code, then establish this specific result: Show the unsorted input produces separated runs, then assert the sorted grouping has one entry per category and preserves every record. That connects the answer to functions as values and composable iterable tools.

```python
from itertools import groupby
from operator import itemgetter

pairs = [("b", 2), ("a", 1), ("b", 3)]
ordered = sorted(pairs, key=itemgetter(0))
grouped = {
    key: [value for _, value in rows]
    for key, rows in groupby(ordered, key=itemgetter(0))
}
assert grouped == {"a": [1], "b": [2, 3]}
```

Sorting is part of the contract because `groupby` collects adjacent
runs rather than searching the entire iterable.

**Verification evidence:** Show the unsorted input produces separated runs, then assert the sorted grouping has one entry per category and preserves every record.

### Exercise 2 — worked answer

**Learner contract:** Use `functools.reduce` to compute a product for `[2, 3, 4]`, giving an explicit identity so empty input returns `1`. **Then:** implement the same result with a named loop and compare readability. **Verify:** both return `24` and both define empty behavior; state why `sum`/`math.prod` is preferable in ordinary production code.

**Reasoning:** Implement this exact contract as written: Use `functools.reduce` to compute a product for `[2, 3, 4]`, giving an explicit identity so empty input returns `1`. Then: implement the same result with a named loop and compare readability. Keep the prompt's named data and constraints visible in the code, then establish this specific result: both return `24` and both define empty behavior; state why `sum`/`math.prod` is preferable in ordinary production code. That connects the answer to functions as values and composable iterable tools.

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

**Verification evidence:** both return `24` and both define empty behavior; state why `sum`/`math.prod` is preferable in ordinary production code.

## Exercises 3–7 — Expanded mastery answers

### Exercise 3 — answer contract

**Learner contract:** **Prediction:** Predict what remains after calling `next` on a `map` object and then converting it to a list. **Progressive hint:** `map` is a lazy one-shot iterator in Python 3. **Verify:** Assert the first mapped value and exact remaining list, then confirm another pass is empty because the map iterator is exhausted.

**Reasoning:** Predict this named state change before running it: Prediction: Predict what remains after calling `next` on a `map` object and then converting it to a list. Progressive hint: `map` is a lazy one-shot iterator in Python 3. Then compare the prediction with this proof target: Assert the first mapped value and exact remaining list, then confirm another pass is empty because the map iterator is exhausted. This makes functions as values and composable iterable tools observable instead of relying on intuition.

**Evidence to locate in the grouped implementation:** Assert the first mapped value and exact remaining list, then confirm another pass is empty because the map iterator is exhausted.

### Exercise 4 — answer contract

**Learner contract:** **Tracing:** Trace `sorted(records, key=lambda row: (row['team'], -row['score']))` and explain the tuple key. **Progressive hint:** Tuple components are compared left to right. **Verify:** Compute each tuple key beside its record and assert final order groups team ascending and score descending within team.

**Reasoning:** Trace the concrete values in this contract one step at a time: Tracing: Trace `sorted(records, key=lambda row: (row['team'], -row['score']))` and explain the tuple key. Progressive hint: Tuple components are compared left to right. Record the named value, shape, label, or iterator position needed to establish: Compute each tuple key beside its record and assert final order groups team ascending and score descending within team. The trace exposes functions as values and composable iterable tools directly.

**Evidence to locate in the grouped implementation:** Compute each tuple key beside its record and assert final order groups team ascending and score descending within team.

### Exercise 5 — answer contract

**Learner contract:** **Implementation:** Implement `compose(*functions)` so `compose(f, g)(x)` applies `g` then `f`, and handle no functions as identity. **Progressive hint:** Apply the reversed function sequence to the current value. **Verify:** Assert composition order with noncommutative functions and assert `compose()(value)` returns the original value unchanged.

**Reasoning:** Implement this exact contract as written: Implementation: Implement `compose(*functions)` so `compose(f, g)(x)` applies `g` then `f`, and handle no functions as identity. Progressive hint: Apply the reversed function sequence to the current value. Keep the prompt's named data and constraints visible in the code, then establish this specific result: Assert composition order with noncommutative functions and assert `compose()(value)` returns the original value unchanged. That connects the answer to functions as values and composable iterable tools.

**Evidence to locate in the grouped implementation:** Assert composition order with noncommutative functions and assert `compose()(value)` returns the original value unchanged.

### Exercise 6 — answer contract

**Learner contract:** **Debugging:** Repair lambdas created in a loop that all use the final loop value. **Progressive hint:** Bind the current value as a default argument or use a factory function. **Verify:** Call every produced function and show the faulty results share the final loop value; assert the factory/default-binding repair preserves each intended value.

**Reasoning:** Reproduce the exact failure described here before changing code: Debugging: Repair lambdas created in a loop that all use the final loop value. Progressive hint: Bind the current value as a default argument or use a factory function. Preserve that failing case, repair the violated rule, and rerun the evidence named here: Call every produced function and show the faulty results share the final loop value; assert the factory/default-binding repair preserves each intended value. The diagnosis depends on functions as values and composable iterable tools.

**Evidence to locate in the grouped implementation:** Call every produced function and show the faulty results share the final loop value; assert the factory/default-binding repair preserves each intended value.

### Exercise 7 — answer contract

**Learner contract:** **Edge case and explanation:** Refactor a pipeline that prints inside `map` into pure transforms plus one explicit presentation step. **Progressive hint:** Pure stages are easier to test and reuse. **Verify:** Assert transformed values are identical before/after refactoring and capture presentation output only in the final explicit step.

**Reasoning:** Make this boundary unambiguous in code: Edge case and explanation: Refactor a pipeline that prints inside `map` into pure transforms plus one explicit presentation step. Progressive hint: Pure stages are easier to test and reuse. Values below, at, and above the named boundary must produce the evidence Assert transformed values are identical before/after refactoring and capture presentation output only in the final explicit step. Those cases show how functions as values and composable iterable tools behaves at its edge.

**Evidence to locate in the grouped implementation:** Assert transformed values are identical before/after refactoring and capture presentation output only in the final explicit step.

## Expanded mastery lab solutions

Use functional tools when they make data flow clearer. Preserve laziness intentionally and keep side effects at explicit boundaries.

### Shared implementation for Exercises 3–4 — Lazy iterators and tuple ordering

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

### Shared implementation for Exercises 5–7 — Composition, binding, and pure stages

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
