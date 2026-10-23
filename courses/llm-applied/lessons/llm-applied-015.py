"""llm-applied-015: Full supervised fine-tuning of a tiny causal decoder.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Build an explicit SFT batch
# Use sequences[1, 2, 5, 3] and[1, 4, 6, 3], masking the first shifted target.
# Expected: inputs shape(2, 3); labels[[-100, 5, 3], [-100, 6, 3]]; 4 active targets.

# Exercise 2: Measure the initial state
# Calculate initial training loss and a held-out prompt loss before any update; count
# trainable parameters.
# Expected: both losses finite; all model parameters trainable; count below50000.

# Exercise 3: Perform actual full fine-tuning
# Run20 Adam updates atlearningrate.01, clearing gradients each time.
# Expected: 20 finite losses; training loss decreases; an embedding parameter changes.

# Exercise 4: Inspect the mask derivative
# Differentiate cross entropy with respect to fresh zero logits under the samelabels.
# Expected: ignored prompt positions have zero gradient; answer positions do not.

# Exercise 5: Evaluate the frozen held-out prompt
# After the declared20 updates, evaluate the held-out sequence without another optimizer
# step.
# Expected: finite held-out loss and unchanged weights during evaluation; no promised improvement.

# Exercise 6: Write an honest adaptation receipt
# Record update count, active training targets, train/heldout losses and the literal-token
# limitation.
# Expected: receipt says20 updates, 4 active training targets and no natural-language competence claim.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
