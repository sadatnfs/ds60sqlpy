"""cuda-009: CPU reference only, not CUDA execution."""

values = [-1, 0, 2]
result = [3 * value + 1 for value in values]
assert result == [-2, 1, 7]
padded = [1, 2, 99, 3, 4, 99]
row_sums = [sum(padded[r * 3 : r * 3 + 2]) for r in range(2)]
assert row_sums == [3, 7]
print({"affine": result, "row_sums": row_sums})
