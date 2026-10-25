"""Independent CPU reference with deterministic contract assertions."""

import math

scores = [1000.0, 1001.0]
shift = max(scores)
exp = [math.exp(x - shift) for x in scores]
weights = [x / sum(exp) for x in exp]
assert abs(sum(weights) - 1) < 1e-12
assert weights[1] > weights[0]
causal = [[int(j <= i) for j in range(3)] for i in range(3)]
assert causal == [[1, 0, 0], [1, 1, 0], [1, 1, 1]]
print("CPU attention oracle:", weights, causal)
