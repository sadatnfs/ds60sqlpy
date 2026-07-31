# Day 6 — Lists, Tuples, Sets, and Dictionaries

**Level:** Beginner

Choose a data structure from the operations you need, not from habit.

## Learning objectives

By the end of this lesson, you can:

- explain ordering, mutability, uniqueness, and lookup behavior;
- select a list, tuple, set, or dictionary for a stated requirement;
- count, group, and de-duplicate values without losing required information;
- avoid unintended aliasing when working with mutable collections.

## Prerequisites

Complete Day 5 (`python-05`): functions, collection annotations, and contracts.





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

2. Read `python/ds-60day/companion-guides/day06_data_structures.md`, then open `python/ds-60day/notebooks/day06_data_structures.ipynb` from the repository
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

**Lesson outcome:** use day 6 — lists, tuples, sets, and dictionaries to practice choosing lists, tuples, sets, and dictionaries by semantics
and explain the evidence produced by your code.
<!-- END HOW TO RUN -->

<!-- BEGIN BEGINNER DEEP DIVE -->
## Beginner deep dive — build the idea before the syntax

### Start with one mental picture

Python's core collections answer different questions. A list keeps
ordered, possibly repeated values and can change. A tuple is an ordered
fixed record-like sequence. A set represents unique hashable members
and makes membership tests fast. A dictionary maps unique hashable keys
to values.

“Mutable” means an object can change in place; “hashable” means it has a
stable hash suitable for a set member or dictionary key. Copying a
collection is also about reference depth: a shallow copy creates a new
outer container but still points to the same nested objects. Choose a
structure from the meaning of order, duplicates, lookup, and mutation,
not simply from familiar syntax.

### Vocabulary in plain language

- **sequence:** an ordered collection addressable by position.
- **mapping:** a collection that associates keys with values.
- **mutable:** able to change in place after creation.
- **hashable:** having a stable hash and equality behavior while stored.
- **membership:** the question whether a value is present.
- **shallow copy:** a new outer container that shares referenced inner objects.

### Syntax anatomy

`counts[key] = counts.get(key, 0) + amount` first asks the dictionary
for `key`, substitutes `0` only when it is absent, adds `amount`, and
writes the new total back. `value in seen` is a membership expression;
for a set or dictionary it is normally much cheaper than scanning a
long list.

### Worked example 1 — Preserve order while removing repeats

Use one structure for fast membership and another for ordered output. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
values = ["a", "b", "a", "c", "b"]
seen = set()
unique_in_order = []
for value in values:
    if value not in seen:
        seen.add(value)
        unique_in_order.append(value)
unique_in_order
```

**Expected observation**

```text
`['a', 'b', 'c']`. Converting straight to a set would represent uniqueness but would not express first-seen order.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### Worked example 2 — Aggregate pairs into a dictionary

Make the missing-key starting value explicit. Before running it, predict the final displayed value and
identify which line creates each intermediate object.

```python
purchases = [("tea", 2), ("coffee", 1), ("tea", 3)]
totals = {}
for product, quantity in purchases:
    totals[product] = totals.get(product, 0) + quantity
totals
```

**Expected observation**

```text
`{'tea': 5, 'coffee': 1}`. Tuple unpacking gives names to the two fields in each pair.
```

Do not memorize the surface syntax. Point from the input, through
each transformation or decision, to the final evidence.

### A debugging routine for this topic

When the output differs from your prediction, use this order:

1. When an unhashable-type error appears, inspect the set member or dictionary key and ask whether its identity can be a tuple.
2. When nested data changes through a copy, determine whether the copy was shallow.
3. Do not depend on a set's display order; sort only when presentation needs a deterministic order.
4. Use `.get`, `setdefault`, `defaultdict`, or `Counter` according to the missing-key behavior you want.

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

**Useful alternative:** `dict.fromkeys(values)` is a compact stable de-duplication technique for hashable values, while an explicit loop adapts to a derived key.

**Boundary to remember:** Nested mutable values, unhashable records, missing keys, empty inputs, and repeated records with the same identity expose collection-policy choices.
<!-- END BEGINNER DEEP DIVE -->

## Vocabulary and mental model

- **List:** mutable, ordered sequence that permits duplicates.
- **Tuple:** immutable, ordered sequence; useful for fixed records or keys.
- **Set:** mutable collection of unique, hashable values; fast membership.
- **Dictionary:** mapping from unique, hashable keys to values.
- **Hashable:** stable enough to be used as a set member or dictionary key.
- **Aliasing:** two names refer to the same mutable object.

Think in operations: preserve order, enforce uniqueness, look up by key, or
represent a fixed record. A set removes duplicates but does not represent the
original sequence order as a contract.

## Worked example

```python
pipeline = ["extract", "clean", "load"]
coordinate = (37.7749, -122.4194)
allowed_roles = {"reader", "editor"}
user_by_id = {7: "Ada", 12: "Grace"}

pipeline.append("validate")
can_edit = "editor" in allowed_roles
user_name = user_by_id[7]
```

