"""torch-023: Debugging custom loops, accumulation and clipping.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Expose detachment
# Detach (w-2)**2 before backward and inspect tracking.
# Expected: detached loss requires_grad False; backward raises RuntimeError.

# Exercise 2: Repair two exact updates
# Usex 1, 2, 3, y2x, w0 and two SGD.1 steps with gradient clearing.
# Expected: weights 28/15 then 448/225.

# Exercise 3: Inspect norm clipping
# Assign gradient 3, 4 to a parameter vector and clip to norm 1.
# Expected: returned norm 5; new gradient approximately.6, .8.

# Exercise 4: Apply the clipped update
# Use SGD.1 after clipping and inspect the parameter.
# Expected: approximately-.06, -.08.

# Exercise 5: Reject nonfinite gradient norms
# Assign an infinite gradient and request error_if_nonfinite True.
# Expected: RuntimeError before a valid update.

# Exercise 6: Recompute post-update loss
# Calculate current loss after the two scalar updates and compare with the one-step
# oracle.
# Expected: nonnegative and below 56/675.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
