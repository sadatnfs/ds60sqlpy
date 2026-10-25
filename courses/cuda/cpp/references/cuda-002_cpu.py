"""cuda-002: CPU reference only, not CUDA execution."""

from math import ceil

assert ceil(10 / 4) == 3
assert [ceil(n / 32) for n in (31, 32, 33, 100)] == [1, 1, 2, 4]
print({"simplified_waves": ceil(10 / 4), "warps_for_100_threads": ceil(100 / 32)})
