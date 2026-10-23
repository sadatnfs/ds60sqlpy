"""torch-007: Leaf tensors, detach, no_grad and gradient accumulation.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Inspect leaf and nonleaf state
# Create leaf w0 and intermediate 2 w, retain the intermediate gradient and backpropagate
# its sum.
# Expected: w leaf True; intermediate False; gradients 2 and 1.

# Exercise 2: Observe accumulation across fresh graphs
# Compute (w-2)**2 twice at w=0 without clearing grad.
# Expected: after resetting first, grad -4 then -8.

# Exercise 3: Clear before an independent step
# Set grad None and backpropagate once more.
# Expected: grad returns to-4.

# Exercise 4: Separate detach from ownership
# Detach a tensor, mutate the detached view, and compare with a detached clone.
# Expected: shared original changes; owned clone stays unchanged.

# Exercise 5: Use no_grad for an observation
# Multiply a requires_grad tensor inside and outside no_grad.
# Expected: tracked result requires_grad True; observed result False.

# Exercise 6: Show eval is separate
# Put a Linear module in eval mode, run a differentiable input, and inspect output
# tracking.
# Expected: output still requires_grad True.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
