"""Editable CPU worked example. This does not execute or simulate a GPU.

Complete the six guide exercises separately; modify one bounded case at a time.
"""

values = [1, 2, 3]
result = sum(values)
assert result == 6
assert sum([]) == 0
ledger = [("input", "CPU"), ("sum", "CPU"), ("result", "CPU")]
assert all(device == "CPU" for _, device in ledger)
print("CPU reference:", result, ledger)
