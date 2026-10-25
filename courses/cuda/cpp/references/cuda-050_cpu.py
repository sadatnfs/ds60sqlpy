"""cuda-050: CPU reference only, not CUDA execution."""

import random

rng = random.Random(7)
samples = [rng.random() ** 2 for _ in range(10000)]
estimate = sum(samples) / len(samples)
assert abs(estimate - 1 / 3) < 0.03
repeated = [0.1, 0.7] * 4
assert len(repeated) == 8 and len(set(repeated)) == 2
print(
    {
        "CPU_integral_estimate": estimate,
        "exact_integral": 1 / 3,
        "duplicated_stream_unique_draws": 2,
    }
)
