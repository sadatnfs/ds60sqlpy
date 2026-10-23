"""llm-026: What a representation probe establishes.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Construct transparent representations
# Use features[-2,0],[-1,1],[1,0],[2,1] and labels0,0,1,1.
# Expected: first-coordinate sign predicts all four labels.

# Exercise 2: Use a held-out fixture
# Evaluate the same fixed threshold on new representations[-3,1],[3,0].
# Expected: two correct held-out predictions.

# Exercise 3: Add shuffled-label control
# Compare predictions against shuffled labels0,1,0,1.
# Expected: 2 of4 correct.

# Exercise 4: Protect frozen state
# Clone features, compute a probe loss using a separate trainable weight, and inspect
# gradients.
# Expected: probe gradient exists; features have no gradient.

# Exercise 5: Expose family leakage
# Mark rows0 and1 as versions of familyA and place them on opposite sides of a split.
# Expected: familyA crosses partitions.

# Exercise 6: Bound the interpretation
# Write a result with heldout_count2,control_accuracy.5 and causal_use_establishedFalse.
# Expected: report distinguishes decodability from causal use.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
