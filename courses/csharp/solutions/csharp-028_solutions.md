# csharp-028: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-028_solution.cs](csharp-028_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Use independently derived cases:** The literal expectations come from the stated clamp rule, not a duplicated implementation. Negative, zero and positive cases preserve their intended categories.

**Detect a plausible wrong function:** A property complements examples but does not replace the domain-specific expected values. The zero case catches the incorrect default, and clamping twice changes nothing further.

## Task answers

### Task 1: Predict and explain

Explain which wrong implementations each case would reject.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The literal expectations come from the stated clamp rule, not a duplicated implementation. Negative, zero and positive cases preserve their intended categories.

### Task 2: Guided modification

Add an extreme integer case without overflow.

No separate reference answer has been written for this task. Start from Example B: A property complements examples but does not replace the domain-specific expected values. The zero case catches the incorrect default, and clamping twice changes nothing further.

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

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Tests that always print success or catch their own assertion failures provide misleading evidence. A flaky test weakens trust even when production code is correct. Random generation requires a reproducible seed and a clear oracle.

### Task 5: Boundary evidence

Test idempotence and an independently derived boundary value.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Use independently derived cases) and Example B (Detect a plausible wrong function).

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
