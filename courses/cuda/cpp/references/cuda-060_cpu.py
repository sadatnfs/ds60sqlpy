"""cuda-060: CPU reference only, not CUDA execution."""

values = [1, 2, 3, 4, 5]
partials = [sum(values[:3]), sum(values[3:])]
all_reduce_model = [sum(partials)] * 2
assert partials == [6, 9] and all_reduce_model == [15, 15]
print({"CPU_collective_model": all_reduce_model, "multi_GPU_executed": False})
assert 1.6 / 2 == 0.8
