"""torch-007: Leaf tensors, detach, no_grad and gradient accumulation.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Predict a nonleaf gradient
# Create leaf v=1.0 and intermediate u=3v, retain u's gradient and backpropagate u*u.
# Expected: u.grad is 6 and v.grad is 18; u is not a leaf.

# Exercise 2: Accumulate three backward calls
# At w=1, backpropagate (w-2)**2 three times without clearing the gradient.
# Expected: each call contributes -2, so the stored gradient is -6.

# Exercise 3: Clear with zero_ and with None
# Clear the accumulated gradient with p.grad.zero_() and backpropagate once, then set it
# to None and backpropagate once more.
# Expected: both routes end at -2; after the None assignment the gradient is absent until the next backward.

# Exercise 4: Separate detach from ownership
# Detach a tensor, mutate the detached view, and compare with a detached clone.
# Expected: shared original changes; owned clone stays unchanged.

# Exercise 5: Use no_grad for an observation
# Multiply a requires_grad tensor inside and outside no_grad.
# Expected: tracked result requires_grad True; observed result False.

# Exercise 6: Show eval is separate
# Put a Linear module in eval mode, run a differentiable input, and inspect output
# tracking.
# Expected: the output still has `requires_grad=True`.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
