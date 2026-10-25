"""cuda-055: CPU reference only, not CUDA execution."""

values = list(range(1, 9))
partials = [sum(values[start : start + 4]) for start in range(0, len(values), 4)]
assert partials == [10, 26] and sum(partials) == 36
assert 12 > 4 * 2
print({"group_sums": partials, "simplified_cooperative_capacity": 8})
