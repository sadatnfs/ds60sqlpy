"""torch-027: Transfer learning, frozen layers and optimizer membership.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Freeze a scaling base
# Create a bias-free 2-to-2 base whose weight is 2 times the identity, freeze it and
# evaluate the row [1, 2].
# Expected: output [[2, 4]]; the base weight does not require gradients.

# Exercise 2: Predict the head update
# Attach a zero-initialized bias-free 2-to-1 head, take one SGD step with learning rate
# 0.1 toward target 1 using mean squared error.
# Expected: head weight [0.4, 0.8]; the base receives no gradient.

# Exercise 3: Count trainable parameters
# Count the scalars that still require gradients across the frozen base and the new head.
# Expected: 2 trainable scalars, all in the head.

# Exercise 4: Expose buffer updates despite freezing
# Freeze BatchNorm affine parameters but call it in train mode on a nonzero batch.
# Expected: running mean changes.

# Exercise 5: Freeze normalization behavior with eval
# Switch that BatchNorm to eval and call a different batch.
# Expected: running mean remains unchanged.

# Exercise 6: Begin an explicit unfreeze phase
# Enable base gradients, create a new optimizer over base+head, and take one smaller-rate
# step.
# Expected: base weight now changes.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
