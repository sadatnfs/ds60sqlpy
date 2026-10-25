"""cuda-059: CPU reference only, not CUDA execution."""

artifacts = {
    "source.cu": "CUDA C++ source",
    "kernel.ptx": "virtual instructions",
    "kernel.cubin": "target machine code",
    "main": "host executable",
}
assert artifacts["kernel.ptx"] != artifacts["kernel.cubin"]
print(artifacts)
