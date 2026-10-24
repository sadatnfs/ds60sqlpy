# rust-024: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-024_solution.rs](rust-024_solution.rs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Use independent expected cases:** Literal expectations make the test independent of the implementation expression. Negative, zero and positive cases satisfy the stated clamp rule.

**Reject a plausible wrong boundary:** The property alone would not necessarily distinguish every wrong constant implementation. Zero rejects the incorrect default while idempotence adds a second property.

## Reason through the six tasks

1. **Predict and explain.** Name a wrong implementation each case catches.

2. **Guided modification.** Add an extreme integer input without negating its minimum value.

3. **Independent construction.** Write table-driven checks for a quantity validator.

4. **Diagnose a defect.** Diagnose an assertion comparing a function call with itself.

5. **Boundary evidence.** Test idempotence alongside independent boundary expectations.

6. **Transfer and justify.** Separate unit, integration, compile-fail and runtime evidence for a library change.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

A test is strong when a plausible wrong implementation fails it. Derive expected results from the contract rather than copying the same formula into the assertion. Normal, boundary and invalid cases expose different assumptions. Properties such as idempotence can cover a wider relationship but do not replace concrete expected values.

Rust's built-in test harness runs functions marked test when compiling a test target. The classroom ordinary reference instead invokes always-active assertions through main. This keeps code execution distinct from a Cargo test workflow. A clean unit test does not prove filesystem configuration, network availability or deployment correctness.

assert and assert_eq remain active in ordinary builds, unlike debug_assert. A cfg(test) module belongs to a test compilation. Cargo test discovers unit, integration and documentation tests under their own contracts.

A disabled debug_assert is not a release invariant. Random cases require reproducibility and an oracle. A test that catches and ignores its own failure is misleading.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
