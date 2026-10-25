"""cuda-026: CPU reference only, not CUDA execution."""

n = 4
indices = list(range(5))
invalid = [i for i in indices if not 0 <= i < n]
assert invalid == [4]
checker = {
    "out_of_bounds": "memcheck",
    "shared_hazard": "racecheck",
    "uninitialized": "initcheck",
    "invalid_barrier": "synccheck",
}
print({"CPU_bounds_audit": invalid, "tool_selection": checker})
