"""torch-022: Attention, transformer masks and information boundaries.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Compute uniform causal mixtures
# Use zero3x2queries/keys and values2, 0; 0, 2; 6, 6.
# Expected: outputs2, 0; 1, 1; 8/3, 8/3.

# Exercise 2: Perturb only the future
# Change only the third value to100, 200.
# Expected: first two rows unchanged; last34, 202/3.

# Exercise 3: Recompute nonuniform prefixes
# UseQ=K rows1, 0; 0, 1; 1, 1 and compare cuts1..3.
# Expected: all prefix outputs match within1e-12.

# Exercise 4: Reject an all-masked row
# Set the second allowed row to False.
# Expected: ValueError before the attention call.

# Exercise 5: Translate mask polarity explicitly
# Invert the allowed matrix to obtain a forbidden mask for APIs using True as blocked.
# Expected: first forbidden row False, True, True.

# Exercise 6: Keep inference dropout disabled
# Repeat functional attention with dropout_p0 and compare exact outputs.
# Expected: repeated evaluation matches.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
