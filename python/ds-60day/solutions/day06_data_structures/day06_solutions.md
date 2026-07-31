# Day 06 — Solutions: Lists, Tuples, Sets, Dicts

<!-- BEGIN BEGINNER SOLUTION REVIEW -->
## Concept review before comparing answers

The solution is not a typing template. Read the learner contract, predict
the result, then compare decisions and evidence. The central mental model is
**choosing lists, tuples, sets, and dictionaries by semantics**.

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

### Reference pattern 1 — Preserve order while removing repeats

Use one structure for fast membership and another for ordered output.

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

**Expected observation:** `['a', 'b', 'c']`. Converting straight to a set would represent uniqueness but would not express first-seen order.

### Reference pattern 2 — Aggregate pairs into a dictionary

Make the missing-key starting value explicit.

```python
purchases = [("tea", 2), ("coffee", 1), ("tea", 3)]
totals = {}
for product, quantity in purchases:
    totals[product] = totals.get(product, 0) + quantity
totals
```

**Expected observation:** `{'tea': 5, 'coffee': 1}`. Tuple unpacking gives names to the two fields in each pair.

## Exercise-by-exercise reasoning map

The numbering and learner contracts below match the guide and notebook.
Each entry explains what to reason about, how to inspect the worked code,
an alternative, an edge case, and the evidence required for completion.

### Exercise 1 — reasoning, alternatives, and proof

**Learner contract:** Implement `stable_unique(values)` for `['b', 'a', 'b', 'c', 'a']`. **Expected result:** `['b', 'a', 'c']`. **Constraints:** preserve the first occurrence, leave the input unchanged, use a set for membership and a list for output, and state that items must be hashable. **Verify:** test the example, an empty list, and a list with no duplicates.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies choosing lists, tuples, sets, and dictionaries by semantics.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** `dict.fromkeys(values)` is a compact stable de-duplication technique for hashable values, while an explicit loop adapts to a derived key.

**Edge case:** Nested mutable values, unhashable records, missing keys, empty inputs, and repeated records with the same identity expose collection-policy choices.

**Solution evidence to inspect:** test the example, an empty list, and a list with no duplicates.

### Exercise 2 — reasoning, alternatives, and proof

**Learner contract:** Given `[('east', 4), ('west', 2), ('east', 3)]`, build three mappings: region to list of all values, region to set of unique values, and region to numeric total. **Expected totals:** `{'east': 7, 'west': 2}`. **Constraints:** make the missing-key initial value explicit and preserve encounter order in the list version. **Verify:** assert all three outputs.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies choosing lists, tuples, sets, and dictionaries by semantics.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** `dict.fromkeys(values)` is a compact stable de-duplication technique for hashable values, while an explicit loop adapts to a derived key.

**Edge case:** Nested mutable values, unhashable records, missing keys, empty inputs, and repeated records with the same identity expose collection-policy choices.

**Solution evidence to inspect:** assert all three outputs.

### Exercise 3 — reasoning, alternatives, and proof

**Learner contract:** **Prediction:** Predict the length and membership behavior of `{3, 1, 3, 2}`. Why must display order not be treated as a sorting guarantee? **Progressive hint:** Sets enforce uniqueness and optimize membership, not presentation order. **Verify:** Assert the set has length `3` and contains `1`, `2`, and `3`; compare values as a set rather than asserting display iteration order.

**Reasoning before code:** Evaluate the expression or state transition by hand first. Name the input state, the next operation, and the exact evidence that would falsify the prediction while applying choosing lists, tuples, sets, and dictionaries by semantics.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** `dict.fromkeys(values)` is a compact stable de-duplication technique for hashable values, while an explicit loop adapts to a derived key.

**Edge case:** Nested mutable values, unhashable records, missing keys, empty inputs, and repeated records with the same identity expose collection-policy choices.

**Solution evidence to inspect:** Assert the set has length `3` and contains `1`, `2`, and `3`; compare values as a set rather than asserting display iteration order.

