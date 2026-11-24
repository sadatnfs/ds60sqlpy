"""llm-applied-020: Fine-tuning embeddings and a small reranker.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Construct paired retrieval features
# Use queries and documents equal to the 2x2 identity matrix, with positive labels 0, 1.
# Expected: score shape (2, 2); one positive per query.

# Exercise 2: Train the query projection
# Run 30 SGD updates at learning rate 0.5 on cross entropy against diagonal positives.
# Expected: loss decreases; each query ranks its paired document first.

# Exercise 3: Evaluate a perturbed held-out query
# Use held-out feature [.9, .1] and compare its two document scores.
# Expected: document 0 remains higher on this declared local perturbation.

# Exercise 4: Train a pairwise reranker
# Use positive feature [1, 0], negative [0, 1] and a zero linear weight; run 20 SGD updates at learning rate 0.2.
# Expected: positive score exceeds negative and pairwise loss decreases.

# Exercise 5: Detect a false-negative identity
# Assign the same document ID to positive and negative roles and identify the collision as
# a prospective admission failure.
# Expected: identity collision detected; this check is separate from the earlier training loops.

# Exercise 6: Bound the model claim
# Record that fixed vectors were used and natural-language encoder quality was not
# measured.
# Expected: actual gradient updates True; pretrained_semantic_encoder False.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
