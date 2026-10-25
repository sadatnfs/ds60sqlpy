"""cuda-032: CPU reference only, not CUDA execution."""

phases = {"upload": 3, "kernel": 2, "download": 3, "host": 2}
total = sum(phases.values())
optimized = total - phases["kernel"] + phases["kernel"] / 2
assert total == 10 and optimized == 9
print({"synthetic_total_ms": total, "half_kernel_total_ms": optimized})
