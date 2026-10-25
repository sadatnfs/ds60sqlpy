"""cuda-036: CPU reference only, not CUDA execution."""

register_file, threads = 65536, 256
blocks = [register_file // (threads * registers) for registers in (64, 128)]
assert blocks == [4, 2]
print({"register_only_block_limits": blocks, "other_hardware_limits_included": False})
