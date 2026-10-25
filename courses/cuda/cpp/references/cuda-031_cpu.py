"""cuda-031: CPU reference only, not CUDA execution."""

import statistics

samples = [1.0, 1.1, 1.0, 1.2, 9.0]
assert statistics.median(samples) == 1.1
assert 12 / 4 == 3
print(
    {
        "synthetic_samples_ms": samples,
        "median_ms": statistics.median(samples),
        "maximum_ms": max(samples),
    }
)