The structures express different guarantees: ordered mutable stages, a fixed
coordinate pair, unique role membership, and keyed user lookup.

## Exercises and progressive hints

Each item is a complete mini-contract. Before writing code, copy its input,
expected behavior, constraints, and verification into your work cell. A
result is not complete merely because it “looks right”; run the stated
assertion or inspection and explain what it proves.

1. Implement `stable_unique(values)` for `['b', 'a', 'b', 'c', 'a']`.
   **Expected result:** `['b', 'a', 'c']`. **Constraints:** preserve the first occurrence, leave the input unchanged, use a set for membership and a list for output, and state that items must be hashable.
   **Verify:** test the example, an empty list, and a list with no duplicates.

2. Given `[('east', 4), ('west', 2), ('east', 3)]`, build three mappings: region to list of all values, region to set of unique values, and region to numeric total. **Expected totals:** `{'east': 7, 'west': 2}`. **Constraints:** make the missing-key initial value explicit and preserve encounter order in the list version.
   **Verify:** assert all three outputs.

### Additional mastery practice

Choose structures by semantics—ordering, uniqueness, lookup, and mutability—not by habit. State what duplicates and missing keys mean.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

3. **Prediction:** Predict the length and membership behavior of `{3, 1, 3, 2}`. Why must display order not be treated as a sorting guarantee?
   **Progressive hint:** Sets enforce uniqueness and optimize membership, not presentation order.
   **Verify:** Assert the set has length `3` and contains `1`, `2`, and `3`; compare values as a set rather than asserting display iteration order.
4. **Tracing:** Trace shallow copying for `original = [[1], [2]]; copied = original.copy(); copied[0].append(9)`.
   **Progressive hint:** The outer lists differ but still refer to the same inner lists.
   **Verify:** Assert `original is not copied` but `original[0] is copied[0]`, then confirm appending through the copy appears in both nested lists.
5. **Implementation:** Implement `invert_multimap(mapping)` so values become keys and each new key maps to a list of original keys in encounter order.
   **Progressive hint:** Use `setdefault` or `defaultdict(list)`.
   **Verify:** Assert exact output lists and encounter order for a mapping where two original keys share a value; also test an empty mapping.
6. **Debugging:** Repair code that attempts to use a list as a dictionary key. Explain hashability and choose a tuple when the sequence is an identity.
   **Progressive hint:** Dictionary keys must have a stable hash while stored.
   **Verify:** Show the list-key version raises `TypeError`, then assert the tuple-key replacement retrieves the intended value and remains unmodified.
7. **Edge case and explanation:** Extend stable de-duplication to records using a `key` function, then test repeated dictionaries whose IDs match but other fields differ.
   **Progressive hint:** Store hashable derived keys while returning original records.
   **Verify:** Use repeated record dictionaries with the same ID; assert the first complete record is returned once, input order is preserved, and the input remains unchanged.

Before opening the reference solution, write one sentence explaining
which contract or mental model each result confirms.

## Self-check

- Why is `item in a_set` usually preferable to `item in a_list` for repeated
  membership checks?
- Why can a tuple contain a list but then fail as a dictionary key?
- What is the difference between `copy = original` and
  `copy = original.copy()`?
- Which required guarantee would make a set the wrong output type?

Expected behavior: stable de-duplication retains original order, and each
aggregation uses an appropriate empty starting value.

## Common pitfalls and diagnosis

- **Output order changes after `set(values)`:** a set is not the ordered result
  you need; retain a separate list.
- **`KeyError`:** inspect whether the key should be required or initialized
  with `get`, `setdefault`, or `defaultdict`.
- **`TypeError: unhashable type`:** a mutable list or dictionary was used where
  a stable key is required.
- **Changing one nested list changes another:** print object identities; a
  shallow copy still shares nested objects.
- **Removing items while iterating skips values:** build a new collection or
  iterate over a copy.

## Continue

- [Open the learner notebook](../notebooks/day06_data_structures.ipynb)
- [Check the separate solution](../solutions/day06_data_structures/day06_solutions.md)
- [Next: Day 7 — Strings, regex, and paths](day07_strings_regex_pathlib.md)

## Ask Codex about this lesson

Codex coaching is optional; the guide and notebook above contain the full
lesson. If you want a patient tutor, copy this prompt from the repository
root:

```text
Use $guide-ds60sqlpy-learning to tutor me through `python-06`
(Day 6 — Lists, Tuples, Sets, and Dictionaries). I am a complete beginner. Emphasize choosing lists, tuples, sets, and dictionaries by semantics.
Read `python/ds-60day/companion-guides/day06_data_structures.md` and use the learner notebook
`python/ds-60day/notebooks/day06_data_structures.ipynb`. Do not open or quote anything under `solutions/` unless
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
