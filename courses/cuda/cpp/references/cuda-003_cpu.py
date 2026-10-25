"""cuda-003: CPU reference only, not CUDA execution."""

checks = {"compiler": True, "device_visible": False, "kernel_validated": False}
assert checks["compiler"] and not checks["kernel_validated"]
print("Compilation evidence only; no GPU execution evidence.")
