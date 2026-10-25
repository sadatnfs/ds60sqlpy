"""cuda-046: CPU reference only, not CUDA execution."""

product = [[7, 4], [16, 13]]
result = [[2 * x + 3 for x in row] for row in product]
assert result == [[17, 11], [35, 29]]
A = [[1, 2, 3], [4, 5, 6]]
column_major = [A[r][c] for c in range(3) for r in range(2)]
assert column_major == [1, 4, 2, 5, 3, 6]
print({"scaled_GEMM": result, "column_major": column_major})
