# rust-007: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-007_solution.rs](rust-007_solution.rs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Return a derived integer:** The Copy semantics of this small value permit reuse without transferring an owned allocation. The integer remains available after the call.

**Accept different text owners:** The function needs only a read-only text view, so taking String would impose unnecessary ownership transfer. One borrowed interface accepts owned text and a literal.

## Reason through the six tasks

1. **Predict and explain.** Identify which arguments are copied and which are borrowed.

2. **Guided modification.** Add a function computing a labeled length from &str.

3. **Independent construction.** Write a pure rectangle-area function with a documented valid range.

4. **Diagnose a defect.** Diagnose an accidental semicolon on the final return expression.

5. **Boundary evidence.** Test empty text and zero dimensions.

6. **Transfer and justify.** Choose owned or borrowed inputs for an API that stores data after the call.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

A function should expose accepted inputs, result meaning, mutation and failure. A compact signature cannot tell the whole story, so write the domain contract beside it. Begin with pure computations that return a value; their behavior is easy to test because they do not depend on hidden state.

Rust makes ownership transfer part of an argument type. Passing an integer copies it, while passing an owned String normally moves it. Borrowing can let a function inspect text while leaving ownership with the caller. Choose the signature from the needed capability rather than adding clones until the compiler is quiet.

`fn double(value: i32) -> i32` declares input and output types. A final expression returns its value without a semicolon. `&str` accepts borrowed text, including literals and owned String views.

A reference is not permission to retain data beyond its lifetime. Pure-looking names can hide side effects. Do not clone an entire buffer when a borrow expresses the actual requirement.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
