"""Optional NVIDIA CUDA lab. No CPU fallback or external dataset."""

import cupy as cp

if cp.cuda.runtime.getDeviceCount() < 1:
    raise RuntimeError("This variant requires an explicitly prepared NVIDIA CUDA GPU")
cp.cuda.Device(0).use()

kernel = cp.RawKernel(
    r"""
extern "C" __global__ void twice(const float* x, float* y, int n) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n) y[i] = 2.0f * x[i];
}
""",
    "twice",
)
for n in [0, 1, 127, 128, 129, 257]:
    x = cp.arange(n, dtype=cp.float32)
    y = cp.empty_like(x)
    if n:
        kernel(((n + 127) // 128,), (128,), (x, y, cp.int32(n)))
    cp.cuda.get_current_stream().synchronize()
    cp.testing.assert_array_equal(y, 2 * x)
print("CUDA tail tests passed for zero, singleton and nonmultiples")
