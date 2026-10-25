"""cuda-030: CPU reference only, not CUDA execution."""


def invalid_indices(n):
    return [i for i in range(n + 1) if not 0 <= i < n]


assert invalid_indices(1) == [1]
assert invalid_indices(33) == [33]
receipt = {"submitted": True, "completed": False, "validated": False}
assert not receipt["validated"]
print({"minimal_bounds_case": invalid_indices(1), "timeout_receipt": receipt})
