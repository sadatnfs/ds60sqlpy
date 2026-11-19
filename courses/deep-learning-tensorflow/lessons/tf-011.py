"""tf-011: Keras models and explicit training contracts.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Fit one epoch with the standard loop
# Build a fresh zero-initialized model, compile it with SGD(0.1) and loss='mse', then call
# fit(x, y, epochs=1, batch_size=3, shuffle=False, verbose=0).
# Expected: History loss 56/3 (the loss before the update); kernel 28/15, the same as train_on_batch.

# Exercise 2: Predict a halved learning rate
# Before running it, predict the kernel and post-update loss for a fresh model trained
# once with SGD(0.05); then check the prediction.
# Expected: kernel 14/15; post-update loss 3584/675, about 5.31.

# Exercise 3: Inspect forward shape
# Pass two observations [[4], [5]] through the trained model and inspect output axes.
# Expected: shape (2, 1), predictions 112/15 and 28/3.

# Exercise 4: Evaluation leaves weights alone
# Snapshot the kernel, run a forward evaluation with training=False, and compare.
# Expected: kernel is exactly unchanged.

# Exercise 5: Show the extra intercept
# Construct an otherwise equivalent Dense layer with bias enabled and count trainable
# scalars.
# Expected: 2 parameters; bias starts 0.

# Exercise 6: Compare the scalar oracle
# Compute the first gradient directly from NumPy residuals and inputs, without Keras.
# Expected: gradient -56/3 and update 28/15.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
