# Day 11 — Debugging, Logging, and Profiling (Companion Guide)

## Learning objectives
- Choose between `print` and `logging` and configure loggers
- Measure performance with `timeit` and `cProfile`
- Identify and address hot spots (vectorization, algorithms)

## Why this matters
Clear diagnostics reduce mean‑time‑to‑repair. Performance wins often come from measurement + picking the right algorithm or vectorization.

## Logging setup
```python
import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
log = logging.getLogger(__name__)
log.info('starting…')
```
Use levels intentionally; avoid logging secrets/PII.

## Timing snippets
```python
import timeit
setup = 'import numpy as np; x = np.arange(1_000_000)'
stmt  = 'x * 2'
print(timeit.timeit(stmt, setup=setup, number=100))
```

## Profiling functions
- `cProfile`: whole‑program profiling
- `line_profiler` (optional): line‑level timing

## Common patterns
- Replace Python loops over arrays with NumPy vectorization
- Cache pure function results with `functools.lru_cache`

## Practice exercises
1) Add logging to your CLI tool; include start/end timestamps and input size
2) Profile a slow function, then: pick a better data structure or vectorize

## Further reading
- logging: https://docs.python.org/3/library/logging.html
- timeit: https://docs.python.org/3/library/timeit.html
- cProfile: https://docs.python.org/3/library/profile.html
