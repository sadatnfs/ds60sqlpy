"""Editable CPU worked example. This does not execute or simulate a GPU.

Complete the six guide exercises separately; modify one bounded case at a time.
"""

x, y = [1.0, 2.0], [2.0, 4.0]
w = 0.0
loss = sum((w * a - b) ** 2 for a, b in zip(x, y, strict=True)) / len(x)
grad = sum(2 * a * (w * a - b) for a, b in zip(x, y, strict=True)) / len(x)
w -= 0.1 * grad
assert loss == 10 and grad == -10 and w == 1
print("CPU training oracle:", loss, grad, w)
