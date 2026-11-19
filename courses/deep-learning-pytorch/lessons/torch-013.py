"""torch-013: Binary logits, BCEWithLogitsLoss and thresholds.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Convert new logits
# Apply sigmoid to the float64 logits -1, 1 and 3.
# Expected: probabilities about 0.2689, 0.7311 and 0.9526; the first two sum to 1.

# Exercise 2: Compute a negative-label loss
# Compute BCEWithLogitsLoss for logit 2 with label 0.
# Expected: loss \(\log(1+e^{2})\), about 2.1269, within 1e-12.

# Exercise 3: Threshold the new probabilities
# Classify the new probabilities at thresholds 0.5 and 0.75, counting a probability equal
# to the threshold as positive.
# Expected: labels False, True, True versus False, False, True.

# Exercise 4: Expose a double-sigmoid mistake
# Feed probability 0.5 as though it were a logit and compare with log 2.
# Expected: incorrect loss differs by more than 0.1.

# Exercise 5: Test extreme finite scores
# Use logits 1000, -1000 with labels 1, 0.
# Expected: finite losses approximately 0.

# Exercise 6: Count threshold errors
# Use truth 0, 1, 1 and compare the two decision policies.
# Expected: 0 errors at 0.5 and 1 at 0.8.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
