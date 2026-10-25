"""cuda-007: CPU reference only, not CUDA execution."""

n, bytes_per_element, bandwidth = 1_000_000, 12, 600e9
seconds = n * bytes_per_element / bandwidth
assert abs(seconds - 20e-6) < 1e-15
limits = [min(10e12, intensity * 500e9) for intensity in (2, 40)]
assert limits == [1e12, 10e12]
print({"ideal_memory_seconds": seconds, "roofline_flops_per_second": limits})
