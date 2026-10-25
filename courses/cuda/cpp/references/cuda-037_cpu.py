"""cuda-037: CPU reference only, not CUDA execution."""

workloads = [1, 1, 1, 9]
utilization = sum(workloads) / (len(workloads) * max(workloads))
assert utilization == 1 / 3
assert sum([3, 3, 3, 3]) == sum(workloads)
print({"synthetic_lockstep_useful_fraction": utilization, "preprocess_ms_minus_saved_ms": 2 - 1})
