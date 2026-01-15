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
