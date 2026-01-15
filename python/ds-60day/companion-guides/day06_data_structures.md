# Day 6 — Core Data Structures: Lists, Tuples, Sets, Dicts (Companion Guide)

## Learning objectives
- Understand each built‑in collection’s properties (mutability, ordering, uniqueness)
- Choose the right structure for the job (lookup vs order vs uniqueness vs memory)
- Implement common DS tasks: frequency counting, stable dedupe, grouping/aggregating
- Use purpose‑built helpers: `collections.Counter`, `defaultdict`, `deque`

## Why this matters
Data structure choice affects clarity and performance. In data science you’ll count, deduplicate, group, and join constantly. Knowing the right tool prevents O(n²) mistakes and makes your code simpler.

## Mental models
- List = ordered, mutable sequence; fast append, O(n) membership
- Tuple = ordered, immutable; hashable when elements are hashable (good as dict/set keys)
- Set = unordered, unique membership; O(1) average membership test
- Dict = key → value mapping; O(1) average get/set; preserves insertion order (3.7+)

## Patterns and examples
### Frequency counting
```python
from collections import Counter
words = "this is a test this is".split()
counts = Counter(words)          # {'this': 2, 'is': 2, 'a': 1, 'test': 1}
counts.most_common(2)
```

### Stable dedupe (preserve first occurrence order)
```python
def dedupe_stable(xs):
    seen = set()
    out = []
    for x in xs:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out
```

### Grouping with `defaultdict`
```python
from collections import defaultdict
pairs = [("a", 1), ("b", 2), ("a", 3)]
by_key = defaultdict(list)
for k, v in pairs:
    by_key[k].append(v)          # {'a': [1, 3], 'b': [2]}
```

### Using tuples as dict keys
```python
edges = {("SFO", "LAX"): 337, ("SFO", "SEA"): 679}
edges[("SFO", "LAX")]
```

## Performance notes
- Prefer sets when you need fast membership tests: `x in my_set`
- Prefer dict lookups over repeated `list.index` or `list.count`
- Converting a large list to a set for one‑time membership checks can pay off

## Common pitfalls
- Modifying a list while iterating forward (skip elements unexpectedly). Iterate a copy or go backward when removing
- Using lists for membership tests in hot loops (switch to set)
- Forgetting that dict/set membership checks depend on `__hash__`/`__eq__` semantics

## Practice exercises
1) Implement `top_k_frequent(xs, k)` using `Counter.most_common` and also without `Counter` (for practice).
2) Given `records = [(user, score), ...]`, build a dict of `user → max_score`.
3) Write `group_by_key(pairs)` returning `dict[key, list[values]]` and `group_by_key_set` returning `dict[key, set[values]]`.

## Stretch goals
- Implement a simple multimap class on top of `defaultdict(list)` with `.add(key, value)` and `.get(key)`
- Time `x in list` vs `x in set` for increasing sizes; plot the results

## Check your understanding
- When would you choose a tuple over a list? Give two examples
- Why does `set` drop duplicates but also scramble order (pre‑3.7 mental model)?
- What’s the complexity of `dict.get(k)` on average and worst case?

## Further reading
- collections: https://docs.python.org/3/library/collections.html
- time complexity reference (CPython): https://wiki.python.org/moin/TimeComplexity
