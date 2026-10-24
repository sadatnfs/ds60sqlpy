# swift-035: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [swift-035_solution.swift](swift-035_solution.swift). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Borrow only within the closure:** Scoped access limits the lifetime reasoning to one visible closure. The result escapes as an integer while the borrowed pointer does not.

**Handle empty storage without dereferencing:** No base-address dereference is needed, avoiding assumptions about a pointer for empty storage. An empty buffer is valid to inspect by count.

## Reason through the six tasks

1. **Predict and explain.** Identify the pointer lifetime and the returned owned result.

2. **Guided modification.** Compute a maximum with an explicit empty-input policy.

3. **Independent construction.** Wrap a scoped read-only buffer operation behind a safe function contract.

4. **Diagnose a defect.** Diagnose returning the buffer baseAddress for later use.

5. **Boundary evidence.** Test empty, singleton and multi-element buffers.

6. **Transfer and justify.** Write an interoperability checklist covering ownership, alignment, initialization and error reporting.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Swift normally protects memory through value semantics, ARC and checked collection access. Unsafe pointer APIs deliberately cross that protection boundary for interoperability and specialized performance work. A pointer is valid only while its owner guarantees storage lifetime and binding. Compiling unsafe code does not prove its memory access is valid.

Prefer scoped buffer APIs that lend a pointer only for a closure. Do not store that pointer or use it after the closure returns. Distinguish initialized elements from allocated capacity, and preserve element alignment and type binding. This lesson uses read-only scoped access to an owned array, keeping the demonstration small enough to inspect fully.

withUnsafeBufferPointer temporarily borrows contiguous elements. The pointer count states initialized accessible elements. Return a copied result from the closure, never the borrowed pointer itself.

Unsafe does not disable all runtime checks or make an operation faster. Never infer lifetime from a pointer value remaining numerically unchanged. Keep native API ownership documented and avoid unsafe code when safe collections suffice.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