### Exercise 4 — reasoning, alternatives, and proof

**Learner contract:** **Tracing:** Trace shallow copying for `original = [[1], [2]]; copied = original.copy(); copied[0].append(9)`. **Progressive hint:** The outer lists differ but still refer to the same inner lists. **Verify:** Assert `original is not copied` but `original[0] is copied[0]`, then confirm appending through the copy appears in both nested lists.

**Reasoning before code:** Create a small trace table with one row per operation or input item. Record the relevant names, labels, shape, or iterator position after each step so the choosing lists, tuples, sets, and dictionaries by semantics model is visible.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** `dict.fromkeys(values)` is a compact stable de-duplication technique for hashable values, while an explicit loop adapts to a derived key.

**Edge case:** Nested mutable values, unhashable records, missing keys, empty inputs, and repeated records with the same identity expose collection-policy choices.

**Solution evidence to inspect:** Assert `original is not copied` but `original[0] is copied[0]`, then confirm appending through the copy appears in both nested lists.

### Exercise 5 — reasoning, alternatives, and proof

**Learner contract:** **Implementation:** Implement `invert_multimap(mapping)` so values become keys and each new key maps to a list of original keys in encounter order. **Progressive hint:** Use `setdefault` or `defaultdict(list)`. **Verify:** Assert exact output lists and encounter order for a mapping where two original keys share a value; also test an empty mapping.

**Reasoning before code:** Separate setup/input, the operation being learned, and verification. Write the smallest implementation satisfying the stated constraints, then explain how every line applies choosing lists, tuples, sets, and dictionaries by semantics.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** `dict.fromkeys(values)` is a compact stable de-duplication technique for hashable values, while an explicit loop adapts to a derived key.

**Edge case:** Nested mutable values, unhashable records, missing keys, empty inputs, and repeated records with the same identity expose collection-policy choices.

**Solution evidence to inspect:** Assert exact output lists and encounter order for a mapping where two original keys share a value; also test an empty mapping.

### Exercise 6 — reasoning, alternatives, and proof

**Learner contract:** **Debugging:** Repair code that attempts to use a list as a dictionary key. Explain hashability and choose a tuple when the sequence is an identity. **Progressive hint:** Dictionary keys must have a stable hash while stored. **Verify:** Show the list-key version raises `TypeError`, then assert the tuple-key replacement retrieves the intended value and remains unmodified.

**Reasoning before code:** Reproduce the bad behavior on the smallest input, state the violated contract, make one repair, and rerun both the failing boundary and a normal case. Keep the diagnosis grounded in choosing lists, tuples, sets, and dictionaries by semantics.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** `dict.fromkeys(values)` is a compact stable de-duplication technique for hashable values, while an explicit loop adapts to a derived key.

**Edge case:** Nested mutable values, unhashable records, missing keys, empty inputs, and repeated records with the same identity expose collection-policy choices.

**Solution evidence to inspect:** Show the list-key version raises `TypeError`, then assert the tuple-key replacement retrieves the intended value and remains unmodified.

### Exercise 7 — reasoning, alternatives, and proof

**Learner contract:** **Edge case and explanation:** Extend stable de-duplication to records using a `key` function, then test repeated dictionaries whose IDs match but other fields differ. **Progressive hint:** Store hashable derived keys while returning original records. **Verify:** Use repeated record dictionaries with the same ID; assert the first complete record is returned once, input order is preserved, and the input remains unchanged.

**Reasoning before code:** Turn the ambiguous boundary into an explicit contract before coding. Test values immediately below, at, and above the boundary and explain how the result follows from choosing lists, tuples, sets, and dictionaries by semantics.

**How to read the code:** identify (1) the fixture or input,
(2) the operation that implements the contract, (3) the returned
value or side effect, and (4) the assertion/inspection that proves
the behavior. Comments should explain *why* a boundary exists, not
merely repeat the syntax.

