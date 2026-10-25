"""Optional NVIDIA CUDA lab. No CPU fallback or external dataset."""

import cupy as cp

if cp.cuda.runtime.getDeviceCount() < 1:
    raise RuntimeError("This variant requires an explicitly prepared NVIDIA CUDA GPU")
cp.cuda.Device(0).use()

x = cp.asarray([[1.0, 3.0], [3.0, 7.0]], dtype=cp.float32)
centered = x - cp.mean(x, axis=0)
cp.testing.assert_allclose(centered, cp.asarray([[-1, -2], [1, 2]], dtype=cp.float32))
cp.cuda.get_current_stream().synchronize()
print("CUDA centered features:", cp.asnumpy(centered).tolist())
