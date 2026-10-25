"""cuda-045: CPU reference only, not CUDA execution."""

values = [1, 2, 3, 4]
assert sum(x * x for x in values) == 30
selected = [x for x in [5, 2, 5, 1] if x >= 5]
assert selected == [5, 5]
print({"transform_reduce_reference": 30, "stable_selection": selected})
