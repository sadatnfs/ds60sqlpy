"""Editable CPU worked example. This does not execute or simulate a GPU.

Complete the six guide exercises separately; modify one bounded case at a time.
"""

rows, cols, rank = 1024, 1024, 8
base = rows * cols
adapter = rank * (rows + cols)
assert base == 1048576 and adapter == 16384
assert base + adapter > base
print("CPU adapter ledger:", base, adapter, "parameters")
