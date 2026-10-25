"""Independent CPU reference with deterministic contract assertions."""

counts, gradients = [3, 1], [2.0, 4.0]
weighted = sum(n * g for n, g in zip(counts, gradients, strict=True)) / sum(counts)
assert weighted == 2.5
assert sum(gradients) / 2 == 3.0
print("CPU distributed-gradient oracle:", weighted)
