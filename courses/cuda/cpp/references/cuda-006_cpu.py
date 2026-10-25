"""cuda-006: CPU reference only, not CUDA execution."""

import math

values = [1e16, 1.0, -1e16]
naive = 0.0
for value in values:
    naive += value
assert naive == 0.0 and math.fsum(values) == 1.0
assert abs(4e-8) <= 1e-7
print({"sequential": naive, "compensated_reference": math.fsum(values)})
