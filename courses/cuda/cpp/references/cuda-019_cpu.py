"""cuda-019: CPU reference only, not CUDA execution."""

k, tile = 5, 2
phases = [(start, min(start + tile, k)) for start in range(0, k, tile)]
assert phases == [(0, 2), (2, 4), (4, 5)]
assert 2 * 16 * 16 * 4 == 2048
print({"phases": phases, "two_tiles_bytes": 2048})
