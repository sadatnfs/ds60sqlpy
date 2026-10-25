"""cuda-005: CPU reference only, not CUDA execution."""

rows, cols, stride, itemsize = 2, 3, 5, 4
assert ((1 * stride + 2) * itemsize) == 28
storage = [1, 2, 3, 4, 5, 6]
transposed = [[storage[r + c * 3] for c in range(2)] for r in range(3)]
assert transposed == [[1, 4], [2, 5], [3, 6]]
print({"offset_bytes": 28, "transpose_view_values": transposed})
