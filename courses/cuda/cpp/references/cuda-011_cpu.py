"""cuda-011: CPU reference only, not CUDA execution."""

stages = ["source", "host/device compilation", "link", "load", "execute", "validate"]
assert stages.index("link") < stages.index("execute")
assert stages.index("execute") < stages.index("validate")
print(" -> ".join(stages))
