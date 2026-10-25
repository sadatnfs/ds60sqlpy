"""Optional NVIDIA CUDA lab. No CPU fallback or external dataset."""

import cupy as cp

if cp.cuda.runtime.getDeviceCount() < 1:
    raise RuntimeError("This variant requires an explicitly prepared NVIDIA CUDA GPU")
cp.cuda.Device(0).use()

x = cp.arange(6, dtype=cp.float32).reshape(2, 3)
view = x[:, ::2]
assert view.shape == (2, 2)
assert view.strides == (12, 8)
cp.testing.assert_array_equal(view, cp.asarray([[0, 2], [3, 5]], dtype=cp.float32))
cp.cuda.get_current_stream().synchronize()
print("CUDA layout:", view.shape, view.strides, cp.asnumpy(view).tolist())
