"""cuda-049: CPU reference only, not CUDA execution."""

A, b, x = [[3, 1], [1, 2]], [9, 8], [2, 3]
product = [sum(a * v for a, v in zip(row, x)) for row in A]
residual = [rhs - value for rhs, value in zip(b, product)]
assert residual == [0, 0]
wrong = [sum(a * v for a, v in zip(row, [2, 2])) for row in A]
assert [rhs - value for rhs, value in zip(b, wrong)] == [1, 2]
print({"solution": x, "residual": residual})
