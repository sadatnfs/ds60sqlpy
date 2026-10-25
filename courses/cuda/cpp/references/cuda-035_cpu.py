"""cuda-035: CPU reference only, not CUDA execution."""

banks_plain = [(row * 32) % 32 for row in range(32)]
banks_padded = [(row * 33) % 32 for row in range(32)]
assert len(set(banks_plain)) == 1 and len(set(banks_padded)) == 32
matrix = [[1, 2, 3], [4, 5, 6]]
assert list(map(list, zip(*matrix))) == [[1, 4], [2, 5], [3, 6]]
print({"model_unique_banks": [len(set(banks_plain)), len(set(banks_padded))]})
