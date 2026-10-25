"""cuda-034: CPU reference only, not CUDA execution."""

contiguous = [lane * 4 for lane in range(32)]
strided = [lane * 8 * 4 for lane in range(32)]
assert contiguous[-1] + 4 == 128
assert strided[-1] + 4 == 996
print({"contiguous_span_bytes": 128, "strided_span_bytes": 996})
