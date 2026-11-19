# csharp-003: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-003_solution.cs](csharp-003_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Reject overflowing counts:** The normal and failure paths separate an exceptional boundary from ordinary arithmetic. The maximum int plus one is rejected; 100 plus 20 is accepted.

**Preserve decimal intent:** A rounding difference can be a policy disagreement rather than a compiler defect. Write the expected rule before the implementation. Two valid midpoint policies produce 2.34 and 2.35.

## Task answers

### Task 1: Predict and explain

Predict which arithmetic operation throws and explain the representation boundary.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The normal and failure paths separate an exceptional boundary from ordinary arithmetic. The maximum int plus one is rejected; 100 plus 20 is accepted.

### Task 2: Guided modification

Replace maximum plus one with minimum minus one and check the failure.

No separate reference answer has been written for this task. Start from Example B: A rounding difference can be a policy disagreement rather than a compiler defect. Write the expected rule before the implementation. Two valid midpoint policies produce 2.34 and 2.35.

### Task 3: Independent construction

Calculate a decimal subtotal and tax, rounding only the final payable amount.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```csharp
decimal[] prices = { 19.99m, 5.01m, 0.35m };
decimal subtotal = prices.Sum();
decimal tax = subtotal * 0.0825m;
decimal payable = Math.Round(subtotal + tax, 2, MidpointRounding.ToEven);
Check(subtotal == 25.35m, "exact decimal subtotal");
Check(tax == 2.091375m, "unrounded tax");
Check(payable == 27.44m, "rounded only at the end");
```

**Observe:** Subtotal 25.35, unrounded tax 2.091375 and payable 27.44.

decimal keeps the cents exact, the tax keeps its full precision, and only the final payable amount is rounded once with a named midpoint rule.

### Task 4: Diagnose a defect

Diagnose a price parsed as double and later converted to decimal. Explain where approximation entered.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: `checked` does not turn floating-point arithmetic into exact decimal arithmetic. Rounding before aggregation can produce a different total than rounding afterward. Never use an unexplained tolerance to hide a unit mismatch.

### Task 5: Boundary evidence

Compare midpoint values immediately below, at and above the rounding boundary.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Reject overflowing counts) and Example B (Preserve decimal intent).

### Task 6: Transfer and justify

Design a quantity and currency contract that states overflow, rounding and invalid-input behavior.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Overflow**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

Arithmetic has representation limits. An `int` has a finite range, so mathematically valid addition may overflow. C# supports checked contexts that reject integral overflow and unchecked contexts that wrap. Neither behavior should be chosen accidentally for business quantities. Floating-point arithmetic instead approximates most decimal fractions, so equality of independently calculated doubles often needs a scale-aware tolerance.

Use `decimal` when a decimal representation matches the domain, such as many monetary calculations. Decimal arithmetic still has finite precision and range. Specify rounding at a business boundary, including its midpoint rule, rather than rounding every intermediate operation. Keep currency and units explicit: a bare number does not identify what it measures.

`checked(expression)` asks for integral overflow detection in that expression. The `m` suffix selects decimal, while `0.1` defaults to double. `Math.Round(amount, 2, MidpointRounding.ToEven)` records both precision and tie policy.

`checked` does not turn floating-point arithmetic into exact decimal arithmetic. Rounding before aggregation can produce a different total than rounding afterward. Never use an unexplained tolerance to hide a unit mismatch.

## Review before continuing

Run the reference and confirm that it prints `csharp-003: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
