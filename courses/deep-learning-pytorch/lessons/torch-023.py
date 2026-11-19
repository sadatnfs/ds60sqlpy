"""torch-023: Debugging custom loops, accumulation and clipping.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Detect a detached intermediate
# With Parameter w=1, compute h=(3w).detach() and loss=(h-1)**2, then inspect tracking and
# attempt backward.
# Expected: loss.requires_grad is False and backward raises RuntimeError.

# Exercise 2: Trace two updates on a new target
# Train w from 0 on x = 1, 2, 3 with y = 3x, two SGD steps with learning rate 0.1,
# clearing gradients before each.
# Expected: weights 2.8 then 224/75.

# Exercise 3: Clip a new gradient
# Assign gradient [6, 8] to a parameter vector and clip it to norm 5.
# Expected: returned norm 10; clipped gradient approximately [3, 4].

# Exercise 4: Apply the clipped update
# Use SGD with rate 0.1 after clipping and inspect the parameter.
# Expected: approximately -0.06, -0.08.

# Exercise 5: Reject nonfinite gradient norms
# Assign an infinite gradient and request error_if_nonfinite True.
# Expected: RuntimeError before a valid update.

# Exercise 6: Recompute post-update loss
# Calculate current loss after the two scalar updates and compare with the one-step
# oracle.
# Expected: nonnegative and below 56/675.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
