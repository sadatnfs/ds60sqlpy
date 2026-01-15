# Day 13 — Solutions: Functional Tools (itertools, functools, map/filter)

We implement grouping with itertools.groupby and create specialized functions with functools.partial.

Contents
- Exercise 1: Group pairs by key with itertools.groupby
- Exercise 2: Use partial to specialize a function

---

Exercise 1 — Group by key
Note: itertools.groupby requires data to be sorted by the same key.

```python
import itertools as it
from operator import itemgetter
from typing import Iterable, Tuple, Hashable, List

Pair = Tuple[Hashable, int]

def group_pairs(pairs: Iterable[Pair]) -> dict[Hashable, list[int]]:
    # 1) sort by key so groupby can group consecutive items
    pairs_sorted = sorted(pairs, key=itemgetter(0))
    out: dict[Hashable, list[int]] = {}
    # 2) groupby yields (key, iterator-over-group)
    for k, group in it.groupby(pairs_sorted, key=itemgetter(0)):
        vals = [v for _, v in group]         # 3) extract second element
        out[k] = vals
    return out

# Demo
pairs = [("b",2),("a",1),("a",3),("b",4)]
assert group_pairs(pairs) == {"a":[1,3], "b":[2,4]}
```
Line-by-line
- sorted by itemgetter(0) aligns with groupby’s key
- group is an iterator over consecutive items with the same key

Alternative: collections.defaultdict (often simpler and order-preserving per input).

---

Exercise 2 — partial to specialize
Given a generic power function, make square and cube variants.

```python
from functools import partial

def power(base: float, exp: float) -> float:
    return base ** exp

square = partial(power, exp=2)
cube   = partial(power, exp=3)

assert square(5) == 25
assert cube(2) == 8
```
Notes
- partial binds some parameters, returning a new callable with fewer arguments.
- Combine with map for pipelines, but prefer comprehensions for clarity when possible.
