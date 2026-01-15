# Day 23 — Data Pipelines and Generators (Companion Guide)

## Learning objectives
- Stream large files with chunking and generators
- Compose iterators with itertools and generator functions
- Separate I/O from pure transforms for testability

## Why this matters
Not all data fits in memory. Streaming pipelines enable scalable, memory-efficient processing and clearer architecture.

## Core concepts and examples
### read_csv with chunksize
```python
import pandas as pd
chunks = pd.read_csv('big.csv', chunksize=100_000)
for chunk in chunks:
    process(chunk)
```

### Generator functions
```python
def read_lines(path):
    with open(path, 'r') as f:
        for line in f:
            yield line.rstrip('\n')
```

### Composing iterators
```python
from itertools import islice, chain
first_1k = islice(read_lines('log.txt'), 1000)
all_lines = chain(read_lines('a.txt'), read_lines('b.txt'))
```

### Pure transforms
```python
def clean(df):
    return (df.assign(sku=lambda d: d['sku'].str.strip().str.upper())
              .astype({'qty':'int64'}))
```

## Common pitfalls
- Mixing side effects and transforms; keep functions pure where possible
- Forgetting to close file handles; use context managers
- Accumulating lists in memory when a stream would suffice

## Practice exercises
1) Build a CSV-to-Parquet converter that processes in chunks
2) Implement a generator that yields parsed log records as dicts
3) Write tests for your pure transform functions

## Further reading
- itertools: https://docs.python.org/3/library/itertools.html
- Toolz: https://toolz.readthedocs.io
