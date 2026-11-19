# Day 6 Solutions: Lists, Tuples, Sets, and Dictionaries

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

## Exercises 1-2: Worked answers

### Exercise 1: worked answer

**Learner contract:** Implement `stable_unique(values)` for `['b', 'a', 'b', 'c', 'a']`. **Expected result:** `['b', 'a', 'c']`. **Constraints:** preserve the first occurrence, leave the input unchanged, use a set for membership and a list for output, and state that items must be hashable. **Verify:** test the example, an empty list, and a list with no duplicates.

**Reasoning:** A set answers "have I seen this value?" quickly, while the list records output order, so each structure does the job it is good at. Checking membership in the result list instead would also work but rescans that list for every item, which becomes slow for long inputs. The input is only read, never modified, and an empty input naturally returns `[]`. Items must be hashable because they are stored in the set; a list of lists would raise `TypeError`, which the keyed version in the seventh exercise addresses.

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

### Exercise 2: worked answer

**Learner contract:** Given `[('east', 4), ('west', 2), ('east', 3)]`, build three mappings: region to list of all values, region to set of unique values, and region to numeric total. **Expected totals:** `{'east': 7, 'west': 2}`. **Constraints:** make the missing-key initial value explicit and preserve encounter order in the list version. **Verify:** assert all three outputs.

**Reasoning:** All three mappings are built in one pass, and each states its missing-key starting value explicitly: `setdefault(key, [])` for the list, `setdefault(key, set())` for the set, and `get(key, 0)` for the total. The list keeps every value in encounter order (`[4, 3]` for east), the set keeps only distinct values with no order promise, and the total keeps only the sum. A frequent slip is writing `{}` where an empty set was meant: `{}` is an empty dictionary, and `set()` is the empty set.

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

## Exercises 3-7: Expanded mastery answers

### Exercise 3: answer contract

**Learner contract:** **Prediction:** Predict the length and membership behavior of `{3, 1, 3, 2}`. Why must display order not be treated as a sorting guarantee? **Progressive hint:** Sets enforce uniqueness and optimize membership, not presentation order. **Verify:** Assert the set has length `3` and contains `1`, `2`, and `3`; compare values as a set rather than asserting display iteration order.

**Reasoning:** A set stores each distinct value once, so `{3, 1, 3, 2}` has length 3 and supports fast membership tests for 1, 2, and 3. Small integers often display in sorted order, but that is an accident of how integers hash, not a promise; a set of strings can display in a different order on every run. Tests should therefore compare with another set (`== {1, 2, 3}`) or use `sorted(...)` when order matters, as the shared implementation for Exercises 3-4 explains. Comparing a set with a list is always `False`, even when they hold the same values.

### Exercise 4: answer contract

**Learner contract:** **Tracing:** Trace shallow copying for `original = [[1], [2]]; copied = original.copy(); copied[0].append(9)`. **Progressive hint:** The outer lists differ but still refer to the same inner lists. **Verify:** Assert `original is not copied` but `original[0] is copied[0]`, then confirm appending through the copy appears in both nested lists.

**Reasoning:** `original.copy()` creates a new outer list but fills it with references to the same inner lists, so `copied is not original` is true while `copied[0] is original[0]` is also true. Appending 9 through `copied[0]` therefore changes the list that `original[0]` refers to, and both show `[1, 9]`. Replacing an outer element (`copied[0] = [7]`) would not affect `original`, which is the distinction most often blurred. `copy.deepcopy(original)` copies the nested lists as well when full independence is required.

### Exercise 5: answer contract

**Learner contract:** **Implementation:** Implement `invert_multimap(mapping)` so values become keys and each new key maps to a list of original keys in encounter order. **Progressive hint:** Use `setdefault` or `defaultdict(list)`. **Verify:** Assert exact output lists and encounter order for a mapping where two original keys share a value; also test an empty mapping.

**Reasoning:** Inverting a mapping can merge keys: two original keys with the same value must both appear under the new key, so each new value is a list rather than a single key. `defaultdict(list)` supplies the empty list on first use, and iterating `mapping.items()` keeps the original insertion order, so `{"a": 1, "b": 2, "c": 1}` becomes `{1: ["a", "c"], 2: ["b"]}`. Converting back to a plain `dict` at the end stops later lookups of missing keys from silently inserting empty lists. A naive `{value: key for key, value in mapping.items()}` keeps only the last key for each value.

### Exercise 6: answer contract

**Learner contract:** **Debugging:** Repair code that attempts to use a list as a dictionary key. Explain hashability and choose a tuple when the sequence is an identity. **Progressive hint:** Dictionary keys must have a stable hash while stored. **Verify:** Show the list-key version raises `TypeError`, then assert the tuple-key replacement retrieves the intended value and remains unmodified.

**Reasoning:** Dictionary keys must be hashable so the dictionary can find them again; a list is mutable, so Python refuses it with `TypeError: unhashable type: 'list'`. When a sequence is an identity, such as a coordinate pair, a tuple states that it will not change and is hashable. `tuple(coordinates)` converts the list once, and lookups must use the same tuple, `(40, -74)`. Converting with `str(coordinates)` would also run, but it creates fragile keys that depend on formatting.

### Exercise 7: answer contract

**Learner contract:** **Edge case and explanation:** Extend stable de-duplication to records using a `key` function, then test repeated dictionaries whose IDs match but other fields differ. **Progressive hint:** Store hashable derived keys while returning original records. **Verify:** Use repeated record dictionaries with the same ID; assert the first complete record is returned once, input order is preserved, and the input remains unchanged.

**Reasoning:** Dictionaries are not hashable, so the function stores a derived hashable key, here the `id`, in the `seen` set while returning the original record objects. The first record for each id wins and later duplicates are skipped even when their other fields differ; that is a policy to state, because "first wins" is not "latest wins". Encounter order is preserved because the result list is appended in input order. The assertion compares with `records[0]` and `records[2]`, proving that the original objects, not copies, are returned.

## Expanded mastery lab solutions

Choose structures by semantics, ordering, uniqueness, lookup, and mutability, not by habit. State what duplicates and missing keys mean.

### Shared implementation for Exercises 3-4: Set and copy semantics

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

### Shared implementation for Exercises 5-7: Multimaps, hashable identities, and keyed de-duplication

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
try:
    {coordinates: "station"}  # A list cannot be a key.
except TypeError as error:
    assert "unhashable" in str(error)


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
assert invert_multimap({}) == {}
```
