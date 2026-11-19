"""torch-031: Profiling, torch.compile and honest performance measurement.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Establish a new eager oracle
# Evaluate g(x)=2x-1 eagerly at the float32 inputs [0, 3].
# Expected: output [-1, 5].

# Exercise 2: Capture the new function
# Compile g with a counting backend that returns graph.forward and compare it with the
# eager output.
# Expected: at least one captured graph; outputs match exactly.

# Exercise 3: Predict recompilation for a new shape
# Call the compiled function with a three-element input, then with a second three-element
# input.
# Expected: the first three-element call adds a graph; the repeated shape reuses it.

# Exercise 4: Measure warmed calls honestly
# Warm the float32 path, then execute 20 calls and record elapsed time.
# Expected: 20 correct outputs and nonnegative elapsed time.

# Exercise 5: Inspect actual CPU operations
# Profile one eager call and inspect operation names.
# Expected: aten::mul and aten::add appear.

# Exercise 6: State the backend limitation
# Record graph capture True, optimizing native backend False and GPU benchmark False.
# Expected: receipt does not claim universal speedup.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
