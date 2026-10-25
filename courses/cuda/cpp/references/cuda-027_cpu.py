"""cuda-027: CPU reference only, not CUDA execution."""

mask = sum(1 << lane for lane in (0, 2, 5))
assert mask == 37 and mask.bit_count() == 3
contributions = list(range(1, 9)) + [0] * 24
assert sum(contributions) == 36
print({"ballot_mask": mask, "count": mask.bit_count(), "sum": sum(contributions)})
