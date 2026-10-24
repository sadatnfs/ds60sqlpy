# swift-020: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-020_solution.swift](swift-020_solution.swift). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Use slice indices honestly:** Element count and index origin are different properties. The slice starts at index 1 while traversal still produces two elements.

**Materialize a lazy transformation:** Pure transformations keep delayed execution understandable and reproducible. The lazy recipe produces 20 and 30 when consumed.

## Reason through the six tasks

1. **Predict and explain.** Predict slice count and startIndex separately.

2. **Guided modification.** Traverse the slice using its indices.

3. **Independent construction.** Write a generic sum over Sequence where the element type is suitable.

4. **Diagnose a defect.** Diagnose indexing a slice from zero to count minus one.

5. **Boundary evidence.** Test an empty slice and a single-pass custom sequence.

6. **Transfer and justify.** Choose lazy or materialized processing for a large input and explain repeatability and memory costs.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Sequence promises iteration but not necessarily repeatability or efficient indexing. Collection adds reusable traversal with indices, and more specialized protocols add bidirectional or random access. Write an algorithm against the capability it needs rather than assuming every sequence behaves like an array.

Lazy transformations defer work until consumption. This can avoid intermediate storage, but it also delays side effects and errors. Keep transformation closures pure. A slice can retain original indices, so using zero-based offsets indiscriminately breaks otherwise generic code. Complexity belongs to the chosen collection and operation, not merely to its spelling.

`collection.indices` supplies valid positions. `lazy.map` creates deferred transformation. `Array(sequence)` materializes. reduce summarizes a sequence without requiring indexing.

Not every Sequence can be traversed repeatedly. Index movement may be linear. Side effects in lazy closures can run later or more often than a caller expects.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
