"""llm-047: Sparse experts, routing capacity and load balancing.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Calculate a top-2 expert mixture
# Use experts I, 2I, -I and three token/router rows with selected probabilities 3/4 and
# 1/4.
# Expected: outputs [1.25, 0], [0, 1.75], [-0.25, -0.25].

# Exercise 2: Enforce expert capacity with residual fallback
# Route four tokens to experts 0, 0, 1, 0 with capacity 2 and unit top-1 gates.
# Expected: assigned counts 3, 1; accepted 2, 1; last token drops its expert delta and keeps its input.

# Exercise 3: Compute a load-balancing term
# Use hard fractions f = [0.75, 0.25], mean router probabilities P = [0.7, 0.3], expert
# count 2 and coefficient 0.01.
# Expected: auxiliary loss .012; balanced fixture .01.

# Exercise 4: Trace a local router gradient
# Perturb the first logit of the first top-2 mixture row without changing selected
# experts.
# Expected: derivative of first output coordinate is -3/16 within1e-8.

# Exercise 5: Separate total and active parameter counts
# Use 8 two-layer experts with width 64, hidden width 128 and top-2 activation, excluding
# router and biases.
# Expected: total 131072 expert weights; 32768selectedexpertweights per token.

# Exercise 6: Validate routing policy and ties
# Reject top-k 0 and capacity 0; check that equal router logits choose lower indices
# deterministically.
# Expected: invalid policies raise ValueError; top-2 tie indices 0, 1.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
