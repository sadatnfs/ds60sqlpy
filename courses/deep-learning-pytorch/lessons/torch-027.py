"""torch-027: Transfer learning, frozen layers and optimizer membership.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Freeze a known base
# Create a bias-free 2-to-2identity Linear base and disable its parameter gradients.
# Expected: base output equals input; all base parameters frozen.

# Exercise 2: Train a new head
# Attach a zero-initialized 2-to-1head and take one SGD.1step toward targets 1, 2, 3.
# Expected: head changes; base remains exact identity.

# Exercise 3: Inspect absent base gradients
# Check the frozen base after head backward.
# Expected: base gradient None; head gradient present.

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
