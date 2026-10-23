"""torch-016: Initialization, nonlinearities and gradient diagnostics.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Construct XOR by hand
# Use inputs00, 01, 10, 11 and two rectified differences.
# Expected: outputs0, 1, 1, 0.

# Exercise 2: Remove the nonlinearity
# Sum the raw difference features without ReLU.
# Expected: all four outputs0.

# Exercise 3: Map the construction into Linear
# Seta2-to-2bias-free Linear weight to W.T and apply ReLU.
# Expected: module features equal manual features.

# Exercise 4: Inspect activation gradients
# Differentiate ReLU at-2 and2.
# Expected: gradients0 and1.

# Exercise 5: Expose identical-unit symmetry
# Initialize both stored Linear rows identically and compare their outputs.
# Expected: two unit outputs match on every row.

# Exercise 6: Transfer to continuous inputs
# Evaluate the fixed construction at(.2, .8) and(.8, .2).
# Expected: both.6; the function is absolute difference.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
