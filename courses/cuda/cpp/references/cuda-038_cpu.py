"""cuda-038: CPU reference only, not CUDA execution."""

import statistics

baseline, candidate = [10, 11, 10, 9, 10], [8, 8, 9, 8, 7]
speedup = statistics.median(baseline) / statistics.median(candidate)
assert speedup == 1.25
print(
    {
        "synthetic_median_speedup": speedup,
        "baseline_samples_ms": baseline,
        "candidate_samples_ms": candidate,
    }
)
