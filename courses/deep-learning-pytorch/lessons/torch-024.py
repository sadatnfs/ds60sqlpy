"""torch-024: Capstone: a small classifier with honest evaluation.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Fit normalization on new training values
# Use training inputs 0, 2, 4, 6, compute the mean and population standard deviation, and
# transform the test input 8.
# Expected: mean 3; scale \(\sqrt{5}\); transformed test value \(\sqrt{5}\), about 2.2361.

# Exercise 2: Count a new confusion table
# Compare predictions True, False, True, True with truth True, False, False, True.
# Expected: TP 2, TN 1, FP 1, FN 0.

# Exercise 3: Classify with a fixed weight
# With weight 2 and no bias, classify the normalized inputs -1.5, -0.2, 0 and 0.4 at logit
# 0, counting 0 as positive.
# Expected: False, False, True, True.

# Exercise 4: Account for every test prediction
# Threshold test logits at 0 and calculate confusion counts.
# Expected: TP 1, TN 1, FP 0, FN 0, total 2.

# Exercise 5: Compare a constant baseline
# Predict class 0 for both test rows and count mistakes.
# Expected: baseline 1 error; model 0 on this fixture.

# Exercise 6: Reveal a group-specific failure
# Flip only the positive group decision and report group counts.
# Expected: negative class: 0 of 1 wrong; positive class: 1 of 1 wrong.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
