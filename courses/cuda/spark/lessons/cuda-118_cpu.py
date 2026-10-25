"""Editable CPU worked example. This does not execute or simulate a GPU.

Complete the six guide exercises separately; modify one bounded case at a time.
"""

rows, itemsize = 1000, 8
payload = rows * itemsize
mask = (9 + 7) // 8
assert payload == 8000 and mask == 2
strings = ["a", "longer", ""]
assert sum(len(s.encode("utf-8")) for s in strings) == 7
print("CPU columnar ledger:", payload, mask, 7)
