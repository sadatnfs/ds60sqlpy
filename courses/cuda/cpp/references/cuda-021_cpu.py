"""cuda-021: CPU reference only, not CUDA execution."""

values = [8, 3, 6, 1, 4]
flags = [int(v % 2 == 0) for v in values]
positions, count = [], 0
for flag in flags:
    positions.append(count)
    count += flag
out = [None] * count
for v, flag, position in zip(values, flags, positions):
    if flag:
        out[position] = v
assert out == [8, 6, 4] and positions == [0, 1, 1, 2, 2]
print({"flags": flags, "positions": positions, "compacted": out})
