# rust-012: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [rust-012_solution.rs](rust-012_solution.rs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Reserve within an invariant:** The method owns both the affordability check and the subtraction. A successful reservation leaves three units.

**Reject without partial mutation:** Validation occurs before changing state, preserving the prior valid value. Excess demand is rejected and zero is an allowed no-op.

## Reason through the six tasks

1. **Predict and explain.** Explain the capability expressed by each method receiver.

2. **Guided modification.** Add a checked restock method.

3. **Independent construction.** Create a bounded counter with private state and validated operations.

4. **Diagnose a defect.** Diagnose subtracting before checking available stock.

5. **Boundary evidence.** Test zero, exact-stock and excess reservations.

6. **Transfer and justify.** Choose a consuming method when an operation should make the prior state unavailable.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

A struct groups named fields into a domain value. Methods express operations on that value, and their receiver states whether they borrow, mutate or consume it. A constructor function can validate inputs before creating a valid instance. Private fields prevent callers from bypassing that constructor or later invariants.

Failure atomicity means a rejected operation leaves the prior valid state unchanged. Check all rejection conditions before mutation or build a candidate value and commit it only after validation. Encapsulation is useful because it keeps this reasoning in one place rather than requiring every caller to remember the rule.

`impl Inventory` contains associated functions and methods. `&self` reads, `&mut self` mutates, and `self` consumes. An associated constructor such as new can return Option or Result.

Public writable fields can bypass invariants. Unsigned types prevent negative representation but do not prevent overflow. A method taking &mut self is not automatically safe for unsynchronized sharing across threads.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
