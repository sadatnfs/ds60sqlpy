"""torch-018: BatchNorm, LayerNorm and stateful normalization.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Predict a running mean with momentum 0.25
# Apply a fresh BatchNorm1d(2, momentum=0.25) in train mode to rows [2, 4] and [6, 8].
# Expected: batch means [4, 6]; running mean [1, 1.5].

# Exercise 2: Predict the running variance
# Inspect the same layer's running variance after that one update.
# Expected: running variance [2.75, 2.75].

# Exercise 3: Normalize a new LayerNorm row
# Apply a default LayerNorm(3) to the row [1, 2, 3].
# Expected: approximately [-1.2247, 0, 1.2247], equal to \([-1, 0, 1]/\sqrt{2/3+10^{-5}}\) within 1e-5.

# Exercise 4: Inspect running variance convention
# From initial running variance 1, use batch values 1 and 3 (unbiased variance 2) with
# momentum 0.5.
# Expected: running variance 1.5 for each feature.

# Exercise 5: Translate momentum explicitly
# Compute updates with old mean 0, batch mean 10 and PyTorch momentum 0.1 versus Keras
# momentum 0.1.
# Expected: PyTorch 1; Keras 9 under their respective conventions.

# Exercise 6: Handle a constant feature row
# Apply LayerNorm to 5, 5 and inspect finiteness.
# Expected: finite zeros with default affine initialization.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
