"""cuda-048: CPU reference only, not CUDA execution."""

offsets, columns, values = [0, 2, 3], [0, 2, 1], [2, 1, 3]
x = [4, 5, 6]
y = [sum(values[j] * x[columns[j]] for j in range(offsets[r], offsets[r + 1])) for r in range(2)]
assert y == [14, 15]
assert offsets[-1] == len(values) == len(columns)
print({"CSR_product": y, "row_lengths": [offsets[i + 1] - offsets[i] for i in range(2)]})
