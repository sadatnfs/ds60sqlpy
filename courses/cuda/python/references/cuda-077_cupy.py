"""Optional NVIDIA CUDA lab. No CPU fallback or external dataset."""

import math

import cupy as cp

if cp.cuda.runtime.getDeviceCount() < 1:
    raise RuntimeError("This variant requires an explicitly prepared NVIDIA CUDA GPU")
cp.cuda.Device(0).use()

values = [1.0, 2.0, 3.0, 4.0, 5.0]
x = cp.asarray(values, dtype=cp.float64)
result = float(cp.sum(x).get())
assert math.isclose(result, math.fsum(values), rel_tol=1e-12, abs_tol=1e-12)
cp.cuda.get_current_stream().synchronize()
print("CUDA library reduction:", result, "; order-sensitive cases need a documented tolerance")
