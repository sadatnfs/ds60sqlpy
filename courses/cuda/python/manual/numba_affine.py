"""Optional maintained numba-cuda lab for an explicitly prepared NVIDIA host."""

from importlib.metadata import PackageNotFoundError, version

import numpy as np
from numba import config, cuda

try:
    distribution = version("numba-cuda")
except PackageNotFoundError as exc:
    raise RuntimeError("Prepare the maintained numba-cuda distribution explicitly") from exc
if config.ENABLE_CUDASIM:
    raise RuntimeError("This is a real-device evidence lab; simulator runs need a different label")
if not cuda.is_available():
    raise RuntimeError("This optional lab requires a compatible NVIDIA CUDA device")


@cuda.jit
def affine_kernel(source, output):
    index = cuda.grid(1)
    if index < source.size:
        output[index] = 2 * source[index] + 1


for size in (1, 127, 128, 129, 257):
    host = np.arange(size, dtype=np.float32)
    source = cuda.to_device(host)
    output = cuda.device_array_like(source)
    threads = 128
    affine_kernel[(size + threads - 1) // threads, threads](source, output)
    cuda.synchronize()
    actual = output.copy_to_host()
    np.testing.assert_array_equal(actual, 2 * host + 1)
print("Real-device numba-cuda affine checks passed; distribution", distribution)
