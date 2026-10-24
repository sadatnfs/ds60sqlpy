"""torch-024: Capstone: a small classifier with honest evaluation.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Freeze the geometric task
# Use training x-2, -1, 1, 2 with labels 0, 0, 1, 1 and test x-3, 3.
# Expected: 4training records, 2test records.

# Exercise 2: Fit explicit normalization
# Calculate training mean and population standard deviation.
# Expected: mean 0; scale sqrt 2.5.

# Exercise 3: Train a fixed classifier
# Zero-initialize the weight and run 40 SGD.1 steps with binary logits loss.
# Expected: positive finite weight after 40 updates.

# Exercise 4: Account for every test prediction
# Threshold test logits at 0 and calculate confusion counts.
# Expected: TP 1, TN 1, FP 0, FN 0, total 2.

# Exercise 5: Compare a constant baseline
# Predict class 0 for both test rows and count mistakes.
# Expected: baseline 1 error; model 0 on this fixture.

# Exercise 6: Reveal a group-specific failure
# Flip only the positive group decision and report group counts.
# Expected: negative 0/1errors; positive 1/1.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
