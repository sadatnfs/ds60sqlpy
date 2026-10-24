# csharp-005: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-005_solution.cs](csharp-005_solution.cs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**A guard prevents unsafe access:** The left operand establishes the precondition needed by the right operand. The missing value is handled without dereferencing null.

**Classify a threshold:** Ordered relational patterns make the inclusive boundary visible and preserve the invalid-input category. 59 retries, 60 passes, and 101 is rejected.

## Reason through the six tasks

1. **Predict and explain.** Trace which operands execute when label is null.

2. **Guided modification.** Change the classifier pass threshold to 70 and update boundary checks.

3. **Independent construction.** Write a classifier for negative, zero and positive temperatures.

4. **Diagnose a defect.** Find why replacing && with & can break a null guard.

5. **Boundary evidence.** Test the two ends of the valid score range and one value beyond each end.

6. **Transfer and justify.** Choose a routing policy with three mutually exclusive outcomes and explain how invalid values are represented.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

A branch chooses one path based on a Boolean expression. Good branches expose the domain distinction, not just a compact operator chain. Short-circuit operators evaluate their right side only when needed, which lets a guard protect a later operation. This is a control-flow property, not merely a performance optimization.

For mutually exclusive categories, put the cases in an order that matches the domain and include a policy for values outside the range. A boundary such as zero should have a deliberate meaning. Testing values just below, exactly at and just above a threshold detects mistakes that a typical middle value will miss.

`&&` requires both conditions and stops after false; `||` stops after true. A switch expression returns one value from its matching arm. The discard pattern `_` can provide an explicit fallback but must not conceal invalid input.

An else branch can accidentally classify every invalid value as valid. Test domain validity independently from success thresholds. Do not use a fallback to hide an impossible state without explaining recovery.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
