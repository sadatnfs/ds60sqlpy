"""cuda-056: CPU reference only, not CUDA execution."""

states = ["free", "copying", "ready", "consuming", "done", "free"]
assert states.index("ready") < states.index("consuming") < states.index("done")
assert 16 % 16 == 0 and (16 + 4) % 16 != 0
print({"slot_lifetime": states, "offset_address_aligned_to_16": False})
