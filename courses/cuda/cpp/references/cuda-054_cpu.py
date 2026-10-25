"""cuda-054: CPU reference only, not CUDA execution."""

import math

weights = [math.exp(1) / (math.exp(1) + 1), 1 / (math.exp(1) + 1)]
out = [weights[0] * 2, weights[1] * 4]
assert abs(sum(weights) - 1) < 1e-12
assert 4096 * 4096 * 4 == 64 * 1024 * 1024
print({"unscaled_tiny_attention": out, "score_matrix_MiB": 64})
