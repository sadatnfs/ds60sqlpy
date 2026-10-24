# csharp-034: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-034_solution.cs](csharp-034_solution.cs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Count atomically:** Each increment is one supported atomic operation rather than a compound unsynchronized expression. The atomic count is exactly 400.

**Update one key safely:** The update delegate is a pure calculation, so repeated evaluation cannot duplicate an external effect. Twenty admitted updates produce 20.

## Reason through the six tasks

1. **Predict and explain.** Compare count++ with Interlocked.Increment.

2. **Guided modification.** Add a second independently counted key.

3. **Independent construction.** Build a concurrent frequency counter using pure update functions.

4. **Diagnose a defect.** Diagnose sending a message inside an AddOrUpdate delegate.

5. **Boundary evidence.** Test absent and already-present keys.

6. **Transfer and justify.** Explain why atomically updating two separate balances does not preserve a transfer invariant.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Interlocked provides atomic operations on supported locations, such as increment and compare-exchange. These operations are useful for simple shared state, but several individually atomic operations do not automatically form one atomic transaction. Match the mechanism to the complete invariant.

Concurrent collections make their documented operations thread-safe. Delegates passed to GetOrAdd or AddOrUpdate may execute more than once and outside internal locks. They should therefore avoid irreversible side effects. A dictionary value being safely published does not make a mutable object stored inside it automatically thread-safe.

`Interlocked.Increment(ref value)` atomically updates one location. ConcurrentDictionary manages concurrent lookup/update operations. A factory must tolerate repeated evaluation.

Concurrent containers protect their own structure, not arbitrary objects stored inside them. Do not infer once-only callback execution. Use a higher-level lock or transaction for multi-location invariants.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
