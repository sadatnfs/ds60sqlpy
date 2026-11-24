# csharp-028: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-028_solution.cs](csharp-028_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Use independently derived cases:** The literal expectations come from the stated clamp rule, not a duplicated implementation. Negative, zero and positive cases preserve their intended categories.

**Detect a plausible wrong function:** A property complements examples but does not replace the domain-specific expected values. The zero case catches the incorrect default, and clamping twice changes nothing further.

## Task answers

### Task 1: Predict and explain

Explain which wrong implementations each case would reject.

**Written answer.** In Example A, `-2 -> 0` rejects an identity implementation that returns its input and an absolute-value implementation that returns 2. `0 -> 0` rejects implementations with a wrong default at the boundary, such as `value <= 0 ? 1 : value`. `3 -> 3` rejects implementations that always return 0 or that clamp too much. In Example B, the zero case rejects `Wrong`, and the idempotence check rejects implementations whose second application changes the value, such as one that negates negative numbers.

**Why it is correct.** A case is useful only if some plausible wrong implementation gives a different answer for it. Each category, negative, boundary and positive, separates a different family of mistakes.

**Plausible wrong approach.** Saying the cases test that the function works overstates them: an implementation that special-cases exactly -2, 0 and 3 would pass. The cases exclude named families of errors, not every error.

**How to verify.** Write `int Identity(int v) => v;` and `int Zero(int v) => 0;` and confirm each fails at least one case in Example A, and that `Wrong` fails only the zero case.

### Task 2: Guided modification

Add an extreme integer case without overflow.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```csharp
Check(ClampNonnegative(int.MinValue) == 0, "most negative clamps to 0");
Check(ClampNonnegative(int.MaxValue) == int.MaxValue, "largest kept");
bool overflow = false;
try {
  Math.Abs(int.MinValue);
} catch (OverflowException) {
  overflow = true;
}
Check(overflow, "an Abs-based clamp would fail at the extreme");
```

**Observe:** int.MinValue clamps to 0, int.MaxValue is unchanged and Math.Abs(int.MinValue) throws OverflowException.

`ClampNonnegative` only compares and returns either 0 or the input, so it never computes a value outside the `int` range. The extreme cases are still worth writing because a plausible alternative implementation, `Math.Abs` or negation, overflows exactly at `int.MinValue`, which has no positive counterpart in two's complement.

**Plausible wrong approach.** Testing only small numbers such as -2 cannot distinguish the correct clamp from a rewrite such as `Math.Abs(value) == value ? value : 0`, which agrees everywhere except at `int.MinValue`, where it throws. Expecting `-int.MinValue` to be positive is the overflow the case is designed to catch.

**How to verify.** In an `unchecked` context compute `-int.MinValue` and observe that it is still `int.MinValue`. That shows why negation-based clamps return a negative number at the extreme.

### Task 3: Independent construction

Write table-driven checks for your inventory quantity validator.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```csharp
bool ValidQuantity(int value) => value >= 0 && value <= 1000;
int[] inputs = { -1, 0, 1000, 1001 };
bool[] expected = { false, true, true, false };
for (int i = 0; i < inputs.Length; i++) {
  Check(ValidQuantity(inputs[i]) == expected[i], $"case {inputs[i]}");
}
```

**Observe:** All four rows pass, including both edges of the 0 to 1000 range.

Each row pairs an input with an expected answer written independently, and the boundary rows make an off-by-one implementation fail.

### Task 4: Diagnose a defect

Diagnose an assertion comparing a function call with the same call.

**Written answer.** `Check(ClampNonnegative(-2) == ClampNonnegative(-2), ...)` compares the function with itself. Any deterministic implementation, including one that returns -2 or 42, makes both sides equal, so the assertion cannot fail and tests nothing about the contract. Replace the right side with an expected value derived independently from the specification: `Check(ClampNonnegative(-2) == 0, ...)`.

**Why it is correct.** A test needs an oracle that does not come from the code under test. When both sides are produced by the same call, a bug appears on both sides and cancels out.

**Plausible wrong approach.** Copying the current output into the expected value, such as running the function once and pasting the result, has the same flaw one step removed: the test freezes whatever the code does today, bugs included.

**How to verify.** Change `ClampNonnegative` temporarily to return its input. The self-comparison still passes, while the independent `== 0` assertion fails. Restore the function afterwards.

### Task 5: Boundary evidence

Test idempotence and an independently derived boundary value.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```csharp
int[] samples = { int.MinValue, -1, 0, 1, int.MaxValue };
foreach (int value in samples) {
  int once = ClampNonnegative(value);
  Check(ClampNonnegative(once) == once, $"idempotent at {value}");
}
Check(ClampNonnegative(-1) == 0, "largest invalid input becomes 0");
Check(ClampNonnegative(0) == 0, "boundary itself is kept");
Check(ClampNonnegative(1) == 1, "smallest positive is kept");
```

**Observe:** Clamping twice equals clamping once for every sample, and -1, 0 and 1 map to 0, 0 and 1.

Idempotence is a property that must hold for any input, so it is checked across extremes and the boundary. The boundary values come from the specification, not from running the code: the rule is that negative inputs become 0, so the boundary sits between -1 and 0, and the cases on each side of it have expected values you can write down before running.

**Plausible wrong approach.** Checking idempotence alone is not enough: a function that always returns 5 is idempotent. The independently derived boundary cases are what tie the property to the actual contract.

**How to verify.** Replace the body temporarily with `value < -1 ? 0 : value` and confirm the `-1` check fails while idempotence still passes. That shows why both kinds of test are needed.

### Task 6: Transfer and justify

Separate unit and integration evidence for a JSON file importer.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Test oracle**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

A test is useful when a plausible wrong implementation would fail it. Repeating the implementation expression on both sides of an assertion provides weak independence. Start from a contract, choose a normal case, a boundary case and a known misconception, then derive expected outcomes separately.

The classroom uses framework-free throwing checks so the default route needs no package download. A separate prepared project can use a test framework and a test runner. Keep deterministic unit tests focused on pure behavior, and label integration tests that exercise files, databases or networks. A passing unit test does not prove a dependency is configured correctly.

A table of inputs and expected values separates cases from the loop executing them. An exception assertion should check the intended category. Avoid sleep-based timing tests; coordinate concurrent states with explicit signals.

Tests that always print success or catch their own assertion failures provide misleading evidence. A flaky test weakens trust even when production code is correct. Random generation requires a reproducible seed and a clear oracle.

## Review before continuing

Run the reference and confirm that it prints `csharp-028: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
