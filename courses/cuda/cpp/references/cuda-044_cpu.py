"""cuda-044: CPU reference only, not CUDA execution."""

states = ["free", "filling", "computing", "copying", "consumed", "free"]
assert states.index("computing") < states.index("consumed")
chunks = [[1, 2], [3], [], [4, 5]]
results = [[2 * x for x in chunk] for chunk in chunks]
assert results == [[2, 4], [6], [], [8, 10]]
print({"reference_results": results, "slot_lifecycle": states})
