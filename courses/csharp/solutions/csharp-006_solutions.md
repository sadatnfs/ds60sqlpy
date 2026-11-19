# csharp-006: explanation and comparison

Attempt the six guide tasks before opening this comparison. The executable reference is [csharp-006_solution.cs](csharp-006_solution.cs). It runs both worked examples and the reference answers below, and its assertions are always active under the prepared classroom compile settings.

## Why the two examples differ

**Sum with a maintained invariant:** Before each iteration, sum equals the sum of values already visited. Zero is the identity that makes the invariant true initially. The sum is 12 and the empty sum is zero.

**Locate the first match:** Stopping at the first match is part of the contract. Without break, the same loop could return the last match. The first 8 is at index 1; 9 is absent.

## Task answers

### Task 1: Predict and explain

Write the accumulator value before and after every iteration in Example A.

No separate reference answer has been written for this task. Example A is the evidence to compare with: Before each iteration, sum equals the sum of values already visited. Zero is the identity that makes the invariant true initially. The sum is 12 and the empty sum is zero.

### Task 2: Guided modification

Skip negative values while preserving the sum invariant.

No separate reference answer has been written for this task. Start from Example B: Stopping at the first match is part of the contract. Without break, the same loop could return the last match. The first 8 is at index 1; 9 is absent.

### Task 3: Independent construction

Implement a first-match search returning a separate not-found representation.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```csharp
bool TryFirstIndex(int[] items, int target, out int index) {
  for (int i = 0; i < items.Length; i++) {
    if (items[i] == target) {
      index = i;
      return true;
    }
  }
  index = -1;
  return false;
}
var values = new[] { 5, 7, 7 };
Check(TryFirstIndex(values, 7, out int at) && at == 1, "first match");
Check(!TryFirstIndex(values, 9, out _), "not found");
Check(!TryFirstIndex(Array.Empty<int>(), 1, out _), "empty input");
```

**Observe:** The first 7 is at index 1; a missing target and an empty array both return false.

The loop stops at the first match, and the Try pattern reports not-found through its bool result, so a caller checks that result before using the index instead of mistaking a sentinel such as -1 for a position.

### Task 4: Diagnose a defect

Diagnose the condition i <= values.Length using a one-element array.

No reference answer has been written for this task yet. The wrong assumptions to look for are this lesson's pitfalls: Loop indices count from zero while lengths count elements. A sentinel such as -1 must be checked before indexing. Mutating a collection during enumeration can invalidate the traversal contract.

### Task 5: Boundary evidence

Check empty, singleton, no-match and repeated-match inputs.

No reference answer has been written for this task yet. Write the expected value or documented rejection for each boundary before running it, and compare with the checks in Example A (Sum with a maintained invariant) and Example B (Locate the first match).

### Task 6: Transfer and justify

Design a bounded retry loop and explain both its invariant and its stopping argument.

No single reference answer exists: several designs can satisfy this transfer task. Justify yours against the mechanism described below and the vocabulary entry **Invariant**, and state one limitation of your choice.

## Mechanism and diagnostic reasoning

A loop repeats a state transition. To understand it, state what is true before the first iteration and what remains true after each iteration. This repeated truth is an invariant. A second argument explains termination: some bounded quantity moves toward a stopping condition. A correct-looking body can still fail because its boundary executes once too often or never stops.

`foreach` expresses traversal of an existing sequence and usually avoids manual index bookkeeping. Use an index when the position itself matters, but relate the valid index range to the collection length. Empty inputs are especially revealing because the initial state becomes the final result without any iteration.

`for (initial; condition; update)` initializes once, checks before each body, and updates after each body. For an array of Length n, valid indices are zero through n minus one. `break` exits the loop; `continue` skips the remainder of one iteration.

Loop indices count from zero while lengths count elements. A sentinel such as -1 must be checked before indexing. Mutating a collection during enumeration can invalidate the traversal contract.

## Review before continuing

Run the reference and confirm that it prints `csharp-006: passed`, then reconstruct one boundary case from memory and explain which check would reject a plausible wrong implementation. External project steps need their own build and platform evidence; a passing portable reference does not establish them.
