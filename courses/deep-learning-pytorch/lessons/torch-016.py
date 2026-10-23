"""torch-016: Initialization, nonlinearities and gradient diagnostics.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Construct XOR by hand
# Use inputs 00, 01, 10, 11 and two rectified differences.
# Expected: outputs 0, 1, 1, 0.

# Exercise 2: Remove the nonlinearity
# Sum the raw difference features without ReLU.
# Expected: all four outputs 0.

# Exercise 3: Map the construction into Linear
# Set a 2-to-2 bias-free Linear weight to W.T, then check a separate asymmetric matrix.
# Expected: module features equal manual features; the asymmetric probe distinguishes the two orientations.

# Exercise 4: Inspect activation gradients
# Differentiate ReLU at-2 and 2.
# Expected: gradients 0 and 1.

# Exercise 5: Expose identical-unit symmetry
# Initialize both stored Linear rows identically and compare their outputs.
# Expected: two unit outputs match on every row.

# Exercise 6: Transfer to continuous inputs
# Evaluate the fixed construction at(.2, .8) and(.8, .2).
# Expected: both.6; the function is absolute difference.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
