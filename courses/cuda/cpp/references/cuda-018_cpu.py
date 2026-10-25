"""cuda-018: CPU reference only, not CUDA execution."""

A = [[1, 2, 3], [4, 5, 6]]
B = [[1, 2], [0, 1], [2, 0]]
C = [[sum(A[r][k] * B[k][c] for k in range(3)) for c in range(2)] for r in range(2)]
assert C == [[7, 4], [16, 13]]
print(C)
