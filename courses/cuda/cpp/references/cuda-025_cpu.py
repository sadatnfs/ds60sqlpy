"""cuda-025: CPU reference only, not CUDA execution."""

failures = {
    "unknown identifier": "compile",
    "undefined reference": "link",
    "illegal access at completion": "execute",
    "wrong sum": "validate",
}
assert failures["wrong sum"] == "validate"
assert failures["unknown identifier"] != failures["illegal access at completion"]
print(failures)
