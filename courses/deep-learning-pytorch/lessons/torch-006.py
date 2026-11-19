"""torch-006: Autograd graphs, the chain rule and in-place hazards.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Trace the chain at a new point
# Use w=2, z=2*w, a=z*z and loss=(a-1)**2, and predict each intermediate value and
# dloss/dw.
# Expected: z = 4, a = 16, loss 225, gradient 480.

# Exercise 2: Check the new slope numerically
# Compare 480 with a central difference of ((2w)**2-1)**2 at w=2 using h=1e-5.
# Expected: the central difference agrees with 480 within 1e-6.

# Exercise 3: Update a leaf under no_grad
# Repeat the in-place add on a leaf that requires gradients, but inside torch.no_grad().
# Expected: the update succeeds; the value is 2 and the tensor is still a leaf that requires gradients.

# Exercise 4: Expose saved-value invalidation
# Build loss=x*x, mutate x under no_grad before backward, and inspect the failure.
# Expected: RuntimeError from a changed saved tensor version.

# Exercise 5: Inspect a ReLU convention
# Differentiate ReLU at negative, zero and positive inputs.
# Expected: gradients 0, 0, 1.

# Exercise 6: Recompute after an update
# Update a scalar under no_grad, then build a fresh quadratic objective and request its
# derivative.
# Expected: at new w=1.5, gradient -1 for (w-2)**2.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
