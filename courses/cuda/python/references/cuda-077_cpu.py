"""Independent CPU reference with deterministic contract assertions."""

import math

values = [1e16, 1.0, -1e16]
assert math.fsum(values) == 1.0
items = [1, 2, 3, 4, 5]
while len(items) > 1:
    items = [sum(items[i : i + 2]) for i in range(0, len(items), 2)]
assert items == [15]
print("CPU reduction reference:", math.fsum(values), items[0])
