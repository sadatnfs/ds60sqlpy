"""cuda-016: CPU reference only, not CUDA execution."""

bytes_per_thread = 1024 * 4
logical_bytes_per_block = bytes_per_thread * 128
assert bytes_per_thread == 4096 and logical_bytes_per_block == 524288
placements = {"image": "global", "cooperative_tile": "shared", "sum": "thread local"}
print({"logical_temporary_bytes": logical_bytes_per_block, "storage_roles": placements})
