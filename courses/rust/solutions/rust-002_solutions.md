# rust-002: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-002_solution.rs](rust-002_solution.rs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Expose an accumulator:** Only the value requiring state transitions is declared mutable. The mutable total changes while the fixed input remains 4.

**Shadow after a representation change:** Shadowing can change type, but names must still explain whether a value is text, length or parsed quantity. The new count is the text length, not the number twelve.

## Reason through the six tasks

1. **Predict and explain.** Identify the static type and mutability of each binding.

2. **Guided modification.** Remove unnecessary mut declarations in a small program.

3. **Independent construction.** Write a running total with fixed input and mutable accumulator.

4. **Diagnose a defect.** Diagnose assigning a String to a mutable integer binding.

5. **Boundary evidence.** Test an empty input string and a zero accumulator.

6. **Transfer and justify.** Choose shadowing or distinct names for parsing stages and justify readability.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Rust bindings are immutable by default. `mut` grants permission to change a binding's value. Immutability reduces the number of state transitions a reader must consider, but it is not a substitute for understanding ownership and interior mutability introduced later. Prefer a new derived value when that expresses the operation clearly.

Type inference remains static: the compiler determines a concrete type from context. Shadowing introduces a new binding with the same name and can deliberately change its type. Reassignment instead changes the value of an existing mutable binding and must preserve its type. Use either technique to expose meaning rather than obscure where a value came from.

`let count: i32 = 3` annotates a type. `let mut total = 0` allows reassignment. `let text = text.len()` shadows the earlier name with a new binding. Integer suffixes such as `3_u64` constrain inference.

Immutable does not mean every object reachable through a type is deeply frozen. Shadowing can conceal a units change. Type inference is not dynamic typing.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
