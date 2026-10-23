"""torch-013: Binary logits, BCEWithLogitsLoss and thresholds.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Convert fixed logits
# Apply sigmoid to-2, 0, 2.
# Expected: middle probability.5 and strictly increasing values.

# Exercise 2: Check the midpoint objective
# Compute positive-label BCE at zero logit.
# Expected: loss log 2 within 1e-12.

# Exercise 3: Move the decision threshold
# Compare thresholds.5 and.8 with>=ties.
# Expected: labels False, True, True versus False, False, True.

# Exercise 4: Expose a double-sigmoid mistake
# Feed probability.5 as though it were a logit and compare with log 2.
# Expected: incorrect loss differs by more than.1.

# Exercise 5: Test extreme finite scores
# Use logits 1000, -1000 with labels 1, 0.
# Expected: finite losses approximately 0.

# Exercise 6: Count threshold errors
# Use truth 0, 1, 1 and compare the two decision policies.
# Expected: 0 errors at.5 and 1 at.8.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
