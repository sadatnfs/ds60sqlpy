# Day 06 — Solutions: Lists, Tuples, Sets, Dicts

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

These worked answers demonstrate **choosing lists, tuples, sets, and dictionaries by semantics**. Predict each named
result before comparing your attempt with its matching assertions.

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

### Vocabulary used in the worked answers

- **sequence:** an ordered collection addressable by position.
- **mapping:** a collection that associates keys with values.
- **mutable:** able to change in place after creation.
- **hashable:** having a stable hash and equality behavior while stored.
- **membership:** the question whether a value is present.
- **shallow copy:** a new outer container that shares referenced inner objects.

### How to compare an answer

For this lesson's **choosing lists, tuples, sets, and dictionaries by semantics** model, follow the exact values from each learner contract through its function or expression to the assertion that proves the expected behavior; then change one boundary input and make that assertion fail once before accepting the answer.
<!-- END BEGINNER SOLUTION REVIEW -->

## Exercises 1–2 — Worked answers

### Exercise 1 — worked answer

**Learner contract:** Implement `stable_unique(values)` for `['b', 'a', 'b', 'c', 'a']`. **Expected result:** `['b', 'a', 'c']`. **Constraints:** preserve the first occurrence, leave the input unchanged, use a set for membership and a list for output, and state that items must be hashable. **Verify:** test the example, an empty list, and a list with no duplicates.

**Reasoning:** Implement this exact contract as written: Implement `stable_unique(values)` for `['b', 'a', 'b', 'c', 'a']`. Expected result: `['b', 'a', 'c']`. Constraints: preserve the first occurrence, leave the input unchanged, use a set for membership and a list for output, and state that items must be hashable. Keep the prompt's named data and constraints visible in the code, then establish this specific result: test the example, an empty list, and a list with no duplicates. That connects the answer to choosing lists, tuples, sets, and dictionaries by semantics.

```python
from collections.abc import Hashable, Iterable
from typing import TypeVar

T = TypeVar("T", bound=Hashable)


def stable_unique(values: Iterable[T]) -> list[T]:
    seen: set[T] = set()
    result: list[T] = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


source = ["b", "a", "b", "c", "a"]
assert stable_unique(source) == ["b", "a", "c"]
assert source == ["b", "a", "b", "c", "a"]
assert stable_unique([]) == []
```

**Verification evidence:** test the example, an empty list, and a list with no duplicates.

### Exercise 2 — worked answer

**Learner contract:** Given `[('east', 4), ('west', 2), ('east', 3)]`, build three mappings: region to list of all values, region to set of unique values, and region to numeric total. **Expected totals:** `{'east': 7, 'west': 2}`. **Constraints:** make the missing-key initial value explicit and preserve encounter order in the list version. **Verify:** assert all three outputs.

**Reasoning:** Implement this exact contract as written: Given `[('east', 4), ('west', 2), ('east', 3)]`, build three mappings: region to list of all values, region to set of unique values, and region to numeric total. Expected totals: `{'east': 7, 'west': 2}`. Constraints: make the missing-key initial value explicit and preserve encounter order in the list version. Keep the prompt's named data and constraints visible in the code, then establish this specific result: assert all three outputs. That connects the answer to choosing lists, tuples, sets, and dictionaries by semantics.

```python
pairs = [("east", 4), ("west", 2), ("east", 3)]
all_values: dict[str, list[int]] = {}
unique_values: dict[str, set[int]] = {}
totals: dict[str, int] = {}
for key, value in pairs:
    all_values.setdefault(key, []).append(value)
    unique_values.setdefault(key, set()).add(value)
    totals[key] = totals.get(key, 0) + value

assert all_values == {"east": [4, 3], "west": [2]}
assert unique_values == {"east": {3, 4}, "west": {2}}
assert totals == {"east": 7, "west": 2}
```

**Verification evidence:** assert all three outputs.

## Exercises 3–7 — Expanded mastery answers

### Exercise 3 — answer contract

**Learner contract:** **Prediction:** Predict the length and membership behavior of `{3, 1, 3, 2}`. Why must display order not be treated as a sorting guarantee? **Progressive hint:** Sets enforce uniqueness and optimize membership, not presentation order. **Verify:** Assert the set has length `3` and contains `1`, `2`, and `3`; compare values as a set rather than asserting display iteration order.

**Reasoning:** Predict this named state change before running it: Prediction: Predict the length and membership behavior of `{3, 1, 3, 2}`. Why must display order not be treated as a sorting guarantee? Progressive hint: Sets enforce uniqueness and optimize membership, not presentation order. Then compare the prediction with this proof target: Assert the set has length `3` and contains `1`, `2`, and `3`; compare values as a set rather than asserting display iteration order. This makes choosing lists, tuples, sets, and dictionaries by semantics observable instead of relying on intuition.

**Evidence to locate in the grouped implementation:** Assert the set has length `3` and contains `1`, `2`, and `3`; compare values as a set rather than asserting display iteration order.

### Exercise 4 — answer contract

**Learner contract:** **Tracing:** Trace shallow copying for `original = [[1], [2]]; copied = original.copy(); copied[0].append(9)`. **Progressive hint:** The outer lists differ but still refer to the same inner lists. **Verify:** Assert `original is not copied` but `original[0] is copied[0]`, then confirm appending through the copy appears in both nested lists.

