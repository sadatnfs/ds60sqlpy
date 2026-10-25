"""cuda-022: CPU reference only, not CUDA execution."""

values = [0, 2, 2, 1, 2, 0]


def histogram(items):
    bins = [0, 0, 0]
    for value in items:
        assert 0 <= value < len(bins)
        bins[value] += 1
    return bins


parts = [histogram(values[:3]), histogram(values[3:])]
merged = [sum(pair) for pair in zip(*parts)]
assert merged == [2, 1, 3] and sum(merged) == len(values)
print({"partials": parts, "merged": merged})
