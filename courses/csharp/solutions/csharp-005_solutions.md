# csharp-005: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-005_solution.cs](csharp-005_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**A guard prevents unsafe access:** The left operand establishes the precondition needed by the right operand. The missing value is handled without dereferencing null.

**Classify a threshold:** Ordered relational patterns make the inclusive boundary visible and preserve the invalid-input category. 59 retries, 60 passes, and 101 is rejected.

## Task answers

### Task 1: Predict and explain

Trace which operands execute when label is null.

No separate reference answer has been written for this task. Example A is the evidence to compare with: The left operand establishes the precondition needed by the right operand. The missing value is handled without dereferencing null.

### Task 2: Guided modification

Change the classifier pass threshold to 70 and update boundary checks.

No separate reference answer has been written for this task. Start from Example B: Ordered relational patterns make the inclusive boundary visible and preserve the invalid-input category. 59 retries, 60 passes, and 101 is rejected.

### Task 3: Independent construction

Write a classifier for negative, zero and positive temperatures.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```csharp
string Temperature(int celsius) {
  if (celsius < 0) {
    return "below zero";
  }
  if (celsius == 0) {
    return "zero";
  }
  return "above zero";
}
Check(Temperature(-5) == "below zero", "negative");
Check(Temperature(0) == "zero", "zero");
Check(Temperature(12) == "above zero", "positive");
```

**Observe:** -5, 0 and 12 are classified as below zero, zero and above zero.

The three branches cover every int exactly once, and zero is tested on its own instead of being folded into either side.

### Task 4: Diagnose a defect

Find why replacing && with & can break a null guard.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: An else branch can accidentally classify every invalid value as valid. Test domain validity independently from success thresholds. Do not use a fallback to hide an impossible state without explaining recovery.

### Task 5: Boundary evidence

Test the two ends of the valid score range and one value beyond each end.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (A guard prevents unsafe access) and Example B (Classify a threshold).

### Task 6: Transfer and justify

Choose a routing policy with three mutually exclusive outcomes and explain how invalid values are represented.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Predicate**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

A branch chooses one path based on a Boolean expression. Good branches expose the domain distinction, not just a compact operator chain. Short-circuit operators evaluate their right side only when needed, which lets a guard protect a later operation. This is a control-flow property, not merely a performance optimization.

For mutually exclusive categories, put the cases in an order that matches the domain and include a policy for values outside the range. A boundary such as zero should have a deliberate meaning. Testing values just below, exactly at and just above a threshold detects mistakes that a typical middle value will miss.

`&&` requires both conditions and stops after false; `||` stops after true. A switch expression returns one value from its matching arm. The discard pattern `_` can provide an explicit fallback but must not conceal invalid input.

An else branch can accidentally classify every invalid value as valid. Test domain validity independently from success thresholds. Do not use a fallback to hide an impossible state without explaining recovery.

## Review before continuing

Run the reference and confirm that it prints `csharp-005: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
