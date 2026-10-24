"""tf-022: Attention with an explicit information boundary.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Calculate uniform mixtures
# Use zero3x2 queries and keys with V[[2,0],[0,2],[6,6]].
# Expected: outputs[[2,0],[1,1],[8/3,8/3]].

# Exercise 2: Perturb the future
# Replace only the third value with[100,200].
# Expected: first two rows unchanged; final row[34,202/3].

# Exercise 3: Recompute every prefix
# For prefix lengths1,2,3 run the function anew on sliced Q,K,V.
# Expected: all prefix outputs match the full early rows.

# Exercise 4: Expose post-softmax masking
# Multiply uniform1/3 weights by a triangle without renormalizing.
# Expected: row sums[1/3,2/3,1].

# Exercise 5: Use nonuniform scores
# Set Q=K[[1,0],[0,1],[1,1]] and repeat the prefix test.
# Expected: prefix comparisons pass within1e-6.

# Exercise 6: Refuse malformed input
# Pass an empty sequence and a value matrix with the wrong row count.
# Expected: both raise ValueError.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
