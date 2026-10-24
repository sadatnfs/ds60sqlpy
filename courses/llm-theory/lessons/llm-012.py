"""llm-012: Greedy decoding, temperature and sampling.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Calculate greedy choice
# Use scores[2,1,0] and choose the maximum index.
# Expected: token0.

# Exercise 2: Change temperature
# Compare probabilities at temperatures1 and.5 using stable softmax.
# Expected: token0 probability increases; argmax stays0.

# Exercise 3: Use fixed draws
# Sample from probabilities[.5,.3,.2] with draws.1,.6,.9.
# Expected: tokens0,1,2.

# Exercise 4: Retain two candidates
# Apply top-k2 to scores[2,1,0] and normalize only retained candidates.
# Expected: token2 probability0; first two sum1.

# Exercise 5: Declare ties
# Use equal scores[1,1,0] and choose the smallest-index maximum.
# Expected: token0 under the stated rule.

# Exercise 6: Reject invalid draws
# Validate draws0,.999,1 and-.1 before cumulative lookup.
# Expected: 0 and.999 accepted;1 and-.1 rejected.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
