"""cuda-004: CPU reference only, not CUDA execution."""

values = [2, 1, 3, 4]
prefix, total = [], 0
for value in values:
    prefix.append(total)
    total += value
assert prefix == [0, 2, 3, 6] and total == 10
ranges = [list(range(start, min(start + 4, 10))) for start in range(0, 10, 4)]
assert sum(ranges, []) == list(range(10))
print({"exclusive_scan": prefix, "reduction": total, "ownership": ranges})
