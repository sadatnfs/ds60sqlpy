"""tf-011: Keras models and explicit training contracts.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Construct a scalar model
# Create a zero-initialized single-unit model without bias and inspect its parameter
# count.
# Expected: one parameter and all initial predictions0.

# Exercise 2: Audit the first update
# Compile with mean squared error and SGD(.1), then call train_on_batch once.
# Expected: kernel28/15 and post-update loss56/675 within1e-6.

# Exercise 3: Inspect forward shape
# Pass two observations [[4],[5]] through the trained model and inspect output axes.
# Expected: shape(2,1), predictions112/15 and28/3.

# Exercise 4: Evaluation leaves weights alone
# Snapshot the kernel, run a forward evaluation with training=False, and compare.
# Expected: kernel is exactly unchanged.

# Exercise 5: Show the extra intercept
# Construct an otherwise equivalent Dense layer with bias enabled and count trainable
# scalars.
# Expected: 2 parameters; bias starts0.

# Exercise 6: Compare the scalar oracle
# Compute the first gradient directly from NumPy residuals and inputs, without Keras.
# Expected: gradient-56/3 and update28/15.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