**Reasoning:** Trace the concrete values in this contract one step at a time: Tracing: Trace shallow copying for `original = [[1], [2]]; copied = original.copy(); copied[0].append(9)`. Progressive hint: The outer lists differ but still refer to the same inner lists. Record the named value, shape, label, or iterator position needed to establish: Assert `original is not copied` but `original[0] is copied[0]`, then confirm appending through the copy appears in both nested lists. The trace exposes choosing lists, tuples, sets, and dictionaries by semantics directly.

**Evidence to locate in the grouped implementation:** Assert `original is not copied` but `original[0] is copied[0]`, then confirm appending through the copy appears in both nested lists.

### Exercise 5 — answer contract

**Learner contract:** **Implementation:** Implement `invert_multimap(mapping)` so values become keys and each new key maps to a list of original keys in encounter order. **Progressive hint:** Use `setdefault` or `defaultdict(list)`. **Verify:** Assert exact output lists and encounter order for a mapping where two original keys share a value; also test an empty mapping.

**Reasoning:** Implement this exact contract as written: Implementation: Implement `invert_multimap(mapping)` so values become keys and each new key maps to a list of original keys in encounter order. Progressive hint: Use `setdefault` or `defaultdict(list)`. Keep the prompt's named data and constraints visible in the code, then establish this specific result: Assert exact output lists and encounter order for a mapping where two original keys share a value; also test an empty mapping. That connects the answer to choosing lists, tuples, sets, and dictionaries by semantics.

**Evidence to locate in the grouped implementation:** Assert exact output lists and encounter order for a mapping where two original keys share a value; also test an empty mapping.

### Exercise 6 — answer contract

**Learner contract:** **Debugging:** Repair code that attempts to use a list as a dictionary key. Explain hashability and choose a tuple when the sequence is an identity. **Progressive hint:** Dictionary keys must have a stable hash while stored. **Verify:** Show the list-key version raises `TypeError`, then assert the tuple-key replacement retrieves the intended value and remains unmodified.

**Reasoning:** Reproduce the exact failure described here before changing code: Debugging: Repair code that attempts to use a list as a dictionary key. Explain hashability and choose a tuple when the sequence is an identity. Progressive hint: Dictionary keys must have a stable hash while stored. Preserve that failing case, repair the violated rule, and rerun the evidence named here: Show the list-key version raises `TypeError`, then assert the tuple-key replacement retrieves the intended value and remains unmodified. The diagnosis depends on choosing lists, tuples, sets, and dictionaries by semantics.

**Evidence to locate in the grouped implementation:** Show the list-key version raises `TypeError`, then assert the tuple-key replacement retrieves the intended value and remains unmodified.

### Exercise 7 — answer contract

**Learner contract:** **Edge case and explanation:** Extend stable de-duplication to records using a `key` function, then test repeated dictionaries whose IDs match but other fields differ. **Progressive hint:** Store hashable derived keys while returning original records. **Verify:** Use repeated record dictionaries with the same ID; assert the first complete record is returned once, input order is preserved, and the input remains unchanged.

**Reasoning:** Make this boundary unambiguous in code: Edge case and explanation: Extend stable de-duplication to records using a `key` function, then test repeated dictionaries whose IDs match but other fields differ. Progressive hint: Store hashable derived keys while returning original records. Values below, at, and above the named boundary must produce the evidence Use repeated record dictionaries with the same ID; assert the first complete record is returned once, input order is preserved, and the input remains unchanged. Those cases show how choosing lists, tuples, sets, and dictionaries by semantics behaves at its edge.

**Evidence to locate in the grouped implementation:** Use repeated record dictionaries with the same ID; assert the first complete record is returned once, input order is preserved, and the input remains unchanged.

## Expanded mastery lab solutions

Choose structures by semantics—ordering, uniqueness, lookup, and mutability—not by habit. State what duplicates and missing keys mean.

### Shared implementation for Exercises 3–4 — Set and copy semantics

`{3, 1, 3, 2}` contains three unique integers. Membership is the contract;
iteration order is not a portable sorting rule. A shallow list copy duplicates
only the outer container, so both versions still share the nested lists.

```python
original = [[1], [2]]
copied = original.copy()
copied[0].append(9)
assert original == [[1, 9], [2]]
assert copied is not original and copied[0] is original[0]
```

### Shared implementation for Exercises 5–7 — Multimaps, hashable identities, and keyed de-duplication

```python
from collections import defaultdict
from collections.abc import Callable, Hashable, Iterable, Mapping
from typing import TypeVar

K = TypeVar("K", bound=Hashable)
V = TypeVar("V", bound=Hashable)
T = TypeVar("T")


def invert_multimap(mapping: Mapping[K, V]) -> dict[V, list[K]]:
    """Group original keys by value, preserving mapping encounter order."""

    inverted: defaultdict[V, list[K]] = defaultdict(list)
    for key, value in mapping.items():
        inverted[value].append(key)
    return dict(inverted)


coordinates = [40, -74]
location_by_point = {tuple(coordinates): "station"}  # Tuple is hashable.
assert location_by_point[(40, -74)] == "station"


def dedupe_by(items: Iterable[T], key: Callable[[T], Hashable]) -> list[T]:
    """Keep the first item for each derived hashable key."""

    seen: set[Hashable] = set()
    result: list[T] = []
    for item in items:
        identity = key(item)
        if identity not in seen:
            seen.add(identity)
            result.append(item)
    return result


records = [{"id": 1, "name": "first"}, {"id": 1, "name": "later"}, {"id": 2}]
assert dedupe_by(records, key=lambda row: row["id"]) == [records[0], records[2]]
assert invert_multimap({"a": 1, "b": 2, "c": 1}) == {1: ["a", "c"], 2: ["b"]}
```
