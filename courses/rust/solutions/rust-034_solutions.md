# rust-034: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-034_solution.rs](rust-034_solution.rs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Reconstruct a bounded borrowed view:** The safety proof is tied to the pointer origin and exact length, not merely to the pointer being non-null. The reconstructed view matches the live initialized array.

**Prefer the safe operation when available:** Unsafe should be justified by a real boundary, not used because pointer syntax appears advanced. A normal slice provides the same read contract without a manual safety burden.

## Reason through the six tasks

1. **Predict and explain.** State every precondition needed by from_raw_parts.

2. **Guided modification.** Reduce the borrowed length while retaining valid initialized storage.

3. **Independent construction.** Write a safe wrapper specification before considering an unsafe implementation.

4. **Diagnose a defect.** Diagnose returning a pointer after its owner is dropped.

5. **Boundary evidence.** Review zero-length and alignment rules without executing undefined behavior.

6. **Transfer and justify.** Design an FFI ownership document stating allocation, release, encoding and error conventions.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Unsafe permits a small set of operations whose correctness the compiler cannot fully establish. It does not disable every safety rule or turn wrong memory access into valid behavior. Each unsafe block needs an argument covering pointer validity, alignment, initialized length, aliasing and lifetime. Keep the block small and wrap it in a safe interface that enforces those conditions.

Foreign-function interfaces add an ABI contract: layout, calling convention, string encoding, ownership and failure signaling must agree across languages. A successful link does not prove those agreements. The ordinary fixture uses a pointer obtained from a live array and immediately reconstructs a read-only slice under a documented invariant, without calling undeclared native libraries.

`as_ptr` borrows an address from live storage. `slice::from_raw_parts` is unsafe because the caller supplies validity and length. A SAFETY comment explains why this exact operation satisfies its preconditions.

Never test undefined behavior by hoping it crashes predictably. A null check is insufficient to prove pointer validity. Panics crossing an incompatible FFI boundary need a deliberate policy.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
