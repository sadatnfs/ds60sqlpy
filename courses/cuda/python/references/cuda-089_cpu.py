"""Independent CPU reference with deterministic contract assertions."""

params = 1000
state_bytes = params * 4 * 4
activations = 8 * 128 * 4
assert state_bytes == 16000 and activations == 4096
assert state_bytes + 2 * activations == 24192
print("CPU memory ledger:", state_bytes, activations)
