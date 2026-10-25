"""Independent CPU reference with deterministic contract assertions."""

size = 4096
iterations = 10
round_trip = 2 * size * iterations
resident = 2 * size
assert round_trip == 81920
assert resident == 8192
latency = 10e-6
bandwidth = 1e9
many = 100 * (latency + 40 / bandwidth)
one = latency + 4000 / bandwidth
assert many > one
print("CPU cost model:", round_trip, resident, "bytes")
