"""tf-005: predict from the companion guide, then modify an owned copy."""

import math


def f(w):
    return (w - 2) ** 2


w, h = 0.0, 0.01
central = (f(w + h) - f(w - h)) / (2 * h)
assert math.isclose(central, -4.0, rel_tol=0, abs_tol=1e-10)
updated = w - 0.1 * central
assert math.isclose(updated, 0.4, rel_tol=0, abs_tol=1e-12)
print(central, updated, f(updated))

h = 0.01
left_slope = (abs(0.0) - abs(-h)) / h
right_slope = (abs(h) - abs(0.0)) / h
central = (abs(h) - abs(-h)) / (2 * h)
assert (left_slope, right_slope, central) == (-1.0, 1.0, 0.0)
print(left_slope, right_slope, central)

# Exercise 1: Label slope and state
# For f(w)=(w-2)^2 at zero, derive the loss, derivative and a rate-0.1 update.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 2: Construct central probes
# Implement central_difference(function,point,h) and evaluate h=0.1,0.01,0.001 on the
# quadratic at zero.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 3: Expose a one-sided bias
# Compute the forward difference (f(h)-f(0))/h for the same three h values.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 4: Move from the other side
# At w=3, derive the derivative and apply rate 0.1.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 5: Diagnose an invalid derivative claim
# Use abs(w) at zero and inspect left, right and central probes; also test h=0 and a NaN
# point.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 6: Transfer to a scaled objective
# For g(w)=3*(w-1)^2 at w=2, derive a gradient and one rate-0.1 step.
# Add your attempt and keep its observed values or exception beside your prediction.
