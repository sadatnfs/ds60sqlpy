"""llm-012: Greedy decoding, temperature and sampling.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Predict a hotter distribution
# Use scores [0.5, 3, 3.5, -1]. Name the greedy token, then predict how temperature 2
# changes the probabilities of the top and bottom tokens.
# Expected: greedy token 2; at temperature 2 its probability falls, token 3 gains mass and the argmax stays 2.

# Exercise 2: Compute an exact two-token probability
# For scores [1, 0], compute the probability of token 0 at temperatures 1 and 0.5 and
# compare it with the logistic function.
# Expected: token 0 probability \(1/(1+e^{-1})\approx 0.731\) at temperature 1 and \(1/(1+e^{-2})\approx 0.881\) at temperature 0.5.

# Exercise 3: Use fixed draws
# Sample from probabilities [0.5, 0.3, 0.2] with draws 0.1, 0.6, 0.9.
# Expected: tokens 0, 1, 2.

# Exercise 4: Retain two candidates
# Apply top-k2 to scores [2, 1, 0] and normalize only retained candidates.
# Expected: token 2 probability 0; first two sum 1.

# Exercise 5: Declare ties
# Use equal scores [1, 1, 0] and choose the smallest-index maximum.
# Expected: token 0 under the stated rule.

# Exercise 6: Reject invalid draws
# Validate draws 0, 0.999, 1 and -0.1 before cumulative lookup.
# Expected: 0 and 0.999 accepted; 1 and -0.1 rejected.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
