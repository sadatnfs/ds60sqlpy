"""Optional NVIDIA CUDA lab. No CPU fallback or external dataset."""

import cupy as cp

if cp.cuda.runtime.getDeviceCount() < 1:
    raise RuntimeError("This variant requires an explicitly prepared NVIDIA CUDA GPU")
cp.cuda.Device(0).use()

kernel = cp.RawKernel(
    r"""
extern "C" __global__ void affine(const float* x, float* y, int n) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    if (i < n) y[i] = 2.0f * x[i] + 1.0f;
}
""",
    "affine",
)
x = cp.asarray([-1.0, 0.0, 3.0], dtype=cp.float32)
y = cp.empty_like(x)
kernel((1,), (128,), (x, y, cp.int32(x.size)))
cp.cuda.get_current_stream().synchronize()
cp.testing.assert_allclose(y, cp.asarray([-1.0, 1.0, 7.0], dtype=cp.float32))
print("CUDA raw affine:", cp.asnumpy(y).tolist())
