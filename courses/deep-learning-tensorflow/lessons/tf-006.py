"""tf-006: predict from the companion guide, then modify an owned copy."""

w = 1.0
z = 2 * w
a = z * z
loss = (a - 1) ** 2
gradient = (2 * (a - 1)) * (2 * z) * 2
assert (z, a, loss, gradient) == (2.0, 4.0, 9.0, 48.0)
print(z, a, loss, gradient)


def full(value):
    return ((2 * value) ** 2 - 1) ** 2


frozen_a = 4.0


def frozen(value):
    return (frozen_a - 1) ** 2


h = 1e-5
full_slope = (full(1 + h) - full(1 - h)) / (2 * h)
frozen_slope = (frozen(1 + h) - frozen(1 - h)) / (2 * h)
assert abs(full_slope - 48) < 1e-7
assert frozen_slope == 0.0
print(full_slope, frozen_slope)

# Exercise 1: Build a forward/backward table
# Trace z, a, loss and all three derivative factors at w=1 for inner scale 2.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 2: Change one inner operation
# Change z=2*w to z=3*w and keep the rest of the composition fixed at w=1.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 3: Construct an independent probe
# Implement chain_trace(weight,scale) and compare the scale-2 gradient with a central
# probe using h=1e-5.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 4: State the activation boundary
# Write ReLU values/slopes at -1 and +1. At zero, distinguish one-sided slopes from a
# chosen zero convention.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 5: Diagnose a disconnected calculation
# Freeze a=4 outside a function of w, compare its loss and slope at one with the fully
# recomputed path.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 6: Find a missing factor
# A proposed backward pass multiplies only dL/da and da/dz, omitting dz/dw. Diagnose it
# for scales 2 and 3.
# Add your attempt and keep its observed values or exception beside your prediction.
