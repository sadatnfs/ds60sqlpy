"""Editable CPU worked example. This does not execute or simulate a GPU.

Complete the six guide exercises separately; modify one bounded case at a time.
"""

operations, bytes_moved = 4096, 8192
intensity = operations / bytes_moved
intermediate = 1024 * 4
saved = 2 * intermediate
assert intensity == 0.5 and saved == 8192
print("CPU roofline inputs:", intensity, "operations/byte; removable traffic", saved)
