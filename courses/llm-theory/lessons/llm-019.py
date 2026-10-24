"""llm-019: Overfit one batch to diagnose the loop.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Clone the initial state
# Build two identical decoders with seed9 and copy one state into the other.
# Expected: all parameter tensors initially equal.

# Exercise 2: Run a no-update control
# Compute the same loss5 times without backward or step.
# Expected: all losses equal; weights unchanged.

# Exercise 3: Train the repeated batch
# Apply30 Adam(.02) updates to the other model, using the same batch each time.
# Expected: final batch loss below its initial loss.

# Exercise 4: Check the class axis
# Inspect logits before flattening and verify vocabulary dimension16.
# Expected: shape(1,3,16).

# Exercise 5: Verify the control stayed isolated
# Compare control state with its original snapshot after training the other model.
# Expected: every control tensor unchanged.

# Exercise 6: Limit the conclusion
# Write a diagnostic record naming one training sequence and zero held-out sequences.
# Expected: heldout_count0 and generalization_establishedFalse.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
