"""tf-031: Graphs, retracing and measurement.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Check eager arithmetic
# Evaluate x*x+1 at float32[1,2].
# Expected: output[2,5].

# Exercise 2: Compile and compare
# Wrap the same expression in tf.function and compare output.
# Expected: graph output equals eager output.

# Exercise 3: Reuse an equal signature
# Call with float32[3,4] and inspect trace count.
# Expected: output[10,17]; trace count unchanged.

# Exercise 4: Change dtype deliberately
# Call with float64[1,2] and inspect trace count and output dtype.
# Expected: float64 result[2,5]; at least one new trace.

# Exercise 5: Measure only warmed calls
# After warmup, time10 repeated float32 calls and materialize outputs.
# Expected: 10 finite outputs and nonnegative elapsed time.

# Exercise 6: Separate shape contracts
# Create a function with a variable-length float32 vector signature; call lengths2 and3.
# Expected: one trace reused; outputs have lengths2 and3.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
