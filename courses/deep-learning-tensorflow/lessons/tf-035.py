"""tf-035: Comparing models with uncertainty.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Align by identity
# Use trutha0,b1,c2 and two prediction dictionaries with different insertion order.
# Expected: paired differences[-1,0,-1].

# Exercise 2: Calculate the mean difference
# Average the three paired loss differences and interpret its sign.
# Expected: mean-2/3; modelA has lower MSE on this fixture.

# Exercise 3: Resample paired units
# Draw1000 bootstrap index rows with seed7 and average each selected difference vector.
# Expected: 1000 finite estimates within[-1,0].

# Exercise 4: Reproduce the resampling
# Repeat with a fresh seed7 generator and compare the entire estimate vector.
# Expected: exact same estimates.

# Exercise 5: Refuse mismatched IDs
# Remove predictionc from one model and check alignment before computing differences.
# Expected: key-set mismatch detected.

# Exercise 6: Keep selection and final evaluation separate
# Record configuration choice on validation and a single frozen-test assessment; reject a
# later test-driven retune.
# Expected: selection partitionvalidation; final-test tuning prohibited.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
