"""tf-027: Transfer learning without a model download.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Construct the local base
# Create a fixed two-feature identity Dense base and freeze it.
# Expected: base output equals input; no trainable base variables.

# Exercise 2: Train a new head
# Attach a zero-initialized one-unit head; fit targets[1,2,3] for one SGD step.
# Expected: at least one head coefficient changes.

# Exercise 3: Prove base preservation
# Compare the base kernel with identity after head training.
# Expected: base weights remain byte-identical to identity.

# Exercise 4: Compare predictions
# Evaluate the new head on all three local records and compare with initial zero
# predictions.
# Expected: all three predictions positive.

# Exercise 5: Begin an explicit unfreeze phase
# Unfreeze the base and initialize a new SGD optimizer; differentiate a combined loss.
# Expected: both base and head now have connected gradients.

# Exercise 6: Detect changed base state
# Compare the unfrozen base with its original identity after the explicit update.
# Expected: base is no longer identical.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
