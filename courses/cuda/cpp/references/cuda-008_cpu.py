"""cuda-008: CPU reference only, not CUDA execution."""

x, y = [0, -2, 5], [3, 2, -1]
assert [a + b for a, b in zip(x, y)] == [3, 0, 4]
assert 3 * 1_000_000 * 4 == 12_000_000
receipt = {"surface": "CPU reference", "shape": [3], "result": [3, 0, 4], "gpu_executed": False}
print(receipt)
