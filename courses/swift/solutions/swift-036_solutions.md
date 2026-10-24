# swift-036: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-036_solution.swift](swift-036_solution.swift). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Count a linear search:** An exact operation count avoids fragile machine-speed assumptions. The last-element search performs four comparisons.

**Build a reusable membership index:** Index construction and storage are costs that should be justified by repeated queries. The index preserves four identities and answers membership.

## Reason through the six tasks

1. **Predict and explain.** Count comparisons for first, last and absent targets.

2. **Guided modification.** Double input size and predict worst-case work.

3. **Independent construction.** Compare repeated array scans with one built Set under the same identity policy.

4. **Diagnose a defect.** Diagnose a benchmark that excludes index construction for a one-shot query.

5. **Boundary evidence.** Test duplicate inputs and empty workloads.

6. **Transfer and justify.** Write a measurement plan covering workload, correctness, optimization mode and allocation evidence.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Performance reasoning begins with the workload and the resource being measured. Array copy-on-write can make assignment cheap until mutation requires unique storage. Repeated front insertion still shifts elements and can dominate runtime regardless of that optimization. A collection's semantic convenience does not imply every operation has the same cost.

Use deterministic operation counts to explain algorithm growth, and use a prepared benchmark for elapsed-time claims. Warmup, optimization, allocation and system load can distort small measurements. Preserve correctness checks when comparing implementations. A faster result that omits validation or changes ordering is not an equivalent implementation.

Set membership can replace repeated linear searches when an equality index is appropriate. reserveCapacity can reduce reallocations but does not change the algorithmic complexity of shifting elements.

Big-O is a growth model, not an elapsed-time promise. A single stopwatch observation is weak evidence. Avoid optimizing ownership complexity before measuring the real bottleneck.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
