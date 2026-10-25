"""cuda-024: CPU reference only, not CUDA execution."""

values = [-2, 1, 3, -1, 2]
selected = [v for v in values if v >= 0]
bins = [selected.count(i) for i in range(4)]
assert selected == [1, 3, 2] and bins == [0, 1, 1, 1]
result = {"count": len(selected), "sum": sum(selected), "mean": sum(selected) / len(selected)}
assert result == {"count": 3, "sum": 6, "mean": 2.0}
print(result, bins)
