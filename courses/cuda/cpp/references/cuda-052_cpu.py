"""cuda-052: CPU reference only, not CUDA execution."""

import math

row = [1.0, 3.0]
mean = sum(row) / len(row)
variance = sum((x - mean) ** 2 for x in row) / len(row)
normalized = [(x - mean) / math.sqrt(variance) for x in row]
assert normalized == [-1.0, 1.0]
assert [max(0, x + 1) for x in [-2, 1]] == [0, 2]
print({"layer_normalized": normalized, "RMS_denominator": math.sqrt(5)})
