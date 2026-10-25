"""cuda-012: CPU reference only, not CUDA execution."""

n, launched = 5, 8
out = [None] * n
for i in range(launched):
    if i < n:
        out[i] = 2 * i + 1
assert out == [1, 3, 5, 7, 9]
print({"CPU_ownership_trace": out, "GPU_execution": "not performed"})
