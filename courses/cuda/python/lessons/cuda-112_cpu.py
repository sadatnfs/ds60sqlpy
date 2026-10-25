"""Editable CPU worked example. This does not execute or simulate a GPU.

Complete the six guide exercises separately; modify one bounded case at a time.
"""

import statistics

baseline, candidate = [10, 11, 9], [8, 8, 9]
speedup = statistics.median(baseline) / statistics.median(candidate)
assert speedup == 1.25
report = {
    "fixture": "synthetic CPU timing analysis",
    "median_ratio": speedup,
    "gpu_benchmark": False,
}
print(report)
