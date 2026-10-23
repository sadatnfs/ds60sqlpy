"""tf-031: Graphs, retracing and measurement.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Check eager arithmetic
# Evaluate x*x+1 at float32[1,2].
# Expected: output[2,5].

# Exercise 2: Trace a graph and compare
# Wrap the expression in plain tf.function, run it and inspect the initial trace count.
# Expected: Graph output equals eager output; at least one trace exists. No XLA compilation is requested.

# Exercise 3: Reuse an equal signature
# Call with float32[3,4] and inspect trace count.
# Expected: output[10,17]; trace count unchanged.

# Exercise 4: Change dtype deliberately
# Call with float64[1,2] and inspect trace count and output dtype.
# Expected: float64 result[2,5]; at least one new trace.

# Exercise 5: Measure only warmed calls
# Warm the float32 graph, time ten completed calls, then check every collected result.
# Expected: Ten finite [2,5] results and a nonnegative measured interval, without a speed-ranking claim.

# Exercise 6: Separate shape contracts
# Reuse a variable-length float32 vector signature at lengths two and three, then reject
# wrong rank and dtype.
# Expected: One declared trace is reused for both lengths; incompatible rank or dtype is rejected.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
