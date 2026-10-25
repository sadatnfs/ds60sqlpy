"""cuda-064: CPU reference only, not CUDA execution."""

x, a, b = [-1.0, 0.0, 2.0], 3.0, 1.0
forward = [a * value + b for value in x]
assert forward == [-2.0, 1.0, 7.0]


def loss(values):
    return sum(a * value + b for value in values)


epsilon = 1e-5
gradients = []
for i in range(len(x)):
    plus, minus = x.copy(), x.copy()
    plus[i] += epsilon
    minus[i] -= epsilon
    gradients.append((loss(plus) - loss(minus)) / (2 * epsilon))
assert all(abs(g - a) < 1e-8 for g in gradients)
print({"forward": forward, "CPU_finite_difference_gradients": gradients})
