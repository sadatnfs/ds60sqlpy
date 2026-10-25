"""Editable CPU worked example. This does not execute or simulate a GPU.

Complete the six guide exercises separately; modify one bounded case at a time.
"""

prepare, compute = 6, 4
serial = prepare + compute
ideal = max(prepare, compute)
queued = 3 * 8 * 1024 * 1024
assert serial == 10 and ideal == 6 and queued == 25165824
print("CPU pipeline model:", serial, ideal, queued)
