"""tf-025: Embedding objectives and negative examples.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Compare similarity measures
# Use anchor[1,0],positive[1,1],negative[0,1]; compute dots and cosines.
# Expected: dots1,0; cosines1/sqrt2,0.

# Exercise 2: Scale a candidate
# Multiply the positive vector by10 and compare dot product and cosine.
# Expected: dot10; cosine unchanged.

# Exercise 3: Calculate a contrastive loss
# Use logits[1,0] with the positive at index0.
# Expected: losslog(1+exp(-1)).

# Exercise 4: Detect a false negative
# Replace the negative vector and identity with the positive identity.
# Expected: duplicate positive/negative identity is flagged.

# Exercise 5: Observe temperature
# Compare softmax[1,0] at temperatures1 and.5.
# Expected: positive probability increases at.5; ranking stays0 first.

# Exercise 6: Reject undefined cosine
# Implement cosine with finite and nonzero-norm checks; pass a zero anchor.
# Expected: ValueError for zero norm.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
