"""cuda-023: CPU reference only, not CUDA execution."""

values = [2.0, 4.0, 8.0]


def at(i):
    return values[i] if 0 <= i < len(values) else 0.0


out = [(at(i - 1) + at(i) + at(i + 1)) / 3 for i in range(len(values))]
assert out == [2.0, 14 / 3, 4.0]
assert values == [2.0, 4.0, 8.0]
print({"fixed_zero_mean": out, "original_preserved": values})
