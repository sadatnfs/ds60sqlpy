"""llm-applied-016: Low-rank adaptation: dimensions, gradients and a real update.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Count and orient parameters
# ConstructW=I8, A=ones(8, 2)/8, B=zeros(2, 8), rank 2, alpha 4.
# Expected: base64 entries; adapter32; scale2.

# Exercise 2: Prove zero-delta initialization
# Compare the effective output with the frozen base before updating.
# Expected: outputs exactly equalones(1, 8).

# Exercise 3: Inspect the first gradients
# Minimize mean squared output towardzero and backpropagate once.
# Expected: A gradientzero; B gradientnonzero; W has no gradient.

# Exercise 4: Take an adapter-only step
# UseSGD.1 onA/B and recalculate the objective.
# Expected: B changes; loss decreases; W remains byte-identical.

# Exercise 5: Merge without changing the base
# Create a detached merged matrix and compare predictions with the unmerged expression.
# Expected: parity within1e-6; originalW unchanged.

# Exercise 6: Inspect rank and scaling consequences
# Check the numerical rank of the update and comparealpha4 withalpha2 using the same
# factors.
# Expected: rank at most2; delta atalpha4 is twice delta atalpha2.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
