"""Editable CPU worked example. This does not execute or simulate a GPU.

Complete the six guide exercises separately; modify one bounded case at a time.
"""

w, v = 1.0, 0.5
checkpoint = {"w": w, "v": v, "next_batch": 3}
grad = 0.2
continued = checkpoint["w"] - 0.1 * (0.9 * checkpoint["v"] + grad)
weights_only = w - 0.1 * grad
assert abs(continued - 0.935) < 1e-12
assert continued != weights_only
print("CPU restart model:", continued, weights_only)
