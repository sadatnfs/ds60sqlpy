"""cuda-017: CPU reference only, not CUDA execution."""

tile = [3, 6, 9, 12]
# A CPU phase boundary models the dependency, not GPU scheduling.
output = [tile[3 - lane] for lane in range(4)]
assert output == [12, 9, 6, 3]
partial = [3, 6, 9, 0]
assert sum(partial) == 18
print({"reversal": output, "neutralized_tail_sum": sum(partial)})
