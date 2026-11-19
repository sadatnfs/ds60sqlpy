"""torch-025: Contrastive embeddings and negative sampling.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Score a new pair
# Compute the dot product and cosine similarity of [3, 4] and [4, 3].
# Expected: dot 24; cosine 0.96.

# Exercise 2: Predict scores after negation
# Negate the second vector and recompute both scores.
# Expected: dot -24; cosine -0.96.

# Exercise 3: Compute a three-candidate loss
# Use logits [2, 0, 0] with target 0.
# Expected: cross entropy \(\log(1+2e^{-2})\), about 0.2395, within 1e-12.

# Exercise 4: Inspect a projection gradient
# Create a trainable 2-by-2 identity projection and backpropagate the positive-versus-
# negative objective.
# Expected: finite nonzero projection gradient.

# Exercise 5: Detect contradictory candidate identity
# Assign the same document ID to positive and negative roles.
# Expected: identity collision detected.

# Exercise 6: Separate temperature from ranking
# Compare the softmax of logits [1, 0] at temperatures 1 and 0.5.
# Expected: positive probability increases; argmax remains 0.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
