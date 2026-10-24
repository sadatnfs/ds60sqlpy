# rust-005: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-005_solution.rs](rust-005_solution.rs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Choose a value with if:** Both branches return the same kind of value, so the result has one static type. The branch expression supplies one immutable label.

**Classify explicit boundaries:** A tiny boundary fixture rejects an off-by-one policy error. The transition at sixty and the invalid upper range are distinct.

## Reason through the six tasks

1. **Predict and explain.** Identify the value produced by each branch.

2. **Guided modification.** Change the threshold and update neighboring tests.

3. **Independent construction.** Write a negative, zero and positive classifier.

4. **Diagnose a defect.** Diagnose a semicolon that changes a branch result into unit.

5. **Boundary evidence.** Test both valid endpoints and one value beyond each.

6. **Transfer and justify.** Choose explicit enum matches or a wildcard for a finite application state model.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Rust treats many control-flow constructs as expressions producing values. An if expression must return compatible types from its branches. This encourages deriving one result instead of initializing a mutable variable and assigning it inconsistently on several paths.

Match handles patterns and requires coverage of possibilities. A broad wildcard can be useful for invalid numeric ranges but can hide newly added enum cases. Make boundaries explicit and test adjacent inputs. A correct normal example does not prove that an inclusive versus exclusive threshold is right.

`let label = if condition { "yes" } else { "no" };` uses a branch result. The final expression in a block has no semicolon when it supplies the value. `0..=59` is an inclusive pattern range.

A semicolon can change a block value. Match arm order matters when patterns overlap. A wildcard that hides an unhandled domain state weakens maintenance feedback.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
