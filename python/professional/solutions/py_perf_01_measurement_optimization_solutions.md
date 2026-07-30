# Measurement-first optimization solution reasoning

Attempt `python-perf-01` before opening
[`py_perf_01_measurement_optimization_solution.py`](py_perf_01_measurement_optimization_solution.py).

The solution first fixes the workload and output semantics. The quadratic
duplicate search repeatedly scans prefixes; the set-based implementation keeps
the value whose second occurrence appears first while changing expected
complexity from O(n squared) to O(n). Correctness tests compare varied edge
cases before any timing is interpreted.

`timeit` performs warmups and repeated batches. Minimum, median, and maximum are
reported as evidence from one machine; none becomes a universal test
threshold. `cProfile` locates cumulative hotspots, while `tracemalloc` measures
Python allocations and peak pressure. Native-library buffers and operating
system memory may require additional tools.

The streamed sum avoids an intermediate list. NumPy is an optional vectorized
comparison, not a promised speedup: conversion cost and array size matter.
Likewise, process work may copy or serialize the payload per worker, so adding
processes can increase elapsed time and memory.

Caching trades recomputation for memory and staleness. The deterministic policy
refuses cache when freshness or budget disallows it, accepts high measured
reuse within budget, and otherwise requests more evidence.

Native extensions and foreign-function interfaces (FFIs) add packaging,
portability, safety, and boundary-transfer costs. Improve the algorithm first.
When native work owns a measured hotspot, batch calls and data transfer rather
than crossing the boundary in a tight Python loop.

Edge cases include benchmarks smaller than timer noise, cold imports, thermal
or background-load variation, changed semantics, hash/cache keys that retain
large objects, process copies hidden by copy-on-write assumptions, native
allocations invisible to `tracemalloc`, and microbenchmarks that do not
represent production data.

