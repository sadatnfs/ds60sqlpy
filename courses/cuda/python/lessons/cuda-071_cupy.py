"""Optional NVIDIA CUDA lab. No CPU fallback or external dataset."""

import cupy as cp

if cp.cuda.runtime.getDeviceCount() < 1:
    raise RuntimeError("This variant requires an explicitly prepared NVIDIA CUDA GPU")
cp.cuda.Device(0).use()

x = cp.arange(4096, dtype=cp.float32)
for _ in range(2):
    y = x * 2 + 1
cp.cuda.get_current_stream().synchronize()
start, end = cp.cuda.Event(), cp.cuda.Event()
start.record()
y = x * 2 + 1
end.record()
end.synchronize()
cp.testing.assert_allclose(y, 2 * cp.arange(4096, dtype=cp.float32) + 1)
print(
    "CUDA event interval:",
    cp.cuda.get_elapsed_time(start, end),
    "ms; excludes transfers and initial compilation",
)
