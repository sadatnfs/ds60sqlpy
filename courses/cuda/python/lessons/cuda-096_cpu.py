"""Editable CPU worked example. This does not execute or simulate a GPU.

Complete the six guide exercises separately; modify one bounded case at a time.
"""

predictions, targets = [1, 2, 3], [1, 3, 2]
mse = sum((p - t) ** 2 for p, t in zip(predictions, targets, strict=True)) / len(targets)
assert abs(mse - 2 / 3) < 1e-12
report = {"backend": "CPU reference", "examples": len(targets), "mse": mse, "gpu_verified": False}
assert report["examples"] == 3 and not report["gpu_verified"]
print(report)
