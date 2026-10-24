"""llm-003: predict from the companion guide, then modify an owned copy."""

import math

probabilities = [0.5, 0.25, 0.8]
likelihood = math.prod(probabilities)
nll = -sum(math.log(p) for p in probabilities)
assert math.isclose(likelihood, 0.1, rel_tol=0, abs_tol=1e-12)
assert math.isclose(nll, math.log(10), rel_tol=0, abs_tol=1e-12)
print(likelihood, nll)

probabilities = [0.01] * 1000
likelihood = math.prod(probabilities)
nll = -sum(math.log(p) for p in probabilities)
assert likelihood == 0.0
assert math.isfinite(nll)
assert math.isclose(nll, 1000 * math.log(100), rel_tol=0, abs_tol=1e-9)
print(likelihood, nll)

# Exercise 1: Trace the fixed conditionals
# Derive the product, total negative log likelihood and scored-target count for
# [0.5,0.25,0.8].
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 2: Change the conditioning assumption
# Compare the supplied table with [0.5,0.5,0.5], which incorrectly reuses one
# unconditional frequency for all positions.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 3: Preserve a long log score
# Implement sequence_score(probabilities) and test 1000 copies of 0.01 without summing
# logs of an already multiplied product.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 4: Handle certain and impossible targets
# Score [1,1] and [0.5,0]. Do not replace zero with an undisclosed epsilon.
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 5: Reject invalid probabilities
# Test an empty list, [-0.1], [1.1] and [NaN].
# Add your attempt and keep its observed values or exception beside your prediction.

# Exercise 6: Declare an aggregation unit
# Document A has target probabilities [0.5]; document B has [0.25,0.25,0.25]. Compare
# token-weighted mean NLL and equal-document mean NLL.
# Add your attempt and keep its observed values or exception beside your prediction.
