"""tf-013: Binary logits, probabilities and thresholds.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Convert scores
# Convert logits [-2, 0, 2] into probabilities and inspect the central value.
# Expected: middle probability 0.5; probabilities increase.

# Exercise 2: Check the midpoint loss
# Calculate positive-label binary cross entropy at zero logit.
# Expected: loss log(2) within 1e-6.

# Exercise 3: Move the threshold
# Compare decisions at thresholds 0.5 and 0.8, counting a probability equal to the
# threshold as positive.
# Expected: decisions [False, True, True] versus [False, False, True].

# Exercise 4: Expose a convention mismatch
# Treat probability 0.5 as if it were a logit and compare the positive-label loss with log
# 2.
# Expected: wrong loss differs from log 2 by more than 0.1.

# Exercise 5: Stress large scores
# Calculate losses for logits 1000, -1000 with labels 1, 0 using the logits-aware form.
# Expected: both finite losses approximately 0.

# Exercise 6: Count decisions separately
# For labels [0, 1, 1], count errors under the two thresholds.
# Expected: 0 errors at 0.5 and 1 at 0.8 on this fixture.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
