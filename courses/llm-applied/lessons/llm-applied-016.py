"""llm-applied-016: Low-rank adaptation: dimensions, gradients and a real update.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Count and orient parameters
# Construct W=I8, A=ones(8, 2)/8, B=zeros(2, 8), rank 2 and alpha 4, then count stored
# entries.
# Expected: 64 base entries, 32 trainable adapter entries and scale 2.

# Exercise 2: Prove zero-delta initialization
# Compare the effective output with the frozen base before any update.
# Expected: Both outputs equal a row of eight ones; the initial update matrix is zero.

# Exercise 3: Inspect the first gradients
# Differentiate the mean squared output against a zero target and inspect both factor
# gradients.
# Expected: A has a connected zero gradient; every B-gradient entry is 0.5; W has no accumulated gradient.

# Exercise 4: Take an adapter-only step
# Take one SGD step of size 0.1 on A and B and derive the updated output and objective.
# Expected: B entries become -0.05, outputs become 0.8 and mean squared loss becomes 0.64; W stays exactly unchanged.

# Exercise 5: Merge without changing the base
# Create a detached merged matrix without mutating W and compare its predictions.
# Expected: Merged/unmerged parity within 1e-6; original W remains exactly unchanged.

# Exercise 6: Inspect rank and scaling consequences
# Measure the update rank after this symmetric first step and compare alpha 4 with alpha 2
# using the same factors.
# Expected: The actual update has rank 1, within the configured bound 2; alpha 4 gives twice the alpha-2 delta.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
