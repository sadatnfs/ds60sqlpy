"""Optional NVIDIA CUDA lab. No CPU fallback or external dataset."""

import cupy as cp

if cp.cuda.runtime.getDeviceCount() < 1:
    raise RuntimeError("This variant requires an explicitly prepared NVIDIA CUDA GPU")
cp.cuda.Device(0).use()

x = cp.asarray([1.0, 2.0, 3.0], dtype=cp.float32)
y = cp.sum(x)
cp.cuda.get_current_stream().synchronize()
assert float(y.get()) == 6.0
print("CUDA array sum:", float(y.get()), "device", x.device.id)
