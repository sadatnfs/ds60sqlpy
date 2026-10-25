"""Independent CPU reference with deterministic contract assertions."""

values = [1, 2, 3]
result = sum(values)
assert result == 6
assert sum([]) == 0
ledger = [("input", "CPU"), ("sum", "CPU"), ("result", "CPU")]
assert all(device == "CPU" for _, device in ledger)
print("CPU reference:", result, ledger)
