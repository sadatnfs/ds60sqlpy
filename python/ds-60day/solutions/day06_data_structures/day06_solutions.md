# Day 06 — Solutions: Lists, Tuples, Sets, Dicts

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

## Exercise-by-exercise reference

Every numbered learner exercise has a matching entry here. The original
worked examples remain above; the expanded answers below add heavily
commented code, explicit reasoning, and executable checks.

### Exercise 1 — Original lesson practice

**Prompt:** Implement stable de-duplication that preserves the first occurrence. **Hint:** keep one structure for membership checks and another for ordered output.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 2 — Original lesson practice

**Prompt:** Aggregate key-value pairs by key. Try collecting values, unique values, and numeric totals. **Hint:** decide what a missing key should start with before processing the pair.

The earlier worked solution in this file is the reference answer. Trace it from inputs to output, then run its assertions or stated checks. The important review question is how that implementation applies the lesson contract rather than merely reproducing syntax.

### Exercise 3 — Prediction

**Prompt:** Predict the length and membership behavior of `{3, 1, 3, 2}`. Why must display order not be treated as a sorting guarantee?

**Reasoning checkpoint:** Sets enforce uniqueness and optimize membership, not presentation order. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 4 — Tracing

**Prompt:** Trace shallow copying for `original = [[1], [2]]; copied = original.copy(); copied[0].append(9)`.

**Reasoning checkpoint:** The outer lists differ but still refer to the same inner lists. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 5 — Implementation

**Prompt:** Implement `invert_multimap(mapping)` so values become keys and each new key maps to a list of original keys in encounter order.

**Reasoning checkpoint:** Use `setdefault` or `defaultdict(list)`. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 6 — Debugging

**Prompt:** Repair code that attempts to use a list as a dictionary key. Explain hashability and choose a tuple when the sequence is an identity.

**Reasoning checkpoint:** Dictionary keys must have a stable hash while stored. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

### Exercise 7 — Edge case and explanation

**Prompt:** Extend stable de-duplication to records using a `key` function, then test repeated dictionaries whose IDs match but other fields differ.

**Reasoning checkpoint:** Store hashable derived keys while returning original records. The detailed worked reasoning and commented implementation appear in the expanded solution immediately below.

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
