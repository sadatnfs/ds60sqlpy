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

<!-- BEGIN HOW TO RUN -->
## How to run this lesson

Work from the repository root. The rendered HTML lesson is a readable
preview; execute the real notebook in VS Code or JupyterLab.

1. Confirm the course environment before changing it:

   ```powershell
   # Windows PowerShell
   $CoursePython = if (Test-Path .\.venv\Scripts\python.exe) {
       (Resolve-Path .\.venv\Scripts\python.exe).Path
   } else {
       (Resolve-Path .\.venv\python.exe).Path
   }
   & $CoursePython scripts\course.py doctor
   ```

   ```bash
   # macOS/Linux
   .venv/bin/python scripts/course.py doctor
   ```

2. Read `python/ds-60day/companion-guides/day13_functional_tools.md`, then open `python/ds-60day/notebooks/day13_functional_tools.ipynb` from the repository
   folder in VS Code or JupyterLab.
3. Select **Python (ds60sqlpy)**. Do not run `%pip` in the notebook. If
   an import is missing, use the doctor and the catalog dependency label
   to repair the shared environment.
4. Restart the kernel and run from the first cell downward. Before every
   example, write a prediction; after it runs, compare the actual value,
   type, shape, or side effect with the stated observation.
5. Attempt each numbered exercise in its own work cell. Use the explicit
   verification as part of the task. Keep `solutions/` closed until you
   have a tested attempt or deliberately ask for help.

**Lesson outcome:** use day 13 — functional tools: `itertools` and `functools` to practice functions as values and composable iterable tools
and explain the evidence produced by your code.
<!-- END HOW TO RUN -->

<!-- BEGIN BEGINNER DEEP DIVE -->
## Beginner deep dive — build the idea before the syntax

### Start with one mental picture

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

### Vocabulary in plain language

- **first-class function:** a function usable as an ordinary runtime value.
- **higher-order function:** a function that accepts or returns functions.
- **lambda:** a small anonymous single-expression function.
- **lazy iterator:** an iterator that computes values only when requested.
- **accumulator:** the progressively combined value in a fold/reduction.
- **cache:** stored results reused for repeated equivalent calls.

### Syntax anatomy

`map(normalize, names)` receives the function object `normalize`—without
parentheses—and an iterable. Iteration later calls it for each item.
`sorted(records, key=lambda row: row["score"])` calls the key function
once per row to derive comparison keys; the lambda returns one
expression.

### Worked example 1 — Pass a named function into a lazy transformation

Keep the operation testable on its own. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
def normalize_name(text: str) -> str:
    return " ".join(text.strip().title().split())

raw_names = ["  ada lovelace", "GRACE   HOPPER  "]
normalized_iter = map(normalize_name, raw_names)
list(normalized_iter)
```

**Expected observation**

```text
`['Ada Lovelace', 'Grace Hopper']`. `map` is lazy; `list` consumes it.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### Worked example 2 — Compose lazy filtering and slicing

Generate only as many values as the consumer requests. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
from itertools import islice

squares = (number**2 for number in range(100))
even_squares = filter(lambda value: value % 2 == 0, squares)
list(islice(even_squares, 5))
```

**Expected observation**

```text
`[0, 4, 16, 36, 64]`. `islice` stops after five accepted values rather than consuming all 100 squares.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### A debugging routine for this topic

When the output differs from your prediction, use this order:

1. If a function runs too early, check whether you passed `function` or called `function(...)`.
2. If output prints as a map/filter object, remember these are lazy iterators and consume only as needed.
3. Replace a multi-step lambda with a named function and tests.
4. Cache only functions whose result depends entirely on hashable arguments and stable external state.

### Practice ramp

Work through the numbered exercises in five modes rather than treating all
of them as blank-code prompts:

1. **Prediction:** state the value, type, shape, rows, or side effect before
   execution.
2. **Guided modification:** change one part of a worked example and explain
   which part of the result must change.
3. **Independent application:** implement the same idea with a new input and
   an explicit contract.
4. **Debugging and edge cases:** reproduce a failure, identify the violated
   assumption, and prove the repair at a boundary.
