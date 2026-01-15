# Day 13 — Functional Tools: itertools, functools, map/filter (Companion Guide)

## Learning objectives
- Compose transformations with `itertools` and generator patterns
- Cache and partially apply functions with `functools`
- Know when vectorization (NumPy/pandas) beats Python‑level `map/filter`

## Essentials
```python
import itertools as it
from functools import lru_cache, partial

list(it.accumulate([1,2,3,4]))   # running totals

@lru_cache(maxsize=None)
def fib(n: int) -> int:
    return n if n < 2 else fib(n-1) + fib(n-2)

pow2 = partial(pow, 2)
pow2(5)  # 32
```

## Tips
- Prefer comprehensions for readability; switch to `itertools` for advanced streams
- Cache pure functions with `lru_cache` to avoid recomputation

## Practice exercises
1) Use `groupby` to summarize consecutive events by user
2) Build a pipeline with `itertools.chain.from_iterable` to flatten nested lists lazily

## Further reading
- itertools: https://docs.python.org/3/library/itertools.html
- functools: https://docs.python.org/3/library/functools.html
