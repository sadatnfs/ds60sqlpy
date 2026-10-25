"""Independent CPU reference with deterministic contract assertions."""


def f(x):
    return max(0.0, 2 * x + 1)


x, eps = 2.0, 1e-5
numeric = (f(x + eps) - f(x - eps)) / (2 * eps)
assert abs(numeric - 2.0) < 1e-8
upstream = [1, 3]
mask = [0, 1]
bias_grad = sum(g * m for g, m in zip(upstream, mask, strict=True))
assert bias_grad == 3
print("CPU gradient oracle:", numeric, bias_grad)