5. **Retrieval:** close the guide and explain the core model from memory
   before moving on.

**Useful alternative:** Use a comprehension for a clear transform/filter, `itertools` for lazy composition, and an explicit loop when stateful branching matters.

**Boundary to remember:** One-shot iterators, infinite inputs, side effects inside transformations, unhashable cache arguments, and empty reductions require care.
<!-- END BEGINNER DEEP DIVE -->

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

Each item is a complete mini-contract. Before writing code, copy its input,
expected behavior, constraints, and verification into your work cell. A
result is not complete merely because it “looks right”; run the stated
assertion or inspection and explain what it proves.

1. Use `itertools.groupby` to group records that are already sorted by a category key. **Inputs:** include the same category in separated positions before sorting.
   **Expected behavior:** after explicit sorting, each category appears once with all of its records. **Constraint:** explain why `groupby` groups adjacent runs rather than globally collecting unsorted data.
   **Verify:** Show the unsorted input produces separated runs, then assert the sorted grouping has one entry per category and preserves every record.

2. Use `functools.reduce` to compute a product for `[2, 3, 4]`, giving an explicit identity so empty input returns `1`. **Then:** implement the same result with a named loop and compare readability.
   **Verify:** both return `24` and both define empty behavior; state why `sum`/`math.prod` is preferable in ordinary production code.

### Additional mastery practice

Use functional tools when they make data flow clearer. Preserve laziness intentionally and keep side effects at explicit boundaries.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

3. **Prediction:** Predict what remains after calling `next` on a `map` object and then converting it to a list.
   **Progressive hint:** `map` is a lazy one-shot iterator in Python 3.
   **Verify:** Assert the first mapped value and exact remaining list, then confirm another pass is empty because the map iterator is exhausted.
4. **Tracing:** Trace `sorted(records, key=lambda row: (row['team'], -row['score']))` and explain the tuple key.
   **Progressive hint:** Tuple components are compared left to right.
   **Verify:** Compute each tuple key beside its record and assert final order groups team ascending and score descending within team.
5. **Implementation:** Implement `compose(*functions)` so `compose(f, g)(x)` applies `g` then `f`, and handle no functions as identity.
   **Progressive hint:** Apply the reversed function sequence to the current value.
   **Verify:** Assert composition order with noncommutative functions and assert `compose()(value)` returns the original value unchanged.
6. **Debugging:** Repair lambdas created in a loop that all use the final loop value.
   **Progressive hint:** Bind the current value as a default argument or use a factory function.
   **Verify:** Call every produced function and show the faulty results share the final loop value; assert the factory/default-binding repair preserves each intended value.
7. **Edge case and explanation:** Refactor a pipeline that prints inside `map` into pure transforms plus one explicit presentation step.
   **Progressive hint:** Pure stages are easier to test and reuse.
   **Verify:** Assert transformed values are identical before/after refactoring and capture presentation output only in the final explicit step.

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

## Ask Codex about this lesson

Codex coaching is optional; the guide and notebook above contain the full
lesson. If you want a patient tutor, copy this prompt from the repository
root:

```text
Use $guide-ds60sqlpy-learning to tutor me through `python-13`
(Day 13 — Functional Tools: `itertools` and `functools`). Direct catalog prerequisites: `python-12`.
I have completed the direct prerequisites: `python-12`. Emphasize functions as values and composable iterable tools.
Read `python/ds-60day/companion-guides/day13_functional_tools.md` and use the learner notebook
`python/ds-60day/notebooks/day13_functional_tools.ipynb`. Do not open or quote anything under `solutions/` unless
I explicitly ask after making an honest attempt. Use these visible phases:
Explain, Predict, Attempt, Hint, Evidence, and Retrieval. First explain one
concept in plain language, then ask me to predict a small example and wait
for my attempt. Give only one progressive hint at a time. Help me run or
inspect my actual notebook evidence, adapt commands to my operating system,
and do not treat the rendered HTML preview as executable. Finish with 2-3
retrieval questions and one next step. Done when I can explain the mental
model without the guide, complete one independent exercise, and show the
prompt's verification evidence from my notebook.
```
