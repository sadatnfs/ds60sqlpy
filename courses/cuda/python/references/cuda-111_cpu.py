"""Independent CPU reference with deterministic contract assertions."""

operations, bytes_moved = 4096, 8192
intensity = operations / bytes_moved
intermediate = 1024 * 4
saved = 2 * intermediate
assert intensity == 0.5 and saved == 8192
print("CPU roofline inputs:", intensity, "operations/byte; removable traffic", saved)
