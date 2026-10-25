"""Fixed optional CUDA operations. A CPU result never establishes GPU readiness."""

import sys
from pathlib import Path

GPU_PROFILES = frozenset({"cuda-cpp", "cuda-python", "pytorch-cuda", "tensorflow-cuda"})

CPP_PROBE = r"""#include <cuda_runtime.h>
#include <cstdio>
__global__ void add(int *value) { value[0] = 20 + 22; }
bool checked(cudaError_t status, const char *phase) {
    if (status == cudaSuccess) return true;
    std::fprintf(stderr,
                 "%s: %s. Check NVIDIA driver and container GPU access.\n",
                 phase, cudaGetErrorString(status));
    return false;
}
int main() {
    int count = 0, result = 0; int *device = nullptr;
    if (!checked(cudaGetDeviceCount(&count), "CUDA device discovery")) return 77;
    if (count < 1) {
        std::fputs("No NVIDIA CUDA device is visible to this worker.\n", stderr);
        return 77;
    }
    if (!checked(cudaMalloc(&device, sizeof(int)), "CUDA allocation")) return 78;
    add<<<1, 1>>>(device);
    bool ok = checked(cudaGetLastError(), "CUDA launch");
    ok = ok && checked(cudaDeviceSynchronize(), "CUDA completion");
    ok = ok && checked(
        cudaMemcpy(&result, device, sizeof(int), cudaMemcpyDeviceToHost),
        "CUDA readback");
    ok = checked(cudaFree(device), "CUDA cleanup") && ok;
    if (!ok) return 79;
    if (result != 42) {
        std::fputs("CUDA readback did not match the expected result.\n", stderr);
        return 79;
    }
    std::puts("CUDA allocation, kernel, synchronization and readback passed.");
}
"""

PYTHON_PROBES = {
    "cuda-python": (
        "import cupy as cp\n"
        "assert cp.cuda.runtime.getDeviceCount() > 0\n"
        "a = cp.asarray([20, 22], dtype=cp.int32)\n"
        "b = a.sum(); cp.cuda.get_current_stream().synchronize()\n"
        "assert int(b.get()) == 42\n"
        "print('CuPy CUDA computation and readback passed.')\n"
    ),
    "pytorch-cuda": (
        "import torch\n"
        "assert torch.version.cuda is not None and torch.cuda.is_available(), "
        "'A CUDA-enabled PyTorch build and a visible NVIDIA GPU are required.'\n"
        "a = torch.tensor([20, 22], device='cuda')\n"
        "b = a.sum(); torch.cuda.synchronize()\n"
        "assert b.is_cuda and int(b.cpu()) == 42\n"
        "print('PyTorch CUDA computation and readback passed.')\n"
    ),
    "tensorflow-cuda": (
        "import tensorflow as tf\n"
        "assert tf.test.is_built_with_cuda(), "
        "'This TensorFlow build does not include CUDA support.'\n"
        "devices = tf.config.list_physical_devices('GPU'); assert devices, "
        "'No GPU is visible to the TensorFlow worker.'\n"
        "for device in devices: tf.config.experimental.set_memory_growth(device, True)\n"
        "tf.config.set_soft_device_placement(False)\n"
        "with tf.device('/GPU:0'): b = tf.reduce_sum(tf.constant([20, 22]))\n"
        "assert 'GPU:0' in b.device and int(b.numpy()) == 42\n"
        "print('TensorFlow CUDA computation and readback passed.')\n"
    ),
}


def commands(profile: str, directory: Path) -> tuple[list[list[str]], list[str]]:
    if profile not in GPU_PROFILES:
        raise ValueError("Choose a registered CUDA profile.")
    if profile == "cuda-cpp":
        return [
            [
                "nvcc",
                "-std=c++20",
                "-O1",
                "-lineinfo",
                "-gencode=arch=compute_75,code=[sm_75,compute_75]",
                "main.cu",
                "-o",
                "program",
            ]
        ], [str(directory / "program")]
    return [], [sys.executable, "-u", "main.py"]


def probe_commands(profile: str, directory: Path) -> list[list[str]]:
    if profile == "cuda-cpp":
        (directory / "main.cu").write_text(CPP_PROBE, encoding="utf-8")
    else:
        (directory / "main.py").write_text(PYTHON_PROBES[profile], encoding="utf-8")
    compiling, run = commands(profile, directory)
    return [*compiling, run]


def needs_device_review(
    status: str, output: str, detail: str, returncode: int | None = None
) -> bool:
    """Keep interrupted device work unavailable without classifying lesson text as failure."""
    if detail == "Compilation did not produce a runnable artifact.":
        return False
    if (
        status in {"cancelled", "timed_out"}
        or detail.startswith("Scratch allowance exceeded")
        or (returncode is not None and returncode < 0)
    ):
        return True
    # A successful program may quote CUDA diagnostics as part of its lesson.
    # Only a failed runtime result makes those output strings fault evidence.
    if status != "failed":
        return False
    return any(
        term in output.lower()
        for term in (
            "illegal memory access",
            "device-side assert",
            "unspecified launch failure",
            "context is destroyed",
            "cudaerrorillegaladdress",
        )
    )
