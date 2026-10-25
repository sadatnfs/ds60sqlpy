"""cuda-051: CPU reference only, not CUDA execution."""

import math


def softmax(values):
    maximum = max(values)
    exp = [math.exp(v - maximum) for v in values]
    return [v / sum(exp) for v in exp]


p = softmax([1000, 1001])
assert abs(sum(p) - 1) < 1e-12 and abs(p[1] - 0.7310585786300049) < 1e-12
assert softmax([4, 4, 4]) == [1 / 3] * 3
print(p)
