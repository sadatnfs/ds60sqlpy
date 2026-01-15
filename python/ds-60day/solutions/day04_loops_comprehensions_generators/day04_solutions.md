# Day 04 — Solutions: Loops, Comprehensions, and Generators

Beginner-friendly, line-by-line explanations for each exercise.

Contents
- Exercise 1: Loop → list comprehension
- Exercise 2: Even-number generator up to N
- Exercise 3: Frequency dictionary via comprehension (and Counter)

---

Exercise 1 — Convert a loop that builds a filtered list into a comprehension
Goal: Given a list of numbers, keep the squares of the positive ones.

Loop version (starting point)
```python
nums = [-2, -1, 0, 3, 5]
out = []
for x in nums:                  # 1) iterate each element
    if x > 0:                   # 2) keep only positives
        out.append(x * x)       # 3) append its square
```

Comprehension version
```python
nums = [-2, -1, 0, 3, 5]
out = [x * x for x in nums if x > 0]
```
Line-by-line mapping
- [x * x ...] → what to compute per kept element (the square)
- for x in nums → where elements come from (the input iterable)
- if x > 0 → filter condition; only truthy items are included

Notes
- List comprehensions are concise and often faster than manual loops for simple transforms + filters.
- Prefer readability: if the expression becomes long or uses nested loops, break it back into a normal loop.

---

Exercise 2 — Generator that yields even numbers up to N
Goal: Produce a sequence lazily (one-at-a-time) to avoid building large lists in memory.

```python
def evens_up_to(n: int):
    """Yield even integers from 0 up to and including n.

    Args:
        n: non-negative upper bound

    Yields:
        even integers in ascending order
    """
    if n < 0:                          # 1) guard clause for invalid input
        raise ValueError("n must be >= 0")
    for i in range(0, n + 1, 2):       # 2) start at 0, step by 2
        yield i                        # 3) produce one value at a time

# Demo
list(evens_up_to(10))  # [0, 2, 4, 6, 8, 10]
```
Why a generator?
- Memory-friendly for large n (doesn’t build a full list)
- Composable with other generators or streaming pipelines

Variation: generator expression
```python
evens = (i for i in range(101) if i % 2 == 0)
```

---

Exercise 3 — Build a frequency dict using a comprehension
Goal: Count occurrences of items. We’ll show both a comprehension-based approach and the purpose-built tools.

Comprehension + set baseline
```python
items = list("datascience")
unique = set(items)                                   # unique symbols
freq = {ch: sum(1 for x in items if x == ch) for ch in unique}
freq  # e.g., {'d': 1, 'a': 2, ...}
```
Line-by-line
- unique = set(items) → we only compute one count per unique element
- {ch: ... for ch in unique} → dict comprehension mapping char → count
- sum(1 for x in items if x == ch) → count matches by summing 1s

Better: collections.Counter (clearer and faster)
```python
from collections import Counter
items = list("datascience")
freq = Counter(items)           # Counter({'e': 3, 'a': 2, 's': 2, 'd': 1, 't': 1, 'c': 1, 'i': 1, 'n': 1})
```
Trade-offs
- Comprehension teaches the mechanics but is O(n^2) in worst case
- Counter is the idiomatic O(n) solution and should be preferred in practice
