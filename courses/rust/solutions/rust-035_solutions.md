# rust-035: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-035_solution.rs](rust-035_solution.rs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Distinguish handle size from owned data:** Inline size is not a total retained-memory measurement. String handle size is equal while the owned text lengths differ.

**Prepare capacity without inventing elements:** Reserved capacity is a resource decision, not part of the logical dataset. Only ten initialized elements participate in the sum.

## Reason through the six tasks

1. **Predict and explain.** Separate inline handles from their owned allocations.

2. **Guided modification.** Compare vector lengths after different reserve calls.

3. **Independent construction.** Write a benchmark plan comparing repeated clone with borrowed processing.

4. **Diagnose a defect.** Diagnose measuring size_of as total memory retained by nested objects.

5. **Boundary evidence.** Test empty and large inputs with the same correctness oracle.

6. **Transfer and justify.** Choose a layout for repeated column scans and explain locality, ownership and update tradeoffs.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Rust exposes enough control to optimize data layout and allocation, but correctness and a workload model come first. Contiguous arrays can improve locality for column scans, while pointer-heavy structures may incur indirection. Copying a small value can be cheaper than managing shared ownership; cloning a large buffer can dominate a pipeline.

Measure allocations and throughput under a realistic workload, and retain identical semantics across implementations. A single elapsed-time sample is weak evidence. The classroom uses deterministic size and operation observations, then prepares the learner to design an external benchmark. Representation details should not leak into a stable API unless the contract requires them.

size_of measures a type's inline representation, not every allocation reachable from it. Vec capacity is separate allocated storage. reserve can reduce reallocations without changing the algorithmic cost of shifting or sorting.

Benchmarking different validation or ordering semantics is invalid. Size and alignment can vary by target. Do not use unsafe layout assumptions to replace an actual profiling result.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
