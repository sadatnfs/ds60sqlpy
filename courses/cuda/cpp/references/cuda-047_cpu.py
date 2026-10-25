"""cuda-047: CPU reference only, not CUDA execution."""

import cmath

signal = [0, 1, 0, -1]
spectrum = [
    sum(x * cmath.exp(-2j * cmath.pi * k * n / 4) for n, x in enumerate(signal)) for k in range(4)
]
expected = [0, -2j, 0, 2j]
assert all(abs(a - b) < 1e-12 for a, b in zip(spectrum, expected))
assert [1 * 3, 1 * 4 + 2 * 3, 2 * 4] == [3, 10, 8]
print({"DFT": spectrum, "linear_convolution": [3, 10, 8]})
