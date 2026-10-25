"""cuda-001: CPU reference only, not CUDA execution."""

cpu = 20 + 80
gpu = 20 + 80 / 10 + 4
assert gpu == 32
assert cpu / gpu == 3.125
assert 100 / 40 == 2.5
print({"CPU_seconds": cpu, "modeled_GPU_seconds": gpu, "speedup": cpu / gpu})
