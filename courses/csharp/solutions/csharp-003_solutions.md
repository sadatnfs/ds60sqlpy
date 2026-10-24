# csharp-003: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-003_solution.cs](csharp-003_solution.cs). Its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Reject overflowing counts:** The normal and failure paths separate an exceptional boundary from ordinary arithmetic. The maximum int plus one is rejected; 100 plus 20 is accepted.

**Preserve decimal intent:** A rounding difference can be a policy disagreement rather than a compiler defect. Write the expected rule before the implementation. Two valid midpoint policies produce 2.34 and 2.35.

## Reason through the six tasks

1. **Predict and explain.** Predict which arithmetic operation throws and explain the representation boundary.

2. **Guided modification.** Replace maximum plus one with minimum minus one and check the failure.

3. **Independent construction.** Calculate a decimal subtotal and tax, rounding only the final payable amount.

4. **Diagnose a defect.** Diagnose a price parsed as double and later converted to decimal. Explain where approximation entered.

5. **Boundary evidence.** Compare midpoint values immediately below, at and above the rounding boundary.

6. **Transfer and justify.** Design a quantity and currency contract that states overflow, rounding and invalid-input behavior.

For tasks 1 and 2, use the checked values and mechanism trace in the two examples. For task 3, choose names that expose the input and result contract and retain the same invariants. For task 4, the diagnosed mistakes below supply a concrete wrong assumption: preserve its counterexample before repairing it. Task 5 needs an explicit expected value or documented rejection at the boundary, not just successful execution. For task 6, explain what changes in the new context and which part of the original mechanism remains applicable. Several representations may satisfy this transfer task; justify the choice rather than treating this reference as the only architecture.

## Mechanism and diagnostic reasoning

Arithmetic has representation limits. An `int` has a finite range, so mathematically valid addition may overflow. C# supports checked contexts that reject integral overflow and unchecked contexts that wrap. Neither behavior should be chosen accidentally for business quantities. Floating-point arithmetic instead approximates most decimal fractions, so equality of independently calculated doubles often needs a scale-aware tolerance.

Use `decimal` when a decimal representation matches the domain, such as many monetary calculations. Decimal arithmetic still has finite precision and range. Specify rounding at a business boundary, including its midpoint rule, rather than rounding every intermediate operation. Keep currency and units explicit: a bare number does not identify what it measures.

`checked(expression)` asks for integral overflow detection in that expression. The `m` suffix selects decimal, while `0.1` defaults to double. `Math.Round(amount, 2, MidpointRounding.ToEven)` records both precision and tie policy.

`checked` does not turn floating-point arithmetic into exact decimal arithmetic. Rounding before aggregation can produce a different total than rounding afterward. Never use an unexplained tolerance to hide a unit mismatch.

## Review before continuing

The reference checks the worked scenarios, including their boundary distinctions. Your independent and transfer artifacts may have additional checks. Compare observations rather than only source text. Preserve any new regression case you discover and explain why it would reject a plausible wrong implementation. External project steps require their own build and platform evidence and are not established by a portable reference passing.
