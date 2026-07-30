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

1. Implement stable de-duplication that preserves the first occurrence.
   **Hint:** keep one structure for membership checks and another for ordered
   output.
2. Aggregate key-value pairs by key. Try collecting values, unique values, and
   numeric totals. **Hint:** decide what a missing key should start with before
   processing the pair.

### Additional mastery practice

Choose structures by semantics—ordering, uniqueness, lookup, and mutability—not by habit. State what duplicates and missing keys mean.

Continue with five new exercises. Record each prediction before running
code; these extend rather than replace the original practice above.

3. **Prediction:** Predict the length and membership behavior of `{3, 1, 3, 2}`. Why must display order not be treated as a sorting guarantee?
   **Progressive hint:** Sets enforce uniqueness and optimize membership, not presentation order.
4. **Tracing:** Trace shallow copying for `original = [[1], [2]]; copied = original.copy(); copied[0].append(9)`.
   **Progressive hint:** The outer lists differ but still refer to the same inner lists.
5. **Implementation:** Implement `invert_multimap(mapping)` so values become keys and each new key maps to a list of original keys in encounter order.
   **Progressive hint:** Use `setdefault` or `defaultdict(list)`.
6. **Debugging:** Repair code that attempts to use a list as a dictionary key. Explain hashability and choose a tuple when the sequence is an identity.
   **Progressive hint:** Dictionary keys must have a stable hash while stored.
7. **Edge case and explanation:** Extend stable de-duplication to records using a `key` function, then test repeated dictionaries whose IDs match but other fields differ.
   **Progressive hint:** Store hashable derived keys while returning original records.

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