**Alternative:** `dict.fromkeys(values)` is a compact stable de-duplication technique for hashable values, while an explicit loop adapts to a derived key.

**Edge case:** Nested mutable values, unhashable records, missing keys, empty inputs, and repeated records with the same identity expose collection-policy choices.

**Solution evidence to inspect:** Use repeated record dictionaries with the same ID; assert the first complete record is returned once, input order is preserved, and the input remains unchanged.
<!-- END BEGINNER SOLUTION REVIEW -->

We implement order-preserving dedupe and key-based aggregation with clear explanations.

Contents
- Exercise 1: Stable dedupe (preserve first occurrence order)
- Exercise 2: Aggregate by key (→ list, set, sum/max)

---

Exercise 1 — Stable dedupe
```python
from typing import Iterable, TypeVar, List
T = TypeVar('T')

def dedupe_stable(xs: Iterable[T]) -> List[T]:
    """Return items from xs with first occurrences preserved.

    Implementation keeps a set of seen items and appends unseen ones to output.
    """
    seen: set[T] = set()                 # 1) track items we've seen
    out: list[T] = []                    # 2) ordered result
    for x in xs:                         # 3) one pass (O(n))
        if x not in seen:                # 4) O(1) average membership
            seen.add(x)                  # 5) remember it
            out.append(x)                # 6) keep first occurrence
    return out

# Demo
assert dedupe_stable([1,2,2,3,3,3,1]) == [1,2,3]
```
Notes
- Requires elements to be hashable for set membership (numbers, strings, tuples). For unhashable items, use a key function or serialize.

---

Exercise 2 — Aggregate by key
Given pairs like [("a",1),("b",2),("a",3)], build structures grouped by key.

→ dict of lists
```python
from collections import defaultdict
from typing import Dict, List, Tuple, Hashable

Pair = Tuple[Hashable, T]

def group_list(pairs: Iterable[Pair]) -> Dict[Hashable, List[T]]:
    groups: defaultdict[Hashable, list[T]] = defaultdict(list)
    for k, v in pairs:
        groups[k].append(v)              # append preserves input order per key
    return dict(groups)
```

→ dict of sets (unique values per key)
```python
def group_set(pairs: Iterable[Pair]) -> Dict[Hashable, set[T]]:
    groups: defaultdict[Hashable, set[T]] = defaultdict(set)
    for k, v in pairs:
        groups[k].add(v)                 # set ensures uniqueness
    return dict(groups)
```

→ aggregate to a single value per key (sum / max)
```python
def aggregate_sum(pairs: Iterable[tuple[Hashable, float]]) -> dict[Hashable, float]:
    totals: dict[Hashable, float] = {}
    for k, v in pairs:
        totals[k] = totals.get(k, 0.0) + float(v)
    return totals


def aggregate_max(pairs: Iterable[tuple[Hashable, float]]) -> dict[Hashable, float]:
    best: dict[Hashable, float] = {}
    for k, v in pairs:
        v = float(v)
        best[k] = v if k not in best else max(best[k], v)
    return best

# Demo
pairs = [("a",1),("b",2),("a",3)]
assert group_list(pairs) == {"a":[1,3],"b":[2]}
assert group_set(pairs) == {"a":{1,3},"b":{2}}
assert aggregate_sum(pairs) == {"a":4.0, "b":2.0}
assert aggregate_max(pairs) == {"a":3.0, "b":2.0}
```
Tips
- defaultdict eliminates KeyError checks and keeps code compact.
- Choose list vs set based on whether order/duplicates matter for your task.

---

## Expanded mastery lab solutions

Choose structures by semantics—ordering, uniqueness, lookup, and mutability—not by habit. State what duplicates and missing keys mean.

Read the reasoning before the code. Inline comments explain ownership, boundary choices, and why each check exists; assertions turn the stated contract into executable evidence.

### Practices 1–2 — Set and copy semantics

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

### Practices 3–5 — Multimaps, hashable identities, and keyed de-duplication

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
