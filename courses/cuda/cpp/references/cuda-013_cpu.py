"""cuda-013: CPU reference only, not CUDA execution."""

storage = [-99, 1, 2, 3, -99]
for i in range(1, 4):
    storage[i] *= 2
assert storage == [-99, 2, 4, 6, -99]
assert 4 * 4 == 16 and 33 * 8 == 264
print({"guarded_output": storage, "four_float32_bytes": 16})
