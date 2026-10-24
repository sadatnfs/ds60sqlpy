"""llm-028: Capstone: train and audit a tiny transformer.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Freeze corpus identity
# Use train sequences[1,2,3,4],[1,2,4,3] and holdout[1,3,2,4] with distinct document IDs.
# Expected: train2 documents;holdout1;context3.

# Exercise 2: Train a bounded decoder
# Initialize seed11 and train20 Adam(.01) updates on the two training sequences.
# Expected: 20 finite losses;parameter count below50000.

# Exercise 3: Fit the count baseline
# Build16x16 transition counts from training documents and add-one smooth each row.
# Expected: total6 observed transitions; every row sums1.

# Exercise 4: Score one frozen holdout
# Compute both mean losses on the three held-out target events.
# Expected: both finite; denominator3; no required winner.

# Exercise 5: Retest causality after training
# Compare the first two logits from the full holdout input with an independent two-token
# prefix.
# Expected: prefix agreement within1e-6.

# Exercise 6: Record model identity and limits
# Hash ordered parameter bytes and build a report with3 held-out targets,20 updates and
# the split hash.
# Expected: two64-character hashes and explicit tiny-corpus limitation.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
