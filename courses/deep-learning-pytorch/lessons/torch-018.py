"""torch-018: BatchNorm, LayerNorm and stateful normalization.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Update a running mean
# Apply BatchNorm momentum.5 to rows1, 3 and3, 5.
# Expected: running mean1, 2; batch counter1.

# Exercise 2: Freeze state during evaluation
# Call the trained layer in eval mode on100, 200.
# Expected: running mean and batch counter unchanged.

# Exercise 3: Check LayerNorm row independence
# Normalize1, 3alone and beside100, 200.
# Expected: first row matches within1e-6.

# Exercise 4: Inspect running variance convention
# From initial running variance1, use batch values1, 3whose unbiased variance is2 and
# momentum.5.
# Expected: running variance1.5 for each feature.

# Exercise 5: Translate momentum explicitly
# Compute updates with old mean0, batch mean10 and PyTorch momentum.1versus Keras
# momentum.1.
# Expected: PyTorch1; Keras9 under their respective conventions.

# Exercise 6: Handle a constant feature row
# Apply LayerNorm to5, 5 and inspect finiteness.
# Expected: finite zeros with default affine initialization.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
