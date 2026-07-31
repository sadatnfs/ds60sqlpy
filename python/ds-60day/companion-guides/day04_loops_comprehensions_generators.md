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

2. Read `python/ds-60day/companion-guides/day04_loops_comprehensions_generators.md`, then open `python/ds-60day/notebooks/day04_loops_comprehensions_generators.ipynb` from the repository
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

**Lesson outcome:** use day 4 — loops, comprehensions, and generators to practice iteration, eager collection building, and lazy generators
and explain the evidence produced by your code.
<!-- END HOW TO RUN -->

<!-- BEGIN BEGINNER DEEP DIVE -->
## Beginner deep dive — build the idea before the syntax

### Start with one mental picture

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

### Vocabulary in plain language

- **iterable:** an object able to provide an iterator, such as a list or range.
- **iterator:** a stateful one-way cursor that provides the next value.
- **iteration:** one pass through successive values.
- **comprehension:** compact syntax that eagerly constructs a collection.
- **generator:** an iterator that computes values lazily.
- **exhaustion:** the state after an iterator has no more values.

### Syntax anatomy

In `[n * n for n in numbers if n > 0]`, `n * n` is the output
expression, `for n in numbers` names the source and current item, and
`if n > 0` is the filter. The filter runs before the output expression.
In a generator function, each `yield value` pauses the function while
preserving local state; the next request resumes immediately after that
`yield`.

### Worked example 1 — Translate an append loop one clause at a time

Use the loop as a readable specification before compressing it. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
temperatures = [-4, 0, 7, 12]
warm_fahrenheit = []
for celsius in temperatures:
    if celsius > 0:
        warm_fahrenheit.append(celsius * 9 / 5 + 32)

compact = [c * 9 / 5 + 32 for c in temperatures if c > 0]
(warm_fahrenheit, compact, warm_fahrenheit == compact)
```

**Expected observation**

```text
`([44.6, 53.6], [44.6, 53.6], True)`. The two forms implement the same filter and transformation.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### Worked example 2 — Observe a generator's saved position

Consumption advances the iterator instead of restarting it. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
squares = (number**2 for number in range(4))
first = next(squares)
rest = list(squares)
after_exhaustion = list(squares)
(first, rest, after_exhaustion)
```

**Expected observation**

```text
`(0, [1, 4, 9], [])`. Materializing `rest` consumes everything that remained.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### A debugging routine for this topic

When the output differs from your prediction, use this order:

1. Print or record the exact values produced by `range(start, stop, step)` when a boundary is wrong.
2. Expand a confusing comprehension back into loops and name its filter and transformation.
3. If a second pass is empty, check whether you retained an iterator instead of an iterable.
4. Never remove items from the same list being iterated; build a result or iterate over a copy.

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

**Useful alternative:** Choose a normal loop for side effects or several decisions, a comprehension for one clear collection transformation, and a generator for streaming.

**Boundary to remember:** Empty inputs, a non-positive batch size, a final partial batch, and inclusive versus exclusive endpoints must be explicit.
<!-- END BEGINNER DEEP DIVE -->

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

Each item is a complete mini-contract. Before writing code, copy its input,
expected behavior, constraints, and verification into your work cell. A
result is not complete merely because it “looks right”; run the stated
assertion or inspection and explain what it proves.

1. Start with `numbers = [-3, -1, 0, 2, 5]`. Write an ordinary loop that appends the **squares of strictly positive values** to `positive_squares`, then write an equivalent list comprehension named `compact_squares`.
   **Expected result:** both are `[4, 25]`. **Constraints:** do not mutate `numbers`, and keep the filter (`> 0`) distinct from the transformation (`value ** 2`).
   **Verify:** assert the two results are equal and the input is unchanged.

2. Implement `evens_through(limit)` as a generator that yields even integers from `0` through `limit` **inclusive**. **Inputs to verify:** `-1`, `0`, `1`, `2`, and `7`. **Expected results:** `[]`, `[0]`, `[0]`, `[0, 2]`, and `[0, 2, 4, 6]`. **Constraints:** use `yield`, return no stored list, and document the inclusive endpoint.
   **Verify:** Assert the exact five expected lists for limits `-1`, `0`, `1`, `2`, and `7`; also confirm `inspect.isgenerator(evens_through(2))` is true.

3. For `items = ['red', 'blue', 'red', 'green', 'blue', 'red']`, build a frequency mapping whose expected value is `{'red': 3, 'blue': 2, 'green': 1}`. **First:** implement an explicit one-pass loop with `dict.get`. **Then:** compare it with `collections.Counter`. **Constraint:** do not repeatedly call `items.count` in production code.
   **Verify:** assert both mappings agree and explain their time-cost difference.

### Additional mastery practice

Trace iteration boundaries and laziness. Prefer a clear loop when a comprehension would hide state changes or several decisions.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

4. **Prediction:** Create a generator expression, consume one item with `next`, then convert the rest to a list. Predict what remains and why.
   **Progressive hint:** Iterators remember their current position and are usually one-shot.
   **Verify:** Assert the first consumed square is `0`, the remaining list is `[1, 4, 9]`, and a third pass is empty; explain the saved iterator position.
5. **Tracing:** Trace `[n * 10 for n in range(6) if n % 2]` one input at a time.
   **Progressive hint:** Evaluate the filter before the output expression.
   **Verify:** Build a six-row trace for inputs `0..5` containing filter result and optional output; confirm the final list is `[10, 30, 50]`.
6. **Implementation:** Implement `batched(items, size)` yielding lists of at most `size`, including a final partial batch.
   **Progressive hint:** Accumulate, yield when full, then handle leftovers after the loop.
   **Verify:** Assert `list(batched(range(5), 2)) == [[0, 1], [2, 3], [4]]`, empty input yields no batches, and size `0` raises.
7. **Debugging:** Explain and repair a loop that removes negative values from the same list it is iterating over.
   **Progressive hint:** Build a new list or iterate over a copy.
   **Verify:** Keep the original failing list as evidence, then assert the repaired result removes every negative without skipping adjacent negatives or mutating the source unexpectedly.
8. **Edge case and explanation:** Define whether an even-number generator 'up to N' includes N and test N values -1, 0, 1, 2, and 3.
   **Progressive hint:** Boundary examples turn ambiguous English into a contract.
   **Verify:** Assert exact output for `N` values `-1, 0, 1, 2, 3`; identify which tests prove the endpoint is inclusive and how negative input behaves.

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

## Ask Codex about this lesson

Codex coaching is optional; the guide and notebook above contain the full
lesson. If you want a patient tutor, copy this prompt from the repository
root:

```text
Use $guide-ds60sqlpy-learning to tutor me through `python-04`
(Day 4 — Loops, Comprehensions, and Generators). Direct catalog prerequisites: `python-03`.
I have completed the direct prerequisites: `python-03`. Emphasize iteration, eager collection building, and lazy generators.
Read `python/ds-60day/companion-guides/day04_loops_comprehensions_generators.md` and use the learner notebook
`python/ds-60day/notebooks/day04_loops_comprehensions_generators.ipynb`. Do not open or quote anything under `solutions/` unless
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
