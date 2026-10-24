# rust-009: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-009_solution.rs](rust-009_solution.rs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Borrow more than once:** Both references inspect the same allocation without taking release responsibility. Two readers coexist and the owner remains intact.

**Return a borrowed view:** The function returns a slice whose validity depends on the input owner. The result is a view into caller-owned text, with an explicit empty policy.

## Reason through the six tasks

1. **Predict and explain.** Identify the owner and both readers.

2. **Guided modification.** Add another read-only inspection without cloning.

3. **Independent construction.** Write a last-word function returning a borrowed slice.

4. **Diagnose a defect.** Try returning a reference to a local String and explain the compiler rejection.

5. **Boundary evidence.** Test empty text and a single word.

6. **Transfer and justify.** Choose a borrowed view or owned result for a parser whose caller may discard the input immediately.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

A shared reference grants temporary read access without taking ownership. Several shared borrows can coexist when no conflicting mutation occurs. The owner must remain alive while borrowed data can still be used. Rust's borrow checker tracks these relationships through control flow, often ending a borrow after its last use rather than the end of the entire lexical block.

A borrowed API is useful for inspection, searching and parsing views. It avoids unnecessary allocation while preserving caller ownership. The lifetime constraint is not a runtime timer: it is a compile-time relationship between valid uses. Returning a reference to a local value is invalid because the owner disappears when the function returns.

`&value` creates a shared reference. Dereferencing with `*reference` accesses a referenced scalar when needed. Auto-dereferencing makes many method calls convenient. A return type `&str` must refer to storage owned elsewhere for a sufficient lifetime.

A reference cannot make its owner live longer by declaration alone. Borrow duration follows actual use constraints. Avoid converting every slice to String unless independent ownership is needed.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
