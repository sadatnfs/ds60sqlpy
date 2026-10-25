"""Independent CPU reference with deterministic contract assertions."""

sizes, means = [3, 1], [2.0, 8.0]
weighted = sum(n * g for n, g in zip(sizes, means, strict=True)) / sum(sizes)
wrong = sum(means) / len(means)
assert weighted == 3.5 and wrong == 5
print("CPU accumulation oracle:", weighted, wrong)
