"""torch-025: Contrastive embeddings and negative sampling.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Compare dot and cosine scores
# Use anchor[1, 0], positive[1, 1], negative[0, 1].
# Expected: dots1, 0; cosines1/sqrt2, 0.

# Exercise 2: Scale without changing direction
# Multiply the positive vector by 10 and compare scores.
# Expected: dot becomes10; cosine unchanged.

# Exercise 3: Calculate a two-candidate loss
# Use logits[1, 0] with target0.
# Expected: cross entropy log(1+exp(-1)).

# Exercise 4: Inspect a projection gradient
# Create a trainable2 x2 identity projection and back propagate the positive-versus-
# negative objective.
# Expected: finite nonzero projection gradient.

# Exercise 5: Detect contradictory candidate identity
# Assign the same document ID to positive and negative roles.
# Expected: identity collision detected.

# Exercise 6: Separate temperature from ranking
# Compare softmax[1, 0] at temperatures1 and.5.
# Expected: positive probability increases; argmax remains0.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
