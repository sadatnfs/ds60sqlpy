# csharp-003: explanation and comparison

Reference program: [csharp-003_solution.cs](csharp-003_solution.cs), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**Reject overflowing counts:** The normal and failure paths separate an exceptional boundary from ordinary arithmetic. The maximum int plus one is rejected; 100 plus 20 is accepted.

**Preserve decimal intent:** A rounding difference can be a policy disagreement rather than a compiler defect. Write the expected rule before the implementation. Two valid midpoint policies produce 2.34 and 2.35.

## Task answers

### Task 1: Predict and explain

Predict which arithmetic operation throws and explain the representation boundary.

**Written answer.** `checked(large + 1)` throws `OverflowException`; `checked(100 + 20)` returns 120. `int` is a 32-bit two's complement type whose largest value is `int.MaxValue`, 2147483647. Adding 1 needs a value the 32 bits cannot represent, and `checked` turns that into an exception instead of a wrapped result.

**Why it is correct.** The range of `int` runs from -2147483648 to 2147483647. 120 is far inside it. `large + 1` would be 2147483648, one past the top, and without `checked` the bits would wrap to `int.MinValue`, a negative count.

**Plausible wrong approach.** Predicting that both lines succeed because 2147483648 looks like an ordinary number ignores the fixed width of `int`. Predicting that the program crashes at compile time is also wrong: `large` is a variable, so the overflow is found while running.

**How to verify.** Run Example A: the `overflow must be visible` check passes, proving the exception was caught. Then add `Check(unchecked(int.MaxValue + 1) == int.MinValue, "wraps")` to see the silent result that `checked` prevents.

### Task 2: Guided modification

Replace maximum plus one with minimum minus one and check the failure.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```csharp
bool overflowed = false;
try {
  int small = int.MinValue;
  _ = checked(small - 1);
} catch (OverflowException) {
  overflowed = true;
}
Check(overflowed, "minimum minus one rejected");
Check(checked(-100 - 20) == -120, "normal subtraction");
```

**Observe:** int.MinValue minus one throws OverflowException; -100 minus 20 returns -120.

The lower boundary behaves like the upper one. `int.MinValue` is -2147483648, and -2147483649 does not fit in 32 bits, so the checked subtraction throws. A value well inside the range still subtracts normally, which shows the check rejects only the boundary crossing.

**Plausible wrong approach.** Assuming the failure cannot happen at the bottom of the range because counts are usually positive leaves differences such as `start - end` unprotected. Without `checked`, `int.MinValue - 1` silently becomes `int.MaxValue`.

**How to verify.** Remove `checked` from the subtraction (wrap it in `unchecked(...)`) and confirm `overflowed` stays false and the result equals `int.MaxValue`. Restore `checked` and the first check passes again.

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

**Written answer.** Parsing `"2.675"` with `double.Parse` stores the nearest binary fraction, 2.67499999999999982236431605997495353221893310546875. The approximation enters at that parse, before any decimal exists. Code that rounds or computes while the value is still a `double` sees a number below the midpoint: `Math.Round(2.675, 2, MidpointRounding.AwayFromZero)` gives 2.67. Parse money with `decimal.Parse(text, CultureInfo.InvariantCulture)`, which keeps 2.675 exactly and rounds it to 2.68.

**Why it is correct.** `double` stores base-2 fractions, and 0.675 has no finite base-2 form. `decimal` stores a base-10 integer and a scale, so 2.675 is exactly 2675 with scale 3. A later `(decimal)` conversion cannot know which decimal text produced the binary value.

**Plausible wrong approach.** Converting to `decimal` immediately after the `double` parse and assuming that repairs the value hides the problem in simple cases, because the conversion rounds to about 15 significant digits. Any `double` arithmetic or rounding done before the conversion still used the approximate value.

**How to verify.** Check `Math.Round(2.675, 2, MidpointRounding.AwayFromZero) == 2.67` and `Math.Round(2.675m, 2, MidpointRounding.AwayFromZero) == 2.68m`. The two policies differ only because of where the approximation entered.

### Task 5: Boundary evidence

Compare midpoint values immediately below, at and above the rounding boundary.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```csharp
var even = MidpointRounding.ToEven;
var away = MidpointRounding.AwayFromZero;
Check(Math.Round(2.344m, 2, even) == 2.34m, "below, even");
Check(Math.Round(2.344m, 2, away) == 2.34m, "below, away");
Check(Math.Round(2.345m, 2, even) == 2.34m, "midpoint, even");
Check(Math.Round(2.345m, 2, away) == 2.35m, "midpoint, away");
Check(Math.Round(2.346m, 2, even) == 2.35m, "above, even");
Check(Math.Round(2.346m, 2, away) == 2.35m, "above, away");
```

**Observe:** 2.344 rounds to 2.34 and 2.346 to 2.35 under both policies; only 2.345 differs, 2.34 versus 2.35.

A midpoint policy applies only to values exactly halfway between two candidates. 2.344 is nearer 2.34 and 2.346 is nearer 2.35, so both policies agree. At 2.345 `ToEven` picks the candidate with an even last digit, 2.34, while `AwayFromZero` picks 2.35. Decimal literals keep these thousandths exact, so the midpoint is a real midpoint.

**Plausible wrong approach.** Testing only 2.345 shows the policies differ but cannot show that they agree elsewhere. Testing only 2.344 and 2.346 makes the policy choice look irrelevant, and a later switch of policy would pass unnoticed.

**How to verify.** Add 2.355m: `ToEven` gives 2.36 because 6 is even, and `AwayFromZero` also gives 2.36. Then add -2.345m and confirm `AwayFromZero` gives -2.35, away from zero rather than upward.

### Task 6: Transfer and justify

Design a quantity and currency contract that states overflow, rounding and invalid-input behavior.

No single answer exists; extend task 3 using the [open transfer routine](../STUDY-GUIDE.md#open-transfer-tasks).

## Mechanism and diagnostic reasoning

Arithmetic has representation limits. An `int` has a finite range, so mathematically valid addition may overflow. C# supports checked contexts that reject integral overflow and unchecked contexts that wrap. Neither behavior should be chosen accidentally for business quantities. Floating-point arithmetic instead approximates most decimal fractions, so equality of independently calculated doubles often needs a scale-aware tolerance.

Use `decimal` when a decimal representation matches the domain, such as many monetary calculations. Decimal arithmetic still has finite precision and range. Specify rounding at a business boundary, including its midpoint rule, rather than rounding every intermediate operation. Keep currency and units explicit: a bare number does not identify what it measures.

`checked(expression)` asks for integral overflow detection in that expression. The `m` suffix selects decimal, while `0.1` defaults to double. `Math.Round(amount, 2, MidpointRounding.ToEven)` records both precision and tie policy.

`checked` does not turn floating-point arithmetic into exact decimal arithmetic. Rounding before aggregation can produce a different total than rounding afterward. Never use an unexplained tolerance to hide a unit mismatch.

## Review before continuing

Run the reference and confirm it prints `csharp-003: passed`, then rerun the guide's counterexample.
