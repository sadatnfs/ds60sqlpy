"""Editable CPU worked example. This does not execute or simulate a GPU.

Complete the six guide exercises separately; modify one bounded case at a time.
"""

import statistics

samples = [10, 11, 10, 12, 100]
assert statistics.median(samples) == 11
submit_us, finish_us = 2, 102
assert finish_us / submit_us == 51
print("CPU trace analysis: median", statistics.median(samples), "ms; tail", max(samples))
