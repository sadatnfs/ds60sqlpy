"""Independent CPU reference with deterministic contract assertions."""

rows, cols, rank = 1024, 1024, 8
base = rows * cols
adapter = rank * (rows + cols)
assert base == 1048576 and adapter == 16384
assert base + adapter > base
print("CPU adapter ledger:", base, adapter, "parameters")
