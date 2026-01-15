# Day 11 — Solutions: Debugging, Logging, and Profiling

Line-by-line solutions that add logging to utilities and profile a slow function.

Contents
- Exercise 1: Add logging to CSV/JSON utilities
- Exercise 2: Profile and optimize a slow function

---

Exercise 1 — Add logging to utilities
We’ll instrument `safe_load_json` and the CSV/JSON converters (from Day 08) with the standard library `logging`.

```python
import logging
from pathlib import Path
import json, csv
from typing import Any

log = logging.getLogger(__name__)                  # 1) get a module-level logger


def safe_load_json(path: str | Path) -> Any | None:
    p = Path(path)
    log.info("loading JSON: %s", p)               # 2) info-level start message
    try:
        with p.open(encoding="utf-8") as f:
            data = json.load(f)
            log.debug("loaded keys: %s", list(data)[:5])
            return data
    except FileNotFoundError:
        log.error("not found: %s", p)
    except PermissionError:
        log.error("permission denied: %s", p)
    except json.JSONDecodeError as e:
        log.error("invalid JSON %s (line %d col %d): %s", p, e.lineno, e.colno, e.msg)
    return None


def csv_to_json(csv_path: Path, json_path: Path) -> None:
    log.info("csv→json: %s → %s", csv_path, json_path)
    with csv_path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
        log.info("rows read: %d", len(rows))
    with json_path.open("w", encoding="utf-8") as out:
        json.dump(rows, out, indent=2)
        log.info("wrote json: %s", json_path)


def json_to_csv(json_path: Path, csv_path: Path) -> None:
    log.info("json→csv: %s → %s", json_path, csv_path)
    data = safe_load_json(json_path)
    if not data:
        log.warning("no data; writing empty CSV: %s", csv_path)
        csv_path.write_text("", encoding="utf-8")
        return
    fieldnames = sorted({k for rec in data for k in rec})
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for rec in data:
            w.writerow({k: rec.get(k, "") for k in fieldnames})
    log.info("wrote csv: %s (cols=%d)", csv_path, len(fieldnames))

# Configure logging in your app entry point (once):
# logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
```
Line-by-line highlights
- Use a module-level logger (getLogger(__name__)) so libraries can be configured by applications.
- INFO for high-level progress; DEBUG for noisy details; ERROR for failures.
- Prefer structured messages (`"%s"` placeholders) over f-strings in logging for lazy formatting.

---

Exercise 2 — Profile and optimize
Start with a slow Python loop and compare with NumPy vectorization.

```python
import timeit, numpy as np

# Baseline: Python loop (intentionally slow)
def scale_loop(xs: list[float], k: float) -> list[float]:
    out = []                               # 1) new list to hold results
    for x in xs:                           # 2) Python-level loop
        out.append(x * k)                  # 3) multiply and append
    return out

# Vectorized: ndarray operations

def scale_vec(xs: np.ndarray, k: float) -> np.ndarray:
    return xs * k                          # elementwise multiply in C

# Timing
arr = np.arange(1_000_00, dtype=float)     # 100k elements
lst = arr.tolist()

loop_t = timeit.timeit(lambda: scale_loop(lst, 2.0), number=10)
vec_t  = timeit.timeit(lambda: scale_vec(arr, 2.0), number=10)
print({"loop_sec": loop_t, "vec_sec": vec_t})
```
Explanation
- timeit runs the callable multiple times; compare totals.
- Expect significant speedup from vectorization due to C-level loops and contiguous memory.

Extra: Using `cProfile`
```python
import cProfile, pstats

with cProfile.Profile() as pr:
    _ = scale_loop(lst, 2.0)

pstats.Stats(pr).strip_dirs().sort_stats("cumtime").print_stats(10)
```
- cumtime shows where total time is spent; optimize those hot paths first.
