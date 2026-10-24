# rust-001: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-001_solution.rs](rust-001_solution.rs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Check a greeting:** The explicit check connects a value to its expected observation. Hello, Rust appears before the lesson marker.

**Calculate instead of copying output:** A second check rejects a plausible wrong operator rather than merely confirming that printing works. The calculated capacity is 24, while addition would give 10.

## Reason through the six tasks

1. **Predict and explain.** Predict the greeting and final marker order.

2. **Guided modification.** Change the greeting and keep its expected value independent.

3. **Independent construction.** Compute the capacity of three shelves with eight books each.

4. **Diagnose a defect.** Remove a closing brace temporarily and classify the compiler diagnostic.

5. **Boundary evidence.** Check zero shelves and one shelf.

6. **Transfer and justify.** Model a three-level capacity calculation and explain every intermediate value.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Rust checks source before producing a native executable. A compiler diagnostic means the program has not reached its entrypoint. A panic during execution means an operation violated a checked assumption. Successful output means only the path that actually ran completed. Keep these forms of evidence separate when learning to diagnose a program.

The classroom supplies a pinned compiler and Arrow library inside Linux Docker. The browser sends a single source file, not a Cargo project or arbitrary shell command. Start by tracing a tiny calculation and independently checking its result. This builds the habit of distinguishing observed behavior from a printed success claim.

`fn main` declares the entry function. `let` introduces a binding. `println!` is a macro, indicated by the exclamation mark. `assert_eq!` compares actual and expected values and panics on disagreement. A semicolon turns an expression into a statement whose value is discarded.

A compiler success does not establish business correctness. Do not replace a failing assertion with a success print. The Result-returning main wrapper is scaffolding for later error propagation; its full meaning is taught in the error chapters.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
