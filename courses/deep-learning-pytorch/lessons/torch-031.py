"""torch-031: Profiling, torch.compile and honest performance measurement.

Answer-free learner worksheet. See the companion guide for worked examples.
Copy to .learning before editing. Six independent attempts belong below.
"""

# Exercise 1: Establish an eager oracle
# Evaluatef(x)=x*x+1 at float32[1, 2].
# Expected: output[2, 5].

# Exercise 2: Capture with a transparent backend
# Compile using a counting backend that returns graph.forward and compare output.
# Expected: captured graph exists; output matches eager.

# Exercise 3: Check signature reuse
# Call with float32[3, 4], then with float64[1, 2].
# Expected: same signature reuses capture; changed dtype adds a graph.

# Exercise 4: Measure warmed calls honestly
# Warm the float32 path, then execute 20 calls and record elapsed time.
# Expected: 20 correct outputs and nonnegative elapsed time.

# Exercise 5: Inspect actual CPU operations
# Profile one eager call and inspect operation names.
# Expected: aten:: mul and aten:: add appear.

# Exercise 6: State the backend limitation
# Record graph capture True, optimizing native backend False and GPU benchmark False.
# Expected: receipt does not claim universal speedup.

if __name__ == "__main__":
    print("Read the guide and implement the six exercises in your saved copy.")
