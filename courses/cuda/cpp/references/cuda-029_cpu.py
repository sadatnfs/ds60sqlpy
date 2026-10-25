"""cuda-029: CPU reference only, not CUDA execution."""

import math

values = [100000001.0, 100000002.0, 100000003.0]
mean = math.fsum(values) / len(values)
variance = math.fsum((x - mean) ** 2 for x in values) / len(values)
assert variance == 2 / 3
assert math.fsum((x - 2) ** 2 for x in [2, 2, 2]) == 0
print({"mean": mean, "centered_population_variance": variance})
