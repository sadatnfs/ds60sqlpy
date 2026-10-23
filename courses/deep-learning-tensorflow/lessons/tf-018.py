"""tf-018: Normalization state and batch dependence.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Update and inspect moving state
# Apply Keras BatchNorm with momentum 0.5 to [[1,3],[3,5]], then use a separate variance-
# four probe.
# Expected: moving mean [1,2]; main variance stays [1,1]; variance-four probe updates moving variance to [2.5,2.5].

# Exercise 2: Freeze evaluation state
# After one training call, evaluate the same batch and compare with the stored-statistic
# formula.
# Expected: moving state stays unchanged; inference output uses mean [1,2] and differs from training output.

# Exercise 3: Test LayerNorm row independence
# Normalize [1,3] alone and as the first row beside [100,200].
# Expected: the first output is unchanged; LayerNorm has no running-statistic variables.

# Exercise 4: Expose actual BatchNorm batch dependence
# Compare the first row of training normalization with and without the added row [98,199].
# Expected: the output changes and matches independent per-channel NumPy mean/variance calculations.

# Exercise 5: Repeat updates and translate asymmetric momentum
# Repeat the 0.5 update, then run a fresh Keras layer with momentum 0.8 and compare
# old/new-weight arithmetic.
# Expected: 0.5 repeat gives [1.5,3]; Keras0.8 first/second means are [0.4,0.8] and [0.72,1.44]; matching Torch new-batch weight is 0.2.

# Exercise 6: Handle constant rows and frozen BatchNorm
# Normalize a constant row, then freeze a trained Keras BatchNorm layer and call it with
# training=True.
# Expected: LayerNorm returns finite zeros; frozen Keras BatchNorm preserves moving state and uses its inference statistics.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
