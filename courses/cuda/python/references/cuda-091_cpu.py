"""Independent CPU reference with deterministic contract assertions."""

x, k = [1, 2, 3, 4], [1, -1]
out = [sum(x[i + j] * k[j] for j in range(len(k))) for i in range(len(x) - len(k) + 1)]
assert out == [-1, -1, -1]
assert 2 + 1 * 1 > 2 * 1
assert 2 + 1 * 4 < 2 * 4
print("CPU convolution oracle:", out)
