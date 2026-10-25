"""cuda-062: CPU reference only, not CUDA execution."""

capability = {"reading": True, "CPU_reference": True, "CUDA_device_probe": False}
selected = "CUDA" if capability["CUDA_device_probe"] else "CPU_reference"
assert selected == "CPU_reference"
print({"selected_path": selected, "CUDA_execution": "unavailable"})
