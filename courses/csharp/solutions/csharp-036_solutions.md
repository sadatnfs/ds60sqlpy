# csharp-036: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-036_solution.cs](csharp-036_solution.cs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Use only admitted buffer contents:** The pool guarantees minimum capacity, not exact size or zeroed contents. Only three initialized elements contribute to the total.

**Release retained references deliberately:** The test checks controllable ownership, avoiding a flaky assumption about when garbage collection occurs. Clearing removes the application references without promising collection timing.

## Reason through the six tasks

1. **Predict and explain.** Separate logical length from rented array length.

2. **Guided modification.** Use a different requested length while initializing exactly that region.

3. **Independent construction.** Write a pooled-buffer helper with finally-based return.

4. **Diagnose a defect.** Diagnose reading uninitialized pooled capacity or returning the same buffer twice.

5. **Boundary evidence.** Test cleanup when the computation throws.

6. **Transfer and justify.** Decide whether pooling is justified using allocation measurements and a stated lifetime contract.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

The garbage collector reclaims unreachable managed objects. Reachability is not the same as usefulness: a global list or event subscription can keep an otherwise unwanted object alive. Resource cleanup still belongs to IDisposable rather than collection timing. Measure retained references before assuming the collector is malfunctioning.

ArrayPool reuses buffers to reduce allocation pressure. A rented array may be larger than requested and may contain prior data. Use only the logical length, initialize what will be read, and return exactly the borrowed array once. Clearing sensitive contents is a deliberate policy. Pooling adds ownership complexity, so it should solve a measured allocation problem.

`ArrayPool<T>.Shared.Rent(n)` grants temporary use of at least n elements. `Return` ends ownership. A try/finally protects return on failure; never expose a view after return.

Never assert that a weak reference must disappear immediately after a collection request. Returning a buffer while asynchronous work still uses it causes data corruption. Pooling is not inherently a performance win.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
